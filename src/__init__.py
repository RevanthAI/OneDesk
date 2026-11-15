"""Canonical versioned packages with compatibility for historical imports."""
import importlib
import importlib.abc
import importlib.util
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent
_VERSIONS = {'src_v2': 'src.v2', 'src_v2_1': 'src.v2_1', 'src_v2_2': 'src.v2_2'}


class _AliasLoader(importlib.abc.Loader):
    def __init__(self, target): self.target = target
    def create_module(self, spec): return None
    def exec_module(self, module):
        sys.modules[module.__name__] = importlib.import_module(self.target)


class _LegacyImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        first, _, suffix = fullname.partition('.')
        canonical = None
        if first in _VERSIONS:
            canonical = _VERSIONS[first] + ('.' + suffix if suffix else '')
        elif fullname.startswith('src.v1.') and fullname.count('.') == 2:
            leaf = fullname.rsplit('.', 1)[1]
            if (_ROOT / (leaf + '.py')).is_file() and not (_ROOT / 'v1' / (leaf + '.py')).exists():
                canonical = 'src.' + leaf
        elif fullname.startswith('src.') and fullname.count('.') == 1:
            leaf = fullname.split('.')[1]
            if not (_ROOT / (leaf + '.py')).exists() and (_ROOT / 'v1' / (leaf + '.py')).is_file():
                canonical = 'src.v1.' + leaf
        if canonical:
            return importlib.util.spec_from_loader(fullname, _AliasLoader(canonical))


if not any(isinstance(f, _LegacyImports) for f in sys.meta_path):
    sys.meta_path.insert(0, _LegacyImports())
for _legacy, _canonical in _VERSIONS.items():
    if (_ROOT / _canonical.split('.')[-1]).is_dir():
        sys.modules.setdefault(_legacy, importlib.import_module(_canonical))
