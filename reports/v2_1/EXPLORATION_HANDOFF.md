# G=4 pilot to G=6 GRPO handoff

The four-epoch SFT and its validation/holdout evaluations are complete and unchanged (73.75% validation, 77.25% synthetic, 76% OSS-style). The preliminary G=4 GRPO run had accepted only four groups out of 51 attempts at the decision point; one incident request exhausted all 32 retries on uniform rewards. Its policy updates are discarded, not mixed into the reported bounded experiment.

The next run starts again from the same revision-pinned selected SFT. G=6 is explicitly allowed by the task; exploration uses temperature 1.0 and 1.15 on retries 17–32 to obtain useful stochastic variation from the stronger, low-entropy SFT. All three reward definitions, the positive-anchor acceptance rule, 7:1 rotation, 60+60-update ceiling, beta 0.05, learning rate 5e-6, validation selection, collapse stop and frozen cohorts remain unchanged. The first pilot's source, raw logs and job status remain archived under its original run prefix.

This is an operational exploration adjustment, not a reward/data change or a checkpoint chosen using holdout scores. Completed SFT and diagnostic work is reused to avoid paying for duplicate training/evaluation. The final report records actual group size, sampling temperatures, completed updates and validation-selected step.
