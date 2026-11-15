"""Frozen-data regression checks for the publication's live reward implementation."""
import copy
import pytest
from src_v2.data import load,world
from src_v2.mcp_env import MCPEnv
from src_v2.oracle_solver import run_oracle
from src_v2.reward import score_episode


@pytest.mark.parametrize('subtype',['sla_penalty','payload_lb','payload_mib'])
def test_mental_math_skip_utility_policy(subtype):
    task=next(t for t in load('sft') if t['incident_subtype']==subtype)
    with MCPEnv(world(),task['active_mcps']) as env:episode=run_oracle(task,env)
    assert score_episode(task,episode,'evidence_gated')>=1
    episode['calls']=[c for c in episode['calls'] if c['server']=='db-mcp']
    episode['num_tool_calls']=len(episode['calls'])
    assert score_episode(task,episode,'evidence_gated')==0


@pytest.mark.parametrize('subtype',['sla_penalty','payload_lb','payload_mib'])
def test_failed_utility_call_does_not_satisfy_chain(subtype):
    task=next(t for t in load('sft') if t['incident_subtype']==subtype)
    with MCPEnv(world(),task['active_mcps']) as env:episode=run_oracle(task,env)
    episode=copy.deepcopy(episode)
    for call in episode['calls']:
        if call['server']=='math-mcp':call['output']={'error':'calculation failed'}
    assert score_episode(task,episode,'evidence_gated')==0
