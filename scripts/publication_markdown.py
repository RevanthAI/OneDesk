"""Offline published-link resolution and portable GitHub Markdown formatting."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
MODEL_COLLECTION_URL = 'https://huggingface.co/collections/Revanth-ml/onedesk-models-and-experimental-controls-6af97221a617ddc3326204a6'
DATA_COLLECTION_URL = 'https://huggingface.co/collections/Revanth-ml/onedesk-data-and-experiment-evidence-6af97225c0f1dc548b9ba8ce'


def publication():
    path = ROOT / 'docs/hf_cards/PUBLISH_RECEIPT.json'
    data = json.loads(path.read_text()) if path.exists() else {}
    return {**data, 'complete': True,
            'model_collection_url': MODEL_COLLECTION_URL,
            'data_collection_url': DATA_COLLECTION_URL}


def current_repo(repo_id):
    return repo_id.replace('Revanth-ml/driftguard-', 'Revanth-ml/onedesk-', 1)


def sync_publication_links(text, mapping=None):
    mapping = publication().get('repo_mapping', {}) if mapping is None else mapping
    for old, new in sorted(mapping.items(), key=lambda pair: -len(pair[0])):
        text = re.sub(re.escape(old) + r'(?![\w.-])', lambda match, replacement=new: replacement, text)
    return text


def url_link(url):
    label = url.removeprefix('https://huggingface.co/datasets/').removeprefix('https://huggingface.co/collections/').removeprefix('https://huggingface.co/')
    if '/collections/' in url:
        label=re.sub(r'-[0-9a-f]{24}$','',label)
    return f'[{label}]({url})'


def collection_links(data=None):
    data = publication() if data is None else data
    return (f"**Model Collection:** {url_link(data['model_collection_url'])}\n\n"
            f"**Data Collection:** {url_link(data['data_collection_url'])}")


def format_gfm(text):
    """Separate block elements; format table cells without touching fenced code/YAML."""
    front = ''
    if text.startswith('---\n'):
        end = text.find('\n---\n', 4)
        if end != -1:
            front, text = text[:end+5], text[end+5:]
    output = []
    in_fence = False
    previous = None
    def blank():
        if output and output[-1] != '':
            output.append('')
    for line in text.splitlines():
        if line.lstrip().startswith('```'):
            if not in_fence:
                blank(); output.append(line); in_fence = True
            else:
                output.append(line); output.append(''); in_fence = False
            previous = None
            continue
        if in_fence:
            output.append(line)
            continue
        if line.startswith('|'):
            cells = re.split(r'(?<!\\)\|', line.strip())[1:-1]
            formatted = []
            for cell in cells:
                cell = cell.strip()
                cell = re.sub(r'(?<![\w(])https://huggingface\.co/[^\s|)<>`]+',
                              lambda m: url_link(m[0].rstrip('.,')) + m[0][len(m[0].rstrip('.,')):], cell)
                formatted.append(cell)
            line = '| ' + ' | '.join(formatted) + ' |'
            kind = 'table'
        elif re.match(r'^#{1,6}\s', line):
            kind = 'heading'
        elif re.match(r'^\s*(?:[-*+] |\d+\. )', line):
            kind = 'list'
        elif not line.strip():
            kind = 'blank'
        else:
            kind = 'text'
        if previous in ('table', 'list') and kind not in (previous, 'blank'):
            blank()
        if kind in ('heading', 'table', 'list') and previous != kind:
            blank()
        output.append(line.rstrip())
        if kind == 'heading':
            output.append('')
        previous = kind
    body = re.sub(r'\n{3,}', '\n\n', '\n'.join(output)).strip() + '\n'
    return front + ('\n' if front else '') + body
