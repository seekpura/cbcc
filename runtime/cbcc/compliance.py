from __future__ import annotations
from typing import Any
import re

_NUM=re.compile(r'(?<!\w)(\d+(?:\.\d+)?\s*(?:%|g|kg|ml|l|cm|mm|h|hr|hours?|x))',re.I)


def compile_compliance(product_truth:dict[str,Any], claims:list[dict[str,Any]], listing:dict[str,Any]|None, assets:list[dict[str,Any]]|None, platform_compile:dict[str,Any], research_gate:dict[str,Any]|None=None)->dict[str,Any]:
    claims=claims or []; assets=assets or []; approved={c.get('claim_id') for c in claims if c.get('claim_id') and str(c.get('evidence_grade') or c.get('evidence_level') or '').upper() in {'A','B'} and str(c.get('publication_status') or '').upper() not in {'BLOCKED','SOFT_ONLY_NO_HARD_CLAIM'}}
    issues=[]; checks=[]
    for c in claims:
        grade=str(c.get('evidence_grade') or c.get('evidence_level') or '').upper()
        if c.get('claim_id') and grade not in {'A','B','C'}: issues.append({'scope':c.get('claim_id'),'code':'CLAIM_EVIDENCE_GRADE_MISSING'})
        if c.get('claim_id') and grade=='C' and str(c.get('status') or '').upper() in {'APPROVED','VERIFIED','ACTIVE'}: issues.append({'scope':c.get('claim_id'),'code':'C_GRADE_CANNOT_BE_HARD_APPROVED'})
    for a in assets:
        unknown=[x for x in a.get('claim_ids',[]) if x not in approved]
        if unknown: issues.append({'scope':a.get('asset_id'),'code':'UNAPPROVED_CLAIM_REFERENCE','claim_ids':unknown})
        checks.append({'asset_id':a.get('asset_id'),'claim_ids':a.get('claim_ids',[]),'status':'PASS' if not unknown else 'HOLD'})
    listing_status=(listing or {}).get('status') or ((listing or {}).get('compiled') or {}).get('status')
    research_rows=list((research_gate or {}).get('pending') or [])
    research_pending=bool(research_rows)
    research_blocking_pending=any(bool(row.get('blocking', True)) for row in research_rows)
    platform_ready=platform_compile.get('status') in {'VERIFIED_FOR_REQUEST','FAMILY_PLANNING_ONLY','PLANNING_ONLY_RESEARCH_PENDING'}
    return {
        'status':'HOLD' if issues or research_blocking_pending or not platform_ready else 'READY_REVIEW',
        'issues':issues,'asset_checks':checks,'listing_status':listing_status,'platform_status':platform_compile.get('status'),
        'research_pending':research_pending,'research_blocking_pending':research_blocking_pending,
        'layers':{'product':'SOURCE_BOUND','claim':'LEDGER_BOUND','creative':'ASSET_BOUND','platform':'CURRENT_EVIDENCE_BOUND'},
        'principle':'Compliance compiles evidence and current platform scope; it does not manufacture legal or regulatory approval.'
    }
