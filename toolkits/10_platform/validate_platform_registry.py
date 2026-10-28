#!/usr/bin/env python3
from pathlib import Path
import sys
try: import yaml
except Exception: print('PyYAML required'); sys.exit(2)
p=Path(sys.argv[1]); d=yaml.safe_load(p.read_text(encoding='utf-8')); errors=[]
for k,v in d.get('platforms',{}).items():
    if not v.get('capabilities'): errors.append(f'{k}: no capabilities')
    if v.get('rules_status') not in {'VERIFIED','REVERIFY_REQUIRED'}: errors.append(f'{k}: bad rules_status')
print({'pass':not errors,'errors':errors}); sys.exit(1 if errors else 0)
