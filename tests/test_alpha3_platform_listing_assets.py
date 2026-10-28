from pathlib import Path
import json,sys,yaml
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.platform import PlatformCompiler
from cbcc.tools.listing import compile_listing
from cbcc.asset_architecture import build_asset_architecture
from cbcc.asset_compiler import compile_asset_packages
from cbcc.culture import compile_culture_context
from cbcc.locale import compile_language_profiles, typography_profile
from cbcc.compiler import build_project


def test_exact_platform_pack_scopes_rules_and_business_caps(tmp_path):
    pack=tmp_path/'packs'; pack.mkdir()
    (pack/'x.yaml').write_text('''pack_id: x\nplatform_family: p\nsite: MY\nprogram: cross_border\nstatus: VERIFIED\ncapabilities: [LISTING, VISUAL]\nbusiness_capabilities: {affiliate: true}\nsurfaces: [PDP, GALLERY]\nrule_atoms:\n- rule_id: TITLE\n  scope: {site: MY, category: beauty, surface: PDP}\n  statement: test\n  source_url: fixture://x\n  verified_at: '2026-01-01'\n  expires_at: '2099-01-01'\n  authority: TEST_FIXTURE\n  payload: {listing_field: title, constraints: {required: true, max_chars: 80}}\nresearch_required_for: []\n''')
    out=PlatformCompiler(pack).compile({'platform_family':'p','site':'MY','program':'cross_border','category':'beauty','surfaces':['PDP'],'primary_locale':'en-MY'},['TITLE'])
    assert out['resolution']=='EXACT' and out['status']=='VERIFIED_FOR_REQUEST'
    assert out['business_capabilities']['affiliate'] is True
    assert out['rules'][0]['payload']['listing_field']=='title'
    assert out['submission_readiness']=='ASSESSED'


def test_family_pack_never_establishes_submission_readiness(tmp_path):
    pack=tmp_path/'packs'; pack.mkdir()
    (pack/'x.yaml').write_text('''pack_id: generic\nplatform_family: p\nsite: '*'\nstatus: FAMILY_PLANNING_ONLY\ncapabilities: [LISTING]\nsurfaces: [PDP]\nrule_atoms: []\nresearch_required_for: [SUBMISSION_RULES]\n''')
    out=PlatformCompiler(pack).compile({'platform_family':'p','site':'ZZ','program':None,'category':'x','surfaces':['PDP'],'primary_locale':'en-US'},[])
    assert out['resolution']=='FAMILY' and out['status']=='FAMILY_PLANNING_ONLY'
    assert out['submission_readiness']=='NOT_ESTABLISHED'


def test_listing_field_contract_and_keyword_priority():
    fields={'title':'Product 30g','_source_refs':{'title':['S1']}}
    rules={'title':{'required':True,'max_chars':20}}
    out=compile_listing(fields,{'net':'30g'},[],rules,{'visible_copy_locales':['en-MY']},[{'term':'core','cluster':'CORE','priority':9},{'term':'long','cluster':'CORE','priority':1}])
    assert out['pass']
    assert out['field_contracts'][0]['visible_copy_locales']==['en-MY']
    assert out['keywords']['clusters']['CORE'][0]['term']=='core'


def test_dynamic_asset_architecture_merges_duplicate_jobs_and_has_no_fixed_count():
    target={'target_id':'T1'}
    jobs=[{'consumer_question':'What is it?','surface':'GALLERY','family':'VISUAL','source_ids':['S1']},{'consumer_question':'What is it?','surface':'GALLERY','family':'VISUAL','source_ids':['S2']},{'consumer_question':'How use?','surface':'FAQ','family':'CX'}]
    out=build_asset_architecture('P',target,[],[],jobs)
    assert out['fixed_count_authority'] is False and out['asset_count']==2
    assert set(out['assets'][0]['source_ids'])=={'S1','S2'}


def test_locale_profiles_and_culture_are_evidence_bounded():
    c=compile_culture_context({'statements':[{'statement':'x','status':'VERIFIED','source_ids':['S']}],'intersectionality':{'ethnicity':['multi-ethnic']}})
    assert c['status']=='COMPILED_FROM_SUPPLIED_EVIDENCE' and c['statements'][0]['source_ids']==['S']
    assert typography_profile('ar-AE')['direction']=='RTL'
    p=compile_language_profiles('en-MY',['ms-MY'],['en-MY','ms-MY'])
    assert len(p['profiles'])==2 and all(x['script']=='LATN' for x in p['profiles'])


def test_kiyuu_alpha3_compiles_asset_packages(tmp_path):
    fx=ROOT/'tests/fixtures/kiyuu_my_tiktok'; req=json.loads((fx/'request.json').read_text(encoding='utf-8'))
    out=build_project(tmp_path/'proj',req,fx)
    assert out['gates']['CULTURE_CONTEXT']['status']=='READY_REVIEW'
    assert out['gates']['ASSET_ARCHITECTURE']['status']=='READY_REVIEW'
    assert out['gates']['ASSET_COMPILE']['status']=='READY_REVIEW'
    arch=json.loads((tmp_path/'proj/artifacts/asset_architecture.json').read_text(encoding='utf-8'))
    assert arch['asset_count']==3 and arch['fixed_count_authority'] is False
    idx=json.loads((tmp_path/'proj/artifacts/asset_packages/ASSET_PACKAGE_INDEX.json').read_text(encoding='utf-8'))
    assert idx['count']==3
    first=tmp_path/'proj/artifacts/asset_packages'/arch['assets'][0]['asset_id']
    assert (first/'05_prompt_CN.txt').exists() and (first/'10_source_trace.md').exists()
    txt=(first/'05_prompt_CN.txt').read_text(encoding='utf-8')
    assert '真实产品' in txt and '消费者问题' in txt
    culture=json.loads((tmp_path/'proj/artifacts/culture_context.json').read_text(encoding='utf-8'))
    assert culture['language_profiles']['profiles'][0]['locale']=='en-MY'
    pc=json.loads((tmp_path/'proj/artifacts/platform_compile.json').read_text(encoding='utf-8'))
    assert pc['business_capabilities']['affiliate'] is True
    listing=json.loads((tmp_path/'proj/artifacts/listing_analysis.json').read_text(encoding='utf-8'))
    title_contract=next(x for x in listing['field_contracts'] if x['field']=='title')
    assert title_contract['max_chars']==80

def test_production_provider_routing_is_explicit_contract():
    from cbcc.providers import route_production
    x=route_production({'asset_id':'A','production_mode':'REAL_PHOTO'})
    assert x['provider']=='HUMAN_PHOTOGRAPHY' and x['execution_authorized'] is False
    y=route_production({'asset_id':'B','production_mode':'AI_GENERATIVE'},{'AI_GENERATIVE':'EPV_ADAPTER'})
    assert y['provider']=='EPV_ADAPTER'

def test_asset_package_validator_and_prompt_isolation(tmp_path):
    from cbcc.asset_compiler import compile_asset_packages, validate_asset_packages
    assets=[{'asset_id':'AST-AAAAAAAAAA','asset_name':'A','asset_type':'IMAGE','status':'ACTIVATE','surface':'GALLERY','family':'VISUAL','consumer_question':'What is it?','strategic_job':'Identify product','production_mode':'REAL_PRODUCT_COMPOSITE','product_fidelity':'LOCKED_PIXEL','priority':'P0','dependencies':[],'source_ids':['S1'],'claim_ids':[],'listing_reference':[],'success_metric':'clarity'}]
    compile_asset_packages(tmp_path,assets,{'name':'P'},{'platform_family':'x','site':'MY','market':'Malaysia'},{'visual_implications':[]},{'visible_copy_locales':['en-MY']},{'profiles':[]})
    out=validate_asset_packages(tmp_path)
    assert out['pass'] and out['count']==1

def test_family_planning_packs_cover_researched_platform_set():
    from cbcc.platform import PlatformCompiler
    c=PlatformCompiler(ROOT/'platform_packs')
    families=['amazon','shopify','tiktok_shop','shopee','mercadolivre','ebay','etsy','walmart','ozon','wayfair','noon','lazada','temu']
    for fam in families:
        out=c.compile({'platform_family':fam,'site':'TEST-SITE','program':None,'category':'test','surfaces':['PDP'],'primary_locale':'en-US'},[])
        assert out['resolution']=='FAMILY', fam
        assert out['submission_readiness']=='NOT_ESTABLISHED', fam
