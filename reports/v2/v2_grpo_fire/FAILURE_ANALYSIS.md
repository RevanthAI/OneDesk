# V2 evaluation failure analysis

Exact outcome requires both the expected status and normalized scalar value. Diagnostic flags below can overlap; they describe saved traces, not causal proof. No holdout was modified or used to retrain.

## validation

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| consistent | 1/20 | 20/20 |
| abstain | 20/20 | 20/20 |
| conflict | 0/20 | 20/20 |
| incident | 0/20 | 20/20 |

Observed error flags: wrong_value: 59, wrong_status: 46, unnecessary_abstention: 40, returned_stale_value: 3, cites_staging_record: 1.

### Saved trace examples

**train_val-0000-en** (consistent, en): expected answered / 13; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**train_val-0000-hi** (consistent, hi): expected answered / 13; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**train_val-0000-hinglish** (consistent, hinglish): expected answered / 13; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**train_val-0000-te** (consistent, te): expected answered / 13; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**train_val-0002-en** (consistent, en): expected answered / 406; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**train_val-0002-hi** (consistent, hi): expected answered / 406; flags: wrong_value.

```json
{"status": "answered", "value": 1024, "cites": [], "stale_source": null}
```

## test_synth

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| conflict | 0/200 | 197/200 |
| incident | 0/60 | 60/60 |
| abstain | 60/60 | 60/60 |
| consistent | 10/80 | 77/80 |

Observed error flags: wrong_value: 317, wrong_status: 302, unnecessary_abstention: 249, cites_staging_record: 12, returned_stale_value: 10, invalid_final_format: 6.

### Saved trace examples

**holdout_synth-0000-en** (conflict, en): expected conflict_resolved / 3836; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**holdout_synth-0000-hi** (conflict, hi): expected conflict_resolved / 3836; flags: wrong_status, wrong_value.

```json
{"status": "answered", "value": 1000, "cites": ["notion-mcp:search_notion", "github-mcp:search_github_prs"], "stale_source": null}
```

**holdout_synth-0000-hinglish** (conflict, hinglish): expected conflict_resolved / 3836; flags: wrong_status, wrong_value, returned_stale_value.

```json
{"status": "answered", "value": 3878, "cites": ["NOTION-V2-TS-044", "PR-V2-TS-044"], "stale_source": null}
```

**holdout_synth-0000-te** (conflict, te): expected conflict_resolved / 3836; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**holdout_synth-0001-en** (incident, en): expected answered / 15.0; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**holdout_synth-0001-hi** (incident, hi): expected answered / 15.0; flags: wrong_value.

```json
{"status": "answered", "value": 0.0, "cites": ["INC-V2-TS-000"], "stale_source": null}
```

## repo_style

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| consistent | 0/20 | 18/20 |
| abstain | 15/15 | 15/15 |
| conflict | 0/50 | 50/50 |
| incident | 0/15 | 15/15 |

Observed error flags: wrong_value: 83, wrong_status: 78, unnecessary_abstention: 70, returned_stale_value: 3, cites_staging_record: 3, invalid_final_format: 2.

### Saved trace examples

**holdout_repo_style-0000-en** (consistent, en): expected answered / 33; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**holdout_repo_style-0000-hi** (consistent, hi): expected answered / 33; flags: wrong_value.

```json
{"status": "answered", "value": 30, "cites": ["notion-mcp:search_notion('pydantic-schema-validator production timeout_sec')"], "stale_source": null}
```

**holdout_repo_style-0000-hinglish** (consistent, hinglish): expected answered / 33; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**holdout_repo_style-0000-te** (consistent, te): expected answered / 33; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**holdout_repo_style-0002-en** (conflict, en): expected conflict_resolved / 57; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**holdout_repo_style-0002-hi** (conflict, hi): expected conflict_resolved / 57; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

