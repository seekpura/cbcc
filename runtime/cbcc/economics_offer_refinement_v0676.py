from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping

LINEAGE_FIELDS=('source_refs','source_type','recency','exact_fact','interpretation','confidence','assumption_boundary','downstream_use','conflict_status','proof_object')


def _p(v:Any)->bool: return v not in (None,'',[],{})
def _d(v:Any)->dict[str,Any]: return deepcopy(dict(v)) if isinstance(v,Mapping) else {}
def _l(v:Any)->list[Any]:
    if v in (None,'',{}): return []
    return list(v) if isinstance(v,(list,tuple,set,frozenset)) else [v]

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

def _lineage(name:str, value:Any, row:Mapping[str,Any])->dict[str,Any]:
    meta=_d(value) if isinstance(value,Mapping) else {}
    refs=meta.get('source_refs') or meta.get('source_ids') or ([meta.get('source_id')] if _p(meta.get('source_id')) else [])
    refs=list(dict.fromkeys(str(x) for x in _l(refs) if _p(x)))
    source_type=meta.get('source_type') or meta.get('kind') or meta.get('evidence_type')
    observed=meta.get('observed_at') or meta.get('updated_at') or meta.get('as_of') or meta.get('collected_at')
    present=str(row.get('status') or '').upper() in {'EXPLICIT','READY','APPLIED','NOT_NEEDED'}
    return {
      'source_refs':refs,
      'source_type':[str(source_type)] if _p(source_type) else (['UNRESOLVED_SOURCE_REF'] if refs else ['USER_OR_PROJECT_INPUT'] if present else []),
      'recency':[{'source_id':refs[0] if refs else None,'observed_at':observed}] if _p(observed) or refs else [],
      'interpretation':row.get('interpretation') or row.get('what') or row.get('why') or ('Explicit economics input.' if present else 'Unresolved economics input.'),
      'confidence':str(row.get('confidence') or ('HIGH' if refs else 'MEDIUM' if present else 'LOW')).upper(),
      'assumption_boundary':row.get('assumption_boundary'),
      'downstream_use':deepcopy(row.get('downstream_use') or ['pricing_offer','listing','ads']),
      'conflict_status':row.get('conflict_status') or 'NO_DECLARED_CONFLICT',
      'proof_object':row.get('proof_object') or f'offer_economics.{name}',
    }

def refine_economics_offer_authority(authority:Mapping[str,Any], request:Mapping[str,Any]|None=None)->dict[str,Any]:
    out=deepcopy(dict(authority)); offer=_d(_d(request).get('offer_economics'))
    inputs=_d(out.get('input_integrity'))
    for name,row0 in list(inputs.items()):
        if not isinstance(row0,Mapping): continue
        row=deepcopy(dict(row0))
        value=_input_value(offer,name) if name not in {'click_to_order_cvr','target_contribution'} else (offer.get('click_to_order_cvr') if name=='click_to_order_cvr' else offer.get('target_contribution',offer.get('minimum_contribution')))
        for k,v in _lineage(name,value,row).items(): row.setdefault(k,v)
        inputs[name]=row
    out['input_integrity']=inputs

    for key in ('pricing_decision','offer_decision'):
        row=_d(out.get(key)); source=_d(offer.get(key))
        refs=row.get('source_refs') or source.get('source_refs') or source.get('source_ids') or source.get('evidence_refs') or []
        row.setdefault('source_refs',list(dict.fromkeys(str(x) for x in _l(refs) if _p(x))))
        row.setdefault('source_type',['UNRESOLVED_SOURCE_REF'] if row.get('source_refs') else ['AGENT_AUTHORED_DECISION'] if row.get('density_status')=='READY' else [])
        row.setdefault('recency',deepcopy(source.get('recency') or []))
        row.setdefault('interpretation',row.get('what') or row.get('why'))
        row.setdefault('downstream_use',['listing','ads','promotion','creator_affiliate'])
        row.setdefault('conflict_status','NO_DECLARED_CONFLICT')
        row.setdefault('proof_object',f'pricing_economics_authority.{key}')
        out[key]=row

    target=_d(inputs.get('target_contribution'))
    target_explicit=target.get('status')=='EXPLICIT'
    br=_d(out.get('break_even'))
    if not target_explicit:
        for metric in ('cpa','cpc','roas'):
            row=_d(br.get(metric))
            if row.get('value') is not None and row.get('status')=='AVAILABLE':
                row['status']='BASELINE_ZERO_CONTRIBUTION_FLOOR_ONLY'
            if row:
                reqs=list(row.get('required_inputs') or [])
                if 'target_contribution_for_operating_boundary' not in reqs: reqs.append('target_contribution_for_operating_boundary')
                row['required_inputs']=reqs
                br[metric]=row
        br['target_contribution_status']=target.get('status') or 'BASELINE_ONLY'
        br['rule']='Zero-contribution break-even may remain as a labeled mathematical baseline. It is not an Ads/Offer operating boundary until target contribution is explicit.'
    out['break_even']=br
    out['req088_lineage_status']='READY' if not refinement_issues(out) else 'TO_VERIFY'
    return out

def refinement_issues(authority:Mapping[str,Any])->list[dict[str,Any]]:
    out=[]; auth=_d(authority)
    for name,row0 in _d(auth.get('input_integrity')).items():
        row=_d(row0); missing=[k for k in LINEAGE_FIELDS if k not in row]
        if missing: out.append({'code':'FULL_ECONOMICS_INPUT_LINEAGE_INCOMPLETE_V0676','input':name,'fields':missing})
    for key in ('pricing_decision','offer_decision'):
        row=_d(auth.get(key)); missing=[k for k in LINEAGE_FIELDS if k not in row]
        if missing: out.append({'code':'FULL_ECONOMICS_DECISION_LINEAGE_INCOMPLETE_V0676','decision':key,'fields':missing})
    target=_d(_d(auth.get('input_integrity')).get('target_contribution'))
    if target.get('status')!='EXPLICIT':
        for metric,row0 in _d(auth.get('break_even')).items():
            if metric not in {'cpa','cpc','roas'} or not isinstance(row0,Mapping): continue
            row=_d(row0)
            if row.get('value') is not None and row.get('status')=='AVAILABLE':
                out.append({'code':'FULL_BREAK_EVEN_ZERO_TARGET_FALSE_AVAILABLE_V0676','metric':metric})
    return out

def wrap_compile_pricing_economics_authority(fn:Callable[...,dict[str,Any]]):
    def compiled(request:dict[str,Any], *args:Any, **kwargs:Any):
        out=fn(request,*args,**kwargs); phase=_d(out.get('phase2_economics_offer_authority'))
        if phase:
            phase=refine_economics_offer_authority(phase,request); out=deepcopy(out)
            out['phase2_economics_offer_authority']=phase; out['phase2_business_status']=phase.get('status')
        return out
    setattr(compiled,'_cbcc_v0676_economics_offer_refinement',True); return compiled

def wrap_build_master_strategy(fn:Callable[...,dict[str,Any]]):
    def built(request:dict[str,Any], *args:Any, **kwargs:Any):
        out=fn(request,*args,**kwargs); sections=_d(out.get('sections')); core=_d(sections.get('04_marketing_core_strategy')); phase=_d(core.get('pricing_economics_offer'))
        if phase:
            core['pricing_economics_offer']=refine_economics_offer_authority(phase,request); sections['04_marketing_core_strategy']=core; out=deepcopy(out); out['sections']=sections
        return out
    setattr(built,'_cbcc_v0676_economics_offer_refinement',True); return built

def wrap_validate_strategy_delivery(fn:Callable[[dict[str,Any]],dict[str,Any]]):
    def validated(strategy:dict[str,Any]):
        result=fn(strategy); phase=_d(_d(_d(strategy.get('sections')).get('04_marketing_core_strategy')).get('pricing_economics_offer'))
        if not phase: return result
        current=refinement_issues(phase); issues=list(result.get('issues') or [])+current; dedup=[]
        for x in issues:
            if x not in dedup: dedup.append(x)
        result['issues']=dedup; result['status']='PASS' if not dedup else 'INCOMPLETE'
        result['economics_offer_refinement_v0676_audit']={'status':'PASS' if not current else 'INCOMPLETE','issues':current}
        return result
    setattr(validated,'_cbcc_v0676_economics_offer_refinement',True); return validated
