"""Build the OneDesk README and maintain the detailed evidence in docs/."""
from pathlib import Path
import json
import re
from clean_report_data import (ROOT, BASE, summaries, combined_holdouts, table, ci, percent, language_examples, roi, protect, digest)
from publication_markdown import publication as published_state, format_gfm, url_link
from dataset_narrative import data_section
from roi_analysis import narrative as roi_narrative, scenarios as roi_scenarios

FINAL_REPO='Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val'
SPACE_URL='https://huggingface.co/spaces/Revanth-ml/OneDesk'
NAMING_NOTE='Formerly DriftGuard-MCP, hence the `DriftGuard*` class names in `src/v2_2/`. Unrelated to the commercial OneDesk helpdesk software.'


def details(summary, body):
    return '<details>\n<summary><strong>'+summary+'</strong></summary>\n\n'+body.strip()+'\n\n</details>'


def validity_note(saved):
    weak=[saved['Weak SFT · 15 steps'][sp]['auditkit_headline']['tool_call_validity'] for sp in ('test_synth','repo_style')]
    early=saved['Early RL · 120 updates']['test_synth']['auditkit_headline']['tool_call_validity']
    return ('Format percentages count valid structured final answers. AuditKIT records **100% tool-call validity for the warmup, final, and full-SFT checkpoints** on both holdouts; '
            f'the early 15-step SFT scores **{percent(min(weak))}–{percent(max(weak))}%**, and Stage 1 scores **{percent(early,2)}%** on synthetic. '
            'Pooled means use metric-specific denominators; paired confidence intervals remain split-specific.')


def compact_data(audit):
    expanded=data_section(audit)
    deep='### 3.1'+expanded.split('### 3.1',1)[1].split('### 3.4',1)[0]
    summary=('We generated deterministic Python facts for **60 services and 80 incidents**; no LLM invented gold facts.\n'
             'Question templates cover **six language/script styles**, and **CuratorKIT 0.1.21** deduplicated **1,955 → 1,700 tasks**.\n'
             'A live tool-executing oracle verified outcomes and evidence before trajectory export; training and holdout cases are disjoint.')
    scenarios=table(['Scenario','Required behavior'],[
        ['Consistent','Verify production agreement while ignoring staging/sibling distractors.'],
        ['Conflicting / Outdated','Find newer production evidence, cite it and flag the stale page.'],
        ['Database & Calculation Chains','Execute SQL, time/unit conversions and rounded incident-cost calculations.'],
        ['Safe Refusal','Abstain for missing entities or an unavailable required source.']])
    metrics=('- **Exact accuracy:** correct status plus normalized value.\n'
             '- **Strict stale catch:** correct answer and stale-page flag; every gold source retrieved and cited.\n'
             '- **Citation & tool-chain compliance:** verified citation F1, successful required-server calls and AuditKIT routing diagnostics.\n'
             '- **Refusal calibration & 10,000-sample case bootstrap:** track false/necessary refusals and uncertainty, keeping translations clustered by semantic case.')
    return '\n\n'.join(['## 3. Data Creation, Curation & Evaluation Strategy',summary,scenarios.strip(),metrics,
        details('Deep dive: How the data was built (facts-first world, live oracle, CuratorKIT funnel & v1→v2 anti-shortcut constraints)',deep)])


def compact_roi():
    data=roi_scenarios();edge=next(r for r in data if r['key']=='edge');cloud=next(r for r in data if r['key']=='l40s')
    counts=json.loads((ROOT/'reports/submission/ROI_VERIFIED_BENCHMARK.json').read_text())['token_audit']['token_counts']['o200k_base']['per_episode']
    names={'edge':'Local workstation · RTX 2070 NF4','l40s':'Self-hosted L40S · BF16','t4':'Cloud T4-small · NF4 scenario',
           'gpt4o_cached':'Closed API · GPT-4o (prefix cached)','gpt4o':'Closed API · GPT-4o (uncached)'}
    basis={
        'edge':f"Measured final v2.1 NF4 (`{edge['output_tps']:.2f} out tok/s`, `{edge['vram_gib']:.2f} GiB` VRAM); electricity only (`175W × $0.10/kWh`)",
        'l40s':f"Measured HF Jobs BF16 (`{cloud['output_tps']:.1f} out tok/s`, `{cloud['hours_100000']:.2f} GPU-h/100k` at `$1.80/h`)",
        't4':'Unmeasured T4; token-adjusted local NF4 proxy at `$0.40/h`',
        'gpt4o_cached':f"`o200k_base` counts (`{counts['input_tokens']:,.0f}` in / `{counts['output_tokens']:,.0f}` out) with 50% eligible prefix-cache discount",
        'gpt4o':'Historical uncached `$2.50/M` input + `$10/M` output'}
    summary=('Serving scenario: **100,000 multi-turn audits/month**; local electricity excludes hardware and operations.\n'
             'Local timing uses **20 distinct final-adapter NF4 cases**; L40S throughput comes from **580 recorded BF16 episodes**.\n'
             '**Hackathon compute used:** ~**12.05 L40S GPU-hours + 2.35 A100 minutes ≈ $21.80** at list rates '
             '([recorded compute lower bound](reports/submission/COMPUTE_ACCOUNTING.json)).')
    visible=table(['Serving option','USD / 1k audits','USD / 100k audits','Basis'],[
        [names[r['key']],f"${r['cost_1000']:,.2f}",f"${r['cost_100000']:,.2f}",basis[r['key']]] for r in data])
    return '\n\n'.join([summary,visible.strip(),details('Deep dive: Rule 5 throughput (tokens/sec), GPU runtime hours, live v2.1 NF4 timing & prefix-caching methodology',roi_narrative())])


def update_full_report(audit):
    """Refresh Section 3 while preserving detailed experimental evidence."""
    path=ROOT/'docs/FULL_REPORT.md'
    if not path.exists():
        raise FileNotFoundError('Preserve the complete report in docs/FULL_REPORT.md before trimming.')
    text=path.read_text()
    if '## Submission info\n' not in text:
        space_info='## Submission info\n'+table(['Artifact','Public link'],[['Interactive Space',f'[Revanth-ml/OneDesk]({SPACE_URL})']])+'\n'
        text=text.replace('## ⚡ For Judges: 60-Second Overview',space_info+'## ⚡ For Judges: 60-Second Overview',1)
    text=text.replace('No public Gradio application is established by these artifacts.','The public OneDesk Space provides recorded traces; live MCP inference requires owner-configured gated-model access.')
    text=text.replace('The public OneDesk Space provides recorded traces and opt-in live MCP inference.','The public OneDesk Space provides recorded traces; live MCP inference requires owner-configured gated-model access.')
    text=re.sub(r'## 3\. Data Creation, Curation & Evaluation Strategy\n.*?(?=## 4\.)',lambda _:data_section(audit,prefix='../'),text,flags=re.S)
    text=re.sub(r'### Enterprise ROI & Privacy\n.*?(?=## 5\.)',lambda _:'### Enterprise ROI & Privacy\n\n![Cost and Privacy ROI](../figures/4_cost_and_privacy_roi.png)\n\n'+roi_narrative(prefix='../'),text,flags=re.S)
    local=next(s for s in roi_scenarios() if s['key']=='edge')
    text=re.sub(r'^\| On-premises & affordable \|.*$',lambda _:f"| On-premises & affordable | Final-adapter NF4 timing uses **{local['vram_gib']:.2f} GiB reserved VRAM** on 20 local tasks; $0 API fees. L40S is **$1.22/1k audits** at **$1.80/GPU-hour**; the detailed table includes cached/uncached API scenarios and measured throughput. Connector/logging controls define the privacy boundary. |",text,flags=re.M)
    text=text.replace('local 3.15 GiB and speed measurements are from the v1 NF4 adapter, while v2 quality/throughput was measured in BF16.', 'final-adapter local NF4 timing/memory is measured on 20 stratified tasks; complete v2 quality results use BF16. The historical 3.15 GiB measurement belongs to v1.')
    # Keep the full evidence expanded while aligning the final navigation to eight sections.
    for old,new in [
        ('## 6. Datasets and Benchmarks Used and Their Licenses','### Datasets and Benchmarks Used and Their Licenses'),
        ('## 7. Model Artifacts Public, as an HF Collection','### Model Artifacts Public, as an HF Collection'),
        ('## 8. Data Artifacts Public, as an HF Collection','### Data Artifacts Public, as an HF Collection'),
        ('## 9. With More Credits: Approach, Before and After Results','## 6. With More Credits: Approach, Before and After Results'),
        ('## 10. Honest Limitations','## 8. Honest Limitations')]:
        text=text.replace(old,new)
    if '## 7. Repo Layout & Run Instructions' not in text:
        text=text.replace('### Reproducibility commands','## 7. Repo Layout & Run Instructions\n\n'+NAMING_NOTE+'\n\n### Reproducibility commands',1)
    note=validity_note(summaries())
    text=re.sub(r'Format percentages count valid structured final answers; AuditKIT independently records 100% tool-call validity for each trained stage on both holdouts\.[^\n]*',lambda _:note,text)
    marker='In the AuditKIT table, — means the native metric is absent from that saved headline, rather than a zero score.'
    if note not in text:text=text.replace(marker,marker+'\n\n'+note)
    path.write_text(format_gfm(text))


def update_article(audit):
    path=ROOT/'docs/HF_ARTICLE.md'
    if not path.exists():return
    image='![Multilingual results](https://raw.githubusercontent.com/RevanthAI/OneDesk/main/figures/2_multilingual_reach.png)\n\n'
    text=re.sub(r'## 3\. Data Creation, Curation & Evaluation Strategy\n.*?(?=## Three Lexsi toolkits in one pipeline)',lambda _:data_section(audit,article=True)+image,path.read_text(),flags=re.S)
    text=re.sub(r'## What would it cost to run internally\?\n.*?(?=## What we would do next)',lambda _:'## What would it cost to run internally?\n\n![ROI scenarios](https://raw.githubusercontent.com/RevanthAI/OneDesk/main/figures/4_cost_and_privacy_roi.png)\n\n'+roi_narrative(article=True),text,flags=re.S)
    path.write_text(format_gfm(text))


def build(publication=None, output_path=None):
    protect();ss=summaries();final=ss['Final OneDesk · selected update 40']
    audit=json.loads((ROOT/'reports/submission/TEXT_LEAK_AUDIT.json').read_text())
    pub=publication if publication is not None else published_state()
    parts=[]
    def add(text):parts.append(text.strip()+'\n')
    add('# OneDesk: One Multilingual Workspace to Query Your Company’s Knowledge Base')
    add('*Track 3 · Agentic Fine-Tuning · `CohereLabs/tiny-aya-fire` (3.35B) with CuratorKIT, AgentTune and AuditKIT*')
    add('## The problem')
    add("Company knowledge is split across Notion wikis, GitHub pull requests, Slack threads and SQL databases, and the newest-looking document is often a trap: a stale runbook that wasn't updated after yesterday's hotfix, or a `[STAGING-ONLY]` configuration page. Meanwhile, engineering and operations teams ask questions in English, Hindi (Devanagari and Latin), Hinglish and Telugu (native and Latin).")
    add('Organizations want to run compact, on-premises models (~3B parameters) so private code, incidents and database schemas never leave their infrastructure. However, out of the box, small models struggle with multi-turn tool use and strict output formatting: our base model lacks a valid structured final answer on 30% of benchmark episodes, calls the wrong tools, or fails multi-step SQL, unit-conversion and math chains—scoring just **0.4% exact accuracy** across our 500-task benchmark.')
    add('**Can a small, locally deployable 3.35B model learn to produce valid tool calls, find the current production answer, cite verified evidence, flag the outdated page, and refuse when a source is missing, using real tool calls instead of memorized answers?**')
    add('## Results')
    add('![Headline Results](figures/1_headline_success.png)')
    add('Combined performance across all **500 held-out queries** (400 synthetic + 100 repo-style; see [docs/FULL_REPORT.md](docs/FULL_REPORT.md) for separate split tables and 95% bootstrap CIs):')
    pooled=combined_holdouts(ss)
    stage_keys=['Base','Warmup SFT · 60 steps','Full SFT · 120 steps','Final OneDesk · selected update 40']
    result_rows=[]
    for label,metric in [('**Strict stale-doc catch** (`n=250` conflicts)','stale_catch'),('**Exact answer accuracy** (`n=500` all tasks)','exact_outcome'),('**Valid tool & response format** (`n=500`)','format_valid'),('**Verified citation F1** (`n=425` cited tasks)','verified_citation_f1'),('**Required-chain compliance** (`n=425` answerable)','required_chain_compliance')]:
        values=[percent(pooled[key][metric]['estimate'])+'%' for key in stage_keys]
        if metric=='stale_catch':values[-1]='**'+values[-1]+' (+14.4 pp vs Full SFT)**'
        elif metric=='format_valid':values[1:]=['**'+v+'**' for v in values[1:]]
        else:values[2]='**'+values[2]+'**'
        result_rows.append([label]+values)
    add(table(['Metric (Combined 500-Query Holdout)','Untrained Base','Warmup SFT (2-ep)','Full SFT (4-ep)','**OneDesk (Final RL)**'],result_rows))
    add('OneDesk improves strict stale-document catch over full 4-epoch SFT by **+14.4 pp pooled** (**+15.5 pp [+5.5, +26.0]** on synthetic and **+10.0 pp [+2.0, +20.4]** on repo-style), while reaching **100% valid tool-call and response formatting**. Full SFT stays slightly ahead on overall accuracy (`77.0%` vs `74.8%`) and exhaustive 3-server chain compliance, and all benchmark data is synthetic.')
    add(validity_note(ss))
    local=next(s for s in roi_scenarios() if s['key']=='edge');api=next(s for s in roi_scenarios() if s['key']=='gpt4o')
    add(f"The final adapter runs locally in NF4 (**{local['vram_gib']:.2f} GiB reserved VRAM**, 20-task timing sample). Self-hosted L40S serving is **$1.22 per 1k audits**, versus **${api['cost_1000']:.2f}** in the historical uncached GPT-4o same-string token scenario; cached billing is detailed below.")
    add('## Submission info')
    add('> **Where to look:** **Skim:** [Results](#results), then [Section 4 (Experiments)](#4-experiments-run-what-failed-and-how-we-found-the-winning-recipe) · **Verify:** [Section 7 (Repo Layout & Run Instructions)](#7-repo-layout--run-instructions) · **Depth:** Expand the `<details>` blocks below or read [`docs/FULL_REPORT.md`](docs/FULL_REPORT.md).')
    add(table(['',''],[
        ['Track','3, problem statements 1, 2, 4, 5, 6, 9'],
        ['Model to use',f'[onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val](https://huggingface.co/{FINAL_REPO})'],
        ['Public Space',f'[Revanth-ml/OneDesk]({SPACE_URL})'],
        ['Collections',f"[Models]({pub['model_collection_url']}) · [Data]({pub['data_collection_url']})"],
        ['Full report','[docs/FULL_REPORT.md](docs/FULL_REPORT.md)'],
        ['Work before the hackathon','None']]))
    add('Detailed submission reference: [docs/SUBMISSION_DOSSIER.md](docs/SUBMISSION_DOSSIER.md).')
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
    add(compact_data(audit))
    add('## 4. Experiments Run, What Failed, and How We Found the Winning Recipe')
    add('![Training Journey](figures/3_training_journey.png)')
    add('### Lazy Refusal Trap\n\nOnly 15 SFT steps left a weak starting policy. Long RL then favored comparatively less-penalized refusal over malformed or stale answers. At 340 updates it refused **77.3%** of synthetic queries and caught **0%** of stale docs.')
    add('### Clone Bottleneck\n\nFull four-epoch SFT reached **77.3% / 76.0%** holdout accuracy. Its RL pilot accepted only **6/72 groups (8.3%)**; 62 of 66 rejected zero-variance groups had identical token sequences. Strict synthetic stale catch was **63.5%**, exposing a gap beyond overall accuracy.')
    add('### Winning Recipe\n\nTwo-epoch protocol warmup followed by anti-collapse, positive-anchor G6 GRPO completed **80 active updates**, accepting **23.4%** of groups. Validation selected update **40** at **80.0%** accuracy, with no abstention-collapse guard triggered. Selected holdout accuracy reached **75.8% / 71.0%**, and strict stale catch **79.0% / 62.0%**.')
    keys=[('Base','Base'),('Warmup SFT · 60 steps','Warmup SFT · 60 steps'),('Final OneDesk · selected update 40','Final OneDesk · GRPO update 40'),('Full SFT · 120 steps','Full 4-Epoch SFT · 120 steps')]
    add(table(['Checkpoint','Synthetic % [95% CI]','Repo-style % [95% CI]','Validation % [95% CI]'],[[label]+[ci(ss[key][sp]['metrics']['exact_outcome']) for sp in ('test_synth','repo_style','validation')] for key,label in keys]))
    add('[Full seven-checkpoint, multilingual and AuditKIT tables](docs/FULL_REPORT.md).')
    add('### Enterprise ROI & Privacy')
    add('![Cost and Privacy ROI](figures/4_cost_and_privacy_roi.png)')
    add(compact_roi())
    add('## 5. Models, Datasets & Public HF Collections')
    add(f'- **Primary Final Model:** [{FINAL_REPO}](https://huggingface.co/{FINAL_REPO}) (base: [{BASE}](https://huggingface.co/{BASE}), rev `73500c80`).\n- **Public Model Collection (all 9 artifacts & controls):** '+url_link(pub['model_collection_url'])+'.\n- **Public Data Collection (frozen benchmark & rollout journals):** '+url_link(pub['data_collection_url'])+'.\n- **Licenses:** model weights/adapters `CC-BY-NC-4.0` · synthetic data `CC-BY-4.0` ([LICENSE-DATA.md](LICENSE-DATA.md)) · code `Apache-2.0` ([LICENSE](LICENSE)).')
    add('[Nine-row revision table, six split hashes and all 19 protected-file checksums](docs/FULL_REPORT.md#5-models-used-and-their-licenses).')
    add('## 6. With More Credits: Approach, Before and After Results')
    add('**Targets, not measured results:**')
    add(table(['Priority','Measured before','Next change','Future target'],[
        ['Complete evidence','Chain: **86.47% / 74.12%**','Enforce three-server completeness; harder audit trails','**>96%** chain compliance'],
        ['Unplugged DB','Recall: **'+percent(final['test_synth']['metrics']['unplugged_recall']['estimate'],2)+'% / '+percent(final['repo_style']['metrics']['unplugged_recall']['estimate'],2)+'%**','Oversample unavailable-source contrasts','Fewer missed/false refusals'],
        ['Overall accuracy','**75.75% / 71.00%**','Matched-compute warmup/reward/sampling sweep','**83%+**, aspirational'],
        ['Confirmation','One selected recipe','Multiple seeds; fresh source-backed cohort','Replicated paired gains']]))
    add('## 7. Repo Layout & Run Instructions')
    add(NAMING_NOTE)
    add('''```text
├── src/              # v1/, v2/, v2_1/, v2_2/ runtimes; provenance-listed sources stay here
├── data_v2/          # Frozen 1,700 tasks, worlds and SHA-256 manifest
├── checkpoints/      # v1/, v2/, v2_1/, v2_2/ adapters and metadata
├── reports/          # v1/, v2/, v2_1/, v2_2/, submission/ evidence
├── figures/          # Benchmark charts and static architecture diagrams
├── docs/             # Full report, dossier, hf_cards/ and archive/data_v1/
└── tests/            # v1/, v2/, v2_1/, v2_2/: 126 regression tests
```''')
    add('Canonical commands use `src.v2_2`; legacy imports remain supported. See [repository layout and source-provenance notes](docs/REPOSITORY_LAYOUT.md), including the two pre-existing source-checksum mismatches.')
    add('From the project root with the pinned toolkits/dependencies installed; use fresh output paths. The training/evaluation modules expose Python functions, so the commands below call those functions directly; GPU stages need suitable CUDA hardware.')
    add('''```bash
# CPU data curation: new directory, never overwrite frozen data_v2/.
python -c "from src.v2_dataset import build; build('data_rebuild')"

# GPU: two-epoch SFT warmup, then live 40+40-update GRPO.
python - <<'PYTHON'
from src.v2_2.training import run_sft, run_grpo
adapter, metadata = run_sft('runs/repro_sft')
run_grpo(adapter, 'runs/repro_grpo', metadata)
PYTHON

# GPU: AuditKIT on validation and both frozen holdouts.
python - <<'PYTHON'
from peft import PeftModel
from src.v2_2.backend import load_base
from src.v2_2.evaluate_auditkit import evaluate
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
    local_dir='checkpoints/v2_2/grpo_best_val_adapter')
PYTHON
python -m src.v2_2.local_demo --adapter checkpoints/v2_2/grpo_best_val_adapter

# CPU audit and complete regression suite.
python scripts/text_leak_check.py
python scripts/verify_roi_billing.py --local-files-only
CUDA_VISIBLE_DEVICES='' python -m pytest tests -q

# Local GPU timing of the final adapter on 20 distinct cases.
python scripts/benchmark_v2_1_roi.py
```''')
    add('## 8. Honest Limitations & Teammates Tagged')
    add('- Constructed fixtures, modulo-3 configuration values and correlated template translations; no verified live-OSS transfer. Scalar answers recur across different facts, as the [text audit](reports/submission/TEXT_LEAK_AUDIT.json) reports.\n- Overall GRPO-over-warmup holdout gain intervals include zero; repeated validation selection and one run need fresh confirmation.\n- Prefer **full SFT for overall accuracy**, selected **GRPO for strict stale catch**; chain completeness, incident reasoning and unplugged-DB handling still need work.\n- Warmup length, group size and temperature changed together; zero variance does not prove full-distribution entropy collapse.\n- Final-adapter local NF4 speed/memory is measured on 20 stratified episodes; full v2 accuracy results are BF16. ROI excludes hardware/operations, uses historical same-string API price estimates, and does not establish equal API accuracy; privacy requires appropriate connectors and logging.\n- Model weights retain noncommercial terms; third-party licenses apply. The public Space distinguishes recorded evidence from opt-in live runs; future targets remain unmeasured.')
    add('**Teammates tagged:** [@Revanth-ml](https://huggingface.co/Revanth-ml).')
    text=format_gfm('\n'.join(parts))
    output=Path(output_path) if output_path is not None else ROOT/'README.md';output.write_text(text)
    if output_path is None:
        update_full_report(audit)
        update_article(audit)
    target=output.parent if output_path is not None else ROOT/'reports/submission/clean_assets';target.mkdir(exist_ok=True)
    meta=dict(project='OneDesk',words=len(text.split()),sha256=digest(output),source='Saved results plus CPU TEXT_LEAK_AUDIT',no_inference=True,no_paid_jobs=True)
    (target/'REPORT_METADATA.json').write_text(json.dumps(meta,indent=2)+'\n')
    protect();print(json.dumps(meta));return text

if __name__=='__main__':build()
