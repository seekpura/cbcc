#!/usr/bin/env python3
from pathlib import Path
import zipfile,sys,hashlib,json

ROOT=Path(__file__).resolve().parents[1]
out=(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/f'{ROOT.name}.zip').resolve()
out.parent.mkdir(parents=True,exist_ok=True)
exclude_parts={'__pycache__','.pytest_cache','.git'}
exclude_suffix={'.pyc','.pyo'}
exclude_roots={'evidence','dist'}

with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if not p.is_file():
            continue
        if p.resolve()==out:
            continue
        if rel.parts and rel.parts[0] in exclude_roots:
            continue
        if any(x in exclude_parts for x in rel.parts) or p.suffix in exclude_suffix:
            continue
        z.write(p,Path(ROOT.name)/rel)

h=hashlib.sha256(out.read_bytes()).hexdigest()
print(json.dumps({'output':str(out),'sha256':h,'bytes':out.stat().st_size},indent=2))
