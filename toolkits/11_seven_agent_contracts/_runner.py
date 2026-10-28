from __future__ import annotations
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.tools.seven_agent import SEVEN_TOOLS

def run(tool:str):
    if len(sys.argv)>1 and sys.argv[1] not in {'-','--stdin'}:
        data=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    else:
        data=json.load(sys.stdin)
    fn=SEVEN_TOOLS[tool]
    out=fn(**data)
    print(json.dumps(out,ensure_ascii=False,indent=2))
