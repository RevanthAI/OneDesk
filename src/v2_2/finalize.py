"""Post-download figures and task-kind tables derived only from recorded episodes."""
import argparse,json
from pathlib import Path
import numpy as np
from .evaluation_core import summary_metrics
from .data import write_json
from .manage import protected


def finalize(root=Path('reports_v2_2')):
    root=Path(root)
    completion=json.loads((root/'COMPLETION.json').read_text())
    if completion['status']!='complete':raise ValueError('Refuse to present an incomplete pipeline as completed')
    folders={'Base':root/'prior_v2/base','v2 SFT15':root/'prior_v2/sft','v2 GRPO Stage1':root/'stage1_evaluation','v2 collapsed':root/'prior_v2/grpo','SFT warmup':root/'sft_evaluation','GRPO best':root/'grpo_evaluation','SFT full120':root/'sft_full_evaluation'}
    out=root/'comparison';lines=['','## Task-kind exact outcome breakdown','','Percentages and 95% semantic-case bootstrap intervals; no additional model selection.','','| Cohort / kind | '+' | '.join(folders)+' |','|---|'+'---:|'*len(folders)];detail={}
    for split in ('validation','test_synth','repo_style'):
        detail[split]={}
        rows={n:[json.loads(l) for l in (p/(split+'_metrics.jsonl')).read_text().splitlines()] for n,p in folders.items()}
        for kind in ('conflict','incident','consistent','abstain'):
            values=[];detail[split][kind]={}
            for name,rr in rows.items():
                group=[r for r in rr if r['kind']==kind]
                if not group:values.append('N/A');continue
                m=summary_metrics(group)['exact_outcome'];detail[split][kind][name]=m
                values.append('%.2f [%.2f, %.2f]'%(100*m['estimate'],100*m['ci95'][0],100*m['ci95'][1]))
            lines.append('| '+split+' / '+kind+' | '+' | '.join(values)+' |')
    sft_meta=json.loads((root/'sft_training/metadata.json').read_text())
    if sft_meta.get('validation'):
        lines+=['','## Warmup validation checkpoints','','| Update | Epochs | Exact outcome [95% CI] | Format valid | Predicted abstention | Selected |','|---|---:|---:|---:|---:|---|']
        for v in sft_meta['validation']:
            candidate=json.loads((root/('sft_training/step%03d/validation/summary.json'%v['step'])).read_text())['validation']['metrics']['exact_outcome']
            lines.append('| %s | %.1f | %.2f [%.2f, %.2f] | %.2f%% | %.2f%% | %s |'%(v['step'],v['epoch'],100*candidate['estimate'],100*candidate['ci95'][0],100*candidate['ci95'][1],100*v['format_valid'],100*v['predicted_abstention_rate'],v['step']==sft_meta['selected_step']))
    historical=root/'HISTORICAL_DIVERSITY_CHECK.json'
    if historical.exists():
        h=json.loads(historical.read_text());lines+=['','## Historical diversity check','','Of the old pilot’s 66 zero-variance groups, 62 had identical assistant-token sequences and four had multiple distinct sequences. This is evidence about sampled diversity, not a measurement of full next-token distribution entropy. See HISTORICAL_DIVERSITY_CHECK.json.']
    gp=json.loads((root/'grpo_training/metadata.json').read_text())
    if gp.get('validation'):
        lines+=['','## GRPO validation and selection','','| Cumulative update | Exact outcome [95% CI] | Predicted abstention | Safe | Selected final |','|---|---:|---:|---|---|']
        for v in gp['validation']:
            m=json.loads((root/('grpo_training/validation/step_%03d/summary.json'%v['step'])).read_text())['validation']['metrics']['exact_outcome']
            lines.append('| %s | %.2f [%.2f, %.2f] | %.2f%% | %s | %s |'%(v['step'],100*m['estimate'],100*m['ci95'][0],100*m['ci95'][1],100*v['predicted_abstention_rate'],v['safe'],gp['selected_step']==v['step']))
    handoff=root/'HANDOFF.json'
    if handoff.exists():
        h=json.loads(handoff.read_text());boundary=json.loads((root/'grpo_training/STAGE_BOUNDARY.json').read_text())
        expected=root/'STAGE_BOUNDARY_SOURCE.json'
        if expected.exists():
            original=json.loads(expected.read_text())
            if boundary['policy_sha256']!=original['source_stage1_adapter_sha256'] or h['source_revision']!=original['source_revision']:raise ValueError('Stage-boundary policy or source revision changed')
        lines+=['','## Execution continuity','','Preparation and Stage 1 ran in the first allocation; Stage 2 continued in a second capped L40S allocation. Each had a three-hour timeout. The completed SFT, diagnostics and baseline evaluations were reused unchanged. The first allocation was canceled after its safe 40-update boundary was saved. A preliminary Stage-2 update in that allocation was discarded; the main journal records the retained Stage-1 prefix plus the actually completed Stage-2 updates (counts are reported above). This was a resource handoff, with no hyperparameter or dataset change.','','Source run: `'+h['source_prefix']+'`, immutable revision `'+h['source_revision']+'`. Stage-1 policy SHA-256: `'+boundary['policy_sha256']+'`. The Stage-2 optimizer was fresh by the original two-stage recipe, and the KL reference remained the same selected warmup adapter. Source validation selection and all Stage-1 logs were retained. The first restarted Stage-2 group reproduced the original partial group’s reward, outcome rate, sampled-token count and sampled-token surprisal.']
    lines+=['','## Metric and optimization interpretation','','Exact outcome checks normalized value plus expected status. Citation F1 and required-server chain compliance are separate metrics. Chain compliance measures required server calls; it is not a formal proof that a final calculation was causally derived from each tool result.','','With one optimizer iteration per newly sampled group, the mean-centered policy surrogate can have a scalar value near zero at the on-policy ratio while still producing nonzero gradients. The loss curve must be read alongside gradient norms, KL, parameter changes and validation accuracy. It is not a quality score.']
    lines+=['','## Recorded failure analysis and visualizations','','- [Warmup failure analysis](../sft_evaluation/FAILURE_ANALYSIS.md)','- [GRPO failure analysis](../grpo_evaluation/FAILURE_ANALYSIS.md)','- [Original v2 Stage-1 failure analysis](../stage1_evaluation/FAILURE_ANALYSIS.md)','- [Sampling acceptance and sequence diversity](sampling_diversity.png)','- [Validation accuracy and abstention](validation_progress.png)','- [Training and optimizer diagnostics](../grpo_training/dashboard.html)','- [Filterable recorded rollout traces](../grpo_training/rollout_explorer.html)']
    report=out/'EXPERIMENT_REPORT.md';text=report.read_text().split('\n## Task-kind exact outcome breakdown')[0];report.write_text(text+'\n'.join(lines)+'\n');write_json(out/'task_kind_comparison.json',detail)
    rows=[json.loads(l) for p in sorted((root/'grpo_training').glob('stage*/rollout_metrics.jsonl')) for l in p.read_text().splitlines()]
    if rows:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        active=[r for r in rows if r['optimizer_update_eligible']]
        support=dict(attempted_groups=len(rows),accepted_groups=len(active),acceptance_rate=len(active)/len(rows),all_negative_skipped=sum(r['all_negative_skipped'] for r in rows),zero_variance_skipped=sum(r['zero_variance_skipped'] for r in rows),accepted_mixed_outcomes=sum(0<r['exact_outcome']<1 for r in active),accepted_all_correct=sum(r['exact_outcome']==1 for r in active),accepted_all_wrong_positive_evidence=sum(r['exact_outcome']==0 for r in active),accepted_with_format_errors=sum(r['format_valid']<1 for r in active))
        write_json(out/'FULL_RUN_GROUP_SUPPORT.json',support)
        with report.open('a') as stream:
            stream.write('\n## Full-run sampling support\n\nAccepted %s/%s attempted groups (%.2f%%). Rejected %s zero-variance and %s all-non-positive answerable groups (these categories may overlap). Accepted groups: %s mixed outcome, %s all-correct outcome with process variation, %s all-wrong outcome with positive evidence-retrieval support; %s contained formatting errors. Positive evidence anchors do not require a fully correct answer. These are training sample statistics, not held-out accuracy.\n'%(support['accepted_groups'],support['attempted_groups'],100*support['acceptance_rate'],support['zero_variance_skipped'],support['all_negative_skipped'],support['accepted_mixed_outcomes'],support['accepted_all_correct'],support['accepted_all_wrong_positive_evidence'],support['accepted_with_format_errors']))
        accepted=np.array([bool(r['optimizer_update_eligible']) for r in rows]);x=np.arange(1,len(rows)+1);fig,axes=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
        axes[0].plot(x,100*accepted.cumsum()/x,label='Current cumulative acceptance');axes[0].axhline(100*6/72,color='#d97706',linestyle='--',label='Historical G4 reference (confounded)');axes[0].legend(fontsize=8);axes[0].set(xlabel='Attempted groups',ylabel='Accepted groups (%)',title='Genuine optimizer-eligible groups')
        axes[1].plot(x,[r.get('unique_assistant_sequences',float('nan')) for r in rows],marker='.',linewidth=.7);axes[1].set(xlabel='Attempted groups',ylabel='Distinct assistant-token sequences',title='Observed within-group output diversity',ylim=(0,6.5))
        for ax in axes:ax.grid(alpha=.2)
        fig.suptitle('Training sample diagnostics; not frozen-holdout accuracy or distribution entropy');fig.savefig(out/'sampling_diversity.png',dpi=170);fig.savefig(out/'sampling_diversity.svg');plt.close(fig)
    if gp.get('validation'):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        ss=json.loads((root/'sft_evaluation/summary.json').read_text())['validation']['metrics']['exact_outcome']
        history=[dict(step=0,exact_outcome=ss['estimate'],predicted_abstention_rate=sft_meta['selection']['predicted_abstention_rate'])]+gp['validation']
        points=[ss]+[json.loads((root/('grpo_training/validation/step_%03d/summary.json'%v['step'])).read_text())['validation']['metrics']['exact_outcome'] for v in gp['validation']]
        x=np.array([v['step'] for v in history]);y=np.array([100*m['estimate'] for m in points]);errors=np.array([[y[i]-100*m['ci95'][0] for i,m in enumerate(points)],[100*m['ci95'][1]-y[i] for i,m in enumerate(points)]])
        fig,axes=plt.subplots(1,2,figsize=(12,4.8),constrained_layout=True)
        axes[0].errorbar(x,y,yerr=errors,marker='o',capsize=4,label='Warmup + GRPO validation')
        full=json.loads((root/'sft_full_evaluation/summary.json').read_text())['validation']['metrics']['exact_outcome']['estimate'];axes[0].axhline(100*full,color='grey',linestyle=':',label='Full SFT120 reference');axes[0].scatter([gp['selected_step']],[100*gp['selected_validation_accuracy']],marker='*',s=190,color='#059669',label='Selected best');axes[0].set(ylabel='Exact outcome (%)',title='Validation, with 95% case-bootstrap intervals',ylim=(0,105));axes[0].legend(fontsize=8)
        axes[1].plot(x,[100*v['predicted_abstention_rate'] for v in history],marker='o',color='#d97706');axes[1].axhline(25,color='grey',linestyle=':',label='True validation abstention (25%)');axes[1].axhline(40,color='#dc2626',linestyle='--',label='Early stop above 40%');axes[1].set(ylabel='Predicted abstention (%)',title='Collapse guard',ylim=(0,100));axes[1].legend(fontsize=8)
        for ax in axes:ax.set(xlabel='Cumulative active GRPO updates',xticks=[0,20,40,60,80],xlim=(-2,82));ax.grid(alpha=.2)
        fig.suptitle('Validation used for selection; not an independent confirmation set');fig.savefig(out/'validation_progress.png',dpi=170);fig.savefig(out/'validation_progress.svg');plt.close(fig)
    count=protected();write_json(out/'FINAL_VERIFICATION.json',dict(completion=completion,unchanged_frozen_files=count,old_v2_and_full_sft_ablation_preserved=True,postprocessing='Tables and figures computed from saved per-episode metrics and rollout logs; no regeneration or model inference'))
    return str(report.resolve())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('reports_v2_2'));a=p.parse_args();print(finalize(a.root))
