"""Post-run evidence review and optional private sync; never train or infer."""
import argparse,hashlib,json,os,shutil
from pathlib import Path
from .data import verify,write_json
from .compare import paired_delta
from .publication import build


def rows(path):return [json.loads(x) for x in Path(path).read_text().splitlines()]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def review(sync=False):
    root=Path('reports_v2');job=json.loads((root/'LATEST_JOB.json').read_text());cloud=root/'cloud'/job['run_prefix'];download=json.loads((cloud/'downloads.json').read_text())
    assert json.loads((root/'COMPLETION.json').read_text())['status']=='complete'
    verify();frozen=json.loads((root/'APPROVED_DATA_LOCK.json').read_text());assert frozen=={p.name:sha(p) for p in Path('data_v2').iterdir() if p.is_file()}
    manifest=json.loads((cloud/'bundle_manifest.json').read_text());core=['reward.py','active_advantage.py','grpo_core.py','grpo_rollout.py','agenttune_sft_backend.py','agenttune_grpo_backend.py','training.py','evaluation_core.py','backend.py','evaluate_auditkit.py','mcp_env.py','v2_env.py','mcp_adapter.py','preflight.py','pipeline.py']
    checks={n:sha(Path('src_v2',n))==manifest['files']['src_v2/'+n] for n in core}
    if not all(checks.values()):raise ValueError('Published numerical runtime differs from the trained bundle')
    write_json(root/'SOURCE_PROVENANCE.json',dict(bundle_revision=job['bundle_revision'],bundle_sha256=job['bundle_sha256'],numerical_runtime_matches_launch=checks,post_launch_changes='Local retrieval, documentation, diagnostics and publication helpers only'))
    summaries={m:json.loads((root/f'v2_{m}_fire'/'summary.json').read_text()) for m in ('base','sft','grpo')};metrics={m:{w:rows(root/f'v2_{m}_fire'/(w+'_metrics.jsonl')) for w in ('test_synth','repo_style')} for m in summaries}
    details={}
    for world in ('test_synth','repo_style'):
        a=metrics['grpo'][world]
        details[world]=dict(predicted_abstain=sum(r['predicted_abstain'] for r in a),expected_abstain=sum(r['expected_abstain'] for r in a),n=len(a),by_kind={k:dict(n=len(g:=[r for r in a if r['kind']==k]),correct=sum(r['exact_outcome'] for r in g)) for k in ('consistent','incident','conflict','abstain')},paired_accuracy_change=json.loads((root/'paired_comparison.json').read_text())[world]['SFT -> SFT+GRPO'])
    vp=[root/'v2_sft_fire',root/'grpo_validation/after_stage1',root/'grpo_validation/after_stage2'];val=[rows(p/'validation_metrics.jsonl') for p in vp];vs=[sum(r['exact_outcome'] for r in a)/len(a) for a in val];vd={'SFT_to_stage1':paired_delta(val[0],val[1]),'stage1_to_stage2':paired_delta(val[1],val[2]),'SFT_to_final':paired_delta(val[0],val[2])}
    sampling=json.loads((root/'grpo_training/ACTIVE_SAMPLING_ANALYSIS.json').read_text())
    write_json(root/'GRPO_FINDINGS.json',dict(holdouts=details,validation_scores=vs,validation_paired_changes=vd,sampling=sampling,interpretation='Final policy collapsed toward abstention; no statistically supported overall accuracy gain over SFT'))
    lines=['# V2 GRPO findings: abstention collapse','','The complete 340-update experiment ran successfully, but the final policy failed the intended drift-resolution objective. Synthetic stale catch fell from 4% after SFT to 0%; OSS-style stale catch fell from 14% to 0%. Final GRPO solved zero conflict and zero incident tasks in either holdout. This is a negative result, not a successful drift-detection model.','','## Outcomes and uncertainty','','| World | SFT accuracy | Final GRPO accuracy | Paired change, pp [95% CI] |','|---|---:|---:|---:|']
    for w,d in details.items():
        delta=d['paired_accuracy_change'];lines.append('| %s | %.2f%% | %.2f%% | %+.2f [%+.2f, %+.2f] |'%(w,100*summaries['sft'][w]['metrics']['exact_outcome']['estimate'],100*summaries['grpo'][w]['metrics']['exact_outcome']['estimate'],100*delta['estimate'],100*delta['ci95'][0],100*delta['ci95'][1]))
    lines+=['','Both paired intervals include zero. The apparent 2.5-point synthetic accuracy rise does not establish an improvement. On the OSS-style holdout, every correct final answer was an abstention.','','## Measured failure pattern','','| World | Predicted abstain / all queries | Required abstain | Conflict correct | Incident correct |','|---|---:|---:|---:|']
    for w,d in details.items():lines.append('| %s | %s/%s | %s/%s | %s/%s | %s/%s |'%(w,d['predicted_abstain'],d['n'],d['expected_abstain'],d['n'],int(d['by_kind']['conflict']['correct']),d['by_kind']['conflict']['n'],int(d['by_kind']['incident']['correct']),d['by_kind']['incident']['n']))
    lines+=['','Synthetic final-format validity rose from 75% to 98.5%, while required-chain compliance fell from 78.53% to 7.65% and verified-citation F1 fell from 38.27% to 7.06%. OSS-style chain compliance fell from 69.41% to 1.18%. Better formatting and perfect abstention recall masked severe false abstention and loss of evidence use.','','## Validation trajectory','','| Checkpoint | Validation accuracy |','|---|---:|']
    for label,v in zip(('SFT','GRPO stage 1, 120 updates','GRPO stage 2, 340 cumulative updates'),vs):lines.append('| %s | %.2f%% |'%(label,100*v))
    lines+=['','Validation has only 20 independent semantic cases. Its paired changes and intervals are retained in GRPO_FINDINGS.json. Stage one is selected as a candidate by validation alone; its holdout performance was not measured. The requested three-way table remains the final 340-update adapter, with no checkpoint substitution.','','## Sampling and optimization','','| Stage | Attempts | Active updates | All-correct skipped | All-wrong skipped |','|---|---:|---:|---:|---:|']
    for stage,d in sampling.items():lines.append('| %s | %s | %s | %s | %s |'%(stage,d['attempted_groups'],d['accepted_groups'],d['skipped_outcome_composition'].get('all_outcomes_correct',0),d['skipped_outcome_composition'].get('all_outcomes_wrong',0)))
    lines+=['','Both stages retained exact accepted-kind balance: 30 updates per kind in stage one, 55 per kind in stage two. Stage two used seven temperature-0.95 groups. No kind exhausted all 32 retries, so fallback was covered by tests rather than triggered in this run. Dynamic filtering prevented fake zero-signal updates, but it did not prevent collapse. The frozen SFT reference had zero measured weight change, and logged losses/gradient norms were finite.','','## Plausible mechanism and limits','','The evidence-gated reward gives a valid wrong answer -0.2, malformed finals -0.8, and correct abstentions +1. Abstaining can therefore beat risky malformed tool trajectories. Once a group uniformly abstains on an answerable prompt, its negative rewards have zero relative advantage; active filtering skips that group without a corrective optimizer update. This is consistent with the observed collapse, but this run does not isolate causality. The utility-chain gate passed its regression tests and prevented full reward for unsupported calculations; it did not make the complete reward objective ungameable.','','The cold-start was deliberately small (240 rows, one epoch, 15 updates). GRPO sampled 3,232 training rollouts across 808 groups, compared with 240 SFT trajectories. A compute-matched continued-SFT control is absent. Model limitations, exploration, reward asymmetry and the weak warm start are not separated by this experiment.','','## Follow-up experiment proposals, not executed','','Use validation-based early stopping; separately confirm the saved stage-one checkpoint. Compare against additional SFT at a matched compute budget. Explicitly test false-abstention penalties and successful-tool-trajectory anchors, while keeping evaluation separate. Check sampled task coverage and all-wrong skipped groups, rather than accepting nonzero reward variance as sufficient evidence of useful learning. Any revised recipe needs a fresh confirmation set for strong generalization claims. No extra paid training or model evaluation was launched for these proposals.','','See [failure_modes.png](failure_modes.png), [sampling balance](grpo_training/sampling_balance.png), per-model FAILURE_ANALYSIS.md, raw rollouts and TensorBoard logs.']
    (root/'GRPO_FINDINGS.md').write_text('\n'.join(lines)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig,axes=plt.subplots(2,2,figsize=(13,9),constrained_layout=True);colors={'sft':'#2563eb','grpo':'#d97706'}
    for ax,w in zip(axes[0],('test_synth','repo_style')):
        kinds=['consistent','incident','conflict','abstain'];x=np.arange(4)
        for shift,m,label in ((-.18,'sft','SFT'),(.18,'grpo','Final GRPO')):
            values=[100*sum(r['exact_outcome'] for r in metrics[m][w] if r['kind']==k)/sum(r['kind']==k for r in metrics[m][w]) for k in kinds];ax.bar(x+shift,values,.36,label=label,color=colors[m])
        ax.set(xticks=x,xticklabels=kinds,ylim=(0,105),ylabel='Exact outcome (%)',title=w);ax.legend()
    keys=['format_valid','verified_citation_f1','required_chain_compliance','stale_catch'];labels=['Valid format','Verified citations','Required chain','Stale catch'];x=np.arange(4)
    for shift,m,label in ((-.18,'sft','SFT'),(.18,'grpo','Final GRPO')):axes[1,0].bar(x+shift,[100*summaries[m]['test_synth']['metrics'][k]['estimate'] for k in keys],.36,label=label,color=colors[m])
    axes[1,0].set(xticks=x,xticklabels=labels,ylim=(0,105),ylabel='Metric (%)',title='Synthetic: format improved, evidence use regressed');axes[1,0].tick_params(axis='x',labelrotation=15)
    x=np.arange(2)
    for shift,m,label in ((-.25,'sft','SFT predicted'),(0,'grpo','GRPO predicted')):axes[1,1].bar(x+shift,[100*sum(r['predicted_abstain'] for r in metrics[m][w])/len(metrics[m][w]) for w in ('test_synth','repo_style')],.24,label=label,color=colors[m])
    axes[1,1].bar(x+.25,[15,15],.24,color='#059669',label='Actually required');axes[1,1].set(xticks=x,xticklabels=['Synthetic','OSS-style'],ylim=(0,105),ylabel='Abstention rate (%)',title='False abstention dominates');axes[1,1].legend()
    for ax in axes.flat:ax.grid(axis='y',alpha=.2)
    fig.suptitle('Final v2 GRPO: improved protocol formatting, failed drift resolution');fig.savefig(root/'failure_modes.png',dpi=170);fig.savefig(root/'failure_modes.svg');plt.close(fig)
    original=(root/'EXPERIMENT_REPORT.md').read_text().split('\n<!-- V2_REVIEW -->')[0]
    lead='**Primary finding: the final GRPO policy collapsed toward abstention. Stale-doc catch is 0% on both holdouts; its overall accuracy change versus SFT is not statistically supported.**\n\n'
    if lead not in original:original=original.replace('# DriftGuard-MCP v2 experiment report\n\n','# DriftGuard-MCP v2 experiment report\n\n'+lead)
    (root/'EXPERIMENT_REPORT.md').write_text(original+'\n<!-- V2_REVIEW -->\n\n## Detailed interpretation\n\nSee [GRPO_FINDINGS.md](GRPO_FINDINGS.md) for the collapse evidence, validation trajectory, all-wrong skipped groups and unexecuted follow-up proposals. [Failure-mode plot](failure_modes.png) makes the lost evidence use visible alongside formatting gains. Approved DATA_REVIEW.md and REVIEW_SAMPLES.md remain unchanged approval-time snapshots.\n')
    readme=Path('docs/archive/README_v2.md');text=readme.read_text();banner='**Measured result:** all 340 updates completed, but final GRPO collapsed toward abstention and achieved 0% stale catch on both holdouts. See [the experiment report](../../reports_v2/EXPERIMENT_REPORT.md) and [GRPO findings](../../reports_v2/GRPO_FINDINGS.md).\n\n'
    if banner not in text:readme.write_text(text.replace('# DriftGuard-MCP v2\n\n','# DriftGuard-MCP v2\n\n'+banner))
    if sync:
        from dotenv import load_dotenv
        from huggingface_hub import HfApi,snapshot_download
        load_dotenv(Path.cwd().parent/'.env');api=HfApi(token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN'))
        if not api.repo_info(job['run_repo'],repo_type='dataset').private:raise ValueError('Supplemental sync requires private run repository')
        final_status=[]
        for p in sorted((root/'cloud').glob('*/job.json')):
            info=json.loads(p.read_text());j=api.inspect_job(job_id=info['job_id'],namespace=info['namespace']);final_status.append(dict(job_id=j.id,stage=j.status.stage,url=info['url']))
        if any(j['stage'] not in ('COMPLETED','CANCELED','ERROR','DELETED') for j in final_status):raise ValueError('An experiment job is still running')
        write_json(root/'JOB_FINAL_STATUS.json',final_status)
        pattern=job['run_prefix']+'/grpo_training/stage1/last_safe_adapter/'
        folder=Path(snapshot_download(job['run_repo'],repo_type='dataset',revision=download['revision'],token=api.token,local_dir=str(root/'downloads/stage1_candidate'),allow_patterns=[pattern+'**']))/pattern
        target=Path('checkpoints_v2/grpo_stage1_adapter')
        if target.exists() and (target/'adapter_model.safetensors').exists() and sha(target/'adapter_model.safetensors')!=sha(folder/'adapter_model.safetensors'):raise ValueError('Existing stage-one adapter differs; refuse overwrite')
        shutil.copytree(folder,target,dirs_exist_ok=True)
        write_json(root/'SELECTED_STAGE1.json',dict(selection='Highest stage-end validation accuracy only; holdouts not evaluated',validation_accuracy=vs[1],local_path=str(target.resolve()),source_repo=job['run_repo'],source_revision=download['revision'],source_path=pattern,adapter_sha256=sha(target/'adapter_model.safetensors')))
        release=build();review_dir=root/'review';review_dir.mkdir(exist_ok=True)
        for name in ('EXPERIMENT_REPORT.md','RESULTS.md','GRPO_FINDINGS.md','GRPO_FINDINGS.json','PREFLIGHT.md','SFT_FINDINGS.md','SOURCE_PROVENANCE.json','SELECTED_STAGE1.json','JOB_FINAL_STATUS.json','publication_summary.json','failure_modes.png','failure_modes.svg','comparison.png','driftguard_v2_release.zip','driftguard_v2_release.json'):
            shutil.copy2(root/name,review_dir/name)
        commit=api.upload_folder(repo_id=job['run_repo'],repo_type='dataset',folder_path=str(review_dir),path_in_repo=job['run_prefix']+'/final_review',commit_message='Final v2 negative findings, plots and isolated release; frozen inputs unchanged')
        write_json(root/'FINAL_REVIEW_SYNC.json',dict(repo=job['run_repo'],revision=commit.oid,path=job['run_prefix']+'/final_review',private=True,release=release))
        state=json.loads((root/'FINALIZATION.json').read_text());state['release']=release;state['review_complete']=True;state['review_sync']=dict(repo=job['run_repo'],revision=commit.oid,path=job['run_prefix']+'/final_review');write_json(root/'FINALIZATION.json',state)
    return details

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sync',action='store_true');a=p.parse_args();print(json.dumps(review(a.sync),indent=2))
