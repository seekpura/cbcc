from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project
from cbcc.tools.source_adapters import compile_source_adapters

FULL_ASSET_FILES={
'00_asset_manifest.yaml','01_strategy.md','02_visual_spec.md','03_photography_contract.json','04_layout_contract.json','05_prompt_CN.txt','06_prompt_EN.txt','07_generation_guidance.txt','08_copy.md','09_production_notes.md','10_source_trace.md','11_strategy_authority_trace.json'}

def _pack(tmp_path):
    pack=tmp_path/'packs'; pack.mkdir()
    (pack/'test.yaml').write_text('''pack_id: tiktok_shop_my_test_v057\nplatform_family: tiktok_shop\nsite: "*"\nstatus: TEST_FIXTURE_VERIFIED\nsynthetic_for_test: true\ncapabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, CREATOR_AFFILIATE, PAID, CX, MEASUREMENT, COMPLIANCE]\nsurfaces: [SEARCH_RESULTS, PDP, GALLERY, PDP_VIDEO, CREATOR, LIVE, PAID_AD, FAQ]\nrule_atoms: []\nresearch_required_for: []\n''')
    return pack

def test_v057_cursor_advanced_causal_terminology_provider_binding_and_prelight(tmp_path):
    first=compile_source_adapters([{
        'adapter_id':'MARKET-SNAP','adapter_family':'MARKET_SNAPSHOT','refresh_mode':'FULL_SNAPSHOT','primary_key':'listing_id','cursor_field':'observed_at','updated_at_field':'observed_at','source_id':'M1',
        'rows':[{'listing_id':'A','seller':'Seller A','price':49,'units':100,'revenue':4900,'configuration':'30ml','observed_at':'2026-10-20'}]
    }])
    prev=first['refresh_state']
    req={
      'project_id':'V057','planning_only':True,'sku':'S1',
      'product':{'name':'Glass Serum','category':'serum','net_content':'30ml','primary_conversion_proposition':'Light daily hydration'},
      'sources':[{'source_id':'SRC-PROD','kind':'PRODUCT_TRUTH'}],
      'claims':[{'claim_id':'CLM-1','claim':'Contains glycerin','status':'ACTIVE','evidence_level':'B','source_ids':['SRC-PROD']}],
      'target':{'market':'MY','jurisdiction':'MY','platform_family':'tiktok_shop','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY','ms-MY'],'surfaces':['SEARCH_RESULTS','PDP','GALLERY','PDP_VIDEO'],'currency':'MYR','category':'beauty'},
      'platform_content_targets':[{'market':'MY','site':'TEST','platform_family':'tiktok_shop','primary_locale':'ms-MY','visible_copy_locales':['ms-MY','en-MY']}],
      'research_adapter_previous_state':prev,
      'research_source_adapters':[
        {'adapter_id':'MARKET-SNAP','adapter_family':'MARKET_SNAPSHOT','refresh_mode':'INCREMENTAL_BATCH','primary_key':'listing_id','cursor_field':'observed_at','updated_at_field':'observed_at','source_id':'M1','batch_id':'B2','has_more':False,'source_record':{'source_id':'M1','kind':'MARKET_SNAPSHOT','observed_at':'2026-10-27','market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty','max_age_days':14,'sample_frame':'named competitor set','sampling_method':'host export','population_scope':'supplied competitors','inclusion_criteria':'active supplied rows'},'rows':[{'listing_id':'A','seller':'Seller A','price':50,'units':110,'revenue':5500,'configuration':'30ml','observed_at':'2026-10-27'},{'listing_id':'B','seller':'Seller B','price':59,'units':60,'revenue':3540,'configuration':'30ml','observed_at':'2026-10-27'}]},
        {'adapter_id':'SEARCH','adapter_family':'SEARCH_DEMAND','refresh_mode':'FULL_SNAPSHOT','primary_key':'term','source_id':'K1','rows':[{'term':'serum ringan','volume':1000,'competition':20,'cluster':'CORE'}]},
        {'adapter_id':'REVIEWS','adapter_family':'REVIEW_VOICE','refresh_mode':'FULL_SNAPSHOT','primary_key':'review_id','source_id':'R1','semantic_duplicate_fields':['text'],'rows':[{'review_id':'r1','theme':'sticky','sentiment':'negative','text':'Feels sticky on humid days'}]},
      ],
      'market_field_map':{'seller':'seller','price':'price','units':'units','revenue':'revenue','configuration':'configuration'},
      'market_research_as_of':'2026-10-27','market_research_scope':{'market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty'},
      'offer_economics':{'currency':'MYR','scenarios':[{'scenario_id':'CORE','sku':'S1','price':50,'costs':{'landed_cost':18,'platform_fee':{'type':'rate','value':0.1},'fulfillment':4,'affiliate_commission':{'type':'rate','value':0.08},'ad_cost':4,'tax':0,'refund_allowance':2},'minimum_contribution':6}]},
      'listing_input':{
        'terminology_memory':[{'locale':'ms-MY','term_id':'TERM-PRODUCT','concept':'product_name','canonical':'Serum Kaca','allowed_variants':['Serum Glass'],'consistency_mode':'CANONICAL_ONLY','required_in_fields':['title']}],
        'fields':{
          'title':'Glass Serum 30ml','highlights':['Light daily hydration'],
          '_localized_copy':{'en-MY':{'title':'Glass Serum 30ml','highlights':['Light daily hydration']},'ms-MY':{'title':'Serum Kaca 30ml','highlights':['Serum Glass untuk hidrasi ringan']}},
          '_localized_copy_reviews':[{'locale':'ms-MY','field':'title','decision':'APPROVED','native_fluency':'PASS','claim_equivalence':'PASS','platform_fit':'PASS','culture_fit':'PASS'},{'locale':'ms-MY','field':'highlights','decision':'APPROVED','native_fluency':'PASS','claim_equivalence':'PASS','platform_fit':'PASS','culture_fit':'PASS'}],
          '_source_refs':{'title':['SRC-PROD']},'_claim_refs':{'highlights':['CLM-1']},
        }
      },
      'experiment':{
        'assignment_unit':'store','randomized':True,'baseline_rate':0.10,'absolute_mde':0.02,'target_power':0.8,'alpha':0.05,
        'control_success':100,'control_total':1000,'test_success':130,'test_total':1000,
        'cluster_design':{'cluster_id_field':'store_id','avg_cluster_size':20,'icc':0.05,'clusters_per_arm':25},
        'geo_design':{'pairs':[{'treatment_geo':'KL','control_geo':'PJ','treatment_pre':100,'control_pre':96}]},
        'cuped':{'pre_metric':'pre_orders','outcome_metric':'orders','pre_outcome_correlation':0.6,'pre_period_frozen_before_outcome':True},
        'sequential':{'planned_looks':4,'current_look':2,'method':'BONFERRONI_CONSERVATIVE'},
      },
      'shopper_questions':['What is it?','Why is it relevant?','Why believe it?'],
      'cmf':{'color':'clear bottle / neutral label','material':'clear glass bottle','finish':'gloss glass + matte paper label','surface_behavior':{'bottle':'specular transparent','label':'diffuse matte'}},
      'photography_contract':{'capture_mode':'REAL_PHOTO','camera':{'focal_length_mm':85,'camera_height':'product center','working_distance':'1m','focus_plane':'front label','yaw':0,'pitch':0,'roll':0,'aperture':'f/8','dof':'full front label legible'},'composition':{'product_occupancy':{'height_pct':68},'shot_size':'product hero'},'lighting':{'key':{'direction':'camera-left 45deg','modifier':'large diffusion'},'fill':'low soft fill','negative_fill':'camera-right flag','rim':'subtle edge separation','cct':5200,'white_balance':'neutral reference','shadow_policy':'soft grounding shadow','highlight_policy':'protect label','reflection_control':'flags + angle + conditional polarization'},'color_management':{'white_balance':'neutral reference','output_space':'sRGB','product_color_fidelity':'truth-first'}},
      'compile_assets':True,
      'production_run':{'asset_ids':[]},
    }
    build_project(tmp_path/'proj',req,_pack(tmp_path))
    adapter=json.loads((tmp_path/'proj/artifacts/research_source_adapter_refresh.json').read_text())
    snap=next(x for x in adapter['adapters'] if x['adapter_id']=='MARKET-SNAP')
    assert snap['adapter_family']=='MARKET_SNAPSHOT'
    assert snap['checkpoint']['previous_cursor']=='2026-10-20'
    assert snap['checkpoint']['next_cursor']=='2026-10-27'
    assert 'A' in snap['change_set']['changed'] and 'B' in snap['change_set']['added']
    search=next(x for x in adapter['adapters'] if x['adapter_id']=='SEARCH')
    assert search['dataset']=='market_keyword_rows'

    exp=json.loads((tmp_path/'proj/artifacts/experiment_analysis.json').read_text())
    adv=exp['advanced_design_review']
    assert adv['cluster']['design_effect']>1
    assert adv['geo']['comparable_pair_count']==1
    assert adv['cuped']['approx_variance_reduction']==0.36
    assert adv['sequential']['conservative_alpha_per_look']==0.0125

    listing=json.loads((tmp_path/'proj/artifacts/listing_analysis.json').read_text())['compiled']
    ta=listing['terminology_memory_audit']
    assert ta['blocking_issue_count']==1
    ms=next(x for x in listing['final_copy_workflow']['packages'] if x['locale']=='ms-MY')
    assert any(x['release_status']=='BLOCKED_HARD_CONSTRAINT' for x in ms['fields'])
    host_req=json.loads((tmp_path/'proj/artifacts/listing_copy_host_authoring_requests.json').read_text())
    assert host_req['terminology_memory'][0]['canonical']=='Serum Kaca'

    strategy=json.loads((tmp_path/'proj/artifacts/strategy/strategy_authority.json').read_text())
    assert len(strategy['sections'])==9
    assert strategy['runtime_strategy_depth'].startswith(('0.5.7-','0.5.8-','0.5.9-','0.5.10-','0.5.11-','0.5.12-','0.5.13-','0.5.14-'))
    market=strategy['sections']['03_platform_region_audience_culture_insight']['market']
    assert market['source_adapter_refresh']['adapters'][0]['checkpoint']['next_cursor']=='2026-10-27'
    listing_s=strategy['sections']['04_marketing_core_strategy']['listing_strategy']
    assert listing_s['terminology_memory_audit']['blocking_issue_count']==1
    visual=strategy['sections']['05_visual_photography_strategy']
    mlp=visual['material_lighting_profile']
    assert mlp['prelight_plan']['frames']
    assert mlp['lighting_diagram']['key']
    assert mlp['exposure_ratio_plan']['status']=='MEASURE_IN_PRELIGHT'
    assert mlp['polarization_plan']['applicable']=='CONDITIONAL_TEST'
    assert mlp['color_consistency_plan']['capture_rule']
    rows=strategy['sections']['06_platform_content_matrix']
    assert rows and rows[0]['platform_pack_binding']['pack_id']=='tiktok_shop_my_test_v057'
    assert rows[0]['surface_production_contract']['platform_pack_binding']['pack_id']=='tiktok_shop_my_test_v057'

    asset_root=tmp_path/'proj/artifacts/asset_packages'
    index=json.loads((asset_root/'ASSET_PACKAGE_INDEX.json').read_text())
    assert len(index['assets'])==3
    for row in index['assets']:
        d=asset_root/row['asset_id']
        assert FULL_ASSET_FILES.issubset({x.name for x in d.iterdir()})
        photo=json.loads((d/'03_photography_contract.json').read_text())
        if photo.get('asset_reasoning'):
            sr=photo['asset_reasoning']['shot_lighting_reasoning']
            assert sr['prelight_plan'] and sr['lighting_diagram'] and sr['color_consistency_plan']

    run=json.loads((tmp_path/'proj/artifacts/production_run.json').read_text())
    assert run['assets']
    job_index=json.loads((tmp_path/'proj/artifacts/provider_jobs/PROVIDER_JOB_INDEX.json').read_text())
    assert job_index['job_count']==0
    assert len(run.get('preflight_holds') or [])==3
    assert all('REAL_PRODUCT_MASTER_NOT_BOUND' in x.get('errors',[]) for x in run.get('preflight_holds') or [])
    bind=run['assets'][0]['production_contract_binding']
    assert bind['layout_contract_hash'] and bind['photography_contract_hash']
    assert bind['platform_pack_bindings'][0]['pack_id']=='tiktok_shop_my_test_v057'
    assert bind['shot_lighting_reasoning']['prelight_plan']

    ctx=json.loads((tmp_path/'proj/artifacts/strategy_reasoning_context.json').read_text())
    ids={x['id'] for x in ctx['selected_prompts']}
    assert {'PROMPT-ADAPTER-CURSOR','PROMPT-ADVANCED-CAUSAL','PROMPT-TERMINOLOGY-MEMORY','PROMPT-PRODUCTION-BINDING','PROMPT-PRELIGHT-COLOR'}.issubset(ids)
