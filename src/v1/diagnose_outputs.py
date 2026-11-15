"""Post-hoc descriptive diagnostics. These never repair headline outcomes."""
from __future__ import annotations
from collections import Counter,defaultdict
import json
from pathlib import Path
import re
from .reward import normalize_val,outcome_ok

def diagnose(tasks,episodes):
    counters=Counter();examples={};by_kind=defaultdict(lambda:{'items':0,'strict_correct':0})
    for t,e in zip(tasks,episodes):
        counters['items']+=1
        by_kind[t['kind']]['items']+=1
        by_kind[t['kind']]['strict_correct']+=int(outcome_ok(e.get('prediction'),t))
        matches=re.findall(r'<final_answer>(.*?)</final_answer>',e.get('final_text',''),re.S)
        obj=None
        if len(matches)==1:
            try:
                parsed=json.loads(matches[0])
                if isinstance(parsed,dict): obj=parsed
            except ValueError: pass
        if obj is not None:
            counters['parseable_final_json']+=1
            if obj.get('status')==t['expected_status']: counters['raw_json_status_correct']+=1
            if t['kind']=='conflict' and normalize_val(obj.get('value'))==normalize_val(t['stale_trap_value']): counters['raw_json_stale_value_returned']+=1
            if set(obj)!={'status','value','cites','stale_source'}:
                counters['wrong_final_keys']+=1
            if normalize_val(obj.get('value'))==normalize_val(t['gold_value']): counters['raw_json_value_correct']+=1
            if outcome_ok(obj,t): counters['raw_json_status_and_value_correct']+=1
        if set(t['gold_cites']) and set(t['gold_cites'])<=set(e['retrieved_ids']): counters['all_required_evidence_retrieved']+=1
        if e['prediction'] is not None: counters['strict_final_valid']+=1
        for call in e['calls']:
            if isinstance(call['output'],dict) and 'error' in call['output']: counters['tool_error_results']+=1
            if isinstance(call['output'],list) and not call['output']: counters['empty_search_results']+=1
        reason=e['completion_reason']
        if reason not in examples:
            examples[reason]={'task_id':t['task_id'],'question':t['question'],'raw_final':e.get('final_text','')[:1200],'tool_calls':e['num_tool_calls'],'expected_status':t['expected_status'],'gold_value':t['gold_value']}
    return {'counts':dict(counters),'examples':examples,'by_kind':dict(by_kind)}

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',default='reports/v1/base_fire_nf4');a=p.parse_args()
    out=Path(a.output);results={}
    for world,filename in [('test_synth','holdout_synth_400_frozen.jsonl'),('repo_style','holdout_repo_style_100_frozen.jsonl')]:
        tasks=[json.loads(l) for l in (Path('docs/archive/data_v1')/filename).read_text().splitlines()]
        episodes=[json.loads(l) for l in (out/(world+'_episodes.jsonl')).read_text().splitlines()]
        by_id={e['task_id']:e for e in episodes};tasks=[t for t in tasks if t['task_id'] in by_id]
        results[world]=diagnose(tasks,[by_id[t['task_id']] for t in tasks])
    (out/'descriptive_diagnostics.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
    lines=['## Descriptive output diagnostics','', 'These diagnostics inspect parseable final JSON even when required fields are missing. They do not repair or replace strict headline outcomes. Raw value correctness ignores status and format. Counts are over all questions.','', '| Count | Synthetic | OSS-style |','|---|---:|---:|']
    keys=['items','parseable_final_json','wrong_final_keys','raw_json_value_correct','raw_json_status_correct','raw_json_status_and_value_correct','raw_json_stale_value_returned','tool_error_results','all_required_evidence_retrieved','strict_final_valid','empty_search_results']
    for k in keys: lines.append('| '+k+' | '+' | '.join(str(results[w]['counts'].get(k,0)) for w in ('test_synth','repo_style'))+' |')
    lines+=['','### Exact outcome by task kind','','| Task kind | Synthetic correct / total | OSS-style correct / total |','|---|---:|---:|']
    for kind in ('consistent','incident','conflict','abstain'):
        cells=[]
        for w in ('test_synth','repo_style'):
            v=results[w]['by_kind'].get(kind,{'strict_correct':0,'items':0})
            cells.append(str(v['strict_correct'])+' / '+str(v['items']))
        lines.append('| '+kind+' | '+' | '.join(cells)+' |')
    lines+=['','### Representative raw failures','']
    for world,r in results.items():
        for reason,e in r['examples'].items():
            lines += [f'**{world}: {reason}, {e["task_id"]}**','',e['question'],'','```text',e['raw_final'],'```','',f'Gold status/value: `{e["expected_status"]}` / `{e["gold_value"]}`; executed calls: {e["tool_calls"]}.','']
    summary_path=out/'summary.json'
    if summary_path.exists():
        summary=json.loads(summary_path.read_text())
        lines+=['## Native AuditKIT tool diagnostics','','These are means without bootstrap intervals. Tool-selection F1 matches tool names against the scripted reference; it is not SQL semantic equivalence or outcome correctness. Schema validity is computed only on samples with tool calls.','','| Metric | Synthetic | OSS-style |','|---|---:|---:|']
        for key in ('tool_call_precision_name','tool_call_recall_name','tool_call_f1_name','tool_call_exact_name','tool_call_validity','redundant_tool_calls'):
            lines.append('| '+key+' | '+' | '.join(f'{summary[w]["auditkit_headline"].get(key,float("nan")):.4f}' for w in ('test_synth','repo_style'))+' |')
        lines.append('')
    text='\n'.join(lines)+'\n';(out/'diagnostics.md').write_text(text)
    paths=[out/'RESULTS.md']
    if out.resolve()==Path('reports/v1/base_fire_nf4').resolve(): paths.append(Path('docs/archive/RESULTS.md'))
    for path in paths:
        if path.exists():
            original=path.read_text().split('\n## Descriptive output diagnostics')[0]
            path.write_text(original.rstrip()+'\n\n'+text)
    print(json.dumps({w:r['counts'] for w,r in results.items()},indent=2))
if __name__=='__main__':main()
