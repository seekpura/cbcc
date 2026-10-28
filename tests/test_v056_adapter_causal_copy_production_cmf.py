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
    (pack/'test.yaml').write_text('''pack_id: test\nplatform_family: tiktok_shop\nsite: "*"\nstatus: TEST_FIXTURE_VERIFIED\nsynthetic_for_test: true\ncapabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, CREATOR_AFFILIATE, PAID, CX, MEASUREMENT, COMPLIANCE]\nsurfaces: [SEARCH_RESULTS, PDP, GALLERY, PDP_VIDEO, CREATOR, LIVE, PAID_AD, FAQ]\nrule_atoms: []\nresearch_required_for: []\n''')
    return pack

def test_v056_incremental_adapter_experiment_host_copy_surface_and_cmf(tmp_path):
    first=compile_source_adapters([{
        'adapter_id':'COMPETITOR-SNAPSHOT','dataset':'market_rows','refresh_mode':'FULL_SNAPSHOT','primary_key':'listing_id','updated_at_field':'observed_at','source_id':'M1',
        'rows':[{'listing_id':'A','seller':'Seller A','price':49,'units':100,'revenue':4900,'configuration':'30ml','observed_at':'2026-10-20'}]
    }])
    prev=first['refresh_state']
    req={
      'project_id':'V056','planning_only':True,'sku':'S1',
      'product':{'name':'Glass Serum','category':'serum','net_content':'30ml','primary_conversion_proposition':'Light daily hydration'},
      'sources':[{'source_id':'SRC-PROD','kind':'PRODUCT_TRUTH'}],
      'claims':[{'claim_id':'CLM-1','claim':'Contains glycerin','status':'ACTIVE','evidence_level':'B','source_ids':['SRC-PROD']}],
      'target':{'market':'MY','jurisdiction':'MY','platform_family':'tiktok_shop','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY','ms-MY'],'surfaces':['SEARCH_RESULTS','PDP','GALLERY','PDP_VIDEO'],'currency':'MYR','category':'beauty'},
      'platform_content_targets':[{'market':'MY','site':'TEST','platform_family':'tiktok_shop','primary_locale':'ms-MY','visible_copy_locales':['ms-MY','en-MY'],'surface_production_overrides':{'TikTok Shop Gallery / PDP':{'working_canvas':'project-defined mobile master'}}}],
      'research_adapter_previous_state':prev,
      'research_source_adapters':[
        {'adapter_id':'COMPETITOR-SNAPSHOT','dataset':'market_rows','refresh_mode':'INCREMENTAL_BATCH','primary_key':'listing_id','updated_at_field':'observed_at','source_id':'M1','source_record':{'source_id':'M1','kind':'MARKET_SNAPSHOT','observed_at':'2026-10-27','market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty','max_age_days':14,'sample_frame':'named competitor set','sampling_method':'host export','population_scope':'supplied competitors','inclusion_criteria':'active supplied rows'},'rows':[{'listing_id':'A','seller':'Seller A','price':50,'units':110,'revenue':5500,'configuration':'30ml','observed_at':'2026-10-27'},{'listing_id':'B','seller':'Seller B','price':59,'units':60,'revenue':3540,'configuration':'30ml','observed_at':'2026-10-27'}]},
        {'adapter_id':'REVIEWS','dataset':'market_review_rows','refresh_mode':'FULL_SNAPSHOT','primary_key':'review_id','source_id':'R1','semantic_duplicate_fields':['text'],'semantic_duplicate_threshold':0.8,'source_record':{'source_id':'R1','kind':'REVIEW_EXPORT','observed_at':'2026-10-26','market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty','max_age_days':30,'sample_frame':'supplied reviews','sampling_method':'host export','population_scope':'supplied reviews','inclusion_criteria':'reviews in export'},'rows':[{'review_id':'r1','theme':'sticky','sentiment':'negative','text':'Feels sticky on humid days'},{'review_id':'r2','theme':'sticky','sentiment':'negative','text':'Feels sticky on humid days!'}]},
      ],
      'market_field_map':{'seller':'seller','price':'price','units':'units','revenue':'revenue','configuration':'configuration'},
      'market_research_as_of':'2026-10-27','market_research_scope':{'market':'MY','site':'TEST','platform_family':'tiktok_shop','category':'beauty'},
      'offer_economics':{'currency':'MYR','scenarios':[{'scenario_id':'CORE','sku':'S1','price':50,'costs':{'landed_cost':18,'platform_fee':{'type':'rate','value':0.1},'fulfillment':4,'affiliate_commission':{'type':'rate','value':0.08},'ad_cost':4,'tax':0,'refund_allowance':2},'minimum_contribution':6}]},
      'listing_input':{'fields':{
        'title':'Glass Serum 30ml','attributes':{'size':'30ml'},'highlights':['Light daily hydration'],
        '_localized_copy':{'en-MY':{'title':'Glass Serum 30ml','attributes':{'size':'30ml'},'highlights':['Light daily hydration']},'ms-MY':{'title':'Serum Kaca 30ml','attributes':{'size':'30ml'},'highlights':['Hidrasi ringan harian']}},
        '_localized_copy_history':[{'locale':'ms-MY','field':'title','version_id':'MS-T-V1','copy':'Serum Kaca 30ml','created_at':'2026-10-20'}],
        '_localized_copy_reviews':[{'locale':'ms-MY','field':'title','version_id':'MS-T-V1','decision':'APPROVED','native_fluency':'PASS','claim_equivalence':'PASS','platform_fit':'PASS','culture_fit':'PASS'}],
        '_source_refs':{'title':['SRC-PROD'],'attributes':['SRC-PROD']},'_claim_refs':{'highlights':['CLM-1']},
      },'host_authoring_responses':[{'locale':'ms-MY','field':'title','task_type':'REVISE','task_id':'REV-1','version_id':'MS-T-V2','parent_version_id':'MS-T-V1','copy':'Serum Ringan 30ml','author':'HOST-MODEL'}]},
      'experiment':{'assignment_unit':'user','randomized':True,'baseline_rate':0.10,'absolute_mde':0.02,'target_power':0.8,'alpha':0.05,'contamination_rate':0.02,'spillover_rate':0.01,'interference_risk':'LOW','pre_period_metrics':[{'metric':'pre_conversion','treatment_mean':0.101,'control_mean':0.10,'treatment_sd':0.30,'control_sd':0.30}], 'control_success':100,'control_total':1000,'test_success':125,'test_total':1000,'segments':[{'segment':'new','control_success':60,'control_total':600,'test_success':80,'test_total':600}]},
      'shopper_questions':['What is it?','Why is it relevant?','Why believe it?'],
      'cmf':{'color':'clear bottle / neutral label','material':'clear glass bottle','finish':'gloss glass + matte paper label','surface_behavior':{'bottle':'specular transparent','label':'diffuse matte'}},
      'photography_contract':{'capture_mode':'REAL_PHOTO','camera':{'focal_length_mm':85,'camera_height':'product center','working_distance':'1m','focus_plane':'front label','yaw':0,'pitch':0,'roll':0,'aperture':'f/8','dof':'full front label legible'},'composition':{'product_occupancy':{'height_pct':68},'shot_size':'product hero'},'lighting':{'key':{'direction':'camera-left 45deg','modifier':'large diffusion'},'fill':'low soft fill','negative_fill':'camera-right flag','rim':'subtle edge separation','cct':5200,'white_balance':'neutral reference','shadow_policy':'soft grounding shadow','highlight_policy':'protect label','reflection_control':'flags + angle + conditional polarization'},'color_management':{'white_balance':'neutral reference','output_space':'sRGB','product_color_fidelity':'truth-first'}},
      'compile_assets':True,
    }
    build_project(tmp_path/'proj',req,_pack(tmp_path))
    adapter=json.loads((tmp_path/'proj/artifacts/research_source_adapter_refresh.json').read_text())
    comp=next(x for x in adapter['adapters'] if x['adapter_id']=='COMPETITOR-SNAPSHOT')
    assert 'A' in comp['change_set']['changed'] and 'B' in comp['change_set']['added']
    rev=next(x for x in adapter['adapters'] if x['adapter_id']=='REVIEWS')
    assert rev['semantic_near_duplicate_review'] and rev['semantic_near_duplicate_review'][0]['decision']=='REPORT_ONLY_NEVER_AUTO_DELETE'
    market=json.loads((tmp_path/'proj/artifacts/market_analysis.json').read_text())
    assert market['normalization']['row_count']==2
    exp=json.loads((tmp_path/'proj/artifacts/experiment_analysis.json').read_text())
    assert exp['design_review']['power_plan']['approx_required_n_per_arm']>0
    assert exp['design_review']['design_readiness']=='DESIGN_REVIEW_READY'
    assert exp['segments'][0]['segment']=='new'
    listing=json.loads((tmp_path/'proj/artifacts/listing_analysis.json').read_text())['compiled']
    title=next(x for pkg in listing['final_copy_workflow']['packages'] if pkg['locale']=='ms-MY' for x in pkg['fields'] if x['field']=='title')
    assert title['current_version_id']=='MS-T-V2' and title['review_version_id']=='MS-T-V1'
    assert title['release_status']=='REVIEW_STALE_AFTER_REVISION'
    assert listing['host_authoring_apply']['applied'][0]['version_id']=='MS-T-V2'
    strategy=json.loads((tmp_path/'proj/artifacts/strategy/strategy_authority.json').read_text())
    assert len(strategy['sections'])==9
    assert strategy['runtime_strategy_depth'].startswith(('0.5.6-','0.5.7-','0.5.8-','0.5.9-','0.5.10-','0.5.11-','0.5.12-','0.5.13-','0.5.14-'))
    market_s=strategy['sections']['03_platform_region_audience_culture_insight']['market']
    assert market_s['source_adapter_refresh']['status']=='SOURCE_ADAPTERS_COMPILED'
    rows=strategy['sections']['06_platform_content_matrix']
    assert rows and all(r.get('surface_production_contract') for r in rows)
    vis=strategy['sections']['05_visual_photography_strategy']
    assert 'refraction' in ' '.join(vis['material_lighting_profile']['optical_risks']).lower()
    assert all(x.get('shot_lighting_reasoning') for x in vis['asset_parameter_reasoning'])
    asset_root=tmp_path/'proj/artifacts/asset_packages'
    index=json.loads((asset_root/'ASSET_PACKAGE_INDEX.json').read_text())
    assert len(index['assets'])==3
    for row in index['assets']:
        d=asset_root/row['asset_id']
        assert FULL_ASSET_FILES.issubset({x.name for x in d.iterdir()})
        notes=(d/'09_production_notes.md').read_text()
        assert 'Surface Production Contract' in notes
        photo=json.loads((d/'03_photography_contract.json').read_text())
        if photo.get('asset_reasoning'):
            assert photo['asset_reasoning']['shot_lighting_reasoning']['truth_boundary']
    ctx=json.loads((tmp_path/'proj/artifacts/strategy_reasoning_context.json').read_text())
    ids={x['id'] for x in ctx['selected_prompts']}
    assert {'PROMPT-SOURCE-ADAPTERS','PROMPT-CAUSAL-EXPERIMENT','PROMPT-HOST-COPY','PROMPT-SURFACE-PRODUCTION','PROMPT-CMF-LIGHTING'}.issubset(ids)
