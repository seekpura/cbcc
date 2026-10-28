#!/usr/bin/env python3
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.tools.video import timing
if __name__=='__main__':
 d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); out=timing(d['segments'],d['target_seconds']); print(json.dumps(out,ensure_ascii=False,indent=2)); raise SystemExit(0 if out['pass'] else 1)
