# OneDesk: teaching a 3.35B model to catch stale company knowledge

*A Track 3 agentic fine-tuning experiment with Tiny Aya Fire, CuratorKIT, AgentTune and AuditKIT.*

**[Try OneDesk](https://huggingface.co/spaces/Revanth-ml/OneDesk)** · **[GitHub and reproducibility guide](https://github.com/RevanthAI/OneDesk)** · **[Model collection](https://huggingface.co/collections/Revanth-ml/onedesk-models-and-experimental-controls-6af97221a617ddc3326204a6)** · **[Data collection](https://huggingface.co/collections/Revanth-ml/onedesk-data-and-experiment-evidence-6af97225c0f1dc548b9ba8ce)**

## The newest document can still be the wrong answer

An engineer asks, in Hinglish: “What is the actual production setting? Check the runbook against deployment updates and flag the outdated page.”

The wiki contains a plausible number. A newer document contains another number—but it is marked **[STAGING-ONLY]**. A production pull request changed the configuration, and an emergency Slack hotfix superseded that PR.

Answering correctly requires more than retrieving a relevant paragraph. The assistant must match the service and production scope, follow clues between tools, compare deployment evidence, cite records it actually retrieved, and identify the stale runbook. For incidents, it must execute SQL and chain time, unit-conversion and arithmetic tools. When the required database is unplugged, guessing is a failure.

We built **OneDesk** to study whether a compact, locally deployable model can learn this behavior across English, Hindi in Devanagari and Latin, Hinglish, and Telugu in native and Latin scripts.

![OneDesk combined benchmark](https://raw.githubusercontent.com/RevanthAI/OneDesk/main/figures/1_headline_success.png)

Across **500 held-out questions**, our final agent reaches **74.8% exact outcome accuracy** and **75.6% strict stale-document catch**, compared with **0.4%** and **0.0%** for the untrained base. The main RL gain is specific: stale-document catch improves by **14.4 percentage points over full four-epoch SFT**. Full SFT still wins on overall accuracy and complete tool-chain execution.

## One question, nine MCP interfaces

The student is [`CohereLabs/tiny-aya-fire`](https://huggingface.co/CohereLabs/tiny-aya-fire), a 3.35B model. Its environment contains seven useful MCP interfaces—Notion, GitHub, Slack, SQL, time, unit conversion and math—plus weather and calendar distractors.

![Nine-server workspace](https://raw.githubusercontent.com/RevanthAI/OneDesk/main/figures/0_workspace_architecture.png)

These are executable tools, not names in a prompt. Each episode gets its own in-memory SQLite database, populated from a fixed world snapshot. SQL is read-only and bounded. Search returns production, staging and sibling-service records, so simply picking the newest result fails.

The model emits one XML-wrapped JSON action at a time. A compact example from our training world:

```xml
<tool_call>{"server":"notion-mcp","tool":"search_notion","arguments":{"query":"loyalty-api batch_size_mb"}}</tool_call>
<tool_call>{"server":"slack-mcp","tool":"search_slack","arguments":{"query":"loyalty-api batch_size_mb"}}</tool_call>
<final_answer>{"status":"conflict_resolved","value":16,"cites":["NOTION-V2-TR-105","SLACK-V2-TR-105"],"stale_source":"NOTION-V2-TR-105"}</final_answer>
```

The first query is shortened for readability. Actual observations enter the next model turn; reference labels and oracle actions do not.

## 3. Data Creation, Curation & Evaluation Strategy

### 3.1 Rationale: Why We Built a Custom Benchmark & Chose `CohereLabs/tiny-aya-fire`

Single-turn English API-syntax accuracy alone does not establish enterprise reliability. We needed one benchmark combining **contradictory silos** (a stale Notion runbook versus a newer GitHub PR or Slack hotfix), **scope traps** (a newer `[STAGING-ONLY]` record ranked above `[PROD]`), **SQL-to-time/unit/math chains**, and English, Hindi (Devanagari/Latin), Hinglish and Telugu (native/Latin) questions. We chose **`CohereLabs/tiny-aya-fire` (3.35B)** for South Asian-script text alongside Latin technical identifiers such as `loyalty-api` and `batch_size_mb`, at a size suited to an organization-controlled on-premises boundary: our **v1 NF4 adapter used 3.15 GiB peak reserved VRAM**. That edge measurement is separate from final v2 BF16 benchmark accuracy; tokenizer support is not itself evidence of answer correctness.

### 3.2 How We Created the Data: Facts-First World + Live Oracle + CuratorKIT Funnel

**No LLM invented gold facts.** The four components below separate fact generation, tool verification, language rendering and curation; the actual builder executes **facts → rendering → CuratorKIT → oracle verification/trajectory export**.

1. **Deterministic Python worlds** ([src/v2_world.py](https://github.com/RevanthAI/OneDesk/blob/main/src/v2_world.py); [src/v2_tasks.py](https://github.com/RevanthAI/OneDesk/blob/main/src/v2_tasks.py)): fixed **seed 42** creates the training world with **60 microservices and 80 incidents**; **seed 99** creates the synthetic holdout, with a separate constructed OSS repo-style world. Structured histories determine values, timestamps, source IDs and labels for **consistent**, **conflict/outdated-doc**, **incident** (`sla_penalty`, `payload_lb`, `payload_mib`, `config_audit`) and **abstain** tasks (missing entity or unplugged `db-mcp`).

2. **Live tool-executing oracle** ([src/v2_oracle.py](https://github.com/RevanthAI/OneDesk/blob/main/src/v2_oracle.py)): a deterministic discovery policy executes `notion-mcp`, `github-mcp`, `slack-mcp`, `db-mcp`, `time-mcp`, `unit-converter-mcp` and `math-mcp` as required, against each episode’s isolated in-memory SQLite snapshot. It uses task identity/request metadata, then discovers values and authority through returned observations—not hidden gold values or source labels. The builder checks predicted outcomes and retrieved gold IDs before export, reusing one verified semantic-case trajectory across its language variants. The **240** [AgentTune SFT trajectories](https://github.com/RevanthAI/OneDesk/blob/main/data_v2/train_sft_agenttune_trajectories.jsonl) carry measured `evidence_gated` oracle rewards: **`{"1.0": 60, "1.3": 112, "1.5": 68}`**. Expected abstentions are verified safe refusals, not tasks requiring an unavailable answer.

3. **Six-style multilingual rendering:** templates cover `en:latin`, `hi:native`, `hi:latin`, `hinglish:latin`, `te:native` and `te:latin`. Most cases have **four language/register versions**, with Hindi and Telugu alternating native/Latin templates—not six versions per case. The corpus has **425 rows per language group**; Hindi and Telugu each have **213 native / 212 Latin** rows. Four repo-style translations are omitted to retain exactly 100 rows from 26 cases. Template rendering and tool checks do not replace human linguistic review.

4. **CuratorKIT 0.1.21 deduplication** ([src/v2_dataset.py:curate](https://github.com/RevanthAI/OneDesk/blob/main/src/v2_dataset.py)): `curatorkit.schema.DataSample` and `ExactDeduplicator.run` process **1,955 candidate model-visible prompts**, rejecting **255 injected exact-duplicate controls** to freeze **1,700 oracle-verified tasks**. Controls add **15%** to the clean-row count; they are **13.0% of all candidates**. Every rejection is logged in [data_v2/curation_rejections.jsonl](https://github.com/RevanthAI/OneDesk/blob/main/data_v2/curation_rejections.jsonl); the [funnel](https://github.com/RevanthAI/OneDesk/blob/main/data_v2/curation_funnel.json) measures exact deduplication, not semantic paraphrase filtering or independent natural-data quality gains.

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

4. **All 15 split-pair checks + modulo-3 partitioning:** [audit_splits](https://github.com/RevanthAI/OneDesk/blob/main/src/v2_dataset.py) and regression tests enforce **zero shared `case_id`**, **zero `(service, parameter)` pairs**, and **zero `incident_id`** across all six splits. Configuration integers use **train ≡ 1**, **synthetic holdout ≡ 2**, **repo-style holdout ≡ 0 (mod 3)**, preventing a training config integer from matching a holdout config answer. This rule does not make calculated incident costs or every scalar answer globally unique.

5. **CPU Text-Level Overlap Check** ([reports/submission/TEXT_LEAK_AUDIT.json](https://github.com/RevanthAI/OneDesk/blob/main/reports/submission/TEXT_LEAK_AUDIT.json)): **0/500 exact holdout prompt duplicates** against **1,120 training prompts**; mean nearest-train 5-word Jaccard is **0.0012 raw / 0.0012 entity-masked**. Independent structured checks find **zero `(service, parameter, gold_value)` tuple overlaps**. Shared system/tool instructions recur; **32/425 non-null holdout scalar answers repeat** on different facts. Low text overlap alone does not prove semantic independence.

6. **Tokenizer truncation preflight** ([data_v2/token_length_audit.json](https://github.com/RevanthAI/OneDesk/blob/main/data_v2/token_length_audit.json)): the cached Tiny Aya Fire tokenizer measured **min 979, mean 1,646.5, max 2,359 tokens** across 240 SFT conversations. The old **1,536-token** limit would truncate **136/240 (56.7%) of the full multilingual set**, not only native-script rows. We require **2,560 SFT tokens**, **zero truncated trajectories**, and **4,096 GRPO/evaluation context tokens**; generation is bounded to 192 tokens per turn and six tool calls.

### 3.4 Evaluation Strategy: Metrics Chosen and Why

- **Exact Answer Accuracy (`exact_outcome`, 500 holdouts):** both the expected status (`answered`, `conflict_resolved`, `abstain`) and normalized scalar must match. The right number with the wrong conflict/refusal status is still an operational error; dumping several numbers cannot satisfy a single-scalar answer.
- **Strict Outdated-Doc Catch (`stale_catch`, 250 conflicts):** exact outcome **plus the exact stale-page ID plus every gold source actually retrieved and cited**. This tests whether the agent caught and grounded the documentation drift, rather than guessing the updated value or merely collecting evidence.
- **Verified Citation & Tool-Chain Compliance (425 evidence/answerable tasks):** citation F1 credits retrieved-and-cited gold IDs while penalizing unsupported IDs; required-chain compliance checks successful required-server calls, including time/conversion/math utilities. These detect correct-looking unsupported answers and skipped calculations. AuditKIT’s native tool-selection precision/recall/F1, validity and redundancy diagnose routing/schema errors and wasted calls; valid final format is tracked separately. Tool calls per successful task measure efficiency without rewarding premature failure.
- **Refusal Calibration:** abstention precision penalizes false refusals of answerable questions; recall checks necessary refusals, with unplugged-source recall isolated. An agent that refuses everything can appear cautious while failing the job—the failure our collapsed-RL control exposes.

Reported 95% intervals use **10,000 semantic-case cluster bootstrap resamples**, keeping correlated language versions together: **20 validation / 100 synthetic / 26 repo-style cases**. Confidence intervals describe these frozen cohorts, not independent translations or verified live-enterprise generalization.

![Multilingual results](https://raw.githubusercontent.com/RevanthAI/OneDesk/main/figures/2_multilingual_reach.png)

## Three Lexsi toolkits in one pipeline

![Lexsi toolkit chain](https://raw.githubusercontent.com/RevanthAI/OneDesk/main/figures/0_toolkit_pipeline.png)

- **CuratorKIT 0.1.21:** `DataSample` and `ExactDeduplicator.run` filtered 1,955 candidates into 1,700 tasks, recording 255 deliberately injected exact duplicates.
- **AgentTune 1.1.4:** trajectory serialization, assistant-only SFT warmup, and a live multi-turn GRPO backend built around its trainer lifecycle.
- **AuditKIT 1.1.7:** outcome/citation scorers and native tool-selection F1, validity and redundancy, evaluated alongside our strict grounding metrics.

We also documented three compatibility fixes: AgentTune’s missing TRL 0.23.1 generation hook, eager optional imports, and explicit BF16 autocast for unwrapped decoder scoring.

## Why our first RL attempt collapsed

Our first v2 SFT warm-start used just **15 optimizer steps**. It achieved 15% synthetic holdout accuracy, then entered a long 340-update GRPO run.

Within failed rollout groups, false abstention could receive a smaller penalty than malformed output or a stale answer. Relative optimization reinforced that fallback. The resulting policy predicted abstention on **309/400 synthetic questions**, with **0% stale catch**.

More SFT initially looked like the obvious answer. Four epochs and 120 updates reached **77.25% synthetic / 76.00% repo-style accuracy**. But the following RL pilot accepted only **6/72 groups**: 62 of 66 rejected zero-variance groups contained identical assistant-token sequences. This demonstrated a sampled-diversity bottleneck, not proof that we had measured the model’s full-distribution entropy.

![Training journey](https://raw.githubusercontent.com/RevanthAI/OneDesk/main/figures/3_training_journey.png)

## The working recipe: protocol warmup, then selective RL

We stopped SFT at **two epochs / 60 steps**. The model had learned the tool protocol while leaving more variation in sampled trajectories.

Our final GRPO recipe combined:

- A stronger penalty for false abstention on answerable tasks.
- Partial credit for retrieving the required evidence when final synthesis is still wrong.
- Positive-anchor filtering: answerable groups need reward variation and at least one positive-reward rollout before an optimizer update.
- Six rollouts per group, a 7:1 answerable-to-abstention rotation, and validation monitoring with an abstention-collapse guard.

The smoke gate accepted **5/9 groups**; the full run accepted **80/342**. Validation selected **update 40**, at **80.0% exact accuracy**, after the full schedule completed 80 active updates.

| Combined holdout metric | Base | Two-epoch warmup | Four-epoch SFT | Final OneDesk |
| --- | --- | --- | --- | --- |
| Exact outcome · 500 tasks | 0.4% | 70.8% | **77.0%** | 74.8% |
| Strict stale catch · 250 conflicts | 0.0% | 70.4% | 61.2% | **75.6%** |
| Verified citation F1 · 425 evidence tasks | 0.0% | 88.3% | **93.2%** | 87.6% |
| Valid structured final answer · 500 tasks | 70.0% | 100.0% | 100.0% | 100.0% |
| Required-chain compliance · 425 answerable tasks | 0.0% | 93.2% | **97.6%** | 84.0% |

AuditKIT separately records **100% tool-call validity for all three trained stages**. Pooled values use each metric’s eligible-task denominator.

For strict stale catch, final GRPO beats four-epoch SFT by **+15.5 pp [95% CI +5.5, +26.0]** on synthetic and **+10.0 pp [+2.0, +20.4]** on repo-style. These are paired semantic-case cluster-bootstrap intervals. They are split-specific; we do not attach an invented pooled confidence interval to the 14.4-point aggregate gain.

The trade-off matters. Full SFT remains better on overall accuracy and exhaustive chain compliance. Overall paired holdout gains over warmup include zero, and warmup length, temperature and group size changed together. Repeated validation selection and one completed recipe need confirmation with more seeds and fresh cases.

## Inspect the evidence in the public Space

The [OneDesk Space](https://huggingface.co/spaces/Revanth-ml/OneDesk) exposes **2,500 recorded episodes: five checkpoints × 500 questions**.

1. Select a language, task kind or flagship example and inspect its saved trace instantly.
2. Compare Base, collapsed RL, full SFT and final OneDesk on exactly the same question.
3. Explore G=6 rollout groups, rewards and advantages in the embedded journals.
4. Adjust the ROI calculator or run a fresh model answer through the real SQLite/MCP sandbox.

Recorded traces are explicitly labeled. Edited questions or server selections are live sandbox experiments and disable frozen benchmark badges. Live inference loads pinned weights only when requested and requires the host to configure accepted access to the gated base; model downloads and hardware availability affect first-run latency. Recorded traces work independently of that model-access setup. The deployment smoke tests use a scripted model boundary to verify the real tool loop without pretending those checks are model evaluations.

The released adapter is [`Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val`](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val).

## What would it cost to run internally?

![ROI scenarios](https://raw.githubusercontent.com/RevanthAI/OneDesk/main/figures/4_cost_and_privacy_roi.png)

At **100,000 audits/month**, our saved throughput and token-volume scenario gives:

| Serving option | Estimated monthly cost | Basis |
| --- | --- | --- |
| Owned RTX 2070 workstation, NF4 | $8.00 | Electricity only; $0 API fees |
| Self-hosted L40S, BF16 | $122.36 | Measured batched throughput at $1.80/GPU-hour |
| GPT-4o historical price scenario | $1,316.66 | About 4,653 input and 153 generated tokens per multi-turn episode |

These are serving scenarios, not hardware or staffing-inclusive TCO. API quality was not benchmarked. The **3.15 GiB local VRAM measurement comes from the v1 NF4 adapter**, while final v2 benchmark accuracy comes from cloud BF16. Keeping enterprise evidence private also requires controlled connectors and logs; a public synthetic demonstration is not a private production deployment.

## What we would do next

We would prioritize complete three-source evidence trails, unplugged-database handling, matched-compute ablations and multi-seed confirmation. We would also replace constructed repo-style fixtures with source-backed historical drift cases before making claims about live OSS transfer.

All generators, datasets, toolkit integrations, training and evaluations were built during the hackathon. Code is **Apache-2.0**, original synthetic data **CC-BY-4.0**, and base/model adapters **CC-BY-NC-4.0**, including their noncommercial restrictions. OneDesk is our research prototype, unrelated to the commercial OneDesk helpdesk product.

**[Try the Space](https://huggingface.co/spaces/Revanth-ml/OneDesk)** · **[Read the complete report](https://github.com/RevanthAI/OneDesk/blob/main/docs/FULL_REPORT.md)** · **[Inspect the submission dossier](https://github.com/RevanthAI/OneDesk/blob/main/docs/SUBMISSION_DOSSIER.md)**

Built by [@Revanth-ml](https://huggingface.co/Revanth-ml).
