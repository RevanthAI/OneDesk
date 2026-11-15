"""Analyze real attempted/accepted v2 rollouts; never count skipped groups as updates."""
from collections import Counter
import argparse,csv,json
from pathlib import Path
from .data import write_json
from .plot_grpo import plot_run


def analyze(directory):
    directory=Path(directory);plot_run(directory);stats={};records=[]
    for folder in sorted(directory.glob('stage*')):
        file=folder/'rollout_metrics.jsonl'
        if not file.exists():continue
        groups=[json.loads(line) for line in file.read_text().splitlines()]
        accepted=[r for r in groups if r.get('optimizer_update_eligible',not r.get('zero_variance_skipped',False))]
        skipped=[r for r in groups if not r.get('optimizer_update_eligible',not r.get('zero_variance_skipped',False))]
        stats[folder.name]=dict(attempted_groups=len(groups),accepted_groups=len(accepted),skipped_groups=len(skipped),acceptance_rate=len(accepted)/len(groups) if groups else None,kind_fallback_events=sum(r.get('kind_saturated_fallback',False) and r.get('zero_variance_skipped',False) for r in groups),sampling_temperatures=dict(Counter(str(r.get('sampling_temperature',.8)) for r in groups)),mean_attempted_reward=sum(r['mean_reward'] for r in groups)/len(groups) if groups else None)
        stats[folder.name]['all_negative_skipped']=sum(r.get('all_negative_skipped',False) for r in groups)
        stats[folder.name]['skipped_outcome_composition']=dict(Counter('all_outcomes_correct' if r['exact_outcome']==1 else 'all_outcomes_wrong' if r['exact_outcome']==0 else 'mixed_outcomes_skipped' for r in skipped))
        stats[folder.name]['skipped_uniform_rewards']=dict(Counter(format(r['mean_reward'],'.6g') for r in skipped))
        group_info={}
        raw=folder/'rollouts.jsonl'
        if raw.exists():
            with raw.open() as stream:
                for line in stream:
                    row=json.loads(line);group_info.setdefault(row['rollout_batch'],{k:row.get(k) for k in ('kind','language','task_id','case_id')})
            for r in groups:r.update(group_info.get(r['rollout_batch'],{}))
            stats[folder.name]['attempted_by_kind']=dict(Counter(r.get('kind','unknown') for r in groups))
            stats[folder.name]['accepted_by_kind']=dict(Counter(r.get('kind','unknown') for r in accepted))
        summary=folder/'sampler_summary.json'
        if summary.exists():stats[folder.name]['final_sampler']=json.loads(summary.read_text())
        for r in groups:records.append(dict(stage=folder.name,**r))
    if records:
        keys=sorted(set().union(*(r.keys() for r in records)))
        with (directory/'rollout_metrics.csv').open('w') as stream:
            writer=csv.DictWriter(stream,fieldnames=keys);writer.writeheader();writer.writerows(records)
    write_json(directory/'ACTIVE_SAMPLING_ANALYSIS.json',stats)
    lines=['# V2 active sampling diagnostics','','Skipped groups are attempts, not optimizer updates. Training outcomes/rewards are not held-out accuracy.','','| Stage | Attempted groups | Accepted active groups | Skipped groups | Acceptance |','|---|---:|---:|---:|---:|']
    for name,s in stats.items():lines.append(f'| {name} | {s["attempted_groups"]} | {s["accepted_groups"]} | {s["skipped_groups"]} | {100*s["acceptance_rate"]:.2f}% |')
    lines+=['','Uniform rewards do not establish mastery: skipped groups are divided into all-outcomes-correct, all-outcomes-wrong, and mixed outcomes with equal rewards in the JSON report. Correct scalar/status outcomes can still be unsupported under the chain gate. Accepted groups are selected training samples, not an unbiased estimate of model accuracy.','','Temperature and kind-fallback counts, accepted kind coverage and the final saturated-kind set are retained in `ACTIVE_SAMPLING_ANALYSIS.json`. See per-stage raw rollouts for exact model tokens, tool results and rewards.']
    if stats:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        labels=list(stats);x=np.arange(len(labels));fig,axes=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
        axes[0].bar(x-.18,[stats[k]['accepted_groups'] for k in labels],.36,label='Accepted active groups',color='#2563eb')
        axes[0].bar(x+.18,[stats[k]['skipped_groups'] for k in labels],.36,label='Skipped groups',color='#9ca3af')
        axes[0].set(xticks=x,xticklabels=labels,ylabel='Group count',title='Attempts and optimizer-eligible groups');axes[0].legend()
        bottom=np.zeros(len(labels))
        for key,color in [('all_outcomes_correct','#059669'),('all_outcomes_wrong','#d97706'),('mixed_outcomes_skipped','#7c3aed')]:
            values=np.array([stats[k]['skipped_outcome_composition'].get(key,0) for k in labels]);axes[1].bar(x,values,bottom=bottom,label=key.replace('_',' '),color=color);bottom+=values
        axes[1].set(xticks=x,xticklabels=labels,ylabel='Skipped group count',title='Skipped groups: variance or positive-anchor rejection');axes[1].legend(fontsize=8);axes[1].set_ylim(0,max(1,max(bottom))*1.10)
        for ax in axes:ax.grid(axis='y',alpha=.2)
        fig.suptitle('Actual training samples; not held-out accuracy');fig.savefig(directory/'sampling_balance.png',dpi=170);fig.savefig(directory/'sampling_balance.svg');plt.close(fig)
    (directory/'ACTIVE_SAMPLING_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
    return stats

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory');a=p.parse_args();print(json.dumps(analyze(a.directory),indent=2))
