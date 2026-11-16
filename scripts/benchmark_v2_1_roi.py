"""Time the selected final adapter; cloud execution is explicitly opt-in."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUTPUT = ROOT / 'reports/submission/ROI_LOCAL_NF4_BENCHMARK.json'
ADAPTER_REVISION = '016676680121b4dd90ec6026978de7ee1cdb1271'


def select_tasks():
    """Deterministic 16+4 sample, unique cases, all kinds and incident subtypes."""
    from src.v2_2.data import load
    selected = []
    for split, count in [('test_synth', 4), ('repo_style', 1)]:
        tasks = load(split)
        for ki, kind in enumerate(['conflict', 'consistent', 'incident', 'abstain']):
            for i in range(count):
                language = ['en', 'hi', 'hinglish', 'te'][(ki+i) % 4]
                subtype=['sla_penalty','payload_lb','payload_mib','config_audit'][i] if kind=='incident' and split=='test_synth' else None
                item = next(t for t in tasks if t['kind'] == kind and t['language'] == language
                            and t['case_id'] not in {t['case_id'] for t in selected}
                            and (subtype is None or t['incident_subtype']==subtype))
                selected.append(dict(item, benchmark_split=split))
    assert len(selected) == 20
    return selected


def cloud_job(args):
    """Launch the same script on t4-small, retaining output in the job logs."""
    from huggingface_hub import HfApi
    from dotenv import load_dotenv
    load_dotenv(ROOT.parent / '.env')
    token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
    if not token: raise RuntimeError('HF_TOKEN or HUGGINGFACE_TOKEN is required for the optional paid T4 job.')
    api = HfApi(token=token)
    command = ['bash', '-lc', 'git clone --depth 1 https://github.com/RevanthAI/OneDesk.git /tmp/onedesk && cd /tmp/onedesk && pip install torch==2.8.0 transformers==4.57.6 peft==0.17.1 accelerate==1.15.0 bitsandbytes==0.50.2 python-dotenv huggingface_hub==0.36.2 && python scripts/benchmark_v2_1_roi.py --output /tmp/roi-t4.json && cat /tmp/roi-t4.json']
    job = api.run_job(image='python:3.12', command=command, flavor='t4-small', timeout='1h',
                      secrets={'HF_TOKEN': token}, env={'HF_HOME': '/tmp/hf'})
    print(json.dumps({'job_id': job.id, 'hardware': 't4-small', 'usd_per_hour': .40,
                      'results': 'Job logs contain the full JSON after completion.'}))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--adapter', default='checkpoints/v2_2/grpo_best_val_adapter')
    p.add_argument('--output', default=str(OUTPUT))
    p.add_argument('--run-hf-t4', action='store_true', help='Explicitly launch a paid 1-hour-limited HF T4 job; requires this script pushed to main.')
    args = p.parse_args(argv)
    if args.run_hf_t4:
        return cloud_job(args)
    import torch
    from importlib.metadata import version
    from src.v2_2.manage import protected
    assert protected() == 19
    tasks = select_tasks()
    result = dict(schema_version=1, adapter=args.adapter, sample_volume=20,
                  sample_task_ids=[t['task_id'] for t in tasks], batch_size=1,
                  sample_case_count=len({t['case_id'] for t in tasks}),
                  sample_design='20 distinct semantic cases; balanced across four kinds and four language groups; synthetic incidents cover all four subtypes. Not a full NF4 accuracy evaluation.',
                  versions={k:version(k) for k in ['torch','transformers','peft','bitsandbytes']},
                  cuda_available=torch.cuda.is_available(), cloud_job_launched=False)
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    if not result['cuda_available']:
        result.update(status='not_measured_no_cuda', note='No model inference was run; use explicitly labeled historical token-adjusted scenario.')
        output.write_text(json.dumps(result, indent=2)+'\n'); print(json.dumps(result, indent=2)); return
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    from dotenv import load_dotenv
    from src.v2_2.backend import MODEL, REVISION, Backend
    from src.v2_2.data import world
    from src.v2_2.evaluation_core import run_batch, measure
    load_dotenv(ROOT.parent / '.env')
    token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, token=token, padding_side='left')
    if tokenizer.pad_token_id is None: tokenizer.pad_token = tokenizer.eos_token
    import transformers.integrations.sdpa_attention as sdpa
    sdpa.use_gqa_in_sdpa = lambda attention_mask, key: False
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
    loading = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION, token=token, dtype=torch.float16,
                 quantization_config=quant, attn_implementation='sdpa', device_map={'': 'cuda:0'})
    adapter = ROOT / args.adapter
    if not (adapter / 'adapter_model.safetensors').is_file():
        from huggingface_hub import snapshot_download
        adapter = Path(snapshot_download('Revanth-ml/onedesk-tiny-aya-fire-v2-1-warmup-grpo-best-val',
                        revision=ADAPTER_REVISION, token=token, allow_patterns=['adapter_config.json','adapter_model.safetensors']))
    model = PeftModel.from_pretrained(model, str(adapter), is_trainable=False).eval()
    result.update(model=MODEL, revision=REVISION, adapter_revision=ADAPTER_REVISION, adapter_sha256=hashlib.sha256((adapter/'adapter_model.safetensors').read_bytes()).hexdigest(),
                  model_load_seconds=time.perf_counter()-loading, gpu=torch.cuda.get_device_name(0), compute_dtype='float16', quantization='bitsandbytes NF4 double-quant')
    if args.adapter=='checkpoints/v2_2/grpo_best_val_adapter':
        assert result['adapter_sha256']=='b286392a2d979af730b6c9fcd1c2a14369a2f859bcc691526478d0e8220a2f07', 'Final adapter checksum mismatch'

    class TimedBackend(Backend):
        def __init__(self, model, tokenizer):
            super().__init__(model, tokenizer); self.input_tokens=0
        def generate_messages(self, batch):
            self.input_tokens += sum(len(self.tokenizer.apply_chat_template(m, tokenize=True, add_generation_prompt=True)) for m in batch)
            torch.cuda.synchronize(); return super().generate_messages(batch)
        def generate(self, batch):
            torch.cuda.synchronize()
            answer=super().generate(batch)
            torch.cuda.synchronize()
            # Parent generation timing already surrounds generate; synchronization assures completion.
            return answer

    # Warm CUDA kernels on a separate copy of the first task; exclude warmup from timing.
    backend = TimedBackend(model, tokenizer)
    run_batch(tasks[:1], world(tasks[0]['benchmark_split']), backend)
    torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
    backend = TimedBackend(model, tokenizer); start = time.perf_counter(); episodes=[]
    for task in tasks:
        episode = run_batch([task], world(task['benchmark_split']), backend)[0]
        episodes.append(dict(task_id=task['task_id'], split=task['benchmark_split'], kind=task['kind'],
                             language=task['language'], elapsed_seconds=episode['elapsed_seconds'], metrics=measure(task, episode), episode=episode))
        print(json.dumps({'completed':len(episodes), 'total':20, 'generated_tokens':backend.generated_tokens}), flush=True)
    torch.cuda.synchronize(); wall=time.perf_counter()-start
    hours1k=wall/20*1000/3600
    result.update(status='measured', wall_seconds=wall, generation_seconds=backend.seconds,
          input_tokens=backend.input_tokens, generated_tokens=backend.generated_tokens,
          output_tokens_per_second=backend.generated_tokens/wall,
          total_tokens_per_second=(backend.generated_tokens+backend.input_tokens)/wall,
          generation_only_output_tokens_per_second=backend.generated_tokens/backend.seconds,
          peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
          gpu_hours_per_1000=hours1k, gpu_hours_per_100000=hours1k*100,
          electricity_usd_per_1000=hours1k*.175*.10,
          electricity_usd_per_100000=hours1k*100*.175*.10,
          power_basis='175 W nameplate scenario, not measured energy; $0.10/kWh; excludes CPU, idle and hardware',
          episodes=episodes, protected_files=protected())
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    if (ROOT/'reports/submission/ROI_TOKEN_AUDIT.json').is_file():
        from roi_analysis import compile_report
        compile_report()
    print(json.dumps({k:v for k,v in result.items() if k!='episodes'}, indent=2))


if __name__ == '__main__': main()
