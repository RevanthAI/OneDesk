"""Download private model artifacts and verify the merged checkpoint is complete."""
import argparse
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi

def main():
    p=argparse.ArgumentParser();p.add_argument('--namespace',default=None);a=p.parse_args()
    load_dotenv(Path.cwd().parent/'.env');token=os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN');api=HfApi(token=token)
    namespace=a.namespace or api.whoami()['name'];records={}
    for kind,repo,name in [('adapter','driftguard-tiny-aya-fire-sft','tiny-aya-fire-sft-adapter'),('merged','driftguard-tiny-aya-fire-sft-merged','tiny-aya-fire-sft-merged')]:
        dest=Path('checkpoints/v1')/name
        revision=api.model_info(namespace+'/'+repo).sha
        api.snapshot_download(namespace+'/'+repo,revision=revision,local_dir=str(dest),token=token)
        records[kind]={'repo':namespace+'/'+repo,'revision':revision,'local_path':str(dest.resolve())}
        if kind=='merged':
            config=json.loads((dest/'config.json').read_text());assert config['model_type']=='cohere2'
            index=dest/'model.safetensors.index.json'
            weights=set(json.loads(index.read_text())['weight_map'].values()) if index.exists() else {'model.safetensors'}
            if not all((dest/w).is_file() and (dest/w).stat().st_size>0 for w in weights):raise ValueError('incomplete merged checkpoint')
        elif not (dest/'adapter_model.safetensors').exists():raise ValueError('adapter checkpoint missing')
    Path('reports/v1/cloud_sft').mkdir(parents=True,exist_ok=True)
    Path('reports/v1/cloud_sft/downloaded_models.json').write_text(json.dumps(records,indent=2))
    print(json.dumps(records,indent=2))
if __name__=='__main__':main()
