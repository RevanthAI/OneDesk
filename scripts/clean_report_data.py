"""Read-only, CPU-only inputs for the OneDesk submission assets."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
PROJECT_NAME = 'OneDesk'
BASE = 'CohereLabs/tiny-aya-fire'
BASE_REVISION = '73500c80fcb6c8bea3e830c21d5d2920249a0e1a'
FOLDERS = {
    'Base': 'reports/v2_2/prior_v2/base',
    'Weak SFT · 15 steps': 'reports/v2_2/prior_v2/sft',
    'Early RL · 120 updates': 'reports/v2_2/stage1_evaluation',
    'Collapsed RL · 340 updates': 'reports/v2_2/prior_v2/grpo',
    'Warmup SFT · 60 steps': 'reports/v2_2/sft_evaluation',
    'Final OneDesk · selected update 40': 'reports/v2_2/grpo_evaluation',
    'Full SFT · 120 steps': 'reports/v2_2/sft_full_evaluation',
}
SPLITS = [
    ('train_sft_240.jsonl', 'SFT warmup', 240),
    ('train_grpo_stage1.jsonl', 'RL stage 1', 400),
    ('train_grpo_stage2.jsonl', 'RL stage 2', 480),
    ('val_train_80.jsonl', 'Validation', 80),
    ('holdout_synth_400_frozen.jsonl', 'Synthetic holdout', 400),
    ('holdout_repo_style_100_frozen.jsonl', 'Repo-style holdout', 100),
]

def read(path):
    return json.loads(_artifact(path).read_text())

def rows(path):
    return [json.loads(line) for line in _artifact(path).read_text().splitlines()]

def digest(path):
    with _artifact(path).open('rb') as stream:
        h = hashlib.file_digest(stream, 'sha256')
    return h.hexdigest()


def _artifact(path):
    import sys
    if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
    from src.layout import relocated_path
    return ROOT / relocated_path(path)

def fmt(value, places=1):
    return str(Decimal(str(value)).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))

def percent(value, places=1):
    return fmt(Decimal(str(value)) * 100, places)

def ci(metric, places=2):
    if metric['estimate'] is None:
        return '—'
    return f"{percent(metric['estimate'], places)} [{percent(metric['ci95'][0], places)}, {percent(metric['ci95'][1], places)}]"

def table(headers, values):
    return '\n| ' + ' | '.join(headers) + ' |\n| ' + ' | '.join(['---'] * len(headers)) + ' |\n' + ''.join(
        '| ' + ' | '.join(str(v).replace('|', '\\|').replace('\n', '<br>') for v in row) + ' |\n' for row in values) + '\n'

def summaries():
    return {name: read(Path(folder) / 'summary.json') for name, folder in FOLDERS.items()}


def combined_holdouts(saved=None):
    """Pool each saved metric with its own eligible-task denominator."""
    saved = summaries() if saved is None else saved
    denominators = {'exact_outcome': 500, 'stale_catch': 250,
                    'verified_citation_f1': 425, 'format_valid': 500,
                    'required_chain_compliance': 425}
    result = {}
    for key in ['Base', 'Warmup SFT · 60 steps', 'Full SFT · 120 steps', 'Final OneDesk · selected update 40']:
        result[key] = {}
        for metric, expected in denominators.items():
            values = [saved[key][split]['metrics'][metric] for split in ['test_synth', 'repo_style']]
            total = sum(v['denominator'] for v in values)
            assert total == expected
            result[key][metric] = dict(estimate=sum(v['estimate'] * v['denominator'] for v in values) / total,
                                       denominator=total)
        result[key]['native_tool_call_validity'] = {
            split: saved[key][split]['auditkit_headline'].get('tool_call_validity')
            for split in ['test_synth', 'repo_style']}
    return result

def protect():
    # Import only hashing/data-verification helpers. No model is instantiated.
    import sys
    sys.path.insert(0, str(ROOT))
    from src.v2_2.manage import protected
    previous = Path.cwd()
    import os
    try:
        os.chdir(ROOT)
        assert protected() == 19
    finally:
        os.chdir(previous)

def data_manifest():
    result = []
    for filename, label, count in SPLITS:
        rs = rows(Path('data_v2') / filename)
        assert len(rs) == count
        result.append(dict(file=filename, label=label, rows=count,
                           cases=len({r['case_id'] for r in rs}), sha256=digest(Path('data_v2') / filename)))
    return result

def language_examples():
    rs = rows('data_v2/train_sft_240.jsonl')
    keys = [('en', 'latin'), ('hi', 'native'), ('hi', 'latin'), ('hinglish', 'latin'), ('te', 'native'), ('te', 'latin')]
    return [next(r for r in rs if r['language'] == lang and r['script'] == script and r['kind'] == 'conflict') for lang, script in keys]

def roi():
    from roi_analysis import scenarios
    return [dict(r, cost=r['cost_100000'], detail=r['basis']) for r in scenarios()]

def registry():
    """Only artifact-backed repositories, never the two untrained planned v2.1 names."""
    records = []
    def model(repo, revision, local, label, score_folder=None, merged=False, note=''):
        records.append(dict(repo_id=repo, repo_type='model', revision=revision, local=local,
                            label=label, score_folder=score_folder, merged=merged, note=note))
    for kind, info in read('reports/v1/cloud_sft/downloaded_models.json').items():
        model(info['repo'], info['revision'], 'checkpoints/v1/' + Path(info['local_path']).name,
              'Historical v1 SFT ' + kind, 'reports/v1/sft_fire_nf4' if kind == 'adapter' else None,
              kind == 'merged', 'V1 explicit-routing benchmark; v2 results do not apply. Merged export was not evaluated on the full holdout.' if kind == 'merged' else 'V1 explicit-routing benchmark; local NF4 results.')
    info = read('reports/v1/cloud_grpo/pilot-l40sx1-20261111T160022Z/downloads.json')
    model(info['adapter_repo'], info['adapter_revision'], 'checkpoints/v1/tiny-aya-fire-grpo-pilot-adapter',
          'Historical v1 GRPO pilot', note='40/40 validation before and after; no complete frozen-holdout evaluation.')
    for kind, info in read('reports/v2/MODEL_REVISIONS.json').items():
        model(info['repo'], info['revision'], 'checkpoints/v2/' + ('sft_adapter' if kind == 'SFT' else 'grpo_adapter'),
              'V2 weak SFT' if kind == 'SFT' else 'V2 collapsed RL — negative-result control',
              FOLDERS['Weak SFT · 15 steps'] if kind == 'SFT' else FOLDERS['Collapsed RL · 340 updates'])
    info = read('reports/v2_1/SAVED_SFT_ADAPTER.json')
    model(info['repo'], info['revision'], 'checkpoints/v2_1/sft_adapter', 'Full four-epoch SFT control', FOLDERS['Full SFT · 120 steps'])
    for kind, info in read('reports/v2_2/LOCAL_COMPLETION.json')['models'].items():
        labels = {'SFT_WARMUP': 'OneDesk protocol warmup · 60 steps', 'GRPO_BEST_VAL': 'OneDesk final agent · validation-selected update 40', 'GRPO_FINAL': 'OneDesk final-update ablation · update 80'}
        folders = {'SFT_WARMUP': FOLDERS['Warmup SFT · 60 steps'], 'GRPO_BEST_VAL': FOLDERS['Final OneDesk · selected update 40'], 'GRPO_FINAL': None}
        model(info['repo'], info['revision'], 'checkpoints/v2_2/' + Path(info['local_path']).name,
              labels[kind], folders[kind], note='Update 80 saved separately; selected update 40 has the reported holdout scores.' if kind == 'GRPO_FINAL' else '')
    for repo in ['driftguard-mcp-v2-data', 'driftguard-mcp-warmup-runs', 'driftguard-mcp-v2-runs',
                 'driftguard-mcp-v2-1-runs', 'driftguard-mcp-training-runs', 'driftguard-mcp-grpo-runs']:
        records.append(dict(repo_id='Revanth-ml/' + repo, repo_type='dataset', label='Frozen benchmark' if repo.endswith('v2-data') else 'Recorded experiment artifacts',
                            scope='data' if repo.endswith('v2-data') else 'runs'))
    return records
