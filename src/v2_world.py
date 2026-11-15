"""Version-two structured worlds; no model invents facts or labels."""
from __future__ import annotations
from datetime import datetime,timedelta,timezone
import hashlib,random
from .world_generator import PARAMS,TRAIN_SERVICES,TEST_SERVICES

DOMAINS={'timeout_sec':(5,180),'max_retries':(1,12),'rate_limit_rpm':(100,5000),'batch_size_mb':(16,512),'sla_hours':(1,48),'circuit_breaker_pct':(10,80)}
EXTRA_TRAIN='bank-feed balance-worker account-vault credit-router debit-processor wire-dispatch fx-router mandate-store payout-worker merchant-api receipt-worker invoice-store reconciliation-worker fraud-router consent-api signing-gateway analytics-sink backup-worker token-service limit-manager ledger-writer routing-proxy document-store identity-worker attachment-api reconciliation-store vendor-router transfer-ledger settlement-worker fee-engine dispute-api customer-vault export-worker policy-router notification-worker'.split()
OSS_NAMES='fastapi-gzip-middleware litellm-router-proxy pydantic-schema-validator vllm-kv-cache-manager uvicorn-worker-pool fastapi-request-router litellm-retry-handler pydantic-settings-loader vllm-scheduler uvicorn-keepalive-manager starlette-session-middleware httpx-connection-pool celery-task-router redis-stream-consumer sqlalchemy-pool-manager trl-rollout-worker gradio-queue-manager django-cache-backend aiohttp-client-pool rq-job-worker dramatiq-broker-worker ray-object-spiller bentoml-batch-runner prefect-flow-runner dagster-event-writer streamlit-session-store sanic-http-worker tornado-request-handler quart-websocket-worker falcon-api-middleware'.split()
KINDS=('consistent','incident','conflict','abstain')
POOLS=(('train_sft',60),('train_grpo1',100),('train_grpo2',120),('train_val',20),('train_reserved',20))


def values_for(param,split):
    lo,hi=DOMAINS[param];residue={'train':1,'test_synth':2,'repo_style':0}[split]
    return [v for v in range(lo,hi+1) if v%3==residue]


def missing_names(split,n):
    starts={'train':['forex','biometric','swift','escrow','margin','merchant','funding','collateral'], 'test_synth':['crypto','ach','iban','sepa','custody','derivative','reserve','clearing'], 'repo_style':['asgi','wsgi','schema','tokenizer','worker','gateway','stream','http']}[split]
    ends=['hedger','gate','bridge','reconciler','validator','vault','dispatcher','broker','relay','coordinator']
    return [a+'-'+b for a in starts for b in ends][:n]


def make_world(seed=42,split='train'):
    rng=random.Random(seed);prefix={'train':'V2-TR','test_synth':'V2-TS','repo_style':'V2-OSS'}[split]
    services=list(TRAIN_SERVICES)+EXTRA_TRAIN if split=='train' else list(TEST_SERVICES) if split=='test_synth' else OSS_NAMES
    assert len(services)==len(set(services))
    employee_count=80 if split=='train' else 40
    world=dict(schema_version=2,seed=seed,split=split,services=services,employees=[f'@{prefix.lower()}_engineer_{i:02d}' for i in range(employee_count)],facts=[],incidents=[],case_pools={})
    facts=world['facts']
    for i,(service,param) in enumerate((s,p) for s in services for p in PARAMS):
        candidates=values_for(param,split);old,current,intermediate,staging=rng.sample(candidates,4)
        changed=rng.random()<.6
        facts.append(dict(service_name=service,param_name=param,initial_value=old,current_value=current if changed else old,intermediate_value=intermediate,staging_value=staging,was_updated=changed,cross_channel=False,tracking_hint=rng.choice(['github','slack','none']),source_server=rng.choice(['github-mcp','slack-mcp']),notion_page_id=f'NOTION-{prefix}-{i:03d}',source_id=f'RECORD-{prefix}-{i:03d}',owner_handle=world['employees'][i%employee_count],db_id=f'DB-{prefix}-{services.index(service):03d}',initial_date='2026-02-05T09:30:00+00:00',updated_date='2026-09-17T14:00:00+00:00'))
    available=facts.copy();rng.shuffle(available)
    # Explicit allocation consumes each configuration pair at most once.
    absent=iter(missing_names(split,80));incident_counter=0;missing_counter=0
    subtype_counts={s:0 for s in ('sla_penalty','config_audit','payload_lb','payload_mib')}
    subtype_services={s:rng.sample(services,len(services)) for s in subtype_counts}
    if split=='train':pool_sizes=POOLS
    elif split=='test_synth':pool_sizes=(('holdout_synth',100),)
    else:pool_sizes=(('holdout_repo_style',26),)
    for pool,size in pool_sizes:
        if split=='repo_style':kind_counts={'consistent':5,'incident':4,'conflict':13,'abstain':4}
        elif split=='test_synth':kind_counts={'consistent':20,'incident':15,'conflict':50,'abstain':15}
        else:kind_counts={kind:size//4 for kind in KINDS}
        kinds=[k for k in KINDS for _ in range(kind_counts[k])];rng.shuffle(kinds);cases=[]
        for index,kind in enumerate(kinds):
            case=dict(case_id=f'{pool}-{index:04d}',pool=pool,kind=kind,incident_id=None,incident_subtype=None,request_mode='audit',missing_entity=False)
            if kind=='incident':
                subtype=tuple(subtype_counts)[incident_counter%4];counter=subtype_counts[subtype];subtype_counts[subtype]+=1
                if subtype=='config_audit':
                    fact=available.pop();service=fact['service_name'];param=fact['param_name'];fact['was_updated']=bool(counter%2)
                    if not fact['was_updated']:fact['current_value']=fact['initial_value']
                    elif fact['current_value']==fact['initial_value']:fact['current_value']=next(v for v in values_for(param,split) if v not in (fact['initial_value'],fact['intermediate_value'],fact['staging_value']))
                else:
                    service=subtype_services[subtype][counter];param={'sla_penalty':'sla_penalty_usd','payload_lb':'recovery_cost_lb_usd','payload_mib':'recovery_cost_mib_usd'}[subtype]
                start=datetime(2026,10,1,tzinfo=timezone.utc)+timedelta(days=rng.randrange(20),minutes=rng.choice([30,90,150,270,390,510,690,810,1020,1170,1290,1410]))
                duration=rng.choice([.5,1.,1.5,2.5,3.5,4.,6.5,9.,13.5,19.])
                incident_id=f'INC-{prefix}-{incident_counter:03d}'
                world['incidents'].append(dict(incident_id=incident_id,service_name=service,environment='prod',started_at=start.isoformat(),resolved_at=(start+timedelta(hours=duration)).isoformat(),root_cause_pr=f'PR-{prefix}-{rng.randrange(len(facts)):03d}',penalty_rate_per_hour=rng.choice([12.5,15.,22.,35.,18.75,27.5]),weight_kg=rng.choice([1.25,3.5,8.75,12.5,24.,42.5,65.,110.]),data_spill_gb=rng.choice([.125,.5,1.25,2.5,6.,12.75]),recovery_cost_per_lb=rng.choice([.75,1.25,2.,3.5]),recovery_cost_per_mib=rng.choice([.0125,.025,.04,.075])))
                incident_counter+=1;case.update(service_name=service,param_name=param,incident_id=incident_id,incident_subtype=subtype)
            else:
                fact=available.pop();param=fact['param_name'];service=fact['service_name']
                if kind=='consistent':fact.update(was_updated=False,current_value=fact['initial_value'])
                if kind=='conflict':
                    fact['was_updated']=True
                    if fact['current_value']==fact['initial_value']:fact['current_value']=next(v for v in values_for(param,split) if v not in (fact['initial_value'],fact['intermediate_value'],fact['staging_value']))
                if kind=='abstain':
                    case['request_mode']='database_only';missing=missing_counter%2==0;missing_counter+=1
                    if missing:service=next(absent);case['missing_entity']=True
                case.update(service_name=service,param_name=param)
            cases.append(case)
        world['case_pools'][pool]=cases
    # Thirty percent of config-conflict cases (exact for the full 320 train pool).
    conflict_cases=[c for cases in world['case_pools'].values() for c in cases if c['kind']=='conflict']
    chosen=rng.sample(conflict_cases,round(.3*len(conflict_cases)))
    lookup={(f['service_name'],f['param_name']):f for f in facts}
    for c in chosen:lookup[(c['service_name'],c['param_name'])]['cross_channel']=True
    for fact in facts:
        source=fact['source_server'];hint=fact['tracking_hint']
        if hint!='none':fact['tracking_hint']='github' if source=='github-mcp' else 'slack'
        if not fact['was_updated']:fact['updated_date']='2026-03-11T11:00:00+00:00'
    world['search_records']=render_records(world)
    for incident in world['incidents']:
        records=[r for r in world['search_records']['github-mcp'] if r['service_name']==incident['service_name'] and r['environment']=='prod']
        incident['root_cause_pr']=max(records,key=lambda r:r['merged_at'])['pr_id'] if records else None
    if split=='repo_style':world['provenance']={'kind':'constructed_oss_style_v2','verified_real_changes':False,'notes':'Domain-valid fixtures, not historical upstream snapshots.'}
    world['world_id']=hashlib.sha256((str(seed)+split+'v2').encode()).hexdigest()
    return world


def render_records(world):
    result={'notion-mcp':[],'github-mcp':[],'slack-mcp':[]};prefix={'train':'V2-TR','test_synth':'V2-TS','repo_style':'V2-OSS'}[world['split']]
    def deployment(f,server,value,date,suffix='',environment='prod',followup=False):
        label='PROD' if environment=='prod' else 'STAGING-ONLY';kind='PR' if server=='github-mcp' else 'SLACK'
        record=dict(service_name=f['service_name'],param_name=f['param_name'],environment=environment,title=f'{f["service_name"]} [{label}] {f["param_name"]}')
        text=f'{f["service_name"]} [{label}] {f["param_name"]} = {value}. '+('Production deployment verified.' if environment=='prod' else 'Staging test; this is not a production setting.')
        if followup:text+=' Production hotfix follow-ups are tracked in '+('Slack #deployments.' if server=='github-mcp' else 'GitHub PRs.')
        rid=f'{kind}-{prefix}-{world["facts"].index(f):03d}{suffix}'
        if server=='github-mcp':record.update(pr_id=rid,merged_at=date,summary=text)
        else:record.update(msg_id=rid,channel='#deployments' if environment=='prod' else '#staging',posted_at=date,text=text)
        result[server].append(record);return rid
    for f in world['facts']:
        hint=''
        if f['tracking_hint']!='none':hint=' Tracked via '+('GitHub PRs.' if f['source_server']=='github-mcp' else 'Slack #deployments.')
        result['notion-mcp'].append(dict(page_id=f['notion_page_id'],service_name=f['service_name'],param_name=f['param_name'],environment='prod',title=f'{f["service_name"]} [PROD] {f["param_name"]}',updated_at=f['initial_date'],snippet=f'{f["service_name"]} [PROD] {f["param_name"]} = {f["initial_value"]}. Production runbook at publication.'+hint))
        result['notion-mcp'].append(dict(page_id=f['notion_page_id']+'-STG',service_name=f['service_name'],param_name=f['param_name'],environment='staging',title=f'{f["service_name"]} [STAGING-ONLY] {f["param_name"]}',updated_at='2026-10-25T18:30:00+00:00',snippet=f'{f["service_name"]} [STAGING-ONLY] {f["param_name"]} = {f["staging_value"]}. Staging-only trial; do not apply this setting to production.'))
        first=f['source_server'];other='slack-mcp' if first=='github-mcp' else 'github-mcp'
        if f['cross_channel']:
            deployment(f,first,f['intermediate_value'],'2026-06-13T10:30:00+00:00',followup=True)
            f['source_id']=deployment(f,other,f['current_value'],f['updated_date']);f['latest_source_server']=other
        else:
            f['source_id']=deployment(f,first,f['current_value'],f['updated_date']);f['latest_source_server']=first
        for server in (first,other):deployment(f,server,f['staging_value'],'2026-10-26T19:00:00+00:00',suffix='-STG',environment='staging')
    return result
