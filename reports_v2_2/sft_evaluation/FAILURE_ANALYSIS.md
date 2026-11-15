# V2 evaluation failure analysis

Exact outcome requires both the expected status and normalized scalar value. Diagnostic flags below can overlap; they describe saved traces, not causal proof. No holdout was modified or used to retrain.

## validation

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| consistent | 6/20 | 20/20 |
| abstain | 19/20 | 20/20 |
| conflict | 13/20 | 20/20 |
| incident | 16/20 | 20/20 |

Observed error flags: wrong_status: 19, wrong_value: 8.

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

**train_val-0002-hi** (consistent, hi): expected answered / 406; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 406, "cites": ["NOTION-V2-TR-219", "SLACK-V2-TR-219"], "stale_source": "NOTION-V2-TR-219"}
```

**train_val-0002-hinglish** (consistent, hinglish): expected answered / 406; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 406, "cites": ["NOTION-V2-TR-219", "SLACK-V2-TR-219"], "stale_source": "NOTION-V2-TR-219"}
```

## test_synth

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| conflict | 175/200 | 200/200 |
| incident | 45/60 | 60/60 |
| abstain | 38/60 | 60/60 |
| consistent | 32/80 | 80/80 |

Observed error flags: wrong_status: 96, wrong_value: 57, unnecessary_abstention: 17, cites_staging_record: 8, returned_stale_value: 2, tool_error: 1.

### Saved trace examples

**holdout_synth-0001-te** (incident, te): expected answered / 15.0; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
```

**holdout_synth-0003-hinglish** (incident, hinglish): expected answered / 2; flags: wrong_status, wrong_value, cites_staging_record.

```json
{"status": "conflict_resolved", "value": 11, "cites": ["INC-V2-TS-001", "NOTION-V2-TS-145-STG", "PR-V2-TS-145", "SLACK-V2-TS-103"], "stale_source": "NOTION-V2-TS-145-STG"}
```

**holdout_synth-0003-te** (incident, te): expected answered / 2; flags: wrong_status, wrong_value, unnecessary_abstention.

```json
{"status": "abstain", "value": null, "cites": [], "stale_source": null}
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
| consistent | 6/20 | 20/20 |
| abstain | 13/15 | 15/15 |
| conflict | 36/50 | 50/50 |
| incident | 9/15 | 15/15 |

Observed error flags: wrong_status: 24, wrong_value: 22, unnecessary_abstention: 7, cites_staging_record: 2.

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
{"status": "conflict_resolved", "value": 33, "cites": ["NOTION-V2-OSS-012", "PR-V2-OSS-012"], "stale_source": "NOTION-V2-OSS-012"}
```

**holdout_repo_style-0000-te** (consistent, te): expected answered / 33; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 33, "cites": ["NOTION-V2-OSS-012", "PR-V2-OSS-012"], "stale_source": "NOTION-V2-OSS-012"}
```

**holdout_repo_style-0003-en** (consistent, en): expected answered / 30; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 30, "cites": ["NOTION-V2-OSS-178", "PR-V2-OSS-178"], "stale_source": "NOTION-V2-OSS-178"}
```

**holdout_repo_style-0003-hi** (consistent, hi): expected answered / 30; flags: wrong_status.

```json
{"status": "conflict_resolved", "value": 30, "cites": ["NOTION-V2-OSS-178", "PR-V2-OSS-178"], "stale_source": "NOTION-V2-OSS-178"}
```

