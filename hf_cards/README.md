# OneDesk — prepared Hugging Face cards

Local generation and dry-run do not use network calls or credentials. All remote operations require explicit `--publish`.

|Type|Existing repository|Prepared card|Optional target|
|---|---|---|---|
|model|Revanth-ml/driftguard-tiny-aya-fire-sft|[Historical v1 SFT adapter](model/driftguard-tiny-aya-fire-sft/README.md)|Revanth-ml/onedesk-tiny-aya-fire-sft|
|model|Revanth-ml/driftguard-tiny-aya-fire-sft-merged|[Historical v1 SFT merged](model/driftguard-tiny-aya-fire-sft-merged/README.md)|Revanth-ml/onedesk-tiny-aya-fire-sft-merged|
|model|Revanth-ml/driftguard-tiny-aya-fire-grpo-pilot|[Historical v1 GRPO pilot](model/driftguard-tiny-aya-fire-grpo-pilot/README.md)|Revanth-ml/onedesk-tiny-aya-fire-grpo-pilot|
|model|Revanth-ml/driftguard-tiny-aya-fire-v2-sft|[V2 weak SFT](model/driftguard-tiny-aya-fire-v2-sft/README.md)|Revanth-ml/onedesk-tiny-aya-fire-v2-sft|
|model|Revanth-ml/driftguard-tiny-aya-fire-v2-grpo|[V2 collapsed RL — negative-result control](model/driftguard-tiny-aya-fire-v2-grpo/README.md)|Revanth-ml/onedesk-tiny-aya-fire-v2-grpo|
|model|Revanth-ml/driftguard-tiny-aya-fire-v2-1-sft|[Full four-epoch SFT control](model/driftguard-tiny-aya-fire-v2-1-sft/README.md)|Revanth-ml/onedesk-tiny-aya-fire-v2-1-sft|
|model|Revanth-ml/driftguard-tiny-aya-fire-v2-1-warmup-sft|[OneDesk protocol warmup · 60 steps](model/driftguard-tiny-aya-fire-v2-1-warmup-sft/README.md)|Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-sft|
|model|Revanth-ml/driftguard-tiny-aya-fire-v2-1-warmup-grpo-best-val|[OneDesk final agent · validation-selected update 40](model/driftguard-tiny-aya-fire-v2-1-warmup-grpo-best-val/README.md)|Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val|
|model|Revanth-ml/driftguard-tiny-aya-fire-v2-1-warmup-grpo-final|[OneDesk final-update ablation · update 80](model/driftguard-tiny-aya-fire-v2-1-warmup-grpo-final/README.md)|Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-final|
|dataset|Revanth-ml/driftguard-mcp-v2-data|[Frozen benchmark](dataset/driftguard-mcp-v2-data/README.md)|Revanth-ml/onedesk-mcp-v2-data|
|dataset|Revanth-ml/driftguard-mcp-warmup-runs|[Recorded experiment artifacts](dataset/driftguard-mcp-warmup-runs/README.md)|Revanth-ml/onedesk-mcp-warmup-runs|
|dataset|Revanth-ml/driftguard-mcp-v2-runs|[Recorded experiment artifacts](dataset/driftguard-mcp-v2-runs/README.md)|Revanth-ml/onedesk-mcp-v2-runs|
|dataset|Revanth-ml/driftguard-mcp-v2-1-runs|[Recorded experiment artifacts](dataset/driftguard-mcp-v2-1-runs/README.md)|Revanth-ml/onedesk-mcp-v2-1-runs|
|dataset|Revanth-ml/driftguard-mcp-training-runs|[Recorded experiment artifacts](dataset/driftguard-mcp-training-runs/README.md)|Revanth-ml/onedesk-mcp-training-runs|
|dataset|Revanth-ml/driftguard-mcp-grpo-runs|[Recorded experiment artifacts](dataset/driftguard-mcp-grpo-runs/README.md)|Revanth-ml/onedesk-mcp-grpo-runs|


```bash
.venv/bin/python scripts/prepare_hf_repos.py --dry-run
# When ready:
.venv/bin/python scripts/prepare_hf_repos.py --publish
# Optional OneDesk rename:
# .venv/bin/python scripts/prepare_hf_repos.py --publish --rename-prefix onedesk
```

Publishing makes the listed run repositories and their existing contents public; review PLAN.json and those repositories before invoking it. Two historical planned-but-untrained v2.1 model names are intentionally excluded. Original synthetic datasets are CC-BY-4.0; original project code is Apache-2.0; model weights/adapters retain CC BY-NC 4.0. Collections are created only by publish; URLs are saved to PUBLISH_RECEIPT.json and printed. Publication automatically updates both collection URLs in REPORT.md.
