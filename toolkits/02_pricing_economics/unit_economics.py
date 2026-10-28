#!/usr/bin/env python3
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.tools.economics import unit_economics,economics_strategy
p=argparse.ArgumentParser(); p.add_argument('input_json'); a=p.parse_args(); d=json.loads(Path(a.input_json).read_text(encoding='utf-8'))
out=economics_strategy(d['scenarios'],d.get('demand_signals')) if 'scenarios' in d else unit_economics(d['price'],d['costs'])
print(json.dumps(out,ensure_ascii=False,indent=2))
