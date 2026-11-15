"""V2 SQLite initialization, ranked retrieval and bounded currency rounding."""
import ast,json,re,sqlite3
from .world_generator import PARAMS
from .mcp_env import safe_calculate

INCIDENT_COLUMNS=('incident_id','service_name','environment','started_at','resolved_at','root_cause_pr','penalty_rate_per_hour','weight_kg','data_spill_gb','recovery_cost_per_lb','recovery_cost_per_mib')
STOPWORDS=set('a an the is are what please tell me current active production prod runbook configuration config effective deployed setting settings audit documented document documentation reconcile compare against our deployment channels records recent value for of in and to this that ka ki ke kya hai bataiye batao prabhaavi maan lo entha kosam cheppu ni tho'.split())


def initialize(env):
    env.conn=sqlite3.connect(':memory:');env.conn.row_factory=sqlite3.Row
    env.conn.execute('CREATE TABLE microservices(service_name TEXT PRIMARY KEY, owner_handle TEXT, environment TEXT, '+','.join(p+' INTEGER' for p in PARAMS)+',updated_at TEXT,last_pr TEXT,evidence_id TEXT)')
    env.conn.execute('CREATE TABLE production_incidents(incident_id TEXT PRIMARY KEY,service_name TEXT,environment TEXT,started_at TEXT,resolved_at TEXT,root_cause_pr TEXT,penalty_rate_per_hour REAL,weight_kg REAL,data_spill_gb REAL,recovery_cost_per_lb REAL,recovery_cost_per_mib REAL)')
    env.conn.execute('CREATE TABLE notion_pages(page_id TEXT PRIMARY KEY,title TEXT,updated_at TEXT,snippet TEXT)')
    env.conn.execute('CREATE TABLE github_prs(pr_id TEXT PRIMARY KEY,title TEXT,merged_at TEXT,summary TEXT)')
    env.conn.execute('CREATE TABLE slack_messages(msg_id TEXT PRIMARY KEY,title TEXT,posted_at TEXT,text TEXT)')
    grouped={s:[] for s in env.world['services']}
    for fact in env.world['facts']:grouped[fact['service_name']].append(fact)
    for service,facts in grouped.items():
        values=[service,facts[0]['owner_handle'],'prod']+[next(f['current_value'] for f in facts if f['param_name']==p) for p in PARAMS]+[max(f['updated_date'] for f in facts),next((f['source_id'] for f in facts if f['latest_source_server']=='github-mcp'),None),facts[0]['db_id']]
        env.conn.execute('INSERT INTO microservices VALUES ('+','.join('?' for _ in values)+')',values)
    for row in env.world['incidents']:env.conn.execute('INSERT INTO production_incidents VALUES ('+','.join('?' for _ in INCIDENT_COLUMNS)+')',[row[k] for k in INCIDENT_COLUMNS])
    for server,rows in env.world['search_records'].items():
        table,cols={'notion-mcp':('notion_pages',('page_id','title','updated_at','snippet')),'github-mcp':('github_prs',('pr_id','title','merged_at','summary')),'slack-mcp':('slack_messages',('msg_id','title','posted_at','text'))}[server]
        env.conn.executemany('INSERT INTO '+table+' VALUES (?,?,?,?)',([r[k] for k in cols] for r in rows))
    env.conn.commit();env.conn.execute('PRAGMA query_only=ON');env.conn.set_authorizer(env._authorize)


def search(world,server,query):
    tokens={t for t in re.findall(r'[\w-]+',query.casefold()) if t not in STOPWORDS}
    if not tokens:return []
    params=[p for p in PARAMS if p in tokens];services=[s for s in world['services'] if s.casefold() in query.casefold()]
    target=max(services,key=len) if services else None
    candidates=[]
    for row in world['search_records'][server]:
        if params and row['param_name'] not in params:continue
        text=' '.join(str(v) for v in row.values()).casefold();terms=set(re.findall(r'[\w-]+',text))
        overlap=len(tokens&terms)
        if not overlap:continue
        score=overlap+20*bool(target and row['service_name']==target)+4*bool(params and row['param_name'] in params)
        if target:score+=len(set(target.split('-'))&set(row['service_name'].split('-')))*.2
        timestamp=row.get('updated_at',row.get('merged_at',row.get('posted_at','')))
        candidates.append((score,timestamp,json.dumps(row,sort_keys=True),row))
    candidates.sort(key=lambda r:r[:3],reverse=True)
    if target:
        # Retrieval diversity is query-based, not task/gold-aware. Do not always
        # rank PROD first: the newer staging trap commonly ranks above it.
        own=[r for r in candidates if r[3]['service_name']==target][:2]
        others=[r for r in candidates if r[3]['service_name']!=target]
        chosen=own+others[:3-len(own)]
        chosen.sort(key=lambda r:r[:3],reverse=True)
        return [dict(r[3]) for r in chosen]
    return [dict(r[3]) for r in candidates[:3]]


def calculate(expression):
    tree=ast.parse(expression,mode='eval').body
    if isinstance(tree,ast.Call):
        if not isinstance(tree.func,ast.Name) or tree.func.id!='round' or len(tree.args)!=2 or tree.keywords:raise ValueError('only round(arithmetic, decimal_places) is supported')
        places=tree.args[1]
        if not isinstance(places,ast.Constant) or type(places.value)!=int or not 0<=places.value<=6:raise ValueError('round precision must be 0..6')
        return round(safe_calculate(ast.unparse(tree.args[0])),places.value)
    return safe_calculate(expression)


def schema():
    return ['microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,'+','.join(p+' INTEGER' for p in PARAMS)+',updated_at TEXT,last_pr TEXT,evidence_id TEXT)', 'production_incidents('+','.join(INCIDENT_COLUMNS)+')']
