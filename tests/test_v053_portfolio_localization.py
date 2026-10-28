from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project


def _pack(tmp_path):
    pack=tmp_path/'packs'; pack.mkdir()
    (pack/'test.yaml').write_text('''pack_id: test\nplatform_family: test_platform\nsite: "*"\nstatus: TEST_FIXTURE_VERIFIED\nsynthetic_for_test: true\ncapabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, CREATOR_AFFILIATE, PAID, CX, MEASUREMENT, COMPLIANCE]\nsurfaces: [PDP, GALLERY, FAQ, PAID_AD]\nrule_atoms: []\nresearch_required_for: []\n''')
    return pack


def test_v053_competitor_portfolio_transcreation_and_native_authoring(tmp_path):
    costs={'landed_cost':18,'platform_fee':{'type':'rate','value':0.1},'fulfillment':4,'affiliate_commission':{'type':'rate','value':0.08},'ad_cost':5,'tax':0,'refund_allowance':2}
    req={
      'project_id':'V053-INTEGRATION','planning_only':True,'sku':'S1',
      'product':{'name':'Portfolio Serum','category':'serum','net_content':'30ml','primary_conversion_proposition':'Light daily hydration'},
      'sources':[{'source_id':'SRC-1','kind':'TEST_FIXTURE'}],
      'claims':[{'claim_id':'CLM-1','claim':'Contains glycerin','status':'ACTIVE','evidence_level':'B','source_ids':['SRC-1']}],
      'target':{'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY','ms-MY'],'surfaces':['GALLERY','PDP'],'currency':'MYR'},
      # Intentionally no market_rows: supplemental competitor/search/review evidence must still compile.
      'market_keyword_rows':[{'term':'hydrating serum','volume':1000,'competition':0.4,'intent':'BENEFIT'}],
      'market_review_rows':[
          {'theme':'sticky feel','sentiment':'negative','competitor':'A','count':7,'source_id':'REV-A'},
          {'theme':'easy layering','sentiment':'positive','competitor':'B','count':4,'source_id':'REV-B'},
      ],
      'competitor_listing_rows':[
          {'competitor':'A','title':'A Hydrating Serum 30ml','message_theme':'sticky feel','offer_type':'single','proof_type':'ingredient callout','configuration':'30ml','surface':'PDP','locale':'en-MY','source_id':'LST-A'},
          {'competitor':'B','title':'B Daily Serum','message_theme':'daily hydration','offer_type':'bundle','proof_type':'rating','configuration':'2x30ml','surface':'PDP','locale':'en-MY','source_id':'LST-B'},
      ],
      'offer_economics':{'currency':'MYR','scenarios':[
          {'scenario_id':'TRIAL','sku':'S1','price':49,'costs':costs,'minimum_contribution':6,'configuration':'30ml','buyer_job':'try daily hydration','target_segment':'new users','channel':'shop','trial':True,'lifecycle_stage':'ACQUISITION'},
          {'scenario_id':'CORE','sku':'S2','price':55,'costs':{**costs,'landed_cost':20},'minimum_contribution':7,'configuration':'30ml','buyer_job':'try daily hydration','target_segment':'new users','channel':'shop','lifecycle_stage':'CONVERSION'},
          {'scenario_id':'BUNDLE','sku':'S3','price':99,'costs':{**costs,'landed_cost':34,'fulfillment':6},'minimum_contribution':12,'configuration':'2x30ml','buyer_job':'stock up','target_segment':'repeat users','channel':'shop','bundle':True,'lifecycle_stage':'RETENTION'},
      ],'demand_signals':{'S1':{'traffic':True},'S2':{'orders':120},'S3':{'retention':True}}},
      'listing_input':{'fields':{
          'title':'Portfolio Serum 30ml',
          'attributes':{'size':'30ml'},
          'highlights':['Light daily hydration'],
          '_localized_copy':{'ms-MY':{'title':'Portfolio Serum 30ml','highlights':['Hidrasi ringan harian']}},
          '_source_refs':{'title':['SRC-1'],'attributes':['SRC-1']},'_claim_refs':{'highlights':['CLM-1']}
      },'keywords':[{'term':'hydrating serum','cluster':'BENEFIT','volume':1000,'source_id':'KW-1'}]},
      'shopper_questions':['What is it?','Why is it relevant?','Why believe it?'],
      'cmf':{'color':'truth-first','material':'packaging','finish':'preserve'},
      'compile_assets':True,
    }
    build_project(tmp_path/'proj',req,_pack(tmp_path))
    strategy=json.loads((tmp_path/'proj/artifacts/strategy/strategy_authority.json').read_text())
    market=strategy['sections']['03_platform_region_audience_culture_insight']['market']
    ci=market['competitor_listing_intelligence']
    assert ci['status']=='AGGREGATED_FROM_SUPPLIED_LISTING_FIELDS'
    assert ci['competitors'][0]['competitor'] in {'A','B'}
    assert any(x['competitor']=='A' and x['theme']=='sticky feel' for x in ci['message_review_overlap'])
    core=strategy['sections']['04_marketing_core_strategy']
    sku=core['product_strategy']
    assert sku['portfolio_interactions']['pairs']
    pair=next(x for x in sku['portfolio_interactions']['pairs'] if {x['sku_a'],x['sku_b']}=={'S1','S2'})
    assert pair['overlap_signal_strength'] in {'MEDIUM','HIGH'}
    assert sku['trade_up_architecture'][-1]['sku']=='S3'
    assert sku['lifecycle_offer_map'][-1]['lifecycle_stage']=='RETENTION'
    listing=core['listing_strategy']
    assert listing['transcreation_task_matrix']['status']=='TRANSCREATION_TASKS_COMPILED'
    assert {'en-MY','ms-MY'}==set(listing['transcreation_task_matrix']['locales'])
    assert listing['localized_copy_audit']['status']=='AUDITED_SUPPLIED_LOCAL_COPY'
    content=strategy['sections']['06_platform_content_matrix']
    assert content and all('local_authoring_tasks' in x and 'beat_plan' in x and 'copy_contract' in x for x in content)
    assert all({'en-MY','ms-MY'}==set(x['visible_copy_locales']) for x in content)
    ctx=json.loads((tmp_path/'proj/artifacts/strategy_reasoning_context.json').read_text())
    ids={x['id'] for x in ctx['selected_prompts']}
    assert {'PROMPT-COMPETITOR-INTEL','PROMPT-PORTFOLIO-STRATEGY','PROMPT-TRANScreation-AUTHORING'} <= ids
    md=(tmp_path/'proj/artifacts/strategy/MASTER_STRATEGY_CN.md').read_text()
    assert 'Competitor Listing × Review Intelligence' in md
    assert 'SKU Cannibalization / Overlap Hypotheses' in md
    assert 'Locale × Field Transcreation Tasks' in md
