# NF4 versus FP16: paired Tiny Aya Fire findings

The two runs use identical frozen questions, prompts, greedy decoding, tool budgets and batch size. No answer repair is used. Descriptive raw-JSON scores ignore schema requirements but still compare exact scalar values.

Model commit: `73500c80fcb6c8bea3e830c21d5d2920249a0e1a`. Batch size: 1. Sample per language: full holdout.

Intervals below are 95% paired semantic-case bootstrap intervals for FP16 minus NF4, with 10,000 resamples. A small pilot is exploratory; a wide interval or unchanged score does not establish equivalence. Batch differences versus the older batch-16 NF4 run are controlled by rerunning NF4 here.

## repo_style: 100 paired questions (100 expected in reference cohort)

| Metric | NF4 | FP16 | FP16 − NF4, pp [95% CI] |
|---|---:|---:|---:|
| exact_outcome | 0.00% | 0.00% | +0.00 [+0.00, +0.00] |
| format_valid | 8.00% | 18.00% | +10.00 [+0.00, +20.00] |
| raw_value | 11.00% | 14.00% | +3.00 [-3.09, +9.28] |
| raw_status | 37.00% | 51.00% | +14.00 [+5.88, +23.08] |
| raw_status_value | 0.00% | 0.00% | +0.00 [+0.00, +0.00] |
| stale_catch | 0.00% | 0.00% | +0.00 [+0.00, +0.00] |
| verified_citation_f1 | 0.00% | 2.00% | +2.00 [+0.00, +4.17] |
| distractor_immunity | 100.00% | 100.00% | +0.00 [+0.00, +0.00] |

### Failure counts (categories can overlap)

| Failure | NF4 | FP16 |
|---|---:|---:|
| required_evidence_missing | 100 | 100 |
| wrong_value | 73 | 71 |
| missing_or_extra_final_fields | 61 | 41 |
| empty_search_result | 47 | 45 |
| wrong_status | 47 | 34 |
| unretrieved_citations | 33 | 48 |
| no_parseable_final_json | 16 | 15 |

### By language

| Group | N | NF4 valid format | FP16 valid format | NF4 exact outcome | FP16 exact outcome |
|---|---:|---:|---:|---:|---:|
| en | 25 | 0.00% | 16.00% | 0.00% | 0.00% |
| hi | 25 | 28.00% | 0.00% | 0.00% | 0.00% |
| hinglish | 25 | 0.00% | 32.00% | 0.00% | 0.00% |
| te | 25 | 4.00% | 24.00% | 0.00% | 0.00% |

### By kind

| Group | N | NF4 valid format | FP16 valid format | NF4 exact outcome | FP16 exact outcome |
|---|---:|---:|---:|---:|---:|
| conflict | 100 | 8.00% | 18.00% | 0.00% | 0.00% |

Format validity improves on 18 questions and regresses on 8.

Most frequent remaining FP16 failure categories: required_evidence_missing (100/100), wrong_value (71/100), unretrieved_citations (48/100).

## Interpretation

A meaningful format improvement in FP16 supports quantization contributing under this protocol. Persistent missing fields, quoted nulls or invalid tags suggest a protocol-following gap. Valid JSON with wrong status/value, SQL errors, missing evidence or fabricated citations identifies additional tool-use/reasoning gaps. Similar NF4 and FP16 pilot results are evidence from this cohort only, not proof that quantization has no effect.

If FP16 improves formatting but strict outcomes remain low, formatting alone does not explain the benchmark failures. The OSS-style holdout, if included, is constructed and cannot establish transfer to real repositories.

## Runtime / placement

NF4:

```json
{
  "quantization": "4bit",
  "gpu_memory_gib": null,
  "sdpa_expand_kv": true,
  "device_map": {
    "": "cuda:0"
  },
  "peak_vram_allocated_gib": 2.5341787338256836,
  "generated_tokens_per_second": 13.41070909926151
}
```

FP16:

```json
{
  "quantization": "fp16",
  "gpu_memory_gib": 6.0,
  "sdpa_expand_kv": true,
  "device_map": {
    "model.embed_tokens": "0",
    "lm_head": "0",
    "model.layers.0": "0",
    "model.layers.1": "0",
    "model.layers.2": "0",
    "model.layers.3": "0",
    "model.layers.4": "0",
    "model.layers.5": "0",
    "model.layers.6": "0",
    "model.layers.7": "0",
    "model.layers.8": "0",
    "model.layers.9": "0",
    "model.layers.10": "0",
    "model.layers.11": "0",
    "model.layers.12": "0",
    "model.layers.13": "0",
    "model.layers.14": "0",
    "model.layers.15": "0",
    "model.layers.16": "0",
    "model.layers.17": "0",
    "model.layers.18": "0",
    "model.layers.19": "0",
    "model.layers.20": "0",
    "model.layers.21": "0",
    "model.layers.22": "0",
    "model.layers.23": "0",
    "model.layers.24": "0",
    "model.layers.25": "0",
    "model.layers.26": "0",
    "model.layers.27": "0",
    "model.layers.28": "0",
    "model.layers.29": "0",
    "model.layers.30": "0",
    "model.layers.31": "0",
    "model.layers.32": "0",
    "model.layers.33": "cpu",
    "model.layers.34": "cpu",
    "model.layers.35": "cpu",
    "model.norm": "cpu",
    "model.rotary_emb": "cpu"
  },
  "peak_vram_allocated_gib": 5.982152938842773,
  "generated_tokens_per_second": 6.229519146726945
}
```

CPU offload changes placement and speed. Throughput differences between offloaded FP16 and GPU-resident NF4 must not be interpreted as a precision-only speed comparison.

## Paired examples

### repo_style-0000-en

Audit the documented timeout_sec for fastapi-case-00 against github-mcp; report the effective setting and any stale page.

Expected: conflict_resolved, value=10001.

NF4:
```text
<final_answer>{"status":"answered","value":"timeout_sec = 10001","cites":["PR-REALSTYLE-00"]}</final_answer>
```
FP16:
```text
<final_answer>{"status":"answered","value":"timeout_sec = 10001","cites":["PR-REALSTYLE-00"]}</final_answer>
```

### repo_style-0001-en

Audit the documented max_retries for pydantic-case-00 against github-mcp; report the effective setting and any stale page.

Expected: conflict_resolved, value=10003.

NF4:
```text
<final_answer>{"status":"answered","value":"max_retries = 10003","cites":["PR-REALSTYLE-01"]}</final_answer>
```
FP16:
```text
<final_answer>{"status":"answered","value":"max_retries = 10003","cites":["PR-REALSTYLE-01"]}</final_answer>
```

### repo_style-0005-en

Audit the documented circuit_breaker_pct for litellm-case-01 against github-mcp; report the effective setting and any stale page.

Expected: conflict_resolved, value=10011.

NF4:
```text
<final_answer>{"status":"answered","value":"circuit_breaker_pct = 10011","cites":["PR-REALSTYLE-05"]}</final_answer>
```
FP16:
```text
<final_answer>{"status":"conflict_resolved","value":null,"cites":["github-mcp:search_github_prs:litellm-case-01 circuit_breaker_pct stale page"], "stale_source":"github-mcp:search_github_prs:litellm-case-01 circuit_breaker_pct stale page"}</final_answer>
```

### repo_style-0011-en

Audit the documented circuit_breaker_pct for litellm-case-03 against github-mcp; report the effective setting and any stale page.

Expected: conflict_resolved, value=10023.

NF4:
```text
<final_answer>{"status":"answered","value":"circuit_breaker_pct = 10023","cites":["PR-REALSTYLE-11"]}</final_answer>
```
FP16:
```text
<final_answer>{"status":"conflict_resolved","value":"circuit_breaker_pct = 10023","cites":["PR-REALSTYLE-11"],"stale_source":"PR-REALSTYLE-11"}</final_answer>
```

### repo_style-0017-en

Audit the documented circuit_breaker_pct for litellm-case-05 against github-mcp; report the effective setting and any stale page.

Expected: conflict_resolved, value=10035.

NF4:
```text
<final_answer>{"status":"answered","value":"circuit_breaker_pct = 10035","cites":["PR-REALSTYLE-17"]}</final_answer>
```
FP16:
```text
<final_answer>{"status":"conflict_resolved","value":"circuit_breaker_pct = 10035","cites":["PR-REALSTYLE-17"],"stale_source":"PR-REALSTYLE-17"}</final_answer>
```

### repo_style-0023-en

Audit the documented circuit_breaker_pct for litellm-case-07 against github-mcp; report the effective setting and any stale page.

Expected: conflict_resolved, value=10047.

NF4:
```text
<final_answer>{"status":"answered","value":"circuit_breaker_pct = 10047","cites":["PR-REALSTYLE-23"]}</final_answer>
```
FP16:
```text
<final_answer>{"status":"conflict_resolved","value":"circuit_breaker_pct = 10047","cites":["PR-REALSTYLE-23"],"stale_source":"PR-REALSTYLE-23"}</final_answer>
```


## Domain-validity limitation identified after evaluation

The frozen OSS-style fixtures include 17 rendered questions across five cases with percentages above 100. They are constructed fixtures, not verified repository snapshots. See `../FINDINGS.md` and `../DATASET_ISSUES.json`; the frozen inputs were not changed.
