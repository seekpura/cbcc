from __future__ import annotations

from copy import deepcopy
from contextvars import ContextVar
from typing import Any, Mapping
import re

DENSITY_FIELDS=('what','why','evidence','tradeoff','execution','measurement')
REPAIR_BUSINESS_FIELDS=(
    'issue_class','issue_signal','root_cause_hypothesis','root_cause_layer','root_cause_status',
    'responsible_layer','repair_action','repair_scope','frozen_layers','why_not_broader_rework',
    'verification_metric','success_rule','failure_rule','learning_handoff',
)
POSITIVE_BUSINESS_FIELDS=(
    'issue_class','issue_signal','decision_type','preservation_action','frozen_layers',
    'verification_metric','success_rule','failure_rule','learning_handoff',
)
BUSINESS_FIELDS=REPAIR_BUSINESS_FIELDS
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
LEGACY_CLASS_MAP={
    'PRODUCT_DEFECT':'PRODUCT_QUALITY','TEXTURE':'PRODUCT_QUALITY','EXPECTATION_GAP':'EXPECTATION_GAP',
    'MISUNDERSTANDING':'MISUNDERSTANDING','PARAMETER_CONFUSION':'MISUNDERSTANDING',
    'USAGE_DIFFICULTY':'USAGE_EXPERIENCE','SIZE':'FIT_SIZE_COMPATIBILITY','COMPATIBILITY':'FIT_SIZE_COMPATIBILITY',
    'PACKAGE_CONFUSION':'PACKAGE_CONTENTS','LOGISTICS':'LOGISTICS_SERVICE','CUSTOMER_SERVICE':'LOGISTICS_SERVICE',
    'PRAISE':'POSITIVE_VALUE','POSITIVE':'POSITIVE_VALUE','POSITIVE_VALUE':'POSITIVE_VALUE',
}
SCOPE_PREFIXES={
    'PRODUCT_QUALITY':('PRODUCT','QUALITY'),
    'EXPECTATION_GAP':('LISTING','IMAGE','VISUAL','CREATOR','FAQ','CX'),
    'MISUNDERSTANDING':('LISTING','IMAGE','VISUAL','FAQ','CX'),
    'USAGE_EXPERIENCE':('LISTING','VIDEO','CX','USAGE','FAQ'),
    'FIT_SIZE_COMPATIBILITY':('LISTING','IMAGE','SCALE','ATTRIBUTE','CX'),
    'PACKAGE_CONTENTS':('LISTING','IMAGE','PACKAGE','CX'),
    'LOGISTICS_SERVICE':('FULFILLMENT','CX','LOGISTICS','SERVICE'),
}
HYPOTHESIS_STATUS_TOKENS={'WORKING_HYPOTHESIS','EVIDENCE_SUPPORTED_HYPOTHESIS'}
CAUSAL_STATUS_TOKENS={'CONFIRMED_CAUSE','CAUSAL_CONFIRMED','PROVEN_CAUSE','VERIFIED_CAUSE'}
CAUSAL_METHODS={'CONTROLLED_EXPERIMENT','HOLDOUT','DIAGNOSTIC_CONFIRMATION','RETURN_INSPECTION','QUALITY_INVESTIGATION'}


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

def _legacy_class(value:Any)->str:
    token=str(value or '').upper()
    return LEGACY_CLASS_MAP.get(token,token if token in REVIEW_EIGHT_CLASSES else '')

def _observed_classes(legacy:Mapping[str,Any])->set[str]:
    out=set()
    for row in _l(legacy.get('issues')):
        if isinstance(row,Mapping):
            c=_legacy_class(row.get('category') or row.get('issue_class'))
            if c:out.add(c)
    for key in _d(_d(legacy.get('summary')).get('categories')).keys():
        c=_legacy_class(key)
        if c:out.add(c)
    return out

def _evidence_alignment_status(src:Mapping[str,Any],legacy:Mapping[str,Any])->tuple[str,list[str]]:
    observed=_observed_classes(legacy)
    if not observed:
        return ('NOT_APPLICABLE_NO_AGGREGATED_FEEDBACK',[])
    cls=str(src.get('issue_class') or '').upper()
    if cls in observed:return ('READY',[])
    return ('TO_VERIFY',['issue_class_not_observed_in_aggregated_feedback'])

def _causal_boundary_status(src:Mapping[str,Any],sources:Mapping[str,Mapping[str,Any]])->tuple[str,list[str]]:
    if str(src.get('issue_class') or '').upper()=='POSITIVE_VALUE':
        return ('NOT_APPLICABLE_POSITIVE_VALUE',[])
    status=str(src.get('root_cause_status') or '').upper()
    if status in HYPOTHESIS_STATUS_TOKENS:
        return ('READY',[])
    if status not in CAUSAL_STATUS_TOKENS:
        return ('TO_VERIFY',['root_cause_status_not_supported'])
    refs=[str(x) for x in _l(src.get('causal_evidence_refs')) if _p(x)]
    unresolved=[x for x in refs if x not in sources]
    method=str(src.get('causal_method') or '').upper()
    gaps=[]
    if not refs:gaps.append('causal_evidence_refs')
    if unresolved:gaps.append('unresolved_causal_evidence_refs')
    if method not in CAUSAL_METHODS:gaps.append('causal_method')
    return ('READY' if not gaps else 'TO_VERIFY',gaps)

def _route_status(src:Mapping[str,Any])->tuple[str,list[str]]:
    cls=str(src.get('issue_class') or '').upper()
    if cls=='POSITIVE_VALUE':
        return ('NOT_APPLICABLE_POSITIVE_VALUE',[])
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
    scope=[str(x).upper() for x in _l(src.get('repair_scope')) if _p(x)]
    prefixes=SCOPE_PREFIXES.get(cls,())
    if scope and prefixes and any(not any(item.startswith(prefix) or prefix in item for prefix in prefixes) for item in scope):
        gaps.append('repair_scope_not_supported_by_issue_class')
    return ('READY' if not gaps else 'TO_VERIFY',gaps)

def _smallest_repair_status(src:Mapping[str,Any])->tuple[str,list[str]]:
    if str(src.get('issue_class') or '').upper()=='POSITIVE_VALUE':
        return ('NOT_APPLICABLE_POSITIVE_VALUE',[])
    gaps=[]
    scope=[str(x).upper() for x in _l(src.get('repair_scope')) if _p(x)]
    frozen=[str(x).upper() for x in _l(src.get('frozen_layers')) if _p(x)]
    responsible=str(src.get('responsible_layer') or '').upper()
    if not scope:gaps.append('repair_scope')
    if not frozen:gaps.append('frozen_layers')
    if responsible and any(item==responsible or item.startswith(responsible+'.') or item.startswith(responsible+'_') for item in frozen):
        gaps.append('responsible_layer_cannot_be_frozen')
    if not _p(src.get('why_not_broader_rework')):gaps.append('why_not_broader_rework')
    if any(any(token in item for token in BROAD_REPAIR_TOKENS) for item in scope):gaps.append('broad_rework_not_smallest_repair')
    return ('READY' if not gaps else 'TO_VERIFY',gaps)

def _normalize_row(raw:Any,i:int,sources:Mapping[str,Mapping[str,Any]],legacy:Mapping[str,Any])->dict[str,Any]:
    src=_d(raw); out=deepcopy(src)
    out.setdefault('review_decision_id',f'REV-ROOT-{i+1:02d}')
    cls=str(src.get('issue_class') or '').upper()
    out.setdefault('decision_type','PRESERVE_LEARN' if cls=='POSITIVE_VALUE' else 'REPAIR')
    required=POSITIVE_BUSINESS_FIELDS if cls=='POSITIVE_VALUE' else REPAIR_BUSINESS_FIELDS
    gaps=[k for k in required if not _p(out.get(k))]
    if cls=='POSITIVE_VALUE' and str(out.get('decision_type') or '').upper()!='PRESERVE_LEARN':gaps.append('decision_type=PRESERVE_LEARN')
    out['business_contract_gaps']=gaps
    out['business_contract_status']='READY' if not gaps else 'TO_VERIFY'
    den,dg=_density(src); out['density_status']=den; out['density_gaps']=dg
    for k,v in _lineage(src,sources,f'review_analysis_authority.repair_rows[{i}]').items():out[k]=deepcopy(v)
    ea,eg=_evidence_alignment_status(src,legacy); out['evidence_alignment_status']=ea; out['evidence_alignment_gaps']=eg
    cb,cg=_causal_boundary_status(src,sources); out['causal_boundary_status']=cb; out['causal_boundary_gaps']=cg
    rs,rg=_route_status(out); out['root_cause_route_status']=rs; out['root_cause_route_gaps']=rg
    ss,sg=_smallest_repair_status(out); out['smallest_repair_status']=ss; out['smallest_repair_gaps']=sg
    ok={'READY','NOT_APPLICABLE_POSITIVE_VALUE','NOT_APPLICABLE_NO_AGGREGATED_FEEDBACK'}
    out['row_status']='READY' if all(out.get(k) in ok for k in ('business_contract_status','density_status','lineage_status','evidence_alignment_status','causal_boundary_status','root_cause_route_status','smallest_repair_status')) else 'TO_VERIFY'
    return out

def review_analysis_issues(authority:Mapping[str,Any])->list[dict[str,Any]]:
    auth=_d(authority); issues=[]
    rows=[x for x in _l(auth.get('repair_rows')) if isinstance(x,Mapping)]
    if not rows:issues.append({'code':'FULL_REVIEW_ROOT_CAUSE_REPAIR_DECISION_MISSING_V0676'})
    for i,row in enumerate(rows):
        if row.get('business_contract_status')!='READY':issues.append({'code':'FULL_REVIEW_ROOT_CAUSE_REPAIR_OBJECT_INCOMPLETE_V0676','row':i,'fields':row.get('business_contract_gaps') or []})
        if row.get('density_status')!='READY':issues.append({'code':'FULL_REVIEW_DECISION_DENSITY_INCOMPLETE_V0676','row':i,'fields':row.get('density_gaps') or list(DENSITY_FIELDS)})
        if row.get('lineage_status')!='READY':issues.append({'code':'FULL_REVIEW_LINEAGE_INCOMPLETE_V0676','row':i,'fields':row.get('lineage_gaps') or []})
        if row.get('evidence_alignment_status') not in {'READY','NOT_APPLICABLE_NO_AGGREGATED_FEEDBACK'}:
            issues.append({'code':'FULL_REVIEW_EVIDENCE_CLASS_ALIGNMENT_INCOMPLETE_V0676','row':i,'fields':row.get('evidence_alignment_gaps') or []})
        if row.get('causal_boundary_status') not in {'READY','NOT_APPLICABLE_POSITIVE_VALUE'}:
            issues.append({'code':'FULL_REVIEW_CAUSAL_ROOT_CAUSE_OVERCLAIM_V0676','row':i,'fields':row.get('causal_boundary_gaps') or []})
        if row.get('root_cause_route_status') not in {'READY','NOT_APPLICABLE_POSITIVE_VALUE'}:
            code='FULL_REVIEW_PRODUCT_DEFECT_COPY_ONLY_REPAIR_V0676' if 'product_quality_issue_cannot_be_repaired_by_communication_only' in (row.get('root_cause_route_gaps') or []) else 'FULL_REVIEW_RESPONSIBLE_LAYER_CONTRADICTION_V0676'
            issues.append({'code':code,'row':i,'fields':row.get('root_cause_route_gaps') or []})
        if row.get('smallest_repair_status') not in {'READY','NOT_APPLICABLE_POSITIVE_VALUE'}:
            issues.append({'code':'FULL_REVIEW_SMALLEST_REPAIR_ROUTE_INCOMPLETE_V0676','row':i,'fields':row.get('smallest_repair_gaps') or []})
    dedup=[]
    for x in issues:
        if x not in dedup:dedup.append(x)
    return dedup

def materialize_review_analysis_authority(legacy_feedback:Mapping[str,Any],request:Mapping[str,Any]|None=None)->dict[str,Any]:
    base=deepcopy(dict(legacy_feedback or {})); req=_d(request)
    if not _is_full(req,base):return base
    sources=_source_index(req)
    rows=[_normalize_row(x,i,sources,base) for i,x in enumerate(_review_rows(req)) if isinstance(x,Mapping)]
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


def compile_review_analysis_domain(legacy_feedback:Mapping[str,Any],request:Mapping[str,Any]|None=None)->dict[str,Any]:
    base=deepcopy(dict(legacy_feedback or {}))
    authority=materialize_review_analysis_authority(base,request)
    if not _is_full(request,base):return base
    out=deepcopy(base)
    out['phase2_review_analysis_authority']=authority
    out['phase2_business_status']=authority.get('status')
    return out


def wrap_compile_seven_tool_continuity(fn):
    def compiled(*args:Any,**kwargs:Any):
        out=fn(*args,**kwargs)
        domain=_d(kwargs.get('domain'))
        if not domain and args and isinstance(args[0],Mapping):domain=_d(args[0])
        feedback=_d(domain.get('feedback'))
        authority=_d(feedback.get('phase2_review_analysis_authority'))
        status=feedback.get('phase2_business_status') or authority.get('status') or 'TO_VERIFY'
        for row in _l(out.get('capabilities')):
            if isinstance(row,dict) and row.get('id')=='07_REVIEW_ANALYSIS':
                row['business_readiness_status']=status
                ev=row.setdefault('evidence',{})
                ev['review_business_readiness_status']=status
                ev['review_authority_status']=authority.get('status') or 'NOT_MATERIALIZED'
                ev['review_issue_count']=len(authority.get('issues') or []) if authority else None
        out['review_analysis_integrity']={
            'business_readiness_status':status,
            'authority_status':authority.get('status') or 'NOT_MATERIALIZED',
            'issues':deepcopy(authority.get('issues') or []),
            'rule':'Legacy feedback aggregation/classification is evidence state. Phase 2 Review business readiness independently requires an authored root-cause hypothesis, responsible layer, smallest repair, frozen layers, local verification and learning handoff.'
        }
        return out
    setattr(compiled,'_cbcc_v0676_review_analysis_authority',True)
    return compiled


_REVIEW_CONTEXT:ContextVar[dict[str,Any]|None]=ContextVar('cbcc_v0676_review_context',default=None)
_REVIEW_STUB_STATE:ContextVar[dict[str,Any]|None]=ContextVar('cbcc_v0676_review_stub_state',default=None)

def _cleanup_internal_review_stub():
    state=_REVIEW_STUB_STATE.get()
    if isinstance(state,Mapping):
        req=state.get('request')
        if isinstance(req,dict):
            if state.get('had_key'):
                req['feedback_rows']=deepcopy(state.get('original'))
            else:
                req.pop('feedback_rows',None)
    _REVIEW_STUB_STATE.set(None)

def _inject_internal_no_feedback_stub(request:dict[str,Any]):
    had_key='feedback_rows' in request
    original=deepcopy(request.get('feedback_rows'))
    request['feedback_rows']=[{'_phase2_no_feedback_data':True}]
    _REVIEW_STUB_STATE.set({'request':request,'had_key':had_key,'original':original})

def _explicit_review_scope(request:Mapping[str,Any])->bool:
    return bool(request.get('review_analysis') or request.get('review_root_cause'))

def _has_feedback_input(request:Mapping[str,Any])->bool:
    rows=request.get('feedback_rows')
    if not isinstance(rows,(list,tuple)) or not rows:return False
    return not (len(rows)==1 and isinstance(rows[0],Mapping) and rows[0].get('_phase2_no_feedback_data') is True)

def _review_analyzer_scope(request:Mapping[str,Any])->bool:
    return _has_feedback_input(request) or _explicit_review_scope(request)

def wrap_compile_request_checkpoint_for_review_context(fn):
    def compiled(request:dict[str,Any],*args:Any,**kwargs:Any):
        _cleanup_internal_review_stub()
        _REVIEW_CONTEXT.set(None)
        out=fn(request,*args,**kwargs)
        if _is_full(request,out) and _review_analyzer_scope(request):
            if _explicit_review_scope(request) and not _has_feedback_input(request):
                _inject_internal_no_feedback_stub(request)
            _REVIEW_CONTEXT.set({'request':deepcopy(request),'checkpoint':deepcopy(out)})
        return out
    setattr(compiled,'_cbcc_v0676_review_analysis_context_bridge',True)
    return compiled

def wrap_analyze_feedback(fn):
    def compiled(*args:Any,**kwargs:Any):
        ctx=_d(_REVIEW_CONTEXT.get())
        req=_d(ctx.get('request'))
        rows=req.get('feedback_rows')
        no_feedback=bool(isinstance(rows,list) and len(rows)==1 and isinstance(rows[0],Mapping) and rows[0].get('_phase2_no_feedback_data') is True)
        try:
            legacy=(
                {
                    'status':'NO_CUSTOMER_REVIEW_DATA_SUPPLIED',
                    'summary':{'total':0,'categories':{},'shares':{}},
                    'issues':[],
                    'revision_actions':[],
                    'source_matrix':{},
                    'severity_matrix':{},
                    'unclassified_count':0,
                    'note':'No customer review/CS/returns data was supplied. No counts, rates, root causes or issue frequency are fabricated.'
                }
                if no_feedback else fn(*args,**kwargs)
            )
        except Exception:
            if ctx:
                _REVIEW_CONTEXT.set(None)
                _cleanup_internal_review_stub()
            raise
        if not ctx:return legacy
        try:
            return compile_review_analysis_domain(legacy,ctx.get('request'))
        finally:
            _REVIEW_CONTEXT.set(None)
            _cleanup_internal_review_stub()
    setattr(compiled,'_cbcc_v0676_review_analysis_authority',True)
    return compiled
