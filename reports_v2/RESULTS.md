# DriftGuard v2: Base, SFT and active-advantage GRPO

All evaluations use identical approved v2 task IDs, BF16 weights/computation on L40S, greedy decoding, and the same tool/context budgets. Results are not directly comparable to earlier v1/NF4 reports.

Values are percentages with 95% semantic-case cluster-bootstrap confidence intervals (10,000 resamples). Correlated translations remain together. Degenerate intervals do not imply certainty outside this benchmark.

| World | Metric | Base | SFT | SFT+GRPO |
|---|---|---:|---:|---:|
| test_synth | exact_outcome | 0.50 [0.00, 1.25] | 15.00 [10.50, 20.00] | 17.50 [11.00, 24.75] |
| test_synth | stale_catch | 0.00 [0.00, 0.00] | 4.00 [1.39, 7.14] | 0.00 [0.00, 0.00] |
| test_synth | verified_citation_f1 | 0.00 [0.00, 0.00] | 38.27 [33.14, 43.45] | 7.06 [4.96, 9.31] |
| test_synth | format_valid | 69.00 [64.00, 73.75] | 75.00 [70.25, 79.75] | 98.50 [97.25, 99.50] |
| test_synth | required_chain_compliance | 0.00 [0.00, 0.00] | 78.53 [71.55, 85.06] | 7.65 [5.29, 10.17] |
| test_synth | abstention_precision | N/A | 46.00 [21.62, 66.13] | 19.42 [11.21, 28.21] |
| test_synth | abstention_recall | 0.00 [0.00, 0.00] | 38.33 [17.30, 61.11] | 100.00 [100.00, 100.00] |
| test_synth | unplugged_recall | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 100.00 [100.00, 100.00] |
| test_synth | distractor_immunity | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| test_synth | exact_outcome (en) | 0.00 [0.00, 0.00] | 16.00 [9.00, 23.00] | 15.00 [8.00, 22.00] |
| test_synth | exact_outcome (hi) | 0.00 [0.00, 0.00] | 22.00 [14.00, 30.00] | 15.00 [8.00, 22.00] |
| test_synth | exact_outcome (hinglish) | 0.00 [0.00, 0.00] | 11.00 [5.00, 18.00] | 25.00 [17.00, 34.00] |
| test_synth | exact_outcome (te) | 2.00 [0.00, 5.00] | 11.00 [5.00, 17.00] | 15.00 [8.00, 22.00] |
| repo_style | exact_outcome | 0.00 [0.00, 0.00] | 16.00 [7.52, 25.74] | 15.00 [3.09, 30.30] |
| repo_style | stale_catch | 0.00 [0.00, 0.00] | 14.00 [2.27, 28.57] | 0.00 [0.00, 0.00] |
| repo_style | verified_citation_f1 | 0.00 [0.00, 0.00] | 48.90 [39.31, 58.10] | 2.90 [0.00, 6.50] |
| repo_style | format_valid | 74.00 [62.38, 84.31] | 70.00 [61.00, 78.85] | 98.00 [95.00, 100.00] |
| repo_style | required_chain_compliance | 0.00 [0.00, 0.00] | 69.41 [54.43, 83.10] | 1.18 [0.00, 3.95] |
| repo_style | abstention_precision | N/A | 62.50 [0.00, 100.00] | 17.65 [3.80, 34.52] |
| repo_style | abstention_recall | 0.00 [0.00, 0.00] | 33.33 [0.00, 75.00] | 100.00 [100.00, 100.00] |
| repo_style | unplugged_recall | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 100.00 [100.00, 100.00] |
| repo_style | distractor_immunity | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| repo_style | exact_outcome (en) | 0.00 [0.00, 0.00] | 20.00 [4.00, 36.00] | 16.00 [4.00, 32.00] |
| repo_style | exact_outcome (hi) | 0.00 [0.00, 0.00] | 28.00 [12.00, 48.00] | 16.00 [4.00, 32.00] |
| repo_style | exact_outcome (hinglish) | 0.00 [0.00, 0.00] | 16.00 [4.00, 32.00] | 16.00 [4.00, 32.00] |
| repo_style | exact_outcome (te) | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 12.00 [0.00, 24.00] |

## Paired accuracy changes

| World | Comparison | Change, percentage points [95% CI] |
|---|---|---:|
| test_synth | Base -> SFT | +14.50 [+9.75, +19.75] |
| test_synth | SFT -> SFT+GRPO | +2.50 [-4.00, +9.50] |
| repo_style | Base -> SFT | +16.00 [+7.14, +25.25] |
| repo_style | SFT -> SFT+GRPO | -1.00 [-14.00, +14.00] |

## Scope

The OSS-style holdout contains domain-valid constructed fixtures, not verified historical upstream changes. Hindi and Telugu include native and romanized text. Independent native-speaker review is not claimed. Required utility-server calls are enforced in evidence-gated rewards and reported separately from scalar/status accuracy. Active filtering and saturated-kind fallback condition the training distribution; inspect attempted and accepted coverage. These approved holdouts have been reviewed during development, so an untouched confirmation set is needed for stronger generalization claims.
