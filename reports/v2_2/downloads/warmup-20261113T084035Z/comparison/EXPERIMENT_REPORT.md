# DriftGuard: protocol warmup and positive-anchor GRPO

All seven checkpoints use identical frozen data_v2 cohorts, the same pinned Tiny Aya Fire base, BF16 greedy inference, batch 16 with OOM splitting, context 4096, 192 new tokens per turn and six tool calls. Original evaluations and the full four-epoch adapter remain unchanged; missing base validation and original stage-one holdouts were evaluated in this follow-up.

Percentages show 95% semantic-case cluster-bootstrap intervals (10,000 resamples); translations remain grouped. These are reviewed synthetic and constructed OSS-style fixtures, not independently verified upstream drift cases.

## Findings at a glance

- All **80 active updates** completed; validation selected **update 40**. Stage 2 did not improve that checkpoint, and no abstention collapse guard fired.
- Overall point estimates: warmup **72.50% / 64.00%** → GRPO **75.75% / 71.00%** (synthetic / OSS-style). Paired 95% intervals for both gains include zero.
- Full four-epoch SFT remains higher on overall holdout point estimates (**77.25% / 76.00%**). GRPO has higher strict stale-document catch rates (**79.00% / 62.00%**, versus **63.50% / 52.00%** for full SFT), with paired intervals excluding zero for those comparisons.
- Required-server chain compliance regressed to **86.47% / 74.12%** from warmup **93.82% / 90.59%**. Correct scalar/status outputs do not necessarily satisfy all evidence/chain requirements.
- Full-run active acceptance was **23.39%** (80/342), below the initial smoke's **55.56%** but above the historical G4 pilot's **8.33%**. Sampling settings differ, so this is not an isolated entropy ablation.

See [FINDINGS.md](FINDINGS.md) for paired trade-offs, failure examples, limitations and local inference instructions.

## Complete progression

| Checkpoint | Validation exact outcome | Synthetic exact outcome | OSS-style exact outcome |
|---|---:|---:|---:|
| Base (Tiny Aya Fire) | 1.25 [0.00, 3.75] | 0.50 [0.00, 1.25] | 0.00 [0.00, 0.00] |
| v2 SFT (15 steps) | 22.50 [7.50, 40.00] | 15.00 [10.50, 20.00] | 16.00 [7.52, 25.74] |
| v2 GRPO Stage 1 (120 updates) | 43.75 [23.75, 62.50] | 26.25 [18.75, 34.50] | 26.00 [11.00, 43.14] |
| v2 GRPO Stage 2 (collapsed) | 26.25 [8.72, 46.25] | 17.50 [11.00, 24.75] | 15.00 [3.09, 30.30] |
| v2.1 SFT Warmup | 67.50 [48.75, 85.00] | 72.50 [65.25, 79.25] | 64.00 [46.53, 80.39] |
| v2.1 GRPO Anti-Collapse | 80.00 [63.75, 93.75] | 75.75 [68.50, 82.50] | 71.00 [55.45, 84.31] |
| v2.1 SFT Full 4-Epoch (ablation) | 73.75 [56.25, 90.00] | 77.25 [70.00, 84.00] | 76.00 [61.39, 88.89] |

## Training and validation selection

Warmup ran 60 optimizer steps / 480 exposures, batch 8, LR 1.5e-4, zero truncation at sequence length 2560. The first 60 steps of the original 120-step cosine schedule retain the original six-step LR warmup; stopping at 60 does not force LR to zero. Candidates 45/60 were selected on validation alone (>=90% format validity, <=40% abstention; prefer the requested 55–68% accuracy range). Selected step: 60.

GRPO requested 40+40 active updates; completed 80; selected cumulative step 40. Status: complete; early-stop reason: None. G=6, temperatures 1.0/1.15, beta .04, LR 5e-6, frozen selected warmup KL reference. Validation every 20 updates; predicted abstention >40% stops training and restores the best safe validation checkpoint.

If GRPO selects step zero, its adapter is unchanged warmup SFT and there is no demonstrated RL gain. The final un-restored policy is retained separately.

## Five-update operational smoke gate

Accepted 5/9 groups (55.56% versus historical 6/72 = 8.33%); finite gradients: True; passed: True; peak reserved VRAM 9.86 GiB.

## Metrics by cohort

| World | Metric | Base (Tiny Aya Fire) | v2 SFT (15 steps) | v2 GRPO Stage 1 (120 updates) | v2 GRPO Stage 2 (collapsed) | v2.1 SFT Warmup | v2.1 GRPO Anti-Collapse | v2.1 SFT Full 4-Epoch (ablation) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| validation | exact_outcome | 1.25 [0.00, 3.75] | 22.50 [7.50, 40.00] | 43.75 [23.75, 62.50] | 26.25 [8.72, 46.25] | 67.50 [48.75, 85.00] | 80.00 [63.75, 93.75] | 73.75 [56.25, 90.00] |
| validation | stale_catch | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 45.00 [0.00, 100.00] | 70.00 [37.50, 100.00] | 30.00 [0.00, 67.86] |
| validation | verified_citation_f1 | 0.00 [0.00, 0.00] | 54.50 [41.37, 67.41] | 53.67 [37.02, 69.65] | 5.50 [0.00, 11.72] | 95.33 [91.07, 98.93] | 93.94 [87.12, 99.55] | 96.33 [92.14, 100.00] |
| validation | format_valid | 47.50 [36.25, 57.50] | 78.75 [70.00, 87.50] | 98.75 [96.25, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 97.50 [92.50, 100.00] |
| validation | required_chain_compliance | 0.00 [0.00, 0.00] | 71.67 [51.56, 89.29] | 36.67 [18.18, 56.25] | 3.33 [0.00, 8.33] | 95.00 [83.93, 100.00] | 90.00 [75.00, 100.00] | 100.00 [100.00, 100.00] |
| validation | abstention_precision | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 64.00 [23.53, 100.00] | 33.33 [8.00, 56.14] | 100.00 [100.00, 100.00] | 95.00 [75.73, 100.00] | 100.00 [100.00, 100.00] |
| validation | abstention_recall | 5.00 [0.00, 16.67] | 55.00 [0.00, 100.00] | 80.00 [50.00, 100.00] | 100.00 [100.00, 100.00] | 95.00 [83.33, 100.00] | 95.00 [83.33, 100.00] | 90.00 [66.67, 100.00] |
| validation | unplugged_recall | 12.50 [0.00, 25.00] | 0.00 [0.00, 0.00] | 50.00 [25.00, 75.00] | 100.00 [100.00, 100.00] | 87.50 [75.00, 100.00] | 87.50 [75.00, 100.00] | 100.00 [100.00, 100.00] |
| validation | distractor_immunity | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| validation | exact_outcome (en) | 5.00 [0.00, 15.00] | 25.00 [5.00, 45.00] | 55.00 [35.00, 75.00] | 30.00 [10.00, 50.00] | 75.00 [55.00, 90.00] | 85.00 [70.00, 100.00] | 80.00 [60.00, 95.00] |
| validation | exact_outcome (hi) | 0.00 [0.00, 0.00] | 25.00 [5.00, 45.00] | 40.00 [20.00, 60.00] | 25.00 [5.00, 45.00] | 65.00 [45.00, 85.00] | 80.00 [60.00, 95.00] | 70.00 [50.00, 90.00] |
| validation | exact_outcome (hinglish) | 0.00 [0.00, 0.00] | 25.00 [5.00, 45.00] | 40.00 [20.00, 60.00] | 25.00 [5.00, 45.00] | 60.00 [40.00, 80.00] | 80.00 [60.00, 95.00] | 75.00 [55.00, 90.00] |
| validation | exact_outcome (te) | 0.00 [0.00, 0.00] | 15.00 [0.00, 30.00] | 40.00 [20.00, 60.00] | 25.00 [5.00, 45.00] | 70.00 [50.00, 90.00] | 75.00 [55.00, 95.00] | 70.00 [50.00, 90.00] |
| test_synth | exact_outcome | 0.50 [0.00, 1.25] | 15.00 [10.50, 20.00] | 26.25 [18.75, 34.50] | 17.50 [11.00, 24.75] | 72.50 [65.25, 79.25] | 75.75 [68.50, 82.50] | 77.25 [70.00, 84.00] |
| test_synth | stale_catch | 0.00 [0.00, 0.00] | 4.00 [1.39, 7.14] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 74.00 [63.30, 83.96] | 79.00 [69.20, 87.74] | 63.50 [50.56, 75.52] |
| test_synth | verified_citation_f1 | 0.00 [0.00, 0.00] | 38.27 [33.14, 43.45] | 58.37 [52.46, 64.36] | 7.06 [4.96, 9.31] | 88.82 [85.37, 92.11] | 88.29 [83.95, 92.18] | 92.56 [89.54, 95.39] |
| test_synth | format_valid | 69.00 [64.00, 73.75] | 75.00 [70.25, 79.75] | 99.00 [98.00, 99.75] | 98.50 [97.25, 99.50] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| test_synth | required_chain_compliance | 0.00 [0.00, 0.00] | 78.53 [71.55, 85.06] | 39.71 [31.59, 47.99] | 7.65 [5.29, 10.17] | 93.82 [90.74, 96.63] | 86.47 [80.85, 91.57] | 97.35 [95.37, 99.07] |
| test_synth | abstention_precision | N/A | 46.00 [21.62, 66.13] | 44.12 [22.41, 64.15] | 19.42 [11.21, 28.21] | 69.09 [48.65, 83.14] | 66.67 [44.68, 83.08] | 96.08 [86.36, 100.00] |
| test_synth | abstention_recall | 0.00 [0.00, 0.00] | 38.33 [17.30, 61.11] | 50.00 [26.92, 73.33] | 100.00 [100.00, 100.00] | 63.33 [41.07, 84.62] | 63.33 [41.67, 84.62] | 81.67 [70.45, 92.31] |
| test_synth | unplugged_recall | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 3.57 [0.00, 12.50] | 100.00 [100.00, 100.00] | 21.43 [5.00, 37.50] | 21.43 [5.00, 39.29] | 60.71 [50.00, 70.83] |
| test_synth | distractor_immunity | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| test_synth | exact_outcome (en) | 0.00 [0.00, 0.00] | 16.00 [9.00, 23.00] | 29.00 [20.00, 38.00] | 15.00 [8.00, 22.00] | 77.00 [68.00, 85.00] | 77.00 [68.00, 85.00] | 77.00 [68.00, 85.00] |
| test_synth | exact_outcome (hi) | 0.00 [0.00, 0.00] | 22.00 [14.00, 30.00] | 29.00 [20.00, 38.00] | 15.00 [8.00, 22.00] | 76.00 [67.00, 84.00] | 83.00 [75.00, 90.00] | 82.00 [74.00, 89.00] |
| test_synth | exact_outcome (hinglish) | 0.00 [0.00, 0.00] | 11.00 [5.00, 18.00] | 23.00 [15.00, 32.00] | 25.00 [17.00, 34.00] | 66.00 [57.00, 75.00] | 69.00 [60.00, 78.00] | 79.00 [71.00, 87.00] |
| test_synth | exact_outcome (te) | 2.00 [0.00, 5.00] | 11.00 [5.00, 17.00] | 24.00 [16.00, 33.00] | 15.00 [8.00, 22.00] | 71.00 [62.00, 80.00] | 74.00 [65.00, 82.00] | 71.00 [62.00, 80.00] |
| repo_style | exact_outcome | 0.00 [0.00, 0.00] | 16.00 [7.52, 25.74] | 26.00 [11.00, 43.14] | 15.00 [3.09, 30.30] | 64.00 [46.53, 80.39] | 71.00 [55.45, 84.31] | 76.00 [61.39, 88.89] |
| repo_style | stale_catch | 0.00 [0.00, 0.00] | 14.00 [2.27, 28.57] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 56.00 [28.21, 82.05] | 62.00 [37.10, 83.87] | 52.00 [25.00, 77.08] |
| repo_style | verified_citation_f1 | 0.00 [0.00, 0.00] | 48.90 [39.31, 58.10] | 54.32 [41.77, 66.59] | 2.90 [0.00, 6.50] | 86.00 [75.46, 94.44] | 84.59 [76.40, 91.67] | 95.65 [92.30, 98.46] |
| repo_style | format_valid | 74.00 [62.38, 84.31] | 70.00 [61.00, 78.85] | 100.00 [100.00, 100.00] | 98.00 [95.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| repo_style | required_chain_compliance | 0.00 [0.00, 0.00] | 69.41 [54.43, 83.10] | 34.12 [16.28, 53.33] | 1.18 [0.00, 3.95] | 90.59 [79.49, 97.85] | 74.12 [58.58, 88.04] | 98.82 [96.20, 100.00] |
| repo_style | abstention_precision | N/A | 62.50 [0.00, 100.00] | 43.75 [0.00, 87.50] | 17.65 [3.80, 34.52] | 65.00 [16.67, 94.12] | 64.71 [16.67, 90.25] | 100.00 [100.00, 100.00] |
| repo_style | abstention_recall | 0.00 [0.00, 0.00] | 33.33 [0.00, 75.00] | 46.67 [0.00, 100.00] | 100.00 [100.00, 100.00] | 86.67 [33.33, 100.00] | 73.33 [33.33, 100.00] | 80.00 [50.00, 100.00] |
| repo_style | unplugged_recall | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 100.00 [100.00, 100.00] | 71.43 [33.33, 100.00] | 42.86 [33.33, 50.00] | 57.14 [50.00, 66.67] |
| repo_style | distractor_immunity | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| repo_style | exact_outcome (en) | 0.00 [0.00, 0.00] | 20.00 [4.00, 36.00] | 32.00 [16.00, 52.00] | 16.00 [4.00, 32.00] | 64.00 [44.00, 84.00] | 72.00 [52.00, 88.00] | 76.00 [60.00, 92.00] |
| repo_style | exact_outcome (hi) | 0.00 [0.00, 0.00] | 28.00 [12.00, 48.00] | 28.00 [12.00, 48.00] | 16.00 [4.00, 32.00] | 64.00 [44.00, 80.00] | 68.00 [48.00, 84.00] | 76.00 [60.00, 92.00] |
| repo_style | exact_outcome (hinglish) | 0.00 [0.00, 0.00] | 16.00 [4.00, 32.00] | 24.00 [8.00, 40.00] | 16.00 [4.00, 32.00] | 64.00 [44.00, 84.00] | 72.00 [52.00, 88.00] | 76.00 [60.00, 92.00] |
| repo_style | exact_outcome (te) | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 20.00 [4.00, 36.00] | 12.00 [0.00, 24.00] | 64.00 [44.00, 84.00] | 72.00 [52.00, 88.00] | 76.00 [60.00, 92.00] |

## Paired accuracy changes

| World | Comparison | Percentage points [95% CI] |
|---|---|---:|
| validation | v2 SFT (15 steps) -> v2 GRPO Stage 1 (120 updates) | +21.25 [+6.25, +38.75] |
| validation | v2 GRPO Stage 1 (120 updates) -> v2 GRPO Stage 2 (collapsed) | -17.50 [-37.50, +1.25] |
| validation | v2.1 SFT Warmup -> v2.1 GRPO Anti-Collapse | +12.50 [+0.00, +26.25] |
| validation | v2.1 SFT Warmup -> v2.1 SFT Full 4-Epoch (ablation) | +6.25 [-8.75, +22.50] |
| test_synth | v2 SFT (15 steps) -> v2 GRPO Stage 1 (120 updates) | +11.25 [+5.00, +18.00] |
| test_synth | v2 GRPO Stage 1 (120 updates) -> v2 GRPO Stage 2 (collapsed) | -8.75 [-17.25, -0.75] |
| test_synth | v2.1 SFT Warmup -> v2.1 GRPO Anti-Collapse | +3.25 [-2.50, +9.00] |
| test_synth | v2.1 SFT Warmup -> v2.1 SFT Full 4-Epoch (ablation) | +4.75 [-1.75, +11.00] |
| repo_style | v2 SFT (15 steps) -> v2 GRPO Stage 1 (120 updates) | +10.00 [-5.83, +27.45] |
| repo_style | v2 GRPO Stage 1 (120 updates) -> v2 GRPO Stage 2 (collapsed) | -11.00 [-29.70, +7.14] |
| repo_style | v2.1 SFT Warmup -> v2.1 GRPO Anti-Collapse | +7.00 [-5.00, +20.00] |
| repo_style | v2.1 SFT Warmup -> v2.1 SFT Full 4-Epoch (ablation) | +12.00 [-3.03, +28.00] |

## Interpretation and limits

The four-epoch model is a behavioral-cloning reference, not a mathematical accuracy ceiling. Zero reward variance does not prove identical text or collapsed token entropy: multiple different traces can earn the same reward, including uniformly wrong traces. New logs record unique assistant sequences and accepted-group sampled-token surprisal (not full distribution entropy). The historical pilot and new smoke test differ in SFT budget, group size and temperatures, so any acceptance improvement cannot be attributed solely to fewer SFT steps.

The seven-slot answerable to one-slot abstention rotation, dense evidence bridge, required utility chain, and nonzero-variance/positive-anchor rules remain enforced. All three reward variants and skipped attempts are retained. Skipped attempts do not count as optimizer updates. These are selected training samples, not unbiased performance estimates.

Selection and exploratory comparisons reuse the same small validation set and reviewed holdouts. Results are not a fresh confirmation or a compute-matched causal ablation. We report actual scores even outside the preferred warmup accuracy band and retain old collapse findings.

## Task-kind exact outcome breakdown

Percentages and 95% semantic-case bootstrap intervals; no additional model selection.

| Cohort / kind | Base | v2 SFT15 | v2 GRPO Stage1 | v2 collapsed | SFT warmup | GRPO best | SFT full120 |
|---|---:|---:|---:|---:|---:|---:|---:|
| validation / conflict | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 65.00 [25.00, 100.00] | 70.00 [45.00, 95.00] | 45.00 [5.00, 85.00] |
| validation / incident | 0.00 [0.00, 0.00] | 25.00 [0.00, 65.00] | 20.00 [0.00, 60.00] | 0.00 [0.00, 0.00] | 80.00 [40.00, 100.00] | 80.00 [40.00, 100.00] | 100.00 [100.00, 100.00] |
| validation / consistent | 0.00 [0.00, 0.00] | 10.00 [0.00, 30.00] | 75.00 [55.00, 95.00] | 5.00 [0.00, 15.00] | 30.00 [5.00, 55.00] | 75.00 [35.00, 100.00] | 60.00 [30.00, 90.00] |
| validation / abstain | 5.00 [0.00, 15.00] | 55.00 [15.00, 95.00] | 80.00 [50.00, 100.00] | 100.00 [100.00, 100.00] | 95.00 [85.00, 100.00] | 95.00 [85.00, 100.00] | 90.00 [70.00, 100.00] |
| test_synth / conflict | 1.00 [0.00, 2.50] | 7.00 [4.00, 10.50] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 87.50 [79.50, 94.00] | 81.00 [71.50, 89.50] | 75.00 [63.00, 86.00] |
| test_synth / incident | 0.00 [0.00, 0.00] | 13.33 [5.00, 23.33] | 10.00 [3.33, 18.33] | 0.00 [0.00, 0.00] | 75.00 [63.33, 86.67] | 73.33 [58.33, 86.67] | 85.00 [76.67, 91.67] |
| test_synth / consistent | 0.00 [0.00, 0.00] | 18.75 [8.75, 28.75] | 86.25 [78.75, 93.75] | 12.50 [7.50, 17.50] | 40.00 [22.50, 57.50] | 73.75 [55.00, 90.00] | 73.75 [56.25, 88.75] |
| test_synth / abstain | 0.00 [0.00, 0.00] | 38.33 [16.67, 60.00] | 50.00 [26.67, 73.33] | 100.00 [100.00, 100.00] | 63.33 [41.67, 83.33] | 63.33 [41.67, 83.33] | 81.67 [70.00, 91.67] |
| repo_style / conflict | 0.00 [0.00, 0.00] | 14.00 [2.04, 27.45] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 72.00 [47.06, 93.88] | 74.00 [51.02, 92.31] | 66.00 [40.82, 88.01] |
| repo_style / incident | 0.00 [0.00, 0.00] | 13.33 [0.00, 28.57] | 6.67 [0.00, 18.75] | 0.00 [0.00, 0.00] | 60.00 [18.75, 92.31] | 53.33 [18.75, 75.00] | 93.33 [81.25, 100.00] |
| repo_style / consistent | 0.00 [0.00, 0.00] | 10.00 [0.00, 20.00] | 90.00 [70.00, 100.00] | 0.00 [0.00, 0.00] | 30.00 [0.00, 70.00] | 75.00 [35.00, 100.00] | 85.00 [65.00, 100.00] |
| repo_style / abstain | 0.00 [0.00, 0.00] | 33.33 [0.00, 62.50] | 46.67 [0.00, 87.50] | 100.00 [100.00, 100.00] | 86.67 [53.85, 100.00] | 73.33 [42.86, 100.00] | 80.00 [57.14, 100.00] |

## Warmup validation checkpoints

| Update | Epochs | Exact outcome [95% CI] | Format valid | Predicted abstention | Selected |
|---|---:|---:|---:|---:|---|
| 30 | 1.0 | 52.50 [31.25, 72.50] | 100.00% | 15.00% | False |
| 45 | 1.5 | 58.75 [38.75, 77.50] | 100.00% | 21.25% | False |
| 60 | 2.0 | 67.50 [48.75, 85.00] | 100.00% | 23.75% | True |

## Historical diversity check

Of the old pilot’s 66 zero-variance groups, 62 had identical assistant-token sequences and four had multiple distinct sequences. This is evidence about sampled diversity, not a measurement of full next-token distribution entropy. See HISTORICAL_DIVERSITY_CHECK.json.

## GRPO validation and selection

| Cumulative update | Exact outcome [95% CI] | Predicted abstention | Safe | Selected final |
|---|---:|---:|---|---|
| 20 | 73.75 [56.25, 90.00] | 26.25% | True | False |
| 40 | 80.00 [63.75, 93.75] | 25.00% | True | True |
| 60 | 76.25 [58.75, 91.25] | 23.75% | True | False |
| 80 | 78.75 [58.75, 95.00] | 23.75% | True | False |

## Execution continuity

Preparation and Stage 1 ran in the first allocation; Stage 2 continued in a second capped L40S allocation. Each had a three-hour timeout. The completed SFT, diagnostics and baseline evaluations were reused unchanged. The first allocation was canceled after its safe 40-update boundary was saved. A preliminary Stage-2 update in that allocation was discarded; the main journal records the retained Stage-1 prefix plus the actually completed Stage-2 updates (counts are reported above). This was a resource handoff, with no hyperparameter or dataset change.

Source run: `warmup-20261113T055708Z`, immutable revision `c28a459859bcdeeaebdfe3695ec68a9d17478ad6`. Stage-1 policy SHA-256: `b286392a2d979af730b6c9fcd1c2a14369a2f859bcc691526478d0e8220a2f07`. The Stage-2 optimizer was fresh by the original two-stage recipe, and the KL reference remained the same selected warmup adapter. Source validation selection and all Stage-1 logs were retained. The first restarted Stage-2 group reproduced the original partial group’s reward, outcome rate, sampled-token count and sampled-token surprisal.

## Metric and optimization interpretation

Exact outcome checks normalized value plus expected status. Citation F1 and required-server chain compliance are separate metrics. Chain compliance measures required server calls; it is not a formal proof that a final calculation was causally derived from each tool result.

With one optimizer iteration per newly sampled group, the mean-centered policy surrogate can have a scalar value near zero at the on-policy ratio while still producing nonzero gradients. The loss curve must be read alongside gradient norms, KL, parameter changes and validation accuracy. It is not a quality score.

## Recorded failure analysis and visualizations

- [Warmup failure analysis](../sft_evaluation/FAILURE_ANALYSIS.md)
- [GRPO failure analysis](../grpo_evaluation/FAILURE_ANALYSIS.md)
- [Original v2 Stage-1 failure analysis](../stage1_evaluation/FAILURE_ANALYSIS.md)
- [Sampling acceptance and sequence diversity](sampling_diversity.png)
- [Validation accuracy and abstention](validation_progress.png)
- [Training and optimizer diagnostics](../grpo_training/dashboard.html)
- [Filterable recorded rollout traces](../grpo_training/rollout_explorer.html)

## Full-run sampling support

Accepted 80/342 attempted groups (23.39%). Rejected 260 zero-variance and 3 all-non-positive answerable groups (these categories may overlap). Accepted groups: 68 mixed outcome, 7 all-correct outcome with process variation, 5 all-wrong outcome with positive evidence-retrieval support; 9 contained formatting errors. Positive evidence anchors do not require a fully correct answer. These are training sample statistics, not held-out accuracy.
