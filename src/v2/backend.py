"""Cloud BF16 greedy evaluation, matching precision across Base/SFT/GRPO."""
import time,torch
from transformers import AutoModelForCausalLM,AutoTokenizer
MODEL='CohereLabs/tiny-aya-fire';REVISION='73500c80fcb6c8bea3e830c21d5d2920249a0e1a'

class Backend:
    def __init__(self,model,tokenizer):
        self.model=model;self.tokenizer=tokenizer;self.generated_tokens=0;self.seconds=0;self.oom_splits=0
    def context_fits(self,messages):
        return len(self.tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True))+192<=4096
    def generate_messages(self,batch):
        try:return self.generate(batch)
        except torch.cuda.OutOfMemoryError:
            if len(batch)==1:raise
            self.oom_splits+=1
        import gc
        gc.collect();torch.cuda.empty_cache();middle=len(batch)//2
        return self.generate_messages(batch[:middle])+self.generate_messages(batch[middle:])
    def generate(self,batch):
        prompts=[self.tokenizer.apply_chat_template(m,tokenize=False,add_generation_prompt=True) for m in batch]
        inputs=self.tokenizer(prompts,padding=True,return_tensors='pt',add_special_tokens=False,return_token_type_ids=False).to('cuda')
        if inputs['input_ids'].shape[1]+192>4096:raise ValueError('evaluation context budget exceeded')
        self.model.eval();self.model.config.use_cache=True
        start=time.perf_counter()
        with torch.inference_mode():
            outputs=self.model.generate(**inputs,max_new_tokens=192,do_sample=False,pad_token_id=self.tokenizer.pad_token_id,stop_strings=['</tool_call>','</final_answer>'],tokenizer=self.tokenizer,use_cache=True)
        tokens=outputs[:,inputs['input_ids'].shape[1]:]
        self.generated_tokens+=int((tokens!=self.tokenizer.pad_token_id).sum());self.seconds+=time.perf_counter()-start
        return self.tokenizer.batch_decode(tokens,skip_special_tokens=True)
    def stats(self):return dict(dtype='bfloat16',quantization=None,gpu=torch.cuda.get_device_name(0),generated_tokens=self.generated_tokens,generation_seconds=self.seconds,tokens_per_second=self.generated_tokens/self.seconds if self.seconds else None,oom_splits=self.oom_splits,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30)

def load_base():
    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=REVISION,padding_side='left')
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REVISION,dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':'cuda:0'})
    return model,tokenizer
