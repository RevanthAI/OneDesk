"""Task specifications and an evidence-consuming deterministic oracle."""
from __future__ import annotations
from .mcp_env import SCHEMAS, DISTRACTORS
from .mcp_adapter import wrap, initial_messages

LANGUAGES = ('en','hi','hinglish','te')
# Intentionally different surface forms in training and held-out evaluation.
TEMPLATES = {
 'train': {
  'en': ['What is {s} {p} now? Verify the runbook using {source}.', 'Please retrieve {s} {p}; compare documentation with {source}.'],
  'hi': ['{s} ka vartamaan {p} bataiye. Dastavez aur {source} se pushti kijiye.', 'Kripya {s} ke {p} ki jaanch dastavez tatha {source} se kijiye.'],
  'hinglish': ['Bhai, {s} ka current {p} kya hai? Notion aur {source} check karo.', '{s} ke liye {p} confirm kar do, docs ko {source} se cross-check karo.'],
  'te': ['{s} ki ippudu {p} entha? Runbook ni {source} tho sarichoodu.', '{s} yokka {p} cheppu; patram mariyu {source} rendu choodu.'],
 },
 'test': {
  'en': ['Audit the documented {p} for {s} against {source}; report the effective setting and any stale page.', 'Determine the deployed {p} of {s}, reconciling its runbook with {source}.'],
  'hi': ['{s} ke {p} ka prabhaavi maan kya hai? Puraane nirdesh ko {source} ke pramaan se milaakar bataaiye.', '{s} mein {p} sambandhi dastavez aur {source} ki tulna karke sahi maan dijiye.'],
  'hinglish': ['Hey, {s} pe {p} actually kitna configured hai? Runbook vs {source} reconcile karke outdated page flag karna.', '{s} ka {p} audit karna hai; docs aur {source} ko match karke final setting do.'],
  'te': ['{s} lo amalulo unna {p} viluva telapandi. Runbook vivaralanu {source} aadharaalatho polchandi.', '{s} kosam {p} pai patram paathadaa? {source} saakshyamtho polchi sariyaina viluva ivvandi.'],
 }}
INC_TEMPLATES = {
 'train': {
 'en': 'For incident {inc}, use db-mcp and time-mcp to find elapsed hours, then math-mcp to calculate elapsed hours times penalty_rate_per_hour. Give the total penalty.',
 'hi': 'Ghatna {inc} ke liye db-mcp tatha time-mcp se beetey ghante nikaaliye, phir math-mcp se ghante guna penalty_rate_per_hour karke kul jurmaana bataaiye.',
 'hinglish': 'Incident {inc} ka total penalty chahiye. db-mcp se details, time-mcp se hours, math-mcp se hours times penalty_rate_per_hour nikaalo.',
 'te': 'Sanghatana {inc} vivaraalu db-mcp lo choodu, time-mcp tho gantalu lekkinchu, math-mcp tho gantalu guninchu penalty_rate_per_hour; mottham penalty cheppu.'},
 'test': {
 'en': 'Compute the total time-based penalty for {inc}: retrieve the database incident, measure its duration using time-mcp, and multiply hours by penalty_rate_per_hour using math-mcp.',
 'hi': '{inc} ka samay-aadhaarit kul jurmaana nirdhaarit kijiye: db-mcp ke samay se time-mcp dwaara avadhi ghanton mein aur math-mcp dwaara avadhi guna penalty_rate_per_hour.',
 'hinglish': '{inc} pe kitni penalty bani? DB row lo, duration hours time-mcp se calculate karo aur hourly penalty_rate_per_hour se math-mcp pe multiply kar do.',
 'te': '{inc} valla vacchina mottham jarimaana entha? db-mcp saakshyam teesukoni time-mcp lo vyavadhi gantalu, math-mcp lo gantalu mariyu penalty_rate_per_hour gunakaaram cheyyandi.'}}

def build_tasks(world, count=400, mix=(20,15,50,15), split=None, pool=None):
    if world.get('schema_version')==2:
        from .v2_tasks import build_tasks_v2
        return build_tasks_v2(world,pool)
    if count % 4: raise ValueError('count must balance four languages')
    split = split or ('train' if world['split']=='train' else 'test')
    n = count//4
    if sum(mix)!=100: raise ValueError('mixture must sum to 100')
    counts=[round(n*x/100) for x in mix[:3]]
    counts.append(n-sum(counts))
    kinds=[kind for kind,c in zip(('consistent','incident','conflict','abstain'),counts) for _ in range(c)]
    if world['split']=='repo_style': kinds=['conflict']*n
    changed=[f for f in world['facts'] if f['was_updated']]
    same=[f for f in world['facts'] if not f['was_updated']]
    tasks=[]
    for i,kind in enumerate(kinds):
        f=(changed if kind=='conflict' else same)[i % len(changed if kind=='conflict' else same)]
        if world['split']=='repo_style': f=changed[i%len(changed)]
        active=['notion-mcp', f['source_server'],'db-mcp','time-mcp','unit-converter-mcp','math-mcp']
        if i%2==0: active+=DISTRACTORS
        # Expose alternate valid servers on some tasks without changing what the question requires.
        if i%3==0:
            active=list(dict.fromkeys(active+['github-mcp','slack-mcp']))
        expected='conflict_resolved' if kind=='conflict' else 'answered'
        gold=f['current_value']; cites=[f['notion_page_id'],f['source_id']]
        required=['notion-mcp',f['source_server']]
        steps=2; incident=None; missing=False
        if kind=='incident':
            incident=world['incidents'][i%len(world['incidents'])]
            from datetime import datetime
            hours=(datetime.fromisoformat(incident['resolved_at'])-datetime.fromisoformat(incident['started_at'])).total_seconds()/3600
            gold=hours*incident['penalty_rate_per_hour']; cites=[incident['incident_id']]
            required=['db-mcp','time-mcp','math-mcp']; steps=3
        if kind=='abstain':
            expected='abstain';gold=None;cites=[];required=['db-mcp']
            missing=bool(i%2)
            if not missing: active=[s for s in active if s!='db-mcp'];steps=0
            else: steps=1
        for li,lang in enumerate(LANGUAGES):
            s=f['service_name'] if not missing else f'unknown-{world["split"]}-service-{i}'
            if kind=='incident': question=INC_TEMPLATES[split][lang].format(inc=incident['incident_id'])
            elif kind=='abstain':
                forms={
                'train': {'en':'Read {s} {p} from db-mcp only. If db-mcp is unavailable or this service is absent, abstain.',
                'hi':'Keval db-mcp se {s} ka {p} bataaiye. Server na ho ya seva na mile to uttar dene se bachiye.',
                'hinglish':'{s} ka {p} DB se hi do. db-mcp off ho ya service missing ho toh abstain karo.',
                'te':'{s} ki {p} db-mcp nunche teesuko. Server lekapoyina seva dorakakapoyina samaadhaanam ivvaku.'},
                'test': {'en':'Database-only request: determine {p} for {s}. Return abstain if the database server is disconnected or has no such service.',
                'hi':'{s} ke {p} ke liye sirf db-mcp ka pramaan sweekar hai. Server anupalabdh ya seva agyaat hone par virat rahiye.',
                'hinglish':'DB-only audit: {s} ka {p} nikaalna hai. db-mcp disconnected ya entity missing hai toh answer guess mat karo, abstain do.',
                'te':'db-mcp aadharam maatrame vaadandi: {s} lo {p} entha? Database andubaatulo lekapothe leda seva lekapothe abstain ivvandi.'}}
                question=forms[split][lang].format(s=s,p=f['param_name'])
            else: question=TEMPLATES[split][lang][(i//len(same))%2].format(s=s,p=f['param_name'],source=f['source_server'])
            tasks.append(dict(task_id=f'{world["split"]}-{i:04d}-{lang}',case_id=f'{world["split"]}-{i:04d}',language=lang,kind=kind,question=question,
                world_split=world['split'],service_name=s,param_name=f['param_name'],source_server=f['source_server'],active_mcps=active,required_mcps=required,
                distractor_mcps=[s for s in active if s in DISTRACTORS],expected_status=expected,gold_value=gold,gold_cites=cites,
                stale_trap_value=f['initial_value'] if kind=='conflict' else None,stale_doc_id=f['notion_page_id'] if kind=='conflict' else None,
                oracle_optimal_steps=steps,incident_id=incident['incident_id'] if incident else None))
    return tasks

def run_oracle(task, env):
    if env.world.get('schema_version')==2:
        from .v2_oracle import run_oracle_v2
        return run_oracle_v2(task,env)
    messages=initial_messages(task,env)
    def call(server,tool,args):
        obj=dict(server=server,tool=tool,arguments=args)
        messages.append({'role':'assistant','content':wrap('tool_call',obj)})
        result=env.call(**obj)
        if isinstance(result,dict) and 'error' in result: raise AssertionError(result)
        messages.append({'role':'user','content':'Tool result: '+__import__('json').dumps(result)})
        return result
    cites=[];stale=None
    if any(s not in env.active_mcps for s in task['required_mcps']):
        status='abstain';value=None
    elif task['kind']=='abstain':
        rows=call('db-mcp','query_db',{'sql':f"SELECT * FROM microservices WHERE service_name = '{task['service_name']}'"})['rows']
        assert not rows
        status='abstain';value=None
    elif task['kind']=='incident':
        row=call('db-mcp','query_db',{'sql':f"SELECT * FROM production_incidents WHERE incident_id = '{task['incident_id']}'"})['rows'][0]
        hours=call('time-mcp','hours_between',{'start_iso':row['started_at'],'end_iso':row['resolved_at']})
        value=call('math-mcp','calculate',{'expression':f'{hours} * {row["penalty_rate_per_hour"]}'})
        status='answered';cites=[row['incident_id']]
    else:
        query=task['service_name']+' '+task['param_name']
        doc=call('notion-mcp','search_notion',{'query':query})[0]
        server=task['source_server']
        fresh=call(server,'search_github_prs' if server=='github-mcp' else 'search_slack',{'query':query})[0]
        import re
        old=int(re.search(r'= (\d+)',doc['snippet'])[1])
        text=fresh.get('summary',fresh.get('text'))
        value=int(re.search(r'= (\d+)',text)[1])
        date=fresh.get('merged_at',fresh.get('posted_at'))
        if value!=old:
            assert date>doc['updated_at']
            status='conflict_resolved';stale=doc['page_id']
        else: status='answered'
        cites=[doc['page_id'],fresh.get('pr_id',fresh.get('msg_id'))]
    final=dict(status=status,value=value,cites=cites,stale_source=stale)
    messages.append({'role':'assistant','content':wrap('final_answer',final)})
    return dict(prediction=final,messages=messages,num_tool_calls=len(env.calls),retrieved_ids=sorted(env.retrieved_ids),calls=list(env.calls))
