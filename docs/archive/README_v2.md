# DriftGuard-MCP v2

**Measured result:** all 340 updates completed, but final GRPO collapsed toward abstention and achieved 0% stale catch on both holdouts. See [the experiment report](../../reports/v2/EXPERIMENT_REPORT.md) and [GRPO findings](../../reports/v2/GRPO_FINDINGS.md).

This is the independent runtime for the approved, immutable `data_v2/` release. `src/v2/` does not import legacy `src/`, and all new reports live in `reports/v2/`. The earlier `data/`, `src/`, `reports/`, model checkpoints and measured v1 results remain available as historical material, not inputs to this experiment.

## Approved experiment

1. Test required-utility reward gates, budgeted active sampling/fallback, frozen inputs, and exact 2,560-token untruncated SFT encoding.
2. Evaluate the pinned base model on both v2 frozen holdouts.
3. Train a fresh one-epoch SFT adapter on all 240 SFT rows, using the separate 80-row validation set; evaluate validation and both holdouts.
4. Run five active GRPO smoke updates from that SFT adapter. Discard smoke updates before the full run.
5. Train 120 + 220 active GRPO updates on the separate 400/480-row stage files, with validation after each stage. Persist raw attempted/skipped/accepted rollouts, TensorBoard events and resumable TRL checkpoints.
6. Evaluate the final adapter and generate a cohort-matched Base/SFT/SFT+GRPO table with individual and paired semantic-case bootstrap intervals.

All model training and v2 inference/validation run on Hugging Face L40S. Evaluation is matched BF16, greedy, batch 16 (with OOM splitting), max 192 new tokens per turn, max six tool calls and 4,096 total context tokens. It is a different deployment from the earlier local NF4 benchmark and must not be presented as a controlled v1 comparison.

SFT uses an exact 2,560-token budget and refuses truncation. GRPO uses 4,096 context / 192 per-turn generation tokens. Its four-sample groups are dynamically filtered. Retries 17–32 use temperature 0.95, and the accepted sampling temperature is also used to score old/reference/current policy log probabilities. A saturated kind falls back to unsaturated kinds; global exhaustion preserves the last adapter and is reported as early termination, never completion of nonexistent updates.

The evidence-gated reward requires successful utility calls for SLA and payload incident chains. Audit requests, including incident config audits, require the database where applicable, Notion, and the authoritative deployment channel(s) identified by gold citations, rather than unrelated channels. The original specified reward is retained only as a logged diagnostic.

## Cloud launch and review

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m src.v2.cloud_job --timeout 12h
```

The Hugging Face token is read from the existing parent `.env` and passed as a Job secret, never bundled. Repositories remain private. The job cap is 12 hours, a maximum listed L40S hardware-time charge of $21.60 at $1.80/hour; actual billing and remaining account credit must be checked in Hugging Face. See [Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing).

The cloud bundle includes approved holdouts solely for evaluation. Training loaders explicitly read only the assigned training split and validation split, and model tools expose only the currently selected world, not the filesystem. Every phase verifies `data_v2/SHA256SUMS`; the complete data-folder byte snapshot is checked again at completion.

The oracle and reference trajectories are deterministic fixtures, not model behavior. Constructed OSS-style cases are not verified upstream changes. No fixed target accuracy is imposed or manufactured. A high accuracy on reviewed synthetic fixtures does not establish broad enterprise reliability.

## Publication allowlist

Publish `src/v2/`, `data_v2/`, `README_v2.md`, `requirements_v2.txt`, `toolkit_revisions.json`, the pinned toolkit licenses/source references, and selected `reports/v2/` reports/plots. Omit legacy `src/`, `data/`, `reports/` and heavyweight model/optimizer files from a source publication; link the private/public model and run repositories as appropriate. Do not delete historical results or expose `.env`.

## Local use after cloud training

Download both exported adapters and reports with `python -m src.v2.manage download --models`. Adapter weights require the pinned Tiny Aya Fire base weights; this is a LoRA distribution, not a merged checkpoint.

The optional RTX 2070 deployment command is `python -m src.v2.local_demo --adapter checkpoints/v2/grpo_adapter`. It uses NF4 weights, FP16 computation, batch one and the Turing SDPA compatibility setting. It is intentionally separate from the matched cloud BF16 benchmark. No local model inference is run as part of this cloud experiment.

The release archive carries the pinned AgentTune/AuditKIT Python sources and their licenses. For a fresh source checkout, install `requirements_v2.txt` with the CUDA-compatible PyTorch wheel and expose `vendor/AgentTune/src` and `vendor/AuditKIT/src` on `PYTHONPATH`, as the cloud bootstrap does. Local NF4 use additionally requires bitsandbytes; it is not a dependency of the matched BF16 cloud experiment.

`python -m src.v2.finish --wait` waits for the current cloud job, retrieves both adapters and reports, verifies all 340 active updates, and creates the final v2-only source/report archive. It does not run inference or publish publicly.
