"""Bounded two-stage on-policy GRPO experiment from pinned SFT; persist real logs."""
from __future__ import annotations
import argparse,hashlib,json,os,time,traceback
from pathlib import Path
import torch
from datasets import Dataset
from transformers import AutoTokenizer,AutoModelForCausalLM
from peft import PeftModel
from trl import GRPOConfig
from .grpo_core import load_curriculum
from .grpo_rollout import sample_episodes
from .agenttune_grpo_backend import DriftGuardAgentTuneGRPO,PersistentLogs
from .reward import outcome_ok,citation_f1
from .plot_grpo import plot_run
MODEL='CohereLabs/tiny-aya-fire';BASE_REVISION='73500c80fcb6c8bea3e830c21d5d2920249a0e1a'
SFT_REPO='Revanth-ml/driftguard-tiny-aya-fire-sft';SFT_REVISION='b0d0d072311e62e31eb6258ad8ce987e8bf7926d'


def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=('smoke','pilot'),default='smoke');p.add_argument('--output',default='output');p.add_argument('--stage1-steps',type=int,default=20);p.add_argument('--stage2-steps',type=int,default=40);p.add_argument('--run-repo');p.add_argument('--run-prefix',default='grpo');p.add_argument('--adapter-repo');args=p.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    from huggingface_hub import HfApi
    api=HfApi(token=os.environ.get('HF_TOKEN'))
    def persist():
        plot_run(out)
        if args.run_repo:api.upload_folder(repo_id=args.run_repo,repo_type='dataset',folder_path=str(out),path_in_repo=args.run_prefix,ignore_patterns=['**/adapter_model.*','**/optimizer.pt','**/scheduler.pt','**/rng_state.pth','**/tokenizer.json','**/reference/**'],commit_message='GRPO diagnostics '+args.run_prefix)
    metadata=dict(mode=args.mode,model=MODEL,base_revision=BASE_REVISION,sft_repo=SFT_REPO,sft_revision=SFT_REVISION,seed=20261111,group_size=4,temperature=.8,top_p=1.,top_k=0,beta=.04,learning_rate=5e-6,reward_mode='evidence_gated',reward_diagnostic='specified',algorithm='live multi-turn episode GRPO; assistant-only sampled-token loss; SFT reference adapter',agenttune='upstream TrlAgenticGrpo train/data/save lifecycle with project TRL0.23 live rollout and sparse loss compatibility backend',started_at=time.time())
    try:
        if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():raise RuntimeError('BF16-capable cloud GPU required')
        torch.manual_seed(metadata['seed']);torch.set_num_threads(8)
        stages,validation,world=load_curriculum()
        metadata.update(gpu=torch.cuda.get_device_name(0),gpu_memory_gib=torch.cuda.get_device_properties(0).total_memory/2**30,stage_sizes=[len(s) for s in stages],validation_case_ids=sorted({t['case_id'] for t in validation}),training_source_hashes={f:hashlib.sha256(Path('data',f).read_bytes()).hexdigest() for f in ('train_grpo_stage1.jsonl','train_grpo_stage2.jsonl','world_train.json')})
        (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2));persist()
        tokenizer=AutoTokenizer.from_pretrained(SFT_REPO,revision=SFT_REVISION,token=os.environ.get('HF_TOKEN'),padding_side='left')
        if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
        base=AutoModelForCausalLM.from_pretrained(MODEL,revision=BASE_REVISION,token=os.environ.get('HF_TOKEN'),dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':'cuda:0'})
        model=PeftModel.from_pretrained(base,SFT_REPO,revision=SFT_REVISION,is_trainable=True,token=os.environ.get('HF_TOKEN'))
        model.load_adapter(SFT_REPO,adapter_name='reference',revision=SFT_REVISION,is_trainable=False,token=os.environ.get('HF_TOKEN'));model.set_adapter('default')
        for module in model.modules():
            if isinstance(module,torch.nn.Dropout):module.p=0.
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});model.config.use_cache=False
        initial={n:p.detach().cpu().clone() for n,p in model.named_parameters() if p.requires_grad}
        initial_reference={n:p.detach().cpu().clone() for n,p in model.named_parameters() if '.reference.' in n}
        metadata['trainable_parameters']=sum(p.numel() for p in model.parameters() if p.requires_grad)
        def evaluate(label):
            # Validation is train-world data excluded from both SFT fit and GRPO fit.
            # No frozen synthetic/OSS holdout is packaged or evaluated in this job.
            episodes=[]
            for i in range(0,len(validation),4):
                samples=sample_episodes(validation[i:i+4],world,model,tokenizer,temperature=0)
                for task,sample in zip(validation[i:i+4],samples):episodes.append(dict(task_id=task['task_id'],case_id=task['case_id'],language=task['language'],kind=task['kind'],exact_outcome=int(outcome_ok(sample['episode']['prediction'],task)),reward=sample['reward'],episode=sample['episode']))
            result={'label':label,'n':len(episodes),'exact_outcome':sum(e['exact_outcome'] for e in episodes)/len(episodes),'mean_reward':sum(e['reward'] for e in episodes)/len(episodes)}
            (out/(label+'_validation.json')).write_text(json.dumps(dict(result,episodes=episodes),indent=2,ensure_ascii=False));print(json.dumps({'event':'validation',**result}),flush=True);persist();return result
        before=evaluate('before') if args.mode=='pilot' else None
        step_counts=[5] if args.mode=='smoke' else [args.stage1_steps,args.stage2_steps]
        completed=[]
        for stage_index,steps in enumerate(step_counts):
            stage_out=out/f'stage{stage_index+1}';stage_out.mkdir(parents=True,exist_ok=True)
            rows=stages[stage_index]
            if args.mode=='smoke':
                # Balanced task/language representatives, independently of test outcomes.
                ordered=sorted(rows,key=lambda t:hashlib.sha256(('grpo-smoke:'+t['task_id']).encode()).hexdigest())
                rows=[];seen=set()
                for row in ordered:
                    key=(row['language'],row['kind'])
                    if key not in seen:rows.append(row);seen.add(key)
            dataset=Dataset.from_list([{'prompt':t['prompt'],'task':t} for t in rows])
            config=GRPOConfig(output_dir=str(stage_out),max_steps=steps,per_device_train_batch_size=4,gradient_accumulation_steps=1,num_generations=4,steps_per_generation=1,num_iterations=1,learning_rate=5e-6,lr_scheduler_type='constant',warmup_steps=0,beta=.04,epsilon=.2,temperature=.8,top_p=1.,top_k=0,max_completion_length=1536,max_prompt_length=None,bf16=True,fp16=False,gradient_checkpointing=True,gradient_checkpointing_kwargs={'use_reentrant':False},logging_steps=1,save_steps=10,save_total_limit=2,save_only_model=True,report_to=['tensorboard'],logging_dir=str(stage_out/'tensorboard'),remove_unused_columns=False,seed=metadata['seed']+stage_index,data_seed=metadata['seed']+stage_index,dataloader_num_workers=0,disable_tqdm=True,loss_type='grpo',max_grad_norm=1.)
            wrapper=DriftGuardAgentTuneGRPO(model=model,processing_class=tokenizer,train_dataset=dataset,output_dir=str(stage_out),dataset_name=f'train_grpo_stage{stage_index+1}.jsonl',grpo_config=config,world=world,trace_dir=stage_out,callbacks=[PersistentLogs(stage_out,persist)])
            stats=wrapper.train();completed.append({'stage':stage_index+1,'steps':steps,'metrics':stats['metrics']});persist()
        change=sum(float((p.detach().cpu()-initial[n]).abs().sum()) for n,p in model.named_parameters() if n in initial)
        reference_change=sum(float((p.detach().cpu()-initial_reference[n]).abs().sum()) for n,p in model.named_parameters() if n in initial_reference)
        metrics=[json.loads(line) for f in out.glob('stage*/rollout_metrics.jsonl') for line in f.read_text().splitlines()]
        mixed=sum(r['zero_variance_fraction']<1 for r in metrics)
        if reference_change!=0:raise RuntimeError('frozen SFT reference changed')
        if not change>0 or not mixed:raise RuntimeError('no useful policy update: no adapter change or no mixed-reward groups')
        metadata.update(adapter_l1_change=change,reference_l1_change=reference_change,mixed_reward_batches=mixed,rollout_batches=len(metrics),stages=completed,validation_before=before)
        if args.mode=='pilot':metadata['validation_after']=evaluate('after')
        adapter=out/'adapter';model.save_pretrained(adapter,selected_adapters=['default'],safe_serialization=True);tokenizer.save_pretrained(adapter)
        card='---\nlicense: cc-by-nc-4.0\nbase_model: CohereLabs/tiny-aya-fire\npipeline_tag: text-generation\n---\n\n# DriftGuard GRPO experiment\n\nContinues the pinned DriftGuard SFT adapter with live multi-turn GRPO. This is an experimental checkpoint, not a proven improvement over SFT. See run artifacts for reward, optimizer, rollout and validation diagnostics. No evaluation holdout was used for training.\n'
        (adapter/'README.md').write_text(card)
        if args.adapter_repo and args.mode=='pilot':api.upload_folder(repo_id=args.adapter_repo,folder_path=str(adapter),commit_message='Bounded GRPO pilot adapter')
        metadata.update(status='smoke_passed' if args.mode=='smoke' else 'pilot_complete',finished_at=time.time(),peak_vram_reserved_gib=torch.cuda.max_memory_reserved()/2**30)
        (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2));persist();print(json.dumps({'event':'complete','status':metadata['status'],'adapter_l1_change':change,'mixed_reward_batches':mixed}),flush=True)
    except Exception as e:
        (out/'failure.json').write_text(json.dumps({'type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc()},indent=2))
        persist();raise

if __name__=='__main__':main()
