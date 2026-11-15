"""CPU-only content checks and mocked publication checks; no remote mutations."""
import ast
import contextlib
import io
import json
import re
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import yaml
from PIL import Image
from clean_report_data import ROOT, protect, digest
import prepare_hf_repos as publisher
import build_clean_report


def main():
    protect();cards=publisher.CARDS;plan=json.loads((cards/'PLAN.json').read_text())
    assert (plan['models'],plan['datasets'])==(9,6)
    assert len(plan['repositories'])==15
    snippets=0
    for entry in plan['repositories']:
        path=ROOT/entry['card'];assert path.is_file() and not path.is_symlink()
        text=path.read_text();metadata=yaml.safe_load(text.split('---',2)[1]);assert metadata['license']
        if entry['repo_type']=='model':
            assert metadata['license']=='cc-by-nc-4.0' and metadata['base_model']=='CohereLabs/tiny-aya-fire'
            assert metadata['tags']==publisher.TAGS
        else:
            assert metadata['license']=='cc-by-4.0'
        for code in re.findall(r'```python\n(.*?)```',text,re.S):ast.parse(code);snippets+=1
    figures=[]
    for n in range(1,5):
        png=next((ROOT/'figures').glob(f'{n}_*.png'));svg=png.with_suffix('.svg')
        assert svg.exists() and not png.is_symlink() and not svg.is_symlink()
        with Image.open(png) as im:
            assert im.width>=4000 and im.height>=2000
            assert all(abs(x-300)<1 for x in im.info['dpi'])
            figures.append(dict(path=str(png.relative_to(ROOT)),size=list(im.size),dpi=list(im.info['dpi'])))
    report=(ROOT/'REPORT.md').read_text()
    assert report.startswith('# OneDesk:') and 'SangamKB' not in report
    assert [int(x) for x in re.findall(r'^## (\d+)\.',report,re.M)]==list(range(1,11))
    assert 'targets, not measured results' in report and 'pending `--publish`' in report
    assert '**CC-BY-4.0**' in report and '**Apache-2.0**' in report
    chart=json.loads((ROOT/'figures/CHART_DATA.json').read_text())['charts'][1]['values']
    for split,expected in [('test_synth',[77.,76.,66.,71.]),('repo_style',[64.,64.,64.,64.])]:
        assert len(chart[split])==3
        assert chart[split]['Warmup SFT · 60 steps']==expected
        assert all(a>=b for a,b in zip(chart[split]['Final OneDesk · selected update 40'],expected))
    assert report.count('<tool_call>')==2 and 'train_sft-0000-hinglish' in report
    missing=[]
    for target in re.findall(r'\]\(([^)]+)\)',report):
        if target.startswith(('https://','http://','#')):continue
        if not (ROOT/target.split('#')[0]).exists():missing.append(target)
    assert not missing,missing
    # A dry run must not instantiate a client or attempt a connection.
    with patch('huggingface_hub.HfApi',side_effect=AssertionError('Network client in dry-run')),patch('socket.create_connection',side_effect=AssertionError('Network call in dry-run')),contextlib.redirect_stdout(io.StringIO()):
        publisher.main(['--dry-run'])
    generated_plan=json.loads((cards/'PLAN.json').read_text())
    assert generated_plan['network_calls']==0
    mutation_checks=[]
    for rename in [False,True]:
        simulated=json.loads(json.dumps(generated_plan))
        if rename:
            simulated['repo_mapping']={r['repo_id']:publisher.target_name(r['repo_id'],'onedesk') for r in simulated['repositories']}
            for r in simulated['repositories']:r['target_repo_id']=simulated['repo_mapping'][r['repo_id']]
        original={r['repo_id'] for r in simulated['repositories']};calls=[]
        class FakeApi:
            def __init__(self,token):assert token=='mock-not-a-real-token'
            def whoami(self):return {'name':'Revanth-ml'}
            def repo_info(self,repo_id,**kw):
                from huggingface_hub.errors import RepositoryNotFoundError
                if repo_id not in original:raise RepositoryNotFoundError('Mock rename target absent')
                calls.append(('read',repo_id));return SimpleNamespace(private=True)
            def upload_file(self,**kw):calls.append(('upload',kw['repo_id']));assert kw['path_in_repo']=='README.md'
            def move_repo(self,**kw):calls.append(('move',kw['from_id']))
            def update_repo_visibility(self,**kw):calls.append(('public',kw['repo_id']));assert kw['private'] is False
            def create_collection(self,**kw):
                calls.append(('collection',kw['title']));assert kw['private'] is False
                return SimpleNamespace(slug='Revanth-ml/'+('models' if 'Models' in kw['title'] else 'data'),url='https://example.invalid/mock-collection')
            def update_collection_metadata(self,collection_slug,**kw):
                calls.append(('collection_public',collection_slug));assert kw['private'] is False
                return SimpleNamespace(slug=collection_slug,url='https://huggingface.co/collections/'+collection_slug)
            def add_collection_item(self,**kw):calls.append(('item',kw['item_id']));assert kw['exists_ok'] is True
        with tempfile.TemporaryDirectory(prefix='onedesk-mock-publish-',dir='/tmp') as td:
            with patch.object(publisher,'CARDS',Path(td)),patch('huggingface_hub.HfApi',FakeApi),patch('dotenv.load_dotenv',return_value=False),patch.dict('os.environ',{'HUGGINGFACE_TOKEN':'mock-not-a-real-token'}),patch.object(build_clean_report,'build',return_value='mocked; real report unchanged') as rebuilt:
                result=publisher.publish(simulated)
                rebuilt.assert_called_once_with(publication=result)
            with contextlib.redirect_stdout(io.StringIO()):
                published_report=build_clean_report.build(publication=result,output_path=Path(td)/'REPORT.md')
            assert result['model_collection_url'] in published_report and result['data_collection_url'] in published_report
            assert result['model_collection_url']!=result['data_collection_url']
            assert 'MODEL_COLLECTION_URL' not in published_report and 'DATA_COLLECTION_URL' not in published_report
            assert result['complete'] and len(calls)>0
            counts={key:sum(c[0]==key for c in calls) for key in ['read','upload','move','public','collection','item']}
            assert counts['upload']==15 and counts['public']==15 and counts['collection']==2 and counts['item']==15
            assert counts['move']==(15 if rename else 0)
            assert max(i for i,c in enumerate(calls) if c[0]=='read')<min(i for i,c in enumerate(calls) if c[0]=='upload')
            mutation_checks.append(dict(mocked=True,rename=rename,counts=counts))
    assert not (cards/'PUBLISH_RECEIPT.json').exists(),'Unexpected real publication receipt'
    assert not (cards/'PUBLISH_PROGRESS.json').exists(),'Unexpected real publication progress'
    assert digest('REPORT.md')==json.loads((ROOT/'reports_submission/clean_assets/REPORT_METADATA.json').read_text())['sha256']
    protect()
    result=dict(cards=15,model_cards=9,dataset_cards=6,python_snippets_parsed=snippets,yaml_valid=True,charts=figures,
                local_report_links_valid=True,dry_run_network_calls=0,mock_publication=mutation_checks,
                remote_publication_performed=False,protected_files=19)
    (ROOT/'reports_submission/clean_assets/ASSET_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
