"""Shared Rule 5 tables from trace audit and measured deployment timing."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/submission'


def compile_report():
    audit=json.loads((OUT/'ROI_TOKEN_AUDIT.json').read_text())
    path=OUT/'ROI_LOCAL_NF4_BENCHMARK.json'
    local=json.loads(path.read_text()) if path.exists() else {'status':'pending_local_benchmark'}
    legacy=json.loads((OUT/'ROI_SCENARIOS.json').read_text())
    l40=audit['l40s'];counts=audit['token_counts']['cohere']['per_episode']
    if local.get('status')=='measured':
        h=local['gpu_hours_per_1000'];speed=local['output_tokens_per_second'];total=local['total_tokens_per_second'];vram=local['peak_reserved_gib']
        local_basis='Measured final v2.1 adapter, 20 episodes, batch 1'
        sample=20
    else:
        old=json.loads((ROOT/'reports/v1/sft_fire_nf4/runtime.json').read_text())
        speed=old['generated_tokens_per_second'];total=(old['input_tokens']+old['generated_tokens'])/old['generation_seconds'];vram=old['peak_vram_reserved_gib']
        h=(counts['input_tokens']+counts['output_tokens'])/total*1000/3600
        local_basis='UNMEASURED final adapter; v1 NF4 token-volume-adjusted proxy'
        sample='500 v1 episodes (proxy)'
    # T4 has not been benchmarked. Match token volume to the final-model holdouts.
    t4h=(counts['input_tokens']+counts['output_tokens'])/total*1000/3600
    api=audit['billing']['o200k_base']['gpt4o']
    scenarios=[
        dict(key='edge',name='Local workstation · RTX 2070 NF4',sample_volume=sample,
             basis=local_basis,pricing='$0 API; 175 W × $0.10/kWh',gpu_usd_per_hour=None,
             output_tps=speed,total_tps=total,vram_gib=vram,hours_1000=h,hours_100000=h*100,
             cost_1000=h*.175*.10,cost_100000=h*100*.175*.10),
        dict(key='l40s',name='Self-hosted L40S · BF16',sample_volume=580,
             basis='Recorded final adapter, batch 16, end-to-end runtime',pricing='$1.80/GPU-hour',gpu_usd_per_hour=1.8,
             output_tps=l40['generation_output_tokens_per_second'],total_tps=l40['generation_total_tokens_per_second'],
             wall_output_tps=l40['wall_output_tokens_per_second'],wall_total_tps=l40['wall_total_tokens_per_second'],
             hours_1000=l40['gpu_hours_per_1000'],hours_100000=l40['gpu_hours_per_100000'],
             cost_1000=l40['usd_per_1000'],cost_100000=l40['usd_per_100000']),
        dict(key='t4',name='Cloud T4-small · NF4 scenario',sample_volume='500 saved; timing proxy',
             basis='Unmeasured T4; final holdout logical-token volume / edge total tok/s',pricing='$0.40/GPU-hour',gpu_usd_per_hour=.4,
             output_tps=counts['output_tokens']/(t4h*3.6),total_tps=total,
             hours_1000=t4h,hours_100000=t4h*100,cost_1000=t4h*.4,cost_100000=t4h*40),
        dict(key='gpt4o_cached',name='GPT-4o · eligible prefix caching',sample_volume='500 saved; offline pricing',
             basis='o200k_base same-string scenario; ideal eligible hits, not an API invoice',
             pricing='$2.50/M new in · $1.25/M cache · $10/M out',gpu_usd_per_hour=None,
             output_tps=None,total_tps=None,hours_1000=None,hours_100000=None,
             cost_1000=api['cached_usd_per_1000'],cost_100000=api['cached_usd_per_100000']),
        dict(key='gpt4o',name='GPT-4o · uncached baseline',sample_volume='500 saved; offline pricing',
             basis='o200k_base exact same-string tokenization, not provider wire framing',
             pricing='$2.50/M input · $10/M output',gpu_usd_per_hour=None,
             output_tps=None,total_tps=None,hours_1000=None,hours_100000=None,
             cost_1000=api['uncached_usd_per_1000'],cost_100000=api['uncached_usd_per_100000'])]
    if local.get('episodes'):
        local['sample_case_count']=len({e['metrics']['case_id'] for e in local['episodes']})
        local['sample_exact_outcome']=sum(e['metrics']['exact_outcome'] for e in local['episodes'])/len(local['episodes'])
        local['sample_task_kind_counts']={k:sum(e['kind']==k for e in local['episodes']) for k in ['conflict','consistent','incident','abstain']}
        saved={}
        for split in ['test_synth','repo_style']:
            for row in map(json.loads,(ROOT/'reports/v2_2/grpo_evaluation'/(split+'_metrics.jsonl')).read_text().splitlines()):saved[row['task_id']]=row
        local['matched_saved_bf16_exact_outcome']=sum(saved[e['task_id']]['exact_outcome'] for e in local['episodes'])/len(local['episodes'])
        local['nf4_bf16_outcome_disagreement_task_ids']=[e['task_id'] for e in local['episodes'] if e['metrics']['exact_outcome']!=saved[e['task_id']]['exact_outcome']]
    result=dict(schema_version=1,monthly_audits=100000,unit_audits=1000,scenarios=scenarios,
        token_audit=audit,local_benchmark={k:v for k,v in local.items() if k!='episodes'},
        t4_measured=False,paid_job_launched=False,
        caveats=['No frontier accuracy/latency or actual API cache usage measured.',
                 'Local 20-task sample is balanced by kind/language and is not a full frozen-holdout NF4 accuracy evaluation.',
                 '3.15 GiB belongs to v1; final v2 NF4 memory is separately measured.',
                 'Input throughput counts logical unpadded tokens; output timing and full-wall timing differ.',
                 '175 W is nameplate power, not a metered energy reading. Electricity excludes CPU, cooling, idle and hardware.',
                 'T4 is token-adjusted edge-speed proxy, not a hardware benchmark.'],
        historical_cohere_uncached_usd_100000=legacy['gpt4o_historical_usd_per_1000']*100)
    (OUT/'ROI_VERIFIED_BENCHMARK.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def scenarios():
    path=OUT/'ROI_VERIFIED_BENCHMARK.json'
    if not path.exists():return compile_report()['scenarios']
    return json.loads(path.read_text())['scenarios']


def narrative(prefix='',article=False):
    from clean_report_data import table
    r=json.loads((OUT/'ROI_VERIFIED_BENCHMARK.json').read_text());a=r['token_audit'];l=a['l40s']
    rows=[]
    for s in r['scenarios']:
        if s['output_tps'] is None:
            throughput='Provider-managed; **not measured**; 3.24 turns/audit'
            hours='N/A · external API'
        else:
            throughput=f"{s['output_tps']:.2f} out / {s['total_tps']:,.1f} total tok/s"
            if s['key']=='l40s':throughput+=' (generation); 61.99 / 1,937.4 wall; 1,471 audits/hr'
            if s['key']=='t4':throughput+=' (**proxy**)'
            hours=f"{s['hours_1000']:.3f} / {s['hours_100000']:.2f} hrs"
        pricing=s['pricing']
        if s['key']=='edge':pricing+=f"; {s['vram_gib']:.2f} GiB reserved; {s['basis']}"
        rows.append([s['name'],s['sample_volume'],pricing,throughput,hours,
                     f"**${s['cost_1000']:,.2f}**",f"**${s['cost_100000']:,.2f}**"])
    result=table(['Serving option','Sample volume','Pricing basis (GPU/hr or token rate)',
                  'Tokens/sec throughput','GPU runtime hours (1k /100k audits)',
                  'Cost /1k audits','Cost /100k audits'],rows)
    result+='\n**Volume rationale:** 100,000 audits/month is about 3,333/day—for example, roughly 200 service owners or scheduled agents running 17 configuration/incident checks per day. This is a deployment load scenario, not observed enterprise traffic or 100,000 independent incidents.\n'
    c=a['token_counts']['cohere']['per_episode'];o=a['token_counts']['o200k_base']['per_episode']
    result+=f"\n**Workload:** 100,000 company audits/month, with 1,000-audit unit costs. Exact replay of **500 saved holdouts / 1,620 assistant turns** gives **{c['input_tokens']:,.3f} Cohere input / {c['output_tokens']:,.3f} visible output tokens per audit**; the identical strings encode as **{o['input_tokens']:,.3f} input / {o['output_tokens']:,.3f} output in `o200k_base`**. Of the OpenAI-encoded input, **{o['new_input_tokens']:,.3f}** tokens/audit are newly introduced and **{o['repeated_prefix_tokens']:,.3f}** repeat an earlier input prefix; **{o['eligible_cached_tokens']:,.3f}** qualify under the historical ≥1,024-token / 128-token-block rule.\n"
    result+=f"\n**Timing basis:** the L40S log covers **580 episodes** (500 holdouts + 80 validation), **{l['wall_seconds']:,.3f} seconds full wall / {l['generation_seconds']:,.3f} seconds generation**, and **{l['runtime_generated_tokens']:,} generated tokens**. Its **67.53 output / 2,110.62 logical total tok/s** generation rate differs from **61.99 output / 1,937.42 total tok/s** end-to-end; runtime costs use the full wall clock. Replaying all 580 inputs yields **{l['replayed_input_tokens']:,}** logical input tokens. Startup, idle capacity, API quality equivalence and operations are outside the serving projection.\n"
    local=r['local_benchmark']
    if local.get('status')=='measured':
        result+=f"\n**Live final-adapter NF4 check:** RTX 2070, FP16 compute, greedy batch 1, six-call limit, 192 generated tokens/turn, 4,096 context tokens; **16 synthetic + 4 repo-style tasks**, balanced five per kind, cover **{local['sample_case_count']} distinct semantic cases**. After one excluded warmup episode, the 20 episodes used **{local['wall_seconds']:.3f} wall seconds**, **{local['generation_seconds']:.3f} generation seconds**, **{local['input_tokens']:,} input / {local['generated_tokens']:,} generated tokens**, and **{local['peak_reserved_gib']:.3f} GiB peak reserved VRAM**. Sample exact-outcome accuracy is **{local['sample_exact_outcome']*100:.1f}%**, versus **{local['matched_saved_bf16_exact_outcome']*100:.1f}%** for the same 20 saved BF16 episodes; this is not a 500-task NF4 quality estimate. The table projects the measured sample runtime; T4 instead adjusts final holdout logical-token volume to edge speed and remains a proxy.\n"
    claude=a['billing']['o200k_base']['claude35']
    result+=f"\n**Caching and billing:** GPT-4o costs use `o200k_base` counts of the saved strings and historical token prices; cached costs assume eligible in-TTL hits, not observed usage. Provider message framing differs from the Cohere template, so these are offline estimates, not API invoices. Historical Claude 3.5 at $3/M ordinary input, $0.30/M cache reads, $3.75/M 5-minute writes and $15/M output gives **${claude['uncached_usd_per_1000']:.2f} uncached / ${claude['cached_usd_per_1000']:.2f} cached per 1k**, or **${claude['uncached_usd_per_100000']:,.2f} / ${claude['cached_usd_per_100000']:,.2f} per 100k**, using an explicitly non-native `o200k_base` token proxy with charged writes.\n"
    target='reports/submission/ROI_VERIFIED_BENCHMARK.json'
    link='https://github.com/RevanthAI/OneDesk/blob/main/'+target if article else prefix+target
    result+=f"\n[Full audit, per-hour prices and benchmark provenance]({link}); per-turn counts are in `ROI_TOKEN_TURNS.jsonl`. Electricity uses **175 W × $0.10/kWh**, not a power meter. T4 remains an unmeasured token-adjusted edge proxy; on-premises/VPC privacy depends on connector and logging controls. Historical schedules: [OpenAI caching](https://openai.com/index/api-prompt-caching/), [Claude caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [HF Jobs rates](https://huggingface.co/docs/hub/en/jobs-pricing).\n"
    return result+'\n'
