"""v2.1: four-epoch SFT and bounded, validation-selected anti-collapse GRPO."""
import gc,json,time,shutil
from pathlib import Path
import torch
from peft import LoraConfig,PeftModel,get_peft_model
from peft.utils.save_and_load import load_peft_weights,set_peft_model_state_dict
from safetensors.torch import load_file
from datasets import Dataset
from trl import GRPOConfig
from transformers import TrainerCallback
from agenttune.core.sft.config import SFTConfig,ModelConfig,DatasetConfig,TrainingConfig,LoggingConfig
from .backend import MODEL,REVISION,load_base
from .data import load,world,write_json
from .preflight import encode_sft
from .agenttune_sft_backend import DriftGuardSFTTrainer
from .agenttune_grpo_backend import DriftGuardAgentTuneGRPO,PersistentLogs
from .active_advantage import NoActiveAdvantage
from .evaluate_auditkit import evaluate
from .selection import ValidationSelector,warm_start_gate
TARGETS=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj']

def cleanup():gc.collect();torch.cuda.empty_cache()
def read_rows(path):return [json.loads(x) for x in Path(path).read_text().splitlines()]
def export_adapter(model,tokenizer,path,phase):
    path=Path(path);path.mkdir(parents=True,exist_ok=True);model.set_adapter('default');model.save_pretrained(path,selected_adapters=['default'],safe_serialization=True);tokenizer.save_pretrained(path)
    (path/'README.md').write_text('---\nlicense: cc-by-nc-4.0\nbase_model: CohereLabs/tiny-aya-fire\npipeline_tag: text-generation\n---\n\n# DriftGuard v2.1 '+phase+'\n\nPinned base revision '+REVISION+'. Frozen data_v2. Read validation selection and matched holdout metrics; no quality claim follows from training rewards alone.\n')
    return path

def run_sft(output,persist=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);model,tok=load_base();encoded,val,audit=encode_sft(tok,output/'preflight.json');assert audit['truncated_conversations']==0
    model.config.use_cache=False;model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
    model=get_peft_model(model,LoraConfig(r=16,lora_alpha=32,lora_dropout=.05,bias='none',task_type='CAUSAL_LM',target_modules=TARGETS))
    config=SFTConfig(model=ModelConfig(name_or_path=MODEL,precision='bf16',max_seq_length=2560,peft_enabled=True,lora_rank=16,lora_alpha=32,lora_dropout=.05,target_modules=TARGETS,gradient_checkpointing=True,trust_remote_code=False),dataset=DatasetConfig(name='data_v2/train_sft_240.jsonl',task_type='chat_completion'),train=TrainingConfig(epochs=4,per_device_batch_size=8,gradient_accumulation_steps=1,max_steps=120,learning_rate=1.5e-4,bf16=True,fp16=False,assistant_only_loss=True,gradient_checkpointing=True,eval_interval=10000,save_interval=10000,load_best_model_at_end=False),logging=LoggingConfig(output_dir=str(output),loggers=[],log_interval=1))
    validations=[];best={'accuracy':-1.,'step':None,'path':None}
    class EpochTrainer(DriftGuardSFTTrainer):
        def train_step(self,batch):
            metrics=super().train_step(batch);step=len(self.history)
            if step%30==0:
                self.model.zero_grad(set_to_none=True);folder=output/f'epoch{step//30}'
                candidate=export_adapter(self.model,self.tokenizer,folder/'adapter',f'SFT epoch {step//30}')
                result=evaluate(self.model,self.tokenizer,folder/'validation',splits=('validation',),persist=persist)['validation']
                accuracy=result['metrics']['exact_outcome']['estimate'];metrics_rows=read_rows(folder/'validation/validation_metrics.jsonl');abstain=sum(r['predicted_abstain'] for r in metrics_rows)/80
                event=dict(step=step,epoch=step//30,exact_outcome=accuracy,predicted_abstention_rate=abstain,adapter=str(candidate));validations.append(event)
                if accuracy>best['accuracy']:best.update(accuracy=accuracy,step=step,path=str(candidate))
                write_json(output/'selection.json',dict(best=best,validation=validations));print(json.dumps(dict(event='sft_epoch_validation',**event)),flush=True)
                self.model.train();self.model.config.use_cache=False
                if persist:persist()
            return metrics
    trainer=EpochTrainer(config,model,tok,encoded,val,output,accumulation=1);before=trainer.evaluate();trainer.train();assert trainer.samples_seen==960 and len(trainer.history)==120
    export_adapter(model,tok,output/'final_adapter','SFT final epoch 4');selected=output/'best_adapter';shutil.copytree(best['path'],selected,dirs_exist_ok=True)
    baseline=read_rows('reports_v2_1/prior_v2/sft/validation_metrics.jsonl');selected_rows=read_rows(output/f'epoch{best["step"]//30}/validation/validation_metrics.jsonl');gate=warm_start_gate(baseline,selected_rows);gate['selected_sft_abstention_rate']=sum(r['predicted_abstain'] for r in selected_rows)/len(selected_rows);gate['abstention_safe']=gate['selected_sft_abstention_rate']<=.40;gate['passed']=gate['passed'] and gate['abstention_safe']
    meta=dict(num_train_epochs=4,optimizer_steps=120,effective_batch_size=8,learning_rate=1.5e-4,schedule='cosine with six-step warmup',samples_seen=960,max_seq_length=2560,truncated_conversations=0,selected_step=best['step'],selected_validation_accuracy=best['accuracy'],validation=validations,warm_start_gate=gate,validation_loss_before=before)
    write_json(output/'metadata.json',meta)
    if persist:persist()
    del trainer,model;cleanup();return selected,meta

def load_sft_policy(adapter):
    base,tok=load_base();model=PeftModel.from_pretrained(base,str(adapter),is_trainable=True);model.load_adapter(str(adapter),adapter_name='reference',is_trainable=False);model.set_adapter('default')
    for module in model.modules():
        if isinstance(module,torch.nn.Dropout):module.p=0.
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});model.config.use_cache=False;return model,tok

def run_grpo(adapter,output,sft_meta,persist=None,group_size=4,temperature=.8,retry_temperature=.95):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);model,tok=load_sft_policy(adapter);w=world();initial={n:p.detach().cpu().clone() for n,p in model.named_parameters() if p.requires_grad};reference={n:p.detach().cpu().clone() for n,p in model.named_parameters() if '.reference.' in n}
    best_path=export_adapter(model,tok,output/'best_val_adapter','GRPO selection baseline: SFT, zero GRPO updates');selector=ValidationSelector(sft_meta['selected_validation_accuracy'],best_path);stages=[];started=time.time();total=0;early=None;torch.cuda.reset_peak_memory_stats()
    class ValidatePolicy(TrainerCallback):
        def on_step_end(self,args,state,control,**kwargs):
            step=total+state.global_step
            if step%30:return
            model.zero_grad(set_to_none=True);candidate=export_adapter(model,tok,output/f'validation_checkpoints/step_{step:03d}','GRPO validation candidate')
            folder=output/f'validation/step_{step:03d}';result=evaluate(model,tok,folder,splits=('validation',),persist=persist)['validation'];rr=read_rows(folder/'validation_metrics.jsonl');rate=sum(r['predicted_abstain'] for r in rr)/len(rr)
            event=selector.consider(step,result['metrics']['exact_outcome']['estimate'],rate,candidate)
            if event['selected']:shutil.copytree(candidate,best_path,dirs_exist_ok=True);selector.best_path=str(best_path)
            write_json(output/'validation_history.json',selector.history);print(json.dumps(dict(event='grpo_validation',**event)),flush=True)
            if event['early_stop']:control.should_training_stop=True
            model.train();model.config.use_cache=False
            if persist:persist()
    try:
        for index in range(2):
            stage=output/f'stage{index+1}';stage.mkdir(parents=True,exist_ok=True);dataset=Dataset.from_list([{'prompt':t['prompt'],'task':t} for t in load('stage'+str(index+1))])
            config=GRPOConfig(output_dir=str(stage),max_steps=60,per_device_train_batch_size=group_size,gradient_accumulation_steps=1,num_generations=group_size,steps_per_generation=1,num_iterations=1,learning_rate=5e-6,lr_scheduler_type='constant',warmup_steps=0,beta=.05,epsilon=.2,temperature=temperature,top_p=1.,top_k=0,max_completion_length=4096,max_prompt_length=None,bf16=True,fp16=False,gradient_checkpointing=True,gradient_checkpointing_kwargs={'use_reentrant':False},logging_steps=1,save_steps=10,save_total_limit=2,save_only_model=False,report_to=['tensorboard'],logging_dir=str(stage/'tensorboard'),remove_unused_columns=False,seed=20261113+index,data_seed=20261113+index,dataloader_num_workers=0,disable_tqdm=True,loss_type='grpo',max_grad_norm=1.)
            config.recipe_cycle_offset=total;config.recipe_retry_temperature=retry_temperature
            wrapper=DriftGuardAgentTuneGRPO(model=model,processing_class=tok,train_dataset=dataset,output_dir=str(stage),dataset_name='data_v2/train_grpo_stage'+str(index+1)+'.jsonl',grpo_config=config,world=w,trace_dir=stage,callbacks=[ValidatePolicy(),PersistentLogs(stage,persist)])
            try:stats=wrapper.train()
            except NoActiveAdvantage as error:early='no_positive_anchor: '+str(error);stats={'metrics':{}}
            actual=wrapper.trainer.state.global_step;total+=actual;sampler=wrapper.trainer.active_sampler
            write_json(stage/'sampler_summary.json',dict(accepted=sampler.accepted,accepted_by_kind=sampler.accepted_by_kind,draws=sampler.draws,fallbacks=sampler.fallbacks,cycle_offset=sampler.offset))
            stages.append(dict(stage=index+1,requested_steps=60,completed_steps=actual,metrics=stats.get('metrics',{})));export_adapter(model,tok,stage/'last_adapter','GRPO stage end')
            if selector.stop:early='validation_abstention_rate_exceeded_40_percent'
            if persist:persist()
            model.zero_grad(set_to_none=True);del wrapper;cleanup()
            if early:break
        final=export_adapter(model,tok,output/'final_adapter','GRPO final policy before validation restoration');delta=sum(float((p.detach().cpu()-initial[n]).abs().sum()) for n,p in model.named_parameters() if n in initial);ref_delta=sum(float((p.detach().cpu()-reference[n]).abs().sum()) for n,p in model.named_parameters() if n in reference)
        if ref_delta!=0:raise RuntimeError('SFT reference changed')
        if total and not delta>0:raise RuntimeError('No GRPO weight change')
        set_peft_model_state_dict(model,load_peft_weights(str(best_path),device='cpu'),adapter_name='default');restored=export_adapter(model,tok,output/'restored_best_adapter','GRPO validation-selected deployment policy')
        a=load_file(str(best_path/'adapter_model.safetensors'));b=load_file(str(restored/'adapter_model.safetensors'));assert a.keys()==b.keys() and all(torch.equal(a[k],b[k]) for k in a),'Best-val restoration mismatch'
        groups=[r for p in output.glob('stage*/rollout_metrics.jsonl') for r in read_rows(p)];active=[r for r in groups if r['optimizer_update_eligible']]
        assert len(active)==total and all(r['reward_std']>1e-6 and (r['kind']=='abstain' or r['max_reward']>0) for r in active)
        meta=dict(status='early_stopped' if early else 'complete',early_stop=early,stages=stages,completed_updates=total,requested_updates=120,selected_step=selector.best_step,selected_validation_accuracy=selector.best_accuracy,validation=selector.history,attempted_groups=len(groups),active_groups=len(active),all_negative_skipped=sum(r.get('all_negative_skipped',False) for r in groups),reference_l1_change=ref_delta,adapter_l1_change=delta,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,wall_seconds=time.time()-started,beta=.05,learning_rate=5e-6,group_size=group_size,temperature=temperature,retry_temperature=retry_temperature,max_context_length=4096,max_new_tokens_per_turn=192,cycle=list(sampler.cycle),restored_best_weights_verified=True)
        write_json(output/'metadata.json',meta)
        if persist:persist()
        return best_path,final,meta
    except Exception:
        export_adapter(model,tok,output/'emergency_adapter','GRPO interrupted');
        if persist:persist()
        raise
    finally:del model;cleanup()
