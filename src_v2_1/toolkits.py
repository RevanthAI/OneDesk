"""Narrow integration with real installed AgentTune trajectory code.

AgentTune's agentic/__init__.py eagerly imports optional training/OpenEnv/RAG
stacks. Load its dependency-free trajectory module by installed file location,
without importing that initializer or pretending training dependencies exist.
"""
import importlib.util
from pathlib import Path
import sys

def trajectory_module():
    import agenttune
    name='_driftguard_agenttune_trajectory'
    if name not in sys.modules:
        path=Path(agenttune.__file__).parent/'agentic'/'trajectory'/'dataset.py'
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec)
        sys.modules[name]=module
        spec.loader.exec_module(module)
    return sys.modules[name]

def portable_trajectory(task,episode):
    m=trajectory_module()
    import json
    steps=[m.Step(step_number=i,state=task['question'] if i==0 else 'Previous tool observation',
        action={'name':c['server']+'__'+c['tool'],'arguments':c['arguments']},
        observation=json.dumps(c['output'],ensure_ascii=False)) for i,c in enumerate(episode['calls'])]
    final=episode.get('final_text')
    if not final:
        from .mcp_adapter import wrap
        final=wrap('final_answer',episode.get('prediction'))
    steps.append(m.Step(step_number=len(steps),state='Final synthesis',action={},observation=final))
    row=m.Trajectory(task=task['question'],steps=steps,trajectory_id=task['task_id'],final_response=final,
        metadata={'task_id':task['task_id'],'world_split':task['world_split'],'language':task['language']}).to_dict()
    from .reward import score_episode
    row['reward']=score_episode(task,episode,'evidence_gated')
    return row
