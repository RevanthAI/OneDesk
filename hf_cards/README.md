# OneDesk — prepared Hugging Face cards

Local generation and dry-run do not use network calls or credentials. All remote operations require explicit `--publish`.

**Model Collection:** [Revanth-ml/onedesk-models-and-experimental-controls](https://huggingface.co/collections/Revanth-ml/onedesk-models-and-experimental-controls-6af97221a617ddc3326204a6)

**Data Collection:** [Revanth-ml/onedesk-data-and-experiment-evidence](https://huggingface.co/collections/Revanth-ml/onedesk-data-and-experiment-evidence-6af97225c0f1dc548b9ba8ce)

| Type | Published repository | Prepared card |
| --- | --- | --- |
| model | [Revanth-ml/onedesk-tiny-aya-fire-sft](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-sft) | [Historical v1 SFT adapter](model/onedesk-tiny-aya-fire-sft/README.md) |
| model | [Revanth-ml/onedesk-tiny-aya-fire-sft-merged](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-sft-merged) | [Historical v1 SFT merged](model/onedesk-tiny-aya-fire-sft-merged/README.md) |
| model | [Revanth-ml/onedesk-tiny-aya-fire-grpo-pilot](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-grpo-pilot) | [Historical v1 GRPO pilot](model/onedesk-tiny-aya-fire-grpo-pilot/README.md) |
| model | [Revanth-ml/onedesk-tiny-aya-fire-v2-sft](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-v2-sft) | [V2 weak SFT](model/onedesk-tiny-aya-fire-v2-sft/README.md) |
| model | [Revanth-ml/onedesk-tiny-aya-fire-v2-grpo](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-v2-grpo) | [V2 collapsed RL — negative-result control](model/onedesk-tiny-aya-fire-v2-grpo/README.md) |
| model | [Revanth-ml/onedesk-tiny-aya-fire-v2-1-sft](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-v2-1-sft) | [Full four-epoch SFT control](model/onedesk-tiny-aya-fire-v2-1-sft/README.md) |
| model | [Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-sft](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-sft) | [OneDesk protocol warmup · 60 steps](model/onedesk-tiny-aya-fire-v2-1-warmup-sft/README.md) |
| model | [Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val) | [OneDesk final agent · validation-selected update 40](model/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val/README.md) |
| model | [Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-final](https://huggingface.co/Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-final) | [OneDesk final-update ablation · update 80](model/onedesk-tiny-aya-fire-v2-1-warmup-grpo-final/README.md) |
| dataset | [Revanth-ml/onedesk-mcp-v2-data](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-v2-data) | [Frozen benchmark](dataset/onedesk-mcp-v2-data/README.md) |
| dataset | [Revanth-ml/onedesk-mcp-warmup-runs](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-warmup-runs) | [Recorded experiment artifacts](dataset/onedesk-mcp-warmup-runs/README.md) |
| dataset | [Revanth-ml/onedesk-mcp-v2-runs](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-v2-runs) | [Recorded experiment artifacts](dataset/onedesk-mcp-v2-runs/README.md) |
| dataset | [Revanth-ml/onedesk-mcp-v2-1-runs](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-v2-1-runs) | [Recorded experiment artifacts](dataset/onedesk-mcp-v2-1-runs/README.md) |
| dataset | [Revanth-ml/onedesk-mcp-training-runs](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-training-runs) | [Recorded experiment artifacts](dataset/onedesk-mcp-training-runs/README.md) |
| dataset | [Revanth-ml/onedesk-mcp-grpo-runs](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-grpo-runs) | [Recorded experiment artifacts](dataset/onedesk-mcp-grpo-runs/README.md) |

```bash
.venv/bin/python scripts/prepare_hf_repos.py --dry-run
# When ready:
.venv/bin/python scripts/prepare_hf_repos.py --publish
# Optional OneDesk rename:
# .venv/bin/python scripts/prepare_hf_repos.py --publish --rename-prefix onedesk
```

Publishing makes the listed run repositories and their existing contents public; review PLAN.json and those repositories before invoking it. Two historical planned-but-untrained v2.1 model names are intentionally excluded. Original synthetic datasets are CC-BY-4.0; original project code is Apache-2.0; model weights/adapters retain CC BY-NC 4.0. Collections are created only by publish; URLs are saved to PUBLISH_RECEIPT.json and printed. Publication automatically updates both collection URLs in README.md.
