#!/usr/bin/env python3
import json,sys
p=json.load(open(sys.argv[1],encoding='utf-8')); missing=[]
for k in ['capture_mode','composition','lighting','color_management']:
    if not p.get(k): missing.append(k)
if p.get('capture_mode') in {'REAL_PHOTO','PHOTOREAL_AI','COMPOSITE'}:
    if not p.get('camera'): missing.append('camera')
print(json.dumps({'pass':not missing,'missing':missing},indent=2)); sys.exit(1 if missing else 0)
