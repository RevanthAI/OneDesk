"""Launch bounded, private GRPO jobs with a source-only/train-only frozen bundle."""
import argparse,hashlib,json,os,shlex,zipfile
from datetime import datetime,timezone
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi


def package(path):
    files=sorted(Path('src').glob('*.py'))+sorted(Path('src/v1').glob('*.py'))+sorted(Path('vendor/AgentTune/src').rglob('*.py'))
    files += [Path('docs/archive/data_v1',f) for f in ('train_sft_400.jsonl','train_grpo_stage1.jsonl','train_grpo_stage2.jsonl','world_train.json','SHA256SUMS')]
    files += [Path('docs/archive/cloud_grpo_bootstrap.sh'),Path('toolkit_revisions.json'),Path('vendor/AgentTune/LICENSE')]
    files=[f for f in files if f.exists()]
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        for f in files:
            if f.name=='.env' or 'holdout' in f.name or f.name.startswith('world_test'):raise ValueError('forbidden training input')
            archive.write(f,f.as_posix())
    return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),files={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},included_holdouts=False,included_env=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=('smoke','pilot'),default='smoke');p.add_argument('--flavor',default='l40sx1');p.add_argument('--timeout',default='30m');p.add_argument('--stage1-steps',type=int,default=20);p.add_argument('--stage2-steps',type=int,default=40);args=p.parse_args()
    if args.stage1_steps<1 or args.stage2_steps<1:raise ValueError('positive steps required')
    load_dotenv(Path.cwd().parent/'.env');token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN');api=HfApi(token=token);namespace=api.whoami()['name']
    repo=namespace+'/driftguard-mcp-grpo-runs';adapter=namespace+'/driftguard-tiny-aya-fire-grpo-pilot'
    prefix=args.mode+'-'+args.flavor+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    local=Path('reports/v1/cloud_grpo',prefix);local.mkdir(parents=True,exist_ok=True)
    archive=local/'cloud_grpo_bundle.zip';bundle=package(archive);(local/'bundle_manifest.json').write_text(json.dumps(bundle,indent=2))
    api.create_repo(repo,repo_type='dataset',private=True,exist_ok=True)
    if args.mode=='pilot':api.create_repo(adapter,private=True,exist_ok=True)
    api.upload_file(path_or_fileobj=str(archive),path_in_repo='cloud_grpo_bundle.zip',repo_id=repo,repo_type='dataset',commit_message='GRPO train-only bundle '+prefix)
    revision=api.upload_file(path_or_fileobj='docs/archive/cloud_grpo_bootstrap.sh',path_in_repo='cloud_grpo_bootstrap.sh',repo_id=repo,repo_type='dataset',commit_message='GRPO bootstrap '+prefix).oid
    arguments=['--mode',args.mode,'--output','/workspace/output','--run-repo',repo,'--run-prefix',prefix,'--stage1-steps',str(args.stage1_steps),'--stage2-steps',str(args.stage2_steps)]
    if args.mode=='pilot':arguments+=['--adapter-repo',adapter]
    downloader="import os,subprocess,json;from huggingface_hub import hf_hub_download;p=hf_hub_download(os.environ['RUN_REPO'],'cloud_grpo_bootstrap.sh',repo_type='dataset',revision=os.environ['BUNDLE_REVISION'],token=os.environ['HF_TOKEN']);subprocess.run(['bash',p]+json.loads(os.environ['TRAIN_ARGS']),check=True)"
    record=dict(mode=args.mode,flavor=args.flavor,timeout=args.timeout,namespace=namespace,run_repo=repo,run_prefix=prefix,bundle_revision=revision,bundle_sha256=bundle['sha256'],arguments=arguments,adapter_repo=adapter)
    (local/'submission.json').write_text(json.dumps(record,indent=2))
    job=api.run_job(image='ghcr.io/astral-sh/uv:python3.12-bookworm',command=['bash','-lc','uv pip install --system huggingface-hub==0.36.2 && python -c '+shlex.quote(downloader)],env={'RUN_REPO':repo,'BUNDLE_REVISION':revision,'BUNDLE_SHA256':bundle['sha256'],'TRAIN_ARGS':json.dumps(arguments)},secrets={'HF_TOKEN':token},flavor=args.flavor,timeout=args.timeout)
    record.update(job_id=job.id,url=f'https://huggingface.co/jobs/{namespace}/{job.id}')
    (local/'job.json').write_text(json.dumps(record,indent=2));Path('reports/v1/cloud_grpo/latest_job.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
if __name__=='__main__':main()
