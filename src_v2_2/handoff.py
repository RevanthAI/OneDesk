"""Validate an exact planned stage boundary, never resume through a collapse guard."""
import json,shutil,hashlib
from pathlib import Path
from .data import write_json

REPORT_DIRS=('prior_v2','stage1_evaluation','sft_training','sft_evaluation','sft_full_evaluation')

def prepare_stage2(source,output,sft_accuracy):
    source=Path(source);output=Path(output)
    summary=json.loads((source/'stage1/sampler_summary.json').read_text())
    rows=[json.loads(l) for l in (source/'stage1/rollout_metrics.jsonl').read_text().splitlines()]
    active=[r for r in rows if r['optimizer_update_eligible']]
    history=json.loads((source/'validation_history.json').read_text())
    if summary['accepted']!=40 or len(active)!=40:raise ValueError('Continuation requires exactly 40 completed active Stage-1 updates')
    if any(r['reward_std']<=1e-6 or (r['kind']!='abstain' and r['max_reward']<=0) for r in active):raise ValueError('Source stage contains an invalid active group')
    if not history or history[-1]['step']!=40:raise ValueError('Missing stage-boundary validation')
    if any(h['early_stop'] or not h['safe'] for h in history):raise ValueError('Cannot bypass the validation abstention collapse guard')
    if history[-1]['best_accuracy']<sft_accuracy:raise ValueError('Selected best must retain the SFT fallback')
    for path in ('stage1/last_adapter/adapter_model.safetensors','best_val_adapter/adapter_model.safetensors'):
        if not (source/path).is_file():raise ValueError('Stage boundary is missing saved adapter weights')
    output.mkdir(parents=True,exist_ok=True)
    smoke=json.loads((source/'stage1/smoke_gate.json').read_text())
    if not smoke['passed']:raise ValueError('Cannot bypass a failed smoke gate')
    shutil.copytree(source/'stage1',output/'stage1',dirs_exist_ok=True)
    for name in ('step_020','step_040'):
        shutil.copytree(source/'validation'/name,output/'validation'/name,dirs_exist_ok=True)
    shutil.copytree(source/'best_val_adapter',output/'best_val_adapter',dirs_exist_ok=True)
    write_json(output/'validation_history.json',history)
    receipt=dict(starting_update=40,stage1_completed_updates=40,best_step=history[-1]['best_step'],best_accuracy=history[-1]['best_accuracy'],history=history,policy_sha256=hashlib.sha256((source/'stage1/last_adapter/adapter_model.safetensors').read_bytes()).hexdigest(),best_sha256=hashlib.sha256((source/'best_val_adapter/adapter_model.safetensors').read_bytes()).hexdigest(),optimizer='Fresh Stage-2 optimizer, exactly as in the original two-stage recipe; Stage-1 policy and frozen warmup reference are retained unchanged')
    write_json(output/'STAGE_BOUNDARY.json',receipt)
    return receipt
