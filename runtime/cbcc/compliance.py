from __future__ import annotations
from typing import Any
import re

_NUM=re.compile(r'(?<!\w)(\d+(?:\.\d+)?\s*(?:%|g|kg|ml|l|cm|mm|h|hr|hours?|x))',re.I)


def compile_compliance(product_truth:dict[str,Any], claims:list[dict[str,Any]], listing:dict[str,Any]|None, assets:list[dict[str,Any]]|None, platform_compile:dict[str,Any], research_gate:dict[str,Any]|None=None)->dict[str,Any]:
    claims=claims or []; assets=assets or []
    # Asset-reference routing and publication evidence are separate authorities.
    # A raw/direct caller may explicitly mark a known claim APPROVED before Claim Authority normalization;
    # that makes the claim a known reference target, but missing/weak evidence still creates claim_issues
    # and keeps overall Compliance on HOLD. Explicit C-grade or blocked claims are never route-authorized.
    route_authorized={
        c.get('claim_id') for c in claims
        if c.get('claim_id')
        and str(c.get('publication_status') or '').upper() not in {'BLOCKED','SOFT_ONLY_NO_HARD_CLAIM'}
        and str(c.get('status') or '').upper() not in {'BLOCKED','PROHIBITED','REJECTED','INVALID'}
        and (
            str(c.get('evidence_grade') or c.get('evidence_level') or '').upper() in {'A','B'}
            or (
                not str(c.get('evidence_grade') or c.get('evidence_level') or '').upper()
                and str(c.get('status') or '').upper() in {'APPROVED','VERIFIED','ACTIVE'}
            )
        )
    }
    claim_issues=[]; asset_issues=[]; checks=[]

    def issue(*, scope, code, claim_ids=None, asset_id=None, severity='HOLD', details=None):
        row={
            'scope':scope,
            'asset_id':asset_id,
            'code':code,
            'claim_ids':list(claim_ids or []),
            'severity':severity,
        }
        if details:
            row['details']=details
        return row

    for c in claims:
        cid=c.get('claim_id')
        grade=str(c.get('evidence_grade') or c.get('evidence_level') or '').upper()
        declared_status=str(c.get('status') or '').upper()
        if cid and grade not in {'A','B','C'}:
            claim_issues.append(issue(scope=cid, code='CLAIM_EVIDENCE_GRADE_MISSING', claim_ids=[cid]))
        if cid and grade=='C' and declared_status in {'APPROVED','VERIFIED','ACTIVE'}:
            claim_issues.append(issue(scope=cid, code='C_GRADE_CANNOT_BE_HARD_APPROVED', claim_ids=[cid]))

    for a in assets:
        asset_id=a.get('asset_id')
        unknown=[x for x in a.get('claim_ids',[]) if x not in route_authorized]
        if unknown:
            asset_issues.append(issue(scope=asset_id, asset_id=asset_id, code='UNAPPROVED_CLAIM_REFERENCE', claim_ids=unknown))
        checks.append({
            'asset_id':asset_id,
            'claim_ids':a.get('claim_ids',[]),
            'unapproved_claim_ids':unknown,
            'status':'PASS' if not unknown else 'HOLD',
        })

    # Asset-routing problems are first because they are directly actionable by callers.
    issues=asset_issues+claim_issues
    listing_status=(listing or {}).get('status') or ((listing or {}).get('compiled') or {}).get('status')
    research_rows=list((research_gate or {}).get('pending') or [])
    research_pending=bool(research_rows)
    research_blocking_pending=any(bool(row.get('blocking', True)) for row in research_rows)
    platform_ready=platform_compile.get('status') in {'VERIFIED_FOR_REQUEST','FAMILY_PLANNING_ONLY','PLANNING_ONLY_RESEARCH_PENDING'} or (platform_compile.get('status')=='RESEARCH_REQUIRED' and not research_blocking_pending)
    return {
        'status':'HOLD' if issues or research_blocking_pending or not platform_ready else 'READY_REVIEW',
        'issues':issues,
        'claim_issues':claim_issues,
        'asset_issues':asset_issues,
        'asset_checks':checks,
        'listing_status':listing_status,
        'platform_status':platform_compile.get('status'),
        'research_pending':research_pending,
        'research_blocking_pending':research_blocking_pending,
        'issue_contract':{
            'required_keys':['scope','asset_id','code','claim_ids','severity'],
            'ordering':'ASSET_ROUTING_FIRST_THEN_CLAIM_LEDGER',
        },
        'layers':{'product':'SOURCE_BOUND','claim':'LEDGER_BOUND','creative':'ASSET_BOUND','platform':'CURRENT_EVIDENCE_BOUND'},
        'principle':'Compliance compiles evidence and current platform scope; it does not manufacture legal or regulatory approval.'
    }
