# SFT findings: Tiny Aya Fire, NF4 local deployment

Recorded 2026-11-11. Full frozen evaluation completed: 400 synthetic questions and 100 constructed OSS-style questions. The model is the downloaded SFT adapter over the pinned original base in NF4; this report does not evaluate the separately merged model. No GRPO has run.

## Headline results

| Metric | Synthetic | Constructed OSS-style |
|---|---:|---:|
| Exact status + value | 85.25% [80.75, 89.50] | 68.00% [61.62, 74.49] |
| Strict stale-document catch | 87.00% [80.36, 92.65] | 68.00% [61.62, 74.49] |
| Verified citation F1 (evidence tasks) | 89.41% [85.63, 92.93] | 100.00% [100.00, 100.00] |
| Valid final response | 99.00% [98.00, 99.75] | 100.00% [100.00, 100.00] |

Brackets are 95% cluster-bootstrap intervals from 10,000 resamples, grouping translations of a semantic case. There are 100 synthetic cases and 30 constructed OSS-style cases; these are not 500 independent examples.

Against the completed NF4 baseline in `reports/precision_full/nf4`, exact outcome increased from 0% to 85.25% (+85.25 percentage points) on synthetic tasks and from 0% to 68% (+68 points) on the constructed OSS-style set. Synthetic strict stale catch increased from 0% to 87%, and valid final responses from 9.25% to 99%. OSS-style valid final responses increased from 8% to 100%. These are observed deployment comparisons; the SFT run enables expanded-KV SDPA whereas the original NF4 baseline did not record that option. They are not a controlled precision/attention ablation.

## What worked

- Synthetic exact outcome: 341/400. Conflict tasks: 174/200; consistent verification: 80/80. The model generally performs the actual tool calls and uses returned evidence.
- Citation F1: 89.41% on synthetic evidence-bearing tasks and 100% on constructed OSS-style tasks. AuditKIT reports synthetic tool-call F1 of 89.24% and tool-call validity of 98.92%.
- No distractor calls on the exposed items in either world. No redundant calls according to AuditKIT. Successful synthetic tasks used 1.89 calls on average.
- Missing-entity abstention: 32/32. Format failures fell to four synthetic episodes; all 100 constructed OSS-style episodes finished with valid final responses.

## Synthetic accuracy by task

| Task | Correct / total | Accuracy |
|---|---:|---:|
| consistent | 80/80 | 100.00% |
| incident | 37/60 | 61.67% |
| conflict | 174/200 | 87.00% |
| abstain | 50/60 | 83.33% |

## Language results

| Language/register | Synthetic | Constructed OSS-style |
|---|---:|---:|
| en | 88% | 100% |
| hi | 83% | 0% |
| hinglish | 85% | 100% |
| te | 85% | 72% |

All Hindi and Telugu text is romanized. These results do not measure native-script performance. Related template translations and the small OSS-style language cohorts limit broad multilingual claims.

## What failed, based on raw traces

**1. OSS-style Hindi failures are conflict-contract failures.** All 25 Hindi questions retrieve both correct evidence IDs and return the correct current value, but output `status="answered"` and `stale_source=null`. The expected status is `conflict_resolved` and the stale page must be identified. The seven Telugu failures have the same pattern. All 32 OSS-style strict-outcome failures are status mismatches with correct values and full verified citations. Value-only accuracy is therefore 100/100, a secondary diagnostic that must not replace the frozen primary metric. The observations suggest phrasing-sensitive conflict classification; they do not establish a general inability to understand Hindi. Example: `repo_style-0005-hi`.

**2. Incident chaining is the weakest synthetic task: 37/60 (61.67%).** Of 23 failures, 13 romanized Hindi episodes query `microservices` for an incident ID rather than `production_incidents`; five English/Hinglish episodes search Notion/Slack for an incident instead of querying the DB; one Telugu episode uses `service_name` instead of `incident_id`. These 19 episodes incorrectly abstain after empty retrievals. Four other Telugu episodes get the correct incident and duration but ask math-mcp to divide hours by 24 rather than multiply by `penalty_rate_per_hour`. Example `test_synth-0021-te` computes `8 / 24` instead of `8 * 14 = 112`. Tool execution works; routing and selecting the requested operation fail. Hindi incident accuracy is 2/15, despite 83/100 overall Hindi accuracy.

**3. Conflict reasoning remains imperfect: 26/200 fail.** Eight return the correct value but use `answered`; other traces stop at Notion, lose the service identifier in their query, add natural-language filler to the exact-match search, or query only the DB without identifying the stale document. `test_synth-0036-en` shortens `reconciliation-api` to `reconcile-api`, gets an empty result and abstains. `test_synth-0068-en` retrieves the current value 200 and both sources but omits conflict status and stale-page identification. The frozen stale-value-returned metric counts 10/200 (5%); it excludes an additional raw stale-valued response rejected by the protocol parser, so it is not an exhaustive raw-text stale-answer count.

**4. Server-unplugged abstention needs work.** Only 18/28 required-DB-unavailable requests succeed (64.29%). Seven Telugu failures answer from Notion/Slack despite an explicit database-only requirement; three English episodes produce malformed invented tool calls (`server="query_db", tool="select"`). Missing-entity requests all succeed, so these are distinct failure modes. Overall abstention recall is 50/60 (83.33%); precision is 50/72 (69.44%). The 22 false abstentions comprise 19 incident tasks and three conflict tasks.

**5. Four remaining protocol failures are not all JSON syntax failures.** Three are malformed/incomplete invented tool calls on unplugged DB requests. One (`test_synth-0046-en`) contains parseable JSON but violates the response contract by setting a stale source while status is `answered`; the parser classifies it as malformed output.

Synthetic strict failures total 59: 42 wrong status and value, eight status-only mismatches, five value-only mismatches, and four invalid-protocol episodes. Categories are mutually exclusive and describe the final response, not a unique cognitive cause.

## Runtime and reproducibility

Completed locally on NVIDIA GeForce RTX 2070, batch 1, NF4 weights with FP16 computation, greedy decoding and expanded-KV SDPA. Scoring-session elapsed time was 137.1 minutes; generation throughput was 7.91 tokens/sec. Peak reserved VRAM was 3.15 GiB; OOM batch splits: 0.

Dataset checksums, complete task coverage, and reported task counts were checked against the saved artifacts. `run_config.json` records dataset and adapter hashes; `runtime.json` records implementation versions and hardware. `summary.json`, `*_metrics.jsonl`, `*_episodes.jsonl` and AuditKIT outputs are the primary evidence. `FAILURE_ANALYSIS.json` lists every failed task and aggregate category; `FAILURE_EXAMPLES.json` preserves representative model calls and tool results. Original episodes and frozen datasets were not modified.

## Limitations and next experiments

The OSS-style world is constructed, not a verified snapshot of real upstream repositories. It includes 17 questions across five cases with impossible circuit-breaker percentages above 100; other fixture defaults are also artificial. Keep the frozen result for comparability, but do not claim real-repository transfer. High citation scores do not by themselves prove correct interpretation of evidence or compliance with source requirements.

The baseline failed largely at protocol adherence; the measured SFT gain combines better formatting, routing, evidence use and answer classification. It should not be described solely as curing stale-document trust. This run does not establish a GRPO benefit or characterize the separately merged model.

For the next training experiment, prioritize fresh train-world analogues of incident-table routing, correct penalty operations, explicit source requirements, and multilingual conflict classification. Generate new entities/phrasing and verify oracle solutions. Do not copy these holdout questions, values, or traces into training. Because these holdouts have now guided development, further results on them are development comparisons; reserve a newly frozen, untouched confirmation set for final generalization claims. Keep current metrics unchanged and compare future checkpoints under matched inference settings.

No additional training or GPU evaluation was launched to create this analysis.
