#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mode="${1:-quick}"
case "$mode" in
  quick) cohort=(--worlds test_synth --sample-per-language 8) ;;
  full) cohort=() ;;
  *) echo 'Usage: bash scripts/run_precision_comparison.sh [quick|full]' >&2; exit 2 ;;
esac
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
run_dir="${PRECISION_RUN_DIR:-reports/precision_${mode}_lowmem}"
# Batch size 1 in BOTH arms controls batching. FP16 has a 4.5-GiB parameter
# placement budget, leaving room for KV cache/activations/display on 8-GB GPUs.
# The placement budget is not a hard limit on total CUDA memory consumption.
.venv/bin/python -u -m src.evaluate_auditkit --quantization 4bit --batch-size 1 --output "$run_dir/nf4" "${cohort[@]}"
.venv/bin/python -u -m src.evaluate_auditkit --quantization fp16 --batch-size 1 --gpu-memory-gib 4.5 --output "$run_dir/fp16" "${cohort[@]}"
.venv/bin/python -m src.compare_precision --reference "$run_dir/nf4" --candidate "$run_dir/fp16" --output "$run_dir"
echo "Read $run_dir/FINDINGS.md"
