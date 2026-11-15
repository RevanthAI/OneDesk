"""Describe saved evaluation errors without changing datasets or rerunning inference."""
import argparse,json
from collections import Counter
from pathlib import Path
from .data import load,write_json
from .reward import normalize_val


def analyze(directory):
    directory=Path(directory);report={};lines=['# V2 evaluation failure analysis','','Exact outcome requires both the expected status and normalized scalar value. Diagnostic flags below can overlap; they describe saved traces, not causal proof. No holdout was modified or used to retrain.','']
    for split in ('validation','test_synth','repo_style'):
        mf=directory/(split+'_metrics.jsonl');ef=directory/(split+'_episodes.jsonl')
        if not mf.exists() or not ef.exists():continue
        tasks={t['task_id']:t for t in load(split)}
        metrics=[json.loads(x) for x in mf.read_text().splitlines()]
        episodes={e['task_id']:e for e in map(json.loads,ef.read_text().splitlines())}
        flags=Counter();examples=[];breakdowns={}
        for field in ('kind','language','incident_subtype'):
            groups={}
            for m in metrics:
                t=tasks[m['task_id']];key=t.get(field)
                if key is None:continue
                g=groups.setdefault(str(key),dict(n=0,correct=0,format_valid=0,chain_compliant=0))
                g['n']+=1;g['correct']+=int(m['exact_outcome']);g['format_valid']+=int(m['format_valid']);g['chain_compliant']+=int(m.get('required_chain_compliance') or 0)
            breakdowns[field]=groups
        for m in metrics:
            if m['exact_outcome']:continue
            t=tasks[m['task_id']];e=episodes[m['task_id']];p=e.get('prediction') or {};f=[]
            if not m['format_valid']:f.append('invalid_final_format')
            if p:
                if p.get('status')!=t['expected_status']:f.append('wrong_status')
                if normalize_val(p.get('value'))!=normalize_val(t['gold_value']):f.append('wrong_value')
                if p.get('status')=='abstain' and t['expected_status']!='abstain':f.append('unnecessary_abstention')
                if any(str(c).endswith('-STG') for c in p.get('cites',[])):f.append('cites_staging_record')
            if m.get('stale_value_returned'):f.append('returned_stale_value')
            if m.get('tool_errors'):f.append('tool_error')
            if e.get('completion_reason') in ('tool_budget_exhausted','context_budget_exhausted'):f.append(e['completion_reason'])
            flags.update(f)
            if len(examples)<16:examples.append(dict(task_id=t['task_id'],kind=t['kind'],language=t['language'],expected_status=t['expected_status'],gold_value=t['gold_value'],prediction=p,flags=f,raw_turns=e.get('raw_turns',[])))
        report[split]=dict(n=len(metrics),correct=sum(int(m['exact_outcome']) for m in metrics),breakdowns=breakdowns,error_flags=dict(flags),examples=examples)
        lines += ['## '+split,'','| Task kind | Correct / total | Valid final format |','|---|---:|---:|']
        for k,g in breakdowns['kind'].items():lines.append(f"| {k} | {g['correct']}/{g['n']} | {g['format_valid']}/{g['n']} |")
        lines+=['','Observed error flags: '+', '.join(f'{k}: {v}' for k,v in flags.most_common())+'.','','### Saved trace examples','']
        for ex in examples[:6]:
            lines += [f"**{ex['task_id']}** ({ex['kind']}, {ex['language']}): expected {ex['expected_status']} / {ex['gold_value']}; flags: {', '.join(ex['flags'])}.",'','```json',json.dumps(ex['prediction'],ensure_ascii=False),'```','']
    write_json(directory/'FAILURE_ANALYSIS.json',report)
    (directory/'FAILURE_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
    return {s:dict(n=r['n'],correct=r['correct'],error_flags=r['error_flags']) for s,r in report.items()}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory');args=parser.parse_args();print(json.dumps(analyze(args.directory),indent=2))
