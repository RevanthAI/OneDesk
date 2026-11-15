from __future__ import annotations
import json
import re

class FormatError(ValueError): pass

def wrap(tag, value): return f'<{tag}>'+json.dumps(value, ensure_ascii=False, allow_nan=False)+f'</{tag}>'

def parse_turn(text):
    m = re.fullmatch(r'\s*<(tool_call|final_answer)>(.*?)</\1>\s*', text, re.S)
    if not m: raise FormatError('expected exactly one tool_call or final_answer JSON object')
    def reject_constant(x): raise ValueError('non-finite JSON')
    def unique(pairs):
        out = {}
        for k,v in pairs:
            if k in out: raise ValueError('duplicate JSON key')
            out[k] = v
        return out
    try: obj = json.loads(m[2], parse_constant=reject_constant, object_pairs_hook=unique)
    except (ValueError,TypeError) as e: raise FormatError(str(e)) from e
    if not isinstance(obj,dict): raise FormatError('JSON must be an object')
    if m[1] == 'tool_call':
        if set(obj) != {'server','tool','arguments'} or not isinstance(obj['arguments'],dict) or not all(isinstance(obj[k],str) for k in ('server','tool')): raise FormatError('invalid tool call structure')
    else:
        if set(obj) != {'status','value','cites','stale_source'}: raise FormatError('invalid final answer fields')
        if obj['status'] not in ('answered','conflict_resolved','abstain'): raise FormatError('invalid status')
        if not isinstance(obj['cites'],list) or not all(isinstance(x,str) for x in obj['cites']): raise FormatError('invalid citations')
        if obj['value'] is not None and type(obj['value']) not in (str,int,float): raise FormatError('invalid value')
        if obj['stale_source'] is not None and not isinstance(obj['stale_source'],str): raise FormatError('invalid stale_source')
        if obj['status'] == 'abstain' and obj['value'] is not None: raise FormatError('abstain value must be null')
        if obj['status'] == 'conflict_resolved' and not obj['stale_source']: raise FormatError('conflict requires stale_source')
        if obj['status'] != 'conflict_resolved' and obj['stale_source'] is not None: raise FormatError('stale_source must be null')
    return m[1], obj

def initial_messages(task, env):
    if getattr(env,'world',{}).get('schema_version')==2:
        from .v2_tasks import initial_messages_v2
        return initial_messages_v2(task,env)
    # Do not pass task metadata, gold values or oracle trajectories to the model.
    system = '''You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:
<tool_call>{"server":"server-name","tool":"tool-name","arguments":{}}</tool_call>
or <final_answer>{"status":"answered|conflict_resolved|abstain","value":"one exact value or null","cites":["retrieved evidence IDs"],"stale_source":null}</final_answer>
For conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n'''
    return [{'role':'system','content':system+json.dumps(env.schemas(), separators=(',',':'))}, {'role':'user','content':task['question']}]
