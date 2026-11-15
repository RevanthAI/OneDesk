"""V2 oracle discovers authority from tool observations, never hidden source labels."""
from datetime import datetime
import json,re
from .mcp_adapter import initial_messages,wrap


def run_oracle_v2(task,env):
    messages=initial_messages(task,env)
    def call(server,tool,args):
        messages.append({'role':'assistant','content':wrap('tool_call',dict(server=server,tool=tool,arguments=args))})
        out=env.call(server,tool,args)
        if isinstance(out,dict) and 'error' in out:raise AssertionError(out)
        messages.append({'role':'user','content':'Tool result: '+json.dumps(out,ensure_ascii=False)})
        return out
    def audit(service,param):
        query=service+' '+param+' current configuration runbook'
        candidates=call('notion-mcp','search_notion',{'query':query})
        docs=[r for r in candidates if r['service_name']==service and r['param_name']==param and r['environment']=='prod']
        if not docs:return dict(status='abstain',value=None,cites=[],stale_source=None)
        doc=max(docs,key=lambda r:r['updated_at']);snippet=doc['snippet'].casefold()
        hint='github-mcp' if 'tracked via github' in snippet else 'slack-mcp' if 'tracked via slack' in snippet else None
        order=[hint] if hint else ['github-mcp','slack-mcp'];records=[];seen=set()
        while order:
            server=order.pop(0)
            if server in seen:continue
            seen.add(server)
            rows=call(server,'search_github_prs' if server=='github-mcp' else 'search_slack',{'query':service+' '+param})
            good=[r for r in rows if r['service_name']==service and r['param_name']==param and r['environment']=='prod']
            records+=good
            texts=' '.join(r.get('summary',r.get('text','')) for r in good).casefold()
            other='slack-mcp' if server=='github-mcp' else 'github-mcp'
            if (not good or 'hotfix follow-ups' in texts) and other not in seen:order.append(other)
        if not records:return dict(status='abstain',value=None,cites=[],stale_source=None)
        latest=max(records,key=lambda r:datetime.fromisoformat(r.get('merged_at',r.get('posted_at'))))
        def value(text):
            match=re.search(re.escape(param)+r'\s*=\s*([+-]?\d+(?:\.\d+)?)',text)
            if not match:raise AssertionError('value missing from production evidence')
            number=float(match[1]);return int(number) if number.is_integer() else number
        documented=value(doc['snippet']);current=value(latest.get('summary',latest.get('text','')))
        conflict=current!=documented
        if conflict:assert latest.get('merged_at',latest.get('posted_at'))>doc['updated_at']
        return dict(status='conflict_resolved' if conflict else 'answered',value=current,cites=[doc['page_id']]+[r.get('pr_id',r.get('msg_id')) for r in records],stale_source=doc['page_id'] if conflict else None)
    if task['request_mode']=='database_only':
        if 'db-mcp' not in env.active_mcps:final=dict(status='abstain',value=None,cites=[],stale_source=None)
        else:
            rows=call('db-mcp','query_db',{'sql':f"SELECT * FROM microservices WHERE service_name = '{task['service_name']}'"})['rows']
            final=dict(status='answered',value=rows[0][task['param_name']],cites=[rows[0]['evidence_id']],stale_source=None) if rows else dict(status='abstain',value=None,cites=[],stale_source=None)
    elif task['incident_id']:
        rows=call('db-mcp','query_db',{'sql':f"SELECT * FROM production_incidents WHERE incident_id = '{task['incident_id']}'"})['rows']
        row=rows[0];subtype=task['incident_subtype']
        if subtype=='config_audit':
            final=audit(row['service_name'],task['param_name']);final['cites']=[row['incident_id']]+final['cites']
        else:
            if subtype=='sla_penalty':
                quantity=call('time-mcp','hours_between',{'start_iso':row['started_at'],'end_iso':row['resolved_at']});rate=row['penalty_rate_per_hour']
            elif subtype=='payload_lb':
                quantity=call('unit-converter-mcp','convert_unit',{'value':row['weight_kg'],'from_unit':'kg','to_unit':'lb'});rate=row['recovery_cost_per_lb']
            else:
                quantity=call('unit-converter-mcp','convert_unit',{'value':row['data_spill_gb'],'from_unit':'gb','to_unit':'mib'});rate=row['recovery_cost_per_mib']
            cost=call('math-mcp','calculate',{'expression':f'round({quantity} * {rate}, 2)'})
            final=dict(status='answered',value=cost,cites=[row['incident_id']],stale_source=None)
    else:final=audit(task['service_name'],task['param_name'])
    messages.append({'role':'assistant','content':wrap('final_answer',final)})
    return dict(prediction=final,final_text=messages[-1]['content'],messages=messages,num_tool_calls=len(env.calls),retrieved_ids=sorted(env.retrieved_ids),calls=list(env.calls),tool_format_error=False)
