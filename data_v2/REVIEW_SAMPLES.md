# DriftGuard-MCP v2 — review before training

**Status: data/environment/oracle verification only. No v2 model training, inference benchmark, or paid job has run. Review this file before approving experiments.**

## Counts and separation

| Dataset | Rows | Semantic cases | consistent / incident / conflict / abstain |
|---|---:|---:|---|
| train_sft_240.jsonl | 240 | 60 | 60 / 60 / 60 / 60 |
| train_grpo_stage1.jsonl | 400 | 100 | 100 / 100 / 100 / 100 |
| train_grpo_stage2.jsonl | 480 | 120 | 120 / 120 / 120 / 120 |
| val_train_80.jsonl | 80 | 20 | 20 / 20 / 20 / 20 |
| holdout_synth_400_frozen.jsonl | 400 | 100 | 80 / 60 / 200 / 60 |
| holdout_repo_style_100_frozen.jsonl | 100 | 26 | 20 / 15 / 50 / 15 |

The four named training splits allocate 300 semantic cases. Twenty additional cases remain unused in `train_reserved`, bringing the train-world pool to 320. They are not silently added to SFT or GRPO. Every pair of the six named datasets has zero case-ID, service/parameter-pair and non-null incident-ID overlap. The train world contains 60 services and 80 incidents. Services can still share other parameters across training pools; full DB rows may expose those values. Pair-disjoint questions do not imply isolated information universes.

The OSS-style mix is exactly 50 conflict / 20 consistent / 15 incident / 15 abstention rows and 25 rows per language. This requires 26 cases and four omitted translations, because 50 and 15 are not divisible by four. It remains a constructed fixture, not verified upstream repository history.

## Audit changes and boundaries

1. Separate SFT, stage-1, stage-2 and validation case pools, plus 20 unused reserve cases. Case metadata is checked against underlying service/parameter and incident identities, not merely renamed IDs.
2. User questions contain no MCP tool names or spelled-out tool sequence. Both deployment channels are active. No source-server label is used by the discovery oracle. The oracle reads runbook hints, filters production scope and follows cross-channel observations. Exactly 24/80 main conflict cases in the complete train pool have an older override followed by a newer override in the other channel; subset percentages vary.
3. Missing services use realistic names with no `unknown-` marker. They are checked absent from the service registry. Missing and unplugged requests remain distinct cases.
4. Incident start times, durations, rates and payloads vary. Cost requests start from an incident ID only. References execute elapsed-time penalty, incident-to-config discovery, kg-to-lb recovery, and decimal-GB-to-MiB recovery chains.
5. Every initial/current/intermediate/staging configuration value is within its parameter domain. Small-domain values are separated between worlds by residues modulo three rather than huge numeric offsets; this remains a synthetic artifact.
6. Search returns up to three query-ranked results, including staging and sibling distractors. Newer staging records can rank first. A wrong channel can return only irrelevant records, requiring filtering and fallback. Ranking uses query/record content, not gold labels.
7. Real CuratorKIT exact deduplication removes deliberately injected duplicate controls (15% extra candidates). Rejected candidate provenance is retained. These are not naturally occurring defects and do not establish semantic paraphrase deduplication. AgentTune trajectory rewards are computed from verified episodes, not set to zero. Hindi/Telugu include native and romanized scripts with multiple conflict phrasings; independent native-speaker review remains necessary.

## What the model sees

Only `prompt` (system/tool schemas plus the natural user request), followed by tool observations during interaction. SFT additionally learns from `messages`, the verified reference conversation. Gold values, expected status, source histories, case IDs, reference tool sequences and reward fields are grader/training bookkeeping; they must never be concatenated into inference prompts.

No prompt gives incident timestamps, penalty rates, affected service, payload amount or the channel holding the answer. Generic system instructions define the protocol and production scope. Oracle rewards are 1.0 for correct abstentions, 1.3 for ordinary fully evidenced answers and 1.5 for fully evidenced conflicts under the existing formula; they cannot honestly all be 1.35–1.50.

## Closed-loop example: input, retrieved distractors, decisions, outcome

### Model-visible initial input

```json
[
  {
    "role": "system",
    "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]"
  },
  {
    "role": "user",
    "content": "What is the active production circuit_breaker_pct for cart-ledger? Compare the runbook with deployment records and flag any outdated page."
  }
]
```

### Verified interaction (real v2 tools, including all returned distractors)

```json
{
  "prediction": {
    "status": "conflict_resolved",
    "value": 16,
    "cites": [
      "NOTION-V2-TR-017",
      "PR-V2-TR-017"
    ],
    "stale_source": "NOTION-V2-TR-017"
  },
  "final_text": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 16, \"cites\": [\"NOTION-V2-TR-017\", \"PR-V2-TR-017\"], \"stale_source\": \"NOTION-V2-TR-017\"}</final_answer>",
  "messages": [
    {
      "role": "system",
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]"
    },
    {
      "role": "user",
      "content": "What is the active production circuit_breaker_pct for cart-ledger? Compare the runbook with deployment records and flag any outdated page."
    },
    {
      "role": "assistant",
      "content": "<tool_call>{\"server\": \"notion-mcp\", \"tool\": \"search_notion\", \"arguments\": {\"query\": \"cart-ledger circuit_breaker_pct current configuration runbook\"}}</tool_call>"
    },
    {
      "role": "user",
      "content": "Tool result: [{\"page_id\": \"NOTION-V2-TR-017-STG\", \"service_name\": \"cart-ledger\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"cart-ledger [STAGING-ONLY] circuit_breaker_pct\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"cart-ledger [STAGING-ONLY] circuit_breaker_pct = 52. Staging-only trial; do not apply this setting to production.\"}, {\"page_id\": \"NOTION-V2-TR-017\", \"service_name\": \"cart-ledger\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"prod\", \"title\": \"cart-ledger [PROD] circuit_breaker_pct\", \"updated_at\": \"2026-02-05T09:30:00+00:00\", \"snippet\": \"cart-ledger [PROD] circuit_breaker_pct = 67. Production runbook at publication.\"}, {\"page_id\": \"NOTION-V2-TR-317-STG\", \"service_name\": \"transfer-ledger\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"transfer-ledger [STAGING-ONLY] circuit_breaker_pct\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"transfer-ledger [STAGING-ONLY] circuit_breaker_pct = 40. Staging-only trial; do not apply this setting to production.\"}]"
    },
    {
      "role": "assistant",
      "content": "<tool_call>{\"server\": \"github-mcp\", \"tool\": \"search_github_prs\", \"arguments\": {\"query\": \"cart-ledger circuit_breaker_pct\"}}</tool_call>"
    },
    {
      "role": "user",
      "content": "Tool result: [{\"service_name\": \"cart-ledger\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"cart-ledger [STAGING-ONLY] circuit_breaker_pct\", \"pr_id\": \"PR-V2-TR-017-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"cart-ledger [STAGING-ONLY] circuit_breaker_pct = 52. Staging test; this is not a production setting.\"}, {\"service_name\": \"cart-ledger\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"prod\", \"title\": \"cart-ledger [PROD] circuit_breaker_pct\", \"pr_id\": \"PR-V2-TR-017\", \"merged_at\": \"2026-09-17T14:00:00+00:00\", \"summary\": \"cart-ledger [PROD] circuit_breaker_pct = 16. Production deployment verified.\"}, {\"service_name\": \"transfer-ledger\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"transfer-ledger [STAGING-ONLY] circuit_breaker_pct\", \"pr_id\": \"PR-V2-TR-317-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"transfer-ledger [STAGING-ONLY] circuit_breaker_pct = 40. Staging test; this is not a production setting.\"}]"
    },
    {
      "role": "assistant",
      "content": "<tool_call>{\"server\": \"slack-mcp\", \"tool\": \"search_slack\", \"arguments\": {\"query\": \"cart-ledger circuit_breaker_pct\"}}</tool_call>"
    },
    {
      "role": "user",
      "content": "Tool result: [{\"service_name\": \"cart-ledger\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"cart-ledger [STAGING-ONLY] circuit_breaker_pct\", \"msg_id\": \"SLACK-V2-TR-017-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"cart-ledger [STAGING-ONLY] circuit_breaker_pct = 52. Staging test; this is not a production setting.\"}, {\"service_name\": \"transfer-ledger\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"transfer-ledger [STAGING-ONLY] circuit_breaker_pct\", \"msg_id\": \"SLACK-V2-TR-317-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"transfer-ledger [STAGING-ONLY] circuit_breaker_pct = 40. Staging test; this is not a production setting.\"}, {\"service_name\": \"ledger-writer\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"ledger-writer [STAGING-ONLY] circuit_breaker_pct\", \"msg_id\": \"SLACK-V2-TR-275-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"ledger-writer [STAGING-ONLY] circuit_breaker_pct = 64. Staging test; this is not a production setting.\"}]"
    },
    {
      "role": "assistant",
      "content": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 16, \"cites\": [\"NOTION-V2-TR-017\", \"PR-V2-TR-017\"], \"stale_source\": \"NOTION-V2-TR-017\"}</final_answer>"
    }
  ],
  "num_tool_calls": 3,
  "retrieved_ids": [
    "NOTION-V2-TR-017",
    "NOTION-V2-TR-017-STG",
    "NOTION-V2-TR-317-STG",
    "PR-V2-TR-017",
    "PR-V2-TR-017-STG",
    "PR-V2-TR-317-STG",
    "SLACK-V2-TR-017-STG",
    "SLACK-V2-TR-275-STG",
    "SLACK-V2-TR-317-STG"
  ],
  "calls": [
    {
      "server": "notion-mcp",
      "tool": "search_notion",
      "arguments": {
        "query": "cart-ledger circuit_breaker_pct current configuration runbook"
      },
      "output": [
        {
          "page_id": "NOTION-V2-TR-017-STG",
          "service_name": "cart-ledger",
          "param_name": "circuit_breaker_pct",
          "environment": "staging",
          "title": "cart-ledger [STAGING-ONLY] circuit_breaker_pct",
          "updated_at": "2026-10-25T18:30:00+00:00",
          "snippet": "cart-ledger [STAGING-ONLY] circuit_breaker_pct = 52. Staging-only trial; do not apply this setting to production."
        },
        {
          "page_id": "NOTION-V2-TR-017",
          "service_name": "cart-ledger",
          "param_name": "circuit_breaker_pct",
          "environment": "prod",
          "title": "cart-ledger [PROD] circuit_breaker_pct",
          "updated_at": "2026-02-05T09:30:00+00:00",
          "snippet": "cart-ledger [PROD] circuit_breaker_pct = 67. Production runbook at publication."
        },
        {
          "page_id": "NOTION-V2-TR-317-STG",
          "service_name": "transfer-ledger",
          "param_name": "circuit_breaker_pct",
          "environment": "staging",
          "title": "transfer-ledger [STAGING-ONLY] circuit_breaker_pct",
          "updated_at": "2026-10-25T18:30:00+00:00",
          "snippet": "transfer-ledger [STAGING-ONLY] circuit_breaker_pct = 40. Staging-only trial; do not apply this setting to production."
        }
      ]
    },
    {
      "server": "github-mcp",
      "tool": "search_github_prs",
      "arguments": {
        "query": "cart-ledger circuit_breaker_pct"
      },
      "output": [
        {
          "service_name": "cart-ledger",
          "param_name": "circuit_breaker_pct",
          "environment": "staging",
          "title": "cart-ledger [STAGING-ONLY] circuit_breaker_pct",
          "pr_id": "PR-V2-TR-017-STG",
          "merged_at": "2026-10-26T19:00:00+00:00",
          "summary": "cart-ledger [STAGING-ONLY] circuit_breaker_pct = 52. Staging test; this is not a production setting."
        },
        {
          "service_name": "cart-ledger",
          "param_name": "circuit_breaker_pct",
          "environment": "prod",
          "title": "cart-ledger [PROD] circuit_breaker_pct",
          "pr_id": "PR-V2-TR-017",
          "merged_at": "2026-09-17T14:00:00+00:00",
          "summary": "cart-ledger [PROD] circuit_breaker_pct = 16. Production deployment verified."
        },
        {
          "service_name": "transfer-ledger",
          "param_name": "circuit_breaker_pct",
          "environment": "staging",
          "title": "transfer-ledger [STAGING-ONLY] circuit_breaker_pct",
          "pr_id": "PR-V2-TR-317-STG",
          "merged_at": "2026-10-26T19:00:00+00:00",
          "summary": "transfer-ledger [STAGING-ONLY] circuit_breaker_pct = 40. Staging test; this is not a production setting."
        }
      ]
    },
    {
      "server": "slack-mcp",
      "tool": "search_slack",
      "arguments": {
        "query": "cart-ledger circuit_breaker_pct"
      },
      "output": [
        {
          "service_name": "cart-ledger",
          "param_name": "circuit_breaker_pct",
          "environment": "staging",
          "title": "cart-ledger [STAGING-ONLY] circuit_breaker_pct",
          "msg_id": "SLACK-V2-TR-017-STG",
          "channel": "#staging",
          "posted_at": "2026-10-26T19:00:00+00:00",
          "text": "cart-ledger [STAGING-ONLY] circuit_breaker_pct = 52. Staging test; this is not a production setting."
        },
        {
          "service_name": "transfer-ledger",
          "param_name": "circuit_breaker_pct",
          "environment": "staging",
          "title": "transfer-ledger [STAGING-ONLY] circuit_breaker_pct",
          "msg_id": "SLACK-V2-TR-317-STG",
          "channel": "#staging",
          "posted_at": "2026-10-26T19:00:00+00:00",
          "text": "transfer-ledger [STAGING-ONLY] circuit_breaker_pct = 40. Staging test; this is not a production setting."
        },
        {
          "service_name": "ledger-writer",
          "param_name": "circuit_breaker_pct",
          "environment": "staging",
          "title": "ledger-writer [STAGING-ONLY] circuit_breaker_pct",
          "msg_id": "SLACK-V2-TR-275-STG",
          "channel": "#staging",
          "posted_at": "2026-10-26T19:00:00+00:00",
          "text": "ledger-writer [STAGING-ONLY] circuit_breaker_pct = 64. Staging test; this is not a production setting."
        }
      ]
    }
  ],
  "tool_format_error": false
}
```

## File samples

Ten complete records per JSONL file follow, stratified where possible across task/language. JSON files contain up to ten entries per list, with scalar/dictionary metadata retained. Excerpts of world collections are not complete runnable worlds. Source rows are 1-based and all copied fields are unchanged.

---

# File: `AUDIT.json`

Source SHA-256: `5316e6e04bb476181e826ba9a23229440595f9e892ac628cd50b8be00fe1e35b`

```json
{
  "causal_claim": "The audit identified plausible confounds, not proven causes of the prior accuracy or zero-variance groups.",
  "datasets": {
    "holdout_repo_style_100_frozen": {
      "incident_subtypes": {
        "config_audit": 4,
        "payload_lb": 4,
        "payload_mib": 3,
        "sla_penalty": 4
      },
      "injected_duplicate_controls": 15,
      "input": 115,
      "kept": 100,
      "kinds": {
        "abstain": 15,
        "conflict": 50,
        "consistent": 20,
        "incident": 15
      },
      "languages": {
        "en": 25,
        "hi": 25,
        "hinglish": 25,
        "te": 25
      },
      "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
      "oracle_verified": 100,
      "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
      "rejected": 15,
      "scripts": {
        "en:latin": 25,
        "hi:latin": 12,
        "hi:native": 13,
        "hinglish:latin": 25,
        "te:latin": 12,
        "te:native": 13
      },
      "semantic_cases": 26,
      "semantic_dedup": false
    },
    "holdout_synth_400_frozen": {
      "incident_subtypes": {
        "config_audit": 16,
        "payload_lb": 16,
        "payload_mib": 12,
        "sla_penalty": 16
      },
      "injected_duplicate_controls": 60,
      "input": 460,
      "kept": 400,
      "kinds": {
        "abstain": 60,
        "conflict": 200,
        "consistent": 80,
        "incident": 60
      },
      "languages": {
        "en": 100,
        "hi": 100,
        "hinglish": 100,
        "te": 100
      },
      "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
      "oracle_verified": 400,
      "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
      "rejected": 60,
      "scripts": {
        "en:latin": 100,
        "hi:latin": 50,
        "hi:native": 50,
        "hinglish:latin": 100,
        "te:latin": 50,
        "te:native": 50
      },
      "semantic_cases": 100,
      "semantic_dedup": false
    },
    "train_grpo_stage1": {
      "incident_subtypes": {
        "config_audit": 24,
        "payload_lb": 24,
        "payload_mib": 28,
        "sla_penalty": 24
      },
      "injected_duplicate_controls": 60,
      "input": 460,
      "kept": 400,
      "kinds": {
        "abstain": 100,
        "conflict": 100,
        "consistent": 100,
        "incident": 100
      },
      "languages": {
        "en": 100,
        "hi": 100,
        "hinglish": 100,
        "te": 100
      },
      "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
      "oracle_verified": 400,
      "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
      "rejected": 60,
      "scripts": {
        "en:latin": 100,
        "hi:latin": 50,
        "hi:native": 50,
        "hinglish:latin": 100,
        "te:latin": 50,
        "te:native": 50
      },
      "semantic_cases": 100,
      "semantic_dedup": false
    },
    "train_grpo_stage2": {
      "incident_subtypes": {
        "config_audit": 32,
        "payload_lb": 28,
        "payload_mib": 28,
        "sla_penalty": 32
      },
      "injected_duplicate_controls": 72,
      "input": 552,
      "kept": 480,
      "kinds": {
        "abstain": 120,
        "conflict": 120,
        "consistent": 120,
        "incident": 120
      },
      "languages": {
        "en": 120,
        "hi": 120,
        "hinglish": 120,
        "te": 120
      },
      "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
      "oracle_verified": 480,
      "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
      "rejected": 72,
      "scripts": {
        "en:latin": 120,
        "hi:latin": 60,
        "hi:native": 60,
        "hinglish:latin": 120,
        "te:latin": 60,
        "te:native": 60
      },
      "semantic_cases": 120,
      "semantic_dedup": false
    },
    "train_sft_240": {
      "incident_subtypes": {
        "config_audit": 16,
        "payload_lb": 16,
        "payload_mib": 12,
        "sla_penalty": 16
      },
      "injected_duplicate_controls": 36,
      "input": 276,
      "kept": 240,
      "kinds": {
        "abstain": 60,
        "conflict": 60,
        "consistent": 60,
        "incident": 60
      },
      "languages": {
        "en": 60,
        "hi": 60,
        "hinglish": 60,
        "te": 60
      },
      "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
      "oracle_verified": 240,
      "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
      "rejected": 36,
      "scripts": {
        "en:latin": 60,
        "hi:latin": 30,
        "hi:native": 30,
        "hinglish:latin": 60,
        "te:latin": 30,
        "te:native": 30
      },
      "semantic_cases": 60,
      "semantic_dedup": false
    },
    "val_train_80": {
      "incident_subtypes": {
        "config_audit": 4,
        "payload_lb": 8,
        "payload_mib": 4,
        "sla_penalty": 4
      },
      "injected_duplicate_controls": 12,
      "input": 92,
      "kept": 80,
      "kinds": {
        "abstain": 20,
        "conflict": 20,
        "consistent": 20,
        "incident": 20
      },
      "languages": {
        "en": 20,
        "hi": 20,
        "hinglish": 20,
        "te": 20
      },
      "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
      "oracle_verified": 80,
      "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
      "rejected": 12,
      "scripts": {
        "en:latin": 20,
        "hi:latin": 10,
        "hi:native": 10,
        "hinglish:latin": 20,
        "te:latin": 10,
        "te:native": 10
      },
      "semantic_cases": 20,
      "semantic_dedup": false
    }
  },
  "disjoint_splits": {
    "holdout_synth_400_frozen vs holdout_repo_style_100_frozen": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_grpo_stage1 vs holdout_repo_style_100_frozen": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_grpo_stage1 vs holdout_synth_400_frozen": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_grpo_stage1 vs train_grpo_stage2": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_grpo_stage1 vs val_train_80": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_grpo_stage2 vs holdout_repo_style_100_frozen": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_grpo_stage2 vs holdout_synth_400_frozen": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_grpo_stage2 vs val_train_80": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_sft_240 vs holdout_repo_style_100_frozen": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_sft_240 vs holdout_synth_400_frozen": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_sft_240 vs train_grpo_stage1": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_sft_240 vs train_grpo_stage2": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "train_sft_240 vs val_train_80": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "val_train_80 vs holdout_repo_style_100_frozen": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    },
    "val_train_80 vs holdout_synth_400_frozen": {
      "case_id_overlap": 0,
      "incident_id_overlap": 0,
      "service_parameter_overlap": 0
    }
  },
  "inference_claim": "No v2 model accuracy is available; no attempt is made to force SFT below an arbitrary accuracy threshold.",
  "oracle_rewards": {
    "1.0": 60,
    "1.3": 112,
    "1.5": 68
  },
  "paid_jobs_launched": false,
  "repo_style_partial_translations": 4,
  "repo_style_semantic_cases": 26,
  "reserved_cases": 20,
  "schema_version": 2,
  "training_allocated_cases": 300,
  "training_launched": false,
  "training_requested_total": 320,
  "training_world_incidents": 80,
  "training_world_services": 60
}
```

---

# File: `case_pool_manifest.json`

Source SHA-256: `51612d5c14ed2a9fcf930825d042da23ad59870665ced07a54a0c6c558b3e0e3`

```json
{
  "train_grpo1": [
    {
      "case_id": "train_grpo1-0000",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "sla_hours",
      "service_name": "metrics-agent"
    },
    {
      "case_id": "train_grpo1-0001",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "batch_size_mb",
      "service_name": "fee-engine"
    },
    {
      "case_id": "train_grpo1-0002",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "timeout_sec",
      "service_name": "mandate-store"
    },
    {
      "case_id": "train_grpo1-0003",
      "incident_id": "INC-V2-TR-015",
      "kind": "incident",
      "param_name": "recovery_cost_mib_usd",
      "service_name": "export-worker"
    },
    {
      "case_id": "train_grpo1-0004",
      "incident_id": "INC-V2-TR-016",
      "kind": "incident",
      "param_name": "sla_penalty_usd",
      "service_name": "loyalty-api"
    },
    {
      "case_id": "train_grpo1-0005",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "sla_hours",
      "service_name": "media-worker"
    },
    {
      "case_id": "train_grpo1-0006",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "circuit_breaker_pct",
      "service_name": "ledger-writer"
    },
    {
      "case_id": "train_grpo1-0007",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "rate_limit_rpm",
      "service_name": "signing-gateway"
    },
    {
      "case_id": "train_grpo1-0008",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "batch_size_mb",
      "service_name": "event-router"
    },
    {
      "case_id": "train_grpo1-0009",
      "incident_id": "INC-V2-TR-017",
      "kind": "incident",
      "param_name": "max_retries",
      "service_name": "product-catalog"
    }
  ],
  "train_grpo2": [
    {
      "case_id": "train_grpo2-0000",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "batch_size_mb",
      "service_name": "refund-worker"
    },
    {
      "case_id": "train_grpo2-0001",
      "incident_id": "INC-V2-TR-040",
      "kind": "incident",
      "param_name": "sla_penalty_usd",
      "service_name": "export-worker"
    },
    {
      "case_id": "train_grpo2-0002",
      "incident_id": null,
      "kind": "abstain",
      "param_name": "circuit_breaker_pct",
      "service_name": "swift-hedger"
    },
    {
      "case_id": "train_grpo2-0003",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "sla_hours",
      "service_name": "customer-vault"
    },
    {
      "case_id": "train_grpo2-0004",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "max_retries",
      "service_name": "analytics-sink"
    },
    {
      "case_id": "train_grpo2-0005",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "batch_size_mb",
      "service_name": "ledger-writer"
    },
    {
      "case_id": "train_grpo2-0006",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "batch_size_mb",
      "service_name": "metrics-agent"
    },
    {
      "case_id": "train_grpo2-0007",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "batch_size_mb",
      "service_name": "search-indexer"
    },
    {
      "case_id": "train_grpo2-0008",
      "incident_id": null,
      "kind": "abstain",
      "param_name": "rate_limit_rpm",
      "service_name": "email-relay"
    },
    {
      "case_id": "train_grpo2-0009",
      "incident_id": null,
      "kind": "abstain",
      "param_name": "timeout_sec",
      "service_name": "swift-gate"
    }
  ],
  "train_reserved": [
    {
      "case_id": "train_reserved-0000",
      "incident_id": "INC-V2-TR-075",
      "kind": "incident",
      "param_name": "recovery_cost_mib_usd",
      "service_name": "profile-store"
    },
    {
      "case_id": "train_reserved-0001",
      "incident_id": null,
      "kind": "abstain",
      "param_name": "timeout_sec",
      "service_name": "profile-store"
    },
    {
      "case_id": "train_reserved-0002",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "timeout_sec",
      "service_name": "metrics-agent"
    },
    {
      "case_id": "train_reserved-0003",
      "incident_id": "INC-V2-TR-076",
      "kind": "incident",
      "param_name": "sla_penalty_usd",
      "service_name": "media-worker"
    },
    {
      "case_id": "train_reserved-0004",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "max_retries",
      "service_name": "shipment-router"
    },
    {
      "case_id": "train_reserved-0005",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "timeout_sec",
      "service_name": "fx-router"
    },
    {
      "case_id": "train_reserved-0006",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "max_retries",
      "service_name": "audit-stream"
    },
    {
      "case_id": "train_reserved-0007",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "circuit_breaker_pct",
      "service_name": "upi-gateway"
    },
    {
      "case_id": "train_reserved-0008",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "circuit_breaker_pct",
      "service_name": "attachment-api"
    },
    {
      "case_id": "train_reserved-0009",
      "incident_id": null,
      "kind": "abstain",
      "param_name": "max_retries",
      "service_name": "escrow-relay"
    }
  ],
  "train_sft": [
    {
      "case_id": "train_sft-0000",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "batch_size_mb",
      "service_name": "loyalty-api"
    },
    {
      "case_id": "train_sft-0001",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "sla_hours",
      "service_name": "payment-worker"
    },
    {
      "case_id": "train_sft-0002",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "batch_size_mb",
      "service_name": "email-relay"
    },
    {
      "case_id": "train_sft-0003",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "sla_hours",
      "service_name": "reconciliation-store"
    },
    {
      "case_id": "train_sft-0004",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "circuit_breaker_pct",
      "service_name": "cart-ledger"
    },
    {
      "case_id": "train_sft-0005",
      "incident_id": "INC-V2-TR-000",
      "kind": "incident",
      "param_name": "sla_penalty_usd",
      "service_name": "token-service"
    },
    {
      "case_id": "train_sft-0006",
      "incident_id": "INC-V2-TR-001",
      "kind": "incident",
      "param_name": "timeout_sec",
      "service_name": "fraud-router"
    },
    {
      "case_id": "train_sft-0007",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "timeout_sec",
      "service_name": "vendor-router"
    },
    {
      "case_id": "train_sft-0008",
      "incident_id": null,
      "kind": "abstain",
      "param_name": "rate_limit_rpm",
      "service_name": "forex-hedger"
    },
    {
      "case_id": "train_sft-0009",
      "incident_id": "INC-V2-TR-002",
      "kind": "incident",
      "param_name": "recovery_cost_lb_usd",
      "service_name": "debit-processor"
    }
  ],
  "train_val": [
    {
      "case_id": "train_val-0000",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "circuit_breaker_pct",
      "service_name": "webhook-dispatcher"
    },
    {
      "case_id": "train_val-0001",
      "incident_id": null,
      "kind": "abstain",
      "param_name": "batch_size_mb",
      "service_name": "escrow-vault"
    },
    {
      "case_id": "train_val-0002",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "batch_size_mb",
      "service_name": "invoice-store"
    },
    {
      "case_id": "train_val-0003",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "batch_size_mb",
      "service_name": "export-worker"
    },
    {
      "case_id": "train_val-0004",
      "incident_id": null,
      "kind": "conflict",
      "param_name": "batch_size_mb",
      "service_name": "dispute-api"
    },
    {
      "case_id": "train_val-0005",
      "incident_id": "INC-V2-TR-070",
      "kind": "incident",
      "param_name": "recovery_cost_lb_usd",
      "service_name": "product-catalog"
    },
    {
      "case_id": "train_val-0006",
      "incident_id": null,
      "kind": "abstain",
      "param_name": "timeout_sec",
      "service_name": "ledger-writer"
    },
    {
      "case_id": "train_val-0007",
      "incident_id": null,
      "kind": "abstain",
      "param_name": "batch_size_mb",
      "service_name": "escrow-dispatcher"
    },
    {
      "case_id": "train_val-0008",
      "incident_id": null,
      "kind": "consistent",
      "param_name": "batch_size_mb",
      "service_name": "account-vault"
    },
    {
      "case_id": "train_val-0009",
      "incident_id": null,
      "kind": "abstain",
      "param_name": "sla_hours",
      "service_name": "settlement-worker"
    }
  ]
}
```

---

# File: `curation_funnel.json`

Source SHA-256: `a1e8630f4cc9244ee96d2ab41ab811918417da1b510ee987b54bb9902dcef3da`

```json
{
  "holdout_repo_style_100_frozen": {
    "incident_subtypes": {
      "config_audit": 4,
      "payload_lb": 4,
      "payload_mib": 3,
      "sla_penalty": 4
    },
    "injected_duplicate_controls": 15,
    "input": 115,
    "kept": 100,
    "kinds": {
      "abstain": 15,
      "conflict": 50,
      "consistent": 20,
      "incident": 15
    },
    "languages": {
      "en": 25,
      "hi": 25,
      "hinglish": 25,
      "te": 25
    },
    "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
    "oracle_verified": 100,
    "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
    "rejected": 15,
    "scripts": {
      "en:latin": 25,
      "hi:latin": 12,
      "hi:native": 13,
      "hinglish:latin": 25,
      "te:latin": 12,
      "te:native": 13
    },
    "semantic_cases": 26,
    "semantic_dedup": false
  },
  "holdout_synth_400_frozen": {
    "incident_subtypes": {
      "config_audit": 16,
      "payload_lb": 16,
      "payload_mib": 12,
      "sla_penalty": 16
    },
    "injected_duplicate_controls": 60,
    "input": 460,
    "kept": 400,
    "kinds": {
      "abstain": 60,
      "conflict": 200,
      "consistent": 80,
      "incident": 60
    },
    "languages": {
      "en": 100,
      "hi": 100,
      "hinglish": 100,
      "te": 100
    },
    "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
    "oracle_verified": 400,
    "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
    "rejected": 60,
    "scripts": {
      "en:latin": 100,
      "hi:latin": 50,
      "hi:native": 50,
      "hinglish:latin": 100,
      "te:latin": 50,
      "te:native": 50
    },
    "semantic_cases": 100,
    "semantic_dedup": false
  },
  "train_grpo_stage1": {
    "incident_subtypes": {
      "config_audit": 24,
      "payload_lb": 24,
      "payload_mib": 28,
      "sla_penalty": 24
    },
    "injected_duplicate_controls": 60,
    "input": 460,
    "kept": 400,
    "kinds": {
      "abstain": 100,
      "conflict": 100,
      "consistent": 100,
      "incident": 100
    },
    "languages": {
      "en": 100,
      "hi": 100,
      "hinglish": 100,
      "te": 100
    },
    "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
    "oracle_verified": 400,
    "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
    "rejected": 60,
    "scripts": {
      "en:latin": 100,
      "hi:latin": 50,
      "hi:native": 50,
      "hinglish:latin": 100,
      "te:latin": 50,
      "te:native": 50
    },
    "semantic_cases": 100,
    "semantic_dedup": false
  },
  "train_grpo_stage2": {
    "incident_subtypes": {
      "config_audit": 32,
      "payload_lb": 28,
      "payload_mib": 28,
      "sla_penalty": 32
    },
    "injected_duplicate_controls": 72,
    "input": 552,
    "kept": 480,
    "kinds": {
      "abstain": 120,
      "conflict": 120,
      "consistent": 120,
      "incident": 120
    },
    "languages": {
      "en": 120,
      "hi": 120,
      "hinglish": 120,
      "te": 120
    },
    "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
    "oracle_verified": 480,
    "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
    "rejected": 72,
    "scripts": {
      "en:latin": 120,
      "hi:latin": 60,
      "hi:native": 60,
      "hinglish:latin": 120,
      "te:latin": 60,
      "te:native": 60
    },
    "semantic_cases": 120,
    "semantic_dedup": false
  },
  "train_sft_240": {
    "incident_subtypes": {
      "config_audit": 16,
      "payload_lb": 16,
      "payload_mib": 12,
      "sla_penalty": 16
    },
    "injected_duplicate_controls": 36,
    "input": 276,
    "kept": 240,
    "kinds": {
      "abstain": 60,
      "conflict": 60,
      "consistent": 60,
      "incident": 60
    },
    "languages": {
      "en": 60,
      "hi": 60,
      "hinglish": 60,
      "te": 60
    },
    "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
    "oracle_verified": 240,
    "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
    "rejected": 36,
    "scripts": {
      "en:latin": 60,
      "hi:latin": 30,
      "hi:native": 30,
      "hinglish:latin": 60,
      "te:latin": 30,
      "te:native": 30
    },
    "semantic_cases": 60,
    "semantic_dedup": false
  },
  "val_train_80": {
    "incident_subtypes": {
      "config_audit": 4,
      "payload_lb": 8,
      "payload_mib": 4,
      "sla_penalty": 4
    },
    "injected_duplicate_controls": 12,
    "input": 92,
    "kept": 80,
    "kinds": {
      "abstain": 20,
      "conflict": 20,
      "consistent": 20,
      "incident": 20
    },
    "languages": {
      "en": 20,
      "hi": 20,
      "hinglish": 20,
      "te": 20
    },
    "method": "Real CuratorKIT ExactDeduplicator over model-visible messages",
    "oracle_verified": 80,
    "quality_claim": "Injected exact-duplicate controls only; no claim of semantic paraphrase filtering or natural-data quality gains.",
    "rejected": 12,
    "scripts": {
      "en:latin": 20,
      "hi:latin": 10,
      "hi:native": 10,
      "hinglish:latin": 20,
      "te:latin": 10,
      "te:native": 10
    },
    "semantic_cases": 20,
    "semantic_dedup": false
  }
}
```

---

# File: `curation_rejections.jsonl`

Source SHA-256: `622e3bf8fce40796c64c6b3683bba441e096272ebf02fb83e3a430ae45f5acf2`

## Sample 1 — source line 1

```json
{
  "candidate_id": "train_sft_240-candidate-0240",
  "dataset": "train_sft_240",
  "origin": "injected_exact_duplicate",
  "reason": "duplicate_model_visible_prompt",
  "task_id": "train_sft-0044-hi"
}
```

## Sample 2 — source line 2

```json
{
  "candidate_id": "train_sft_240-candidate-0241",
  "dataset": "train_sft_240",
  "origin": "injected_exact_duplicate",
  "reason": "duplicate_model_visible_prompt",
  "task_id": "train_sft-0045-te"
}
```

## Sample 3 — source line 3

```json
{
  "candidate_id": "train_sft_240-candidate-0242",
  "dataset": "train_sft_240",
  "origin": "injected_exact_duplicate",
  "reason": "duplicate_model_visible_prompt",
  "task_id": "train_sft-0023-hi"
}
```

## Sample 4 — source line 4

```json
{
  "candidate_id": "train_sft_240-candidate-0243",
  "dataset": "train_sft_240",
  "origin": "injected_exact_duplicate",
  "reason": "duplicate_model_visible_prompt",
  "task_id": "train_sft-0050-te"
}
```

## Sample 5 — source line 5

```json
{
  "candidate_id": "train_sft_240-candidate-0244",
  "dataset": "train_sft_240",
  "origin": "injected_exact_duplicate",
  "reason": "duplicate_model_visible_prompt",
  "task_id": "train_sft-0039-hi"
}
```

## Sample 6 — source line 6

```json
{
  "candidate_id": "train_sft_240-candidate-0245",
  "dataset": "train_sft_240",
  "origin": "injected_exact_duplicate",
  "reason": "duplicate_model_visible_prompt",
  "task_id": "train_sft-0014-hinglish"
}
```

## Sample 7 — source line 7

```json
{
  "candidate_id": "train_sft_240-candidate-0246",
  "dataset": "train_sft_240",
  "origin": "injected_exact_duplicate",
  "reason": "duplicate_model_visible_prompt",
  "task_id": "train_sft-0010-te"
}
```

## Sample 8 — source line 8

```json
{
  "candidate_id": "train_sft_240-candidate-0247",
  "dataset": "train_sft_240",
  "origin": "injected_exact_duplicate",
  "reason": "duplicate_model_visible_prompt",
  "task_id": "train_sft-0051-hi"
}
```

## Sample 9 — source line 9

```json
{
  "candidate_id": "train_sft_240-candidate-0248",
  "dataset": "train_sft_240",
  "origin": "injected_exact_duplicate",
  "reason": "duplicate_model_visible_prompt",
  "task_id": "train_sft-0041-te"
}
```

## Sample 10 — source line 245

```json
{
  "candidate_id": "holdout_repo_style_100_frozen-candidate-0104",
  "dataset": "holdout_repo_style_100_frozen",
  "origin": "injected_exact_duplicate",
  "reason": "duplicate_model_visible_prompt",
  "task_id": "holdout_repo_style-0010-hi"
}
```

---

# File: `holdout_repo_style_100_frozen.jsonl`

Source SHA-256: `c6d808482bb85143b08eda51e6703f13f9f0817dd0b30a90ca3cd2d81e8b3469`

## Sample 1 — source line 8

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "holdout_repo_style-0001",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "te",
  "missing_entity": true,
  "oracle_optimal_steps": 1,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "holdout_repo_style",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Ee abhyarthanaku database aadhaaram tappanisari: asgi-hedger yokka circuit_breaker_pct nirnayinchandi; database connection lekapothe leda seva lekapothe viraminchandi.",
      "role": "user"
    }
  ],
  "question": "Ee abhyarthanaku database aadhaaram tappanisari: asgi-hedger yokka circuit_breaker_pct nirnayinchandi; database connection lekapothe leda seva lekapothe viraminchandi.",
  "reference_tool_sequence": [
    "db-mcp__query_db"
  ],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "asgi-hedger",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_repo_style-0001-te",
  "world_split": "repo_style"
}
```

## Sample 2 — source line 29

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "holdout_repo_style-0007",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-OSS-000"
  ],
  "gold_value": 143.0,
  "incident_id": "INC-V2-OSS-000",
  "incident_subtype": "sla_penalty",
  "kind": "incident",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_penalty_usd",
  "pool": "holdout_repo_style",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Assess the USD SLA charge incurred during the outage logged as INC-V2-OSS-000.",
      "role": "user"
    }
  ],
  "question": "Assess the USD SLA charge incurred during the outage logged as INC-V2-OSS-000.",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "time-mcp__hours_between",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "quart-websocket-worker",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_repo_style-0007-en",
  "world_split": "repo_style"
}
```

## Sample 3 — source line 41

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "holdout_repo_style-0010",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-OSS-000",
    "SLACK-V2-OSS-000"
  ],
  "gold_value": 18,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "timeout_sec",
  "pool": "holdout_repo_style",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Determine the deployed timeout_sec of fastapi-gzip-middleware, checking the operational documentation against the release trail. Identify any superseded page.",
      "role": "user"
    }
  ],
  "question": "Determine the deployed timeout_sec of fastapi-gzip-middleware, checking the operational documentation against the release trail. Identify any superseded page.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "fastapi-gzip-middleware",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_repo_style-0010-en",
  "world_split": "repo_style"
}
```

## Sample 4 — source line 47

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "holdout_repo_style-0011",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-OSS-143",
    "PR-V2-OSS-143"
  ],
  "gold_value": 75,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "hinglish",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "holdout_repo_style",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Production review mein prefect-flow-runner ka circuit_breaker_pct verify karna hai; release evidence se jo doc purana nikle use flag karo.",
      "role": "user"
    }
  ],
  "question": "Production review mein prefect-flow-runner ka circuit_breaker_pct verify karna hai; release evidence se jo doc purana nikle use flag karo.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "prefect-flow-runner",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_repo_style-0011-hinglish",
  "world_split": "repo_style"
}
```

## Sample 5 — source line 50

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "holdout_repo_style-0012",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-OSS-177",
    "PR-V2-OSS-177"
  ],
  "gold_value": 18,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "hi",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "batch_size_mb",
  "pool": "holdout_repo_style",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "falcon-api-middleware में production batch_size_mb का प्रभावी मान निर्धारित कीजिए। संचालन निर्देशों को जारी deployment के प्रमाण से मिलाकर पुराने पन्ने का उल्लेख कीजिए।",
      "role": "user"
    }
  ],
  "question": "falcon-api-middleware में production batch_size_mb का प्रभावी मान निर्धारित कीजिए। संचालन निर्देशों को जारी deployment के प्रमाण से मिलाकर पुराने पन्ने का उल्लेख कीजिए।",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "falcon-api-middleware",
  "stale_doc_id": "NOTION-V2-OSS-177",
  "stale_trap_value": 363,
  "task_id": "holdout_repo_style-0012-hi",
  "world_split": "repo_style"
}
```

## Sample 6 — source line 58

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "holdout_repo_style-0014",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-OSS-002"
  ],
  "gold_value": 55.12,
  "incident_id": "INC-V2-OSS-002",
  "incident_subtype": "payload_lb",
  "kind": "incident",
  "language": "hi",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "recovery_cost_lb_usd",
  "pool": "holdout_repo_style",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "INC-V2-OSS-002 में प्रभावित सामग्री के प्रति pound शुल्क पर बहाली का कुल USD बिल निकालिए।",
      "role": "user"
    }
  ],
  "question": "INC-V2-OSS-002 में प्रभावित सामग्री के प्रति pound शुल्क पर बहाली का कुल USD बिल निकालिए।",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "unit-converter-mcp__convert_unit",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "falcon-api-middleware",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_repo_style-0014-hi",
  "world_split": "repo_style"
}
```

## Sample 7 — source line 60

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "holdout_repo_style-0014",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-OSS-002"
  ],
  "gold_value": 55.12,
  "incident_id": "INC-V2-OSS-002",
  "incident_subtype": "payload_lb",
  "kind": "incident",
  "language": "te",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "recovery_cost_lb_usd",
  "pool": "holdout_repo_style",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "INC-V2-OSS-002 లో ప్రభావితమైన పదార్థానికి ప్రతి pound ధరతో పునరుద్ధరణ మొత్తం USD బిల్లును అంచనా వేయండి.",
      "role": "user"
    }
  ],
  "question": "INC-V2-OSS-002 లో ప్రభావితమైన పదార్థానికి ప్రతి pound ధరతో పునరుద్ధరణ మొత్తం USD బిల్లును అంచనా వేయండి.",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "unit-converter-mcp__convert_unit",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "falcon-api-middleware",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_repo_style-0014-te",
  "world_split": "repo_style"
}
```

## Sample 8 — source line 65

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "holdout_repo_style-0016",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 0,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "holdout_repo_style",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Database evidence is mandatory for this request: establish sqlalchemy-pool-manager circuit_breaker_pct, or decline if the database is disconnected or that service is absent.",
      "role": "user"
    }
  ],
  "question": "Database evidence is mandatory for this request: establish sqlalchemy-pool-manager circuit_breaker_pct, or decline if the database is disconnected or that service is absent.",
  "reference_tool_sequence": [],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "sqlalchemy-pool-manager",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_repo_style-0016-en",
  "world_split": "repo_style"
}
```

## Sample 9 — source line 67

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "holdout_repo_style-0016",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "hinglish",
  "missing_entity": false,
  "oracle_optimal_steps": 0,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "holdout_repo_style",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Is request mein database evidence mandatory hai: sqlalchemy-pool-manager ka circuit_breaker_pct establish karo; database disconnected ya service absent ho toh decline karna.",
      "role": "user"
    }
  ],
  "question": "Is request mein database evidence mandatory hai: sqlalchemy-pool-manager ka circuit_breaker_pct establish karo; database disconnected ya service absent ho toh decline karna.",
  "reference_tool_sequence": [],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "sqlalchemy-pool-manager",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_repo_style-0016-hinglish",
  "world_split": "repo_style"
}
```

## Sample 10 — source line 91

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "holdout_repo_style-0022",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-OSS-007",
    "PR-V2-OSS-007",
    "SLACK-V2-OSS-007"
  ],
  "gold_value": 12,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "te",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "max_retries",
  "pool": "holdout_repo_style",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "litellm-router-proxy లో అమలైన production max_retries విలువను నిర్ధారించండి. నిర్వహణ పత్రాన్ని release ఆధారాలతో పరిశీలించి కాలం చెల్లిన పేజీని సూచించండి.",
      "role": "user"
    }
  ],
  "question": "litellm-router-proxy లో అమలైన production max_retries విలువను నిర్ధారించండి. నిర్వహణ పత్రాన్ని release ఆధారాలతో పరిశీలించి కాలం చెల్లిన పేజీని సూచించండి.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "litellm-router-proxy",
  "stale_doc_id": "NOTION-V2-OSS-007",
  "stale_trap_value": 3,
  "task_id": "holdout_repo_style-0022-te",
  "world_split": "repo_style"
}
```

---

# File: `holdout_synth_400_frozen.jsonl`

Source SHA-256: `82b92badc6f1fdc71bba41a876db4adf9f19633108b26331297227a7587ac50b`

## Sample 1 — source line 49

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "holdout_synth-0012",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 0,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "max_retries",
  "pool": "holdout_synth",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Database evidence is mandatory for this request: establish merchant-registry max_retries, or decline if the database is disconnected or that service is absent.",
      "role": "user"
    }
  ],
  "question": "Database evidence is mandatory for this request: establish merchant-registry max_retries, or decline if the database is disconnected or that service is absent.",
  "reference_tool_sequence": [],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "merchant-registry",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_synth-0012-en",
  "world_split": "test_synth"
}
```

## Sample 2 — source line 51

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "holdout_synth-0012",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "hinglish",
  "missing_entity": false,
  "oracle_optimal_steps": 0,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "max_retries",
  "pool": "holdout_synth",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Is request mein database evidence mandatory hai: merchant-registry ka max_retries establish karo; database disconnected ya service absent ho toh decline karna.",
      "role": "user"
    }
  ],
  "question": "Is request mein database evidence mandatory hai: merchant-registry ka max_retries establish karo; database disconnected ya service absent ho toh decline karna.",
  "reference_tool_sequence": [],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "merchant-registry",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_synth-0012-hinglish",
  "world_split": "test_synth"
}
```

## Sample 3 — source line 149

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "holdout_synth-0037",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-TS-071",
    "SLACK-V2-TS-071"
  ],
  "gold_value": 17,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "holdout_synth",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "We need a production configuration review for wallet-bridge: establish circuit_breaker_pct and identify documentation that deployment history has overtaken.",
      "role": "user"
    }
  ],
  "question": "We need a production configuration review for wallet-bridge: establish circuit_breaker_pct and identify documentation that deployment history has overtaken.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "wallet-bridge",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_synth-0037-en",
  "world_split": "test_synth"
}
```

## Sample 4 — source line 216

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "holdout_synth-0053",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TS-007"
  ],
  "gold_value": 19.07,
  "incident_id": "INC-V2-TS-007",
  "incident_subtype": "payload_mib",
  "kind": "incident",
  "language": "te",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "recovery_cost_mib_usd",
  "pool": "holdout_synth",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "data-loss namodu INC-V2-TS-007 ku prati MiB punaruddharana dharatho mottham USD billunu nirnayinchandi.",
      "role": "user"
    }
  ],
  "question": "data-loss namodu INC-V2-TS-007 ku prati MiB punaruddharana dharatho mottham USD billunu nirnayinchandi.",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "unit-converter-mcp__convert_unit",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "ledger-exporter",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_synth-0053-te",
  "world_split": "test_synth"
}
```

## Sample 5 — source line 229

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "holdout_synth-0057",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TS-008"
  ],
  "gold_value": 315.0,
  "incident_id": "INC-V2-TS-008",
  "incident_subtype": "sla_penalty",
  "kind": "incident",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_penalty_usd",
  "pool": "holdout_synth",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Assess the USD SLA charge incurred during the outage logged as INC-V2-TS-008.",
      "role": "user"
    }
  ],
  "question": "Assess the USD SLA charge incurred during the outage logged as INC-V2-TS-008.",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "time-mcp__hours_between",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "transfer-worker",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_synth-0057-en",
  "world_split": "test_synth"
}
```

## Sample 6 — source line 327

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "holdout_synth-0081",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-TS-143",
    "PR-V2-TS-143"
  ],
  "gold_value": 14,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "hinglish",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "holdout_synth",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Production review mein treasury-router ka circuit_breaker_pct verify karna hai; release evidence se jo doc purana nikle use flag karo.",
      "role": "user"
    }
  ],
  "question": "Production review mein treasury-router ka circuit_breaker_pct verify karna hai; release evidence se jo doc purana nikle use flag karo.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "treasury-router",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_synth-0081-hinglish",
  "world_split": "test_synth"
}
```

## Sample 7 — source line 344

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "holdout_synth-0085",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "te",
  "missing_entity": false,
  "oracle_optimal_steps": 0,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "rate_limit_rpm",
  "pool": "holdout_synth",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Ee abhyarthanaku database aadhaaram tappanisari: fraud-sentinel yokka rate_limit_rpm nirnayinchandi; database connection lekapothe leda seva lekapothe viraminchandi.",
      "role": "user"
    }
  ],
  "question": "Ee abhyarthanaku database aadhaaram tappanisari: fraud-sentinel yokka rate_limit_rpm nirnayinchandi; database connection lekapothe leda seva lekapothe viraminchandi.",
  "reference_tool_sequence": [],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "fraud-sentinel",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_synth-0085-te",
  "world_split": "test_synth"
}
```

## Sample 8 — source line 374

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "holdout_synth-0093",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-TS-049",
    "PR-V2-TS-049"
  ],
  "gold_value": 5,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "hi",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "max_retries",
  "pool": "holdout_synth",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "receipt-store ke production max_retries ka prabhaavi maan nikaaliye; sanchaalan nirdesh aur release ke pramaan mein virodh ho to puraana panna chuniye.",
      "role": "user"
    }
  ],
  "question": "receipt-store ke production max_retries ka prabhaavi maan nikaaliye; sanchaalan nirdesh aur release ke pramaan mein virodh ho to puraana panna chuniye.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "receipt-store",
  "stale_doc_id": "NOTION-V2-TS-049",
  "stale_trap_value": 8,
  "task_id": "holdout_synth-0093-hi",
  "world_split": "test_synth"
}
```

## Sample 9 — source line 376

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "holdout_synth-0093",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-TS-049",
    "PR-V2-TS-049"
  ],
  "gold_value": 5,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "te",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "max_retries",
  "pool": "holdout_synth",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "receipt-store lo deploy ayina production max_retries nirdhaarinchandi; nirvahana patram ni release saakshyaalatho saripolchi kaalam chellina page soochinchandi.",
      "role": "user"
    }
  ],
  "question": "receipt-store lo deploy ayina production max_retries nirdhaarinchandi; nirvahana patram ni release saakshyaalatho saripolchi kaalam chellina page soochinchandi.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "receipt-store",
  "stale_doc_id": "NOTION-V2-TS-049",
  "stale_trap_value": 8,
  "task_id": "holdout_synth-0093-te",
  "world_split": "test_synth"
}
```

## Sample 10 — source line 394

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "holdout_synth-0098",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TS-014"
  ],
  "gold_value": 105.82,
  "incident_id": "INC-V2-TS-014",
  "incident_subtype": "payload_lb",
  "kind": "incident",
  "language": "hi",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "recovery_cost_lb_usd",
  "pool": "holdout_synth",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "INC-V2-TS-014 में प्रभावित सामग्री के प्रति pound शुल्क पर बहाली का कुल USD बिल निकालिए।",
      "role": "user"
    }
  ],
  "question": "INC-V2-TS-014 में प्रभावित सामग्री के प्रति pound शुल्क पर बहाली का कुल USD बिल निकालिए।",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "unit-converter-mcp__convert_unit",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "treasury-router",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "holdout_synth-0098-hi",
  "world_split": "test_synth"
}
```

---

# File: `train_grpo_stage1.jsonl`

Source SHA-256: `b44e67d78d2abc921583c535a10c3a2bd790aca8fd43723e87151c0c962b7768`

## Sample 1 — source line 49

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_grpo1-0012",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TR-018"
  ],
  "gold_value": 38.58,
  "incident_id": "INC-V2-TR-018",
  "incident_subtype": "payload_lb",
  "kind": "incident",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "recovery_cost_lb_usd",
  "pool": "train_grpo1",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "For incident INC-V2-TR-018, calculate total recovery cost in USD using affected payload in pounds and the per-pound recovery tariff.",
      "role": "user"
    }
  ],
  "question": "For incident INC-V2-TR-018, calculate total recovery cost in USD using affected payload in pounds and the per-pound recovery tariff.",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "unit-converter-mcp__convert_unit",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "limit-manager",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo1-0012-en",
  "world_split": "train"
}
```

## Sample 2 — source line 55

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo1-0013",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-TR-237",
    "PR-V2-TR-237"
  ],
  "gold_value": 154,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "hinglish",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "batch_size_mb",
  "pool": "train_grpo1",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "consent-api pe batch_size_mb confirm karna hai; docs aur deployment history disagree karein toh stale page identify karo.",
      "role": "user"
    }
  ],
  "question": "consent-api pe batch_size_mb confirm karna hai; docs aur deployment history disagree karein toh stale page identify karo.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "consent-api",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo1-0013-hinglish",
  "world_split": "train"
}
```

## Sample 3 — source line 216

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo1-0053",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "INC-V2-TR-029",
    "NOTION-V2-TR-282",
    "PR-V2-TR-282"
  ],
  "gold_value": 76,
  "incident_id": "INC-V2-TR-029",
  "incident_subtype": "config_audit",
  "kind": "incident",
  "language": "te",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "timeout_sec",
  "pool": "train_grpo1",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "INC-V2-TR-029 valla prabhaavitamaina seva yokka prastuta production timeout_sec tanikhi cheyyandi; patram mariyu tainaati charitranu polchandi.",
      "role": "user"
    }
  ],
  "question": "INC-V2-TR-029 valla prabhaavitamaina seva yokka prastuta production timeout_sec tanikhi cheyyandi; patram mariyu tainaati charitranu polchandi.",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "document-store",
  "stale_doc_id": "NOTION-V2-TR-282",
  "stale_trap_value": 157,
  "task_id": "train_grpo1-0053-te",
  "world_split": "train"
}
```

## Sample 4 — source line 245

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo1-0061",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 0,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_hours",
  "pool": "train_grpo1",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Using only the production database, report dispute-api sla_hours. If that source is unavailable or has no such service, abstain.",
      "role": "user"
    }
  ],
  "question": "Using only the production database, report dispute-api sla_hours. If that source is unavailable or has no such service, abstain.",
  "reference_tool_sequence": [],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "dispute-api",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo1-0061-en",
  "world_split": "train"
}
```

## Sample 5 — source line 286

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo1-0071",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TR-033",
    "NOTION-V2-TR-131",
    "SLACK-V2-TR-131"
  ],
  "gold_value": 73,
  "incident_id": "INC-V2-TR-033",
  "incident_subtype": "config_audit",
  "kind": "incident",
  "language": "hi",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "train_grpo1",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "INC-V2-TR-033 se prabhaavit seva ka vartamaan production circuit_breaker_pct jaanchiye; dastavez aur tainaati itihaas ka milaan kijiye.",
      "role": "user"
    }
  ],
  "question": "INC-V2-TR-033 se prabhaavit seva ka vartamaan production circuit_breaker_pct jaanchiye; dastavez aur tainaati itihaas ka milaan kijiye.",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "notion-mcp__search_notion",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "notification-hub",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo1-0071-hi",
  "world_split": "train"
}
```

## Sample 6 — source line 344

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo1-0085",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "te",
  "missing_entity": true,
  "oracle_optimal_steps": 1,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_hours",
  "pool": "train_grpo1",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "production database aadharanga maatrame biometric-relay yokka sla_hours cheppandi. Aa moolam andubaatulo lekapoyina seva lekapoyina samaadhaanam ivvavaddu.",
      "role": "user"
    }
  ],
  "question": "production database aadharanga maatrame biometric-relay yokka sla_hours cheppandi. Aa moolam andubaatulo lekapoyina seva lekapoyina samaadhaanam ivvavaddu.",
  "reference_tool_sequence": [
    "db-mcp__query_db"
  ],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "biometric-relay",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo1-0085-te",
  "world_split": "train"
}
```

## Sample 7 — source line 354

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_grpo1-0088",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-TR-359",
    "PR-V2-TR-359"
  ],
  "gold_value": 10,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "hi",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "train_grpo1",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "notification-worker का वर्तमान production circuit_breaker_pct क्या है? दस्तावेज़ और deployment records की तुलना करें और पुराने पन्ने को पहचानें।",
      "role": "user"
    }
  ],
  "question": "notification-worker का वर्तमान production circuit_breaker_pct क्या है? दस्तावेज़ और deployment records की तुलना करें और पुराने पन्ने को पहचानें।",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "notification-worker",
  "stale_doc_id": "NOTION-V2-TR-359",
  "stale_trap_value": 13,
  "task_id": "train_grpo1-0088-hi",
  "world_split": "train"
}
```

## Sample 8 — source line 356

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_grpo1-0088",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-TR-359",
    "PR-V2-TR-359"
  ],
  "gold_value": 10,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "te",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "train_grpo1",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "notification-worker కోసం ప్రస్తుతం production లో circuit_breaker_pct ఎంత? రన్‌బుక్‌ను deployment ఆధారాలతో పోల్చి పాత పేజీని గుర్తించండి.",
      "role": "user"
    }
  ],
  "question": "notification-worker కోసం ప్రస్తుతం production లో circuit_breaker_pct ఎంత? రన్‌బుక్‌ను deployment ఆధారాలతో పోల్చి పాత పేజీని గుర్తించండి.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "notification-worker",
  "stale_doc_id": "NOTION-V2-TR-359",
  "stale_trap_value": 13,
  "task_id": "train_grpo1-0088-te",
  "world_split": "train"
}
```

## Sample 9 — source line 367

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo1-0091",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "hinglish",
  "missing_entity": false,
  "oracle_optimal_steps": 0,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "train_grpo1",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "invoice-store ka circuit_breaker_pct production database se hi do. Source unavailable ho ya service na mile toh abstain karo.",
      "role": "user"
    }
  ],
  "question": "invoice-store ka circuit_breaker_pct production database se hi do. Source unavailable ho ya service na mile toh abstain karo.",
  "reference_tool_sequence": [],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "invoice-store",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo1-0091-hinglish",
  "world_split": "train"
}
```

## Sample 10 — source line 397

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo1-0099",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-TR-066",
    "PR-V2-TR-066"
  ],
  "gold_value": 13,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "timeout_sec",
  "pool": "train_grpo1",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Please audit audit-stream: reconcile its documented timeout_sec with production deployment history.",
      "role": "user"
    }
  ],
  "question": "Please audit audit-stream: reconcile its documented timeout_sec with production deployment history.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "audit-stream",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo1-0099-en",
  "world_split": "train"
}
```

---

# File: `train_grpo_stage2.jsonl`

Source SHA-256: `8d7f5236f1fad9450f5ae3ecb81e83b9acda96f01d548225787b7f7eb5754977`

## Sample 1 — source line 178

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_grpo2-0044",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-TR-206",
    "PR-V2-TR-206"
  ],
  "gold_value": 100,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "hi",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "rate_limit_rpm",
  "pool": "train_grpo2",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "merchant-api का वर्तमान production rate_limit_rpm क्या है? दस्तावेज़ और deployment records की तुलना करें और पुराने पन्ने को पहचानें।",
      "role": "user"
    }
  ],
  "question": "merchant-api का वर्तमान production rate_limit_rpm क्या है? दस्तावेज़ और deployment records की तुलना करें और पुराने पन्ने को पहचानें।",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "merchant-api",
  "stale_doc_id": "NOTION-V2-TR-206",
  "stale_trap_value": 4870,
  "task_id": "train_grpo2-0044-hi",
  "world_split": "train"
}
```

## Sample 2 — source line 229

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo2-0057",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-TR-059",
    "SLACK-V2-TR-059"
  ],
  "gold_value": 34,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "train_grpo2",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Please audit inventory-sync: reconcile its documented circuit_breaker_pct with production deployment history.",
      "role": "user"
    }
  ],
  "question": "Please audit inventory-sync: reconcile its documented circuit_breaker_pct with production deployment history.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "inventory-sync",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo2-0057-en",
  "world_split": "train"
}
```

## Sample 3 — source line 245

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo2-0061",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TR-054"
  ],
  "gold_value": 181.88,
  "incident_id": "INC-V2-TR-054",
  "incident_subtype": "payload_lb",
  "kind": "incident",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "recovery_cost_lb_usd",
  "pool": "train_grpo2",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "For incident INC-V2-TR-054, calculate total recovery cost in USD using affected payload in pounds and the per-pound recovery tariff.",
      "role": "user"
    }
  ],
  "question": "For incident INC-V2-TR-054, calculate total recovery cost in USD using affected payload in pounds and the per-pound recovery tariff.",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "unit-converter-mcp__convert_unit",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "payment-worker",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo2-0061-en",
  "world_split": "train"
}
```

## Sample 4 — source line 286

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo2-0071",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TR-055"
  ],
  "gold_value": 5.96,
  "incident_id": "INC-V2-TR-055",
  "incident_subtype": "payload_mib",
  "kind": "incident",
  "language": "hi",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "recovery_cost_mib_usd",
  "pool": "train_grpo2",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "INC-V2-TR-055 ke prabhaavit data ko MiB mein lekar prati-MiB shulk ke anusaar kul recovery bill USD mein kitna hai?",
      "role": "user"
    }
  ],
  "question": "INC-V2-TR-055 ke prabhaavit data ko MiB mein lekar prati-MiB shulk ke anusaar kul recovery bill USD mein kitna hai?",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "unit-converter-mcp__convert_unit",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "audit-stream",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo2-0071-hi",
  "world_split": "train"
}
```

## Sample 5 — source line 324

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_grpo2-0080",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "te",
  "missing_entity": true,
  "oracle_optimal_steps": 1,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "train_grpo2",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "production database ఆధారంగా మాత్రమే escrow-gate యొక్క circuit_breaker_pct చెప్పండి. ఆ మూలం అందుబాటులో లేకపోయినా సేవ లేకపోయినా సమాధానం ఇవ్వవద్దు.",
      "role": "user"
    }
  ],
  "question": "production database ఆధారంగా మాత్రమే escrow-gate యొక్క circuit_breaker_pct చెప్పండి. ఆ మూలం అందుబాటులో లేకపోయినా సేవ లేకపోయినా సమాధానం ఇవ్వవద్దు.",
  "reference_tool_sequence": [
    "db-mcp__query_db"
  ],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "escrow-gate",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo2-0080-te",
  "world_split": "train"
}
```

## Sample 6 — source line 344

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo2-0085",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-TR-135",
    "PR-V2-TR-135"
  ],
  "gold_value": 43,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "te",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "batch_size_mb",
  "pool": "train_grpo2",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "tax-engine lo ippudu production batch_size_mb entha? Runbook ni deployment aadharaalatho polchi paatha page gurthinchu.",
      "role": "user"
    }
  ],
  "question": "tax-engine lo ippudu production batch_size_mb entha? Runbook ni deployment aadharaalatho polchi paatha page gurthinchu.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "tax-engine",
  "stale_doc_id": "NOTION-V2-TR-135",
  "stale_trap_value": 436,
  "task_id": "train_grpo2-0085-te",
  "world_split": "train"
}
```

## Sample 7 — source line 351

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo2-0087",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-TR-280",
    "PR-V2-TR-280"
  ],
  "gold_value": 7,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "hinglish",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_hours",
  "pool": "train_grpo2",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "routing-proxy pe sla_hours confirm karna hai; docs aur deployment history disagree karein toh stale page identify karo.",
      "role": "user"
    }
  ],
  "question": "routing-proxy pe sla_hours confirm karna hai; docs aur deployment history disagree karein toh stale page identify karo.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "routing-proxy",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo2-0087-hinglish",
  "world_split": "train"
}
```

## Sample 8 — source line 356

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_grpo2-0088",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TR-060"
  ],
  "gold_value": 472.5,
  "incident_id": "INC-V2-TR-060",
  "incident_subtype": "sla_penalty",
  "kind": "incident",
  "language": "te",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_penalty_usd",
  "pool": "train_grpo2",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "సంఘటన INC-V2-TR-060 కోసం సమయం ఆధారంగా మొత్తం SLA జరిమానా USD లో ఎంత?",
      "role": "user"
    }
  ],
  "question": "సంఘటన INC-V2-TR-060 కోసం సమయం ఆధారంగా మొత్తం SLA జరిమానా USD లో ఎంత?",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "time-mcp__hours_between",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "wire-dispatch",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo2-0088-te",
  "world_split": "train"
}
```

## Sample 9 — source line 445

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo2-0111",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "en",
  "missing_entity": true,
  "oracle_optimal_steps": 1,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "rate_limit_rpm",
  "pool": "train_grpo2",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Using only the production database, report escrow-reconciler rate_limit_rpm. If that source is unavailable or has no such service, abstain.",
      "role": "user"
    }
  ],
  "question": "Using only the production database, report escrow-reconciler rate_limit_rpm. If that source is unavailable or has no such service, abstain.",
  "reference_tool_sequence": [
    "db-mcp__query_db"
  ],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "escrow-reconciler",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo2-0111-en",
  "world_split": "train"
}
```

## Sample 10 — source line 463

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_grpo2-0115",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "hinglish",
  "missing_entity": true,
  "oracle_optimal_steps": 1,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "timeout_sec",
  "pool": "train_grpo2",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "escrow-validator ka timeout_sec production database se hi do. Source unavailable ho ya service na mile toh abstain karo.",
      "role": "user"
    }
  ],
  "question": "escrow-validator ka timeout_sec production database se hi do. Source unavailable ho ya service na mile toh abstain karo.",
  "reference_tool_sequence": [
    "db-mcp__query_db"
  ],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "escrow-validator",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_grpo2-0115-hinglish",
  "world_split": "train"
}
```

---

# File: `train_sft_240.jsonl`

Source SHA-256: `96402f7d8ce8f05ee98aee212f1af9ac7a2b51fef1098e2beda3e395b90e1932`

## Sample 1 — source line 51

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_sft-0012",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "hinglish",
  "messages": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "forex-gate ka sla_hours production database se hi do. Source unavailable ho ya service na mile toh abstain karo.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"db-mcp\", \"tool\": \"query_db\", \"arguments\": {\"sql\": \"SELECT * FROM microservices WHERE service_name = 'forex-gate'\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: {\"rows\": []}",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "missing_entity": true,
  "oracle_optimal_steps": 1,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_hours",
  "pool": "train_sft",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "forex-gate ka sla_hours production database se hi do. Source unavailable ho ya service na mile toh abstain karo.",
      "role": "user"
    }
  ],
  "question": "forex-gate ka sla_hours production database se hi do. Source unavailable ho ya service na mile toh abstain karo.",
  "reference_tool_sequence": [
    "db-mcp__query_db"
  ],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "forex-gate",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_sft-0012-hinglish",
  "world_split": "train"
}
```

## Sample 2 — source line 55

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_sft-0013",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-TR-205",
    "SLACK-V2-TR-205"
  ],
  "gold_value": 10,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "hinglish",
  "messages": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "merchant-api pe max_retries confirm karna hai; docs aur deployment history disagree karein toh stale page identify karo.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"notion-mcp\", \"tool\": \"search_notion\", \"arguments\": {\"query\": \"merchant-api max_retries current configuration runbook\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"page_id\": \"NOTION-V2-TR-205-STG\", \"service_name\": \"merchant-api\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"merchant-api [STAGING-ONLY] max_retries\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"merchant-api [STAGING-ONLY] max_retries = 1. Staging-only trial; do not apply this setting to production.\"}, {\"page_id\": \"NOTION-V2-TR-205\", \"service_name\": \"merchant-api\", \"param_name\": \"max_retries\", \"environment\": \"prod\", \"title\": \"merchant-api [PROD] max_retries\", \"updated_at\": \"2026-02-05T09:30:00+00:00\", \"snippet\": \"merchant-api [PROD] max_retries = 10. Production runbook at publication. Tracked via Slack #deployments.\"}, {\"page_id\": \"NOTION-V2-TR-331-STG\", \"service_name\": \"dispute-api\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"dispute-api [STAGING-ONLY] max_retries\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"dispute-api [STAGING-ONLY] max_retries = 1. Staging-only trial; do not apply this setting to production.\"}]",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"slack-mcp\", \"tool\": \"search_slack\", \"arguments\": {\"query\": \"merchant-api max_retries\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"service_name\": \"merchant-api\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"merchant-api [STAGING-ONLY] max_retries\", \"msg_id\": \"SLACK-V2-TR-205-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"merchant-api [STAGING-ONLY] max_retries = 1. Staging test; this is not a production setting.\"}, {\"service_name\": \"merchant-api\", \"param_name\": \"max_retries\", \"environment\": \"prod\", \"title\": \"merchant-api [PROD] max_retries\", \"msg_id\": \"SLACK-V2-TR-205\", \"channel\": \"#deployments\", \"posted_at\": \"2026-03-11T11:00:00+00:00\", \"text\": \"merchant-api [PROD] max_retries = 10. Production deployment verified.\"}, {\"service_name\": \"dispute-api\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"dispute-api [STAGING-ONLY] max_retries\", \"msg_id\": \"SLACK-V2-TR-331-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"dispute-api [STAGING-ONLY] max_retries = 1. Staging test; this is not a production setting.\"}]",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"answered\", \"value\": 10, \"cites\": [\"NOTION-V2-TR-205\", \"SLACK-V2-TR-205\"], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "max_retries",
  "pool": "train_sft",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "merchant-api pe max_retries confirm karna hai; docs aur deployment history disagree karein toh stale page identify karo.",
      "role": "user"
    }
  ],
  "question": "merchant-api pe max_retries confirm karna hai; docs aur deployment history disagree karein toh stale page identify karo.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "merchant-api",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_sft-0013-hinglish",
  "world_split": "train"
}
```

## Sample 3 — source line 109

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_sft-0027",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TR-008"
  ],
  "gold_value": 202.5,
  "incident_id": "INC-V2-TR-008",
  "incident_subtype": "sla_penalty",
  "kind": "incident",
  "language": "en",
  "messages": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "What is the total time-based SLA penalty in USD for incident INC-V2-TR-008?",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"db-mcp\", \"tool\": \"query_db\", \"arguments\": {\"sql\": \"SELECT * FROM production_incidents WHERE incident_id = 'INC-V2-TR-008'\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: {\"rows\": [{\"incident_id\": \"INC-V2-TR-008\", \"service_name\": \"session-cache\", \"environment\": \"prod\", \"started_at\": \"2026-10-10T08:30:00+00:00\", \"resolved_at\": \"2026-10-10T22:00:00+00:00\", \"root_cause_pr\": \"PR-V2-TR-060\", \"penalty_rate_per_hour\": 15.0, \"weight_kg\": 110.0, \"data_spill_gb\": 1.25, \"recovery_cost_per_lb\": 0.75, \"recovery_cost_per_mib\": 0.0125}]}",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"time-mcp\", \"tool\": \"hours_between\", \"arguments\": {\"start_iso\": \"2026-10-10T08:30:00+00:00\", \"end_iso\": \"2026-10-10T22:00:00+00:00\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 13.5",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"math-mcp\", \"tool\": \"calculate\", \"arguments\": {\"expression\": \"round(13.5 * 15.0, 2)\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 202.5",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"answered\", \"value\": 202.5, \"cites\": [\"INC-V2-TR-008\"], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_penalty_usd",
  "pool": "train_sft",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "What is the total time-based SLA penalty in USD for incident INC-V2-TR-008?",
      "role": "user"
    }
  ],
  "question": "What is the total time-based SLA penalty in USD for incident INC-V2-TR-008?",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "time-mcp__hours_between",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "session-cache",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_sft-0027-en",
  "world_split": "train"
}
```

## Sample 4 — source line 149

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_sft-0037",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "en",
  "messages": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Using only the production database, report forex-vault circuit_breaker_pct. If that source is unavailable or has no such service, abstain.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"db-mcp\", \"tool\": \"query_db\", \"arguments\": {\"sql\": \"SELECT * FROM microservices WHERE service_name = 'forex-vault'\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: {\"rows\": []}",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "missing_entity": true,
  "oracle_optimal_steps": 1,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "train_sft",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Using only the production database, report forex-vault circuit_breaker_pct. If that source is unavailable or has no such service, abstain.",
      "role": "user"
    }
  ],
  "question": "Using only the production database, report forex-vault circuit_breaker_pct. If that source is unavailable or has no such service, abstain.",
  "reference_tool_sequence": [
    "db-mcp__query_db"
  ],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "forex-vault",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_sft-0037-en",
  "world_split": "train"
}
```

## Sample 5 — source line 152

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_sft-0037",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "te",
  "messages": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "production database aadharanga maatrame forex-vault yokka circuit_breaker_pct cheppandi. Aa moolam andubaatulo lekapoyina seva lekapoyina samaadhaanam ivvavaddu.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"db-mcp\", \"tool\": \"query_db\", \"arguments\": {\"sql\": \"SELECT * FROM microservices WHERE service_name = 'forex-vault'\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: {\"rows\": []}",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "missing_entity": true,
  "oracle_optimal_steps": 1,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "train_sft",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "production database aadharanga maatrame forex-vault yokka circuit_breaker_pct cheppandi. Aa moolam andubaatulo lekapoyina seva lekapoyina samaadhaanam ivvavaddu.",
      "role": "user"
    }
  ],
  "question": "production database aadharanga maatrame forex-vault yokka circuit_breaker_pct cheppandi. Aa moolam andubaatulo lekapoyina seva lekapoyina samaadhaanam ivvavaddu.",
  "reference_tool_sequence": [
    "db-mcp__query_db"
  ],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "forex-vault",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_sft-0037-te",
  "world_split": "train"
}
```

## Sample 6 — source line 156

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_sft-0038",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-TR-211",
    "PR-V2-TR-211",
    "SLACK-V2-TR-211"
  ],
  "gold_value": 1,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "te",
  "messages": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "receipt-worker యొక్క అమలులో ఉన్న max_retries చెప్పండి; పాత సూచనలు వేరుగా ఉంటే ఆ పేజీని తెలియజేయండి.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"notion-mcp\", \"tool\": \"search_notion\", \"arguments\": {\"query\": \"receipt-worker max_retries current configuration runbook\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"page_id\": \"NOTION-V2-TR-211-STG\", \"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] max_retries\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"receipt-worker [STAGING-ONLY] max_retries = 7. Staging-only trial; do not apply this setting to production.\"}, {\"page_id\": \"NOTION-V2-TR-211\", \"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"prod\", \"title\": \"receipt-worker [PROD] max_retries\", \"updated_at\": \"2026-02-05T09:30:00+00:00\", \"snippet\": \"receipt-worker [PROD] max_retries = 4. Production runbook at publication. Tracked via Slack #deployments.\"}, {\"page_id\": \"NOTION-V2-TR-355-STG\", \"service_name\": \"notification-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] max_retries\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"notification-worker [STAGING-ONLY] max_retries = 4. Staging-only trial; do not apply this setting to production.\"}]",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"slack-mcp\", \"tool\": \"search_slack\", \"arguments\": {\"query\": \"receipt-worker max_retries\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] max_retries\", \"msg_id\": \"SLACK-V2-TR-211-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"receipt-worker [STAGING-ONLY] max_retries = 7. Staging test; this is not a production setting.\"}, {\"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"prod\", \"title\": \"receipt-worker [PROD] max_retries\", \"msg_id\": \"SLACK-V2-TR-211\", \"channel\": \"#deployments\", \"posted_at\": \"2026-06-13T10:30:00+00:00\", \"text\": \"receipt-worker [PROD] max_retries = 10. Production deployment verified. Production hotfix follow-ups are tracked in GitHub PRs.\"}, {\"service_name\": \"notification-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] max_retries\", \"msg_id\": \"SLACK-V2-TR-355-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"notification-worker [STAGING-ONLY] max_retries = 4. Staging test; this is not a production setting.\"}]",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"github-mcp\", \"tool\": \"search_github_prs\", \"arguments\": {\"query\": \"receipt-worker max_retries\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] max_retries\", \"pr_id\": \"PR-V2-TR-211-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"receipt-worker [STAGING-ONLY] max_retries = 7. Staging test; this is not a production setting.\"}, {\"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"prod\", \"title\": \"receipt-worker [PROD] max_retries\", \"pr_id\": \"PR-V2-TR-211\", \"merged_at\": \"2026-09-17T14:00:00+00:00\", \"summary\": \"receipt-worker [PROD] max_retries = 1. Production deployment verified.\"}, {\"service_name\": \"notification-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] max_retries\", \"pr_id\": \"PR-V2-TR-355-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"notification-worker [STAGING-ONLY] max_retries = 4. Staging test; this is not a production setting.\"}]",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 1, \"cites\": [\"NOTION-V2-TR-211\", \"SLACK-V2-TR-211\", \"PR-V2-TR-211\"], \"stale_source\": \"NOTION-V2-TR-211\"}</final_answer>",
      "role": "assistant"
    }
  ],
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "max_retries",
  "pool": "train_sft",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "receipt-worker యొక్క అమలులో ఉన్న max_retries చెప్పండి; పాత సూచనలు వేరుగా ఉంటే ఆ పేజీని తెలియజేయండి.",
      "role": "user"
    }
  ],
  "question": "receipt-worker యొక్క అమలులో ఉన్న max_retries చెప్పండి; పాత సూచనలు వేరుగా ఉంటే ఆ పేజీని తెలియజేయండి.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "slack-mcp__search_slack",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "receipt-worker",
  "stale_doc_id": "NOTION-V2-TR-211",
  "stale_trap_value": 4,
  "task_id": "train_sft-0038-te",
  "world_split": "train"
}
```

## Sample 7 — source line 178

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_sft-0044",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-TR-089",
    "PR-V2-TR-089",
    "SLACK-V2-TR-089"
  ],
  "gold_value": 64,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "hi",
  "messages": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "checkout-api का वर्तमान production circuit_breaker_pct क्या है? दस्तावेज़ और deployment records की तुलना करें और पुराने पन्ने को पहचानें।",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"notion-mcp\", \"tool\": \"search_notion\", \"arguments\": {\"query\": \"checkout-api circuit_breaker_pct current configuration runbook\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"page_id\": \"NOTION-V2-TR-089-STG\", \"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct = 10. Staging-only trial; do not apply this setting to production.\"}, {\"page_id\": \"NOTION-V2-TR-089\", \"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"prod\", \"title\": \"checkout-api [PROD] circuit_breaker_pct\", \"updated_at\": \"2026-02-05T09:30:00+00:00\", \"snippet\": \"checkout-api [PROD] circuit_breaker_pct = 46. Production runbook at publication. Tracked via GitHub PRs.\"}, {\"page_id\": \"NOTION-V2-TR-335-STG\", \"service_name\": \"dispute-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct = 58. Staging-only trial; do not apply this setting to production.\"}]",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"github-mcp\", \"tool\": \"search_github_prs\", \"arguments\": {\"query\": \"checkout-api circuit_breaker_pct\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct\", \"pr_id\": \"PR-V2-TR-089-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct = 10. Staging test; this is not a production setting.\"}, {\"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"prod\", \"title\": \"checkout-api [PROD] circuit_breaker_pct\", \"pr_id\": \"PR-V2-TR-089\", \"merged_at\": \"2026-06-13T10:30:00+00:00\", \"summary\": \"checkout-api [PROD] circuit_breaker_pct = 73. Production deployment verified. Production hotfix follow-ups are tracked in Slack #deployments.\"}, {\"service_name\": \"dispute-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct\", \"pr_id\": \"PR-V2-TR-335-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct = 58. Staging test; this is not a production setting.\"}]",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"slack-mcp\", \"tool\": \"search_slack\", \"arguments\": {\"query\": \"checkout-api circuit_breaker_pct\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct\", \"msg_id\": \"SLACK-V2-TR-089-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct = 10. Staging test; this is not a production setting.\"}, {\"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"prod\", \"title\": \"checkout-api [PROD] circuit_breaker_pct\", \"msg_id\": \"SLACK-V2-TR-089\", \"channel\": \"#deployments\", \"posted_at\": \"2026-09-17T14:00:00+00:00\", \"text\": \"checkout-api [PROD] circuit_breaker_pct = 64. Production deployment verified.\"}, {\"service_name\": \"dispute-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct\", \"msg_id\": \"SLACK-V2-TR-335-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct = 58. Staging test; this is not a production setting.\"}]",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 64, \"cites\": [\"NOTION-V2-TR-089\", \"PR-V2-TR-089\", \"SLACK-V2-TR-089\"], \"stale_source\": \"NOTION-V2-TR-089\"}</final_answer>",
      "role": "assistant"
    }
  ],
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "train_sft",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "checkout-api का वर्तमान production circuit_breaker_pct क्या है? दस्तावेज़ और deployment records की तुलना करें और पुराने पन्ने को पहचानें।",
      "role": "user"
    }
  ],
  "question": "checkout-api का वर्तमान production circuit_breaker_pct क्या है? दस्तावेज़ और deployment records की तुलना करें और पुराने पन्ने को पहचानें।",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "checkout-api",
  "stale_doc_id": "NOTION-V2-TR-089",
  "stale_trap_value": 46,
  "task_id": "train_sft-0044-hi",
  "world_split": "train"
}
```

## Sample 8 — source line 216

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_sft-0053",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TR-012"
  ],
  "gold_value": 12.5,
  "incident_id": "INC-V2-TR-012",
  "incident_subtype": "sla_penalty",
  "kind": "incident",
  "language": "te",
  "messages": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Sanghatana INC-V2-TR-012 kosam samayam aadharanga mottham SLA jarimaana USD lo entha?",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"db-mcp\", \"tool\": \"query_db\", \"arguments\": {\"sql\": \"SELECT * FROM production_incidents WHERE incident_id = 'INC-V2-TR-012'\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: {\"rows\": [{\"incident_id\": \"INC-V2-TR-012\", \"service_name\": \"email-relay\", \"environment\": \"prod\", \"started_at\": \"2026-10-08T11:30:00+00:00\", \"resolved_at\": \"2026-10-08T12:30:00+00:00\", \"root_cause_pr\": \"PR-V2-TR-052\", \"penalty_rate_per_hour\": 12.5, \"weight_kg\": 12.5, \"data_spill_gb\": 2.5, \"recovery_cost_per_lb\": 0.75, \"recovery_cost_per_mib\": 0.025}]}",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"time-mcp\", \"tool\": \"hours_between\", \"arguments\": {\"start_iso\": \"2026-10-08T11:30:00+00:00\", \"end_iso\": \"2026-10-08T12:30:00+00:00\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 1.0",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"math-mcp\", \"tool\": \"calculate\", \"arguments\": {\"expression\": \"round(1.0 * 12.5, 2)\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 12.5",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"answered\", \"value\": 12.5, \"cites\": [\"INC-V2-TR-012\"], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_penalty_usd",
  "pool": "train_sft",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Sanghatana INC-V2-TR-012 kosam samayam aadharanga mottham SLA jarimaana USD lo entha?",
      "role": "user"
    }
  ],
  "question": "Sanghatana INC-V2-TR-012 kosam samayam aadharanga mottham SLA jarimaana USD lo entha?",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "time-mcp__hours_between",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "email-relay",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_sft-0053-te",
  "world_split": "train"
}
```

## Sample 9 — source line 229

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_sft-0057",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-TR-213",
    "PR-V2-TR-213"
  ],
  "gold_value": 400,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "en",
  "messages": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Please audit receipt-worker: reconcile its documented batch_size_mb with production deployment history.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"notion-mcp\", \"tool\": \"search_notion\", \"arguments\": {\"query\": \"receipt-worker batch_size_mb current configuration runbook\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"page_id\": \"NOTION-V2-TR-213-STG\", \"service_name\": \"receipt-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] batch_size_mb\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"receipt-worker [STAGING-ONLY] batch_size_mb = 70. Staging-only trial; do not apply this setting to production.\"}, {\"page_id\": \"NOTION-V2-TR-213\", \"service_name\": \"receipt-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"prod\", \"title\": \"receipt-worker [PROD] batch_size_mb\", \"updated_at\": \"2026-02-05T09:30:00+00:00\", \"snippet\": \"receipt-worker [PROD] batch_size_mb = 400. Production runbook at publication.\"}, {\"page_id\": \"NOTION-V2-TR-357-STG\", \"service_name\": \"notification-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] batch_size_mb\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"notification-worker [STAGING-ONLY] batch_size_mb = 424. Staging-only trial; do not apply this setting to production.\"}]",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"github-mcp\", \"tool\": \"search_github_prs\", \"arguments\": {\"query\": \"receipt-worker batch_size_mb\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"service_name\": \"receipt-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] batch_size_mb\", \"pr_id\": \"PR-V2-TR-213-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"receipt-worker [STAGING-ONLY] batch_size_mb = 70. Staging test; this is not a production setting.\"}, {\"service_name\": \"receipt-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"prod\", \"title\": \"receipt-worker [PROD] batch_size_mb\", \"pr_id\": \"PR-V2-TR-213\", \"merged_at\": \"2026-03-11T11:00:00+00:00\", \"summary\": \"receipt-worker [PROD] batch_size_mb = 400. Production deployment verified.\"}, {\"service_name\": \"notification-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] batch_size_mb\", \"pr_id\": \"PR-V2-TR-357-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"notification-worker [STAGING-ONLY] batch_size_mb = 424. Staging test; this is not a production setting.\"}]",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"slack-mcp\", \"tool\": \"search_slack\", \"arguments\": {\"query\": \"receipt-worker batch_size_mb\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"service_name\": \"receipt-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] batch_size_mb\", \"msg_id\": \"SLACK-V2-TR-213-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"receipt-worker [STAGING-ONLY] batch_size_mb = 70. Staging test; this is not a production setting.\"}, {\"service_name\": \"notification-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] batch_size_mb\", \"msg_id\": \"SLACK-V2-TR-357-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"notification-worker [STAGING-ONLY] batch_size_mb = 424. Staging test; this is not a production setting.\"}, {\"service_name\": \"export-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"export-worker [STAGING-ONLY] batch_size_mb\", \"msg_id\": \"SLACK-V2-TR-345-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"export-worker [STAGING-ONLY] batch_size_mb = 181. Staging test; this is not a production setting.\"}]",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"answered\", \"value\": 400, \"cites\": [\"NOTION-V2-TR-213\", \"PR-V2-TR-213\"], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "batch_size_mb",
  "pool": "train_sft",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Please audit receipt-worker: reconcile its documented batch_size_mb with production deployment history.",
      "role": "user"
    }
  ],
  "question": "Please audit receipt-worker: reconcile its documented batch_size_mb with production deployment history.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "receipt-worker",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_sft-0057-en",
  "world_split": "train"
}
```

## Sample 10 — source line 234

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_sft-0058",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TR-014"
  ],
  "gold_value": 20.67,
  "incident_id": "INC-V2-TR-014",
  "incident_subtype": "payload_lb",
  "kind": "incident",
  "language": "hi",
  "messages": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "घटना INC-V2-TR-014 के प्रभावित भार को pounds में मानकर प्रति-pound शुल्क से कुल recovery cost USD में बताइए।",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"db-mcp\", \"tool\": \"query_db\", \"arguments\": {\"sql\": \"SELECT * FROM production_incidents WHERE incident_id = 'INC-V2-TR-014'\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: {\"rows\": [{\"incident_id\": \"INC-V2-TR-014\", \"service_name\": \"reconciliation-worker\", \"environment\": \"prod\", \"started_at\": \"2026-10-14T23:30:00+00:00\", \"resolved_at\": \"2026-10-15T01:00:00+00:00\", \"root_cause_pr\": \"PR-V2-TR-227\", \"penalty_rate_per_hour\": 12.5, \"weight_kg\": 12.5, \"data_spill_gb\": 2.5, \"recovery_cost_per_lb\": 0.75, \"recovery_cost_per_mib\": 0.0125}]}",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"unit-converter-mcp\", \"tool\": \"convert_unit\", \"arguments\": {\"value\": 12.5, \"from_unit\": \"kg\", \"to_unit\": \"lb\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 27.557782773109697",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"math-mcp\", \"tool\": \"calculate\", \"arguments\": {\"expression\": \"round(27.557782773109697 * 0.75, 2)\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 20.67",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"answered\", \"value\": 20.67, \"cites\": [\"INC-V2-TR-014\"], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "recovery_cost_lb_usd",
  "pool": "train_sft",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "घटना INC-V2-TR-014 के प्रभावित भार को pounds में मानकर प्रति-pound शुल्क से कुल recovery cost USD में बताइए।",
      "role": "user"
    }
  ],
  "question": "घटना INC-V2-TR-014 के प्रभावित भार को pounds में मानकर प्रति-pound शुल्क से कुल recovery cost USD में बताइए।",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "unit-converter-mcp__convert_unit",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "reconciliation-worker",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_sft-0058-hi",
  "world_split": "train"
}
```

---

# File: `train_sft_agenttune_trajectories.jsonl`

Source SHA-256: `63265574e26aad81ee4d136b461eacd7fcf8dcd283a87231bcb181a7e2db1674`

## Sample 1 — source line 51

```json
{
  "final_response": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
  "metadata": {
    "case_id": "train_sft-0012",
    "kind": "abstain",
    "language": "hinglish",
    "oracle_tool_calls": 1,
    "reward_mode": "evidence_gated",
    "schema_version": 2,
    "script": "latin",
    "task_id": "train_sft-0012-hinglish",
    "world_split": "train"
  },
  "reward": 1.0,
  "steps": [
    {
      "action": {
        "arguments": {
          "sql": "SELECT * FROM microservices WHERE service_name = 'forex-gate'"
        },
        "name": "db-mcp__query_db"
      },
      "observation": "{\"rows\": []}",
      "reward": null,
      "state": "forex-gate ka sla_hours production database se hi do. Source unavailable ho ya service na mile toh abstain karo.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 1,
      "thought": null
    }
  ],
  "task": "forex-gate ka sla_hours production database se hi do. Source unavailable ho ya service na mile toh abstain karo.",
  "trajectory_id": "train_sft-0012-hinglish"
}
```

## Sample 2 — source line 55

```json
{
  "final_response": "<final_answer>{\"status\": \"answered\", \"value\": 10, \"cites\": [\"NOTION-V2-TR-205\", \"SLACK-V2-TR-205\"], \"stale_source\": null}</final_answer>",
  "metadata": {
    "case_id": "train_sft-0013",
    "kind": "consistent",
    "language": "hinglish",
    "oracle_tool_calls": 2,
    "reward_mode": "evidence_gated",
    "schema_version": 2,
    "script": "latin",
    "task_id": "train_sft-0013-hinglish",
    "world_split": "train"
  },
  "reward": 1.3,
  "steps": [
    {
      "action": {
        "arguments": {
          "query": "merchant-api max_retries current configuration runbook"
        },
        "name": "notion-mcp__search_notion"
      },
      "observation": "[{\"page_id\": \"NOTION-V2-TR-205-STG\", \"service_name\": \"merchant-api\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"merchant-api [STAGING-ONLY] max_retries\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"merchant-api [STAGING-ONLY] max_retries = 1. Staging-only trial; do not apply this setting to production.\"}, {\"page_id\": \"NOTION-V2-TR-205\", \"service_name\": \"merchant-api\", \"param_name\": \"max_retries\", \"environment\": \"prod\", \"title\": \"merchant-api [PROD] max_retries\", \"updated_at\": \"2026-02-05T09:30:00+00:00\", \"snippet\": \"merchant-api [PROD] max_retries = 10. Production runbook at publication. Tracked via Slack #deployments.\"}, {\"page_id\": \"NOTION-V2-TR-331-STG\", \"service_name\": \"dispute-api\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"dispute-api [STAGING-ONLY] max_retries\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"dispute-api [STAGING-ONLY] max_retries = 1. Staging-only trial; do not apply this setting to production.\"}]",
      "reward": null,
      "state": "merchant-api pe max_retries confirm karna hai; docs aur deployment history disagree karein toh stale page identify karo.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "query": "merchant-api max_retries"
        },
        "name": "slack-mcp__search_slack"
      },
      "observation": "[{\"service_name\": \"merchant-api\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"merchant-api [STAGING-ONLY] max_retries\", \"msg_id\": \"SLACK-V2-TR-205-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"merchant-api [STAGING-ONLY] max_retries = 1. Staging test; this is not a production setting.\"}, {\"service_name\": \"merchant-api\", \"param_name\": \"max_retries\", \"environment\": \"prod\", \"title\": \"merchant-api [PROD] max_retries\", \"msg_id\": \"SLACK-V2-TR-205\", \"channel\": \"#deployments\", \"posted_at\": \"2026-03-11T11:00:00+00:00\", \"text\": \"merchant-api [PROD] max_retries = 10. Production deployment verified.\"}, {\"service_name\": \"dispute-api\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"dispute-api [STAGING-ONLY] max_retries\", \"msg_id\": \"SLACK-V2-TR-331-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"dispute-api [STAGING-ONLY] max_retries = 1. Staging test; this is not a production setting.\"}]",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"answered\", \"value\": 10, \"cites\": [\"NOTION-V2-TR-205\", \"SLACK-V2-TR-205\"], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 2,
      "thought": null
    }
  ],
  "task": "merchant-api pe max_retries confirm karna hai; docs aur deployment history disagree karein toh stale page identify karo.",
  "trajectory_id": "train_sft-0013-hinglish"
}
```

## Sample 3 — source line 109

```json
{
  "final_response": "<final_answer>{\"status\": \"answered\", \"value\": 202.5, \"cites\": [\"INC-V2-TR-008\"], \"stale_source\": null}</final_answer>",
  "metadata": {
    "case_id": "train_sft-0027",
    "kind": "incident",
    "language": "en",
    "oracle_tool_calls": 3,
    "reward_mode": "evidence_gated",
    "schema_version": 2,
    "script": "latin",
    "task_id": "train_sft-0027-en",
    "world_split": "train"
  },
  "reward": 1.3,
  "steps": [
    {
      "action": {
        "arguments": {
          "sql": "SELECT * FROM production_incidents WHERE incident_id = 'INC-V2-TR-008'"
        },
        "name": "db-mcp__query_db"
      },
      "observation": "{\"rows\": [{\"incident_id\": \"INC-V2-TR-008\", \"service_name\": \"session-cache\", \"environment\": \"prod\", \"started_at\": \"2026-10-10T08:30:00+00:00\", \"resolved_at\": \"2026-10-10T22:00:00+00:00\", \"root_cause_pr\": \"PR-V2-TR-060\", \"penalty_rate_per_hour\": 15.0, \"weight_kg\": 110.0, \"data_spill_gb\": 1.25, \"recovery_cost_per_lb\": 0.75, \"recovery_cost_per_mib\": 0.0125}]}",
      "reward": null,
      "state": "What is the total time-based SLA penalty in USD for incident INC-V2-TR-008?",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "end_iso": "2026-10-10T22:00:00+00:00",
          "start_iso": "2026-10-10T08:30:00+00:00"
        },
        "name": "time-mcp__hours_between"
      },
      "observation": "13.5",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "expression": "round(13.5 * 15.0, 2)"
        },
        "name": "math-mcp__calculate"
      },
      "observation": "202.5",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 2,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"answered\", \"value\": 202.5, \"cites\": [\"INC-V2-TR-008\"], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 3,
      "thought": null
    }
  ],
  "task": "What is the total time-based SLA penalty in USD for incident INC-V2-TR-008?",
  "trajectory_id": "train_sft-0027-en"
}
```

## Sample 4 — source line 149

```json
{
  "final_response": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
  "metadata": {
    "case_id": "train_sft-0037",
    "kind": "abstain",
    "language": "en",
    "oracle_tool_calls": 1,
    "reward_mode": "evidence_gated",
    "schema_version": 2,
    "script": "latin",
    "task_id": "train_sft-0037-en",
    "world_split": "train"
  },
  "reward": 1.0,
  "steps": [
    {
      "action": {
        "arguments": {
          "sql": "SELECT * FROM microservices WHERE service_name = 'forex-vault'"
        },
        "name": "db-mcp__query_db"
      },
      "observation": "{\"rows\": []}",
      "reward": null,
      "state": "Using only the production database, report forex-vault circuit_breaker_pct. If that source is unavailable or has no such service, abstain.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 1,
      "thought": null
    }
  ],
  "task": "Using only the production database, report forex-vault circuit_breaker_pct. If that source is unavailable or has no such service, abstain.",
  "trajectory_id": "train_sft-0037-en"
}
```

## Sample 5 — source line 152

```json
{
  "final_response": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
  "metadata": {
    "case_id": "train_sft-0037",
    "kind": "abstain",
    "language": "te",
    "oracle_tool_calls": 1,
    "reward_mode": "evidence_gated",
    "schema_version": 2,
    "script": "latin",
    "task_id": "train_sft-0037-te",
    "world_split": "train"
  },
  "reward": 1.0,
  "steps": [
    {
      "action": {
        "arguments": {
          "sql": "SELECT * FROM microservices WHERE service_name = 'forex-vault'"
        },
        "name": "db-mcp__query_db"
      },
      "observation": "{\"rows\": []}",
      "reward": null,
      "state": "production database aadharanga maatrame forex-vault yokka circuit_breaker_pct cheppandi. Aa moolam andubaatulo lekapoyina seva lekapoyina samaadhaanam ivvavaddu.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 1,
      "thought": null
    }
  ],
  "task": "production database aadharanga maatrame forex-vault yokka circuit_breaker_pct cheppandi. Aa moolam andubaatulo lekapoyina seva lekapoyina samaadhaanam ivvavaddu.",
  "trajectory_id": "train_sft-0037-te"
}
```

## Sample 6 — source line 156

```json
{
  "final_response": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 1, \"cites\": [\"NOTION-V2-TR-211\", \"SLACK-V2-TR-211\", \"PR-V2-TR-211\"], \"stale_source\": \"NOTION-V2-TR-211\"}</final_answer>",
  "metadata": {
    "case_id": "train_sft-0038",
    "kind": "conflict",
    "language": "te",
    "oracle_tool_calls": 3,
    "reward_mode": "evidence_gated",
    "schema_version": 2,
    "script": "native",
    "task_id": "train_sft-0038-te",
    "world_split": "train"
  },
  "reward": 1.5,
  "steps": [
    {
      "action": {
        "arguments": {
          "query": "receipt-worker max_retries current configuration runbook"
        },
        "name": "notion-mcp__search_notion"
      },
      "observation": "[{\"page_id\": \"NOTION-V2-TR-211-STG\", \"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] max_retries\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"receipt-worker [STAGING-ONLY] max_retries = 7. Staging-only trial; do not apply this setting to production.\"}, {\"page_id\": \"NOTION-V2-TR-211\", \"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"prod\", \"title\": \"receipt-worker [PROD] max_retries\", \"updated_at\": \"2026-02-05T09:30:00+00:00\", \"snippet\": \"receipt-worker [PROD] max_retries = 4. Production runbook at publication. Tracked via Slack #deployments.\"}, {\"page_id\": \"NOTION-V2-TR-355-STG\", \"service_name\": \"notification-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] max_retries\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"notification-worker [STAGING-ONLY] max_retries = 4. Staging-only trial; do not apply this setting to production.\"}]",
      "reward": null,
      "state": "receipt-worker యొక్క అమలులో ఉన్న max_retries చెప్పండి; పాత సూచనలు వేరుగా ఉంటే ఆ పేజీని తెలియజేయండి.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "query": "receipt-worker max_retries"
        },
        "name": "slack-mcp__search_slack"
      },
      "observation": "[{\"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] max_retries\", \"msg_id\": \"SLACK-V2-TR-211-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"receipt-worker [STAGING-ONLY] max_retries = 7. Staging test; this is not a production setting.\"}, {\"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"prod\", \"title\": \"receipt-worker [PROD] max_retries\", \"msg_id\": \"SLACK-V2-TR-211\", \"channel\": \"#deployments\", \"posted_at\": \"2026-06-13T10:30:00+00:00\", \"text\": \"receipt-worker [PROD] max_retries = 10. Production deployment verified. Production hotfix follow-ups are tracked in GitHub PRs.\"}, {\"service_name\": \"notification-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] max_retries\", \"msg_id\": \"SLACK-V2-TR-355-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"notification-worker [STAGING-ONLY] max_retries = 4. Staging test; this is not a production setting.\"}]",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "query": "receipt-worker max_retries"
        },
        "name": "github-mcp__search_github_prs"
      },
      "observation": "[{\"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] max_retries\", \"pr_id\": \"PR-V2-TR-211-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"receipt-worker [STAGING-ONLY] max_retries = 7. Staging test; this is not a production setting.\"}, {\"service_name\": \"receipt-worker\", \"param_name\": \"max_retries\", \"environment\": \"prod\", \"title\": \"receipt-worker [PROD] max_retries\", \"pr_id\": \"PR-V2-TR-211\", \"merged_at\": \"2026-09-17T14:00:00+00:00\", \"summary\": \"receipt-worker [PROD] max_retries = 1. Production deployment verified.\"}, {\"service_name\": \"notification-worker\", \"param_name\": \"max_retries\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] max_retries\", \"pr_id\": \"PR-V2-TR-355-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"notification-worker [STAGING-ONLY] max_retries = 4. Staging test; this is not a production setting.\"}]",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 2,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 1, \"cites\": [\"NOTION-V2-TR-211\", \"SLACK-V2-TR-211\", \"PR-V2-TR-211\"], \"stale_source\": \"NOTION-V2-TR-211\"}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 3,
      "thought": null
    }
  ],
  "task": "receipt-worker యొక్క అమలులో ఉన్న max_retries చెప్పండి; పాత సూచనలు వేరుగా ఉంటే ఆ పేజీని తెలియజేయండి.",
  "trajectory_id": "train_sft-0038-te"
}
```

## Sample 7 — source line 178

```json
{
  "final_response": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 64, \"cites\": [\"NOTION-V2-TR-089\", \"PR-V2-TR-089\", \"SLACK-V2-TR-089\"], \"stale_source\": \"NOTION-V2-TR-089\"}</final_answer>",
  "metadata": {
    "case_id": "train_sft-0044",
    "kind": "conflict",
    "language": "hi",
    "oracle_tool_calls": 3,
    "reward_mode": "evidence_gated",
    "schema_version": 2,
    "script": "native",
    "task_id": "train_sft-0044-hi",
    "world_split": "train"
  },
  "reward": 1.5,
  "steps": [
    {
      "action": {
        "arguments": {
          "query": "checkout-api circuit_breaker_pct current configuration runbook"
        },
        "name": "notion-mcp__search_notion"
      },
      "observation": "[{\"page_id\": \"NOTION-V2-TR-089-STG\", \"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct = 10. Staging-only trial; do not apply this setting to production.\"}, {\"page_id\": \"NOTION-V2-TR-089\", \"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"prod\", \"title\": \"checkout-api [PROD] circuit_breaker_pct\", \"updated_at\": \"2026-02-05T09:30:00+00:00\", \"snippet\": \"checkout-api [PROD] circuit_breaker_pct = 46. Production runbook at publication. Tracked via GitHub PRs.\"}, {\"page_id\": \"NOTION-V2-TR-335-STG\", \"service_name\": \"dispute-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct = 58. Staging-only trial; do not apply this setting to production.\"}]",
      "reward": null,
      "state": "checkout-api का वर्तमान production circuit_breaker_pct क्या है? दस्तावेज़ और deployment records की तुलना करें और पुराने पन्ने को पहचानें।",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "query": "checkout-api circuit_breaker_pct"
        },
        "name": "github-mcp__search_github_prs"
      },
      "observation": "[{\"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct\", \"pr_id\": \"PR-V2-TR-089-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct = 10. Staging test; this is not a production setting.\"}, {\"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"prod\", \"title\": \"checkout-api [PROD] circuit_breaker_pct\", \"pr_id\": \"PR-V2-TR-089\", \"merged_at\": \"2026-06-13T10:30:00+00:00\", \"summary\": \"checkout-api [PROD] circuit_breaker_pct = 73. Production deployment verified. Production hotfix follow-ups are tracked in Slack #deployments.\"}, {\"service_name\": \"dispute-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct\", \"pr_id\": \"PR-V2-TR-335-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct = 58. Staging test; this is not a production setting.\"}]",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "query": "checkout-api circuit_breaker_pct"
        },
        "name": "slack-mcp__search_slack"
      },
      "observation": "[{\"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct\", \"msg_id\": \"SLACK-V2-TR-089-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"checkout-api [STAGING-ONLY] circuit_breaker_pct = 10. Staging test; this is not a production setting.\"}, {\"service_name\": \"checkout-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"prod\", \"title\": \"checkout-api [PROD] circuit_breaker_pct\", \"msg_id\": \"SLACK-V2-TR-089\", \"channel\": \"#deployments\", \"posted_at\": \"2026-09-17T14:00:00+00:00\", \"text\": \"checkout-api [PROD] circuit_breaker_pct = 64. Production deployment verified.\"}, {\"service_name\": \"dispute-api\", \"param_name\": \"circuit_breaker_pct\", \"environment\": \"staging\", \"title\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct\", \"msg_id\": \"SLACK-V2-TR-335-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"dispute-api [STAGING-ONLY] circuit_breaker_pct = 58. Staging test; this is not a production setting.\"}]",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 2,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 64, \"cites\": [\"NOTION-V2-TR-089\", \"PR-V2-TR-089\", \"SLACK-V2-TR-089\"], \"stale_source\": \"NOTION-V2-TR-089\"}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 3,
      "thought": null
    }
  ],
  "task": "checkout-api का वर्तमान production circuit_breaker_pct क्या है? दस्तावेज़ और deployment records की तुलना करें और पुराने पन्ने को पहचानें।",
  "trajectory_id": "train_sft-0044-hi"
}
```

## Sample 8 — source line 216

```json
{
  "final_response": "<final_answer>{\"status\": \"answered\", \"value\": 12.5, \"cites\": [\"INC-V2-TR-012\"], \"stale_source\": null}</final_answer>",
  "metadata": {
    "case_id": "train_sft-0053",
    "kind": "incident",
    "language": "te",
    "oracle_tool_calls": 3,
    "reward_mode": "evidence_gated",
    "schema_version": 2,
    "script": "latin",
    "task_id": "train_sft-0053-te",
    "world_split": "train"
  },
  "reward": 1.3,
  "steps": [
    {
      "action": {
        "arguments": {
          "sql": "SELECT * FROM production_incidents WHERE incident_id = 'INC-V2-TR-012'"
        },
        "name": "db-mcp__query_db"
      },
      "observation": "{\"rows\": [{\"incident_id\": \"INC-V2-TR-012\", \"service_name\": \"email-relay\", \"environment\": \"prod\", \"started_at\": \"2026-10-08T11:30:00+00:00\", \"resolved_at\": \"2026-10-08T12:30:00+00:00\", \"root_cause_pr\": \"PR-V2-TR-052\", \"penalty_rate_per_hour\": 12.5, \"weight_kg\": 12.5, \"data_spill_gb\": 2.5, \"recovery_cost_per_lb\": 0.75, \"recovery_cost_per_mib\": 0.025}]}",
      "reward": null,
      "state": "Sanghatana INC-V2-TR-012 kosam samayam aadharanga mottham SLA jarimaana USD lo entha?",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "end_iso": "2026-10-08T12:30:00+00:00",
          "start_iso": "2026-10-08T11:30:00+00:00"
        },
        "name": "time-mcp__hours_between"
      },
      "observation": "1.0",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "expression": "round(1.0 * 12.5, 2)"
        },
        "name": "math-mcp__calculate"
      },
      "observation": "12.5",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 2,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"answered\", \"value\": 12.5, \"cites\": [\"INC-V2-TR-012\"], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 3,
      "thought": null
    }
  ],
  "task": "Sanghatana INC-V2-TR-012 kosam samayam aadharanga mottham SLA jarimaana USD lo entha?",
  "trajectory_id": "train_sft-0053-te"
}
```

## Sample 9 — source line 229

```json
{
  "final_response": "<final_answer>{\"status\": \"answered\", \"value\": 400, \"cites\": [\"NOTION-V2-TR-213\", \"PR-V2-TR-213\"], \"stale_source\": null}</final_answer>",
  "metadata": {
    "case_id": "train_sft-0057",
    "kind": "consistent",
    "language": "en",
    "oracle_tool_calls": 3,
    "reward_mode": "evidence_gated",
    "schema_version": 2,
    "script": "latin",
    "task_id": "train_sft-0057-en",
    "world_split": "train"
  },
  "reward": 1.3,
  "steps": [
    {
      "action": {
        "arguments": {
          "query": "receipt-worker batch_size_mb current configuration runbook"
        },
        "name": "notion-mcp__search_notion"
      },
      "observation": "[{\"page_id\": \"NOTION-V2-TR-213-STG\", \"service_name\": \"receipt-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] batch_size_mb\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"receipt-worker [STAGING-ONLY] batch_size_mb = 70. Staging-only trial; do not apply this setting to production.\"}, {\"page_id\": \"NOTION-V2-TR-213\", \"service_name\": \"receipt-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"prod\", \"title\": \"receipt-worker [PROD] batch_size_mb\", \"updated_at\": \"2026-02-05T09:30:00+00:00\", \"snippet\": \"receipt-worker [PROD] batch_size_mb = 400. Production runbook at publication.\"}, {\"page_id\": \"NOTION-V2-TR-357-STG\", \"service_name\": \"notification-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] batch_size_mb\", \"updated_at\": \"2026-10-25T18:30:00+00:00\", \"snippet\": \"notification-worker [STAGING-ONLY] batch_size_mb = 424. Staging-only trial; do not apply this setting to production.\"}]",
      "reward": null,
      "state": "Please audit receipt-worker: reconcile its documented batch_size_mb with production deployment history.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "query": "receipt-worker batch_size_mb"
        },
        "name": "github-mcp__search_github_prs"
      },
      "observation": "[{\"service_name\": \"receipt-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] batch_size_mb\", \"pr_id\": \"PR-V2-TR-213-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"receipt-worker [STAGING-ONLY] batch_size_mb = 70. Staging test; this is not a production setting.\"}, {\"service_name\": \"receipt-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"prod\", \"title\": \"receipt-worker [PROD] batch_size_mb\", \"pr_id\": \"PR-V2-TR-213\", \"merged_at\": \"2026-03-11T11:00:00+00:00\", \"summary\": \"receipt-worker [PROD] batch_size_mb = 400. Production deployment verified.\"}, {\"service_name\": \"notification-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] batch_size_mb\", \"pr_id\": \"PR-V2-TR-357-STG\", \"merged_at\": \"2026-10-26T19:00:00+00:00\", \"summary\": \"notification-worker [STAGING-ONLY] batch_size_mb = 424. Staging test; this is not a production setting.\"}]",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "query": "receipt-worker batch_size_mb"
        },
        "name": "slack-mcp__search_slack"
      },
      "observation": "[{\"service_name\": \"receipt-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"receipt-worker [STAGING-ONLY] batch_size_mb\", \"msg_id\": \"SLACK-V2-TR-213-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"receipt-worker [STAGING-ONLY] batch_size_mb = 70. Staging test; this is not a production setting.\"}, {\"service_name\": \"notification-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"notification-worker [STAGING-ONLY] batch_size_mb\", \"msg_id\": \"SLACK-V2-TR-357-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"notification-worker [STAGING-ONLY] batch_size_mb = 424. Staging test; this is not a production setting.\"}, {\"service_name\": \"export-worker\", \"param_name\": \"batch_size_mb\", \"environment\": \"staging\", \"title\": \"export-worker [STAGING-ONLY] batch_size_mb\", \"msg_id\": \"SLACK-V2-TR-345-STG\", \"channel\": \"#staging\", \"posted_at\": \"2026-10-26T19:00:00+00:00\", \"text\": \"export-worker [STAGING-ONLY] batch_size_mb = 181. Staging test; this is not a production setting.\"}]",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 2,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"answered\", \"value\": 400, \"cites\": [\"NOTION-V2-TR-213\", \"PR-V2-TR-213\"], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 3,
      "thought": null
    }
  ],
  "task": "Please audit receipt-worker: reconcile its documented batch_size_mb with production deployment history.",
  "trajectory_id": "train_sft-0057-en"
}
```

## Sample 10 — source line 234

```json
{
  "final_response": "<final_answer>{\"status\": \"answered\", \"value\": 20.67, \"cites\": [\"INC-V2-TR-014\"], \"stale_source\": null}</final_answer>",
  "metadata": {
    "case_id": "train_sft-0058",
    "kind": "incident",
    "language": "hi",
    "oracle_tool_calls": 3,
    "reward_mode": "evidence_gated",
    "schema_version": 2,
    "script": "native",
    "task_id": "train_sft-0058-hi",
    "world_split": "train"
  },
  "reward": 1.3,
  "steps": [
    {
      "action": {
        "arguments": {
          "sql": "SELECT * FROM production_incidents WHERE incident_id = 'INC-V2-TR-014'"
        },
        "name": "db-mcp__query_db"
      },
      "observation": "{\"rows\": [{\"incident_id\": \"INC-V2-TR-014\", \"service_name\": \"reconciliation-worker\", \"environment\": \"prod\", \"started_at\": \"2026-10-14T23:30:00+00:00\", \"resolved_at\": \"2026-10-15T01:00:00+00:00\", \"root_cause_pr\": \"PR-V2-TR-227\", \"penalty_rate_per_hour\": 12.5, \"weight_kg\": 12.5, \"data_spill_gb\": 2.5, \"recovery_cost_per_lb\": 0.75, \"recovery_cost_per_mib\": 0.0125}]}",
      "reward": null,
      "state": "घटना INC-V2-TR-014 के प्रभावित भार को pounds में मानकर प्रति-pound शुल्क से कुल recovery cost USD में बताइए।",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "from_unit": "kg",
          "to_unit": "lb",
          "value": 12.5
        },
        "name": "unit-converter-mcp__convert_unit"
      },
      "observation": "27.557782773109697",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "expression": "round(27.557782773109697 * 0.75, 2)"
        },
        "name": "math-mcp__calculate"
      },
      "observation": "20.67",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 2,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"answered\", \"value\": 20.67, \"cites\": [\"INC-V2-TR-014\"], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 3,
      "thought": null
    }
  ],
  "task": "घटना INC-V2-TR-014 के प्रभावित भार को pounds में मानकर प्रति-pound शुल्क से कुल recovery cost USD में बताइए।",
  "trajectory_id": "train_sft-0058-hi"
}
```

---

# File: `val_train_80.jsonl`

Source SHA-256: `4eb608f1391596afe2ad62f67e9c5a68e5b396838b8c97f130638d9510f3b254`

## Sample 1 — source line 3

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_val-0000",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-TR-023",
    "PR-V2-TR-023"
  ],
  "gold_value": 13,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "hinglish",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "circuit_breaker_pct",
  "pool": "train_val",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Bhai, webhook-dispatcher ka actual production circuit_breaker_pct kya hai? Runbook aur deployment updates match karke outdated page flag karo.",
      "role": "user"
    }
  ],
  "question": "Bhai, webhook-dispatcher ka actual production circuit_breaker_pct kya hai? Runbook aur deployment updates match karke outdated page flag karo.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "webhook-dispatcher",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_val-0000-hinglish",
  "world_split": "train"
}
```

## Sample 2 — source line 8

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_val-0001",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "te",
  "missing_entity": true,
  "oracle_optimal_steps": 1,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "batch_size_mb",
  "pool": "train_val",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "production database aadharanga maatrame escrow-vault yokka batch_size_mb cheppandi. Aa moolam andubaatulo lekapoyina seva lekapoyina samaadhaanam ivvavaddu.",
      "role": "user"
    }
  ],
  "question": "production database aadharanga maatrame escrow-vault yokka batch_size_mb cheppandi. Aa moolam andubaatulo lekapoyina seva lekapoyina samaadhaanam ivvavaddu.",
  "reference_tool_sequence": [
    "db-mcp__query_db"
  ],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "escrow-vault",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_val-0001-te",
  "world_split": "train"
}
```

## Sample 3 — source line 9

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_val-0002",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-V2-TR-219",
    "SLACK-V2-TR-219"
  ],
  "gold_value": 406,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "consistent",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "batch_size_mb",
  "pool": "train_val",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "What is the active production batch_size_mb for invoice-store? Compare the runbook with deployment records and flag any outdated page.",
      "role": "user"
    }
  ],
  "question": "What is the active production batch_size_mb for invoice-store? Compare the runbook with deployment records and flag any outdated page.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "invoice-store",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_val-0002-en",
  "world_split": "train"
}
```

## Sample 4 — source line 29

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_val-0007",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "en",
  "missing_entity": true,
  "oracle_optimal_steps": 1,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "batch_size_mb",
  "pool": "train_val",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Using only the production database, report escrow-dispatcher batch_size_mb. If that source is unavailable or has no such service, abstain.",
      "role": "user"
    }
  ],
  "question": "Using only the production database, report escrow-dispatcher batch_size_mb. If that source is unavailable or has no such service, abstain.",
  "reference_tool_sequence": [
    "db-mcp__query_db"
  ],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "escrow-dispatcher",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_val-0007-en",
  "world_split": "train"
}
```

## Sample 5 — source line 39

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_val-0009",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "abstain",
  "language": "hinglish",
  "missing_entity": false,
  "oracle_optimal_steps": 0,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_hours",
  "pool": "train_val",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "settlement-worker ka sla_hours production database se hi do. Source unavailable ho ya service na mile toh abstain karo.",
      "role": "user"
    }
  ],
  "question": "settlement-worker ka sla_hours production database se hi do. Source unavailable ho ya service na mile toh abstain karo.",
  "reference_tool_sequence": [],
  "request_mode": "database_only",
  "required_mcps": [
    "db-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "settlement-worker",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_val-0009-hinglish",
  "world_split": "train"
}
```

## Sample 6 — source line 49

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_val-0012",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TR-072"
  ],
  "gold_value": 315.0,
  "incident_id": "INC-V2-TR-072",
  "incident_subtype": "sla_penalty",
  "kind": "incident",
  "language": "en",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_penalty_usd",
  "pool": "train_val",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "What is the total time-based SLA penalty in USD for incident INC-V2-TR-072?",
      "role": "user"
    }
  ],
  "question": "What is the total time-based SLA penalty in USD for incident INC-V2-TR-072?",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "time-mcp__hours_between",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "coupon-engine",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_val-0012-en",
  "world_split": "train"
}
```

## Sample 7 — source line 50

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_val-0012",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TR-072"
  ],
  "gold_value": 315.0,
  "incident_id": "INC-V2-TR-072",
  "incident_subtype": "sla_penalty",
  "kind": "incident",
  "language": "hi",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_penalty_usd",
  "pool": "train_val",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "घटना INC-V2-TR-072 का कुल समय-आधारित SLA जुर्माना USD में कितना है?",
      "role": "user"
    }
  ],
  "question": "घटना INC-V2-TR-072 का कुल समय-आधारित SLA जुर्माना USD में कितना है?",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "time-mcp__hours_between",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "coupon-engine",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_val-0012-hi",
  "world_split": "train"
}
```

## Sample 8 — source line 52

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_val-0012",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-V2-TR-072"
  ],
  "gold_value": 315.0,
  "incident_id": "INC-V2-TR-072",
  "incident_subtype": "sla_penalty",
  "kind": "incident",
  "language": "te",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_penalty_usd",
  "pool": "train_val",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "సంఘటన INC-V2-TR-072 కోసం సమయం ఆధారంగా మొత్తం SLA జరిమానా USD లో ఎంత?",
      "role": "user"
    }
  ],
  "question": "సంఘటన INC-V2-TR-072 కోసం సమయం ఆధారంగా మొత్తం SLA జరిమానా USD లో ఎంత?",
  "reference_tool_sequence": [
    "db-mcp__query_db",
    "time-mcp__hours_between",
    "math-mcp__calculate"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "coupon-engine",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train_val-0012-te",
  "world_split": "train"
}
```

## Sample 9 — source line 54

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train_val-0013",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-TR-010",
    "PR-V2-TR-010"
  ],
  "gold_value": 28,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "hi",
  "missing_entity": false,
  "oracle_optimal_steps": 2,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "sla_hours",
  "pool": "train_val",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Kripya auth-proxy ke vartamaan production sla_hours ko dastavez aur tainaati ke pramaanon se jaanchkar puraana panna bataaiye.",
      "role": "user"
    }
  ],
  "question": "Kripya auth-proxy ke vartamaan production sla_hours ko dastavez aur tainaati ke pramaanon se jaanchkar puraana panna bataaiye.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "latin",
  "service_name": "auth-proxy",
  "stale_doc_id": "NOTION-V2-TR-010",
  "stale_trap_value": 7,
  "task_id": "train_val-0013-hi",
  "world_split": "train"
}
```

## Sample 10 — source line 60

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train_val-0014",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-V2-TR-063",
    "PR-V2-TR-063",
    "SLACK-V2-TR-063"
  ],
  "gold_value": 103,
  "incident_id": null,
  "incident_subtype": null,
  "kind": "conflict",
  "language": "te",
  "missing_entity": false,
  "oracle_optimal_steps": 3,
  "oracle_steps_semantics": "Measured discovery-policy length; not a proof of global SQL/tool optimality.",
  "param_name": "batch_size_mb",
  "pool": "train_val",
  "prompt": [
    {
      "content": "You are an enterprise operations assistant. Discover evidence with the available tools; do not invent service names, configuration values, citations or incident fields. Search results may contain sibling services, older production records, and newer STAGING-ONLY records. Match the requested entity, parameter and production scope before comparing dates. Resolve documented settings against deployment evidence; follow tracking hints found in observations. An explicitly database-only request cannot be satisfied by another source. Monetary totals are USD rounded to two decimal places; math-mcp supports round(arithmetic,2). GB is decimal (1 GB = 1e9 bytes); MiB is 2^20 bytes. Output exactly one XML-wrapped JSON turn, without explanation:\n<tool_call>{\"server\":\"active server\",\"tool\":\"available tool\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"single scalar or null\",\"cites\":[\"actually retrieved IDs\"],\"stale_source\":null}</final_answer>\nUse conflict_resolved when a documented production value is superseded, identifying its outdated page; answered when evidence agrees; abstain when the requested source is unavailable or entity absent. Incident requests identify the affected service through incident evidence. Database schema: microservices(service_name TEXT PRIMARY KEY,owner_handle TEXT,environment TEXT,timeout_sec INTEGER,max_retries INTEGER,rate_limit_rpm INTEGER,batch_size_mb INTEGER,sla_hours INTEGER,circuit_breaker_pct INTEGER,updated_at TEXT,last_pr TEXT,evidence_id TEXT); production_incidents(incident_id,service_name,environment,started_at,resolved_at,root_cause_pr,penalty_rate_per_hour,weight_kg,data_spill_gb,recovery_cost_per_lb,recovery_cost_per_mib)\nActive schemas: [{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "session-cache యొక్క అమలులో ఉన్న batch_size_mb చెప్పండి; పాత సూచనలు వేరుగా ఉంటే ఆ పేజీని తెలియజేయండి.",
      "role": "user"
    }
  ],
  "question": "session-cache యొక్క అమలులో ఉన్న batch_size_mb చెప్పండి; పాత సూచనలు వేరుగా ఉంటే ఆ పేజీని తెలియజేయండి.",
  "reference_tool_sequence": [
    "notion-mcp__search_notion",
    "github-mcp__search_github_prs",
    "slack-mcp__search_slack"
  ],
  "request_mode": "audit",
  "required_mcps": [
    "notion-mcp",
    "github-mcp",
    "slack-mcp"
  ],
  "schema_version": 2,
  "script": "native",
  "service_name": "session-cache",
  "stale_doc_id": "NOTION-V2-TR-063",
  "stale_trap_value": 37,
  "task_id": "train_val-0014-te",
  "world_split": "train"
}
```

---

# File: `world_repo_style.json`

Source SHA-256: `e0cc20b5d5ccc5e1dc6ab8042390077d4fc040760c9aae74508e95e665a19df6`

```json
{
  "case_pools": {
    "holdout_repo_style": [
      {
        "case_id": "holdout_repo_style-0000",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "timeout_sec",
        "pool": "holdout_repo_style",
        "request_mode": "audit",
        "service_name": "pydantic-schema-validator"
      },
      {
        "case_id": "holdout_repo_style-0001",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": true,
        "param_name": "circuit_breaker_pct",
        "pool": "holdout_repo_style",
        "request_mode": "database_only",
        "service_name": "asgi-hedger"
      },
      {
        "case_id": "holdout_repo_style-0002",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "circuit_breaker_pct",
        "pool": "holdout_repo_style",
        "request_mode": "audit",
        "service_name": "rq-job-worker"
      },
      {
        "case_id": "holdout_repo_style-0003",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "sla_hours",
        "pool": "holdout_repo_style",
        "request_mode": "audit",
        "service_name": "falcon-api-middleware"
      },
      {
        "case_id": "holdout_repo_style-0004",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "holdout_repo_style",
        "request_mode": "audit",
        "service_name": "quart-websocket-worker"
      },
      {
        "case_id": "holdout_repo_style-0005",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "holdout_repo_style",
        "request_mode": "audit",
        "service_name": "trl-rollout-worker"
      },
      {
        "case_id": "holdout_repo_style-0006",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "holdout_repo_style",
        "request_mode": "audit",
        "service_name": "dramatiq-broker-worker"
      },
      {
        "case_id": "holdout_repo_style-0007",
        "incident_id": "INC-V2-OSS-000",
        "incident_subtype": "sla_penalty",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "sla_penalty_usd",
        "pool": "holdout_repo_style",
        "request_mode": "audit",
        "service_name": "quart-websocket-worker"
      },
      {
        "case_id": "holdout_repo_style-0008",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "sla_hours",
        "pool": "holdout_repo_style",
        "request_mode": "audit",
        "service_name": "httpx-connection-pool"
      },
      {
        "case_id": "holdout_repo_style-0009",
        "incident_id": "INC-V2-OSS-001",
        "incident_subtype": "config_audit",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "holdout_repo_style",
        "request_mode": "audit",
        "service_name": "redis-stream-consumer"
      }
    ]
  },
  "employees": [
    "@v2-oss_engineer_00",
    "@v2-oss_engineer_01",
    "@v2-oss_engineer_02",
    "@v2-oss_engineer_03",
    "@v2-oss_engineer_04",
    "@v2-oss_engineer_05",
    "@v2-oss_engineer_06",
    "@v2-oss_engineer_07",
    "@v2-oss_engineer_08",
    "@v2-oss_engineer_09"
  ],
  "facts": [
    {
      "cross_channel": false,
      "current_value": 18,
      "db_id": "DB-V2-OSS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 18,
      "intermediate_value": 84,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-OSS-000",
      "owner_handle": "@v2-oss_engineer_00",
      "param_name": "timeout_sec",
      "service_name": "fastapi-gzip-middleware",
      "source_id": "SLACK-V2-OSS-000",
      "source_server": "slack-mcp",
      "staging_value": 66,
      "tracking_hint": "slack",
      "updated_date": "2026-03-11T11:00:00+00:00",
      "was_updated": false
    },
    {
      "cross_channel": false,
      "current_value": 9,
      "db_id": "DB-V2-OSS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 9,
      "intermediate_value": 6,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-OSS-001",
      "owner_handle": "@v2-oss_engineer_01",
      "param_name": "max_retries",
      "service_name": "fastapi-gzip-middleware",
      "source_id": "SLACK-V2-OSS-001",
      "source_server": "slack-mcp",
      "staging_value": 12,
      "tracking_hint": "none",
      "updated_date": "2026-03-11T11:00:00+00:00",
      "was_updated": false
    },
    {
      "cross_channel": false,
      "current_value": 2724,
      "db_id": "DB-V2-OSS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 939,
      "intermediate_value": 3294,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-OSS-002",
      "owner_handle": "@v2-oss_engineer_02",
      "param_name": "rate_limit_rpm",
      "service_name": "fastapi-gzip-middleware",
      "source_id": "PR-V2-OSS-002",
      "source_server": "github-mcp",
      "staging_value": 3285,
      "tracking_hint": "none",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 384,
      "db_id": "DB-V2-OSS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 126,
      "intermediate_value": 294,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-OSS-003",
      "owner_handle": "@v2-oss_engineer_03",
      "param_name": "batch_size_mb",
      "service_name": "fastapi-gzip-middleware",
      "source_id": "SLACK-V2-OSS-003",
      "source_server": "slack-mcp",
      "staging_value": 153,
      "tracking_hint": "slack",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 39,
      "db_id": "DB-V2-OSS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 39,
      "intermediate_value": 18,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-OSS-004",
      "owner_handle": "@v2-oss_engineer_04",
      "param_name": "sla_hours",
      "service_name": "fastapi-gzip-middleware",
      "source_id": "SLACK-V2-OSS-004",
      "source_server": "slack-mcp",
      "staging_value": 42,
      "tracking_hint": "none",
      "updated_date": "2026-03-11T11:00:00+00:00",
      "was_updated": false
    },
    {
      "cross_channel": false,
      "current_value": 18,
      "db_id": "DB-V2-OSS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 42,
      "intermediate_value": 45,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-OSS-005",
      "owner_handle": "@v2-oss_engineer_05",
      "param_name": "circuit_breaker_pct",
      "service_name": "fastapi-gzip-middleware",
      "source_id": "PR-V2-OSS-005",
      "source_server": "github-mcp",
      "staging_value": 78,
      "tracking_hint": "github",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 66,
      "db_id": "DB-V2-OSS-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 120,
      "intermediate_value": 180,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-OSS-006",
      "owner_handle": "@v2-oss_engineer_06",
      "param_name": "timeout_sec",
      "service_name": "litellm-router-proxy",
      "source_id": "SLACK-V2-OSS-006",
      "source_server": "slack-mcp",
      "staging_value": 108,
      "tracking_hint": "none",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": true,
      "current_value": 12,
      "db_id": "DB-V2-OSS-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 3,
      "intermediate_value": 9,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-OSS-007",
      "owner_handle": "@v2-oss_engineer_07",
      "param_name": "max_retries",
      "service_name": "litellm-router-proxy",
      "source_id": "SLACK-V2-OSS-007",
      "source_server": "github-mcp",
      "staging_value": 6,
      "tracking_hint": "none",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 4518,
      "db_id": "DB-V2-OSS-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 4356,
      "intermediate_value": 1440,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-OSS-008",
      "owner_handle": "@v2-oss_engineer_08",
      "param_name": "rate_limit_rpm",
      "service_name": "litellm-router-proxy",
      "source_id": "SLACK-V2-OSS-008",
      "source_server": "slack-mcp",
      "staging_value": 2145,
      "tracking_hint": "none",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 495,
      "db_id": "DB-V2-OSS-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 120,
      "intermediate_value": 351,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-OSS-009",
      "owner_handle": "@v2-oss_engineer_09",
      "param_name": "batch_size_mb",
      "service_name": "litellm-router-proxy",
      "source_id": "SLACK-V2-OSS-009",
      "source_server": "slack-mcp",
      "staging_value": 195,
      "tracking_hint": "slack",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    }
  ],
  "incidents": [
    {
      "data_spill_gb": 6.0,
      "environment": "prod",
      "incident_id": "INC-V2-OSS-000",
      "penalty_rate_per_hour": 22.0,
      "recovery_cost_per_lb": 1.25,
      "recovery_cost_per_mib": 0.075,
      "resolved_at": "2026-10-06T09:00:00+00:00",
      "root_cause_pr": "PR-V2-OSS-170",
      "service_name": "quart-websocket-worker",
      "started_at": "2026-10-06T02:30:00+00:00",
      "weight_kg": 42.5
    },
    {
      "data_spill_gb": 12.75,
      "environment": "prod",
      "incident_id": "INC-V2-OSS-001",
      "penalty_rate_per_hour": 18.75,
      "recovery_cost_per_lb": 2.0,
      "recovery_cost_per_mib": 0.075,
      "resolved_at": "2026-10-08T20:30:00+00:00",
      "root_cause_pr": "PR-V2-OSS-079",
      "service_name": "redis-stream-consumer",
      "started_at": "2026-10-08T01:30:00+00:00",
      "weight_kg": 42.5
    },
    {
      "data_spill_gb": 12.75,
      "environment": "prod",
      "incident_id": "INC-V2-OSS-002",
      "penalty_rate_per_hour": 15.0,
      "recovery_cost_per_lb": 2.0,
      "recovery_cost_per_mib": 0.0125,
      "resolved_at": "2026-10-05T12:30:00+00:00",
      "root_cause_pr": "PR-V2-OSS-174",
      "service_name": "falcon-api-middleware",
      "started_at": "2026-10-05T11:30:00+00:00",
      "weight_kg": 12.5
    },
    {
      "data_spill_gb": 2.5,
      "environment": "prod",
      "incident_id": "INC-V2-OSS-003",
      "penalty_rate_per_hour": 27.5,
      "recovery_cost_per_lb": 0.75,
      "recovery_cost_per_mib": 0.025,
      "resolved_at": "2026-10-16T02:00:00+00:00",
      "root_cause_pr": "PR-V2-OSS-123",
      "service_name": "dramatiq-broker-worker",
      "started_at": "2026-10-15T19:30:00+00:00",
      "weight_kg": 24.0
    }
  ],
  "provenance": {
    "kind": "constructed_oss_style_v2",
    "notes": "Domain-valid fixtures, not historical upstream snapshots.",
    "verified_real_changes": false
  },
  "schema_version": 2,
  "search_records": {
    "github-mcp": [
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "timeout_sec",
        "pr_id": "PR-V2-OSS-000-STG",
        "service_name": "fastapi-gzip-middleware",
        "summary": "fastapi-gzip-middleware [STAGING-ONLY] timeout_sec = 66. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] timeout_sec"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "max_retries",
        "pr_id": "PR-V2-OSS-001-STG",
        "service_name": "fastapi-gzip-middleware",
        "summary": "fastapi-gzip-middleware [STAGING-ONLY] max_retries = 12. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] max_retries"
      },
      {
        "environment": "prod",
        "merged_at": "2026-09-17T14:00:00+00:00",
        "param_name": "rate_limit_rpm",
        "pr_id": "PR-V2-OSS-002",
        "service_name": "fastapi-gzip-middleware",
        "summary": "fastapi-gzip-middleware [PROD] rate_limit_rpm = 2724. Production deployment verified.",
        "title": "fastapi-gzip-middleware [PROD] rate_limit_rpm"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "rate_limit_rpm",
        "pr_id": "PR-V2-OSS-002-STG",
        "service_name": "fastapi-gzip-middleware",
        "summary": "fastapi-gzip-middleware [STAGING-ONLY] rate_limit_rpm = 3285. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] rate_limit_rpm"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "batch_size_mb",
        "pr_id": "PR-V2-OSS-003-STG",
        "service_name": "fastapi-gzip-middleware",
        "summary": "fastapi-gzip-middleware [STAGING-ONLY] batch_size_mb = 153. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] batch_size_mb"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "sla_hours",
        "pr_id": "PR-V2-OSS-004-STG",
        "service_name": "fastapi-gzip-middleware",
        "summary": "fastapi-gzip-middleware [STAGING-ONLY] sla_hours = 42. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] sla_hours"
      },
      {
        "environment": "prod",
        "merged_at": "2026-09-17T14:00:00+00:00",
        "param_name": "circuit_breaker_pct",
        "pr_id": "PR-V2-OSS-005",
        "service_name": "fastapi-gzip-middleware",
        "summary": "fastapi-gzip-middleware [PROD] circuit_breaker_pct = 18. Production deployment verified.",
        "title": "fastapi-gzip-middleware [PROD] circuit_breaker_pct"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "circuit_breaker_pct",
        "pr_id": "PR-V2-OSS-005-STG",
        "service_name": "fastapi-gzip-middleware",
        "summary": "fastapi-gzip-middleware [STAGING-ONLY] circuit_breaker_pct = 78. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] circuit_breaker_pct"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "timeout_sec",
        "pr_id": "PR-V2-OSS-006-STG",
        "service_name": "litellm-router-proxy",
        "summary": "litellm-router-proxy [STAGING-ONLY] timeout_sec = 108. Staging test; this is not a production setting.",
        "title": "litellm-router-proxy [STAGING-ONLY] timeout_sec"
      },
      {
        "environment": "prod",
        "merged_at": "2026-06-13T10:30:00+00:00",
        "param_name": "max_retries",
        "pr_id": "PR-V2-OSS-007",
        "service_name": "litellm-router-proxy",
        "summary": "litellm-router-proxy [PROD] max_retries = 9. Production deployment verified. Production hotfix follow-ups are tracked in Slack #deployments.",
        "title": "litellm-router-proxy [PROD] max_retries"
      }
    ],
    "notion-mcp": [
      {
        "environment": "prod",
        "page_id": "NOTION-V2-OSS-000",
        "param_name": "timeout_sec",
        "service_name": "fastapi-gzip-middleware",
        "snippet": "fastapi-gzip-middleware [PROD] timeout_sec = 18. Production runbook at publication. Tracked via Slack #deployments.",
        "title": "fastapi-gzip-middleware [PROD] timeout_sec",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-OSS-000-STG",
        "param_name": "timeout_sec",
        "service_name": "fastapi-gzip-middleware",
        "snippet": "fastapi-gzip-middleware [STAGING-ONLY] timeout_sec = 66. Staging-only trial; do not apply this setting to production.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] timeout_sec",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-OSS-001",
        "param_name": "max_retries",
        "service_name": "fastapi-gzip-middleware",
        "snippet": "fastapi-gzip-middleware [PROD] max_retries = 9. Production runbook at publication.",
        "title": "fastapi-gzip-middleware [PROD] max_retries",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-OSS-001-STG",
        "param_name": "max_retries",
        "service_name": "fastapi-gzip-middleware",
        "snippet": "fastapi-gzip-middleware [STAGING-ONLY] max_retries = 12. Staging-only trial; do not apply this setting to production.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] max_retries",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-OSS-002",
        "param_name": "rate_limit_rpm",
        "service_name": "fastapi-gzip-middleware",
        "snippet": "fastapi-gzip-middleware [PROD] rate_limit_rpm = 939. Production runbook at publication.",
        "title": "fastapi-gzip-middleware [PROD] rate_limit_rpm",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-OSS-002-STG",
        "param_name": "rate_limit_rpm",
        "service_name": "fastapi-gzip-middleware",
        "snippet": "fastapi-gzip-middleware [STAGING-ONLY] rate_limit_rpm = 3285. Staging-only trial; do not apply this setting to production.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] rate_limit_rpm",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-OSS-003",
        "param_name": "batch_size_mb",
        "service_name": "fastapi-gzip-middleware",
        "snippet": "fastapi-gzip-middleware [PROD] batch_size_mb = 126. Production runbook at publication. Tracked via Slack #deployments.",
        "title": "fastapi-gzip-middleware [PROD] batch_size_mb",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-OSS-003-STG",
        "param_name": "batch_size_mb",
        "service_name": "fastapi-gzip-middleware",
        "snippet": "fastapi-gzip-middleware [STAGING-ONLY] batch_size_mb = 153. Staging-only trial; do not apply this setting to production.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] batch_size_mb",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-OSS-004",
        "param_name": "sla_hours",
        "service_name": "fastapi-gzip-middleware",
        "snippet": "fastapi-gzip-middleware [PROD] sla_hours = 39. Production runbook at publication.",
        "title": "fastapi-gzip-middleware [PROD] sla_hours",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-OSS-004-STG",
        "param_name": "sla_hours",
        "service_name": "fastapi-gzip-middleware",
        "snippet": "fastapi-gzip-middleware [STAGING-ONLY] sla_hours = 42. Staging-only trial; do not apply this setting to production.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] sla_hours",
        "updated_at": "2026-10-25T18:30:00+00:00"
      }
    ],
    "slack-mcp": [
      {
        "channel": "#deployments",
        "environment": "prod",
        "msg_id": "SLACK-V2-OSS-000",
        "param_name": "timeout_sec",
        "posted_at": "2026-03-11T11:00:00+00:00",
        "service_name": "fastapi-gzip-middleware",
        "text": "fastapi-gzip-middleware [PROD] timeout_sec = 18. Production deployment verified.",
        "title": "fastapi-gzip-middleware [PROD] timeout_sec"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-OSS-000-STG",
        "param_name": "timeout_sec",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "fastapi-gzip-middleware",
        "text": "fastapi-gzip-middleware [STAGING-ONLY] timeout_sec = 66. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] timeout_sec"
      },
      {
        "channel": "#deployments",
        "environment": "prod",
        "msg_id": "SLACK-V2-OSS-001",
        "param_name": "max_retries",
        "posted_at": "2026-03-11T11:00:00+00:00",
        "service_name": "fastapi-gzip-middleware",
        "text": "fastapi-gzip-middleware [PROD] max_retries = 9. Production deployment verified.",
        "title": "fastapi-gzip-middleware [PROD] max_retries"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-OSS-001-STG",
        "param_name": "max_retries",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "fastapi-gzip-middleware",
        "text": "fastapi-gzip-middleware [STAGING-ONLY] max_retries = 12. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] max_retries"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-OSS-002-STG",
        "param_name": "rate_limit_rpm",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "fastapi-gzip-middleware",
        "text": "fastapi-gzip-middleware [STAGING-ONLY] rate_limit_rpm = 3285. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] rate_limit_rpm"
      },
      {
        "channel": "#deployments",
        "environment": "prod",
        "msg_id": "SLACK-V2-OSS-003",
        "param_name": "batch_size_mb",
        "posted_at": "2026-09-17T14:00:00+00:00",
        "service_name": "fastapi-gzip-middleware",
        "text": "fastapi-gzip-middleware [PROD] batch_size_mb = 384. Production deployment verified.",
        "title": "fastapi-gzip-middleware [PROD] batch_size_mb"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-OSS-003-STG",
        "param_name": "batch_size_mb",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "fastapi-gzip-middleware",
        "text": "fastapi-gzip-middleware [STAGING-ONLY] batch_size_mb = 153. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] batch_size_mb"
      },
      {
        "channel": "#deployments",
        "environment": "prod",
        "msg_id": "SLACK-V2-OSS-004",
        "param_name": "sla_hours",
        "posted_at": "2026-03-11T11:00:00+00:00",
        "service_name": "fastapi-gzip-middleware",
        "text": "fastapi-gzip-middleware [PROD] sla_hours = 39. Production deployment verified.",
        "title": "fastapi-gzip-middleware [PROD] sla_hours"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-OSS-004-STG",
        "param_name": "sla_hours",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "fastapi-gzip-middleware",
        "text": "fastapi-gzip-middleware [STAGING-ONLY] sla_hours = 42. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] sla_hours"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-OSS-005-STG",
        "param_name": "circuit_breaker_pct",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "fastapi-gzip-middleware",
        "text": "fastapi-gzip-middleware [STAGING-ONLY] circuit_breaker_pct = 78. Staging test; this is not a production setting.",
        "title": "fastapi-gzip-middleware [STAGING-ONLY] circuit_breaker_pct"
      }
    ]
  },
  "seed": 137,
  "services": [
    "fastapi-gzip-middleware",
    "litellm-router-proxy",
    "pydantic-schema-validator",
    "vllm-kv-cache-manager",
    "uvicorn-worker-pool",
    "fastapi-request-router",
    "litellm-retry-handler",
    "pydantic-settings-loader",
    "vllm-scheduler",
    "uvicorn-keepalive-manager"
  ],
  "split": "repo_style",
  "world_id": "0a27e13bf742cc5ce75923b132a8b6fb46fccf2372108a4a46bdef32d8003456"
}
```

---

# File: `world_test_synth.json`

Source SHA-256: `664177831119ebd56744a45791a43510600294bcca87d4176b4f45c50eab3985`

```json
{
  "case_pools": {
    "holdout_synth": [
      {
        "case_id": "holdout_synth-0000",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "rate_limit_rpm",
        "pool": "holdout_synth",
        "request_mode": "audit",
        "service_name": "statement-worker"
      },
      {
        "case_id": "holdout_synth-0001",
        "incident_id": "INC-V2-TS-000",
        "incident_subtype": "sla_penalty",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "sla_penalty_usd",
        "pool": "holdout_synth",
        "request_mode": "audit",
        "service_name": "beneficiary-store"
      },
      {
        "case_id": "holdout_synth-0002",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": true,
        "param_name": "circuit_breaker_pct",
        "pool": "holdout_synth",
        "request_mode": "database_only",
        "service_name": "crypto-hedger"
      },
      {
        "case_id": "holdout_synth-0003",
        "incident_id": "INC-V2-TS-001",
        "incident_subtype": "config_audit",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "max_retries",
        "pool": "holdout_synth",
        "request_mode": "audit",
        "service_name": "clearing-agent"
      },
      {
        "case_id": "holdout_synth-0004",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "holdout_synth",
        "request_mode": "audit",
        "service_name": "clearing-agent"
      },
      {
        "case_id": "holdout_synth-0005",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": false,
        "param_name": "rate_limit_rpm",
        "pool": "holdout_synth",
        "request_mode": "database_only",
        "service_name": "token-vault"
      },
      {
        "case_id": "holdout_synth-0006",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "holdout_synth",
        "request_mode": "audit",
        "service_name": "wallet-bridge"
      },
      {
        "case_id": "holdout_synth-0007",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "holdout_synth",
        "request_mode": "audit",
        "service_name": "merchant-registry"
      },
      {
        "case_id": "holdout_synth-0008",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "max_retries",
        "pool": "holdout_synth",
        "request_mode": "audit",
        "service_name": "wallet-bridge"
      },
      {
        "case_id": "holdout_synth-0009",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": true,
        "param_name": "batch_size_mb",
        "pool": "holdout_synth",
        "request_mode": "database_only",
        "service_name": "crypto-gate"
      }
    ]
  },
  "employees": [
    "@v2-ts_engineer_00",
    "@v2-ts_engineer_01",
    "@v2-ts_engineer_02",
    "@v2-ts_engineer_03",
    "@v2-ts_engineer_04",
    "@v2-ts_engineer_05",
    "@v2-ts_engineer_06",
    "@v2-ts_engineer_07",
    "@v2-ts_engineer_08",
    "@v2-ts_engineer_09"
  ],
  "facts": [
    {
      "cross_channel": false,
      "current_value": 77,
      "db_id": "DB-V2-TS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 80,
      "intermediate_value": 41,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TS-000",
      "owner_handle": "@v2-ts_engineer_00",
      "param_name": "timeout_sec",
      "service_name": "kyc-verifier",
      "source_id": "PR-V2-TS-000",
      "source_server": "github-mcp",
      "staging_value": 119,
      "tracking_hint": "github",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 2,
      "db_id": "DB-V2-TS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 2,
      "intermediate_value": 8,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TS-001",
      "owner_handle": "@v2-ts_engineer_01",
      "param_name": "max_retries",
      "service_name": "kyc-verifier",
      "source_id": "PR-V2-TS-001",
      "source_server": "github-mcp",
      "staging_value": 11,
      "tracking_hint": "github",
      "updated_date": "2026-03-11T11:00:00+00:00",
      "was_updated": false
    },
    {
      "cross_channel": false,
      "current_value": 2690,
      "db_id": "DB-V2-TS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 2690,
      "intermediate_value": 3866,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-TS-002",
      "owner_handle": "@v2-ts_engineer_02",
      "param_name": "rate_limit_rpm",
      "service_name": "kyc-verifier",
      "source_id": "SLACK-V2-TS-002",
      "source_server": "slack-mcp",
      "staging_value": 3716,
      "tracking_hint": "slack",
      "updated_date": "2026-03-11T11:00:00+00:00",
      "was_updated": false
    },
    {
      "cross_channel": false,
      "current_value": 179,
      "db_id": "DB-V2-TS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 179,
      "intermediate_value": 371,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TS-003",
      "owner_handle": "@v2-ts_engineer_03",
      "param_name": "batch_size_mb",
      "service_name": "kyc-verifier",
      "source_id": "PR-V2-TS-003",
      "source_server": "github-mcp",
      "staging_value": 152,
      "tracking_hint": "github",
      "updated_date": "2026-03-11T11:00:00+00:00",
      "was_updated": false
    },
    {
      "cross_channel": false,
      "current_value": 23,
      "db_id": "DB-V2-TS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 8,
      "intermediate_value": 17,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TS-004",
      "owner_handle": "@v2-ts_engineer_04",
      "param_name": "sla_hours",
      "service_name": "kyc-verifier",
      "source_id": "PR-V2-TS-004",
      "source_server": "github-mcp",
      "staging_value": 20,
      "tracking_hint": "none",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 29,
      "db_id": "DB-V2-TS-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 50,
      "intermediate_value": 44,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TS-005",
      "owner_handle": "@v2-ts_engineer_05",
      "param_name": "circuit_breaker_pct",
      "service_name": "kyc-verifier",
      "source_id": "PR-V2-TS-005",
      "source_server": "github-mcp",
      "staging_value": 62,
      "tracking_hint": "none",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 92,
      "db_id": "DB-V2-TS-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 119,
      "intermediate_value": 14,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TS-006",
      "owner_handle": "@v2-ts_engineer_06",
      "param_name": "timeout_sec",
      "service_name": "settlement-engine",
      "source_id": "PR-V2-TS-006",
      "source_server": "github-mcp",
      "staging_value": 71,
      "tracking_hint": "none",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": true,
      "current_value": 8,
      "db_id": "DB-V2-TS-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 11,
      "intermediate_value": 2,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-TS-007",
      "owner_handle": "@v2-ts_engineer_07",
      "param_name": "max_retries",
      "service_name": "settlement-engine",
      "source_id": "SLACK-V2-TS-007",
      "source_server": "github-mcp",
      "staging_value": 5,
      "tracking_hint": "github",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 3011,
      "db_id": "DB-V2-TS-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 3011,
      "intermediate_value": 2675,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TS-008",
      "owner_handle": "@v2-ts_engineer_08",
      "param_name": "rate_limit_rpm",
      "service_name": "settlement-engine",
      "source_id": "PR-V2-TS-008",
      "source_server": "github-mcp",
      "staging_value": 599,
      "tracking_hint": "none",
      "updated_date": "2026-03-11T11:00:00+00:00",
      "was_updated": false
    },
    {
      "cross_channel": false,
      "current_value": 254,
      "db_id": "DB-V2-TS-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 125,
      "intermediate_value": 491,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-TS-009",
      "owner_handle": "@v2-ts_engineer_09",
      "param_name": "batch_size_mb",
      "service_name": "settlement-engine",
      "source_id": "SLACK-V2-TS-009",
      "source_server": "slack-mcp",
      "staging_value": 20,
      "tracking_hint": "slack",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    }
  ],
  "incidents": [
    {
      "data_spill_gb": 2.5,
      "environment": "prod",
      "incident_id": "INC-V2-TS-000",
      "penalty_rate_per_hour": 15.0,
      "recovery_cost_per_lb": 1.25,
      "recovery_cost_per_mib": 0.04,
      "resolved_at": "2026-10-17T02:30:00+00:00",
      "root_cause_pr": "PR-V2-TS-120",
      "service_name": "beneficiary-store",
      "started_at": "2026-10-17T01:30:00+00:00",
      "weight_kg": 24.0
    },
    {
      "data_spill_gb": 2.5,
      "environment": "prod",
      "incident_id": "INC-V2-TS-001",
      "penalty_rate_per_hour": 27.5,
      "recovery_cost_per_lb": 1.25,
      "recovery_cost_per_mib": 0.025,
      "resolved_at": "2026-10-20T06:30:00+00:00",
      "root_cause_pr": "PR-V2-TS-093",
      "service_name": "clearing-agent",
      "started_at": "2026-10-19T11:30:00+00:00",
      "weight_kg": 8.75
    },
    {
      "data_spill_gb": 12.75,
      "environment": "prod",
      "incident_id": "INC-V2-TS-002",
      "penalty_rate_per_hour": 22.0,
      "recovery_cost_per_lb": 3.5,
      "recovery_cost_per_mib": 0.04,
      "resolved_at": "2026-10-05T20:30:00+00:00",
      "root_cause_pr": "PR-V2-TS-026",
      "service_name": "consent-vault",
      "started_at": "2026-10-05T11:30:00+00:00",
      "weight_kg": 42.5
    },
    {
      "data_spill_gb": 6.0,
      "environment": "prod",
      "incident_id": "INC-V2-TS-003",
      "penalty_rate_per_hour": 15.0,
      "recovery_cost_per_lb": 0.75,
      "recovery_cost_per_mib": 0.075,
      "resolved_at": "2026-10-04T09:00:00+00:00",
      "root_cause_pr": "PR-V2-TS-026",
      "service_name": "consent-vault",
      "started_at": "2026-10-03T19:30:00+00:00",
      "weight_kg": 110.0
    },
    {
      "data_spill_gb": 6.0,
      "environment": "prod",
      "incident_id": "INC-V2-TS-004",
      "penalty_rate_per_hour": 12.5,
      "recovery_cost_per_lb": 3.5,
      "recovery_cost_per_mib": 0.075,
      "resolved_at": "2026-10-14T17:30:00+00:00",
      "root_cause_pr": "PR-V2-TS-036",
      "service_name": "mandate-engine",
      "started_at": "2026-10-14T17:00:00+00:00",
      "weight_kg": 110.0
    },
    {
      "data_spill_gb": 0.5,
      "environment": "prod",
      "incident_id": "INC-V2-TS-005",
      "penalty_rate_per_hour": 15.0,
      "recovery_cost_per_lb": 1.25,
      "recovery_cost_per_mib": 0.025,
      "resolved_at": "2026-10-01T07:00:00+00:00",
      "root_cause_pr": "PR-V2-TS-012",
      "service_name": "fraud-sentinel",
      "started_at": "2026-10-01T04:30:00+00:00",
      "weight_kg": 65.0
    },
    {
      "data_spill_gb": 0.125,
      "environment": "prod",
      "incident_id": "INC-V2-TS-006",
      "penalty_rate_per_hour": 18.75,
      "recovery_cost_per_lb": 1.25,
      "recovery_cost_per_mib": 0.075,
      "resolved_at": "2026-10-11T15:30:00+00:00",
      "root_cause_pr": "PR-V2-TS-012",
      "service_name": "fraud-sentinel",
      "started_at": "2026-10-11T11:30:00+00:00",
      "weight_kg": 110.0
    },
    {
      "data_spill_gb": 0.5,
      "environment": "prod",
      "incident_id": "INC-V2-TS-007",
      "penalty_rate_per_hour": 22.0,
      "recovery_cost_per_lb": 2.0,
      "recovery_cost_per_mib": 0.04,
      "resolved_at": "2026-10-18T13:00:00+00:00",
      "root_cause_pr": "PR-V2-TS-148",
      "service_name": "ledger-exporter",
      "started_at": "2026-10-18T11:30:00+00:00",
      "weight_kg": 42.5
    },
    {
      "data_spill_gb": 6.0,
      "environment": "prod",
      "incident_id": "INC-V2-TS-008",
      "penalty_rate_per_hour": 35.0,
      "recovery_cost_per_lb": 3.5,
      "recovery_cost_per_mib": 0.025,
      "resolved_at": "2026-10-04T13:30:00+00:00",
      "root_cause_pr": "PR-V2-TS-126",
      "service_name": "transfer-worker",
      "started_at": "2026-10-04T04:30:00+00:00",
      "weight_kg": 42.5
    },
    {
      "data_spill_gb": 6.0,
      "environment": "prod",
      "incident_id": "INC-V2-TS-009",
      "penalty_rate_per_hour": 12.5,
      "recovery_cost_per_lb": 2.0,
      "recovery_cost_per_mib": 0.075,
      "resolved_at": "2026-10-01T20:30:00+00:00",
      "root_cause_pr": "PR-V2-TS-000",
      "service_name": "kyc-verifier",
      "started_at": "2026-10-01T01:30:00+00:00",
      "weight_kg": 42.5
    }
  ],
  "schema_version": 2,
  "search_records": {
    "github-mcp": [
      {
        "environment": "prod",
        "merged_at": "2026-09-17T14:00:00+00:00",
        "param_name": "timeout_sec",
        "pr_id": "PR-V2-TS-000",
        "service_name": "kyc-verifier",
        "summary": "kyc-verifier [PROD] timeout_sec = 77. Production deployment verified.",
        "title": "kyc-verifier [PROD] timeout_sec"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "timeout_sec",
        "pr_id": "PR-V2-TS-000-STG",
        "service_name": "kyc-verifier",
        "summary": "kyc-verifier [STAGING-ONLY] timeout_sec = 119. Staging test; this is not a production setting.",
        "title": "kyc-verifier [STAGING-ONLY] timeout_sec"
      },
      {
        "environment": "prod",
        "merged_at": "2026-03-11T11:00:00+00:00",
        "param_name": "max_retries",
        "pr_id": "PR-V2-TS-001",
        "service_name": "kyc-verifier",
        "summary": "kyc-verifier [PROD] max_retries = 2. Production deployment verified.",
        "title": "kyc-verifier [PROD] max_retries"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "max_retries",
        "pr_id": "PR-V2-TS-001-STG",
        "service_name": "kyc-verifier",
        "summary": "kyc-verifier [STAGING-ONLY] max_retries = 11. Staging test; this is not a production setting.",
        "title": "kyc-verifier [STAGING-ONLY] max_retries"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "rate_limit_rpm",
        "pr_id": "PR-V2-TS-002-STG",
        "service_name": "kyc-verifier",
        "summary": "kyc-verifier [STAGING-ONLY] rate_limit_rpm = 3716. Staging test; this is not a production setting.",
        "title": "kyc-verifier [STAGING-ONLY] rate_limit_rpm"
      },
      {
        "environment": "prod",
        "merged_at": "2026-03-11T11:00:00+00:00",
        "param_name": "batch_size_mb",
        "pr_id": "PR-V2-TS-003",
        "service_name": "kyc-verifier",
        "summary": "kyc-verifier [PROD] batch_size_mb = 179. Production deployment verified.",
        "title": "kyc-verifier [PROD] batch_size_mb"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "batch_size_mb",
        "pr_id": "PR-V2-TS-003-STG",
        "service_name": "kyc-verifier",
        "summary": "kyc-verifier [STAGING-ONLY] batch_size_mb = 152. Staging test; this is not a production setting.",
        "title": "kyc-verifier [STAGING-ONLY] batch_size_mb"
      },
      {
        "environment": "prod",
        "merged_at": "2026-09-17T14:00:00+00:00",
        "param_name": "sla_hours",
        "pr_id": "PR-V2-TS-004",
        "service_name": "kyc-verifier",
        "summary": "kyc-verifier [PROD] sla_hours = 23. Production deployment verified.",
        "title": "kyc-verifier [PROD] sla_hours"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "sla_hours",
        "pr_id": "PR-V2-TS-004-STG",
        "service_name": "kyc-verifier",
        "summary": "kyc-verifier [STAGING-ONLY] sla_hours = 20. Staging test; this is not a production setting.",
        "title": "kyc-verifier [STAGING-ONLY] sla_hours"
      },
      {
        "environment": "prod",
        "merged_at": "2026-09-17T14:00:00+00:00",
        "param_name": "circuit_breaker_pct",
        "pr_id": "PR-V2-TS-005",
        "service_name": "kyc-verifier",
        "summary": "kyc-verifier [PROD] circuit_breaker_pct = 29. Production deployment verified.",
        "title": "kyc-verifier [PROD] circuit_breaker_pct"
      }
    ],
    "notion-mcp": [
      {
        "environment": "prod",
        "page_id": "NOTION-V2-TS-000",
        "param_name": "timeout_sec",
        "service_name": "kyc-verifier",
        "snippet": "kyc-verifier [PROD] timeout_sec = 80. Production runbook at publication. Tracked via GitHub PRs.",
        "title": "kyc-verifier [PROD] timeout_sec",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-TS-000-STG",
        "param_name": "timeout_sec",
        "service_name": "kyc-verifier",
        "snippet": "kyc-verifier [STAGING-ONLY] timeout_sec = 119. Staging-only trial; do not apply this setting to production.",
        "title": "kyc-verifier [STAGING-ONLY] timeout_sec",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-TS-001",
        "param_name": "max_retries",
        "service_name": "kyc-verifier",
        "snippet": "kyc-verifier [PROD] max_retries = 2. Production runbook at publication. Tracked via GitHub PRs.",
        "title": "kyc-verifier [PROD] max_retries",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-TS-001-STG",
        "param_name": "max_retries",
        "service_name": "kyc-verifier",
        "snippet": "kyc-verifier [STAGING-ONLY] max_retries = 11. Staging-only trial; do not apply this setting to production.",
        "title": "kyc-verifier [STAGING-ONLY] max_retries",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-TS-002",
        "param_name": "rate_limit_rpm",
        "service_name": "kyc-verifier",
        "snippet": "kyc-verifier [PROD] rate_limit_rpm = 2690. Production runbook at publication. Tracked via Slack #deployments.",
        "title": "kyc-verifier [PROD] rate_limit_rpm",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-TS-002-STG",
        "param_name": "rate_limit_rpm",
        "service_name": "kyc-verifier",
        "snippet": "kyc-verifier [STAGING-ONLY] rate_limit_rpm = 3716. Staging-only trial; do not apply this setting to production.",
        "title": "kyc-verifier [STAGING-ONLY] rate_limit_rpm",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-TS-003",
        "param_name": "batch_size_mb",
        "service_name": "kyc-verifier",
        "snippet": "kyc-verifier [PROD] batch_size_mb = 179. Production runbook at publication. Tracked via GitHub PRs.",
        "title": "kyc-verifier [PROD] batch_size_mb",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-TS-003-STG",
        "param_name": "batch_size_mb",
        "service_name": "kyc-verifier",
        "snippet": "kyc-verifier [STAGING-ONLY] batch_size_mb = 152. Staging-only trial; do not apply this setting to production.",
        "title": "kyc-verifier [STAGING-ONLY] batch_size_mb",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-TS-004",
        "param_name": "sla_hours",
        "service_name": "kyc-verifier",
        "snippet": "kyc-verifier [PROD] sla_hours = 8. Production runbook at publication.",
        "title": "kyc-verifier [PROD] sla_hours",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-TS-004-STG",
        "param_name": "sla_hours",
        "service_name": "kyc-verifier",
        "snippet": "kyc-verifier [STAGING-ONLY] sla_hours = 20. Staging-only trial; do not apply this setting to production.",
        "title": "kyc-verifier [STAGING-ONLY] sla_hours",
        "updated_at": "2026-10-25T18:30:00+00:00"
      }
    ],
    "slack-mcp": [
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TS-000-STG",
        "param_name": "timeout_sec",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "kyc-verifier",
        "text": "kyc-verifier [STAGING-ONLY] timeout_sec = 119. Staging test; this is not a production setting.",
        "title": "kyc-verifier [STAGING-ONLY] timeout_sec"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TS-001-STG",
        "param_name": "max_retries",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "kyc-verifier",
        "text": "kyc-verifier [STAGING-ONLY] max_retries = 11. Staging test; this is not a production setting.",
        "title": "kyc-verifier [STAGING-ONLY] max_retries"
      },
      {
        "channel": "#deployments",
        "environment": "prod",
        "msg_id": "SLACK-V2-TS-002",
        "param_name": "rate_limit_rpm",
        "posted_at": "2026-03-11T11:00:00+00:00",
        "service_name": "kyc-verifier",
        "text": "kyc-verifier [PROD] rate_limit_rpm = 2690. Production deployment verified.",
        "title": "kyc-verifier [PROD] rate_limit_rpm"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TS-002-STG",
        "param_name": "rate_limit_rpm",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "kyc-verifier",
        "text": "kyc-verifier [STAGING-ONLY] rate_limit_rpm = 3716. Staging test; this is not a production setting.",
        "title": "kyc-verifier [STAGING-ONLY] rate_limit_rpm"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TS-003-STG",
        "param_name": "batch_size_mb",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "kyc-verifier",
        "text": "kyc-verifier [STAGING-ONLY] batch_size_mb = 152. Staging test; this is not a production setting.",
        "title": "kyc-verifier [STAGING-ONLY] batch_size_mb"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TS-004-STG",
        "param_name": "sla_hours",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "kyc-verifier",
        "text": "kyc-verifier [STAGING-ONLY] sla_hours = 20. Staging test; this is not a production setting.",
        "title": "kyc-verifier [STAGING-ONLY] sla_hours"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TS-005-STG",
        "param_name": "circuit_breaker_pct",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "kyc-verifier",
        "text": "kyc-verifier [STAGING-ONLY] circuit_breaker_pct = 62. Staging test; this is not a production setting.",
        "title": "kyc-verifier [STAGING-ONLY] circuit_breaker_pct"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TS-006-STG",
        "param_name": "timeout_sec",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "settlement-engine",
        "text": "settlement-engine [STAGING-ONLY] timeout_sec = 71. Staging test; this is not a production setting.",
        "title": "settlement-engine [STAGING-ONLY] timeout_sec"
      },
      {
        "channel": "#deployments",
        "environment": "prod",
        "msg_id": "SLACK-V2-TS-007",
        "param_name": "max_retries",
        "posted_at": "2026-09-17T14:00:00+00:00",
        "service_name": "settlement-engine",
        "text": "settlement-engine [PROD] max_retries = 8. Production deployment verified.",
        "title": "settlement-engine [PROD] max_retries"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TS-007-STG",
        "param_name": "max_retries",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "settlement-engine",
        "text": "settlement-engine [STAGING-ONLY] max_retries = 5. Staging test; this is not a production setting.",
        "title": "settlement-engine [STAGING-ONLY] max_retries"
      }
    ]
  },
  "seed": 99,
  "services": [
    "kyc-verifier",
    "settlement-engine",
    "fraud-sentinel",
    "invoice-mailer",
    "consent-vault",
    "payout-router",
    "mandate-engine",
    "statement-worker",
    "receipt-store",
    "reconciliation-api"
  ],
  "split": "test_synth",
  "world_id": "484d0bc8ff30426a39f7f1727d62da7a43447089010144b5b5a86ceab0ab2b69"
}
```

---

# File: `world_train.json`

Source SHA-256: `664c892b8cf7971a8da92a6f2e5f1e6e1ece0103e73479af4e20c427a4cf68cb`

```json
{
  "case_pools": {
    "train_grpo1": [
      {
        "case_id": "train_grpo1-0000",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "sla_hours",
        "pool": "train_grpo1",
        "request_mode": "audit",
        "service_name": "metrics-agent"
      },
      {
        "case_id": "train_grpo1-0001",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_grpo1",
        "request_mode": "audit",
        "service_name": "fee-engine"
      },
      {
        "case_id": "train_grpo1-0002",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "timeout_sec",
        "pool": "train_grpo1",
        "request_mode": "audit",
        "service_name": "mandate-store"
      },
      {
        "case_id": "train_grpo1-0003",
        "incident_id": "INC-V2-TR-015",
        "incident_subtype": "payload_mib",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "recovery_cost_mib_usd",
        "pool": "train_grpo1",
        "request_mode": "audit",
        "service_name": "export-worker"
      },
      {
        "case_id": "train_grpo1-0004",
        "incident_id": "INC-V2-TR-016",
        "incident_subtype": "sla_penalty",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "sla_penalty_usd",
        "pool": "train_grpo1",
        "request_mode": "audit",
        "service_name": "loyalty-api"
      },
      {
        "case_id": "train_grpo1-0005",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "sla_hours",
        "pool": "train_grpo1",
        "request_mode": "audit",
        "service_name": "media-worker"
      },
      {
        "case_id": "train_grpo1-0006",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "circuit_breaker_pct",
        "pool": "train_grpo1",
        "request_mode": "audit",
        "service_name": "ledger-writer"
      },
      {
        "case_id": "train_grpo1-0007",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "rate_limit_rpm",
        "pool": "train_grpo1",
        "request_mode": "audit",
        "service_name": "signing-gateway"
      },
      {
        "case_id": "train_grpo1-0008",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_grpo1",
        "request_mode": "audit",
        "service_name": "event-router"
      },
      {
        "case_id": "train_grpo1-0009",
        "incident_id": "INC-V2-TR-017",
        "incident_subtype": "config_audit",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "max_retries",
        "pool": "train_grpo1",
        "request_mode": "audit",
        "service_name": "product-catalog"
      }
    ],
    "train_grpo2": [
      {
        "case_id": "train_grpo2-0000",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_grpo2",
        "request_mode": "audit",
        "service_name": "refund-worker"
      },
      {
        "case_id": "train_grpo2-0001",
        "incident_id": "INC-V2-TR-040",
        "incident_subtype": "sla_penalty",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "sla_penalty_usd",
        "pool": "train_grpo2",
        "request_mode": "audit",
        "service_name": "export-worker"
      },
      {
        "case_id": "train_grpo2-0002",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": true,
        "param_name": "circuit_breaker_pct",
        "pool": "train_grpo2",
        "request_mode": "database_only",
        "service_name": "swift-hedger"
      },
      {
        "case_id": "train_grpo2-0003",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "sla_hours",
        "pool": "train_grpo2",
        "request_mode": "audit",
        "service_name": "customer-vault"
      },
      {
        "case_id": "train_grpo2-0004",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "max_retries",
        "pool": "train_grpo2",
        "request_mode": "audit",
        "service_name": "analytics-sink"
      },
      {
        "case_id": "train_grpo2-0005",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_grpo2",
        "request_mode": "audit",
        "service_name": "ledger-writer"
      },
      {
        "case_id": "train_grpo2-0006",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_grpo2",
        "request_mode": "audit",
        "service_name": "metrics-agent"
      },
      {
        "case_id": "train_grpo2-0007",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_grpo2",
        "request_mode": "audit",
        "service_name": "search-indexer"
      },
      {
        "case_id": "train_grpo2-0008",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": false,
        "param_name": "rate_limit_rpm",
        "pool": "train_grpo2",
        "request_mode": "database_only",
        "service_name": "email-relay"
      },
      {
        "case_id": "train_grpo2-0009",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": true,
        "param_name": "timeout_sec",
        "pool": "train_grpo2",
        "request_mode": "database_only",
        "service_name": "swift-gate"
      }
    ],
    "train_reserved": [
      {
        "case_id": "train_reserved-0000",
        "incident_id": "INC-V2-TR-075",
        "incident_subtype": "payload_mib",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "recovery_cost_mib_usd",
        "pool": "train_reserved",
        "request_mode": "audit",
        "service_name": "profile-store"
      },
      {
        "case_id": "train_reserved-0001",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": false,
        "param_name": "timeout_sec",
        "pool": "train_reserved",
        "request_mode": "database_only",
        "service_name": "profile-store"
      },
      {
        "case_id": "train_reserved-0002",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "timeout_sec",
        "pool": "train_reserved",
        "request_mode": "audit",
        "service_name": "metrics-agent"
      },
      {
        "case_id": "train_reserved-0003",
        "incident_id": "INC-V2-TR-076",
        "incident_subtype": "sla_penalty",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "sla_penalty_usd",
        "pool": "train_reserved",
        "request_mode": "audit",
        "service_name": "media-worker"
      },
      {
        "case_id": "train_reserved-0004",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "max_retries",
        "pool": "train_reserved",
        "request_mode": "audit",
        "service_name": "shipment-router"
      },
      {
        "case_id": "train_reserved-0005",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "timeout_sec",
        "pool": "train_reserved",
        "request_mode": "audit",
        "service_name": "fx-router"
      },
      {
        "case_id": "train_reserved-0006",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "max_retries",
        "pool": "train_reserved",
        "request_mode": "audit",
        "service_name": "audit-stream"
      },
      {
        "case_id": "train_reserved-0007",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "circuit_breaker_pct",
        "pool": "train_reserved",
        "request_mode": "audit",
        "service_name": "upi-gateway"
      },
      {
        "case_id": "train_reserved-0008",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "circuit_breaker_pct",
        "pool": "train_reserved",
        "request_mode": "audit",
        "service_name": "attachment-api"
      },
      {
        "case_id": "train_reserved-0009",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": true,
        "param_name": "max_retries",
        "pool": "train_reserved",
        "request_mode": "database_only",
        "service_name": "escrow-relay"
      }
    ],
    "train_sft": [
      {
        "case_id": "train_sft-0000",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_sft",
        "request_mode": "audit",
        "service_name": "loyalty-api"
      },
      {
        "case_id": "train_sft-0001",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "sla_hours",
        "pool": "train_sft",
        "request_mode": "audit",
        "service_name": "payment-worker"
      },
      {
        "case_id": "train_sft-0002",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_sft",
        "request_mode": "audit",
        "service_name": "email-relay"
      },
      {
        "case_id": "train_sft-0003",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "sla_hours",
        "pool": "train_sft",
        "request_mode": "audit",
        "service_name": "reconciliation-store"
      },
      {
        "case_id": "train_sft-0004",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "circuit_breaker_pct",
        "pool": "train_sft",
        "request_mode": "audit",
        "service_name": "cart-ledger"
      },
      {
        "case_id": "train_sft-0005",
        "incident_id": "INC-V2-TR-000",
        "incident_subtype": "sla_penalty",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "sla_penalty_usd",
        "pool": "train_sft",
        "request_mode": "audit",
        "service_name": "token-service"
      },
      {
        "case_id": "train_sft-0006",
        "incident_id": "INC-V2-TR-001",
        "incident_subtype": "config_audit",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "timeout_sec",
        "pool": "train_sft",
        "request_mode": "audit",
        "service_name": "fraud-router"
      },
      {
        "case_id": "train_sft-0007",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "timeout_sec",
        "pool": "train_sft",
        "request_mode": "audit",
        "service_name": "vendor-router"
      },
      {
        "case_id": "train_sft-0008",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": true,
        "param_name": "rate_limit_rpm",
        "pool": "train_sft",
        "request_mode": "database_only",
        "service_name": "forex-hedger"
      },
      {
        "case_id": "train_sft-0009",
        "incident_id": "INC-V2-TR-002",
        "incident_subtype": "payload_lb",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "recovery_cost_lb_usd",
        "pool": "train_sft",
        "request_mode": "audit",
        "service_name": "debit-processor"
      }
    ],
    "train_val": [
      {
        "case_id": "train_val-0000",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "circuit_breaker_pct",
        "pool": "train_val",
        "request_mode": "audit",
        "service_name": "webhook-dispatcher"
      },
      {
        "case_id": "train_val-0001",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": true,
        "param_name": "batch_size_mb",
        "pool": "train_val",
        "request_mode": "database_only",
        "service_name": "escrow-vault"
      },
      {
        "case_id": "train_val-0002",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_val",
        "request_mode": "audit",
        "service_name": "invoice-store"
      },
      {
        "case_id": "train_val-0003",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_val",
        "request_mode": "audit",
        "service_name": "export-worker"
      },
      {
        "case_id": "train_val-0004",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "conflict",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_val",
        "request_mode": "audit",
        "service_name": "dispute-api"
      },
      {
        "case_id": "train_val-0005",
        "incident_id": "INC-V2-TR-070",
        "incident_subtype": "payload_lb",
        "kind": "incident",
        "missing_entity": false,
        "param_name": "recovery_cost_lb_usd",
        "pool": "train_val",
        "request_mode": "audit",
        "service_name": "product-catalog"
      },
      {
        "case_id": "train_val-0006",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": false,
        "param_name": "timeout_sec",
        "pool": "train_val",
        "request_mode": "database_only",
        "service_name": "ledger-writer"
      },
      {
        "case_id": "train_val-0007",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": true,
        "param_name": "batch_size_mb",
        "pool": "train_val",
        "request_mode": "database_only",
        "service_name": "escrow-dispatcher"
      },
      {
        "case_id": "train_val-0008",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "consistent",
        "missing_entity": false,
        "param_name": "batch_size_mb",
        "pool": "train_val",
        "request_mode": "audit",
        "service_name": "account-vault"
      },
      {
        "case_id": "train_val-0009",
        "incident_id": null,
        "incident_subtype": null,
        "kind": "abstain",
        "missing_entity": false,
        "param_name": "sla_hours",
        "pool": "train_val",
        "request_mode": "database_only",
        "service_name": "settlement-worker"
      }
    ]
  },
  "employees": [
    "@v2-tr_engineer_00",
    "@v2-tr_engineer_01",
    "@v2-tr_engineer_02",
    "@v2-tr_engineer_03",
    "@v2-tr_engineer_04",
    "@v2-tr_engineer_05",
    "@v2-tr_engineer_06",
    "@v2-tr_engineer_07",
    "@v2-tr_engineer_08",
    "@v2-tr_engineer_09"
  ],
  "facts": [
    {
      "cross_channel": false,
      "current_value": 28,
      "db_id": "DB-V2-TR-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 127,
      "intermediate_value": 10,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TR-000",
      "owner_handle": "@v2-tr_engineer_00",
      "param_name": "timeout_sec",
      "service_name": "upi-gateway",
      "source_id": "PR-V2-TR-000",
      "source_server": "github-mcp",
      "staging_value": 148,
      "tracking_hint": "github",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 7,
      "db_id": "DB-V2-TR-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 1,
      "intermediate_value": 10,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TR-001",
      "owner_handle": "@v2-tr_engineer_01",
      "param_name": "max_retries",
      "service_name": "upi-gateway",
      "source_id": "PR-V2-TR-001",
      "source_server": "github-mcp",
      "staging_value": 4,
      "tracking_hint": "github",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 3202,
      "db_id": "DB-V2-TR-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 1528,
      "intermediate_value": 3796,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-TR-002",
      "owner_handle": "@v2-tr_engineer_02",
      "param_name": "rate_limit_rpm",
      "service_name": "upi-gateway",
      "source_id": "SLACK-V2-TR-002",
      "source_server": "slack-mcp",
      "staging_value": 262,
      "tracking_hint": "none",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 16,
      "db_id": "DB-V2-TR-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 184,
      "intermediate_value": 466,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TR-003",
      "owner_handle": "@v2-tr_engineer_03",
      "param_name": "batch_size_mb",
      "service_name": "upi-gateway",
      "source_id": "PR-V2-TR-003",
      "source_server": "github-mcp",
      "staging_value": 229,
      "tracking_hint": "github",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 16,
      "db_id": "DB-V2-TR-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 40,
      "intermediate_value": 13,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TR-004",
      "owner_handle": "@v2-tr_engineer_04",
      "param_name": "sla_hours",
      "service_name": "upi-gateway",
      "source_id": "PR-V2-TR-004",
      "source_server": "github-mcp",
      "staging_value": 7,
      "tracking_hint": "github",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 10,
      "db_id": "DB-V2-TR-000",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 16,
      "intermediate_value": 19,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-TR-005",
      "owner_handle": "@v2-tr_engineer_05",
      "param_name": "circuit_breaker_pct",
      "service_name": "upi-gateway",
      "source_id": "SLACK-V2-TR-005",
      "source_server": "slack-mcp",
      "staging_value": 43,
      "tracking_hint": "none",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 13,
      "db_id": "DB-V2-TR-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 160,
      "intermediate_value": 145,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TR-006",
      "owner_handle": "@v2-tr_engineer_06",
      "param_name": "timeout_sec",
      "service_name": "auth-proxy",
      "source_id": "PR-V2-TR-006",
      "source_server": "github-mcp",
      "staging_value": 94,
      "tracking_hint": "github",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    },
    {
      "cross_channel": false,
      "current_value": 7,
      "db_id": "DB-V2-TR-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 7,
      "intermediate_value": 4,
      "latest_source_server": "github-mcp",
      "notion_page_id": "NOTION-V2-TR-007",
      "owner_handle": "@v2-tr_engineer_07",
      "param_name": "max_retries",
      "service_name": "auth-proxy",
      "source_id": "PR-V2-TR-007",
      "source_server": "github-mcp",
      "staging_value": 1,
      "tracking_hint": "github",
      "updated_date": "2026-03-11T11:00:00+00:00",
      "was_updated": false
    },
    {
      "cross_channel": false,
      "current_value": 4849,
      "db_id": "DB-V2-TR-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 4849,
      "intermediate_value": 589,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-TR-008",
      "owner_handle": "@v2-tr_engineer_08",
      "param_name": "rate_limit_rpm",
      "service_name": "auth-proxy",
      "source_id": "SLACK-V2-TR-008",
      "source_server": "slack-mcp",
      "staging_value": 1528,
      "tracking_hint": "slack",
      "updated_date": "2026-03-11T11:00:00+00:00",
      "was_updated": false
    },
    {
      "cross_channel": false,
      "current_value": 502,
      "db_id": "DB-V2-TR-001",
      "initial_date": "2026-02-05T09:30:00+00:00",
      "initial_value": 364,
      "intermediate_value": 295,
      "latest_source_server": "slack-mcp",
      "notion_page_id": "NOTION-V2-TR-009",
      "owner_handle": "@v2-tr_engineer_09",
      "param_name": "batch_size_mb",
      "service_name": "auth-proxy",
      "source_id": "SLACK-V2-TR-009",
      "source_server": "slack-mcp",
      "staging_value": 139,
      "tracking_hint": "slack",
      "updated_date": "2026-09-17T14:00:00+00:00",
      "was_updated": true
    }
  ],
  "incidents": [
    {
      "data_spill_gb": 0.5,
      "environment": "prod",
      "incident_id": "INC-V2-TR-000",
      "penalty_rate_per_hour": 12.5,
      "recovery_cost_per_lb": 2.0,
      "recovery_cost_per_mib": 0.075,
      "resolved_at": "2026-10-09T09:30:00+00:00",
      "root_cause_pr": "PR-V2-TR-259",
      "service_name": "token-service",
      "started_at": "2026-10-09T08:30:00+00:00",
      "weight_kg": 12.5
    },
    {
      "data_spill_gb": 6.0,
      "environment": "prod",
      "incident_id": "INC-V2-TR-001",
      "penalty_rate_per_hour": 15.0,
      "recovery_cost_per_lb": 2.0,
      "recovery_cost_per_mib": 0.04,
      "resolved_at": "2026-10-06T21:00:00+00:00",
      "root_cause_pr": "PR-V2-TR-233",
      "service_name": "fraud-router",
      "started_at": "2026-10-06T19:30:00+00:00",
      "weight_kg": 1.25
    },
    {
      "data_spill_gb": 1.25,
      "environment": "prod",
      "incident_id": "INC-V2-TR-002",
      "penalty_rate_per_hour": 27.5,
      "recovery_cost_per_lb": 2.0,
      "recovery_cost_per_mib": 0.0125,
      "resolved_at": "2026-10-20T18:30:00+00:00",
      "root_cause_pr": "PR-V2-TR-175",
      "service_name": "debit-processor",
      "started_at": "2026-10-20T17:00:00+00:00",
      "weight_kg": 24.0
    },
    {
      "data_spill_gb": 12.75,
      "environment": "prod",
      "incident_id": "INC-V2-TR-003",
      "penalty_rate_per_hour": 27.5,
      "recovery_cost_per_lb": 1.25,
      "recovery_cost_per_mib": 0.025,
      "resolved_at": "2026-10-05T12:00:00+00:00",
      "root_cause_pr": "PR-V2-TR-000",
      "service_name": "upi-gateway",
      "started_at": "2026-10-05T11:30:00+00:00",
      "weight_kg": 8.75
    },
    {
      "data_spill_gb": 2.5,
      "environment": "prod",
      "incident_id": "INC-V2-TR-004",
      "penalty_rate_per_hour": 27.5,
      "recovery_cost_per_lb": 1.25,
      "recovery_cost_per_mib": 0.04,
      "resolved_at": "2026-10-06T03:30:00+00:00",
      "root_cause_pr": "PR-V2-TR-145",
      "service_name": "identity-broker",
      "started_at": "2026-10-05T23:30:00+00:00",
      "weight_kg": 65.0
    },
    {
      "data_spill_gb": 2.5,
      "environment": "prod",
      "incident_id": "INC-V2-TR-005",
      "penalty_rate_per_hour": 27.5,
      "recovery_cost_per_lb": 2.0,
      "recovery_cost_per_mib": 0.04,
      "resolved_at": "2026-10-14T20:30:00+00:00",
      "root_cause_pr": "PR-V2-TR-111",
      "service_name": "shipment-router",
      "started_at": "2026-10-14T11:30:00+00:00",
      "weight_kg": 3.5
    },
    {
      "data_spill_gb": 12.75,
      "environment": "prod",
      "incident_id": "INC-V2-TR-006",
      "penalty_rate_per_hour": 12.5,
      "recovery_cost_per_lb": 3.5,
      "recovery_cost_per_mib": 0.04,
      "resolved_at": "2026-10-15T17:30:00+00:00",
      "root_cause_pr": "PR-V2-TR-298",
      "service_name": "attachment-api",
      "started_at": "2026-10-15T13:30:00+00:00",
      "weight_kg": 3.5
    },
    {
      "data_spill_gb": 2.5,
      "environment": "prod",
      "incident_id": "INC-V2-TR-007",
      "penalty_rate_per_hour": 35.0,
      "recovery_cost_per_lb": 2.0,
      "recovery_cost_per_mib": 0.04,
      "resolved_at": "2026-10-03T23:30:00+00:00",
      "root_cause_pr": "PR-V2-TR-274",
      "service_name": "ledger-writer",
      "started_at": "2026-10-03T17:00:00+00:00",
      "weight_kg": 12.5
    },
    {
      "data_spill_gb": 1.25,
      "environment": "prod",
      "incident_id": "INC-V2-TR-008",
      "penalty_rate_per_hour": 15.0,
      "recovery_cost_per_lb": 0.75,
      "recovery_cost_per_mib": 0.0125,
      "resolved_at": "2026-10-10T22:00:00+00:00",
      "root_cause_pr": "PR-V2-TR-060",
      "service_name": "session-cache",
      "started_at": "2026-10-10T08:30:00+00:00",
      "weight_kg": 110.0
    },
    {
      "data_spill_gb": 2.5,
      "environment": "prod",
      "incident_id": "INC-V2-TR-009",
      "penalty_rate_per_hour": 12.5,
      "recovery_cost_per_lb": 3.5,
      "recovery_cost_per_mib": 0.0125,
      "resolved_at": "2026-10-05T06:30:00+00:00",
      "root_cause_pr": "PR-V2-TR-142",
      "service_name": "refund-worker",
      "started_at": "2026-10-04T21:30:00+00:00",
      "weight_kg": 8.75
    }
  ],
  "schema_version": 2,
  "search_records": {
    "github-mcp": [
      {
        "environment": "prod",
        "merged_at": "2026-09-17T14:00:00+00:00",
        "param_name": "timeout_sec",
        "pr_id": "PR-V2-TR-000",
        "service_name": "upi-gateway",
        "summary": "upi-gateway [PROD] timeout_sec = 28. Production deployment verified.",
        "title": "upi-gateway [PROD] timeout_sec"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "timeout_sec",
        "pr_id": "PR-V2-TR-000-STG",
        "service_name": "upi-gateway",
        "summary": "upi-gateway [STAGING-ONLY] timeout_sec = 148. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] timeout_sec"
      },
      {
        "environment": "prod",
        "merged_at": "2026-09-17T14:00:00+00:00",
        "param_name": "max_retries",
        "pr_id": "PR-V2-TR-001",
        "service_name": "upi-gateway",
        "summary": "upi-gateway [PROD] max_retries = 7. Production deployment verified.",
        "title": "upi-gateway [PROD] max_retries"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "max_retries",
        "pr_id": "PR-V2-TR-001-STG",
        "service_name": "upi-gateway",
        "summary": "upi-gateway [STAGING-ONLY] max_retries = 4. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] max_retries"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "rate_limit_rpm",
        "pr_id": "PR-V2-TR-002-STG",
        "service_name": "upi-gateway",
        "summary": "upi-gateway [STAGING-ONLY] rate_limit_rpm = 262. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] rate_limit_rpm"
      },
      {
        "environment": "prod",
        "merged_at": "2026-09-17T14:00:00+00:00",
        "param_name": "batch_size_mb",
        "pr_id": "PR-V2-TR-003",
        "service_name": "upi-gateway",
        "summary": "upi-gateway [PROD] batch_size_mb = 16. Production deployment verified.",
        "title": "upi-gateway [PROD] batch_size_mb"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "batch_size_mb",
        "pr_id": "PR-V2-TR-003-STG",
        "service_name": "upi-gateway",
        "summary": "upi-gateway [STAGING-ONLY] batch_size_mb = 229. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] batch_size_mb"
      },
      {
        "environment": "prod",
        "merged_at": "2026-09-17T14:00:00+00:00",
        "param_name": "sla_hours",
        "pr_id": "PR-V2-TR-004",
        "service_name": "upi-gateway",
        "summary": "upi-gateway [PROD] sla_hours = 16. Production deployment verified.",
        "title": "upi-gateway [PROD] sla_hours"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "sla_hours",
        "pr_id": "PR-V2-TR-004-STG",
        "service_name": "upi-gateway",
        "summary": "upi-gateway [STAGING-ONLY] sla_hours = 7. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] sla_hours"
      },
      {
        "environment": "staging",
        "merged_at": "2026-10-26T19:00:00+00:00",
        "param_name": "circuit_breaker_pct",
        "pr_id": "PR-V2-TR-005-STG",
        "service_name": "upi-gateway",
        "summary": "upi-gateway [STAGING-ONLY] circuit_breaker_pct = 43. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] circuit_breaker_pct"
      }
    ],
    "notion-mcp": [
      {
        "environment": "prod",
        "page_id": "NOTION-V2-TR-000",
        "param_name": "timeout_sec",
        "service_name": "upi-gateway",
        "snippet": "upi-gateway [PROD] timeout_sec = 127. Production runbook at publication. Tracked via GitHub PRs.",
        "title": "upi-gateway [PROD] timeout_sec",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-TR-000-STG",
        "param_name": "timeout_sec",
        "service_name": "upi-gateway",
        "snippet": "upi-gateway [STAGING-ONLY] timeout_sec = 148. Staging-only trial; do not apply this setting to production.",
        "title": "upi-gateway [STAGING-ONLY] timeout_sec",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-TR-001",
        "param_name": "max_retries",
        "service_name": "upi-gateway",
        "snippet": "upi-gateway [PROD] max_retries = 1. Production runbook at publication. Tracked via GitHub PRs.",
        "title": "upi-gateway [PROD] max_retries",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-TR-001-STG",
        "param_name": "max_retries",
        "service_name": "upi-gateway",
        "snippet": "upi-gateway [STAGING-ONLY] max_retries = 4. Staging-only trial; do not apply this setting to production.",
        "title": "upi-gateway [STAGING-ONLY] max_retries",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-TR-002",
        "param_name": "rate_limit_rpm",
        "service_name": "upi-gateway",
        "snippet": "upi-gateway [PROD] rate_limit_rpm = 1528. Production runbook at publication.",
        "title": "upi-gateway [PROD] rate_limit_rpm",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-TR-002-STG",
        "param_name": "rate_limit_rpm",
        "service_name": "upi-gateway",
        "snippet": "upi-gateway [STAGING-ONLY] rate_limit_rpm = 262. Staging-only trial; do not apply this setting to production.",
        "title": "upi-gateway [STAGING-ONLY] rate_limit_rpm",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-TR-003",
        "param_name": "batch_size_mb",
        "service_name": "upi-gateway",
        "snippet": "upi-gateway [PROD] batch_size_mb = 184. Production runbook at publication. Tracked via GitHub PRs.",
        "title": "upi-gateway [PROD] batch_size_mb",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-TR-003-STG",
        "param_name": "batch_size_mb",
        "service_name": "upi-gateway",
        "snippet": "upi-gateway [STAGING-ONLY] batch_size_mb = 229. Staging-only trial; do not apply this setting to production.",
        "title": "upi-gateway [STAGING-ONLY] batch_size_mb",
        "updated_at": "2026-10-25T18:30:00+00:00"
      },
      {
        "environment": "prod",
        "page_id": "NOTION-V2-TR-004",
        "param_name": "sla_hours",
        "service_name": "upi-gateway",
        "snippet": "upi-gateway [PROD] sla_hours = 40. Production runbook at publication. Tracked via GitHub PRs.",
        "title": "upi-gateway [PROD] sla_hours",
        "updated_at": "2026-02-05T09:30:00+00:00"
      },
      {
        "environment": "staging",
        "page_id": "NOTION-V2-TR-004-STG",
        "param_name": "sla_hours",
        "service_name": "upi-gateway",
        "snippet": "upi-gateway [STAGING-ONLY] sla_hours = 7. Staging-only trial; do not apply this setting to production.",
        "title": "upi-gateway [STAGING-ONLY] sla_hours",
        "updated_at": "2026-10-25T18:30:00+00:00"
      }
    ],
    "slack-mcp": [
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TR-000-STG",
        "param_name": "timeout_sec",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "upi-gateway",
        "text": "upi-gateway [STAGING-ONLY] timeout_sec = 148. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] timeout_sec"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TR-001-STG",
        "param_name": "max_retries",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "upi-gateway",
        "text": "upi-gateway [STAGING-ONLY] max_retries = 4. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] max_retries"
      },
      {
        "channel": "#deployments",
        "environment": "prod",
        "msg_id": "SLACK-V2-TR-002",
        "param_name": "rate_limit_rpm",
        "posted_at": "2026-09-17T14:00:00+00:00",
        "service_name": "upi-gateway",
        "text": "upi-gateway [PROD] rate_limit_rpm = 3202. Production deployment verified.",
        "title": "upi-gateway [PROD] rate_limit_rpm"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TR-002-STG",
        "param_name": "rate_limit_rpm",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "upi-gateway",
        "text": "upi-gateway [STAGING-ONLY] rate_limit_rpm = 262. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] rate_limit_rpm"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TR-003-STG",
        "param_name": "batch_size_mb",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "upi-gateway",
        "text": "upi-gateway [STAGING-ONLY] batch_size_mb = 229. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] batch_size_mb"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TR-004-STG",
        "param_name": "sla_hours",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "upi-gateway",
        "text": "upi-gateway [STAGING-ONLY] sla_hours = 7. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] sla_hours"
      },
      {
        "channel": "#deployments",
        "environment": "prod",
        "msg_id": "SLACK-V2-TR-005",
        "param_name": "circuit_breaker_pct",
        "posted_at": "2026-09-17T14:00:00+00:00",
        "service_name": "upi-gateway",
        "text": "upi-gateway [PROD] circuit_breaker_pct = 10. Production deployment verified.",
        "title": "upi-gateway [PROD] circuit_breaker_pct"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TR-005-STG",
        "param_name": "circuit_breaker_pct",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "upi-gateway",
        "text": "upi-gateway [STAGING-ONLY] circuit_breaker_pct = 43. Staging test; this is not a production setting.",
        "title": "upi-gateway [STAGING-ONLY] circuit_breaker_pct"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TR-006-STG",
        "param_name": "timeout_sec",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "auth-proxy",
        "text": "auth-proxy [STAGING-ONLY] timeout_sec = 94. Staging test; this is not a production setting.",
        "title": "auth-proxy [STAGING-ONLY] timeout_sec"
      },
      {
        "channel": "#staging",
        "environment": "staging",
        "msg_id": "SLACK-V2-TR-007-STG",
        "param_name": "max_retries",
        "posted_at": "2026-10-26T19:00:00+00:00",
        "service_name": "auth-proxy",
        "text": "auth-proxy [STAGING-ONLY] max_retries = 1. Staging test; this is not a production setting.",
        "title": "auth-proxy [STAGING-ONLY] max_retries"
      }
    ]
  },
  "seed": 42,
  "services": [
    "upi-gateway",
    "auth-proxy",
    "cart-ledger",
    "webhook-dispatcher",
    "order-router",
    "payment-worker",
    "search-indexer",
    "profile-store",
    "email-relay",
    "inventory-sync"
  ],
  "split": "train",
  "world_id": "25301a36d04c0159439ca0268527731335cc8ee75cbeb85ac08651d7c76f0ad9"
}
```

## Review gate and known limitations

No claim is made that these issues caused the exact prior 85.25% result, or that v2 SFT must score below 85%. Difficulty/headroom must be measured without tuning the holdout to force a target score. Oracle tools and labels have been checked; natural-language realism and native-script quality still need human review.

Reference-path lengths are measured, not claimed to be a global minimum over every possible SQL strategy. The database remains read-only but can perform arithmetic expressions; therefore utility use in the oracle is not proof that every correct policy must call that utility. Required-chain compliance should be reported separately or explicitly enforced by a reviewed reward rule before training.

V1 training/evaluation entry points still default to `data/`. Do not accidentally train the reviewed v2 files with legacy counts, split logic, 1,536-token limits or v1 evaluation names. A bounded active-advantage sampler and v2 backend hook are implemented and CPU-tested: skipped groups are logged, accepted updates rotate evenly across all four task kinds, and exhaustion raises rather than inventing an optimizer update. V2 CLI training bindings, token budgets and GPU integration still require a fresh smoke test after data approval. Dynamic filtering must bound retries and report selection bias; it cannot create reward variation when a kind is already solved by every sample.

All original v1 files are preserved. The v2 freeze is `data_v2/SHA256SUMS`; it intentionally does not replace `data/SHA256SUMS`.

# File: `token_length_audit.json`

```json
{
  "model": "CohereLabs/tiny-aya-fire",
  "tokenizer_source": "local cached tokenizer; no model inference",
  "rows": 240,
  "min_tokens": 979,
  "max_tokens": 2359,
  "mean_tokens": 1646.4541666666667,
  "above_legacy_1536": 136,
  "recommended_untruncated_budget": 2560
}
```

Tokenizer-only measurement; no model was trained or benchmarked.

## Native-script and romanized conflict spot checks

- `train_sft-0000-hi` (native): loyalty-api का वर्तमान production batch_size_mb क्या है? दस्तावेज़ और deployment records की तुलना करें और पुराने पन्ने को पहचानें।
- `train_sft-0023-hi` (latin): audit-stream ka production circuit_breaker_pct nirdhaarit kijiye; likhit nirdesh aur naveen tainaati soochna mein antar ho to bataaiye.
- `train_sft-0000-te` (native): loyalty-api కోసం ప్రస్తుతం production లో batch_size_mb ఎంత? రన్‌బుక్‌ను deployment ఆధారాలతో పోల్చి పాత పేజీని గుర్తించండి.
- `train_sft-0023-te` (latin): audit-stream kosam amalulo unna circuit_breaker_pct ni cheppu; patram mariyu tainaati vivaraalu veruga unte paatha page chupinchu.

## Proposed next phase — not launched

After review: start a fresh one-epoch SFT run from the pinned base model on all 240 SFT rows, validate on the separate 80-row split, and use at least the measured 2,560-token budget. Do not reuse the v1 adapter or its automatic validation split. Then smoke-test v2 active-advantage GRPO before any longer L40S run, and compare newly evaluated Base/SFT/GRPO checkpoints on the same v2 frozen holdouts. No target accuracy is imposed.

The active sampler rotates accepted groups across the four task kinds, logs `zero_variance_skipped`, and bounds retries at 32 per requested kind. If all candidates for that kind have identical rewards it raises an error rather than counting a fake update. This conditions the accepted training distribution on reward variance; accepted/attempted coverage and sampling cost need to be reported. A CPU integration test covers the actual backend hook; GPU behavior remains untested for v2.


# File: `SHA256SUMS`

```text
5316e6e04bb476181e826ba9a23229440595f9e892ac628cd50b8be00fe1e35b  AUDIT.json
51612d5c14ed2a9fcf930825d042da23ad59870665ced07a54a0c6c558b3e0e3  case_pool_manifest.json
a1e8630f4cc9244ee96d2ab41ab811918417da1b510ee987b54bb9902dcef3da  curation_funnel.json
622e3bf8fce40796c64c6b3683bba441e096272ebf02fb83e3a430ae45f5acf2  curation_rejections.jsonl
c6d808482bb85143b08eda51e6703f13f9f0817dd0b30a90ca3cd2d81e8b3469  holdout_repo_style_100_frozen.jsonl
82b92badc6f1fdc71bba41a876db4adf9f19633108b26331297227a7587ac50b  holdout_synth_400_frozen.jsonl
936b456679fed055e3e2f1953011bbe3d86be296788972d55d8a52d998cf1d41  token_length_audit.json
b44e67d78d2abc921583c535a10c3a2bd790aca8fd43723e87151c0c962b7768  train_grpo_stage1.jsonl
8d7f5236f1fad9450f5ae3ecb81e83b9acda96f01d548225787b7f7eb5754977  train_grpo_stage2.jsonl
96402f7d8ce8f05ee98aee212f1af9ac7a2b51fef1098e2beda3e395b90e1932  train_sft_240.jsonl
63265574e26aad81ee4d136b461eacd7fcf8dcd283a87231bcb181a7e2db1674  train_sft_agenttune_trajectories.jsonl
4eb608f1391596afe2ad62f67e9c5a68e5b396838b8c97f130638d9510f3b254  val_train_80.jsonl
e0cc20b5d5ccc5e1dc6ab8042390077d4fc040760c9aae74508e95e665a19df6  world_repo_style.json
664177831119ebd56744a45791a43510600294bcca87d4176b4f45c50eab3985  world_test_synth.json
664c892b8cf7971a8da92a6f2e5f1e6e1ece0103e73479af4e20c427a4cf68cb  world_train.json
```

## Final verification

The complete project suite passed: **50 tests**, including v2 pairwise split separation, all semantic oracle paths, production/staging distractors, native-script coverage, incident conversions, real curation, reward-hacking regressions and the active-advantage backend CPU integration check. A benign warning remains in an existing tiny PEFT save/reload fixture.

Both manifests were verified: all 10 original v1 machine files remain unchanged, and all 15 v2 machine files match `data_v2/SHA256SUMS`. The new sampler/backend has not had a v2 GPU training smoke test. No v2 SFT, GRPO, baseline evaluation or paid cloud job was launched. Training remains gated on this data review.
