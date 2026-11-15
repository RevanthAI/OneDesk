# V2 evaluation failure analysis

Exact outcome requires both the expected status and normalized scalar value. Diagnostic flags below can overlap; they describe saved traces, not causal proof. No holdout was modified or used to retrain.

## test_synth

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| conflict | 2/200 | 156/200 |
| incident | 0/60 | 19/60 |
| abstain | 0/60 | 39/60 |
| consistent | 0/80 | 62/80 |

Observed error flags: wrong_value: 274, invalid_final_format: 124, wrong_status: 121, returned_stale_value: 1.

### Saved trace examples

**holdout_synth-0000-en** (conflict, en): expected conflict_resolved / 3836; flags: wrong_value.

```json
{"status": "conflict_resolved", "value": 100, "cites": ["production_incidents:incident_id=12345,service_name=statement-worker,environment=production"], "stale_source": "notion-mcp/search_notion?query=statement-worker+rate_limit_rpm"}
```

**holdout_synth-0000-hi** (conflict, hi): expected conflict_resolved / 3836; flags: invalid_final_format.

```json
{}
```

**holdout_synth-0000-hinglish** (conflict, hinglish): expected conflict_resolved / 3836; flags: wrong_value.

```json
{"status": "conflict_resolved", "value": "rate_limit_rpm superseded", "cites": ["operational_docs", "release_trail"], "stale_source": "operational_docs"}
```

**holdout_synth-0000-te** (conflict, te): expected conflict_resolved / 3836; flags: wrong_value.

```json
{"status": "conflict_resolved", "value": "rate_limit_rpm=1000 RPM", "cites": ["production_incidents#service-worker#environment#rate_limit_rpm"], "stale_source": "notion-mcp#production_rate_limit#service-worker#environment"}
```

**holdout_synth-0001-en** (incident, en): expected answered / 15.0; flags: wrong_value.

```json
{"status": "answered", "value": "$1,200.00", "cites": ["production_incidents(incident_id='INC-V2-TS-000',environment='production')", "unit-converter-mcp(convert_unit(value=1,from_unit='hour',to_unit='day'))", "math-mcp(calculate(expression='1200 * 1'))"], "stale_source": null}
```

**holdout_synth-0001-hi** (incident, hi): expected answered / 15.0; flags: invalid_final_format.

```json
{}
```

## repo_style

| Task kind | Correct / total | Valid final format |
|---|---:|---:|
| consistent | 0/20 | 17/20 |
| abstain | 0/15 | 12/15 |
| conflict | 0/50 | 41/50 |
| incident | 0/15 | 4/15 |

Observed error flags: wrong_value: 74, wrong_status: 34, invalid_final_format: 26, returned_stale_value: 3.

### Saved trace examples

**holdout_repo_style-0000-en** (consistent, en): expected answered / 33; flags: wrong_status, wrong_value.

```json
{"status": "conflict_resolved", "value": 30, "cites": ["https://docs.pydantic.dev/latest/usage/pydantic_validator/#timeout"], "stale_source": "https://docs.pydantic.dev/latest/usage/pydantic_validator/#timeout"}
```

**holdout_repo_style-0000-hi** (consistent, hi): expected answered / 33; flags: wrong_status, wrong_value.

```json
{"status": "conflict_resolved", "value": 30, "cites": ["production timeout_sec: 30s (documented in deployment evidence)"], "stale_source": "notion-mcp"}
```

**holdout_repo_style-0000-hinglish** (consistent, hinglish): expected answered / 33; flags: wrong_status, wrong_value.

```json
{"status": "conflict_resolved", "value": "timeout_sec superseded by operational docs", "cites": ["operational_docs"], "stale_source": "release_trail"}
```

**holdout_repo_style-0000-te** (consistent, te): expected answered / 33; flags: invalid_final_format.

```json
{}
```

**holdout_repo_style-0001-en** (abstain, en): expected abstain / None; flags: wrong_status, wrong_value.

```json
{"status": "conflict_resolved", "value": 50, "cites": ["active_services.circuit_breaker_pct"], "stale_source": "notion-mcp"}
```

**holdout_repo_style-0001-hi** (abstain, hi): expected abstain / None; flags: wrong_status, wrong_value.

```json
{"status": "conflict_resolved", "value": "Circuit Breaker Percentage: 0%", "cites": ["asgi-hedger.circuit_breaker_pct"], "stale_source": "notion-mcp/search_notion"}
```

