from __future__ import annotations

def encode_trajectory(row,tokenizer,max_length=2560):
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


def collate(rows,pad_token_id,pad_length=2560):
    import torch
    if max(len(r['input_ids']) for r in rows)>pad_length:raise ValueError('batch would truncate')
    inputs=[];labels=[];mask=[]
    for r in rows:
        n=len(r['input_ids']);pad=pad_length-n
        inputs.append(r['input_ids']+[pad_token_id]*pad)
        labels.append(r['labels']+[-100]*pad)
        mask.append([1]*n+[0]*pad)
    return {'input_ids':torch.tensor(inputs,dtype=torch.long),'labels':torch.tensor(labels,dtype=torch.long),'attention_mask':torch.tensor(mask,dtype=torch.long)}

