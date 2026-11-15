# DriftGuard GRPO pilot experiment

## Status

The five-update smoke and the full bounded 20 + 40 update pilot completed successfully. Greedy training-world validation scored 40/40 both before and after GRPO, with unchanged mean reward 1.46. This ceiling-limited cohort shows no observed regression, not an accuracy improvement. The full frozen 500-question post-GRPO benchmark has not run; the last measured synthetic benchmark accuracy remains the SFT result of 85.25%.

## Design and controls

- Start from `Revanth-ml/driftguard-tiny-aya-fire-sft` at `b0d0d072311e62e31eb6258ad8ce987e8bf7926d`, over `CohereLabs/tiny-aya-fire` at `73500c80fcb6c8bea3e830c21d5d2920249a0e1a`.
- BF16 LoRA continuation on one L40S; group size 4; one prompt group per optimizer update; learning rate 5e-6; constant schedule; gradient clipping 1; KL coefficient 0.04; PPO ratio clip 0.2.
- Sampling temperature 0.8, top-p 1 and top-k 0. Policy scoring uses the same temperature, without an unaccounted top-p/top-k sampling filter.
- Live multi-turn episodes execute the actual isolated MCP environment. At most six tool calls, 192 generated tokens per turn and context budget 4,096. There is no oracle completion substituted for a sampled model action.
- Only actual sampled assistant tokens receive policy-gradient and KL loss. Prompts, tool responses, and injected turn delimiters remain visible in attention but are masked out of the loss. Sampled token IDs are retained exactly.
- Reference log probabilities come from a frozen copy of the SFT adapter, not from disabling adapters and reverting to the original base. Parameter checks verify the reference did not change.
- The existing frozen curriculum files are used without inserting observed test failures. Ten semantic cases reserved by the SFT validation split are excluded from both GRPO stages, leaving 360 curriculum rows per stage. Validation contains 40 translations of those ten cases, primarily conflicts, with no abstention tasks. It is a limited diagnostic, not the final evaluation.
- Neither frozen evaluation world nor its task JSONL is included in the cloud bundle. The SHA manifest contains their hashes, not their contents. The source-only/train-only bundle and input hashes are recorded per job.
- Stage 1 runs 20 updates, stage 2 runs 40. This is a bounded pilot, not the original 120 + 220 step curriculum. Each stage starts a fresh optimizer; the policy carries forward, while the KL reference remains the original SFT policy.

## Reward choice

Optimization uses the already-audited `evidence_gated` variant in `src/reward.py`. The originally specified reward is logged alongside it for every rollout. This is an explicit experimental change: wrong well-formed answers receive -0.2 instead of +0.05, and a correct non-abstention answer without any verified citation receives zero rather than base success reward. The existing malformed-output, stale-trap, citation, stale-source, efficiency and distractor logic otherwise remains in place.

This reduces known incentives for unsupported guesses; it is not claimed to be mathematically ungameable. Correct abstentions still receive reward. Outcome accuracy, evidence quality and task mix must be examined together. Groups with identical rewards have zero relative advantage and provide no outcome learning signal; their frequency is logged explicitly. Training reward curves are not held-out accuracy curves. With centered group advantages, a policy loss near zero or negative can still have a nonzero useful gradient; inspect reward variation, gradient norm and validation alongside the loss.

## AgentTune compatibility

Pinned AgentTune's `TrlAgenticGrpo` expects `_generate_single_turn`, which is absent in installed TRL 0.23.1. The project loads that dependency-free upstream wrapper leaf to avoid eager optional imports, subclasses its trainer setup hook, and retains its real data, train, save and stats lifecycle. TRL owns the optimizer, scheduler, sampling order, callbacks, checkpoints and TensorBoard. The project supplies live MCP rollouts and exact sparse-vocabulary GRPO scoring/loss. This compatibility path is documented rather than presented as unmodified upstream native support.

The five-update smoke used implicit gradient-pass autocast; the pilot makes BF16 autocast explicit in all old/reference/update scoring passes because direct decoder calls bypass the outer Accelerate wrapper. Both frozen source bundles are retained. Sparse policy log probabilities and gradients are tested against a dense reference; masking and group advantages have separate tests.

## Smoke results

- Job: https://huggingface.co/jobs/Revanth-ml/6af4903f9737d9a9e09312af
- Five optimizer updates / 20 sampled episodes completed.
- Three of five groups had nonzero reward variation.
- Adapter parameter L1 change: 266.667832; frozen reference L1 change: 0.
- Peak reserved VRAM: 7.924 GiB. Trainer runtime: 106.45 seconds, excluding installation/download/setup.
- All logged gradients were finite. Thirty-nine project tests passed; one benign PEFT fixture warning.

The pilot first optimizer update recorded KL = 0 and clip fraction = 0 after making precision explicit. Later nonzero KL measures departure from the frozen SFT reference. All-wrong Telugu groups expose database-only constraint and conflict-status failures, with no outcome signal when every sample receives the same penalty.

## Completed pilot results

- Job: https://huggingface.co/jobs/Revanth-ml/6af4911e9737d9a9e093136b
- All 60 optimizer updates completed: 20 stage 1 + 40 stage 2; 240 sampled full episodes.
- Mixed-reward groups: 21/60. The remaining 39 groups had zero relative-advantage outcome signal: 37 were all-correct and two were all-wrong. Thus most zero-signal groups reflect already-successful behavior, not demonstrated entropy collapse.
- Policy adapter parameter L1 change: 1104.732532. Frozen SFT reference L1 change: 0.
- Validation: SFT 40/40, GRPO 40/40; mean evidence-gated reward 1.46 for both. Only ten cases, predominantly conflict tasks, with no abstention cases. These observations cannot establish broad improvement or unchanged performance on the frozen evaluation worlds.
- The pilot uses the explicitly documented evidence-gated reward, not solely the originally specified formula. Both rewards were logged per episode.
- Peak reserved VRAM: 8.801 GiB. All 60 optimizer log entries were finite; maximum pre-clipping gradient norm 0.80256; maximum logged sampled-token KL 0.03078. Stage training runtimes were 437.13 and 835.14 seconds; the full training program, including validation/model setup/export, took 28.64 minutes. These durations are not an HF invoice.
- Review the full NF4 deployment benchmark before promoting this checkpoint over SFT or launching the full 340-update recipe. Many zero-signal groups reflect an already-correct policy; the all-failed groups specifically motivate testing more exploration or a separately labelled decision-state curriculum in a future experiment.

## Logs, plots and downloads

Private run repository: https://huggingface.co/datasets/Revanth-ml/driftguard-mcp-grpo-runs

Each stage saves `rollouts.jsonl` (actual token IDs, loss masks, model turns, MCP calls/results, rewards and advantages), `rollout_metrics.jsonl`, `optimizer_log.jsonl`, TensorBoard event files, actual trainer config, trainer state and bounded adapter checkpoints. Metrics are persisted to the Hub every five steps and at stage boundaries. There is no external telemetry account required. Checkpoint saves omit optimizer state, so they are not exact optimizer-resumption snapshots. Intermediate adapter weights exist only in the cloud job filesystem and are excluded from run-repository uploads; downloaded checkpoint folders contain metadata. The final adapter is retained separately in the private model repository.

Plots are available as standalone PNG/SVG files: `training_rollouts.*` and `optimization.*`. Open `dashboard.html` in the same directory to view both. The dashboard uses local image files and works without a network connection. Local post-processing also exports `rollout_explorer.html`, a self-contained viewer with stage/language/task filters and actual MCP conversations. Unsmooth lines show actual sampled groups, not fabricated or interpolated evaluation points.

```bash
# Current job status
.venv/bin/python -m src.manage_grpo status

# Follow logs (Ctrl+C only disconnects this viewer; it does not cancel the cloud job)
.venv/bin/python -m src.manage_grpo logs

# Download current diagnostics
.venv/bin/python -m src.manage_grpo download

# Once the pilot completes, also download its adapter
.venv/bin/python -m src.manage_grpo download --model

# View both stages in TensorBoard after downloading
.venv/bin/python -m tensorboard.main --logdir reports/cloud_grpo/downloaded_artifacts --port 6006
```

After download, evaluate the GRPO adapter under the same local inference settings as SFT:

```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv/bin/python -u -m src.evaluate_auditkit \
  --adapter-path checkpoints/tiny-aya-fire-grpo-pilot-adapter \
  --quantization 4bit --batch-size 1 --sdpa-expand-kv \
  --output reports/grpo_pilot_fire_nf4 \
  --baseline reports/sft_fire_nf4
```

The comparison validates identical dataset hashes and task-ID cohorts. `COMPARISON.md` is descriptive; per-run intervals do not establish significance for the change. The existing OSS-style fixtures have documented validity defects. These test sets have guided development, so final generalization claims require an untouched confirmation holdout.

## Cost controls

Smoke timeout: 30 minutes. Pilot timeout: 90 minutes. At the listed L40S rate of $1.80/hour, their combined hardware-time ceiling is about $3.60; actual billed duration should be checked in HF billing. The installed Jobs SDK does not expose an account credit-balance method, so remaining credit has not been independently verified. Sources: https://huggingface.co/docs/hub/jobs-pricing and https://huggingface.co/docs/huggingface_hub/en/guides/jobs .

## Final local artifacts and verification

Both cloud jobs are confirmed COMPLETED in `final_job_statuses.json`; no job from this experiment remains active. The adapter is downloaded at `checkpoints/tiny-aya-fire-grpo-pilot-adapter`, pinned to model revision `1eae42be5b7a3e8eeeb8408078537b4b0b243732` in https://huggingface.co/Revanth-ml/driftguard-tiny-aya-fire-grpo-pilot . Run artifacts were downloaded at repository revision `cd0d2913857874550c564a19546248d08e9e9061`; per-job `downloads.json` records the exact source.

The final local diagnostics are under `reports/cloud_grpo/downloaded_artifacts/pilot-l40sx1-20261111T160022Z/`:

- [Analysis and paired comparison](downloaded_artifacts/pilot-l40sx1-20261111T160022Z/ANALYSIS.md)
- [Training, optimization and validation plots](downloaded_artifacts/pilot-l40sx1-20261111T160022Z/dashboard.html)
- [Filterable rollout explorer](downloaded_artifacts/pilot-l40sx1-20261111T160022Z/rollout_explorer.html)
- `analysis.json`, `rollout_metrics.csv`, `ANALYSIS_SHA256SUMS` and per-stage raw logs/TensorBoard events.

The paired validation change is 0 percentage points, with a degenerate [0, 0] cluster-bootstrap interval because all 40 paired outcomes stayed correct. This is a ceiling-limited diagnostic, not proof of equivalent general performance. The realized pilot exposure is also uneven: stage 2 sampled only one incident question group (four episodes), so its mean training score cannot establish improved incident chaining.

The final adapter was checked on the RTX 2070 in NF4 with the existing English synthetic conflict example (`test_synth-0035-en`). It queried Notion and GitHub, returned value 20 with both correct citations and stale-page identification, and scored exact outcome 1 / reward 1.5. See `local_grpo_example.json`. This is an installation check on one previously inspected example, not independent evidence of a generalization gain. No merged GRPO model was exported; the downloaded adapter runs over the original cached base.

```bash
.venv/bin/python -m src.run_local_sft \
  --adapter checkpoints/tiny-aya-fire-grpo-pilot-adapter
```

The model-weight checksums are in `GRPO_MODEL_SHA256SUMS`. The next comparison is the full frozen NF4 evaluation command above, using `reports/sft_fire_nf4` as the baseline. That full evaluation was deliberately left for the same local deployment workflow as the SFT benchmark; no post-GRPO 500-item accuracy is claimed here.
