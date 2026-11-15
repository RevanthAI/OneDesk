"""Project SFT backend using AgentTune's real lifecycle, config and logging.

The pinned upstream TRL SFT implementation is absent. This subclass supplies
model/data/optimizer hooks while AgentTune owns the training loop/callbacks.
The assistant-only sparse, checkpointed CE is mathematically standard causal
cross-entropy but avoids materializing full sequence x 262k vocabulary logits.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import time
import torch
from torch.utils.checkpoint import checkpoint
from agenttune.core.sft.trainer_base import SFTTrainerBase
from .sft_data import collate


def sparse_causal_loss(hidden,labels,head,scale=1.0,chunk_size=128,recompute=True):
    valid=labels[:,1:]!=-100
    h=hidden[:,:-1][valid];targets=labels[:,1:][valid]
    if not targets.numel():raise ValueError('empty loss mask')
    def loss_part(x,y):
        logits=head(x)*scale
        return torch.nn.functional.cross_entropy(logits.float(),y,reduction='sum')
    total=hidden.new_zeros((),dtype=torch.float32)
    for start in range(0,len(targets),chunk_size):
        x=h[start:start+chunk_size];y=targets[start:start+chunk_size]
        value=checkpoint(loss_part,x,y,use_reentrant=False) if recompute and torch.is_grad_enabled() else loss_part(x,y)
        total=total+value
    return total/targets.numel()


class DriftGuardSFTTrainer(SFTTrainerBase):
    def __init__(self,config,model,tokenizer,rows,validation,output,accumulation=1):
        super().__init__(config)
        self.model=model;self.tokenizer=tokenizer;self.rows=rows;self.validation=validation
        self.output=Path(output);self.output.mkdir(parents=True,exist_ok=True)
        self.accumulation=accumulation;self.history=[];self.samples_seen=0
        self.optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=config.train.learning_rate,weight_decay=.01)
        steps=config.train.max_steps;warmup=max(1,int(steps*.05))
        self.scheduler=torch.optim.lr_scheduler.LambdaLR(self.optimizer,lambda step:min(1.,(step+1)/warmup)*(.5*(1+math.cos(math.pi*max(0,step-warmup)/max(1,steps-warmup)))))
    def setup_model(self):
        self.model.train();self.model.config.use_cache=False
    def setup_data(self):
        self.dataset=self.rows
        self.data_loader=iter(self.create_data_loader())
    def create_data_loader(self):
        from torch.utils.data import DataLoader
        generator=torch.Generator().manual_seed(42+self.samples_seen)
        return DataLoader(self.rows,batch_size=self.config.train.per_device_batch_size,shuffle=True,generator=generator,drop_last=False,collate_fn=lambda xs:collate(xs,self.tokenizer.pad_token_id,self.config.model.max_seq_length))
    def forward_loss(self,batch,recompute=True):
        causal=self.model.get_base_model()
        hidden=causal.model(input_ids=batch['input_ids'],attention_mask=batch['attention_mask'],use_cache=False).last_hidden_state
        return sparse_causal_loss(hidden,batch['labels'],causal.get_output_embeddings(),float(causal.logit_scale),recompute=recompute)
    def train_step(self,batch):
        self.optimizer.zero_grad(set_to_none=True)
        losses=[];supervised=0
        start=time.perf_counter()
        for index in range(self.accumulation):
            current=batch if index==0 else self.get_next_batch()
            current={k:v.to('cuda') for k,v in current.items()}
            with torch.autocast('cuda',dtype=torch.bfloat16):loss=self.forward_loss(current)
            if not torch.isfinite(loss):raise FloatingPointError('non-finite loss')
            (loss/self.accumulation).backward();losses.append(float(loss.detach()));self.samples_seen+=len(current['input_ids'])
            supervised+=int((current['labels']!=-100).sum())
        self.state.update_epoch(self.samples_seen/len(self.rows))
        grad=torch.nn.utils.clip_grad_norm_([p for p in self.model.parameters() if p.requires_grad],1.)
        if not torch.isfinite(grad):raise FloatingPointError('non-finite gradient')
        self.optimizer.step();self.scheduler.step();torch.cuda.synchronize()
        metrics={'loss':sum(losses)/len(losses),'grad_norm':float(grad),'seconds':time.perf_counter()-start,'supervised_tokens':supervised,'samples_seen':self.samples_seen,'learning_rate':self.optimizer.param_groups[0]['lr']}
        self.history.append(metrics)
        with (self.output/'training_log.jsonl').open('a') as f:f.write(json.dumps(dict(step=len(self.history),**metrics))+'\n')
        print(json.dumps({'event':'sft_step','step':len(self.history),**metrics}),flush=True)
        return metrics
    def evaluate(self,*args,**kwargs):
        self.model.eval();values=[]
        with torch.no_grad():
            for i in range(0,len(self.validation),1):
                batch=collate(self.validation[i:i+1],self.tokenizer.pad_token_id,self.config.model.max_seq_length)
                batch={k:v.to('cuda') for k,v in batch.items()}
                with torch.autocast('cuda',dtype=torch.bfloat16):values.append(float(self.forward_loss(batch,recompute=False)))
        metrics={'validation_loss':sum(values)/len(values)} if values else {}
        self.model.train()
        (self.output/'validation.json').write_text(json.dumps(metrics,indent=2))
        return metrics
    def save_checkpoint(self):
        path=self.output/f'checkpoint-{self.state.step+1}'
        self.model.save_pretrained(path,safe_serialization=True);self.tokenizer.save_pretrained(path)
        torch.save({'optimizer':self.optimizer.state_dict(),'scheduler':self.scheduler.state_dict(),'state_step':self.state.step,'samples_seen':self.samples_seen},path/'optimizer_state.pt')
        self.state.checkpoint_path=str(path)
        if self.callback_handler:self.callback_handler.on_save(self.config,self.state,self.control)
