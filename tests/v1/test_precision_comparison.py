import copy
import json
from pathlib import Path
from collections import Counter
import pytest
from src.evaluate_auditkit import select_tasks,verify_manifest
from src.compare_precision import check_configs,features,load_run,compare
from src.oracle_solver import run_oracle
from src.mcp_env import MCPEnv

def frozen_tasks():return [json.loads(l) for l in Path('docs/archive/data_v1/holdout_synth_400_frozen.jsonl').read_text().splitlines()]

def test_balanced_pilot_and_translation_pairing():
    tasks=frozen_tasks();subset=select_tasks(tasks,8)
    assert len(subset)==32
    assert Counter(t['language'] for t in subset)==dict(en=8,hi=8,hinglish=8,te=8)
    assert all(v==2 for v in Counter((t['language'],t['kind']) for t in subset).values())
    assert len({t['case_id'] for t in subset})==8
    assert select_tasks(list(reversed(tasks)),8)==subset

def test_comparison_rejects_changed_decoding_or_batch():
    a={'quantization':'4bit','batch_size':1,'temperature':0};b=dict(a,quantization='fp16')
    check_configs(a,b)
    with pytest.raises(ValueError,match='batch_size'):check_configs(a,dict(b,batch_size=16))
    with pytest.raises(ValueError,match='temperature'):check_configs(a,dict(b,temperature=.8))

def test_partial_episodes_rejected(tmp_path):
    (tmp_path/'test_synth_episodes.jsonl').write_text('')
    with pytest.raises(ValueError,match='incomplete'):load_run(tmp_path,{'sample_per_language':8,'limit':0},'test_synth')

def test_end_to_end_paired_findings_with_simulated_traces(tmp_path):
    tasks=select_tasks(frozen_tasks(),8)
    world=json.loads(Path('docs/archive/data_v1/world_test_synth.json').read_text())
    base={'model':'test-only','revision':'test','quantization':'4bit','max_new_tokens':384,'max_tool_calls':6,'seed':42,'temperature':0.,'dataset_hashes':verify_manifest(Path('docs/archive/data_v1')),'limit':0,'sample_per_language':8,'worlds':['test_synth'],'batch_size':1}
    reference=tmp_path/'nf4';candidate=tmp_path/'fp16'
    for path,q in [(reference,'4bit'),(candidate,'fp16')]:
        path.mkdir();(path/'run_config.json').write_text(json.dumps(dict(base,quantization=q)));(path/'runtime.json').write_text('{}')
    ea=[];eb=[]
    for t in tasks:
        with MCPEnv(world,t['active_mcps']) as env:e=run_oracle(t,env)
        e.update(task_id=t['task_id'],final_text=e['messages'][-1]['content'],completion_reason='final_answer')
        eb.append(e)
        bad=copy.deepcopy(e);bad.update(prediction=None,final_text='invalid test output',completion_reason='malformed_output');ea.append(bad)
    for path,episodes in [(reference,ea),(candidate,eb)]:
        (path/'test_synth_episodes.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in episodes))
    output=tmp_path/'findings';compare(reference,candidate,output)
    summary=json.loads((output/'comparison.json').read_text())['test_synth']
    assert summary['format_improved']==32 and summary['format_regressed']==0
    assert summary['metrics']['exact_outcome']['paired_delta']['estimate']==1
    assert summary['metrics']['format_valid']['paired_delta']['ci95']==[1,1]
    assert (output/'FINDINGS.md').exists()
    malformed=copy.deepcopy(eb[0]);malformed.update(prediction=None,final_text='<final_answer>{"status":"abstain","value":"null","cites":null}</final_answer>')
    result=features(tasks[0],malformed)
    assert 'quoted_null' in result['errors'] and 'invalid_citation_field' in result['errors']

def test_partial_loading_requires_explicit_flag_and_preserves_ids(tmp_path):
    tasks=select_tasks(frozen_tasks(),8)
    t=tasks[0]
    (tmp_path/'test_synth_episodes.jsonl').write_text(json.dumps({'task_id':t['task_id'],'messages':t['prompt']})+'\n')
    config={'sample_per_language':8,'limit':0}
    with pytest.raises(ValueError,match='incomplete'):load_run(tmp_path,config,'test_synth')
    selected,episodes=load_run(tmp_path,config,'test_synth',allow_partial=True)
    assert [x['task_id'] for x in selected]==[t['task_id']]
    assert len(episodes)==1
    with pytest.raises(ValueError,match='worlds'):
        check_configs({'quantization':'4bit','worlds':['test_synth','repo_style']},{'quantization':'fp16','worlds':['repo_style']})
    check_configs({'quantization':'4bit','worlds':['test_synth','repo_style']},{'quantization':'fp16','worlds':['repo_style']},ignore_worlds=True)

def test_attention_setting_must_match_between_runs():
    a={'quantization':'4bit','sdpa_expand_kv':True};b={'quantization':'fp16','sdpa_expand_kv':True}
    check_configs(a,b)
    with pytest.raises(ValueError,match='sdpa_expand_kv'):check_configs(a,dict(b,sdpa_expand_kv=False))

def test_explicit_kv_repetition_preserves_grouped_attention_math():
    import torch
    torch.manual_seed(42)
    q=torch.randn(1,4,5,8);k=torch.randn(1,2,5,8);v=torch.randn_like(k)
    grouped=torch.nn.functional.scaled_dot_product_attention(q,k,v,is_causal=True,enable_gqa=True)
    expanded=torch.nn.functional.scaled_dot_product_attention(q,k.repeat_interleave(2,1),v.repeat_interleave(2,1),is_causal=True)
    torch.testing.assert_close(grouped,expanded,atol=1e-6,rtol=1e-5)
