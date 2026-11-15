"""Bounded deterministic tool router; a separate SQLite connection per episode."""
from __future__ import annotations
import ast
from datetime import datetime
import json
import math
import operator
import re
import sqlite3
from .world_generator import PARAMS

SCHEMAS = {
 'notion-mcp': {'search_notion': {'query': 'string'}},
 'github-mcp': {'search_github_prs': {'query': 'string'}},
 'slack-mcp': {'search_slack': {'query': 'string'}},
 'db-mcp': {'query_db': {'sql': 'string'}, 'inspect_schema': {}},
 'time-mcp': {'hours_between': {'start_iso': 'string', 'end_iso': 'string'}},
 'unit-converter-mcp': {'convert_unit': {'value': 'number', 'from_unit': 'string', 'to_unit': 'string'}},
 'math-mcp': {'calculate': {'expression': 'string'}},
 'weather-mcp': {'get_weather': {'city': 'string'}},
 'calendar-mcp': {'list_meetings': {'date': 'string'}},
}
DISTRACTORS = ['weather-mcp', 'calendar-mcp']

def safe_calculate(expression):
    if len(expression) > 180: raise ValueError('expression too long')
    tree = ast.parse(expression, mode='eval')
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}
    def visit(n):
        if isinstance(n, ast.Expression): return visit(n.body)
        if isinstance(n, ast.Constant) and type(n.value) in (int, float): return n.value
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            return -visit(n.operand) if isinstance(n.op, ast.USub) else visit(n.operand)
        if isinstance(n, ast.BinOp) and type(n.op) in ops: return ops[type(n.op)](visit(n.left), visit(n.right))
        raise ValueError('only finite arithmetic with + - * / is allowed')
    result = visit(tree)
    if not math.isfinite(result) or abs(result) > 1e15: raise ValueError('numeric bound exceeded')
    return result

class MCPEnv:
    def __init__(self,world,active_mcps=None):
        if world.get('schema_version')!=2:raise ValueError('src_v2_1 accepts approved v2 worlds only')
        self.world=world;self.active_mcps=list(SCHEMAS) if active_mcps is None else list(active_mcps)
        if set(self.active_mcps)-SCHEMAS.keys():raise ValueError('unknown MCP server')
        self.calls=[];self.retrieved_ids=set()
        from .v2_env import initialize
        initialize(self)
    @staticmethod
    def _authorize(action, arg1, arg2, db, trigger):
        if action == sqlite3.SQLITE_READ:
            return sqlite3.SQLITE_OK if arg1 in ('microservices', 'production_incidents') else sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_SELECT: return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_FUNCTION:
            return sqlite3.SQLITE_OK if arg2 in ('count','max','min','sum','avg','abs','round','coalesce','lower','upper','length') else sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_DENY
    def sql_dump(self):
        """Trusted snapshot export; never exposed as a model tool.

        Generated DDL uses TEXT/INTEGER/REAL and standard INSERT syntax.
        PostgreSQL execution must still be checked on the deployment target.
        """
        replica=sqlite3.connect(':memory:')
        try:
            self.conn.backup(replica)
            return '\n'.join(replica.iterdump())+'\n'
        finally: replica.close()
    def close(self): self.conn.close()
    def __enter__(self): return self
    def __exit__(self, *args): self.close()
    def schemas(self):
        return [{'server': s, 'tool': t, 'arguments': a} for s in self.active_mcps for t, a in SCHEMAS[s].items()]
    def call(self, server, tool, arguments):
        record = dict(server=server, tool=tool, arguments=arguments)
        self.calls.append(record)
        try:
            if server not in self.active_mcps: raise ValueError('MCP server unavailable')
            if tool not in SCHEMAS[server]: raise ValueError('unknown tool')
            expected = SCHEMAS[server][tool]
            if not isinstance(arguments, dict) or set(arguments) != set(expected): raise ValueError('invalid argument keys')
            for k, typ in expected.items():
                v = arguments[k]
                if (typ == 'string' and not isinstance(v, str)) or (typ == 'number' and (type(v) not in (int,float) or not math.isfinite(v))): raise ValueError('invalid argument type')
            out = self._execute(server, tool, arguments)
        except (ValueError, TypeError, sqlite3.Error, SyntaxError, ZeroDivisionError, OverflowError) as e:
            out = {'error': str(e)}
        record['output'] = out
        def collect(v):
            if isinstance(v, dict):
                for k,x in v.items():
                    if k in ('page_id','pr_id','msg_id','incident_id','evidence_id') and isinstance(x,str): self.retrieved_ids.add(x)
                    collect(x)
            elif isinstance(v,list):
                for x in v: collect(x)
        collect(out)
        return out
    def _execute(self,server,tool,a):
        from . import v2_env
        if tool in ('search_notion','search_github_prs','search_slack'):return v2_env.search(self.world,server,a['query'])
        if tool=='inspect_schema':return v2_env.schema()
        if tool=='calculate':return v2_env.calculate(a['expression'])

        if tool == 'query_db':
            sql = a['sql']
            if not re.match(r'^\s*SELECT\b', sql, re.I): raise ValueError('only SELECT is allowed')
            budget = [0]
            def progress():
                budget[0] += 1
                return int(budget[0] > 1000)
            self.conn.set_progress_handler(progress, 100)
            try: return {'rows': [dict(r) for r in self.conn.execute(sql).fetchmany(32)]}
            finally: self.conn.set_progress_handler(None, 0)
        if tool == 'hours_between':
            start, end = (datetime.fromisoformat(a[k].replace('Z','+00:00')) for k in ('start_iso','end_iso'))
            return (end-start).total_seconds()/3600
        if tool == 'calculate': return safe_calculate(a['expression'])
        if tool == 'convert_unit':
            factors = {('kg','lb'):2.2046226218487757, ('gb','mib'):1e9/2**20, ('hours','minutes'):60}
            pair = (a['from_unit'].lower(),a['to_unit'].lower())
            if pair in factors: return a['value']*factors[pair]
            if pair[::-1] in factors: return a['value']/factors[pair[::-1]]
            raise ValueError('unsupported conversion; gb is decimal GB')
        if tool == 'get_weather': return {'city': a['city'], 'forecast': 'synthetic distractor, no live weather'}
        if tool == 'list_meetings': return {'date': a['date'], 'meetings': []}
        raise ValueError('unsupported tool')

def fastmcp_server(world, active_mcps=None):
    """Optional actual MCP transport; the same router is used for local rollouts."""
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP('driftguard')
    env = MCPEnv(world, active_mcps)
    @mcp.tool()
    def route(server: str, tool: str, arguments: dict) -> str:
        return json.dumps(env.call(server, tool, arguments), ensure_ascii=False)
    return mcp
