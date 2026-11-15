"""Create a local, filterable viewer for recorded rollouts (no server/telemetry)."""
import json
from pathlib import Path


def export_viewer(root):
    root=Path(root);records=[]
    for file in sorted(root.glob('stage*/rollouts.jsonl')):
        for line in file.read_text().splitlines():
            r=json.loads(line);e=r['episode']
            records.append(dict(stage=file.parent.name,optimizer_step_before=r['step'],attempt=r.get('rollout_batch'),acceptance='skipped' if r.get('zero_variance_skipped') else 'accepted',language=r['language'],kind=r['kind'],task_id=r['task_id'],sample=r['sample'],reward=r['reward'],advantage=r['advantage'],calls=e['num_tool_calls'],completion_reason=e['completion_reason'],prediction=e['prediction'],messages=e['messages'],tool_calls=e['calls']))
    # Escaping '<' prevents a recorded model/tool string from ending the script.
    payload=json.dumps(records,ensure_ascii=False).replace('<','\\u003c')
    html='''<!doctype html><html><head><meta charset="utf-8"><title>V2 GRPO rollout explorer</title><style>
body{font:15px system-ui;margin:24px;color:#172033;background:#f7f9fc}h1{margin-bottom:8px}label{margin-right:18px}select{padding:7px}main{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px}table{border-collapse:collapse;width:100%;background:white}th,td{padding:9px;border-bottom:1px solid #dde3ea;text-align:left}tr{cursor:pointer}tbody tr:hover{background:#eaf2ff}pre{background:#111c31;color:#ecf2fa;padding:18px;white-space:pre-wrap;overflow-wrap:anywhere;max-height:75vh;overflow:auto;border-radius:8px;margin:0}.scroll{max-height:75vh;overflow:auto}small{color:#506079}@media(max-width:1000px){main{grid-template-columns:1fr}}</style></head><body>
<h1>V2 GRPO rollout explorer</h1><p>Recorded sampled training episodes. Reward is not held-out accuracy. An accepted group is eligible for optimization; skipped groups never count as updates. The displayed optimizer step is the count before that rollout. Select a row to inspect the actual model conversation and MCP results.</p>
<div id="filters"></div><p id="count"></p><main><div class="scroll"><table><thead><tr><th>Stage</th><th>Step before</th><th>Attempt</th><th>Group</th><th>Language</th><th>Task</th><th>Reward</th><th>Calls</th></tr></thead><tbody id="rows"></tbody></table></div><pre id="trace">Select an episode.</pre></main><script>
const data=PAYLOAD;
const filters=document.getElementById('filters');const controls={};
for(const key of ['stage','language','kind','acceptance']){const label=document.createElement('label');label.textContent=key+' ';const select=document.createElement('select');for(const value of ['',...new Set(data.map(r=>r[key]))]){const opt=document.createElement('option');opt.value=value;opt.textContent=value||'All';select.append(opt)}label.append(select);filters.append(label);controls[key]=select;select.onchange=render}
function render(){const shown=data.filter(r=>Object.entries(controls).every(([k,c])=>!c.value||c.value===r[k]));document.getElementById('count').textContent=shown.length+' episodes';const body=document.getElementById('rows');body.replaceChildren();for(const r of shown){const tr=document.createElement('tr');for(const value of [r.stage,r.optimizer_step_before,r.attempt,r.acceptance,r.language,r.kind,r.reward.toFixed(3),r.calls]){const td=document.createElement('td');td.textContent=value;tr.append(td)}tr.onclick=()=>document.getElementById('trace').textContent=JSON.stringify(r,null,2);body.append(tr)}}render();
</script></body></html>'''.replace('PAYLOAD',payload)
    (root/'rollout_explorer.html').write_text(html)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('directory');args=parser.parse_args();export_viewer(args.directory)
