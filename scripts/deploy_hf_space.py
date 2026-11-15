"""Smoke-test, publish and monitor the public OneDesk Gradio Space.

No weights are loaded by smoke tests. A scripted model boundary exercises the
actual live callback, protocol loop, SQLite and utilities; real inference is
opt-in through the deployed Live button.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib,json,os,sys,time
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
REPORT=ROOT/'reports/submission/space';REPORT.mkdir(parents=True,exist_ok=True)
REPO='Revanth-ml/OneDesk';URL='https://huggingface.co/spaces/'+REPO

def smoke():
 from src.v2_2.manage import protected
 protected();app=importlib.import_module('space.app');core=importlib.import_module('space.demo_core')
 assert len(core.index()['tasks'])==500
 totals={k:sum(e['episodes'][k]['metrics']['exact_outcome'] for e in core.index()['tasks'].values()) for k in core.index()['checkpoints']}
 assert totals=={'base':2,'collapsed':85,'warmup':354,'full_sft':385,'final':374},totals
 times=[]
 for task_id,entry in core.index()['tasks'].items():
  for key,episode in entry['episodes'].items():
   result=core.render_episode(entry['task'],episode,key);assert 'odk-result' in result
  started=time.perf_counter();core.inspect_trace(task_id);times.append(time.perf_counter()-started)
  assert len(core.comparison(task_id))==4
 class ScriptedBoundary:
  def __init__(self,turns):self.turns=iter(turns);self.tokens=0
  def generate_messages(self,batch):
   assert len(batch)==1;turn=next(self.turns);self.tokens+=len(turn.split());return [turn]
 selectors=[('conflict',None),('consistent',None),('abstain',None),('incident','sla_penalty'),('incident','payload_lb'),('incident','payload_mib'),('incident','config_audit')]
 live_checks=[]
 live=importlib.import_module('space.live_backend')
 for kind,subtype in selectors:
  pair=next((item for item in core.index()['tasks'].items() if item[1]['task']['kind']==kind and (not subtype or item[1]['task']['incident_subtype']==subtype) and item[1]['episodes']['final']['metrics']['exact_outcome']==1),None)
  if not pair:continue
  task_id,entry=pair;t=entry['task'];boundary=ScriptedBoundary(entry['episodes']['final']['raw_turns'])
  with patch.dict(os.environ,{'HF_TOKEN':'mock-local-test-only'}),patch.object(live,'download_snapshots',return_value=('offline-base','offline-adapter')),patch.object(live,'get_backend',return_value=(boundary,'scripted model boundary; real SQLite/tools')):
   rendered,raw,note=app.run_live(task_id,t['question'],t['active_mcps'])
  assert '✅ PASS' in rendered and 'LIVE' in rendered
  live_checks.append({'task_id':task_id,'kind':kind,'subtype':subtype,'real_tools':True,'model_boundary':'scripted; no weights loaded'})
 t=core.task(core.index()['flagships'][0]['task_id'])
 with core.MCPEnv(core.world(t['world_split']),t['active_mcps']) as env:
  rows=env.call('db-mcp','query_db',{'sql':'SELECT service_name FROM microservices LIMIT 2'});assert len(rows['rows'])==2
  denied=env.call('db-mcp','query_db',{'sql':'DELETE FROM microservices'});assert 'error' in denied
 bad=copy.deepcopy(core.record(t['task_id']));bad['prediction']['value']='<img src=x onerror=alert(1)>'
 escaped=core.render_episode(t,bad,'XSS check');assert '<img src=x' not in escaped and '&lt;img' in escaped
 assert 'srcdoc="' in core.iframe('rollout_explorer.html') and 'data:image/svg+xml;base64,' in core.iframe('dashboard.html')
 rows,_=core.roi(100000,1.8,2.5,10);assert [r[1] for r in rows]==[8.0,122.36,1316.66]
 assert len(app.demo.config['components'])>40
 protected();result={'tasks':500,'recorded_episodes_rendered':2500,'comparator_tasks':500,'mean_instant_ms':sum(times)/len(times)*1000,'max_instant_ms':max(times)*1000,'live_callback_checks':live_checks,'sqlite_read_only_authorizer_checked':True,'html_escaping_checked':True,'roi_default_costs':[r[1] for r in rows],'gradio_import_and_config_ok':True,'benchmark_model_weights_loaded':False,'protected_files':19}
 (REPORT/'LOCAL_SMOKE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return result

def publish(hardware='auto',wait=0,configure_model_secret=False):
 from dotenv import load_dotenv
 from huggingface_hub import HfApi,SpaceHardware
 import requests
 load_dotenv(ROOT.parent/'.env');token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN')
 if not token:raise RuntimeError('Set HUGGINGFACE_TOKEN or HF_TOKEN in the environment or parent .env.')
 api=HfApi(token=token);identity=api.whoami();assert identity['name']=='Revanth-ml','Expected Revanth-ml publishing identity'
 aliases={'l40s-small':'l40sx1'};hardware=aliases.get(hardware,hardware)
 requested=['zero-a10g','cpu-basic'] if hardware=='auto' else list(dict.fromkeys([hardware,'cpu-basic']))
 if hardware=='auto':
  try:
   existing=api.get_space_runtime(REPO);current=existing.hardware or existing.requested_hardware
   if current:requested=[getattr(current,'value',current)]
  except Exception:pass
 if any(h not in [v.value for v in SpaceHardware] for h in requested):raise ValueError('Unknown Space hardware flavor')
 attempts=[];created=False;selected=None
 for flavor in requested:
  try:
   api.create_repo(REPO,repo_type='space',space_sdk='gradio',private=False,exist_ok=True,space_hardware=SpaceHardware(flavor),space_sleep_time=900 if flavor not in ['zero-a10g','cpu-basic'] else None)
   api.request_space_hardware(REPO,SpaceHardware(flavor),sleep_time=900 if flavor not in ['zero-a10g','cpu-basic'] else None)
   attempts.append({'hardware':flavor,'accepted':True});selected=flavor;created=True;break
  except Exception as error:
   attempts.append({'hardware':flavor,'accepted':False,'error':str(error).replace(token,'[REDACTED]')[:700]})
 if not created:
  (REPORT/'DEPLOYMENT.json').write_text(json.dumps({'repo':REPO,'url':URL,'hardware_attempts':attempts,'uploaded':False},indent=2)+'\n')
  raise RuntimeError('Space hardware/create requests failed: '+json.dumps(attempts))
 api.update_repo_visibility(REPO,repo_type='space',private=False)
 # Never upload credentials. The gated base needs the owner's accepted access.
 # Prefer a dedicated read token when one is supplied; otherwise use the user's
 # already authorized deployment token, stored only in private Space secrets.
 if configure_model_secret:
  model_token=os.getenv('HF_READ_TOKEN') or os.getenv('HUGGINGFACE_READ_TOKEN') or token
  api.add_space_secret(REPO,key='HF_TOKEN',value=model_token)
 commit=api.upload_folder(repo_id=REPO,repo_type='space',folder_path=str(ROOT/'space'),ignore_patterns=['**/__pycache__/**','**/*.pyc','.env','**/.env','**/.cache/**'],commit_message='Public OneDesk: 500-task trace browser, live MCP sandbox and benchmark dashboard')
 receipt={'repo':REPO,'url':URL,'revision':commit.oid,'hardware':selected,'hardware_attempts':attempts,'uploaded':True,'runtime_stage':None,'app_url':'https://revanth-ml-onedesk.hf.space','live_weights_smoke_performed':False,'model_secret_configured_by_this_run':configure_model_secret}
 deadline=time.time()+wait
 while True:
  runtime=api.get_space_runtime(REPO);receipt['runtime_stage']=str(runtime.stage);receipt['runtime']=runtime.raw
  (REPORT/'DEPLOYMENT.json').write_text(json.dumps(receipt,indent=2,default=str)+'\n');print(json.dumps({'event':'space_runtime','stage':str(runtime.stage),'url':URL}),flush=True)
  if str(runtime.stage)=='RUNNING':
   response=requests.get(receipt['app_url']+'/config',timeout=30)
   if response.ok:
    config=response.json();receipt['public_http_config_verified']=len(config.get('components',[]))>40
    if receipt['public_http_config_verified']:break
  if any(word in str(runtime.stage) for word in ['ERROR','FAILED']):break
  if time.time()>=deadline:break
  time.sleep(15)
 (REPORT/'DEPLOYMENT.json').write_text(json.dumps(receipt,indent=2,default=str)+'\n');print(URL);return receipt

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--smoke-only',action='store_true');p.add_argument('--hardware',default='auto');p.add_argument('--wait',type=int,default=0);p.add_argument('--configure-model-secret',action='store_true',help='Explicitly store the authorized model-read token as the private Space HF_TOKEN secret.');args=p.parse_args();smoke()
 if not args.smoke_only:publish(args.hardware,args.wait,args.configure_model_secret)
if __name__=='__main__':main()
