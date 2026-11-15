"""Create an explicit v2-only source/report archive; never publish remotely."""
import hashlib,json,zipfile
from pathlib import Path
from .data import verify,write_json


def build(destination='reports/v2/driftguard_v2_release.zip'):
    verify();paths={Path('src/__init__.py'),Path('src/layout.py')}
    for name in ('docs/archive/README_v2.md','requirements_v2.txt','docs/archive/cloud_v2_bootstrap.sh','toolkit_revisions.json'):
        paths.add(Path(name))
    for folder in ('src/v2','tests/v2','data_v2'):
        paths.update(p for p in Path(folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    for library in ('AgentTune','AuditKIT'):
        paths.update(p for p in Path('vendor',library).glob('LICENSE*') if p.is_file())
        paths.update(Path('vendor',library,'src').rglob('*.py'))
    report_names=('RESULTS.md','GRPO_FINDINGS.md','GRPO_FINDINGS.json','failure_modes.png','failure_modes.svg','SOURCE_PROVENANCE.json','SELECTED_STAGE1.json','JOB_FINAL_STATUS.json','SFT_FINDINGS.md','PREFLIGHT.md','EXPERIMENT_REPORT.md','paired_comparison.json','comparison.png','comparison.svg','APPROVED_DATA_LOCK.json','SCORER_FIX_HANDOFF.json','COMPLETION.json','RUN_CONFIG.json','MODEL_REVISIONS.json','ENVIRONMENT.json','publication_summary.json')
    for name in report_names:
        p=Path('reports/v2',name)
        if p.is_file():paths.add(p)
    for phase in ('v2_base_fire','v2_sft_fire','v2_grpo_fire','grpo_training','grpo_smoke','sft_training','grpo_validation'):
        folder=Path('reports/v2',phase)
        if not folder.is_dir():continue
        for p in folder.rglob('*'):
            if not p.is_file() or any(x.startswith('checkpoint-') for x in p.parts):continue
            if p.name in ('rollouts.jsonl','input_ids.jsonl'):continue
            if p.suffix in ('.json','.jsonl','.md','.png','.svg','.csv','.html') or 'tfevents' in p.name:paths.add(p)
    for p in Path('reports/v2/cloud').glob('*/job.json'):paths.add(p)
    for p in Path('reports/v2/cloud').glob('*/bundle_manifest.json'):paths.add(p)
    for p in paths:
        if '.env' in p.parts or p.as_posix().startswith(('src/v1/','docs/archive/data_v1/','reports/v1/','checkpoints/v1/')):raise ValueError('forbidden release path')
    manifest={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(paths):archive.write(p,p.as_posix())
        archive.writestr('V2_RELEASE_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    info=dict(path=str(destination.resolve()),sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),files=len(paths),bytes=destination.stat().st_size,legacy_included=False,secrets_included=False,raw_training_rollouts='Linked private HF run repository; omitted from source archive',remote_publication_performed=False)
    write_json(destination.with_suffix('.json'),info);return info

if __name__=='__main__':print(json.dumps(build(),indent=2))
