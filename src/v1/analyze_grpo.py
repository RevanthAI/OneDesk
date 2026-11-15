"""Summarize recorded GRPO rollouts and paired training-world validation."""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np


def paired_validation(before,after,resamples=10000):
    a={r['task_id']:r for r in before};b={r['task_id']:r for r in after}
    if len(a)!=len(before) or len(b)!=len(after) or a.keys()!=b.keys():raise ValueError('validation cohorts differ or contain duplicate IDs')
    groups=defaultdict(lambda:[0.,0.])
    flips=Counter()
    for key,r in a.items():
        other=b[key]
        if (r['case_id'],r['language'],r['kind'])!=(other['case_id'],other['language'],other['kind']):raise ValueError('validation identity changed')
        groups[r['case_id']][0]+=other['exact_outcome']-r['exact_outcome'];groups[r['case_id']][1]+=1
        flips['improved' if other['exact_outcome']>r['exact_outcome'] else 'regressed' if other['exact_outcome']<r['exact_outcome'] else 'unchanged']+=1
    values=np.array(list(groups.values()));rng=np.random.default_rng(20261111)
    weights=rng.multinomial(len(values),np.full(len(values),1/len(values)),size=resamples)
    deltas=(weights@values[:,0])/(weights@values[:,1]);lo,hi=np.percentile(deltas,[2.5,97.5])
    return dict(n=len(a),clusters=len(groups),before=sum(r['exact_outcome'] for r in a.values())/len(a),after=sum(r['exact_outcome'] for r in b.values())/len(b),change=values[:,0].sum()/values[:,1].sum(),change_ci95=[float(lo),float(hi)],paired_flips=dict(flips))


def analyze(root):
    from .plot_grpo import plot_run
    root=Path(root);plot_run(root);stage_stats={};records=[]
    from .grpo_trace_viewer import export_viewer
    export_viewer(root)
    for folder in sorted(root.glob('stage*')):
        if not (folder/'rollout_metrics.jsonl').exists():continue
        batches=[json.loads(line) for line in (folder/'rollout_metrics.jsonl').read_text().splitlines()]
        samples=[json.loads(line) for line in (folder/'rollouts.jsonl').read_text().splitlines()]
        stats=dict(batches=len(batches),episodes=len(samples),mean_reward=float(np.mean([r['reward'] for r in samples])),mean_specified_reward=float(np.mean([r['specified_reward'] for r in samples])),zero_variance_fraction=float(np.mean([r['zero_variance_fraction'] for r in batches])),sampled_outcome_accuracy=float(np.mean([r['exact_outcome'] for r in batches])),completion_reasons=dict(Counter(r['episode']['completion_reason'] for r in samples)),by_kind=dict(Counter(r['kind'] for r in samples)),by_language=dict(Counter(r['language'] for r in samples)))
        for sample in samples:
            assert len(sample['input_ids'])==len(sample['assistant_mask'])
            assert sum(sample['assistant_mask'])==sample['sampled_tokens']
        source=Path('docs/archive/data_v1',f'train_grpo_{folder.name}.jsonl')
        if source.exists():
            from .reward import outcome_ok
            task_lookup={t['task_id']:t for t in map(json.loads,source.read_text().splitlines())}
            grouped=defaultdict(list)
            for sample in samples:grouped[(sample['rollout_batch'],sample['group'])].append(sample)
            zero_types=Counter()
            for group in grouped.values():
                if max(r['reward'] for r in group)-min(r['reward'] for r in group)<1e-8:
                    correct=[outcome_ok(r['episode']['prediction'],task_lookup[r['task_id']]) for r in group]
                    zero_types['all_outcomes_correct' if all(correct) else 'all_outcomes_wrong' if not any(correct) else 'mixed_outcomes']+=1
            stats['zero_variance_groups_by_outcome']=dict(zero_types)
        stage_stats[folder.name]=stats
        for batch in batches:records.append(dict(stage=folder.name,**batch))
    metadata=json.loads((root/'run_metadata.json').read_text()) if (root/'run_metadata.json').exists() else {}
    report={'run_status':metadata.get('status','in_progress_or_incomplete'),'stage_statistics':stage_stats}
    if records:
        with (root/'rollout_metrics.csv').open('w') as f:
            writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    if (root/'before_validation.json').exists() and (root/'after_validation.json').exists():
        before=json.loads((root/'before_validation.json').read_text())['episodes'];after=json.loads((root/'after_validation.json').read_text())['episodes']
        report['validation']=paired_validation(before,after)
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,axes=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
        for ax,key in zip(axes,['language','kind']):
            labels=sorted({r[key] for r in before});xs=np.arange(len(labels));before_values=[];after_values=[]
            for label in labels:
                a=[r['exact_outcome'] for r in before if r[key]==label];b=[r['exact_outcome'] for r in after if r[key]==label]
                before_values.append(100*np.mean(a));after_values.append(100*np.mean(b))
            ax.bar(xs-.18,before_values,.36,label='SFT (before)');ax.bar(xs+.18,after_values,.36,label='GRPO (after)')
            ax.set(xticks=xs,xticklabels=labels,ylim=(0,105),ylabel='Exact outcome (%)',title='By '+key);ax.legend();ax.grid(axis='y',alpha=.2)
        fig.suptitle(f'Training-world validation only: {len(before)} questions / {len({r["case_id"] for r in before})} cases')
        fig.savefig(root/'validation_comparison.png',dpi=160);fig.savefig(root/'validation_comparison.svg');plt.close(fig)
        dashboard=root/'dashboard.html'
        if dashboard.exists():dashboard.write_text(dashboard.read_text()+'<h2>Paired training-world validation</h2><p>This small diagnostic is separate from the frozen 500-question benchmark.</p><img src="validation_comparison.svg">')
    (root/'analysis.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# GRPO recorded experiment diagnostics','',f'Run status: `{report["run_status"]}`.','', 'Training rollouts are sampled at temperature 0.8; validation is greedy. Stage task mixtures differ. Their average rewards are not directly comparable learning curves.','','| Stage | Updates/groups | Sampled episodes | Mean reward | Sampled accuracy | Zero-variance groups |','|---|---:|---:|---:|---:|---:|']
    for name,s in stage_stats.items():lines.append(f'| {name} | {s["batches"]} | {s["episodes"]} | {s["mean_reward"]:.4f} | {100*s["sampled_outcome_accuracy"]:.2f}% | {100*s["zero_variance_fraction"]:.2f}% |')
    lines+=['', 'Zero-variance groups can reflect either an already successful policy or failure to explore a correct action. The breakdown is retained separately in `analysis.json`; identical rewards alone do not establish entropy collapse.']
    if 'validation' in report:
        v=report['validation'];lines+=['','## Paired training-world validation','',f'SFT: {100*v["before"]:.2f}%; GRPO: {100*v["after"]:.2f}%. Change: {100*v["change"]:+.2f} percentage points; 95% paired semantic-case bootstrap interval [{100*v["change_ci95"][0]:+.2f}, {100*v["change_ci95"][1]:+.2f}] points (10,000 resamples).', '', f'Paired changes: {v["paired_flips"]}. There are only {v["clusters"]} cases / {v["n"]} correlated translations. This does not replace the full frozen holdout evaluation.']
    lines+=['','Evidence: `analysis.json`, `rollout_metrics.csv`, per-stage optimizer/rollout logs, model-generated tokens and masks, and before/after validation traces. No oracle actions were substituted into training rollouts.']
    (root/'ANALYSIS.md').write_text('\n'.join(lines)+'\n')
    files=[f for f in root.rglob('*') if f.is_file() and '.cache' not in f.parts and f.name!='ANALYSIS_SHA256SUMS']
    (root/'ANALYSIS_SHA256SUMS').write_text('\n'.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(root).as_posix() for f in sorted(files))+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory');a=p.parse_args();analyze(a.directory)
