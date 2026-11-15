# Protocol warmup follow-up: execution record

Existing four-epoch SFT and all v2 evidence are protected by SHA-256; no frozen data bytes changed. Runtime/reports/checkpoints use isolated v2_2 directories while report labels retain v2.1 warmup terminology.

Fresh pinned-base SFT trains 60 updates at batch eight; validate 30/45/60, select 45 or 60 on validation protocol validity (>=90%), abstention safety (<=40%), and preferred 55–68% accuracy. Use first 60 steps of the original 120-step cosine schedule to avoid changing the early learning-rate trajectory or forcing decay to zero. Full frozen holdouts are evaluated after selection only.

GRPO uses G6, temperature 1.0 / retry 1.15, LR 5e-6, beta .04, 40+40 accepted updates, validation every 20 and >40% abstention stop. At five actual optimizer updates, require finite gradients and acceptance strictly above historical 6/72 before continuing. Keep raw attempts and distinguish equal rewards from identical assistant sequences. A soft time limit leaves time before the three-hour hard cloud timeout for saving/evaluation; if reached, report early stop and actual updates. No unbounded retries.

The original v2 Stage-1 adapter is hash-verified and evaluated on validation plus both holdouts in the same job. Base validation is filled in; original SFT15/collapsed-GRPO and full-SFT120 evaluations are copied unchanged. Final report has seven rows with all three cohorts and paired semantic-case bootstrap differences. Original full SFT is a behavioral-cloning ablation reference, not a mathematically established ceiling.

Test record: original 105 tests passed in the combined run; a new report-formatting bug was fixed before launch. All nine added warmup/smoke/diversity/report/preservation tests subsequently pass. No training scores were inferred from these tests.
