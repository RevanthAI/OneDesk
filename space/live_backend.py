"""Lazy, pinned live inference. Imports/downloads/weights are avoided in trace mode."""
import os,threading,time
from functools import lru_cache
from pathlib import Path
BASE='CohereLabs/tiny-aya-fire';BASE_REVISION='73500c80fcb6c8bea3e830c21d5d2920249a0e1a'
ADAPTER='Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val';ADAPTER_REVISION='016676680121b4dd90ec6026978de7ee1cdb1271'
_LOCK=threading.Lock();_CACHE={}
@lru_cache(maxsize=1)
def download_snapshots():
 from huggingface_hub import snapshot_download
 # The base is license-gated: HF_TOKEN is a server-side Space secret only.
 token=os.getenv('HF_TOKEN')
 base=snapshot_download(BASE,revision=BASE_REVISION,token=token,allow_patterns=['*.safetensors','*.json','*.model','*.txt','*.jinja','merges.txt'])
 adapter=snapshot_download(ADAPTER,revision=ADAPTER_REVISION,token=token,allow_patterns=['adapter*','*.json','*.model','*.txt','*.jinja'])
 return base,adapter
class LiveBackend:
 def __init__(self,model,tokenizer,device):self.model=model;self.tokenizer=tokenizer;self.device=device;self.tokens=0
 def context_fits(self,messages):return len(self.tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True))+192<=4096
 def generate_messages(self,batch):
  import torch
  prompts=[self.tokenizer.apply_chat_template(m,tokenize=False,add_generation_prompt=True) for m in batch]
  inputs=self.tokenizer(prompts,padding=True,return_tensors='pt',add_special_tokens=False,return_token_type_ids=False).to(self.device)
  if inputs['input_ids'].shape[1]+192>4096:raise ValueError('Conversation exceeds the 4,096-token sandbox limit.')
  with torch.inference_mode():
   out=self.model.generate(**inputs,max_new_tokens=192,do_sample=False,pad_token_id=self.tokenizer.pad_token_id,stop_strings=['</tool_call>','</final_answer>'],tokenizer=self.tokenizer,use_cache=True)
  generated=out[:,inputs['input_ids'].shape[1]:];self.tokens+=int(generated.numel())
  return self.tokenizer.batch_decode(generated,skip_special_tokens=True)
def get_backend():
 import torch
 from transformers import AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig
 from peft import PeftModel
 cuda=torch.cuda.is_available();device='cuda:0' if cuda else 'cpu'
 small=cuda and torch.cuda.get_device_properties(0).total_memory<12*2**30
 mode='CUDA NF4 / FP16 compute' if small else ('CUDA BF16' if cuda and torch.cuda.is_bf16_supported() else ('CUDA FP16' if cuda else 'CPU BF16 (slow)'))
 if mode in _CACHE:return _CACHE[mode]
 base,adapter=download_snapshots()
 dtype=torch.float16 if small or (cuda and not torch.cuda.is_bf16_supported()) else torch.bfloat16
 # Cohere2 SDPA GQA expansion avoids the small-GPU attention allocation spike.
 import transformers.integrations.sdpa_attention as sdpa
 sdpa.use_gqa_in_sdpa=lambda attention_mask,key:False
 kwargs={'dtype':dtype,'device_map':{'':device},'low_cpu_mem_usage':True,'attn_implementation':'sdpa'}
 if small:kwargs['quantization_config']=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.float16)
 if not cuda:torch.set_num_threads(min(4,os.cpu_count() or 2))
 tokenizer=AutoTokenizer.from_pretrained(base,padding_side='left')
 if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
 model=AutoModelForCausalLM.from_pretrained(base,**kwargs)
 model=PeftModel.from_pretrained(model,adapter,is_trainable=False).eval();model.config.use_cache=True
 result=(LiveBackend(model,tokenizer,device),mode);_CACHE[mode]=result;return result
try:
 import spaces
 gpu=spaces.GPU(duration=120)
except ImportError:
 def gpu(fn):return fn
@gpu
def gpu_episode(task_id,question,active):
 try:from .demo_core import run_sandbox
 except ImportError:from demo_core import run_sandbox
 with _LOCK:
  backend,mode=get_backend();before=backend.tokens;start=time.perf_counter()
  t,episode=run_sandbox(task_id,question,active,backend)
  return t,episode,{'mode':mode,'seconds':time.perf_counter()-start,'generated_tokens':backend.tokens-before,'base_revision':BASE_REVISION,'adapter_revision':ADAPTER_REVISION}
