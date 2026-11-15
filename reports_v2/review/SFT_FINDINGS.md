# V2 cold-start SFT findings

The fresh one-epoch SFT consumed 240 examples in 15 optimizer updates, with zero truncation at 2,560 tokens. Teacher-forced validation loss fell from 0.72708 to 0.09261. Closed-loop validation accuracy was only 18/80 (22.5%; 95% semantic-case bootstrap CI 7.5–40.0%). This gap shows that low token loss on reference trajectories is not sufficient evidence of reliable closed-loop decisions: generated tool choices and observations can differ from the reference path.

| Frozen holdout | Base exact outcome | SFT exact outcome |
|---|---:|---:|
| Synthetic, 400 rows / 100 cases | 0.50% | 15.00% [10.50, 20.00] |
| OSS-style, 100 rows / 26 cases | 0.00% | 16.00% [7.52, 25.74] |

These are matched cloud BF16 evaluations. They are separate from the earlier v1 NF4/FP16 results.

## Observed failure categories

On synthetic data, 340 SFT answers failed the exact status-and-scalar outcome criterion. Among these failures, 99 cited a STAGING-ONLY record, 155 had the wrong status, 195 had the wrong scalar, 100 lacked a valid final answer, 26 encountered tool errors, and 19 exhausted the tool budget. Categories overlap. The model returned the stale value on 26 conflict items. Consult v2_sft_fire/FAILURE_ANALYSIS.json for exact saved examples; these are descriptive flags rather than an assertion that one cause explains every error.

Synthetic exact outcomes by task kind: conflict 14/200; consistent 15/80; incident 8/60; abstain 23/60. Thus the compact SFT leaves headroom on all task types. Stale catch is stricter than exact outcome because it also requires the correct stale-page identification: SFT stale catch was 4.0% on synthetic conflicts and 14.0% on OSS-style conflicts.

The varied staging/sibling search results, branching deployment evidence, unseen facts and varied incident calculations are materially harder than v1. Both the data and SFT budget changed, so the v1→v2 accuracy drop cannot be causally assigned to any single change. No additional SFT epoch or holdout-specific tuning was introduced to raise these scores. The approved GRPO experiment proceeds from this exact SFT adapter.
