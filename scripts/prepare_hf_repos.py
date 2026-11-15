"""Stage OneDesk cards locally; publish/rename ONLY with explicit --publish.

The default and --dry-run paths make no network calls and do not read tokens.
Existing model weights, data files and saved reports are never changed locally.
"""
from pathlib import Path
import argparse
import json
import os
import re
from datetime import datetime, timezone
import yaml
from publication_markdown import publication, format_gfm, sync_publication_links, current_repo, collection_links
from clean_report_data import (ROOT, PROJECT_NAME, BASE, BASE_REVISION, registry, read, rows,
                               ci, percent, table, data_manifest, protect, digest)

CARDS = ROOT / 'docs/hf_cards'
TAGS = ['agenttune','curatorkit','auditkit','mcp','grpo','tool-calling','multilingual','tiny-aya-fire']


def frontmatter(metadata, body):
    return '---\n'+yaml.safe_dump(metadata,sort_keys=False,allow_unicode=True)+'---\n\n'+body.strip()+'\n'


def split_table():
    return table(['Companion benchmark split','Rows','Semantic cases'],[[x['file'],x['rows'],x['cases']] for x in data_manifest()])


def benchmark(record):
    if not record.get('score_folder'):
        return ('| Check | Result |\n|---|---|\n| Full holdout evaluation for this exact export | Not measured |\n\n'+record.get('note','')+'\n')
    summary=read(Path(record['score_folder'])/'summary.json');result=[]
    for split,label in [('validation','Validation'),('test_synth','Synthetic holdout'),('repo_style','Repo-style holdout')]:
        if split not in summary:continue
        r=summary[split];m=r['metrics']
        result.append([label,r['n'],ci(m['exact_outcome']),ci(m['stale_catch']),ci(m['format_valid'])])
    return table(['Cohort','Queries','Exact outcome % [95% CI]','Strict outdated-doc catch % [95% CI]','Valid final format % [95% CI]'],result)


def load_snippet(record, target_repo):
    if record.get('merged'):
        code=f'''from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Standalone v1 merged export (no separate LoRA load).
repo = "{target_repo}"
# Pin the saved weight revision shown in the Provenance section.
revision = "{record['revision']}"
tokenizer = AutoTokenizer.from_pretrained(repo, revision=revision)
model = AutoModelForCausalLM.from_pretrained(
    repo, revision=revision, dtype=torch.float16, device_map="auto"
)
model.eval()'''
    else:
        code=f'''from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

adapter = "{target_repo}"
# Weights are pinned independently of subsequent README-only updates.
adapter_revision = "{record['revision']}"
tokenizer = AutoTokenizer.from_pretrained(adapter, revision=adapter_revision)
base = AutoModelForCausalLM.from_pretrained(
    "{BASE}",
    revision="{BASE_REVISION}",
    dtype=torch.bfloat16,  # use float16 on hardware without BF16 support
    device_map="auto",
)
model = PeftModel.from_pretrained(base, adapter, revision=adapter_revision)
model.eval()'''
    return '```python\n'+code+'\n```\n\nThis snippet loads weights only. Full agent evaluation needs the OneDesk router, active tool schemas and tool-result feedback loop. Use the project’s local-demo/evaluation entry points to execute tool calls. Local NF4 deployment uses a separate numerical path from the BF16 benchmark.'


def training_recipe(record):
    name=record['repo_id'].split('/')[1]
    if 'warmup-grpo-best-val' in name:
        return 'Selected update 40 from 80 active GRPO updates (40+40), starting from 60-step/two-epoch SFT. G=6; temperature 1.0, retry 1.15; LR 5e-6; beta 0.04; anti-collapse reward, nonzero variance and positive evidence anchors. Validation selected the checkpoint.'
    if 'warmup-grpo-final' in name:
        return 'Saved final update 80 from the same 40+40-update recipe. Validation at update 80 was 78.75%; update 40 was better at 80.00%. No separate full holdout evaluation of this final-update export was run.'
    if 'warmup-sft' in name:
        return 'Fresh two-epoch SFT: 60 optimizer steps, effective batch 8, 480 exposures, LR 1.5e-4, 2,560-token context, zero truncation. Validation at steps 30/45/60 selected 60; the first 60 steps use a 120-step cosine horizon.'
    if name.endswith('v2-1-sft'):
        return 'Fresh four-epoch SFT: 120 steps, effective batch 8, 960 exposures, LR 1.5e-4 and cosine decay to zero, context 2,560 with zero truncation. Validation selected update 120.'
    if name.endswith('v2-grpo'):
        return 'Negative-result control: weak 15-step SFT followed by 120+220 GRPO updates, G=4 and evidence-gated reward. Stage 2 collapsed to excessive abstention; preserve this export for analysis rather than recommending it for deployment.'
    if name.endswith('v2-sft'):
        return 'Deliberately small cold start: one epoch on 240 rows, effective batch 16, only 15 optimizer steps; context 2,560 with zero truncation.'
    if 'grpo-pilot' in name:
        return 'Historical v1 pilot: 60 GRPO updates (20+40), G=4, temperature 0.8, LR 5e-6 and beta 0.04 from the v1 SFT adapter. Limited validation had a 40/40 ceiling before and after.'
    return 'Historical v1 SFT: 34 optimizer steps, 360 train and 40 validation trajectories, effective batch 16, 544 rounded exposures and a 1,536-token budget. Rank-16/alpha-32 LoRA with assistant-only supervision. The merged export is a separate numerical deployment path.'


def model_card(record, target_repo):
    metadata=dict(license='cc-by-nc-4.0',base_model=BASE,library_name='transformers' if record.get('merged') else 'peft',
                  pipeline_tag='text-generation',language=['en','hi','te'],tags=TAGS,inference=False)
    data_label='the original v1 explicit-routing benchmark' if 'v1' in record['label'].lower() else 'the frozen data_v2 company-knowledge benchmark'
    body=f'''# {PROJECT_NAME} — {record['label']}

## Overview

OneDesk is a multilingual company-knowledge agent built on **Tiny Aya Fire (3.35B)**. It reconciles runbooks, GitHub PRs, Slack deployment records and live SQL data, and can chain time, conversion and arithmetic tools. Users can ask in English, Hindi (Devanagari/Latin), Hinglish, and Telugu (native/Latin).

This repository contains **{record['label']}**, evaluated or retained as described below on {data_label}. Published repositories use the OneDesk name; frozen task IDs and historical run metadata retain their original experiment identifiers.

## Benchmark results

{benchmark(record)}
{record.get('note','')}

Exact outcome requires the right status and normalized value. Strict outdated-doc catch also requires the correct stale page and all gold citations retrieved and cited. Confidence intervals use 10,000 semantic-case cluster resamples. Translations share cases.

## Intended use

Research on evidence-grounded multilingual tool calling, retrieval, stale-document reconciliation and read-only incident calculations. Nine logical MCP interfaces are available: Notion, GitHub, Slack, SQL, time, conversion, arithmetic, weather and calendar. The latter two test routing immunity.

## Load the {'standalone export' if record.get('merged') else 'LoRA adapter'}

Install compatible `transformers`, `peft`, `accelerate`, `torch` and `safetensors`; the recorded experiment used Transformers 4.57.6 and PEFT 0.17.1.

{load_snippet(record,target_repo)}

## Training recipe

{training_recipe(record)}

## Toolkit chain

CuratorKIT 0.1.21 exact-deduplicates model-visible prompts. AgentTune 1.1.4 runs assistant-only SFT and live multi-turn GRPO through the project compatibility backend. AuditKIT 1.1.7 scores actual saved tool episodes. The final selected recipe uses 60-step SFT, followed by 80 active G6 GRPO updates; validation selected update 40. A separate 120-step full SFT model is the strongest overall-accuracy control. The historical weak/collapsed and v1 repositories have their own recipes and are not the final selected policy.

## Provenance

- Base: `{BASE}` at `{BASE_REVISION}`.
- Saved weight revision in this repository: `{record['revision']}`.
- Local artifact path in the project: `{record['local']}`.
- Owner and teammate: [@Revanth-ml](https://huggingface.co/Revanth-ml).
- Companion frozen data: [onedesk-mcp-v2-data](https://huggingface.co/datasets/Revanth-ml/driftguard-mcp-v2-data).
- Final study logs: [onedesk-mcp-warmup-runs](https://huggingface.co/datasets/Revanth-ml/driftguard-mcp-warmup-runs).

## Limitations and license

The worlds and repo-style records are constructed fixtures, not live company connectors or verified upstream Git histories. The final GRPO policy improves strict stale catch over full SFT while having lower overall holdout accuracy and lower required-server chain compliance. Overall GRPO gains over warmup have paired intervals including zero. Final-update 80 has no separate complete holdout benchmark. An on-premises deployment can keep evidence local only when connectors and logging follow that boundary; the model does not guarantee privacy or correctness.

Original synthetic datasets are licensed under **CC-BY-4.0** and original project code under **Apache-2.0**; third-party code retains its own license. The model and adapters are under **CC BY-NC 4.0**, retaining the base model’s attribution and noncommercial conditions. This card does not grant commercial rights. Historical v1 NF4 VRAM/speed results do not establish final v2 NF4 quality.
'''
    path=ROOT/record['local']/'adapter_model.safetensors'
    if path.exists():body+='\nAdapter SHA-256: `'+digest(path)+'`.\n'
    return frontmatter(metadata,body)


def dataset_card(record,target_repo):
    is_data=record['scope']=='data'
    metadata=dict(license='cc-by-4.0',
                  language=['en','hi','te'],tags=['synthetic','agenttune','curatorkit','auditkit','mcp','tool-calling','multilingual'],
                  task_categories=['question-answering','text-generation'])
    if is_data:
        metadata['size_categories']=['1K<n<10K']
        metadata['configs']=[dict(config_name='default',data_files=[dict(split=x['label'].lower().replace(' ','_'),path=x['file']) for x in data_manifest()])]
    kind='Frozen company-knowledge benchmark' if is_data else 'Recorded experiment runs and diagnostics'
    location='The six JSONL files below are stored at the repository root alongside world snapshots and `SHA256SUMS`.' if is_data else 'This is a **run-artifact repository**, not a six-split dataset viewer. Its companion benchmark has the six splits below; run prefixes contain summaries, trajectories, provenance and dashboards. The synthetic query splits live in the separate frozen-data repository.'
    body=f'''# {PROJECT_NAME} — {kind}

## Overview

OneDesk studies a small multilingual assistant that answers current company-knowledge questions across a **nine-server MCP environment**: `notion-mcp`, `github-mcp`, `slack-mcp`, `db-mcp`, `time-mcp`, `unit-converter-mcp`, `math-mcp`, `weather-mcp`, and `calendar-mcp`.

Structured Python facts determine gold answers before language rendering. Tasks cover consistent settings, stale runbooks, incident cost/configuration chains, and missing-entity or unplugged-source abstention. Scope-aware retrieval mixes production records with newer `[STAGING-ONLY]` and sibling distractors. SQLite SELECT and deterministic utility calculations execute as real local tools.

{location}

## Companion split table — 1,700 curated rendered tasks

{split_table()}

The train world has 60 services, 80 incidents and 320 semantic cases: 300 allocated plus 20 reserved. Training phases, validation and holdouts have disjoint case IDs, service-parameter pairs and incident IDs. Script styles are `en:latin`, `hi:native`, `hi:latin`, `hinglish:latin`, `te:native` and `te:latin`.

## Curation and verification

CuratorKIT 0.1.21 processed **1,955 candidates**, retained **1,700**, and logged **255 rejected injected exact duplicates**. This validates exact deduplication, not semantic paraphrase filtering. The maximum SFT trajectory measured 2,359 tokens; the 2,560-token training budget preserves all 240 oracle conversations without truncation. Training/evaluation never regenerates the frozen inputs.

## Schema

| Field | Meaning |
|---|---|
| `task_id`, `case_id` | Unique rendered query and shared semantic-case identifier |
| `world_split`, `pool`, `schema_version` | World, phase case pool, schema version 2 |
| `question`, `language`, `script` | User text, en/hi/hinglish/te register and native/Latin script |
| `prompt` | System instructions, active schemas and user query; model-visible input |
| `messages` | Full oracle SFT conversation, including tool calls, observations and final response, when present |
| `kind`, `incident_subtype` | consistent/conflict/incident/abstain; SLA, payload or config-audit subtype |
| `service_name`, `param_name`, `incident_id` | Entity/parameter or incident selectors |
| `active_mcps`, `required_mcps`, `distractor_mcps` | Available tool interfaces, gold-required chain and routing distractors |
| `expected_status`, `gold_value`, `gold_cites` | Deterministic target status, normalized scalar and supporting IDs |
| `stale_doc_id`, `stale_trap_value` | Stale page identifier and outdated scalar trap |
| `oracle_optimal_steps`, `reference_tool_sequence` | Measured discovery-policy call length and reference sequence |

Run records additionally include raw assistant turns, messages, calls/outputs, retrieved IDs, predictions, completion reasons, rewards, token masks, group eligibility and optimizer/validation logs. Record types vary by historical run version. The oracle length is a measured policy length, not a proof of global optimality.

Tool protocol:

```xml
<tool_call>{{"server":"db-mcp","tool":"query_db","arguments":{{"sql":"SELECT incident_id FROM production_incidents LIMIT 1"}}}}</tool_call>
<final_answer>{{"status":"answered","value":16,"cites":["retrieved-id"],"stale_source":null}}</final_answer>
```

## Checksums and provenance

The frozen data directory has 19 locked files, including a 15-artifact `SHA256SUMS`. The split hashes are:

{table(['JSONL artifact','SHA-256'],[[x['file'],'`'+x['sha256']+'`'] for x in data_manifest()])}

Repository owner: [@Revanth-ml](https://huggingface.co/Revanth-ml). [Frozen data](https://huggingface.co/datasets/Revanth-ml/driftguard-mcp-v2-data) · [Final study artifacts](https://huggingface.co/datasets/Revanth-ml/driftguard-mcp-warmup-runs).

## Limitations

Facts and repo-style fixtures are synthetic. Configuration values are split by modulo-3 residue; template translations are correlated. Reviewed holdouts and repeated validation selection do not constitute a fresh confirmation study. No real company data, live Notion/Slack/GitHub network connector, or independently verified OSS drift transfer is claimed.

## Licensing

Our original synthetic benchmark data and original dataset annotations are licensed under **CC-BY-4.0**. Attribution: **OneDesk contributors / Revanth-ml**. Original project code is licensed under **Apache-2.0**; model weights and adapters retain **CC BY-NC 4.0**, and bundled third-party code retains its own license. These terms are recorded outside the immutable data files; benchmark contents and checksums are unchanged. CC-BY-4.0 terms: https://creativecommons.org/licenses/by/4.0/. Apache-2.0 terms: https://www.apache.org/licenses/LICENSE-2.0.
'''
    return frontmatter(metadata,body)


def target_name(repo_id,prefix):
    if not prefix:return repo_id
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',prefix):
        raise ValueError('Rename prefix must be a repository-name prefix, without namespace or slashes')
    namespace,name=repo_id.split('/',1)
    suffix=name[len('driftguard-'):] if name.startswith('driftguard-') else name
    return namespace+'/'+prefix+'-'+suffix


def generate(prefix=None):
    protect();records=registry();published=publication()
    mapping={r['repo_id']:(target_name(r['repo_id'],prefix) if prefix else published.get('repo_mapping',{}).get(r['repo_id'],current_repo(r['repo_id']))) for r in records}
    if len(set(mapping.values()))!=len(records):raise ValueError('Rename creates duplicate targets')
    CARDS.mkdir(exist_ok=True);plan=[]
    for record in records:
        repo=record['repo_id'];target=mapping[repo]
        folder=CARDS/record['repo_type']/target.split('/')[1];folder.mkdir(parents=True,exist_ok=True)
        content=model_card(record,target) if record['repo_type']=='model' else dataset_card(record,target)
        for original,renamed in mapping.items():
            content=content.replace('https://huggingface.co/datasets/'+original+')','https://huggingface.co/datasets/'+renamed+')').replace('https://huggingface.co/'+original+')','https://huggingface.co/'+renamed+')')
        content=sync_publication_links(content,mapping)
        content += '\n## Published collections\n\n'+collection_links(published)+'\n'
        content=format_gfm(content)
        path=folder/'README.md';path.write_text(content)
        old=CARDS/record['repo_type']/repo.split('/')[1]/'README.md'
        if old!=path and old.is_file():
            old.unlink()
            if not any(old.parent.iterdir()):old.parent.rmdir()
        # Parse with the real HF card classes, entirely from local text.
        from huggingface_hub import ModelCard,DatasetCard
        card=(ModelCard if record['repo_type']=='model' else DatasetCard)(content)
        parsed=card.data.to_dict()
        assert parsed.get('license')==('cc-by-nc-4.0' if record['repo_type']=='model' else 'cc-by-4.0')
        plan.append(dict(**record,target_repo_id=target,card=str(path.relative_to(ROOT)),card_sha256=digest(path),yaml_valid=True))
    value=dict(project=PROJECT_NAME,dry_run=True,network_calls=0,models=sum(r['repo_type']=='model' for r in plan),datasets=sum(r['repo_type']=='dataset' for r in plan),rename_prefix=prefix,repositories=plan,repo_mapping=mapping,
               excluded_planned_repositories=['Revanth-ml/driftguard-tiny-aya-fire-v2-1-grpo-best-val','Revanth-ml/driftguard-tiny-aya-fire-v2-1-grpo-final'],
               operations_if_publish=['Preflight existing repositories and optional rename collisions','Upload prepared README cards without changing weights/data','Optionally move repositories within the same namespace','Make selected repositories public','Create public model/data collections and add repositories'])
    (CARDS/'PLAN.json').write_text(json.dumps(value,indent=2)+'\n')
    index='# OneDesk — prepared Hugging Face cards\n\nLocal generation and dry-run do not use network calls or credentials. All remote operations require explicit `--publish`.\n'
    index+='\n'+collection_links(published)+'\n'
    index+=table(['Type','Published repository','Prepared card'],[[r['repo_type'],'https://huggingface.co/'+('datasets/' if r['repo_type']=='dataset' else '')+r['target_repo_id'],'['+r['label']+']('+str(Path(r['card']).relative_to('docs/hf_cards'))+')'] for r in plan])
    index+='\n```bash\n.venv/bin/python scripts/prepare_hf_repos.py --dry-run\n# When ready:\n.venv/bin/python scripts/prepare_hf_repos.py --publish\n# Optional OneDesk rename:\n# .venv/bin/python scripts/prepare_hf_repos.py --publish --rename-prefix onedesk\n```\n\nPublishing makes the listed run repositories and their existing contents public; review PLAN.json and those repositories before invoking it. Two historical planned-but-untrained v2.1 model names are intentionally excluded. Original synthetic datasets are CC-BY-4.0; original project code is Apache-2.0; model weights/adapters retain CC BY-NC 4.0. Collections are created only by publish; URLs are saved to PUBLISH_RECEIPT.json and printed. Publication automatically updates both collection URLs in README.md.\n'
    (CARDS/'README.md').write_text(format_gfm(index));protect();return value


def upload_cards(plan):
    """Refresh README cards in already-published repositories; no rename or visibility edits."""
    from dotenv import load_dotenv
    from huggingface_hub import HfApi, hf_hub_download
    import tempfile
    load_dotenv(ROOT.parent/'.env')
    token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN')
    if not token:raise RuntimeError('Set HUGGINGFACE_TOKEN or HF_TOKEN before --upload-cards')
    api=HfApi(token=token)
    # Confirm every exact target before writing any card.
    for r in plan['repositories']:
        info=api.repo_info(r['target_repo_id'],repo_type=r['repo_type'])
        if info.private:raise RuntimeError('Expected a published repository: '+r['target_repo_id'])
    uploaded=[]
    for r in plan['repositories']:
        commit=api.upload_file(path_or_fileobj=str(ROOT/r['card']),path_in_repo='README.md',repo_id=r['target_repo_id'],repo_type=r['repo_type'],commit_message='OneDesk: published collection links and readable benchmark card')
        with tempfile.TemporaryDirectory(prefix='onedesk-card-readback-',dir='/tmp') as td:
            downloaded=hf_hub_download(r['target_repo_id'],'README.md',repo_type=r['repo_type'],revision=commit.oid,token=token,local_dir=td)
            if Path(downloaded).read_bytes()!=(ROOT/r['card']).read_bytes():raise RuntimeError('README read-back mismatch: '+r['target_repo_id'])
        uploaded.append(dict(repo_id=r['target_repo_id'],repo_type=r['repo_type'],commit=commit.oid,card_sha256=r['card_sha256'],verified=True))
        (CARDS/'CARD_UPLOAD_RECEIPT.json').write_text(json.dumps(dict(updated_at=datetime.now(timezone.utc).isoformat(),complete=len(uploaded)==len(plan['repositories']),cards=uploaded,renamed=False,visibility_changed=False),indent=2)+'\n')
        print(json.dumps(dict(event='card_uploaded',repo=r['target_repo_id'],commit=commit.oid)),flush=True)
    protect();return dict(complete=True,cards_uploaded=len(uploaded),renamed=False,visibility_changed=False)


def publish(plan):
    """Remote mutations authorized only by an explicit CLI flag; resumable journal."""
    from dotenv import load_dotenv
    from huggingface_hub import HfApi
    from huggingface_hub.errors import RepositoryNotFoundError
    load_dotenv(ROOT.parent/'.env')
    token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN')
    if not token:raise RuntimeError('Set HUGGINGFACE_TOKEN or HF_TOKEN before --publish')
    api=HfApi(token=token);identity=api.whoami();namespace=identity['name']
    state_path=CARDS/'PUBLISH_PROGRESS.json'
    old=json.loads(state_path.read_text()) if state_path.exists() else {}
    if old and old.get('repo_mapping')!=plan['repo_mapping']:
        raise RuntimeError('Existing publication journal uses another rename mapping; inspect it before starting a different publication')
    state=old or dict(repo_mapping=plan['repo_mapping'],completed=[],started_at=datetime.now(timezone.utc).isoformat())
    def persist():state_path.write_text(json.dumps(state,indent=2)+'\n')
    completed=set(state['completed'])
    def done(key):completed.add(key);state['completed']=sorted(completed);persist()
    # All read-only checks happen before the first upload, rename or visibility change.
    for r in plan['repositories']:
        if r['repo_id'].split('/')[0]!=namespace:raise RuntimeError('Authenticated account must own every listed repository')
        current=r['target_repo_id'] if 'move:'+r['repo_id'] in completed else r['repo_id']
        api.repo_info(current,repo_type=r['repo_type'])
        if r['repo_id']!=r['target_repo_id'] and 'move:'+r['repo_id'] not in completed:
            try:api.repo_info(r['target_repo_id'],repo_type=r['repo_type'])
            except RepositoryNotFoundError:pass
            else:raise RuntimeError('Rename target already exists: '+r['target_repo_id'])
    persist()
    for r in plan['repositories']:
        key='card:'+r['repo_id']+':'+r['card_sha256']
        current=r['target_repo_id'] if 'move:'+r['repo_id'] in completed else r['repo_id']
        if key not in completed:
            api.upload_file(path_or_fileobj=str(ROOT/r['card']),path_in_repo='README.md',repo_id=current,repo_type=r['repo_type'],commit_message='OneDesk: readable experiment card and exact benchmark provenance')
            done(key)
    for r in plan['repositories']:
        move='move:'+r['repo_id']
        if r['repo_id']!=r['target_repo_id'] and move not in completed:
            api.move_repo(from_id=r['repo_id'],to_id=r['target_repo_id'],repo_type=r['repo_type']);done(move)
        visibility='public:'+r['target_repo_id']
        if visibility not in completed:
            api.update_repo_visibility(repo_id=r['target_repo_id'],repo_type=r['repo_type'],private=False);done(visibility)
    collections={}
    for kind,title in [('model','OneDesk — Models and Experimental Controls'),('dataset','OneDesk — Data and Experiment Evidence')]:
        collection=api.create_collection(title=title,namespace=namespace,description='OneDesk multilingual company-knowledge agent: frozen benchmark, exact evidence and experimental controls.',private=False,exists_ok=True)
        collection=api.update_collection_metadata(collection_slug=collection.slug,private=False)
        for r in plan['repositories']:
            if r['repo_type']==kind:
                api.add_collection_item(collection_slug=collection.slug,item_id=r['target_repo_id'],item_type=kind,note=r['label'],exists_ok=True)
        collections[kind]=getattr(collection,'url',None) or 'https://huggingface.co/collections/'+collection.slug
    receipt=dict(complete=True,published_at=datetime.now(timezone.utc).isoformat(),repo_mapping=plan['repo_mapping'],
                 model_collection_url=collections['model'],data_collection_url=collections['dataset'],
                 models=plan['models'],datasets=plan['datasets'],weights_and_data_uploaded=False,readme_cards_uploaded=True)
    (CARDS/'PUBLISH_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    # The report reads this receipt to replace pending collection links.
    from build_clean_report import build
    build(publication=receipt);protect();return receipt


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group();modes.add_argument('--publish',action='store_true');modes.add_argument('--dry-run',action='store_true');modes.add_argument('--upload-cards',action='store_true',help='Refresh README cards in the existing public repositories only')
    parser.add_argument('--rename-prefix',help='Optional same-account prefix, e.g. onedesk; mutation still requires --publish')
    args=parser.parse_args(argv);plan=generate(args.rename_prefix)
    if args.upload_cards:
        print(json.dumps(upload_cards(plan),indent=2))
    elif args.publish:
        print(json.dumps(publish(plan),indent=2))
    else:
        print(json.dumps(dict(project=PROJECT_NAME,mode='dry-run',network_calls=0,models=plan['models'],datasets=plan['datasets'],rename_prefix=args.rename_prefix,plan='docs/hf_cards/PLAN.json',collections={'model':publication()['model_collection_url'],'data':publication()['data_collection_url']}),indent=2))
    return plan

if __name__=='__main__':main()
