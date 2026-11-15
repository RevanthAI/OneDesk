# NF4 versus FP16: paired Tiny Aya Fire findings

The two runs use identical frozen questions, prompts, greedy decoding, tool budgets and batch size. No answer repair is used. Descriptive raw-JSON scores ignore schema requirements but still compare exact scalar values.

Model commit: `73500c80fcb6c8bea3e830c21d5d2920249a0e1a`. Batch size: 1. Sample per language: full holdout.

Intervals below are 95% paired semantic-case bootstrap intervals for FP16 minus NF4, with 10,000 resamples. A small pilot is exploratory; a wide interval or unchanged score does not establish equivalence. Batch differences versus the older batch-16 NF4 run are controlled by rerunning NF4 here.

**Partial-run analysis:** only completed FP16 episodes are included and matched to the same NF4 task IDs. Missing episodes are not counted as failures or successes. A prefix of the holdout may have biased language/task coverage; this is not a full-holdout result.

## test_synth: 90 paired questions (400 expected in reference cohort)

| Metric | NF4 | FP16 | FP16 − NF4, pp [95% CI] |
|---|---:|---:|---:|
| exact_outcome | 0.00% | 0.00% | +0.00 [+0.00, +0.00] |
| format_valid | 18.89% | 16.67% | -2.22 [-13.64, +8.70] |
| raw_value | 18.89% | 13.33% | -5.56 [-13.04, +2.22] |
| raw_status | 32.22% | 15.56% | -16.67 [-27.78, -5.68] |
| raw_status_value | 16.67% | 8.89% | -7.78 [-15.12, -1.09] |
| stale_catch | N/A | N/A | N/A |
| verified_citation_f1 | 2.96% | 3.52% | +0.56 [-2.41, +3.60] |
| distractor_immunity | 100.00% | 100.00% | +0.00 [+0.00, +0.00] |

### Failure counts (categories can overlap)

| Failure | NF4 | FP16 |
|---|---:|---:|
| required_evidence_missing | 89 | 90 |
| wrong_value | 65 | 50 |
| wrong_status | 53 | 48 |
| unretrieved_citations | 54 | 44 |
| empty_search_result | 43 | 49 |
| missing_or_extra_final_fields | 44 | 17 |
| no_parseable_final_json | 8 | 25 |
| tool_execution_error | 9 | 10 |
| quoted_null | 5 | 0 |
| tool_budget_exhausted | 0 | 3 |

### By language

| Group | N | NF4 valid format | FP16 valid format | NF4 exact outcome | FP16 exact outcome |
|---|---:|---:|---:|---:|---:|
| en | 23 | 30.43% | 34.78% | 0.00% | 0.00% |
| hi | 23 | 21.74% | 4.35% | 0.00% | 0.00% |
| hinglish | 22 | 13.64% | 0.00% | 0.00% | 0.00% |
| te | 22 | 9.09% | 27.27% | 0.00% | 0.00% |

### By kind

| Group | N | NF4 valid format | FP16 valid format | NF4 exact outcome | FP16 exact outcome |
|---|---:|---:|---:|---:|---:|
| consistent | 80 | 16.25% | 17.50% | 0.00% | 0.00% |
| incident | 10 | 40.00% | 10.00% | 0.00% | 0.00% |

Format validity improves on 13 questions and regresses on 15.

Most frequent remaining FP16 failure categories: required_evidence_missing (90/90), wrong_value (50/90), empty_search_result (49/90).

## Interpretation

A meaningful format improvement in FP16 supports quantization contributing under this protocol. Persistent missing fields, quoted nulls or invalid tags suggest a protocol-following gap. Valid JSON with wrong status/value, SQL errors, missing evidence or fabricated citations identifies additional tool-use/reasoning gaps. Similar NF4 and FP16 pilot results are evidence from this cohort only, not proof that quantization has no effect.

If FP16 improves formatting but strict outcomes remain low, formatting alone does not explain the benchmark failures. The OSS-style holdout, if included, is constructed and cannot establish transfer to real repositories.

## Runtime / placement

NF4:

```json
{
  "quantization": "4bit",
  "gpu_memory_gib": null,
  "device_map": {
    "": "cuda:0"
  },
  "peak_vram_allocated_gib": 5.583664894104004,
  "generated_tokens_per_second": 11.190519880940613
}
```

FP16:

```json
{
  "quantization": "fp16",
  "gpu_memory_gib": 6.0,
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
  "peak_vram_allocated_gib": 6.402490615844727,
  "generated_tokens_per_second": 5.915003252991961
}
```

CPU offload changes placement and speed. Throughput differences between offloaded FP16 and GPU-resident NF4 must not be interpreted as a precision-only speed comparison.

## Paired examples

### test_synth-0000-en

Audit the documented max_retries for kyc-verifier against slack-mcp; report the effective setting and any stale page.

Expected: answered, value=4.

NF4:
```text
<final_answer>{"status":"answered","value":"max_retries = 4","cites":["SLACK-TS-001"]}</final_answer>
```
FP16:
```text
<final_answer>{"status":"conflict_resolved","value":"4","cites":["SLACK-TS-001"],"stale_source":"None"}</final_answer>
```

### test_synth-0000-hi

kyc-verifier ke max_retries ka prabhaavi maan kya hai? Puraane nirdesh ko slack-mcp ke pramaan se milaakar bataaiye.

Expected: answered, value=4.

NF4:
```text
<final_answer>{"status":"conflict_resolved","value":"max_retries ka prabhaavi maan kaise hota hai: max_retries ka prabhaavi maan kaise hota hai, is ka samna kyc-verifier ka `max_retries` paramater se hota hai. `max_retries` ka moolya `timeout_sec` se bhi jodh sakta hai, jaise ki `max_retries: timeout_sec`. `max_retries` ka moolya kaise hota hai, is ka samna kyc-verifier ka `max_retries` paramater se hota hai. `max_retries` ka moolya kaise hota hai, is ka samna kyc-verifier ka `max_retries` paramater se hota hai. `max_retries` ka moolya kaise hota hai, is ka samna kyc-verifier ka `max_retries` paramater se hota hai. `max_retries` ka moolya kaise hota hai, is ka samna kyc-verifier ka `max_retries` paramater se hota hai. `max_retries` ka moolya kaise hota hai, is ka samna kyc-verifier ka `max_retries` paramater se hota hai. `max_retries` ka moolya kaise hota hai, is ka samna kyc-verifier ka `max_retries` paramater se hota hai. `max_retries` ka moolya kaise hota hai, is ka samna kyc-verifier ka `max_retries` paramater se hota hai. `max_retries` ka moolya kaise hota
```
FP16:
```text
<final_answer>{"status":"conflict_resolved","value":"KYC-Verifier ka `max_retries` paramater ka prabhaavi maan `maxRetries` hai, jo unki `timeout_sec` se 10 gune mein set kiya ja sakta hai. 10 gune ka matlab hai ki KYC-Verifier 10 baar tak retry karega, aur pratyek retry ke baad unki `timeout_sec` 10 gune se badh jaati hai. 10 gune ka matlab hai ki KYC-Verifier unki `timeout_sec` se 10 gune tak retry karega, aur pratyek retry ke baad unki `timeout_sec` 10 gune se badh jaati hai. 10 gune ka matlab hai ki KYC-Verifier unki `timeout_sec` se 10 gune tak retry karega, aur pratyek retry ke baad unki `timeout_sec` 10 gune se badh jaati hai. 10 gune ka matlab hai ki KYC-Verifier unki `timeout_sec` se 10 gune tak retry karega, aur pratyek retry ke baad unki `timeout_sec` 10 gune se badh jaati hai. 10 gune ka matlab hai ki KYC-Verifier unki `timeout_sec` se 10 gune tak retry karega, aur pratyek retry ke baad unki `timeout_sec` 10 gune se badh jaati hai. 10 gune ka matlab hai ki KYC-Verifier unki `timeout_sec` se 10 gune tak retry karega, aur pratyek retry ke baad unki `timeout_sec` 10 gune se badh jaati hai. 10 gune ka matlab hai ki KYC-Verifier
```

### test_synth-0000-hinglish

Hey, kyc-verifier pe max_retries actually kitna configured hai? Runbook vs slack-mcp reconcile karke outdated page flag karna.

Expected: answered, value=4.

NF4:
```text
<final_answer>{"status":"conflict_resolved","value":"max_retries = 3","cites":["search_notion('runbook max_retries configuration')","search_slack('runbook max_retries configuration')"],"stale_source":"search_notion('runbook max_retries configuration')"}</final_answer>
```
FP16:
```text
<final_answer>{"status":"conflict_resolved","value":null,"cites":["search_slack:runbook vs slack-mcp reconcile max_retries kitna configured hai"], "stale_source":null}</final_answer>
```

### test_synth-0000-te

kyc-verifier lo amalulo unna max_retries viluva telapandi. Runbook vivaralanu slack-mcp aadharaalatho polchandi.

Expected: answered, value=4.

NF4:
```text
<final_answer>{"status":"conflict_resolved","value":"The Kyc-Verifier service has a max_retries value of 0, indicating it will not retry failed requests.","cites":["retrieved from the service's configuration in the Notion database"], "stale_source":"runbook-2023-10-01"} </final_answer>
```
FP16:
```text
<final_answer>{"status":"conflict_resolved","value":null,"cites":["search_slack:query=kyc-verifier max_retries failed runbook"],"stale_source":null}</final_answer>
```

### test_synth-0001-en

Audit the documented batch_size_mb for kyc-verifier against slack-mcp; report the effective setting and any stale page.

Expected: answered, value=160.

NF4:
```text
<final_answer>{"status":"conflict_resolved","value":"batch_size_mb = 1024 MB","cites":["search_notion","search_slack","query_db","inspect_schema"],"stale_source":null}</final_answer>
```
FP16:
```text
<final_answer>{"status":"conflict_resolved","value":"160","cites":["SLACK-TS-003"],"stale_source":"None"}</final_answer>
```

### test_synth-0002-hinglish

Hey, settlement-engine pe rate_limit_rpm actually kitna configured hai? Runbook vs github-mcp reconcile karke outdated page flag karna.

Expected: answered, value=600.

NF4:
```text
<final_answer>{"status":"answered","value":600,"cites":["retrieved evidence ID: 1"]}</final_answer>
```
FP16:
```text
<final_answer>{"status":"conflict_resolved","value":null,"cites":["github-mcp: search_github_prs returned empty results"], "stale_source":null}</final_answer>
```


## Domain-validity limitation identified after evaluation

The frozen OSS-style fixtures include 17 rendered questions across five cases with percentages above 100. They are constructed fixtures, not verified repository snapshots. See `../FINDINGS.md` and `../DATASET_ISSUES.json`; the frozen inputs were not changed.
