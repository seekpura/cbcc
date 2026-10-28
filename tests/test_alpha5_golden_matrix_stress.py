from pathlib import Path
import sys,json,random
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project
from cbcc.tools.market import analyze_market
from cbcc.asset_architecture import build_asset_architecture
from cbcc.tools.listing import compile_listing


def base_request(project_id, platform_family, site, market, category, surfaces, locale='en-US'):
    return {
      'project_id':project_id,
      'sku':'SKU-1',
      'product':{'name':f'{category.title()} Test Product','capacity':'500 ml','material':'verified material'},
      'claims':[],
      'sources':[{'source_id':'SRC-1','kind':'PRODUCT_SOURCE'}],
      'target':{'target_id':'T1','market':market,'jurisdiction':market,'platform_family':platform_family,'site':site,'program':None,'surfaces':surfaces,'category':category,'primary_locale':locale,'visible_copy_locales':[locale]},
      'shopper_questions':['What is it?','Why choose it?','What should I verify?'],
      'audience_culture':{'statements':[{'statement':'Use the supplied local-language context when available.','status':'ASSUMPTION','source_ids':[],'implications':[]}]},
      'cmf':{'color':'truth-bound product color','material':'verified product material','finish':'truth-bound finish'},
      'creative_directions':[{'direction_id':'TRUTH_FIRST','product_fit':5,'audience_fit':4,'platform_fit':5,'culture_fit':4,'differentiation':4,'production_feasibility':5,'decision':'SELECT'}],
      'compile_assets':True,
      'planning_only':False,
    }


def test_multi_category_golden_matrix(tmp_path):
    cases=[
      base_request('AMZ-ELEC','amazon','US','United States','electronics',['SEARCH_RESULTS','PDP','GALLERY'],'en-US'),
      base_request('NOON-HOME','noon','AE','United Arab Emirates','home',['GALLERY'],'en-AE'),
      base_request('SHOPEE-FOOD','shopee','MY','Malaysia','food',['PDP'],'en-MY'),
    ]
    for i,req in enumerate(cases):
        proj=tmp_path/f'p{i}'; out=build_project(proj,req,ROOT/'platform_packs')
        assert out['gates']['PLATFORM_COMPILE']['status']=='READY_REVIEW'
        assert (proj/'.cbcc/review/index.html').exists()
        arch=json.loads((proj/'artifacts/asset_architecture.json').read_text(encoding='utf-8'))
        assert arch['fixed_count_authority'] is False
        comp=json.loads((proj/'artifacts/asset_compile.json').read_text(encoding='utf-8'))
        assert comp['validation']['pass']


def test_market_engine_large_input_is_deterministic_and_complete():
    rows=[]
    for i in range(1500):
        price=10+(i%60)*2
        units=(i%17)+1
        rows.append({'seller':f'S{i%80}','price':price,'units':units,'revenue':price*units,'configuration':f'C{i%8}'})
    a=analyze_market(rows,10,'configuration'); b=analyze_market(rows,10,'configuration')
    assert a==b and a['row_count']==1500
    assert a['concentration']['seller_count']==80 and len(a['configuration'])==8 and len(a['price_bands'])>5


def test_asset_architecture_deduplicates_repeated_decision_jobs_without_target_count():
    jobs=[]
    for i in range(100):
        jobs.append({'consumer_question':f'Question {i%10}','surface':'GALLERY','family':'VISUAL','strategic_job':'Resolve'})
    out=build_asset_architecture('P',{'target_id':'T'},[f'Question {i}' for i in range(10)],[],jobs)
    assert out['asset_count']==10 and out['fixed_count_authority'] is False


def test_listing_stress_honors_current_title_contract():
    fields={'title':'A'*76,'_source_refs':{'title':['SRC-1']}}
    out=compile_listing(fields,{},[],{'title':{'required':True,'max_chars':75}}, {'visible_copy_locales':['en-US']}, [])
    assert out['pass'] is False and any('76>75' in x for x in out['checks']['title']['issues'])
