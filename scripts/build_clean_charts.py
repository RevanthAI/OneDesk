"""Build four CPU-only publication figures from existing saved benchmark JSON."""
PROJECT_NAME = 'OneDesk'

import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/onedesk-matplotlib')
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from clean_report_data import ROOT, summaries, rows, roi, fmt, protect, digest

BASE = '#94a3b8'
SFT = '#3b82f6'
FAILED = '#ef4444'
FINAL = '#10b981'
INK = '#0f172a'
OUT = ROOT / 'figures'


def style():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12, 'axes.titlesize': 15,
                         'axes.labelsize': 12, 'xtick.labelsize': 11, 'ytick.labelsize': 12,
                         'legend.fontsize': 11, 'figure.facecolor': 'white', 'axes.facecolor': 'white',
                         'text.color': INK, 'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
                         'svg.fonttype': 'none', 'savefig.facecolor': 'white'})


def clean(ax, horizontal=False):
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    ax.set_axisbelow(True)
    ax.grid(axis='x' if horizontal else 'y', color='#e2e8f0', linewidth=.8)


def labels(ax, bars, currency=False, horizontal=False):
    for bar in bars:
        val = bar.get_width() if horizontal else bar.get_height()
        label = f'${val:,.2f}' if currency else f'{fmt(val)}%'
        if horizontal:
            ax.annotate(label, (val, bar.get_y() + bar.get_height()/2), xytext=(8, 0), textcoords='offset points', va='center', fontsize=12, weight='bold')
        else:
            ax.annotate(label, (bar.get_x()+bar.get_width()/2, val), xytext=(0, 5), textcoords='offset points', ha='center', fontsize=11, weight='bold')


def save(fig, name, metadata):
    fig.savefig(OUT / (name+'.png'), dpi=300, bbox_inches='tight', pad_inches=.22)
    fig.savefig(OUT / (name+'.svg'), dpi=300, bbox_inches='tight', pad_inches=.22)
    plt.close(fig)
    return dict(name=name, **metadata, png_sha256=digest(OUT/(name+'.png')), svg_sha256=digest(OUT/(name+'.svg')))


def headline(ss):
    fig, ax = plt.subplots(figsize=(16, 8))
    fig.subplots_adjust(top=.73, bottom=.20, left=.07, right=.99)
    fig.suptitle(f'{PROJECT_NAME}: From Near-Zero Base Model to Reliable Company Knowledge Agent', fontsize=20, weight='bold', y=.97)
    fig.text(.5, .91, 'Performance across 500 held-out company queries (Synthetic & Repo-Style Benchmarks)', ha='center', fontsize=14)
    keys = ['Base', 'Warmup SFT · 60 steps', 'Final OneDesk · selected update 40']
    names = ['Untrained Base Model\n(Tiny Aya Fire 3.35B)', 'Warmup Fine-Tuning\n(2-Epoch SFT)', f'Final {PROJECT_NAME} Agent\n(Warmup + Smart RL)']
    x=np.arange(4); width=.24; data={}
    for offset, (key, name, color) in enumerate(zip(keys,names,[BASE,SFT,FINAL])):
        sm=ss[key]; vals=[100*sm['test_synth']['metrics']['exact_outcome']['estimate'],100*sm['repo_style']['metrics']['exact_outcome']['estimate'],100*sm['test_synth']['metrics']['stale_catch']['estimate'],100*sm['test_synth']['metrics']['format_valid']['estimate']]
        labels(ax, ax.bar(x+(offset-1)*width, vals, width, color=color, label=name, zorder=3));data[key]=vals
    ax.set(xticks=x, xticklabels=['Synthetic\naccuracy', 'Repo-style\naccuracy', 'Catching outdated docs\n(synthetic conflicts)', 'Valid response format\n(synthetic)'], ylim=(0,114), ylabel='Queries meeting the metric (%)')
    clean(ax);fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.53,.86),ncol=3,frameon=False)
    fig.text(.07,.045,'Accuracy = correct status + exact value. Strict outdated-doc catch also requires the stale page and all gold citations.\n500 holdouts = 400 synthetic + 100 repo-style; the last two metrics use the indicated synthetic subsets.',fontsize=11)
    return save(fig,'1_headline_success',dict(values=data,cohort='Frozen data_v2 holdouts; displayed labels round exact estimates'))


def multilingual(ss):
    fig, axes=plt.subplots(1,2,figsize=(19,8.5));fig.subplots_adjust(top=.78,bottom=.20,left=.16,right=.97,wspace=.38)
    fig.suptitle(f'{PROJECT_NAME} Across Languages: Ask in English, Hindi, Hinglish, or Telugu',fontsize=21,weight='bold',y=.98)
    fig.text(.5,.92,'Exact answer accuracy (%) on held-out queries before vs. after training',ha='center',fontsize=14)
    names=['English\nLatin','Hindi\nDevanagari & Latin','Hinglish\nCode-mixed','Telugu\nNative & Latin']; langs=['en','hi','hinglish','te']; data={}
    keys=['Base','Warmup SFT · 60 steps','Final OneDesk · selected update 40']
    model_names={'Base':'Untrained Base Model','Warmup SFT · 60 steps':'Warmup Fine-Tuning (2-Epoch SFT)','Final OneDesk · selected update 40':f'Final {PROJECT_NAME} Agent'}
    for ax,split,title in [(axes[0],'test_synth','Synthetic holdout · 100 queries per language'), (axes[1],'repo_style','Repo-style holdout · 25 queries per language')]:
        y=np.arange(4);width=.23;data[split]={}
        for i,key in enumerate(keys):
            vals=[100*ss[key][split]['metrics']['accuracy_by_language'][lang]['estimate'] for lang in langs]
            off=(i-(len(keys)-1)/2)*width;color=BASE if key=='Base' else SFT if key.startswith('Warmup') else FINAL
            labels(ax,ax.barh(y+off,vals,height=width,color=color,label=model_names[key]),horizontal=True);data[split][key]=vals
        ax.set(yticks=y,yticklabels=names,xlim=(0,105),xlabel='Exact answer accuracy (%)',title=title);ax.invert_yaxis();clean(ax,True)
    handles, labs=axes[0].get_legend_handles_labels();fig.legend(handles,labs,loc='upper center',bbox_to_anchor=(.55,.87),ncol=3,frameon=False)
    fig.text(.16,.055,'Both panels compare the same stages: base, 2-epoch warmup, and final agent. Native and Latin prompts share semantic cases.\nThe final agent matches or improves on warmup across all languages here; the separate full 4-epoch SFT control is reported in REPORT.md.',fontsize=11)
    return save(fig,'2_multilingual_reach',dict(values=data))


def journey(ss):
    fig,(left,right)=plt.subplots(1,2,figsize=(23,10),gridspec_kw={'width_ratios':[1.35,1]})
    fig.subplots_adjust(top=.77,bottom=.25,left=.055,right=.98,wspace=.22)
    fig.suptitle('Our Training Journey: Why Naive RL Failed & How the Sweet-Spot Recipe Won',fontsize=22,weight='bold',y=.98)
    fig.text(.5,.925,'Stronger drift detection through protocol warmup and selective, anti-collapse reinforcement learning',ha='center',fontsize=14)
    keys=['Collapsed RL · 340 updates','Full SFT · 120 steps','Warmup SFT · 60 steps','Final OneDesk · selected update 40'];colors=[FAILED,SFT,SFT,FINAL]
    accuracy=[100*ss[k]['test_synth']['metrics']['exact_outcome']['estimate'] for k in keys]
    catches=[100*ss[k]['test_synth']['metrics']['stale_catch']['estimate'] for k in keys]
    false=[]
    for key in keys:
        metrics=rows(Path(__import__('clean_report_data').FOLDERS[key])/'test_synth_metrics.jsonl')
        false.append(100*sum(r['predicted_abstain'] and not r['expected_abstain'] for r in metrics)/sum(not r['expected_abstain'] for r in metrics))
    x=np.arange(4);width=.23
    labels(left,left.bar(x-width,accuracy,width,color=colors))
    labels(left,left.bar(x,catches,width,color=colors,alpha=.55,hatch='///',edgecolor='white'))
    labels(left,left.bar(x+width,false,width,color='white',edgecolor=FAILED,linewidth=1.8))
    left.set(xticks=x,xticklabels=['Attempt 1\nWeak SFT + long RL\nLazy refusal trap','Attempt 2\nFull 4-epoch SFT\nClone bottleneck','Attempt 3\n2-epoch warmup\nStarting point',f'Final {PROJECT_NAME}\nWarmup +\nanti-collapse RL'],ylim=(0,108),ylabel='Rate (%)',title='Accuracy, outdated-doc catch & false refusal\nSynthetic benchmark')
    clean(left)
    left.legend(handles=[Patch(facecolor=BASE,label='Exact answer accuracy'),Patch(facecolor=BASE,alpha=.55,hatch='///',label='Strict outdated-doc catch'),Patch(facecolor='white',edgecolor=FAILED,label='False refusal · answerable only')],loc='upper center',bbox_to_anchor=(.5,1.28),ncol=1,frameon=False)
    # Keep notes outside the bars: factual distinctions must remain readable.
    fig.text(.055,.10,'LAZY REFUSAL TRAP\n309/400 queries refused (77.3% overall);\n249/340 answerable queries refused (73.2%).',color=FAILED,fontsize=12,weight='bold')
    fig.text(.285,.10,'CLONE BOTTLENECK\n66/72 groups had zero reward variance (91.7%);\n62 of those 66 had identical token sequences.',color=INK,fontsize=12)
    groups=['Synthetic\nbenchmark','Repo-style\nbenchmark','Validation\nset'];xx=np.arange(3);ww=.32
    old=[100*ss['Full SFT · 120 steps'][sp]['metrics']['stale_catch']['estimate'] for sp in ['test_synth','repo_style','validation']]
    new=[100*ss['Final OneDesk · selected update 40'][sp]['metrics']['stale_catch']['estimate'] for sp in ['test_synth','repo_style','validation']]
    labels(right,right.bar(xx-ww/2,old,ww,color=SFT,label='Full 4-Epoch SFT'))
    labels(right,right.bar(xx+ww/2,new,ww,color=FINAL,label=f'Final {PROJECT_NAME} Agent'))
    for a,b,i in zip(old,new,xx):right.text(i,max(a,b)+10,f'+{fmt(b-a)} pp',ha='center',fontsize=13,color='#047857',weight='bold')
    right.set(xticks=xx,xticklabels=groups,ylim=(0,108),ylabel='Strict outdated-doc catch (%)',title='Catching Outdated Runbooks\nConflict resolution')
    clean(right);right.legend(loc='upper center',bbox_to_anchor=(.5,1.25),frameon=False)
    fig.text(.62,.10,'FINAL AGENT\n+15.5 percentage points on synthetic conflicts\nand +10.0 points on repo-style vs. full SFT.',fontsize=13,color='#047857',weight='bold')
    fig.text(.055,.025,'False refusal denominator: answerable synthetic queries. Zero reward variance is not the same as zero text diversity.\nValidation selected update 40 of 80 completed updates. Full SFT retains higher overall holdout accuracy; strict catch is the final agent’s stronger metric.',fontsize=11)
    return save(fig,'3_training_journey',dict(accuracy=accuracy,strict_catch=catches,false_refusal_answerable=false,catch_control=old,catch_final=new))


def cost():
    data=roi();fig,ax=plt.subplots(figsize=(17,9));fig.subplots_adjust(top=.79,bottom=.21,left=.37,right=.89)
    fig.suptitle('Enterprise ROI: ~10× Lower Serving Cost & an On-Premises Option',fontsize=21,weight='bold',y=.98)
    fig.text(.5,.92,'Estimated monthly cost for 100,000 multi-turn company knowledge queries',ha='center',fontsize=14)
    names=[r['name']+'\n'+r['detail'] for r in data]
    bars=ax.barh(np.arange(5),[r['cost'] for r in data],height=.60,color=[FINAL,SFT,BASE,FAILED,FAILED],alpha=.95)
    labels(ax,bars,currency=True,horizontal=True);ax.set(yticks=np.arange(5),yticklabels=names,xlim=(0,1800),xlabel='Estimated monthly serving cost (USD)');ax.invert_yaxis();clean(ax,True)
    ax.axvline(0,color='#cbd5e1',linewidth=.8)
    fig.text(.37,.12,'Electricity-only edge cost excludes hardware, CPU and operations. Cloud cost assumes on-demand use.\nVPC/on-premises deployment controls the data boundary; privacy depends on connectors and logging.',fontsize=11)
    fig.text(.37,.045,'Local: measured v1 NF4 speed, 175 W × $0.10/kWh. L40S: measured v2 BF16 batch throughput.\nT4: unmeasured proxy. APIs: historical uncached prices; Claude 3.5 Sonnet is retired. No API accuracy comparison.',fontsize=11)
    return save(fig,'4_cost_and_privacy_roi',dict(scenarios=data,input_basis=__import__('clean_report_data').read('reports_submission/ROI_SCENARIOS.json')))


def main():
    protect();style();OUT.mkdir(exist_ok=True)
    ss=summaries()
    # Assert the user-facing headline is grounded in the saved, unrounded results.
    assert ss['Final OneDesk · selected update 40']['test_synth']['metrics']['exact_outcome']['estimate']==.7575
    results=[headline(ss),multilingual(ss),journey(ss),cost()]
    (OUT/'CHART_DATA.json').write_text(json.dumps(dict(project=PROJECT_NAME,dpi=300,source='Existing saved JSON only; no inference',charts=results),indent=2)+'\n')
    protect();print(json.dumps({'project':PROJECT_NAME,'charts':4,'png':4,'svg':4,'dpi':300,'output':str(OUT)}))

if __name__=='__main__':main()
