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
    (pack/'test.yaml').write_text('''pack_id: test\nplatform_family: test_platform\nsite: "*"\nstatus: TEST_FIXTURE_VERIFIED\nsynthetic_for_test: true\ncapabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, CREATOR_AFFILIATE, PAID, CX, MEASUREMENT, COMPLIANCE]\nsurfaces: [PDP, GALLERY, FAQ, PAID_AD]\nrule_atoms: []\nresearch_required_for: []\n''')
    return pack

def test_v052_strategy_tools_flow_back_into_authority_and_assets(tmp_path):
    costs={'landed_cost':18,'platform_fee':{'type':'rate','value':0.1},'fulfillment':4,'affiliate_commission':{'type':'rate','value':0.1},'ad_cost':8,'tax':0,'refund_allowance':2}
    req={
      'project_id':'V052-INTEGRATION','sku':'S1','planning_only':True,
      'product':{'name':'Integration Serum','category':'serum','net_content':'30ml','primary_conversion_proposition':'Light daily hydration'},
      'sources':[{'source_id':'SRC-PRODUCT','kind':'TEST_FIXTURE'}],
      'claims':[{'claim_id':'CLM-1','claim':'Contains glycerin','status':'ACTIVE','evidence_level':'B','source_ids':['SRC-PRODUCT']}],
      'target':{'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY'],'surfaces':['GALLERY','PDP'],'currency':'MYR'},
      'market_rows':[
          {'seller_name':'A','selling_price':39,'sold':100,'gmv':3900,'pack':'30ml','rating':4.8,'review_count':120},
          {'seller_name':'B','selling_price':59,'sold':80,'gmv':4720,'pack':'30ml','rating':4.7,'review_count':90},
          {'seller_name':'C','selling_price':79,'sold':40,'gmv':3160,'pack':'2x30ml','rating':4.6,'review_count':60},
      ],
      'market_field_map':{'seller':'seller_name','price':'selling_price','units':'sold','revenue':'gmv','configuration':'pack','reviews':'review_count'},
      'market_keyword_rows':[
          {'term':'hydrating serum','volume':1000,'competition':0.6,'rank':8,'intent':'BENEFIT'},
          {'term':'30ml serum','volume':300,'competition':0.3,'rank':4,'intent':'SPECIFICATION'},
      ],
      'market_review_rows':[
          {'theme':'sticky feel','sentiment':'negative','competitor':'A','audience_segment':'humid-climate users','count':6,'text':'feels sticky in humid weather','source_id':'REV-A1'},
          {'theme':'sticky feel','sentiment':'negative','competitor':'B','audience_segment':'humid-climate users','count':4,'text':'too sticky for daytime','source_id':'REV-B1'},
          {'theme':'easy layering','sentiment':'positive','competitor':'C','audience_segment':'daily routine users','count':3,'text':'layers well under sunscreen','source_id':'REV-C1'},
      ],
      'offer_economics':{'currency':'MYR','scenarios':[
          {'scenario_id':'BASE','sku':'S1','price':59,'costs':costs,'minimum_contribution':8,'configuration':'30ml','include_sensitivity':True},
          {'scenario_id':'BUNDLE','sku':'S2','price':99,'costs':{**costs,'landed_cost':32,'fulfillment':6},'minimum_contribution':12,'configuration':'2x30ml','bundle':True},
      ],'demand_signals':{'S1':{'orders':120},'S2':{'retention':True}}},
      'listing_input':{'fields':{
          'title':'Integration Serum 30ml',
          'attributes':{'size':'30ml'},
          'highlights':['Light daily hydration'],
          '_objections':[{'objection':'What exactly is included?','category':'PACKAGE','source_ids':['SRC-PRODUCT']}],
          '_usage':['Use according to supplied product directions.'],
          '_package':['1 × 30ml bottle'],
          '_faq':[{'question':'What is included?','answer':'1 × 30ml bottle','source_ids':['SRC-PRODUCT']}],
          '_source_refs':{'title':['SRC-PRODUCT'],'attributes':['SRC-PRODUCT']},
          '_claim_refs':{'highlights':['CLM-1']},
      },'keywords':[{'term':'hydrating serum','cluster':'BENEFIT','volume':1000,'source_id':'KW1'}]},
      'ad_analysis':{'price':59,'costs':costs,'ad_data':{'impressions':10000,'clicks':180,'orders':12,'spend':300,'revenue':708},'thresholds':{'min_ctr':0.02}},
      'feedback_rows':[{'source':'review','category':'PACKAGE_CONFUSION','severity':'HIGH','text':'not clear what is included'}],
      'shopper_questions':['What is it?','Why is it relevant to me?','What evidence supports the choice?','How should I use it?'],
      'cmf':{'color':'truth-first','material':'packaging reference','finish':'preserve supplied finish'},
      'photography_contract':{'capture_mode':'REAL_PHOTO','camera':{'focal_length_mm':85,'camera_height':'product center','working_distance':'1m','focus_plane':'front label'},'composition':{'product_occupancy':{'height_pct':68}},'lighting':{'key':{'direction':'camera-left','modifier':'large diffusion'},'fill':'low soft fill','negative_fill':'camera-right flag','cct':5200,'highlight_policy':'protect label','reflection_control':'angle + flags'},'color_management':{'white_balance':'neutral reference','output_space':'sRGB','product_color_fidelity':'truth-first'}},
      'compile_assets':True
    }
    build_project(tmp_path/'proj',req,_pack(tmp_path))
    strategy=json.loads((tmp_path/'proj/artifacts/strategy/strategy_authority.json').read_text())
    market=strategy['sections']['03_platform_region_audience_culture_insight']['market']
    assert market['competitor_clusters'] and market['keyword_demand']['top_terms'] and market['opportunity_map'] is not None
    assert market['customer_voice']['theme_summary'][0]['theme']=='sticky feel'
    assert any(x.get('type')=='CUSTOMER_TENSION_ALIGNMENT' for x in market['opportunity_map'])
    core=strategy['sections']['04_marketing_core_strategy']
    assert core['product_strategy']['price_ladder_strategy']
    assert core['positioning']['value_proposition']['value_promise']=='Light daily hydration'
    assert core['listing_strategy']['objection_resolution_plan'][0]['recommended_field']=='package'
    assert core['listing_strategy']['field_content_plan']['package']
    visual=strategy['sections']['05_visual_photography_strategy']
    assert any(x['element']=='Focal Length' and x.get('why') for x in visual['photography_rationale'])
    assert all(a.get('surface_need') and a.get('business_hypothesis') for a in visual['asset_portfolio']['portfolio'])
    ctx=json.loads((tmp_path/'proj/artifacts/strategy_reasoning_context.json').read_text())
    assert ctx['authority_bindings']['04_marketing_core_strategy']
    assert any(x.get('authority_excerpt') for x in ctx['selected_prompts'])
    idx=json.loads((tmp_path/'proj/artifacts/asset_packages/ASSET_PACKAGE_INDEX.json').read_text())
    for row in idx['assets']:
        names={p.name for p in Path(row['path']).iterdir()}
        assert FULL_ASSET_FILES.issubset(names)
        trace=json.loads((Path(row['path'])/'11_strategy_authority_trace.json').read_text())
        assert trace['strategy_status']=='STRATEGY_AUTHORITY_COMPILED'
    md=(tmp_path/'proj/artifacts/strategy/MASTER_STRATEGY_CN.md').read_text()
    assert 'Shared Growth Budget' in md and 'Search Intent Architecture' in md and '摄影参数 WHY' in md and 'Business Hypothesis' in md and 'Customer Voice' in md
