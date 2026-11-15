# DriftGuard-MCP v2 experiment report

**Primary finding: the final GRPO policy collapsed toward abstention. Stale-doc catch is 0% on both holdouts; its overall accuracy change versus SFT is not statistically supported.**

The approved Base → one-epoch SFT → active-advantage GRPO experiment completed on Hugging Face L40S. All 19 approved data-folder files remain byte-identical; the 15-artifact SHA-256 manifest verifies. Historical v1 results are excluded.

## Execution and safeguards

Main tests: 58 passed. Independent v2 tests: 15 passed. Required utility-call gates, saturated-kind fallback and the BF16 temperature-order correction were verified before GRPO. See [PREFLIGHT.md](PREFLIGHT.md).

SFT: exactly 240 examples, one epoch, 15 optimizer steps, effective batch 16, 2,560-token budget, zero truncated conversations. Validation contains 80 rows from 20 separate semantic cases.

GRPO smoke: five active updates in 175.5 seconds; 9.10 GiB peak reserved VRAM; unchanged SFT reference. Smoke updates were discarded before the full run.

Full GRPO: 120 + 220 active optimizer updates; four sampled episodes per group; 4,096-token context and 192 tokens per turn. Attempted groups: 808; acceptance: 42.08%; peak reserved VRAM: 12.79 GiB; training wall time: 293.7 minutes.

The first v2 job was stopped at the saved SFT handoff after a probability-scoring precision issue was found before GRPO. The corrected pinned job reused the valid Base evaluation and SFT adapter. Both job records and SCORER_FIX_HANDOFF.json retain provenance.

## Results

See [RESULTS.md](RESULTS.md) for all metrics and paired accuracy changes with 95% semantic-case cluster-bootstrap intervals.

| Holdout | Base exact outcome | SFT exact outcome | SFT+GRPO exact outcome |
|---|---:|---:|---:|
| test_synth | 0.50% [0.00, 1.25] | 15.00% [10.50, 20.00] | 17.50% [11.00, 24.75] |
| repo_style | 0.00% [0.00, 0.00] | 16.00% [7.52, 25.74] | 15.00% [3.09, 30.30] |

## Findings and artifacts

Per-model FAILURE_ANALYSIS.md/JSON contains task-kind/language/subtype breakdowns and actual saved error examples. Counts of wrong status, wrong scalar, invalid format, staging citations and tool errors can overlap. Training rewards are not holdout accuracy.

- [Three-way accuracy plot](comparison.png) and [vector export](comparison.svg).
- [Training curves](grpo_training/training_rollouts.png), [optimization diagnostics](grpo_training/optimization.png), and [sampling analysis](grpo_training/ACTIVE_SAMPLING_ANALYSIS.md).
- [Offline rollout explorer](grpo_training/rollout_explorer.html), raw JSONL logs and TensorBoard events.
- Local adapters: checkpoints_v2/sft_adapter and checkpoints_v2/grpo_adapter. Adapter SHA-256 hashes are in publication_summary.json; pinned Hub revisions are in MODEL_REVISIONS.json.

## Interpretation and limits

The v2 SFT recipe was deliberately compact and differs from the v1 training/data recipe. Score differences across v1 and v2 cannot be attributed to one change. This matched comparison uses BF16 cloud inference throughout; local NF4 deployment may behave differently. OSS-style cases are constructed fixtures, not verified historical upstream changes. Multilingual prompts have no claimed independent native-speaker review. These holdouts were reviewed during development; stronger generalization claims require an untouched confirmation set. Active-group filtering changes the sampled distribution; inspect accepted-kind coverage and skipped attempts. Normal TRL checkpoints retain optimizer/model state, but exact replay of the dynamic sampler mid-stage is not implemented.

Repositories remain private. The release ZIP includes only the v2 allowlist; no public publication was performed. Pricing estimates are not billing records; inspect Hugging Face billing for actual charges.

<!-- V2_REVIEW -->

## Detailed interpretation

See [GRPO_FINDINGS.md](GRPO_FINDINGS.md) for the collapse evidence, validation trajectory, all-wrong skipped groups and unexecuted follow-up proposals. [Failure-mode plot](failure_modes.png) makes the lost evidence use visible alongside formatting gains. Approved DATA_REVIEW.md and REVIEW_SAMPLES.md remain unchanged approval-time snapshots.
