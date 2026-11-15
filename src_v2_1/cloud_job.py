"""Submit one private, bounded v2.1 L40S job; frozen v2 data is only read."""
import argparse,hashlib,json,os,shlex,zipfile
from datetime import datetime,timezone
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi
from .data import verify,write_json

def package(path):
    files=sorted(Path('src_v2_1').glob('*.py'))+sorted(p for p in Path('data_v2').iterdir() if p.is_file())+sorted(p for p in Path('reports_v2_1/prior_v2').rglob('*') if p.is_file())
    for lib in ('AgentTune','AuditKIT'):
        files+=sorted(Path('vendor',lib,'src').rglob('*.py'))+[p for p in Path('vendor',lib).glob('LICENSE*') if p.is_file()]
    files += sorted(Path('tests_v2_1').glob('*.py'))+[Path('docs/archive/README_v2_1.md'),Path('reports_v2_1/PREFLIGHT.md'),Path('toolkit_revisions.json'),Path('docs/archive/cloud_v2_1_bootstrap.sh')]
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        for f in files:
            if f.name=='.env' or f.parts[0] in ('src','reports_v2','data'):raise ValueError('Forbidden bundle path')
            archive.write(f,f.as_posix())
    return dict(sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),files={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},data_hashes=verify())

def main():
    p=argparse.ArgumentParser();p.add_argument('--timeout',default='8h');p.add_argument('--resume-prefix');p.add_argument('--group-size',type=int,choices=(4,6),default=4);p.add_argument('--temperature',type=float,default=.8);p.add_argument('--retry-temperature',type=float,default=.95);a=p.parse_args();load_dotenv(Path.cwd().parent/'.env');token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN');api=HfApi(token=token);ns=api.whoami()['name'];prefix='v2-1-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');local=Path('reports_v2_1/cloud',prefix);local.mkdir(parents=True)
    run=ns+'/driftguard-mcp-v2-1-runs';sft=ns+'/driftguard-tiny-aya-fire-v2-1-sft';best=ns+'/driftguard-tiny-aya-fire-v2-1-grpo-best-val';final=ns+'/driftguard-tiny-aya-fire-v2-1-grpo-final'
    for name,kind in ((run,'dataset'),(sft,'model'),(best,'model'),(final,'model')):
        api.create_repo(name,repo_type=kind,private=True,exist_ok=True)
        if not api.repo_info(name,repo_type=kind).private:raise ValueError('All experiment repositories must remain private')
    bundle=local/'pipeline_bundle.zip';manifest=package(bundle);write_json(local/'bundle_manifest.json',manifest);api.upload_file(repo_id=run,repo_type='dataset',path_or_fileobj=str(bundle),path_in_repo='pipeline_bundle.zip',commit_message='Pinned v2.1 source and immutable v2 data')
    revision=api.upload_file(repo_id=run,repo_type='dataset',path_or_fileobj='docs/archive/cloud_v2_1_bootstrap.sh',path_in_repo='cloud_v2_1_bootstrap.sh',commit_message='v2.1 bootstrap').oid
    args=['--run-repo',run,'--run-prefix',prefix,'--sft-repo',sft,'--grpo-best-repo',best,'--grpo-final-repo',final,'--group-size',str(a.group_size),'--temperature',str(a.temperature),'--retry-temperature',str(a.retry_temperature)]
    resume_revision=None
    if a.resume_prefix:
        resume_revision=api.repo_info(run,repo_type='dataset').sha;args+=['--resume-prefix',a.resume_prefix,'--resume-revision',resume_revision]
    downloader="import os,json,subprocess;from huggingface_hub import hf_hub_download;p=hf_hub_download(os.environ['RUN_REPO'],'cloud_v2_1_bootstrap.sh',repo_type='dataset',revision=os.environ['BUNDLE_REVISION'],token=os.environ['HF_TOKEN']);subprocess.run(['bash',p]+json.loads(os.environ['PIPELINE_ARGS']),check=True)"
    record=dict(namespace=ns,run_repo=run,run_prefix=prefix,bundle_revision=revision,bundle_sha256=manifest['sha256'],sft_repo=sft,grpo_best_repo=best,grpo_final_repo=final,timeout=a.timeout,flavor='l40sx1',resume_prefix=a.resume_prefix,resume_revision=resume_revision,group_size=a.group_size,temperature=a.temperature,retry_temperature=a.retry_temperature)
    write_json(local/'submission.json',record)
    job=api.run_job(image='ghcr.io/astral-sh/uv:python3.12-bookworm',command=['bash','-lc','uv pip install --system huggingface-hub==0.36.2 && python -c '+shlex.quote(downloader)],env={'RUN_REPO':run,'BUNDLE_REVISION':revision,'BUNDLE_SHA256':manifest['sha256'],'PIPELINE_ARGS':json.dumps(args)},secrets={'HF_TOKEN':token},flavor='l40sx1',timeout=a.timeout)
    record.update(job_id=job.id,url=f'https://huggingface.co/jobs/{ns}/{job.id}');write_json(local/'job.json',record);write_json('reports_v2_1/LATEST_JOB.json',record);print(json.dumps(record,indent=2))
if __name__=='__main__':main()
