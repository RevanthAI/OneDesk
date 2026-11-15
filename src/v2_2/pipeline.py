"""Isolated two-epoch protocol warmup, guarded 40+40 GRPO and seven-row study."""
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

def main():
    p=argparse.ArgumentParser()
    for name in ('run-repo','run-prefix','sft-repo','grpo-best-repo','grpo-final-repo'):p.add_argument('--'+name,required=True)
    p.add_argument('--stage1-prefix');p.add_argument('--stage1-revision');p.add_argument('--resume-step',type=int,choices=(20,30));p.add_argument('--group-size',type=int,choices=(6,),default=6);p.add_argument('--temperature',type=float,default=1.);p.add_argument('--retry-temperature',type=float,default=1.15);a=p.parse_args()
    api=HfApi(token=os.environ['HF_TOKEN']);out=Path('reports_v2_2');out.mkdir(exist_ok=True);started=time.time();torch.manual_seed(20261113);torch.set_num_threads(8)
    snapshot=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('data_v2').iterdir() if p.is_file()}
    frozen=snapshot();write_json(out/'APPROVED_DATA_LOCK.json',frozen)
    write_json(out/'RUN_CONFIG.json',dict(recipe='v2.1 protocol warmup follow-up (isolated v2_2 runtime)',model=MODEL,revision=REVISION,dataset_hashes=verify(),sft_epochs=2,sft_steps=60,sft_candidates=[45,60],sft_validation_steps=[30,45,60],sft_effective_batch=8,sft_lr=1.5e-4,sft_scheduler_horizon=120,sft_max_seq_length=2560,grpo_steps=[40,40],grpo_lr=5e-6,beta=.04,group_size=a.group_size,temperature=a.temperature,retry_temperature=a.retry_temperature,validation_every=20,abstention_stop_above=.40,max_context_length=4096,max_new_tokens_per_turn=192,compute_dtype='bfloat16',quantization=None,grpo_soft_deadline_seconds_from_pipeline_start=8700,stage1_source_prefix=a.stage1_prefix,stage1_source_revision=a.stage1_revision))
    write_json(out/'ENVIRONMENT.json',dict(python=sys.version,packages={d.metadata['Name']:d.version for d in importlib.metadata.distributions() if d.metadata['Name']},toolkits=json.loads(Path('toolkit_revisions.json').read_text())))
    def persist():
        if (out/'grpo_training').exists():plot_run(out/'grpo_training')
        api.upload_folder(repo_id=a.run_repo,repo_type='dataset',folder_path=str(out),path_in_repo=a.run_prefix,ignore_patterns=['cloud/**','downloads/**','**/.cache/**','**/reference/**'],commit_message='Warmup GRPO checkpoint '+a.run_prefix)
    def event(phase,**extra):
        data=dict(phase=phase,updated_at=time.time(),**extra);write_json(out/'STATUS.json',data);print(json.dumps(dict(event='warmup_phase',**data)),flush=True);persist()
    revisions={}
    def export(path,repo,label):
        commit=api.upload_folder(repo_id=repo,folder_path=str(path),commit_message='Warmup experiment '+label+' '+a.run_prefix);revisions[label]=dict(repo=repo,revision=commit.oid);write_json(out/'MODEL_REVISIONS.json',revisions);persist()
    def eval_adapter(path,folder,splits):
        model,tok=load_base()
        if path is not None:model=PeftModel.from_pretrained(model,str(path),is_trainable=False)
        try:return evaluate(model,tok,folder,splits=splits,persist=persist)
        finally:del model,tok;cleanup()
    try:
        stage1_source=None
        if a.stage1_prefix:
            from .handoff import REPORT_DIRS
            event('reuse_completed_stage1_boundary')
            revision=a.stage1_revision or api.repo_info(a.run_repo,repo_type='dataset').sha
            patterns=[a.stage1_prefix+'/'+name+'/**' for name in REPORT_DIRS]+[a.stage1_prefix+'/MODEL_REVISIONS.json',a.stage1_prefix+'/grpo_training/stage1/**',a.stage1_prefix+'/grpo_training/best_val_adapter/**',a.stage1_prefix+'/grpo_training/validation_checkpoints/**',a.stage1_prefix+'/grpo_training/validation_history.json',a.stage1_prefix+'/grpo_training/validation/step_020/**',a.stage1_prefix+'/grpo_training/validation/step_040/**']
            source=Path(snapshot_download(a.run_repo,repo_type='dataset',revision=revision,local_dir='/workspace/stage_boundary_input',allow_patterns=patterns,ignore_patterns=(['**/sft_training/checkpoint-*/**','**/tokenizer.json','**/reference/**','**/sft_training/**/adapter_model.safetensors'] if a.resume_step else ['**/checkpoint-*/**','**/*.pt','**/*.bin','**/tokenizer.json','**/reference/**','**/sft_training/**/adapter_model.safetensors'])))/a.stage1_prefix
            for name in REPORT_DIRS:shutil.copytree(source/name,out/name,dirs_exist_ok=True)
            revisions['SFT_WARMUP']=json.loads((source/'MODEL_REVISIONS.json').read_text())['SFT_WARMUP'];write_json(out/'MODEL_REVISIONS.json',revisions)
            sft=Path('/workspace/checkpoints_v2_2/frozen_warmup_reference');snapshot_download(revisions['SFT_WARMUP']['repo'],revision=revisions['SFT_WARMUP']['revision'],local_dir=str(sft))
            sft_meta=json.loads((out/'sft_training/metadata.json').read_text());stage1_source=source/'grpo_training'
            write_json(out/'HANDOFF.json',dict(source_prefix=a.stage1_prefix,source_revision=revision,policy=('Stage-1 optimizer checkpoint at update '+str(a.resume_step)) if a.resume_step else 'Exact Stage-1 40-update last_adapter',reference=revisions['SFT_WARMUP'],optimizer='Stage-1 optimizer/scheduler/RNG restored when resuming a checkpoint; fresh Stage-2 optimizer as specified by the original recipe',resume_step=a.resume_step,reason='Separate planned stages to finish the requested 40+40 updates and evaluation within capped cloud allocations; no SFT, Stage-1 or baseline retraining'))
        else:
            event('preserved_stage1_full_diagnostic')
            old=json.loads((out/'prior_v2/selected_stage1.json').read_text());source=Path(snapshot_download(old['source_repo'],repo_type='dataset',revision=old['source_revision'],local_dir='/workspace/diagnostic_input',allow_patterns=[old['source_path']+'**']))/old['source_path']
            assert hashlib.sha256((source/'adapter_model.safetensors').read_bytes()).hexdigest()==old['adapter_sha256']
            diagnostic=eval_adapter(source,out/'stage1_evaluation',('validation','test_synth','repo_style'));write_json(out/'stage1_evaluation/provenance.json',dict(source=old,selection='Preserved original validation-selected v2 stage1; no new selection on holdouts'))
            event('base_validation_completion');eval_adapter(None,out/'prior_v2/base',('validation',))
            event('sft_warmup_training');sft,sft_meta=run_sft(out/'sft_training',persist);export(sft,a.sft_repo,'SFT_WARMUP')
            event('warmup_full_evaluation',selected_sft_step=sft_meta['selected_step']);eval_adapter(sft,out/'sft_evaluation',('validation','test_synth','repo_style'))
        if not sft_meta['warm_start_gate']['passed']:
            write_json(out/'COMPLETION.json',dict(status='warm_start_gate_blocked',reason='Warmup did not pass validation improvement and safety gate',sft=sft_meta,approved_data_unchanged=snapshot()==frozen));event('warm_start_gate_blocked');return
        event('positive_anchor_grpo',selected_sft_step=sft_meta['selected_step'])
        best,final,gp=run_grpo(sft,out/'grpo_training',sft_meta,persist,group_size=a.group_size,temperature=a.temperature,retry_temperature=a.retry_temperature,deadline=started+8700,stage1_source=stage1_source,resume_step=a.resume_step)
        export(best,a.grpo_best_repo,'GRPO_BEST_VAL');export(final,a.grpo_final_repo,'GRPO_FINAL')
        event('grpo_best_full_evaluation',completed_updates=gp['completed_updates'],selected_step=gp['selected_step'],early_stop=gp['early_stop']);eval_adapter(best,out/'grpo_evaluation',('validation','test_synth','repo_style'))
        compare(out)
        from .diagnostics import analyze
        from .trace_viewer import export_viewer
        from .failure_analysis import analyze as analyze_failures
        analyze(out/'grpo_training');export_viewer(out/'grpo_training')
        for folder in ('sft_evaluation','grpo_evaluation','stage1_evaluation'):analyze_failures(out/folder)
        if snapshot()!=frozen:raise RuntimeError('Frozen data changed')
        write_json(out/'COMPLETION.json',dict(status='complete',grpo_training_status=gp['status'],completed_grpo_updates=gp['completed_updates'],selected_grpo_step=gp['selected_step'],approved_data_unchanged=True,wall_seconds=time.time()-started,model_revisions=revisions))
        event('finished',status='complete')
    except Exception as error:
        write_json(out/'FAILURE.json',dict(type=type(error).__name__,error=str(error),traceback=traceback.format_exc()));persist();raise
if __name__=='__main__':main()
