"""Live bounded tool-use evaluation; gold labels never enter model messages."""
from __future__ import annotations
import argparse
import copy
from collections import Counter,defaultdict
import hashlib
import importlib.metadata
import json
from pathlib import Path
import time
from .mcp_env import MCPEnv
from .mcp_adapter import initial_messages,parse_turn,FormatError,wrap
from .reward import outcome_ok,citation_f1,normalize_val,score_episode
from .toolkits import portable_trajectory
from .dataset_builder import write_jsonl
MODEL='CohereLabs/tiny-aya-fire'
REVISION='73500c80fcb6c8bea3e830c21d5d2920249a0e1a'

def verify_manifest(data):
    entries={}
    for line in (data/'SHA256SUMS').read_text().splitlines():
        sha,name=line.split('  ',1)
        if Path(name).name!=name: raise ValueError('unsafe manifest path')
        if sha!=hashlib.sha256((data/name).read_bytes()).hexdigest(): raise ValueError('frozen dataset changed: '+name)
        entries[name]=sha
    return entries

class HFBackend:
    def __init__(self,quantization='4bit',max_new_tokens=384,gpu_memory_gib=0,sdpa_expand_kv=False,model_path=None,adapter_path=None):
        from dotenv import load_dotenv
        import os
        import torch
        from transformers import AutoTokenizer,AutoModelForCausalLM,BitsAndBytesConfig
        load_dotenv(Path.cwd().parent/'.env')
        token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN')
        if not torch.cuda.is_available(): raise RuntimeError('CUDA unavailable; host GPU access is required')
        torch.manual_seed(42);torch.set_num_threads(4)
        self.torch=torch
        if sdpa_expand_kv:
            # On Turing, native GQA cannot use the efficient SDPA kernel.
            # Repeating KV heads preserves grouped attention mathematically
            # while allowing the same-head-count memory-efficient kernel.
            import transformers.integrations.sdpa_attention as sdpa_module
            sdpa_module.use_gqa_in_sdpa=lambda attention_mask,key: False
        self.model_source=str(model_path) if model_path else MODEL
        self.loaded_revision=None if model_path else REVISION
        self.adapter_path=str(adapter_path) if adapter_path else None
        self.tokenizer=AutoTokenizer.from_pretrained(self.model_source,revision=self.loaded_revision,token=token,padding_side='left')
        if self.tokenizer.pad_token_id is None: self.tokenizer.pad_token=self.tokenizer.eos_token
        kwargs=dict(revision=self.loaded_revision,token=token,dtype=torch.float16,device_map={'':'cuda:0'},attn_implementation='sdpa')
        if gpu_memory_gib:
            kwargs.update(device_map='auto',max_memory={0:int(gpu_memory_gib*2**30),'cpu':'16GiB'},offload_buffers=True)
        if quantization=='4bit': kwargs['quantization_config']=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.float16)
        self.model=AutoModelForCausalLM.from_pretrained(self.model_source,**kwargs).eval()
        if adapter_path:
            from peft import PeftModel
            self.model=PeftModel.from_pretrained(self.model,str(adapter_path),is_trainable=False).eval()
        self.max_new_tokens=max_new_tokens
        self.generated_tokens=0;self.input_tokens=0;self.generate_seconds=0;self.generation_batches=0;self.oom_splits=0;self.prior_peaks={}
        torch.cuda.reset_peak_memory_stats()
    def generate_messages(self,batch):
        try:
            return self._generate_messages(batch)
        except self.torch.cuda.OutOfMemoryError:
            if len(batch)<=1: raise
            self.oom_splits+=1
        # Leave the except block before collecting, releasing its traceback and
        # GPU tensor references. No outputs from the failed call are scored.
        import gc
        gc.collect();self.torch.cuda.empty_cache()
        mid=len(batch)//2
        return self.generate_messages(batch[:mid])+self.generate_messages(batch[mid:])
    def _generate_messages(self,batch):
        prompts=[self.tokenizer.apply_chat_template(m,tokenize=False,add_generation_prompt=True) for m in batch]
        inputs=self.tokenizer(prompts,padding=True,return_tensors='pt',add_special_tokens=False,return_token_type_ids=False).to('cuda:0')
        if inputs['input_ids'].shape[1]+self.max_new_tokens>8192: raise ValueError('context budget exceeded')
        self.torch.cuda.synchronize();start=time.perf_counter()
        with self.torch.inference_mode():
            output=self.model.generate(**inputs,max_new_tokens=self.max_new_tokens,do_sample=False,pad_token_id=self.tokenizer.pad_token_id,stop_strings=['</tool_call>','</final_answer>'],tokenizer=self.tokenizer,use_cache=True)
        self.torch.cuda.synchronize();self.generate_seconds+=time.perf_counter()-start
        self.input_tokens+=int(inputs['attention_mask'].sum())
        ids=output[:,inputs['input_ids'].shape[1]:]
        self.generated_tokens+=int((ids!=self.tokenizer.pad_token_id).sum());self.generation_batches+=1
        return self.tokenizer.batch_decode(ids,skip_special_tokens=True)
    def stats(self):
        return dict(device_map={k:str(v) for k,v in getattr(self.model,'hf_device_map',{}).items()},model=self.model_source,revision=self.loaded_revision,adapter_path=self.adapter_path,gpu=self.torch.cuda.get_device_name(0),compute_dtype='float16',peak_vram_allocated_gib=max(self.prior_peaks.get("peak_vram_allocated_gib",0),self.torch.cuda.max_memory_allocated()/2**30),peak_vram_reserved_gib=max(self.prior_peaks.get("peak_vram_reserved_gib",0),self.torch.cuda.max_memory_reserved()/2**30),oom_splits=self.oom_splits,generated_tokens=self.generated_tokens,input_tokens=self.input_tokens,generation_seconds=self.generate_seconds,generated_tokens_per_second=self.generated_tokens/self.generate_seconds if self.generate_seconds else None,generation_batches=self.generation_batches)

def run_batch(tasks,world,backend,max_calls=6):
    states=[]
    for task in tasks:
        env=MCPEnv(world,task['active_mcps'])
        states.append(dict(task=task,env=env,messages=copy.deepcopy(task.get('prompt') or initial_messages(task,env)),raw_turns=[],done=False,prediction=None,final_text='',completion_reason=None,tool_format_error=False,started=time.perf_counter()))
    try:
        for turn in range(max_calls+1):
            live=[s for s in states if not s['done']]
            if not live: break
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
        successful_tool_calls=episode['num_tool_calls'] if correct else None,tool_calls=episode['num_tool_calls'],tool_errors=sum(isinstance(c['output'],dict) and 'error' in c['output'] for c in episode['calls']),format_valid=float(episode['prediction'] is not None),completion_reason=episode['completion_reason'],reward=score_episode(task,episode))

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
    for key in ('exact_outcome','stale_catch','verified_citation_f1','distractor_immunity','successful_tool_calls','format_valid','stale_value_returned'):
        metrics[key]=bootstrap_ratio(rows,lambda r,k=key:r[k] if r[k] is not None else 0.,lambda r,k=key:float(r[k] is not None))
    for name,den in [('abstention_precision','predicted_abstain'),('abstention_recall','expected_abstain'),('unplugged_recall','unplugged')]:
        target='unplugged' if name=='unplugged_recall' else 'expected_abstain'
        metrics[name]=bootstrap_ratio(rows,lambda r,k=target:float(r['predicted_abstain'] and r[k]),lambda r,k=den:float(r[k]))
    metrics['accuracy_by_language']={lang:bootstrap_ratio([r for r in rows if r['language']==lang],lambda r:r['exact_outcome'],lambda r:1.) for lang in sorted({r['language'] for r in rows})}
    return metrics

def auditkit_score(tasks,episodes,out):
    import auditkit as ak
    from auditkit.sample import Sample
    from auditkit.scorers import FunctionScorer
    from auditkit.types import Direction
    from auditkit.metrics.agent import ToolCallF1,ToolCallValidity,RedundantToolCalls
    from .oracle_solver import run_oracle
    from .mcp_env import SCHEMAS
    world=json.loads(Path('docs/archive/data_v1/world_'+tasks[0]['world_split']+'.json').read_text())
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

def checkpoint_label(metadata):
    if metadata.get('checkpoint_label'): return metadata['checkpoint_label']
    if metadata.get('adapter_path'): return 'GRPO' if 'grpo' in str(metadata['adapter_path']).lower() else 'SFT'
    return 'Base'

def render_report(out,results,metadata):
    def fmt(m,pct=True):
        if m['estimate'] is None: return 'N/A (zero denominator)'
        scale=100 if pct else 1
        return f'{m["estimate"]*scale:.2f} [{m["ci95"][0]*scale:.2f}, {m["ci95"][1]*scale:.2f}]'
    lines=['# Tiny Aya Fire: zero-shot baseline results','',f'Model: `{MODEL}` at `{REVISION}`. No fine-tuning or oracle actions were used in model episodes.','',f'Quantization: {metadata["quantization"]} (NF4 with double quantization for 4bit); compute: float16; GPU: {metadata.get("gpu","unknown")}. Greedy decoding, max 384 new tokens/turn, at most 6 tool calls/task. XML-wrapped JSON protocol; malformed output ends the episode without repair.','', 'Intervals: 95% percentile bootstrap, 10,000 resamples of semantic cases with translations kept together. Degenerate [0,0] or [100,100] intervals do not imply certainty outside this benchmark. All Hindi/Telugu queries are romanized.','', '| Metric | Synthetic holdout (400) | Constructed OSS-style holdout (100) |','|---|---:|---:|']
    labels=[('stale_catch','Stale-doc catch (%)',True),('exact_outcome','Exact outcome (%)',True),('verified_citation_f1','Verified citation F1, evidence tasks (%)',True),('abstention_precision','Abstention precision (%)',True),('abstention_recall','Abstention recall (%)',True),('unplugged_recall','Unplugged DB abstention recall (%)',True),('distractor_immunity','Distractor immunity, exposed tasks (%)',True),('successful_tool_calls','Tool calls per successful task',False),('format_valid','Valid final format (%)',True),('stale_value_returned','Stale value returned, conflict tasks (%)',True)]
    for key,label,pct in labels: lines.append('| '+label+' | '+' | '.join(fmt(results[w]['metrics'][key],pct) for w in ('test_synth','repo_style'))+' |')
    lines+=['','| Language | Synthetic exact outcome (%) | OSS-style exact outcome (%) |','|---|---:|---:|']
    for lang in ('en','hi','hinglish','te'): lines.append('| '+lang+' | '+' | '.join(fmt(results[w]['metrics']['accuracy_by_language'][lang]) for w in ('test_synth','repo_style'))+' |')
    lines+=['','## Work completed','', '- Deterministic train/test worlds, isolated SQLite rollouts, strict protocol parsing, read-only queries and optional FastMCP wrapper.', '- Evidence-consuming oracle, specified reward and separately named hardened variant, adversarial tests.', '- Four-language SFT and curriculum datasets, CuratorKIT exact deduplication, actual AgentTune trajectory JSONL round-trip into AuditKIT, SHA-256 freeze.', '- Live GPU base-model tool episodes, raw generations and tool outputs, AuditKIT custom scoring, resumable runs and cluster bootstrap metrics.','', '## Scope and limitations','',
        'The OSS-style cases are constructed fixtures. They contain no verified upstream PRs or real doc snapshots; these scores do not establish real-repository transfer. A source-backed OSS holdout remains future work.','',
        'Train/test services, employees, config values and question-template sets are disjoint. Odd/even config partitions enforce numeric separation within plausible overlapping ranges, rather than disjoint magnitude ranges. Synthetic evaluation has 100 semantic cases translated four ways; the OSS-style set has 30 cases. These are not 500 independent cases.','',
        'Original reward: always-abstain scores 0.1925, oracle 1.3550 on the 100-case adversarial suite. The requested thresholds cannot hold under that formula and task mix. The optional hardened variant reduces always-abstain to -0.0200. Correct unsupported guesses retain base reward under the original formula. Neither variant is claimed to be ungameable.','',
        'AgentTune is used for its installed trajectory classes and interoperable exports. Its eager agentic package initializer imports training/OpenEnv/RAG dependencies, so the dependency-free trajectory file is loaded directly by installed path. Full trainer dependencies are deferred; no claim of training readiness is made.','',
        'The MCP tools run in-process. The optional FastMCP wrapper is not a benchmark of separate network servers. No sub-millisecond parallel rollout claim is made. No adapters were trained or published, and no fine-tuning gains or ROI are claimed.','',
        'Romanized Hindi and Hinglish are distinct prompt groups but related registers. Template translations have not had independent native-speaker review. '+('NF4 quantization may affect quality; this is a quantized deployment baseline, not an unquantized reference result.' if metadata['quantization']=='4bit' else 'This run uses FP16 weights. Any CPU offload and actual layer placement are recorded in runtime metadata.'),'',
        'Stale catch requires correct status/value, the correct stale page and both required citations actually retrieved. Exact outcome checks status/value. Citation precision includes hallucinated IDs in its denominator. Headline citation F1 excludes citation-free abstention; the AuditKIT all-item diagnostic includes zeros for those tasks.','',
        '## Runtime','', '```json',json.dumps(metadata,indent=2),'```','', '## Completion reasons','', '```json',json.dumps({w:r['completion_reasons'] for w,r in results.items()},indent=2),'```','', 'Evidence: `docs/archive/data_v1/SHA256SUMS`, `reports/v1/reward_hacking.md`, raw episode JSONL, metric JSONL and AuditKIT output folders.']
    lines+=['','## Validation and reward audit','','Verification covers world isolation, oracle outcomes, reward loopholes, prompt immutability, memory recovery, paired cohort matching, and frozen world/data checksums. The original reward and optional hardened variant were audited over 100 semantic cases:','',Path('reports/v1/reward_hacking.md').read_text().strip(),'','The local search tools use conjunctive token matching over entity/parameter identifiers. Natural-language filler in a search query can therefore return an empty result. This is a constrained local benchmark, not a measurement against production Notion/Slack search. Missing-entity fixtures have recognizable synthetic names; human-reviewed, more natural prompts and a source-backed repository holdout are further benchmark improvements.','','A zero strict outcome score here does not mean the model has no useful language or factual capability. The raw-output diagnostics distinguish value/status matches from the required structured contract. These observations do not independently confirm the proposed narrative that the base model specifically trusts stale Notion documents; protocol and verification failures dominate this run.','','Toolkit commits are recorded in `toolkit_revisions.json`; setup and scope are in `README.md`; compatibility and GPU restart details are in `reports/v1/IMPLEMENTATION_NOTES.md`. Model and toolkit primary sources: [Tiny Aya Fire](https://huggingface.co/CohereLabs/tiny-aya-fire), [AgentTune](https://github.com/Lexsi-Labs/AgentTune), [AuditKIT](https://github.com/Lexsi-Labs/AuditKIT), [CuratorKIT](https://github.com/Lexsi-Labs/CuratorKIT).']
    if metadata.get('adapter_path'):
        label=checkpoint_label(metadata)
        lines[0]=f'# Tiny Aya Fire: {label} adapter evaluation'
        lines[2]=f'Base model: `{MODEL}` at `{REVISION}`. {label} adapter: `{metadata["adapter_path"]}`. Live model actions were used; no oracle actions were substituted.'
        lines=[line for line in lines if not line.startswith('AgentTune is used for its installed trajectory') and not line.startswith('The MCP tools run in-process.') and not line.startswith('A zero strict outcome score here')]
        lines+=['', 'Training and compatibility details are in `reports/v1/cloud_sft/SFT_REPORT.md` and `reports/v1/cloud_grpo/GRPO_EXPERIMENT.md`. The MCP tools run in-process. These results evaluate the named adapter over an NF4 base when quantization is 4bit. Other precision or merged-model deployments are different inference paths.', '', 'The constructed OSS fixtures include 17 questions from five cases with implausible percentage values above 100. They are retained for frozen-set comparability; see `reports/v1/precision_full/FINDINGS.md`.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n');
    if out.resolve()==Path('reports/v1/base_fire_nf4').resolve(): Path('docs/archive/RESULTS.md').write_text('\n'.join(lines)+'\n')


def select_tasks(tasks,per_language=0):
    """Outcome-independent, deterministic, balanced kind/language sample."""
    if not per_language: return tasks
    if per_language<1: raise ValueError('sample size must be positive')
    selected=[]
    for language in sorted({t['language'] for t in tasks}):
        pools={kind:sorted([t for t in tasks if t['language']==language and t['kind']==kind],key=lambda t:hashlib.sha256(t['case_id'].encode()).hexdigest()) for kind in sorted({t['kind'] for t in tasks})}
        if sum(map(len,pools.values()))<per_language: raise ValueError('sample exceeds available tasks per language')
        chosen=[]
        while len(chosen)<per_language:
            for pool in pools.values():
                if pool and len(chosen)<per_language: chosen.append(pool.pop(0))
        selected.extend(chosen)
    return sorted(selected,key=lambda t:t['task_id'])

def compare_baseline(out,baseline,results,config):
    """Compare complete identical frozen cohorts; retain each run's own CIs."""
    old=json.loads((baseline/'summary.json').read_text())
    old_config=json.loads((baseline/'run_config.json').read_text())
    if old_config['dataset_hashes']!=config['dataset_hashes']:
        raise ValueError('baseline dataset hashes differ; comparison refused')
    old_label=checkpoint_label(old_config);new_label=checkpoint_label(config)
    lines=[f'# {old_label} versus {new_label} evaluation', '', f'Baseline: `{baseline}`. Current run: `{out}`.', '', 'Positive deltas indicate higher scores. Deltas are descriptive percentage-point differences; intervals in RESULTS.md belong to individual runs, not the difference. Check run_config.json and runtime.json for precision, attention and batching differences. These can affect generated outputs.', '', f'| World | Metric | {old_label} (%) | {new_label} (%) | Change (pp) |', '|---|---|---:|---:|---:|']
    for world,result in results.items():
        if world not in old or old[world]['n']!=result['n']: raise ValueError('baseline cohort sizes differ')
        def ids(folder):
            return {json.loads(line)['task_id'] for line in (folder/(world+'_episodes.jsonl')).read_text().splitlines()}
        if ids(baseline)!=ids(out): raise ValueError('baseline task IDs differ')
        for key in ('exact_outcome','stale_catch','verified_citation_f1','format_valid','abstention_precision','abstention_recall','distractor_immunity'):
            a=old[world]['metrics'][key]['estimate'];b=result['metrics'][key]['estimate']
            fmt=lambda x:'N/A' if x is None else f'{100*x:.2f}'
            delta='N/A' if a is None or b is None else f'{100*(b-a):+.2f}'
            lines.append(f'| {world} | {key} | {fmt(a)} | {fmt(b)} | {delta} |')
        for lang,m in result['metrics']['accuracy_by_language'].items():
            a=old[world]['metrics']['accuracy_by_language'][lang]['estimate'];b=m['estimate']
            lines.append(f'| {world} | exact_outcome ({lang}) | {100*a:.2f} | {100*b:.2f} | {100*(b-a):+.2f} |')
    lines+=['', 'Constructed OSS-style fixtures are not source-backed real repositories and include documented domain-validity defects. Synthetic translations are correlated within semantic cases.']
    (out/'COMPARISON.md').write_text('\n'.join(lines)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default='reports/v1/base_fire_nf4');p.add_argument('--batch-size',type=int,default=4);p.add_argument('--quantization',choices=('4bit','fp16'),default='4bit');p.add_argument('--limit',type=int,default=0);p.add_argument('--rescore',action='store_true');p.add_argument('--adapter-path');p.add_argument('--checkpoint-label',choices=('SFT','GRPO'));p.add_argument('--baseline',help='Completed baseline output directory for a comparison report');p.add_argument('--sample-per-language',type=int,default=0);p.add_argument('--worlds',nargs='+',choices=('test_synth','repo_style'),default=['test_synth','repo_style']);p.add_argument('--gpu-memory-gib',type=float,default=0);p.add_argument('--sdpa-expand-kv',action='store_true');args=p.parse_args()
    if args.limit<0 or args.sample_per_language<0 or args.batch_size<1 or args.gpu_memory_gib<0: p.error('invalid negative/zero size or memory setting')
    if args.adapter_path and not Path(args.adapter_path).is_dir(): p.error('adapter directory does not exist')
    if args.limit and args.sample_per_language: p.error('use either limit or a stratified sample')
    data=Path('docs/archive/data_v1');hashes=verify_manifest(data);out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    datasets=[('test_synth','holdout_synth_400_frozen.jsonl'),('repo_style','holdout_repo_style_100_frozen.jsonl')]
    datasets=[d for d in datasets if d[0] in args.worlds]
    config=dict(model=MODEL,revision=REVISION,quantization=args.quantization,max_new_tokens=384,max_tool_calls=6,batch_size=args.batch_size,seed=42,temperature=0.,dataset_hashes=hashes,limit=args.limit)
    if args.checkpoint_label: config['checkpoint_label']=args.checkpoint_label
    if args.adapter_path:
        adapter=Path(args.adapter_path).resolve()
        config['adapter_path']=str(adapter)
        config['adapter_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(adapter.iterdir()) if f.name=='adapter_config.json' or f.name.startswith('adapter_model.')}
        if 'adapter_config.json' not in config['adapter_sha256'] or len(config['adapter_sha256'])<2: raise ValueError('adapter config or weights missing')
    if args.sample_per_language: config['sample_per_language']=args.sample_per_language
    if args.worlds!=['test_synth','repo_style']: config['worlds']=args.worlds
    if args.gpu_memory_gib: config['gpu_memory_gib']=args.gpu_memory_gib
    if args.sdpa_expand_kv: config['sdpa_expand_kv']=True
    if (out/'run_config.json').exists() and json.loads((out/'run_config.json').read_text())!=config: raise ValueError('existing run config differs; choose a new output directory')
    (out/'run_config.json').write_text(json.dumps(config,indent=2));backend=None;results={};start=time.perf_counter()
    try:
        for wkey,filename in datasets:
            tasks=[json.loads(l) for l in (data/filename).read_text().splitlines()]
            tasks=select_tasks(tasks,args.sample_per_language)
            if args.limit: tasks=tasks[:args.limit]
            world=json.loads((data/('world_'+wkey+'.json')).read_text());path=out/(wkey+'_episodes.jsonl')
            saved=[json.loads(l) for l in path.read_text().splitlines()] if path.exists() else [];by_id={e['task_id']:e for e in saved}
            if len(by_id)!=len(saved): raise ValueError('duplicate saved episode IDs')
            todo=[t for t in tasks if t['task_id'] not in by_id]
            if args.rescore and todo: raise ValueError('cannot rescore incomplete episodes')
            if todo and backend is None:
                backend=HFBackend(args.quantization,gpu_memory_gib=args.gpu_memory_gib,sdpa_expand_kv=args.sdpa_expand_kv,adapter_path=args.adapter_path)
                if (out/'runtime_live.json').exists():
                    prior=json.loads((out/'runtime_live.json').read_text())
                    for field in ('generated_tokens','input_tokens','generation_batches','oom_splits'):
                        setattr(backend,field,prior.get(field,0))
                    backend.generate_seconds=prior.get('generation_seconds',0)
                    backend.prior_peaks=prior
            for offset in range(0,len(todo),args.batch_size):
                batch=todo[offset:offset+args.batch_size];episodes=run_batch(batch,world,backend)
                with path.open('a') as f:
                    for e in episodes: f.write(json.dumps(e,ensure_ascii=False)+'\n');f.flush();by_id[e['task_id']]=e
                print(json.dumps({'world':wkey,'completed':len(by_id),'total':len(tasks),'batch_accuracy':sum(outcome_ok(e['prediction'],t) for t,e in zip(batch,episodes))/len(batch),'tokens_per_second':backend.stats()['generated_tokens_per_second']}),flush=True)
                (out/'runtime_live.json').write_text(json.dumps(backend.stats(),indent=2))
            episodes=[by_id[t['task_id']] for t in tasks];rows=[measure(t,e) for t,e in zip(tasks,episodes)]
            write_jsonl(out/(wkey+'_metrics.jsonl'),rows);write_jsonl(out/(wkey+'_agenttune_trajectories.jsonl'),[portable_trajectory(t,e) for t,e in zip(tasks,episodes)])
            from auditkit.agent_eval.importers import episodes_from_agenttune
            assert len(episodes_from_agenttune(str(out/(wkey+'_agenttune_trajectories.jsonl'))))==len(tasks)
            headline=auditkit_score(tasks,episodes,out/(wkey+'_auditkit'))
            results[wkey]=dict(n=len(tasks),metrics=summary_metrics(rows),auditkit_headline=headline,completion_reasons=dict(Counter(r['completion_reason'] for r in rows)))
            (out/'summary.json').write_text(json.dumps(results,indent=2))
        metadata=dict(config)
        if backend: metadata.update(backend.stats())
        elif (out/'runtime_live.json').exists(): metadata.update(json.loads((out/'runtime_live.json').read_text()))
        metadata['scoring_session_elapsed_seconds']=time.perf_counter()-start;metadata['versions']={x:importlib.metadata.version(x) for x in ('torch','transformers','bitsandbytes','agenttune','auditkit','curatorkit')}
        (out/'runtime.json').write_text(json.dumps(metadata,indent=2))
        if (out/'failure.json').exists(): (out/'failure.json').rename(out/'resolved_failure.json')
        if not args.limit and not args.sample_per_language and len(results)==2: render_report(out,results,metadata)
        if args.baseline: compare_baseline(out,Path(args.baseline),results,config)
        print(json.dumps(results,indent=2))
    except Exception as e:
        (out/'failure.json').write_text(json.dumps({'type':type(e).__name__,'error':str(e),'elapsed_seconds':time.perf_counter()-start},indent=2));raise
if __name__=='__main__': main()
