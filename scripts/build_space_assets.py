"""Bundle immutable recorded evidence and stdlib MCP runtime; never run a model."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.v2_2.manage import protected
from src.v2_2.evaluation_core import measure
CHECKPOINTS={
 'base':('Base (Tiny Aya Fire 3.35B)','reports/v2/v2_base_fire'),
 'collapsed':('Collapsed RL (v2 340-update Refusal Trap)','reports/v2/v2_grpo_fire'),
 'warmup':('Warmup SFT (2-Epoch / 60 steps)','reports/v2_2/sft_evaluation'),
 'full_sft':('Full SFT (4-Epoch / 120 steps)','reports/v2_2/sft_full_evaluation'),
 'final':('OneDesk Final Agent (Warmup + Anti-Collapse GRPO, Update 40)','reports/v2_2/grpo_evaluation')}
def read_rows(p):return [json.loads(x) for x in p.read_text().splitlines()]
def copy(source,target):
 target.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['cp','-L',str(source),str(target)],check=True)
def main():
 protected();out=ROOT/'space/assets';out.mkdir(parents=True,exist_ok=True);tasks={};provenance={}
 for split,filename in [('test_synth','holdout_synth_400_frozen.jsonl'),('repo_style','holdout_repo_style_100_frozen.jsonl')]:
  source=ROOT/'data_v2'/filename;copy(source,out/filename)
  for task in read_rows(source):
   tasks[task['task_id']]={'task':{k:v for k,v in task.items() if k!='prompt'},'episodes':{}}
  for key,(label,folder) in CHECKPOINTS.items():
   epfile=ROOT/folder/(split+'_episodes.jsonl');metricfile=ROOT/folder/(split+'_metrics.jsonl')
   metrics={r['task_id']:r for r in read_rows(metricfile)}
   episodes=read_rows(epfile);assert len(episodes)==(400 if split=='test_synth' else 100)
   for episode in episodes:
    compact={k:v for k,v in episode.items() if k!='messages'};compact['recorded_metrics']=metrics[episode['task_id']];compact['metrics']=measure(tasks[episode['task_id']]['task'],episode)
    tasks[episode['task_id']]['episodes'][key]=compact
   provenance[str(epfile.relative_to(ROOT))]=hashlib.sha256(epfile.read_bytes()).hexdigest()
 assert len(tasks)==500 and all(len(t['episodes'])==5 for t in tasks.values())
 flags=[]
 for category,predicate in [
  ('Final beats full SFT · strict conflict',lambda t:t['task']['kind']=='conflict' and t['episodes']['final']['metrics']['stale_catch']==1 and t['episodes']['full_sft']['metrics']['stale_catch']==0),
  ('SQL + conversion',lambda t:t['task']['incident_subtype'] in ('payload_lb','payload_mib') and t['episodes']['final']['metrics']['exact_outcome']==1),
  ('Safe refusal',lambda t:t['task']['kind']=='abstain' and t['episodes']['final']['metrics']['exact_outcome']==1)]:
  chosen=next((t for t in tasks.values() if predicate(t) and t['task']['language']=='en'),None)
  if chosen:flags.append({'label':category,'task_id':chosen['task']['task_id']})
 for language,script in [('hi','native'),('hinglish','latin'),('te','native')]:
  chosen=next(t for t in tasks.values() if t['task']['language']==language and t['task']['script']==script and t['task']['kind']=='conflict' and t['episodes']['final']['metrics']['stale_catch']==1)
  flags.append({'label':language+':'+script+' · resolved conflict','task_id':chosen['task']['task_id']})
 payload={'schema_version':1,'checkpoints':{k:v[0] for k,v in CHECKPOINTS.items()},'flagships':flags,'tasks':tasks,'provenance_sha256':provenance}
 (out/'holdout_traces_index.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n')
 for name in ['world_train.json','world_test_synth.json','world_repo_style.json']:copy(ROOT/'data_v2'/name,out/name)
 for path in (ROOT/'figures').glob('*.png'):copy(path,out/'figures'/path.name)
 training=ROOT/'reports/v2_2/downloads/warmup-20261113T084035Z/grpo_training'
 for name in ['rollout_explorer.html','dashboard.html','training_rollouts.svg','optimization.svg']:copy(training/name,out/name)
 for name in ['mcp_env.py','v2_env.py','mcp_adapter.py','v2_tasks.py','world_generator.py','reward.py','evaluation_core.py','v2_oracle.py']:
  copy(ROOT/'src/v2_2'/name,ROOT/'space/runtime'/name)
 (ROOT/'space/runtime/__init__.py').write_text('"""Standalone, stdlib-only recorded-benchmark MCP runtime."""\n')
 for name in ['LICENSE','LICENSE-DATA.md']:copy(ROOT/name,ROOT/'space'/name)
 copy(ROOT/'reports/submission/ROI_SCENARIOS.json',out/'roi_scenarios.json')
 files=[p for p in out.rglob('*') if p.is_file()]+list((ROOT/'space/runtime').glob('*.py'))
 manifest={str(p.relative_to(ROOT/'space')):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
 (out/'BUNDLE_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n');protected()
 print(json.dumps({'tasks':len(tasks),'episodes':2500,'checkpoints':5,'assets_bytes':sum(p.stat().st_size for p in files),'flagships':flags}))
if __name__=='__main__':main()
