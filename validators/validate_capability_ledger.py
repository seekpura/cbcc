#!/usr/bin/env python3
from pathlib import Path
import sys,yaml,json
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('.').resolve()
ledger=yaml.safe_load((root/'references/capability_ledger.yaml').read_text(encoding='utf-8'))
errors=[]; counts={}
for cap in ledger.get('capabilities',[]):
    if not cap.get('required'): continue
    cid=cap.get('id'); maturity=cap.get('maturity','UNKNOWN'); counts[maturity]=counts.get(maturity,0)+1
    for field in ['implementation_paths','trigger_examples','runtime_consumers','behavior_test','e2e_evidence','maturity']:
        if not cap.get(field): errors.append(f'{cid}: missing {field}')
    for rel in (cap.get('implementation_paths') or [])+(cap.get('runtime_consumers') or []):
        if not (root/rel).exists(): errors.append(f'{cid}: missing path {rel}')
    for rel in [cap.get('behavior_test'),cap.get('e2e_evidence')]:
        if rel and not (root/rel).exists(): errors.append(f'{cid}: missing evidence {rel}')
print(json.dumps({'pass':not errors,'required_count':sum(counts.values()),'maturity_counts':counts,'errors':errors},ensure_ascii=False,indent=2)); raise SystemExit(1 if errors else 0)
