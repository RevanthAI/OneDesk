# Tiny Aya Fire: zero-shot baseline results

Model: `CohereLabs/tiny-aya-fire` at `73500c80fcb6c8bea3e830c21d5d2920249a0e1a`. No fine-tuning or oracle actions were used in model episodes.

Quantization: 4bit (NF4 with double quantization for 4bit); compute: float16; GPU: NVIDIA GeForce RTX 2070. Greedy decoding, max 384 new tokens/turn, at most 6 tool calls/task. XML-wrapped JSON protocol; malformed output ends the episode without repair.

Intervals: 95% percentile bootstrap, 10,000 resamples of semantic cases with translations kept together. Degenerate [0,0] or [100,100] intervals do not imply certainty outside this benchmark. All Hindi/Telugu queries are romanized.

| Metric | Synthetic holdout (400) | Constructed OSS-style holdout (100) |
|---|---:|---:|
| Stale-doc catch (%) | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Exact outcome (%) | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Verified citation F1, evidence tasks (%) | 0.78 [0.19, 1.59] | 0.00 [0.00, 0.00] |
| Abstention precision (%) | N/A (zero denominator) | N/A (zero denominator) |
| Abstention recall (%) | 0.00 [0.00, 0.00] | N/A (zero denominator) |
| Unplugged DB abstention recall (%) | 0.00 [0.00, 0.00] | N/A (zero denominator) |
| Distractor immunity, exposed tasks (%) | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| Tool calls per successful task | N/A (zero denominator) | N/A (zero denominator) |
| Valid final format (%) | 8.75 [5.75, 12.00] | 8.00 [3.92, 12.75] |
| Stale value returned, conflict tasks (%) | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

| Language | Synthetic exact outcome (%) | OSS-style exact outcome (%) |
|---|---:|---:|
| en | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| hi | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| hinglish | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| te | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

## Work completed

- Deterministic train/test worlds, isolated SQLite rollouts, strict protocol parsing, read-only queries and optional FastMCP wrapper.
- Evidence-consuming oracle, specified reward and separately named hardened variant, adversarial tests.
- Four-language SFT and curriculum datasets, CuratorKIT exact deduplication, actual AgentTune trajectory JSONL round-trip into AuditKIT, SHA-256 freeze.
- Live GPU base-model tool episodes, raw generations and tool outputs, AuditKIT custom scoring, resumable runs and cluster bootstrap metrics.

## Scope and limitations

The OSS-style cases are constructed fixtures. They contain no verified upstream PRs or real doc snapshots; these scores do not establish real-repository transfer. A source-backed OSS holdout remains future work.

Train/test services, employees, config values and question-template sets are disjoint. Odd/even config partitions enforce numeric separation within plausible overlapping ranges, rather than disjoint magnitude ranges. Synthetic evaluation has 100 semantic cases translated four ways; the OSS-style set has 30 cases. These are not 500 independent cases.

Original reward: always-abstain scores 0.1925, oracle 1.3550 on the 100-case adversarial suite. The requested thresholds cannot hold under that formula and task mix. The optional hardened variant reduces always-abstain to -0.0200. Correct unsupported guesses retain base reward under the original formula. Neither variant is claimed to be ungameable.

AgentTune is used for its installed trajectory classes and interoperable exports. Its eager agentic package initializer imports training/OpenEnv/RAG dependencies, so the dependency-free trajectory file is loaded directly by installed path. Full trainer dependencies are deferred; no claim of training readiness is made.

The MCP tools run in-process. The optional FastMCP wrapper is not a benchmark of separate network servers. No sub-millisecond parallel rollout claim is made. No adapters were trained or published, and no fine-tuning gains or ROI are claimed.

Romanized Hindi and Hinglish are distinct prompt groups but related registers. Template translations have not had independent native-speaker review. NF4 quantization may affect quality; this is a quantized deployment baseline, not an unquantized reference result.

Stale catch requires correct status/value, the correct stale page and both required citations actually retrieved. Exact outcome checks status/value. Citation precision includes hallucinated IDs in its denominator. Headline citation F1 excludes citation-free abstention; the AuditKIT all-item diagnostic includes zeros for those tasks.

## Runtime

```json
{
  "model": "CohereLabs/tiny-aya-fire",
  "revision": "73500c80fcb6c8bea3e830c21d5d2920249a0e1a",
  "quantization": "4bit",
  "max_new_tokens": 384,
  "max_tool_calls": 6,
  "batch_size": 16,
  "seed": 42,
  "temperature": 0.0,
  "dataset_hashes": {
    "curation_funnel.json": "9ccf35c212138b4281ac4812bb5ae9205a7b12674683f28673becf9464631637",
    "holdout_repo_style_100_frozen.jsonl": "bafc7eae5563216963cf36e284d376a32f7be95369b3b266af8412a70e6af253",
    "holdout_synth_400_frozen.jsonl": "4fc790e517f4f5c34c887a68c2a4a95de0eb98347eeaac855f3e0e4e861e8ef9",
    "train_grpo_stage1.jsonl": "ac9a066588db779fb37f866858d0592cf64560e214cc87be2ffcffb4c86b589d",
    "train_grpo_stage2.jsonl": "88b917119182c1941a49078fd02352a356cdd3eb79ae02350c95670b095a010a",
    "train_sft_400.jsonl": "4f6926280ecbc6aa5b78a9ee5804351cb991c5be3d894d90b75bc1905dcf78a0",
    "train_sft_agenttune_trajectories.jsonl": "237b733ac831be5ecedbc505f38868b039dc6a3de548304a558d943af41c05a4",
    "world_repo_style.json": "986244ef0d7c7f7755d67bfcb461ec5bbbf66856d2328e4727c64b455717830f",
    "world_test_synth.json": "8917e2520ba04b2809c65004e45035507bca2efc56bd383089c13306fc10a544",
    "world_train.json": "2f68a305b5eeb515442f6564a9fb2399b5f5291bd2172e4697d9b29a1594cf44"
  },
  "limit": 0,
  "gpu": "NVIDIA GeForce RTX 2070",
  "compute_dtype": "float16",
  "peak_vram_allocated_gib": 6.121118545532227,
  "peak_vram_reserved_gib": 6.794921875,
  "oom_splits": 0,
  "generated_tokens": 58016,
  "input_tokens": 1013403,
  "generation_seconds": 1874.372104793003,
  "generated_tokens_per_second": 30.952231870953405,
  "generation_batches": 108,
  "scoring_session_elapsed_seconds": 2.346300974000769,
  "versions": {
    "torch": "2.8.0+cu128",
    "transformers": "4.57.6",
    "bitsandbytes": "0.50.2",
    "agenttune": "1.1.4",
    "auditkit": "1.1.7",
    "curatorkit": "0.1.21"
  }
}
```

## Completion reasons

```json
{
  "test_synth": {
    "malformed_output": 360,
    "final_answer": 35,
    "tool_budget_exhausted": 5
  },
  "repo_style": {
    "malformed_output": 92,
    "final_answer": 8
  }
}
```

Evidence: `data/SHA256SUMS`, `reports/reward_hacking.md`, raw episode JSONL, metric JSONL and AuditKIT output folders.

## Validation and reward audit

The final project verification suite passes 21 tests. Frozen world/data checksums and saved model prompts were verified. The original reward and optional hardened variant were audited over 100 semantic cases:

| Policy | Specified reward | Evidence-gated reward |
|---|---:|---:|
| AlwaysAbstainPolicy | 0.1925 | -0.0200 |
| DumpAllNumbersPolicy | 0.0500 | -0.2000 |
| TrustOnlyNotionLazyPolicy | -0.0450 | -0.1200 |
| SpamAllToolsThenGuessPolicy | 0.0500 | -0.2000 |
| HallucinateCitationsWithoutToolsPolicy | 0.0500 | -0.2000 |
| HonestOraclePolicy | 1.3550 | 1.3550 |

The local search tools use conjunctive token matching over entity/parameter identifiers. Natural-language filler in a search query can therefore return an empty result. This is a constrained local benchmark, not a measurement against production Notion/Slack search. Missing-entity fixtures have recognizable synthetic names; human-reviewed, more natural prompts and a source-backed repository holdout are further benchmark improvements.

A zero strict outcome score here does not mean the model has no useful language or factual capability. The raw-output diagnostics distinguish value/status matches from the required structured contract. These observations do not independently confirm the proposed narrative that the base model specifically trusts stale Notion documents; protocol and verification failures dominate this run.

Toolkit commits are recorded in `toolkit_revisions.json`; setup and scope are in `README.md`; compatibility and GPU restart details are in `reports/IMPLEMENTATION_NOTES.md`. Model and toolkit primary sources: [Tiny Aya Fire](https://huggingface.co/CohereLabs/tiny-aya-fire), [AgentTune](https://github.com/Lexsi-Labs/AgentTune), [AuditKIT](https://github.com/Lexsi-Labs/AuditKIT), [CuratorKIT](https://github.com/Lexsi-Labs/CuratorKIT).

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

