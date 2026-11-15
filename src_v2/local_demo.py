"""Optional post-download NF4 deployment demo; never part of cloud BF16 results."""
import argparse,json,os
from pathlib import Path
from dotenv import load_dotenv
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM,BitsAndBytesConfig
from peft import PeftModel
from .backend import Backend,MODEL,REVISION
from .data import load,world,write_json
from .evaluation_core import run_batch,measure


def main():
    p=argparse.ArgumentParser();p.add_argument('--adapter',default='checkpoints_v2/grpo_adapter');p.add_argument('--split',choices=('validation','test_synth','repo_style'),default='test_synth');p.add_argument('--task-id');p.add_argument('--language',default='en');p.add_argument('--kind',default='conflict');p.add_argument('--output',default='reports_v2/local_deployment_example.json');a=p.parse_args()
    if not Path(a.adapter,'adapter_model.safetensors').is_file():raise FileNotFoundError('Download the v2 adapter first: python -m src_v2.manage download --models')
    if not torch.cuda.is_available():raise RuntimeError('CUDA GPU required')
    load_dotenv(Path.cwd().parent/'.env');token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN')
    import transformers.integrations.sdpa_attention as sdpa
    sdpa.use_gqa_in_sdpa=lambda attention_mask,key:False
    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=REVISION,token=token,padding_side='left')
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.float16)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REVISION,token=token,dtype=torch.float16,quantization_config=quant,attn_implementation='sdpa',device_map={'':'cuda:0'})
    model=PeftModel.from_pretrained(model,a.adapter,is_trainable=False).eval()
    tasks=load(a.split);selected=[t for t in tasks if (t['task_id']==a.task_id if a.task_id else t['language']==a.language and t['kind']==a.kind)]
    if not selected:raise ValueError('No matching frozen v2 task')
    task=selected[0];backend=Backend(model,tokenizer);episode=run_batch([task],world('train' if a.split=='validation' else a.split),backend)[0]
    for m in task['prompt']:
        if m['role']=='user':print('QUESTION:',m['content'])
    for turn in episode['raw_turns']:print(turn)
    result=dict(deployment='local NF4 / FP16 compute; separate from cloud BF16 benchmark',adapter=str(Path(a.adapter).resolve()),metrics=measure(task,episode),episode=episode)
    write_json(a.output,result);print(json.dumps(result['metrics'],indent=2));print('Saved:',a.output)

if __name__=='__main__':main()
