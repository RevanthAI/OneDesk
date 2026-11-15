# GRPO recorded experiment diagnostics

Run status: `pilot_complete`.

Training rollouts are sampled at temperature 0.8; validation is greedy. Stage task mixtures differ. Their average rewards are not directly comparable learning curves.

| Stage | Updates/groups | Sampled episodes | Mean reward | Sampled accuracy | Zero-variance groups |
|---|---:|---:|---:|---:|---:|
| stage1 | 20 | 80 | 0.9768 | 81.25% | 70.00% |
| stage2 | 40 | 160 | 1.1754 | 89.38% | 62.50% |

Zero-variance groups can reflect either an already successful policy or failure to explore a correct action. The breakdown is retained separately in `analysis.json`; identical rewards alone do not establish entropy collapse.

## Paired training-world validation

SFT: 100.00%; GRPO: 100.00%. Change: +0.00 percentage points; 95% paired semantic-case bootstrap interval [+0.00, +0.00] points (10,000 resamples).

Paired changes: {'unchanged': 40}. There are only 10 cases / 40 correlated translations. This does not replace the full frozen holdout evaluation.

Evidence: `analysis.json`, `rollout_metrics.csv`, per-stage optimizer/rollout logs, model-generated tokens and masks, and before/after validation traces. No oracle actions were substituted into training rollouts.
