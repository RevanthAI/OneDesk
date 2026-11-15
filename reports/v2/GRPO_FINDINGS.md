# V2 GRPO findings: abstention collapse

The complete 340-update experiment ran successfully, but the final policy failed the intended drift-resolution objective. Synthetic stale catch fell from 4% after SFT to 0%; OSS-style stale catch fell from 14% to 0%. Final GRPO solved zero conflict and zero incident tasks in either holdout. This is a negative result, not a successful drift-detection model.

## Outcomes and uncertainty

| World | SFT accuracy | Final GRPO accuracy | Paired change, pp [95% CI] |
|---|---:|---:|---:|
| test_synth | 15.00% | 17.50% | +2.50 [-4.00, +9.50] |
| repo_style | 16.00% | 15.00% | -1.00 [-14.00, +14.00] |

Both paired intervals include zero. The apparent 2.5-point synthetic accuracy rise does not establish an improvement. On the OSS-style holdout, every correct final answer was an abstention.

## Measured failure pattern

| World | Predicted abstain / all queries | Required abstain | Conflict correct | Incident correct |
|---|---:|---:|---:|
| test_synth | 309/400 | 60/400 | 0/200 | 0/60 |
| repo_style | 85/100 | 15/100 | 0/50 | 0/15 |

Synthetic final-format validity rose from 75% to 98.5%, while required-chain compliance fell from 78.53% to 7.65% and verified-citation F1 fell from 38.27% to 7.06%. OSS-style chain compliance fell from 69.41% to 1.18%. Better formatting and perfect abstention recall masked severe false abstention and loss of evidence use.

## Validation trajectory

| Checkpoint | Validation accuracy |
|---|---:|
| SFT | 22.50% |
| GRPO stage 1, 120 updates | 43.75% |
| GRPO stage 2, 340 cumulative updates | 26.25% |

Validation has only 20 independent semantic cases. Its paired changes and intervals are retained in GRPO_FINDINGS.json. Stage one is selected as a candidate by validation alone; its holdout performance was not measured. The requested three-way table remains the final 340-update adapter, with no checkpoint substitution.

## Sampling and optimization

| Stage | Attempts | Active updates | All-correct skipped | All-wrong skipped |
|---|---:|---:|---:|---:|
| stage1 | 153 | 120 | 8 | 25 |
| stage2 | 655 | 220 | 182 | 253 |

Both stages retained exact accepted-kind balance: 30 updates per kind in stage one, 55 per kind in stage two. Stage two used seven temperature-0.95 groups. No kind exhausted all 32 retries, so fallback was covered by tests rather than triggered in this run. Dynamic filtering prevented fake zero-signal updates, but it did not prevent collapse. The frozen SFT reference had zero measured weight change, and logged losses/gradient norms were finite.

## Plausible mechanism and limits

The evidence-gated reward gives a valid wrong answer -0.2, malformed finals -0.8, and correct abstentions +1. Abstaining can therefore beat risky malformed tool trajectories. Once a group uniformly abstains on an answerable prompt, its negative rewards have zero relative advantage; active filtering skips that group without a corrective optimizer update. This is consistent with the observed collapse, but this run does not isolate causality. The utility-chain gate passed its regression tests and prevented full reward for unsupported calculations; it did not make the complete reward objective ungameable.

The cold-start was deliberately small (240 rows, one epoch, 15 updates). GRPO sampled 3,232 training rollouts across 808 groups, compared with 240 SFT trajectories. A compute-matched continued-SFT control is absent. Model limitations, exploration, reward asymmetry and the weak warm start are not separated by this experiment.

## Follow-up experiment proposals, not executed

Use validation-based early stopping; separately confirm the saved stage-one checkpoint. Compare against additional SFT at a matched compute budget. Explicitly test false-abstention penalties and successful-tool-trajectory anchors, while keeping evaluation separate. Check sampled task coverage and all-wrong skipped groups, rather than accepting nonzero reward variance as sufficient evidence of useful learning. Any revised recipe needs a fresh confirmation set for strong generalization claims. No extra paid training or model evaluation was launched for these proposals.

See [failure_modes.png](failure_modes.png), [sampling balance](grpo_training/sampling_balance.png), per-model FAILURE_ANALYSIS.md, raw rollouts and TensorBoard logs.
