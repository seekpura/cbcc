from __future__ import annotations

from copy import deepcopy
from contextvars import ContextVar
from typing import Any, Callable, Mapping
import re

DENSITY_FIELDS=('what','why','evidence','tradeoff','execution','measurement')
LINEAGE_FIELDS=('source_refs','source_type','recency','exact_fact','interpretation','confidence','assumption_boundary','downstream_use','conflict_status','proof_object')
MAJOR_OBJECTS=('search','title','bullets','description','attributes','usage','package','faq','claim_mapping')
_FULL_DENY={'TASK_SCOPED','TASK_SCOPE','PARTIAL','NOT_FULL','NON_FULL','SCOPED','MINIMAL'}
_FULL_EXACT={'FULL','FULL_PROJECT','FULL_DELIVERY','FULL_PACKAGE','FULL_COMMERCE','FULL_STRATEGY','FULL_WORKSPACE','FULL_E2E','END_TO_END','COMPLETE_DELIVERY','COMPLETE_PROJECT','完整交付','全量交付','完整项目','全量项目'}
_LISTING_CONTEXT:ContextVar[dict[str,Any]|None]=ContextVar('cbcc_v0676_listing_context', default=None)


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

def _is_full_context(request:Mapping[str,Any]|None, payload:Mapping[str,Any]|None=None)->bool:
    merged={}
    if isinstance(payload,Mapping): merged.update(payload)
    if isinstance(request,Mapping):
        for k in ('human_projection','delivery_mode','scope_mode'):
            if k in request: merged[k]=request[k]
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
        if sid not in (None,''): out[str(sid)]=deepcopy(dict(row))
    return out


def _decision(raw:Any, *, name:str, sources:Mapping[str,Mapping[str,Any]])->dict[str,Any]:
    src=_d(raw); out=deepcopy(src)
    out['decision']=src.get('decision') or src.get('what')
    for key in DENSITY_FIELDS: out.setdefault(key,None if key!='evidence' else [])
    if not _p(out.get('evidence')):
        out['evidence']=deepcopy(src.get('source_refs') or src.get('source_ids') or [])
    refs=list(dict.fromkeys(str(x) for x in _l(src.get('source_refs') or src.get('source_ids') or src.get('evidence')) if _p(x)))
    out['source_refs']=refs
    first=_d(sources.get(refs[0])) if refs else {}
    out['source_type']=src.get('source_type') or first.get('source_type') or first.get('authority') or first.get('kind')
    out['recency']=src.get('recency') or first.get('as_of') or first.get('published_at') or first.get('date')
    out['exact_fact']=deepcopy(src.get('exact_fact')) if 'exact_fact' in src else None
    out['interpretation']=src.get('interpretation')
    out['confidence']=str(src.get('confidence') or ('MEDIUM' if refs else 'LOW')).upper()
    out['assumption_boundary']=src.get('assumption_boundary')
    out['downstream_use']=deepcopy(src.get('downstream_use') or ['listing_search'])
    out['conflict_status']=src.get('conflict_status') or 'NO_DECLARED_CONFLICT'
    out['proof_object']=src.get('proof_object') or f'listing_search_authority.decisions.{name}'
    density_missing=[k for k in DENSITY_FIELDS if not _p(out.get(k))]
    if not _p(out.get('decision')): density_missing.append('decision')
    lineage_required=('source_refs','source_type','recency','exact_fact','interpretation','confidence','downstream_use','conflict_status','proof_object')
    lineage_missing=[k for k in lineage_required if not _p(out.get(k))]
    out['density_gaps']=list(dict.fromkeys(density_missing))
    out['lineage_gaps']=list(dict.fromkeys(lineage_missing))
    out['density_status']='READY' if not density_missing and not lineage_missing else 'TO_VERIFY'
    return out


def _field_value(compiled:Mapping[str,Any], name:str)->Any:
    fields=_d(compiled.get('fields'))
    if name=='bullets': return fields.get('bullets') or fields.get('highlights')
    if name=='usage': return fields.get('usage') or compiled.get('usage_plan')
    if name=='package': return fields.get('package') or compiled.get('package_plan')
    if name=='faq': return fields.get('faq') or compiled.get('faq_plan')
    if name=='search': return compiled.get('keyword_priority') or _d(compiled.get('keywords')).get('clusters')
    if name=='claim_mapping': return compiled.get('traceability')
    return fields.get(name)


def _object_presence(compiled:Mapping[str,Any])->dict[str,dict[str,Any]]:
    out={}
    for name in MAJOR_OBJECTS:
        value=_field_value(compiled,name)
        out[name]={'status':'PRESENT' if _p(value) else 'MISSING_INPUT','value_present':_p(value),
                   'why':'The mature Listing compiler produced this object.' if _p(value) else 'This required Listing/Search object is absent; runtime does not invent publishable copy or decision content.'}
    return out


def _search_evidence(compiled:Mapping[str,Any])->dict[str,Any]:
    terms=[]
    for row in _l(compiled.get('keyword_priority')):
        if not isinstance(row,Mapping) or not _p(row.get('term')): continue
        terms.append({k:deepcopy(row.get(k)) for k in ('term','cluster','priority_score','role','decision_stage','source_id')})
    if not terms:
        clusters=_d(_d(compiled.get('keywords')).get('clusters'))
        for cluster, rows in clusters.items():
            for row in _l(rows):
                if isinstance(row,Mapping) and _p(row.get('term')):
                    terms.append({'term':row.get('term'),'cluster':cluster,'priority_score':row.get('priority_score'),'role':row.get('role'),'decision_stage':row.get('decision_stage'),'source_id':row.get('source_id')})
    unsourced=[x.get('term') for x in terms if not _p(x.get('source_id'))]
    status='READY' if terms and not unsourced else 'TO_VERIFY'
    return {'status':status,'terms':terms,'unsourced_terms':unsourced,
            'boundary':'Search terms preserve supplied research lineage. Missing source IDs remain TO_VERIFY; no search volume, rank or demand is invented.'}


def _publishability(compiled:Mapping[str,Any], request:Mapping[str,Any])->dict[str,Any]:
    workflow=_d(compiled.get('final_copy_workflow')); target=_d(request.get('target'))
    required=[str(x) for x in _l(target.get('visible_copy_locales') or ([target.get('primary_locale')] if target.get('primary_locale') else [])) if _p(x)]
    packages=[deepcopy(dict(x)) for x in _l(workflow.get('packages')) if isinstance(x,Mapping)]
    by_locale={str(x.get('locale')):x for x in packages if _p(x.get('locale'))}
    missing=[x for x in required if x not in by_locale]
    not_final=[]
    for locale in required:
        pkg=_d(by_locale.get(locale))
        rows=[x for x in _l(pkg.get('fields')) if isinstance(x,Mapping)]
        if pkg.get('status')!='APPROVED_FINAL' or not rows or any(x.get('release_status')!='APPROVED_FINAL' for x in rows): not_final.append(locale)
    status='READY' if required and not missing and not not_final else 'TO_VERIFY'
    return {'status':status,'primary_locale':target.get('primary_locale') or workflow.get('primary_locale'),'required_locales':required,
            'missing_locales':missing,'not_final_locales':not_final,'packages':packages,
            'rule':'Publishable means the exact target-locale current version is APPROVED_FINAL; draft existence or a legacy compile PASS is not publish readiness.'}


def _language_continuity(compiled:Mapping[str,Any], request:Mapping[str,Any], publishability:Mapping[str,Any])->dict[str,Any]:
    target=_d(request.get('target')); primary=str(target.get('primary_locale') or publishability.get('primary_locale') or '')
    delivery=str(target.get('delivery_locale') or _d(compiled.get('final_copy_workflow')).get('delivery_locale') or 'zh-CN')
    packages=[x for x in _l(publishability.get('packages')) if isinstance(x,Mapping)]
    locales=[str(x.get('locale') or '') for x in packages]
    primary_is_en=primary.casefold().startswith('en')
    english_ready=True if primary_is_en else any(x.casefold().startswith('en') for x in locales)
    companion_gaps=[]
    if delivery.casefold().startswith('zh'):
        for pkg in packages:
            locale=str(pkg.get('locale') or '')
            if locale.casefold().startswith('zh'): continue
            for row in _l(pkg.get('fields')):
                if not isinstance(row,Mapping): continue
                if row.get('delivery_companion_status') not in {'READY','NOT_REQUIRED'} or not _p(row.get('delivery_translation')):
                    companion_gaps.append({'locale':locale,'field':row.get('field')})
    companion_ready=not companion_gaps
    return {
        'primary_locale':primary,'delivery_locale':delivery,
        'english_semantic_baseline_status':'READY' if english_ready else 'TO_VERIFY',
        'delivery_companion_status':'READY' if companion_ready else 'TO_VERIFY',
        'delivery_companion_gaps':companion_gaps,
        'rule':'Non-English market Listing retains an English semantic baseline and the operator-facing delivery-language companion; neither may be silently synthesized.'
    }


def _pricing_offer_context(pricing_economics:Mapping[str,Any]|None, market_analysis:Mapping[str,Any]|None)->dict[str,Any]:
    strict=_d(pricing_economics); phase2=_d(strict.get('phase2_economics_offer_authority')) or strict
    pricing=_d(phase2.get('pricing_decision')); offer=_d(phase2.get('offer_decision'))
    p_ready=phase2.get('status')=='READY' and pricing.get('density_status')=='READY' and _p(pricing.get('decision'))
    o_ready=phase2.get('status')=='READY' and offer.get('density_status')=='READY' and _p(offer.get('decision'))
    return {
        'status':'READY' if p_ready and o_ready else 'TO_VERIFY',
        'selected_price':deepcopy(pricing.get('exact_fact') or pricing.get('decision')) if p_ready else None,
        'selected_offer':deepcopy(offer.get('exact_fact') or offer.get('decision')) if o_ready else None,
        'pricing_decision':pricing,'offer_decision':offer,
        'market_price_evidence':deepcopy(_d(market_analysis).get('price_bands') or _d(_d(phase2.get('market_evidence'))).get('price_bands') or []),
        'boundary':'Market price bands/valleys are evidence only. Listing consumes only the explicit Phase 2 Pricing/Offer decision; missing decisions remain TO_VERIFY.'
    }


def _claim_mapping(compiled:Mapping[str,Any])->dict[str,Any]:
    rows=[]; missing=[]
    for row in _l(compiled.get('traceability')):
        if not isinstance(row,Mapping) or not row.get('has_value'): continue
        item={'field':row.get('field'),'source_ids':deepcopy(row.get('source_ids') or []),'claim_ids':deepcopy(row.get('claim_ids') or [])}
        rows.append(item)
        if not item['source_ids'] and not item['claim_ids']: missing.append(item['field'])
    return {'status':'READY' if rows and not missing else 'TO_VERIFY','rows':rows,'fields_without_trace':missing,
            'rule':'Publishable factual/claim-heavy Listing fields retain explicit Product Truth / Claim evidence references; copy existence alone is not evidence.'}


def listing_search_issues(authority:Mapping[str,Any])->list[dict[str,Any]]:
    auth=_d(authority); issues=[]
    presence=_d(auth.get('object_presence')); decisions=_d(auth.get('decisions'))
    for name in MAJOR_OBJECTS:
        d=_d(decisions.get(name))
        if d.get('density_status')!='READY':
            issues.append({'code':'FULL_LISTING_MAJOR_DECISION_INCOMPLETE_V0676','object':name,'density_gaps':d.get('density_gaps') or list(DENSITY_FIELDS),'lineage_gaps':d.get('lineage_gaps') or []})
        if _d(presence.get(name)).get('status')!='PRESENT':
            issues.append({'code':'FULL_LISTING_MAJOR_OBJECT_MISSING_V0676','object':name})
    if _d(auth.get('search_evidence')).get('status')!='READY':
        issues.append({'code':'FULL_LISTING_SEARCH_EVIDENCE_UNSOURCED_V0676','terms':_d(auth.get('search_evidence')).get('unsourced_terms') or []})
    if _d(auth.get('claim_evidence_mapping')).get('status')!='READY':
        issues.append({'code':'FULL_LISTING_CLAIM_EVIDENCE_MAPPING_INCOMPLETE_V0676','fields':_d(auth.get('claim_evidence_mapping')).get('fields_without_trace') or []})
    if _d(auth.get('pricing_offer_context')).get('status')!='READY':
        issues.append({'code':'FULL_LISTING_PRICING_OFFER_CONTEXT_INCOMPLETE_V0676'})
    pub=_d(auth.get('publishability'))
    if pub.get('status')!='READY':
        issues.append({'code':'FULL_LISTING_PUBLISHABLE_COPY_INCOMPLETE_V0676','missing_locales':pub.get('missing_locales') or [],'not_final_locales':pub.get('not_final_locales') or []})
    lang=_d(auth.get('language_continuity'))
    if lang.get('english_semantic_baseline_status')!='READY': issues.append({'code':'FULL_LISTING_ENGLISH_BASELINE_MISSING_V0676'})
    if lang.get('delivery_companion_status')!='READY': issues.append({'code':'FULL_LISTING_DELIVERY_COMPANION_INCOMPLETE_V0676','gaps':lang.get('delivery_companion_gaps') or []})
    dedup=[]
    for item in issues:
        if item not in dedup: dedup.append(item)
    return dedup


def materialize_listing_search_authority(compiled_listing:Mapping[str,Any], request:Mapping[str,Any]|None=None,
                                         market_analysis:Mapping[str,Any]|None=None,
                                         pricing_economics:Mapping[str,Any]|None=None)->dict[str,Any]:
    if not _is_full_context(request,compiled_listing): return deepcopy(dict(compiled_listing))
    compiled=_d(compiled_listing); req=_d(request); listing_input=_d(req.get('listing_input')); sources=_source_index(req)
    raw_decisions=_d(listing_input.get('phase2_decisions') or req.get('listing_search_decisions'))
    decisions={name:_decision(raw_decisions.get(name),name=name,sources=sources) for name in MAJOR_OBJECTS}
    presence=_object_presence(compiled)
    search=_search_evidence(compiled)
    claims=_claim_mapping(compiled)
    publishability=_publishability(compiled,req)
    language=_language_continuity(compiled,req,publishability)
    pricing=_pricing_offer_context(pricing_economics,market_analysis)
    authority={
        'schema':'cbcc-listing-search-authority-v0.6.76','status':'TO_VERIFY',
        'object_presence':presence,'decisions':decisions,'search_evidence':search,
        'claim_evidence_mapping':claims,'pricing_offer_context':pricing,
        'publishability':publishability,'language_continuity':language,
        'platform_profile':deepcopy(compiled.get('platform_native_listing_profile') or {}),
        'legacy_listing_status':compiled.get('status'),'legacy_compile_pass':compiled.get('pass'),
        'conversion_architecture':deepcopy(compiled.get('conversion_architecture') or {}),
        'field_contracts':deepcopy(compiled.get('field_contracts') or []),
        'principle':'Listing/Search is a first-class publishable commerce object. Existing copy/compile status cannot substitute for decision density, evidence lineage, explicit Pricing/Offer consumption, locale continuity or final-copy readiness.'
    }
    issues=listing_search_issues(authority)
    authority['issues']=issues; authority['status']='READY' if not issues else 'TO_VERIFY'
    return authority


def wrap_compile_pricing_economics_for_listing_context(fn:Callable[...,dict[str,Any]]):
    def compiled(request:dict[str,Any], market_analysis:dict[str,Any]|None=None, legacy_economics:dict[str,Any]|None=None):
        out=fn(request,market_analysis,legacy_economics)
        if _is_full_context(request,out):
            _LISTING_CONTEXT.set({'request':deepcopy(request),'market_analysis':deepcopy(market_analysis or {}),'pricing_economics':deepcopy(out)})
        else:
            _LISTING_CONTEXT.set(None)
        return out
    setattr(compiled,'_cbcc_v0676_listing_search_context_bridge',True)
    return compiled


def wrap_compile_listing(fn:Callable[...,dict[str,Any]]):
    def compiled(*args:Any, **kwargs:Any):
        explicit=_d(kwargs.pop('phase2_context',None))
        implicit=_d(_LISTING_CONTEXT.get())
        phase2_context=explicit or implicit
        try:
            legacy=fn(*args,**kwargs)
            request=_d(phase2_context.get('request'))
            if not phase2_context or not _is_full_context(request,legacy): return legacy
            authority=materialize_listing_search_authority(legacy,request,phase2_context.get('market_analysis'),phase2_context.get('pricing_economics'))
            out=deepcopy(dict(legacy)); out['phase2_listing_search_authority']=authority; out['phase2_business_status']=authority.get('status')
            return out
        finally:
            if implicit and not explicit: _LISTING_CONTEXT.set(None)
    setattr(compiled,'_cbcc_v0676_listing_search_authority',True)
    return compiled


def wrap_compile_seven_tool_continuity(fn:Callable[...,dict[str,Any]]):
    def compiled(*args:Any, **kwargs:Any):
        out=fn(*args,**kwargs)
        domain=_d(kwargs.get('domain'))
        if not domain and args and isinstance(args[0],Mapping): domain=_d(args[0])
        listing=_d(domain.get('listing')); mature=_d(listing.get('compiled'))
        authority=_d(mature.get('phase2_listing_search_authority'))
        status=mature.get('phase2_business_status') or authority.get('status') or 'TO_VERIFY'
        for row in _l(out.get('capabilities')):
            if isinstance(row,dict) and row.get('id')=='03_LISTING_CREATIVE':
                row['business_readiness_status']=status
                evidence=row.setdefault('evidence',{})
                evidence['listing_business_readiness_status']=status
                evidence['listing_authority_status']=authority.get('status') or 'NOT_MATERIALIZED'
                evidence['listing_issue_count']=len(authority.get('issues') or []) if authority else None
        out['listing_search_integrity']={'business_readiness_status':status,'authority_status':authority.get('status') or 'NOT_MATERIALIZED','issues':deepcopy(authority.get('issues') or []),'rule':'Legacy LISTING_CONTRACT_COMPILED is compilation state; Phase 2 business readiness independently requires complete publishable Listing/Search authority.'}
        return out
    setattr(compiled,'_cbcc_v0676_listing_search_authority',True)
    return compiled
