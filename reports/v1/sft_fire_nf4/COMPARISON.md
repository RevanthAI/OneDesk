# Base versus SFT evaluation

Baseline: `reports/precision_full/nf4`. Current run: `reports/sft_fire_nf4`.

Positive deltas indicate higher scores. Deltas are descriptive percentage-point differences; intervals in RESULTS.md belong to individual runs, not the difference. Check run_config.json and runtime.json for precision, attention and batching differences. These can affect generated outputs.

| World | Metric | Base (%) | SFT (%) | Change (pp) |
|---|---|---:|---:|---:|
| test_synth | exact_outcome | 0.00 | 85.25 | +85.25 |
| test_synth | stale_catch | 0.00 | 87.00 | +87.00 |
| test_synth | verified_citation_f1 | 0.78 | 89.41 | +88.63 |
| test_synth | format_valid | 9.25 | 99.00 | +89.75 |
| test_synth | abstention_precision | N/A | 69.44 | N/A |
| test_synth | abstention_recall | 0.00 | 83.33 | +83.33 |
| test_synth | distractor_immunity | 100.00 | 100.00 | +0.00 |
| test_synth | exact_outcome (en) | 0.00 | 88.00 | +88.00 |
| test_synth | exact_outcome (hi) | 0.00 | 83.00 | +83.00 |
| test_synth | exact_outcome (hinglish) | 0.00 | 85.00 | +85.00 |
| test_synth | exact_outcome (te) | 0.00 | 85.00 | +85.00 |
| repo_style | exact_outcome | 0.00 | 68.00 | +68.00 |
| repo_style | stale_catch | 0.00 | 68.00 | +68.00 |
| repo_style | verified_citation_f1 | 0.00 | 100.00 | +100.00 |
| repo_style | format_valid | 8.00 | 100.00 | +92.00 |
| repo_style | abstention_precision | N/A | N/A | N/A |
| repo_style | abstention_recall | N/A | N/A | N/A |
| repo_style | distractor_immunity | 100.00 | 100.00 | +0.00 |
| repo_style | exact_outcome (en) | 0.00 | 100.00 | +100.00 |
| repo_style | exact_outcome (hi) | 0.00 | 0.00 | +0.00 |
| repo_style | exact_outcome (hinglish) | 0.00 | 100.00 | +100.00 |
| repo_style | exact_outcome (te) | 0.00 | 72.00 | +72.00 |

Constructed OSS-style fixtures are not source-backed real repositories and include documented domain-validity defects. Synthetic translations are correlated within semantic cases.
