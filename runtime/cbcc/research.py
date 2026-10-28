from __future__ import annotations
from datetime import date
from typing import Any
from .models import ResearchAction, stable_hash

HIGH_RISK_DOMAINS={'PLATFORM_RULE','REGULATION','FEE','LOGISTICS','CERTIFICATION','CLAIM','LEGAL','CATEGORY_POLICY'}


def compile_research_gate(requirements:list[dict[str,Any]]|None, supplied_sources:list[dict[str,Any]]|None, as_of:str|None=None)->dict[str,Any]:
    """Turn evidence gaps into structured host actions instead of silent inference."""
    requirements=requirements or []; supplied_sources=supplied_sources or []
    source_ids={s.get('source_id') for s in supplied_sources if s.get('source_id')}
    actions=[]; resolved=[]; pending=[]
    for row in requirements:
        rid=row.get('id') or 'REQ-'+stable_hash(row)[:10]
        needed=set(row.get('source_ids',[]))
        verified=bool(needed and needed.issubset(source_ids)) or bool(row.get('verified'))
        blocking=bool(row.get('blocking', True))
        rec={'requirement_id':rid,'topic':row.get('topic'),'domain':row.get('domain','GENERAL'),'required_for':row.get('required_for',[]),'verified':verified,'blocking':blocking}
        if verified:
            resolved.append(rec); continue
        pending.append(rec)
        domain=str(row.get('domain','GENERAL')).upper()
        action=ResearchAction(
            'RA-'+stable_hash([rid,row.get('topic')])[:10],
            row.get('reason') or f"Current evidence is needed for {row.get('topic') or rid}",
            row.get('query') or f"Verify current authoritative evidence for {row.get('topic') or rid}",
            row.get('required_for',[]) or ['RESEARCH'],
            preferred_source=row.get('preferred_source') or ('OFFICIAL_CURRENT_SOURCE' if domain in HIGH_RISK_DOMAINS else 'AUTHORITATIVE_CURRENT_SOURCE')
        ).to_dict()
        action['blocking']=blocking
        actions.append(action)
    return {
        'status':'READY' if not pending else 'RESEARCH_REQUIRED',
        'resolved':resolved,'pending':pending,'actions':actions,
        'blocking_pending':[row for row in pending if row.get('blocking')],
        'advisory_pending':[row for row in pending if not row.get('blocking')],
        'as_of':as_of or date.today().isoformat(),
        'principle':'Evidence-dependent strategy proceeds only to the scope supported by current sources; unresolved items become structured host actions.'
    }


def apply_host_research_response(gate:dict[str,Any], responses:list[dict[str,Any]]|None)->dict[str,Any]:
    responses=responses or []; resolved_ids={r.get('action_id') for r in responses if r.get('status')=='RESOLVED'}
    actions=[]
    for a in gate.get('actions',[]):
        x=dict(a)
        if x.get('action_id') in resolved_ids: x['status']='RESOLVED'
        actions.append(x)
    unresolved=[a for a in actions if a.get('status')!='RESOLVED']
    return {**gate,'actions':actions,'host_status':'RESOLVED' if not unresolved else 'PENDING','unresolved_action_ids':[a['action_id'] for a in unresolved]}
