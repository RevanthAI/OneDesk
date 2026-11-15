---
license: cc-by-4.0
language:
- en
- hi
- te
tags:
- synthetic
- agenttune
- curatorkit
- auditkit
- mcp
- tool-calling
- multilingual
task_categories:
- question-answering
- text-generation
---

# OneDesk — Recorded experiment runs and diagnostics

## Overview

OneDesk studies a small multilingual assistant that answers current company-knowledge questions across a **nine-server MCP environment**: `notion-mcp`, `github-mcp`, `slack-mcp`, `db-mcp`, `time-mcp`, `unit-converter-mcp`, `math-mcp`, `weather-mcp`, and `calendar-mcp`.

Structured Python facts determine gold answers before language rendering. Tasks cover consistent settings, stale runbooks, incident cost/configuration chains, and missing-entity or unplugged-source abstention. Scope-aware retrieval mixes production records with newer `[STAGING-ONLY]` and sibling distractors. SQLite SELECT and deterministic utility calculations execute as real local tools.

This is a **run-artifact repository**, not a six-split dataset viewer. Its companion benchmark has the six splits below; run prefixes contain summaries, trajectories, provenance and dashboards. The synthetic query splits live in the separate frozen-data repository.

## Companion split table — 1,700 curated rendered tasks

| Companion benchmark split | Rows | Semantic cases |
| --- | --- | --- |
| train_sft_240.jsonl | 240 | 60 |
| train_grpo_stage1.jsonl | 400 | 100 |
| train_grpo_stage2.jsonl | 480 | 120 |
| val_train_80.jsonl | 80 | 20 |
| holdout_synth_400_frozen.jsonl | 400 | 100 |
| holdout_repo_style_100_frozen.jsonl | 100 | 26 |

The train world has 60 services, 80 incidents and 320 semantic cases: 300 allocated plus 20 reserved. Training phases, validation and holdouts have disjoint case IDs, service-parameter pairs and incident IDs. Script styles are `en:latin`, `hi:native`, `hi:latin`, `hinglish:latin`, `te:native` and `te:latin`.

## Curation and verification

CuratorKIT 0.1.21 processed **1,955 candidates**, retained **1,700**, and logged **255 rejected injected exact duplicates**. This validates exact deduplication, not semantic paraphrase filtering. The maximum SFT trajectory measured 2,359 tokens; the 2,560-token training budget preserves all 240 oracle conversations without truncation. Training/evaluation never regenerates the frozen inputs.

## Schema

| Field | Meaning |
| --- | --- |
| `task_id`, `case_id` | Unique rendered query and shared semantic-case identifier |
| `world_split`, `pool`, `schema_version` | World, phase case pool, schema version 2 |
| `question`, `language`, `script` | User text, en/hi/hinglish/te register and native/Latin script |
| `prompt` | System instructions, active schemas and user query; model-visible input |
| `messages` | Full oracle SFT conversation, including tool calls, observations and final response, when present |
| `kind`, `incident_subtype` | consistent/conflict/incident/abstain; SLA, payload or config-audit subtype |
| `service_name`, `param_name`, `incident_id` | Entity/parameter or incident selectors |
| `active_mcps`, `required_mcps`, `distractor_mcps` | Available tool interfaces, gold-required chain and routing distractors |
| `expected_status`, `gold_value`, `gold_cites` | Deterministic target status, normalized scalar and supporting IDs |
| `stale_doc_id`, `stale_trap_value` | Stale page identifier and outdated scalar trap |
| `oracle_optimal_steps`, `reference_tool_sequence` | Measured discovery-policy call length and reference sequence |

Run records additionally include raw assistant turns, messages, calls/outputs, retrieved IDs, predictions, completion reasons, rewards, token masks, group eligibility and optimizer/validation logs. Record types vary by historical run version. The oracle length is a measured policy length, not a proof of global optimality.

Tool protocol:

```xml
<tool_call>{"server":"db-mcp","tool":"query_db","arguments":{"sql":"SELECT incident_id FROM production_incidents LIMIT 1"}}</tool_call>
<final_answer>{"status":"answered","value":16,"cites":["retrieved-id"],"stale_source":null}</final_answer>
```

## Checksums and provenance

The frozen data directory has 19 locked files, including a 15-artifact `SHA256SUMS`. The split hashes are:

| JSONL artifact | SHA-256 |
| --- | --- |
| train_sft_240.jsonl | `96402f7d8ce8f05ee98aee212f1af9ac7a2b51fef1098e2beda3e395b90e1932` |
| train_grpo_stage1.jsonl | `b44e67d78d2abc921583c535a10c3a2bd790aca8fd43723e87151c0c962b7768` |
| train_grpo_stage2.jsonl | `8d7f5236f1fad9450f5ae3ecb81e83b9acda96f01d548225787b7f7eb5754977` |
| val_train_80.jsonl | `4eb608f1391596afe2ad62f67e9c5a68e5b396838b8c97f130638d9510f3b254` |
| holdout_synth_400_frozen.jsonl | `82b92badc6f1fdc71bba41a876db4adf9f19633108b26331297227a7587ac50b` |
| holdout_repo_style_100_frozen.jsonl | `c6d808482bb85143b08eda51e6703f13f9f0817dd0b30a90ca3cd2d81e8b3469` |

Repository owner: [@Revanth-ml](https://huggingface.co/Revanth-ml). [Frozen data](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-v2-data) · [Final study artifacts](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-warmup-runs).

## Limitations

Facts and repo-style fixtures are synthetic. Configuration values are split by modulo-3 residue; template translations are correlated. Reviewed holdouts and repeated validation selection do not constitute a fresh confirmation study. No real company data, live Notion/Slack/GitHub network connector, or independently verified OSS drift transfer is claimed.

## Licensing

Our original synthetic benchmark data and original dataset annotations are licensed under **CC-BY-4.0**. Attribution: **OneDesk contributors / Revanth-ml**. Original project code is licensed under **Apache-2.0**; model weights and adapters retain **CC BY-NC 4.0**, and bundled third-party code retains its own license. These terms are recorded outside the immutable data files; benchmark contents and checksums are unchanged. CC-BY-4.0 terms: https://creativecommons.org/licenses/by/4.0/. Apache-2.0 terms: https://www.apache.org/licenses/LICENSE-2.0.

## Published collections

**Model Collection:** [Revanth-ml/onedesk-models-and-experimental-controls](https://huggingface.co/collections/Revanth-ml/onedesk-models-and-experimental-controls-6af97221a617ddc3326204a6)

**Data Collection:** [Revanth-ml/onedesk-data-and-experiment-evidence](https://huggingface.co/collections/Revanth-ml/onedesk-data-and-experiment-evidence-6af97225c0f1dc548b9ba8ce)
