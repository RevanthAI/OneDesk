"""Public OneDesk demo: instant recorded evidence and opt-in live MCP inference."""
import os
os.environ.setdefault('GRADIO_ANALYTICS_ENABLED','False')
os.environ.setdefault('MPLCONFIGDIR','/tmp/onedesk-matplotlib')
from pathlib import Path
print('OneDesk startup: importing optional GPU SDK (no model weights).',flush=True)
try:from . import live_backend as _live_backend
except ImportError:import live_backend as _live_backend
print('OneDesk startup: importing Gradio.',flush=True)
import gradio as gr
try:from . import demo_core as core
except ImportError:import demo_core as core
ROOT=Path(__file__).resolve().parent
CSS='''
.gradio-container{max-width:1600px!important;background:#f7f9fc;font-family:Inter,system-ui,sans-serif;color:#14213d}
.odk-hero{padding:30px 34px;border-radius:22px;background:linear-gradient(115deg,#172554,#164e63);color:white;margin-bottom:18px}
.odk-hero h1{font-size:38px;letter-spacing:-1px;margin:0 0 8px}.odk-hero p{font-size:17px;color:#dbeafe;max-width:1050px}
.odk-hero h1,.odk-hero .odk-chips span{color:#fff!important}
.odk-chips span{display:inline-block;margin:6px 8px 0 0;padding:6px 12px;border:1px solid #ffffff55;border-radius:24px;font-size:13px}
.odk-result{background:white;border:1px solid #dbe3ef;border-radius:18px;padding:20px;margin:12px 0;color:#14213d}
.odk-result-head{display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}.odk-result h2{font-size:20px;margin:0 0 10px}
.odk-summary{background:#f1f5fb;padding:14px;border-radius:12px;margin:10px 0 16px}.odk-badges{display:flex;flex-wrap:wrap;gap:7px;margin-top:10px}
.odk-badge{display:inline-block;padding:5px 9px;border-radius:9px;font-size:12px;font-weight:650;margin:3px}.odk-badge.pass{background:#dcfce7;color:#166534}.odk-badge.fail{background:#fee2e2;color:#991b1b}.odk-badge.neutral{background:#e2e8f0;color:#334155}
.odk-step{border:1px solid #dbe3ef;border-left:5px solid #3b82f6;border-radius:12px;margin:14px 0;overflow:hidden}.odk-step-head{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:12px;background:#f8fafc;font-size:14px}
.odk-server{border-radius:7px;color:white;padding:4px 9px;font-size:12px;font-weight:700}.odk-observations{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:12px;padding:12px}
.odk-result pre,.odk-raw pre{white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word;max-height:360px;overflow:auto;background:#f7f9fc;padding:12px;border-radius:9px;color:#24334c;font-size:13px;line-height:1.6}
.odk-result h4{margin:2px 0 8px;font-size:13px;text-transform:uppercase;color:#64748b}.odk-prod{background:#bbf7d0;color:#14532d}.odk-stage{background:#fde68a;color:#78350f}.odk-resolution{background:#effdf5;border:1px solid #86efac;border-radius:14px;padding:18px}.odk-value{font-size:32px;font-weight:800;overflow-wrap:anywhere;margin:8px 0;color:#065f46}.odk-stale{padding:12px;background:#fffbeb;border-left:4px solid #f59e0b;border-radius:7px;margin:14px 0;font-size:15px}.odk-empty{background:#fff7ed;color:#9a3412;padding:14px;border-radius:9px;margin-bottom:12px}.odk-muted{color:#64748b}.odk-raw{background:white;padding:14px;border-radius:12px}
.odk-comparison .odk-observations{grid-template-columns:1fr}.odk-comparison .odk-result{padding:12px}.odk-comparison .odk-result h2{font-size:17px}.odk-comparison .odk-result pre{max-height:260px;font-size:12px}.odk-comparison .odk-value{font-size:25px}details summary{cursor:pointer;font-weight:650}
@media(max-width:900px){.odk-observations{grid-template-columns:1fr}.odk-hero h1{font-size:29px}}
'''
HERO='''<div class="odk-hero"><h1>🏢 OneDesk</h1><p>One multilingual workspace for company knowledge. Watch a 3.35B agent reconcile Notion, GitHub, Slack and live SQL evidence — then inspect every tool call.</p><div class="odk-chips"><span>500 held-out questions · 5 checkpoints</span><span>75.6% strict stale-doc catch</span><span>9 isolated MCP interfaces</span><span>English · Hindi · Hinglish · Telugu</span></div></div>'''
LANGUAGES=['All','en:latin','hi:native','hi:latin','hinglish:latin','te:native','te:latin']
KINDS=[('All','All'),('conflict (Stale Runbook)','conflict'),('consistent','consistent'),('incident (SQL + Math/Unit Chain)','incident'),('abstain (Missing Entity / Unplugged DB)','abstain')]
def selected(task_id):
 t=core.task(task_id);return t['question'],t['active_mcps']
def filter_sandbox(language,kind):
 options=core.choices(language,kind);first=options[0][1] if options else None
 if first:q,a=selected(first)
 else:q,a='',[]
 return gr.update(choices=options,value=first),q,a
def inspect(task_id,question,active):
 if not task_id:raise gr.Error('Choose a holdout task first.')
 return core.inspect_trace(task_id,question,active)
def filter_comparator(category):
 options=core.choices(category=category);return gr.update(choices=options,value=options[0][1] if options else None)
def compare(task_id):
 if not task_id:return ('<p>No task matches this filter.</p>',)*4
 return core.comparison(task_id)
def run_live(task_id,question,active,progress=gr.Progress()):
 if not os.getenv('HF_TOKEN'):raise gr.Error('Live model access is not configured on this host. Recorded verified traces remain available.')
 if task_id not in core.index()['tasks']:raise gr.Error('Choose a known holdout task before editing the question.')
 if not isinstance(question,str) or not question.strip() or len(question)>1800:raise gr.Error('Use a question between 1 and 1,800 characters.')
 if not isinstance(active,list) or not set(active)<=set(core.SCHEMAS):raise gr.Error('Choose servers from the supported MCP list.')
 try:
  try:from .live_backend import download_snapshots,gpu_episode
  except ImportError:from live_backend import download_snapshots,gpu_episode
  progress(.05,desc='Preparing pinned public base + adapter files (first run downloads weights)…')
  download_snapshots()
  progress(.3,desc='Running the model and isolated SQLite/MCP tools…')
  t,episode,runtime=gpu_episode(task_id,question,active)
  original=core.task(task_id);scored=question.strip()==original['question'].strip() and set(active)==set(original['active_mcps'])
  note=f"**Live model execution · {runtime['mode']} · {runtime['seconds']:.1f}s · {runtime['generated_tokens']} generated tokens.** "
  note+='Scores apply to this selected frozen question, not a new benchmark run.' if scored else 'Custom question/tools: benchmark scores and reference labels are disabled.'
  return core.render_episode(t,episode,'OneDesk · LIVE model + real MCP tools',scored),core.raw_trace(episode),note
 except Exception as error:raise gr.Error(f'Live inference unavailable: {type(error).__name__}: {error}. Saved verified traces remain available instantly.') from error

def build_app():
 options=core.choices();default=core.index()['flagships'][0]['task_id'];q,active=selected(default)
 first_html,first_raw,first_note=core.inspect_trace(default)
 with gr.Blocks(title='OneDesk · Company Knowledge Agent',theme=gr.themes.Soft(primary_hue='blue',secondary_hue='emerald'),css=CSS) as demo:
  gr.HTML(HERO)
  gr.Markdown('**Start with an instant recorded trace.** Live mode generates a fresh answer through real, read-only SQLite and MCP tools; cold model downloads can take several minutes. All company worlds are synthetic.')
  with gr.Tabs():
   with gr.Tab('🚀 Sandbox · Trace + Live'):
    gr.Markdown('### Interactive OneDesk Sandbox · formatted trace + live GPU / CPU')
    with gr.Row():
     language=gr.Dropdown(LANGUAGES,value='All',label='Language / script')
     kind=gr.Dropdown(KINDS,value='All',label='Task kind')
    picker=gr.Dropdown(options,value=default,label='★ Curated flagships + all 500 holdouts',filterable=True)
    question=gr.Textbox(value=q,label='Question · editable for Live mode',lines=3,max_lines=6)
    servers=gr.CheckboxGroup(list(core.SCHEMAS),value=active,label='Active MCP servers · editable for Live mode')
    with gr.Row():
     instant=gr.Button('⚡ Inspect Verified OneDesk Trace (Instant)',variant='primary')
     live=gr.Button('🔥 Run Live Model Inference in MCP Sandbox (GPU / CPU)',variant='secondary',interactive=bool(os.getenv('HF_TOKEN')))
    if not os.getenv('HF_TOKEN'):gr.Markdown('**Live model access awaits owner configuration.** The base model is gated; recorded traces and all comparison/explorer features work without model access.')
    mode=gr.Markdown(first_note);trace=gr.HTML(first_html)
    with gr.Accordion('Exact raw XML / JSON protocol',open=False):raw=gr.Code(first_raw,language='html',lines=10,interactive=False)
    picker.change(selected,[picker],[question,servers],queue=False,api_name=False)
    for control in [language,kind]:control.change(filter_sandbox,[language,kind],[picker,question,servers],queue=False,api_name=False)
    instant.click(inspect,[picker,question,servers],[trace,raw,mode],queue=False,api_name='inspect_trace')
    live.click(run_live,[picker,question,servers],[trace,raw,mode],concurrency_limit=1,concurrency_id='live_model',api_name='live_inference')
   with gr.Tab('⚖️ Checkpoint Comparator'):
    gr.Markdown('### Side-by-side checkpoint comparison · all 500 holdouts')
    gr.Markdown('Every card is an actual recorded holdout episode. Warmup SFT is also available in the bundled five-checkpoint trace index; this view highlights four experimental controls.')
    quick=[]
    with gr.Row():
     for label,value in [('All 500 questions','all'),('🏆 OneDesk stale-doc wins','wins'),('⛔ RL false refusals','collapse'),('🌐 Hindi / Telugu / Hinglish','languages'),('🧮 SQL + unit chains','chains')]:quick.append((gr.Button(label,size='sm'),value))
    comp_picker=gr.Dropdown(options,value=default,label='Compare the same task across checkpoints',filterable=True)
    comp=gr.Button('Compare recorded checkpoints',variant='primary')
    outputs=[]
    with gr.Row(elem_classes='odk-comparison'):
     for value in core.comparison(default):
      with gr.Column(min_width=270):outputs.append(gr.HTML(value))
    def quick_handler(value):
     def apply():return filter_comparator(value)
     return apply
    for button,value in quick:button.click(quick_handler(value),None,[comp_picker],queue=False,api_name=False)
    comp.click(compare,[comp_picker],outputs,queue=False,api_name='compare_checkpoints')
    comp_picker.change(compare,[comp_picker],outputs,queue=False,api_name=False)
   with gr.Tab('🧭 RL Rollout Explorer') as journal_tab:
    gr.Markdown('### RL rollout explorer · G=6 GRPO journals')
    gr.Markdown('Actual G=6 training groups, sampled answers, advantages and reward diagnostics. Loaded on demand so instant traces stay lightweight. Training journals are not holdout evaluation.')
    journals=gr.HTML('<p>Open this tab to load the interactive rollout explorer.</p>')
    journal_tab.select(lambda:core.iframe('rollout_explorer.html'),None,journals,queue=False,api_name=False)
   with gr.Tab('📊 Benchmarks & ROI') as dashboard_tab:
    gr.Markdown('### Benchmark dashboard & enterprise ROI calculator')
    with gr.Row():
     queries=gr.Slider(10000,500000,value=100000,step=10000,label='Monthly queries')
     hourly=gr.Slider(.1,10,value=1.8,step=.05,label='Self-hosted L40S USD / hour')
    with gr.Row():
     api_in=gr.Slider(0,20,value=2.5,step=.25,label='API input USD / 1M tokens')
     api_out=gr.Slider(0,100,value=10,step=.5,label='API output USD / 1M tokens')
    rows,description=core.roi(100000,1.8,2.5,10)
    roi_summary=gr.Markdown(description)
    roi_table=gr.Dataframe(value=rows,headers=['Serving option','USD / month','USD / 1k','GPU hours / month','Basis'],interactive=False)
    gr.Markdown('Costs exclude hardware purchase, staff and operations. Local latency/VRAM comes from the **v1 NF4 adapter**, while cloud throughput uses v2 BF16. API prices are editable historical scenarios; equal API answer quality was not measured. Average episode volume: 4,653.332 input and 153.322 generated tokens.')
    for slider in [queries,hourly,api_in,api_out]:slider.change(core.roi,[queries,hourly,api_in,api_out],[roi_table,roi_summary],queue=False,api_name=False)
    for name in ['1_headline_success.png','2_multilingual_reach.png','3_training_journey.png','4_cost_and_privacy_roi.png']:
     gr.Image(str(core.ASSETS/'figures'/name),show_label=False,interactive=False)
    dashboard=gr.HTML('<p>Training dashboard loads when this tab opens.</p>')
    dashboard_tab.select(lambda:core.iframe('dashboard.html'),None,dashboard,queue=False,api_name=False)
  gr.Markdown('[GitHub](https://github.com/RevanthAI/OneDesk) · [Models](https://huggingface.co/collections/Revanth-ml/onedesk-models-and-experimental-controls-6af97221a617ddc3326204a6) · [Data](https://huggingface.co/collections/Revanth-ml/onedesk-data-and-experiment-evidence-6af97225c0f1dc548b9ba8ce)\n\nCode: Apache-2.0 · Synthetic data: CC-BY-4.0 · Base/model adapters: CC-BY-NC-4.0. This is a research sandbox with synthetic company records, unrelated to the commercial OneDesk helpdesk product.')
 return demo.queue(default_concurrency_limit=2,max_size=20)

print('OneDesk startup: building the recorded-trace UI.',flush=True)
demo=build_app()
print('OneDesk startup: UI ready; model loading remains opt-in.',flush=True)
if __name__=='__main__':demo.launch(server_name='0.0.0.0',server_port=int(os.getenv('PORT','7860')),allowed_paths=[str(core.ASSETS)],show_error=True)
