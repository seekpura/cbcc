from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping
import re

DENSITY_FIELDS=('what','why','evidence','tradeoff','execution','measurement')
BUSINESS_FIELDS=(
    'issue_class','issue_signal','root_cause_hypothesis','root_cause_layer','root_cause_status',
    'responsible_layer','repair_action','repair_scope','frozen_layers','why_not_broader_rework',
    'verification_metric','success_rule','failure_rule','learning_handoff',
)
_FULL_DENY={'TASK_SCOPED','TASK_SCOPE','PARTIAL','NOT_FULL','NON_FULL','SCOPED','MINIMAL'}
_FULL_EXACT={'FULL','FULL_PROJECT','FULL_DELIVERY','FULL_PACKAGE','FULL_COMMERCE','FULL_STRATEGY','FULL_WORKSPACE','FULL_E2E','END_TO_END','COMPLETE_DELIVERY','COMPLETE_PROJECT','完整交付','全量交付','完整项目','全量项目'}

REVIEW_EIGHT_CLASSES={
    'PRODUCT_QUALITY','EXPECTATION_GAP','MISUNDERSTANDING','USAGE_EXPERIENCE',
    'FIT_SIZE_COMPATIBILITY','PACKAGE_CONTENTS','LOGISTICS_SERVICE','POSITIVE_VALUE',
}
COMMUNICATION_CLASSES={'EXPECTATION_GAP','MISUNDERSTANDING','USAGE_EXPERIENCE','FIT_SIZE_COMPATIBILITY','PACKAGE_CONTENTS'}
ALLOWED_RESPONSIBLE={
    'PRODUCT_QUALITY':{'PRODUCT_QUALITY','QUALITY','PRODUCT_STRATEGY'},
    'EXPECTATION_GAP':{'LISTING','IMAGE','VISUAL','CREATOR','FAQ','CX'},
    'MISUNDERSTANDING':{'LISTING','IMAGE','VISUAL','FAQ','CX'},
    'USAGE_EXPERIENCE':{'LISTING','VIDEO','CX','USAGE_CONTENT','FAQ'},
    'FIT_SIZE_COMPATIBILITY':{'LISTING','IMAGE','SCALE_ASSET','ATTRIBUTES','CX'},
    'PACKAGE_CONTENTS':{'LISTING','IMAGE','PACKAGE_ASSET','CX'},
    'LOGISTICS_SERVICE':{'FULFILLMENT','CX'},
    'POSITIVE_VALUE':{'LISTING','IMAGE','VISUAL','PROOF','CREATOR','PRODUCT_STRATEGY'},
}
BROAD_REPAIR_TOKENS={'FULL_PROJECT','FULL_PROJECT_REDESIGN','FULL_REDESIGN','GLOBAL_REDESIGN','ALL_ASSETS','ALL_CONTENT','EVERYTHING'}


def _p(v:Any)->bool: return v not in (None,'',[],{})
def _d(v:Any)->dict[str,Any]: return deepcopy(dict(v)) if isinstance(v,Mapping) else {}
def _l(v:Any)->list[Any]:
    if v in (None,'',{}): return []
    return list(v) if isinstance(v,(list,tuple,set,frozenset)) else [v]

def _mode_token(v:Any)->str:
    raw=str(v or '').strip()
    if not raw:return ''
    if re.search(r'[\u3400-\u9fff]',raw):return re.sub(r'\s+','',raw)
    return re.sub(r'[^A-Z0-9]+','_',raw.upper()).strip('_')

def _is_full(request:Mapping[str,Any]|None,payload:Mapping[str,Any]|None=None)->bool:
    merged=_d(payload)
    if isinstance(request,Mapping):
        for key in ('human_projection','delivery_mode','scope_mode'):
            if key in request: merged[key]=request[key]
    hp=_d(merged.get('human_projection'))
    if hp.get('fixed_human_section_quota') is True:return True
    token=_mode_token(hp.get('mode') or merged.get('delivery_mode') or merged.get('scope_mode') or '')
    if token in _FULL_DENY or token.startswith('NOT_FULL') or token.startswith('NON_FULL'):return False
    if token in _FULL_EXACT:return True
    if token.startswith('FULL_') and any(x in token for x in ('PROJECT','DELIVERY','PACKAGE','COMMERCE','WORKSPACE','STRATEGY','E2E')):return True
    return token in {'完整','全量'}

def _source_index(request:Mapping[str,Any])->dict[str,dict[str,Any]]:
    out={}
    for row in _l(request.get('sources')):
        if not isinstance(row,Mapping):continue
        sid=row.get('source_id') or row.get('id')
        if _p(sid):out[str(sid)]=deepcopy(dict(row))
    return out

def _refs(raw:Mapping[str,Any])->list[str]:
    vals=raw.get('source_refs') or raw.get('source_ids') or raw.get('evidence_refs') or []
    if not _p(vals):
        ev=raw.get('evidence')
        if isinstance(ev,(list,tuple,set,frozenset)):
            vals=[x for x in ev if isinstance(x,str) and str(x).strip()]
    return list(dict.fromkeys(str(x) for x in _l(vals) if _p(x)))

def _lineage(raw:Mapping[str,Any],sources:Mapping[str,Mapping[str,Any]],proof:str)->dict[str,Any]:
    refs=_refs(raw); unresolved=[x for x in refs if x not in sources]
    first=_d(sources.get(refs[0])) if refs and refs[0] in sources else {}
    explicit_assumption=_p(raw.get('assumption_boundary'))
    exact_fact=deepcopy(raw.get('exact_fact')) if 'exact_fact' in raw else None
    out={
        'source_refs':refs,
        'source_type':raw.get('source_type') or first.get('source_type') or first.get('authority') or first.get('kind'),
        'recency':raw.get('recency') or first.get('as_of') or first.get('published_at') or first.get('date'),
        'exact_fact':exact_fact,
        'interpretation':raw.get('interpretation'),
        'confidence':str(raw.get('confidence') or ('MEDIUM' if refs else 'LOW')).upper(),
        'assumption_boundary':raw.get('assumption_boundary') if explicit_assumption else ('REVIEW_ROOT_CAUSE_DECISION_NOT_SOURCE_BOUND' if not refs else None),
        'downstream_use':deepcopy(raw.get('downstream_use') or []),
        'conflict_status':raw.get('conflict_status') or 'NO_DECLARED_CONFLICT',
        'proof_object':raw.get('proof_object') or proof,
        'unresolved_source_refs':unresolved,
    }
    gaps=[]
    if unresolved:gaps.append('unresolved_source_refs')
    if not refs and not explicit_assumption:gaps.append('source_refs_or_explicit_assumption_boundary')
    for key in ('source_type','recency','interpretation','confidence','downstream_use','conflict_status','proof_object'):
        if not _p(out.get(key)):gaps.append(key)
    if not _p(exact_fact) and not explicit_assumption:gaps.append('exact_fact_or_explicit_assumption_boundary')
    out['lineage_gaps']=gaps
    out['lineage_status']='READY' if not gaps else 'TO_VERIFY'
    return out

def _density(raw:Mapping[str,Any])->tuple[str,list[str]]:
    gaps=[k for k in DENSITY_FIELDS if not _p(raw.get(k))]
    return ('READY' if not gaps else 'TO_VERIFY',gaps)

def _review_rows(request:Mapping[str,Any])->list[Any]:
    obj=request.get('review_analysis') or request.get('review_root_cause') or {}
    if isinstance(obj,Mapping):return _l(obj.get('rows') or obj.get('decisions') or obj.get('repair_rows'))
    return _l(obj)

def _route_status(src:Mapping[str,Any])->tuple[str,list[str]]:
    cls=str(src.get('issue_class') or '').upper()
    responsible=str(src.get('responsible_layer') or '').upper()
    root_layer=str(src.get('root_cause_layer') or '').upper()
    gaps=[]
    if cls not in REVIEW_EIGHT_CLASSES:gaps.append('issue_class_not_in_eight_class_taxonomy')
    allowed=ALLOWED_RESPONSIBLE.get(cls,set())
    if allowed and responsible not in allowed:gaps.append('responsible_layer_not_supported_by_issue_class')
    if cls in COMMUNICATION_CLASSES and (responsible in {'PRODUCT','PRODUCT_QUALITY','QUALITY','PRODUCT_STRATEGY'} or root_layer in {'PRODUCT_QUALITY','QUALITY'}):
        gaps.append('communication_issue_cannot_default_to_product_change_without_separate_defect_evidence')
    if cls=='PRODUCT_QUALITY' and responsible in {'LISTING','IMAGE','VISUAL','FAQ','CREATOR','CX'}:
        gaps.append('product_quality_issue_cannot_be_repaired_by_communication_only')
    return ('READY' if not gaps else 'TO_VERIFY',gaps)

def _smallest_repair_status(src:Mapping[str,Any])->tuple[str,list[str]]:
    gaps=[]
    scope=[str(x).upper() for x in _l(src.get('repair_scope')) if _p(x)]
    frozen=[str(x).upper() for x in _l(src.get('frozen_layers')) if _p(x)]
    if not scope:gaps.append('repair_scope')
    if not frozen:gaps.append('frozen_layers')
    if not _p(src.get('why_not_broader_rework')):gaps.append('why_not_broader_rework')
    if any(any(token in item for token in BROAD_REPAIR_TOKENS) for item in scope):gaps.append('broad_rework_not_smallest_repair')
    return ('READY' if not gaps else 'TO_VERIFY',gaps)

def _normalize_row(raw:Any,i:int,sources:Mapping[str,Mapping[str,Any]])->dict[str,Any]:
    src=_d(raw); out=deepcopy(src)
    out.setdefault('review_decision_id',f'REV-ROOT-{i+1:02d}')
    gaps=[k for k in BUSINESS_FIELDS if not _p(src.get(k))]
    out['business_contract_gaps']=gaps
    out['business_contract_status']='READY' if not gaps else 'TO_VERIFY'
    den,dg=_density(src); out['density_status']=den; out['density_gaps']=dg
    for k,v in _lineage(src,sources,f'review_analysis_authority.repair_rows[{i}]').items():out[k]=deepcopy(v)
    rs,rg=_route_status(src); out['root_cause_route_status']=rs; out['root_cause_route_gaps']=rg
    ss,sg=_smallest_repair_status(src); out['smallest_repair_status']=ss; out['smallest_repair_gaps']=sg
    out['row_status']='READY' if all(out.get(k)=='READY' for k in ('business_contract_status','density_status','lineage_status','root_cause_route_status','smallest_repair_status')) else 'TO_VERIFY'
    return out

def review_analysis_issues(authority:Mapping[str,Any])->list[dict[str,Any]]:
    auth=_d(authority); issues=[]
    rows=[x for x in _l(auth.get('repair_rows')) if isinstance(x,Mapping)]
    if not rows:issues.append({'code':'FULL_REVIEW_ROOT_CAUSE_REPAIR_DECISION_MISSING_V0676'})
    for i,row in enumerate(rows):
        if row.get('business_contract_status')!='READY':issues.append({'code':'FULL_REVIEW_ROOT_CAUSE_REPAIR_OBJECT_INCOMPLETE_V0676','row':i,'fields':row.get('business_contract_gaps') or list(BUSINESS_FIELDS)})
        if row.get('density_status')!='READY':issues.append({'code':'FULL_REVIEW_DECISION_DENSITY_INCOMPLETE_V0676','row':i,'fields':row.get('density_gaps') or list(DENSITY_FIELDS)})
        if row.get('lineage_status')!='READY':issues.append({'code':'FULL_REVIEW_LINEAGE_INCOMPLETE_V0676','row':i,'fields':row.get('lineage_gaps') or []})
        if row.get('root_cause_route_status')!='READY':
            code='FULL_REVIEW_PRODUCT_DEFECT_COPY_ONLY_REPAIR_V0676' if 'product_quality_issue_cannot_be_repaired_by_communication_only' in (row.get('root_cause_route_gaps') or []) else 'FULL_REVIEW_RESPONSIBLE_LAYER_CONTRADICTION_V0676'
            issues.append({'code':code,'row':i,'fields':row.get('root_cause_route_gaps') or []})
        if row.get('smallest_repair_status')!='READY':issues.append({'code':'FULL_REVIEW_SMALLEST_REPAIR_ROUTE_INCOMPLETE_V0676','row':i,'fields':row.get('smallest_repair_gaps') or []})
    dedup=[]
    for x in issues:
        if x not in dedup:dedup.append(x)
    return dedup

def materialize_review_analysis_authority(legacy_feedback:Mapping[str,Any],request:Mapping[str,Any]|None=None)->dict[str,Any]:
    base=deepcopy(dict(legacy_feedback or {})); req=_d(request)
    if not _is_full(req,base):return base
    sources=_source_index(req)
    rows=[_normalize_row(x,i,sources) for i,x in enumerate(_review_rows(req)) if isinstance(x,Mapping)]
    local_verify_ready=bool(rows) and all(_p(r.get('verification_metric')) and _p(r.get('success_rule')) and _p(r.get('failure_rule')) for r in rows)
    authority={
        'schema':'cbcc-review-analysis-authority-v0.6.76',
        'status':'TO_VERIFY',
        'asset_dependency':'NOT_REQUIRED_FOR_PHASE2_BUSINESS_AUTHORITY',
        'production_review_dependency':'NOT_REQUIRED_FOR_PHASE2_CUSTOMER_REVIEW_AUTHORITY',
        'repair_rows':rows,
        'feedback_analysis':base,
        'verification_boundary':{
            'local_repair_verification_contract':'READY' if local_verify_ready else 'TO_VERIFY',
            'global_measurement_status':'DEFERRED_PHASE2_SUBTASK_12',
            'measurement_closure_claimed':False,
            'rule':'Phase 2 #11 defines the local verify-after-repair rule and learning handoff only. Global A/B, P0/P1/P2 prioritization, experiment governance and next-input measurement closure remain #12.'
        },
        'principle':'Review Analysis is a first-class customer-feedback business authority: classify observed signal → author an evidence-bounded root-cause hypothesis → select the smallest responsible repair layer → freeze unrelated layers → define local verification → hand learning forward. Aggregation statistics never author the root cause by themselves.'
    }
    authority['issues']=review_analysis_issues(authority)
    authority['status']='READY' if not authority['issues'] else 'TO_VERIFY'
    return authority
