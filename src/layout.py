"""Resolve historical artifact paths without rewriting immutable evidence."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIXES = {
    'reports_submission': 'reports/submission',
    'reports_v2_2': 'reports/v2_2', 'reports_v2_1': 'reports/v2_1', 'reports_v2': 'reports/v2',
    'checkpoints_v2_2': 'checkpoints/v2_2', 'checkpoints_v2_1': 'checkpoints/v2_1', 'checkpoints_v2': 'checkpoints/v2',
    'src_v2_2': 'src/v2_2', 'src_v2_1': 'src/v2_1', 'src_v2': 'src/v2',
    'tests_v2_2': 'tests/v2_2', 'tests_v2_1': 'tests/v2_1', 'tests_v2': 'tests/v2',
    'hf_cards': 'docs/hf_cards', 'data': 'docs/archive/data_v1',
}


def relocated_path(value):
    path = Path(value)
    absolute = path.is_absolute()
    if absolute:
        try: path = path.relative_to(ROOT)
        except ValueError: return path
    parts = path.parts
    if not parts: return ROOT if absolute else path
    if parts[0] in PREFIXES:
        path = Path(PREFIXES[parts[0]], *parts[1:])
    elif parts[0] in ('reports', 'checkpoints') and len(parts) > 1 and parts[1] not in ('v1', 'v2', 'v2_1', 'v2_2', 'submission'):
        path = Path(parts[0], 'v1', *parts[1:])
    elif parts[0] == 'src' and len(parts) == 2 and not (ROOT / path).exists() and (ROOT / 'src/v1' / parts[1]).is_file():
        path = Path('src/v1', parts[1])
    return ROOT / path if absolute else path
