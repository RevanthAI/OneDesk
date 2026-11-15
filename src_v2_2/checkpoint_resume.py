"""Restore a saved Stage-1 optimizer checkpoint without recounting abandoned work."""
from collections import Counter
import hashlib,json,shutil
from pathlib import Path
from .data import write_json


def restore_sampler(sampler,state):
    if state['offset']!=sampler.offset:raise ValueError('Sampler cycle offset changed')
    sampler.accepted=state['accepted'];sampler.accepted_by_kind=state['accepted_by_kind'];sampler.draws=state['draws'];sampler.fallbacks=state['fallbacks']


def prepare_partial(source,output,sft_accuracy,step,warmup):
    source=Path(source);output=Path(output);checkpoint=source/f'stage1/checkpoint-{step}'
    state=json.loads((checkpoint/'trainer_state.json').read_text())
    if state['global_step']!=step or not 0<step<40:raise ValueError('Invalid Stage-1 checkpoint step')
    required=('optimizer.pt','scheduler.pt','rng_state.pth','adapter_model.safetensors','adapter_config.json')
    if any(not (checkpoint/name).is_file() for name in required):raise ValueError('Incomplete optimizer/scheduler/RNG checkpoint')
    all_history=json.loads((source/'validation_history.json').read_text())
    if any(h['early_stop'] or not h['safe'] for h in all_history):raise ValueError('Cannot bypass a validation collapse stop')
    history=[h for h in all_history if h['step']<=step]
    if not history:raise ValueError('A validated checkpoint is required')
    best=history[-1]
    if best['best_accuracy']<sft_accuracy:raise ValueError('Lost SFT fallback')
    rows=[json.loads(l) for l in (source/'stage1/rollout_metrics.jsonl').read_text().splitlines()]
    rows=[r for r in rows if r['step']<step];active=[r for r in rows if r['optimizer_update_eligible']]
    if len(active)!=step or any(r['reward_std']<=1e-6 or (r['kind']!='abstain' and r['max_reward']<=0) for r in active):raise ValueError('Checkpoint and accepted-update journal differ')
    output.mkdir(parents=True,exist_ok=True);stage=output/'stage1';stage.mkdir(exist_ok=True)
    shutil.copytree(checkpoint,stage/checkpoint.name,dirs_exist_ok=True)
    smoke=json.loads((source/'stage1/smoke_gate.json').read_text())
    if not smoke['passed']:raise ValueError('Cannot bypass failed smoke gate')
    shutil.copy2(source/'stage1/smoke_gate.json',stage/'smoke_gate.json')
    def save_rows(name,rr):(stage/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr))
    save_rows('rollout_metrics.jsonl',rows)
    raw=[json.loads(l) for l in (source/'stage1/rollouts.jsonl').read_text().splitlines()]
    save_rows('rollouts.jsonl',[r for r in raw if r['step']<step])
    logs=[json.loads(l) for l in (source/'stage1/optimizer_log.jsonl').read_text().splitlines()]
    logs=[r for r in logs if r['step']<=step and 'grad_norm' in r];save_rows('optimizer_log.jsonl',logs)
    for event in history:
        name='step_%03d'%event['step'];shutil.copytree(source/'validation'/name,output/'validation'/name,dirs_exist_ok=True)
    if best['best_step']==0:best_source=Path(warmup)
    elif all_history[-1]['best_step']==best['best_step']:best_source=source/'best_val_adapter'
    else:best_source=source/('validation_checkpoints/step_%03d'%best['best_step'])
    shutil.copytree(best_source,output/'best_val_adapter',dirs_exist_ok=True);write_json(output/'validation_history.json',history)
    kinds=('conflict','incident','consistent','abstain')
    restore=dict(offset=0,accepted=step,accepted_by_kind={k:sum(r['kind']==k for r in active) for k in kinds},draws={k:sum(r['kind']==k for r in rows) for k in kinds},fallbacks=sum(bool(r.get('kind_saturated_fallback')) for r in active),rollout_batch=max(r['rollout_batch'] for r in rows))
    write_json(stage/'sampler_restore.json',restore)
    # Reconstruct only the retained prefix of TensorBoard from its raw JSON log.
    from torch.utils.tensorboard import SummaryWriter
    with SummaryWriter(str(stage/'tensorboard')) as writer:
        for r in logs:
            for k,v in r.items():
                if k not in ('step','wall_time') and isinstance(v,(int,float)):writer.add_scalar(k,v,r['step'])
    receipt=dict(starting_update=step,best_step=best['best_step'],best_accuracy=best['best_accuracy'],history=history,checkpoint=str(stage/checkpoint.name),policy_sha256=hashlib.sha256((checkpoint/'adapter_model.safetensors').read_bytes()).hexdigest(),optimizer='Restored Stage-1 optimizer, scheduler and RNG through AgentTune/TRL resume_from_checkpoint; sampler draw counters reconstructed from the exact retained journal prefix',discarded_later_active_updates=sum(r['optimizer_update_eligible'] for r in [json.loads(l) for l in (source/'stage1/rollout_metrics.jsonl').read_text().splitlines()] if r['step']>=step))
    write_json(output/'CHECKPOINT_RESUME.json',receipt);return receipt
