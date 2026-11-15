"""Paired NF4/FP16 findings from complete, identical frozen task cohorts."""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import re
from .evaluate_auditkit import verify_manifest,select_tasks,measure,bootstrap_ratio
from .reward import normalize_val,outcome_ok

FILES={'test_synth':'holdout_synth_400_frozen.jsonl','repo_style':'holdout_repo_style_100_frozen.jsonl'}
CONTROL_FIELDS=('model','revision','max_new_tokens','max_tool_calls','seed','temperature','dataset_hashes','limit','sample_per_language','worlds','batch_size','sdpa_expand_kv')

def check_configs(a,b,ignore_worlds=False):
    for field in CONTROL_FIELDS:
        if ignore_worlds and field=='worlds': continue
        if a.get(field)!=b.get(field): raise ValueError('unmatched comparison setting: '+field)
    if a['quantization']!='4bit' or b['quantization']!='fp16': raise ValueError('expected NF4 reference and FP16 candidate')

def features(task,episode):
    base=measure(task,episode);errors=[];obj={}
    matches=re.findall(r'<final_answer>(.*?)</final_answer>',episode.get('final_text',''),re.S)
    if len(matches)==1:
        try:
            value=json.loads(matches[0])
            if isinstance(value,dict): obj=value
        except ValueError: pass
    if obj:
        if set(obj)!={'status','value','cites','stale_source'}:errors.append('missing_or_extra_final_fields')
        if obj.get('value')=='null':errors.append('quoted_null')
        if obj.get('status')!=task['expected_status']:errors.append('wrong_status')
        if 'value' not in obj or normalize_val(obj['value'])!=normalize_val(task['gold_value']):errors.append('wrong_value')
        cites=obj.get('cites',[])
        if not isinstance(cites,list) or not all(isinstance(c,str) for c in cites):errors.append('invalid_citation_field')
        elif any(c not in episode['retrieved_ids'] for c in cites):errors.append('unretrieved_citations')
    elif episode['completion_reason']=='malformed_output':errors.append('no_parseable_final_json')
    if base['tool_errors']:errors.append('tool_execution_error')
    if any(isinstance(c['output'],list) and not c['output'] for c in episode['calls']):errors.append('empty_search_result')
    if task['gold_cites'] and not set(task['gold_cites'])<=set(episode['retrieved_ids']):errors.append('required_evidence_missing')
    if episode['completion_reason']=='tool_budget_exhausted':errors.append('tool_budget_exhausted')
    return dict(base,raw_value=float('value' in obj and normalize_val(obj['value'])==normalize_val(task['gold_value'])),raw_status=float(obj.get('status')==task['expected_status']),raw_status_value=float('value' in obj and outcome_ok(obj,task)),evidence_complete=float(bool(task['gold_cites']) and set(task['gold_cites'])<=set(episode['retrieved_ids'])),errors=sorted(set(errors)))

def load_run(path,config,world,allow_partial=False):
    tasks=[json.loads(l) for l in (Path('docs/archive/data_v1')/FILES[world]).read_text().splitlines()]
    tasks=select_tasks(tasks,config.get('sample_per_language',0))
    if config['limit']:tasks=tasks[:config['limit']]
    episodes=[json.loads(l) for l in (path/(world+'_episodes.jsonl')).read_text().splitlines()]
    idx={e['task_id']:e for e in episodes}
    expected={t['task_id'] for t in tasks}
    if len(idx)!=len(episodes) or not set(idx)<=expected:raise ValueError('duplicate or unexpected task cohort: '+str(path))
    if not allow_partial and set(idx)!=expected:raise ValueError('incomplete task cohort: '+str(path))
    if allow_partial:
        tasks=[t for t in tasks if t['task_id'] in idx]
        if not tasks:raise ValueError('no completed episodes: '+str(path))
    if any(idx[t['task_id']]['messages'][:2]!=t['prompt'] for t in tasks):raise ValueError('episode prompt differs from frozen prompt')
    return tasks,[idx[t['task_id']] for t in tasks]

def mean(rows,key):
    vals=[r[key] for r in rows if r[key] is not None]
    return sum(vals)/len(vals) if vals else None

def format_rate(v):return 'N/A' if v is None else f'{100*v:.2f}%'

def compare(reference,candidate,output,worlds_override=None,allow_partial=False):
    hashes=verify_manifest(Path('docs/archive/data_v1'))
    a=json.loads((reference/'run_config.json').read_text());b=json.loads((candidate/'run_config.json').read_text());check_configs(a,b,ignore_worlds=worlds_override is not None)
    if a['dataset_hashes']!=hashes:raise ValueError('run dataset hashes differ from current frozen manifest')
    worlds=worlds_override or a.get('worlds',list(FILES));summary={};all_examples=[]
    lines=['# NF4 versus FP16: paired Tiny Aya Fire findings','', 'The two runs use identical frozen questions, prompts, greedy decoding, tool budgets and batch size. No answer repair is used. Descriptive raw-JSON scores ignore schema requirements but still compare exact scalar values.','',f'Model commit: `{a["revision"]}`. Batch size: {a["batch_size"]}. Sample per language: {a.get("sample_per_language","full holdout")}.','', 'Intervals below are 95% paired semantic-case bootstrap intervals for FP16 minus NF4, with 10,000 resamples. A small pilot is exploratory; a wide interval or unchanged score does not establish equivalence. Batch differences versus the older batch-16 NF4 run are controlled by rerunning NF4 here.','']
    if allow_partial: lines+=['**Partial-run analysis:** only completed FP16 episodes are included and matched to the same NF4 task IDs. Missing episodes are not counted as failures or successes. A prefix of the holdout may have biased language/task coverage; this is not a full-holdout result.','']
    for world in worlds:
        tasks,ea=load_run(reference,a,world);tb,eb=load_run(candidate,b,world,allow_partial=allow_partial)
        total_expected=len(tasks)
        if allow_partial:
            paired={t['task_id'] for t in tb}
            aligned=[(t,e) for t,e in zip(tasks,ea) if t['task_id'] in paired]
            tasks=[t for t,e in aligned];ea=[e for t,e in aligned]
        if [t['task_id'] for t in tasks]!=[t['task_id'] for t in tb]:raise ValueError('task pairing failed')
        fa=[features(t,e) for t,e in zip(tasks,ea)];fb=[features(t,e) for t,e in zip(tasks,eb)]
        lines += [f'## {world}: {len(tasks)} paired questions ({total_expected} expected in reference cohort)','', '| Metric | NF4 | FP16 | FP16 − NF4, pp [95% CI] |','|---|---:|---:|---:|']
        metrics={}
        for key in ('exact_outcome','format_valid','raw_value','raw_status','raw_status_value','stale_catch','verified_citation_f1','distractor_immunity'):
            rows=[dict(case_id=t['case_id'],delta=y[key]-x[key]) for t,x,y in zip(tasks,fa,fb) if x[key] is not None and y[key] is not None]
            delta=bootstrap_ratio(rows,lambda r:r['delta'],lambda r:1.) if rows else {'estimate':None,'ci95':[None,None]}
            left=mean(fa,key);right=mean(fb,key);metrics[key]={'nf4':left,'fp16':right,'paired_delta':delta}
            diff='N/A' if delta['estimate'] is None else f'{100*delta["estimate"]:+.2f} [{100*delta["ci95"][0]:+.2f}, {100*delta["ci95"][1]:+.2f}]'
            lines.append(f'| {key} | {format_rate(left)} | {format_rate(right)} | {diff} |')
        counts={label:dict(Counter(error for row in features_ for error in row['errors'])) for label,features_ in [('nf4',fa),('fp16',fb)]}
        lines += ['','### Failure counts (categories can overlap)','','| Failure | NF4 | FP16 |','|---|---:|---:|']
        for error in sorted(set(counts['nf4'])|set(counts['fp16']),key=lambda k:-(counts['nf4'].get(k,0)+counts['fp16'].get(k,0))):lines.append(f'| {error} | {counts["nf4"].get(error,0)} | {counts["fp16"].get(error,0)} |')
        breakdown={}
        for group in ('language','kind'):
            lines += ['',f'### By {group}','','| Group | N | NF4 valid format | FP16 valid format | NF4 exact outcome | FP16 exact outcome |','|---|---:|---:|---:|---:|---:|']
            breakdown[group]={}
            for value in sorted({t[group] for t in tasks}):
                xs=[r for t,r in zip(tasks,fa) if t[group]==value];ys=[r for t,r in zip(tasks,fb) if t[group]==value]
                record={'n':len(xs),'nf4_format':mean(xs,'format_valid'),'fp16_format':mean(ys,'format_valid'),'nf4_outcome':mean(xs,'exact_outcome'),'fp16_outcome':mean(ys,'exact_outcome')};breakdown[group][value]=record
                lines.append(f'| {value} | {len(xs)} | {format_rate(record["nf4_format"])} | {format_rate(record["fp16_format"])} | {format_rate(record["nf4_outcome"])} | {format_rate(record["fp16_outcome"])} |')
        wins=sum(y['format_valid']>x['format_valid'] for x,y in zip(fa,fb));losses=sum(y['format_valid']<x['format_valid'] for x,y in zip(fa,fb))
        lines += ['',f'Format validity improves on {wins} questions and regresses on {losses}.', '']
        top=sorted(counts['fp16'],key=counts['fp16'].get,reverse=True)[:3]
        lines += ['Most frequent remaining FP16 failure categories: '+(', '.join(f'{k} ({counts["fp16"][k]}/{len(tasks)})' for k in top) or 'none observed')+'.','']
        for t,x,y,e1,e2 in zip(tasks,fa,fb,ea,eb):
            if len(all_examples)<6 and (x['format_valid']!=y['format_valid'] or x['raw_value']!=y['raw_value'] or len(all_examples)<2):
                all_examples.append({'task_id':t['task_id'],'question':t['question'],'gold_value':t['gold_value'],'expected_status':t['expected_status'],'nf4_final':e1['final_text'],'fp16_final':e2['final_text'],'nf4_errors':x['errors'],'fp16_errors':y['errors']})
        summary[world]={'n':len(tasks),'reference_cohort_n':total_expected,'partial':len(tasks)!=total_expected,'metrics':metrics,'failures':counts,'breakdown':breakdown,'format_improved':wins,'format_regressed':losses}
    lines+=['## Interpretation','','A meaningful format improvement in FP16 supports quantization contributing under this protocol. Persistent missing fields, quoted nulls or invalid tags suggest a protocol-following gap. Valid JSON with wrong status/value, SQL errors, missing evidence or fabricated citations identifies additional tool-use/reasoning gaps. Similar NF4 and FP16 pilot results are evidence from this cohort only, not proof that quantization has no effect.','', 'If FP16 improves formatting but strict outcomes remain low, formatting alone does not explain the benchmark failures. The OSS-style holdout, if included, is constructed and cannot establish transfer to real repositories.','', '## Runtime / placement','']
    for label,path in [('NF4',reference),('FP16',candidate)]:
        runtime_path=path/'runtime.json'
        if not runtime_path.exists():runtime_path=path/'runtime_live.json'
        runtime=json.loads((path/'run_config.json').read_text())|json.loads(runtime_path.read_text())
        lines += [label+':','', '```json',json.dumps({k:runtime.get(k) for k in ('quantization','gpu_memory_gib','sdpa_expand_kv','device_map','peak_vram_allocated_gib','generated_tokens_per_second')},indent=2),'```','']
    lines+=['CPU offload changes placement and speed. Throughput differences between offloaded FP16 and GPU-resident NF4 must not be interpreted as a precision-only speed comparison.','', '## Paired examples','']
    for e in all_examples:
        lines += [f'### {e["task_id"]}','',e['question'],'',f'Expected: {e["expected_status"]}, value={e["gold_value"]}.','', 'NF4:','```text',e['nf4_final'][:1600],'```','FP16:','```text',e['fp16_final'][:1600],'```','']
    output.mkdir(parents=True,exist_ok=True)
    (output/'FINDINGS.md').write_text('\n'.join(lines)+'\n');(output/'comparison.json').write_text(json.dumps(summary,indent=2));(output/'paired_examples.json').write_text(json.dumps(all_examples,indent=2,ensure_ascii=False))
    print(output/'FINDINGS.md')

def main():
    p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--worlds',nargs='+',choices=list(FILES));p.add_argument('--allow-partial',action='store_true');a=p.parse_args();compare(a.reference,a.candidate,a.output,a.worlds,a.allow_partial)
if __name__=='__main__':main()
