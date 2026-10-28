from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project
from cbcc.category_strategy import classify_decision_intent


def _pack(tmp_path):
    d=tmp_path/'packs'; d.mkdir()
    (d/'test.yaml').write_text('''pack_id: test\nplatform_family: tiktok_shop\nsite: "*"\nstatus: TEST_FIXTURE_VERIFIED\nsynthetic_for_test: true\ncapabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, CREATOR_AFFILIATE, CX, MEASUREMENT]\nsurfaces: [PDP, GALLERY, PDP_VIDEO, CREATOR, FAQ]\nrule_atoms: []\nresearch_required_for: []\n''')
    return d


def test_v0510_current_evidence_can_reorder_category_prior_and_offer_stays_hypothesis(tmp_path):
    req=json.loads((ROOT/'tests/fixtures/v059_category_commerce/food_tea.json').read_text(encoding='utf-8'))
    req['project_id']='V0510-EVIDENCE-CONFLICT'
    req['shopper_questions']=[
        'What is this tea and what pack am I buying?',
        'How should I brew it and what flavor description is actually supported?',
        'What exactly is included in the pack?'
    ]
    req['market_keyword_rows']=[
        {'term':'how to brew black tea bags','volume':6000,'intent':'USAGE','source_id':'KW-PREP'},
        {'term':'black tea flavor','volume':5000,'intent':'BENEFIT','source_id':'KW-FLAVOR'},
    ]
    req['market_review_rows']=[
        {'theme':'brew preparation','sentiment':'negative','count':30,'source_id':'REV-PREP'},
        {'theme':'flavor expectation','sentiment':'negative','count':25,'source_id':'REV-FLAVOR'},
    ]
    req['market_source_records']=[
        {'source_id':'KW-PREP','kind':'SEARCH_DATA','observed_at':'2026-10-20','market':'Malaysia','site':'MY','platform_family':'tiktok_shop','category':'food_beverage'},
        {'source_id':'KW-FLAVOR','kind':'SEARCH_DATA','observed_at':'2026-10-20','market':'Malaysia','site':'MY','platform_family':'tiktok_shop','category':'food_beverage'},
        {'source_id':'REV-PREP','kind':'REVIEW_SAMPLE','observed_at':'2026-10-20','market':'Malaysia','site':'MY','platform_family':'tiktok_shop','category':'food_beverage'},
        {'source_id':'REV-FLAVOR','kind':'REVIEW_SAMPLE','observed_at':'2026-10-20','market':'Malaysia','site':'MY','platform_family':'tiktok_shop','category':'food_beverage'},
    ]
    costs={'landed_cost':8,'platform_fee':{'type':'rate','value':0.08},'fulfillment':3,'affiliate_commission':{'type':'rate','value':0.08},'ad_cost':3,'tax':0,'refund_allowance':1}
    req['offer_economics']={
        'currency':'MYR',
        'scenarios':[
            {'scenario_id':'SINGLE','sku':'TEA-1','price':29,'costs':costs,'minimum_contribution':5,'configuration':'20 bags'},
            {'scenario_id':'MULTI','sku':'TEA-2','price':52,'costs':{**costs,'landed_cost':15,'fulfillment':4},'minimum_contribution':8,'configuration':'2 x 20 bags','bundle':True},
        ],
        'promo_response_rows':[
            {'row_id':'P0','sku':'TEA-1','price':29,'orders':100,'conversion_rate':0.04,'discount_pct':0,'contribution_per_order':10,'period':'W1'},
            {'row_id':'P1','sku':'TEA-1','price':26.1,'orders':112,'conversion_rate':0.043,'discount_pct':0.10,'contribution_per_order':7,'period':'W2'},
        ],
        'bundle_affinity_rows':[
            {'pair_id':'B1','base_sku':'TEA-1','add_on_sku':'TEA-2','eligible_orders':200,'paired_orders':35,'incremental_contribution':40,'source_id':'BEH-1'}
        ],
        'repeat_cycle_rows':[
            {'observation_id':'R1','sku':'TEA-1','segment':'repeat buyers','days_between_orders':31,'customers':80,'repeat_rate':0.28,'source_id':'BEH-2'}
        ]
    }
    p=tmp_path/'proj'; build_project(p,req,_pack(tmp_path))
    st=json.loads((p/'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
    core=st['sections']['04_marketing_core_strategy']
    rec=core['category_evidence_reconciliation']
    assert rec['status']=='CATEGORY_EVIDENCE_RECONCILED'
    assert rec['effective_objection_priorities'][0]['objection_key']=='TASTE_PREP'
    assert any(x['type']=='CATEGORY_PRIOR_VS_CURRENT_EVIDENCE' for x in rec['conflicts'])
    assert rec['effective_proof_hierarchy'][0]['evidence_condition']['evidence_type']
    assert core['listing_strategy']['category_objection_checks'][0]['objection_key']=='TASTE_PREP'
    offer=core['product_strategy']['category_offer_evidence_validation']
    assert offer['promo_response']['status']=='PROMO_RESPONSE_COMPILED'
    assert offer['bundle_affinity']['status']=='BUNDLE_AFFINITY_COMPILED'
    assert offer['repeat_replacement_cycle']['status']=='REPEAT_REPLACEMENT_CYCLE_COMPILED'
    assert any(x['status']=='EVIDENCE_SUPPORTED_TEST_CANDIDATE_NOT_LOCKED' for x in offer['candidates'])
    matrix=st['sections']['06_platform_content_matrix']
    assert matrix and all(x['platform_category_intersection']['status']=='PLATFORM_CATEGORY_INTERSECTION' for x in matrix)
    ctx=json.loads((p/'artifacts/strategy_reasoning_context.json').read_text())
    pids={x['id'] for x in ctx['selected_prompts']}; kids={x.get('id') for x in ctx['selected_knowledge']}
    assert {'PROMPT-CATEGORY-EVIDENCE-RECONCILIATION','PROMPT-OFFER-RESPONSE-EVIDENCE'}.issubset(pids)
    assert {'KNOW-CATEGORY-EVIDENCE-RECONCILIATION','KNOW-OFFER-RESPONSE-EVIDENCE'}.issubset(kids)
    ents=set(ctx['ontology']['entities'])
    assert {'CategoryEvidenceReconciliation','ProofEvidenceCondition','PromoResponseObservation','PlatformCategoryIntersection'}.issubset(ents)


def test_v0510_fulfillment_intent_outranks_generic_prepare_word():
    assert classify_decision_intent('How is delivery and installation handled and what must I prepare?')=='DELIVERY_INSTALLATION'
    assert classify_decision_intent('How should I prepare and brew this tea?')=='SENSORY_PREP'
