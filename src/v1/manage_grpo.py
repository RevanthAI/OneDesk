"""Inspect, follow, and download an authorized HF GRPO experiment."""
import argparse,json,os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi,snapshot_download

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('status','logs','download'));p.add_argument('--job-file',default='reports/v1/cloud_grpo/latest_job.json');p.add_argument('--model',action='store_true');a=p.parse_args()
    load_dotenv(Path.cwd().parent/'.env');token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN');api=HfApi(token=token)
    record=json.loads(Path(a.job_file).read_text());job=api.inspect_job(job_id=record['job_id'],namespace=record['namespace'])
    status={'job_id':job.id,'stage':job.status.stage,'message':job.status.message,'url':record['url']}
    local=Path('reports/v1/cloud_grpo',record['run_prefix']);local.mkdir(parents=True,exist_ok=True)
    (local/'last_status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status,indent=2),flush=True)
    if a.action=='logs':
        with (local/'cloud.log').open('w') as f:
            for entry in api.fetch_job_logs(job_id=job.id,namespace=record['namespace']):
                line=entry.get('data',str(entry)) if isinstance(entry,dict) else str(entry)
                f.write(line+'\n');f.flush();print(line,flush=True)
    elif a.action=='download':
        revision=api.repo_info(record['run_repo'],repo_type='dataset').sha
        destination=Path('reports/v1/cloud_grpo/downloaded_artifacts')
        snapshot_download(record['run_repo'],repo_type='dataset',revision=revision,token=token,local_dir=str(destination),allow_patterns=[record['run_prefix']+'/**'])
        result={'run_repo':record['run_repo'],'run_revision':revision,'artifacts':str((destination/record['run_prefix']).resolve())}
        if a.model:
            if record['mode']!='pilot' or status['stage']!='COMPLETED':raise ValueError('only download an adapter from a completed pilot')
            revision=api.model_info(record['adapter_repo']).sha
            path=Path('checkpoints/v1/tiny-aya-fire-grpo-pilot-adapter')
            snapshot_download(record['adapter_repo'],revision=revision,token=token,local_dir=str(path))
            if not (path/'adapter_model.safetensors').is_file():raise ValueError('adapter weights missing')
            result.update(adapter_repo=record['adapter_repo'],adapter_revision=revision,adapter_path=str(path.resolve()))
        (local/'downloads.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
