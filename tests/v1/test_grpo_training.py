import json
from pathlib import Path
import torch
from src.grpo_core import group_advantages,grpo_loss,token_logps,load_curriculum


def test_group_relative_advantages_and_zero_signal():
    rewards=torch.tensor([1.5,1.5,-.2,-.8,1.,1.,1.,1.])
    advantages,std=group_advantages(rewards)
    assert torch.allclose(advantages[:4].sum(),torch.tensor(0.),atol=1e-6)
    assert advantages[:2].min()>0 and advantages[2:4].max()<0
    assert std[1]==0 and torch.equal(advantages[4:],torch.zeros(4))


def test_sparse_policy_logps_and_gradients_match_dense():
    torch.manual_seed(7)
    h=torch.randn(2,9,8,requires_grad=True);head=torch.nn.Linear(8,17,bias=False)
    ids=torch.randint(0,17,(2,9));mask=torch.tensor([[0,0,1,1,0,0,1,1,1],[0,0,0,1,1,0,0,1,1]])
    actual=token_logps(h,ids,mask,head,scale=.7,temperature=.8,chunk_size=2)
    dense=torch.log_softmax(head(h[:,:-1])*.7/.8,-1).gather(-1,ids[:,1:,None]).squeeze(-1)*mask[:,1:]
    assert torch.allclose(actual,dense,atol=1e-6)
    a=torch.autograd.grad(actual.sum(),(h,head.weight),retain_graph=True)
    b=torch.autograd.grad(dense.sum(),(h,head.weight))
    for x,y in zip(a,b):assert torch.allclose(x,y,atol=1e-6)


def test_clipped_loss_masks_observations_and_kl_reference():
    lp=torch.tensor([[-1.,-2.,-3.]],requires_grad=True);old=lp.detach().clone();ref=old.clone();mask=torch.tensor([[1.,0.,1.]])
    loss,kl,clip=grpo_loss(lp,old,ref,mask,torch.tensor([1.]))
    assert loss.item()==-1 and kl.item()==0 and clip.item()==0
    loss.backward();assert lp.grad[0,1]==0 and lp.grad[0,0]<0
    changed=ref.clone();changed[0,0]+=.4
    _,kl,_=grpo_loss(lp.detach(),old,changed,mask,torch.tensor([0.]))
    assert kl>0


def test_curriculum_excludes_sft_validation_and_all_test_worlds():
    stages,validation,world=load_curriculum()
    assert world['split']=='train'
    cases={t['case_id'] for t in validation}
    assert len(validation)==40 and len(cases)==10
    for stage in stages:
        assert stage and not ({t['case_id'] for t in stage}&cases)
        assert all(t['world_split']=='train' for t in stage)


def test_live_rollout_preserves_sampled_ids_and_masks_tool_results():
    from transformers import AutoTokenizer
    from src.grpo_rollout import sample_episodes
    from src.oracle_solver import run_oracle
    from src.mcp_env import MCPEnv
    stages,_,world=load_curriculum();task=next(t for t in stages[0] if t['kind']=='conflict')
    tokenizer=AutoTokenizer.from_pretrained('checkpoints/v1/tiny-aya-fire-sft-adapter',local_files_only=True)
    with MCPEnv(world,task['active_mcps']) as env:oracle=run_oracle(task,env)
    turns=[m['content'] for m in oracle['messages'] if m['role']=='assistant']
    class Replay(torch.nn.Module):
        def __init__(self):
            super().__init__();self.anchor=torch.nn.Parameter(torch.zeros(1));self.config=type('Config',(),{'use_cache':False})();self.index=0;self.prefixes=[]
        def generate(self,input_ids,attention_mask,**kwargs):
            self.prefixes.append(input_ids[0].tolist())
            new=tokenizer.encode(turns[self.index],add_special_tokens=False);self.index+=1
            return torch.cat([input_ids,torch.tensor([new])],dim=1)
    model=Replay();result=sample_episodes([task],world,model,tokenizer)[0]
    assert result['reward']==1.5 and result['episode']['num_tool_calls']==2
    assert len(result['assistant_mask'])==len(result['input_ids'])
    expected=sum(len(tokenizer.encode(turn,add_special_tokens=False)) for turn in turns)
    assert sum(result['assistant_mask'])==expected
    for prefix in model.prefixes:assert result['input_ids'][:len(prefix)]==prefix
    text=tokenizer.decode([t for t,m in zip(result['input_ids'],result['assistant_mask']) if m])
    assert text==''.join(turns)


def test_paired_validation_preserves_cases_and_refuses_changed_cohorts():
    import pytest
    from src.analyze_grpo import paired_validation
    before=[dict(task_id=f'{case}-{lang}',case_id=case,language=lang,kind='conflict',exact_outcome=0) for case in ('a','b') for lang in ('en','hi')]
    after=[dict(row,exact_outcome=1) for row in before]
    result=paired_validation(before,after)
    assert result['change']==1 and result['change_ci95']==[1,1] and result['clusters']==2
    with pytest.raises(ValueError):paired_validation(before,after[:-1])
    with pytest.raises(ValueError):paired_validation(before,before+[before[0]])
