from __future__ import annotations
from pathlib import Path
import json

def validate_sources(doc:dict):
    errors=[]
    for i,s in enumerate(doc.get('sources',[])):
        if not s.get('source_id'): errors.append(f'source[{i}] missing source_id')
        if not (s.get('path') or s.get('url') or s.get('kind')=='USER_PROVIDED_FACT'): errors.append(f"{s.get('source_id','source?')} missing path/url")
    return errors

def validate_claims(doc:dict):
    errors=[]; source_ids={s.get('source_id') for s in doc.get('sources',[]) if s.get('source_id')}
    for c in doc.get('claims',[]):
        if not c.get('claim_id'): errors.append('claim missing claim_id')
        if c.get('status')=='APPROVED' and not c.get('evidence_source_ids'): errors.append(f"{c.get('claim_id')} approved without evidence")
        for sid in c.get('evidence_source_ids',[]):
            if sid not in source_ids: errors.append(f"{c.get('claim_id')} unknown source {sid}")
    return errors
