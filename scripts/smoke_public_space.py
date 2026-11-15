"""Check public Gradio APIs; --live explicitly requests one real model episode."""
import argparse,json,time
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def main():
 from gradio_client import Client
 from space import demo_core as core
 p=argparse.ArgumentParser();p.add_argument('--url',default='https://revanth-ml-onedesk.hf.space');p.add_argument('--live',action='store_true');p.add_argument('--timeout',type=int,default=900);args=p.parse_args()
 out=ROOT/'reports/submission/space';out.mkdir(parents=True,exist_ok=True)
 client=Client(args.url,hf_token=False,verbose=False,analytics_enabled=False,download_files=False,httpx_kwargs={'timeout':120})
 assert 'authorization' not in {key.lower() for key in client.headers}
 task_id=core.index()['flagships'][0]['task_id'];t=core.task(task_id)
 rendered,raw,note=client.predict(task_id,t['question'],t['active_mcps'],api_name='/inspect_trace')
 assert 'saved verified trace' in rendered and '3836' in rendered
 compared=client.predict(task_id,api_name='/compare_checkpoints');assert len(compared)==4
 live_button=next(c for c in client.config['components'] if c.get('props',{}).get('value','')=='🔥 Run Live Model Inference in MCP Sandbox (GPU / CPU)')
 result={'app_url':args.url,'public_without_authentication':True,'inspect_endpoint':True,'comparator_endpoint':True,'task_id':task_id,'model_inference_requested':args.live,'live_button_enabled':live_button['props'].get('interactive',True)}
 if args.live:
  started=time.perf_counter();job=client.submit(task_id,t['question'],t['active_mcps'],api_name='/live_inference')
  while not job.done():
   if time.perf_counter()-started>args.timeout:raise TimeoutError('Live endpoint exceeded smoke-test timeout')
   print(json.dumps({'event':'live_smoke_progress','status':str(job.status().code),'elapsed_seconds':round(time.perf_counter()-started,1)}),flush=True);time.sleep(10)
  live_html,live_raw,live_note=job.result()
  result.update(live_mode_note=live_note,live_raw_turns=live_raw,exact_outcome_pass='Exact outcome: ✅ PASS' in live_html,strict_stale_catch_pass='Strict stale-doc catch: ✅ PASS' in live_html,real_tool_cards=live_html.count('class="odk-step"'),wall_seconds=time.perf_counter()-started)
  (out/'LIVE_GPU_RENDER.html').write_text('<!doctype html><meta charset="utf-8"><title>OneDesk live model smoke</title>'+live_html)
  assert 'LIVE model' in live_html and result['real_tool_cards']>0
  assert 'CUDA' in live_note,'Live test ran without CUDA: '+live_note
 (out/('LIVE_GPU_SMOKE.json' if args.live else 'PUBLIC_API_SMOKE.json')).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,ensure_ascii=False));client.close()
if __name__=='__main__':main()
