import json
from pathlib import Path
import pytest
from src_v2.data import load,verify,world
from src_v2.mcp_env import MCPEnv
from src_v2.oracle_solver import run_oracle
from src_v2.reward import score_episode


def test_standalone_v2_runtime_and_data_binding():
    assert len(verify())==15
    with pytest.raises(ValueError):verify(Path('data'))
    w=world();tasks=load('sft')
    for kind in ('consistent','incident','conflict','abstain'):
        task=next(t for t in tasks if t['kind']==kind)
        with MCPEnv(w,task['active_mcps']) as env:e=run_oracle(task,env)
        assert score_episode(task,e,'evidence_gated')>=1
    assert len(load('validation'))==80 and len(load('stage1'))==400 and len(load('stage2'))==480


def test_v2_sft_has_no_truncation_with_exact_2560_budget():
    from transformers import AutoTokenizer
    from src_v2.preflight import encode_sft
    from src_v2.backend import MODEL,REVISION
    cached=Path('checkpoints/tiny-aya-fire-sft-adapter')
    tokenizer=AutoTokenizer.from_pretrained(str(cached) if cached.is_dir() else MODEL,revision=None if cached.is_dir() else REVISION)
    train,validation,report=encode_sft(tokenizer)
    assert len(train)==240 and len(validation)==80 and report['truncated_conversations']==0
    assert report['max_actual_tokens']<=2560


def test_v2_bundle_is_independent_and_does_not_include_credentials(tmp_path):
    import zipfile
    from src_v2.cloud_job import package
    archive=tmp_path/'bundle.zip';manifest=package(archive)
    with zipfile.ZipFile(archive) as z:
        names=z.namelist()
        assert 'src_v2/pipeline.py' in names and 'data_v2/SHA256SUMS' in names
        assert not any(n.startswith(('src/','data/','reports/')) or n.endswith('/.env') for n in names)
        assert z.read('data_v2/SHA256SUMS')==Path('data_v2/SHA256SUMS').read_bytes()
    assert len(manifest['data_hashes'])==15 and not manifest['legacy_included']


def test_pipeline_import_and_required_chain_metric():
    import src_v2.pipeline
    from src_v2.evaluation_core import measure,summary_metrics
    task=next(t for t in load('sft') if t['incident_subtype']=='payload_lb')
    with MCPEnv(world(),task['active_mcps']) as env:e=run_oracle(task,env)
    e['completion_reason']='final_answer'
    row=measure(task,e)
    assert row['required_chain_compliance']==1 and row['reward']>=1
    assert summary_metrics([row])['required_chain_compliance']['estimate']==1
