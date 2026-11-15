import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from src_v2_2.selection import select_warmup
from src_v2_2.active_advantage import PositiveAnchorSampler


def tasks():return [dict(task_id=k+'-'+l,kind=k,language=l) for k in PositiveAnchorSampler.kinds for l in ('en','hi','hinglish','te')]

def row(step,accuracy,valid=.95,abstain=.25):return dict(step=step,exact_outcome=accuracy,format_valid=valid,predicted_abstention_rate=abstain,adapter='step'+str(step))

def test_warmup_selection_excludes_step30_and_protocol_failures():
    chosen=select_warmup([row(30,.80),row(45,.60),row(60,.67,.89)])
    assert chosen['step']==45

def test_warmup_selection_is_validation_only_and_prefers_requested_band():
    assert select_warmup([row(45,.60),row(60,.675)])['step']==60
    assert select_warmup([row(45,.675),row(60,.70)])['step']==45
    assert select_warmup([row(45,.70),row(60,.75)])['step']==60
    assert not select_warmup([row(45,.70),row(60,.75)])['within_preferred_accuracy_range']
    with pytest.raises(ValueError):select_warmup([row(45,.60,.89),row(60,.675,abstain=.41)])

@pytest.mark.parametrize('attempts,passed',[(12,True),(60,False)])
def test_smoke_gate_checks_five_real_updates_and_finite_logged_gradients(tmp_path,monkeypatch,attempts,passed):
    import torch
    from src_v2_2.agenttune_grpo_backend import PersistentLogs
    monkeypatch.setattr(torch.cuda,'max_memory_reserved',lambda:123)
    rows=[dict(optimizer_update_eligible=i<5) for i in range(attempts)]
    (tmp_path/'rollout_metrics.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    callback=PersistentLogs(tmp_path);control=SimpleNamespace(should_training_stop=False)
    for step in range(1,6):callback.on_log(SimpleNamespace(recipe_global_offset=0),SimpleNamespace(global_step=step),control,logs=dict(grad_norm=.1,loss=.1))
    g=json.loads((tmp_path/'smoke_gate.json').read_text())
    assert g['passed']==passed and g['finite_gradients'] and g['accepted_updates']==5
    assert control.should_training_stop==(not passed)

def test_weighted_rotation_carries_across_forty_update_stages():
    tasks=[dict(task_id=k+'-'+l,kind=k,language=l) for k in PositiveAnchorSampler.kinds for l in ('en','hi','hinglish','te')]
    accepted=[]
    for offset in (0,40):
        sampler=PositiveAnchorSampler(tasks,offset=offset)
        for _ in range(40):
            ts,_,_=sampler.next_active(lambda ts,temperature:[dict(reward=r) for r in [.3,-.85,-.3,-1,.3,1.3]],group_size=6);accepted.append(ts[0]['kind'])
    assert accepted==list(PositiveAnchorSampler.cycle)*10

def test_original_artifacts_and_frozen_data_preserved():
    from src_v2_2.manage import protected
    assert protected()==19


def test_seven_way_comparison_includes_validation_and_paired_clusters(tmp_path,monkeypatch):
    from src_v2_2.compare import compare
    template=Path('reports/v2_2')
    mapping=['prior_v2/base','prior_v2/sft','stage1_evaluation','prior_v2/grpo','sft_evaluation','grpo_evaluation','sft_full_evaluation']
    for name in mapping:
        original=template/('prior_v2/sft' if name in ('stage1_evaluation','sft_evaluation','grpo_evaluation') else name)
        dest=tmp_path/name;dest.mkdir(parents=True)
        (dest/'summary.json').write_text((template/'prior_v2/sft/summary.json').read_text())
        (dest/'run_config.json').write_text((original/'run_config.json').read_text())
        for split in ('validation','test_synth','repo_style'):(dest/(split+'_metrics.jsonl')).write_text((template/'prior_v2/sft'/(split+'_metrics.jsonl')).read_text())
    (tmp_path/'sft_training').mkdir();(tmp_path/'sft_training/metadata.json').write_text(json.dumps(dict(selected_step=60,selection=dict(predicted_abstention_rate=.25))))
    (tmp_path/'grpo_training').mkdir();history=[dict(step=step,exact_outcome=.225,predicted_abstention_rate=.25,safe=True,selected=step==60) for step in (20,40,60,80)]
    (tmp_path/'grpo_training/metadata.json').write_text(json.dumps(dict(completed_updates=80,selected_step=60,selected_validation_accuracy=.225,status='complete',early_stop=None,validation=history)))
    for event in history:
        folder=tmp_path/('grpo_training/validation/step_%03d'%event['step']);folder.mkdir(parents=True);(folder/'summary.json').write_text((template/'prior_v2/sft/summary.json').read_text())
    compare(tmp_path)
    text=(tmp_path/'comparison/EXPERIMENT_REPORT.md').read_text()
    assert 'v2 GRPO Stage 1 (120 updates)' in text and 'v2.1 SFT Full 4-Epoch (ablation)' in text and 'Validation exact outcome' in text
    assert set(json.loads((tmp_path/'comparison/paired_comparison.json').read_text()))=={'validation','test_synth','repo_style'}
    from src_v2_2 import finalize as post
    monkeypatch.setattr(post,'protected',lambda:19)
    (tmp_path/'COMPLETION.json').write_text('{"status":"complete"}')
    post.finalize(tmp_path)
    assert 'Task-kind exact outcome breakdown' in (tmp_path/'comparison/EXPERIMENT_REPORT.md').read_text()
    assert (tmp_path/'comparison/FINAL_VERIFICATION.json').exists()
    assert (tmp_path/'comparison/validation_progress.png').is_file()


@pytest.mark.parametrize('group_size',[4,6])
def test_live_warmup_backend_logs_diversity_and_rejects_negative_group(tmp_path,monkeypatch,group_size):
    import contextlib
    from collections import defaultdict
    from types import SimpleNamespace
    import torch
    import src_v2_2.agenttune_grpo_backend as backend
    trainer=backend.MCPGRPOTrainer.__new__(backend.MCPGRPOTrainer);ts=[dict(t,case_id=t['task_id'],gold_value=1,expected_status='answered',gold_cites=['DOC'],stale_doc_id=None) for t in tasks()]
    trainer.args=SimpleNamespace(recipe_deadline=None);trainer.world={'schema_version':2};trainer.trace_dir=tmp_path;trainer.rollout_batch=0;trainer.active_sampler=PositiveAnchorSampler(ts);trainer.num_generations=group_size;trainer.temperature=.8;trainer.state=SimpleNamespace(global_step=0,num_input_tokens_seen=0);trainer.model=SimpleNamespace(set_adapter=lambda name:None);trainer.accelerator=SimpleNamespace(device=torch.device('cpu'),unwrap_model=lambda m:m,autocast=contextlib.nullcontext);trainer.processing_class=SimpleNamespace(pad_token_id=0);trainer._metrics={'train':defaultdict(list)};trainer.logps=lambda m,ids,att,mask,**kw:torch.zeros((len(ids),ids.shape[1]-1));monkeypatch.setattr(torch.cuda,'max_memory_reserved',lambda:0)
    attempts=[]
    def sample(candidates,*args,**kwargs):
        attempts.append(candidates);rr=([-1,-.85,-.3,0,-1,-.85] if len(attempts)==1 else [.3,-.85,-.3,-1,.3,1.3])[:group_size];out=[]
        for t,r in zip(candidates,rr):
            e=dict(prediction=dict(status='answered',value=0,cites=['DOC'],stale_source=None),retrieved_ids=['DOC'],num_tool_calls=0,calls=[],messages=[],raw_turns=[],completion_reason='final_answer')
            out.append(dict(reward=r,specified_reward=.05,evidence_gated_reward=-.2,anti_collapse_reward=r,input_ids=[1,2,3],assistant_mask=[0,1,1],episode=e))
        return out
    monkeypatch.setattr(backend,'sample_episodes',sample);result=trainer._generate_and_score_completions([{'task':ts[0]}]*group_size);logged=[json.loads(x) for x in (tmp_path/'rollout_metrics.jsonl').read_text().splitlines()];raw=[json.loads(x) for x in (tmp_path/'rollouts.jsonl').read_text().splitlines()]
    assert len(attempts)==2 and trainer.state.global_step==0
    assert [r['optimizer_update_eligible'] for r in logged]==[False,True] and logged[0]['all_negative_skipped'] and not logged[0]['zero_variance_skipped']
    assert all({'specified_reward','evidence_gated_reward','anti_collapse_reward'}<=r.keys() for r in raw)
    assert result['advantages'][1]<0

    assert logged[0]["unique_assistant_sequences"]==1 and logged[1]["unique_assistant_sequences"]==1
    assert logged[1]["sampled_token_surprisal"]==0


def test_download_sync_fills_existing_prior_base_validation(tmp_path):
    from src_v2_2.manage import sync_reports
    remote=tmp_path/'downloaded';root=tmp_path/'canonical'
    for folder in (remote/'prior_v2/base',root/'prior_v2/base'):folder.mkdir(parents=True)
    (root/'prior_v2/base/summary.json').write_text('{"holdout":"old"}')
    (remote/'prior_v2/base/summary.json').write_text('{"holdout":"old","validation":"new"}')
    (remote/'prior_v2/base/validation_metrics.jsonl').write_text('new evaluation')
    (remote/'comparison').mkdir()
    sync_reports(remote,root)
    assert (root/'prior_v2/base/validation_metrics.jsonl').read_text()=='new evaluation'
    assert json.loads((root/'prior_v2/base/summary.json').read_text())['validation']=='new'
    assert (root/'comparison').is_symlink()


def boundary_fixture(root):
    source=root/'source'
    for folder in ('stage1/last_adapter','best_val_adapter','validation/step_020','validation/step_040','validation/step_060'):(source/folder).mkdir(parents=True)
    (source/'stage1/last_adapter/adapter_model.safetensors').write_bytes(b'exact-stage1-40-policy')
    (source/'best_val_adapter/adapter_model.safetensors').write_bytes(b'best-at-step20-not-latest40')
    (source/'stage1/sampler_summary.json').write_text('{"accepted":40}')
    (source/'stage1/smoke_gate.json').write_text('{"passed":true}')
    (source/'stage1/rollout_metrics.jsonl').write_text(''.join(json.dumps(dict(step=i,optimizer_update_eligible=True,reward_std=.5,kind='conflict',max_reward=1.5))+'\n' for i in range(40)))
    h=[dict(step=i,safe=True,early_stop=False,best_accuracy=.75,best_step=20) for i in (20,40)]
    (source/'validation_history.json').write_text(json.dumps(h));(source/'validation/step_060/DO_NOT_COPY').write_text('unrelated future partial run')
    return source


def test_boundary_transfer_retains_best_and_omits_future_stage2_validation(tmp_path):
    from src_v2_2.handoff import prepare_stage2
    source=boundary_fixture(tmp_path);out=tmp_path/'next';b=prepare_stage2(source,out,.675)
    assert b['starting_update']==40 and b['best_step']==20 and b['best_accuracy']==.75
    assert (out/'best_val_adapter/adapter_model.safetensors').read_bytes()==b'best-at-step20-not-latest40'
    assert not (out/'validation/step_060').exists()
    assert (out/'stage1/last_adapter/adapter_model.safetensors').read_bytes()==b'exact-stage1-40-policy'


def test_boundary_cannot_bypass_collapse_guard_or_incomplete_stage(tmp_path):
    from src_v2_2.handoff import prepare_stage2
    source=boundary_fixture(tmp_path)
    h=json.loads((source/'validation_history.json').read_text());h[-1].update(safe=False,early_stop=True)
    (source/'validation_history.json').write_text(json.dumps(h))
    with pytest.raises(ValueError,match='collapse guard'):prepare_stage2(source,tmp_path/'next',.675)
    (source/'stage1/sampler_summary.json').write_text('{"accepted":39}')
    with pytest.raises(ValueError,match='exactly 40'):prepare_stage2(source,tmp_path/'next',.675)


def test_continuation_kl_reference_stays_warmup_not_stage1_policy(monkeypatch):
    import src_v2_2.training as training
    calls=[]
    model=SimpleNamespace(config=SimpleNamespace(use_cache=True),load_adapter=lambda path,**kw:calls.append((path,kw)),set_adapter=lambda name:None,modules=lambda:[],gradient_checkpointing_enable=lambda **kw:None)
    monkeypatch.setattr(training,'load_base',lambda:('base','tokenizer'))
    monkeypatch.setattr(training.PeftModel,'from_pretrained',lambda *a,**kw:model)
    training.load_sft_policy('stage1-trained-policy',reference_adapter='frozen-warmup')
    assert calls==[('frozen-warmup',dict(adapter_name='reference',is_trainable=False))]


def test_partial_resume_retains_exact_journal_prefix_and_optimizer_files(tmp_path):
    from src_v2_2.checkpoint_resume import prepare_partial
    source=tmp_path/'source';cp=source/'stage1/checkpoint-20';cp.mkdir(parents=True)
    (cp/'trainer_state.json').write_text('{"global_step":20}')
    for name in ('optimizer.pt','scheduler.pt','rng_state.pth','adapter_model.safetensors','adapter_config.json'):(cp/name).write_bytes(name.encode())
    (source/'stage1/smoke_gate.json').write_text('{"passed":true}')
    rows=[dict(step=i,rollout_batch=i+1,kind='conflict',optimizer_update_eligible=True,reward_std=.5,max_reward=1.5,kind_saturated_fallback=False) for i in range(25)]
    for name in ('rollout_metrics.jsonl','rollouts.jsonl'):(source/'stage1'/name).write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (source/'stage1/optimizer_log.jsonl').write_text(''.join(json.dumps(dict(step=i+1,grad_norm=.1,loss=.01))+'\n' for i in range(25)))
    history=[dict(step=20,safe=True,early_stop=False,best_step=20,best_accuracy=.7375)]
    (source/'validation_history.json').write_text(json.dumps(history));(source/'validation/step_020').mkdir(parents=True)
    (source/'best_val_adapter').mkdir();(source/'best_val_adapter/adapter_model.safetensors').write_bytes(b'best20')
    out=tmp_path/'next';receipt=prepare_partial(source,out,.675,20,tmp_path/'warmup')
    assert receipt['starting_update']==20 and receipt['discarded_later_active_updates']==5
    kept=[json.loads(l) for l in (out/'stage1/rollout_metrics.jsonl').read_text().splitlines()]
    assert len(kept)==20 and all(r['step']<20 for r in kept)
    assert (out/'stage1/checkpoint-20/optimizer.pt').read_bytes()==b'optimizer.pt'
    state=json.loads((out/'stage1/sampler_restore.json').read_text());assert state['accepted']==20 and state['draws']['conflict']==20 and state['rollout_batch']==20


def test_sampler_restore_replays_next_prompt_after_skips():
    from src_v2_2.checkpoint_resume import restore_sampler
    ts=[dict(task_id=f'{k}-{l}-{i}',kind=k,language=l) for k in PositiveAnchorSampler.kinds for l in ('en','hi','hinglish','te') for i in range(8)]
    original=PositiveAnchorSampler(ts,seed=20261113,temperature=1.,retry_temperature=1.15);calls=0
    def sample(candidates,temperature):
        nonlocal calls
        calls+=1;rewards=[1.3]*6 if calls%3==1 else [1.3,.3,-.85,.3,-1.,1.3]
        return [dict(reward=r) for r in rewards]
    for _ in range(20):original.next_active(sample,group_size=6)
    state=dict(offset=0,accepted=original.accepted,accepted_by_kind=original.accepted_by_kind.copy(),draws=original.draws.copy(),fallbacks=original.fallbacks)
    restored=PositiveAnchorSampler(ts,seed=20261113,temperature=1.,retry_temperature=1.15);restore_sampler(restored,state)
    mixed=lambda candidates,temperature:[dict(reward=r) for r in [1.3,.3,-.85,.3,-1.,1.3]]
    before=original.next_active(mixed,group_size=6)[0][0];after=restored.next_active(mixed,group_size=6)[0][0]
    assert before==after and original.draws==restored.draws and original.accepted==restored.accepted==21
