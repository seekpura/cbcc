#!/usr/bin/env python3
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.tools.listing import spec_consistency
if __name__=='__main__':
 d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); out=spec_consistency(d['left'],d['right'],d['fields']); print(json.dumps({'pass':not out,'mismatches':out},ensure_ascii=False,indent=2)); raise SystemExit(1 if out else 0)
