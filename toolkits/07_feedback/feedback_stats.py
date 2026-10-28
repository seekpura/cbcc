#!/usr/bin/env python3
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.tools.feedback import analyze_feedback
p=argparse.ArgumentParser(); p.add_argument('input_json'); a=p.parse_args(); d=json.loads(Path(a.input_json).read_text(encoding='utf-8')); rows=d if isinstance(d,list) else d['rows']
print(json.dumps(analyze_feedback(rows),ensure_ascii=False,indent=2))
