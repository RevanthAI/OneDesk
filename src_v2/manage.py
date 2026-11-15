"""Inspect HF v2 jobs, retain logs, and retrieve reports/adapters without legacy output."""
import argparse,json,os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi,snapshot_download
from .data import write_json


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('status','logs','download'));p.add_argument('--job-file',default='reports_v2/LATEST_JOB.json');p.add_argument('--models',action='store_true');p.add_argument('--all-logs',action='store_true');a=p.parse_args()
    load_dotenv(Path.cwd().parent/'.env');api=HfApi(token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN'));record=json.loads(Path(a.job_file).read_text())
    job=api.inspect_job(job_id=record['job_id'],namespace=record['namespace']);status=dict(job_id=job.id,stage=job.status.stage,message=job.status.message,url=record['url'])
    local=Path('reports_v2/cloud',record['run_prefix']);write_json(local/'last_status.json',status);print(json.dumps(status,indent=2),flush=True)
    if a.action=='logs':
        with (local/'cloud.log').open('w') as f:
            for entry in api.fetch_job_logs(job_id=job.id,namespace=record['namespace']):
                text=entry.get('data',str(entry)) if isinstance(entry,dict) else str(entry)
                f.write(text+'\n');f.flush()
                if a.all_logs or any(s in text for s in ['"event"','Traceback','Error:','Exception:']):print(text,flush=True)
    elif a.action=='download':
        revision=api.repo_info(record['run_repo'],repo_type='dataset').sha
        folder=Path('reports_v2/downloads')
        snapshot_download(record['run_repo'],repo_type='dataset',revision=revision,token=api.token,local_dir=str(folder),allow_patterns=[record['run_prefix']+'/**'],ignore_patterns=['**/*.safetensors','**/*.pt','**/*.bin','**/tokenizer.json','**/reference/**'])
        run=folder/record['run_prefix'];root=Path('reports_v2')
        if not run.exists():raise RuntimeError('no persisted v2 reports yet')
        for path in run.iterdir():
            target=root/path.name
            if target.is_symlink():target.unlink()
            if target.exists():continue
            target.symlink_to(path.resolve(),target_is_directory=path.is_dir())
        for phase in ('v2_base_fire','v2_sft_fire','v2_grpo_fire'):
            alias=Path('reports')/phase
            if not alias.exists() and not alias.is_symlink():alias.symlink_to((root/phase).resolve(),target_is_directory=True)
        result=dict(repo=record['run_repo'],revision=revision,run_directory=str(run.resolve()),status=status)
        if a.models:
            model_records=json.loads((run/'MODEL_REVISIONS.json').read_text());result['models']={}
            for label,info in model_records.items():
                path=Path('checkpoints_v2')/(label.lower()+'_adapter')
                snapshot_download(info['repo'],revision=info['revision'],token=api.token,local_dir=str(path))
                if not (path/'adapter_model.safetensors').is_file():raise ValueError('adapter download incomplete')
                result['models'][label]=dict(info,local_path=str(path.resolve()))
        write_json(local/'downloads.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
