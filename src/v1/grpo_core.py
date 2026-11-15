"""Auditable GRPO math and train-only curriculum loading (no GPU required)."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
import torch
from torch.utils.checkpoint import checkpoint
from .sft_data import case_split,load_training_rows


def load_curriculum():
    expected={line.split('  ',1)[1]:line.split('  ',1)[0] for line in Path('data/SHA256SUMS').read_text().splitlines()}
    fit,val=case_split(load_training_rows());validation_cases={r['case_id'] for r in val}
    stages=[]
    for file in ('train_grpo_stage1.jsonl','train_grpo_stage2.jsonl'):
        raw=Path('data',file).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected[file]:raise ValueError('curriculum hash mismatch')
        rows=[json.loads(line) for line in raw.splitlines()]
        if any(r['world_split']!='train' or not r['case_id'].startswith('train-') for r in rows):raise ValueError('non-training row')
        stages.append([r for r in rows if r['case_id'] not in validation_cases])
    # Preserve the exact ten SFT-validation cases, with prompts generated from the same train world.
    from .oracle_solver import build_tasks
    world=json.loads(Path('data/world_train.json').read_text())
    validation=[r for r in build_tasks(world) if r['case_id'] in validation_cases]
    if len(validation)!=40:raise ValueError('expected forty grouped training-world validation tasks')
    if any(set(r['case_id'] for r in stage)&validation_cases for stage in stages):raise ValueError('validation leakage')
    return stages,validation,world


def group_advantages(rewards,group_size=4):
    if rewards.numel()%group_size:raise ValueError('incomplete GRPO group')
    grouped=rewards.reshape(-1,group_size)
    std=grouped.std(dim=1,unbiased=True)
    advantages=(grouped-grouped.mean(dim=1,keepdim=True))/(std[:,None]+1e-4)
    return advantages.reshape(-1),std


def token_logps(hidden,ids,mask,head,scale=1.,temperature=.8,chunk_size=64):
    """Exact sampled-token log probabilities; zero at context positions.

    hidden predicts the next token. Prompt/tool tokens remain visible in attention
    but are excluded from the loss. Checkpoint vocabulary chunks to limit memory.
    """
    valid=mask[:,1:].bool()
    h=hidden[:,:-1][valid];targets=ids[:,1:][valid]
    if not targets.numel():raise ValueError('no sampled tokens')
    def part(x,y):
        logits=(head(x)*scale).float()/temperature
        return logits.gather(1,y[:,None]).squeeze(1)-torch.logsumexp(logits,dim=-1)
    chunks=[]
    for i in range(0,len(targets),chunk_size):
        x=h[i:i+chunk_size];y=targets[i:i+chunk_size]
        chunks.append(checkpoint(part,x,y,use_reentrant=False) if torch.is_grad_enabled() else part(x,y))
    output=torch.zeros_like(mask[:,1:],dtype=torch.float32)
    return output.masked_scatter(valid,torch.cat(chunks))


def grpo_loss(logps,old,reference,mask,advantages,beta=.04,epsilon=.2):
    ratio=(logps-old).exp()
    unclipped=ratio*advantages[:,None]
    clipped=ratio.clamp(1-epsilon,1+epsilon)*advantages[:,None]
    delta=reference-logps
    kl=delta.exp()-delta-1
    loss=((-torch.minimum(unclipped,clipped)+beta*kl)*mask).sum(-1)/mask.sum(-1).clamp(min=1)
    return loss.mean(),(kl*mask).sum()/mask.sum().clamp(min=1),((ratio-1).abs()>epsilon).float().mul(mask).sum()/mask.sum().clamp(min=1)
