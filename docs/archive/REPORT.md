# OneDesk (formerly DriftGuard-MCP): One Multilingual Workspace to Query Your Company’s Knowledge Base

*Track 3: Agentic Fine-Tuning — Problem Statements Covered: **1, 2, 4, 5, 6, and 9***

**Which model to use:** [Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val) *(Base: `CohereLabs/tiny-aya-fire` 3.35B · Full tables & checksums in [docs/FULL_REPORT.md](../FULL_REPORT.md) and [SUBMISSION_DOSSIER.md](../SUBMISSION_DOSSIER.md))*

**Declaration of work done outside the hackathon:** **None.** All world generators, synthetic datasets, CuratorKIT/AgentTune/AuditKIT integrations, training runs, and evaluations were built from scratch during the hackathon window.

**Naming note:** *OneDesk is an open-source hackathon research prototype (formerly named `DriftGuard-MCP`, which is why internal Python classes retain the `DriftGuard*` prefix) and is unrelated to the commercial OneDesk helpdesk software.*

## ⚡ For Judges: 60-Second Overview

|  |  |
| --- | --- |
| **Claim** | A local 3.35B model checks Notion, GitHub, Slack and SQL for current, cited answers in English, Hindi, Hinglish or Telugu. |
| **Result** | Exact accuracy **0.5% → 75.8%** (synthetic, n=400), **0.0% → 71.0%** (repo-style, n=100); **100%** valid final format. |
| **Strongest at** | Stale docs: **79.0% vs 63.5%** full SFT; **+15.5 pp [+5.5, +26.0]** synthetic and **+10.0 pp [+2.0, +20.4]** repo-style. |
| **Caveat** | Full SFT is more accurate overall (**77.3% / 76.0%**); synthetic chain compliance trades off (**86.5% vs 97.4%**); all benchmark data is synthetic. |
| **Cost & Compute** | **$1.22/1k audits** on L40S vs historical GPT-4o **$13.17**; v1 local NF4: **3.15 GiB**, $0 API fees; recorded compute **~12.05 L40S h**, **~$21.80** list-rate lower bound. |

![Headline Results](../../figures/1_headline_success.png)

## 1. Problem Statement & Approach

A Hinglish employee asks for `loyalty-api`’s actual production `batch_size_mb`: the runbook says 154, a newer staging-only distractor says 286, and the production Slack update says 16. This `train_sft-0000-hinglish` protocol example shows the tool calls, cited answer and stale-page flag; the first query is shortened for readability.

```xml
<tool_call>{"server":"notion-mcp","tool":"search_notion","arguments":{"query":"loyalty-api batch_size_mb"}}</tool_call>
<tool_call>{"server":"slack-mcp","tool":"search_slack","arguments":{"query":"loyalty-api batch_size_mb"}}</tool_call>
<final_answer>{"status":"conflict_resolved","value":16,"cites":["NOTION-V2-TR-105","SLACK-V2-TR-105"],"stale_source":"NOTION-V2-TR-105"}</final_answer>
```

![Unified 9-Server MCP Workspace](../../figures/0_workspace_architecture.png)

| Script style | Frozen example |
| --- | --- |
| en:latin | What is the active production batch_size_mb for loyalty-api? Compare the runbook with deployment records and flag any outdated page. |
| te:native | loyalty-api కోసం ప్రస్తుతం production లో batch_size_mb ఎంత? రన్‌బుక్‌ను deployment ఆధారాలతో పోల్చి పాత పేజీని గుర్తించండి. |

All six script styles: [full report](../FULL_REPORT.md#six-language-and-script-styles--verbatim-frozen-prompts).

![Multilingual Reach](../../figures/2_multilingual_reach.png)

## 2. Hackathon Repos Used

![Lexsi Toolkit Pipeline](../../figures/0_toolkit_pipeline.png)

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

| Scenario | Required behavior |
| --- | --- |
| Consistent knowledge | Match production scope; verify agreement despite staging/sibling distractors. |
| Outdated documents | Reconcile Notion against newer PR/hotfix evidence; identify and cite the stale page. |
| Database/calculation chains | Execute SQLite SELECT; derive duration or convert kg→lb / GB→MiB; calculate rounded incident cost. |
| Safe refusal | Abstain for absent entities or an unavailable explicitly required database. |

The CPU text audit found **0/500 exact holdout prompt duplicates**, with mean nearest-train 5-word Jaccard **0.001189 raw / 0.001189 entity-masked**; including shared system/tool instructions raises raw similarity to **0.901369**. All 15 split pairs have zero shared case IDs, service/parameter pairs or incident IDs, but **32/425 non-null holdout scalar answers recur** (8 numbers) on different facts; no service/parameter/gold-value tuple overlaps. A **2,560-token SFT window preserves every trajectory (0 truncations)**; evaluation uses 4,096 tokens, with [full split/token details and the audit](../FULL_REPORT.md#cpu-text-level-overlap-check).

- **Exact accuracy:** correct status plus normalized scalar.
- **Strict stale catch:** correct answer, correct stale page, every gold source retrieved and cited.
- **Citation/tool compliance:** verified citation F1, required-server checks and AuditKIT metrics.
- **Refusal calibration:** necessary versus false refusals, including unplugged-source recall.

## 4. Experiments Run, What Failed & Winning Recipe

![Training Journey](../../figures/3_training_journey.png)

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

[Full seven-checkpoint, multilingual and AuditKIT tables](../FULL_REPORT.md).

![Cost and Privacy ROI](../../figures/4_cost_and_privacy_roi.png)

| Serving option | USD /1k audits | USD /100k audits |
| --- | --- | --- |
| Local workstation · RTX 2070 NF4 | $0.08 | $8.00 |
| Self-hosted L40S · BF16 | $1.22 | $122.36 |
| Closed API · GPT-4o | $13.17 | $1,316.66 |

**Hackathon Compute Used:** recorded **12.05 L40S hours + 2.35 A100 minutes ≈ $21.80** continuous list-rate lower bound.

Includes observed training/evaluation work; excludes uncovered setup/charged intervals and minute rounding, so it is not an invoice total ([accounting](../../reports/submission/COMPUTE_ACCOUNTING.json)).

## 5–8. Models, Datasets & Public HF Collections

- **Primary Final Model:** [Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val) (base: [CohereLabs/tiny-aya-fire](https://huggingface.co/CohereLabs/tiny-aya-fire), rev `73500c80`).
- **Public Model Collection (all 9 artifacts & controls):** [Revanth-ml/onedesk-models-and-experimental-controls](https://huggingface.co/collections/Revanth-ml/onedesk-models-and-experimental-controls-6af97221a617ddc3326204a6).
- **Public Data Collection (frozen benchmark & rollout journals):** [Revanth-ml/onedesk-data-and-experiment-evidence](https://huggingface.co/collections/Revanth-ml/onedesk-data-and-experiment-evidence-6af97225c0f1dc548b9ba8ce).
- **Licenses:** model weights/adapters `CC-BY-NC-4.0` · synthetic data `CC-BY-4.0` ([LICENSE-DATA.md](../../LICENSE-DATA.md)) · code `Apache-2.0` ([LICENSE](../../LICENSE)).

[Nine-row revision table, six split hashes and all 19 protected-file checksums](../FULL_REPORT.md#5-models-used-and-their-licenses).

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
├── src/v2_2/          # Final MCP runtime, AgentTune backends and AuditKIT scorer
├── src/              # v2 facts-first generator, oracle and CuratorKIT pipeline
├── data_v2/          # Frozen 1,700 tasks, worlds and SHA-256 manifest
├── checkpoints/v2_2/ # sft_warmup_adapter, grpo_best_val_adapter, grpo_final_adapter
├── figures/          # Benchmark charts and static architecture diagrams
├── docs/             # FULL_REPORT.md: complete tables and checksums
└── tests/v2_2/       # Final-recipe tests; 120 tests total across four test folders
```

From the project root with the pinned toolkits/dependencies installed; use fresh output paths. The training/evaluation modules expose Python functions, so the commands below call those functions directly; GPU stages need suitable CUDA hardware.

```bash
# CPU data curation: new directory, never overwrite frozen data_v2/.
python -c "from src.v2_dataset import build; build('data_rebuild')"

# GPU: two-epoch SFT warmup, then live 40+40-update GRPO.
python - <<'PYTHON'
from src_v2_2.training import run_sft, run_grpo
adapter, metadata = run_sft('runs/repro_sft')
run_grpo(adapter, 'runs/repro_grpo', metadata)
PYTHON

# GPU: AuditKIT on validation and both frozen holdouts.
python - <<'PYTHON'
from peft import PeftModel
from src_v2_2.backend import load_base
from src_v2_2.evaluate_auditkit import evaluate
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

- Constructed fixtures, modulo-3 configuration values and correlated template translations; no verified live-OSS transfer. Scalar answers recur across different facts, as the [text audit](../../reports/submission/TEXT_LEAK_AUDIT.json) reports.
- Overall GRPO-over-warmup holdout gain intervals include zero; repeated validation selection and one run need fresh confirmation.
- Prefer **full SFT for overall accuracy**, selected **GRPO for strict stale catch**; chain completeness, incident reasoning and unplugged-DB handling still need work.
- Warmup length, group size and temperature changed together; zero variance does not prove full-distribution entropy collapse.
- Local VRAM/speed is measured on the **v1 NF4 adapter**; v2 results are BF16. ROI excludes hardware/operations, uses historical API prices, and does not establish equal API accuracy; privacy requires appropriate connectors and logging.
- Model weights retain noncommercial terms; third-party licenses apply. No public Gradio app is established, and future targets are unmeasured.

**Teammates tagged:** [@Revanth-ml](https://huggingface.co/Revanth-ml).
