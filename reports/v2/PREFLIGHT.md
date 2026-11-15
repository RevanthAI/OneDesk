# V2 pre-flight safeguards

The user approved the existing v2 review and all frozen inputs. No dataset regeneration was performed. The complete approval snapshot covers 19 files; the supplied SHA256SUMS covers 15 artifacts.

## Verification

- Main test suite: 58 passed after the safeguards.
- Independent publication-facing v2 tests: 15 passed, including the added BF16 temperature-order regression.
- SFT token preflight refuses any truncation at 2,560 tokens. Cloud training consumed exactly 240 rows in one epoch (15 optimizer steps, effective batch 16).
- All new inference, training and model validation execute on Hugging Face L40S. Local work only checks source, analyzes downloaded traces, and retrieves artifacts.

## Reward gate

Evidence-gated successful incident calculations must execute successful calls to every declared required server, including DB, time/conversion and math. Correct mental-math or SQL-arithmetic answers without the required utility chain receive zero reward. Failed calls cannot satisfy the chain. Config audits require Notion, their gold-authoritative deployment channel(s), and DB for incident lookup; unrelated deployment channels are not mandatory. Abstention is exempt. Exact-outcome accuracy remains separately reported from procedural compliance.

## Active sampling

Four rollouts form a group. Zero-variance groups are logged as skipped attempts, never counted as optimizer updates. Retries 1–16 use temperature 0.8; 17–32 use 0.95. After exhaustion of one kind, sampling falls back to remaining unsaturated kinds. Only budget exhaustion across all four kinds raises NoActiveAdvantage; the cloud wrapper preserves the last adapter and labels the run early-stopped. This is budgeted sampling, not a proof that every possible stochastic rollout has zero variance. Accepted sampling temperature is used consistently in policy probabilities.

## Precision correction and continuation

Before any v2 GRPO ran, a BF16 scoring-order issue was found: temperature must be applied after logits are promoted to FP32, matching Transformers generation. The first cloud job was stopped at its saved SFT handoff. Its completed Base evaluation and one-epoch SFT are reused by the corrected pinned job. No pre-fix GRPO updates are included. SCORER_FIX_HANDOFF.json and both cloud job records retain provenance.

## Output isolation

Runtime: src_v2/. Results: reports_v2/. Local adapters: checkpoints_v2/. README_v2.md and the v2-only release packager define publication inputs. Historical experiments remain available separately. Repositories are private; no public publication has occurred.
