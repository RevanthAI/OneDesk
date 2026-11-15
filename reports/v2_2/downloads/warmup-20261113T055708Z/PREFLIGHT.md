# v2.1 pre-flight verification

All 94 tests passed with `pytest tests tests_v2 tests_v2_1 --import-mode=importlib -q`. Importlib mode prevents duplicate historical test filenames from conflicting. One benign PEFT test-fixture vocabulary warning occurred. Real model training/inference was not run locally.

The tests cover the new reward ordering and exact dense bridge values, AlwaysAbstain on the actual frozen holdout mix, preservation of specified/evidence_gated modes, required incident utilities, rejection of variable all-negative groups, G=4/G=6 false-abstention advantage sign, exact 7:1 rotation across the stage boundary, exploration temperature/fallback, validation stopping and safe best selection, all-three-reward backend logging, and unchanged frozen data/old reports.

The v2.1 runtime is isolated. Existing v2 files are protected by PROTECTED_V2_LOCK.json; all 19 data_v2 files have a complete byte snapshot in addition to the unchanged 15-entry SHA256SUMS. New data generation is not part of this experiment.

The explicit stale bridge uses -0.45 rather than the task's earlier illustrative -0.50. AlwaysAbstain is below -0.50 on the frozen 15%-abstention holdouts and the nominal 7:1 update cycle, but not on balanced validation. Malformed rollouts remain below false abstention in absolute reward; the positive-anchor constraint ensures that false abstention has negative relative advantage in every accepted answerable G=4/G=6 group under the -1 reward floor.

The selected stronger SFT checkpoint is eligible as GRPO step zero. If no safe GRPO checkpoint improves validation, the selected policy remains SFT and the final report explicitly labels that fact. Warm-start significance is an exploratory paired bootstrap gate after four validation looks; it is not an independently confirmed statistical claim.
