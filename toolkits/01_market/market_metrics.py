#!/usr/bin/env python3
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.tools.market import analyze_market
p=argparse.ArgumentParser(description='Deterministic market metrics over supplied rows only')
p.add_argument('input_json'); p.add_argument('--price-step',type=float); p.add_argument('--config-key',default='configuration')
a=p.parse_args(); d=json.loads(Path(a.input_json).read_text(encoding='utf-8')); rows=d if isinstance(d,list) else d['rows']
print(json.dumps(analyze_market(rows,a.price_step,a.config_key),ensure_ascii=False,indent=2))
