"""Three-way cohort-matched reports and actual result plots, no inferred gains."""
from collections import defaultdict
import json
from pathlib import Path
import numpy as np
from .data import write_json


def paired_delta(a,b,key='exact_outcome'):
    a={r['task_id']:r for r in a};b={r['task_id']:r for r in b}
    if a.keys()!=b.keys():raise ValueError('paired evaluation IDs differ')
    groups=defaultdict(lambda:[0.,0.])
    for tid,r in a.items():
        if r['case_id']!=b[tid]['case_id']:raise ValueError('paired semantic identity differs')
        if r[key] is None:continue
        groups[r['case_id']][0]+=b[tid][key]-r[key];groups[r['case_id']][1]+=1
    arr=np.array(list(groups.values()));weights=np.random.default_rng(20261112).multinomial(len(arr),np.full(len(arr),1/len(arr)),size=10000)
    den=weights@arr[:,1];d=np.divide(weights@arr[:,0],den,out=np.full(len(weights),np.nan),where=den>0)
    return dict(estimate=float(arr[:,0].sum()/arr[:,1].sum()),ci95=np.nanpercentile(d,[2.5,97.5]).tolist(),clusters=len(groups))


def compare(root):
    root=Path(root);folders={'Base':root/'v2_base_fire','SFT':root/'v2_sft_fire','SFT+GRPO':root/'v2_grpo_fire'}
    summaries={name:json.loads((folder/'summary.json').read_text()) for name,folder in folders.items()}
    configs=[json.loads((folder/'run_config.json').read_text()) for folder in folders.values()]
    for field in ('dataset_hashes','compute_dtype','quantization','batch_size','max_new_tokens_per_turn','max_context_length'):
        if any(c[field]!=configs[0][field] for c in configs):raise ValueError('comparison config mismatch: '+field)
    fmt=lambda m:'N/A' if m['estimate'] is None else f'{100*m["estimate"]:.2f} [{100*m["ci95"][0]:.2f}, {100*m["ci95"][1]:.2f}]'
    lines=['# DriftGuard v2: Base, SFT and active-advantage GRPO','','All evaluations use identical approved v2 task IDs, BF16 weights/computation on L40S, greedy decoding, and the same tool/context budgets. Results are not directly comparable to earlier v1/NF4 reports.','','Values are percentages with 95% semantic-case cluster-bootstrap confidence intervals (10,000 resamples). Correlated translations remain together. Degenerate intervals do not imply certainty outside this benchmark.','','| World | Metric | Base | SFT | SFT+GRPO |','|---|---|---:|---:|---:|'];paired={}
    for split in ('test_synth','repo_style'):
        for metric in ('exact_outcome','stale_catch','verified_citation_f1','format_valid','required_chain_compliance','abstention_precision','abstention_recall','unplugged_recall','distractor_immunity'):
            lines.append('| '+split+' | '+metric+' | '+' | '.join(fmt(summaries[name][split]['metrics'][metric]) for name in folders)+' |')
        for lang in ('en','hi','hinglish','te'):
            lines.append('| '+split+' | exact_outcome ('+lang+') | '+' | '.join(fmt(summaries[name][split]['metrics']['accuracy_by_language'][lang]) for name in folders)+' |')
        paired[split]={}
        for before,after in (('Base','SFT'),('SFT','SFT+GRPO')):
            read=lambda name:[json.loads(line) for line in (folders[name]/(split+'_metrics.jsonl')).read_text().splitlines()]
            paired[split][before+' -> '+after]=paired_delta(read(before),read(after))
    lines+=['','## Paired accuracy changes','','| World | Comparison | Change, percentage points [95% CI] |','|---|---|---:|']
    for split,comparisons in paired.items():
        for name,m in comparisons.items():lines.append(f'| {split} | {name} | {100*m["estimate"]:+.2f} [{100*m["ci95"][0]:+.2f}, {100*m["ci95"][1]:+.2f}] |')
    lines+=['','## Scope','','The OSS-style holdout contains domain-valid constructed fixtures, not verified historical upstream changes. Hindi and Telugu include native and romanized text. Independent native-speaker review is not claimed. Required utility-server calls are enforced in evidence-gated rewards and reported separately from scalar/status accuracy. Active filtering and saturated-kind fallback condition the training distribution; inspect attempted and accepted coverage. These approved holdouts have been reviewed during development, so an untouched confirmation set is needed for stronger generalization claims.']
    (root/'RESULTS.md').write_text('\n'.join(lines)+'\n');write_json(root/'paired_comparison.json',paired)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),constrained_layout=True)
    for ax,split in zip(axes,('test_synth','repo_style')):
        values=[summaries[n][split]['metrics']['exact_outcome'] for n in folders];x=np.arange(3)
        y=np.array([v['estimate']*100 for v in values]);err=np.array([[y[i]-v['ci95'][0]*100 for i,v in enumerate(values)],[v['ci95'][1]*100-y[i] for i,v in enumerate(values)]])
        ax.bar(x,y,color=['#6b7280','#2563eb','#059669']);ax.errorbar(x,y,yerr=err,fmt='none',color='black',capsize=4);ax.set(xticks=x,xticklabels=list(folders),ylim=(0,105),ylabel='Exact outcome (%)',title=split);ax.grid(axis='y',alpha=.2)
    fig.suptitle('Approved v2 frozen holdouts: 95% cluster-bootstrap intervals');fig.savefig(root/'comparison.png',dpi=170);fig.savefig(root/'comparison.svg');plt.close(fig)
