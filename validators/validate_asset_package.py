#!/usr/bin/env python3
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.asset_compiler import validate_asset_packages
p=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'artifacts/asset_packages'
out=validate_asset_packages(p)
print(json.dumps(out,ensure_ascii=False,indent=2)); raise SystemExit(0 if out['pass'] else 1)
