#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
.venv/bin/python -u -m src.evaluate_auditkit --quantization 4bit --batch-size 1 --sdpa-expand-kv --worlds repo_style --output reports/precision_full/nf4_oss_efficient
.venv/bin/python -u -m src.evaluate_auditkit --quantization fp16 --batch-size 1 --gpu-memory-gib 6 --sdpa-expand-kv --worlds repo_style --output reports/precision_full/fp16_oss_efficient
.venv/bin/python -m src.compare_precision --reference reports/precision_full/nf4_oss_efficient --candidate reports/precision_full/fp16_oss_efficient --worlds repo_style --output reports/precision_full/oss_findings
