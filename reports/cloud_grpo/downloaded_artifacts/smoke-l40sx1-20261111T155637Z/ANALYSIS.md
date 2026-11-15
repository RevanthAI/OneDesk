# GRPO recorded experiment diagnostics

Training rollouts are sampled at temperature 0.8; validation is greedy. Stage task mixtures differ. Their average rewards are not directly comparable learning curves.

| Stage | Updates/groups | Sampled episodes | Mean reward | Sampled accuracy | Zero-variance groups |
|---|---:|---:|---:|---:|---:|
| stage1 | 5 | 20 | 0.9850 | 85.00% | 40.00% |

Evidence: `analysis.json`, `rollout_metrics.csv`, per-stage optimizer/rollout logs, model-generated tokens and masks, and before/after validation traces. No oracle actions were substituted into training rollouts.
