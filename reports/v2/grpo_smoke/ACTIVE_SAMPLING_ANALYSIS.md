# V2 active sampling diagnostics

Skipped zero-variance groups are attempts, not optimizer updates. Training outcomes/rewards are not held-out accuracy.

| Stage | Attempted groups | Accepted active groups | Skipped groups | Acceptance |
|---|---:|---:|---:|---:|
| stage1 | 5 | 5 | 0 | 100.00% |

Uniform rewards do not establish mastery: skipped groups are divided into all-outcomes-correct, all-outcomes-wrong, and mixed outcomes with equal rewards in the JSON report. Correct scalar/status outcomes can still be unsupported under the chain gate. Accepted groups are selected training samples, not an unbiased estimate of model accuracy.

Temperature and kind-fallback counts, accepted kind coverage and the final saturated-kind set are retained in `ACTIVE_SAMPLING_ANALYSIS.json`. See per-stage raw rollouts for exact model tokens, tool results and rewards.
