#!/usr/bin/env python3
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.tools.listing import lint_title
if __name__=='__main__':
 d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); out=lint_title(d['title'],d.get('max_chars'),d.get('required_terms'),d.get('forbidden_terms')); print(json.dumps(out,ensure_ascii=False,indent=2)); raise SystemExit(0 if out['pass'] else 1)
