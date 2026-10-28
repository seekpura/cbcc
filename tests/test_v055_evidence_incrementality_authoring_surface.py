from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project

FULL_ASSET_FILES={
    '00_asset_manifest.yaml','01_strategy.md','02_visual_spec.md','03_photography_contract.json','04_layout_contract.json',
    '05_prompt_CN.txt','06_prompt_EN.txt','07_generation_guidance.txt','08_copy.md','09_production_notes.md','10_source_trace.md','11_strategy_authority_trace.json'
}


def _pack(tmp_path):
    pack=tmp_path/'packs'; pack.mkdir()
    (pack/'test.yaml').write_text('''pack_id: test
platform_family: tiktok_shop
site: "*"
status: TEST_FIXTURE_VERIFIED
synthetic_for_test: true
capabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, CREATOR_AFFILIATE, PAID, CX, MEASUREMENT, COMPLIANCE]
surfaces: [SEARCH_RESULTS, PDP, GALLERY, PDP_VIDEO, CREATOR, LIVE, PAID_AD, FAQ]
rule_atoms: []
research_required_for: []
''')
    return pack


def test_v055_evidence_incrementality_copy_versions_surface_and_asset_why(tmp_path):
    costs={'landed_cost':18,'platform_fee':{'type':'rate','value':0.10},'fulfillment':4,'affiliate_commission':{'type':'rate','value':0.08},'ad_cost':4,'tax':0,'refund_allowance':2}
    req={
        'project_id':'V055-INTEGRATION','planning_only':True,'sku':'S1',
        'product':{'name':'Portfolio Serum','category':'serum','net_content':'30ml','primary_conversion_proposition':'Light daily hydration'},
        'sources':[{'source_id':'SRC-PROD','kind':'PRODUCT_TRUTH'}],
        'claims':[{'claim_id':'CLM-1','claim':'Contains glycerin','status':'ACTIVE','evidence_level':'B','source_ids':['SRC-PROD']}],
        'target':{'market':'MY','jurisdiction':'MY','platform_family':'tiktok_shop','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY','ms-MY'],'surfaces':['SEARCH_RESULTS','PDP','GALLERY','PDP_VIDEO'],'currency':'MYR','category':'beauty'},
        'platform_content_targets':[
            {'market':'MY','site':'MY','platform_family':'tiktok_shop','primary_locale':'ms-MY','visible_copy_locales':['ms-MY','en-MY'],'surfaces':['SEARCH_RESULTS','PDP','CREATOR','LIVE']},
            {'market':'MY','site':'MY','platform_family':'shopee','primary_locale':'ms-MY','visible_copy_locales':['ms-MY'],'surfaces':['SEARCH_RESULTS','PDP','FAQ']},
            {'market':'US','site':'US','platform_family':'amazon','primary_locale':'en-US','visible_copy_locales':['en-US'],'surfaces':['SEARCH_RESULTS','PDP','A_PLUS']},
            {'market':'US','site':'DTC','platform_family':'shopify','primary_locale':'en-US','visible_copy_locales':['en-US'],'surfaces':['COLLECTION','PDP','LANDING']},
        ],
        'market_rows':[
            {'listing_id':'A-1','seller_name':'A','selling_price':49,'sold':100,'gmv':4900,'pack':'30ml','source_id':'M1','observed_at':'2026-10-20'},
            {'listing_id':'A-1','seller_name':'A','selling_price':49,'sold':100,'gmv':4900,'pack':'30ml','source_id':'M1','observed_at':'2026-10-20'},
        ],
        'market_field_map':{'seller':'seller_name','price':'selling_price','units':'sold','revenue':'gmv','configuration':'pack'},
        'market_research_ingestion':{'dedup_mode':'EXACT_SOURCE_ROW'},
        'market_source_records':[
            {'source_id':'M1','logical_source_id':'COMP-A','version_id':'V1','kind':'MARKET_SNAPSHOT','observed_at':'2026-10-20','max_age_days':30,'market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty','population_scope':'supplied competitor snapshot','sample_frame':'supplied competitor listing','sampling_method':'census of supplied rows','inclusion_criteria':'named competitor'},
            {'source_id':'M1-V2','logical_source_id':'COMP-A','version_id':'V2','supersedes':'V1','kind':'MARKET_SNAPSHOT','observed_at':'2026-10-25','max_age_days':30,'market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty','population_scope':'supplied competitor snapshot','sample_frame':'supplied competitor listing','sampling_method':'census of supplied rows','inclusion_criteria':'named competitor'},
        ],
        'market_research_as_of':'2026-10-27',
        'market_research_scope':{'market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty'},
        'offer_economics':{'currency':'MYR','scenarios':[
            {'scenario_id':'CORE','sku':'S1','price':49,'costs':costs,'minimum_contribution':6,'configuration':'30ml','buyer_job':'daily hydration','target_segment':'new users','channel':'shop','lifecycle_stage':'ACQUISITION'},
            {'scenario_id':'PLUS','sku':'S2','price':59,'costs':{**costs,'landed_cost':20},'minimum_contribution':7,'configuration':'2x30ml','buyer_job':'stock-up hydration','target_segment':'repeat users','channel':'shop','lifecycle_stage':'RETENTION'},
        ]},
        'portfolio_pair_rows':[{'sku_a':'S1','sku_b':'S2','switch_a_to_b':12,'switch_b_to_a':5,'eligible_a':100,'eligible_b':80,'shared_visitors':35,'visitors_a':100,'visitors_b':80,'source_id':'PAIR-1'}],
        'portfolio_cohort_rows':[{'cohort':'2026-Q3','sku':'S1','cohort_definition':'first order in Q3','observation_window':'90d','acquisition_channel':'TikTok Shop','market':'MY','acquired_customers':80,'repeat_customers':20,'orders':120,'revenue':5880,'contribution':1080,'source_id':'COH-1'}],
        'portfolio_holdout_rows':[{'test_id':'H-1','sku':'S2','assignment_unit':'user','randomized':True,'contamination_rate':0.01,'treatment_n':1000,'control_n':1000,'treatment_orders':120,'control_orders':100,'treatment_contribution':1400,'control_contribution':1000,'intervention_cost':100,'source_id':'EXP-1'}],
        'listing_input':{'fields':{
            'title':'Portfolio Serum 30ml',
            'attributes':{'size':'30ml'},
            'highlights':['Light daily hydration'],
            '_localized_copy':{
                'en-MY':{'title':'Portfolio Serum 30ml','attributes':{'size':'30ml'},'highlights':['Light daily hydration']},
                'ms-MY':{'title':'Portfolio Serum 30ml','attributes':{'size':'30ml'},'highlights':['Hidrasi ringan untuk rutin harian']},
            },
            '_localized_copy_history':[
                {'locale':'ms-MY','field':'title','version_id':'MS-TITLE-V1','copy':'Portfolio Serum 30ml','created_at':'2026-10-20T00:00:00+00:00'},
                {'locale':'ms-MY','field':'title','version_id':'MS-TITLE-V2','copy':'Portfolio Serum Ringan 30ml','created_at':'2026-10-26T00:00:00+00:00'},
            ],
            '_localized_copy_reviews':[
                {'locale':'ms-MY','field':'title','version_id':'MS-TITLE-V1','decision':'APPROVED','native_fluency':'PASS','claim_equivalence':'PASS','platform_fit':'PASS','culture_fit':'PASS','reviewer':'NATIVE-REVIEWER'}
            ],
            '_source_refs':{'title':['SRC-PROD'],'attributes':['SRC-PROD']},'_claim_refs':{'highlights':['CLM-1']},
        },'keywords':[]},
        'shopper_questions':['What is it?','Why is it relevant?','Why believe it?'],
        'cmf':{'color':'truth-first','material':'packaging','finish':'preserve'},
        'photography_contract':{
            'capture_mode':'REAL_PHOTO',
            'camera':{'focal_length_mm':85,'camera_height':'product center','working_distance':'1m','focus_plane':'front label','yaw':0,'pitch':0,'roll':0,'aperture':'f/8','dof':'full front label legible'},
            'composition':{'product_occupancy':{'height_pct':68},'shot_size':'product hero'},
            'lighting':{'key':{'direction':'camera-left 45deg','modifier':'large diffusion'},'fill':'low soft fill','negative_fill':'camera-right flag','rim':'subtle separation','cct':5200,'white_balance':'neutral reference','shadow_policy':'soft grounding shadow','highlight_policy':'protect label','reflection_control':'angle + flags + polarization if required'},
            'color_management':{'white_balance':'neutral reference','output_space':'sRGB','product_color_fidelity':'truth-first'},
        },
        'compile_assets':True,
    }

    build_project(tmp_path/'proj',req,_pack(tmp_path))

    market=json.loads((tmp_path/'proj/artifacts/market_analysis.json').read_text())
    ing=market['research_ingestion']
    card=next(x for x in ing['datasets'] if x['dataset']=='market_rows')
    assert card['input_rows']==2 and card['canonical_rows']==1 and card['exact_duplicates']==1
    assert market['normalization']['row_count']==1
    assert any(x['relation']=='EXPLICIT_SUPERSEDES' and x['from_version']=='V1' and x['to_version']=='V2' for x in ing['lineage_edges'])

    econ=json.loads((tmp_path/'proj/artifacts/offer_economics.json').read_text())
    trans=econ['switch_matrix']['transitions']
    ab=next(x for x in trans if x['from_sku']=='S1' and x['to_sku']=='S2')
    ba=next(x for x in trans if x['from_sku']=='S2' and x['to_sku']=='S1')
    assert ab['switch_rate']==0.12 and ba['switch_rate']==0.0625
    assert econ['cohort_comparability']['cohorts'][0]['comparability_status']=='DOCUMENTED_FOR_COMPARISON_REVIEW'
    hold=econ['holdout_marginal_contribution']['tests'][0]
    assert hold['net_incremental_contribution']==300.0
    assert hold['design_readiness']=='CAUSAL_REVIEW_READY_NOT_SIGNIFICANCE_TESTED'

    listing=json.loads((tmp_path/'proj/artifacts/listing_analysis.json').read_text())['compiled']
    ms_title=next(x for p in listing['final_copy_workflow']['packages'] if p['locale']=='ms-MY' for x in p['fields'] if x['field']=='title')
    assert ms_title['current_version_id']=='MS-TITLE-V2'
    assert ms_title['review_version_id']=='MS-TITLE-V1'
    assert ms_title['release_status']=='REVIEW_STALE_AFTER_REVISION'
    assert listing['copy_authoring_iteration_plan']['revision_tasks']
    assert listing['copy_authoring_iteration_plan']['review_tasks']

    strategy=json.loads((tmp_path/'proj/artifacts/strategy/strategy_authority.json').read_text())
    assert len(strategy['sections'])==9
    content=strategy['sections']['06_platform_content_matrix']
    systems={x['native_authoring_system']['system'] for x in content}
    assert {'TIKTOK_SHOP_NATIVE_COMMERCE','SHOPEE_COMPARISON_COMMERCE','AMAZON_SEARCH_PROOF_SYSTEM','DTC_MODULAR_PDP_LIFECYCLE'} <= systems
    assert all(x.get('surface_authoring_contract') for x in content)
    visual=strategy['sections']['05_visual_photography_strategy']
    assert visual['asset_parameter_reasoning']
    assert all(x.get('causal_chain') and x.get('parameter_why') for x in visual['asset_parameter_reasoning'])

    ctx=json.loads((tmp_path/'proj/artifacts/strategy_reasoning_context.json').read_text())
    prompt_ids={x['id'] for x in ctx['selected_prompts']}
    know_ids={x.get('id') for x in ctx['selected_knowledge'] if x.get('id')}
    assert {'PROMPT-EVIDENCE-INGESTION','PROMPT-MARGINAL-CONTRIBUTION','PROMPT-COPY-ITERATION','PROMPT-ASSET-PHOTO-WHY'} <= prompt_ids
    assert {'KNOW-EVIDENCE-INGESTION','KNOW-MARGINAL-CONTRIBUTION','KNOW-COPY-ITERATION','KNOW-ASSET-PHOTO-WHY'} <= know_ids

    idx=json.loads((tmp_path/'proj/artifacts/asset_packages/ASSET_PACKAGE_INDEX.json').read_text())
    assert idx['assets']
    found_photo_reasoning=False
    for row in idx['assets']:
        d=Path(row['path']); names={p.name for p in d.iterdir()}
        assert FULL_ASSET_FILES <= names
        photo=json.loads((d/'03_photography_contract.json').read_text())
        if photo.get('asset_reasoning'):
            found_photo_reasoning=True
            assert photo['asset_reasoning'].get('causal_chain')
    assert found_photo_reasoning

    md=(tmp_path/'proj/artifacts/strategy/MASTER_STRATEGY_CN.md').read_text()
    assert 'Directional Switch Matrix' in md
    assert 'Holdout / Marginal Contribution' in md
    assert 'Asset-level Photography Causal WHY' in md
