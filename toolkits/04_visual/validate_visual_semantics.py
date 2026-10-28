#!/usr/bin/env python3
import json,sys
p=json.load(open(sys.argv[1],encoding='utf-8'))
allowed={'ALLOW','ALLOW_AS_ABSTRACT','CONDITIONAL','BLOCK'}; errors=[]
for i,x in enumerate(p.get('visual_semantics',[])):
    if x.get('decision') not in allowed: errors.append(f'item {i}: invalid decision')
    if not x.get('element'): errors.append(f'item {i}: missing element')
print(json.dumps({'pass':not errors,'errors':errors},indent=2)); sys.exit(1 if errors else 0)
