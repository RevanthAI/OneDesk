import concurrent.futures
import pytest
from src.world_generator import generate_world
from src.mcp_env import MCPEnv, safe_calculate
from src.mcp_adapter import parse_turn, FormatError

def test_disjoint_and_deterministic():
    a,b=generate_world(42,'train'),generate_world(99,'test_synth')
    assert a == generate_world(42,'train')
    for key in ('services','employees'): assert not set(a[key]) & set(b[key])
    vals=lambda w:{f[k] for f in w['facts'] for k in ('initial_value','current_value')}
    assert not vals(a)&vals(b)
    assert len(a['services'])==25 and len(a['employees'])==40
    assert sum(f['was_updated'] for f in a['facts'])==90

def test_sql_readonly_and_errors():
    with MCPEnv(generate_world()) as env:
        for sql in ['DELETE FROM microservices', 'PRAGMA query_only=OFF', 'SELECT * FROM notion_pages', 'SELECT * FROM sqlite_master', 'SELECT load_extension("x")', 'SELECT 1; DELETE FROM microservices']:
            assert 'error' in env.call('db-mcp','query_db',{'sql':sql})
        assert 'error' in env.call('db-mcp','query_db',{'sql':'SELECT bogus FROM microservices'})
        assert len(env.call('db-mcp','query_db',{'sql':'SELECT * FROM microservices'})['rows'])==25

def test_rollout_isolation():
    def run(_):
        with MCPEnv(generate_world()) as e:
            e.call('db-mcp','query_db',{'sql':'DELETE FROM microservices'})
            return len(e.call('db-mcp','query_db',{'sql':'SELECT * FROM microservices'})['rows'])
    with concurrent.futures.ThreadPoolExecutor(8) as pool: assert list(pool.map(run,range(8)))==[25]*8

def test_tools_and_parser():
    assert safe_calculate('(3+2)*4/2')==10
    with pytest.raises(ValueError): safe_calculate('__import__("os")')
    with pytest.raises(ValueError): safe_calculate('2**999')
    with pytest.raises(FormatError): parse_turn('<tool_call>{"server":"x","server":"y"}</tool_call>')
    with MCPEnv(generate_world(),[]) as e: assert 'error' in e.call('db-mcp','inspect_schema',{})

def test_oracle_all_tasks_and_no_gold_dependency():
    import copy
    from src.oracle_solver import build_tasks,run_oracle
    from src.reward import outcome_ok
    for split,seed in [('train',42),('test_synth',99)]:
        world=generate_world(seed,split)
        for t in build_tasks(world,400)[::4]:
            original=copy.deepcopy(t)
            # Oracle may route using task identity/type, but must read values from tools.
            t['gold_value']='POISON';t['gold_cites']=['POISON'];t['expected_status']='POISON'
            with MCPEnv(world,t['active_mcps']) as env: e=run_oracle(t,env)
            assert outcome_ok(e['prediction'],original)
            assert e['num_tool_calls']==original['oracle_optimal_steps']

def test_sql_snapshot_round_trip():
    import sqlite3
    with MCPEnv(generate_world()) as env:
        dump=env.sql_dump()
        assert 'PRAGMA' not in dump
        replica=sqlite3.connect(':memory:')
        try:
            replica.executescript(dump)
            assert replica.execute('SELECT COUNT(*) FROM microservices').fetchone()[0]==25
            assert replica.execute('SELECT COUNT(*) FROM notion_pages').fetchone()[0]==150
        finally: replica.close()
        assert 'error' in env.call('db-mcp','query_db',{'sql':'SELECT * FROM notion_pages'})


# V2 tests read its separately frozen fixtures; all V1 assertions above remain.
def test_v2_pairwise_disjoint_case_pairs_and_incidents():
    import itertools,json
    from pathlib import Path
    names=('train_sft_240','train_grpo_stage1','train_grpo_stage2','val_train_80','holdout_synth_400_frozen','holdout_repo_style_100_frozen')
    rows={n:[json.loads(line) for line in Path('data_v2',n+'.jsonl').read_text().splitlines()] for n in names}
    expected=dict(zip(names,(240,400,480,80,400,100)))
    for name,data in rows.items():assert len(data)==expected[name]
    for a,b in itertools.combinations(names,2):
        assert not {t['case_id'] for t in rows[a]}&{t['case_id'] for t in rows[b]},(a,b,'case_id')
        assert not {(t['service_name'],t['param_name']) for t in rows[a]}&{(t['service_name'],t['param_name']) for t in rows[b]},(a,b,'service_parameter')
        assert not {t['incident_id'] for t in rows[a] if t['incident_id']} & {t['incident_id'] for t in rows[b] if t['incident_id']},(a,b,'incident_id')
