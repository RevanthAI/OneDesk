import torch
from torch.utils.checkpoint import checkpoint

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
