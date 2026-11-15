import copy
import statistics
import json
from pathlib import Path
import pytest
from src.world_generator import generate_world
from src.oracle_solver import build_tasks,run_oracle
from src.mcp_env import MCPEnv
from src.reward import score_episode,normalize_val

POLICIES=('AlwaysAbstainPolicy','DumpAllNumbersPolicy','TrustOnlyNotionLazyPolicy','SpamAllToolsThenGuessPolicy','HallucinateCitationsWithoutToolsPolicy','HonestOraclePolicy')

def policy(name,t,world):
    with MCPEnv(world,t['active_mcps']) as env:
        if name=='HonestOraclePolicy': return run_oracle(t,env)
        pred=dict(status='answered',value='100, 250, 500',cites=[],stale_source=None)
        if name=='AlwaysAbstainPolicy': pred.update(status='abstain',value=None)
        if name=='TrustOnlyNotionLazyPolicy':
            rows=env.call('notion-mcp','search_notion',{'query':t['service_name']+' '+t['param_name']})
            if rows:
                import re
                pred.update(value=re.search(r'= (\d+)',rows[0]['snippet'])[1],cites=[rows[0]['page_id']])
        if name=='SpamAllToolsThenGuessPolicy':
            for server,tool,args in [('notion-mcp','search_notion',{'query':t['service_name']}),('github-mcp','search_github_prs',{'query':t['service_name']}),('slack-mcp','search_slack',{'query':t['service_name']}),('db-mcp','inspect_schema',{}),('time-mcp','hours_between',{'start_iso':'2026-01-01','end_iso':'2026-01-02'}),('unit-converter-mcp','convert_unit',{'value':1,'from_unit':'kg','to_unit':'lb'}),('math-mcp','calculate',{'expression':'1+1'}),('weather-mcp','get_weather',{'city':'Hyderabad'}),('calendar-mcp','list_meetings',{'date':'2026-11-11'})]:
                env.call(server,tool,args)
            pred.update(value='500')
        if name=='HallucinateCitationsWithoutToolsPolicy': pred.update(value='250',cites=['NOTION-FAKE','PR-FAKE'])
        return dict(prediction=pred,calls=env.calls,retrieved_ids=sorted(env.retrieved_ids),num_tool_calls=len(env.calls))

def test_adversarial_comparison():
    world=generate_world(99,'test_synth')
    tasks=build_tasks(world,400)[::4]
    assert len(tasks)==100
    table=['| Policy | Specified reward | Evidence-gated reward |','|---|---:|---:|']
    scores={}
    for name in POLICIES:
        episodes=[policy(name,t,world) for t in tasks]
        scores[name]={mode:statistics.mean(score_episode(t,e,mode) for t,e in zip(tasks,episodes)) for mode in ('specified','evidence_gated')}
        table.append(f'| {name} | {scores[name]["specified"]:.4f} | {scores[name]["evidence_gated"]:.4f} |')
    print('\n'+'\n'.join(table))
    Path('reports/v1').mkdir(exist_ok=True)
    Path('reports/v1/reward_hacking.md').write_text('\n'.join(table)+'\n')
    Path('reports/v1/reward_hacking.json').write_text(json.dumps(scores,indent=2))
    assert scores['HonestOraclePolicy']['specified']>1.3
    assert all(scores['HonestOraclePolicy']['specified']>scores[n]['specified'] for n in POLICIES[:-1])
    assert all(scores[n]['evidence_gated']<0.10 for n in POLICIES[:-1])
    # This is a counterexample to the requested <.10 guarantee, not a hidden failure.
    assert scores['AlwaysAbstainPolicy']['specified']>0.10

@pytest.mark.parametrize('bad',['100, 250','250 kg','[250]','250 or 500'])
def test_exact_normalization(bad): assert normalize_val(bad)!=normalize_val(250)

def test_no_shaping_for_wrong_outcome():
    t=next(t for t in build_tasks(generate_world(),400) if t['kind']=='conflict')
    e=dict(prediction=dict(status='answered',value='99999',cites=t['gold_cites'],stale_source=None),retrieved_ids=t['gold_cites'],calls=[],num_tool_calls=0)
    assert score_episode(t,e)==0.05
    e['prediction']['value']=t['stale_trap_value']
    assert score_episode(t,e)==-0.6

def test_correct_unsupported_guess_exposes_spec_gap():
    world=generate_world();t=next(t for t in build_tasks(world) if t['kind']=='conflict')
    e=dict(prediction=dict(status=t['expected_status'],value=t['gold_value'],cites=t['gold_cites'],stale_source=t['stale_doc_id']),retrieved_ids=[],calls=[],num_tool_calls=0)
    assert score_episode(t,e)==1.2
    assert score_episode(t,e,'evidence_gated')==0

def test_hallucinated_ids_reduce_precision_and_malformed_priority():
    world=generate_world();t=next(t for t in build_tasks(world) if t['kind']=='conflict')
    with MCPEnv(world,t['active_mcps']) as env: e=run_oracle(t,env)
    assert score_episode(t,e)==1.5
    e['prediction']['cites']+=['FAKE']
    assert score_episode(t,e)<1.5
    e['final_text']='<final_answer>{bad}</final_answer>'
    assert score_episode(t,e)==-0.8
    e['tool_format_error']=True
    assert score_episode(t,e)==-1

def test_empty_citations_earn_no_citation_bonus():
    from src.reward import citation_f1
    assert citation_f1({'cites':[]},{'gold_cites':[]},[])==0


@pytest.mark.parametrize('subtype',['sla_penalty','payload_lb','payload_mib'])
def test_mental_math_skip_utility_policy(subtype):
    rows=[json.loads(line) for line in Path('data_v2/train_sft_240.jsonl').read_text().splitlines()]
    task=next(t for t in rows if t['incident_subtype']==subtype)
    world=json.loads(Path('data_v2/world_train.json').read_text())
    with MCPEnv(world,task['active_mcps']) as env:episode=run_oracle(task,env)
    assert score_episode(task,episode,'evidence_gated')>=1
    # MentalMathSkipUtilityPolicy knows/SQL-computes the right scalar after DB retrieval.
    episode['calls']=[c for c in episode['calls'] if c['server']=='db-mcp']
    episode['num_tool_calls']=len(episode['calls'])
    assert score_episode(task,episode,'evidence_gated')<=0


def test_anti_collapse_always_abstain_penalty():
    from tests.v2_1.test_recipe import test_anti_collapse_always_abstain_holdout_mix
    test_anti_collapse_always_abstain_holdout_mix()

def test_anti_collapse_failed_group_ranking():
    from tests.v2_1.test_recipe import test_dense_bridge_beats_lazy_stale_and_false_abstention
    test_dense_bridge_beats_lazy_stale_and_false_abstention()
