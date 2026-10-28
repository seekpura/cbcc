#!/usr/bin/env python3
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.tools.ads import analyze_ads
p=argparse.ArgumentParser(); p.add_argument('input_json'); a=p.parse_args(); d=json.loads(Path(a.input_json).read_text(encoding='utf-8'))
print(json.dumps(analyze_ads(d['ad_data'],d.get('price'),d.get('costs'),d.get('thresholds')),ensure_ascii=False,indent=2))
