#!/usr/bin/env python3
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.io import load_tabular,apply_field_map
from cbcc.tools.market import analyze_market
p=argparse.ArgumentParser(description='Load CSV/XLSX/JSON market exports and run the canonical market engine')
p.add_argument('input_file'); p.add_argument('--sheet'); p.add_argument('--field-map-json'); p.add_argument('--price-step',type=float); p.add_argument('--config-key',default='configuration')
a=p.parse_args(); fmap=json.loads(Path(a.field_map_json).read_text(encoding='utf-8')) if a.field_map_json else None
rows=apply_field_map(load_tabular(a.input_file,a.sheet),fmap)
print(json.dumps(analyze_market(rows,a.price_step,a.config_key),ensure_ascii=False,indent=2))
