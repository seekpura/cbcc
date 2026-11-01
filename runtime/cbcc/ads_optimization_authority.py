from __future__ import annotations

from copy import deepcopy
from contextvars import ContextVar
from typing import Any, Mapping
import re

DENSITY_FIELDS=('what','why','evidence','tradeoff','execution','measurement')
BUSINESS_FIELDS=(
    'objective','funnel_state','audience_state','consumer_tension','creative_hypothesis','creative_mechanism',
    'proof','offer','landing_handoff','spend_boundary','economics_boundary_ref','attribution','test_structure',
    'test_variable','hold_constant','success_rule','failure_rule','failure_diagnosis','repair_route','learning_handoff',
)
_FULL_DENY={'TASK_SCOPED','TASK_SCOPE','PARTIAL','NOT_FULL','NON_FULL','SCOPED','MINIMAL'}
_FULL_EXACT={'FULL','FULL_PROJECT','FULL_DELIVERY','FULL_PACKAGE','FULL_COMMERCE','FULL_STRATEGY','FULL_WORKSPACE','FULL_E2E','END_TO_END','COMPLETE_DELIVERY','COMPLETE_PROJECT','完整交付','全量交付','完整项目','全量项目'}


def _p(v:Any)->bool: return v not in (None,'',[],{})
def _d(v:Any)->dict[str,Any]: return deepcopy(dict(v)) if isinstance(v,Mapping) else {}
def _l(v:Any)->list[Any]:
    if v in (None,'',{}): return []
    return list(v) if isinstance(v,(list,tuple,set,frozenset)) else [v]

def _mode_token(v:Any)->str:
    raw=str(v or '').strip()
    if not raw: return ''
    if re.search(r'[\u3400-\u9fff]',raw): return re.sub(r'\s+','',raw)
    return re.sub(r'[^A-Z0-9]+','_',raw.upper()).strip('_')

def _is_full(request:Mapping[str,Any]|None, payload:Mapping[str,Any]|None=None)->bool:
    merged=_d(payload)
    if isinstance(request,Mapping):
        for key in ('human_projection','delivery_mode','scope_mode'):
            if key in request: merged[key]=request[key]
    hp=_d(merged.get('human_projection'))
    if hp.get('fixed_human_section_quota') is True: return True
    token=_mode_token(hp.get('mode') or merged.get('delivery_mode') or merged.get('scope_mode') or '')
    if token in _FULL_DENY or token.startswith('NOT_FULL') or token.startswith('NON_FULL'): return False
    if token in _FULL_EXACT: return True
    if token.startswith('FULL_') and any(x in token for x in ('PROJECT','DELIVERY','PACKAGE','COMMERCE','WORKSPACE','STRATEGY','E2E')): return True
    return token in {'完整','全量'}

def _source_index(request:Mapping[str,Any])->dict[str,dict[str,Any]]:
    out={}
    for row in _l(request.get('sources')):
        if not isinstance(row,Mapping): continue
        sid=row.get('source_id') or row.get('id')
        if _p(sid): out[str(sid)]=deepcopy(dict(row))
    return out

def _refs(raw:Mapping[str,Any])->list[str]:
    vals=raw.get('source_refs') or raw.get('source_ids') or raw.get('evidence_refs') or []
    if not _p(vals):
        ev=raw.get('evidence')
        if isinstance(ev,(list,tuple,set,frozenset)):
            vals=[x for x in ev if isinstance(x,str) and str(x).strip()]
    return list(dict.fromkeys(str(x) for x in _l(vals) if _p(x)))

def _lineage(raw:Mapping[str,Any], sources:Mapping[str,Mapping[str,Any]], proof:str)->dict[str,Any]:
    refs=_refs(raw)
    unresolved=[x for x in refs if x not in sources]
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
        'assumption_boundary':raw.get('assumption_boundary') if explicit_assumption else ('ADS_OPTIMIZATION_DECISION_NOT_SOURCE_BOUND' if not refs else None),
        'downstream_use':deepcopy(raw.get('downstream_use') or []),
        'conflict_status':raw.get('conflict_status') or 'NO_DECLARED_CONFLICT',
        'proof_object':raw.get('proof_object') or proof,
        'unresolved_source_refs':unresolved,
    }
    gaps=[]
    if unresolved: gaps.append('unresolved_source_refs')
    if not refs and not explicit_assumption: gaps.append('source_refs_or_explicit_assumption_boundary')
    for key in ('source_type','recency','interpretation','confidence','downstream_use','conflict_status','proof_object'):
        if not _p(out.get(key)): gaps.append(key)
    if not _p(exact_fact) and not explicit_assumption: gaps.append('exact_fact_or_explicit_assumption_boundary')
    out['lineage_gaps']=gaps
    out['lineage_status']='READY' if not gaps else 'TO_VERIFY'
    return out

def _density(raw:Mapping[str,Any])->tuple[str,list[str]]:
    gaps=[k for k in DENSITY_FIELDS if not _p(raw.get(k))]
    return ('READY' if not gaps else 'TO_VERIFY',gaps)

def _normalize_row(raw:Any, i:int, sources:Mapping[str,Mapping[str,Any]])->dict[str,Any]:
    src=_d(raw); out=deepcopy(src)
    out.setdefault('optimization_id',f'ADS-OPT-{i+1:02d}')
    gaps=[k for k in BUSINESS_FIELDS if not _p(src.get(k))]
    out['business_contract_gaps']=gaps
    out['business_contract_status']='READY' if not gaps else 'TO_VERIFY'
    density,gaps2=_density(src)
    out['density_status']=density; out['density_gaps']=gaps2
    for key,val in _lineage(src,sources,f'ads_optimization_authority.optimization_rows[{i}]').items():
        out[key]=deepcopy(val)
    out['row_status']='READY' if all(out.get(k)=='READY' for k in ('business_contract_status','density_status','lineage_status')) else 'TO_VERIFY'
    return out

def _phase2_economics(pricing_economics:Mapping[str,Any]|None)->dict[str,Any]:
    strict=_d(pricing_economics); phase2=_d(strict.get('phase2_economics_offer_authority')) or strict
    br=_d(phase2.get('break_even'))
    cpa=_d(br.get('cpa')); cpc=_d(br.get('cpc')); roas=_d(br.get('roas'))
    cpa_ready=cpa.get('status')=='AVAILABLE' and cpa.get('value') is not None
    roas_ready=roas.get('status')=='AVAILABLE' and roas.get('value') is not None
    business_ready=phase2.get('status')=='READY' and cpa_ready and roas_ready
    return {
        'status':'READY' if business_ready else 'TO_VERIFY',
        'phase2_economics_status':phase2.get('status') or 'NOT_SUPPLIED',
        'break_even_cpa':cpa.get('value') if cpa_ready else None,
        'break_even_cpa_status':cpa.get('status') or 'MISSING_INPUT',
        'break_even_cpc':cpc.get('value') if cpc.get('status')=='AVAILABLE' else None,
        'break_even_cpc_status':cpc.get('status') or 'MISSING_INPUT',
        'break_even_roas':roas.get('value') if roas_ready else None,
        'break_even_roas_status':roas.get('status') or 'MISSING_INPUT',
        'pricing_decision':deepcopy(phase2.get('pricing_decision') or {}),
        'offer_decision':deepcopy(phase2.get('offer_decision') or {}),
        'rule':'Ads spend/scale decisions consume only Phase 2 Economics/Offer boundaries. Missing CVR may keep CPC unavailable while CPA/ROAS remain usable; missing core economics never becomes zero or a scale signal.'
    }

def _incrementality_from_legacy(legacy:Mapping[str,Any])->dict[str,Any]:
    candidates=[]
    agg=_d(legacy.get('aggregate'))
    if _p(agg.get('incrementality')): candidates.append(_d(agg.get('incrementality')))
    if _p(legacy.get('incrementality')): candidates.append(_d(legacy.get('incrementality')))
    for row in _l(legacy.get('rows')):
        if isinstance(row,Mapping):
            inc=_d(_d(row.get('analysis')).get('incrementality'))
            if inc: candidates.append(inc)
    evidence=next((x for x in candidates if x.get('status')=='EVIDENCE_AVAILABLE'),None)
    return evidence or next(iter(candidates),{'status':'NOT_ESTABLISHED','signals':{}})

def _attribution_boundary(legacy:Mapping[str,Any], request:Mapping[str,Any])->dict[str,Any]:
    inc=_incrementality_from_legacy(legacy)
    authored=_d(_d(request.get('advertising_optimization')).get('incrementality_decision'))
    established=str(authored.get('status') or '').upper()=='ESTABLISHED' and _p(authored.get('evidence'))
    return {
        'platform_attribution_status':'AVAILABLE' if legacy else 'NOT_SUPPLIED',
        'incrementality_status':'ESTABLISHED' if established else str(inc.get('status') or 'NOT_ESTABLISHED'),
        'counterfactual_signals':deepcopy(inc.get('signals') or {}),
        'causal_sales_claim_allowed':bool(established),
        'rule':'Platform-attributed conversions are not automatically incremental conversions. Causal sales/lift claims require an explicit incrementality decision backed by defensible counterfactual evidence.'
    }
def _optimization_rows(request:Mapping[str,Any])->list[Any]:
    obj=request.get('advertising_optimization') or request.get('ads_optimization') or {}
    if isinstance(obj,Mapping): return _l(obj.get('rows') or obj.get('decisions') or obj.get('optimization_rows'))
    return _l(obj)

def _norm_text(v:Any)->str:
    return re.sub(r'\s+',' ',str(v or '')).strip().casefold()

def _bind_row_to_economics(row:dict[str,Any], econ:Mapping[str,Any])->dict[str,Any]:
    out=deepcopy(row)
    expected_offer=_d(econ.get('offer_decision')).get('decision')
    offer_ready=_p(expected_offer) and _norm_text(out.get('offer'))==_norm_text(expected_offer)
    out['offer_alignment_status']='READY' if offer_ready else 'TO_VERIFY'
    out['verified_offer_decision']=deepcopy(expected_offer) if _p(expected_offer) else None
    expected_ref='phase2_economics_offer_authority.break_even'
    out['economics_binding_status']='READY' if econ.get('status')=='READY' and str(out.get('economics_boundary_ref') or '')==expected_ref else 'TO_VERIFY'
    out['economics_boundary_expected_ref']=expected_ref
    out['row_status']='READY' if all(out.get(k)=='READY' for k in ('business_contract_status','density_status','lineage_status','offer_alignment_status','economics_binding_status')) else 'TO_VERIFY'
    return out

def ads_optimization_issues(authority:Mapping[str,Any])->list[dict[str,Any]]:
    auth=_d(authority); issues=[]
    rows=[x for x in _l(auth.get('optimization_rows')) if isinstance(x,Mapping)]
    if not rows: issues.append({'code':'FULL_ADS_OPTIMIZATION_DECISION_MISSING_V0676'})
    for i,row in enumerate(rows):
        if row.get('business_contract_status')!='READY':
            issues.append({'code':'FULL_ADS_OPTIMIZATION_BUSINESS_OBJECT_INCOMPLETE_V0676','row':i,'fields':row.get('business_contract_gaps') or list(BUSINESS_FIELDS)})
        if row.get('density_status')!='READY':
            issues.append({'code':'FULL_ADS_OPTIMIZATION_BUSINESS_DENSITY_INCOMPLETE_V0676','row':i,'fields':row.get('density_gaps') or list(DENSITY_FIELDS)})
        if row.get('lineage_status')!='READY':
            issues.append({'code':'FULL_ADS_OPTIMIZATION_LINEAGE_INCOMPLETE_V0676','row':i,'fields':row.get('lineage_gaps') or []})
        if row.get('offer_alignment_status')!='READY':
            issues.append({'code':'FULL_ADS_OFFER_ALIGNMENT_INCOMPLETE_V0676','row':i,'offer':row.get('offer'),'verified_offer_decision':row.get('verified_offer_decision')})
        if row.get('economics_binding_status')!='READY':
            issues.append({'code':'FULL_ADS_ECONOMICS_BINDING_INCOMPLETE_V0676','row':i,'economics_boundary_ref':row.get('economics_boundary_ref'),'expected_ref':row.get('economics_boundary_expected_ref')})
    if _d(auth.get('economics_context')).get('status')!='READY':
        issues.append({'code':'FULL_ADS_ECONOMICS_BOUNDARY_INCOMPLETE_V0676'})
    dedup=[]
    for x in issues:
        if x not in dedup: dedup.append(x)
    return dedup

def materialize_ads_optimization_authority(legacy_ads:Mapping[str,Any], request:Mapping[str,Any]|None=None, pricing_economics:Mapping[str,Any]|None=None)->dict[str,Any]:
    base=deepcopy(dict(legacy_ads)); req=_d(request)
    if not _is_full(req,base): return base
    sources=_source_index(req)
    rows=[_normalize_row(x,i,sources) for i,x in enumerate(_optimization_rows(req)) if isinstance(x,Mapping)]
    econ=_phase2_economics(pricing_economics)
    rows=[_bind_row_to_economics(row,econ) for row in rows]
    attr=_attribution_boundary(base,req)
    authority={
        'schema':'cbcc-ads-optimization-authority-v0.6.76',
        'status':'TO_VERIFY',
        'asset_dependency':'NOT_REQUIRED_FOR_PHASE2_BUSINESS_AUTHORITY',
        'paid_campaign_dependency':'NOT_REQUIRED_FOR_PHASE2_BUSINESS_AUTHORITY',
        'optimization_rows':rows,
        'economics_context':econ,
        'attribution_boundary':attr,
        'performance_analysis':base,
        'principle':'Advertising Optimization is a first-class business object: audience state → creative mechanism → proof/offer → landing → explicit economics boundary → attribution/test → failure diagnosis → smallest repair → learning handoff. Metrics and platform attribution inform decisions but never author them or prove incrementality by themselves.'
    }
    authority['issues']=ads_optimization_issues(authority)
    authority['status']='READY' if not authority['issues'] else 'TO_VERIFY'
    return authority


def compile_ads_optimization_domain(legacy_ads:Mapping[str,Any], request:Mapping[str,Any]|None=None, pricing_economics:Mapping[str,Any]|None=None)->dict[str,Any]:
    base=deepcopy(dict(legacy_ads or {}))
    authority=materialize_ads_optimization_authority(base,request,pricing_economics)
    if not _is_full(request,base): return base
    out=deepcopy(base)
    out['phase2_ads_optimization_authority']=authority
    out['phase2_business_status']=authority.get('status')
    return out


def wrap_compile_seven_tool_continuity(fn):
    def compiled(*args:Any, **kwargs:Any):
        out=fn(*args,**kwargs)
        domain=_d(kwargs.get('domain'))
        if not domain and args and isinstance(args[0],Mapping): domain=_d(args[0])
        ads=_d(domain.get('ads'))
        authority=_d(ads.get('phase2_ads_optimization_authority'))
        status=ads.get('phase2_business_status') or authority.get('status') or 'TO_VERIFY'
        for row in _l(out.get('capabilities')):
            if isinstance(row,dict) and row.get('id')=='06_ADVERTISING_OPTIMIZATION':
                row['business_readiness_status']=status
                ev=row.setdefault('evidence',{})
                ev['ads_business_readiness_status']=status
                ev['ads_authority_status']=authority.get('status') or 'NOT_MATERIALIZED'
                ev['ads_issue_count']=len(authority.get('issues') or []) if authority else None
        out['ads_optimization_integrity']={
            'business_readiness_status':status,
            'authority_status':authority.get('status') or 'NOT_MATERIALIZED',
            'issues':deepcopy(authority.get('issues') or []),
            'rule':'Legacy CALCULATED/PORTFOLIO_CALCULATED is performance-analysis state. Phase 2 Ads business readiness independently requires authored optimization decisions + verified economics + attribution/test/repair/learning contracts.'
        }
        return out
    setattr(compiled,'_cbcc_v0676_ads_optimization_authority',True)
    return compiled


_ADS_CONTEXT:ContextVar[dict[str,Any]|None]=ContextVar('cbcc_v0676_ads_context', default=None)
_ADS_PORTFOLIO_DEPTH:ContextVar[int]=ContextVar('cbcc_v0676_ads_portfolio_depth', default=0)

def _ads_analyzer_scope(request:Mapping[str,Any])->bool:
    return bool(request.get('ad_rows') or request.get('ad_analysis'))

def wrap_compile_pricing_economics_for_ads_context(fn):
    def compiled(request:dict[str,Any], market_analysis=None, legacy_economics=None):
        _ADS_CONTEXT.set(None)
        out=fn(request,market_analysis,legacy_economics)
        if _is_full(request,out) and _ads_analyzer_scope(request):
            _ADS_CONTEXT.set({'request':deepcopy(request),'pricing_economics':deepcopy(out)})
        return out
    setattr(compiled,'_cbcc_v0676_ads_optimization_context_bridge',True)
    return compiled

def wrap_analyze_ads(fn):
    def compiled(*args:Any, **kwargs:Any):
        in_portfolio=_ADS_PORTFOLIO_DEPTH.get()>0
        ctx=_d(_ADS_CONTEXT.get())
        try:
            legacy=fn(*args,**kwargs)
        except Exception:
            if ctx and not in_portfolio: _ADS_CONTEXT.set(None)
            raise
        if in_portfolio:
            return legacy
        if not ctx:
            return legacy
        try:
            return compile_ads_optimization_domain(legacy,ctx.get('request'),ctx.get('pricing_economics'))
        finally:
            _ADS_CONTEXT.set(None)
    setattr(compiled,'_cbcc_v0676_ads_optimization_authority',True)
    return compiled

def wrap_analyze_ad_portfolio(fn):
    def compiled(*args:Any, **kwargs:Any):
        token=_ADS_PORTFOLIO_DEPTH.set(_ADS_PORTFOLIO_DEPTH.get()+1)
        try:
            legacy=fn(*args,**kwargs)
        except Exception:
            _ADS_CONTEXT.set(None)
            raise
        finally:
            _ADS_PORTFOLIO_DEPTH.reset(token)
        ctx=_d(_ADS_CONTEXT.get())
        if not ctx:
            return legacy
        try:
            return compile_ads_optimization_domain(legacy,ctx.get('request'),ctx.get('pricing_economics'))
        finally:
            _ADS_CONTEXT.set(None)
    setattr(compiled,'_cbcc_v0676_ads_optimization_authority',True)
    return compiled
