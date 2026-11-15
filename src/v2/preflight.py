"""Approve only immutable v2 data and an untruncated 2560-token SFT view."""
import copy,json
from pathlib import Path
from .data import load,world,verify,write_json
from .oracle_solver import run_oracle
from .mcp_env import MCPEnv
from .sft_data import encode_trajectory


def encode_sft(tokenizer,output=None):
    verify();train=load('sft');validation=load('validation');w=world();cache={};val=[]
    for task in validation:
        if task['case_id'] not in cache:
            with MCPEnv(w,task['active_mcps']) as env:cache[task['case_id']]=run_oracle(task,env)['messages']
        row=copy.deepcopy(task);row['messages']=copy.deepcopy(cache[task['case_id']]);row['messages'][1]['content']=task['question'];val.append(row)
    encoded_train=[encode_trajectory(r,tokenizer,max_length=2560) for r in train]
    encoded_val=[encode_trajectory(r,tokenizer,max_length=2560) for r in val]
    report=dict(data_dir='data_v2',sft_examples=len(train),validation_examples=len(val),sft_semantic_cases=len({r['case_id'] for r in train}),validation_semantic_cases=len({r['case_id'] for r in val}),max_seq_length=2560,max_actual_tokens=max(len(r['input_ids']) for r in encoded_train+encoded_val),truncated_conversations=0,sft_epochs=1)
    assert report['truncated_conversations']==0 and report['max_actual_tokens']<=2560
    assert not {r['case_id'] for r in train}&{r['case_id'] for r in val}
    if output:write_json(output,report)
    return encoded_train,encoded_val,report
