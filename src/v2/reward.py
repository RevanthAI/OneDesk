"""Specified outcome-gated reward, plus an opt-in evidence-gated variant.

The specified reward is NOT mathematically ungameable: correct unsupported
answers still receive base reward, and always-abstain benefits from prevalence.
We preserve its exact behavior for transparent auditing rather than force a table.
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
import re
from .mcp_adapter import parse_turn, FormatError

def normalize_val(v):
    if v is None: return None
    if type(v) not in (int,float,str): return ('invalid',str(v))
    s=str(v).strip()
    if re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?',s):
        try:
            d=Decimal(s)
            if d.is_finite(): return d.normalize()
        except InvalidOperation: pass
    return s.casefold()

def outcome_ok(pred,spec):
    return bool(pred) and pred.get('status')==spec['expected_status'] and normalize_val(pred.get('value'))==normalize_val(spec['gold_value'])

def citation_f1(pred,spec,retrieved):
    claimed=set(pred.get('cites',[]));gold=set(spec['gold_cites'])
    if not claimed and not gold: return 0.0  # No verified cited IDs means no citation shaping reward.
    # Hallucinated IDs remain in the precision denominator.
    hits=len(claimed & set(retrieved) & gold)
    return 2*hits/(len(claimed)+len(gold)) if claimed or gold else 0.0

def required_chain_ok(spec,episode):
    """Successful server calls only; audit authorities derive from gold evidence IDs.

    Config-audit incidents share deployment discovery semantics with ordinary
    audits. Utility incident subtypes must execute every declared required server.
    Neither failed calls nor retrieving an ID from a different server satisfies it.
    """
    if spec.get('expected_status')=='abstain':return True
    called={c.get('server') for c in episode.get('calls',[]) if 'output' in c and not (isinstance(c['output'],dict) and 'error' in c['output'])}
    required=set(spec.get('required_mcps',[]))
    audit=spec.get('kind') in ('consistent','conflict') or spec.get('incident_subtype')=='config_audit'
    if audit:
        required-={'github-mcp','slack-mcp'}
        required.add('notion-mcp')
        for cite in spec.get('gold_cites',[]):
            if cite.startswith('PR-'):required.add('github-mcp')
            elif cite.startswith('SLACK-'):required.add('slack-mcp')
    return required<=called

def score_episode(spec,episode,mode='specified'):
    if episode.get('tool_format_error'): return -1.0
    try:
        if 'final_text' in episode: tag,pred=parse_turn(episode['final_text'])
        else:
            from .mcp_adapter import wrap
            tag,pred=parse_turn(wrap('final_answer',episode.get('prediction')))
        if tag!='final_answer': return -0.8
    except FormatError: return -0.8
    if spec['stale_trap_value'] is not None and normalize_val(pred['value'])==normalize_val(spec['stale_trap_value']): return -0.6
    if not outcome_ok(pred,spec): return 0.05 if mode=='specified' else -0.2
    f1=citation_f1(pred,spec,episode.get('retrieved_ids',[]))
    if mode=='evidence_gated' and spec['expected_status']!='abstain':
        if f1==0 or not required_chain_ok(spec,episode):return 0.0
    result=1.0+0.3*f1
    if spec['expected_status']=='conflict_resolved' and pred['stale_source']==spec['stale_doc_id']: result+=0.2
    result-=0.08*max(0,episode.get('num_tool_calls',0)-spec['oracle_optimal_steps'])
    if any(c.get('server') in spec['distractor_mcps'] for c in episode.get('calls',[])): result-=0.25
    return result
