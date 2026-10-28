from __future__ import annotations
from typing import Any

A_MARKERS=('TEST','LAB','CERT','CERTIFICATION','OFFICIAL','MEASUREMENT','INSTRUMENT','AUDIT REPORT','检测','认证','实验室','测量')
B_MARKERS=('FORMULA','SPEC','SUPPLY','INGREDIENT','MECHANISM','COA','MSDS','SDS','配方','规格','供应链','成分','机理')
BLOCKED={'BLOCKED','PROHIBITED','REJECTED','INVALID'}


def _blob(obj:dict[str,Any])->str:
    keys=['source_type','evidence_type','type','title','name','kind','description','authority','issuer']
    return ' '.join(str(obj.get(k) or '') for k in keys).upper()


def compile_claim_authority(claims:list[dict[str,Any]]|None, sources:list[dict[str,Any]]|None)->dict[str,Any]:
    sources=sources or []; index={str(s.get('source_id')):s for s in sources if s.get('source_id')}
    rows=[]; issues=[]
    for raw in claims or []:
        c=dict(raw); cid=str(c.get('claim_id') or c.get('id') or '')
        refs=c.get('evidence_source_ids') or c.get('source_ids') or []
        if not isinstance(refs,list): refs=[refs]
        linked=[index.get(str(x)) for x in refs if index.get(str(x))]
        source_blob=' '.join(_blob(x) for x in linked)
        claim_blob=_blob(c)
        combined=(source_blob+' '+claim_blob).upper()
        explicit=str(c.get('evidence_level') or '').upper()
        status=str(c.get('status') or '').upper()
        reproducible=bool(c.get('reproducible_measurement') or c.get('test_report') or c.get('official_certification'))
        if status in BLOCKED:
            grade='C'; pub='BLOCKED'
        elif (linked and any(m in source_blob for m in A_MARKERS)) or reproducible:
            grade='A'; pub='HARD_CLAIM_ALLOWED_WITH_SCOPE'
        elif linked or any(m in combined for m in B_MARKERS):
            grade='B'; pub='BOUNDED_SUPPORTED_CLAIM'
        else:
            grade='C'; pub='SOFT_ONLY_NO_HARD_CLAIM'
        # An explicit A/B label is not itself evidence. Record drift instead of trusting it.
        if explicit in {'A','B'} and explicit!=grade:
            issues.append({'claim_id':cid or None,'code':'DECLARED_EVIDENCE_GRADE_NOT_SUPPORTED','declared':explicit,'normalized':grade,'source_ids':refs})
        if status in {'APPROVED','VERIFIED','ACTIVE'} and grade=='C':
            issues.append({'claim_id':cid or None,'code':'APPROVAL_STATUS_WITHOUT_A_OR_B_EVIDENCE','status':status,'normalized_grade':grade})
        c['claim_id']=cid or c.get('claim_id')
        c['source_ids']=refs; c['evidence_source_ids']=refs
        c['evidence_grade']=grade; c['evidence_level']=grade; c['publication_status']=pub
        c['publication_rule']={'A':'Hard claim may be used only within the exact tested/certified/measured scope.','B':'Use bounded wording supported by specification/formula/mechanism; do not upgrade to tested outcome.','C':'Subjective/hypothesis/pending only; never a hard claim.'}[grade]
        c['authority_trace']={'linked_source_ids':[str(x.get('source_id')) for x in linked if x.get('source_id')],'linked_source_count':len(linked),'declared_status':status or None,'declared_evidence_level':explicit or None}
        rows.append(c)
    return {'status':'CLAIM_AUTHORITY_COMPILED','claims':rows,'issues':issues,'grade_definition':{'A':'检测报告/官方认证/可复现实测','B':'供应链规格/配方/成分机理支持','C':'主观体验/创意假设/待验证；不得硬宣称'}}
