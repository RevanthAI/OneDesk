"""Package approved inputs, launch bounded HF Jobs, and retrieve artifacts."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import zipfile
from dotenv import load_dotenv
from huggingface_hub import HfApi


def package(output):
    root=Path.cwd();entries=[]
    entries += sorted(Path('src').glob('*.py'))+sorted(Path('src/v1').glob('*.py'))
    entries += [Path('docs/archive/data_v1/train_sft_400.jsonl'),Path('docs/archive/data_v1/SHA256SUMS'),Path('docs/archive/cloud_bootstrap.sh'),Path('toolkit_revisions.json')]
    entries += sorted(Path('vendor/AgentTune/src').rglob('*.py'))
    entries += [p for p in (Path('vendor/AgentTune/README.md'),Path('vendor/AgentTune/LICENSE')) if p.exists()]
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in entries:
            if p.name=='.env' or p.suffix!='.py' and p not in entries:raise ValueError('unexpected input')
            z.write(p,p.as_posix())
    return {'archive_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'files':len(entries),'bytes':output.stat().st_size,'included_holdouts':False,'included_env':False}


def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=('smoke','train'),default='smoke');p.add_argument('--flavor',default='l40sx1');p.add_argument('--timeout',default='30m');p.add_argument('--batch-size',type=int,default=4);p.add_argument('--effective-batch',type=int,default=16);p.add_argument('--prefix');p.add_argument('--batches',default='1,2,4,8,16,32');args=p.parse_args()
    load_dotenv(Path.cwd().parent/'.env');token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN')
    if not token:raise RuntimeError('HF token missing')
    api=HfApi(token=token);namespace=api.whoami()['name']
    repo=namespace+'/driftguard-mcp-training-runs';adapter=namespace+'/driftguard-tiny-aya-fire-sft';merged=namespace+'/driftguard-tiny-aya-fire-sft-merged'
    prefix=args.prefix or args.mode+'-'+args.flavor+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    local=Path('reports/v1/cloud_sft')/prefix;local.mkdir(parents=True,exist_ok=True)
    bundle=local/'cloud_bundle.zip';info=package(bundle);(local/'bundle_manifest.json').write_text(json.dumps(info,indent=2))
    api.create_repo(repo,repo_type='dataset',private=True,exist_ok=True)
    if args.mode=='train':
        api.create_repo(adapter,private=True,exist_ok=True);api.create_repo(merged,private=True,exist_ok=True)
    commit=api.upload_file(path_or_fileobj=str(bundle),path_in_repo='cloud_bundle.zip',repo_id=repo,repo_type='dataset',commit_message='Frozen SFT code/data bundle '+prefix)
    bootstrap=api.upload_file(path_or_fileobj='docs/archive/cloud_bootstrap.sh',path_in_repo='cloud_bootstrap.sh',repo_id=repo,repo_type='dataset',commit_message='Cloud bootstrap '+prefix)
    revision=bootstrap.oid
    # Only repository identifiers, revision and training arguments enter the
    # command. Credentials are supplied solely through the Jobs secrets field.
    arguments=['--mode',args.mode,'--output','/workspace/output','--run-repo',repo,'--run-prefix',prefix]
    if args.mode=='smoke':arguments+=['--batches',args.batches,'--steps','5']
    else:arguments+=['--batch-size',str(args.batch_size),'--effective-batch',str(args.effective_batch),'--epochs','1.5','--adapter-repo',adapter,'--merged-repo',merged]
    downloader="import os,subprocess; from huggingface_hub import hf_hub_download; p=hf_hub_download(os.environ['RUN_REPO'],'cloud_bootstrap.sh',repo_type='dataset',revision=os.environ['BUNDLE_REVISION'],token=os.environ['HF_TOKEN']); subprocess.run(['bash',p]+__import__('json').loads(os.environ['TRAIN_ARGS']),check=True)"
    command=['bash','-lc','uv pip install --system huggingface-hub==0.36.2 && python -c '+__import__('shlex').quote(downloader)]
    record={'mode':args.mode,'flavor':args.flavor,'timeout':args.timeout,'run_repo':repo,'run_prefix':prefix,'bundle_revision':revision,'adapter_repo':adapter,'merged_repo':merged,'bundle':info,'arguments':arguments}
    (local/'submission.json').write_text(json.dumps(record,indent=2))
    try:
        job=api.run_job(image='ghcr.io/astral-sh/uv:python3.12-bookworm',command=command,env={'RUN_REPO':repo,'BUNDLE_REVISION':revision,'TRAIN_ARGS':json.dumps(arguments)},secrets={'HF_TOKEN':token},flavor=args.flavor,timeout=args.timeout)
        record.update(job_id=job.id,namespace=namespace,url=getattr(job,'url',None))
        (local/'job.json').write_text(json.dumps(record,indent=2));Path('reports/v1/cloud_sft/latest_job.json').write_text(json.dumps(record,indent=2))
        print(json.dumps(record,indent=2))
    except Exception as e:
        record['error_type']=type(e).__name__;record['http_status']=getattr(getattr(e,'response',None),'status_code',None);record['error']=str(e).replace(token,'[REDACTED]')[:1400]
        (local/'submission_failure.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));raise SystemExit(1)
if __name__=='__main__':main()
