"""Generate, curate, oracle-verify, and hash datasets before model evaluation."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
from .world_generator import generate_world
from .real_repo_world import generate_repo_world
from .oracle_solver import build_tasks,run_oracle
from .mcp_env import MCPEnv
from .mcp_adapter import initial_messages
from .reward import outcome_ok
from .toolkits import portable_trajectory,trajectory_module

def write_jsonl(path,rows):
    Path(path).write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')

def curate(tasks,world):
    from curatorkit.schema import DataSample
    from curatorkit.normalizers.dedup import ExactDeduplicator
    samples=[]
    for t in tasks:
        with MCPEnv(world,t['active_mcps']) as env: messages=initial_messages(t,env)
        # Include active tool schemas: identical words under different available
        # tools are different agent tasks. Deduplication is exact, not semantic.
        samples.append(DataSample(id=t['task_id'],source_uri='deterministic://'+world['split'],instruction=json.dumps(messages,sort_keys=True),metadata={'task':t}))
    kept=ExactDeduplicator().run(samples)
    return [s.metadata['task'] for s in kept],{'input':len(tasks),'kept':len(kept),'rejected':len(tasks)-len(kept),'method':'CuratorKIT ExactDeduplicator; prompt plus active schemas','semantic_dedup':False}

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--version',type=int,choices=(1,2),default=1);p.add_argument('--output');args=p.parse_args()
    if args.version==2:
        from .v2_dataset import build
        build(args.output or 'data_v2');return
    if args.output:raise ValueError('custom output is supported by v2 only')
    data=Path('data');data.mkdir(exist_ok=True)
    if (data/'SHA256SUMS').exists(): raise SystemExit('Frozen datasets already exist; do not silently regenerate an evaluated holdout. Use a new output directory/version.')
    worlds={'train':generate_world(42,'train'),'test_synth':generate_world(99,'test_synth'),'repo_style':generate_repo_world()}
    funnel={};sft=[];agent_rows=[]
    specs=[('train_sft_400', 'train',400,(20,15,50,15)),('train_grpo_stage1','train',400,(40,30,20,10)),('train_grpo_stage2','train',400,(20,10,55,15)),('holdout_synth_400_frozen','test_synth',400,(20,15,50,15)),('holdout_repo_style_100_frozen','repo_style',120,(0,0,100,0))]
    for name,wkey,count,mix in specs:
        world=worlds[wkey];tasks=build_tasks(world,count,mix)
        if wkey=='repo_style':
            # 25 items/language spanning all 30 constructed cases across languages.
            tasks=[t for li,lang in enumerate(('en','hi','hinglish','te')) for t in tasks if t['language']==lang and (int(t['case_id'].rsplit('-',1)[1])-5*li)%30<25]
        tasks,info=curate(tasks,world)
        verified=[]
        for t in tasks:
            with MCPEnv(world,t['active_mcps']) as env: episode=run_oracle(t,env)
            assert outcome_ok(episode['prediction'],t),t['task_id']
            assert episode['num_tool_calls']==t['oracle_optimal_steps'],t['task_id']
            assert set(t['gold_cites'])<=set(episode['retrieved_ids']),t['task_id']
            row=dict(t,oracle_optimal_steps=episode['num_tool_calls'])
            with MCPEnv(world,t['active_mcps']) as env: row['prompt']=initial_messages(t,env)
            if name=='train_sft_400':
                row['messages']=episode['messages'];agent_rows.append(portable_trajectory(t,episode))
            verified.append(row)
        write_jsonl(data/(name+'.jsonl'),verified)
        info.update(oracle_verified=len(verified),languages=dict(Counter(t['language'] for t in tasks)),task_kinds=dict(Counter(t['kind'] for t in tasks)))
        funnel[name]=info
        if name=='train_sft_400': assert len(verified)==400
    write_jsonl(data/'train_sft_agenttune_trajectories.jsonl',agent_rows)
    loaded=trajectory_module().TrajectoryDataset.from_jsonl(data/'train_sft_agenttune_trajectories.jsonl')
    assert len(loaded)==400
    from auditkit.agent_eval.importers import episodes_from_agenttune
    imported=episodes_from_agenttune(str(data/'train_sft_agenttune_trajectories.jsonl'))
    assert len(imported)==400
    for name,w in worlds.items(): (data/('world_'+name+'.json')).write_text(json.dumps(w,ensure_ascii=False,sort_keys=True,indent=2))
    (data/'curation_funnel.json').write_text(json.dumps(funnel,indent=2))
    paths=sorted(p for p in data.iterdir() if p.suffix in ('.json','.jsonl'))
    (data/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in paths))
    print(json.dumps(funnel,indent=2))
    print('AgentTune TrajectoryDataset -> AuditKIT episodes: 400 imported; datasets frozen.')

if __name__=='__main__': main()
