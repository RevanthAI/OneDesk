# Cloud SFT smoke test and local model guide

> Update: the full 500-question local SFT evaluation has now completed. See [post-SFT findings](../sft_fire_nf4/FINDINGS.md) for verified results and trace analysis. Earlier statements below about a pending full evaluation describe the initial training/download stage.

## Smoke test: measured on A100 80 GB

Every batch completed five real optimizer steps at a padded length of 1,536. Gradients/losses were finite and LoRA weights changed. These are sizing measurements, not held-out task-success scores.

| Microbatch | Reserved GiB | Allocated GiB | Seconds/step | Examples/sec |
|---:|---:|---:|---:|---:|
| 1 | 7.50 | 7.24 | 0.495 | 2.020 |
| 2 | 8.19 | 7.89 | 0.684 | 2.922 |
| 4 | 9.52 | 9.19 | 1.308 | 3.057 |
| 8 | 12.21 | 11.78 | 2.512 | 3.185 |
| 16 | 17.56 | 16.97 | 4.890 | 3.272 |
| 32 | 28.28 | 27.34 | 9.647 | 3.317 |

Batch 32 is the largest tested batch, not a proven maximum. Batch 8 achieved most of the measured throughput while using substantially less memory. The selected configuration is microbatch 8, gradient accumulation 2, effective batch 16. Its measured memory leaves ample room on L40S 48 GB.

## Training configuration

- CohereLabs/tiny-aya-fire at revision 73500c80fcb6c8bea3e830c21d5d2920249a0e1a.
- BF16 frozen base with LoRA rank 16, alpha 32, dropout 0.05, all seven attention/MLP projection families.
- Exact assistant-only supervision, including tool calls and final responses; user prompts and tool-result turns are masked.
- Standard causal cross-entropy computed sparsely on supervised positions with checkpointed vocabulary-head chunks. Numerical loss and gradient equivalence are tested.
- 360 train trajectories and 40 validation trajectories, grouped by semantic case so translations stay together.
- Requested 1.5 epochs, rounded to 34 optimizer steps / 544 trajectory exposures.
- No frozen synthetic or OSS holdout examples are included in the cloud training bundle.
- Project backend extends the actual pinned AgentTune SFTTrainerBase lifecycle/config/callbacks. The upstream TRL SFT file is absent; no pretend replacement library is used.
- This is SFT only. GRPO has not run.

## Downloads and local usage

Both the adapter and standalone merged model have been downloaded and checked locally. They are also saved in private model repositories under your account. To download them again:

```bash
.venv/bin/python -m src.download_sft
```

The downloader writes:

- `checkpoints/tiny-aya-fire-sft-adapter/`
- `checkpoints/tiny-aya-fire-sft-merged/`

Run the adapter over the original NF4 base on the local RTX 2070:

```bash
.venv/bin/python -m src.run_local_sft --adapter checkpoints/tiny-aya-fire-sft-adapter
```

Or load the standalone merged model in NF4:

```bash
.venv/bin/python -m src.run_local_sft --model checkpoints/tiny-aya-fire-sft-merged
```

The default example is one unseen synthetic English conflict task. Pass `--task-id` to choose a different frozen synthetic question. It executes the real local MCP router and saves a trace and metrics. A single example is an installation smoke test, not a full post-SFT benchmark. The existing OSS holdout has documented domain-validity defects and is not used to claim real-repository transfer.

## Cloud records

- Smoke: https://huggingface.co/jobs/Revanth-ml/6af451009737d9a9e092d528
- SFT: https://huggingface.co/jobs/Revanth-ml/6af451ffab34849891ae08ce
- Private run assets: https://huggingface.co/datasets/Revanth-ml/driftguard-mcp-training-runs
- Adapter: https://huggingface.co/Revanth-ml/driftguard-tiny-aya-fire-sft
- Merged: https://huggingface.co/Revanth-ml/driftguard-tiny-aya-fire-sft-merged

The original L40S smoke allocation was canceled while still scheduling; an A100 ran the sizing test. L40S capacity became available for full training. Each paid job was bounded to 30 minutes. Actual charges should be checked in HF billing; list rates were $2.50/hour for A100 and $1.80/hour for L40S.

## Completed training results

Full SFT completed on L40S 48 GB with microbatch 8 and gradient accumulation 2. All 34 optimizer steps completed. Validation uses 40 trajectories from 10 held-out training-world cases, separate from the frozen evaluation worlds.

| Measurement | Before SFT | After SFT |
|---|---:|---:|
| Assistant-token validation cross-entropy | 0.426899 | 0.002778 |

Training loss was 0.428794 on the first step and 0.003432 on the last step. These losses measure supervised token prediction; they do not establish agent task accuracy or generalization. The full frozen 500-question post-SFT evaluation has not run.

## Local RTX 2070 checks and remaining failure

The downloaded adapter, applied to the original base loaded in NF4, completed the English, romanized Hindi, Hinglish, and romanized Telugu versions of **one** unseen synthetic conflict case. Each made two valid tool calls, returned the correct value 20, cited NOTION-TS-058 and PR-TS-058, and identified the stale page. These four translations share one semantic case and are installation checks, not an accuracy benchmark. Traces are in `local_adapter_example.json` and `local_adapter_language_checks.json` beside this report.

The standalone merged model also loaded and ran in NF4, using approximately 3.05 GiB peak reserved GPU memory, but failed that English case. It searched for `reconcile-api` instead of the requested `reconciliation-api`, received an empty result, and incorrectly abstained. Its final format was valid, but the outcome and citations were wrong. See `local_merged_example.json`.

Merging LoRA weights before quantizing and applying a floating-point adapter over an already quantized base are different numerical inference paths. The observed behavior differs, but this single example does not establish quantization as the cause; no matched full-precision comparison was run. Recommend the adapter command above for initial local use. Preserve both traces when comparing checkpoints.

## Downloaded artifacts

| Artifact | Local directory | Approximate size | Pinned HF revision |
|---|---|---:|---|
| Adapter and tokenizer | `checkpoints/tiny-aya-fire-sft-adapter` | 136 MiB | `b0d0d072311e62e31eb6258ad8ce987e8bf7926d` |
| Standalone merged model and tokenizer | `checkpoints/tiny-aya-fire-sft-merged` | 6.3 GiB | `9747926dfe35d4a7ff10761c8caec3c1714496b2` |

Paths are relative to the `driftguard-mcp` project root. `downloaded_models.json` records their absolute paths and repositories. `MODEL_SHA256SUMS` records checksums of downloaded model and tokenizer files, excluding Hub download metadata.

## Verification and cloud cleanup

The implementation test suite passed 33 tests, including assistant-only masking, grouped case separation, sparse/dense loss and gradient equivalence, LoRA gradients, and merged-model save/reload equivalence on a small unquantized fixture. Original frozen dataset checksums remain intact.

Final job inspection confirms the A100 smoke job and L40S training job are COMPLETED, and the original queued L40S smoke job is CANCELED. None of these jobs remain active; see `job_final_statuses.json`. No GRPO was launched. Check HF billing for actual charges rather than treating the job timeout as billed runtime.

## Full local evaluation after SFT

From the project root, evaluate all 400 synthetic and 100 constructed OSS-style questions and compare with the completed NF4 baseline:

```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv/bin/python -u -m src.evaluate_auditkit \
  --adapter-path checkpoints/tiny-aya-fire-sft-adapter \
  --quantization 4bit --batch-size 1 --sdpa-expand-kv \
  --output reports/sft_fire_nf4 \
  --baseline reports/precision_full/nf4
```

Batch 1 is the conservative RTX 2070 setting. SFT batches on a cloud L40S do not determine safe local inference batching. Completed episodes are saved after every batch; rerun the exact same command to resume an interruption. The adapter config/weight hashes and frozen dataset hashes are recorded to prevent resuming with changed inputs. Keep the baseline output directory unchanged.

Outputs: `reports/sft_fire_nf4/RESULTS.md` (metrics and cluster bootstrap 95% CIs), `summary.json`, `COMPARISON.md` (base/SFT percentages and descriptive percentage-point changes), plus per-world episode and metric JSONL files. Comparison validates dataset hashes and task-ID coverage. Confidence intervals for individual scores are not confidence intervals for the change. Attention implementation differs from the original baseline, and precision/attention/batch metadata must accompany comparisons. A completed evaluation, not the local example, establishes measured post-SFT accuracy.
