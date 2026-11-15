"""Cloud BF16 LoRA smoke/sizing and full SFT, with persistent Hub artifacts."""
from __future__ import annotations
import argparse
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import time
import traceback
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
from peft import LoraConfig,get_peft_model
from agenttune.core.sft.config import SFTConfig,ModelConfig,DatasetConfig,TrainingConfig,LoggingConfig
from .agenttune_sft_backend import DriftGuardSFTTrainer
from .sft_data import load_training_rows,case_split,encode_trajectory,representative_smoke
MODEL='CohereLabs/tiny-aya-fire'
REVISION='73500c80fcb6c8bea3e830c21d5d2920249a0e1a'


def upload(output,args):
    if not args.run_repo:return
    from huggingface_hub import HfApi
    HfApi(token=os.environ['HF_TOKEN']).upload_folder(repo_id=args.run_repo,repo_type='dataset',folder_path=str(output),path_in_repo=args.run_prefix,ignore_patterns=['**/optimizer_state.pt','**/adapter_model.safetensors','**/tokenizer.json','merged/**','adapter/**'],commit_message='Persist '+args.mode+' run artifacts')


def config_for(batch,steps,output,accumulation=1):
    return SFTConfig(model=ModelConfig(name_or_path=MODEL,precision='bf16',max_seq_length=1536,peft_enabled=True,lora_rank=16,lora_alpha=32,lora_dropout=.05,target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],gradient_checkpointing=True,trust_remote_code=False),dataset=DatasetConfig(name='data/train_sft_400.jsonl',task_type='chat_completion'),train=TrainingConfig(per_device_batch_size=batch,gradient_accumulation_steps=accumulation,max_steps=steps,learning_rate=1e-4,bf16=True,fp16=False,assistant_only_loss=True,gradient_checkpointing=True,eval_interval=10000,save_interval=10000,load_best_model_at_end=False),logging=LoggingConfig(output_dir=str(output),loggers=[],log_interval=1))


def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=('smoke','train'),required=True);p.add_argument('--output',default='output');p.add_argument('--batches',default='1,2,4,8,16,32');p.add_argument('--steps',type=int,default=5);p.add_argument('--batch-size',type=int,default=4);p.add_argument('--effective-batch',type=int,default=16);p.add_argument('--epochs',type=float,default=1.5);p.add_argument('--run-repo');p.add_argument('--run-prefix',default='sft');p.add_argument('--adapter-repo');p.add_argument('--merged-repo');args=p.parse_args()
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():raise RuntimeError('cloud BF16-capable GPU required')
    torch.manual_seed(42);torch.set_num_threads(8)
    token=os.getenv('HF_TOKEN')
    metadata={'model':MODEL,'revision':REVISION,'mode':args.mode,'gpu':torch.cuda.get_device_name(0),'gpu_memory_gib':torch.cuda.get_device_properties(0).total_memory/2**30,'dtype':'bfloat16','lora_rank':16,'lora_alpha':32,'lora_targets':['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],'max_length':1536,'loss':'assistant-only checkpointed sparse causal cross entropy','agenttune':'SFTTrainerBase lifecycle with project backend; upstream TRL SFT file absent','started_at':time.time()}
    try:
        tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=REVISION,token=token)
        if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
        source=load_training_rows();train_raw,val_raw=case_split(source)
        train=[encode_trajectory(r,tokenizer) for r in train_raw];validation=[encode_trajectory(r,tokenizer) for r in val_raw]
        metadata.update(training_examples=len(train),validation_examples=len(validation),train_case_ids=sorted({r['case_id'] for r in train}),validation_case_ids=sorted({r['case_id'] for r in validation}),max_actual_tokens=max(len(r['input_ids']) for r in train+validation),supervised_tokens=sum(sum(x!=-100 for x in r['labels']) for r in train),source_sha256=hashlib.sha256(Path('data/train_sft_400.jsonl').read_bytes()).hexdigest())
        (output/'run_metadata.json').write_text(json.dumps(metadata,indent=2));upload(output,args)
        base=AutoModelForCausalLM.from_pretrained(MODEL,revision=REVISION,token=token,torch_dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':'cuda:0'})
        base.config.use_cache=False;base.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
        model=get_peft_model(base,LoraConfig(r=16,lora_alpha=32,lora_dropout=.05,bias='none',task_type='CAUSAL_LM',target_modules=metadata['lora_targets']))
        model.print_trainable_parameters()
        metadata['trainable_parameters']=sum(p.numel() for p in model.parameters() if p.requires_grad)
        initial={n:p.detach().cpu().clone() for n,p in model.named_parameters() if p.requires_grad}
        if args.mode=='smoke':
            smoke=representative_smoke(train);results=[]
            for batch in map(int,args.batches.split(',')):
                for n,param in model.named_parameters():
                    if n in initial:param.data.copy_(initial[n].to(param.device))
                torch.manual_seed(42);model.zero_grad(set_to_none=True);gc.collect();torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats()
                trainer=None;result={'batch_size':batch,'steps':args.steps,'padded_length':1536,'gradient_accumulation':1}
                try:
                    # Repeat the same representative pool, not evaluation examples.
                    rows=(smoke*math.ceil(max(batch,16)/len(smoke)))
                    trainer=DriftGuardSFTTrainer(config_for(batch,args.steps,output/f'batch-{batch}'),model,tokenizer,rows,[],output/f'batch-{batch}')
                    trainer.train()
                    changed=sum(float((p.detach().cpu()-initial[n]).abs().sum()) for n,p in model.named_parameters() if n in initial)
                    if not changed>0:raise RuntimeError('adapter weights did not change')
                    timed=trainer.history[1:] or trainer.history
                    result.update(status='passed',mean_seconds_per_step=statistics.mean(r['seconds'] for r in timed),examples_per_second=batch*len(timed)/sum(r['seconds'] for r in timed),supervised_tokens_per_second=sum(r['supervised_tokens'] for r in timed)/sum(r['seconds'] for r in timed),first_loss=trainer.history[0]['loss'],last_loss=trainer.history[-1]['loss'],adapter_l1_change=changed)
                except torch.cuda.OutOfMemoryError:result.update(status='oom')
                finally:
                    result.update(peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30)
                    results.append(result);print(json.dumps({'event':'batch_smoke',**result}),flush=True)
                    del trainer;model.zero_grad(set_to_none=True);gc.collect();torch.cuda.empty_cache()
                    (output/'smoke_results.json').write_text(json.dumps(results,indent=2));upload(output,args)
                if result['status']=='oom':break
            safe=[r for r in results if r['status']=='passed' and r['peak_reserved_gib']<.85*metadata['gpu_memory_gib']]
            if not safe:raise RuntimeError('no safe batch passed')
            practical=[r for r in safe if r['batch_size']<=8] or safe
            chosen=max(practical,key=lambda r:r['examples_per_second'])
            recommendation={'recommended_microbatch':chosen['batch_size'],'effective_batch':max(16,chosen['batch_size']),'gradient_accumulation':max(1,math.ceil(16/chosen['batch_size'])),'largest_passed_batch':max(r['batch_size'] for r in results if r['status']=='passed'),'selection':'highest measured throughput among safe batches <=8, preserving optimizer update count on the small dataset','successful_batches':len(safe)}
            (output/'recommendation.json').write_text(json.dumps(recommendation,indent=2))
            metadata['status']='smoke_complete'
        else:
            accumulation=max(1,math.ceil(args.effective_batch/args.batch_size));steps=math.ceil(len(train)*args.epochs/(args.batch_size*accumulation))
            trainer=DriftGuardSFTTrainer(config_for(args.batch_size,steps,output,accumulation),model,tokenizer,train,validation,output,accumulation)
            before=trainer.evaluate();(output/'validation_before.json').write_text(json.dumps(before,indent=2))
            trainer.train();after=json.loads((output/'validation.json').read_text())
            adapter=output/'adapter';model.save_pretrained(adapter,safe_serialization=True);tokenizer.save_pretrained(adapter)
            metadata.update(status='training_complete',optimizer_steps=steps,gradient_accumulation=accumulation,microbatch=args.batch_size,effective_batch=args.batch_size*accumulation,samples_seen=trainer.samples_seen,validation_before=before,validation_after=after)
            model_card='---\nlicense: cc-by-nc-4.0\nbase_model: CohereLabs/tiny-aya-fire\npipeline_tag: text-generation\n---\n\n# DriftGuard Tiny Aya Fire SFT\n\nLoRA SFT of Cohere Labs Tiny Aya Fire using deterministic enterprise tool-use trajectories. This is an SFT checkpoint; GRPO has not been applied. Base revision: '+REVISION+'. Trained on 360 trajectories with 40 validation trajectories held out by semantic case. Training settings and validation losses are recorded in the run artifacts.\n'
            (adapter/'README.md').write_text(model_card)
            if args.adapter_repo:model.push_to_hub(args.adapter_repo,private=True,token=token);tokenizer.push_to_hub(args.adapter_repo,private=True,token=token)
            merged=model.merge_and_unload();merged.config.use_cache=True;merged.generation_config.use_cache=True
            merged_dir=output/'merged';merged.save_pretrained(merged_dir,safe_serialization=True,max_shard_size='4GB');tokenizer.save_pretrained(merged_dir)
            if args.merged_repo:merged.push_to_hub(args.merged_repo,private=True,token=token,max_shard_size='4GB');tokenizer.push_to_hub(args.merged_repo,private=True,token=token)
            if args.adapter_repo:
                from huggingface_hub import HfApi
                HfApi(token=token).upload_file(path_or_fileobj=str(adapter/'README.md'),path_in_repo='README.md',repo_id=args.adapter_repo)
            if args.merged_repo:
                from huggingface_hub import HfApi
                HfApi(token=token).upload_file(path_or_fileobj=model_card.encode(),path_in_repo='README.md',repo_id=args.merged_repo)
            metadata['adapter_repo']=args.adapter_repo;metadata['merged_repo']=args.merged_repo
        metadata['finished_at']=time.time();(output/'run_metadata.json').write_text(json.dumps(metadata,indent=2));upload(output,args)
        print(json.dumps({'event':'complete','mode':args.mode,'status':metadata['status']}),flush=True)
    except Exception as e:
        (output/'failure.json').write_text(json.dumps({'type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc()},indent=2));upload(output,args);raise
if __name__=='__main__':
    import sys
    if '--v2-1' in sys.argv:
        sys.argv.remove('--v2-1')
        from src_v2_1.cloud_job import main as v21_main
        v21_main()
    else:main()
