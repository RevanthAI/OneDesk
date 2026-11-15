import pytest
from src.world_generator import generate_world
from src.oracle_solver import build_tasks,run_oracle
from src.mcp_env import MCPEnv
from src.mcp_adapter import wrap
from src.evaluate_auditkit import run_batch,measure,bootstrap_ratio,verify_manifest
class Replay:
    def __init__(self,turns): self.turns=iter(turns)
    def generate_messages(self,messages): return next(self.turns)
def test_live_loop_uses_tools():
    world=generate_world();task=next(t for t in build_tasks(world) if t['kind']=='conflict')
    with MCPEnv(world,task['active_mcps']) as env: oracle=run_oracle(task,env)
    turns=[[m['content']] for m in oracle['messages'] if m['role']=='assistant']
    result=run_batch([task],world,Replay(turns))[0]
    assert measure(task,result)['stale_catch']==1
    assert result['num_tool_calls']==2 and result['prediction']==oracle['prediction']
def test_malformed_and_budget_are_failure():
    world=generate_world();t=build_tasks(world)[0]
    e=run_batch([t],world,Replay([['not JSON']]))[0]
    assert not measure(t,e)['exact_outcome']
    call=wrap('tool_call',{'server':'db-mcp','tool':'inspect_schema','arguments':{}})
    e=run_batch([t],world,Replay([[call],[call],[call]]),max_calls=2)[0]
    assert e['completion_reason']=='tool_budget_exhausted' and e['num_tool_calls']==2
def test_cluster_bootstrap_and_undefined():
    rows=[dict(case_id='a',x=1),dict(case_id='a',x=1),dict(case_id='b',x=0),dict(case_id='b',x=0)]
    r=bootstrap_ratio(rows,lambda r:r['x'],lambda r:1)
    assert r['clusters']==2 and r['estimate']==.5 and r['ci95']==[0,1]
    assert bootstrap_ratio(rows,lambda r:0,lambda r:0)['estimate'] is None
def test_manifest_and_prompt_label_separation():
    import json
    from pathlib import Path
    hashes=verify_manifest(Path('docs/archive/data_v1'));assert 'holdout_synth_400_frozen.jsonl' in hashes
    for line in Path('docs/archive/data_v1/holdout_synth_400_frozen.jsonl').read_text().splitlines():
        task=json.loads(line)
        assert all(key not in str(task['prompt']) for key in ('gold_value','gold_cites','oracle_optimal_steps','expected_status'))

def test_frozen_prompt_is_used_and_not_mutated():
    import copy
    world=generate_world();t=build_tasks(world)[0]
    t['prompt']=[{'role':'system','content':'Frozen prompt'},{'role':'user','content':t['question']}]
    before=copy.deepcopy(t['prompt'])
    class Check:
        def generate_messages(self,batch):
            assert batch[0]==before
            return ['<final_answer>{"status":"abstain","value":null,"cites":[],"stale_source":null}</final_answer>']
    run_batch([t],world,Check())
    assert t['prompt']==before

def test_oom_splits_preserve_order_and_retry_all_inputs():
    from types import SimpleNamespace
    from src.evaluate_auditkit import HFBackend
    class OOM(RuntimeError): pass
    backend=HFBackend.__new__(HFBackend)
    backend.torch=SimpleNamespace(cuda=SimpleNamespace(OutOfMemoryError=OOM,empty_cache=lambda:None))
    backend.oom_splits=0
    def generate(batch):
        if len(batch)>2: raise OOM('simulated memory pressure')
        return [str(x) for x in batch]
    backend._generate_messages=generate
    assert backend.generate_messages(list(range(7)))==[str(x) for x in range(7)]
    assert backend.oom_splits==3
