from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping
import re

DENSITY_FIELDS=('what','why','evidence','tradeoff','execution','measurement')
REQUIRED_INPUTS=('price','landed_cost','platform_fee','payment_fee','fulfillment','affiliate_commission','tax','refund_allowance')
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

def _is_full_context(request:Mapping[str,Any]|None, payload:Mapping[str,Any]|None=None)->bool:
    merged={}
    if isinstance(payload,Mapping): merged.update(payload)
    if isinstance(request,Mapping):
        for k in ('human_projection','delivery_mode','scope_mode'):
            if k in request: merged[k]=request[k]
    try:
        from .v0674_regression_closure import is_full_strategy
        return bool(is_full_strategy(merged))
    except (ImportError,ValueError):
        hp=_d(merged.get('human_projection'))
        if hp.get('fixed_human_section_quota') is True: return True
        token=_mode_token(hp.get('mode') or merged.get('delivery_mode') or merged.get('scope_mode') or '')
        if token in _FULL_DENY or token.startswith('NOT_FULL') or token.startswith('NON_FULL'): return False
        if token in _FULL_EXACT: return True
        if token.startswith('FULL_') and any(x in token for x in ('PROJECT','DELIVERY','PACKAGE','COMMERCE','WORKSPACE','STRATEGY','E2E')): return True
        return token in {'完整','全量'}

def _input_value(offer:Mapping[str,Any], name:str)->Any:
    if name=='price': return offer.get('price')
    costs=_d(offer.get('costs'))
    if name in costs: return costs.get(name)
    aliases={
        'landed_cost':('landed_cost','cogs','product_cost','unit_cost'),
        'platform_fee':('platform_fee','marketplace_fee'),
        'payment_fee':('payment_fee',),
        'fulfillment':('fulfillment','logistics_fulfillment','fulfillment_cost','shipping_fulfillment'),
        'affiliate_commission':('affiliate_commission','creator_commission','affiliate_cost'),
        'tax':('tax','merchant_borne_tax','duties_tax'),
        'refund_allowance':('refund_allowance','returns_refund_cost','return_allowance'),
    }
    for key in aliases.get(name,(name,)):
        if key in offer: return offer.get(key)
    return None

def _input_registry(offer:Mapping[str,Any])->dict[str,dict[str,Any]]:
    out={}
    for name in REQUIRED_INPUTS:
        value=_input_value(offer,name)
        present=value is not None and value!=''
        out[name]={
            'status':'EXPLICIT' if present else 'MISSING_INPUT',
            'exact_fact':deepcopy(value) if present else None,
            'why':('Explicit project economics input; zero is valid when explicitly supplied.' if present else 'Required economics input is absent. Missing values are never treated as zero.'),
            'assumption_boundary':None if present else 'MISSING_ECONOMICS_INPUT_DO_NOT_DEFAULT_ZERO',
            'downstream_use':['unit_economics','contribution','pricing_offer','listing','ads'],
        }
    cvr=offer.get('click_to_order_cvr')
    out['click_to_order_cvr']={
        'status':'EXPLICIT' if cvr not in (None,'') else 'MISSING_INPUT',
        'exact_fact':deepcopy(cvr) if cvr not in (None,'') else None,
        'why':'Required only for CPC relationships; CPA/ROAS may remain available when their own inputs are complete.',
        'assumption_boundary':None if cvr not in (None,'') else 'CPC_UNAVAILABLE_WITHOUT_EXPLICIT_CVR',
        'downstream_use':['break_even_cpc','ads'],
    }
    target=offer.get('target_contribution',offer.get('minimum_contribution'))
    out['target_contribution']={
        'status':'EXPLICIT' if target not in (None,'') else 'BASELINE_ONLY',
        'exact_fact':deepcopy(target) if target not in (None,'') else None,
        'why':'An explicit target is preferred for operating decisions. If absent, legacy math may expose a labeled zero-contribution floor, but that floor is not an authored profit target.',
        'assumption_boundary':None if target not in (None,'') else 'ZERO_CONTRIBUTION_FLOOR_IS_CALCULATION_BASELINE_NOT_STRATEGY_DECISION',
        'downstream_use':['break_even_cpa','break_even_roas','offer_headroom'],
    }
    return out

def _decision(raw:Any, *, kind:str, proof:str, allowed_statuses:tuple[str,...]=())->dict[str,Any]:
    src=_d(raw); out=deepcopy(src)
    status=str(src.get('status') or '').upper()
    decision=src.get('decision') or src.get('recommended_price') or src.get('price')
    out['decision']=deepcopy(decision) if _p(decision) else None
    out.setdefault('what',None); out.setdefault('why',None)
    if not _p(out.get('evidence')):
        ev=src.get('source_refs') or src.get('source_ids') or src.get('evidence_refs')
        out['evidence']=deepcopy(ev) if _p(ev) else []
    out.setdefault('tradeoff',None); out.setdefault('execution',None); out.setdefault('measurement',None)
    missing=[k for k in DENSITY_FIELDS if not _p(out.get(k))]
    if not _p(out.get('decision')): missing.append('decision')
    if allowed_statuses and status and status not in allowed_statuses: missing.append('status')
    if kind=='OFFER' and not status: missing.append('status')
    out['density_status']='READY' if not missing else 'TO_VERIFY'
    out['density_gaps']=list(dict.fromkeys(missing))
    out['source_refs']=list(dict.fromkeys(str(x) for x in _l(out.get('source_refs') or out.get('source_ids') or out.get('evidence_refs')) if _p(x)))
    out['exact_fact']=deepcopy(out.get('decision')) if out['density_status']=='READY' else None
    out['confidence']=str(src.get('confidence') or ('MEDIUM' if out['density_status']=='READY' else 'LOW')).upper()
    out['assumption_boundary']=src.get('assumption_boundary') or (None if out['density_status']=='READY' else f'{kind}_DECISION_NOT_FULLY_AUTHORED')
    out['conflict_status']=src.get('conflict_status') or 'NO_DECLARED_CONFLICT'
    out['proof_object']=proof
    return out

def _scenario(strict:Mapping[str,Any])->dict[str,Any]:
    rows=[x for x in _l(strict.get('scenarios')) if isinstance(x,Mapping)]
    return _d(rows[0]) if rows else {}

def _break_even(strict:Mapping[str,Any], inputs:Mapping[str,Mapping[str,Any]])->dict[str,Any]:
    s=_scenario(strict)
    required_complete=all(_d(inputs.get(k)).get('status')=='EXPLICIT' for k in REQUIRED_INPUTS)
    calc_ready=str(s.get('status') or '').upper()=='CALCULATED_FROM_EXPLICIT_INPUTS'
    base_ready=required_complete and calc_ready
    cpa=s.get('break_even_cpa') if base_ready else None
    roas=s.get('break_even_roas') if base_ready else None
    cvr_explicit=_d(inputs.get('click_to_order_cvr')).get('status')=='EXPLICIT'
    cpc=s.get('break_even_cpc') if base_ready and cvr_explicit else None
    return {
        'cpa':{'status':'AVAILABLE' if cpa is not None else 'MISSING_INPUT','value':cpa,'required_inputs':['price','landed_cost','platform_fee','payment_fee','fulfillment','affiliate_commission','tax','refund_allowance']},
        'cpc':{'status':'AVAILABLE' if cpc is not None else 'MISSING_INPUT','value':cpc,'required_inputs':['break_even_cpa','click_to_order_cvr']},
        'roas':{'status':'AVAILABLE' if roas is not None else ('UNAVAILABLE_NON_POSITIVE_HEADROOM' if base_ready and s.get('break_even_roas') is None else 'MISSING_INPUT'),'value':roas,'required_inputs':['price','break_even_cpa>0']},
        'calculation_source':'pricing_economics_authority.scenarios[0]',
        'rule':'Break-even values are usable only when their required explicit inputs are complete. A legacy number computed while a required economics input is absent is not promoted into the Phase 2 authority.',
    }

def materialize_economics_offer_authority(strict:Mapping[str,Any], request:Mapping[str,Any]|None=None, legacy_economics:Mapping[str,Any]|None=None)->dict[str,Any]:
    if not _is_full_context(request,strict): return deepcopy(dict(strict))
    base=deepcopy(dict(strict)); req=_d(request); offer=_d(req.get('offer_economics'))
    inputs=_input_registry(offer)
    missing=[k for k in REQUIRED_INPUTS if _d(inputs.get(k)).get('status')!='EXPLICIT']
    pricing_source=offer.get('pricing_decision') if isinstance(offer.get('pricing_decision'),Mapping) else base.get('pricing_decision')
    pricing=_decision(pricing_source,kind='PRICING',proof='pricing_economics_authority.pricing_decision')
    offer_source=None
    for key in ('offer_decision','offer_strategy','promotion_decision'):
        if isinstance(offer.get(key),Mapping): offer_source=offer.get(key); break
    offer_decision=_decision(offer_source,kind='OFFER',proof='pricing_economics_authority.offer_decision',allowed_statuses=('APPLIED','NOT_NEEDED'))
    br=_break_even(base,inputs)
    math_rows=[x for x in _l(base.get('scenarios')) if isinstance(x,Mapping)]
    math_status='CALCULATED' if math_rows and all(str(x.get('status') or '').upper()=='CALCULATED_FROM_EXPLICIT_INPUTS' for x in math_rows) else 'INCOMPLETE'
    ready=(not missing and math_status=='CALCULATED' and pricing.get('density_status')=='READY' and offer_decision.get('density_status')=='READY')
    return {
        'schema':'cbcc-economics-offer-authority-v0.6.76','status':'READY' if ready else 'TO_VERIFY',
        'currency':base.get('currency') or offer.get('currency'),'input_integrity':inputs,'missing_inputs':missing,
        'market_evidence':{
            'price_bands':deepcopy(base.get('market_price_bands') or []),'price_valleys':deepcopy(base.get('market_price_valleys') or []),
            'price_configuration_matrix':deepcopy(base.get('price_configuration_matrix') or []),
            'decision_boundary':'Market price evidence informs but never becomes the product price or recommendation without an explicit pricing decision.',
        },
        'scenario_math':{'status':math_status,'scenarios':deepcopy(math_rows),'legacy_status':base.get('status')},
        'pricing_decision':pricing,'offer_decision':offer_decision,'break_even':br,
        'downstream_use':{
            'listing':'Use only an explicitly selected price/offer; missing decision remains TO_VERIFY.',
            'ads':'Use CPA/CPC/ROAS only where the corresponding break-even object is AVAILABLE.',
            'promotion':'Discount/bundle/promo must come from the authored offer decision or a separately authored test.',
            'creator_affiliate':'Commission and offer must remain inside the same explicit contribution boundary.',
        },
        'legacy_compatibility':{
            'legacy_economics_present':bool(legacy_economics),'sensitivity_is_authority':False,
            'rule':'Legacy sensitivity/default scenario rows may remain compatibility analysis but cannot author price, discount, affiliate rate, offer, target contribution or readiness.',
        },
        'principle':'Explicit economics math and commercial Pricing/Offer decisions are separate requirements. Missing inputs remain missing; explicit zero is valid; market bands and legacy sensitivity never author the decision.',
    }

def economics_offer_issues(authority:Mapping[str,Any])->list[dict[str,Any]]:
    auth=_d(authority); issues=[]
    for name in REQUIRED_INPUTS:
        row=_d(_d(auth.get('input_integrity')).get(name))
        if row.get('status')!='EXPLICIT': issues.append({'code':'FULL_ECONOMICS_REQUIRED_INPUT_MISSING_V0676','input':name})
    pricing=_d(auth.get('pricing_decision'))
    if pricing.get('density_status')!='READY': issues.append({'code':'FULL_PRICING_DECISION_DENSITY_INCOMPLETE_V0676','fields':pricing.get('density_gaps') or list(DENSITY_FIELDS)})
    offer=_d(auth.get('offer_decision'))
    if offer.get('density_status')!='READY': issues.append({'code':'FULL_OFFER_DECISION_DENSITY_INCOMPLETE_V0676','fields':offer.get('density_gaps') or list(DENSITY_FIELDS)})
    return issues

def wrap_compile_pricing_economics_authority(fn:Callable[...,dict[str,Any]]):
    def compiled(request:dict[str,Any], market_analysis:dict[str,Any]|None=None, legacy_economics:dict[str,Any]|None=None):
        strict=fn(request,market_analysis,legacy_economics)
        phase2=materialize_economics_offer_authority(strict,request,legacy_economics)
        if _is_full_context(request,strict):
            out=deepcopy(dict(strict)); out['phase2_economics_offer_authority']=phase2
            out['phase2_business_status']=phase2.get('status')
            return out
        return strict
    setattr(compiled,'_cbcc_v0676_economics_offer_authority',True)
    return compiled

def wrap_validate_economics_offer(fn:Callable[...,dict[str,Any]]):
    def validated(value:dict[str,Any], request:dict[str,Any]|None=None, *args:Any, **kwargs:Any):
        result=fn(value,*args,**kwargs)
        if not _is_full_context(request,value): return result
        current=economics_offer_issues(value)
        issues=list(result.get('issues') or [])+current
        dedup=[]
        for item in issues:
            if item not in dedup: dedup.append(item)
        result['issues']=dedup; result['status']='PASS' if not dedup else 'INCOMPLETE'
        result['economics_offer_authority_v0676_audit']={'status':'PASS' if not current else 'INCOMPLETE','issues':current}
        return result
    return validated
