---
license: cc-by-nc-4.0
base_model: CohereLabs/tiny-aya-fire
library_name: transformers
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

# OneDesk — Historical v1 SFT merged

## Overview

OneDesk is a multilingual company-knowledge agent built on **Tiny Aya Fire (3.35B)**. It reconciles runbooks, GitHub PRs, Slack deployment records and live SQL data, and can chain time, conversion and arithmetic tools. Users can ask in English, Hindi (Devanagari/Latin), Hinglish, and Telugu (native/Latin).

This repository contains **Historical v1 SFT merged**, evaluated or retained as described below on the original v1 explicit-routing benchmark. Repository names preserve the original DriftGuard experiment identifiers; OneDesk is the presentation name.

## Benchmark results

| Check | Result |
|---|---|
| Full holdout evaluation for this exact export | Not measured |

V1 explicit-routing benchmark; v2 results do not apply. Merged export was not evaluated on the full holdout.

V1 explicit-routing benchmark; v2 results do not apply. Merged export was not evaluated on the full holdout.

Exact outcome requires the right status and normalized value. Strict outdated-doc catch also requires the correct stale page and all gold citations retrieved and cited. Confidence intervals use 10,000 semantic-case cluster resamples. Translations share cases.

## Intended use

Research on evidence-grounded multilingual tool calling, retrieval, stale-document reconciliation and read-only incident calculations. Nine logical MCP interfaces are available: Notion, GitHub, Slack, SQL, time, conversion, arithmetic, weather and calendar. The latter two test routing immunity.

## Load the standalone export

Install compatible `transformers`, `peft`, `accelerate`, `torch` and `safetensors`; the recorded experiment used Transformers 4.57.6 and PEFT 0.17.1.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Standalone v1 merged export (no separate LoRA load).
repo = "Revanth-ml/onedesk-tiny-aya-fire-sft-merged"
# Pin the saved weight revision shown in the Provenance section.
revision = "9747926dfe35d4a7ff10761c8caec3c1714496b2"
tokenizer = AutoTokenizer.from_pretrained(repo, revision=revision)
model = AutoModelForCausalLM.from_pretrained(
    repo, revision=revision, dtype=torch.float16, device_map="auto"
)
model.eval()
```

This snippet loads weights only. Full agent evaluation needs the OneDesk router, active tool schemas and tool-result feedback loop. Use the project’s local-demo/evaluation entry points to execute tool calls. Local NF4 deployment uses a separate numerical path from the BF16 benchmark.

## Training recipe

Historical v1 SFT: 34 optimizer steps, 360 train and 40 validation trajectories, effective batch 16, 544 rounded exposures and a 1,536-token budget. Rank-16/alpha-32 LoRA with assistant-only supervision. The merged export is a separate numerical deployment path.

## Toolkit chain

CuratorKIT 0.1.21 exact-deduplicates model-visible prompts. AgentTune 1.1.4 runs assistant-only SFT and live multi-turn GRPO through the project compatibility backend. AuditKIT 1.1.7 scores actual saved tool episodes. The final selected recipe uses 60-step SFT, followed by 80 active G6 GRPO updates; validation selected update 40. A separate 120-step full SFT model is the strongest overall-accuracy control. The historical weak/collapsed and v1 repositories have their own recipes and are not the final selected policy.

## Provenance

- Base: `CohereLabs/tiny-aya-fire` at `73500c80fcb6c8bea3e830c21d5d2920249a0e1a`.
- Saved weight revision in this repository: `9747926dfe35d4a7ff10761c8caec3c1714496b2`.
- Local artifact path in the project: `checkpoints/tiny-aya-fire-sft-merged`.
- Owner and teammate: [@Revanth-ml](https://huggingface.co/Revanth-ml).
- Companion frozen data: [driftguard-mcp-v2-data](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-v2-data).
- Final study logs: [driftguard-mcp-warmup-runs](https://huggingface.co/datasets/Revanth-ml/onedesk-mcp-warmup-runs).

## Limitations and license

The worlds and repo-style records are constructed fixtures, not live company connectors or verified upstream Git histories. The final GRPO policy improves strict stale catch over full SFT while having lower overall holdout accuracy and lower required-server chain compliance. Overall GRPO gains over warmup have paired intervals including zero. Final-update 80 has no separate complete holdout benchmark. An on-premises deployment can keep evidence local only when connectors and logging follow that boundary; the model does not guarantee privacy or correctness.

Original synthetic datasets are licensed under **CC-BY-4.0** and original project code under **Apache-2.0**; third-party code retains its own license. The model and adapters are under **CC BY-NC 4.0**, retaining the base model’s attribution and noncommercial conditions. This card does not grant commercial rights. Historical v1 NF4 VRAM/speed results do not establish final v2 NF4 quality.
