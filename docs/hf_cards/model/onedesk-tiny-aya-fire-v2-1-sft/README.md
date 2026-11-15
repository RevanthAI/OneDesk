---
license: cc-by-nc-4.0
base_model: CohereLabs/tiny-aya-fire
library_name: peft
pipeline_tag: text-generation
language:
- en
- hi
- te
tags:
- agenttune
- curatorkit
- auditkit
- mcp
- grpo
- tool-calling
- multilingual
- tiny-aya-fire
inference: false
---

# OneDesk — Full four-epoch SFT control

## Overview

OneDesk is a multilingual company-knowledge agent built on **Tiny Aya Fire (3.35B)**. It reconciles runbooks, GitHub PRs, Slack deployment records and live SQL data, and can chain time, conversion and arithmetic tools. Users can ask in English, Hindi (Devanagari/Latin), Hinglish, and Telugu (native/Latin).

This repository contains **Full four-epoch SFT control**, evaluated or retained as described below on the frozen data_v2 company-knowledge benchmark. Published repositories use the OneDesk name; frozen task IDs and historical run metadata retain their original experiment identifiers.

## Benchmark results

| Cohort | Queries | Exact outcome % [95% CI] | Strict outdated-doc catch % [95% CI] | Valid final format % [95% CI] |
| --- | --- | --- | --- | --- |
| Validation | 80 | 73.75 [56.25, 90.00] | 30.00 [0.00, 67.86] | 97.50 [92.50, 100.00] |
| Synthetic holdout | 400 | 77.25 [70.00, 84.00] | 63.50 [50.56, 75.52] | 100.00 [100.00, 100.00] |
| Repo-style holdout | 100 | 76.00 [61.39, 88.89] | 52.00 [25.00, 77.08] | 100.00 [100.00, 100.00] |

Exact outcome requires the right status and normalized value. Strict outdated-doc catch also requires the correct stale page and all gold citations retrieved and cited. Confidence intervals use 10,000 semantic-case cluster resamples. Translations share cases.

## Intended use

Research on evidence-grounded multilingual tool calling, retrieval, stale-document reconciliation and read-only incident calculations. Nine logical MCP interfaces are available: Notion, GitHub, Slack, SQL, time, conversion, arithmetic, weather and calendar. The latter two test routing immunity.

## Load the LoRA adapter

Install compatible `transformers`, `peft`, `accelerate`, `torch` and `safetensors`; the recorded experiment used Transformers 4.57.6 and PEFT 0.17.1.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

adapter = "Revanth-ml/onedesk-tiny-aya-fire-v2-1-sft"
# Weights are pinned independently of subsequent README-only updates.
adapter_revision = "bf94f4cc6ec420752205859e6d63c7f83b85f14d"
tokenizer = AutoTokenizer.from_pretrained(adapter, revision=adapter_revision)
base = AutoModelForCausalLM.from_pretrained(
    "CohereLabs/tiny-aya-fire",
    revision="73500c80fcb6c8bea3e830c21d5d2920249a0e1a",
    dtype=torch.bfloat16,  # use float16 on hardware without BF16 support
    device_map="auto",
)
model = PeftModel.from_pretrained(base, adapter, revision=adapter_revision)
model.eval()
```

This snippet loads weights only. Full agent evaluation needs the OneDesk router, active tool schemas and tool-result feedback loop. Use the project’s local-demo/evaluation entry points to execute tool calls. Local NF4 deployment uses a separate numerical path from the BF16 benchmark.

## Training recipe

Fresh four-epoch SFT: 120 steps, effective batch 8, 960 exposures, LR 1.5e-4 and cosine decay to zero, context 2,560 with zero truncation. Validation selected update 120.

## Toolkit chain

CuratorKIT 0.1.21 exact-deduplicates model-visible prompts. AgentTune 1.1.4 runs assistant-only SFT and live multi-turn GRPO through the project compatibility backend. AuditKIT 1.1.7 scores actual saved tool episodes. The final selected recipe uses 60-step SFT, followed by 80 active G6 GRPO updates; validation selected update 40. A separate 120-step full SFT model is the strongest overall-accuracy control. The historical weak/collapsed and v1 repositories have their own recipes and are not the final selected policy.

## Provenance

- Base: `CohereLabs/tiny-aya-fire` at `73500c80fcb6c8bea3e830c21d5d2920249a0e1a`.
- Saved weight revision in this repository: `bf94f4cc6ec420752205859e6d63c7f83b85f14d`.
- Local artifact path in the project: `checkpoints_v2_1/sft_adapter`.
- Owner and teammate: [@Revanth-ml](https://huggingface.co/Revanth-ml).
- Companion frozen data: [onedesk-mcp-v2-data](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-v2-data).
- Final study logs: [onedesk-mcp-warmup-runs](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-warmup-runs).

## Limitations and license

The worlds and repo-style records are constructed fixtures, not live company connectors or verified upstream Git histories. The final GRPO policy improves strict stale catch over full SFT while having lower overall holdout accuracy and lower required-server chain compliance. Overall GRPO gains over warmup have paired intervals including zero. Final-update 80 has no separate complete holdout benchmark. An on-premises deployment can keep evidence local only when connectors and logging follow that boundary; the model does not guarantee privacy or correctness.

Original synthetic datasets are licensed under **CC-BY-4.0** and original project code under **Apache-2.0**; third-party code retains its own license. The model and adapters are under **CC BY-NC 4.0**, retaining the base model’s attribution and noncommercial conditions. This card does not grant commercial rights. Historical v1 NF4 VRAM/speed results do not establish final v2 NF4 quality.

Adapter SHA-256: `ec7cddc8a4791a7f740087026b4664518d6e99c05b051cee03f970c0091148d4`.

## Published collections

**Model Collection:** [Revanth-ml/onedesk-models-and-experimental-controls](https://huggingface.co/collections/Revanth-ml/onedesk-models-and-experimental-controls-6af97221a617ddc3326204a6)

**Data Collection:** [Revanth-ml/onedesk-data-and-experiment-evidence](https://huggingface.co/collections/Revanth-ml/onedesk-data-and-experiment-evidence-6af97225c0f1dc548b9ba8ce)
