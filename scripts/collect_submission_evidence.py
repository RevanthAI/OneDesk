import os
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
import json,hashlib,statistics,re
from pathlib import Path
from collections import Counter
from src.v2_2.manage import protected
from src.v2_2.reward import score_episode
from src.v2_2.mcp_env import MCPEnv
from src.v2_2.oracle_solver import run_oracle
out=Path('reports/submission');out.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text())
def rows(p):return [json.loads(l) for l in Path(p).read_text().splitlines()]
def save(n,d):(out/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert protected()==19
# Read and hash every relevant existing text/config/runtime artifact once by real path.
seen=set();inventory=[];jsons={};plots=[];repos=set();revisions=[]
roots=[Path(p) for p in ['reports/v1','reports/v2','reports/v2_1','reports/v2_2','docs/archive/data_v1','data_v2','configs']]+list(Path('.').glob('checkpoints*'))
for root in roots:
 for p in sorted(root.rglob('*')):
  if not p.is_file() or '.cache' in p.parts or '__pycache__' in p.parts:continue
  rp=p.resolve()
  if rp in seen:continue
  seen.add(rp)
  if p.suffix.lower() not in ('.md','.json','.jsonl','.yaml','.yml','.log','.csv','.txt','.png','.svg','.html') and 'SHA256' not in p.name:continue
  raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest();inventory.append(dict(path=str(p),bytes=len(raw),sha256=h))
  if p.suffix in ('.png','.svg','.html'):plots.append(str(p))
  if p.suffix=='.json':
   try:d=json.loads(raw);jsons[str(p)]=d
   except (ValueError,UnicodeDecodeError):continue
   def walk(v):
    if isinstance(v,dict):
     for k,x in v.items():
      if isinstance(x,str) and re.fullmatch(r'Revanth-ml/[A-Za-z0-9_.-]+',x):repos.add(x)
      if isinstance(x,str) and re.fullmatch(r'[0-9a-f]{40}',x):revisions.append(dict(file=str(p),key=k,revision=x))
      walk(x)
    elif isinstance(v,list):
     for x in v:walk(x)
   walk(d)
save('SOURCE_INVENTORY.json',inventory);save('REPOSITORIES_AND_REVISIONS.json',dict(repos=sorted(repos),revisions=revisions));save('PLOT_INVENTORY.json',plots)
world=read('data_v2/world_test_synth.json');tasks=rows('data_v2/holdout_synth_400_frozen.jsonl')[::4];assert len(tasks)==100 and all(t['language']=='en' for t in tasks)
policies=['AlwaysAbstainPolicy','DumpAllNumbersPolicy','TrustOnlyNotionLazyPolicy','SpamAllToolsThenGuessPolicy','HallucinateCitationsWithoutToolsPolicy','MentalMathSkipUtilityPolicy','HonestOraclePolicy'];scores={}
for name in policies:
 selected=[t for t in tasks if t['incident_subtype'] in ('sla_penalty','payload_lb','payload_mib')] if name=='MentalMathSkipUtilityPolicy' else tasks
 es=[]
 for t in selected:
  with MCPEnv(world,t['active_mcps']) as env:
   if name in ('HonestOraclePolicy','MentalMathSkipUtilityPolicy'):
    e=run_oracle(t,env)
    if name=='MentalMathSkipUtilityPolicy':e['calls']=[c for c in e['calls'] if c['server']=='db-mcp'];e['num_tool_calls']=len(e['calls'])
   else:
    pred=dict(status='answered',value='100, 250, 500',cites=[],stale_source=None)
    if name=='AlwaysAbstainPolicy':pred.update(status='abstain',value=None)
    if name=='TrustOnlyNotionLazyPolicy':
     rr=env.call('notion-mcp','search_notion',{'query':t['service_name']+' '+t['param_name']});prod=next((r for r in rr if r.get('environment')=='prod'),None)
     if prod:
      m=re.search(r'= ([\d.]+)',prod['snippet']);pred.update(value=m[1] if m else 'invalid',cites=[prod['page_id']])
    if name=='SpamAllToolsThenGuessPolicy':
     from src.v2_2.mcp_env import SCHEMAS
     for s,tools in SCHEMAS.items():
      tool=next(iter(tools));args={k:(1 if typ=='number' else 'irrelevant') for k,typ in tools[tool].items()};env.call(s,tool,args)
     pred['value']='500'
    if name=='HallucinateCitationsWithoutToolsPolicy':pred.update(value='250',cites=['NOTION-FAKE','PR-FAKE'])
    e=dict(prediction=pred,calls=env.calls,retrieved_ids=sorted(env.retrieved_ids),num_tool_calls=len(env.calls))
   es.append(e)
 scores[name]=dict(n=len(selected),**{mode:statistics.mean(score_episode(t,e,mode) for t,e in zip(selected,es)) for mode in ('specified','evidence_gated','anti_collapse')})
save('REWARD_AUDIT.json',dict(cohort='Frozen v2 synthetic: 100 English semantic cases; MentalMath is restricted to 11 utility incident cases. Deterministic policies, no LLM inference.',scores=scores,mental_math='Uses oracle-correct scalar with DB evidence but removes utility calls; tests a knowingly privileged shortcut upper bound. Not a learned baseline.',lazy='Selects PROD Notion instead of staging, to isolate stale-only failure. No deployment verification.'))
# Tokenize saved traces only. No model weights are loaded or generation performed.
from transformers import AutoTokenizer
tok=AutoTokenizer.from_pretrained(str(Path('checkpoints/v2_2/sft_warmup_adapter').resolve()),local_files_only=True)
tokens={}
for name,folder in [('v1_sft','reports/v1/sft_fire_nf4'),('warmup','reports/v2_2/sft_evaluation'),('grpo','reports/v2_2/grpo_evaluation')]:
 episodes=[e for split in ('test_synth','repo_style') for e in rows(Path(folder)/(split+'_episodes.jsonl'))];inputs=[];outputs=[];turns=[]
 for e in episodes:
  it=ot=nt=0;msgs=e['messages']
  for i,m in enumerate(msgs):
   if m['role']=='assistant':
    it+=len(tok.apply_chat_template(msgs[:i],tokenize=True,add_generation_prompt=True));ot+=len(tok.encode(m['content'],add_special_tokens=False));nt+=1
  inputs.append(it);outputs.append(ot);turns.append(nt)
 runtime=read(Path(folder)/'runtime.json');n=len(episodes)
 tokens[name]=dict(n=n,mean_input_across_turns=statistics.mean(inputs),mean_output_across_turns=statistics.mean(outputs),total_reconstructed_input=sum(inputs),total_reconstructed_output=sum(outputs),mean_assistant_turns=statistics.mean(turns),input_p10=sorted(inputs)[int(n*.1)],input_p90=sorted(inputs)[int(n*.9)],output_p10=sorted(outputs)[int(n*.1)],output_p90=sorted(outputs)[int(n*.9)],runtime=runtime,runtime_episode_count=sum(v['n'] for v in read(Path(folder)/'summary.json').values()))
save('TOKEN_AND_ROI_EVIDENCE.json',dict(method='CPU-only cached tokenizer applied to each saved assistant-prefix. Repeated chat history billed again, unpadded. Decoded assistant token counts may differ from recorded backend counts, which include generation-side batch effects. No model inference.',cohorts=tokens))
print(json.dumps({'inventory_files':len(inventory),'plots':len(plots),'reward':scores,'tokens':{k:{x:v[x] for x in ('n','mean_input_across_turns','mean_output_across_turns','runtime_episode_count')} for k,v in tokens.items()}},ensure_ascii=False))
