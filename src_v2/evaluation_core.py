from __future__ import annotations
import copy,json,time
from collections import defaultdict
from .mcp_env import MCPEnv
from .mcp_adapter import initial_messages,parse_turn,FormatError
from .reward import outcome_ok,citation_f1,normalize_val,score_episode,required_chain_ok

def run_batch(tasks,world,backend,max_calls=6):
    states=[]
    for task in tasks:
        env=MCPEnv(world,task['active_mcps'])
        states.append(dict(task=task,env=env,messages=copy.deepcopy(task.get('prompt') or initial_messages(task,env)),raw_turns=[],done=False,prediction=None,final_text='',completion_reason=None,tool_format_error=False,started=time.perf_counter()))
    try:
        for turn in range(max_calls+1):
            live=[s for s in states if not s['done']]
            if not live: break
            for state in live:
                if hasattr(backend,'context_fits') and not backend.context_fits(state['messages']):state.update(done=True,completion_reason='context_budget_exhausted')
            live=[state for state in live if not state['done']]
            if not live:break
            raw=backend.generate_messages([s['messages'] for s in live])
            if len(raw)!=len(live): raise ValueError('backend returned wrong batch size')
            for s,text in zip(live,raw):
                s['raw_turns'].append(text);s['messages'].append({'role':'assistant','content':text})
                try: tag,obj=parse_turn(text)
                except FormatError as e:
                    s.update(done=True,completion_reason='malformed_output',parse_error=str(e),final_text=text,tool_format_error='<tool_call>' in text)
                    continue
                if tag=='final_answer': s.update(done=True,prediction=obj,final_text=text,completion_reason='final_answer');continue
                if len(s['env'].calls)>=max_calls: s.update(done=True,completion_reason='tool_budget_exhausted');continue
                result=s['env'].call(**obj)
                s['messages'].append({'role':'user','content':'Tool result: '+json.dumps(result,ensure_ascii=False)})
        return [dict(task_id=s['task']['task_id'],prediction=s['prediction'],final_text=s['final_text'],raw_turns=s['raw_turns'],messages=s['messages'],calls=list(s['env'].calls),num_tool_calls=len(s['env'].calls),retrieved_ids=sorted(s['env'].retrieved_ids),tool_format_error=s['tool_format_error'],completion_reason=s['completion_reason'] or 'tool_budget_exhausted',elapsed_seconds=time.perf_counter()-s['started']) for s in states]
    finally:
        for s in states: s['env'].close()

def measure(task,episode):
    pred=episode.get('prediction') or {};correct=outcome_ok(pred,task)
    claims=set(pred.get('cites',[]));retrieved=set(episode['retrieved_ids'])
    catch=correct and pred.get('stale_source')==task['stale_doc_id'] and set(task['gold_cites'])<=claims&retrieved
    return dict(task_id=task['task_id'],case_id=task['case_id'],language=task['language'],kind=task['kind'],exact_outcome=float(correct),stale_catch=float(catch) if task['kind']=='conflict' else None,
        stale_value_returned=float(task['stale_trap_value'] is not None and normalize_val(pred.get('value'))==normalize_val(task['stale_trap_value'])) if task['kind']=='conflict' else None,
        verified_citation_f1=citation_f1(pred,task,retrieved) if task['gold_cites'] else None,predicted_abstain=pred.get('status')=='abstain',expected_abstain=task['expected_status']=='abstain',
        unplugged=task['kind']=='abstain' and 'db-mcp' not in task['active_mcps'],distractor_immunity=float(not any(c['server'] in task['distractor_mcps'] for c in episode['calls'])) if task['distractor_mcps'] else None,
        successful_tool_calls=episode['num_tool_calls'] if correct else None,tool_calls=episode['num_tool_calls'],tool_errors=sum(isinstance(c['output'],dict) and 'error' in c['output'] for c in episode['calls']),format_valid=float(episode['prediction'] is not None),completion_reason=episode['completion_reason'],reward=score_episode(task,episode,'evidence_gated'),required_chain_compliance=float(required_chain_ok(task,episode)) if task['expected_status']!='abstain' else None)

def bootstrap_ratio(rows,num,den,resamples=10000,seed=2026):
    """Bootstrap semantic cases, keeping correlated translations together."""
    import numpy as np
    groups=defaultdict(lambda:[0.,0.])
    for r in rows: groups[r['case_id']][0]+=num(r);groups[r['case_id']][1]+=den(r)
    a=np.array(list(groups.values()),dtype=float);total=a[:,1].sum()
    if not total: return {'estimate':None,'ci95':[None,None],'denominator':0,'clusters':len(groups)}
    rng=np.random.default_rng(seed);weights=rng.multinomial(len(a),np.full(len(a),1/len(a)),size=resamples)
    numer=weights@a[:,0];denom=weights@a[:,1]
    ratio=np.divide(numer,denom,out=np.full(resamples,np.nan),where=denom>0)
    lo,hi=np.nanpercentile(ratio,[2.5,97.5])
    return {'estimate':float(a[:,0].sum()/total),'ci95':[float(lo),float(hi)],'denominator':float(total),'clusters':len(groups)}

def summary_metrics(rows):
    metrics={}
    for key in ('exact_outcome','stale_catch','verified_citation_f1','distractor_immunity','successful_tool_calls','format_valid','stale_value_returned','required_chain_compliance'):
        metrics[key]=bootstrap_ratio(rows,lambda r,k=key:r[k] if r[k] is not None else 0.,lambda r,k=key:float(r[k] is not None))
    for name,den in [('abstention_precision','predicted_abstain'),('abstention_recall','expected_abstain'),('unplugged_recall','unplugged')]:
        target='unplugged' if name=='unplugged_recall' else 'expected_abstain'
        metrics[name]=bootstrap_ratio(rows,lambda r,k=target:float(r['predicted_abstain'] and r[k]),lambda r,k=den:float(r[k]))
    metrics['accuracy_by_language']={lang:bootstrap_ratio([r for r in rows if r['language']==lang],lambda r:r['exact_outcome'],lambda r:1.) for lang in sorted({r['language'] for r in rows})}
    return metrics


def auditkit_score(tasks,episodes,out,world):
    import auditkit as ak
    from auditkit.sample import Sample
    from auditkit.scorers import FunctionScorer
    from auditkit.types import Direction
    from auditkit.metrics.agent import ToolCallF1,ToolCallValidity,RedundantToolCalls
    from .oracle_solver import run_oracle
    from .mcp_env import SCHEMAS
    samples=[]
    for t,e in zip(tasks,episodes):
        with MCPEnv(world,t['active_mcps']) as env: oracle=run_oracle(t,env)
        qualified=lambda c:{'name':c['server']+'__'+c['tool'],'arguments':c['arguments']}
        tools=[{'type':'function','function':{'name':server+'__'+tool,'parameters':{'type':'object','properties':{k:{'type':typ} for k,typ in arguments.items()},'required':list(arguments),'additionalProperties':False}}} for server in t['active_mcps'] for tool,arguments in SCHEMAS[server].items()]
        samples.append(Sample(input=t['question'],id=t['task_id'],target=str(t['gold_value']),actual_output=e['final_text'],metadata={'spec':t,'episode':e},tools=tools,expected_tool_calls=[[qualified(c)] for c in oracle['calls']],actual_trace={'messages':e['messages'],'tool_calls':[[qualified(c)] for c in e['calls']]}))
    def exact(s,output):
        try: tag,pred=parse_turn(output)
        except FormatError: return 0.
        return float(tag=='final_answer' and outcome_ok(pred,s.metadata['spec']))
    def cites(s,output): return measure(s.metadata['spec'],s.metadata['episode'])['verified_citation_f1'] or 0.
    result=ak.evaluate(dataset=samples,model='precomputed',scorers=[FunctionScorer(exact,Direction.MAXIMIZE,name='driftguard_exact_outcome'),FunctionScorer(cites,Direction.MAXIMIZE,name='driftguard_evidence_f1_all_items'),ToolCallF1(arg_mode='name'),ToolCallValidity(),RedundantToolCalls()],cache=False)
    result.save(str(out)+'.json')
    if result.errors or result.failed_count: raise RuntimeError('AuditKIT scoring errors: '+str(result.errors))
    return result.headline

