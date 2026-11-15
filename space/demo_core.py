"""Fast, model-free trace browsing, safe HTML rendering and real MCP episodes."""
from __future__ import annotations
import base64,copy,html,json,time
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from pathlib import Path
try:
 from .runtime.mcp_env import MCPEnv,SCHEMAS
 from .runtime.mcp_adapter import initial_messages
 from .runtime.evaluation_core import run_batch,measure
except ImportError:
 from runtime.mcp_env import MCPEnv,SCHEMAS
 from runtime.mcp_adapter import initial_messages
 from runtime.evaluation_core import run_batch,measure
ROOT=Path(__file__).resolve().parent;ASSETS=ROOT/'assets'
@lru_cache(maxsize=1)
def index():return json.loads((ASSETS/'holdout_traces_index.json').read_text())
@lru_cache(maxsize=3)
def world(split):return json.loads((ASSETS/('world_'+split+'.json')).read_text())
def task(task_id):return index()['tasks'][task_id]['task']
def j(value):return json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)
def esc(value):return html.escape(str(value),quote=True)
def obs(value):
 return esc(j(value)).replace('[STAGING-ONLY]','<mark class="odk-stage">[STAGING-ONLY]</mark>').replace('[PROD]','<mark class="odk-prod">[PROD]</mark>')
def record(task_id,key='final'):return index()['tasks'][task_id]['episodes'][key]
def is_category(t,entry,category):
 if category=='wins':return t['kind']=='conflict' and entry['episodes']['final']['metrics']['stale_catch']==1 and entry['episodes']['full_sft']['metrics']['stale_catch']==0
 if category=='collapse':return t['expected_status']!='abstain' and (entry['episodes']['collapsed'].get('prediction') or {}).get('status')=='abstain'
 if category=='languages':return t['language'] in ['hi','hinglish','te']
 if category=='chains':return t['kind']=='incident' and t['incident_subtype'] in ['payload_lb','payload_mib']
 return True
def choices(language='All',kind='All',category='all'):
 result=[];flagships={r['task_id'] for r in index()['flagships']}
 for task_id,entry in index()['tasks'].items():
  t=entry['task'];lang=t['language']+':'+t['script']
  if language!='All' and lang!=language:continue
  if kind!='All' and t['kind']!=kind:continue
  if not is_category(t,entry,category):continue
  prefix='★ ' if task_id in flagships else ''
  result.append((f"{prefix}[{task_id}] [{lang}] [{t['kind']}] {t['question'][:105]}",task_id))
 return sorted(result,key=lambda r:(not r[0].startswith('★'),r[1]))
def badge(label,value,percentage=False):
 if value is None:return f'<span class="odk-badge neutral">{esc(label)}: —</span>'
 text=f'{value*100:.1f}%' if percentage else ('✅ PASS' if value else '❌ FAIL')
 return f'<span class="odk-badge {"pass" if value else "fail"}">{esc(label)}: {text}</span>'
def render_episode(t,episode,label,scored=True):
 pred=episode.get('prediction') or {};m=episode.get('metrics') or measure(t,episode)
 facts={k:t.get(v) for k,v in [('case_id','case_id'),('kind','kind'),('language','language'),('script','script'),('gold_value','gold_value'),('gold_status','expected_status'),('gold_cites','gold_cites'),('gold_stale_source','stale_doc_id')]}
 if not scored:facts={'task_context':t['task_id'],'scoring':'Custom question/tools: frozen benchmark labels do not apply.'}
 badges=''.join([badge('Exact outcome',m['exact_outcome'] if scored else None),badge('Strict stale-doc catch',m['stale_catch'] if scored else None),badge('Verified citation F1',m['verified_citation_f1'] if scored else None,True),badge('Required chain',m['required_chain_compliance'] if scored else None)])
 reward=f"{m['anti_collapse_reward']:+.2f}" if scored else 'unscored'
 out=[f'<section class="odk-result"><div class="odk-result-head"><h2>{esc(label)}</h2><span class="odk-badge neutral">{esc(episode.get("completion_reason",""))}</span></div><div class="odk-summary"><details><summary>Task & reference labels</summary><pre>{esc(j(facts))}</pre></details><div class="odk-badges">{badges}<span class="odk-badge neutral">Anti-collapse reward: {reward}</span></div></div>']
 for n,call in enumerate(episode.get('calls',[]),1):
  server=call.get('server','unknown');color={'notion-mcp':'#6366f1','github-mcp':'#334155','slack-mcp':'#a21caf','db-mcp':'#0284c7','time-mcp':'#d97706','unit-converter-mcp':'#059669','math-mcp':'#7c3aed'}.get(server,'#64748b')
  out.append(f'<article class="odk-step" style="border-left-color:{color}"><div class="odk-step-head"><b>Turn {n}</b><span class="odk-server" style="background:{color}">{esc(server)}</span><code>{esc(call.get("tool",""))}</code></div><div class="odk-observations"><div><h4>Arguments</h4><pre>{esc(j(call.get("arguments",{})))}</pre></div><div><h4>Returned tool observation</h4><pre>{obs(call.get("output"))}</pre></div></div></article>')
 if not episode.get('calls'):out.append('<div class="odk-empty">No tool calls executed.</div>')
 if pred:
  retrieved=set(episode.get('retrieved_ids',[]));cites=''.join(f'<span class="odk-badge {"pass" if cite in retrieved else "fail"}">{"✓" if cite in retrieved else "✗"} {esc(cite)}</span>' for cite in pred.get('cites',[])) or '<span class="odk-muted">No citations</span>'
  value='null' if pred.get('value') is None else str(pred['value'])
  out.append(f'<div class="odk-resolution"><span class="odk-badge neutral">{esc(pred.get("status","").upper())}</span><div class="odk-value">{esc(value)}</div><div>{cites}</div>')
  if pred.get('stale_source'):out.append(f'<div class="odk-stale">⚑ Outdated page flagged: <strong>{esc(pred["stale_source"])}</strong></div>')
  out.append(f'<details><summary>Final answer JSON</summary><pre>{esc(j(pred))}</pre></details></div>')
 else:out.append('<div class="odk-empty">No valid structured final answer. Inspect the raw protocol below.</div>')
 out.append('</section>');return ''.join(out)
def raw_trace(episode):return '\n'.join(episode.get('raw_turns',[]))
def inspect_trace(task_id,question=None,active=None):
 t=task(task_id);ep=record(task_id);note='Recorded, scored holdout episode — no model generation or external service is running.'
 if question is not None and (question.strip()!=t['question'].strip() or set(active or [])!=set(t['active_mcps'])):note+=' Your edits apply only to Live mode; this saved trace answers the original selected benchmark question.'
 return render_episode(t,ep,'OneDesk · saved verified trace'),raw_trace(ep),note
COMPARISON_KEYS=['base','collapsed','full_sft','final']
def comparison(task_id):
 t=task(task_id)
 return tuple(render_episode(t,record(task_id,k),index()['checkpoints'][k])+f'<details class="odk-raw"><summary>Raw XML / JSON turns</summary><pre>{esc(raw_trace(record(task_id,k)))}</pre></details>' for k in COMPARISON_KEYS)
def run_sandbox(task_id,question,active,backend):
 t=copy.deepcopy(task(task_id));t['question']=question.strip()
 if not t['question'] or len(t['question'])>1800:raise ValueError('Use a question between 1 and 1,800 characters.')
 if not set(active)<=set(SCHEMAS):raise ValueError('Unknown MCP server.')
 t['active_mcps']=list(active)
 # Only the question and actual active schemas go into the model prompt; never gold labels.
 with MCPEnv(world(t['world_split']),t['active_mcps']) as env:t['prompt']=initial_messages(t,env)
 ep=run_batch([t],world(t['world_split']),backend)[0];ep['metrics']=measure(t,ep)
 return t,ep
@lru_cache(maxsize=2)
def iframe(name):
 if name not in ['rollout_explorer.html','dashboard.html']:raise ValueError('Unknown explorer')
 content=(ASSETS/name).read_text()
 if name=='dashboard.html':
  for image in ['training_rollouts.svg','optimization.svg']:
   encoded=base64.b64encode((ASSETS/image).read_bytes()).decode()
   content=content.replace('src="'+image+'"','src="data:image/svg+xml;base64,'+encoded+'"')
 return f'<iframe title="{esc(name)}" sandbox="allow-scripts allow-downloads" loading="lazy" referrerpolicy="no-referrer" style="width:100%;height:1100px;border:1px solid #dbe3ef;border-radius:16px;background:white" srcdoc="{html.escape(content,quote=True)}"></iframe>'
def roi(monthly_queries,l40s_hourly,input_per_million,output_per_million):
 basis=json.loads((ASSETS/'roi_scenarios.json').read_text());q=float(monthly_queries)
 local_hours=q*basis['local_seconds_per_episode']/3600;gpu_hours=q*basis['l40s_mixed_cohort_seconds_per_episode']/3600
 local=local_hours*basis['electricity_power_kw']*basis['electricity_usd_per_kwh'];cloud=gpu_hours*float(l40s_hourly)
 api_exact=Decimal(str(q))*(Decimal(str(basis['input_tokens']))*Decimal(str(input_per_million))+Decimal(str(basis['output_tokens']))*Decimal(str(output_per_million)))/Decimal(1000000)
 api=float(api_exact.quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
 rows=[['Local RTX 2070 NF4',round(local,2),round(local/q*1000,2),round(local_hours,2),'Electricity only; $0 API fees'],['Self-hosted L40S BF16',round(cloud,2),round(cloud/q*1000,2),round(gpu_hours,2),'Measured batched throughput'],['Closed API scenario',round(api,2),round(api/q*1000,2),None,'Historical token-volume scenario']]
 text=f'**{int(q):,} audits/month:** local electricity **${local:,.2f}** · L40S **${cloud:,.2f}** · API **${api:,.2f}**. '
 if cloud>0:text+=f'API / L40S cost ratio: **{api/cloud:.1f}×**.'
 return rows,text
