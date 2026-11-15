import copy
import pytest
from src.sft_data import load_training_rows,case_split,encode_trajectory,collate

class ToyTokenizer:
    def apply_chat_template(self,messages,tokenize=True,add_generation_prompt=False):
        ids=[1]
        for m in messages:
            ids += [2 if m['role']=='assistant' else 3]+[10+ord(c)%30 for c in m['content']]+[4]
        if add_generation_prompt:ids+=[2]
        return ids

def test_mask_teaches_assistants_only_including_tool_calls():
    row={'task_id':'train-x','case_id':'train-x','language':'en','kind':'conflict','messages':[{'role':'system','content':'secret instructions'},{'role':'user','content':'query'},{'role':'assistant','content':'tool call'},{'role':'user','content':'tool evidence'},{'role':'assistant','content':'final'}]}
    encoded=encode_trajectory(row,ToyTokenizer())
    assert sum(x!=-100 for x in encoded['labels'])==len('tool call')+1+len('final')+1
    assert all(y==x for x,y in zip(encoded['input_ids'],encoded['labels']) if y!=-100)
    with pytest.raises(ValueError,match='truncate'):encode_trajectory(row,ToyTokenizer(),max_length=5)

def test_training_validation_cases_and_languages_are_disjoint():
    rows=load_training_rows();train,val=case_split(rows)
    assert len(train)==360 and len(val)==40
    assert not {r['case_id'] for r in train}&{r['case_id'] for r in val}
    assert not {r['task_id'] for r in train}&{r['task_id'] for r in val}
    assert {r['world_split'] for r in rows}=={'train'}

def test_sparse_causal_loss_matches_dense_value_and_gradients():
    import torch
    from src.agenttune_sft_backend import sparse_causal_loss
    torch.manual_seed(42)
    hidden=torch.randn(2,7,8,requires_grad=True);labels=torch.randint(0,17,(2,7));labels[:,:3]=-100;labels[1,6]=-100
    head=torch.nn.Linear(8,17,bias=False)
    dense=torch.nn.functional.cross_entropy((head(hidden)*1.4)[:,:-1].reshape(-1,17),labels[:,1:].reshape(-1),ignore_index=-100)
    dense.backward();expected_h=hidden.grad.clone();expected_w=head.weight.grad.clone();hidden.grad=None;head.weight.grad=None
    sparse=sparse_causal_loss(hidden,labels,head,scale=1.4,chunk_size=2,recompute=True)
    sparse.backward()
    torch.testing.assert_close(dense,sparse)
    torch.testing.assert_close(expected_h,hidden.grad)
    torch.testing.assert_close(expected_w,head.weight.grad)

def test_sparse_loss_matches_peft_cohere2_forward():
    import torch
    from transformers import Cohere2Config,Cohere2ForCausalLM
    from peft import LoraConfig,get_peft_model
    from src.agenttune_sft_backend import sparse_causal_loss
    config=Cohere2Config(vocab_size=64,hidden_size=32,intermediate_size=64,num_hidden_layers=2,num_attention_heads=4,num_key_value_heads=2,head_dim=8,layer_types=['sliding_attention','full_attention'],sliding_window=32,max_position_embeddings=64,logit_scale=1.3)
    model=get_peft_model(Cohere2ForCausalLM(config),LoraConfig(r=2,lora_alpha=4,lora_dropout=0.,target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
    ids=torch.randint(5,64,(2,9));labels=ids.clone();labels[:,:4]=-100
    dense=model(input_ids=ids,labels=labels,use_cache=False).loss
    causal=model.get_base_model();hidden=causal.model(input_ids=ids,use_cache=False).last_hidden_state
    sparse=sparse_causal_loss(hidden,labels,causal.get_output_embeddings(),causal.logit_scale,chunk_size=3)
    torch.testing.assert_close(dense,sparse,rtol=1e-5,atol=1e-6)
    sparse.backward()
    assert any(p.grad is not None and p.grad.abs().sum()>0 for n,p in model.named_parameters() if 'lora_' in n)
    assert all(p.grad is None for n,p in model.named_parameters() if 'lora_' not in n)

def test_trained_adapter_merges_and_reloads_as_standalone_model(tmp_path):
    import torch
    from transformers import Cohere2Config,Cohere2ForCausalLM
    from peft import LoraConfig,get_peft_model
    torch.manual_seed(7)
    config=Cohere2Config(vocab_size=64,hidden_size=32,intermediate_size=64,num_hidden_layers=2,num_attention_heads=4,num_key_value_heads=2,head_dim=8,layer_types=['sliding_attention','full_attention'],sliding_window=32,max_position_embeddings=64)
    model=get_peft_model(Cohere2ForCausalLM(config),LoraConfig(r=2,lora_alpha=4,lora_dropout=0.,target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
    ids=torch.randint(5,64,(1,8));model.train()
    optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=.01)
    model(input_ids=ids,labels=ids,use_cache=False).loss.backward();optimizer.step();model.eval()
    expected=model(input_ids=ids,use_cache=False).logits.detach()
    model.save_pretrained(tmp_path/'adapter')
    merged=model.merge_and_unload().eval();merged.save_pretrained(tmp_path/'merged',safe_serialization=True)
    reloaded=Cohere2ForCausalLM.from_pretrained(tmp_path/'merged').eval()
    torch.testing.assert_close(expected,reloaded(input_ids=ids,use_cache=False).logits,atol=1e-5,rtol=1e-5)
    assert (tmp_path/'adapter'/'adapter_model.safetensors').exists()
    assert (tmp_path/'merged'/'model.safetensors').exists()
