# DriftGuard-MCP: NF4 and FP16 findings

## Summary

The full summary printed before the traceback was the completed batch-1 NF4 evaluation. FP16 saved 90 synthetic episodes and then failed from CUDA memory exhaustion; it did not finish the 400-question synthetic holdout or start its OSS stage. A completed counter means an attempted episode was saved, not that the task was solved.

I subsequently completed all 100 frozen OSS-style questions in FP16, and reran the same 100 in NF4 with matching batch size, prompts, decoding, and attention settings. FP16 produced more valid final answers on that cohort (18% versus 8%), but strict outcome accuracy stayed at 0% in both. Neither precision returned a correct status/value pair on these 100 questions even when schema requirements were ignored. This is evidence that formatting and quantization alone do not explain the failures under this benchmark. A fixture-domain defect also affects the apparent format gain; excluding invalid percentage items reduces that observed gap to 2.41 percentage points (see below).

## Paired results

| Cohort / metric | NF4 | FP16 | Difference, percentage points [95% paired CI] |
|---|---:|---:|---:|
| Synthetic, first 90 only: exact_outcome | 0.00% | 0.00% | +0.00 [+0.00, +0.00] |
| Synthetic, first 90 only: format_valid | 18.89% | 16.67% | -2.22 [-13.64, +8.70] |
| Synthetic, first 90 only: raw_value | 18.89% | 13.33% | -5.56 [-13.04, +2.22] |
| Synthetic, first 90 only: raw_status | 32.22% | 15.56% | -16.67 [-27.78, -5.68] |
| Synthetic, first 90 only: raw_status_value | 16.67% | 8.89% | -7.78 [-15.12, -1.09] |
| Synthetic, first 90 only: verified_citation_f1 | 2.96% | 3.52% | +0.56 [-2.41, +3.60] |
| OSS-style, all 100: exact_outcome | 0.00% | 0.00% | +0.00 [+0.00, +0.00] |
| OSS-style, all 100: format_valid | 8.00% | 18.00% | +10.00 [+0.00, +20.00] |
| OSS-style, all 100: raw_value | 11.00% | 14.00% | +3.00 [-3.09, +9.28] |
| OSS-style, all 100: raw_status | 37.00% | 51.00% | +14.00 [+5.88, +23.08] |
| OSS-style, all 100: raw_status_value | 0.00% | 0.00% | +0.00 [+0.00, +0.00] |
| OSS-style, all 100: verified_citation_f1 | 0.00% | 2.00% | +2.00 [+0.00, +4.17] |

CIs use 10,000 semantic-case cluster bootstrap resamples, preserving translations together. The OSS format-rate difference includes zero at its lower endpoint; this is an observed improvement, not strong evidence of a universal FP16 advantage. All-zero bootstrap intervals are degenerate and do not establish zero population success probability. The synthetic prefix has 80 consistent and 10 incident questions, with no conflict or abstention cases, so it cannot characterize full FP16 drift or abstention performance.

## Where the model struggles

1. **Evidence collection:** all 100 FP16 OSS episodes lacked the complete required evidence pair. It frequently stopped after one source, so the fresh value was not reconciled with the old runbook. NF4 showed the same gap.
2. **Answer schema:** FP16 had 82 malformed OSS final outputs; 41 parseable final JSON objects had missing or extra fields. Typical failures were missing `stale_source`, decorated values such as `"circuit_breaker_pct = 10023"`, and invalid citation structures. The 41 count is conditional on parseable JSON, not all malformed output.
3. **Status/value integration:** FP16 matched the raw expected status on 51/100 and the raw scalar value on 14/100, but on different questions: joint status/value correctness was 0/100. Better formatting alone would not convert these into successful outcomes.
4. **Citations:** 48 FP16 OSS episodes with parseable final JSON cited IDs that were never retrieved. Tool names, SQL descriptions, and query strings were often used as citations. This count was 33 in the matched NF4 arm; improvements were not uniform across metrics.
5. **Search phrasing:** 45 FP16 OSS episodes had an empty search result. The local router uses conjunctive matching of entity/parameter tokens; natural-language filler therefore creates an avoidable benchmark interaction. These results measure this constrained router as well as the model.
6. **Synthetic incident SQL:** the saved FP16 prefix includes SQL/tool errors and incomplete chains, but only ten incident questions. No full FP16 incident, conflict, or abstention result is claimed.

## Dataset flaw found during review

I generated overly schematic numeric defaults for the OSS-style fixtures. Five of the 30 constructed cases use `circuit_breaker_pct` above 100 (for example 10011), affecting 17/100 rendered questions. These are unrealistic percentages and should have been rejected by a domain-validity check. This is a benchmark defect, not a model failure. The data were left frozen to preserve the audit trail.

As an explicitly retrospective sensitivity check, excluding just those 17 percentage items leaves 83 questions; strict outcome accuracy remains 0/83 in both precisions. Format validity becomes 4/83 (4.82%) in NF4 versus 6/83 (7.23%) in FP16: the observed format gap shrinks from 10 percentage points on all items to 2.41 points. Much of the original aggregate format difference therefore occurred on the unrealistic percentage fixtures. Raw value correctness on the remaining items is 13.25% NF4 versus 16.87% FP16. These descriptive, post-hoc exclusions do not repair other realism limitations and are not a replacement for the original 100-item result. Other defaults are schematic, and no fixture is a verified real PR/document snapshot. A new, separately versioned, domain-valid and source-backed holdout is needed before claiming real-repository transfer.

## Memory failure and recovery

The original FP16 job requested a 1.15-GiB attention allocation with only about 571 MiB available. The 6-GiB parameter-placement budget I supplied did not cap total runtime memory or reserve enough space for this longer attention state. The OOM is a hardware/runtime failure; its unfinished task was not scored as a wrong model answer.

A lower 4.5-GiB placement pilot ran at roughly two tokens/second due to offload and was preserved separately. A direct RTX 2070 kernel test then showed that native GQA could not use efficient SDPA, while explicitly repeated KV heads could. The installed Transformers helper was given a version-specific `--sdpa-expand-kv` compatibility option. Both final OSS arms used it. This allows efficient kernels where supported; it does not force them for every shape, and GPU kernel selection may change floating-point outputs. [PyTorch 2.8 documents GQA support and kernel numerical differences](https://docs.pytorch.org/docs/2.8/generated/torch.nn.functional.scaled_dot_product_attention.html).

The numerical equivalence test and attention-setting mismatch guard pass. The two original attention settings were not mixed in the final OSS comparison. Completing these 100 short OSS cases does not prove every long synthetic trajectory now fits.

| Final OSS runtime | NF4 | FP16 |
|---|---:|---:|
| peak_vram_allocated_gib | 2.53 | 5.98 |
| generated_tokens_per_second | 13.41 | 6.23 |
| generation_seconds | 883.40 | 1946.70 |

FP16 used CPU weight offload while NF4 was GPU-resident. These throughput numbers are deployment measurements, not a precision-only speed comparison.

## Recommended next work

First create a new version of the OSS holdout with real or clearly constructed, domain-valid defaults and recorded provenance; preserve this flawed version as an audit artifact. Document realistic search behavior and query schemas in a separately versioned protocol. Then use oracle SFT to teach the exact tool/final contract, followed by separate evaluation of value/status correctness, verified citations, and cross-source verification. Only after protocol reliability improves can a before/after experiment cleanly test the proposed stale-doc GRPO benefit. No fine-tuning was run here.

## Artifacts and reproduction

- Partial synthetic paired report: `partial90_findings/FINDINGS.md` (90 questions only).
- Complete paired OSS report and examples: `oss_findings/FINDINGS.md`.
- Original failed FP16 records: `fp16/` (90 saved episodes and OOM record).
- Complete FP16 OSS traces/runtime: `fp16_oss_efficient/`.
- Complete matched NF4 OSS traces/runtime: `nf4_oss_efficient/`.
- Machine-readable consolidated findings: `PRECISION_FINDINGS.json`.
- Reproduce completed OSS run: `bash scripts/run_oss_precision_comparison.sh` from project root. Matching completed runs are rescored without generating new answers.

Verification: 28 tests passed; frozen data checksums were verified; both new OSS runs contain exactly 100 unique expected task IDs and matching frozen prompts. Missing synthetic FP16 questions remain untested, not failed or imputed.
