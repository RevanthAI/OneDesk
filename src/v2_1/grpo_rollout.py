"""Live sampled MCP trajectories; retain sampled token IDs and mask observations."""
from __future__ import annotations
import copy,json,time
import torch
from .mcp_env import MCPEnv
from .mcp_adapter import initial_messages,parse_turn,FormatError
from .reward import score_episode


def sample_episodes(tasks,world,model,tokenizer,temperature=.8,max_new_tokens=192,max_calls=6,max_context=4096):
    states=[];was_training=model.training;model.eval();model.config.use_cache=True
    for task in tasks:
        env=MCPEnv(world,task['active_mcps']);messages=copy.deepcopy(task.get('prompt') or initial_messages(task,env))
        text=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        ids=tokenizer.encode(text,add_special_tokens=False)
        states.append(dict(task=task,env=env,messages=messages,text=text,ids=ids,mask=[0]*len(ids),done=False,raw_turns=[],prediction=None,final_text='',completion_reason=None,tool_format_error=False,started=time.perf_counter()))
    try:
        for _ in range(max_calls+1):
            live=[s for s in states if not s['done']]
            for s in live:
                if len(s['ids'])+max_new_tokens>max_context:s.update(done=True,completion_reason='context_budget_exhausted')
            live=[s for s in live if not s['done']]
            if not live:break
            width=max(len(s['ids']) for s in live)
            device=next(model.parameters()).device
            inputs=torch.tensor([[tokenizer.pad_token_id]*(width-len(s['ids']))+s['ids'] for s in live],device=device)
            attention=torch.tensor([[0]*(width-len(s['ids']))+[1]*len(s['ids']) for s in live],device=device)
            kwargs=dict(max_new_tokens=max_new_tokens,pad_token_id=tokenizer.pad_token_id,stop_strings=['</tool_call>','</final_answer>'],tokenizer=tokenizer,use_cache=True,do_sample=temperature>0)
            if temperature>0:kwargs.update(temperature=temperature,top_p=1.,top_k=0)
            with torch.no_grad():generated=model.generate(input_ids=inputs,attention_mask=attention,**kwargs)[:,width:]
            for s,tokens in zip(live,generated.tolist()):
                while tokens and tokens[-1]==tokenizer.pad_token_id:tokens.pop()
                raw=tokenizer.decode(tokens,skip_special_tokens=True)
                s['ids'].extend(tokens);s['mask'].extend([1]*len(tokens));s['raw_turns'].append(raw)
                s['messages'].append({'role':'assistant','content':raw})
                try:
                    tag,obj=parse_turn(raw)
                    # Unexpected special-token text would make the canonical tool suffix ambiguous.
                    if tokenizer.decode(tokens,skip_special_tokens=False)!=raw:raise FormatError('unexpected special token in sampled turn')
                except FormatError:
                    s.update(done=True,completion_reason='malformed_output',final_text=raw,tool_format_error='<tool_call>' in raw);continue
                if tag=='final_answer':s.update(done=True,prediction=obj,final_text=raw,completion_reason='final_answer');continue
                if len(s['env'].calls)>=max_calls:s.update(done=True,completion_reason='tool_budget_exhausted',final_text=raw);continue
                result=s['env'].call(**obj)
                s['messages'].append({'role':'user','content':'Tool result: '+json.dumps(result,ensure_ascii=False)})
                next_text=tokenizer.apply_chat_template(s['messages'],tokenize=False,add_generation_prompt=True)
                prefix=s['text']+raw
                if not next_text.startswith(prefix):raise ValueError('non-prefix-preserving chat template')
                suffix=tokenizer.encode(next_text[len(prefix):],add_special_tokens=False)
                s['ids'].extend(suffix);s['mask'].extend([0]*len(suffix));s['text']=next_text
        outputs=[]
        for s in states:
            episode={k:s[k] for k in ('prediction','final_text','raw_turns','messages','tool_format_error')}
            episode.update(task_id=s['task']['task_id'],completion_reason=s['completion_reason'] or 'tool_budget_exhausted',calls=list(s['env'].calls),num_tool_calls=len(s['env'].calls),retrieved_ids=sorted(s['env'].retrieved_ids),elapsed_seconds=time.perf_counter()-s['started'])
            outputs.append(dict(episode=episode,input_ids=s['ids'],assistant_mask=s['mask'],reward=score_episode(s['task'],episode,mode='anti_collapse'),anti_collapse_reward=score_episode(s['task'],episode,'anti_collapse'),evidence_gated_reward=score_episode(s['task'],episode,'evidence_gated'),specified_reward=score_episode(s['task'],episode)))
        return outputs
    finally:
        for s in states:s['env'].close()
        model.config.use_cache=False
        model.train(was_training)
