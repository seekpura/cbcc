from __future__ import annotations
from pathlib import Path
import importlib.util, sys

MODULE=Path(__file__).parents[1]/'runtime/cbcc/listing_search_authority.py'
spec=importlib.util.spec_from_file_location('listing_search_authority_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)

DENSITY=('what','why','evidence','tradeoff','execution','measurement')
LINEAGE=('source_refs','source_type','recency','exact_fact','interpretation','confidence','assumption_boundary','downstream_use','conflict_status','proof_object')
MAJOR=('search','title','bullets','description','attributes','usage','package','faq','claim_mapping')


def decision(name, source='SRC-PRODUCT'):
    return {
        'decision':f'{name} decision',
        'what':f'Use the authored {name} decision.',
        'why':f'{name} changes shopper understanding or publishability.',
        'evidence':[source],
        'tradeoff':f'Keep {name} precise instead of adding unsupported breadth.',
        'execution':f'Apply {name} only in its assigned Listing/Search field or job.',
        'measurement':f'Review {name} accuracy, relevance and conversion contribution.',
        'source_refs':[source], 'source_type':'PRODUCT_TRUTH' if source=='SRC-PRODUCT' else 'SEARCH_RESEARCH',
        'recency':'2026-10-30', 'exact_fact':f'{name} evidence',
        'interpretation':f'{name} evidence informs this decision without increasing claim strength.',
        'confidence':'HIGH', 'assumption_boundary':None,
        'downstream_use':['listing_search'], 'conflict_status':'NO_DECLARED_CONFLICT',
        'proof_object':f'listing_search_authority.decisions.{name}',
    }


def request():
    return {
        'delivery_mode':'FULL_PROJECT',
        'sources':[
            {'source_id':'SRC-PRODUCT','source_type':'PRODUCT_TRUTH','as_of':'2026-10-30'},
            {'source_id':'SRC-SEARCH','source_type':'SEARCH_RESEARCH','as_of':'2026-10-31'},
            {'source_id':'SRC-ECON','source_type':'ECONOMICS','as_of':'2026-11-01'},
        ],
        'target':{
            'market':'Malaysia','site':'MY','platform_family':'TikTok Shop',
            'primary_locale':'ms-MY','visible_copy_locales':['ms-MY','en-MY'],'delivery_locale':'zh-CN'
        },
        'listing_input':{
            'phase2_decisions':{k:decision(k,'SRC-SEARCH' if k=='search' else 'SRC-PRODUCT') for k in MAJOR}
        }
    }


def compiled_listing(include_en=True):
    fields={
        'title':'KIYUU Gel Kawalan Minyak 30g','bullets':['1% Niacinamide','2% Panthenol'],
        'description':'Gel pelembap harian untuk rutin kulit berminyak.','attributes':{'Net Content':'30g'},
        'usage':'Sapukan selepas mencuci muka.','package':'1 × KIYUU Gel 30g',
        'faq':[{'q':'Untuk rutin apa?','a':'Rutin harian kulit berminyak.'}],
    }
    packages=[{
        'locale':'ms-MY','status':'APPROVED_FINAL','fields':[
            {'field':k,'authored_copy':v,'release_status':'APPROVED_FINAL','delivery_companion_status':'READY','delivery_translation':f'中文：{k}'}
            for k,v in fields.items()
        ]
    }]
    if include_en:
        packages.append({'locale':'en-MY','status':'APPROVED_FINAL','fields':[
            {'field':k,'authored_copy':v,'release_status':'APPROVED_FINAL','delivery_companion_status':'READY','delivery_translation':f'中文：{k}'}
            for k,v in fields.items()
        ]})
    return {
        'status':'LISTING_CONTRACT_COMPILED','fields':fields,'pass':True,
        'keyword_priority':[{'term':'gel kawalan minyak','cluster':'CORE','source_id':'SRC-SEARCH','priority_score':1.0,'role':'TITLE_OR_PRIMARY','decision_stage':'SEARCH_RELEVANCE'}],
        'keywords':{'status':'AGGREGATED_FROM_CLASSIFIED_INPUT','clusters':{'CORE':[{'term':'gel kawalan minyak','source_id':'SRC-SEARCH'}]}},
        'traceability':[
            {'field':'title','source_ids':['SRC-PRODUCT'],'claim_ids':['CLM-1'],'has_value':True},
            {'field':'bullets','source_ids':['SRC-PRODUCT'],'claim_ids':['CLM-1'],'has_value':True},
            {'field':'description','source_ids':['SRC-PRODUCT'],'claim_ids':['CLM-1'],'has_value':True},
            {'field':'attributes','source_ids':['SRC-PRODUCT'],'claim_ids':[],'has_value':True},
            {'field':'usage','source_ids':['SRC-PRODUCT'],'claim_ids':[],'has_value':True},
            {'field':'package','source_ids':['SRC-PRODUCT'],'claim_ids':[],'has_value':True},
            {'field':'faq','source_ids':['SRC-PRODUCT'],'claim_ids':['CLM-1'],'has_value':True},
        ],
        'field_decision_map':[{'field':k,'decision_job':'DECISION SUPPORT','why':'explicit'} for k in fields],
        'final_copy_workflow':{'status':'FINAL_COPY_WORKFLOW_COMPILED','primary_locale':'ms-MY','delivery_locale':'zh-CN','packages':packages},
    }


def pricing(ready=True):
    phase2={
        'status':'READY' if ready else 'TO_VERIFY',
        'pricing_decision':{
            'density_status':'READY' if ready else 'TO_VERIFY','decision':'MYR 59 base price' if ready else None,
            'exact_fact':'MYR 59 base price' if ready else None,'source_refs':['SRC-ECON'] if ready else []
        },
        'offer_decision':{
            'density_status':'READY' if ready else 'TO_VERIFY','decision':'No automatic launch discount' if ready else None,
            'exact_fact':'No automatic launch discount' if ready else None,'source_refs':['SRC-ECON'] if ready else []
        }
    }
    return {'phase2_business_status':phase2['status'],'phase2_economics_offer_authority':phase2}


def market():
    return {'research_authority':{'status':'READY'},'price_bands':[{'low':39,'high':69}], 'keyword_research':[{'term':'gel kawalan minyak','source_id':'SRC-SEARCH'}]}


def test_complete_publishable_listing_search_authority_is_ready_with_density_and_lineage():
    out=mod.materialize_listing_search_authority(compiled_listing(),request(),market(),pricing())
    assert out['status']=='READY'
    assert out['publishability']['status']=='READY'
    assert out['language_continuity']['english_semantic_baseline_status']=='READY'
    assert out['language_continuity']['delivery_companion_status']=='READY'
    assert set(out['decisions'])==set(MAJOR)
    for row in out['decisions'].values():
        assert row['density_status']=='READY'
        assert all(row[k] not in (None,'',[],{}) for k in DENSITY)
        assert all(k in row for k in LINEAGE)
    assert out['search_evidence']['terms'][0]['term']=='gel kawalan minyak'
    assert out['search_evidence']['terms'][0]['source_id']=='SRC-SEARCH'
    assert mod.listing_search_issues(out)==[]


def test_missing_major_listing_decision_cannot_false_pass_from_existing_copy():
    req=request(); req['listing_input']['phase2_decisions'].pop('faq')
    out=mod.materialize_listing_search_authority(compiled_listing(),req,market(),pricing())
    assert out['status']=='TO_VERIFY'
    assert out['decisions']['faq']['density_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_LISTING_MAJOR_DECISION_INCOMPLETE_V0676' and x['object']=='faq' for x in mod.listing_search_issues(out))


def test_market_price_band_never_becomes_listing_price_without_explicit_phase2_pricing_decision():
    out=mod.materialize_listing_search_authority(compiled_listing(),request(),market(),pricing(False))
    assert out['pricing_offer_context']['selected_price'] is None
    assert out['pricing_offer_context']['status']=='TO_VERIFY'
    assert out['status']=='TO_VERIFY'
    assert any(x['code']=='FULL_LISTING_PRICING_OFFER_CONTEXT_INCOMPLETE_V0676' for x in mod.listing_search_issues(out))


def test_missing_english_semantic_baseline_blocks_full_non_english_publishability_without_inventing_copy():
    out=mod.materialize_listing_search_authority(compiled_listing(include_en=False),request(),market(),pricing())
    assert out['language_continuity']['english_semantic_baseline_status']=='TO_VERIFY'
    assert out['status']=='TO_VERIFY'
    assert any(x['code']=='FULL_LISTING_ENGLISH_BASELINE_MISSING_V0676' for x in mod.listing_search_issues(out))


def test_unsourced_search_terms_remain_visible_but_do_not_satisfy_search_evidence_lineage():
    compiled=compiled_listing(); compiled['keyword_priority'][0]['source_id']=None
    compiled['keywords']['clusters']['CORE'][0]['source_id']=None
    out=mod.materialize_listing_search_authority(compiled,request(),market(),pricing())
    assert out['search_evidence']['terms'][0]['source_id'] is None
    assert out['search_evidence']['status']=='TO_VERIFY'
    assert out['status']=='TO_VERIFY'
    assert any(x['code']=='FULL_LISTING_SEARCH_EVIDENCE_UNSOURCED_V0676' for x in mod.listing_search_issues(out))


def test_compile_wrapper_adds_phase2_authority_without_destroying_mature_listing_payload():
    legacy=compiled_listing()
    def base(*args,**kwargs): return legacy
    wrapped=mod.wrap_compile_listing(base)
    out=wrapped({}, {}, [], {}, {}, [], {}, phase2_context={'request':request(),'market_analysis':market(),'pricing_economics':pricing()})
    assert out['status']=='LISTING_CONTRACT_COMPILED'
    assert out['fields']==legacy['fields']
    assert out['phase2_business_status']=='READY'
    assert out['phase2_listing_search_authority']['status']=='READY'


def test_seven_tool_bridge_exposes_listing_business_readiness_separately_from_legacy_compile_status():
    authority=mod.materialize_listing_search_authority(compiled_listing(),request(),market(),pricing())
    domain={'listing':{'status':'LISTING_CONTRACT_COMPILED','compiled':{'phase2_business_status':'READY','phase2_listing_search_authority':authority}}}
    def base(**kwargs):
        return {'status':'SEVEN_TOOL_CONTINUITY_COMPILED','capabilities':[{'id':'03_LISTING_CREATIVE','project_status':'LISTING_CONTRACT_COMPILED','evidence':{}}]}
    out=mod.wrap_compile_seven_tool_continuity(base)(domain=domain)
    row=out['capabilities'][0]
    assert row['project_status']=='LISTING_CONTRACT_COMPILED'
    assert row['business_readiness_status']=='READY'
    assert row['evidence']['listing_business_readiness_status']=='READY'
