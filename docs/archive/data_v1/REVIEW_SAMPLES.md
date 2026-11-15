# DriftGuard-MCP data review samples

Review export only. Original datasets, ground truth, prompts, tool schemas, oracle messages and metadata are copied without editing. This file is not training or evaluation input. No experiments were run to produce it.

Each JSONL dataset contributes 10 complete records, selected deterministically across task types and language groups rather than taking ten adjacent records. Source line numbers are shown (1-based). Ten records cannot cover every language/task combination. All fields are retained, including gold labels and oracle traces where present, so the reviewer can assess what is available to the model versus the training/evaluation code.

For world JSON files, metadata is preserved and each top-level list is sampled to at most 10 entries; facts, incidents, service names and employee lists therefore each have up to 10 examples. These independently sampled lists are excerpts, not a runnable or necessarily referentially complete world. The curation metadata and checksum manifest are included in full because they are small.

---

# File: `SHA256SUMS`

Source SHA-256: `1e3672eeb7f426b93e91e8a9e05f237e07c567d5b9e39aeb2461938b734c3048`

Complete supporting manifest.

```text
9ccf35c212138b4281ac4812bb5ae9205a7b12674683f28673becf9464631637  curation_funnel.json
bafc7eae5563216963cf36e284d376a32f7be95369b3b266af8412a70e6af253  holdout_repo_style_100_frozen.jsonl
4fc790e517f4f5c34c887a68c2a4a95de0eb98347eeaac855f3e0e4e861e8ef9  holdout_synth_400_frozen.jsonl
ac9a066588db779fb37f866858d0592cf64560e214cc87be2ffcffb4c86b589d  train_grpo_stage1.jsonl
88b917119182c1941a49078fd02352a356cdd3eb79ae02350c95670b095a010a  train_grpo_stage2.jsonl
4f6926280ecbc6aa5b78a9ee5804351cb991c5be3d894d90b75bc1905dcf78a0  train_sft_400.jsonl
237b733ac831be5ecedbc505f38868b039dc6a3de548304a558d943af41c05a4  train_sft_agenttune_trajectories.jsonl
986244ef0d7c7f7755d67bfcb461ec5bbbf66856d2328e4727c64b455717830f  world_repo_style.json
8917e2520ba04b2809c65004e45035507bca2efc56bd383089c13306fc10a544  world_test_synth.json
2f68a305b5eeb515442f6564a9fb2399b5f5291bd2172e4697d9b29a1594cf44  world_train.json
```

---

# File: `curation_funnel.json`

Source SHA-256: `9ccf35c212138b4281ac4812bb5ae9205a7b12674683f28673becf9464631637`

Complete supporting metadata (no truncation).

```json
{
  "train_sft_400": {
    "input": 400,
    "kept": 400,
    "rejected": 0,
    "method": "CuratorKIT ExactDeduplicator; prompt plus active schemas",
    "semantic_dedup": false,
    "oracle_verified": 400,
    "languages": {
      "en": 100,
      "hi": 100,
      "hinglish": 100,
      "te": 100
    },
    "task_kinds": {
      "consistent": 80,
      "incident": 60,
      "conflict": 200,
      "abstain": 60
    }
  },
  "train_grpo_stage1": {
    "input": 400,
    "kept": 400,
    "rejected": 0,
    "method": "CuratorKIT ExactDeduplicator; prompt plus active schemas",
    "semantic_dedup": false,
    "oracle_verified": 400,
    "languages": {
      "en": 100,
      "hi": 100,
      "hinglish": 100,
      "te": 100
    },
    "task_kinds": {
      "consistent": 160,
      "incident": 120,
      "conflict": 80,
      "abstain": 40
    }
  },
  "train_grpo_stage2": {
    "input": 400,
    "kept": 400,
    "rejected": 0,
    "method": "CuratorKIT ExactDeduplicator; prompt plus active schemas",
    "semantic_dedup": false,
    "oracle_verified": 400,
    "languages": {
      "en": 100,
      "hi": 100,
      "hinglish": 100,
      "te": 100
    },
    "task_kinds": {
      "consistent": 80,
      "incident": 40,
      "conflict": 220,
      "abstain": 60
    }
  },
  "holdout_synth_400_frozen": {
    "input": 400,
    "kept": 400,
    "rejected": 0,
    "method": "CuratorKIT ExactDeduplicator; prompt plus active schemas",
    "semantic_dedup": false,
    "oracle_verified": 400,
    "languages": {
      "en": 100,
      "hi": 100,
      "hinglish": 100,
      "te": 100
    },
    "task_kinds": {
      "consistent": 80,
      "incident": 60,
      "conflict": 200,
      "abstain": 60
    }
  },
  "holdout_repo_style_100_frozen": {
    "input": 100,
    "kept": 100,
    "rejected": 0,
    "method": "CuratorKIT ExactDeduplicator; prompt plus active schemas",
    "semantic_dedup": false,
    "oracle_verified": 100,
    "languages": {
      "en": 25,
      "hi": 25,
      "hinglish": 25,
      "te": 25
    },
    "task_kinds": {
      "conflict": 100
    }
  }
}
```

---

# File: `holdout_repo_style_100_frozen.jsonl`

Source SHA-256: `bafc7eae5563216963cf36e284d376a32f7be95369b3b266af8412a70e6af253`

10 complete records selected from 100 source rows.

## Sample 1 — source line 1

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp",
    "slack-mcp"
  ],
  "case_id": "repo_style-0000",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-REALSTYLE-00",
    "PR-REALSTYLE-00"
  ],
  "gold_value": 10001,
  "incident_id": null,
  "kind": "conflict",
  "language": "en",
  "oracle_optimal_steps": 2,
  "param_name": "timeout_sec",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Audit the documented timeout_sec for fastapi-case-00 against github-mcp; report the effective setting and any stale page.",
      "role": "user"
    }
  ],
  "question": "Audit the documented timeout_sec for fastapi-case-00 against github-mcp; report the effective setting and any stale page.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "fastapi-case-00",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-REALSTYLE-00",
  "stale_trap_value": 10000,
  "task_id": "repo_style-0000-en",
  "world_split": "repo_style"
}
```

## Sample 2 — source line 14

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "repo_style-0013",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-REALSTYLE-13",
    "PR-REALSTYLE-13"
  ],
  "gold_value": 10027,
  "incident_id": null,
  "kind": "conflict",
  "language": "en",
  "oracle_optimal_steps": 2,
  "param_name": "max_retries",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Audit the documented max_retries for pydantic-case-04 against github-mcp; report the effective setting and any stale page.",
      "role": "user"
    }
  ],
  "question": "Audit the documented max_retries for pydantic-case-04 against github-mcp; report the effective setting and any stale page.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "pydantic-case-04",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-REALSTYLE-13",
  "stale_trap_value": 10026,
  "task_id": "repo_style-0013-en",
  "world_split": "repo_style"
}
```

## Sample 3 — source line 21

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "repo_style-0020",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-REALSTYLE-20",
    "PR-REALSTYLE-20"
  ],
  "gold_value": 10041,
  "incident_id": null,
  "kind": "conflict",
  "language": "en",
  "oracle_optimal_steps": 2,
  "param_name": "rate_limit_rpm",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Audit the documented rate_limit_rpm for litellm-case-06 against github-mcp; report the effective setting and any stale page.",
      "role": "user"
    }
  ],
  "question": "Audit the documented rate_limit_rpm for litellm-case-06 against github-mcp; report the effective setting and any stale page.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "litellm-case-06",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-REALSTYLE-20",
  "stale_trap_value": 10040,
  "task_id": "repo_style-0020-en",
  "world_split": "repo_style"
}
```

## Sample 4 — source line 35

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "repo_style-0014",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-REALSTYLE-14",
    "PR-REALSTYLE-14"
  ],
  "gold_value": 10029,
  "incident_id": null,
  "kind": "conflict",
  "language": "hi",
  "oracle_optimal_steps": 2,
  "param_name": "rate_limit_rpm",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "litellm-case-04 ke rate_limit_rpm ka prabhaavi maan kya hai? Puraane nirdesh ko github-mcp ke pramaan se milaakar bataaiye.",
      "role": "user"
    }
  ],
  "question": "litellm-case-04 ke rate_limit_rpm ka prabhaavi maan kya hai? Puraane nirdesh ko github-mcp ke pramaan se milaakar bataaiye.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "litellm-case-04",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-REALSTYLE-14",
  "stale_trap_value": 10028,
  "task_id": "repo_style-0014-hi",
  "world_split": "repo_style"
}
```

## Sample 5 — source line 41

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "repo_style-0020",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-REALSTYLE-20",
    "PR-REALSTYLE-20"
  ],
  "gold_value": 10041,
  "incident_id": null,
  "kind": "conflict",
  "language": "hi",
  "oracle_optimal_steps": 2,
  "param_name": "rate_limit_rpm",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "litellm-case-06 ke rate_limit_rpm ka prabhaavi maan kya hai? Puraane nirdesh ko github-mcp ke pramaan se milaakar bataaiye.",
      "role": "user"
    }
  ],
  "question": "litellm-case-06 ke rate_limit_rpm ka prabhaavi maan kya hai? Puraane nirdesh ko github-mcp ke pramaan se milaakar bataaiye.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "litellm-case-06",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-REALSTYLE-20",
  "stale_trap_value": 10040,
  "task_id": "repo_style-0020-hi",
  "world_split": "repo_style"
}
```

## Sample 6 — source line 60

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "repo_style-0014",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-REALSTYLE-14",
    "PR-REALSTYLE-14"
  ],
  "gold_value": 10029,
  "incident_id": null,
  "kind": "conflict",
  "language": "hinglish",
  "oracle_optimal_steps": 2,
  "param_name": "rate_limit_rpm",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Hey, litellm-case-04 pe rate_limit_rpm actually kitna configured hai? Runbook vs github-mcp reconcile karke outdated page flag karna.",
      "role": "user"
    }
  ],
  "question": "Hey, litellm-case-04 pe rate_limit_rpm actually kitna configured hai? Runbook vs github-mcp reconcile karke outdated page flag karna.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "litellm-case-04",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-REALSTYLE-14",
  "stale_trap_value": 10028,
  "task_id": "repo_style-0014-hinglish",
  "world_split": "repo_style"
}
```

## Sample 7 — source line 66

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "repo_style-0020",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-REALSTYLE-20",
    "PR-REALSTYLE-20"
  ],
  "gold_value": 10041,
  "incident_id": null,
  "kind": "conflict",
  "language": "hinglish",
  "oracle_optimal_steps": 2,
  "param_name": "rate_limit_rpm",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Hey, litellm-case-06 pe rate_limit_rpm actually kitna configured hai? Runbook vs github-mcp reconcile karke outdated page flag karna.",
      "role": "user"
    }
  ],
  "question": "Hey, litellm-case-06 pe rate_limit_rpm actually kitna configured hai? Runbook vs github-mcp reconcile karke outdated page flag karna.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "litellm-case-06",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-REALSTYLE-20",
  "stale_trap_value": 10040,
  "task_id": "repo_style-0020-hinglish",
  "world_split": "repo_style"
}
```

## Sample 8 — source line 80

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "repo_style-0004",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-REALSTYLE-04",
    "PR-REALSTYLE-04"
  ],
  "gold_value": 10009,
  "incident_id": null,
  "kind": "conflict",
  "language": "te",
  "oracle_optimal_steps": 2,
  "param_name": "sla_hours",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "pydantic-case-01 lo amalulo unna sla_hours viluva telapandi. Runbook vivaralanu github-mcp aadharaalatho polchandi.",
      "role": "user"
    }
  ],
  "question": "pydantic-case-01 lo amalulo unna sla_hours viluva telapandi. Runbook vivaralanu github-mcp aadharaalatho polchandi.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "pydantic-case-01",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-REALSTYLE-04",
  "stale_trap_value": 10008,
  "task_id": "repo_style-0004-te",
  "world_split": "repo_style"
}
```

## Sample 9 — source line 96

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "repo_style-0025",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-REALSTYLE-25",
    "PR-REALSTYLE-25"
  ],
  "gold_value": 10051,
  "incident_id": null,
  "kind": "conflict",
  "language": "te",
  "oracle_optimal_steps": 2,
  "param_name": "max_retries",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "pydantic-case-08 lo amalulo unna max_retries viluva telapandi. Runbook vivaralanu github-mcp aadharaalatho polchandi.",
      "role": "user"
    }
  ],
  "question": "pydantic-case-08 lo amalulo unna max_retries viluva telapandi. Runbook vivaralanu github-mcp aadharaalatho polchandi.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "pydantic-case-08",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-REALSTYLE-25",
  "stale_trap_value": 10050,
  "task_id": "repo_style-0025-te",
  "world_split": "repo_style"
}
```

## Sample 10 — source line 100

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "repo_style-0029",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-REALSTYLE-29",
    "PR-REALSTYLE-29"
  ],
  "gold_value": 10059,
  "incident_id": null,
  "kind": "conflict",
  "language": "te",
  "oracle_optimal_steps": 2,
  "param_name": "circuit_breaker_pct",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "litellm-case-09 lo amalulo unna circuit_breaker_pct viluva telapandi. Runbook vivaralanu github-mcp aadharaalatho polchandi.",
      "role": "user"
    }
  ],
  "question": "litellm-case-09 lo amalulo unna circuit_breaker_pct viluva telapandi. Runbook vivaralanu github-mcp aadharaalatho polchandi.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "litellm-case-09",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-REALSTYLE-29",
  "stale_trap_value": 10058,
  "task_id": "repo_style-0029-te",
  "world_split": "repo_style"
}
```

---

# File: `holdout_synth_400_frozen.jsonl`

Source SHA-256: `4fc790e517f4f5c34c887a68c2a4a95de0eb98347eeaac855f3e0e4e861e8ef9`

10 complete records selected from 400 source rows.

## Sample 1 — source line 3

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp",
    "github-mcp"
  ],
  "case_id": "test_synth-0000",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-TS-001",
    "SLACK-TS-001"
  ],
  "gold_value": 4,
  "incident_id": null,
  "kind": "consistent",
  "language": "hinglish",
  "oracle_optimal_steps": 2,
  "param_name": "max_retries",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Hey, kyc-verifier pe max_retries actually kitna configured hai? Runbook vs slack-mcp reconcile karke outdated page flag karna.",
      "role": "user"
    }
  ],
  "question": "Hey, kyc-verifier pe max_retries actually kitna configured hai? Runbook vs slack-mcp reconcile karke outdated page flag karna.",
  "required_mcps": [
    "notion-mcp",
    "slack-mcp"
  ],
  "service_name": "kyc-verifier",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "test_synth-0000-hinglish",
  "world_split": "test_synth"
}
```

## Sample 2 — source line 13

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "github-mcp"
  ],
  "case_id": "test_synth-0003",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-TS-009",
    "SLACK-TS-009"
  ],
  "gold_value": 80,
  "incident_id": null,
  "kind": "consistent",
  "language": "en",
  "oracle_optimal_steps": 2,
  "param_name": "batch_size_mb",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Audit the documented batch_size_mb for settlement-engine against slack-mcp; report the effective setting and any stale page.",
      "role": "user"
    }
  ],
  "question": "Audit the documented batch_size_mb for settlement-engine against slack-mcp; report the effective setting and any stale page.",
  "required_mcps": [
    "notion-mcp",
    "slack-mcp"
  ],
  "service_name": "settlement-engine",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "test_synth-0003-en",
  "world_split": "test_synth"
}
```

## Sample 3 — source line 82

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "test_synth-0020",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TS-20"
  ],
  "gold_value": 56.0,
  "incident_id": "INC-TS-20",
  "kind": "incident",
  "language": "hi",
  "oracle_optimal_steps": 3,
  "param_name": "rate_limit_rpm",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "INC-TS-20 ka samay-aadhaarit kul jurmaana nirdhaarit kijiye: db-mcp ke samay se time-mcp dwaara avadhi ghanton mein aur math-mcp dwaara avadhi guna penalty_rate_per_hour.",
      "role": "user"
    }
  ],
  "question": "INC-TS-20 ka samay-aadhaarit kul jurmaana nirdhaarit kijiye: db-mcp ke samay se time-mcp dwaara avadhi ghanton mein aur math-mcp dwaara avadhi guna penalty_rate_per_hour.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "receipt-store",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "test_synth-0020-hi",
  "world_split": "test_synth"
}
```

## Sample 4 — source line 109

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "slack-mcp"
  ],
  "case_id": "test_synth-0027",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TS-27"
  ],
  "gold_value": 168.0,
  "incident_id": "INC-TS-27",
  "kind": "incident",
  "language": "en",
  "oracle_optimal_steps": 3,
  "param_name": "sla_hours",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Compute the total time-based penalty for INC-TS-27: retrieve the database incident, measure its duration using time-mcp, and multiply hours by penalty_rate_per_hour using math-mcp.",
      "role": "user"
    }
  ],
  "question": "Compute the total time-based penalty for INC-TS-27: retrieve the database incident, measure its duration using time-mcp, and multiply hours by penalty_rate_per_hour using math-mcp.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "wallet-bridge",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "test_synth-0027-en",
  "world_split": "test_synth"
}
```

## Sample 5 — source line 120

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "test_synth-0029",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TS-29"
  ],
  "gold_value": 280.0,
  "incident_id": "INC-TS-29",
  "kind": "incident",
  "language": "te",
  "oracle_optimal_steps": 3,
  "param_name": "rate_limit_rpm",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "INC-TS-29 valla vacchina mottham jarimaana entha? db-mcp saakshyam teesukoni time-mcp lo vyavadhi gantalu, math-mcp lo gantalu mariyu penalty_rate_per_hour gunakaaram cheyyandi.",
      "role": "user"
    }
  ],
  "question": "INC-TS-29 valla vacchina mottham jarimaana entha? db-mcp saakshyam teesukoni time-mcp lo vyavadhi gantalu, math-mcp lo gantalu mariyu penalty_rate_per_hour gunakaaram cheyyandi.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "dispute-manager",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "test_synth-0029-te",
  "world_split": "test_synth"
}
```

## Sample 6 — source line 192

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "test_synth-0047",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-TS-083",
    "SLACK-TS-083"
  ],
  "gold_value": 50,
  "incident_id": null,
  "kind": "conflict",
  "language": "te",
  "oracle_optimal_steps": 2,
  "param_name": "circuit_breaker_pct",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "merchant-registry lo amalulo unna circuit_breaker_pct viluva telapandi. Runbook vivaralanu slack-mcp aadharaalatho polchandi.",
      "role": "user"
    }
  ],
  "question": "merchant-registry lo amalulo unna circuit_breaker_pct viluva telapandi. Runbook vivaralanu slack-mcp aadharaalatho polchandi.",
  "required_mcps": [
    "notion-mcp",
    "slack-mcp"
  ],
  "service_name": "merchant-registry",
  "source_server": "slack-mcp",
  "stale_doc_id": "NOTION-TS-083",
  "stale_trap_value": 40,
  "task_id": "test_synth-0047-te",
  "world_split": "test_synth"
}
```

## Sample 7 — source line 338

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp",
    "slack-mcp"
  ],
  "case_id": "test_synth-0084",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-TS-142",
    "PR-TS-142"
  ],
  "gold_value": 8,
  "incident_id": null,
  "kind": "conflict",
  "language": "hi",
  "oracle_optimal_steps": 2,
  "param_name": "sla_hours",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "treasury-router mein sla_hours sambandhi dastavez aur github-mcp ki tulna karke sahi maan dijiye.",
      "role": "user"
    }
  ],
  "question": "treasury-router mein sla_hours sambandhi dastavez aur github-mcp ki tulna karke sahi maan dijiye.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "treasury-router",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-TS-142",
  "stale_trap_value": 4,
  "task_id": "test_synth-0084-hi",
  "world_split": "test_synth"
}
```

## Sample 8 — source line 341

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "test_synth-0085",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "en",
  "oracle_optimal_steps": 1,
  "param_name": "circuit_breaker_pct",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Database-only request: determine circuit_breaker_pct for unknown-test_synth-service-85. Return abstain if the database server is disconnected or has no such service.",
      "role": "user"
    }
  ],
  "question": "Database-only request: determine circuit_breaker_pct for unknown-test_synth-service-85. Return abstain if the database server is disconnected or has no such service.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "unknown-test_synth-service-85",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "test_synth-0085-en",
  "world_split": "test_synth"
}
```

## Sample 9 — source line 355

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "test_synth-0088",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "hinglish",
  "oracle_optimal_steps": 0,
  "param_name": "max_retries",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "DB-only audit: dispute-manager ka max_retries nikaalna hai. db-mcp disconnected ya entity missing hai toh answer guess mat karo, abstain do.",
      "role": "user"
    }
  ],
  "question": "DB-only audit: dispute-manager ka max_retries nikaalna hai. db-mcp disconnected ya entity missing hai toh answer guess mat karo, abstain do.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "dispute-manager",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "test_synth-0088-hinglish",
  "world_split": "test_synth"
}
```

## Sample 10 — source line 364

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp",
    "github-mcp"
  ],
  "case_id": "test_synth-0090",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "te",
  "oracle_optimal_steps": 0,
  "param_name": "batch_size_mb",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "db-mcp aadharam maatrame vaadandi: dispute-manager lo batch_size_mb entha? Database andubaatulo lekapothe leda seva lekapothe abstain ivvandi.",
      "role": "user"
    }
  ],
  "question": "db-mcp aadharam maatrame vaadandi: dispute-manager lo batch_size_mb entha? Database andubaatulo lekapothe leda seva lekapothe abstain ivvandi.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "dispute-manager",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "test_synth-0090-te",
  "world_split": "test_synth"
}
```

---

# File: `train_grpo_stage1.jsonl`

Source SHA-256: `ac9a066588db779fb37f866858d0592cf64560e214cc87be2ffcffb4c86b589d`

10 complete records selected from 400 source rows.

## Sample 1 — source line 115

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0028",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-TR-081",
    "SLACK-TR-081"
  ],
  "gold_value": 121,
  "incident_id": null,
  "kind": "consistent",
  "language": "hinglish",
  "oracle_optimal_steps": 2,
  "param_name": "batch_size_mb",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Bhai, billing-api ka current batch_size_mb kya hai? Notion aur slack-mcp check karo.",
      "role": "user"
    }
  ],
  "question": "Bhai, billing-api ka current batch_size_mb kya hai? Notion aur slack-mcp check karo.",
  "required_mcps": [
    "notion-mcp",
    "slack-mcp"
  ],
  "service_name": "billing-api",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0028-hinglish",
  "world_split": "train"
}
```

## Sample 2 — source line 129

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0032",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-TR-088",
    "PR-TR-088"
  ],
  "gold_value": 9,
  "incident_id": null,
  "kind": "consistent",
  "language": "en",
  "oracle_optimal_steps": 2,
  "param_name": "sla_hours",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "What is checkout-api sla_hours now? Verify the runbook using github-mcp.",
      "role": "user"
    }
  ],
  "question": "What is checkout-api sla_hours now? Verify the runbook using github-mcp.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "checkout-api",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0032-en",
  "world_split": "train"
}
```

## Sample 3 — source line 228

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0056",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TR-06"
  ],
  "gold_value": 66.0,
  "incident_id": "INC-TR-06",
  "kind": "incident",
  "language": "te",
  "oracle_optimal_steps": 3,
  "param_name": "circuit_breaker_pct",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Sanghatana INC-TR-06 vivaraalu db-mcp lo choodu, time-mcp tho gantalu lekkinchu, math-mcp tho gantalu guninchu penalty_rate_per_hour; mottham penalty cheppu.",
      "role": "user"
    }
  ],
  "question": "Sanghatana INC-TR-06 vivaraalu db-mcp lo choodu, time-mcp tho gantalu lekkinchu, math-mcp tho gantalu guninchu penalty_rate_per_hour; mottham penalty cheppu.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "tax-engine",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0056-te",
  "world_split": "train"
}
```

## Sample 4 — source line 249

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0062",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TR-12"
  ],
  "gold_value": 99.0,
  "incident_id": "INC-TR-12",
  "kind": "incident",
  "language": "en",
  "oracle_optimal_steps": 3,
  "param_name": "sla_hours",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "For incident INC-TR-12, use db-mcp and time-mcp to find elapsed hours, then math-mcp to calculate elapsed hours times penalty_rate_per_hour. Give the total penalty.",
      "role": "user"
    }
  ],
  "question": "For incident INC-TR-12, use db-mcp and time-mcp to find elapsed hours, then math-mcp to calculate elapsed hours times penalty_rate_per_hour. Give the total penalty.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "upi-gateway",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0062-en",
  "world_split": "train"
}
```

## Sample 5 — source line 270

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train-0067",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TR-17"
  ],
  "gold_value": 99.0,
  "incident_id": "INC-TR-17",
  "kind": "incident",
  "language": "hi",
  "oracle_optimal_steps": 3,
  "param_name": "timeout_sec",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Ghatna INC-TR-17 ke liye db-mcp tatha time-mcp se beetey ghante nikaaliye, phir math-mcp se ghante guna penalty_rate_per_hour karke kul jurmaana bataaiye.",
      "role": "user"
    }
  ],
  "question": "Ghatna INC-TR-17 ke liye db-mcp tatha time-mcp se beetey ghante nikaaliye, phir math-mcp se ghante guna penalty_rate_per_hour karke kul jurmaana bataaiye.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "payment-worker",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0067-hi",
  "world_split": "train"
}
```

## Sample 6 — source line 298

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0074",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-TR-120",
    "PR-TR-120"
  ],
  "gold_value": 61,
  "incident_id": null,
  "kind": "conflict",
  "language": "hi",
  "oracle_optimal_steps": 2,
  "param_name": "timeout_sec",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Kripya event-router ke timeout_sec ki jaanch dastavez tatha github-mcp se kijiye.",
      "role": "user"
    }
  ],
  "question": "Kripya event-router ke timeout_sec ki jaanch dastavez tatha github-mcp se kijiye.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "event-router",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-TR-120",
  "stale_trap_value": 41,
  "task_id": "train-0074-hi",
  "world_split": "train"
}
```

## Sample 7 — source line 344

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train-0085",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-TR-143",
    "SLACK-TR-143"
  ],
  "gold_value": 51,
  "incident_id": null,
  "kind": "conflict",
  "language": "te",
  "oracle_optimal_steps": 2,
  "param_name": "circuit_breaker_pct",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "refund-worker yokka circuit_breaker_pct cheppu; patram mariyu slack-mcp rendu choodu.",
      "role": "user"
    }
  ],
  "question": "refund-worker yokka circuit_breaker_pct cheppu; patram mariyu slack-mcp rendu choodu.",
  "required_mcps": [
    "notion-mcp",
    "slack-mcp"
  ],
  "service_name": "refund-worker",
  "source_server": "slack-mcp",
  "stale_doc_id": "NOTION-TR-143",
  "stale_trap_value": 41,
  "task_id": "train-0085-te",
  "world_split": "train"
}
```

## Sample 8 — source line 371

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0092",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "hinglish",
  "oracle_optimal_steps": 0,
  "param_name": "sla_hours",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "checkout-api ka sla_hours DB se hi do. db-mcp off ho ya service missing ho toh abstain karo.",
      "role": "user"
    }
  ],
  "question": "checkout-api ka sla_hours DB se hi do. db-mcp off ho ya service missing ho toh abstain karo.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "checkout-api",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0092-hinglish",
  "world_split": "train"
}
```

## Sample 9 — source line 377

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0094",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "en",
  "oracle_optimal_steps": 0,
  "param_name": "rate_limit_rpm",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Read media-worker rate_limit_rpm from db-mcp only. If db-mcp is unavailable or this service is absent, abstain.",
      "role": "user"
    }
  ],
  "question": "Read media-worker rate_limit_rpm from db-mcp only. If db-mcp is unavailable or this service is absent, abstain.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "media-worker",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0094-en",
  "world_split": "train"
}
```

## Sample 10 — source line 396

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0098",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "te",
  "oracle_optimal_steps": 0,
  "param_name": "circuit_breaker_pct",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "coupon-engine ki circuit_breaker_pct db-mcp nunche teesuko. Server lekapoyina seva dorakakapoyina samaadhaanam ivvaku.",
      "role": "user"
    }
  ],
  "question": "coupon-engine ki circuit_breaker_pct db-mcp nunche teesuko. Server lekapoyina seva dorakakapoyina samaadhaanam ivvaku.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "coupon-engine",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0098-te",
  "world_split": "train"
}
```

---

# File: `train_grpo_stage2.jsonl`

Source SHA-256: `88b917119182c1941a49078fd02352a356cdd3eb79ae02350c95670b095a010a`

10 complete records selected from 400 source rows.

## Sample 1 — source line 53

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train-0013",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-TR-042",
    "PR-TR-042"
  ],
  "gold_value": 61,
  "incident_id": null,
  "kind": "consistent",
  "language": "en",
  "oracle_optimal_steps": 2,
  "param_name": "timeout_sec",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "What is profile-store timeout_sec now? Verify the runbook using github-mcp.",
      "role": "user"
    }
  ],
  "question": "What is profile-store timeout_sec now? Verify the runbook using github-mcp.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "profile-store",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0013-en",
  "world_split": "train"
}
```

## Sample 2 — source line 71

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train-0017",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-TR-060",
    "PR-TR-060"
  ],
  "gold_value": 21,
  "incident_id": null,
  "kind": "consistent",
  "language": "hinglish",
  "oracle_optimal_steps": 2,
  "param_name": "timeout_sec",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Bhai, session-cache ka current timeout_sec kya hai? Notion aur github-mcp check karo.",
      "role": "user"
    }
  ],
  "question": "Bhai, session-cache ka current timeout_sec kya hai? Notion aur github-mcp check karo.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "session-cache",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0017-hinglish",
  "world_split": "train"
}
```

## Sample 3 — source line 102

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train-0025",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TR-25"
  ],
  "gold_value": 33.0,
  "incident_id": "INC-TR-25",
  "kind": "incident",
  "language": "hi",
  "oracle_optimal_steps": 3,
  "param_name": "timeout_sec",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Ghatna INC-TR-25 ke liye db-mcp tatha time-mcp se beetey ghante nikaaliye, phir math-mcp se ghante guna penalty_rate_per_hour karke kul jurmaana bataaiye.",
      "role": "user"
    }
  ],
  "question": "Ghatna INC-TR-25 ke liye db-mcp tatha time-mcp se beetey ghante nikaaliye, phir math-mcp se ghante guna penalty_rate_per_hour karke kul jurmaana bataaiye.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "metrics-agent",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0025-hi",
  "world_split": "train"
}
```

## Sample 4 — source line 108

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0026",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TR-26"
  ],
  "gold_value": 66.0,
  "incident_id": "INC-TR-26",
  "kind": "incident",
  "language": "te",
  "oracle_optimal_steps": 3,
  "param_name": "batch_size_mb",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Sanghatana INC-TR-26 vivaraalu db-mcp lo choodu, time-mcp tho gantalu lekkinchu, math-mcp tho gantalu guninchu penalty_rate_per_hour; mottham penalty cheppu.",
      "role": "user"
    }
  ],
  "question": "Sanghatana INC-TR-26 vivaraalu db-mcp lo choodu, time-mcp tho gantalu lekkinchu, math-mcp tho gantalu guninchu penalty_rate_per_hour; mottham penalty cheppu.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "metrics-agent",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0026-te",
  "world_split": "train"
}
```

## Sample 5 — source line 113

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0028",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TR-28"
  ],
  "gold_value": 132.0,
  "incident_id": "INC-TR-28",
  "kind": "incident",
  "language": "en",
  "oracle_optimal_steps": 3,
  "param_name": "batch_size_mb",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "For incident INC-TR-28, use db-mcp and time-mcp to find elapsed hours, then math-mcp to calculate elapsed hours times penalty_rate_per_hour. Give the total penalty.",
      "role": "user"
    }
  ],
  "question": "For incident INC-TR-28, use db-mcp and time-mcp to find elapsed hours, then math-mcp to calculate elapsed hours times penalty_rate_per_hour. Give the total penalty.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "billing-api",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0028-en",
  "world_split": "train"
}
```

## Sample 6 — source line 168

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train-0041",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-TR-058",
    "PR-TR-058"
  ],
  "gold_value": 9,
  "incident_id": null,
  "kind": "conflict",
  "language": "te",
  "oracle_optimal_steps": 2,
  "param_name": "sla_hours",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "inventory-sync ki ippudu sla_hours entha? Runbook ni github-mcp tho sarichoodu.",
      "role": "user"
    }
  ],
  "question": "inventory-sync ki ippudu sla_hours entha? Runbook ni github-mcp tho sarichoodu.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "inventory-sync",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-TR-058",
  "stale_trap_value": 5,
  "task_id": "train-0041-te",
  "world_split": "train"
}
```

## Sample 7 — source line 254

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "slack-mcp"
  ],
  "case_id": "train-0063",
  "distractor_mcps": [],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-TR-102",
    "PR-TR-102"
  ],
  "gold_value": 61,
  "incident_id": null,
  "kind": "conflict",
  "language": "hi",
  "oracle_optimal_steps": 2,
  "param_name": "timeout_sec",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Kripya loyalty-api ke timeout_sec ki jaanch dastavez tatha github-mcp se kijiye.",
      "role": "user"
    }
  ],
  "question": "Kripya loyalty-api ke timeout_sec ki jaanch dastavez tatha github-mcp se kijiye.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "loyalty-api",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-TR-102",
  "stale_trap_value": 41,
  "task_id": "train-0063-hi",
  "world_split": "train"
}
```

## Sample 8 — source line 371

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0092",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "hinglish",
  "oracle_optimal_steps": 0,
  "param_name": "sla_hours",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "checkout-api ka sla_hours DB se hi do. db-mcp off ho ya service missing ho toh abstain karo.",
      "role": "user"
    }
  ],
  "question": "checkout-api ka sla_hours DB se hi do. db-mcp off ho ya service missing ho toh abstain karo.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "checkout-api",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0092-hinglish",
  "world_split": "train"
}
```

## Sample 9 — source line 377

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0094",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "en",
  "oracle_optimal_steps": 0,
  "param_name": "rate_limit_rpm",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Read media-worker rate_limit_rpm from db-mcp only. If db-mcp is unavailable or this service is absent, abstain.",
      "role": "user"
    }
  ],
  "question": "Read media-worker rate_limit_rpm from db-mcp only. If db-mcp is unavailable or this service is absent, abstain.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "media-worker",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0094-en",
  "world_split": "train"
}
```

## Sample 10 — source line 396

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0098",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "te",
  "oracle_optimal_steps": 0,
  "param_name": "circuit_breaker_pct",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "coupon-engine ki circuit_breaker_pct db-mcp nunche teesuko. Server lekapoyina seva dorakakapoyina samaadhaanam ivvaku.",
      "role": "user"
    }
  ],
  "question": "coupon-engine ki circuit_breaker_pct db-mcp nunche teesuko. Server lekapoyina seva dorakakapoyina samaadhaanam ivvaku.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "coupon-engine",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0098-te",
  "world_split": "train"
}
```

---

# File: `train_sft_400.jsonl`

Source SHA-256: `4f6926280ecbc6aa5b78a9ee5804351cb991c5be3d894d90b75bc1905dcf78a0`

10 complete records selected from 400 source rows.

## Sample 1 — source line 53

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp"
  ],
  "case_id": "train-0013",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-TR-042",
    "PR-TR-042"
  ],
  "gold_value": 61,
  "incident_id": null,
  "kind": "consistent",
  "language": "en",
  "messages": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "What is profile-store timeout_sec now? Verify the runbook using github-mcp.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"notion-mcp\", \"tool\": \"search_notion\", \"arguments\": {\"query\": \"profile-store timeout_sec\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"page_id\": \"NOTION-TR-042\", \"title\": \"profile-store timeout_sec\", \"updated_at\": \"2026-02-10T09:00:00+00:00\", \"snippet\": \"profile-store timeout_sec = 61. Documented configuration at publication. Later deployment records may supersede this runbook.\"}]",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"github-mcp\", \"tool\": \"search_github_prs\", \"arguments\": {\"query\": \"profile-store timeout_sec\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"pr_id\": \"PR-TR-042\", \"service_name\": \"profile-store\", \"merged_at\": \"2026-02-10T09:00:00+00:00\", \"summary\": \"timeout_sec = 61; merged and deployed. Previous value 61.\"}]",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"answered\", \"value\": 61, \"cites\": [\"NOTION-TR-042\", \"PR-TR-042\"], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "oracle_optimal_steps": 2,
  "param_name": "timeout_sec",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "What is profile-store timeout_sec now? Verify the runbook using github-mcp.",
      "role": "user"
    }
  ],
  "question": "What is profile-store timeout_sec now? Verify the runbook using github-mcp.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "profile-store",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0013-en",
  "world_split": "train"
}
```

## Sample 2 — source line 59

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0014",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "NOTION-TR-049",
    "SLACK-TR-049"
  ],
  "gold_value": 5,
  "incident_id": null,
  "kind": "consistent",
  "language": "hinglish",
  "messages": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Bhai, email-relay ka current max_retries kya hai? Notion aur slack-mcp check karo.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"notion-mcp\", \"tool\": \"search_notion\", \"arguments\": {\"query\": \"email-relay max_retries\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"page_id\": \"NOTION-TR-049\", \"title\": \"email-relay max_retries\", \"updated_at\": \"2026-02-10T09:00:00+00:00\", \"snippet\": \"email-relay max_retries = 5. Documented configuration at publication. Later deployment records may supersede this runbook.\"}]",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"slack-mcp\", \"tool\": \"search_slack\", \"arguments\": {\"query\": \"email-relay max_retries\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"msg_id\": \"SLACK-TR-049\", \"channel\": \"#deployments\", \"posted_at\": \"2026-02-10T09:00:00+00:00\", \"text\": \"email-relay max_retries = 5; deployment confirmed. Previous value 5.\"}]",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"answered\", \"value\": 5, \"cites\": [\"NOTION-TR-049\", \"SLACK-TR-049\"], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "oracle_optimal_steps": 2,
  "param_name": "max_retries",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Bhai, email-relay ka current max_retries kya hai? Notion aur slack-mcp check karo.",
      "role": "user"
    }
  ],
  "question": "Bhai, email-relay ka current max_retries kya hai? Notion aur slack-mcp check karo.",
  "required_mcps": [
    "notion-mcp",
    "slack-mcp"
  ],
  "service_name": "email-relay",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0014-hinglish",
  "world_split": "train"
}
```

## Sample 3 — source line 85

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "github-mcp"
  ],
  "case_id": "train-0021",
  "distractor_mcps": [],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TR-21"
  ],
  "gold_value": 66.0,
  "incident_id": "INC-TR-21",
  "kind": "incident",
  "language": "en",
  "messages": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "For incident INC-TR-21, use db-mcp and time-mcp to find elapsed hours, then math-mcp to calculate elapsed hours times penalty_rate_per_hour. Give the total penalty.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"db-mcp\", \"tool\": \"query_db\", \"arguments\": {\"sql\": \"SELECT * FROM production_incidents WHERE incident_id = 'INC-TR-21'\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: {\"rows\": [{\"incident_id\": \"INC-TR-21\", \"service_name\": \"notification-hub\", \"started_at\": \"2026-10-01T00:00:00+00:00\", \"resolved_at\": \"2026-10-01T06:00:00+00:00\", \"root_cause_pr\": \"PR-TR-126\", \"penalty_rate_per_hour\": 11.0, \"weight_kg\": 21.0}]}",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"time-mcp\", \"tool\": \"hours_between\", \"arguments\": {\"start_iso\": \"2026-10-01T00:00:00+00:00\", \"end_iso\": \"2026-10-01T06:00:00+00:00\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 6.0",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"math-mcp\", \"tool\": \"calculate\", \"arguments\": {\"expression\": \"6.0 * 11.0\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 66.0",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"answered\", \"value\": 66.0, \"cites\": [\"INC-TR-21\"], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "oracle_optimal_steps": 3,
  "param_name": "circuit_breaker_pct",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "For incident INC-TR-21, use db-mcp and time-mcp to find elapsed hours, then math-mcp to calculate elapsed hours times penalty_rate_per_hour. Give the total penalty.",
      "role": "user"
    }
  ],
  "question": "For incident INC-TR-21, use db-mcp and time-mcp to find elapsed hours, then math-mcp to calculate elapsed hours times penalty_rate_per_hour. Give the total penalty.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "session-cache",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0021-en",
  "world_split": "train"
}
```

## Sample 4 — source line 124

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp",
    "github-mcp"
  ],
  "case_id": "train-0030",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TR-30"
  ],
  "gold_value": 33.0,
  "incident_id": "INC-TR-30",
  "kind": "incident",
  "language": "te",
  "messages": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Sanghatana INC-TR-30 vivaraalu db-mcp lo choodu, time-mcp tho gantalu lekkinchu, math-mcp tho gantalu guninchu penalty_rate_per_hour; mottham penalty cheppu.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"db-mcp\", \"tool\": \"query_db\", \"arguments\": {\"sql\": \"SELECT * FROM production_incidents WHERE incident_id = 'INC-TR-30'\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: {\"rows\": [{\"incident_id\": \"INC-TR-30\", \"service_name\": \"payment-worker\", \"started_at\": \"2026-10-01T00:00:00+00:00\", \"resolved_at\": \"2026-10-01T03:00:00+00:00\", \"root_cause_pr\": \"PR-TR-180\", \"penalty_rate_per_hour\": 11.0, \"weight_kg\": 21.0}]}",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"time-mcp\", \"tool\": \"hours_between\", \"arguments\": {\"start_iso\": \"2026-10-01T00:00:00+00:00\", \"end_iso\": \"2026-10-01T03:00:00+00:00\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 3.0",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"math-mcp\", \"tool\": \"calculate\", \"arguments\": {\"expression\": \"3.0 * 11.0\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 33.0",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"answered\", \"value\": 33.0, \"cites\": [\"INC-TR-30\"], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "oracle_optimal_steps": 3,
  "param_name": "max_retries",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Sanghatana INC-TR-30 vivaraalu db-mcp lo choodu, time-mcp tho gantalu lekkinchu, math-mcp tho gantalu guninchu penalty_rate_per_hour; mottham penalty cheppu.",
      "role": "user"
    }
  ],
  "question": "Sanghatana INC-TR-30 vivaraalu db-mcp lo choodu, time-mcp tho gantalu lekkinchu, math-mcp tho gantalu guninchu penalty_rate_per_hour; mottham penalty cheppu.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "checkout-api",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0030-te",
  "world_split": "train"
}
```

## Sample 5 — source line 130

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0032",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "answered",
  "gold_cites": [
    "INC-TR-32"
  ],
  "gold_value": 99.0,
  "incident_id": "INC-TR-32",
  "kind": "incident",
  "language": "hi",
  "messages": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Ghatna INC-TR-32 ke liye db-mcp tatha time-mcp se beetey ghante nikaaliye, phir math-mcp se ghante guna penalty_rate_per_hour karke kul jurmaana bataaiye.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"db-mcp\", \"tool\": \"query_db\", \"arguments\": {\"sql\": \"SELECT * FROM production_incidents WHERE incident_id = 'INC-TR-32'\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: {\"rows\": [{\"incident_id\": \"INC-TR-32\", \"service_name\": \"profile-store\", \"started_at\": \"2026-10-01T00:00:00+00:00\", \"resolved_at\": \"2026-10-01T09:00:00+00:00\", \"root_cause_pr\": \"PR-TR-192\", \"penalty_rate_per_hour\": 11.0, \"weight_kg\": 21.0}]}",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"time-mcp\", \"tool\": \"hours_between\", \"arguments\": {\"start_iso\": \"2026-10-01T00:00:00+00:00\", \"end_iso\": \"2026-10-01T09:00:00+00:00\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 9.0",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"math-mcp\", \"tool\": \"calculate\", \"arguments\": {\"expression\": \"9.0 * 11.0\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: 99.0",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"answered\", \"value\": 99.0, \"cites\": [\"INC-TR-32\"], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "oracle_optimal_steps": 3,
  "param_name": "sla_hours",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Ghatna INC-TR-32 ke liye db-mcp tatha time-mcp se beetey ghante nikaaliye, phir math-mcp se ghante guna penalty_rate_per_hour karke kul jurmaana bataaiye.",
      "role": "user"
    }
  ],
  "question": "Ghatna INC-TR-32 ke liye db-mcp tatha time-mcp se beetey ghante nikaaliye, phir math-mcp se ghante guna penalty_rate_per_hour karke kul jurmaana bataaiye.",
  "required_mcps": [
    "db-mcp",
    "time-mcp",
    "math-mcp"
  ],
  "service_name": "checkout-api",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0032-hi",
  "world_split": "train"
}
```

## Sample 6 — source line 148

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp",
    "slack-mcp"
  ],
  "case_id": "train-0036",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-TR-052",
    "PR-TR-052"
  ],
  "gold_value": 21,
  "incident_id": null,
  "kind": "conflict",
  "language": "te",
  "messages": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "email-relay ki ippudu sla_hours entha? Runbook ni github-mcp tho sarichoodu.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"notion-mcp\", \"tool\": \"search_notion\", \"arguments\": {\"query\": \"email-relay sla_hours\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"page_id\": \"NOTION-TR-052\", \"title\": \"email-relay sla_hours\", \"updated_at\": \"2026-02-10T09:00:00+00:00\", \"snippet\": \"email-relay sla_hours = 17. Documented configuration at publication. Later deployment records may supersede this runbook.\"}]",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"github-mcp\", \"tool\": \"search_github_prs\", \"arguments\": {\"query\": \"email-relay sla_hours\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"pr_id\": \"PR-TR-052\", \"service_name\": \"email-relay\", \"merged_at\": \"2026-09-18T09:00:00+00:00\", \"summary\": \"sla_hours = 21; merged and deployed. Previous value 17.\"}]",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 21, \"cites\": [\"NOTION-TR-052\", \"PR-TR-052\"], \"stale_source\": \"NOTION-TR-052\"}</final_answer>",
      "role": "assistant"
    }
  ],
  "oracle_optimal_steps": 2,
  "param_name": "sla_hours",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "email-relay ki ippudu sla_hours entha? Runbook ni github-mcp tho sarichoodu.",
      "role": "user"
    }
  ],
  "question": "email-relay ki ippudu sla_hours entha? Runbook ni github-mcp tho sarichoodu.",
  "required_mcps": [
    "notion-mcp",
    "github-mcp"
  ],
  "service_name": "email-relay",
  "source_server": "github-mcp",
  "stale_doc_id": "NOTION-TR-052",
  "stale_trap_value": 17,
  "task_id": "train-0036-te",
  "world_split": "train"
}
```

## Sample 7 — source line 154

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0038",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "conflict_resolved",
  "gold_cites": [
    "NOTION-TR-055",
    "SLACK-TR-055"
  ],
  "gold_value": 9,
  "incident_id": null,
  "kind": "conflict",
  "language": "hi",
  "messages": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "inventory-sync ka vartamaan max_retries bataiye. Dastavez aur slack-mcp se pushti kijiye.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"notion-mcp\", \"tool\": \"search_notion\", \"arguments\": {\"query\": \"inventory-sync max_retries\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"page_id\": \"NOTION-TR-055\", \"title\": \"inventory-sync max_retries\", \"updated_at\": \"2026-02-10T09:00:00+00:00\", \"snippet\": \"inventory-sync max_retries = 7. Documented configuration at publication. Later deployment records may supersede this runbook.\"}]",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"slack-mcp\", \"tool\": \"search_slack\", \"arguments\": {\"query\": \"inventory-sync max_retries\"}}</tool_call>",
      "role": "assistant"
    },
    {
      "content": "Tool result: [{\"msg_id\": \"SLACK-TR-055\", \"channel\": \"#deployments\", \"posted_at\": \"2026-09-18T09:00:00+00:00\", \"text\": \"inventory-sync max_retries = 9; deployment confirmed. Previous value 7.\"}]",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 9, \"cites\": [\"NOTION-TR-055\", \"SLACK-TR-055\"], \"stale_source\": \"NOTION-TR-055\"}</final_answer>",
      "role": "assistant"
    }
  ],
  "oracle_optimal_steps": 2,
  "param_name": "max_retries",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "inventory-sync ka vartamaan max_retries bataiye. Dastavez aur slack-mcp se pushti kijiye.",
      "role": "user"
    }
  ],
  "question": "inventory-sync ka vartamaan max_retries bataiye. Dastavez aur slack-mcp se pushti kijiye.",
  "required_mcps": [
    "notion-mcp",
    "slack-mcp"
  ],
  "service_name": "inventory-sync",
  "source_server": "slack-mcp",
  "stale_doc_id": "NOTION-TR-055",
  "stale_trap_value": 7,
  "task_id": "train-0038-hi",
  "world_split": "train"
}
```

## Sample 8 — source line 345

```json
{
  "active_mcps": [
    "notion-mcp",
    "slack-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0086",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "en",
  "messages": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Read metrics-agent batch_size_mb from db-mcp only. If db-mcp is unavailable or this service is absent, abstain.",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "oracle_optimal_steps": 0,
  "param_name": "batch_size_mb",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "Read metrics-agent batch_size_mb from db-mcp only. If db-mcp is unavailable or this service is absent, abstain.",
      "role": "user"
    }
  ],
  "question": "Read metrics-agent batch_size_mb from db-mcp only. If db-mcp is unavailable or this service is absent, abstain.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "metrics-agent",
  "source_server": "slack-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0086-en",
  "world_split": "train"
}
```

## Sample 9 — source line 352

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "db-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "slack-mcp"
  ],
  "case_id": "train-0087",
  "distractor_mcps": [],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "te",
  "messages": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "unknown-train-service-87 ki sla_hours db-mcp nunche teesuko. Server lekapoyina seva dorakakapoyina samaadhaanam ivvaku.",
      "role": "user"
    },
    {
      "content": "<tool_call>{\"server\": \"db-mcp\", \"tool\": \"query_db\", \"arguments\": {\"sql\": \"SELECT * FROM microservices WHERE service_name = 'unknown-train-service-87'\"}}</tool_call>",
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
  "oracle_optimal_steps": 1,
  "param_name": "sla_hours",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"query_db\",\"arguments\":{\"sql\":\"string\"}},{\"server\":\"db-mcp\",\"tool\":\"inspect_schema\",\"arguments\":{}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"slack-mcp\",\"tool\":\"search_slack\",\"arguments\":{\"query\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "unknown-train-service-87 ki sla_hours db-mcp nunche teesuko. Server lekapoyina seva dorakakapoyina samaadhaanam ivvaku.",
      "role": "user"
    }
  ],
  "question": "unknown-train-service-87 ki sla_hours db-mcp nunche teesuko. Server lekapoyina seva dorakakapoyina samaadhaanam ivvaku.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "unknown-train-service-87",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0087-te",
  "world_split": "train"
}
```

## Sample 10 — source line 379

```json
{
  "active_mcps": [
    "notion-mcp",
    "github-mcp",
    "time-mcp",
    "unit-converter-mcp",
    "math-mcp",
    "weather-mcp",
    "calendar-mcp"
  ],
  "case_id": "train-0094",
  "distractor_mcps": [
    "weather-mcp",
    "calendar-mcp"
  ],
  "expected_status": "abstain",
  "gold_cites": [],
  "gold_value": null,
  "incident_id": null,
  "kind": "abstain",
  "language": "hinglish",
  "messages": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "media-worker ka rate_limit_rpm DB se hi do. db-mcp off ho ya service missing ho toh abstain karo.",
      "role": "user"
    },
    {
      "content": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
      "role": "assistant"
    }
  ],
  "oracle_optimal_steps": 0,
  "param_name": "rate_limit_rpm",
  "prompt": [
    {
      "content": "You are an enterprise configuration assistant. Use only the active tools and evidence returned in this conversation. A runbook may be stale: compare the documented setting with the requested deployment source. Use timestamps and current production evidence. Abstain when the entity does not exist or an explicitly required server is unavailable. Output exactly one turn at a time, with no extra text:\n<tool_call>{\"server\":\"server-name\",\"tool\":\"tool-name\",\"arguments\":{}}</tool_call>\nor <final_answer>{\"status\":\"answered|conflict_resolved|abstain\",\"value\":\"one exact value or null\",\"cites\":[\"retrieved evidence IDs\"],\"stale_source\":null}</final_answer>\nFor conflict_resolved, stale_source must be the stale runbook ID. For abstain, value must be JSON null and cites may be empty. Do not invent IDs. Database schema: microservices(service_name, owner_handle, timeout_sec, max_retries, rate_limit_rpm, batch_size_mb, sla_hours, circuit_breaker_pct, updated_at, last_pr, evidence_id); production_incidents(incident_id, service_name, started_at, resolved_at, root_cause_pr, penalty_rate_per_hour, weight_kg). query_db accepts read-only SELECT. Call tools until you can answer. Active tool schemas:\n[{\"server\":\"notion-mcp\",\"tool\":\"search_notion\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"github-mcp\",\"tool\":\"search_github_prs\",\"arguments\":{\"query\":\"string\"}},{\"server\":\"time-mcp\",\"tool\":\"hours_between\",\"arguments\":{\"start_iso\":\"string\",\"end_iso\":\"string\"}},{\"server\":\"unit-converter-mcp\",\"tool\":\"convert_unit\",\"arguments\":{\"value\":\"number\",\"from_unit\":\"string\",\"to_unit\":\"string\"}},{\"server\":\"math-mcp\",\"tool\":\"calculate\",\"arguments\":{\"expression\":\"string\"}},{\"server\":\"weather-mcp\",\"tool\":\"get_weather\",\"arguments\":{\"city\":\"string\"}},{\"server\":\"calendar-mcp\",\"tool\":\"list_meetings\",\"arguments\":{\"date\":\"string\"}}]",
      "role": "system"
    },
    {
      "content": "media-worker ka rate_limit_rpm DB se hi do. db-mcp off ho ya service missing ho toh abstain karo.",
      "role": "user"
    }
  ],
  "question": "media-worker ka rate_limit_rpm DB se hi do. db-mcp off ho ya service missing ho toh abstain karo.",
  "required_mcps": [
    "db-mcp"
  ],
  "service_name": "media-worker",
  "source_server": "github-mcp",
  "stale_doc_id": null,
  "stale_trap_value": null,
  "task_id": "train-0094-hinglish",
  "world_split": "train"
}
```

---

# File: `train_sft_agenttune_trajectories.jsonl`

Source SHA-256: `237b733ac831be5ecedbc505f38868b039dc6a3de548304a558d943af41c05a4`

10 complete records selected from 400 source rows.

## Sample 1 — source line 15

```json
{
  "final_response": "<final_answer>{\"status\": \"answered\", \"value\": 17, \"cites\": [\"NOTION-TR-016\", \"PR-TR-016\"], \"stale_source\": null}</final_answer>",
  "metadata": {
    "language": "hinglish",
    "task_id": "train-0003-hinglish",
    "world_split": "train"
  },
  "reward": 0.0,
  "steps": [
    {
      "action": {
        "arguments": {
          "query": "cart-ledger sla_hours"
        },
        "name": "notion-mcp__search_notion"
      },
      "observation": "[{\"page_id\": \"NOTION-TR-016\", \"title\": \"cart-ledger sla_hours\", \"updated_at\": \"2026-02-10T09:00:00+00:00\", \"snippet\": \"cart-ledger sla_hours = 17. Documented configuration at publication. Later deployment records may supersede this runbook.\"}]",
      "reward": null,
      "state": "Bhai, cart-ledger ka current sla_hours kya hai? Notion aur github-mcp check karo.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "query": "cart-ledger sla_hours"
        },
        "name": "github-mcp__search_github_prs"
      },
      "observation": "[{\"pr_id\": \"PR-TR-016\", \"service_name\": \"cart-ledger\", \"merged_at\": \"2026-02-10T09:00:00+00:00\", \"summary\": \"sla_hours = 17; merged and deployed. Previous value 17.\"}]",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"answered\", \"value\": 17, \"cites\": [\"NOTION-TR-016\", \"PR-TR-016\"], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 2,
      "thought": null
    }
  ],
  "task": "Bhai, cart-ledger ka current sla_hours kya hai? Notion aur github-mcp check karo.",
  "trajectory_id": "train-0003-hinglish"
}
```

## Sample 2 — source line 21

```json
{
  "final_response": "<final_answer>{\"status\": \"answered\", \"value\": 41, \"cites\": [\"NOTION-TR-018\", \"PR-TR-018\"], \"stale_source\": null}</final_answer>",
  "metadata": {
    "language": "en",
    "task_id": "train-0005-en",
    "world_split": "train"
  },
  "reward": 0.0,
  "steps": [
    {
      "action": {
        "arguments": {
          "query": "webhook-dispatcher timeout_sec"
        },
        "name": "notion-mcp__search_notion"
      },
      "observation": "[{\"page_id\": \"NOTION-TR-018\", \"title\": \"webhook-dispatcher timeout_sec\", \"updated_at\": \"2026-02-10T09:00:00+00:00\", \"snippet\": \"webhook-dispatcher timeout_sec = 41. Documented configuration at publication. Later deployment records may supersede this runbook.\"}]",
      "reward": null,
      "state": "What is webhook-dispatcher timeout_sec now? Verify the runbook using github-mcp.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "query": "webhook-dispatcher timeout_sec"
        },
        "name": "github-mcp__search_github_prs"
      },
      "observation": "[{\"pr_id\": \"PR-TR-018\", \"service_name\": \"webhook-dispatcher\", \"merged_at\": \"2026-02-10T09:00:00+00:00\", \"summary\": \"timeout_sec = 41; merged and deployed. Previous value 41.\"}]",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"answered\", \"value\": 41, \"cites\": [\"NOTION-TR-018\", \"PR-TR-018\"], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 2,
      "thought": null
    }
  ],
  "task": "What is webhook-dispatcher timeout_sec now? Verify the runbook using github-mcp.",
  "trajectory_id": "train-0005-en"
}
```

## Sample 3 — source line 100

```json
{
  "final_response": "<final_answer>{\"status\": \"answered\", \"value\": 165.0, \"cites\": [\"INC-TR-24\"], \"stale_source\": null}</final_answer>",
  "metadata": {
    "language": "te",
    "task_id": "train-0024-te",
    "world_split": "train"
  },
  "reward": 0.0,
  "steps": [
    {
      "action": {
        "arguments": {
          "sql": "SELECT * FROM production_incidents WHERE incident_id = 'INC-TR-24'"
        },
        "name": "db-mcp__query_db"
      },
      "observation": "{\"rows\": [{\"incident_id\": \"INC-TR-24\", \"service_name\": \"identity-broker\", \"started_at\": \"2026-10-01T00:00:00+00:00\", \"resolved_at\": \"2026-10-01T15:00:00+00:00\", \"root_cause_pr\": \"PR-TR-144\", \"penalty_rate_per_hour\": 11.0, \"weight_kg\": 21.0}]}",
      "reward": null,
      "state": "Sanghatana INC-TR-24 vivaraalu db-mcp lo choodu, time-mcp tho gantalu lekkinchu, math-mcp tho gantalu guninchu penalty_rate_per_hour; mottham penalty cheppu.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "end_iso": "2026-10-01T15:00:00+00:00",
          "start_iso": "2026-10-01T00:00:00+00:00"
        },
        "name": "time-mcp__hours_between"
      },
      "observation": "15.0",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "expression": "15.0 * 11.0"
        },
        "name": "math-mcp__calculate"
      },
      "observation": "165.0",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 2,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"answered\", \"value\": 165.0, \"cites\": [\"INC-TR-24\"], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 3,
      "thought": null
    }
  ],
  "task": "Sanghatana INC-TR-24 vivaraalu db-mcp lo choodu, time-mcp tho gantalu lekkinchu, math-mcp tho gantalu guninchu penalty_rate_per_hour; mottham penalty cheppu.",
  "trajectory_id": "train-0024-te"
}
```

## Sample 4 — source line 105

```json
{
  "final_response": "<final_answer>{\"status\": \"answered\", \"value\": 66.0, \"cites\": [\"INC-TR-26\"], \"stale_source\": null}</final_answer>",
  "metadata": {
    "language": "en",
    "task_id": "train-0026-en",
    "world_split": "train"
  },
  "reward": 0.0,
  "steps": [
    {
      "action": {
        "arguments": {
          "sql": "SELECT * FROM production_incidents WHERE incident_id = 'INC-TR-26'"
        },
        "name": "db-mcp__query_db"
      },
      "observation": "{\"rows\": [{\"incident_id\": \"INC-TR-26\", \"service_name\": \"auth-proxy\", \"started_at\": \"2026-10-01T00:00:00+00:00\", \"resolved_at\": \"2026-10-01T06:00:00+00:00\", \"root_cause_pr\": \"PR-TR-156\", \"penalty_rate_per_hour\": 11.0, \"weight_kg\": 21.0}]}",
      "reward": null,
      "state": "For incident INC-TR-26, use db-mcp and time-mcp to find elapsed hours, then math-mcp to calculate elapsed hours times penalty_rate_per_hour. Give the total penalty.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "end_iso": "2026-10-01T06:00:00+00:00",
          "start_iso": "2026-10-01T00:00:00+00:00"
        },
        "name": "time-mcp__hours_between"
      },
      "observation": "6.0",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "expression": "6.0 * 11.0"
        },
        "name": "math-mcp__calculate"
      },
      "observation": "66.0",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 2,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"answered\", \"value\": 66.0, \"cites\": [\"INC-TR-26\"], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 3,
      "thought": null
    }
  ],
  "task": "For incident INC-TR-26, use db-mcp and time-mcp to find elapsed hours, then math-mcp to calculate elapsed hours times penalty_rate_per_hour. Give the total penalty.",
  "trajectory_id": "train-0026-en"
}
```

## Sample 5 — source line 118

```json
{
  "final_response": "<final_answer>{\"status\": \"answered\", \"value\": 165.0, \"cites\": [\"INC-TR-29\"], \"stale_source\": null}</final_answer>",
  "metadata": {
    "language": "hi",
    "task_id": "train-0029-hi",
    "world_split": "train"
  },
  "reward": 0.0,
  "steps": [
    {
      "action": {
        "arguments": {
          "sql": "SELECT * FROM production_incidents WHERE incident_id = 'INC-TR-29'"
        },
        "name": "db-mcp__query_db"
      },
      "observation": "{\"rows\": [{\"incident_id\": \"INC-TR-29\", \"service_name\": \"order-router\", \"started_at\": \"2026-10-01T00:00:00+00:00\", \"resolved_at\": \"2026-10-01T15:00:00+00:00\", \"root_cause_pr\": \"PR-TR-174\", \"penalty_rate_per_hour\": 11.0, \"weight_kg\": 21.0}]}",
      "reward": null,
      "state": "Ghatna INC-TR-29 ke liye db-mcp tatha time-mcp se beetey ghante nikaaliye, phir math-mcp se ghante guna penalty_rate_per_hour karke kul jurmaana bataaiye.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "end_iso": "2026-10-01T15:00:00+00:00",
          "start_iso": "2026-10-01T00:00:00+00:00"
        },
        "name": "time-mcp__hours_between"
      },
      "observation": "15.0",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "expression": "15.0 * 11.0"
        },
        "name": "math-mcp__calculate"
      },
      "observation": "165.0",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 2,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"answered\", \"value\": 165.0, \"cites\": [\"INC-TR-29\"], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 3,
      "thought": null
    }
  ],
  "task": "Ghatna INC-TR-29 ke liye db-mcp tatha time-mcp se beetey ghante nikaaliye, phir math-mcp se ghante guna penalty_rate_per_hour karke kul jurmaana bataaiye.",
  "trajectory_id": "train-0029-hi"
}
```

## Sample 6 — source line 248

```json
{
  "final_response": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 121, \"cites\": [\"NOTION-TR-099\", \"SLACK-TR-099\"], \"stale_source\": \"NOTION-TR-099\"}</final_answer>",
  "metadata": {
    "language": "te",
    "task_id": "train-0061-te",
    "world_split": "train"
  },
  "reward": 0.0,
  "steps": [
    {
      "action": {
        "arguments": {
          "query": "coupon-engine batch_size_mb"
        },
        "name": "notion-mcp__search_notion"
      },
      "observation": "[{\"page_id\": \"NOTION-TR-099\", \"title\": \"coupon-engine batch_size_mb\", \"updated_at\": \"2026-02-10T09:00:00+00:00\", \"snippet\": \"coupon-engine batch_size_mb = 81. Documented configuration at publication. Later deployment records may supersede this runbook.\"}]",
      "reward": null,
      "state": "coupon-engine yokka batch_size_mb cheppu; patram mariyu slack-mcp rendu choodu.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "query": "coupon-engine batch_size_mb"
        },
        "name": "slack-mcp__search_slack"
      },
      "observation": "[{\"msg_id\": \"SLACK-TR-099\", \"channel\": \"#deployments\", \"posted_at\": \"2026-09-18T09:00:00+00:00\", \"text\": \"coupon-engine batch_size_mb = 121; deployment confirmed. Previous value 81.\"}]",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 121, \"cites\": [\"NOTION-TR-099\", \"SLACK-TR-099\"], \"stale_source\": \"NOTION-TR-099\"}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 2,
      "thought": null
    }
  ],
  "task": "coupon-engine yokka batch_size_mb cheppu; patram mariyu slack-mcp rendu choodu.",
  "trajectory_id": "train-0061-te"
}
```

## Sample 7 — source line 278

```json
{
  "final_response": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 81, \"cites\": [\"NOTION-TR-111\", \"SLACK-TR-111\"], \"stale_source\": \"NOTION-TR-111\"}</final_answer>",
  "metadata": {
    "language": "hi",
    "task_id": "train-0069-hi",
    "world_split": "train"
  },
  "reward": 0.0,
  "steps": [
    {
      "action": {
        "arguments": {
          "query": "shipment-router batch_size_mb"
        },
        "name": "notion-mcp__search_notion"
      },
      "observation": "[{\"page_id\": \"NOTION-TR-111\", \"title\": \"shipment-router batch_size_mb\", \"updated_at\": \"2026-02-10T09:00:00+00:00\", \"snippet\": \"shipment-router batch_size_mb = 41. Documented configuration at publication. Later deployment records may supersede this runbook.\"}]",
      "reward": null,
      "state": "Kripya shipment-router ke batch_size_mb ki jaanch dastavez tatha slack-mcp se kijiye.",
      "step_number": 0,
      "thought": null
    },
    {
      "action": {
        "arguments": {
          "query": "shipment-router batch_size_mb"
        },
        "name": "slack-mcp__search_slack"
      },
      "observation": "[{\"msg_id\": \"SLACK-TR-111\", \"channel\": \"#deployments\", \"posted_at\": \"2026-09-18T09:00:00+00:00\", \"text\": \"shipment-router batch_size_mb = 81; deployment confirmed. Previous value 41.\"}]",
      "reward": null,
      "state": "Previous tool observation",
      "step_number": 1,
      "thought": null
    },
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"conflict_resolved\", \"value\": 81, \"cites\": [\"NOTION-TR-111\", \"SLACK-TR-111\"], \"stale_source\": \"NOTION-TR-111\"}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 2,
      "thought": null
    }
  ],
  "task": "Kripya shipment-router ke batch_size_mb ki jaanch dastavez tatha slack-mcp se kijiye.",
  "trajectory_id": "train-0069-hi"
}
```

## Sample 8 — source line 353

```json
{
  "final_response": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
  "metadata": {
    "language": "en",
    "task_id": "train-0088-en",
    "world_split": "train"
  },
  "reward": 0.0,
  "steps": [
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 0,
      "thought": null
    }
  ],
  "task": "Read billing-api batch_size_mb from db-mcp only. If db-mcp is unavailable or this service is absent, abstain.",
  "trajectory_id": "train-0088-en"
}
```

## Sample 9 — source line 356

```json
{
  "final_response": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
  "metadata": {
    "language": "te",
    "task_id": "train-0088-te",
    "world_split": "train"
  },
  "reward": 0.0,
  "steps": [
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 0,
      "thought": null
    }
  ],
  "task": "billing-api ki batch_size_mb db-mcp nunche teesuko. Server lekapoyina seva dorakakapoyina samaadhaanam ivvaku.",
  "trajectory_id": "train-0088-te"
}
```

## Sample 10 — source line 363

```json
{
  "final_response": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
  "metadata": {
    "language": "hinglish",
    "task_id": "train-0090-hinglish",
    "world_split": "train"
  },
  "reward": 0.0,
  "steps": [
    {
      "action": {},
      "observation": "<final_answer>{\"status\": \"abstain\", \"value\": null, \"cites\": [], \"stale_source\": null}</final_answer>",
      "reward": null,
      "state": "Final synthesis",
      "step_number": 0,
      "thought": null
    }
  ],
  "task": "checkout-api ka max_retries DB se hi do. db-mcp off ho ya service missing ho toh abstain karo.",
  "trajectory_id": "train-0090-hinglish"
}
```

---

# File: `world_repo_style.json`

Source SHA-256: `986244ef0d7c7f7755d67bfcb461ec5bbbf66856d2328e4727c64b455717830f`

Metadata plus up to 10 original entries per collection.

```json
{
  "employees": [
    "@oss_fixture_00",
    "@oss_fixture_04",
    "@oss_fixture_09",
    "@oss_fixture_13",
    "@oss_fixture_17",
    "@oss_fixture_22",
    "@oss_fixture_26",
    "@oss_fixture_30",
    "@oss_fixture_35",
    "@oss_fixture_39"
  ],
  "facts": [
    {
      "current_value": 10001,
      "db_id": "DB-REALSTYLE-00",
      "initial_date": "2025-01-01T00:00:00+00:00",
      "initial_value": 10000,
      "notion_page_id": "NOTION-REALSTYLE-00",
      "owner_handle": "@oss_fixture_00",
      "param_name": "timeout_sec",
      "service_name": "fastapi-case-00",
      "source_id": "PR-REALSTYLE-00",
      "source_server": "github-mcp",
      "updated_date": "2026-01-01T00:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 20003,
      "db_id": "DB-REALSTYLE-03",
      "initial_date": "2025-01-01T00:00:00+00:00",
      "initial_value": 20003,
      "notion_page_id": "NOTION-REALSTYLE-03-max_retries",
      "owner_handle": "@oss_fixture_03",
      "param_name": "max_retries",
      "service_name": "fastapi-case-01",
      "source_id": "PR-REALSTYLE-03-max_retries",
      "source_server": "github-mcp",
      "updated_date": "2026-01-01T00:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 20006,
      "db_id": "DB-REALSTYLE-06",
      "initial_date": "2025-01-01T00:00:00+00:00",
      "initial_value": 20006,
      "notion_page_id": "NOTION-REALSTYLE-06-sla_hours",
      "owner_handle": "@oss_fixture_06",
      "param_name": "sla_hours",
      "service_name": "fastapi-case-02",
      "source_id": "PR-REALSTYLE-06-sla_hours",
      "source_server": "github-mcp",
      "updated_date": "2026-01-01T00:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 10021,
      "db_id": "DB-REALSTYLE-10",
      "initial_date": "2025-01-01T00:00:00+00:00",
      "initial_value": 10020,
      "notion_page_id": "NOTION-REALSTYLE-10",
      "owner_handle": "@oss_fixture_10",
      "param_name": "sla_hours",
      "service_name": "pydantic-case-03",
      "source_id": "PR-REALSTYLE-10",
      "source_server": "github-mcp",
      "updated_date": "2026-01-01T00:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 20013,
      "db_id": "DB-REALSTYLE-13",
      "initial_date": "2025-01-01T00:00:00+00:00",
      "initial_value": 20013,
      "notion_page_id": "NOTION-REALSTYLE-13-rate_limit_rpm",
      "owner_handle": "@oss_fixture_13",
      "param_name": "rate_limit_rpm",
      "service_name": "pydantic-case-04",
      "source_id": "PR-REALSTYLE-13-rate_limit_rpm",
      "source_server": "github-mcp",
      "updated_date": "2026-01-01T00:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 20016,
      "db_id": "DB-REALSTYLE-16",
      "initial_date": "2025-01-01T00:00:00+00:00",
      "initial_value": 20016,
      "notion_page_id": "NOTION-REALSTYLE-16-rate_limit_rpm",
      "owner_handle": "@oss_fixture_16",
      "param_name": "rate_limit_rpm",
      "service_name": "pydantic-case-05",
      "source_id": "PR-REALSTYLE-16-rate_limit_rpm",
      "source_server": "github-mcp",
      "updated_date": "2026-01-01T00:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 20019,
      "db_id": "DB-REALSTYLE-19",
      "initial_date": "2025-01-01T00:00:00+00:00",
      "initial_value": 20019,
      "notion_page_id": "NOTION-REALSTYLE-19-circuit_breaker_pct",
      "owner_handle": "@oss_fixture_19",
      "param_name": "circuit_breaker_pct",
      "service_name": "pydantic-case-06",
      "source_id": "PR-REALSTYLE-19-circuit_breaker_pct",
      "source_server": "github-mcp",
      "updated_date": "2026-01-01T00:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 20023,
      "db_id": "DB-REALSTYLE-23",
      "initial_date": "2025-01-01T00:00:00+00:00",
      "initial_value": 20023,
      "notion_page_id": "NOTION-REALSTYLE-23-timeout_sec",
      "owner_handle": "@oss_fixture_23",
      "param_name": "timeout_sec",
      "service_name": "litellm-case-07",
      "source_id": "PR-REALSTYLE-23-timeout_sec",
      "source_server": "github-mcp",
      "updated_date": "2026-01-01T00:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 20026,
      "db_id": "DB-REALSTYLE-26",
      "initial_date": "2025-01-01T00:00:00+00:00",
      "initial_value": 20026,
      "notion_page_id": "NOTION-REALSTYLE-26-batch_size_mb",
      "owner_handle": "@oss_fixture_26",
      "param_name": "batch_size_mb",
      "service_name": "litellm-case-08",
      "source_id": "PR-REALSTYLE-26-batch_size_mb",
      "source_server": "github-mcp",
      "updated_date": "2026-01-01T00:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 20029,
      "db_id": "DB-REALSTYLE-29",
      "initial_date": "2025-01-01T00:00:00+00:00",
      "initial_value": 20029,
      "notion_page_id": "NOTION-REALSTYLE-29-sla_hours",
      "owner_handle": "@oss_fixture_29",
      "param_name": "sla_hours",
      "service_name": "litellm-case-09",
      "source_id": "PR-REALSTYLE-29-sla_hours",
      "source_server": "github-mcp",
      "updated_date": "2026-01-01T00:00:00+00:00",
      "was_updated": false
    }
  ],
  "incidents": [],
  "provenance": {
    "case_count": 30,
    "kind": "constructed_oss_style",
    "verified_real_changes": false
  },
  "seed": 137,
  "services": [
    "fastapi-case-00",
    "fastapi-case-01",
    "fastapi-case-02",
    "pydantic-case-03",
    "pydantic-case-04",
    "pydantic-case-05",
    "pydantic-case-06",
    "litellm-case-07",
    "litellm-case-08",
    "litellm-case-09"
  ],
  "split": "repo_style"
}
```

---

# File: `world_test_synth.json`

Source SHA-256: `8917e2520ba04b2809c65004e45035507bca2efc56bd383089c13306fc10a544`

Metadata plus up to 10 original entries per collection.

```json
{
  "employees": [
    "@ts_engineer_00",
    "@ts_engineer_04",
    "@ts_engineer_09",
    "@ts_engineer_13",
    "@ts_engineer_17",
    "@ts_engineer_22",
    "@ts_engineer_26",
    "@ts_engineer_30",
    "@ts_engineer_35",
    "@ts_engineer_39"
  ],
  "facts": [
    {
      "current_value": 40,
      "db_id": "DB-TS-00",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 20,
      "notion_page_id": "NOTION-TS-000",
      "owner_handle": "@ts_engineer_00",
      "param_name": "timeout_sec",
      "service_name": "kyc-verifier",
      "source_id": "PR-TS-000",
      "source_server": "github-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 40,
      "db_id": "DB-TS-02",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 30,
      "notion_page_id": "NOTION-TS-017",
      "owner_handle": "@ts_engineer_02",
      "param_name": "circuit_breaker_pct",
      "service_name": "fraud-sentinel",
      "source_id": "SLACK-TS-017",
      "source_server": "slack-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 120,
      "db_id": "DB-TS-05",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 120,
      "notion_page_id": "NOTION-TS-033",
      "owner_handle": "@ts_engineer_05",
      "param_name": "batch_size_mb",
      "service_name": "payout-router",
      "source_id": "SLACK-TS-033",
      "source_server": "slack-mcp",
      "updated_date": "2026-02-10T09:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 800,
      "db_id": "DB-TS-08",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 800,
      "notion_page_id": "NOTION-TS-050",
      "owner_handle": "@ts_engineer_08",
      "param_name": "rate_limit_rpm",
      "service_name": "receipt-store",
      "source_id": "PR-TS-050",
      "source_server": "github-mcp",
      "updated_date": "2026-02-10T09:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 100,
      "db_id": "DB-TS-11",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 80,
      "notion_page_id": "NOTION-TS-066",
      "owner_handle": "@ts_engineer_11",
      "param_name": "timeout_sec",
      "service_name": "wallet-bridge",
      "source_id": "PR-TS-066",
      "source_server": "github-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 50,
      "db_id": "DB-TS-13",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 40,
      "notion_page_id": "NOTION-TS-083",
      "owner_handle": "@ts_engineer_13",
      "param_name": "circuit_breaker_pct",
      "service_name": "merchant-registry",
      "source_id": "SLACK-TS-083",
      "source_server": "slack-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 160,
      "db_id": "DB-TS-16",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 120,
      "notion_page_id": "NOTION-TS-099",
      "owner_handle": "@ts_engineer_16",
      "param_name": "batch_size_mb",
      "service_name": "remittance-api",
      "source_id": "SLACK-TS-099",
      "source_server": "slack-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 600,
      "db_id": "DB-TS-19",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 400,
      "notion_page_id": "NOTION-TS-116",
      "owner_handle": "@ts_engineer_19",
      "param_name": "rate_limit_rpm",
      "service_name": "compliance-gateway",
      "source_id": "PR-TS-116",
      "source_server": "github-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 60,
      "db_id": "DB-TS-22",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 40,
      "notion_page_id": "NOTION-TS-132",
      "owner_handle": "@ts_engineer_22",
      "param_name": "timeout_sec",
      "service_name": "sanctions-checker",
      "source_id": "PR-TS-132",
      "source_server": "github-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 50,
      "db_id": "DB-TS-24",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 40,
      "notion_page_id": "NOTION-TS-149",
      "owner_handle": "@ts_engineer_24",
      "param_name": "circuit_breaker_pct",
      "service_name": "ledger-exporter",
      "source_id": "SLACK-TS-149",
      "source_server": "slack-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    }
  ],
  "incidents": [
    {
      "incident_id": "INC-TS-00",
      "penalty_rate_per_hour": 14,
      "resolved_at": "2026-10-01T04:00:00+00:00",
      "root_cause_pr": "PR-TS-000",
      "service_name": "kyc-verifier",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 24
    },
    {
      "incident_id": "INC-TS-05",
      "penalty_rate_per_hour": 14,
      "resolved_at": "2026-10-01T04:00:00+00:00",
      "root_cause_pr": "PR-TS-030",
      "service_name": "payout-router",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 24
    },
    {
      "incident_id": "INC-TS-11",
      "penalty_rate_per_hour": 14,
      "resolved_at": "2026-10-01T08:00:00+00:00",
      "root_cause_pr": "PR-TS-066",
      "service_name": "wallet-bridge",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 24
    },
    {
      "incident_id": "INC-TS-16",
      "penalty_rate_per_hour": 14,
      "resolved_at": "2026-10-01T08:00:00+00:00",
      "root_cause_pr": "PR-TS-096",
      "service_name": "remittance-api",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 24
    },
    {
      "incident_id": "INC-TS-22",
      "penalty_rate_per_hour": 14,
      "resolved_at": "2026-10-01T12:00:00+00:00",
      "root_cause_pr": "PR-TS-132",
      "service_name": "sanctions-checker",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 24
    },
    {
      "incident_id": "INC-TS-27",
      "penalty_rate_per_hour": 14,
      "resolved_at": "2026-10-01T12:00:00+00:00",
      "root_cause_pr": "PR-TS-162",
      "service_name": "fraud-sentinel",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 24
    },
    {
      "incident_id": "INC-TS-33",
      "penalty_rate_per_hour": 14,
      "resolved_at": "2026-10-01T16:00:00+00:00",
      "root_cause_pr": "PR-TS-198",
      "service_name": "receipt-store",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 24
    },
    {
      "incident_id": "INC-TS-38",
      "penalty_rate_per_hour": 14,
      "resolved_at": "2026-10-01T16:00:00+00:00",
      "root_cause_pr": "PR-TS-228",
      "service_name": "merchant-registry",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 24
    },
    {
      "incident_id": "INC-TS-44",
      "penalty_rate_per_hour": 14,
      "resolved_at": "2026-10-01T20:00:00+00:00",
      "root_cause_pr": "PR-TS-264",
      "service_name": "compliance-gateway",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 24
    },
    {
      "incident_id": "INC-TS-49",
      "penalty_rate_per_hour": 14,
      "resolved_at": "2026-10-01T20:00:00+00:00",
      "root_cause_pr": "PR-TS-294",
      "service_name": "ledger-exporter",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 24
    }
  ],
  "seed": 99,
  "services": [
    "kyc-verifier",
    "invoice-mailer",
    "payout-router",
    "receipt-store",
    "wallet-bridge",
    "merchant-registry",
    "remittance-api",
    "compliance-gateway",
    "transfer-worker",
    "ledger-exporter"
  ],
  "split": "test_synth"
}
```

---

# File: `world_train.json`

Source SHA-256: `2f68a305b5eeb515442f6564a9fb2399b5f5291bd2172e4697d9b29a1594cf44`

Metadata plus up to 10 original entries per collection.

```json
{
  "employees": [
    "@tr_engineer_00",
    "@tr_engineer_04",
    "@tr_engineer_09",
    "@tr_engineer_13",
    "@tr_engineer_17",
    "@tr_engineer_22",
    "@tr_engineer_26",
    "@tr_engineer_30",
    "@tr_engineer_35",
    "@tr_engineer_39"
  ],
  "facts": [
    {
      "current_value": 61,
      "db_id": "DB-TR-00",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 61,
      "notion_page_id": "NOTION-TR-000",
      "owner_handle": "@tr_engineer_00",
      "param_name": "timeout_sec",
      "service_name": "upi-gateway",
      "source_id": "PR-TR-000",
      "source_server": "github-mcp",
      "updated_date": "2026-02-10T09:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 31,
      "db_id": "DB-TR-02",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 31,
      "notion_page_id": "NOTION-TR-017",
      "owner_handle": "@tr_engineer_02",
      "param_name": "circuit_breaker_pct",
      "service_name": "cart-ledger",
      "source_id": "SLACK-TR-017",
      "source_server": "slack-mcp",
      "updated_date": "2026-02-10T09:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 81,
      "db_id": "DB-TR-05",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 41,
      "notion_page_id": "NOTION-TR-033",
      "owner_handle": "@tr_engineer_05",
      "param_name": "batch_size_mb",
      "service_name": "payment-worker",
      "source_id": "SLACK-TR-033",
      "source_server": "slack-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 401,
      "db_id": "DB-TR-08",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 201,
      "notion_page_id": "NOTION-TR-050",
      "owner_handle": "@tr_engineer_08",
      "param_name": "rate_limit_rpm",
      "service_name": "email-relay",
      "source_id": "PR-TR-050",
      "source_server": "github-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 81,
      "db_id": "DB-TR-11",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 81,
      "notion_page_id": "NOTION-TR-066",
      "owner_handle": "@tr_engineer_11",
      "param_name": "timeout_sec",
      "service_name": "audit-stream",
      "source_id": "PR-TR-066",
      "source_server": "github-mcp",
      "updated_date": "2026-02-10T09:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 21,
      "db_id": "DB-TR-13",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 21,
      "notion_page_id": "NOTION-TR-083",
      "owner_handle": "@tr_engineer_13",
      "param_name": "circuit_breaker_pct",
      "service_name": "billing-api",
      "source_id": "SLACK-TR-083",
      "source_server": "slack-mcp",
      "updated_date": "2026-02-10T09:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 121,
      "db_id": "DB-TR-16",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 81,
      "notion_page_id": "NOTION-TR-099",
      "owner_handle": "@tr_engineer_16",
      "param_name": "batch_size_mb",
      "service_name": "coupon-engine",
      "source_id": "SLACK-TR-099",
      "source_server": "slack-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    },
    {
      "current_value": 401,
      "db_id": "DB-TR-19",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 401,
      "notion_page_id": "NOTION-TR-116",
      "owner_handle": "@tr_engineer_19",
      "param_name": "rate_limit_rpm",
      "service_name": "product-catalog",
      "source_id": "PR-TR-116",
      "source_server": "github-mcp",
      "updated_date": "2026-02-10T09:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 41,
      "db_id": "DB-TR-22",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 41,
      "notion_page_id": "NOTION-TR-132",
      "owner_handle": "@tr_engineer_22",
      "param_name": "timeout_sec",
      "service_name": "tax-engine",
      "source_id": "PR-TR-132",
      "source_server": "github-mcp",
      "updated_date": "2026-02-10T09:00:00+00:00",
      "was_updated": false
    },
    {
      "current_value": 31,
      "db_id": "DB-TR-24",
      "initial_date": "2026-02-10T09:00:00+00:00",
      "initial_value": 21,
      "notion_page_id": "NOTION-TR-149",
      "owner_handle": "@tr_engineer_24",
      "param_name": "circuit_breaker_pct",
      "service_name": "identity-broker",
      "source_id": "SLACK-TR-149",
      "source_server": "slack-mcp",
      "updated_date": "2026-09-18T09:00:00+00:00",
      "was_updated": true
    }
  ],
  "incidents": [
    {
      "incident_id": "INC-TR-00",
      "penalty_rate_per_hour": 11,
      "resolved_at": "2026-10-01T03:00:00+00:00",
      "root_cause_pr": "PR-TR-000",
      "service_name": "upi-gateway",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 21
    },
    {
      "incident_id": "INC-TR-05",
      "penalty_rate_per_hour": 11,
      "resolved_at": "2026-10-01T03:00:00+00:00",
      "root_cause_pr": "PR-TR-030",
      "service_name": "payment-worker",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 21
    },
    {
      "incident_id": "INC-TR-11",
      "penalty_rate_per_hour": 11,
      "resolved_at": "2026-10-01T06:00:00+00:00",
      "root_cause_pr": "PR-TR-066",
      "service_name": "audit-stream",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 21
    },
    {
      "incident_id": "INC-TR-16",
      "penalty_rate_per_hour": 11,
      "resolved_at": "2026-10-01T06:00:00+00:00",
      "root_cause_pr": "PR-TR-096",
      "service_name": "coupon-engine",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 21
    },
    {
      "incident_id": "INC-TR-22",
      "penalty_rate_per_hour": 11,
      "resolved_at": "2026-10-01T09:00:00+00:00",
      "root_cause_pr": "PR-TR-132",
      "service_name": "tax-engine",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 21
    },
    {
      "incident_id": "INC-TR-27",
      "penalty_rate_per_hour": 11,
      "resolved_at": "2026-10-01T09:00:00+00:00",
      "root_cause_pr": "PR-TR-162",
      "service_name": "cart-ledger",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 21
    },
    {
      "incident_id": "INC-TR-33",
      "penalty_rate_per_hour": 11,
      "resolved_at": "2026-10-01T12:00:00+00:00",
      "root_cause_pr": "PR-TR-198",
      "service_name": "email-relay",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 21
    },
    {
      "incident_id": "INC-TR-38",
      "penalty_rate_per_hour": 11,
      "resolved_at": "2026-10-01T12:00:00+00:00",
      "root_cause_pr": "PR-TR-228",
      "service_name": "billing-api",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 21
    },
    {
      "incident_id": "INC-TR-44",
      "penalty_rate_per_hour": 11,
      "resolved_at": "2026-10-01T15:00:00+00:00",
      "root_cause_pr": "PR-TR-264",
      "service_name": "product-catalog",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 21
    },
    {
      "incident_id": "INC-TR-49",
      "penalty_rate_per_hour": 11,
      "resolved_at": "2026-10-01T15:00:00+00:00",
      "root_cause_pr": "PR-TR-294",
      "service_name": "identity-broker",
      "started_at": "2026-10-01T00:00:00+00:00",
      "weight_kg": 21
    }
  ],
  "seed": 42,
  "services": [
    "upi-gateway",
    "webhook-dispatcher",
    "payment-worker",
    "email-relay",
    "audit-stream",
    "billing-api",
    "coupon-engine",
    "product-catalog",
    "notification-hub",
    "identity-broker"
  ],
  "split": "train"
}
```

