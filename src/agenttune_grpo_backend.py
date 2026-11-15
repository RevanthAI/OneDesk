"""Actual AgentTune GRPO lifecycle + TRL 0.23 compatibility for live MCP episodes.

Pinned AgentTune expects GRPOTrainer._generate_single_turn, absent in TRL 0.23.
Load the upstream dependency-free wrapper leaf (avoid its eager agentic extras),
subclass its setup hook, and retain upstream train/data/save/stats lifecycle.
TRL owns sampling order, optimization, clipping of gradients, scheduling,
callbacks, TensorBoard, checkpoints. Project supplies live masked rollouts and
exact sparse-vocabulary GRPO loss, tested independently against dense math.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
from trl import GRPOTrainer
from transformers import TrainerCallback
from .grpo_core import token_logps,group_advantages,grpo_loss
from .grpo_rollout import sample_episodes
from .reward import outcome_ok,citation_f1


def upstream_wrapper():
    import agenttune
    path=Path(agenttune.__file__).parent/'backends/trl/agentic/grpo/agentic_grpo.py'
    spec=importlib.util.spec_from_file_location('_driftguard_upstream_grpo',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.TrlAgenticGrpo


def append(path,value):
    with Path(path).open('a') as f:f.write(json.dumps(value,ensure_ascii=False,allow_nan=False)+'\n')


class PersistentLogs(TrainerCallback):
    def __init__(self,output,persist=None):self.output=Path(output);self.persist=persist
    def on_log(self,args,state,control,logs=None,**kwargs):
        if logs:append(self.output/'optimizer_log.jsonl',dict(step=state.global_step,wall_time=time.time(),**logs))
    def on_step_end(self,args,state,control,**kwargs):
        if state.global_step%5==0 and self.persist:self.persist()


class MCPGRPOTrainer(GRPOTrainer):
    def __init__(self,*args,world,trace_dir,**kwargs):
        self.world=world;self.trace_dir=Path(trace_dir);self.trace_dir.mkdir(parents=True,exist_ok=True);self.rollout_batch=0
        super().__init__(*args,**kwargs)
        # TRL's PEFT reference fallback disables adapters (base policy). We instead
        # explicitly score a frozen copy of the trained SFT adapter named reference.
        if self.accelerator.num_processes!=1:raise ValueError('this audited compatibility backend supports one GPU only')
        self.active_sampler=None
        if self.world.get('schema_version')==2:
            from .active_advantage import BalancedActiveSampler
            self.active_sampler=BalancedActiveSampler([r['task'] for r in self.train_dataset],seed=self.args.seed)
    def logps(self,model,ids,attention,mask,temperature=None):
        unwrapped=self.accelerator.unwrap_model(model)
        causal=unwrapped.get_base_model()
        # Calling the decoder directly bypasses Accelerate's outer-model
        # autocast wrapper. Keep old/reference/update passes in identical BF16.
        with torch.autocast(device_type=ids.device.type,dtype=torch.bfloat16,enabled=ids.device.type=='cuda'):
            hidden=causal.model(input_ids=ids,attention_mask=attention,use_cache=False).last_hidden_state
            return token_logps(hidden,ids,mask,causal.get_output_embeddings(),float(causal.logit_scale),self.temperature if temperature is None else temperature)
    def _generate_and_score_completions(self,inputs):
        start=time.perf_counter();tasks=[row['task'] for row in inputs]
        if len(tasks)%self.num_generations:raise ValueError('partial group')
        for offset in range(0,len(tasks),self.num_generations):
            if len({t['task_id'] for t in tasks[offset:offset+self.num_generations]})!=1:raise ValueError('GRPO group mixes prompts')
        model=self.accelerator.unwrap_model(self.model)
        sampling_temperature=self.temperature
        if self.active_sampler is None:
            sampled=sample_episodes(tasks,self.world,model,self.processing_class,temperature=self.temperature,max_new_tokens=192)
        else:
            if len(tasks)!=self.num_generations:raise ValueError('v2 active GRPO requires one prompt group per optimizer microbatch')
            def sample_group(candidates,temperature=.8):return sample_episodes(candidates,self.world,model,self.processing_class,temperature=temperature,max_new_tokens=192,max_context=4096)
            def log_attempt(task,group,event):
                if not event['zero_variance_skipped']:return
                self.rollout_batch+=1;episodes=[r['episode'] for r in group]
                metrics=dict(step=self.state.global_step,rollout_batch=self.rollout_batch,wall_time=time.time(),mean_reward=sum(r['reward'] for r in group)/len(group),mean_specified_reward=sum(r['specified_reward'] for r in group)/len(group),reward_std=event['reward_std'],zero_variance_fraction=1.,exact_outcome=sum(outcome_ok(e.get('prediction'),task) for e in episodes)/len(group),verified_citation_f1=sum(citation_f1(e.get('prediction') or {},task,e['retrieved_ids']) for e in episodes)/len(group),format_valid=sum(e['prediction'] is not None for e in episodes)/len(group),mean_tool_calls=sum(e['num_tool_calls'] for e in episodes)/len(group),sampled_tokens=sum(sum(r['assistant_mask']) for r in group),seconds=time.perf_counter()-start,peak_vram_reserved_gib=torch.cuda.max_memory_reserved()/2**30,zero_variance_skipped=True,optimizer_update_eligible=False,sampling_temperature=event['sampling_temperature'],kind_saturated_fallback=event['kind_saturated_fallback'])
                append(self.trace_dir/'rollout_metrics.jsonl',metrics)
                for i,r in enumerate(group):append(self.trace_dir/'rollouts.jsonl',dict(step=self.state.global_step,rollout_batch=self.rollout_batch,sample=i,group=0,task_id=task['task_id'],case_id=task['case_id'],language=task['language'],kind=task['kind'],reward=r['reward'],specified_reward=r['specified_reward'],advantage=0.,sampled_tokens=sum(r['assistant_mask']),input_ids=r['input_ids'],assistant_mask=r['assistant_mask'],episode=r['episode'],zero_variance_skipped=True))
                print(json.dumps({'event':'zero_variance_skipped',**metrics}),flush=True)
            tasks,sampled,active_event=self.active_sampler.next_active(sample_group,group_size=self.num_generations,on_attempt=log_attempt)
            sampling_temperature=active_event['sampling_temperature']
        width=max(len(r['input_ids']) for r in sampled);device=self.accelerator.device
        ids=torch.tensor([r['input_ids']+[self.processing_class.pad_token_id]*(width-len(r['input_ids'])) for r in sampled],device=device)
        mask=torch.tensor([r['assistant_mask']+[0]*(width-len(r['assistant_mask'])) for r in sampled],device=device)
        attention=torch.tensor([[1]*len(r['input_ids'])+[0]*(width-len(r['input_ids'])) for r in sampled],device=device)
        old=[];reference=[]
        with torch.no_grad(),self.accelerator.autocast():
            for i in range(len(sampled)):old.append(self.logps(model,ids[i:i+1],attention[i:i+1],mask[i:i+1],temperature=sampling_temperature))
            model.set_adapter('reference')
            try:
                for i in range(len(sampled)):reference.append(self.logps(model,ids[i:i+1],attention[i:i+1],mask[i:i+1],temperature=sampling_temperature))
            finally:model.set_adapter('default')
        rewards=torch.tensor([r['reward'] for r in sampled],device=device,dtype=torch.float32)
        advantages,std=group_advantages(rewards,self.num_generations)
        self.rollout_batch+=1;episodes=[r['episode'] for r in sampled]
        metrics=dict(step=self.state.global_step,rollout_batch=self.rollout_batch,wall_time=time.time(),mean_reward=float(rewards.mean()),mean_specified_reward=sum(r['specified_reward'] for r in sampled)/len(sampled),reward_std=float(std.mean()),zero_variance_fraction=float((std<1e-8).float().mean()),exact_outcome=sum(outcome_ok(e.get('prediction'),t) for e,t in zip(episodes,tasks))/len(tasks),verified_citation_f1=sum(citation_f1(e.get('prediction') or {},t,e['retrieved_ids']) for e,t in zip(episodes,tasks))/len(tasks),format_valid=sum(e['prediction'] is not None for e in episodes)/len(tasks),mean_tool_calls=sum(e['num_tool_calls'] for e in episodes)/len(tasks),sampled_tokens=int(mask.sum()),seconds=time.perf_counter()-start,peak_vram_reserved_gib=torch.cuda.max_memory_reserved()/2**30,zero_variance_skipped=False,optimizer_update_eligible=True,sampling_temperature=sampling_temperature,kind_saturated_fallback=bool(self.active_sampler and active_event['kind_saturated_fallback']))
        append(self.trace_dir/'rollout_metrics.jsonl',metrics)
        for i,(t,r) in enumerate(zip(tasks,sampled)):
            append(self.trace_dir/'rollouts.jsonl',dict(step=self.state.global_step,rollout_batch=self.rollout_batch,sample=i,group=i//self.num_generations,task_id=t['task_id'],case_id=t['case_id'],language=t['language'],kind=t['kind'],reward=r['reward'],specified_reward=r['specified_reward'],advantage=float(advantages[i]),sampled_tokens=sum(r['assistant_mask']),input_ids=r['input_ids'],assistant_mask=r['assistant_mask'],episode=r['episode']))
        for key in ('mean_reward','reward_std','zero_variance_fraction','exact_outcome','verified_citation_f1','format_valid','mean_tool_calls'):
            self._metrics['train'][key].append(metrics[key])
        self.state.num_input_tokens_seen+=int(attention.sum())
        print(json.dumps({'event':'grpo_rollout',**metrics}),flush=True)
        return dict(input_ids=ids,attention_mask=attention,assistant_mask=mask,old_logps=torch.cat(old),reference_logps=torch.cat(reference),advantages=advantages,temperatures=torch.full((len(sampled),),sampling_temperature,device=device))
    def _compute_loss(self,model,inputs):
        # Score rows individually to bound activation/vocabulary memory. Prompt
        # and tool-result tokens attend normally but never receive policy loss.
        losses=[];kls=[];clips=[]
        for i in range(len(inputs['input_ids'])):
            ids=inputs['input_ids'][i:i+1];attention=inputs['attention_mask'][i:i+1];mask=inputs['assistant_mask'][i:i+1]
            lp=self.logps(model,ids,attention,mask,temperature=float(inputs['temperatures'][i]) if 'temperatures' in inputs else self.temperature)
            loss,kl,clip=grpo_loss(lp,inputs['old_logps'][i:i+1],inputs['reference_logps'][i:i+1],mask[:,1:],inputs['advantages'][i:i+1],beta=self.beta,epsilon=self.epsilon_low)
            if not torch.isfinite(loss):raise FloatingPointError('non-finite GRPO loss')
            losses.append(loss);kls.append(float(kl.detach()));clips.append(float(clip.detach()))
        self._metrics['train']['kl'].append(sum(kls)/len(kls));self._metrics['train']['clip_fraction'].append(sum(clips)/len(clips))
        return torch.stack(losses).mean()/self.current_gradient_accumulation_steps


class DriftGuardAgentTuneGRPO(upstream_wrapper()):
    def __init__(self,*,grpo_config,world,trace_dir,callbacks=None,**kwargs):
        super().__init__(**kwargs)
        self.grpo_config=grpo_config;self.world=world;self.trace_dir=trace_dir;self.callbacks=callbacks or [];self._agentic_mode=True
    def setup_trainer(self):
        def episode_reward(prompts,completions,**kwargs):
            raise RuntimeError('Live rollout backend must score full episodes; single-turn reward path is forbidden')
        self.trainer=MCPGRPOTrainer(model=self.kwargs['model'],reward_funcs=episode_reward,args=self.grpo_config,train_dataset=self.train_dataset,processing_class=self.kwargs['processing_class'],world=self.world,trace_dir=self.trace_dir,callbacks=self.callbacks)
