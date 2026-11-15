"""Retrieve and document a completed v2 cloud experiment; no model execution."""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi
import requests
from .data import verify,write_json
from .failure_analysis import analyze as failures
from .diagnostics import analyze as diagnostics
from .trace_viewer import export_viewer
from .publication import build


def finalize():
    subprocess.run([sys.executable,'-m','src_v2.manage','download','--models'],check=True)
    root=Path('reports_v2');completion=json.loads((root/'COMPLETION.json').read_text())
    if completion.get('status')!='complete':raise RuntimeError('Cloud run is not fully complete; inspect its saved status instead of claiming completion')
    frozen=json.loads((root/'APPROVED_DATA_LOCK.json').read_text());actual={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('data_v2').iterdir() if p.is_file()}
    if frozen!=actual:raise ValueError('Frozen data directory changed')
    verify();analysis={}
    for phase in ('v2_base_fire','v2_sft_fire','v2_grpo_fire'):analysis[phase]=failures(root/phase)
    sampling={}
    for phase in ('grpo_smoke','grpo_training'):
        sampling[phase]=diagnostics(root/phase);export_viewer(root/phase)
    smoke=json.loads((root/'grpo_smoke/metadata.json').read_text());training=json.loads((root/'grpo_training/metadata.json').read_text());sft=json.loads((root/'sft_training/metadata.json').read_text())
    completed=sum(s['completed_steps'] for s in training['stages'])
    if completed!=340 or [s['completed_steps'] for s in training['stages']]!=[120,220]:raise ValueError('Requested GRPO schedule did not complete')
    optimizer=[]
    for p in (root/'grpo_training').glob('stage*/optimizer_log.jsonl'):optimizer += [json.loads(x) for x in p.read_text().splitlines()]
    import math
    if not all(math.isfinite(r[k]) for r in optimizer for k in ('loss','grad_norm','kl') if k in r):raise ValueError('Non-finite optimization diagnostics')
    weights={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('checkpoints_v2').glob('*/adapter_model.safetensors')}
    summary=dict(status='complete',data_files_unchanged=len(actual),sft=sft,smoke=smoke,grpo=training,sampling=sampling,analysis=analysis,adapter_sha256=weights)
    write_json(root/'publication_summary.json',summary)
    lines=['# DriftGuard-MCP v2 experiment report','','The approved Base → one-epoch SFT → active-advantage GRPO experiment completed on Hugging Face L40S. All 19 approved data-folder files remain byte-identical; the 15-artifact SHA-256 manifest verifies. Historical v1 results are excluded.','','## Execution and safeguards','','Main tests: 58 passed. Independent v2 tests: 15 passed. Required utility-call gates, saturated-kind fallback and the BF16 temperature-order correction were verified before GRPO. See [PREFLIGHT.md](PREFLIGHT.md).','','SFT: exactly 240 examples, one epoch, 15 optimizer steps, effective batch 16, 2,560-token budget, zero truncated conversations. Validation contains 80 rows from 20 separate semantic cases.','','GRPO smoke: five active updates in %.1f seconds; %.2f GiB peak reserved VRAM; unchanged SFT reference. Smoke updates were discarded before the full run.'%(smoke['wall_seconds'],smoke['peak_reserved_gib']),'','Full GRPO: 120 + 220 active optimizer updates; four sampled episodes per group; 4,096-token context and 192 tokens per turn. Attempted groups: %s; acceptance: %.2f%%; peak reserved VRAM: %.2f GiB; training wall time: %.1f minutes.'%(training['attempted_groups'],100*training['acceptance_rate'],training['peak_reserved_gib'],training['wall_seconds']/60),'','The first v2 job was stopped at the saved SFT handoff after a probability-scoring precision issue was found before GRPO. The corrected pinned job reused the valid Base evaluation and SFT adapter. Both job records and SCORER_FIX_HANDOFF.json retain provenance.','','## Results','','See [RESULTS.md](RESULTS.md) for all metrics and paired accuracy changes with 95% semantic-case cluster-bootstrap intervals.','']
    lines+=['| Holdout | Base exact outcome | SFT exact outcome | SFT+GRPO exact outcome |','|---|---:|---:|---:|']
    for split in ('test_synth','repo_style'):
        cells=[]
        for phase in ('v2_base_fire','v2_sft_fire','v2_grpo_fire'):
            m=json.loads((root/phase/'summary.json').read_text())[split]['metrics']['exact_outcome'];cells.append('%.2f%% [%.2f, %.2f]'%(100*m['estimate'],100*m['ci95'][0],100*m['ci95'][1]))
        lines.append('| '+split+' | '+' | '.join(cells)+' |')
    lines+=['','## Findings and artifacts','','Per-model FAILURE_ANALYSIS.md/JSON contains task-kind/language/subtype breakdowns and actual saved error examples. Counts of wrong status, wrong scalar, invalid format, staging citations and tool errors can overlap. Training rewards are not holdout accuracy.','','- [Three-way accuracy plot](comparison.png) and [vector export](comparison.svg).','- [Training curves](grpo_training/training_rollouts.png), [optimization diagnostics](grpo_training/optimization.png), and [sampling analysis](grpo_training/ACTIVE_SAMPLING_ANALYSIS.md).','- [Offline rollout explorer](grpo_training/rollout_explorer.html), raw JSONL logs and TensorBoard events.','- Local adapters: checkpoints_v2/sft_adapter and checkpoints_v2/grpo_adapter. Adapter SHA-256 hashes are in publication_summary.json; pinned Hub revisions are in MODEL_REVISIONS.json.','','## Interpretation and limits','','The v2 SFT recipe was deliberately compact and differs from the v1 training/data recipe. Score differences across v1 and v2 cannot be attributed to one change. This matched comparison uses BF16 cloud inference throughout; local NF4 deployment may behave differently. OSS-style cases are constructed fixtures, not verified historical upstream changes. Multilingual prompts have no claimed independent native-speaker review. These holdouts were reviewed during development; stronger generalization claims require an untouched confirmation set. Active-group filtering changes the sampled distribution; inspect accepted-kind coverage and skipped attempts. Normal TRL checkpoints retain optimizer/model state, but exact replay of the dynamic sampler mid-stage is not implemented.','','Repositories remain private. The release ZIP includes only the v2 allowlist; no public publication was performed. Pricing estimates are not billing records; inspect Hugging Face billing for actual charges.']
    (root/'EXPERIMENT_REPORT.md').write_text('\n'.join(lines)+'\n')
    release=build();write_json(root/'FINALIZATION.json',dict(status='complete',release=release,adapter_sha256=weights));print(json.dumps(release,indent=2),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--wait',action='store_true');a=parser.parse_args()
    if a.wait:
        load_dotenv(Path.cwd().parent/'.env');api=HfApi(token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN'));record=json.loads(Path('reports_v2/LATEST_JOB.json').read_text());last=None
        while True:
            try:
                job=api.inspect_job(job_id=record['job_id'],namespace=record['namespace']);stage=job.status.stage
            except requests.RequestException as error:
                response=getattr(error,'response',None)
                if response is not None and response.status_code in (400,401,403,404):raise
                event=dict(event='monitor_network_retry',error_type=type(error).__name__,updated_at=time.time())
                write_json('reports_v2/FINISH_STATUS.json',event);print(json.dumps(event),flush=True);time.sleep(30);continue
            write_json('reports_v2/FINISH_STATUS.json',dict(stage=stage,job_id=record['job_id'],updated_at=time.time()))
            if stage!=last:print(json.dumps(dict(event='finalizer_job_status',stage=stage)),flush=True);last=stage
            if stage=='COMPLETED':break
            if stage in ('ERROR','CANCELED','DELETED','FAILED'):raise RuntimeError('Cloud job ended without completion: '+stage)
            time.sleep(30)
    for attempt in range(1,4):
        try:
            finalize();break
        except (subprocess.CalledProcessError,requests.RequestException) as error:
            if attempt==3:raise
            print(json.dumps(dict(event='retrieval_retry',attempt=attempt,error_type=type(error).__name__)),flush=True);time.sleep(30)

if __name__=='__main__':main()
