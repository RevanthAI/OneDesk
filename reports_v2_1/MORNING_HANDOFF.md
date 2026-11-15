# v2.1 paused experiment: morning handoff

Saved at the user's request on 13 November 2026 (Asia/Kolkata). **All recorded experiment jobs are terminal; no automatic restart is scheduled.** Resume only when the user returns. The latest queued job was canceled before GPU allocation, so there is no G6 training progress to recover.

## Completed results

Fresh SFT started from pinned `CohereLabs/tiny-aya-fire` revision `73500c80fcb6c8bea3e830c21d5d2920249a0e1a`. Four epochs, effective batch 8, learning rate 1.5e-4, cosine schedule, 120 optimizer steps / 960 example exposures, maximum sequence length 2560, **zero truncated conversations**. Best validation checkpoint: step 120.

| Evaluation | Exact outcome accuracy | 95% cluster-bootstrap CI |
|---|---:|---:|
| Validation (80 rows / 20 cases) | 73.75% | 56.25–90.00% |
| Synthetic holdout (400 rows / 100 cases) | 77.25% | 70.00–84.00% |
| OSS-style holdout (100 rows / 26 cases) | 76.00% | 61.39–88.89% |

The OSS-style cohort is modeled repository data, not independently verified real OSS drift. Cluster counts above come from the actual frozen v2 evaluation, not the original v1 cohort.

| Epoch / update | Validation accuracy | Predicted abstention |
|---|---:|---:|
| 1 / 30 | 52.50% | 15.00% |
| 2 / 60 | 67.50% | 23.75% |
| 3 / 90 | 65.00% | 22.50% |
| 4 / 120 | 73.75% | 22.50% |

The stronger warm-start substantially improved on the previous 15-step SFT: synthetic 15.0% → 77.25%, OSS-style 16.0% → 76.0%, validation 22.5% → 73.75%. Validation abstention is below the 40% collapse threshold and near the true 25% rate. The paired validation accuracy improvement is +51.25 percentage points (95% case-bootstrap CI +30.0 to +71.25). This is an exploratory selection gate after looking at four epochs, not an independent confirmatory test or proof that SFT alone solves every task.

The old v2 stage-1 adapter was also reevaluated and reproduced **43.75% validation accuracy**. Original v2 evidence remains intact.

## Saved adapter and evidence

- Local SFT adapter: `checkpoints_v2_1/sft_adapter/` (downloaded and weight hash recorded).
- Private HF model: `Revanth-ml/driftguard-tiny-aya-fire-v2-1-sft`.
- Exact model revision: `bf94f4cc6ec420752205859e6d63c7f83b85f14d`.
- Adapter SHA-256: `ec7cddc8a4791a7f740087026b4664518d6e99c05b051cee03f970c0091148d4`.
- Completed source run: `v2-1-20261112T173923Z`, private dataset repo `Revanth-ml/driftguard-mcp-v2-1-runs`.
- Local completed logs/results: `reports_v2_1/downloads/v2-1-20261112T173923Z/` (SFT metadata, full evaluation summaries/episodes, stage-1 diagnostic and discarded GRPO pilot logs).
- Machine-readable handoff: `reports_v2_1/RESUME_STATE.json`; cancellation evidence: `PAUSED_FOR_MORNING.json`; model provenance: `SAVED_SFT_ADAPTER.json`.

## GRPO findings and incomplete work

The G4 pilot produced **6 eligible groups out of 72 attempted groups** (8.33%); 66 groups had zero reward variance. No groups were marked all-negative-skipped in this persisted pilot. Many groups were uniformly correct; some uniformly unsuccessful groups also had identical reward. One incident sampling request exhausted its 32 retries. Positive-anchor and variance checks correctly prevented these uniform groups from becoming counted optimizer updates.

This shows an exploration/acceptance bottleneck after the stronger SFT. It does **not** establish that anti-collapse GRPO improves accuracy or that G6 fixes the bottleneck. The pilot policy is discarded. It did not reach the first 30-update validation checkpoint; no completed v2.1 GRPO holdout evaluation or final five-way comparison exists yet.

A replacement was prepared using the allowed G6 option, temperature 1.0 and retry temperature 1.15 (retries 17–32), starting again from the completed selected SFT. The replacement remained SCHEDULING until canceled at the user's request. No training took place in that job. The adjustment changes exploration, while preserving rewards, data, validation rules and the bounded schedule. See `EXPLORATION_HANDOFF.md`.

## Implemented safeguards and verification

- Additive `anti_collapse` reward, with all three reward modes logged; false abstention on answerable items receives -0.85 and useful evidence gathering receives the specified dense bridge reward. Successful incident calculations still require the utility chain.
- Positive-anchor acceptance for answerable groups: nonzero reward variance and at least one positive reward.
- Accepted-update rotation: conflict, incident, consistent, conflict, incident, conflict, incident, abstain; bounded retries and fallback.
- Planned GRPO ceiling 60 + 60 accepted updates, LR 5e-6, beta 0.05; greedy validation every 30 accepted updates; stop when validation abstention exceeds 40% and restore the best safe validation checkpoint.
- SFT step 0 remains an eligible fallback. If selected, report no demonstrated GRPO gain.
- Latest full suite passed: **105 tests**, with one benign PEFT tiny-fixture warning. Command: `.venv/bin/python -m pytest tests tests_v2 tests_v2_1 --import-mode=importlib -q`.
- Pause-time verification passed for all 19 locked data-folder files, including the unchanged manifest and its 15 artifacts, and all protected old v2 reports. No data regeneration.
- No local `src_v2_1.manage watch` processes remained at the pause check.

## Cloud job status at pause

| Job | Run | Verified status |
|---|---|---|
| `6af59651ab34849891af075a` | old v2 first attempt | CANCELED |
| `6af59c409737d9a9e0940742` | completed old v2 | COMPLETED |
| `6af5f9d80f431c4f7b55fbe9` | v2.1 completed SFT + discarded G4 pilot | CANCELED |
| `6af6141d5f2f1b7284b8a934` | queued G6 continuation | CANCELED (previously SCHEDULING) |

## Morning continuation — not executed

From the project root, verify frozen data and protected reports:

```bash
.venv/bin/python -c 'from src_v2_1.manage import protected; print(protected())'
```

When the user resumes, launch a **new** job reusing completed SFT/diagnostics/evaluations, excluding the discarded G4 optimizer/policy state:

```bash
.venv/bin/python -u -m src_v2_1.cloud_job \
  --timeout 8h \
  --resume-prefix v2-1-20261112T173923Z \
  --group-size 6 \
  --temperature 1.0 \
  --retry-temperature 1.15

.venv/bin/python -u -m src_v2_1.manage watch
```

The prepared handoff source revision is `883cbadd7fd29fc89c315e698fe4b6dd2b6ec6e6`; the launcher pins the current run-repository revision on a fresh launch and the model revision remains explicit. `LATEST_JOB.json` currently references the canceled queued job; do not mistake it for active work. The normal completed-job download command expects `COMPLETION.json`, so do not run it against the canceled queue entry expecting final results.

First inspect five active smoke updates for acceptance rate, finite gradients and memory, then continue the bounded schedule only if operationally sound. Track skipped-group cost and stop if the revised exploration still cannot obtain useful groups. Validate at 30/60/90/120, export best and final adapters, evaluate selected GRPO on frozen cohorts, and generate the five-way report in `reports/v2_1_comparison/EXPERIMENT_REPORT.md`. Keep the v2 collapse and discarded pilot evidence. Report actual completed updates, early stopping/fallback and selected checkpoint honestly; do not infer gains from training reward.

The user originally mentioned about $45 HF credit; remaining balance/spend has not been independently verified at this pause. An eight-hour timeout is a ceiling, not a cost estimate. All jobs are stopped now.
