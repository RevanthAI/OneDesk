# Tiny Aya Fire: SFT adapter evaluation

Base model: `CohereLabs/tiny-aya-fire` at `73500c80fcb6c8bea3e830c21d5d2920249a0e1a`. SFT adapter: `checkpoints/tiny-aya-fire-sft-adapter`. Live model actions were used; no oracle actions were substituted.

Quantization: 4bit (NF4 with double quantization for 4bit); compute: float16; GPU: NVIDIA GeForce RTX 2070. Greedy decoding, max 384 new tokens/turn, at most 6 tool calls/task. XML-wrapped JSON protocol; malformed output ends the episode without repair.

Intervals: 95% percentile bootstrap, 10,000 resamples of semantic cases with translations kept together. Degenerate [0,0] or [100,100] intervals do not imply certainty outside this benchmark. All Hindi/Telugu queries are romanized.

| Metric | Synthetic holdout (400) | Constructed OSS-style holdout (100) |
|---|---:|---:|
| Stale-doc catch (%) | 87.00 [80.36, 92.65] | 68.00 [61.62, 74.49] |
| Exact outcome (%) | 85.25 [80.75, 89.50] | 68.00 [61.62, 74.49] |
| Verified citation F1, evidence tasks (%) | 89.41 [85.63, 92.93] | 100.00 [100.00, 100.00] |
| Abstention precision (%) | 69.44 [50.79, 83.15] | N/A (zero denominator) |
| Abstention recall (%) | 83.33 [72.50, 93.18] | N/A (zero denominator) |
| Unplugged DB abstention recall (%) | 64.29 [54.17, 75.00] | N/A (zero denominator) |
| Distractor immunity, exposed tasks (%) | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| Tool calls per successful task | 1.89 [1.76, 2.02] | 2.00 [2.00, 2.00] |
| Valid final format (%) | 99.00 [98.00, 99.75] | 100.00 [100.00, 100.00] |
| Stale value returned, conflict tasks (%) | 5.00 [2.40, 7.89] | 0.00 [0.00, 0.00] |

| Language | Synthetic exact outcome (%) | OSS-style exact outcome (%) |
|---|---:|---:|
| en | 88.00 [81.00, 94.00] | 100.00 [100.00, 100.00] |
| hi | 83.00 [75.00, 90.00] | 0.00 [0.00, 0.00] |
| hinglish | 85.00 [78.00, 91.02] | 100.00 [100.00, 100.00] |
| te | 85.00 [78.00, 92.00] | 72.00 [52.00, 88.00] |

## Work completed

- Deterministic train/test worlds, isolated SQLite rollouts, strict protocol parsing, read-only queries and optional FastMCP wrapper.
- Evidence-consuming oracle, specified reward and separately named hardened variant, adversarial tests.
- Four-language SFT and curriculum datasets, CuratorKIT exact deduplication, actual AgentTune trajectory JSONL round-trip into AuditKIT, SHA-256 freeze.
- Live GPU base-model tool episodes, raw generations and tool outputs, AuditKIT custom scoring, resumable runs and cluster bootstrap metrics.

## Scope and limitations

The OSS-style cases are constructed fixtures. They contain no verified upstream PRs or real doc snapshots; these scores do not establish real-repository transfer. A source-backed OSS holdout remains future work.

Train/test services, employees, config values and question-template sets are disjoint. Odd/even config partitions enforce numeric separation within plausible overlapping ranges, rather than disjoint magnitude ranges. Synthetic evaluation has 100 semantic cases translated four ways; the OSS-style set has 30 cases. These are not 500 independent cases.

Original reward: always-abstain scores 0.1925, oracle 1.3550 on the 100-case adversarial suite. The requested thresholds cannot hold under that formula and task mix. The optional hardened variant reduces always-abstain to -0.0200. Correct unsupported guesses retain base reward under the original formula. Neither variant is claimed to be ungameable.



Romanized Hindi and Hinglish are distinct prompt groups but related registers. Template translations have not had independent native-speaker review. NF4 quantization may affect quality; this is a quantized deployment baseline, not an unquantized reference result.

Stale catch requires correct status/value, the correct stale page and both required citations actually retrieved. Exact outcome checks status/value. Citation precision includes hallucinated IDs in its denominator. Headline citation F1 excludes citation-free abstention; the AuditKIT all-item diagnostic includes zeros for those tasks.

## Runtime

```json
{
  "model": "CohereLabs/tiny-aya-fire",
  "revision": "73500c80fcb6c8bea3e830c21d5d2920249a0e1a",
  "quantization": "4bit",
  "max_new_tokens": 384,
  "max_tool_calls": 6,
  "batch_size": 1,
  "seed": 42,
  "temperature": 0.0,
  "dataset_hashes": {
    "curation_funnel.json": "9ccf35c212138b4281ac4812bb5ae9205a7b12674683f28673becf9464631637",
    "holdout_repo_style_100_frozen.jsonl": "bafc7eae5563216963cf36e284d376a32f7be95369b3b266af8412a70e6af253",
    "holdout_synth_400_frozen.jsonl": "4fc790e517f4f5c34c887a68c2a4a95de0eb98347eeaac855f3e0e4e861e8ef9",
    "train_grpo_stage1.jsonl": "ac9a066588db779fb37f866858d0592cf64560e214cc87be2ffcffb4c86b589d",
    "train_grpo_stage2.jsonl": "88b917119182c1941a49078fd02352a356cdd3eb79ae02350c95670b095a010a",
    "train_sft_400.jsonl": "4f6926280ecbc6aa5b78a9ee5804351cb991c5be3d894d90b75bc1905dcf78a0",
    "train_sft_agenttune_trajectories.jsonl": "237b733ac831be5ecedbc505f38868b039dc6a3de548304a558d943af41c05a4",
    "world_repo_style.json": "986244ef0d7c7f7755d67bfcb461ec5bbbf66856d2328e4727c64b455717830f",
    "world_test_synth.json": "8917e2520ba04b2809c65004e45035507bca2efc56bd383089c13306fc10a544",
    "world_train.json": "2f68a305b5eeb515442f6564a9fb2399b5f5291bd2172e4697d9b29a1594cf44"
  },
  "limit": 0,
  "adapter_path": "checkpoints/tiny-aya-fire-sft-adapter",
  "adapter_sha256": {
    "adapter_config.json": "2f6408bcf9536ba9f24a9e2fe9032ec32adfd7210d01126de8b5055118051826",
    "adapter_model.safetensors": "a3cd9058f25334d724c906521a75b168fe4b07b5dcedcfaf005ebbd0ab321b39"
  },
  "sdpa_expand_kv": true,
  "device_map": {
    "": "cuda:0"
  },
  "gpu": "NVIDIA GeForce RTX 2070",
  "compute_dtype": "float16",
  "peak_vram_allocated_gib": 2.823578357696533,
  "peak_vram_reserved_gib": 3.154296875,
  "oom_splits": 0,
  "generated_tokens": 64664,
  "input_tokens": 1447512,
  "generation_seconds": 8179.517127176856,
  "generated_tokens_per_second": 7.905601149137596,
  "generation_batches": 1421,
  "scoring_session_elapsed_seconds": 8228.351252466004,
  "versions": {
    "torch": "2.8.0+cu128",
    "transformers": "4.57.6",
    "bitsandbytes": "0.50.2",
    "agenttune": "1.1.4",
    "auditkit": "1.1.7",
    "curatorkit": "0.1.21"
  }
}
```

## Completion reasons

```json
{
  "test_synth": {
    "final_answer": 396,
    "malformed_output": 4
  },
  "repo_style": {
    "final_answer": 100
  }
}
```

Evidence: `data/SHA256SUMS`, `reports/reward_hacking.md`, raw episode JSONL, metric JSONL and AuditKIT output folders.

## Validation and reward audit

Verification covers world isolation, oracle outcomes, reward loopholes, prompt immutability, memory recovery, paired cohort matching, and frozen world/data checksums. The original reward and optional hardened variant were audited over 100 semantic cases:

| Policy | Specified reward | Evidence-gated reward |
|---|---:|---:|
| AlwaysAbstainPolicy | 0.1925 | -0.0200 |
| DumpAllNumbersPolicy | 0.0500 | -0.2000 |
| TrustOnlyNotionLazyPolicy | -0.0450 | -0.1200 |
| SpamAllToolsThenGuessPolicy | 0.0500 | -0.2000 |
| HallucinateCitationsWithoutToolsPolicy | 0.0500 | -0.2000 |
| HonestOraclePolicy | 1.3550 | 1.3550 |

The local search tools use conjunctive token matching over entity/parameter identifiers. Natural-language filler in a search query can therefore return an empty result. This is a constrained local benchmark, not a measurement against production Notion/Slack search. Missing-entity fixtures have recognizable synthetic names; human-reviewed, more natural prompts and a source-backed repository holdout are further benchmark improvements.


Toolkit commits are recorded in `toolkit_revisions.json`; setup and scope are in `README.md`; compatibility and GPU restart details are in `reports/IMPLEMENTATION_NOTES.md`. Model and toolkit primary sources: [Tiny Aya Fire](https://huggingface.co/CohereLabs/tiny-aya-fire), [AgentTune](https://github.com/Lexsi-Labs/AgentTune), [AuditKIT](https://github.com/Lexsi-Labs/AuditKIT), [CuratorKIT](https://github.com/Lexsi-Labs/CuratorKIT).

SFT used the actual AgentTune trainer lifecycle with a project backend; see `reports/cloud_sft/SFT_REPORT.md`. The MCP tools run in-process. These results evaluate the adapter over an NF4 base when quantization is 4bit; the separately merged model is a different inference path.

The constructed OSS fixtures include 17 questions from five cases with implausible percentage values above 100. They are retained for frozen-set comparability; see `reports/precision_full/FINDINGS.md`.
