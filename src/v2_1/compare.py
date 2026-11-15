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
    root=Path(root);folders={'Base (v2)':root/'prior_v2/base','v2 SFT (15 steps)':root/'prior_v2/sft','v2 GRPO (collapsed)':root/'prior_v2/grpo','v2.1 SFT':root/'sft_evaluation','v2.1 GRPO best val':root/'grpo_evaluation'}
    summaries={n:json.loads((p/'summary.json').read_text()) for n,p in folders.items()};configs=[json.loads((p/'run_config.json').read_text()) for p in folders.values()]
    for key in ('dataset_hashes','model','revision','compute_dtype','quantization','batch_size','max_new_tokens_per_turn','max_context_length','max_tool_calls'):
        if any(c[key]!=configs[0][key] for c in configs):raise ValueError('Unmatched comparison setting: '+key)
    sft=json.loads((root/'sft_training/metadata.json').read_text());recipe=json.loads((root/'RUN_CONFIG.json').read_text());gp=json.loads((root/'grpo_training/metadata.json').read_text());out=root/'comparison';out.mkdir(exist_ok=True)
    fmt=lambda m:'N/A' if m['estimate'] is None else '%.2f [%.2f, %.2f]'%(100*m['estimate'],100*m['ci95'][0],100*m['ci95'][1])
    lines=['# DriftGuard v2.1 anti-collapse experiment','','All checkpoints use the same frozen v2 cohorts, pinned Tiny Aya Fire base, L40S BF16 greedy inference, batch 16 with OOM splitting, 4,096 context tokens, 192 new tokens per turn and six tool calls. Previous v2 results are copied unchanged.','','Percentages include 95% semantic-case cluster-bootstrap intervals from 10,000 resamples. Translations remain grouped. These are reviewed synthetic and constructed OSS-style fixtures, not an untouched or verified-upstream benchmark.','','SFT budget: four epochs / 120 optimizer steps / effective batch eight. Validation selected the checkpoint at step %s. GRPO requested 60+60 active updates, completed %s, and selected cumulative step %s. Status: %s; reason: %s.'%(sft['selected_step'],gp['completed_updates'],gp['selected_step'],gp['status'],gp['early_stop']),'','If the selected GRPO step is zero, the deployment adapter is the unchanged stronger SFT fallback, not evidence of an RL improvement. Best selection uses validation only.','','| World | Metric | '+' | '.join(folders)+' |','|---|---|'+'---:|'*len(folders)]
    paired={}
    for split in ('test_synth','repo_style'):
        for metric in ('exact_outcome','stale_catch','verified_citation_f1','format_valid','required_chain_compliance','abstention_precision','abstention_recall','unplugged_recall','distractor_immunity'):
            lines.append('| '+split+' | '+metric+' | '+' | '.join(fmt(summaries[n][split]['metrics'][metric]) for n in folders)+' |')
        for lang in ('en','hi','hinglish','te'):lines.append('| '+split+' | exact_outcome ('+lang+') | '+' | '.join(fmt(summaries[n][split]['metrics']['accuracy_by_language'][lang]) for n in folders)+' |')
        paired[split]={}
        for before,after in (('v2 SFT (15 steps)','v2.1 SFT'),('v2 GRPO (collapsed)','v2.1 GRPO best val'),('v2.1 SFT','v2.1 GRPO best val')):
            read=lambda n:[json.loads(x) for x in (folders[n]/(split+'_metrics.jsonl')).read_text().splitlines()]
            paired[split][before+' -> '+after]=paired_delta(read(before),read(after))
    lines+=['','## Paired accuracy changes','','| World | Comparison | Percentage-point change [95% CI] |','|---|---|---:|']
    for split,items in paired.items():
        for name,m in items.items():lines.append('| %s | %s | %+.2f [%+.2f, %+.2f] |'%(split,name,100*m['estimate'],100*m['ci95'][0],100*m['ci95'][1]))
    lines+=['','## Actual sampling configuration','','Group size: %s; temperature: %s; retry temperature: %s. Any handoff is recorded in HANDOFF.json. The preliminary G=4 policy was discarded; its SFT and evaluation artifacts were reused unchanged.'%(gp['group_size'],gp.get('temperature',.8),gp.get('retry_temperature',.95)),'','## Warm-start and GRPO selection','','SFT validation and the exploratory paired gate are in sft_training/metadata.json. GRPO validates every 30 active updates and stops if predicted validation abstention exceeds 40%. The initial selected SFT policy is eligible as the zero-update fallback. Unsafe validation checkpoints cannot replace a safe best checkpoint. The un-restored last policy is retained separately.','','## Reward and sampling','','Every raw rollout logs specified, evidence_gated and anti_collapse rewards. Answerable updates require positive reward support and nonzero within-group variance. Accepted task requests follow conflict/incident/consistent/conflict/incident/conflict/incident/abstain; bounded fallbacks stay within answerable kinds. Deviations and skipped all-negative groups are logged. Seven answerable slots for one abstention slot are not a performance guarantee.','','The explicit stale-bridge formula uses -0.45 (the task prose also mentioned -0.50). False abstention is -0.85 and malformed output is -1.00. With G=4 or G=6 and at least one positive reward, false abstention cannot receive positive group-relative advantage under this reward floor. Reward alone does not provide that guarantee in an all-negative group.','','AlwaysAbstain reward depends on task prevalence: -0.5725 on the frozen 15% abstention holdouts, -0.3875 on balanced validation, and -0.61875 under the nominal 7:1 rotation. We do not force an impossible <-0.50 guarantee on every split.','','## Scope and trade-offs','','The four-epoch SFT and new GRPO recipe change multiple factors together; no single change receives a causal attribution. Stronger SFT has eight times the optimizer updates of v2 SFT and four times the data exposure. GRPO has additional sampled compute. There is no compute-matched continued-SFT control. Selection and repeated inspection reuse the same 20-case validation set and reviewed holdouts; a fresh confirmation set is needed for strong generalization claims. All original v2 collapse reports and frozen data bytes were preserved.']
    (out/'EXPERIMENT_REPORT.md').write_text('\n'.join(lines)+'\n');write_json(out/'paired_comparison.json',paired)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(15,5.8),constrained_layout=True)
    colors=['#6b7280','#93c5fd','#d97706','#2563eb','#059669']
    for ax,split in zip(axes,('test_synth','repo_style')):
        values=[summaries[n][split]['metrics']['exact_outcome'] for n in folders];ys=np.array([100*m['estimate'] for m in values]);err=np.array([[ys[i]-100*m['ci95'][0] for i,m in enumerate(values)],[100*m['ci95'][1]-ys[i] for i,m in enumerate(values)]])
        ax.bar(range(5),ys,color=colors);ax.errorbar(range(5),ys,yerr=err,fmt='none',color='black',capsize=4);ax.set(xticks=range(5),xticklabels=list(folders),ylim=(0,105),ylabel='Exact outcome (%)',title=split);ax.tick_params(axis='x',rotation=30);ax.grid(axis='y',alpha=.2)
    fig.suptitle('Frozen v2 progression: 95% semantic-case bootstrap intervals');fig.savefig(out/'comparison.png',dpi=170);fig.savefig(out/'comparison.svg');plt.close(fig)
