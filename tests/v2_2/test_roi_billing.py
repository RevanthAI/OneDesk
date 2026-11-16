"""Arithmetic and workload safeguards for the offline Rule 5 analysis."""
import pytest
from scripts.verify_roi_billing import split_tokens, billing
from scripts.benchmark_v2_1_roi import select_tasks


def test_prompt_cache_requires_threshold_and_rounds_to_blocks():
    a=split_tokens(list(range(1500)),list(range(1100)),quantum=128,minimum=1024)
    assert a['repeated_prefix_tokens']==1100
    assert a['eligible_cached_tokens']==1024
    assert a['new_input_tokens']==400
    assert a['billed_uncached_tokens']==476
    b=split_tokens(list(range(1500)),list(range(1023)),quantum=128,minimum=1024)
    assert b['eligible_cached_tokens']==0


def test_first_turn_is_entirely_uncached():
    a=split_tokens([1]*1800,[],quantum=128,minimum=1024)
    assert a['input_tokens']==a['new_input_tokens']==a['billed_uncached_tokens']==1800
    assert a['eligible_cached_tokens']==0


def test_changed_prefix_cannot_farm_cache_credit():
    a=split_tokens([9]+list(range(2000)),list(range(2000)),quantum=128,minimum=1024)
    assert a['repeated_prefix_tokens']==a['eligible_cached_tokens']==0


def test_gpt4o_cached_bill_discounts_only_eligible_input():
    x={'episodes':1000,'input_tokens':4000000,'output_tokens':100000,'eligible_cached_tokens':2000000}
    r=billing(x,'gpt4o')
    assert r['uncached_usd_per_1000']==pytest.approx(11.)
    assert r['cached_usd_per_1000']==pytest.approx(8.5)
    assert r['cache_write_tokens']==0


def test_claude_cache_writes_are_charged_not_free():
    x={'episodes':1000,'input_tokens':4000000,'output_tokens':100000,
       'claude_cache_read_tokens':2000000,'claude_cache_write_tokens':1000000}
    r=billing(x,'claude35')
    assert r['uncached_usd_per_1000']==pytest.approx(13.5)
    assert r['cached_usd_per_1000']==pytest.approx(8.85)


def test_timing_sample_has_16_synth_4_repo_and_each_kind_language():
    from collections import Counter
    tasks=select_tasks()
    assert len({t['task_id'] for t in tasks})==20
    assert len({t['case_id'] for t in tasks})==20
    assert Counter(t['benchmark_split'] for t in tasks)=={'test_synth':16,'repo_style':4}
    assert Counter(t['kind'] for t in tasks)=={'conflict':5,'consistent':5,'incident':5,'abstain':5}
    assert set(t['language'] for t in tasks)=={'en','hi','hinglish','te'}
    assert {t['incident_subtype'] for t in tasks if t['kind']=='incident'}=={'sla_penalty','payload_lb','payload_mib','config_audit'}
