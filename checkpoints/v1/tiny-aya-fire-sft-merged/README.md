---
license: cc-by-nc-4.0
base_model: CohereLabs/tiny-aya-fire
pipeline_tag: text-generation
---

# DriftGuard Tiny Aya Fire SFT

LoRA SFT of Cohere Labs Tiny Aya Fire using deterministic enterprise tool-use trajectories. This is an SFT checkpoint; GRPO has not been applied. Base revision: 73500c80fcb6c8bea3e830c21d5d2920249a0e1a. Trained on 360 trajectories with 40 validation trajectories held out by semantic case. Training settings and validation losses are recorded in the run artifacts.
