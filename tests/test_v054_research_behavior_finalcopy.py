from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project


def _pack(tmp_path):
    pack=tmp_path/'packs'; pack.mkdir()
    (pack/'test.yaml').write_text('''pack_id: test\nplatform_family: tiktok_shop\nsite: "*"\nstatus: TEST_FIXTURE_VERIFIED\nsynthetic_for_test: true\ncapabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, CREATOR_AFFILIATE, PAID, CX, MEASUREMENT, COMPLIANCE]\nsurfaces: [SEARCH_RESULTS, PDP, GALLERY, PDP_VIDEO, CREATOR, PAID_AD, FAQ]\nrule_atoms: []\nresearch_required_for: []\n''')
    return pack


def _approved(locale, fields):
    return [
        {'locale':locale,'field':f,'decision':'APPROVED','native_fluency':'PASS','claim_equivalence':'PASS','platform_fit':'PASS','culture_fit':'PASS','reviewer':'TEST_NATIVE_REVIEW'}
        for f in fields
    ]


def test_v054_research_behavior_finalcopy_and_platform_native_systems(tmp_path):
    costs={'landed_cost':18,'platform_fee':{'type':'rate','value':0.1},'fulfillment':4,'affiliate_commission':{'type':'rate','value':0.08},'ad_cost':4,'tax':0,'refund_allowance':2}
    fields={
        'title':'Portfolio Serum 30ml',
        'attributes':{'size':'30ml'},
        'highlights':['Light daily hydration'],
        '_localized_copy':{
            'en-MY':{'title':'Portfolio Serum 30ml','attributes':{'size':'30ml'},'highlights':['Light daily hydration']},
            'ms-MY':{'title':'Portfolio Serum 30ml','attributes':{'size':'30ml'},'highlights':['Hidrasi ringan untuk rutin harian']},
        },
        '_source_refs':{'title':['SRC-PROD'],'attributes':['SRC-PROD']},'_claim_refs':{'highlights':['CLM-1']},
    }
    fields['_localized_copy_reviews']=_approved('en-MY',['title','attributes','highlights'])+_approved('ms-MY',['title','attributes','highlights'])
    req={
      'project_id':'V054-INTEGRATION','planning_only':True,'sku':'S1',
      'product':{'name':'Portfolio Serum','category':'serum','net_content':'30ml','primary_conversion_proposition':'Light daily hydration'},
      'sources':[{'source_id':'SRC-PROD','kind':'PRODUCT_TRUTH'}],
      'claims':[{'claim_id':'CLM-1','claim':'Contains glycerin','status':'ACTIVE','evidence_level':'B','source_ids':['SRC-PROD']}],
      'target':{'market':'MY','jurisdiction':'MY','platform_family':'tiktok_shop','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY','ms-MY'],'surfaces':['SEARCH_RESULTS','PDP','GALLERY'],'currency':'MYR','category':'beauty'},
      'platform_content_targets':[
          {'market':'MY','site':'MY','platform_family':'tiktok_shop','primary_locale':'ms-MY','visible_copy_locales':['ms-MY','en-MY']},
          {'market':'MY','site':'MY','platform_family':'shopee','primary_locale':'ms-MY','visible_copy_locales':['ms-MY']},
          {'market':'US','site':'US','platform_family':'amazon','primary_locale':'en-US','visible_copy_locales':['en-US']},
          {'market':'US','site':'DTC','platform_family':'shopify','primary_locale':'en-US','visible_copy_locales':['en-US']},
      ],
      'market_keyword_rows':[{'term':'hydrating serum','volume':1000,'competition':0.4,'intent':'BENEFIT','source_id':'KW-1'}],
      'market_review_rows':[{'theme':'sticky feel','sentiment':'negative','competitor':'A','count':7,'source_id':'REV-A'}],
      'competitor_listing_rows':[{'competitor':'A','title':'A Hydrating Serum 30ml','message_theme':'sticky feel','offer_type':'single','proof_type':'ingredient callout','configuration':'30ml','surface':'PDP','locale':'en-MY','source_id':'LST-A'}],
      'market_source_records':[
          {'source_id':'KW-1','kind':'KEYWORD_DATA','observed_at':'2026-10-20','max_age_days':30,'market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty','population_scope':'MY TikTok Shop serum queries','sample_frame':'tracked serum keyword set','sampling_method':'query panel','inclusion_criteria':'serum category queries','coverage_note':'fixture'},
          {'source_id':'REV-A','kind':'COMPETITOR_REVIEW','observed_at':'2026-08-01','max_age_days':30,'market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty','population_scope':'competitor A review sample','sample_frame':'recent visible reviews','sampling_method':'convenience sample','inclusion_criteria':'visible reviews'},
          {'source_id':'LST-A','kind':'COMPETITOR_LISTING','observed_at':'2026-10-21','max_age_days':30,'market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty','population_scope':'competitor A listing','sample_frame':'named competitor listing','sampling_method':'census of supplied listing','inclusion_criteria':'current PDP'},
      ],
      'market_research_as_of':'2026-10-27',
      'market_research_scope':{'market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty'},
      'offer_economics':{'currency':'MYR','scenarios':[
          {'scenario_id':'CORE','sku':'S1','price':49,'costs':costs,'minimum_contribution':6,'configuration':'30ml','buyer_job':'daily hydration','target_segment':'new users','channel':'shop','lifecycle_stage':'ACQUISITION'},
          {'scenario_id':'PLUS','sku':'S2','price':55,'costs':{**costs,'landed_cost':20},'minimum_contribution':7,'configuration':'30ml','buyer_job':'daily hydration','target_segment':'new users','channel':'shop','lifecycle_stage':'CONVERSION'},
      ],
      'demand_signals':{'S1':{'orders':100},'S2':{'orders':80}},
      'portfolio_behavior_rows':[
          {'sku':'S1','visitors':1000,'orders':100,'new_customers':80,'repeat_customers':20,'revenue':4900,'contribution':900,'source_id':'BEH-1'},
          {'sku':'S2','visitors':900,'orders':81,'new_customers':60,'repeat_customers':21,'revenue':4455,'contribution':850,'source_id':'BEH-1'},
      ],
      'portfolio_pair_rows':[{'sku_a':'S1','sku_b':'S2','shared_visitors':420,'visitors_a':1000,'visitors_b':900,'switch_a_to_b':35,'switch_b_to_a':20,'source_id':'PAIR-1'}],
      'portfolio_cohort_rows':[{'cohort':'2026-Q3','sku':'S1','lifecycle_stage':'ACQUISITION','acquired_customers':80,'repeat_customers':20,'orders':120,'revenue':5880,'contribution':1080,'source_id':'COH-1'}],
      'portfolio_incrementality_rows':[{'test_id':'TEST-S2','sku':'S2','treatment_n':1000,'treatment_orders':110,'control_n':1000,'control_orders':90,'treatment_contribution':1200,'control_contribution':950,'randomized':True,'source_id':'EXP-1'}],
      },
      'listing_input':{'fields':fields,'keywords':[{'term':'hydrating serum','cluster':'BENEFIT','volume':1000,'source_id':'KW-1'}]},
      'shopper_questions':['What is it?','Why is it relevant?','Why believe it?'],
      'cmf':{'color':'truth-first','material':'packaging','finish':'preserve'},
      'compile_assets':True,
    }
    build_project(tmp_path/'proj',req,_pack(tmp_path))
    market=json.loads((tmp_path/'proj/artifacts/market_analysis.json').read_text())
    rq=market['research_quality']
    assert rq['status']=='SOURCE_QUALITY_COMPILED'
    assert 'REV-A' in rq['stale_by_declared_threshold']
    assert not rq['unresolved_source_ids']
    assert all(x['representativeness_status']=='REPRESENTATIVENESS_DOCUMENTED_NOT_PROVEN' for x in rq['sources'])

    econ=json.loads((tmp_path/'proj/artifacts/offer_economics.json').read_text())
    pb=econ['portfolio_behavior_validation']
    assert pb['status']=='BEHAVIORAL_VALIDATION_COMPILED'
    assert pb['pair_behavior'][0]['shared_on_a']==0.42
    assert pb['cohorts'][0]['repeat_customer_rate']==0.25
    assert pb['incrementality'][0]['relative_conversion_lift']>0.2
    assert econ['interaction_behavior_validation']['pairs'][0]['validation_status']=='BEHAVIORAL_EVIDENCE_AVAILABLE'

    listing=json.loads((tmp_path/'proj/artifacts/listing_analysis.json').read_text())['compiled']
    fc=listing['final_copy_workflow']
    assert fc['status']=='FINAL_COPY_WORKFLOW_COMPILED'
    assert fc['release_counts']['APPROVED_FINAL']==6
    assert all(p['status']=='APPROVED_FINAL' for p in fc['packages'])
    assert (tmp_path/'proj/artifacts/listing_final_copy/ms-MY.md').exists()

    strategy=json.loads((tmp_path/'proj/artifacts/strategy/strategy_authority.json').read_text())
    content=strategy['sections']['06_platform_content_matrix']
    systems={x['native_authoring_system']['system'] for x in content}
    assert {'TIKTOK_SHOP_NATIVE_COMMERCE','SHOPEE_COMPARISON_COMMERCE','AMAZON_SEARCH_PROOF_SYSTEM','DTC_MODULAR_PDP_LIFECYCLE'} <= systems
    core=strategy['sections']['04_marketing_core_strategy']
    assert core['product_strategy']['portfolio_behavior_validation']['status']=='BEHAVIORAL_VALIDATION_COMPILED'
    assert core['listing_strategy']['final_copy_workflow']['release_counts']['APPROVED_FINAL']==6

    ctx=json.loads((tmp_path/'proj/artifacts/strategy_reasoning_context.json').read_text())
    ids={x['id'] for x in ctx['selected_prompts']}
    assert {'PROMPT-RESEARCH-QUALITY','PROMPT-PORTFOLIO-BEHAVIOR','PROMPT-FINAL-COPY','PROMPT-PLATFORM-NATIVE-SYSTEMS'} <= ids
    md=(tmp_path/'proj/artifacts/strategy/MASTER_STRATEGY_CN.md').read_text()
    assert 'Research Source / Freshness / Representativeness Contract' in md
    assert 'Portfolio Behavioral / Cohort / Incrementality Validation' in md
    assert 'Local-language Final Copy Workflow' in md
    assert 'TIKTOK_SHOP_NATIVE_COMMERCE' in md
