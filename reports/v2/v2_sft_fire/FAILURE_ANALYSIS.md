# V2 evaluation failure analysis

Exact outcome requires both the expected status and normalized scalar value. Diagnostic flags below can overlap; they describe saved traces, not causal proof. No holdout was modified or used to retrain.

## validation

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| consistent | 2/20 | 17/20 |
| abstain | 11/20 | 15/20 |
| conflict | 0/20 | 16/20 |
| incident | 5/20 | 15/20 |

Observed error flags: wrong_value: 32, wrong_status: 26, invalid_final_format: 17, cites_staging_record: 14, tool_error: 6, tool_budget_exhausted: 5, returned_stale_value: 3.

### Saved trace examples

**train_val-0000-en** (consistent, en): expected answered / 13; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 13, "cites": ["NOTION-V2-TR-023", "PR-V2-TR-023"], "stale_source": "NOTION-V2-TR-023"}
```

**train_val-0000-hi** (consistent, hi): expected answered / 13; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 13, "cites": ["NOTION-V2-TR-023", "PR-V2-TR-023"], "stale_source": "NOTION-V2-TR-023"}
```

**train_val-0000-hinglish** (consistent, hinglish): expected answered / 13; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 13, "cites": ["NOTION-V2-TR-023", "PR-V2-TR-023"], "stale_source": "NOTION-V2-TR-023"}
```

**train_val-0000-te** (consistent, te): expected answered / 13; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 13, "cites": ["NOTION-V2-TR-023", "PR-V2-TR-023"], "stale_source": "NOTION-V2-TR-023"}
```

**train_val-0002-en** (consistent, en): expected answered / 406; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 406, "cites": ["NOTION-V2-TR-219", "SLACK-V2-TR-219"], "stale_source": "NOTION-V2-TR-219"}
```

**train_val-0002-hi** (consistent, hi): expected answered / 406; flags: wrong_value, cites_staging_record.

```json
{"status": "answered", "value": 421, "cites": ["NOTION-V2-TR-219-STG", "NOTION-V2-TR-303-STG"], "stale_source": null}
```

## test_synth

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| conflict | 14/200 | 148/200 |
| incident | 8/60 | 36/60 |
| abstain | 23/60 | 58/60 |
| consistent | 15/80 | 58/80 |

Observed error flags: wrong_value: 195, wrong_status: 155, invalid_final_format: 100, cites_staging_record: 99, unnecessary_abstention: 27, tool_error: 26, returned_stale_value: 26, tool_budget_exhausted: 19.

### Saved trace examples

**holdout_synth-0000-en** (conflict, en): expected conflict_resolved / 3836; flags: invalid_final_format.

```json
{}
```

**holdout_synth-0000-hi** (conflict, hi): expected conflict_resolved / 3836; flags: wrong_status, wrong_value.

```json
{"status": "answered", "value": 4772, "cites": ["NOTION-V2-TS-044", "PR-V2-TS-044"], "stale_source": null}
```

**holdout_synth-0000-te** (conflict, te): expected conflict_resolved / 3836; flags: invalid_final_format.

```json
{}
```

**holdout_synth-0001-en** (incident, en): expected answered / 15.0; flags: invalid_final_format, tool_error, tool_budget_exhausted.

```json
{}
```

**holdout_synth-0001-hi** (incident, hi): expected answered / 15.0; flags: invalid_final_format, tool_error, tool_budget_exhausted.

```json
{}
```

**holdout_synth-0001-hinglish** (incident, hinglish): expected answered / 15.0; flags: wrong_value, tool_error.

```json
{"status": "answered", "value": 2500000000.0, "cites": ["INC-V2-TS-000"], "stale_source": null}
```

## repo_style

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| consistent | 2/20 | 16/20 |
| abstain | 5/15 | 9/15 |
| conflict | 7/50 | 37/50 |
| incident | 2/15 | 8/15 |

Observed error flags: wrong_value: 37, wrong_status: 31, invalid_final_format: 30, cites_staging_record: 14, returned_stale_value: 9, tool_error: 9, tool_budget_exhausted: 5, unnecessary_abstention: 3.

### Saved trace examples

**holdout_repo_style-0000-en** (consistent, en): expected answered / 33; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 33, "cites": ["NOTION-V2-OSS-012", "PR-V2-OSS-012"], "stale_source": "NOTION-V2-OSS-012"}
```

**holdout_repo_style-0000-hi** (consistent, hi): expected answered / 33; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 33, "cites": ["NOTION-V2-OSS-012", "PR-V2-OSS-012"], "stale_source": "NOTION-V2-OSS-012"}
```

**holdout_repo_style-0000-hinglish** (consistent, hinglish): expected answered / 33; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 33, "cites": ["NOTION-V2-OSS-012", "PR-V2-OSS-012"], "stale_source": "NOTION-V2-OSS-042"}
```

**holdout_repo_style-0000-te** (consistent, te): expected answered / 33; flags: wrong_value, cites_staging_record.

```json
{"status": "answered", "value": "The production timeout_sec values are not defined in the provided sources. All references indicate that the values are STAGING-ONLY settings and should not be applied to production. The latest STAGING values are: falcon-api-middleware: 90, quart-websocket-worker: 102, tornado-request-handler: 54.", "cites": ["NOTION-V2-OSS-174-STG", "NOTION-V2-OSS-168-STG", "NOTION-V2-OSS-162-STG"], "stale_source": null}
```

**holdout_repo_style-0001-te** (abstain, te): expected abstain / None; flags: invalid_final_format.

```json
{}
```

**holdout_repo_style-0002-te** (conflict, te): expected conflict_resolved / 57; flags: invalid_final_format.

```json
{}
```

