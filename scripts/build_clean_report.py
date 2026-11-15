"""Build the concise OneDesk README/report; retain detailed evidence in docs/."""
from pathlib import Path
import json
import re
from clean_report_data import (ROOT, BASE, summaries, table, ci, percent, language_examples, roi, protect, digest)
from publication_markdown import publication as published_state, format_gfm, url_link
from text_leak_check import summary as audit_summary

FINAL_REPO='Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val'


def update_full_report(audit):
    """Only add/update the audit note in the preserved complete snapshot."""
    path=ROOT/'docs/FULL_REPORT.md'
    if not path.exists():
        raise FileNotFoundError('Preserve the complete report in docs/FULL_REPORT.md before trimming.')
    text=path.read_text()
    begin='<!-- TEXT_LEAK_AUDIT:BEGIN -->';end='<!-- TEXT_LEAK_AUDIT:END -->'
    note=begin+'\n\n### CPU Text-Level Overlap Check\n\n'+audit_summary(audit)+'\n\nExact counts, nearest matches and scalar-collision examples: [TEXT_LEAK_AUDIT.json](../reports_submission/TEXT_LEAK_AUDIT.json).\n\n'+end+'\n\n'
    if begin in text:
        text=re.sub(re.escape(begin)+r'.*?'+re.escape(end)+r'\n*',lambda m:note,text,flags=re.S)
    else:
        text=text.replace('## 4. Experiments Run, What Failed, and How We Found the Winning Recipe',note+'## 4. Experiments Run, What Failed, and How We Found the Winning Recipe',1)
    path.write_text(format_gfm(text))


def build(publication=None, output_path=None):
    protect();ss=summaries();final=ss['Final OneDesk · selected update 40']
    audit=json.loads((ROOT/'reports_submission/TEXT_LEAK_AUDIT.json').read_text())
    pub=publication if publication is not None else published_state()
    parts=[]
    def add(text):parts.append(text.strip()+'\n')
    add('# OneDesk (formerly DriftGuard-MCP): One Multilingual Workspace to Query Your Company’s Knowledge Base')
    add('*Track 3: Agentic Fine-Tuning — Problem Statements Covered: **1, 2, 4, 5, 6, and 9***')
    add(f'**Which model to use:** [{FINAL_REPO}](https://huggingface.co/{FINAL_REPO}) *(Base: `{BASE}` 3.35B · Full tables & checksums in [docs/FULL_REPORT.md](docs/FULL_REPORT.md) and [SUBMISSION_DOSSIER.md](SUBMISSION_DOSSIER.md))*')
    add('**Declaration of work done outside the hackathon:** **None.** All world generators, synthetic datasets, CuratorKIT/AgentTune/AuditKIT integrations, training runs, and evaluations were built from scratch during the hackathon window.')
    add('**Naming note:** *OneDesk is an open-source hackathon research prototype (formerly named `DriftGuard-MCP`, which is why internal Python classes retain the `DriftGuard*` prefix) and is unrelated to the commercial OneDesk helpdesk software.*')
    add('## ⚡ For Judges: 60-Second Overview')
    add(table(['',''],[
        ['**Claim**','A local 3.35B model checks Notion, GitHub, Slack and SQL for current, cited answers in English, Hindi, Hinglish or Telugu.'],
        ['**Result**','Exact accuracy **0.5% → 75.8%** (synthetic, n=400), **0.0% → 71.0%** (repo-style, n=100); **100%** valid final format.'],
        ['**Strongest at**','Stale docs: **79.0% vs 63.5%** full SFT; **+15.5 pp [+5.5, +26.0]** synthetic and **+10.0 pp [+2.0, +20.4]** repo-style.'],
        ['**Caveat**','Full SFT is more accurate overall (**77.3% / 76.0%**); synthetic chain compliance trades off (**86.5% vs 97.4%**); all benchmark data is synthetic.'],
        ['**Cost & Compute**','**$1.22/1k audits** on L40S vs historical GPT-4o **$13.17**; v1 local NF4: **3.15 GiB**, $0 API fees; recorded compute **~12.05 L40S h**, **~$21.80** list-rate lower bound.']]))
    add('![Headline Results](figures/1_headline_success.png)')
    add('## 1. Problem Statement & Approach')
    add('A Hinglish employee asks for `loyalty-api`’s actual production `batch_size_mb`: the runbook says 154, a newer staging-only distractor says 286, and the production Slack update says 16. This `train_sft-0000-hinglish` protocol example shows the tool calls, cited answer and stale-page flag; the first query is shortened for readability.')
    add('''```xml
<tool_call>{"server":"notion-mcp","tool":"search_notion","arguments":{"query":"loyalty-api batch_size_mb"}}</tool_call>
<tool_call>{"server":"slack-mcp","tool":"search_slack","arguments":{"query":"loyalty-api batch_size_mb"}}</tool_call>
<final_answer>{"status":"conflict_resolved","value":16,"cites":["NOTION-V2-TR-105","SLACK-V2-TR-105"],"stale_source":"NOTION-V2-TR-105"}</final_answer>
```''')
    add('![Unified 9-Server MCP Workspace](figures/0_workspace_architecture.png)')
    selected={r['language']+':'+r['script']:r for r in language_examples()}
    add(table(['Script style','Frozen example'],[[key,selected[key]['question']] for key in ('en:latin','te:native')]))
    add('All six script styles: [full report](docs/FULL_REPORT.md#six-language-and-script-styles--verbatim-frozen-prompts).')
    add('![Multilingual Reach](figures/2_multilingual_reach.png)')
    add('## 2. Hackathon Repos Used')
    add('![Lexsi Toolkit Pipeline](figures/0_toolkit_pipeline.png)')
    add(table(['Toolkit','Role and features'],[
        ['**CuratorKIT 0.1.21**','`DataSample` + `ExactDeduplicator.run`: **1,955 → 1,700** tasks; 255 injected exact duplicates rejected.'],
        ['**AgentTune 1.1.4**','`Step`/`Trajectory` serialization, `SFTTrainerBase` warmup and `TrlAgenticGrpo` lifecycle with executed live MCP rollouts.'],
        ['**AuditKIT 1.1.7**','580 episodes/checkpoint: trajectory import, outcome/citation scorers and native tool-selection, validity and redundancy metrics.']]))
    add('Compatibility fixes:\n\n- Bridge AgentTune’s missing `_generate_single_turn` hook to TRL 0.23.1 live rollouts.\n- Load dependency-light `agenttune.agentic` leaf modules instead of eager optional stacks.\n- Explicit BF16 autocast for unwrapped PEFT decoder log-probability scoring.')
    add('## 3. Data Creation, Curation & Evaluation Strategy')
    add(table(['Scenario','Required behavior'],[
        ['Consistent knowledge','Match production scope; verify agreement despite staging/sibling distractors.'],
        ['Outdated documents','Reconcile Notion against newer PR/hotfix evidence; identify and cite the stale page.'],
        ['Database/calculation chains','Execute SQLite SELECT; derive duration or convert kg→lb / GB→MiB; calculate rounded incident cost.'],
        ['Safe refusal','Abstain for absent entities or an unavailable explicitly required database.']]))
    add(audit_summary(audit)+' A **2,560-token SFT window preserves every trajectory (0 truncations)**; evaluation uses 4,096 tokens, with [full split/token details and the audit](docs/FULL_REPORT.md#cpu-text-level-overlap-check).')
    add('- **Exact accuracy:** correct status plus normalized scalar.\n- **Strict stale catch:** correct answer, correct stale page, every gold source retrieved and cited.\n- **Citation/tool compliance:** verified citation F1, required-server checks and AuditKIT metrics.\n- **Refusal calibration:** necessary versus false refusals, including unplugged-source recall.')
    add('## 4. Experiments Run, What Failed & Winning Recipe')
    add('![Training Journey](figures/3_training_journey.png)')
    add('### Lazy Refusal Trap\n\nOnly 15 SFT steps left a weak starting policy. Long RL then favored comparatively less-penalized refusal over malformed or stale answers. At 340 updates it refused **77.3%** of synthetic queries and caught **0%** of stale docs.')
    add('### Clone Bottleneck\n\nFull four-epoch SFT reached **77.3% / 76.0%** holdout accuracy. Its RL pilot accepted only **6/72 groups (8.3%)**; 62 of 66 rejected zero-variance groups had identical token sequences. Strict synthetic stale catch was **63.5%**, exposing a gap beyond overall accuracy.')
    add('### Winning Recipe\n\nTwo-epoch protocol warmup followed by anti-collapse, positive-anchor G6 GRPO completed **80 active updates**, accepting **23.4%** of groups. Validation selected update **40** at **80.0%** accuracy, with no abstention-collapse guard triggered. Selected holdout accuracy reached **75.8% / 71.0%**, and strict stale catch **79.0% / 62.0%**.')
    keys=[('Base','Base'),('Warmup SFT · 60 steps','Warmup SFT · 60 steps'),('Final OneDesk · selected update 40','Final OneDesk · GRPO update 40'),('Full SFT · 120 steps','Full 4-Epoch SFT · 120 steps')]
    add(table(['Checkpoint','Synthetic % [95% CI]','Repo-style % [95% CI]','Validation % [95% CI]'],[[label]+[ci(ss[key][sp]['metrics']['exact_outcome']) for sp in ('test_synth','repo_style','validation')] for key,label in keys]))
    add('[Full seven-checkpoint, multilingual and AuditKIT tables](docs/FULL_REPORT.md).')
    add('![Cost and Privacy ROI](figures/4_cost_and_privacy_roi.png)')
    add(table(['Serving option','USD /1k audits','USD /100k audits'],[[r['name'],f"${r['cost']/100:.2f}",f"${r['cost']:,.2f}"] for r in roi() if r['key'] in ('edge','l40s','gpt4o')]))
    add('**Hackathon Compute Used:** recorded **12.05 L40S hours + 2.35 A100 minutes ≈ $21.80** continuous list-rate lower bound.\n\nIncludes observed training/evaluation work; excludes uncovered setup/charged intervals and minute rounding, so it is not an invoice total ([accounting](reports_submission/COMPUTE_ACCOUNTING.json)).')
    add('## 5–8. Models, Datasets & Public HF Collections')
    add(f'- **Primary Final Model:** [{FINAL_REPO}](https://huggingface.co/{FINAL_REPO}) (base: [{BASE}](https://huggingface.co/{BASE}), rev `73500c80`).\n- **Public Model Collection (all 9 artifacts & controls):** '+url_link(pub['model_collection_url'])+'.\n- **Public Data Collection (frozen benchmark & rollout journals):** '+url_link(pub['data_collection_url'])+'.\n- **Licenses:** model weights/adapters `CC-BY-NC-4.0` · synthetic data `CC-BY-4.0` ([LICENSE-DATA.md](LICENSE-DATA.md)) · code `Apache-2.0` ([LICENSE](LICENSE)).')
    add('[Nine-row revision table, six split hashes and all 19 protected-file checksums](docs/FULL_REPORT.md#5-models-used-and-their-licenses).')
    add('## 9. With More Credits: Approach, Before and After Results')
    add('**Targets, not measured results:**')
    add(table(['Priority','Measured before','Next change','Future target'],[
        ['Complete evidence','Chain: **86.47% / 74.12%**','Enforce three-server completeness; harder audit trails','**>96%** chain compliance'],
        ['Unplugged DB','Recall: **'+percent(final['test_synth']['metrics']['unplugged_recall']['estimate'],2)+'% / '+percent(final['repo_style']['metrics']['unplugged_recall']['estimate'],2)+'%**','Oversample unavailable-source contrasts','Fewer missed/false refusals'],
        ['Overall accuracy','**75.75% / 71.00%**','Matched-compute warmup/reward/sampling sweep','**83%+**, aspirational'],
        ['Confirmation','One selected recipe','Multiple seeds; fresh source-backed cohort','Replicated paired gains']]))
    add('## 10. Repo Layout & Run Instructions')
    add('''```text
├── src_v2_2/          # Final MCP runtime, AgentTune backends and AuditKIT scorer
├── src/              # v2 facts-first generator, oracle and CuratorKIT pipeline
├── data_v2/          # Frozen 1,700 tasks, worlds and SHA-256 manifest
├── checkpoints_v2_2/ # sft_warmup_adapter, grpo_best_val_adapter, grpo_final_adapter
├── figures/          # Benchmark charts and static architecture diagrams
├── docs/             # FULL_REPORT.md: complete tables and checksums
└── tests_v2_2/       # Final-recipe tests; 120 tests total across four test folders
```''')
    add('From the project root with the pinned toolkits/dependencies installed; use fresh output paths. The training/evaluation modules expose Python functions, so the commands below call those functions directly; GPU stages need suitable CUDA hardware.')
    add('''```bash
# CPU data curation: new directory, never overwrite frozen data_v2/.
python -c "from src.v2_dataset import build; build('data_rebuild')"

# GPU: two-epoch SFT warmup, then live 40+40-update GRPO.
python - <<'PYTHON'
from src_v2_2.training import run_sft, run_grpo
adapter, metadata = run_sft('runs/repro_sft')
run_grpo(adapter, 'runs/repro_grpo', metadata)
PYTHON

# GPU: AuditKIT on validation and both frozen holdouts.
python - <<'PYTHON'
from peft import PeftModel
from src_v2_2.backend import load_base
from src_v2_2.evaluate_auditkit import evaluate
model, tokenizer = load_base()
model = PeftModel.from_pretrained(model, 'runs/repro_grpo/best_val_adapter')
evaluate(model, tokenizer, 'runs/repro_eval',
         splits=('validation', 'test_synth', 'repo_style'))
PYTHON

# Download selected weights, then run one local NF4 example (GPU).
python - <<'PYTHON'
from huggingface_hub import snapshot_download
snapshot_download('Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val',
    revision='016676680121b4dd90ec6026978de7ee1cdb1271',
    local_dir='checkpoints_v2_2/grpo_best_val_adapter')
PYTHON
python -m src_v2_2.local_demo --adapter checkpoints_v2_2/grpo_best_val_adapter

# CPU audit and complete regression suite.
python scripts/text_leak_check.py
CUDA_VISIBLE_DEVICES='' python -m pytest tests tests_v2 tests_v2_1 tests_v2_2 -q
```''')
    add('## 11. Honest Limitations & Teammates Tagged')
    add('- Constructed fixtures, modulo-3 configuration values and correlated template translations; no verified live-OSS transfer. Scalar answers recur across different facts, as the [text audit](reports_submission/TEXT_LEAK_AUDIT.json) reports.\n- Overall GRPO-over-warmup holdout gain intervals include zero; repeated validation selection and one run need fresh confirmation.\n- Prefer **full SFT for overall accuracy**, selected **GRPO for strict stale catch**; chain completeness, incident reasoning and unplugged-DB handling still need work.\n- Warmup length, group size and temperature changed together; zero variance does not prove full-distribution entropy collapse.\n- Local VRAM/speed is measured on the **v1 NF4 adapter**; v2 results are BF16. ROI excludes hardware/operations, uses historical API prices, and does not establish equal API accuracy; privacy requires appropriate connectors and logging.\n- Model weights retain noncommercial terms; third-party licenses apply. No public Gradio app is established, and future targets are unmeasured.')
    add('**Teammates tagged:** [@Revanth-ml](https://huggingface.co/Revanth-ml).')
    text=format_gfm('\n'.join(parts))
    output=Path(output_path) if output_path is not None else ROOT/'REPORT.md';output.write_text(text)
    if output_path is None:
        (ROOT/'README.md').write_bytes(output.read_bytes());update_full_report(audit)
    target=output.parent if output_path is not None else ROOT/'reports_submission/clean_assets';target.mkdir(exist_ok=True)
    meta=dict(project='OneDesk',words=len(text.split()),sha256=digest(output),source='Saved results plus CPU TEXT_LEAK_AUDIT',no_inference=True,no_paid_jobs=True)
    (target/'REPORT_METADATA.json').write_text(json.dumps(meta,indent=2)+'\n')
    protect();print(json.dumps(meta));return text

if __name__=='__main__':build()
