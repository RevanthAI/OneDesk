"""Constructed OSS-style drift cases. These are NOT verified real repository changes."""
from .world_generator import generate_world, PARAMS

def generate_repo_world(version=1):
    if version==2:
        from .v2_world import make_world
        return make_world(137,'repo_style')
    if version!=1: raise ValueError('unsupported world version')
    world = generate_world(137, 'test_synth')
    names = [f'{lib}-case-{i:02d}' for i in range(10) for lib in ('fastapi','pydantic','litellm')]
    facts = []
    for i,s in enumerate(names):
        old = 10000+2*i
        facts.append(dict(service_name=s,param_name=PARAMS[i%6],initial_value=old,current_value=old+1,
            initial_date='2025-01-01T00:00:00+00:00',updated_date='2026-01-01T00:00:00+00:00',
            was_updated=True,notion_page_id=f'NOTION-REALSTYLE-{i:02d}',source_id=f'PR-REALSTYLE-{i:02d}',
            source_server='github-mcp',owner_handle=f'@oss_fixture_{i:02d}',db_id=f'DB-REALSTYLE-{i:02d}'))
        # Every service has a complete live config row, but only one drift target.
        for p in PARAMS:
            if p != PARAMS[i%6]:
                facts.append(dict(facts[-1],param_name=p,initial_value=20000+i,current_value=20000+i,was_updated=False,
                    notion_page_id=f'NOTION-REALSTYLE-{i:02d}-{p}',source_id=f'PR-REALSTYLE-{i:02d}-{p}'))
    world.update(split='repo_style',services=names,employees=[f'@oss_fixture_{i:02d}' for i in range(40)],facts=facts,incidents=[],
                 provenance={'kind':'constructed_oss_style','verified_real_changes':False,'case_count':30})
    return world
