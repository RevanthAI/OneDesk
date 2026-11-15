## Descriptive output diagnostics

These diagnostics inspect parseable final JSON even when required fields are missing. They do not repair or replace strict headline outcomes. Raw value correctness ignores status and format. Counts are over all questions.

| Count | Synthetic | OSS-style |
|---|---:|---:|
| items | 400 | 100 |
| parseable_final_json | 347 | 86 |
| wrong_final_keys | 222 | 62 |
| raw_json_value_correct | 101 | 11 |
| raw_json_status_correct | 129 | 39 |
| raw_json_status_and_value_correct | 15 | 0 |
| raw_json_stale_value_returned | 0 | 0 |
| tool_error_results | 98 | 0 |
| all_required_evidence_retrieved | 1 | 0 |
| strict_final_valid | 35 | 8 |
| empty_search_results | 116 | 47 |

### Exact outcome by task kind

| Task kind | Synthetic correct / total | OSS-style correct / total |
|---|---:|---:|
| consistent | 0 / 80 | 0 / 0 |
| incident | 0 / 60 | 0 / 0 |
| conflict | 0 / 200 | 0 / 100 |
| abstain | 0 / 60 | 0 / 0 |

### Representative raw failures

**test_synth: malformed_output, test_synth-0000-en**

Audit the documented max_retries for kyc-verifier against slack-mcp; report the effective setting and any stale page.

```text
<final_answer>{"status":"answered","value":"max_retries = 4","cites":["SLACK-TS-001"]}</final_answer>
```

Gold status/value: `answered` / `4`; executed calls: 1.

**test_synth: final_answer, test_synth-0000-hinglish**

Hey, kyc-verifier pe max_retries actually kitna configured hai? Runbook vs slack-mcp reconcile karke outdated page flag karna.

```text
<final_answer>{"status":"conflict_resolved","value":"max_retries = 3","cites":["search_notion('runbook max_retries configuration')","search_slack('runbook max_retries configuration')"],"stale_source":"search_notion('runbook max_retries configuration')"}</final_answer>
```

Gold status/value: `answered` / `4`; executed calls: 1.

**test_synth: tool_budget_exhausted, test_synth-0032-hi**

INC-TS-32 ka samay-aadhaarit kul jurmaana nirdhaarit kijiye: db-mcp ke samay se time-mcp dwaara avadhi ghanton mein aur math-mcp dwaara avadhi guna penalty_rate_per_hour.

```text

```

Gold status/value: `answered` / `168.0`; executed calls: 6.

**repo_style: malformed_output, repo_style-0000-en**

Audit the documented timeout_sec for fastapi-case-00 against github-mcp; report the effective setting and any stale page.

```text
<final_answer>{"status":"answered","value":"timeout_sec = 10001","cites":["PR-REALSTYLE-00"]}</final_answer>
```

Gold status/value: `conflict_resolved` / `10001`; executed calls: 1.

**repo_style: final_answer, repo_style-0008-hi**

litellm-case-02 ke rate_limit_rpm ka prabhaavi maan kya hai? Puraane nirdesh ko github-mcp ke pramaan se milaakar bataaiye.

```text
<final_answer>{"status":"conflict_resolved","value":"Rate limit RPM (requests per minute) sets a hard cap on how many API calls a service can make within a minute. This prevents overloading the system, ensures fair usage, and maintains performance. In the context of `litellm-case-02`, it likely prevents sudden spikes in API calls, ensuring stable service availability.","cites":["github-pr-123456789", "github-pr-987654321"], "stale_source": "github-pr-123456789"}</final_answer>
```

Gold status/value: `conflict_resolved` / `10017`; executed calls: 1.

## Native AuditKIT tool diagnostics

These are means without bootstrap intervals. Tool-selection F1 matches tool names against the scripted reference; it is not SQL semantic equivalence or outcome correctness. Schema validity is computed only on samples with tool calls.

| Metric | Synthetic | OSS-style |
|---|---:|---:|
| tool_call_precision_name | 0.6121 | 0.8300 |
| tool_call_recall_name | 0.3483 | 0.4150 |
| tool_call_f1_name | 0.4343 | 0.5533 |
| tool_call_exact_name | 0.0625 | 0.0000 |
| tool_call_validity | 0.9476 | 1.0000 |
| redundant_tool_calls | 0.0395 | 0.0000 |

