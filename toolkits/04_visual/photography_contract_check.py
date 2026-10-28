#!/usr/bin/env python3
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.tools.visual import validate_photography_contract
p=argparse.ArgumentParser(); p.add_argument('contract_json'); a=p.parse_args(); d=json.loads(Path(a.contract_json).read_text(encoding='utf-8'))
o=validate_photography_contract(d); print(json.dumps(o,ensure_ascii=False,indent=2)); raise SystemExit(0 if o['pass'] else 1)
