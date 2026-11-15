"""Optional desktop/mobile browser verification. Never clicks live inference."""
import argparse,json
from pathlib import Path

def main():
 from playwright.sync_api import sync_playwright
 p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:7878');p.add_argument('--output',type=Path,default=Path('reports/submission/space'));a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 errors=[]
 with sync_playwright() as driver:
  browser=driver.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1600,'height':1100},device_scale_factor=1)
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(a.url,wait_until='networkidle',timeout=90000)
  page.get_by_role('button',name='⚡ Inspect Verified OneDesk Trace (Instant)',exact=True).click();page.wait_for_load_state('networkidle')
  page.get_by_text('OneDesk · saved verified trace',exact=True).wait_for()
  page.screenshot(path=str(a.output/'SANDBOX_DESKTOP.png'),full_page=True)
  color=page.locator('.odk-hero h1').evaluate('(e)=>getComputedStyle(e).color');assert color=='rgb(255, 255, 255)',color
  page.get_by_role('tab',name='⚖️ Checkpoint Comparator',exact=True).click()
  page.get_by_role('button',name='Compare recorded checkpoints',exact=True).click();page.wait_for_load_state('networkidle')
  assert page.locator('.odk-comparison .odk-result').count()==4
  page.get_by_role('button',name='🏆 OneDesk stale-doc wins',exact=True).click();page.wait_for_load_state('networkidle')
  page.screenshot(path=str(a.output/'COMPARATOR_DESKTOP.png'),full_page=True)
  page.get_by_role('tab',name='🧭 RL Rollout Explorer',exact=True).click()
  frame=page.frame_locator('iframe[title="rollout_explorer.html"]');frame.locator('select').first.wait_for(timeout=45000)
  assert frame.locator('select').count()>0
  page.get_by_role('tab',name='📊 Benchmarks & ROI',exact=True).click()
  page.get_by_text('Self-hosted L40S BF16',exact=True).first.wait_for();page.wait_for_load_state('networkidle')
  page.screenshot(path=str(a.output/'ROI_DESKTOP.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844});page.get_by_role('tab',name='🚀 Sandbox · Trace + Live',exact=True).click();page.wait_for_load_state('networkidle')
  page.screenshot(path=str(a.output/'SANDBOX_MOBILE.png'),full_page=True)
  width=page.evaluate('({body:document.documentElement.scrollWidth,viewport:innerWidth})');assert width['body']<=width['viewport']+2,width
  result={'url':a.url,'all_four_tabs_checked':True,'comparator_columns':4,'journals_javascript_controls_present':True,'desktop_and_mobile':True,'hero_contrast_checked':True,'mobile_width':width,'page_errors':errors,'model_inference_triggered':False}
  (a.output/'BROWSER_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));browser.close()
if __name__=='__main__':main()
