"""Replay saved strings through pinned tokenizers; no API inference or billing."""
import argparse
from collections import Counter
import hashlib
import json
from decimal import Decimal
from importlib.metadata import version
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BASE = 'CohereLabs/tiny-aya-fire'
REVISION = '73500c80fcb6c8bea3e830c21d5d2920249a0e1a'
EVAL = ROOT / 'reports/v2_2/grpo_evaluation'
OUT = ROOT / 'reports/submission'


def common_prefix(a, b):
    return next((i for i, (x, y) in enumerate(zip(a,b)) if x != y), min(len(a),len(b)))


def split_tokens(current, previous, quantum=1, minimum=0):
    repeated = common_prefix(current, previous) if previous else 0
    eligible = repeated // quantum * quantum if repeated >= minimum else 0
    return dict(input_tokens=len(current), repeated_prefix_tokens=repeated,
                new_input_tokens=len(current)-repeated, eligible_cached_tokens=eligible,
                billed_uncached_tokens=len(current)-eligible)


def billing(total, provider):
    """Ideal episode-local hits, never assume cross-episode reuse or free writes."""
    n=total['episodes']; inp=total['input_tokens']; out=total['output_tokens']
    if provider=='gpt4o':
        cached=total['eligible_cached_tokens']; write=0
        uncached_usd=(Decimal(inp)*Decimal('2.50')+out*10)/Decimal(1000000)
        cached_usd=(Decimal(inp-cached)*Decimal('2.50')+Decimal(cached)*Decimal('1.25')+out*10)/Decimal(1000000)
    else:
        cached=total['claude_cache_read_tokens']; write=total['claude_cache_write_tokens']
        uncached_usd=Decimal(inp*3+out*15)/Decimal(1000000)
        cached_usd=(Decimal((inp-cached-write)*3)+Decimal(cached)*Decimal('.30')+Decimal(write)*Decimal('3.75')+out*15)/Decimal(1000000)
    return dict(uncached_usd_per_1000=float(uncached_usd/n*1000),
                uncached_usd_per_100000=float(uncached_usd/n*100000),
                cached_usd_per_1000=float(cached_usd/n*1000),
                cached_usd_per_100000=float(cached_usd/n*100000),
                cache_read_tokens=cached,cache_write_tokens=write)


def audit_episodes(episodes, tokenizer, encoding):
    details=[]
    for e in episodes:
        previous={'cohere':[], 'o200k_base':[]};turns=[]
        indices=[i for i,m in enumerate(e['messages']) if m['role']=='assistant']
        assert len(indices)==len(e['raw_turns']),e['task_id']
        for turn,i in enumerate(indices):
            raw=e['messages'][i]['content'];assert raw==e['raw_turns'][turn]
            rendered=tokenizer.apply_chat_template(e['messages'][:i],tokenize=False,add_generation_prompt=True)
            record=dict(turn=turn+1,prompt_sha256=hashlib.sha256(rendered.encode()).hexdigest(),
                        output_sha256=hashlib.sha256(raw.encode()).hexdigest())
            for name,encode in [('cohere',lambda s:tokenizer.encode(s,add_special_tokens=False)),
                                ('o200k_base',lambda s:encoding.encode(s,disallowed_special=()))]:
                tokens=encode(rendered)
                stats=split_tokens(tokens,previous[name],128 if name=='o200k_base' else 1,1024 if name=='o200k_base' else 0)
                stats['output_tokens']=len(encode(raw))
                # Claude scenario: cache full previous INPUT at a message boundary; no OpenAI 128-token rounding.
                stats['claude_cache_read_tokens']=stats['repeated_prefix_tokens'] if stats['repeated_prefix_tokens']>=1024 else 0
                if turn+1<len(indices) and len(tokens)>=1024:
                    # Write only the newly extended cache, or the entire initial prefix.
                    stats['claude_cache_write_tokens']=len(tokens)-stats['claude_cache_read_tokens']
                else:stats['claude_cache_write_tokens']=0
                previous[name]=tokens;record[name]=stats
            turns.append(record)
        details.append(dict(task_id=e['task_id'],turns=turns))
    totals={}
    for name in ['cohere','o200k_base']:
        values=Counter()
        for e in details:
            for turn in e['turns']:values.update(turn[name])
        values.update(episodes=len(details),assistant_turns=sum(len(e['turns']) for e in details))
        totals[name]=dict(values)
        totals[name]['per_episode']={k:v/len(details) for k,v in values.items() if k not in ('episodes',)}
    return totals,details


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--local-files-only',action='store_true');a=p.parse_args(argv)
    from transformers import AutoTokenizer
    import tiktoken
    from src.v2_2.manage import protected
    assert protected()==19
    tokenizer=AutoTokenizer.from_pretrained(BASE,revision=REVISION,local_files_only=a.local_files_only)
    encoding=tiktoken.get_encoding('o200k_base')
    episodes={split:[json.loads(s) for s in (EVAL/(split+'_episodes.jsonl')).read_text().splitlines()]
              for split in ['test_synth','repo_style','validation']}
    holdouts=episodes['test_synth']+episodes['repo_style'];assert len(holdouts)==500
    totals,details=audit_episodes(holdouts,tokenizer,encoding)
    validation_totals,_=audit_episodes(episodes['validation'],tokenizer,encoding)
    runtime=json.loads((EVAL/'runtime.json').read_text());all_count=sum(map(len,episodes.values()));assert all_count==580
    all_input=totals['cohere']['input_tokens']+validation_totals['cohere']['input_tokens']
    hours=runtime['wall_seconds']/all_count*1000/3600
    l40s=dict(sample_volume=580,holdout_sample_volume=500,batch_size=16,gpu=runtime['gpu'],dtype=runtime['dtype'],
        usd_per_gpu_hour=1.8,wall_seconds=runtime['wall_seconds'],generation_seconds=runtime['generation_seconds'],
        runtime_generated_tokens=runtime['generated_tokens'],replayed_input_tokens=all_input,
        generation_output_tokens_per_second=runtime['generated_tokens']/runtime['generation_seconds'],
        generation_total_tokens_per_second=(all_input+runtime['generated_tokens'])/runtime['generation_seconds'],
        wall_output_tokens_per_second=runtime['generated_tokens']/runtime['wall_seconds'],
        wall_total_tokens_per_second=(all_input+runtime['generated_tokens'])/runtime['wall_seconds'],
        audits_per_hour=all_count/runtime['wall_seconds']*3600,gpu_hours_per_1000=hours,gpu_hours_per_100000=hours*100,
        usd_per_1000=hours*1.8,usd_per_100000=hours*180,peak_reserved_gib=runtime['peak_reserved_gib'])
    result=dict(schema_version=1,model=BASE,revision=REVISION,selected_update=40,
        tokenizer_metadata=dict(transformers=version('transformers'),tiktoken=version('tiktoken'),
            encoding='o200k_base',tokenizer_class=type(tokenizer).__name__,
            chat_template_sha256=hashlib.sha256(tokenizer.get_chat_template().encode()).hexdigest()),
        scope='500 saved final-model holdouts; no frontier API requests or measured API quality.',
        tokenizer_basis='Cohere native chat-template strings, encoded identically by Cohere and o200k_base. o200k is exact for these strings, not provider wire framing; Claude uses a disclosed token proxy, NOT a native tokenizer.',
        output_basis='Visible decoded assistant strings, excluding stripped EOS/pad tokens; runtime-generated token count is reported separately.',
        prefix_policy='Longest common token prefix of consecutive per-episode inputs; new input includes prior assistant/tool observation. GPT-4o historical 1024 minimum /128 quantum, ideal in-TTL cache hits, no cross-episode reuse. Cache eligibility is not an observed cache hit.',
        claude_policy='Historical 5-minute cache: read $0.30/M, write $3.75/M, ordinary $3/M, output $15/M. Explicit input-prefix breakpoints each turn except final, minimum1024; full-initial plus incremental writes billed. Token/framing eligibility is a scenario only.',
        token_counts=totals,
        billing={name:{provider:billing(counts,provider) for provider in ['gpt4o','claude35']} for name,counts in totals.items()},
        l40s=l40s,
        sources={'openai':'https://openai.com/index/api-prompt-caching/',
                 'claude':'https://platform.claude.com/docs/en/build-with-claude/prompt-caching',
                 'hf_jobs':'https://huggingface.co/docs/hub/en/jobs-pricing'},
        artifact_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [EVAL/'runtime.json']+[EVAL/(s+'_episodes.jsonl') for s in episodes]},
        protected_files=protected())
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/'ROI_TOKEN_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'ROI_TOKEN_TURNS.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in details))
    from roi_analysis import compile_report
    compile_report()
    print(json.dumps({'counts':{k:v['per_episode'] for k,v in totals.items()},'billing':result['billing'],'l40s':l40s},indent=2))


if __name__=='__main__':main()
