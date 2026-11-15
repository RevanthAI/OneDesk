"""Explicit approved-v2 paths and immutable manifest checks."""
import hashlib,json
from pathlib import Path
DATA=Path('data_v2')
FILES={'sft':'train_sft_240.jsonl','validation':'val_train_80.jsonl','stage1':'train_grpo_stage1.jsonl','stage2':'train_grpo_stage2.jsonl','test_synth':'holdout_synth_400_frozen.jsonl','repo_style':'holdout_repo_style_100_frozen.jsonl'}
EXPECTED={'sft':240,'validation':80,'stage1':400,'stage2':480,'test_synth':400,'repo_style':100}

def verify(data=DATA):
    data=Path(data)
    if data.name!='data_v2':raise ValueError('v2 pipeline must bind explicitly to data_v2/')
    entries={}
    for line in (data/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        if Path(name).name!=name:raise ValueError('unsafe frozen filename')
        actual=hashlib.sha256((data/name).read_bytes()).hexdigest()
        if actual!=digest:raise ValueError('approved v2 artifact changed: '+name)
        entries[name]=digest
    if len(entries)!=15:raise ValueError('expected the approved fifteen-artifact manifest')
    return entries

def load(split,data=DATA):
    verify(data);rows=[json.loads(line) for line in (Path(data)/FILES[split]).read_text().splitlines()]
    if len(rows)!=EXPECTED[split] or len({r['task_id'] for r in rows})!=len(rows):raise ValueError('wrong v2 split count or duplicate IDs')
    if any(r.get('schema_version')!=2 for r in rows):raise ValueError('not v2 data')
    return rows

def world(split='train',data=DATA):
    verify(data);return json.loads((Path(data)/('world_'+split+'.json')).read_text())

def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')

def write_jsonl(path,rows):
    Path(path).write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in rows))
