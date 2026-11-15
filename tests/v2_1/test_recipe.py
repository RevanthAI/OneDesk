from src.layout import relocated_path
import copy,json,statistics
from collections import Counter
from pathlib import Path
import pytest
from src_v2_1.data import load,world
from src_v2_1.mcp_env import MCPEnv
from src_v2_1.oracle_solver import run_oracle
from src_v2_1.mcp_adapter import wrap
from src_v2_1.reward import score_episode,required_servers
from src_v2_1.active_advantage import PositiveAnchorSampler,NoActiveAdvantage
from src_v2_1.selection import ValidationSelector,warm_start_gate


def final(pred,calls=(),ids=()):return dict(prediction=pred,final_text=wrap('final_answer',pred),calls=list(calls),retrieved_ids=list(ids),num_tool_calls=len(calls))
def abstain():return final(dict(status='abstain',value=None,cites=[],stale_source=None))
def conflict():return next(t for t in load('sft') if t['kind']=='conflict' and len(required_servers(t))==2 and len(t['gold_cites'])==2)

def test_anti_collapse_always_abstain_holdout_mix():
    tasks=load('test_synth');average=statistics.mean(score_episode(t,abstain(),'anti_collapse') for t in tasks)
    assert average==pytest.approx(-.5725) and average<-.50
    balanced=statistics.mean(score_episode(t,abstain(),'anti_collapse') for t in load('validation'))
    assert balanced==pytest.approx(-.3875)

def test_dense_bridge_beats_lazy_stale_and_false_abstention():
    t=conflict()
    with MCPEnv(world(),t['active_mcps']) as env:honest=run_oracle(t,env)
    p=dict(status=t['expected_status'],value=999999,cites=t['gold_cites'],stale_source=t['stale_doc_id'])
    bridge=final(p,honest['calls'],honest['retrieved_ids']);assert score_episode(t,bridge,'anti_collapse')==pytest.approx(.30)
    with MCPEnv(world(),t['active_mcps']) as env:
        env.call('notion-mcp','search_notion',{'query':t['service_name']+' '+t['param_name']})
        p.update(value=t['stale_trap_value']);lazy=final(p,env.calls,env.retrieved_ids)
    assert score_episode(t,lazy,'anti_collapse')==pytest.approx(-.20)
    full_stale=final(p,honest['calls'],honest['retrieved_ids']);assert score_episode(t,full_stale,'anti_collapse')==pytest.approx(.05)
    assert score_episode(t,abstain(),'anti_collapse')==-.85
    assert score_episode(t,bridge,'anti_collapse')>score_episode(t,lazy,'anti_collapse')>score_episode(t,abstain(),'anti_collapse')

@pytest.mark.parametrize('kind',['consistent','incident','conflict','abstain'])
def test_old_modes_unchanged_and_success_gate_preserved(kind):
    import src.reward as legacy
    import src_v2.reward as frozen_v2
    t=next(t for t in load('sft') if t['kind']==kind)
    with MCPEnv(world(),t['active_mcps']) as env:e=run_oracle(t,env)
    for mode in ('specified','evidence_gated'):assert legacy.score_episode(t,e,mode)==frozen_v2.score_episode(t,e,mode)==score_episode(t,e,mode)
    assert score_episode(t,e,'anti_collapse')==score_episode(t,e,'evidence_gated')

@pytest.mark.parametrize('subtype',['sla_penalty','payload_lb','payload_mib'])
def test_correct_calculation_still_requires_utilities(subtype):
    t=next(t for t in load('sft') if t['incident_subtype']==subtype)
    with MCPEnv(world(),t['active_mcps']) as env:e=run_oracle(t,env)
    e['calls']=[c for c in e['calls'] if c['server']=='db-mcp'];e['num_tool_calls']=len(e['calls']);assert score_episode(t,e,'anti_collapse')==0

def tasks():return [dict(task_id=k+'-'+l,kind=k,language=l) for k in PositiveAnchorSampler.kinds for l in ('en','hi','hinglish','te')]

def test_positive_anchor_skips_negative_variable_group():
    sampler=PositiveAnchorSampler(tasks());events=[];calls=0
    def sample(ts,temperature):
        nonlocal calls
        calls+=1;rewards=[-1.,-.85,-.3,0.] if calls==1 else [.3,-.85,-.3,-1.]
        return [dict(reward=r) for r in rewards]
    _,group,event=sampler.next_active(sample,on_attempt=lambda t,g,e:events.append(e))
    assert events[0]['all_negative_skipped'] and not events[0]['zero_variance_skipped'] and not events[0]['optimizer_update_eligible']
    assert event['optimizer_update_eligible'] and event['max_reward']>0 and sampler.accepted==1
    assert group[1]['reward']<statistics.mean(r['reward'] for r in group)

@pytest.mark.parametrize('size',[4,6])
def test_false_abstention_has_negative_advantage_in_worst_accepted_group(size):
    rewards=[.0001,-.85]+[-1.]*(size-2);assert rewards[1]-statistics.mean(rewards)<0

def test_weighted_rotation_carries_across_stages():
    accepted=[]
    for offset in (0,60):
        sampler=PositiveAnchorSampler(tasks(),offset=offset)
        for _ in range(60):
            ts,_,_=sampler.next_active(lambda ts,temperature:[dict(reward=r) for r in [.3,-.85,-.3,-1.]])
            accepted.append(ts[0]['kind'])
    assert accepted==list(PositiveAnchorSampler.cycle)*15
    assert Counter(accepted)=={'conflict':45,'incident':45,'consistent':15,'abstain':15}

def test_temperature_ramp_and_answerable_fallback():
    sampler=PositiveAnchorSampler(tasks());events=[]
    def sample(ts,temperature):return [dict(reward=r) for r in ([-1,-.85,-.3,0] if ts[0]['kind']=='conflict' else [.3,-.85,-.3,-1])]
    ts,_,e=sampler.next_active(sample,on_attempt=lambda t,g,e:events.append(e))
    assert ts[0]['kind']=='incident' and e['kind_saturated_fallback']
    assert [e['sampling_temperature'] for e in events[:32]]==[.8]*16+[.95]*16
    assert sampler.accepted==1

def test_no_anchor_exhaustion_never_counts_updates():
    sampler=PositiveAnchorSampler(tasks());events=[]
    with pytest.raises(NoActiveAdvantage):sampler.next_active(lambda ts,temperature:[dict(reward=r) for r in [-1,-.85,-.3,0]],max_attempts=2,on_attempt=lambda t,g,e:events.append(e))
    assert sampler.accepted==0 and len(events)==6 and all(e['all_negative_skipped'] for e in events)

def test_validation_guard_restores_prior_safe_best():
    s=ValidationSelector(.60,'sft');assert s.consider(30,.70,.40,'good')['selected']
    e=s.consider(60,.75,.4125,'unsafe');assert e['early_stop'] and not e['selected'] and s.best_path=='good' and s.best_step==30
    s=ValidationSelector(.60,'sft');s.consider(30,.55,.30,'worse');assert s.best_step==0 and s.best_path=='sft'

def test_warmstart_gate_does_not_accept_equal_baseline():
    before=[dict(task_id=str(i),case_id=str(i//4),exact_outcome=0.) for i in range(80)]
    assert not warm_start_gate(before,before)['passed']
    after=[dict(r,exact_outcome=1.) for r in before];assert warm_start_gate(before,after)['passed']

def test_frozen_inputs_and_old_reports_unchanged():
    import hashlib
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    data=json.loads(Path('reports/v2_1/APPROVED_DATA_LOCK.json').read_text());assert data=={p.name:sha(p) for p in Path('data_v2').iterdir() if p.is_file()}
    for name,digest in json.loads(Path('reports/v2_1/PROTECTED_V2_LOCK.json').read_text()).items():assert sha(relocated_path(name))==digest,name


@pytest.mark.parametrize('group_size',[4,6])
def test_live_backend_logs_three_rewards_and_rejects_negative_group(tmp_path,monkeypatch,group_size):
    import contextlib
    from collections import defaultdict
    from types import SimpleNamespace
    import torch
    import src_v2_1.agenttune_grpo_backend as backend
    trainer=backend.MCPGRPOTrainer.__new__(backend.MCPGRPOTrainer);ts=[dict(t,case_id=t['task_id'],gold_value=1,expected_status='answered',gold_cites=['DOC'],stale_doc_id=None) for t in tasks()]
    trainer.world={'schema_version':2};trainer.trace_dir=tmp_path;trainer.rollout_batch=0;trainer.active_sampler=PositiveAnchorSampler(ts);trainer.num_generations=group_size;trainer.temperature=.8;trainer.state=SimpleNamespace(global_step=0,num_input_tokens_seen=0);trainer.model=SimpleNamespace(set_adapter=lambda name:None);trainer.accelerator=SimpleNamespace(device=torch.device('cpu'),unwrap_model=lambda m:m,autocast=contextlib.nullcontext);trainer.processing_class=SimpleNamespace(pad_token_id=0);trainer._metrics={'train':defaultdict(list)};trainer.logps=lambda m,ids,att,mask,**kw:torch.zeros((len(ids),ids.shape[1]-1));monkeypatch.setattr(torch.cuda,'max_memory_reserved',lambda:0)
    attempts=[]
    def sample(candidates,*args,**kwargs):
        attempts.append(candidates);rr=([-1,-.85,-.3,0,-1,-.85] if len(attempts)==1 else [.3,-.85,-.3,-1,.3,1.3])[:group_size];out=[]
        for t,r in zip(candidates,rr):
            e=dict(prediction=dict(status='answered',value=0,cites=['DOC'],stale_source=None),retrieved_ids=['DOC'],num_tool_calls=0,calls=[],messages=[],raw_turns=[],completion_reason='final_answer')
            out.append(dict(reward=r,specified_reward=.05,evidence_gated_reward=-.2,anti_collapse_reward=r,input_ids=[1,2,3],assistant_mask=[0,1,1],episode=e))
        return out
    monkeypatch.setattr(backend,'sample_episodes',sample);result=trainer._generate_and_score_completions([{'task':ts[0]}]*group_size);logged=[json.loads(x) for x in (tmp_path/'rollout_metrics.jsonl').read_text().splitlines()];raw=[json.loads(x) for x in (tmp_path/'rollouts.jsonl').read_text().splitlines()]
    assert len(attempts)==2 and trainer.state.global_step==0
    assert [r['optimizer_update_eligible'] for r in logged]==[False,True] and logged[0]['all_negative_skipped'] and not logged[0]['zero_variance_skipped']
    assert all({'specified_reward','evidence_gated_reward','anti_collapse_reward'}<=r.keys() for r in raw)
    assert result['advantages'][1]<0


@pytest.mark.parametrize('stage,terminal',[('SCHEDULING',False),('STARTING',False),('PENDING',False),('RUNNING',False),('COMPLETED',True),('CANCELED',True),('ERROR',True),('DELETED',True)])
def test_cloud_queue_states_are_not_terminal(stage,terminal):
    from src_v2_1.manage import terminal_stage
    assert terminal_stage(stage)==terminal


def test_configured_six_sample_exploration_and_anchor():
    sampler=PositiveAnchorSampler(tasks(),temperature=1.,retry_temperature=1.15);events=[]
    def sample(ts,temperature):
        rr=[1.3]*6 if len(events)<16 else [1.3,-.85,-.3,.3,-1.,1.3]
        return [dict(reward=r) for r in rr]
    ts,group,event=sampler.next_active(sample,group_size=6,on_attempt=lambda t,g,e:events.append(e))
    assert len(group)==6 and [e['sampling_temperature'] for e in events]==[1.]*16+[1.15]
    assert group[1]['reward']<statistics.mean(r['reward'] for r in group) and event['max_reward']>0 and event['reward_std']>0

def test_handoff_only_copies_completed_sft_and_diagnostic(tmp_path):
    from src_v2_1.pipeline import copy_completed_sft
    source=tmp_path/'previous';out=tmp_path/'next'
    for folder in ('prior_v2','stage1_diagnostic','sft_training','sft_evaluation','grpo_training'):
        p=source/folder;p.mkdir(parents=True);(p/'evidence.json').write_text('{"kept":true}')
    (source/'MODEL_REVISIONS.json').write_text(json.dumps({'SFT':{'repo':'pinned','revision':'abc'},'GRPO_BEST_VAL':{'repo':'must-not-copy'}}));(source/'V2_STAGE1_DIAGNOSTIC.md').write_text('diagnostic')
    selected=copy_completed_sft(source,out)
    assert selected=={'repo':'pinned','revision':'abc'}
    assert (out/'sft_evaluation/evidence.json').read_bytes()==(source/'sft_evaluation/evidence.json').read_bytes()
    assert not (out/'grpo_training').exists() and not (out/'MODEL_REVISIONS.json').exists()
