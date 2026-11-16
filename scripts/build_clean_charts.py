"""Build CPU-only benchmark charts and static publication flow diagrams."""
PROJECT_NAME = 'OneDesk'

import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/onedesk-matplotlib')
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, FancyBboxPatch, FancyArrowPatch
from clean_report_data import ROOT, summaries, combined_holdouts, rows, roi, fmt, protect, digest

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
                         'text.parse_math': False,
                         'text.color': INK, 'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
                         'svg.fonttype': 'none', 'svg.hashsalt': PROJECT_NAME, 'savefig.facecolor': 'white'})


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
    svg=OUT / (name+'.svg')
    fig.savefig(svg, dpi=300, bbox_inches='tight', pad_inches=.22, metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)
    return dict(name=name, **metadata, png_sha256=digest(OUT/(name+'.png')), svg_sha256=digest(OUT/(name+'.svg')))


def flow_box(ax, x, y, width, height, title, subtitle, color=SFT, dashed=False, title_size=14):
    ax.add_patch(FancyBboxPatch((x,y),width,height,boxstyle='round,pad=0.009,rounding_size=0.018',
                              facecolor=color+'12',edgecolor=color,linewidth=1.7,
                              linestyle='--' if dashed else '-'))
    ax.text(x+width/2,y+height*.66,title,ha='center',va='center',fontsize=title_size,weight='bold')
    ax.text(x+width/2,y+height*.29,subtitle,ha='center',va='center',fontsize=12,color='#475569')


def flow_arrow(ax, start, end, color='#64748b', dashed=False):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=17,linewidth=1.6,
                               color=color,linestyle='--' if dashed else '-',shrinkA=4,shrinkB=4))


def workspace_diagram():
    fig,ax=plt.subplots(figsize=(19,11));fig.subplots_adjust(top=.88,bottom=.10,left=.02,right=.99)
    fig.suptitle(f'{PROJECT_NAME}: Unified 9-Server MCP Workspace',fontsize=23,weight='bold',y=.98)
    fig.text(.5,.925,'One query · production-aware retrieval · real SQL and utility calculations · cited resolution',ha='center',fontsize=14)
    ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    flow_box(ax,.015,.46,.205,.16,'Employee Query','English / Hindi\nHinglish / Telugu',BASE)
    flow_box(ax,.275,.46,.185,.16,PROJECT_NAME,'Tiny Aya Fire 3.35B',SFT,title_size=19)
    flow_arrow(ax,(.22,.54),(.275,.54))
    ax.plot([.465,.505],[.54,.54],color='#64748b',linewidth=1.6)
    ax.plot([.505,.505],[.085,.91],color='#64748b',linewidth=1.4)
    tools=[('notion-mcp','Runbooks & production scope'),('github-mcp','Merged PRs & changes'),
           ('slack-mcp','Deployments & hotfixes'),('db-mcp','Read-only SQLite SELECT'),
           ('time-mcp','Incident durations'),('unit-converter-mcp','kg ↔ lb · decimal GB ↔ MiB'),
           ('math-mcp','Exact rounded costs')]
    ys=[.91,.815,.72,.625,.53,.435,.34]
    for (name,detail),y in zip(tools,ys):
        flow_box(ax,.545,y-.036,.235,.072,name,detail,SFT,title_size=13)
        flow_arrow(ax,(.505,y),(.542,y))
        ax.plot([.79,.815],[y,y],color='#64748b',linewidth=1.3)
    ax.plot([.815,.815],[.34,.91],color='#64748b',linewidth=1.3)
    flow_arrow(ax,(.815,.54),(.85,.54),color=FINAL)
    flow_box(ax,.855,.42,.13,.24,'Verified Answer','Citations\n+ Stale-Page Flag\n(or justified abstention)',FINAL,title_size=14)
    for name,detail,y in [('weather-mcp','Routing distractor',.18),('calendar-mcp','Routing distractor',.085)]:
        flow_box(ax,.545,y-.036,.235,.072,name,detail,BASE,dashed=True,title_size=13)
        flow_arrow(ax,(.505,y),(.542,y),color=BASE,dashed=True)
    fig.text(.05,.035,'Tool observations return to the agent before its next decision. Dashed tools test routing immunity; they do not support the verified answer.',fontsize=12)
    return save(fig,'0_workspace_architecture',dict(type='static_flow_diagram',active_tools=7,routing_distractors=2))


def toolkit_diagram():
    fig,ax=plt.subplots(figsize=(19,6.5));fig.subplots_adjust(top=.82,bottom=.17,left=.02,right=.98)
    fig.suptitle('End-to-End Lexsi Labs Toolkit Chain',fontsize=24,weight='bold',y=.96)
    fig.text(.5,.87,'Facts-first data → protocol warmup and live reinforcement learning → measured agent quality',ha='center',fontsize=14)
    ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    nodes=[(.015,'Python Facts + Oracle','Deterministic gold answers\nExecuted tool trajectories',BASE),
           (.265,'CuratorKIT 0.1.21','1,955 → 1,700 tasks\n255 exact duplicates removed',SFT),
           (.515,'AgentTune 1.1.4','SFT Warmup +\nLive Multi-Turn GRPO',SFT),
           (.765,'AuditKIT 1.1.7','580-Episode Outcome,\nCitation & Tool Evaluation',FINAL)]
    for x,title,subtitle,color in nodes:
        flow_box(ax,x,.28,.215,.43,title,subtitle,color,title_size=15)
    for (x,*_), (next_x,*_) in zip(nodes,nodes[1:]):
        flow_arrow(ax,(x+.225,.49),(next_x-.01,.49))
    fig.text(.5,.075,'Frozen inputs, real multi-turn tool episodes, saved traces and 95% semantic-case bootstrap confidence intervals.',ha='center',fontsize=12)
    return save(fig,'0_toolkit_pipeline',dict(type='static_flow_diagram',toolkits=['CuratorKIT 0.1.21','AgentTune 1.1.4','AuditKIT 1.1.7']))


def headline(ss):
    pooled=combined_holdouts(ss)
    fig, ax = plt.subplots(figsize=(18, 9))
    fig.subplots_adjust(top=.73, bottom=.21, left=.065, right=.99)
    fig.suptitle(f'{PROJECT_NAME}: Combined Holdout Benchmark', fontsize=23, weight='bold', y=.97)
    fig.text(.5,.915,'500 held-out queries · 400 synthetic + 100 repo-style · four training stages',ha='center',fontsize=15)
    keys=['Base','Warmup SFT · 60 steps','Full SFT · 120 steps','Final OneDesk · selected update 40']
    names=['Untrained Base (3.35B)','Warmup SFT (2-Epoch)','Full SFT (4-Epoch)',f'{PROJECT_NAME} Final (Warmup + RL)']
    metrics=['exact_outcome','stale_catch','verified_citation_f1','format_valid']
    colors=[BASE,'#60a5fa','#2563eb',FINAL]
    x=np.arange(4);width=.19;data={}
    for offset,(key,name,color) in enumerate(zip(keys,names,colors)):
        vals=[100*pooled[key][metric]['estimate'] for metric in metrics]
        labels(ax,ax.bar(x+(offset-1.5)*width,vals,width,color=color,label=name,zorder=3));data[key]=vals
    ax.set(xticks=x,xticklabels=['Exact answer accuracy\n(n=500)','Strict stale-doc catch\n(n=250 conflicts)','Verified citation F1\n(n=425)','Valid tool & final format*\n(n=500)'],ylim=(0,117),ylabel='Score (%)')
    ax.annotate('+14.4 pp vs Full SFT!',xy=(1+1.5*width,84),xytext=(1.15,105),ha='center',fontsize=14,weight='bold',color=FINAL,arrowprops={'arrowstyle':'->','color':FINAL,'lw':1.7})
    clean(ax);fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.53,.855),ncol=4,frameon=False,fontsize=12)
    fig.text(.065,.055,'Scores are pooled using each metric’s eligible-task count, not an equal average of the two splits.\n*Format bars measure structured final-answer validity; AuditKIT separately confirms 100% tool-call validity for all trained stages.\nStrict stale catch requires the correct answer, stale-page flag, and every gold source retrieved and cited.',fontsize=11)
    return save(fig,'1_headline_success',dict(values=data,metrics=metrics,pooled=pooled,cohort='Combined 500-query frozen holdout; metric-specific denominators'))


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
    fig.text(.16,.055,'Both panels compare the same stages: base, 2-epoch warmup, and final agent. Native and Latin prompts share semantic cases.\nThe final agent matches or improves on warmup across all languages here; the separate full 4-epoch SFT control is reported in docs/FULL_REPORT.md.',fontsize=11)
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
    data=roi();fig,ax=plt.subplots(figsize=(21,11.5));fig.subplots_adjust(top=.85,bottom=.27,left=.49,right=.90)
    fig.suptitle('Enterprise ROI: Measured Runtime, Throughput & Privacy Options',fontsize=22,weight='bold',y=.98)
    fig.text(.5,.925,'100,000 multi-turn audits/month · 500 held-out traces · all token bills are offline estimates',ha='center',fontsize=14)
    names=[]
    for r in data:
        if r['key']=='edge':
            detail=f"{r['output_tps']:.2f} out / {r['total_tps']:,.0f} total tok/s · {r['hours_100000']:.1f} GPU h/100k\n{r['vram_gib']:.2f} GiB reserved · $0 API · 175 W × $0.10/kWh · n=20 final adapter"
        elif r['key']=='l40s':
            detail=f"$1.80/GPU-h · {r['output_tps']:.1f} out / {r['total_tps']:,.0f} total tok/s (generation)\n{r['hours_100000']:.2f} GPU h/100k · n=580 · organization-controlled VPC option"
        elif r['key']=='t4':
            detail=f"$0.40/GPU-h · {r['output_tps']:.2f} out / {r['total_tps']:,.0f} total tok/s (proxy)\n{r['hours_100000']:.1f} GPU h/100k · token-adjusted edge proxy · NOT measured T4"
        elif r['key']=='gpt4o_cached':
            detail='$1.25–$2.50/M input · $10/M output · eligible prefix-cache hits\nProvider-managed throughput / GPU hours not measured · n=500 saved'
        else:
            detail='$2.50/M input · $10/M output · 4,793.714 in / 147.536 out per audit\nProvider-managed throughput / GPU hours not measured · n=500 saved'
        names.append(r['name']+'\n'+detail)
    bars=ax.barh(np.arange(5),[r['cost'] for r in data],height=.58,color=[FINAL,SFT,BASE,'#fb923c',FAILED],alpha=.95)
    labels(ax,bars,currency=True,horizontal=True)
    ax.set(yticks=np.arange(5),yticklabels=names,xlim=(0,max(r['cost'] for r in data)*1.23),xlabel='Estimated USD / 100,000 audits (electricity only for owned workstation)')
    ax.tick_params(axis='y',labelsize=11,pad=13);ax.invert_yaxis();clean(ax,True)
    ax.axvline(0,color='#cbd5e1',linewidth=.8)
    fig.text(.04,.16,'Rule 5: volume + tokens/sec + GPU hours + hourly prices. L40S end-to-end rate: 61.99 out / 1,937 total tok/s; 1,471 audits/hour.\nL40S prices use full wall time (1,419.402 s); its generation-only rates use 1,302.923 s. Logical input tokens exclude padding.\nLocal: 20 stratified final-adapter NF4 episodes, batch 1. Historical 3.15 GiB is a separate v1 adapter measurement.',fontsize=12)
    fig.text(.04,.055,'GPT-4o same-string o200k counts replace the old Cohere-token $1,316.66 estimate; no actual API invoice or quality parity is asserted.\nCaching assumes in-TTL eligible hits (≥1,024 prefix tokens, 128-token blocks). Privacy depends on VPC, connectors and logging.\nElectricity uses nameplate power, excludes hardware/CPU/idle/operations; T4 speed is unmeasured. Sources and full arithmetic: ROI_VERIFIED_BENCHMARK.json.',fontsize=11)
    return save(fig,'4_cost_and_privacy_roi',dict(scenarios=data,input_basis=__import__('clean_report_data').read('reports/submission/ROI_VERIFIED_BENCHMARK.json')))


def main():
    protect();style();OUT.mkdir(exist_ok=True)
    ss=summaries()
    # Assert the user-facing headline is grounded in the saved, unrounded results.
    assert ss['Final OneDesk · selected update 40']['test_synth']['metrics']['exact_outcome']['estimate']==.7575
    results=[headline(ss),multilingual(ss),journey(ss),cost()]
    (OUT/'CHART_DATA.json').write_text(json.dumps(dict(project=PROJECT_NAME,dpi=300,source='Existing saved JSON only; no inference',charts=results),indent=2)+'\n')
    diagrams=[workspace_diagram(),toolkit_diagram()]
    (OUT/'DIAGRAM_DATA.json').write_text(json.dumps(dict(project=PROJECT_NAME,dpi=300,diagrams=diagrams),indent=2)+'\n')
    protect();print(json.dumps({'project':PROJECT_NAME,'charts':4,'diagrams':2,'png':6,'svg':6,'dpi':300,'output':str(OUT)}))

if __name__=='__main__':main()
