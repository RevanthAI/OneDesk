# OneDesk: One Multilingual Workspace to Query Your Company’s Knowledge Base

*Track 3 · Agentic Fine-Tuning · `CohereLabs/tiny-aya-fire` (3.35B) with CuratorKIT, AgentTune and AuditKIT*

## The problem

Company knowledge is split across Notion wikis, GitHub pull requests, Slack threads and SQL databases, and the newest-looking document is often a trap: a stale runbook that wasn't updated after yesterday's hotfix, or a `[STAGING-ONLY]` configuration page. Meanwhile, engineering and operations teams ask questions in English, Hindi (Devanagari and Latin), Hinglish and Telugu (native and Latin).

Organizations want to run compact, on-premises models (~3B parameters) so private code, incidents and database schemas never leave their infrastructure. However, out of the box, small models struggle with multi-turn tool use and strict output formatting: our base model lacks a valid structured final answer on 30% of benchmark episodes, calls the wrong tools, or fails multi-step SQL, unit-conversion and math chains—scoring just **0.4% exact accuracy** across our 500-task benchmark.

**Can a small, locally deployable 3.35B model learn to generate 100% valid multi-turn tool calls, find the current production answer, cite verified evidence, flag the outdated page, and refuse when a database is offline—without collapsing into lazy refusals during reinforcement learning?**

## Results

![Headline Results](figures/1_headline_success.png)

Combined performance across all **500 held-out queries** (400 synthetic + 100 repo-style; see [docs/FULL_REPORT.md](docs/FULL_REPORT.md) for separate split tables and 95% bootstrap CIs):

| Metric (Combined 500-Query Holdout) | Untrained Base | Warmup SFT (2-ep) | Full SFT (4-ep) | **OneDesk (Final RL)** |
| --- | --- | --- | --- | --- |
| **Strict stale-doc catch** (`n=250` conflicts) | 0.0% | 70.4% | 61.2% | **75.6% (+14.4 pp vs Full SFT)** |
| **Exact answer accuracy** (`n=500` all tasks) | 0.4% | 70.8% | **77.0%** | 74.8% |
| **Valid tool & response format** (`n=500`) | 70.0% | **100.0%** | **100.0%** | **100.0%** |
| **Verified citation F1** (`n=425` cited tasks) | 0.0% | 88.3% | **93.2%** | 87.6% |
| **Required-chain compliance** (`n=425` answerable) | 0.0% | 93.2% | **97.6%** | 84.0% |

OneDesk improves strict stale-document catch over full 4-epoch SFT by **+14.4 pp pooled** (**+15.5 pp [+5.5, +26.0]** on synthetic and **+10.0 pp [+2.0, +20.4]** on repo-style), while reaching **100% valid tool-call and response formatting**. Full SFT stays slightly ahead on overall accuracy (`77.0%` vs `74.8%`) and exhaustive 3-server chain compliance, and all benchmark data is synthetic.

Format percentages count valid structured final answers; AuditKIT independently records 100% tool-call validity for each trained stage on both holdouts. Pooled means use the metric-specific denominators above; paired confidence intervals remain split-specific.

Runs locally in 4-bit NF4 (**3.15 GiB VRAM**, v1 adapter). Self-hosted L40S serving costs **$1.22 per 1k audits** vs **$13.17** at historical GPT-4o prices.

## Submission info

|  |  |
| --- | --- |
| Track | 3, problem statements 1, 2, 4, 5, 6, 9 |
| Model to use | [onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val) |
| Public Space | [Revanth-ml/OneDesk](https://huggingface.co/spaces/Revanth-ml/OneDesk) |
| Collections | [Models](https://huggingface.co/collections/Revanth-ml/onedesk-models-and-experimental-controls-6af97221a617ddc3326204a6) · [Data](https://huggingface.co/collections/Revanth-ml/onedesk-data-and-experiment-evidence-6af97225c0f1dc548b9ba8ce) |
| Full report | [docs/FULL_REPORT.md](docs/FULL_REPORT.md) |
| Work before the hackathon | None |

Detailed submission reference: [docs/SUBMISSION_DOSSIER.md](docs/SUBMISSION_DOSSIER.md).

## 1. Problem Statement & Approach

A Hinglish employee asks for `loyalty-api`’s actual production `batch_size_mb`: the runbook says 154, a newer staging-only distractor says 286, and the production Slack update says 16. This `train_sft-0000-hinglish` protocol example shows the tool calls, cited answer and stale-page flag; the first query is shortened for readability.

```xml
<tool_call>{"server":"notion-mcp","tool":"search_notion","arguments":{"query":"loyalty-api batch_size_mb"}}</tool_call>
<tool_call>{"server":"slack-mcp","tool":"search_slack","arguments":{"query":"loyalty-api batch_size_mb"}}</tool_call>
<final_answer>{"status":"conflict_resolved","value":16,"cites":["NOTION-V2-TR-105","SLACK-V2-TR-105"],"stale_source":"NOTION-V2-TR-105"}</final_answer>
```

![Unified 9-Server MCP Workspace](figures/0_workspace_architecture.png)

| Script style | Frozen example |
| --- | --- |
| en:latin | What is the active production batch_size_mb for loyalty-api? Compare the runbook with deployment records and flag any outdated page. |
| te:native | loyalty-api కోసం ప్రస్తుతం production లో batch_size_mb ఎంత? రన్‌బుక్‌ను deployment ఆధారాలతో పోల్చి పాత పేజీని గుర్తించండి. |

All six script styles: [full report](docs/FULL_REPORT.md#six-language-and-script-styles--verbatim-frozen-prompts).

![Multilingual Reach](figures/2_multilingual_reach.png)

## 2. Hackathon Repos Used

![Lexsi Toolkit Pipeline](figures/0_toolkit_pipeline.png)

| Toolkit | Role and features |
| --- | --- |
| **CuratorKIT 0.1.21** | `DataSample` + `ExactDeduplicator.run`: **1,955 → 1,700** tasks; 255 injected exact duplicates rejected. |
| **AgentTune 1.1.4** | `Step`/`Trajectory` serialization, `SFTTrainerBase` warmup and `TrlAgenticGrpo` lifecycle with executed live MCP rollouts. |
| **AuditKIT 1.1.7** | 580 episodes/checkpoint: trajectory import, outcome/citation scorers and native tool-selection, validity and redundancy metrics. |

Compatibility fixes:

- Bridge AgentTune’s missing `_generate_single_turn` hook to TRL 0.23.1 live rollouts.
- Load dependency-light `agenttune.agentic` leaf modules instead of eager optional stacks.
- Explicit BF16 autocast for unwrapped PEFT decoder log-probability scoring.

## 3. Data Creation, Curation & Evaluation Strategy

### 3.1 Rationale: Why We Built a Custom Benchmark & Chose `CohereLabs/tiny-aya-fire`

Single-turn English API-syntax accuracy alone does not establish enterprise reliability. We needed one benchmark combining **contradictory silos** (a stale Notion runbook versus a newer GitHub PR or Slack hotfix), **scope traps** (a newer `[STAGING-ONLY]` record ranked above `[PROD]`), **SQL-to-time/unit/math chains**, and English, Hindi (Devanagari/Latin), Hinglish and Telugu (native/Latin) questions. We chose **`CohereLabs/tiny-aya-fire` (3.35B)** for South Asian-script text alongside Latin technical identifiers such as `loyalty-api` and `batch_size_mb`, at a size suited to an organization-controlled on-premises boundary: our **v1 NF4 adapter used 3.15 GiB peak reserved VRAM**. That edge measurement is separate from final v2 BF16 benchmark accuracy; tokenizer support is not itself evidence of answer correctness.

### 3.2 How We Created the Data: Facts-First World + Live Oracle + CuratorKIT Funnel

**No LLM invented gold facts.** The four components below separate fact generation, tool verification, language rendering and curation; the actual builder executes **facts → rendering → CuratorKIT → oracle verification/trajectory export**.

1. **Deterministic Python worlds** ([src/v2_world.py](src/v2_world.py); [src/v2_tasks.py](src/v2_tasks.py)): fixed **seed 42** creates the training world with **60 microservices and 80 incidents**; **seed 99** creates the synthetic holdout, with a separate constructed OSS repo-style world. Structured histories determine values, timestamps, source IDs and labels for **consistent**, **conflict/outdated-doc**, **incident** (`sla_penalty`, `payload_lb`, `payload_mib`, `config_audit`) and **abstain** tasks (missing entity or unplugged `db-mcp`).

2. **Live tool-executing oracle** ([src/v2_oracle.py](src/v2_oracle.py)): a deterministic discovery policy executes `notion-mcp`, `github-mcp`, `slack-mcp`, `db-mcp`, `time-mcp`, `unit-converter-mcp` and `math-mcp` as required, against each episode’s isolated in-memory SQLite snapshot. It uses task identity/request metadata, then discovers values and authority through returned observations—not hidden gold values or source labels. The builder checks predicted outcomes and retrieved gold IDs before export, reusing one verified semantic-case trajectory across its language variants. The **240** [AgentTune SFT trajectories](data_v2/train_sft_agenttune_trajectories.jsonl) carry measured `evidence_gated` oracle rewards: **`{"1.0": 60, "1.3": 112, "1.5": 68}`**. Expected abstentions are verified safe refusals, not tasks requiring an unavailable answer.

3. **Six-style multilingual rendering:** templates cover `en:latin`, `hi:native`, `hi:latin`, `hinglish:latin`, `te:native` and `te:latin`. Most cases have **four language/register versions**, with Hindi and Telugu alternating native/Latin templates—not six versions per case. The corpus has **425 rows per language group**; Hindi and Telugu each have **213 native / 212 Latin** rows. Four repo-style translations are omitted to retain exactly 100 rows from 26 cases. Template rendering and tool checks do not replace human linguistic review.

4. **CuratorKIT 0.1.21 deduplication** ([src/v2_dataset.py:curate](src/v2_dataset.py)): `curatorkit.schema.DataSample` and `ExactDeduplicator.run` process **1,955 candidate model-visible prompts**, rejecting **255 injected exact-duplicate controls** to freeze **1,700 oracle-verified tasks**. Controls add **15%** to the clean-row count; they are **13.0% of all candidates**. Every rejection is logged in [data_v2/curation_rejections.jsonl](data_v2/curation_rejections.jsonl); the [funnel](data_v2/curation_funnel.json) measures exact deduplication, not semantic paraphrase filtering or independent natural-data quality gains.

| Split (`data_v2/`) | Candidates → retained (rejected) | Semantic cases | Task mix (rows) | Purpose |
| --- | --- | --- | --- | --- |
| `train_sft_240.jsonl` | 276 → **240** (36) | 60 | 60 consistent, 60 conflict, 60 incident, 60 abstain | Supervised protocol warmup (60 steps) & four-epoch control |
| `train_grpo_stage1.jsonl` | 460 → **400** (60) | 100 | 100 per kind | Final live multi-turn GRPO Stage 1 (updates 1–40) |
| `train_grpo_stage2.jsonl` | 552 → **480** (72) | 120 | 120 per kind | Final live multi-turn GRPO Stage 2 (updates 41–80) |
| `val_train_80.jsonl` | 92 → **80** (12) | 20 | 20 per kind | Checkpoint selection & >40% predicted-abstention collapse guard |
| `holdout_synth_400_frozen.jsonl` | 460 → **400** (60) | 100 | 80 consistent, 200 conflict, 60 incident, 60 abstain | Primary synthetic holdout evaluation |
| `holdout_repo_style_100_frozen.jsonl` | 115 → **100** (15) | 26 | 20 consistent, 50 conflict, 15 incident, 15 abstain | Out-of-domain constructed OSS repo-style holdout |
| **Total frozen corpus** | **1,955 → 1,700 (255)** | **426** (+20 unrendered reserved cases) | Balanced across four language groups; coverage of six script styles | 19 approved data-file hashes checked by `src.v2_2.manage.protected()` |

Task mixes describe frozen rows, not the final sampler’s accepted-update ratio. The 20 reserved training cases are outside these 1,700 rows. `SHA256SUMS` lists 15 artifacts; `protected()` additionally checks all **19 approved data files** without rewriting them.

### 3.3 Strict Curation Constraints We Imposed (`v1 → v2` Anti-Shortcut Hardening)

The audit of v1’s **85.25% (85.3% rounded)** SFT result found seven plausible confounds: reused SFT/GRPO cases, tool-spoiling prompts, `unknown-` missing-entity names, constant incident times/rates, an unused converter, implausible repo-style numbers, and single-result search. These are identified shortcuts, not measured causes of that score. V2 also varies incident times, rates and payloads, exercises kg→lb / decimal GB→MiB conversions, and enforces domain-valid configuration ranges.

1. **Blind tool routing:** user questions never name `github-mcp`, `slack-mcp`, `unit-converter-mcp` or `math-mcp`. Deployment-channel hints appear in retrieved runbooks; incident requests first require discovering service, timestamps or payload through SQLite. The prompt does not supply the tool sequence.

2. **Adversarial search ranking:** forgiving token-overlap search returns **up to three** own-entity/sibling records. Newer `[STAGING-ONLY]` records can rank above `[PROD]`, so “take the first hit” and “pick the newest timestamp” fail without scope filtering.

3. **Realistic refusal conditions:** absent services use plausible names without the `unknown-` prefix and are checked against the world’s service set. On unplugged-database tasks, `db-mcp` is actually absent from active schemas; the agent must respect the explicitly required source rather than substitute another silo.

4. **All 15 split-pair checks + modulo-3 partitioning:** [audit_splits](src/v2_dataset.py) and regression tests enforce **zero shared `case_id`**, **zero `(service, parameter)` pairs**, and **zero `incident_id`** across all six splits. Configuration integers use **train ≡ 1**, **synthetic holdout ≡ 2**, **repo-style holdout ≡ 0 (mod 3)**, preventing a training config integer from matching a holdout config answer. This rule does not make calculated incident costs or every scalar answer globally unique.

5. **CPU Text-Level Overlap Check** ([reports/submission/TEXT_LEAK_AUDIT.json](reports/submission/TEXT_LEAK_AUDIT.json)): **0/500 exact holdout prompt duplicates** against **1,120 training prompts**; mean nearest-train 5-word Jaccard is **0.0012 raw / 0.0012 entity-masked**. Independent structured checks find **zero `(service, parameter, gold_value)` tuple overlaps**. Shared system/tool instructions recur; **32/425 non-null holdout scalar answers repeat** on different facts. Low text overlap alone does not prove semantic independence.

6. **Tokenizer truncation preflight** ([data_v2/token_length_audit.json](data_v2/token_length_audit.json)): the cached Tiny Aya Fire tokenizer measured **min 979, mean 1,646.5, max 2,359 tokens** across 240 SFT conversations. The old **1,536-token** limit would truncate **136/240 (56.7%) of the full multilingual set**, not only native-script rows. We require **2,560 SFT tokens**, **zero truncated trajectories**, and **4,096 GRPO/evaluation context tokens**; generation is bounded to 192 tokens per turn and six tool calls.

### 3.4 Evaluation Strategy: Metrics Chosen and Why

- **Exact Answer Accuracy (`exact_outcome`, 500 holdouts):** both the expected status (`answered`, `conflict_resolved`, `abstain`) and normalized scalar must match. The right number with the wrong conflict/refusal status is still an operational error; dumping several numbers cannot satisfy a single-scalar answer.
- **Strict Outdated-Doc Catch (`stale_catch`, 250 conflicts):** exact outcome **plus the exact stale-page ID plus every gold source actually retrieved and cited**. This tests whether the agent caught and grounded the documentation drift, rather than guessing the updated value or merely collecting evidence.
- **Verified Citation & Tool-Chain Compliance (425 evidence/answerable tasks):** citation F1 credits retrieved-and-cited gold IDs while penalizing unsupported IDs; required-chain compliance checks successful required-server calls, including time/conversion/math utilities. These detect correct-looking unsupported answers and skipped calculations. AuditKIT’s native tool-selection precision/recall/F1, validity and redundancy diagnose routing/schema errors and wasted calls; valid final format is tracked separately. Tool calls per successful task measure efficiency without rewarding premature failure.
- **Refusal Calibration:** abstention precision penalizes false refusals of answerable questions; recall checks necessary refusals, with unplugged-source recall isolated. An agent that refuses everything can appear cautious while failing the job—the failure our collapsed-RL control exposes.

Reported 95% intervals use **10,000 semantic-case cluster bootstrap resamples**, keeping correlated language versions together: **20 validation / 100 synthetic / 26 repo-style cases**. Confidence intervals describe these frozen cohorts, not independent translations or verified live-enterprise generalization.

## 4. Experiments Run, What Failed & Winning Recipe

![Training Journey](figures/3_training_journey.png)

### Lazy Refusal Trap

Only 15 SFT steps left a weak starting policy. Long RL then favored comparatively less-penalized refusal over malformed or stale answers. At 340 updates it refused **77.3%** of synthetic queries and caught **0%** of stale docs.

### Clone Bottleneck

Full four-epoch SFT reached **77.3% / 76.0%** holdout accuracy. Its RL pilot accepted only **6/72 groups (8.3%)**; 62 of 66 rejected zero-variance groups had identical token sequences. Strict synthetic stale catch was **63.5%**, exposing a gap beyond overall accuracy.

### Winning Recipe

Two-epoch protocol warmup followed by anti-collapse, positive-anchor G6 GRPO completed **80 active updates**, accepting **23.4%** of groups. Validation selected update **40** at **80.0%** accuracy, with no abstention-collapse guard triggered. Selected holdout accuracy reached **75.8% / 71.0%**, and strict stale catch **79.0% / 62.0%**.

| Checkpoint | Synthetic % [95% CI] | Repo-style % [95% CI] | Validation % [95% CI] |
| --- | --- | --- | --- |
| Base | 0.50 [0.00, 1.25] | 0.00 [0.00, 0.00] | 1.25 [0.00, 3.75] |
| Warmup SFT · 60 steps | 72.50 [65.25, 79.25] | 64.00 [46.53, 80.39] | 67.50 [48.75, 85.00] |
| Final OneDesk · GRPO update 40 | 75.75 [68.50, 82.50] | 71.00 [55.45, 84.31] | 80.00 [63.75, 93.75] |
| Full 4-Epoch SFT · 120 steps | 77.25 [70.00, 84.00] | 76.00 [61.39, 88.89] | 73.75 [56.25, 90.00] |

[Full seven-checkpoint, multilingual and AuditKIT tables](docs/FULL_REPORT.md).

![Cost and Privacy ROI](figures/4_cost_and_privacy_roi.png)

| Serving option | USD /1k audits | USD /100k audits |
| --- | --- | --- |
| Local workstation · RTX 2070 NF4 | $0.08 | $8.00 |
| Self-hosted L40S · BF16 | $1.22 | $122.36 |
| Closed API · GPT-4o | $13.17 | $1,316.66 |

**Hackathon Compute Used:** recorded **12.05 L40S hours + 2.35 A100 minutes ≈ $21.80** continuous list-rate lower bound.

Includes observed training/evaluation work; excludes uncovered setup/charged intervals and minute rounding, so it is not an invoice total ([accounting](reports/submission/COMPUTE_ACCOUNTING.json)).

## 5–8. Models, Datasets & Public HF Collections

- **Primary Final Model:** [Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val) (base: [CohereLabs/tiny-aya-fire](https://huggingface.co/CohereLabs/tiny-aya-fire), rev `73500c80`).
- **Public Model Collection (all 9 artifacts & controls):** [Revanth-ml/onedesk-models-and-experimental-controls](https://huggingface.co/collections/Revanth-ml/onedesk-models-and-experimental-controls-6af97221a617ddc3326204a6).
- **Public Data Collection (frozen benchmark & rollout journals):** [Revanth-ml/onedesk-data-and-experiment-evidence](https://huggingface.co/collections/Revanth-ml/onedesk-data-and-experiment-evidence-6af97225c0f1dc548b9ba8ce).
- **Licenses:** model weights/adapters `CC-BY-NC-4.0` · synthetic data `CC-BY-4.0` ([LICENSE-DATA.md](LICENSE-DATA.md)) · code `Apache-2.0` ([LICENSE](LICENSE)).

[Nine-row revision table, six split hashes and all 19 protected-file checksums](docs/FULL_REPORT.md#5-models-used-and-their-licenses).

## 9. With More Credits: Approach, Before and After Results

**Targets, not measured results:**

| Priority | Measured before | Next change | Future target |
| --- | --- | --- | --- |
| Complete evidence | Chain: **86.47% / 74.12%** | Enforce three-server completeness; harder audit trails | **>96%** chain compliance |
| Unplugged DB | Recall: **21.43% / 42.86%** | Oversample unavailable-source contrasts | Fewer missed/false refusals |
| Overall accuracy | **75.75% / 71.00%** | Matched-compute warmup/reward/sampling sweep | **83%+**, aspirational |
| Confirmation | One selected recipe | Multiple seeds; fresh source-backed cohort | Replicated paired gains |

## 10. Repo Layout & Run Instructions

```text
├── src/              # v1/, v2/, v2_1/, v2_2/ runtimes; provenance-listed sources stay here
├── data_v2/          # Frozen 1,700 tasks, worlds and SHA-256 manifest
├── checkpoints/      # v1/, v2/, v2_1/, v2_2/ adapters and metadata
├── reports/          # v1/, v2/, v2_1/, v2_2/, submission/ evidence
├── figures/          # Benchmark charts and static architecture diagrams
├── docs/             # Full report, dossier, hf_cards/ and archive/data_v1/
└── tests/            # v1/, v2/, v2_1/, v2_2/: 120 regression tests
```

Canonical commands use `src.v2_2`; legacy imports remain supported. See [repository layout and source-provenance notes](docs/REPOSITORY_LAYOUT.md), including the two pre-existing source-checksum mismatches.

From the project root with the pinned toolkits/dependencies installed; use fresh output paths. The training/evaluation modules expose Python functions, so the commands below call those functions directly; GPU stages need suitable CUDA hardware.

```bash
# CPU data curation: new directory, never overwrite frozen data_v2/.
python -c "from src.v2_dataset import build; build('data_rebuild')"

# GPU: two-epoch SFT warmup, then live 40+40-update GRPO.
python - <<'PYTHON'
from src.v2_2.training import run_sft, run_grpo
adapter, metadata = run_sft('runs/repro_sft')
run_grpo(adapter, 'runs/repro_grpo', metadata)
PYTHON

# GPU: AuditKIT on validation and both frozen holdouts.
python - <<'PYTHON'
from peft import PeftModel
from src.v2_2.backend import load_base
from src.v2_2.evaluate_auditkit import evaluate
model, tokenizer = load_base()
model = PeftModel.from_pretrained(model, 'runs/repro_grpo/best_val_adapter')
evaluate(model, tokenizer, 'runs/repro_eval',
         splits=('validation', 'test_synth', 'repo_style'))
PYTHON

# Download selected weights, then run one local NF4 example (GPU).
python - <<'PYTHON'
from huggingface_hub import snapshot_download
snapshot_download('Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val',
    revision='016676680121b4dd90ec6026978de7ee1cdb1271',
    local_dir='checkpoints/v2_2/grpo_best_val_adapter')
PYTHON
python -m src.v2_2.local_demo --adapter checkpoints/v2_2/grpo_best_val_adapter

# CPU audit and complete regression suite.
python scripts/text_leak_check.py
CUDA_VISIBLE_DEVICES='' python -m pytest tests -q
```

## 11. Honest Limitations & Teammates Tagged

OneDesk is an open-source hackathon research prototype, formerly DriftGuard-MCP, and is unrelated to the commercial OneDesk helpdesk software; internal `DriftGuard*` class names retain that history.

- Constructed fixtures, modulo-3 configuration values and correlated template translations; no verified live-OSS transfer. Scalar answers recur across different facts, as the [text audit](reports/submission/TEXT_LEAK_AUDIT.json) reports.
- Overall GRPO-over-warmup holdout gain intervals include zero; repeated validation selection and one run need fresh confirmation.
- Prefer **full SFT for overall accuracy**, selected **GRPO for strict stale catch**; chain completeness, incident reasoning and unplugged-DB handling still need work.
- Warmup length, group size and temperature changed together; zero variance does not prove full-distribution entropy collapse.
- Local VRAM/speed is measured on the **v1 NF4 adapter**; v2 results are BF16. ROI excludes hardware/operations, uses historical API prices, and does not establish equal API accuracy; privacy requires appropriate connectors and logging.
- Model weights retain noncommercial terms; third-party licenses apply. The public Space distinguishes recorded evidence from opt-in live runs; future targets remain unmeasured.

**Teammates tagged:** [@Revanth-ml](https://huggingface.co/Revanth-ml).
