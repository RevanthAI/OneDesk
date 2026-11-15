# DriftGuard-MCP implementation record

Requested scope: milestones 1–4 using `CohereLabs/tiny-aya-fire`; English, romanized Hindi, Hinglish and romanized Telugu. Training is outside this phase.

## Verification

- Milestone 1: four initial world/parser/SQL/isolation tests passed; an additional oracle fact-independence test later passed.
- Milestone 2: nine reward tests passed. The six named policies were run over 100 semantic tasks; see `reward_hacking.md` and `reward_hacking.json`.
- Milestone 3: 1,700 rows generated and verified against tool evidence, minimum oracle call counts and expected outcomes. CuratorKIT exact deduplication retained all rows. The 400 SFT trajectories round-tripped through real AgentTune classes and imported into AuditKIT.
- Milestone 4: four evaluator tests passed. An explicitly labeled oracle integration check produced AuditKIT exact outcome/citation/tool F1/validity scores of 1.0 and redundancy 0.0. This is a harness check, not model performance.
- Frozen dataset hashes are in `data/SHA256SUMS`. Base-model episodes are separate from oracle artifacts.

## Deliberate specification resolutions

1. Four language groups need 400 synthetic holdout rows for at least 100 per language. The synthetic set has 100 semantic cases translated into four variants.
2. The stated reward cannot give all hacker policies <0.10 under the proposed mix. Always-abstain scores 0.1925, honest oracle 1.3550. An empty citation set receives zero citation bonus, consistent with requiring actually cited evidence. Early diagnostic output used the alternative empty/empty F1=1 convention; the final recorded suite uses zero. Exact outcome gating is preserved; an optional evidence-gated variant is separately named.
3. “Real-style” examples are synthetic fixtures, not evidence of real-repository generalization. The OSS-style set has 30 cases and 100 language-rendered items; its filename and report labels state the distinction.
4. Config value sets are disjoint using parity, while magnitude ranges overlap for realistic values. Service/employee namespaces and question-template sets are disjoint. Ground truth is generated without LLMs.
5. Fresh authoritative evidence alternates between GitHub and Slack. Tasks explicitly ask to compare the runbook against that server. Other tasks require DB; unplugging DB correctly makes those tasks unanswerable even when another silo is active.
6. The optional FastMCP function exposes the router, but evaluation uses in-process calls. Separate Notion/Slack/GitHub deployments are not benchmarked in this phase. Portable SQL snapshots are available under `reports/world_sql_exports/`; SQLite round-trip is tested, but PostgreSQL execution is not.

## Environment and compatibility issues

- `nvidia-smi` fails in the restricted sandbox but succeeds with host access: NVIDIA RTX 2070, 8 GB VRAM, driver 595.99.02.
- Existing workspace Python was 3.9.7. Created project Python 3.12.10 environment, required by the inspected AgentTune package.
- GPU stack: PyTorch 2.8.0+cu128; Transformers 4.57.6; bitsandbytes 0.50.2. FP16 compute is used because the RTX 2070 does not support BF16 training/inference in the intended way.
- Current full AgentTune metadata requires torch 2.11.0 and transformers >=5.15, plus TRL/OpenEnv/RAG. Installed only its actual dependency-free trajectory layer (`--no-deps`); full training readiness is not claimed.
- AgentTune’s `agentic` package initializer eagerly imports optional stacks. `src/toolkits.py` loads the real installed trajectory module directly by file path. No vendored toolkit code was modified.
- AgentTune does support multi-turn rollout hooks: `create_rollout_fn`, `rollout_func`, and `environment_factory` appear in the inspected sources. Its GRPO wrapper patches TRL generation when a custom rollout is present. No single-turn-only limitation is assumed; trainer validation belongs in milestone 5.
- Tiny Aya’s tokenizer returns `token_type_ids` when called normally. Cohere2 generation rejects that field. The evaluator explicitly requests `return_token_type_ids=False`; the initial attempt completed no episodes before this was fixed.
- Model commit is pinned to `73500c80fcb6c8bea3e830c21d5d2920249a0e1a` (about 6.7 GB checkpoint download). The parent `.env` token was loaded without printing or embedding it.
- The hackathon tracks URL returned 404 when checked; rules supplied by the user were treated as the working specification.

## Baseline artifacts

`reports/base_fire_nf4/` contains run configuration and, as the live run progresses, episode JSONL, runtime counters, AgentTune exports, per-item metrics and native AuditKIT output. The completed full-run summary is written to root `RESULTS.md`. Do not interpret oracle tests or partial live batches as the completed model result.

## GPU memory recovery

The batch-16 run saved 304 synthetic episodes before a longer batch caused CUDA OOM. The saved episodes were retained. The evaluator now splits only memory-failing generation batches in half and retries them; inputs, greedy decoding, tool budgets and scoring are unchanged. Runtime counters are accumulated across the restart, and memory splits are counted. Token throughput covers successful generation calls and excludes time spent in the failed allocation attempt. The original OOM record is preserved as `resolved_failure.json` after successful completion.
