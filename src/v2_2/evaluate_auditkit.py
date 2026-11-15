"""V2 cloud evaluation with fixed cohorts, AuditKIT and cluster confidence intervals."""
from collections import Counter
import json,time
from pathlib import Path
from .data import load,world,verify,write_json,write_jsonl
from .backend import Backend,MODEL,REVISION
from .evaluation_core import run_batch,measure,summary_metrics,auditkit_score
from .toolkits import portable_trajectory


def evaluate(model,tokenizer,out,splits=('test_synth','repo_style'),batch_size=16,persist=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);hashes=verify();results=json.loads((out/'summary.json').read_text()) if (out/'summary.json').exists() else {};start=time.perf_counter()
    config=dict(schema_version=2,data_dir='data_v2',dataset_hashes=hashes,model=MODEL,revision=REVISION,compute_dtype='bfloat16',quantization=None,batch_size=batch_size,max_new_tokens_per_turn=192,max_context_length=4096,temperature=0.,max_tool_calls=6)
    if (out/'run_config.json').exists() and json.loads((out/'run_config.json').read_text())!=config:raise ValueError('v2 evaluation configuration changed; refuse mixed run')
    write_json(out/'run_config.json',config);backend=Backend(model,tokenizer)
    for split in splits:
        tasks=load(split);w=world('train' if split=='validation' else split);file=out/(split+'_episodes.jsonl')
        saved=[json.loads(line) for line in file.read_text().splitlines()] if file.exists() else []
        by_id={r['task_id']:r for r in saved}
        if len(by_id)!=len(saved) or set(by_id)-{t['task_id'] for t in tasks}:raise ValueError('saved evaluation coverage invalid')
        todo=[t for t in tasks if t['task_id'] not in by_id]
        for i in range(0,len(todo),batch_size):
            batch=todo[i:i+batch_size];episodes=run_batch(batch,w,backend)
            with file.open('a') as stream:
                for e in episodes:stream.write(json.dumps(e,ensure_ascii=False)+'\n');by_id[e['task_id']]=e
            print(json.dumps({'event':'v2_eval_progress','output':str(out),'split':split,'completed':len(by_id),'total':len(tasks)}),flush=True)
            if persist and ((i//batch_size)%5==0 or i+batch_size>=len(todo)):persist()
        episodes=[by_id[t['task_id']] for t in tasks];rows=[measure(t,e) for t,e in zip(tasks,episodes)]
        write_jsonl(out/(split+'_metrics.jsonl'),rows)
        write_jsonl(out/(split+'_agenttune_trajectories.jsonl'),[portable_trajectory(t,e) for t,e in zip(tasks,episodes)])
        from auditkit.agent_eval.importers import episodes_from_agenttune
        assert len(episodes_from_agenttune(str(out/(split+'_agenttune_trajectories.jsonl'))))==len(tasks)
        headline=auditkit_score(tasks,episodes,out/(split+'_auditkit'),w)
        results[split]=dict(n=len(tasks),metrics=summary_metrics(rows),auditkit_headline=headline,completion_reasons=dict(Counter(e['completion_reason'] for e in episodes)))
        write_json(out/'summary.json',results);write_json(out/'runtime.json',dict(backend.stats(),wall_seconds=time.perf_counter()-start))
        print(json.dumps({'event':'v2_eval_complete','output':str(out),'split':split,'accuracy':results[split]['metrics']['exact_outcome']['estimate']}),flush=True)
        if persist:persist()
    return results
