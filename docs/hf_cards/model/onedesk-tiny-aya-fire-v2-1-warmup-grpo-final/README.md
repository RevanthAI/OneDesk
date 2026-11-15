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

# OneDesk — OneDesk final-update ablation · update 80

## Overview

OneDesk is a multilingual company-knowledge agent built on **Tiny Aya Fire (3.35B)**. It reconciles runbooks, GitHub PRs, Slack deployment records and live SQL data, and can chain time, conversion and arithmetic tools. Users can ask in English, Hindi (Devanagari/Latin), Hinglish, and Telugu (native/Latin).

This repository contains **OneDesk final-update ablation · update 80**, evaluated or retained as described below on the frozen data_v2 company-knowledge benchmark. Published repositories use the OneDesk name; frozen task IDs and historical run metadata retain their original experiment identifiers.

## Benchmark results

| Check | Result |
| --- | --- |
| Full holdout evaluation for this exact export | Not measured |

Update 80 saved separately; selected update 40 has the reported holdout scores.

Update 80 saved separately; selected update 40 has the reported holdout scores.

Exact outcome requires the right status and normalized value. Strict outdated-doc catch also requires the correct stale page and all gold citations retrieved and cited. Confidence intervals use 10,000 semantic-case cluster resamples. Translations share cases.

## Intended use

Research on evidence-grounded multilingual tool calling, retrieval, stale-document reconciliation and read-only incident calculations. Nine logical MCP interfaces are available: Notion, GitHub, Slack, SQL, time, conversion, arithmetic, weather and calendar. The latter two test routing immunity.

## Load the LoRA adapter

Install compatible `transformers`, `peft`, `accelerate`, `torch` and `safetensors`; the recorded experiment used Transformers 4.57.6 and PEFT 0.17.1.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

adapter = "Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-final"
# Weights are pinned independently of subsequent README-only updates.
adapter_revision = "b006ec346e48807afd23030abf17b599adfcf71f"
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

Saved final update 80 from the same 40+40-update recipe. Validation at update 80 was 78.75%; update 40 was better at 80.00%. No separate full holdout evaluation of this final-update export was run.

## Toolkit chain

CuratorKIT 0.1.21 exact-deduplicates model-visible prompts. AgentTune 1.1.4 runs assistant-only SFT and live multi-turn GRPO through the project compatibility backend. AuditKIT 1.1.7 scores actual saved tool episodes. The final selected recipe uses 60-step SFT, followed by 80 active G6 GRPO updates; validation selected update 40. A separate 120-step full SFT model is the strongest overall-accuracy control. The historical weak/collapsed and v1 repositories have their own recipes and are not the final selected policy.

## Provenance

- Base: `CohereLabs/tiny-aya-fire` at `73500c80fcb6c8bea3e830c21d5d2920249a0e1a`.
- Saved weight revision in this repository: `b006ec346e48807afd23030abf17b599adfcf71f`.
- Local artifact path in the project: `checkpoints/v2_2/grpo_final_adapter`.
- Owner and teammate: [@Revanth-ml](https://huggingface.co/Revanth-ml).
- Companion frozen data: [onedesk-mcp-v2-data](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-v2-data).
- Final study logs: [onedesk-mcp-warmup-runs](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-warmup-runs).

## Limitations and license

The worlds and repo-style records are constructed fixtures, not live company connectors or verified upstream Git histories. The final GRPO policy improves strict stale catch over full SFT while having lower overall holdout accuracy and lower required-server chain compliance. Overall GRPO gains over warmup have paired intervals including zero. Final-update 80 has no separate complete holdout benchmark. An on-premises deployment can keep evidence local only when connectors and logging follow that boundary; the model does not guarantee privacy or correctness.

Original synthetic datasets are licensed under **CC-BY-4.0** and original project code under **Apache-2.0**; third-party code retains its own license. The model and adapters are under **CC BY-NC 4.0**, retaining the base model’s attribution and noncommercial conditions. This card does not grant commercial rights. Historical v1 NF4 VRAM/speed results do not establish final v2 NF4 quality.

Adapter SHA-256: `16b135a64f95c3fb74c83a9fd59a3e3c55a1adff48db998549cdaad410e764b8`.

## Published collections

**Model Collection:** [Revanth-ml/onedesk-models-and-experimental-controls](https://huggingface.co/collections/Revanth-ml/onedesk-models-and-experimental-controls-6af97221a617ddc3326204a6)

**Data Collection:** [Revanth-ml/onedesk-data-and-experiment-evidence](https://huggingface.co/collections/Revanth-ml/onedesk-data-and-experiment-evidence-6af97225c0f1dc548b9ba8ce)
