# V2 evaluation failure analysis

Exact outcome requires both the expected status and normalized scalar value. Diagnostic flags below can overlap; they describe saved traces, not causal proof. No holdout was modified or used to retrain.

## validation

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| consistent | 15/20 | 19/20 |
| abstain | 16/20 | 20/20 |
| conflict | 0/20 | 20/20 |
| incident | 4/20 | 20/20 |

Observed error flags: wrong_value: 44, wrong_status: 33, cites_staging_record: 15, returned_stale_value: 15, unnecessary_abstention: 9, tool_error: 2, invalid_final_format: 1.

### Saved trace examples

**train_val-0002-hi** (consistent, hi): expected answered / 406; flags: wrong_value, cites_staging_record.

```json
{"status": "answered", "value": 421, "cites": ["NOTION-V2-TR-219-STG"], "stale_source": null}
```

**train_val-0002-te** (consistent, te): expected answered / 406; flags: wrong_value, cites_staging_record.

```json
{"status": "answered", "value": 421, "cites": ["NOTION-V2-TR-219-STG", "NOTION-V2-TR-303-STG"], "stale_source": null}
```

**train_val-0003-en** (conflict, en): expected conflict_resolved / 16; flags: wrong_status, wrong_value, returned_stale_value.

```json
{"status": "answered", "value": 436, "cites": ["NOTION-V2-TR-345", "PR-V2-TR-345"], "stale_source": null}
```

**train_val-0003-hi** (conflict, hi): expected conflict_resolved / 16; flags: wrong_status, wrong_value, returned_stale_value.

```json
{"status": "answered", "value": 436, "cites": ["NOTION-V2-TR-345", "PR-V2-TR-345"], "stale_source": null}
```

**train_val-0003-hinglish** (conflict, hinglish): expected conflict_resolved / 16; flags: wrong_status, wrong_value, cites_staging_record.

```json
{"status": "answered", "value": 181, "cites": ["NOTION-V2-TR-345-STG", "PR-V2-TR-345"], "stale_source": null}
```

**train_val-0003-te** (conflict, te): expected conflict_resolved / 16; flags: wrong_status, wrong_value, cites_staging_record.

```json
{"status": "answered", "value": 181, "cites": ["NOTION-V2-TR-345-STG", "PR-V2-TR-345-STG"], "stale_source": null}
```

## test_synth

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| conflict | 0/200 | 196/200 |
| incident | 6/60 | 60/60 |
| abstain | 30/60 | 60/60 |
| consistent | 69/80 | 80/80 |

Observed error flags: wrong_status: 266, wrong_value: 232, returned_stale_value: 92, cites_staging_record: 63, unnecessary_abstention: 38, tool_error: 6, invalid_final_format: 4.

### Saved trace examples

**holdout_synth-0000-en** (conflict, en): expected conflict_resolved / 3836; flags: wrong_status.

```json
{"status": "answered", "value": 3836, "cites": ["NOTION-V2-TS-044", "PR-V2-TS-044"], "stale_source": null}
```

**holdout_synth-0000-hi** (conflict, hi): expected conflict_resolved / 3836; flags: wrong_status.

```json
{"status": "answered", "value": 3836, "cites": ["NOTION-V2-TS-044", "PR-V2-TS-044"], "stale_source": null}
```

**holdout_synth-0000-hinglish** (conflict, hinglish): expected conflict_resolved / 3836; flags: wrong_status, wrong_value, returned_stale_value.

```json
{"status": "answered", "value": 3878, "cites": ["NOTION-V2-TS-044", "PR-V2-TS-044"], "stale_source": null}
```

**holdout_synth-0000-te** (conflict, te): expected conflict_resolved / 3836; flags: wrong_status.

```json
{"status": "answered", "value": 3836, "cites": ["NOTION-V2-TS-044", "PR-V2-TS-044"], "stale_source": null}
```

**holdout_synth-0001-en** (incident, en): expected answered / 15.0; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**holdout_synth-0001-hi** (incident, hi): expected answered / 15.0; flags: wrong_value.

```json
{"status": "answered", "value": 24.0, "cites": ["INC-V2-TS-000"], "stale_source": null}
```

## repo_style

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| consistent | 18/20 | 20/20 |
| abstain | 7/15 | 15/15 |
| conflict | 0/50 | 50/50 |
| incident | 1/15 | 15/15 |

Observed error flags: wrong_value: 69, wrong_status: 67, returned_stale_value: 26, cites_staging_record: 24, unnecessary_abstention: 9, tool_error: 3.

### Saved trace examples

**holdout_repo_style-0001-te** (abstain, te): expected abstain / None; flags: wrong_status, wrong_value, cites_staging_record.

```json
{"status": "answered", "value": 36, "cites": ["NOTION-V2-OSS-173-STG", "NOTION-V2-OSS-167-STG"], "stale_source": null}
```

**holdout_repo_style-0002-en** (conflict, en): expected conflict_resolved / 57; flags: wrong_status, wrong_value, returned_stale_value.

```json
{"status": "answered", "value": 51, "cites": ["NOTION-V2-OSS-119"], "stale_source": null}
```

**holdout_repo_style-0002-hi** (conflict, hi): expected conflict_resolved / 57; flags: wrong_status, wrong_value, cites_staging_record, returned_stale_value.

```json
{"status": "answered", "value": 51, "cites": ["NOTION-V2-OSS-119", "NOTION-V2-OSS-119-STG"], "stale_source": null}
```

**holdout_repo_style-0002-hinglish** (conflict, hinglish): expected conflict_resolved / 57; flags: wrong_status, wrong_value, returned_stale_value.

```json
{"status": "answered", "value": 51, "cites": ["NOTION-V2-OSS-119"], "stale_source": null}
```

**holdout_repo_style-0002-te** (conflict, te): expected conflict_resolved / 57; flags: wrong_status, wrong_value, returned_stale_value.

```json
{"status": "answered", "value": 51, "cites": ["NOTION-V2-OSS-119"], "stale_source": null}
```

**holdout_repo_style-0004-en** (conflict, en): expected conflict_resolved / 372; flags: wrong_status, wrong_value, returned_stale_value.

```json
{"status": "answered", "value": 267, "cites": ["NOTION-V2-OSS-171"], "stale_source": null}
```

