"""Natural task rendering and grader-only facts; prompts contain no tool route."""
from datetime import datetime
import hashlib,json
from types import SimpleNamespace
from .mcp_env import SCHEMAS,DISTRACTORS

LANGUAGES=('en','hi','hinglish','te')
CONFIG={
 'train':{
 'en':['What is the active production {p} for {s}? Compare the runbook with deployment records and flag any outdated page.','Please audit {s}: reconcile its documented {p} with production deployment history.'],
 'hi':['{s} का वर्तमान production {p} क्या है? दस्तावेज़ और deployment records की तुलना करें और पुराने पन्ने को पहचानें।','Kripya {s} ke vartamaan production {p} ko dastavez aur tainaati ke pramaanon se jaanchkar puraana panna bataaiye.','{s} के लिए लागू {p} बताइए; यदि पुराने निर्देश अलग हों तो अंतर स्पष्ट करें।','{s} ka production {p} nirdhaarit kijiye; likhit nirdesh aur naveen tainaati soochna mein antar ho to bataaiye.'],
 'hinglish':['Bhai, {s} ka actual production {p} kya hai? Runbook aur deployment updates match karke outdated page flag karo.','{s} pe {p} confirm karna hai; docs aur deployment history disagree karein toh stale page identify karo.'],
 'te':['{s} కోసం ప్రస్తుతం production లో {p} ఎంత? రన్‌బుక్‌ను deployment ఆధారాలతో పోల్చి పాత పేజీని గుర్తించండి.','{s} lo ippudu production {p} entha? Runbook ni deployment aadharaalatho polchi paatha page gurthinchu.','{s} యొక్క అమలులో ఉన్న {p} చెప్పండి; పాత సూచనలు వేరుగా ఉంటే ఆ పేజీని తెలియజేయండి.','{s} kosam amalulo unna {p} ni cheppu; patram mariyu tainaati vivaraalu veruga unte paatha page chupinchu.']},
 'heldout':{
 'en':['Determine the deployed {p} of {s}, checking the operational documentation against the release trail. Identify any superseded page.','We need a production configuration review for {s}: establish {p} and identify documentation that deployment history has overtaken.'],
 'hi':['{s} में production {p} का प्रभावी मान निर्धारित कीजिए। संचालन निर्देशों को जारी deployment के प्रमाण से मिलाकर पुराने पन्ने का उल्लेख कीजिए।','{s} ke production {p} ka prabhaavi maan nikaaliye; sanchaalan nirdesh aur release ke pramaan mein virodh ho to puraana panna chuniye.'],
 'hinglish':['Team ko {s} ka deployed {p} chahiye; operational docs aur release trail reconcile karke superseded page mention karna.','Production review mein {s} ka {p} verify karna hai; release evidence se jo doc purana nikle use flag karo.'],
 'te':['{s} లో అమలైన production {p} విలువను నిర్ధారించండి. నిర్వహణ పత్రాన్ని release ఆధారాలతో పరిశీలించి కాలం చెల్లిన పేజీని సూచించండి.','{s} lo deploy ayina production {p} nirdhaarinchandi; nirvahana patram ni release saakshyaalatho saripolchi kaalam chellina page soochinchandi.']}}
INCIDENT={
 'sla_penalty':{'en':'What is the total time-based SLA penalty in USD for incident {inc}?','hi':'घटना {inc} का कुल समय-आधारित SLA जुर्माना USD में कितना है?','hi_latin':'Ghatna {inc} ka kul samay-aadhaarit SLA jurmaana USD mein kitna hai?','hinglish':'Incident {inc} ka total time-based SLA penalty USD mein kitna bana?','te':'సంఘటన {inc} కోసం సమయం ఆధారంగా మొత్తం SLA జరిమానా USD లో ఎంత?','te_latin':'Sanghatana {inc} kosam samayam aadharanga mottham SLA jarimaana USD lo entha?'},
 'config_audit':{'en':'Audit the current production {p} for the service affected by {inc}; reconcile its runbook and deployment history.','hi':'{inc} से प्रभावित सेवा का वर्तमान production {p} जाँचिए; उसके दस्तावेज़ और deployment इतिहास का मिलान कीजिए।','hi_latin':'{inc} se prabhaavit seva ka vartamaan production {p} jaanchiye; dastavez aur tainaati itihaas ka milaan kijiye.','hinglish':'{inc} jis service pe hua uska current production {p} audit karo; runbook aur deployment history reconcile karna.','te':'{inc} వల్ల ప్రభావితమైన సేవ యొక్క ప్రస్తుత production {p} తనిఖీ చేయండి; పత్రం మరియు deployment చరిత్రను పోల్చండి.','te_latin':'{inc} valla prabhaavitamaina seva yokka prastuta production {p} tanikhi cheyyandi; patram mariyu tainaati charitranu polchandi.'},
 'payload_lb':{'en':'For incident {inc}, calculate total recovery cost in USD using affected payload in pounds and the per-pound recovery tariff.','hi':'घटना {inc} के प्रभावित भार को pounds में मानकर प्रति-pound शुल्क से कुल recovery cost USD में बताइए।','hi_latin':'Ghatna {inc} ke prabhaavit bhaar ko pounds mein maankar prati-pound shulk se kul recovery cost USD mein bataaiye.','hinglish':'{inc} ka payload pounds mein consider karke per-pound recovery rate pe total USD cost nikaalo.','te':'{inc} లో ప్రభావితమైన బరువును pounds లో తీసుకుని ఒక్క pound రుసుముతో మొత్తం recovery cost USD లో లెక్కించండి.','te_latin':'{inc} lo prabhaavitamaina baruvunu pounds lo teesukoni okka pound rusumutho mottham recovery cost USD lo lekkinchandi.'},
 'payload_mib':{'en':'What is the total recovery bill in USD for {inc}, based on the affected data in MiB and the per-MiB recovery tariff?','hi':'{inc} के प्रभावित data को MiB में लेकर प्रति-MiB शुल्क के अनुसार कुल recovery bill USD में कितना है?','hi_latin':'{inc} ke prabhaavit data ko MiB mein lekar prati-MiB shulk ke anusaar kul recovery bill USD mein kitna hai?','hinglish':'{inc} ke affected data ko MiB mein account karke per-MiB rate se total recovery bill USD mein batao.','te':'{inc} లో ప్రభావితమైన data ను MiB లో తీసుకుని ఒక్క MiB రుసుముతో మొత్తం recovery bill USD లో ఎంత?','te_latin':'{inc} lo prabhaavitamaina data nu MiB lo teesukoni okka MiB rusumutho mottham recovery bill USD lo entha?'}}
ABSTAIN={
 'en':'Using only the production database, report {s} {p}. If that source is unavailable or has no such service, abstain.',
 'hi':'केवल production database के आधार पर {s} का {p} बताइए। वह स्रोत उपलब्ध न हो या सेवा न मिले तो उत्तर देने से बचिए।',
 'hi_latin':'Keval production database ke aadhaar par {s} ka {p} bataaiye. Vah srot na mile ya seva na ho to uttar dene se bachiye.',
 'hinglish':'{s} ka {p} production database se hi do. Source unavailable ho ya service na mile toh abstain karo.',
 'te':'production database ఆధారంగా మాత్రమే {s} యొక్క {p} చెప్పండి. ఆ మూలం అందుబాటులో లేకపోయినా సేవ లేకపోయినా సమాధానం ఇవ్వవద్దు.',
 'te_latin':'production database aadharanga maatrame {s} yokka {p} cheppandi. Aa moolam andubaatulo lekapoyina seva lekapoyina samaadhaanam ivvavaddu.'}


INCIDENT_HELDOUT={
 'sla_penalty':{'en':'Assess the USD SLA charge incurred during the outage logged as {inc}.','hi':'{inc} में दर्ज रुकावट पर समय के अनुसार लगने वाला SLA शुल्क USD में निर्धारित करें।','hi_latin':'{inc} mein darj rukaavat par samay ke anusaar lagne vaala SLA shulk USD mein nirdhaarit karein.','hinglish':'Outage record {inc} ka duration-based SLA charge USD mein assess karna hai.','te':'{inc} లో నమోదైన అంతరాయం సమయానికి వర్తించే SLA రుసుమును USD లో నిర్ణయించండి.','te_latin':'{inc} lo namodaina antaraayam samayaaniki vartinche SLA rusumunu USD lo nirnayinchandi.'},
 'config_audit':{'en':'From outage record {inc}, establish the affected component and verify its deployed {p} against operational documentation. Return the effective setting and flag a superseded page.','hi':'{inc} के outage record से संबंधित सेवा पहचानकर उसके लागू {p} को संचालन पत्र से मिलाइए और पुराने पन्ने का उल्लेख कीजिए।','hi_latin':'{inc} ke outage record se sambandhit seva pahchaankar uske laagu {p} ko sanchaalan patra se milaaiye aur puraana panna chuniye.','hinglish':'Outage entry {inc} se affected component identify karke uska deployed {p} operational docs ke against verify karo; superseded page flag karna.','te':'{inc} అంతరాయం నమోదులోని సేవను గుర్తించి దాని అమలైన {p} ను నిర్వహణ పత్రంతో సరిపోల్చండి; పాత పేజీని సూచించండి.','te_latin':'{inc} antaraayam namoduloni sevanu gurthinchi daani amalaina {p} nu nirvahana patramtho saripolchandi; paatha page soochinchandi.'},
 'payload_lb':{'en':'Estimate the USD restoration invoice for {inc} under the tariff billed per pound of affected material.','hi':'{inc} में प्रभावित सामग्री के प्रति pound शुल्क पर बहाली का कुल USD बिल निकालिए।','hi_latin':'{inc} mein prabhaavit saamagri ke prati pound shulk par bahaali ka kul USD bill nikaaliye.','hinglish':'Restoration invoice {inc} ke liye affected material ko per-pound tariff pe bill karo, total USD chahiye.','te':'{inc} లో ప్రభావితమైన పదార్థానికి ప్రతి pound ధరతో పునరుద్ధరణ మొత్తం USD బిల్లును అంచనా వేయండి.','te_latin':'{inc} lo prabhaavitamaina padaarthaaniki prati pound dharatho punaruddharana mottham USD billunu anchanaa veyandi.'},
 'payload_mib':{'en':'Determine the USD restoration invoice for data-loss record {inc}, whose tariff is billed per MiB recovered.','hi':'data-loss record {inc} के लिए प्रति MiB बहाली दर से कुल USD बिल निर्धारित कीजिए।','hi_latin':'data-loss record {inc} ke liye prati MiB bahaali dar se kul USD bill nirdhaarit kijiye.','hinglish':'Data-loss entry {inc} pe per-MiB restoration tariff lagega; USD invoice total determine karo.','te':'data-loss నమోదు {inc} కు ప్రతి MiB పునరుద్ధరణ ధరతో మొత్తం USD బిల్లును నిర్ణయించండి.','te_latin':'data-loss namodu {inc} ku prati MiB punaruddharana dharatho mottham USD billunu nirnayinchandi.'}}
ABSTAIN_HELDOUT={'en':'Database evidence is mandatory for this request: establish {s} {p}, or decline if the database is disconnected or that service is absent.','hi':'इस अनुरोध के लिए database प्रमाण अनिवार्य है: {s} का {p} निर्धारित करें; database बंद हो या सेवा न मिले तो विरत रहें।','hi_latin':'Is anurodh ke liye database pramaan anivaarya hai: {s} ka {p} nirdhaarit karein; database band ho ya seva na mile to virat rahein.','hinglish':'Is request mein database evidence mandatory hai: {s} ka {p} establish karo; database disconnected ya service absent ho toh decline karna.','te':'ఈ అభ్యర్థనకు database ఆధారం తప్పనిసరి: {s} యొక్క {p} నిర్ణయించండి; database కనెక్షన్ లేకపోతే లేదా సేవ లేకపోతే విరమించండి.','te_latin':'Ee abhyarthanaku database aadhaaram tappanisari: {s} yokka {p} nirnayinchandi; database connection lekapothe leda seva lekapothe viraminchandi.'}

def render(case,language,heldout=False):
    i=int(case['case_id'].rsplit('-',1)[1]);family='heldout' if heldout else 'train'
    if case['kind'] in ('consistent','conflict'):
        templates=CONFIG[family][language];text=templates[i%len(templates)].format(s=case['service_name'],p=case['param_name'])
    else:
        key=language+('_latin' if language in ('hi','te') and i%2 else '')
        if case['kind']=='incident':text=(INCIDENT_HELDOUT if heldout else INCIDENT)[case['incident_subtype']][key].format(inc=case['incident_id'],p=case['param_name'])
        else:text=(ABSTAIN_HELDOUT if heldout else ABSTAIN)[key].format(s=case['service_name'],p=case['param_name'])
    return text


def initial_messages_v2(task,env):
    from .v2_env import schema
    system='''You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:
<tool_call>{"server":"active server","tool":"available tool","arguments":{}}</tool_call>
or <final_answer>{"status":"answered|conflict_resolved|abstain","value":"single scalar or null","cites":["actually retrieved IDs"],"stale_source":null}</final_answer>
Use conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: '''+'; '.join(schema())+'\nActive schemas: '+json.dumps(env.schemas(),separators=(',',':'))
    return [{'role':'system','content':system},{'role':'user','content':task['question']}]


def prompt_for(task,world):
    schemas=[{'server':s,'tool':tool,'arguments':args} for s in task['active_mcps'] for tool,args in SCHEMAS[s].items()]
    return initial_messages_v2(task,SimpleNamespace(world=world,schemas=lambda:schemas))


def task_from_case(world,case,language):
    question=render(case,language,heldout=world['split']!='train')
    active=['notion-mcp','github-mcp','slack-mcp','db-mcp','time-mcp','unit-converter-mcp','math-mcp']
    if int(case['case_id'].rsplit('-',1)[1])%2==0:active+=DISTRACTORS
    kind=case['kind'];subtype=case['incident_subtype'];gold=None;status='answered';cites=[];stale=None;old=None
    required=['notion-mcp','github-mcp','slack-mcp']
    if kind=='abstain':
        status='abstain';required=['db-mcp']
        if not case['missing_entity']:active.remove('db-mcp')
    elif kind=='incident' and subtype!='config_audit':
        incident=next(i for i in world['incidents'] if i['incident_id']==case['incident_id']);cites=[incident['incident_id']]
        if subtype=='sla_penalty':
            duration=(datetime.fromisoformat(incident['resolved_at'])-datetime.fromisoformat(incident['started_at'])).total_seconds()/3600
            gold=round(duration*incident['penalty_rate_per_hour'],2);required=['db-mcp','time-mcp','math-mcp']
        elif subtype=='payload_lb':gold=round(incident['weight_kg']*2.2046226218487757*incident['recovery_cost_per_lb'],2);required=['db-mcp','unit-converter-mcp','math-mcp']
        else:gold=round(incident['data_spill_gb']*(1e9/2**20)*incident['recovery_cost_per_mib'],2);required=['db-mcp','unit-converter-mcp','math-mcp']
    else:
        fact=next(f for f in world['facts'] if f['service_name']==case['service_name'] and f['param_name']==case['param_name'])
        gold=fact['current_value'];status='conflict_resolved' if gold!=fact['initial_value'] else 'answered';stale=fact['notion_page_id'] if status=='conflict_resolved' else None;old=fact['initial_value'] if stale else None
        cites=[fact['notion_page_id']]
        for server in ('github-mcp','slack-mcp'):
            cites += [r.get('pr_id',r.get('msg_id')) for r in world['search_records'][server] if r['service_name']==case['service_name'] and r['param_name']==case['param_name'] and r['environment']=='prod']
        if kind=='incident':cites=[case['incident_id']]+cites;required=['db-mcp']+required
    task=dict(case,schema_version=2,world_split=world['split'],task_id=case['case_id']+'-'+language,language=language,question=question,active_mcps=active,required_mcps=required,distractor_mcps=[s for s in active if s in DISTRACTORS],gold_value=gold,expected_status=status,gold_cites=cites,stale_doc_id=stale,stale_trap_value=old,oracle_optimal_steps=0,oracle_steps_semantics='Measured discovery-policy length; not a proof of global SQL/tool optimality.')
    task['script']='native' if (language=='hi' and any('\u0900'<=c<='\u097f' for c in question)) or (language=='te' and any('\u0c00'<=c<='\u0c7f' for c in question)) else 'latin'
    task['prompt']=prompt_for(task,world)
    return task


def build_tasks_v2(world,pool=None):
    pools=[pool] if pool else list(world['case_pools'])
    return [task_from_case(world,case,language) for key in pools for case in world['case_pools'][key] for language in LANGUAGES]
