#!/usr/bin/env python3
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.tools.listing import compile_listing,keyword_architecture
p=argparse.ArgumentParser(); p.add_argument('input_json'); a=p.parse_args(); d=json.loads(Path(a.input_json).read_text(encoding='utf-8'))
out={'listing':compile_listing(d.get('fields',{}),d.get('facts',{}),d.get('claims',[]),d.get('rules',{})),'keyword_architecture':keyword_architecture(d.get('keywords',[]))}
print(json.dumps(out,ensure_ascii=False,indent=2)); raise SystemExit(0 if out['listing']['pass'] else 1)
