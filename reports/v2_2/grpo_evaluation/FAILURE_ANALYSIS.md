# V2 evaluation failure analysis

Exact outcome requires both the expected status and normalized scalar value. Diagnostic flags below can overlap; they describe saved traces, not causal proof. No holdout was modified or used to retrain.

## validation

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| consistent | 15/20 | 20/20 |
| abstain | 19/20 | 20/20 |
| conflict | 14/20 | 20/20 |
| incident | 16/20 | 20/20 |

Observed error flags: wrong_status: 11, wrong_value: 7, returned_stale_value: 1, unnecessary_abstention: 1.

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

**train_val-0003-hi** (conflict, hi): expected conflict_resolved / 16; flags: wrong_value, returned_stale_value.

```json
{"status": "conflict_resolved", "value": 436, "cites": ["NOTION-V2-TR-345", "SLACK-V2-TR-345"], "stale_source": "NOTION-V2-TR-345"}
```

**train_val-0003-te** (conflict, te): expected conflict_resolved / 16; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

## test_synth

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| conflict | 162/200 | 200/200 |
| incident | 44/60 | 60/60 |
| abstain | 38/60 | 60/60 |
| consistent | 59/80 | 80/80 |

Observed error flags: wrong_status: 78, wrong_value: 67, unnecessary_abstention: 19, returned_stale_value: 11, cites_staging_record: 10.

### Saved trace examples

**holdout_synth-0001-te** (incident, te): expected answered / 15.0; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**holdout_synth-0003-hinglish** (incident, hinglish): expected answered / 2; flags: wrong_status, wrong_value, cites_staging_record.

```json
{"status": "conflict_resolved", "value": 5, "cites": ["INC-V2-TS-001", "NOTION-V2-TS-133-STG"], "stale_source": "NOTION-V2-TS-133-STG"}
```

**holdout_synth-0003-te** (incident, te): expected answered / 2; flags: wrong_status, wrong_value, cites_staging_record.

```json
{"status": "conflict_resolved", "value": 5, "cites": ["NOTION-V2-TS-133-STG", "SLACK-V2-TS-133-STG"], "stale_source": "NOTION-V2-TS-133-STG"}
```

**holdout_synth-0005-en** (abstain, en): expected abstain / None; flags: wrong_status, wrong_value.

```json
{"status": "conflict_resolved", "value": 4568, "cites": ["NOTION-V2-TS-086", "PR-V2-TS-086"], "stale_source": "NOTION-V2-TS-086"}
```

**holdout_synth-0005-hi** (abstain, hi): expected abstain / None; flags: wrong_status, wrong_value.

```json
{"status": "conflict_resolved", "value": 4568, "cites": ["NOTION-V2-TS-086", "PR-V2-TS-086"], "stale_source": "NOTION-V2-TS-086"}
```

**holdout_synth-0005-hinglish** (abstain, hinglish): expected abstain / None; flags: wrong_status, wrong_value.

```json
{"status": "conflict_resolved", "value": 4568, "cites": ["NOTION-V2-TS-086", "PR-V2-TS-086"], "stale_source": "NOTION-V2-TS-086"}
```

## repo_style

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| consistent | 15/20 | 20/20 |
| abstain | 11/15 | 15/15 |
| conflict | 37/50 | 50/50 |
| incident | 8/15 | 15/15 |

Observed error flags: wrong_value: 21, wrong_status: 19, unnecessary_abstention: 6, cites_staging_record: 1.

### Saved trace examples

**holdout_repo_style-0003-en** (consistent, en): expected answered / 30; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 30, "cites": ["NOTION-V2-OSS-178", "SLACK-V2-OSS-178"], "stale_source": "NOTION-V2-OSS-178"}
```

**holdout_repo_style-0003-hi** (consistent, hi): expected answered / 30; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 30, "cites": ["NOTION-V2-OSS-178", "PR-V2-OSS-178"], "stale_source": "NOTION-V2-OSS-178"}
```

**holdout_repo_style-0003-hinglish** (consistent, hinglish): expected answered / 30; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 30, "cites": ["NOTION-V2-OSS-178", "SLACK-V2-OSS-178"], "stale_source": "NOTION-V2-OSS-178"}
```

**holdout_repo_style-0003-te** (consistent, te): expected answered / 30; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 30, "cites": ["NOTION-V2-OSS-178", "SLACK-V2-OSS-178"], "stale_source": "NOTION-V2-OSS-178"}
```

**holdout_repo_style-0006-hi** (conflict, hi): expected conflict_resolved / 495; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**holdout_repo_style-0007-te** (incident, te): expected answered / 143.0; flags: wrong_status, wrong_value, cites_staging_record.

```json
{"status": "conflict_resolved", "value": 22.0, "cites": ["INC-V2-OSS-000", "NOTION-V2-OSS-173-STG", "SLACK-V2-OSS-173-STG"], "stale_source": "NOTION-V2-OSS-173-STG"}
```

