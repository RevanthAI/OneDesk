"""Export standalone scientific plots from actual GRPO logs; no fabricated points."""
import argparse,json
from pathlib import Path

def plot_run(root):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    root=Path(root);files=sorted(root.glob('stage*/rollout_metrics.jsonl'))
    if not files:files=sorted(root.glob('rollout_metrics.jsonl'))
    rows=[]
    for file in files:
        for line in file.read_text().splitlines():
            r=json.loads(line);r['phase']=file.parent.name;rows.append(r)
    if not rows:return
    fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    keys=[('mean_reward','Anti-collapse reward'),('exact_outcome','Sampled rollout accuracy'),('zero_variance_fraction','Groups with zero reward variation'),('mean_tool_calls','Tool calls per rollout')]
    for ax,(key,label) in zip(axes.flat,keys):
        ax.plot(range(1,len(rows)+1),[r[key] for r in rows],marker='.',linewidth=1)
        ax.set(xlabel='Rollout batch (chronological)',ylabel=label);ax.grid(alpha=.25)
        if key in ('exact_outcome','zero_variance_fraction'):ax.set_ylim(-.02,1.02)
        for i in range(1,len(rows)):
            if rows[i]['phase']!=rows[i-1]['phase']:ax.axvline(i+.5,color='grey',linestyle='--')
    fig.suptitle('DriftGuard v2.1 GRPO: sampled training rollouts (not held-out accuracy)')
    fig.savefig(root/'training_rollouts.png',dpi=160);fig.savefig(root/'training_rollouts.svg');plt.close(fig)
    logs=[]
    for file in sorted(root.glob('stage*/optimizer_log.jsonl')):
        logs.extend(json.loads(line) for line in file.read_text().splitlines())
    if logs:
        fig,axes=plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
        for ax,key in zip(axes,['loss','kl','grad_norm']):
            points=[(i+1,r[key]) for i,r in enumerate(logs) if isinstance(r.get(key),(float,int))]
            if points:ax.plot(*zip(*points),marker='.')
            ax.set(xlabel='Optimizer log entry',ylabel=key);ax.grid(alpha=.25)
        fig.suptitle('Optimization diagnostics')
        fig.savefig(root/'optimization.png',dpi=160);fig.savefig(root/'optimization.svg');plt.close(fig)
    (root/'dashboard.html').write_text('<!doctype html><meta charset="utf-8"><title>GRPO diagnostics</title><style>body{font:16px sans-serif;max-width:1200px;margin:32px auto}img{width:100%}</style><h1>DriftGuard GRPO diagnostics</h1><p>Actual training rollouts. These curves are not frozen-holdout evaluation results.</p><img src="training_rollouts.svg">'+('<img src="optimization.svg">' if logs else ''))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory');a=p.parse_args();plot_run(a.directory)
