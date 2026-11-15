# DriftGuard v2.1 anti-collapse experiment

Runtime: src_v2_1/. Results: reports_v2_1/. Adapters: checkpoints_v2_1/. The complete progression report is also exposed at reports/v2_1_comparison/EXPERIMENT_REPORT.md. All old v2 reports and all 19 files in data_v2 are protected by byte-hash snapshots. No frozen dataset is regenerated.

One private Hugging Face L40S job reevaluates the saved v2 stage-one adapter on validation, trains fresh Tiny Aya Fire for 4 SFT epochs (120 updates, effective batch 8, LR 1.5e-4 cosine, max length 2560), selects validation-best SFT, checks its paired validation improvement against v2 SFT, then runs bounded anti-collapse GRPO (60+60 active updates, LR 5e-6, beta .05). Validation at cumulative steps 30/60/90/120 selects a safe best checkpoint and stops predicted abstention above 40%. The stronger SFT is the eligible zero-update fallback. Any zero-update selection is explicitly labeled rather than claimed as RL improvement.

The operational warm-start gate requires a positive lower 95% paired case-bootstrap bound versus v2 SFT validation and an abstention rate <=40%. Four-epoch selection reuses the same 20-case validation set; this is exploratory, not independent confirmatory testing.

Anti-collapse rewards keep both older reward modes intact. False abstention is -.85, malformed output -1, stale errors use the explicit -.45 bridge formula, and other wrong answers use -.30 plus server/evidence recall. Dense bridge reward is process support, not proof of a correct answer. Correct answers retain the full evidence/utility gate. All three rewards are logged for every rollout. With G=4 or G=6, a positive-anchor answerable group cannot give false abstention positive relative advantage under the reward floor -1. All-negative and equal-reward groups never count as updates.

Accepted requests follow conflict, incident, consistent, conflict, incident, conflict, incident, abstain across both stages. A 32-attempt kind budget uses .95 on attempts 17–32. Answerable fallbacks never become extra abstention updates; bounded no-anchor exhaustion preserves validation-best policy and reports early stopping.

Use `python -m src_v2_1.cloud_job` to launch and `python -m src_v2_1.manage watch` for resilient logs, automatic reports/model download and preservation checks. Model training and evaluation run only on Hugging Face; local tests and report analysis do not execute a full model. A job has an eight-hour timeout. Repositories remain private; no public publishing is performed.

AlwaysAbstain averages -.5725 on the frozen 15%-abstention holdouts, -.3875 on balanced validation and -.61875 under the nominal 7:1 curriculum. A universal <-.50 claim across all mixes would be false. The old v2 collapse findings remain unchanged; the stage-one diagnostic is an addendum in this experiment.

## Recorded exploration handoff

The exact G=4 pilot was run first. After the stronger SFT, its acceptance was only 4/51 at the adjustment decision, including an incident request with 32 uniform-reward groups. Its raw logs and source are retained. The main GRPO experiment restarts from the same selected SFT with G=6, temperature 1.0 and retry temperature 1.15 (attempts 17–32). G=6 is allowed by the task and retains the negative-false-abstention-advantage guarantee. No frozen data, reward formula, learning rate, KL beta, update rotation, validation rule or inference budget changes. The four SFT epochs and completed evaluations are reused by revision rather than repeated. See EXPLORATION_HANDOFF.md and cloud run records for provenance. The report lists the actual exploration settings.
