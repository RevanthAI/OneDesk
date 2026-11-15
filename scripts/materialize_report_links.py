"""Replace tracked, internal report symlinks with cp -aL copies for GitHub."""
import json
import subprocess
import tempfile
from pathlib import Path
from clean_report_data import ROOT, protect


def materialize():
    protect();records=[]
    tracked=subprocess.check_output(['git','ls-files','-s'],cwd=ROOT,text=True).splitlines()
    for line in tracked:
        if not line.startswith('120000 '):continue
        name=line.split('\t',1)[1];path=ROOT/name
        if not path.is_symlink():continue
        if not name.startswith(('reports/','reports_v2/','reports_v2_1/','reports_v2_2/')):
            raise ValueError('Unexpected symlink outside report trees: '+name)
        target=path.resolve(strict=True);relative=target.relative_to(ROOT)
        with tempfile.TemporaryDirectory(prefix='.onedesk-portable-',dir=path.parent) as td:
            payload=Path(td)/'payload'
            subprocess.run(['cp','-aL','--',str(target),str(payload)],check=True)
            path.unlink();payload.rename(path)
        records.append(dict(path=name,source=str(relative),dereferenced=True))
    protect();return records

if __name__=='__main__':
    records=materialize();output=ROOT/'reports_submission/publishing_sync';output.mkdir(exist_ok=True)
    (output/'MATERIALIZED_LINKS.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps({'materialized_report_links':len(records),'protected_files':19}))
