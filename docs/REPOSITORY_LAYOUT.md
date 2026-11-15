# Repository layout and compatibility

The implementation, regression tests, adapters and evidence now share versioned parent folders:

```text
src/{v1,v2,v2_1,v2_2}/
tests/{v1,v2,v2_1,v2_2}/
checkpoints/{v1,v2,v2_1,v2_2}/
reports/{v1,v2,v2_1,v2_2,submission}/
docs/hf_cards/
docs/archive/data_v1/
data_v2/
```

`data_v2/` stays at the repository root: the runtime explicitly requires its name and the 19-file approval lock. Its contents and manifests were not edited. Fourteen source paths listed in `data_v2/SOURCE_SHA256SUMS` also remain directly under `src/`, including the five dataset-generator files; all other legacy implementation modules live in `src/v1/`.

The canonical final runtime is `src.v2_2`, for example:

```bash
python -m src.v2_2.manage --help
python -c "from src.v2_2.manage import protected; print(protected())"
CUDA_VISIBLE_DEVICES='' python -m pytest tests -q
```

`src/__init__.py` installs module aliases; the three small root `src_v2*.py` compatibility modules make direct historical imports work even when Python does not load a repository `sitecustomize.py`. `conftest.py` installs the same aliases before pytest collection. Aliased submodules share the canonical module objects rather than loading another copy.

`src/layout.py` resolves old artifact paths inside immutable report/checkpoint lock records to their new physical locations. The recorded hashes and historical JSON evidence remain unchanged. Current scripts, document links and newly built source bundles use the consolidated paths.

## Pre-existing source-provenance mismatch

Before any move, 12 of 14 entries in `SOURCE_SHA256SUMS` matched their source files. The entries for `src/active_advantage.py` and `src/agenttune_grpo_backend.py` already differed from the saved source-provenance hashes. Those source bytes and the manifest were preserved; this cleanup does not claim to repair or conceal that historical mismatch. Available local source bundles were checked for the recorded original bytes, without finding them.

This source-provenance issue is separate from the dataset approval checks: `protected()` verifies all 19 frozen dataset files and the preserved historical report/ablation hashes. The before/after source audit and migration details are in [MIGRATION.json](../reports/submission/layout_upgrade/MIGRATION.json).
