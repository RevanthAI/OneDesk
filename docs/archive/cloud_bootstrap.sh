#!/usr/bin/env bash
set -euo pipefail
uv pip install --system torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128
uv pip install --system transformers==4.57.6 peft==0.17.1 accelerate==1.15.0 huggingface-hub==0.36.2 numpy pyyaml
python - <<'PY'
import os,zipfile
from huggingface_hub import hf_hub_download
path=hf_hub_download(os.environ['RUN_REPO'],'cloud_bundle.zip',repo_type='dataset',revision=os.environ['BUNDLE_REVISION'],token=os.environ['HF_TOKEN'])
with zipfile.ZipFile(path) as archive:archive.extractall('/workspace')
PY
cd /workspace
export PYTHONPATH=/workspace/vendor/AgentTune/src:/workspace
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
python -u -m src.train_agenttune "$@"
