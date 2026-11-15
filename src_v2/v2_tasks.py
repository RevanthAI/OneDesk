import json
from types import SimpleNamespace
from .mcp_env import SCHEMAS

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

