import hashlib,json,re,subprocess,tempfile
from pathlib import Path
root=Path.cwd();out=root/'reports/submission'
def run(args,input=None):return subprocess.run(args,input=input,text=True,capture_output=True,check=False)
with tempfile.TemporaryDirectory(prefix='driftguard-gitcheck-',dir='/tmp') as td:
 r=run(['git','init','--quiet',td]);assert r.returncode==0,r.stderr
 base=['git','--git-dir',td+'/.git','--work-tree',str(root)]
 ignored=['.env','.env.production','secrets/token.txt','.venv/bin/python','venv/bin/python','src/__pycache__/x.pyc','.pytest_cache/x','checkpoints/v2_2/grpo_best_val_adapter/adapter_model.safetensors','checkpoints/v2/grpo_adapter/optimizer.pt','models/weights.bin','reports/v2_2/downloads/.cache/huggingface/x','cloud_bundle.zip']
 kept=['.gitignore','docs/SUBMISSION_DOSSIER.md','docs/archive/REPORT.md','README.md','src/v2_2/reward.py','tests/v2_2/test_warmup.py','configs/sft_config.yaml','data_v2/train_sft_240.jsonl','data_v2/SHA256SUMS','reports/v2_2/comparison','reports/v2_2/downloads/warmup-20261113T084035Z/comparison/grounding_tradeoffs.png','reports/v2_2/downloads/warmup-20261113T084035Z/comparison/FINDINGS.md','reports/v2_2/downloads/warmup-20261113T084035Z/comparison/comparison.svg','checkpoints/v2_2/grpo_best_val_adapter/adapter_config.json','.env.example','scripts/build_submission_dossier.py']
 bad=[]
 for p in ignored:
  r=run(base+['check-ignore','--no-index',p]);
  if r.returncode!=0:bad.append({'expected_ignored':p,'exit_code':r.returncode})
 for p in kept:
  r=run(base+['check-ignore','--no-index',p]);
  if r.returncode!=1:bad.append({'expected_eligible':p,'exit_code':r.returncode,'rule':r.stdout.strip()})
 # Every frozen path, including protected files not listed in the 15-artifact manifest.
 for p in (root/'data_v2').iterdir():
  if p.is_file():assert run(base+['check-ignore','--no-index',str(p.relative_to(root))]).returncode==1,p
 assert not bad,bad
 status=run(base+['status','--short','--ignored']);assert status.returncode==0,status.stderr
 (out/'git_status_preview.txt').write_text('Temporary Git index, real project worktree; actual checkout has no repository metadata.\n'+status.stdout)
 eligible=run(base+['ls-files','--others','--exclude-standard']);assert eligible.returncode==0
 files=eligible.stdout.splitlines(); large=[{'path':p,'bytes':(root/p).stat().st_size} for p in files if (root/p).is_file() and (root/p).stat().st_size>100*1024**2]
 assert not large,large
 (out/'GITIGNORE_VALIDATION.json').write_text(json.dumps(dict(actual_git_status='fatal: not a git repository',temporary_index_used=True,expected_ignored=ignored,expected_eligible=kept,protected_data_files_eligible=19,eligible_paths=len(files),eligible_files_over_100MiB=large,preview='reports/submission/git_status_preview.txt',nothing_staged_or_committed=True),indent=2)+'\n')
 print(json.dumps({'gitignore_checks':len(ignored)+len(kept)+19,'eligible_paths':len(files),'large_eligible_files':len(large)}))
# Local Markdown links, allowing HTTP sources and anchors.
dossier=root/'docs/SUBMISSION_DOSSIER.md'
text=dossier.read_text();missing=[]
for target in re.findall(r'\]\(([^)]+)\)',text):
 if target.startswith(('http://','https://','#')):continue
 if not (dossier.parent/target.split('#',1)[0]).exists():missing.append(target)
# Verification receipts are created after tests finish.
missing=[p for p in missing if p not in ['../reports/submission/VERIFICATION.json','../reports/submission/pytest.xml']]
assert not missing,missing
abstract=text.split('## 1. Submission Abstract\n',1)[1].split('**Exact abstract word count:',1)[0].strip();assert len(abstract.split())==365
assert len(re.findall(r'^## \d+\.',text,re.M))==11
print(json.dumps({'abstract_words':len(abstract.split()),'sections':11,'broken_local_links':missing}))
