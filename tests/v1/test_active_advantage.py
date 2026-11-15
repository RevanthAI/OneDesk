from collections import Counter
import pytest
from src.active_advantage import BalancedActiveSampler,NoActiveAdvantage

def tasks():return [dict(task_id=f'{kind}-{lang}',kind=kind,language=lang) for kind in BalancedActiveSampler.kinds for lang in ('en','hi','hinglish','te')]

def test_active_sampler_skips_zero_signal_and_balances_counted_kinds():
    sampler=BalancedActiveSampler(tasks());events=[];calls=Counter();accepted=[]
    def sample(group):
        kind=group[0]['kind'];calls[kind]+=1
        return [{'reward':1.0} for _ in group] if calls[kind]%2 else [{'reward':float(i%2)} for i in range(len(group))]
    for _ in range(8):
        group,outputs,event=sampler.next_active(sample,group_size=6,on_attempt=lambda t,g,e:events.append(e))
        accepted.append(group[0]['kind']);assert event['reward_std']>0 and not event['zero_variance_skipped']
    assert Counter(accepted)==dict.fromkeys(sampler.kinds,2)
    assert len(events)==16 and sum(e['zero_variance_skipped'] for e in events)==8

def test_active_sampler_cannot_turn_solved_groups_into_fake_updates():
    sampler=BalancedActiveSampler(tasks());events=[]
    with pytest.raises(NoActiveAdvantage):sampler.next_active(lambda ts:[{'reward':1.5} for t in ts],max_attempts=3,on_attempt=lambda t,g,e:events.append(e))
    assert sampler.accepted==0 and len(events)==12 and all(e['zero_variance_skipped'] for e in events)


def test_v2_backend_logs_skips_and_returns_only_active_groups(tmp_path,monkeypatch):
    import contextlib,json
    from collections import defaultdict
    from types import SimpleNamespace
    import torch
    import src.agenttune_grpo_backend as backend
    trainer=backend.MCPGRPOTrainer.__new__(backend.MCPGRPOTrainer)
    task_rows=[dict(t,case_id=t['task_id'],gold_value=1,expected_status='answered',gold_cites=['DOC'],stale_doc_id=None) for t in tasks()]
    trainer.world={'schema_version':2};trainer.trace_dir=tmp_path;trainer.rollout_batch=0
    trainer.active_sampler=BalancedActiveSampler(task_rows);trainer.num_generations=4;trainer.temperature=.8
    trainer.state=SimpleNamespace(global_step=0,num_input_tokens_seen=0)
    trainer.model=SimpleNamespace(set_adapter=lambda name:None)
    trainer.accelerator=SimpleNamespace(device=torch.device('cpu'),unwrap_model=lambda model:model,autocast=contextlib.nullcontext)
    trainer.processing_class=SimpleNamespace(pad_token_id=0);trainer._metrics={'train':defaultdict(list)}
    trainer.logps=lambda model,ids,attention,mask,**kwargs:torch.zeros((len(ids),ids.shape[1]-1))
    monkeypatch.setattr(torch.cuda,'max_memory_reserved',lambda:0)
    attempts=[]
    def sample(candidates,*args,**kwargs):
        attempts.append(candidates);out=[]
        for i,t in enumerate(candidates):
            correct=len(attempts)==1 or i<2
            episode=dict(prediction=dict(status='answered',value=1 if correct else 0,cites=['DOC'],stale_source=None),retrieved_ids=['DOC'],num_tool_calls=0,calls=[],messages=[],raw_turns=[],completion_reason='final_answer')
            out.append(dict(reward=1.3 if correct else -.2,specified_reward=1.3 if correct else .05,input_ids=[1,2,3],assistant_mask=[0,1,1],episode=episode))
        return out
    monkeypatch.setattr(backend,'sample_episodes',sample)
    result=trainer._generate_and_score_completions([{'task':task_rows[0]}]*4)
    logged=[json.loads(line) for line in (tmp_path/'rollout_metrics.jsonl').read_text().splitlines()]
    assert len(attempts)==2 and trainer.state.global_step==0
    assert [r['zero_variance_skipped'] for r in logged]==[True,False]
    assert [r['optimizer_update_eligible'] for r in logged]==[False,True]
    assert result['advantages'].abs().sum()>0


def test_temperature_ramp_and_saturated_kind_fallback():
    sampler=BalancedActiveSampler(tasks());events=[];temperatures=[]
    def sample(group,temperature):
        temperatures.append((group[0]['kind'],temperature))
        return [{'reward':1.3} for _ in group] if group[0]['kind']=='consistent' else [{'reward':float(i%2)} for i in range(len(group))]
    group,_,event=sampler.next_active(sample,on_attempt=lambda t,g,e:events.append(e))
    assert group[0]['kind']=='incident' and sampler.accepted==1
    assert [t for k,t in temperatures if k=='consistent']==[.8]*16+[.95]*16
    assert 'consistent' in sampler.saturated and any(e['kind_saturated_fallback'] for e in events)
    assert event['reward_std']>0
