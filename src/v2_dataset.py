"""Build v2 into a new directory; freeze originals; no model inference/training."""
from __future__ import annotations
from collections import Counter
import copy,hashlib,itertools,json
from pathlib import Path
from .world_generator import generate_world
from .real_repo_world import generate_repo_world
from .v2_tasks import build_tasks_v2
from .oracle_solver import run_oracle
from .mcp_env import MCPEnv
from .reward import outcome_ok,score_episode
from .toolkits import portable_trajectory,trajectory_module

FILES={'train_sft_240':('train','train_sft'),'train_grpo_stage1':('train','train_grpo1'),'train_grpo_stage2':('train','train_grpo2'),'val_train_80':('train','train_val'),'holdout_synth_400_frozen':('test_synth','holdout_synth'),'holdout_repo_style_100_frozen':('repo_style','holdout_repo_style')}


def write_json(path,data):Path(path).write_text(json.dumps(data,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
def write_rows(path,rows):Path(path).write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))


def select_repo(tasks):
    # 26 semantic cases give 104 translations. Omit one translation per language
    # to meet exact 50/20/15/15 row counts, retaining every underlying case.
    by_kind={kind:sorted({t['case_id'] for t in tasks if t['kind']==kind}) for kind in ('consistent','incident','conflict','abstain')}
    omissions={(by_kind['conflict'][-1],'en'),(by_kind['conflict'][-2],'hi'),(by_kind['incident'][-1],'hinglish'),(by_kind['abstain'][-1],'te')}
    selected=[t for t in tasks if (t['case_id'],t['language']) not in omissions]
    assert Counter(t['kind'] for t in selected)=={'conflict':50,'consistent':20,'incident':15,'abstain':15}
    assert Counter(t['language'] for t in selected)==dict.fromkeys(('en','hi','hinglish','te'),25)
    return selected


def curate(rows,source):
    from curatorkit.schema import DataSample
    from curatorkit.normalizers.dedup import ExactDeduplicator
    count=round(len(rows)*.15)
    chosen=sorted(rows,key=lambda r:hashlib.sha256(('v2-duplicate-control:'+r['task_id']).encode()).hexdigest())[:count]
    candidates=[(r,'canonical') for r in rows]+[(r,'injected_exact_duplicate') for r in chosen]
    samples=[DataSample(id=f'{source}-candidate-{i:04d}',source_uri='deterministic-v2://'+source,instruction=json.dumps(row['prompt'],sort_keys=True,ensure_ascii=False),metadata={'task':row,'origin':origin}) for i,(row,origin) in enumerate(candidates)]
    kept=ExactDeduplicator().run(samples);ids={s.id for s in kept}
    rejected=[dict(candidate_id=s.id,task_id=s.metadata['task']['task_id'],reason='duplicate_model_visible_prompt',origin=s.metadata['origin']) for s in samples if s.id not in ids]
    out=[s.metadata['task'] for s in kept]
    assert {r['task_id'] for r in out}=={r['task_id'] for r in rows} and len(out)==len(rows)
    info=dict(input=len(samples),kept=len(out),rejected=len(rejected),injected_duplicate_controls=count,method='Real CuratorKIT ExactDeduplicator over model-visible messages',semantic_dedup=False,quality_claim='Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.')
    return out,info,rejected


def audit_splits(datasets):
    result={}
    for a,b in itertools.combinations(datasets,2):
        def values(name,key):return {t[key] for t in datasets[name] if t.get(key) is not None}
        pairs=lambda n:{(t['service_name'],t['param_name']) for t in datasets[n]}
        result[a+' vs '+b]=dict(case_id_overlap=len(values(a,'case_id')&values(b,'case_id')),service_parameter_overlap=len(pairs(a)&pairs(b)),incident_id_overlap=len(values(a,'incident_id')&values(b,'incident_id')))
        assert not any(result[a+' vs '+b].values()),(a,b,result[a+' vs '+b])
    return result


def build(output='data_v2'):
    out=Path(output)
    if out.resolve()==Path('data').resolve():raise ValueError('v2 must not overwrite v1 data')
    out.mkdir(exist_ok=True)
    if any(out.iterdir()):raise ValueError('refusing to overwrite v2 artifacts; use a new empty directory/version')
    worlds={'train':generate_world(42,'train',version=2),'test_synth':generate_world(99,'test_synth',version=2),'repo_style':generate_repo_world(version=2)}
    datasets={};funnel={};rejections=[];trajectories=[];episodes={};episode_cache={}
    for name,(world_key,pool) in FILES.items():
        world=worlds[world_key];tasks=build_tasks_v2(world,pool)
        if world_key=='repo_style':tasks=select_repo(tasks)
        tasks,info,rejected=curate(tasks,name);verified=[]
        for task in tasks:
            if task['case_id'] not in episode_cache:
                with MCPEnv(world,task['active_mcps']) as env:episode_cache[task['case_id']]=run_oracle(task,env)
            episode=copy.deepcopy(episode_cache[task['case_id']]);episode['messages'][1]['content']=task['question']
            assert outcome_ok(episode['prediction'],task),(task['task_id'],episode['prediction'])
            assert set(task['gold_cites'])<=set(episode['retrieved_ids']),task['task_id']
            row=dict(task,oracle_optimal_steps=episode['num_tool_calls'])
            row['reference_tool_sequence']=[c['server']+'__'+c['tool'] for c in episode['calls']]
            reward=score_episode(row,episode,mode='evidence_gated');assert reward>=1
            if name=='train_sft_240':
                row['messages']=episode['messages'];trajectory=portable_trajectory(row,episode);trajectory['reward']=reward
                trajectory['metadata'].update(schema_version=2,case_id=row['case_id'],kind=row['kind'],script=row['script'],reward_mode='evidence_gated',oracle_tool_calls=episode['num_tool_calls'])
                trajectories.append(trajectory)
            verified.append(row);episodes[row['task_id']]=episode
        datasets[name]=verified
        info.update(oracle_verified=len(verified),semantic_cases=len({r['case_id'] for r in verified}),languages=dict(Counter(r['language'] for r in verified)),kinds=dict(Counter(r['kind'] for r in verified)),scripts=dict(Counter(r['language']+':'+r['script'] for r in verified)),incident_subtypes=dict(Counter(r['incident_subtype'] for r in verified if r['kind']=='incident')))
        funnel[name]=info;rejections.extend(dict(dataset=name,**r) for r in rejected)
        write_rows(out/(name+'.jsonl'),verified)
        print(json.dumps({'dataset':name,'rows':len(verified),'verified':True}),flush=True)
    disjoint=audit_splits(datasets)
    for key,world in worlds.items():write_json(out/('world_'+key+'.json'),world)
    write_rows(out/'train_sft_agenttune_trajectories.jsonl',trajectories)
    assert len(trajectory_module().TrajectoryDataset.from_jsonl(out/'train_sft_agenttune_trajectories.jsonl'))==240
    from auditkit.agent_eval.importers import episodes_from_agenttune
    assert len(episodes_from_agenttune(str(out/'train_sft_agenttune_trajectories.jsonl')))==240
    write_json(out/'curation_funnel.json',funnel);write_rows(out/'curation_rejections.jsonl',rejections)
    write_json(out/'case_pool_manifest.json',{pool:[{'case_id':c['case_id'],'service_name':c['service_name'],'param_name':c['param_name'],'incident_id':c['incident_id'],'kind':c['kind']} for c in cases] for pool,cases in worlds['train']['case_pools'].items()})
    report=dict(schema_version=2,training_requested_total=320,training_allocated_cases=300,reserved_cases=20,training_world_services=60,training_world_incidents=80,disjoint_splits=disjoint,datasets=funnel,repo_style_semantic_cases=26,repo_style_partial_translations=4,oracle_rewards=dict(Counter(str(t['reward']) for t in trajectories)),training_launched=False,paid_jobs_launched=False,causal_claim='The audit identified plausible confounds, not proven causes of the prior accuracy or zero-variance groups.',inference_claim='No v2 model accuracy is available; no attempt is made to force SFT below an arbitrary accuracy threshold.')
    write_json(out/'AUDIT.json',report)
    from .v2_review import export_review
    export_review(out,datasets,worlds,episodes,report)
    files=sorted(p for p in out.iterdir() if p.suffix in ('.json','.jsonl'))
    (out/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
    print('Frozen v2 data and review export; no model inference or training launched.',flush=True)
    return report
