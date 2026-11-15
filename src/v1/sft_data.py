"""Frozen train-only SFT data, exact assistant supervision, and case-level split."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def load_training_rows(path='docs/archive/data_v1/train_sft_400.jsonl', manifest='docs/archive/data_v1/SHA256SUMS'):
    path=Path(path)
    expected={line.split('  ',1)[1]:line.split('  ',1)[0] for line in Path(manifest).read_text().splitlines()}
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected[path.name]:raise ValueError('training hash mismatch')
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    if len(rows)!=400 or len({r['task_id'] for r in rows})!=400:raise ValueError('expected 400 unique training trajectories')
    if any(r['world_split']!='train' or not r['task_id'].startswith('train-') for r in rows):raise ValueError('non-training examples forbidden')
    return rows


def case_split(rows,validation_cases=10):
    cases=sorted({r['case_id'] for r in rows},key=lambda c:hashlib.sha256(('sft-validation-42:'+c).encode()).hexdigest())
    val=set(cases[:validation_cases])
    return [r for r in rows if r['case_id'] not in val],[r for r in rows if r['case_id'] in val]


def encode_trajectory(row,tokenizer,max_length=1536):
    messages=row['messages']
    ids=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=False)
    if len(ids)>max_length:raise ValueError('refusing to truncate assistant targets: '+row['task_id'])
    labels=[-100]*len(ids)
    for i,message in enumerate(messages):
        if message['role']!='assistant':continue
        prefix=tokenizer.apply_chat_template(messages[:i],tokenize=True,add_generation_prompt=True)
        complete=tokenizer.apply_chat_template(messages[:i+1],tokenize=True,add_generation_prompt=False)
        if complete[:len(prefix)]!=prefix or ids[:len(complete)]!=complete:raise ValueError('non-prefix-preserving chat template')
        labels[len(prefix):len(complete)]=ids[len(prefix):len(complete)]
    if not any(v!=-100 for v in labels):raise ValueError('no assistant supervision')
    return {'input_ids':ids,'labels':labels,'task_id':row['task_id'],'case_id':row['case_id'],'language':row['language'],'kind':row['kind']}


def collate(rows,pad_token_id,pad_length=1536):
    import torch
    if max(len(r['input_ids']) for r in rows)>pad_length:raise ValueError('batch would truncate')
    inputs=[];labels=[];mask=[]
    for r in rows:
        n=len(r['input_ids']);pad=pad_length-n
        inputs.append(r['input_ids']+[pad_token_id]*pad)
        labels.append(r['labels']+[-100]*pad)
        mask.append([1]*n+[0]*pad)
    return {'input_ids':torch.tensor(inputs,dtype=torch.long),'labels':torch.tensor(labels,dtype=torch.long),'attention_mask':torch.tensor(mask,dtype=torch.long)}


def representative_smoke(rows):
    groups={}
    for r in rows:
        key=(r['language'],r['kind'])
        if key not in groups or len(r['input_ids'])>len(groups[key]['input_ids']):groups[key]=r
    if len(groups)!=16:raise ValueError('smoke needs four languages and four task kinds')
    return sorted(groups.values(),key=lambda r:len(r['input_ids']),reverse=True)
