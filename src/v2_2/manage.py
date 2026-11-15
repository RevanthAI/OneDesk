"""Resilient HF monitoring, private artifact retrieval and old-evidence protection."""
import argparse,hashlib,json,os,shutil,threading,time,zipfile
from pathlib import Path
import requests
from dotenv import load_dotenv
from huggingface_hub import HfApi,snapshot_download
from .data import verify,write_json
from src.layout import relocated_path

def terminal_stage(stage):return stage in ('COMPLETED','CANCELED','ERROR','DELETED','FAILED')

def protected():
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    for path,value in json.loads(Path('reports/v2_2/PROTECTED_V2_LOCK.json').read_text()).items():
        if digest(relocated_path(path))!=value:raise ValueError('Protected v2 report changed: '+path)
    for path,value in json.loads(Path('reports/v2_2/PRESERVED_V2_1_LOCK.json').read_text()).items():
        if digest(relocated_path(path))!=value:raise ValueError('Preserved v2.1 ablation changed: '+path)
    data=json.loads(Path('reports/v2_2/APPROVED_DATA_LOCK.json').read_text());assert data=={p.name:digest(p) for p in Path('data_v2').iterdir() if p.is_file()};verify();return len(data)

def retry(function):
    for attempt in range(8):
        try:return function()
        except requests.RequestException as error:
            response=getattr(error,'response',None)
            if response is not None and response.status_code in (400,401,403,404):raise
            if attempt==7:raise
            print(json.dumps(dict(event='client_network_retry',attempt=attempt+1,error_type=type(error).__name__)),flush=True);time.sleep(15)

def sync_reports(run,root):
    for path in Path(run).iterdir():
        target=Path(root)/path.name
        if target.is_symlink():target.unlink()
        if target.is_dir() and path.name=='prior_v2':shutil.copytree(path,target,dirs_exist_ok=True)
        elif not target.exists():target.symlink_to(path.resolve(),target_is_directory=path.is_dir())

def download(api,record,models=True):
    revision=retry(lambda:api.repo_info(record['run_repo'],repo_type='dataset')).sha;folder=Path('reports/v2_2/downloads')
    retry(lambda:snapshot_download(record['run_repo'],repo_type='dataset',revision=revision,token=api.token,local_dir=str(folder),allow_patterns=[record['run_prefix']+'/**'],ignore_patterns=['**/*.safetensors','**/*.pt','**/*.bin','**/tokenizer.json','**/reference/**']))
    run=folder/record['run_prefix'];root=Path('reports/v2_2')
    sync_reports(run,root)
    alias=Path('reports/v1/v2_1_comparison')
    if alias.is_symlink():alias.unlink()
    if not alias.exists():alias.symlink_to((root/'comparison').resolve(),target_is_directory=True)
    artifacts={}
    if models:
        for label,info in json.loads((run/'MODEL_REVISIONS.json').read_text()).items():
            path=Path('checkpoints/v2_2')/(label.lower()+'_adapter');retry(lambda:snapshot_download(info['repo'],revision=info['revision'],token=api.token,local_dir=str(path)))
            if not (path/'adapter_model.safetensors').exists():raise ValueError('Missing adapter weight')
            artifacts[label]=dict(info,local_path=str(path.resolve()),sha256=hashlib.sha256((path/'adapter_model.safetensors').read_bytes()).hexdigest())
    count=protected();write_json(root/'DOWNLOADS.json',dict(repo=record['run_repo'],revision=revision,run_directory=str(run.resolve()),models=artifacts,frozen_files_unchanged=count));return run,artifacts

def release():
    root=Path('reports/v2_2');files={Path('src/__init__.py'),Path('src/layout.py')}|set(Path('src/v2_2').glob('*.py'))|set(Path('tests/v2_2').glob('*.py'))|set(Path('data_v2').iterdir())|{Path('docs/archive/README_v2_2.md'),Path('docs/archive/cloud_v2_2_bootstrap.sh'),Path('toolkit_revisions.json')}
    for lib in ('AgentTune','AuditKIT'):files.update(Path('vendor',lib,'src').rglob('*.py'));files.update(Path('vendor',lib).glob('LICENSE*'))
    for folder in ('comparison','sft_evaluation','grpo_evaluation','stage1_diagnostic','grpo_training','prior_v2','sft_full_evaluation','stage1_evaluation'):
        for p in (root/folder).rglob('*'):
            if not p.is_file() or any(x.startswith('checkpoint-') for x in p.parts):continue
            if p.name in ('rollouts.jsonl','tokenizer.json'):continue
            if p.suffix in ('.json','.jsonl','.md','.png','.svg','.csv','.html') or 'tfevents' in p.name:files.add(p)
    for name in ('COMPLETION.json','RUN_CONFIG.json','ENVIRONMENT.json','MODEL_REVISIONS.json','V2_STAGE1_DIAGNOSTIC.md','DOWNLOADS.json','APPROVED_DATA_LOCK.json','PREFLIGHT.md'):
        if (root/name).exists():files.add(root/name)
    path=root/'driftguard_v2_1_release.zip'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        manifest={}
        for p in sorted(files):
            if not p.is_file():continue
            if p.name=='.env' or p.as_posix().startswith(('src/v1/','docs/archive/data_v1/','reports/v1/')):raise ValueError('Forbidden release path')
            archive.write(p,p.as_posix());manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
        archive.writestr('RELEASE_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    return dict(path=str(path.resolve()),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),files=len(manifest))

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('status','logs','download','watch'));p.add_argument('--models',action='store_true');a=p.parse_args();load_dotenv(Path.cwd().parent/'.env');api=HfApi(token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN'));record=json.loads(Path('reports/v2_2/LATEST_JOB.json').read_text());local=Path('reports/v2_2/cloud',record['run_prefix']);stop=threading.Event()
    def status():
        j=retry(lambda:api.inspect_job(job_id=record['job_id'],namespace=record['namespace']));value=dict(stage=j.status.stage,message=j.status.message,job_id=j.id,updated_at=time.time());write_json(local/'last_status.json',value);return value
    def logs():
        file=local/'cloud.log';seen=set(file.read_text().splitlines()) if file.exists() else set()
        while not stop.is_set():
            try:
                with (local/'cloud.log').open('w') as f:
                    for entry in api.fetch_job_logs(job_id=record['job_id'],namespace=record['namespace']):
                        text=entry.get('data',str(entry)) if isinstance(entry,dict) else str(entry);f.write(text+'\n');f.flush()
                        if text not in seen and ('"event"' in text or 'Traceback' in text or 'Error:' in text):print(text,flush=True);seen.add(text)
                if terminal_stage(status()['stage']):return
                stop.wait(5)
            except requests.RequestException as error:
                print(json.dumps(dict(event='log_stream_retry',error_type=type(error).__name__)),flush=True);stop.wait(15)
    if a.action=='logs':logs();return
    current=status();print(json.dumps(current),flush=True)
    if a.action=='status':return
    if a.action=='watch':
        threading.Thread(target=logs,daemon=True).start();last=current['stage']
        while not terminal_stage(current['stage']):
            time.sleep(30);current=status()
            if current['stage']!=last:print(json.dumps(current),flush=True);last=current['stage']
        stop.set()
        if current['stage']!='COMPLETED':
            download(api,record,models=False);raise RuntimeError('Cloud job ended with '+current['stage'])
    run,models=download(api,record,models=a.models or a.action=='watch');completion=json.loads((run/'COMPLETION.json').read_text());result=dict(status=completion['status'],cloud=current,models=models,approved_data_unchanged=True,protected_v2_reports_unchanged=True)
    if completion['status']=='complete':result['release']=release()
    write_json('reports/v2_2/LOCAL_COMPLETION.json',result);print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
