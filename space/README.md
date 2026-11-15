---
title: OneDesk MCP Enterprise Agent
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.49.1
python_version: '3.10'
app_file: app.py
pinned: true
license: apache-2.0
models:
- CohereLabs/tiny-aya-fire
- Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val
datasets:
- Revanth-ml/onedesk-mcp-v2-data
- Revanth-ml/onedesk-mcp-warmup-runs
tags:
- mcp
- grpo
- multilingual
- tool-calling
---

# OneDesk · Multilingual company knowledge, with evidence

Browse **2,500 real recorded model episodes**: five checkpoints × 500 frozen holdout tasks. Inspect current production settings, stale runbooks, SQL/incident chains and calibrated refusals across English, Hindi, Hinglish and Telugu.

The instant trace browser needs no model downloads or GPU. The separate **Live** button loads the pinned, license-gated Tiny Aya Fire base and final LoRA adapter on demand, then executes real in-memory SQLite/MCP tools. CUDA uses BF16 when supported, with NF4/FP16 compute on GPUs below 12 GiB; CPU uses BF16 and can be slow. ZeroGPU access depends on available quota. No paid inference API is called.

Edits to the question or active server set are live sandbox experiments: frozen benchmark badges are disabled for those edits. The instant button always shows the original selected holdout question's saved episode and labels it as recorded.

## Benchmark

| Combined holdout | Base | Warmup SFT | Full SFT | Final OneDesk |
| --- | --- | --- | --- | --- |
| Exact outcome · 500 tasks | 0.4% | 70.8% | 77.0% | 74.8% |
| Strict stale catch · 250 conflicts | 0.0% | 70.4% | 61.2% | 75.6% |
| Verified citation F1 · 425 evidence tasks | 0.0% | 88.3% | 93.2% | 87.6% |

Full SFT remains stronger on overall accuracy and exhaustive chain completeness. All company records and repo-style cases are constructed fixtures, not live enterprise connectors or independently verified historical OSS drift.

[GitHub / full report](https://github.com/RevanthAI/OneDesk) · [Model collection](https://huggingface.co/collections/Revanth-ml/onedesk-models-and-experimental-controls-6af97221a617ddc3326204a6) · [Data collection](https://huggingface.co/collections/Revanth-ml/onedesk-data-and-experiment-evidence-6af97225c0f1dc548b9ba8ce)

Code: Apache-2.0. Original synthetic data: CC-BY-4.0. Base model and adapters: **CC-BY-NC-4.0**, including noncommercial restrictions. Space metadata licenses the app code, not the model weights. OneDesk is a hackathon prototype unrelated to the commercial OneDesk helpdesk product.

## Gated model access

The Live button is enabled only when the owner configures an authorized `HF_TOKEN` in Space Settings → Secrets. Prefer a dedicated read token with accepted Tiny Aya Fire access. The deployment script never stores a token unless explicitly invoked with `--configure-model-secret`; secrets are never committed as files. Recorded traces work anonymously without this setup. This account uses T4 hosting with a 15-minute idle sleep; T4 runs FP16 because it does not support BF16.
