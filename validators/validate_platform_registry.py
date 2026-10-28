#!/usr/bin/env python3
from pathlib import Path
from datetime import date
import sys,yaml,json
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 and Path(sys.argv[1]).is_dir() else Path('.').resolve()
reg=(root/'references/platforms/platform_registry.yaml') if root.is_dir() else Path(sys.argv[1])
d=yaml.safe_load(reg.read_text(encoding='utf-8')); errors=[]; exact=[]
for k,v in d.get('platforms',{}).items():
    if not v.get('capabilities'): errors.append(f'{k}: no capabilities')
    if v.get('rules_status') not in {'VERIFIED','VERIFIED_SITE_GENERIC','REVERIFY_REQUIRED'}: errors.append(f'{k}: bad rules_status')
pack_dir=root/'platform_packs' if root.is_dir() else reg.parents[2]/'platform_packs'
if pack_dir.exists():
    for p in pack_dir.glob('*.yaml'):
        x=yaml.safe_load(p.read_text(encoding='utf-8')) or {}
        if x.get('site') in {None,'*'} or x.get('synthetic_for_test'): continue
        exact.append(x.get('pack_id'))
        if not x.get('source_records'): errors.append(f'{p.name}: exact pack missing source_records')
        atoms=x.get('rule_atoms',[]) or []
        if not atoms: errors.append(f'{p.name}: exact pack missing rule_atoms')
        for a in atoms:
            if a.get('authority')!='OFFICIAL': errors.append(f"{p.name}:{a.get('rule_id')}: exact rule not OFFICIAL")
            if not a.get('source_url') or not a.get('verified_at') or not a.get('expires_at'): errors.append(f"{p.name}:{a.get('rule_id')}: incomplete freshness/source")
print(json.dumps({'pass':not errors,'errors':errors,'exact_packs':exact},ensure_ascii=False,indent=2)); sys.exit(1 if errors else 0)
