"""Render evidence-backed dataset documentation without changing frozen inputs."""
from collections import Counter
import json
from clean_report_data import ROOT, table

SPLITS=[
 ('train_sft_240','Supervised protocol warmup (60 steps) & four-epoch control'),
 ('train_grpo_stage1','Final live multi-turn GRPO Stage 1 (updates 1–40)'),
 ('train_grpo_stage2','Final live multi-turn GRPO Stage 2 (updates 41–80)'),
 ('val_train_80','Checkpoint selection & >40% predicted-abstention collapse guard'),
 ('holdout_synth_400_frozen','Primary synthetic holdout evaluation'),
 ('holdout_repo_style_100_frozen','Out-of-domain constructed OSS repo-style holdout')]


def data_section(audit=None,prefix='',article=False):
    """Four subsections shared by README, the detailed report and HF Article."""
    def read(name):return json.loads((ROOT/'data_v2'/name).read_text())
    funnel=read('curation_funnel.json');tokens=read('token_length_audit.json');facts=read('AUDIT.json')
    if audit is None:audit=json.loads((ROOT/'reports/submission/TEXT_LEAK_AUDIT.json').read_text())
    def link(path,label=None):
        target=('https://github.com/RevanthAI/OneDesk/blob/main/'+path) if article else prefix+path
        return f'[{label or path}]({target})'
    candidates=sum(funnel[k]['input'] for k,_ in SPLITS);retained=sum(funnel[k]['kept'] for k,_ in SPLITS);rejected=sum(funnel[k]['rejected'] for k,_ in SPLITS)
    cases=sum(funnel[k]['semantic_cases'] for k,_ in SPLITS)
    assert (candidates,retained,rejected,cases)==(1955,1700,255,426)
    rewards={key:facts['oracle_rewards'][key] for key in ['1.0','1.3','1.5']}
    actual=Counter(str(json.loads(line)['reward']) for line in (ROOT/'data_v2/train_sft_agenttune_trajectories.jsonl').read_text().splitlines())
    assert dict(actual)==rewards=={'1.0':60,'1.3':112,'1.5':68}
    rows=[]
    for name,purpose in SPLITS:
        item=funnel[name];mix=item['kinds']
        description=(str(mix['consistent'])+' per kind') if len(set(mix.values()))==1 and name!='train_sft_240' else ', '.join(f"{mix[k]} {k}" for k in ['consistent','conflict','incident','abstain'])
        rows.append([f'`{name}.jsonl`',f"{item['input']} → **{item['kept']}** ({item['rejected']})",item['semantic_cases'],description,purpose])
    rows.append(['**Total frozen corpus**','**1,955 → 1,700 (255)**','**426** (+20 unrendered reserved cases)','Balanced across four language groups; coverage of six script styles','19 approved data-file hashes checked by `src.v2_2.manage.protected()`'])
    mean=tokens['mean_tokens'];truncated=tokens['above_legacy_1536'];percent=100*truncated/tokens['rows']
    raw=audit['similarity']['raw_question']['overall']['mean'];masked=audit['similarity']['entity_parameter_masked_question']['overall']['mean']
    collision=audit['gold_scalar_overlap']
    parts=[]
    def add(text):parts.append(text.strip())
    add('## 3. Data Creation, Curation & Evaluation Strategy')
    add('### 3.1 Rationale: Why We Built a Custom Benchmark & Chose `CohereLabs/tiny-aya-fire`')
    add('Single-turn English API-syntax accuracy alone does not establish enterprise reliability. We needed one benchmark combining **contradictory silos** (a stale Notion runbook versus a newer GitHub PR or Slack hotfix), **scope traps** (a newer `[STAGING-ONLY]` record ranked above `[PROD]`), **SQL-to-time/unit/math chains**, and English, Hindi (Devanagari/Latin), Hinglish and Telugu (native/Latin) questions. We chose **`CohereLabs/tiny-aya-fire` (3.35B)** for South Asian-script text alongside Latin technical identifiers such as `loyalty-api` and `batch_size_mb`, at a size suited to an organization-controlled on-premises boundary: our **v1 NF4 adapter used 3.15 GiB peak reserved VRAM**. That edge measurement is separate from final v2 BF16 benchmark accuracy; tokenizer support is not itself evidence of answer correctness.')
    add('### 3.2 How We Created the Data: Facts-First World + Live Oracle + CuratorKIT Funnel')
    add('**No LLM invented gold facts.** The four components below separate fact generation, tool verification, language rendering and curation; the actual builder executes **facts → rendering → CuratorKIT → oracle verification/trajectory export**.')
    add('1. **Deterministic Python worlds** ('+link('src/v2_world.py')+'; '+link('src/v2_tasks.py')+'): fixed **seed 42** creates the training world with **60 microservices and 80 incidents**; **seed 99** creates the synthetic holdout, with a separate constructed OSS repo-style world. Structured histories determine values, timestamps, source IDs and labels for **consistent**, **conflict/outdated-doc**, **incident** (`sla_penalty`, `payload_lb`, `payload_mib`, `config_audit`) and **abstain** tasks (missing entity or unplugged `db-mcp`).')
    add('2. **Live tool-executing oracle** ('+link('src/v2_oracle.py')+'): a deterministic discovery policy executes `notion-mcp`, `github-mcp`, `slack-mcp`, `db-mcp`, `time-mcp`, `unit-converter-mcp` and `math-mcp` as required, against each episode’s isolated in-memory SQLite snapshot. It uses task identity/request metadata, then discovers values and authority through returned observations—not hidden gold values or source labels. The builder checks predicted outcomes and retrieved gold IDs before export, reusing one verified semantic-case trajectory across its language variants. The **240** '+link('data_v2/train_sft_agenttune_trajectories.jsonl','AgentTune SFT trajectories')+' carry measured `evidence_gated` oracle rewards: **`'+json.dumps(rewards,separators=(', ',': '))+'`**. Expected abstentions are verified safe refusals, not tasks requiring an unavailable answer.')
    add('3. **Six-style multilingual rendering:** templates cover `en:latin`, `hi:native`, `hi:latin`, `hinglish:latin`, `te:native` and `te:latin`. Most cases have **four language/register versions**, with Hindi and Telugu alternating native/Latin templates—not six versions per case. The corpus has **425 rows per language group**; Hindi and Telugu each have **213 native / 212 Latin** rows. Four repo-style translations are omitted to retain exactly 100 rows from 26 cases. Template rendering and tool checks do not replace human linguistic review.')
    add('4. **CuratorKIT 0.1.21 deduplication** ('+link('src/v2_dataset.py','src/v2_dataset.py:curate')+'): `curatorkit.schema.DataSample` and `ExactDeduplicator.run` process **1,955 candidate model-visible prompts**, rejecting **255 injected exact-duplicate controls** to freeze **1,700 oracle-verified tasks**. Controls add **15%** to the clean-row count; they are **13.0% of all candidates**. Every rejection is logged in '+link('data_v2/curation_rejections.jsonl')+'; the '+link('data_v2/curation_funnel.json','funnel')+' measures exact deduplication, not semantic paraphrase filtering or independent natural-data quality gains.')
    add(table(['Split (`data_v2/`)','Candidates → retained (rejected)','Semantic cases','Task mix (rows)','Purpose'],rows))
    add('Task mixes describe frozen rows, not the final sampler’s accepted-update ratio. The 20 reserved training cases are outside these 1,700 rows. `SHA256SUMS` lists 15 artifacts; `protected()` additionally checks all **19 approved data files** without rewriting them.')
    add('### 3.3 Strict Curation Constraints We Imposed (`v1 → v2` Anti-Shortcut Hardening)')
    add('The audit of v1’s **85.25% (85.3% rounded)** SFT result found seven plausible confounds: reused SFT/GRPO cases, tool-spoiling prompts, `unknown-` missing-entity names, constant incident times/rates, an unused converter, implausible repo-style numbers, and single-result search. These are identified shortcuts, not measured causes of that score. V2 also varies incident times, rates and payloads, exercises kg→lb / decimal GB→MiB conversions, and enforces domain-valid configuration ranges.')
    add('1. **Blind tool routing:** user questions never name `github-mcp`, `slack-mcp`, `unit-converter-mcp` or `math-mcp`. Deployment-channel hints appear in retrieved runbooks; incident requests first require discovering service, timestamps or payload through SQLite. The prompt does not supply the tool sequence.')
    add('2. **Adversarial search ranking:** forgiving token-overlap search returns **up to three** own-entity/sibling records. Newer `[STAGING-ONLY]` records can rank above `[PROD]`, so “take the first hit” and “pick the newest timestamp” fail without scope filtering.')
    add('3. **Realistic refusal conditions:** absent services use plausible names without the `unknown-` prefix and are checked against the world’s service set. On unplugged-database tasks, `db-mcp` is actually absent from active schemas; the agent must respect the explicitly required source rather than substitute another silo.')
    add('4. **All 15 split-pair checks + modulo-3 partitioning:** '+link('src/v2_dataset.py','audit_splits')+' and regression tests enforce **zero shared `case_id`**, **zero `(service, parameter)` pairs**, and **zero `incident_id`** across all six splits. Configuration integers use **train ≡ 1**, **synthetic holdout ≡ 2**, **repo-style holdout ≡ 0 (mod 3)**, preventing a training config integer from matching a holdout config answer. This rule does not make calculated incident costs or every scalar answer globally unique.')
    add('5. **CPU Text-Level Overlap Check** ('+link('reports/submission/TEXT_LEAK_AUDIT.json')+f'): **0/500 exact holdout prompt duplicates** against **1,120 training prompts**; mean nearest-train 5-word Jaccard is **{raw:.4f} raw / {masked:.4f} entity-masked**. Independent structured checks find **zero `(service, parameter, gold_value)` tuple overlaps**. Shared system/tool instructions recur; **'+str(collision['count'])+'/'+str(collision['denominator_nonnull'])+' non-null holdout scalar answers repeat** on different facts. Low text overlap alone does not prove semantic independence.')
    add('6. **Tokenizer truncation preflight** ('+link('data_v2/token_length_audit.json')+f'): the cached Tiny Aya Fire tokenizer measured **min {tokens["min_tokens"]:,}, mean {mean:,.1f}, max {tokens["max_tokens"]:,} tokens** across 240 SFT conversations. The old **1,536-token** limit would truncate **{truncated}/240 ({percent:.1f}%) of the full multilingual set**, not only native-script rows. We require **2,560 SFT tokens**, **zero truncated trajectories**, and **4,096 GRPO/evaluation context tokens**; generation is bounded to 192 tokens per turn and six tool calls.')
    add('### 3.4 Evaluation Strategy: Metrics Chosen and Why')
    add('- **Exact Answer Accuracy (`exact_outcome`, 500 holdouts):** both the expected status (`answered`, `conflict_resolved`, `abstain`) and normalized scalar must match. The right number with the wrong conflict/refusal status is still an operational error; dumping several numbers cannot satisfy a single-scalar answer.\n'
        '- **Strict Outdated-Doc Catch (`stale_catch`, 250 conflicts):** exact outcome **plus the exact stale-page ID plus every gold source actually retrieved and cited**. This tests whether the agent caught and grounded the documentation drift, rather than guessing the updated value or merely collecting evidence.\n'
        '- **Verified Citation & Tool-Chain Compliance (425 evidence/answerable tasks):** citation F1 credits retrieved-and-cited gold IDs while penalizing unsupported IDs; required-chain compliance checks successful required-server calls, including time/conversion/math utilities. These detect correct-looking unsupported answers and skipped calculations. AuditKIT’s native tool-selection precision/recall/F1, validity and redundancy diagnose routing/schema errors and wasted calls; valid final format is tracked separately. Tool calls per successful task measure efficiency without rewarding premature failure.\n'
        '- **Refusal Calibration:** abstention precision penalizes false refusals of answerable questions; recall checks necessary refusals, with unplugged-source recall isolated. An agent that refuses everything can appear cautious while failing the job—the failure our collapsed-RL control exposes.')
    add('Reported 95% intervals use **10,000 semantic-case cluster bootstrap resamples**, keeping correlated language versions together: **20 validation / 100 synthetic / 26 repo-style cases**. Confidence intervals describe these frozen cohorts, not independent translations or verified live-enterprise generalization.')
    return '\n\n'.join(parts)+'\n\n'
