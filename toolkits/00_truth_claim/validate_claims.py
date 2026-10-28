#!/usr/bin/env python3
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.tools.truth import validate_claims
if __name__=="__main__":
    d=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")); e=validate_claims(d); print(json.dumps({"pass":not e,"errors":e},ensure_ascii=False,indent=2)); raise SystemExit(1 if e else 0)
