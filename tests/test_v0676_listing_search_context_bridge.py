from __future__ import annotations
from pathlib import Path
import importlib.util, sys

MODULE=Path(__file__).parents[1]/'runtime/cbcc/listing_search_authority.py'
spec=importlib.util.spec_from_file_location('listing_search_context_bridge_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)


def _decision(name, source):
    return {'decision':f'{name} decision','what':f'{name} what','why':f'{name} why','evidence':[source],
            'tradeoff':f'{name} tradeoff','execution':f'{name} execution','measurement':f'{name} measurement',
            'source_refs':[source],'source_type':'SEARCH_RESEARCH' if name=='search' else 'PRODUCT_TRUTH',
            'recency':'2026-11-01','exact_fact':f'{name} fact','interpretation':f'{name} interpretation','confidence':'HIGH',
            'assumption_boundary':None,'downstream_use':['listing_search'],'conflict_status':'NO_DECLARED_CONFLICT',
            'proof_object':f'listing_search_authority.decisions.{name}'}


def _request():
    major=('search','title','bullets','description','attributes','usage','package','faq','claim_mapping')
    return {'delivery_mode':'FULL_PROJECT','sources':[{'source_id':'SRC-PRODUCT','source_type':'PRODUCT_TRUTH','as_of':'2026-11-01'},{'source_id':'SRC-SEARCH','source_type':'SEARCH_RESEARCH','as_of':'2026-11-01'}],
            'target':{'primary_locale':'ms-MY','visible_copy_locales':['ms-MY','en-MY'],'delivery_locale':'zh-CN'},
            'listing_input':{'phase2_decisions':{k:_decision(k,'SRC-SEARCH' if k=='search' else 'SRC-PRODUCT') for k in major}}}


def _listing():
    fields={'title':'T','bullets':['B'],'description':'D','attributes':{'size':'30g'},'usage':'U','package':'P','faq':[{'q':'Q','a':'A'}]}
    packages=[{'locale':loc,'status':'APPROVED_FINAL','fields':[{'field':k,'authored_copy':v,'release_status':'APPROVED_FINAL','delivery_companion_status':'READY','delivery_translation':'中文'} for k,v in fields.items()]} for loc in ('ms-MY','en-MY')]
    return {'status':'LISTING_CONTRACT_COMPILED','pass':True,'fields':fields,
            'keyword_priority':[{'term':'gel kawalan minyak','source_id':'SRC-SEARCH'}],
            'traceability':[{'field':k,'source_ids':['SRC-PRODUCT'],'claim_ids':[],'has_value':True} for k in fields],
            'final_copy_workflow':{'primary_locale':'ms-MY','delivery_locale':'zh-CN','packages':packages}}


def _pricing():
    phase2={'status':'READY','pricing_decision':{'density_status':'READY','decision':'MYR 59','exact_fact':'MYR 59'},
            'offer_decision':{'density_status':'READY','decision':'No launch discount','exact_fact':'No launch discount'}}
    return {'phase2_business_status':'READY','phase2_economics_offer_authority':phase2}


def test_pricing_context_bridge_hands_real_request_market_and_economics_to_later_listing_compile():
    req=_request(); market={'price_bands':[{'low':39,'high':69}]}
    pricing_wrapped=mod.wrap_compile_pricing_economics_for_listing_context(lambda request, market_analysis=None, legacy_economics=None: _pricing())
    listing_wrapped=mod.wrap_compile_listing(lambda *args,**kwargs: _listing())
    strict=pricing_wrapped(req,market,None)
    assert strict['phase2_business_status']=='READY'
    out=listing_wrapped({}, {}, [], {}, {}, [], {})
    assert out['phase2_business_status']=='READY'
    authority=out['phase2_listing_search_authority']
    assert authority['pricing_offer_context']['selected_price']=='MYR 59'
    assert authority['search_evidence']['terms'][0]['source_id']=='SRC-SEARCH'
