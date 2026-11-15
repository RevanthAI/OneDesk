import copy,itertools,json
from collections import Counter
from pathlib import Path
import pytest
from src.mcp_env import MCPEnv
from src.oracle_solver import run_oracle
from src.reward import outcome_ok,score_episode
from src.v2_world import DOMAINS
from src.evaluate_auditkit import verify_manifest

@pytest.fixture(scope='module')
def worlds():return {key:json.loads(Path('data_v2','world_'+key+'.json').read_text()) for key in ('train','test_synth','repo_style')}

def rows(name):return [json.loads(line) for line in Path('data_v2',name+'.jsonl').read_text().splitlines()]


def test_v2_domains_names_counts_and_incident_variation(worlds):
    from src.world_generator import generate_world
    train=worlds['train'];assert len(train['services'])==60 and len(train['incidents'])==80
    assert train==generate_world(42,'train',version=2)
    assert sum(map(len,train['case_pools'].values()))==320 and len(train['case_pools']['train_reserved'])==20
    for world in worlds.values():
        for f in world['facts']:
            low,high=DOMAINS[f['param_name']]
            assert all(low<=f[k]<=high for k in ('initial_value','current_value','intermediate_value','staging_value'))
            assert f['staging_value'] not in (f['initial_value'],f['current_value'])
        for field in ('started_at','penalty_rate_per_hour','weight_kg','data_spill_gb'):
            assert len({r[field] for r in world['incidents']})>1
    for a,b in itertools.combinations(worlds.values(),2):
        assert not set(a['services'])&set(b['services'])
        vals=lambda w:{f[k] for f in w['facts'] for k in ('initial_value','current_value')}
        assert not vals(a)&vals(b)


def test_v2_prompts_do_not_spoil_tools_or_gold_and_scripts_exist(worlds):
    from src.v2_dataset import FILES
    for name,(key,_) in FILES.items():
        data=rows(name)
        for r in data:
            assert '-mcp' not in r['question']
            assert r['prompt'][1]['content']==r['question']
            assert all(label not in str(r['prompt']) for label in ('gold_value','reference_tool_sequence','source_server','oracle_optimal_steps','expected_status'))
            if r['kind'] in ('consistent','conflict'):assert {'github-mcp','slack-mcp'}<=set(r['active_mcps'])
            if r['kind']=='incident':assert r['incident_id'] in r['question'] and r['service_name'] not in r['question']
            if r['missing_entity']:assert r['service_name'] not in worlds[key]['services'] and not r['service_name'].startswith('unknown-')
        for lang in ('hi','te'):assert {r['script'] for r in data if r['language']==lang}=={'native','latin'}


def test_v2_ranked_search_scope_and_sibling_decoys(worlds):
    world=worlds['train'];t=next(r for r in rows('train_sft_240') if r['kind']=='conflict')
    with MCPEnv(world) as env:
        results=env.call('notion-mcp','search_notion',{'query':f"Please audit the effective deployed configuration setting runbook for {t['service_name']} {t['param_name']}"})
        assert len(results)==3
        own=[r for r in results if r['service_name']==t['service_name']]
        assert {r['environment'] for r in own}=={'prod','staging'}
        assert results[0]['environment']=='staging'
        assert any(r['service_name']!=t['service_name'] for r in results)
        assert all('gold_value' not in r and 'current_value' not in r for r in results)
        assert 'error' in env.call('db-mcp','query_db',{'sql':'SELECT * FROM notion_pages'})


def test_v2_all_oracles_and_incident_tool_chains(worlds):
    from src.v2_dataset import FILES
    seen=set();subtypes=set()
    for name,(world_key,_) in FILES.items():
        for t in rows(name):
            if t['case_id'] in seen:continue
            seen.add(t['case_id']);poison=copy.deepcopy(t)
            poison.update(gold_value='POISON',expected_status='POISON',gold_cites=['POISON'],source_server='INVALID')
            if t['incident_id']:poison['service_name']='poisoned-service-identity'
            with MCPEnv(worlds[world_key],t['active_mcps']) as env:e=run_oracle(poison,env)
            assert outcome_ok(e['prediction'],t),t['task_id']
            assert set(t['gold_cites'])<=set(e['retrieved_ids'])
            assert e['num_tool_calls']==t['oracle_optimal_steps']
            assert score_episode(t,e,'evidence_gated')>=1
            if t['kind']=='incident':
                subtypes.add(t['incident_subtype']);servers=[c['server'] for c in e['calls']]
                assert servers[0]=='db-mcp'
                if t['incident_subtype'] in ('payload_lb','payload_mib'):assert servers==['db-mcp','unit-converter-mcp','math-mcp']
                if t['incident_subtype']=='sla_penalty':assert servers==['db-mcp','time-mcp','math-mcp']
    assert subtypes=={'config_audit','sla_penalty','payload_lb','payload_mib'}


def test_v2_repo_mix_dedup_rewards_and_freeze():
    data=rows('holdout_repo_style_100_frozen')
    assert Counter(r['kind'] for r in data)==dict(conflict=50,consistent=20,incident=15,abstain=15)
    assert Counter(r['language'] for r in data)==dict.fromkeys(('en','hi','hinglish','te'),25)
    funnel=json.loads(Path('data_v2/curation_funnel.json').read_text())
    for stats in funnel.values():assert stats['rejected']==stats['injected_duplicate_controls']>0 and stats['input']-stats['rejected']==stats['kept']
    trajectories=rows('train_sft_agenttune_trajectories')
    assert len(trajectories)==240 and all(1<=t['reward']<=1.5 for t in trajectories)
    assert {'consistent','conflict','incident','abstain'}=={t['metadata']['kind'] for t in trajectories}
    assert verify_manifest(Path('data_v2'))
    assert verify_manifest(Path('docs/archive/data_v1'))


def test_v2_cross_channel_discovery_uses_observations(worlds):
    world=worlds['train'];facts={(f['service_name'],f['param_name']):f for f in world['facts']}
    cases=[c for pool in world['case_pools'].values() for c in pool if c['kind']=='conflict']
    assert len(cases)==80 and sum(facts[(c['service_name'],c['param_name'])]['cross_channel'] for c in cases)==24
    target=next(t for t in rows('train_sft_240') if t['kind']=='conflict' and facts[(t['service_name'],t['param_name'])]['cross_channel'])
    with MCPEnv(world,target['active_mcps']) as env:e=run_oracle(target,env)
    assert len(e['calls'])==3 and {c['server'] for c in e['calls']}=={'notion-mcp','github-mcp','slack-mcp'}
    assert len(e['prediction']['cites'])==3 and outcome_ok(e['prediction'],target)


def test_v2_newest_staging_and_fake_citations_are_not_rewarded(worlds):
    task=next(t for t in rows('holdout_synth_400_frozen') if t['kind']=='conflict')
    world=worlds['test_synth']
    with MCPEnv(world,task['active_mcps']) as env:
        results=env.call('notion-mcp','search_notion',{'query':task['service_name']+' '+task['param_name']})
        staging=next(r for r in results if r['service_name']==task['service_name'] and r['environment']=='staging')
        import re
        value=int(re.search(r'= (\d+)',staging['snippet'])[1])
        bad=dict(prediction={'status':'conflict_resolved','value':value,'cites':[staging['page_id']],'stale_source':task['stale_doc_id']},calls=env.calls,num_tool_calls=len(env.calls),retrieved_ids=list(env.retrieved_ids))
        assert not outcome_ok(bad['prediction'],task) and score_episode(task,bad,'evidence_gated')<=0
    fake=dict(prediction={'status':task['expected_status'],'value':task['gold_value'],'cites':task['gold_cites'],'stale_source':task['stale_doc_id']},retrieved_ids=[],calls=[],num_tool_calls=0)
    assert score_episode(task,fake,'evidence_gated')==0
