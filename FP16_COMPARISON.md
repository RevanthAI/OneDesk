# Test whether NF4 contributes to the formatting failures

FP16 has now completed 90 synthetic questions before a CUDA OOM; the matched partial findings are in `reports/precision_full/partial90_findings/FINDINGS.md`. The 100-question OSS-style run uses a separate lower-memory configuration. The remainder of this file describes the experiment commands. The previous run establishes performance of the NF4 deployment only. Quantization can change generated tokens; the recurring missing fields and quoted nulls may also reflect protocol-following gaps. This experiment separates those explanations without changing prompts or repairing answers.

## Recommended first run: 32 paired questions

Use the existing environment; no model download or package upgrade should be needed.

```bash
cd /home/revanth/workspace/hackathons/lexisai_hackathon/driftguard-mcp
bash scripts/run_precision_comparison.sh quick
```

This runs NF4 and FP16 sequentially, both with batch size 1, the same pinned model revision and frozen prompt messages, greedy decoding, 384 tokens per turn and six tool calls. It selects eight questions per language: two consistent, two incident, two conflict and two abstention tasks. The selection is deterministic and independent of previous model outcomes. There are eight semantic cases translated four ways; treat results as exploratory.

FP16 uses **no bitsandbytes weight quantization**. The 3.35B weights need approximately 6.2 GiB in FP16, plus generation memory. On the 8-GB RTX 2070 the script sets a 4.5-GiB parameter-placement budget using Accelerate; some layers may run through CPU offload. Actual placement is recorded in `runtime.json`. The budget does not cap KV cache/activation memory. Close GPU-heavy applications if needed. Avoid increasing batch size initially.

The script resumes completed task IDs if you run the same command again. It writes separate artifacts and does not replace the original NF4 report.

## Read the findings

After both runs finish:

- `reports/precision_quick_lowmem/FINDINGS.md`: paired scores, confidence intervals, failure counts, per-language/task breakdown, representative outputs and interpretation.
- `reports/precision_quick_lowmem/comparison.json`: machine-readable differences.
- `reports/precision_quick_lowmem/{nf4,fp16}/`: raw episodes, runtime placement, AuditKIT results and per-question metrics.

Compare valid-format rate first, then raw scalar/status correctness, strict outcomes, stale catches and citations. The report distinguishes missing fields, quoted nulls, wrong values/status, SQL/tool errors, empty searches, missing evidence and invented citations. Bootstrap intervals keep translated questions together. Unchanged scores on this small sample cannot prove equivalence.

To regenerate findings without running inference:

```bash
.venv/bin/python -m src.compare_precision \
  --reference reports/precision_quick_lowmem/nf4 \
  --candidate reports/precision_quick_lowmem/fp16 \
  --output reports/precision_quick
```

## Full confirmation

```bash
bash scripts/run_precision_comparison.sh full
```

This runs all 500 frozen questions in each precision mode and writes `reports/precision_full_lowmem/FINDINGS.md`. Batch-1/offloaded inference may take substantially longer than the earlier batched NF4 run. The report checks exact cohort/config/prompt matching and refuses incomplete comparisons.

If batch-1 FP16 still runs out of memory, use a new output path and a smaller placement budget:

```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv/bin/python -u -m src.evaluate_auditkit \
  --quantization fp16 --batch-size 1 --gpu-memory-gib 4 \
  --worlds test_synth --sample-per-language 8 \
  --output reports/precision_quick_lowmem/fp16_offload4
.venv/bin/python -m src.compare_precision \
  --reference reports/precision_quick_lowmem/nf4 \
  --candidate reports/precision_quick_lowmem/fp16_offload4 \
  --output reports/precision_quick_offload4
```

For GPU-only FP16, omit `--gpu-memory-gib` and use a new output directory; the 8-GB GPU may not have enough headroom. CPU offload preserves FP16 weights but changes placement and speed, so its throughput is not a precision-only comparison.

## What happened in the full run

The full printed summary came from the batch-1 NF4 arm, which completed all 500 questions. FP16 completed 90 synthetic questions before an attention allocation of 1.15 GiB failed with only about 571 MiB free. The original 6-GiB placement budget I provided left insufficient headroom for longer attention states on this 8-GB GPU; it budgets parameter placement, not all runtime allocations. The default script now reserves more headroom by using 4.5 GiB. Existing run folders retain their original config; use a new path for a changed memory budget.

Run just the requested OSS-style cohort:

```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv/bin/python -u -m src.evaluate_auditkit \
  --quantization fp16 --batch-size 1 --gpu-memory-gib 4.5 \
  --worlds repo_style --output reports/precision_full/fp16_oss_lowmem
.venv/bin/python -m src.compare_precision \
  --reference reports/precision_full/nf4 \
  --candidate reports/precision_full/fp16_oss_lowmem \
  --worlds repo_style --output reports/precision_full/oss_findings
```

## Turing attention compatibility check

On this RTX 2070 / torch 2.8 / Transformers 4.57.6 stack, a direct kernel test found that native GQA could not use the efficient SDPA kernel, while explicitly repeating KV heads to match query heads could. `--sdpa-expand-kv` disables Transformers' native-GQA shortcut and uses its existing KV-repeat path, allowing the efficient kernel where supported. It does not force a particular backend for every shape. A numerical test verifies equivalence of grouped attention and explicit KV repetition in full precision; different GPU kernels can still have floating-point differences.

Both arms of the OSS comparison use this option, batch size 1, and unchanged frozen prompts. The comparison tool rejects mismatched attention settings. This is a version-specific workaround using the installed Transformers SDPA helper; it should be revalidated after a package upgrade. It is not proof that every long synthetic trajectory now fits.

The very slow 4.5-GiB FP16 offload pilot was preserved separately under `reports/precision_full/fp16_oss_lowmem/` and is excluded from the complete paired result.

After the active evaluations finish, the completed OSS comparison can be reproduced/rescored with:

```bash
bash scripts/run_oss_precision_comparison.sh
```

Final OSS results: `reports/precision_full/oss_findings/FINDINGS.md`. The earlier 90-question synthetic comparison remains at `reports/precision_full/partial90_findings/FINDINGS.md` and must not be described as a full synthetic FP16 evaluation.
