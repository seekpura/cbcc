#!/usr/bin/env python3
from pathlib import Path
import sys,re,json
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('skills')
neg=re.compile(r'\b(?:do not|don\'t|never|must not|forbid|prohibit|banned?)\b|禁止|不要|不得|严禁',re.I)
pos=re.compile(r'\b(?:create|build|use|prefer|define|select|express|show|preserve|deliver|recommend|focus|support|prioritize|design)\b|优先|采用|使用|表达|呈现|建立|输出|保留',re.I)
findings=[]
for p in sorted(root.glob('*/SKILL.md')):
    t=p.read_text(encoding='utf-8'); n=len(neg.findall(t)); q=len(pos.findall(t)); ratio=n/max(q,1)
    if n>=6 and ratio>0.60: findings.append({'file':str(p),'negative':n,'positive':q,'ratio':round(ratio,3)})
print(json.dumps({'pass':not findings,'findings':findings,'policy':'positive-first; necessary precision boundaries remain allowed'},ensure_ascii=False,indent=2)); raise SystemExit(1 if findings else 0)
