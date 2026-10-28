from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project
from cbcc.tools.market import analyze_market
from cbcc.strategy_depth import build_market_depth
from cbcc.category_strategy import category_commerce_profile
from cbcc.evidence_reconciliation import reconcile_category_commerce


def _pack(tmp_path):
    d=tmp_path/'packs'; d.mkdir(exist_ok=True)
    (d/'test.yaml').write_text('''pack_id: test
platform_family: tiktok_shop
site: "*"
status: TEST_FIXTURE_VERIFIED
synthetic_for_test: true
capabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, CREATOR_AFFILIATE, CX, MEASUREMENT]
surfaces: [PDP, GALLERY, PDP_VIDEO, CREATOR, FAQ]
rule_atoms: []
research_required_for: []
''')
    return d


def _food_req():
    req=json.loads((ROOT/'tests/fixtures/v059_category_commerce/food_tea.json').read_text(encoding='utf-8'))
    req['shopper_questions']=['What is this tea?']
    return req


def test_v0511_weak_stale_scope_mismatched_evidence_does_not_easily_overrule_category_prior():
    req=_food_req(); cp=category_commerce_profile(req)
    reviews=[{'theme':'brew preparation','sentiment':'negative','count':100,'source_id':'REV-OLD'}]
    sources=[{'source_id':'REV-OLD','kind':'REVIEW_SAMPLE','observed_at':'2025-01-01','max_age_days':30,'market':'Singapore','site':'SG','platform_family':'amazon','category':'electronics','source_quality_tier':'LOW'}]
    market=analyze_market([],None,'configuration',[],None,reviews,[],sources,'2026-10-27',{'market':'Malaysia','site':'MY','platform_family':'tiktok_shop','category':'food_beverage'},None)
    rec=reconcile_category_commerce(req,build_market_depth(market,req),cp)
    assert rec['effective_objection_priorities'][0]['objection_key']=='DIETARY_FIT'
    taste=next(x for x in rec['effective_objection_priorities'] if x['objection_key']=='TASTE_PREP')
    assert taste['evidence_pressure'] < taste['category_prior_score']
    sig=next(x for x in rec['evidence_priority']['ranked_intents'] if x['intent']=='SENSORY_PREP')
    assert sig['quality_weighted_evidence'] < sig['raw_evidence_weight']
    assert sig['signals'][0]['quality']['freshness'] == 0.25
    assert sig['signals'][0]['quality']['scope_match'] < 1


def test_v0511_strong_current_scope_matched_evidence_can_overrule_category_prior():
    req=_food_req(); cp=category_commerce_profile(req)
    reviews=[{'theme':'brew preparation','sentiment':'negative','count':100,'source_id':'REV-CURRENT'}]
    sources=[{'source_id':'REV-CURRENT','kind':'REVIEW_SAMPLE','observed_at':'2026-10-25','max_age_days':30,'market':'Malaysia','site':'MY','platform_family':'tiktok_shop','category':'food_beverage','population_scope':'MY TikTok tea reviews','sample_frame':'tea listing review sample','sampling_method':'stratified sample','inclusion_criteria':'target category','source_quality_score':1.0}]
    market=analyze_market([],None,'configuration',[],None,reviews,[],sources,'2026-10-27',{'market':'Malaysia','site':'MY','platform_family':'tiktok_shop','category':'food_beverage'},None)
    rec=reconcile_category_commerce(req,build_market_depth(market,req),cp)
    assert rec['effective_objection_priorities'][0]['objection_key']=='TASTE_PREP'
    assert rec['conflicts'] and rec['conflicts'][0]['type']=='CATEGORY_PRIOR_VS_CURRENT_EVIDENCE'
    sig=next(x for x in rec['evidence_priority']['ranked_intents'] if x['intent']=='SENSORY_PREP')
    assert sig['quality_weighted_evidence'] > 80
    assert 'freshness' in rec['evidence_priority']['quality_model']['dimensions']


def test_v0511_market_fit_revision_routing_and_capability_integration_are_real_outputs(tmp_path):
    req=json.loads((ROOT/'tests/fixtures/v059_category_commerce/apparel_tshirt.json').read_text(encoding='utf-8'))
    req['project_id']='V0511-INTEGRATION'
    req['market_review_rows']=[{'theme':'weather resistance','sentiment':'negative','count':20,'source_id':'REV-WEATHER'}]
    req['market_source_records']=[{'source_id':'REV-WEATHER','kind':'REVIEW_SAMPLE','observed_at':'2026-10-25','market':req['target']['market'],'site':req['target']['site'],'platform_family':req['target']['platform_family'],'category':req['target'].get('category'),'population_scope':'target-market reviews','sample_frame':'category sample','sampling_method':'declared sample','inclusion_criteria':'target category','source_quality_score':0.9}]
    req['ad_rows']=[{'campaign_id':'C1','creative_id':'CR-1','impressions':10000,'clicks':40,'orders':2,'spend':100,'revenue':80}]
    req['ad_thresholds']={'min_ctr':0.01,'min_cvr':0.03}
    req['feedback_rows']=[{'category':'USAGE_DIFFICULTY','severity':'HIGH','source':'CS','text':'Customers are unsure about care/use.'}]
    p1=tmp_path/'p1'; build_project(p1,req,_pack(tmp_path))
    fit=json.loads((p1/'artifacts/market_evidence_fit_contract.json').read_text())
    cand=next(x for x in fit['candidates'] if x['kind']=='REVIEW_THEME' and x['label']=='weather resistance')
    arch=json.loads((p1/'artifacts/asset_architecture.json').read_text())
    assert not any(x.get('decision_origin')=='MARKET_THEME_FIT' for x in arch['assets'])
    # Explicit Product Truth fit response is what activates routing; Runtime does not infer it from the review theme.
    req['host_market_evidence_fit_responses']=[{'candidate_id':cand['candidate_id'],'fit_status':'CONFIRMED','product_truth_fit':True,'consumer_question':'What weather-exposure boundary should the shopper understand before purchase?','product_truth_refs':['PRODUCT-TRUTH-DECLARED-BY-HOST']}]
    p2=tmp_path/'p2'; build_project(p2,req,_pack(tmp_path))
    fit2=json.loads((p2/'artifacts/market_evidence_fit_contract.json').read_text())
    assert fit2['approved_asset_jobs']
    arch2=json.loads((p2/'artifacts/asset_architecture.json').read_text())
    assert any(x.get('decision_origin')=='MARKET_THEME_FIT' for x in arch2['assets'])
    routing=json.loads((p2/'artifacts/strategy_revision_routing.json').read_text())
    assert routing['status']=='STRATEGY_REVISION_ROUTING_COMPILED'
    assert any(x['source']=='ADS' and 'MESSAGE_P0' in x['edit_layers'] for x in routing['routes'])
    assert any(x['source']=='FEEDBACK' and 'USAGE_CONTENT' in x['edit_layers'] for x in routing['routes'])
    cmap=json.loads((p2/'artifacts/capability_integration_map.json').read_text())
    assert cmap['integration_gaps']==[]
    rows={x['capability']:x for x in cmap['capabilities']}
    assert rows['ADS']['runtime_wiring_status']=='INTEGRATED_ACTIVE'
    assert rows['FEEDBACK']['runtime_wiring_status']=='INTEGRATED_ACTIVE'
    assert rows['MARKET_COMPETITOR_CUSTOMER']['runtime_wiring_status']=='INTEGRATED_ACTIVE'
    ctx=json.loads((p2/'artifacts/strategy_reasoning_context.json').read_text())
    pids={x['id'] for x in ctx['selected_prompts']}; kids={x.get('id') for x in ctx['selected_knowledge']}
    assert {'PROMPT-EVIDENCE-QUALITY-WEIGHTING','PROMPT-REVISION-INTEGRATION'}.issubset(pids)
    assert {'KNOW-EVIDENCE-QUALITY-WEIGHTING','KNOW-REVISION-INTEGRATION'}.issubset(kids)
    ents=set(ctx['ontology']['entities'])
    assert {'EvidenceQualityWeight','MarketEvidenceFitContract','StrategyRevisionRoute','CapabilityIntegrationMap'}.issubset(ents)


def test_v0511_adapter_only_market_path_activates_quality_and_reconciliation_authorities(tmp_path):
    req=_food_req(); req['project_id']='V0511-ADAPTER-DOMAIN'
    req['research_source_adapters']=[{
        'adapter_id':'REV-ONLY','adapter_family':'REVIEW_VOICE','dataset':'market_review_rows',
        'refresh_mode':'FULL_SNAPSHOT','primary_key':'review_id','source_id':'REV-A',
        'source_record':{'source_id':'REV-A','kind':'REVIEW_EXPORT','observed_at':'2026-10-25','max_age_days':30,'market':'Malaysia','site':'MY','platform_family':'tiktok_shop','category':'food_beverage','population_scope':'target reviews','sample_frame':'supplied target reviews','sampling_method':'host export','inclusion_criteria':'target category','source_quality_score':0.9},
        'rows':[{'review_id':'R1','theme':'brew preparation','sentiment':'negative','count':20}]
    }]
    req['market_research_as_of']='2026-10-27'
    req['market_research_scope']={'market':'Malaysia','site':'MY','platform_family':'tiktok_shop','category':'food_beverage'}
    p=tmp_path/'p'; build_project(p,req,_pack(tmp_path))
    ctx=json.loads((p/'artifacts/strategy_reasoning_context.json').read_text())
    pids={x['id'] for x in ctx['selected_prompts']}; kids={x.get('id') for x in ctx['selected_knowledge']}
    assert 'PROMPT-EVIDENCE-QUALITY-WEIGHTING' in pids
    assert 'PROMPT-CATEGORY-EVIDENCE-RECONCILIATION' in pids
    assert 'KNOW-EVIDENCE-QUALITY-WEIGHTING' in kids
    assert 'KNOW-CATEGORY-EVIDENCE-RECONCILIATION' in kids
