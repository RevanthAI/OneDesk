"""Run a downloaded SFT model/adapter in NF4 with the real local MCP tools."""
import argparse
import json
from pathlib import Path
from .evaluate_auditkit import HFBackend,run_batch,measure,verify_manifest

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--model',default=None);g.add_argument('--adapter',default=None);p.add_argument('--task-id');p.add_argument('--output',default='reports/local_sft_example.json');a=p.parse_args()
    verify_manifest(Path('data'))
    tasks=[json.loads(l) for l in Path('data/holdout_synth_400_frozen.jsonl').read_text().splitlines()]
    task=next((t for t in tasks if t['task_id']==a.task_id),None) if a.task_id else next(t for t in tasks if t['kind']=='conflict' and t['language']=='en')
    if task is None:raise ValueError('unknown task ID')
    path=a.model or (None if a.adapter else 'checkpoints/tiny-aya-fire-sft-merged')
    if path and not Path(path).is_dir():raise ValueError('downloaded model directory missing: '+path)
    backend=HFBackend(quantization='4bit',sdpa_expand_kv=True,model_path=path,adapter_path=a.adapter)
    world=json.loads(Path('data/world_test_synth.json').read_text())
    episode=run_batch([task],world,backend)[0]
    report={'question':task['question'],'task_id':task['task_id'],'episode':episode,'metrics':measure(task,episode),'runtime':backend.stats()}
    target=Path(a.output);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print('QUESTION:',task['question'])
    for turn in episode['raw_turns']:print(turn)
    print(json.dumps(report['metrics'],indent=2))
    print('Saved:',target)
if __name__=='__main__':main()
