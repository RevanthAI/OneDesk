"""Submit one sequential v2 cloud pipeline with frozen bundle and a time cap."""
import argparse,hashlib,json,os,shlex,zipfile
from datetime import datetime,timezone
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi
from .data import verify,write_json


def package(path):
    files=[Path('src/__init__.py'),Path('src/layout.py')]+sorted(Path('src/v2').glob('*.py'))+sorted(p for p in Path('data_v2').iterdir() if p.is_file())
    for library in ('AgentTune','AuditKIT'):
        files+=sorted(Path('vendor',library,'src').rglob('*.py'))
        files+=[p for p in Path('vendor',library).glob('LICENSE*') if p.is_file()]
    files+=[Path('toolkit_revisions.json'),Path('docs/archive/cloud_v2_bootstrap.sh')]
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        for f in files:
            if f.name=='.env' or f.as_posix().startswith(('src/v1/','docs/archive/data_v1/','reports/v1/')):raise ValueError('Forbidden legacy/secret bundle path')
            archive.write(f,f.as_posix())
    return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),files={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},data_hashes=verify(),legacy_included=False,secrets_included=False,holdouts_for_evaluation_only=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--timeout',default='12h');p.add_argument('--phase',choices=('all','base'),default='all');p.add_argument('--resume-prefix');a=p.parse_args()
    load_dotenv(Path.cwd().parent/'.env');token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN');api=HfApi(token=token);namespace=api.whoami()['name']
    repo=namespace+'/driftguard-mcp-v2-runs';dataset_repo=namespace+'/driftguard-mcp-v2-data';sft=namespace+'/driftguard-tiny-aya-fire-v2-sft';grpo=namespace+'/driftguard-tiny-aya-fire-v2-grpo'
    prefix='v2-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');local=Path('reports/v2/cloud',prefix);local.mkdir(parents=True)
    for name,kind in ((repo,'dataset'),(dataset_repo,'dataset'),(sft,'model'),(grpo,'model')):api.create_repo(name,repo_type=kind,private=True,exist_ok=True)
    dataset_revision=api.upload_folder(repo_id=dataset_repo,repo_type='dataset',folder_path='data_v2',commit_message='Approved immutable v2 artifacts; exact locked bytes').oid
    bundle=local/'pipeline_bundle.zip';manifest=package(bundle);write_json(local/'bundle_manifest.json',manifest)
    api.upload_file(repo_id=repo,repo_type='dataset',path_or_fileobj=str(bundle),path_in_repo='pipeline_bundle.zip',commit_message='Frozen independent v2 pipeline '+prefix)
    revision=api.upload_file(repo_id=repo,repo_type='dataset',path_or_fileobj='docs/archive/cloud_v2_bootstrap.sh',path_in_repo='cloud_v2_bootstrap.sh',commit_message='v2 cloud bootstrap').oid
    arguments=['--run-repo',repo,'--run-prefix',prefix,'--sft-repo',sft,'--grpo-repo',grpo,'--phase',a.phase]
    if a.resume_prefix:
        sft_revision=api.model_info(sft).sha
        arguments+=['--resume-prefix',a.resume_prefix,'--sft-revision',sft_revision]
    downloader="import os,json,subprocess;from huggingface_hub import hf_hub_download;p=hf_hub_download(os.environ['RUN_REPO'],'cloud_v2_bootstrap.sh',repo_type='dataset',revision=os.environ['BUNDLE_REVISION'],token=os.environ['HF_TOKEN']);subprocess.run(['bash',p]+json.loads(os.environ['PIPELINE_ARGS']),check=True)"
    record=dict(run_repo=repo,run_prefix=prefix,bundle_revision=revision,bundle_sha256=manifest['sha256'],dataset_repo=dataset_repo,dataset_revision=dataset_revision,sft_repo=sft,grpo_repo=grpo,timeout=a.timeout,flavor='l40sx1',namespace=namespace,phase=a.phase,resume_prefix=a.resume_prefix,resume_sft_revision=sft_revision if a.resume_prefix else None)
    write_json(local/'submission.json',record)
    job=api.run_job(image='ghcr.io/astral-sh/uv:python3.12-bookworm',command=['bash','-lc','uv pip install --system huggingface-hub==0.36.2 && python -c '+shlex.quote(downloader)],env={'RUN_REPO':repo,'BUNDLE_REVISION':revision,'BUNDLE_SHA256':manifest['sha256'],'PIPELINE_ARGS':json.dumps(arguments)},secrets={'HF_TOKEN':token},flavor='l40sx1',timeout=a.timeout)
    record.update(job_id=job.id,url=f'https://huggingface.co/jobs/{namespace}/{job.id}')
    write_json(local/'job.json',record);write_json('reports/v2/LATEST_JOB.json',record);print(json.dumps(record,indent=2))
if __name__=='__main__':main()
