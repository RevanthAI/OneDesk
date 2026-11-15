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


See REVIEW_SAMPLES.md for the complete reference interaction and ten-record file samples.

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


## Final verification

The complete project suite passed: **50 tests**, including v2 pairwise split separation, all semantic oracle paths, production/staging distractors, native-script coverage, incident conversions, real curation, reward-hacking regressions and the active-advantage backend CPU integration check. A benign warning remains in an existing tiny PEFT save/reload fixture.

Both manifests were verified: all 10 original v1 machine files remain unchanged, and all 15 v2 machine files match `data_v2/SHA256SUMS`. The new sampler/backend has not had a v2 GPU training smoke test. No v2 SFT, GRPO, baseline evaluation or paid cloud job was launched. Training remains gated on this data review.
