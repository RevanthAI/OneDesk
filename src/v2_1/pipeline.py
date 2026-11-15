"""One pinned HF job: stage-one diagnostic, stronger SFT, guarded GRPO, five-way eval."""
import argparse,hashlib,importlib.metadata,json,os,shutil,sys,time,traceback
from pathlib import Path
import torch
from peft import PeftModel
from huggingface_hub import HfApi,snapshot_download
from .data import verify,write_json
from .backend import MODEL,REVISION,load_base
from .evaluate_auditkit import evaluate
from .training import run_sft,run_grpo,cleanup
from .compare import compare
from .plot_grpo import plot_run

HANDOFF_DIRS=('prior_v2','stage1_diagnostic','sft_training','sft_evaluation')
def copy_completed_sft(source,out):
    source=Path(source);out=Path(out)
    for name in HANDOFF_DIRS:shutil.copytree(source/name,out/name,dirs_exist_ok=True)
    shutil.copy2(source/'V2_STAGE1_DIAGNOSTIC.md',out/'V2_STAGE1_DIAGNOSTIC.md')
    return json.loads((source/'MODEL_REVISIONS.json').read_text())['SFT']

def main():
    p=argparse.ArgumentParser();p.add_argument('--run-repo',required=True);p.add_argument('--run-prefix',required=True);p.add_argument('--sft-repo',required=True);p.add_argument('--grpo-best-repo',required=True);p.add_argument('--grpo-final-repo',required=True);p.add_argument('--resume-prefix');p.add_argument('--resume-revision');p.add_argument('--group-size',type=int,choices=(4,6),default=4);p.add_argument('--temperature',type=float,default=.8);p.add_argument('--retry-temperature',type=float,default=.95);a=p.parse_args()
    api=HfApi(token=os.environ['HF_TOKEN']);out=Path('reports/v2_1');out.mkdir(exist_ok=True);started=time.time();torch.manual_seed(20261113);torch.set_num_threads(8)
    snapshot=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('data_v2').iterdir() if p.is_file()}
    frozen=snapshot();write_json(out/'APPROVED_DATA_LOCK.json',frozen);write_json(out/'RUN_CONFIG.json',dict(recipe='v2.1',model=MODEL,revision=REVISION,dataset_hashes=verify(),sft_epochs=4,sft_steps=120,sft_effective_batch=8,sft_lr=1.5e-4,sft_max_seq_length=2560,grpo_steps=[60,60],grpo_lr=5e-6,beta=.05,group_size=a.group_size,temperature=a.temperature,retry_temperature=a.retry_temperature,validation_every=30,abstention_stop_above=.40,max_context_length=4096,max_new_tokens_per_turn=192,compute_dtype='bfloat16',quantization=None))
    write_json(out/'ENVIRONMENT.json',dict(python=sys.version,packages={d.metadata['Name']:d.version for d in importlib.metadata.distributions() if d.metadata['Name']},toolkits=json.loads(Path('toolkit_revisions.json').read_text())))
    def persist():
        if (out/'grpo_training').exists():plot_run(out/'grpo_training')
        api.upload_folder(repo_id=a.run_repo,repo_type='dataset',folder_path=str(out),path_in_repo=a.run_prefix,ignore_patterns=['cloud/**','downloads/**','**/.cache/**','**/reference/**'],commit_message='v2.1 diagnostics and checkpoints '+a.run_prefix)
    def event(phase,**extra):
        data=dict(phase=phase,updated_at=time.time(),**extra);write_json(out/'STATUS.json',data);print(json.dumps(dict(event='v21_phase',**data)),flush=True);persist()
    revisions={}
    def export(path,repo,label):
        commit=api.upload_folder(repo_id=repo,folder_path=str(path),commit_message='Validation-tagged v2.1 '+label+' '+a.run_prefix);revisions[label]=dict(repo=repo,revision=commit.oid);write_json(out/'MODEL_REVISIONS.json',revisions)
    def eval_adapter(path,folder,splits):
        model,tok=load_base();model=PeftModel.from_pretrained(model,str(path),is_trainable=False)
        try:return evaluate(model,tok,folder,splits=splits,persist=persist)
        finally:del model,tok;cleanup()
    try:
        if a.resume_prefix:
            event('resume_validated_sft')
            whitelist=HANDOFF_DIRS
            revision=a.resume_revision or api.repo_info(a.run_repo,repo_type='dataset').sha
            patterns=[a.resume_prefix+'/'+name+'/**' for name in whitelist]+[a.resume_prefix+'/MODEL_REVISIONS.json',a.resume_prefix+'/V2_STAGE1_DIAGNOSTIC.md']
            source=Path(snapshot_download(a.run_repo,repo_type='dataset',revision=revision,local_dir='/workspace/sft_handoff',allow_patterns=patterns,ignore_patterns=['**/*.safetensors','**/*.pt','**/*.bin','**/tokenizer.json','**/reference/**']))/a.resume_prefix
            revisions['SFT']=copy_completed_sft(source,out);write_json(out/'MODEL_REVISIONS.json',revisions)
            sft=Path('/workspace/checkpoints_v2_1/validated_sft');snapshot_download(revisions['SFT']['repo'],revision=revisions['SFT']['revision'],local_dir=str(sft));sft_meta=json.loads((out/'sft_training/metadata.json').read_text())
            write_json(out/'HANDOFF.json',dict(source_prefix=a.resume_prefix,source_revision=revision,sft=revisions['SFT'],reason='G=4 pilot had low variance after stronger SFT; reuse completed SFT and evaluations unchanged; discard pilot policy updates and restart the bounded GRPO experiment from the same selected SFT',group_size=a.group_size,temperature=a.temperature,retry_temperature=a.retry_temperature))
        else:
            event('stage1_diagnostic')
            old=json.loads((out/'prior_v2/selected_stage1.json').read_text());source=Path(snapshot_download(old['source_repo'],repo_type='dataset',revision=old['source_revision'],local_dir='/workspace/diagnostic_input',allow_patterns=[old['source_path']+'**']))/old['source_path']
            assert hashlib.sha256((source/'adapter_model.safetensors').read_bytes()).hexdigest()==old['adapter_sha256']
            diagnostic=eval_adapter(source,out/'stage1_diagnostic',('validation',));accuracy=diagnostic['validation']['metrics']['exact_outcome']['estimate'];write_json(out/'stage1_diagnostic/provenance.json',dict(source=old,validation_accuracy=accuracy))
            (out/'V2_STAGE1_DIAGNOSTIC.md').write_text('# Preserved v2 stage-one diagnostic\n\nThe original v2 findings remain untouched. The revision-pinned 120-update adapter was verified by SHA-256 and reevaluated on the same 80 validation rows in matched BF16. Accuracy: %.2f%%. This is a diagnostic reproduction, not a fresh holdout result.\n'%(100*accuracy))
            event('sft_training',stage1_validation_accuracy=accuracy)
            sft,sft_meta=run_sft(out/'sft_training',persist);export(sft,a.sft_repo,'SFT')
            event('sft_holdout_evaluation');eval_adapter(sft,out/'sft_evaluation',('validation','test_synth','repo_style'))
        if not sft_meta['warm_start_gate']['passed']:
            write_json(out/'COMPLETION.json',dict(status='warm_start_gate_blocked',reason='No significantly stronger and abstention-safe SFT warm start; GRPO not launched',sft=sft_meta,approved_data_unchanged=snapshot()==frozen));event('warm_start_gate_blocked');return
        event('positive_anchor_grpo',selected_sft_step=sft_meta['selected_step'],validation_accuracy=sft_meta['selected_validation_accuracy'])
        best,final,gp=run_grpo(sft,out/'grpo_training',sft_meta,persist,group_size=a.group_size,temperature=a.temperature,retry_temperature=a.retry_temperature)
        export(best,a.grpo_best_repo,'GRPO_BEST_VAL');export(final,a.grpo_final_repo,'GRPO_FINAL')
        event('grpo_best_holdout_evaluation',completed_updates=gp['completed_updates'],selected_step=gp['selected_step'],early_stop=gp['early_stop']);eval_adapter(best,out/'grpo_evaluation',('validation','test_synth','repo_style'))
        compare(out)
        from .diagnostics import analyze
        from .trace_viewer import export_viewer
        from .failure_analysis import analyze as analyze_failures
        analyze(out/'grpo_training');export_viewer(out/'grpo_training')
        for folder in ('sft_evaluation','grpo_evaluation'):analyze_failures(out/folder)
        if snapshot()!=frozen:raise RuntimeError('Frozen data changed')
        write_json(out/'COMPLETION.json',dict(status='complete',grpo_training_status=gp['status'],completed_grpo_updates=gp['completed_updates'],selected_grpo_step=gp['selected_step'],approved_data_unchanged=True,wall_seconds=time.time()-started,model_revisions=revisions))
        event('finished',status='complete')
    except Exception as error:
        write_json(out/'FAILURE.json',dict(type=type(error).__name__,error=str(error),traceback=traceback.format_exc()));persist();raise
if __name__=='__main__':main()
