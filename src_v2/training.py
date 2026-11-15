"""Explicit v2 SFT and active-GRPO phases using real AgentTune lifecycles."""
import gc,json,math,time
from pathlib import Path
import torch
from peft import LoraConfig,PeftModel,get_peft_model
from datasets import Dataset
from trl import GRPOConfig
from agenttune.core.sft.config import SFTConfig,ModelConfig,DatasetConfig,TrainingConfig,LoggingConfig
from .backend import MODEL,REVISION,load_base
from .data import load,world,write_json
from .preflight import encode_sft
from .agenttune_sft_backend import DriftGuardSFTTrainer
from .agenttune_grpo_backend import DriftGuardAgentTuneGRPO,PersistentLogs
from .active_advantage import NoActiveAdvantage
TARGETS=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj']


def cleanup():gc.collect();torch.cuda.empty_cache()

def export_adapter(model,tokenizer,path,phase):
    path=Path(path);path.mkdir(parents=True,exist_ok=True)
    model.set_adapter('default');model.save_pretrained(path,selected_adapters=['default'],safe_serialization=True);tokenizer.save_pretrained(path)
    (path/'README.md').write_text('---\nlicense: cc-by-nc-4.0\nbase_model: CohereLabs/tiny-aya-fire\npipeline_tag: text-generation\n---\n\n# DriftGuard v2 '+phase+'\n\nTrained on approved immutable data_v2 artifacts. Base revision: '+REVISION+'. Model quality must be read from the paired v2 evaluation report, not training rewards.\n')
    return path


def run_sft(output,persist=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    model,tokenizer=load_base();encoded,val,preflight=encode_sft(tokenizer,output/'preflight.json')
    assert preflight['truncated_conversations']==0
    model.config.use_cache=False;model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
    model=get_peft_model(model,LoraConfig(r=16,lora_alpha=32,lora_dropout=.05,bias='none',task_type='CAUSAL_LM',target_modules=TARGETS))
    config=SFTConfig(model=ModelConfig(name_or_path=MODEL,precision='bf16',max_seq_length=2560,peft_enabled=True,lora_rank=16,lora_alpha=32,lora_dropout=.05,target_modules=TARGETS,gradient_checkpointing=True,trust_remote_code=False),dataset=DatasetConfig(name='data_v2/train_sft_240.jsonl',task_type='chat_completion'),train=TrainingConfig(per_device_batch_size=8,gradient_accumulation_steps=2,max_steps=15,learning_rate=1e-4,bf16=True,fp16=False,assistant_only_loss=True,gradient_checkpointing=True,eval_interval=10000,save_interval=10000,load_best_model_at_end=False),logging=LoggingConfig(output_dir=str(output),loggers=[],log_interval=1))
    trainer=DriftGuardSFTTrainer(config,model,tokenizer,encoded,val,output,accumulation=2)
    before=trainer.evaluate();trainer.train()
    assert trainer.samples_seen==240,'SFT must be exactly one untruncated epoch'
    adapter=export_adapter(model,tokenizer,output/'adapter','SFT')
    write_json(output/'metadata.json',dict(epochs=1,optimizer_steps=15,samples_seen=trainer.samples_seen,max_seq_length=2560,truncated_conversations=0,validation_loss_before=before,validation_loss_after=trainer.evaluate(),train_rows=240,validation_rows=80))
    if persist:persist()
    del trainer,model;cleanup();return adapter


def load_sft_policy(adapter):
    base,tokenizer=load_base();model=PeftModel.from_pretrained(base,str(adapter),is_trainable=True)
    model.load_adapter(str(adapter),adapter_name='reference',is_trainable=False);model.set_adapter('default')
    for module in model.modules():
        if isinstance(module,torch.nn.Dropout):module.p=0.
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});model.config.use_cache=False
    return model,tokenizer


def run_grpo(adapter,output,steps,persist=None,validate=None):
    """steps=(5,) for smoke; (120,220) for the fixed full curriculum."""
    output=Path(output);output.mkdir(parents=True,exist_ok=True);model,tokenizer=load_sft_policy(adapter);w=world()
    initial={n:p.detach().cpu().clone() for n,p in model.named_parameters() if p.requires_grad}
    reference={n:p.detach().cpu().clone() for n,p in model.named_parameters() if '.reference.' in n}
    torch.cuda.reset_peak_memory_stats();stages=[];early=None;started=time.time()
    try:
        for index,count in enumerate(steps):
            stage=output/f'stage{index+1}';stage.mkdir(parents=True,exist_ok=True)
            dataset=Dataset.from_list([{'prompt':t['prompt'],'task':t} for t in load('stage'+str(index+1))])
            config=GRPOConfig(output_dir=str(stage),max_steps=count,per_device_train_batch_size=4,gradient_accumulation_steps=1,num_generations=4,steps_per_generation=1,num_iterations=1,learning_rate=5e-6,lr_scheduler_type='constant',warmup_steps=0,beta=.04,epsilon=.2,temperature=.8,top_p=1.,top_k=0,max_completion_length=4096,max_prompt_length=None,bf16=True,fp16=False,gradient_checkpointing=True,gradient_checkpointing_kwargs={'use_reentrant':False},logging_steps=1,save_steps=10,save_total_limit=2,save_only_model=False,report_to=['tensorboard'],logging_dir=str(stage/'tensorboard'),remove_unused_columns=False,seed=20261112+index,data_seed=20261112+index,dataloader_num_workers=0,disable_tqdm=True,loss_type='grpo',max_grad_norm=1.)
            wrapper=DriftGuardAgentTuneGRPO(model=model,processing_class=tokenizer,train_dataset=dataset,output_dir=str(stage),dataset_name='data_v2/train_grpo_stage'+str(index+1)+'.jsonl',grpo_config=config,world=w,trace_dir=stage,callbacks=[PersistentLogs(stage,persist)])
            try:stats=wrapper.train()
            except NoActiveAdvantage as error:
                early=str(error);export_adapter(model,tokenizer,stage/'last_safe_adapter','GRPO early stop');write_json(stage/'early_stop.json',dict(reason=early,accepted_updates=wrapper.trainer.state.global_step));stats={'metrics':{}}
            actual=wrapper.trainer.state.global_step
            stages.append(dict(stage=index+1,requested_steps=count,completed_steps=actual,metrics=stats.get('metrics',{})))
            export_adapter(model,tokenizer,stage/'last_safe_adapter','GRPO intermediate')
            # Preserve sampler coverage/state alongside normal TRL checkpoint state.
            sampler=wrapper.trainer.active_sampler
            write_json(stage/'sampler_summary.json',dict(accepted=sampler.accepted,accepted_by_kind=sampler.accepted_by_kind,saturated=sorted(sampler.saturated),draws=sampler.draws))
            if persist:persist()
            if validate:validate(model,tokenizer,'after_stage'+str(index+1))
            model.zero_grad(set_to_none=True);del wrapper;cleanup()
            if early:break
        delta=sum(float((p.detach().cpu()-initial[n]).abs().sum()) for n,p in model.named_parameters() if n in initial)
        ref_delta=sum(float((p.detach().cpu()-reference[n]).abs().sum()) for n,p in model.named_parameters() if n in reference)
        if ref_delta!=0:raise RuntimeError('SFT reference weights changed')
        if not delta>0:raise RuntimeError('no GRPO policy weight change')
        groups=[json.loads(line) for file in output.glob('stage*/rollout_metrics.jsonl') for line in file.read_text().splitlines()]
        accepted=sum(not g.get('zero_variance_skipped',False) for g in groups)
        metadata=dict(attempted_groups=len(groups),active_groups=accepted,acceptance_rate=accepted/len(groups) if groups else 0.,data_dir='data_v2',stages=stages,status='early_stopped' if early else 'complete',early_stop=early,adapter_l1_change=delta,reference_l1_change=ref_delta,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,wall_seconds=time.time()-started,max_context_length=4096,max_new_tokens_per_turn=192,group_size=4,temperature=.8,retry_temperature=.95,beta=.04)
        adapter_path=export_adapter(model,tokenizer,output/'adapter','GRPO');write_json(output/'metadata.json',metadata)
        if persist:persist()
        return adapter_path,metadata
    except Exception:
        export_adapter(model,tokenizer,output/'emergency_adapter','GRPO interrupted')
        if persist:persist()
        raise
    finally:
        del model;cleanup()
