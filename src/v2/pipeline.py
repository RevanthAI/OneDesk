"""Run the approved v2 experiment sequentially on one Hugging Face GPU job."""
import argparse,gc,hashlib,json,os,time,traceback,sys,importlib.metadata,shutil
from pathlib import Path
import torch
from peft import PeftModel
from huggingface_hub import HfApi,snapshot_download
from .data import verify,write_json
from .backend import load_base,MODEL,REVISION
from .evaluate_auditkit import evaluate
from .training import run_sft,run_grpo,cleanup
from .compare import compare
from .plot_grpo import plot_run


def main():
    p=argparse.ArgumentParser();p.add_argument('--run-repo',required=True);p.add_argument('--run-prefix',required=True);p.add_argument('--sft-repo',required=True);p.add_argument('--grpo-repo',required=True);p.add_argument('--phase',choices=('all','base'),default='all');p.add_argument('--resume-prefix');p.add_argument('--sft-revision');args=p.parse_args()
    out=Path('reports_v2');out.mkdir(exist_ok=True);api=HfApi(token=os.getenv('HF_TOKEN'));started=time.time();torch.manual_seed(20261112);torch.set_num_threads(8)
    if args.resume_prefix:
        restore=Path('/workspace/resume_input')
        revision=api.repo_info(args.run_repo,repo_type='dataset').sha
        snapshot_download(args.run_repo,repo_type='dataset',revision=revision,local_dir=str(restore),allow_patterns=[args.resume_prefix+'/**'],ignore_patterns=['**/*.safetensors','**/*.pt','**/*.bin','**/tokenizer.json','**/reference/**'])
        source=restore/args.resume_prefix
        for item in source.iterdir():
            target=out/item.name
            if item.is_dir():shutil.copytree(item,target,dirs_exist_ok=True)
            else:shutil.copy2(item,target)
        write_json(out/'HANDOFF.json',dict(source_prefix=args.resume_prefix,source_revision=revision,reason='Retain completed Base/SFT; correct FP32 temperature-scaling order before GRPO',sft_revision=args.sft_revision))
    frozen={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in Path('data_v2').iterdir() if f.is_file()}
    config=dict(data_dir='data_v2',dataset_hashes=verify(),model=MODEL,revision=REVISION,seed=20261112,sft_epochs=1,sft_rows=240,sft_max_seq_length=2560,validation_rows=80,grpo_stage_steps=[120,220],group_size=4,max_context_length=4096,max_new_tokens_per_turn=192,greedy_evaluation_batch=16,compute_dtype='bfloat16',quantization=None)
    write_json(out/'RUN_CONFIG.json',config);write_json(out/'APPROVED_DATA_LOCK.json',frozen)
    write_json(out/'ENVIRONMENT.json',dict(python=sys.version,packages={d.metadata['Name']:d.version for d in importlib.metadata.distributions() if d.metadata['Name']},toolkits=json.loads(Path('toolkit_revisions.json').read_text())))
    def persist():
        for phase in ('grpo_smoke','grpo_training'):
            if (out/phase).exists():plot_run(out/phase)
        api.upload_folder(repo_id=args.run_repo,repo_type='dataset',folder_path=str(out),path_in_repo=args.run_prefix,ignore_patterns=['cloud/**','downloads/**','**/.cache/**','**/reference/**'],commit_message='v2 pipeline diagnostics/checkpoints '+args.run_prefix)
    def event(phase,**extra):
        value=dict(phase=phase,updated_at=time.time(),**extra);write_json(out/'STATUS.json',value);print(json.dumps({'event':'v2_phase',**value}),flush=True);persist()
    def export_repo(path,repo):
        api.upload_folder(repo_id=repo,folder_path=str(path),commit_message='Approved v2 checkpoint '+args.run_prefix)
        info=api.model_info(repo);return dict(repo=repo,revision=info.sha)
    def evaluate_adapter(path,folder,splits):
        model,tok=load_base();model=PeftModel.from_pretrained(model,str(path),is_trainable=False)
        result=evaluate(model,tok,folder,splits=splits,persist=persist)
        del model,tok;cleanup();return result
    try:
        if not args.resume_prefix:
            event('A_base_evaluation')
            model,tok=load_base();evaluate(model,tok,out/'v2_base_fire',persist=persist);del model,tok;cleanup()
            if args.phase=='base':event('base_complete',status='complete');return
            event('B_sft_training')
            sft=run_sft(out/'sft_training',persist=persist);model_revisions={'SFT':export_repo(sft,args.sft_repo)};write_json(out/'MODEL_REVISIONS.json',model_revisions)
        else:
            if not args.sft_revision:raise ValueError('resumed SFT weights must be revision-pinned')
            if not (out/'v2_base_fire/summary.json').exists():raise ValueError('resume is missing completed Base evaluation')
            sft=Path('/workspace/checkpoints_v2/sft_adapter')
            snapshot_download(args.sft_repo,revision=args.sft_revision,local_dir=str(sft))
            model_revisions={'SFT':dict(repo=args.sft_repo,revision=args.sft_revision)};write_json(out/'MODEL_REVISIONS.json',model_revisions)
        event('B_sft_evaluation');evaluate_adapter(sft,out/'v2_sft_fire',('validation','test_synth','repo_style'))
        event('C_grpo_smoke')
        smoke,smoke_meta=run_grpo(sft,out/'grpo_smoke',(5,),persist=persist)
        if smoke_meta['status']!='complete' or smoke_meta['stages'][0]['completed_steps']!=5:raise RuntimeError('GRPO smoke did not complete five active updates; inspect saturation logs')
        event('C_grpo_training',smoke_peak_reserved_gib=smoke_meta['peak_reserved_gib'])
        def validate(model,tok,label):
            evaluate(model,tok,out/'grpo_validation'/label,splits=('validation',),persist=persist)
            model.train();model.config.use_cache=False
        grpo,grpo_meta=run_grpo(sft,out/'grpo_training',(120,220),persist=persist,validate=validate)
        model_revisions['GRPO']=export_repo(grpo,args.grpo_repo);write_json(out/'MODEL_REVISIONS.json',model_revisions)
        event('C_grpo_evaluation');evaluate_adapter(grpo,out/'v2_grpo_fire',('validation','test_synth','repo_style'))
        compare(out)
        current={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in Path('data_v2').iterdir() if f.is_file()}
        if current!=frozen:raise RuntimeError('approved data folder changed during execution')
        status='complete' if grpo_meta['status']=='complete' else 'early_stopped'
        write_json(out/'COMPLETION.json',dict(status=status,wall_seconds=time.time()-started,completed_grpo_steps=sum(s['completed_steps'] for s in grpo_meta['stages']),requested_grpo_steps=340,approved_data_unchanged=True,model_revisions=model_revisions))
        event('finished',status=status)
    except Exception as error:
        write_json(out/'FAILURE.json',dict(type=type(error).__name__,error=str(error),traceback=traceback.format_exc()))
        persist();raise
if __name__=='__main__':main()
