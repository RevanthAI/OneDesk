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
    root=Path(root)
    folders={'Base (Tiny Aya Fire)':root/'prior_v2/base','v2 SFT (15 steps)':root/'prior_v2/sft','v2 GRPO Stage 1 (120 updates)':root/'stage1_evaluation','v2 GRPO Stage 2 (collapsed)':root/'prior_v2/grpo','v2.1 SFT Warmup':root/'sft_evaluation','v2.1 GRPO Anti-Collapse':root/'grpo_evaluation','v2.1 SFT Full 4-Epoch (ablation)':root/'sft_full_evaluation'}
    summaries={n:json.loads((p/'summary.json').read_text()) for n,p in folders.items()}
    configs=[json.loads((p/'run_config.json').read_text()) for p in folders.values()]
    for key in ('dataset_hashes','model','revision','compute_dtype','quantization','batch_size','max_new_tokens_per_turn','max_context_length','max_tool_calls'):
        if any(c[key]!=configs[0][key] for c in configs):raise ValueError('Unmatched comparison setting: '+key)
    sft=json.loads((root/'sft_training/metadata.json').read_text());gp=json.loads((root/'grpo_training/metadata.json').read_text());out=root/'comparison';out.mkdir(exist_ok=True)
    fmt=lambda m:'N/A' if m['estimate'] is None else '%.2f [%.2f, %.2f]'%(100*m['estimate'],100*m['ci95'][0],100*m['ci95'][1])
    lines=['# DriftGuard: protocol warmup and positive-anchor GRPO','','All seven checkpoints use identical frozen data_v2 cohorts, the same pinned Tiny Aya Fire base, BF16 greedy inference, batch 16 with OOM splitting, context 4096, 192 new tokens per turn and six tool calls. Original evaluations and the full four-epoch adapter remain unchanged; missing base validation and original stage-one holdouts were evaluated in this follow-up.','','Percentages show 95% semantic-case cluster-bootstrap intervals (10,000 resamples); translations remain grouped. These are reviewed synthetic and constructed OSS-style fixtures, not independently verified upstream drift cases.','','## Complete progression','','| Checkpoint | Validation exact outcome | Synthetic exact outcome | OSS-style exact outcome |','|---|---:|---:|---:|']
    for n in folders:lines.append('| '+n+' | '+' | '.join(fmt(summaries[n][sp]['metrics']['exact_outcome']) for sp in ('validation','test_synth','repo_style'))+' |')
    lines+=['','## Training and validation selection','','Warmup ran 60 optimizer steps / 480 exposures, batch 8, LR 1.5e-4, zero truncation at sequence length 2560. The first 60 steps of the original 120-step cosine schedule retain the original six-step LR warmup; stopping at 60 does not force LR to zero. Candidates 45/60 were selected on validation alone (>=90%% format validity, <=40%% abstention; prefer the requested 55–68%% accuracy range). Selected step: %s.'%sft['selected_step'],'','GRPO requested 40+40 active updates; completed %s; selected cumulative step %s. Status: %s; early-stop reason: %s. G=6, temperatures 1.0/1.15, beta .04, LR 5e-6, frozen selected warmup KL reference. Validation every 20 updates; predicted abstention >40%% stops training and restores the best safe validation checkpoint.'%(gp['completed_updates'],gp['selected_step'],gp['status'],gp['early_stop']),'','If GRPO selects step zero, its adapter is unchanged warmup SFT and there is no demonstrated RL gain. The final un-restored policy is retained separately.']
    smoke=root/'grpo_training/stage1/smoke_gate.json'
    if smoke.exists():
        g=json.loads(smoke.read_text());lines+=['','## Five-update operational smoke gate','','Accepted %s/%s groups (%.2f%% versus historical 6/72 = 8.33%%); finite gradients: %s; passed: %s; peak reserved VRAM %.2f GiB.'%(g['accepted_updates'],g['attempted_groups'],100*g['acceptance_rate'],g['finite_gradients'],g['passed'],g['peak_reserved_gib'])]
    else:lines+=['','Five-update smoke gate was not reached; see early-stop reason and attempted groups.']
    lines+=['','## Metrics by cohort','','| World | Metric | '+' | '.join(folders)+' |','|---|---|'+'---:|'*len(folders)]
    paired={}
    for split in ('validation','test_synth','repo_style'):
        for metric in ('exact_outcome','stale_catch','verified_citation_f1','format_valid','required_chain_compliance','abstention_precision','abstention_recall','unplugged_recall','distractor_immunity'):
            lines.append('| '+split+' | '+metric+' | '+' | '.join(fmt(summaries[n][split]['metrics'][metric]) for n in folders)+' |')
        for lang in ('en','hi','hinglish','te'):lines.append('| '+split+' | exact_outcome ('+lang+') | '+' | '.join(fmt(summaries[n][split]['metrics']['accuracy_by_language'][lang]) for n in folders)+' |')
        paired[split]={}
        for before,after in (('v2 SFT (15 steps)','v2 GRPO Stage 1 (120 updates)'),('v2 GRPO Stage 1 (120 updates)','v2 GRPO Stage 2 (collapsed)'),('v2.1 SFT Warmup','v2.1 GRPO Anti-Collapse'),('v2.1 SFT Warmup','v2.1 SFT Full 4-Epoch (ablation)')):
            read=lambda n:[json.loads(x) for x in (folders[n]/(split+'_metrics.jsonl')).read_text().splitlines()]
            paired[split][before+' -> '+after]=paired_delta(read(before),read(after))
    lines+=['','## Paired accuracy changes','','| World | Comparison | Percentage points [95% CI] |','|---|---|---:|']
    for split,items in paired.items():
        for n,m in items.items():lines.append('| %s | %s | %+.2f [%+.2f, %+.2f] |'%(split,n,100*m['estimate'],100*m['ci95'][0],100*m['ci95'][1]))
    lines+=['','## Interpretation and limits','','The four-epoch model is a behavioral-cloning reference, not a mathematical accuracy ceiling. Zero reward variance does not prove identical text or collapsed token entropy: multiple different traces can earn the same reward, including uniformly wrong traces. New logs record unique assistant sequences and accepted-group sampled-token surprisal (not full distribution entropy). The historical pilot and new smoke test differ in SFT budget, group size and temperatures, so any acceptance improvement cannot be attributed solely to fewer SFT steps.','','The seven-slot answerable to one-slot abstention rotation, dense evidence bridge, required utility chain, and nonzero-variance/positive-anchor rules remain enforced. All three reward variants and skipped attempts are retained. Skipped attempts do not count as optimizer updates. These are selected training samples, not unbiased performance estimates.','','Selection and exploratory comparisons reuse the same small validation set and reviewed holdouts. Results are not a fresh confirmation or a compute-matched causal ablation. We report actual scores even outside the preferred warmup accuracy band and retain old collapse findings.']
    (out/'EXPERIMENT_REPORT.md').write_text('\n'.join(lines)+'\n');write_json(out/'paired_comparison.json',paired)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(20,7),constrained_layout=True)
    colors=['#6b7280','#93c5fd','#f59e0b','#dc2626','#2563eb','#059669','#7c3aed']
    for ax,split in zip(axes,('validation','test_synth','repo_style')):
        values=[summaries[n][split]['metrics']['exact_outcome'] for n in folders];ys=np.array([100*m['estimate'] for m in values]);err=np.array([[ys[i]-100*m['ci95'][0] for i,m in enumerate(values)],[100*m['ci95'][1]-ys[i] for i,m in enumerate(values)]])
        ax.bar(range(len(folders)),ys,color=colors);ax.errorbar(range(len(folders)),ys,yerr=err,fmt='none',color='black',capsize=4);ax.set(xticks=range(len(folders)),xticklabels=['Base','v2 SFT15','v2 GRPO120','v2 collapsed','Warmup','Warmup+GRPO','Full SFT120'],ylim=(0,105),ylabel='Exact outcome (%)',title=split);ax.tick_params(axis='x',rotation=50);ax.grid(axis='y',alpha=.2)
    fig.suptitle('Frozen v2 progression: 95% semantic-case bootstrap intervals');fig.savefig(out/'comparison.png',dpi=170);fig.savefig(out/'comparison.svg');plt.close(fig)
