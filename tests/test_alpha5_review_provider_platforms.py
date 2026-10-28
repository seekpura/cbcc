from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project
from cbcc.review import materialize_review_workspace
from cbcc.state import ProjectState
from cbcc.platform import PlatformCompiler
from cbcc.providers import route_production
from cbcc.asset_compiler import compile_asset_packages
from cbcc.production import build_production_run, apply_production_result


def _test_master():
    return [{'asset_id':'TEST-MASTER','role':'FRONT_MASTER','provider_asset_handle':'fixture://TEST-MASTER','sha256':'a'*64,'ingest_status':'EXTERNAL_HANDLE_HASH_DECLARED','pixel_lock':True}]

def _quality_observations(row):
    out={}
    for k in row['production_quality_contract']['required_result_observations']:
        if k=='source_product_asset_ids_used': out[k]=['TEST-MASTER']
        elif k=='source_product_hashes_used': out[k]={'TEST-MASTER':'a'*64}
        elif k=='product_layer_operation': out[k]='COMPOSITE_LOCKED'
        else: out[k]={'status':'PASS','evidence':'test observation for '+k}
    return out


def test_review_workspace_is_materialized_and_read_only(tmp_path):
    fx=ROOT/'tests/fixtures/kiyuu_my_tiktok'; req=json.loads((fx/'request.json').read_text(encoding='utf-8'))
    proj=tmp_path/'proj'; out=build_project(proj,req,fx)
    paths=materialize_review_workspace(proj,out)
    for key,path in paths.items(): assert Path(path).exists(), key
    html=Path(paths['review_html']).read_text(encoding='utf-8')
    assert 'does not mutate authority state' in html
    decision=json.loads(Path(paths['review_decision_template']).read_text(encoding='utf-8'))
    assert decision['project_id']==out['project_id'] and decision['revision']==out['revision']
    manifest=json.loads(Path(paths['delivery_manifest']).read_text(encoding='utf-8'))
    assert any(x['kind']=='CONTENT_OBJECT' for x in manifest['items'])


def test_review_decision_accept_hold_revise_and_stale_guard(tmp_path):
    fx=ROOT/'tests/fixtures/kiyuu_my_tiktok'; req=json.loads((fx/'request.json').read_text(encoding='utf-8'))
    proj=tmp_path/'proj'; build_project(proj,req,fx); st=ProjectState.load(proj)
    r=st.apply_review_decision({'project_id':st.data['project_id'],'revision':0,'accept':['EVIDENCE'],'hold':['CREATIVE'],'notes':{'CREATIVE':'Needs visual review'}})
    assert r['accepted']==['EVIDENCE'] and st.data['gates']['EVIDENCE']['status']=='LOCKED' and st.data['gates']['CREATIVE']['status']=='HOLD'
    st.apply_review_decision({'project_id':st.data['project_id'],'revision':0,'revise':['TARGET_CONTEXT']})
    assert st.data['revision']==1 and st.data['gates']['TARGET_CONTEXT']['status']=='INVALIDATED'
    try:
        st.apply_review_decision({'project_id':st.data['project_id'],'revision':0,'accept':['EVIDENCE']})
    except ValueError as e:
        assert 'stale' in str(e)
    else:
        raise AssertionError('stale review decision should fail')


def test_provider_adapter_contract_and_result_validation(tmp_path):
    asset={'asset_id':'AST-PROVIDER01','asset_name':'A','asset_type':'IMAGE','status':'ACTIVATE','surface':'GALLERY','family':'VISUAL','consumer_question':'What is it?','strategic_job':'Identify','production_mode':'REAL_PRODUCT_COMPOSITE','product_fidelity':'LOCKED_PIXEL','priority':'P0','dependencies':[],'source_ids':['S1'],'claim_ids':[],'listing_reference':[],'success_metric':'clarity'}
    good=route_production(asset)
    assert good['route_status']=='READY' and good['provider_contract']['locked_pixel_support']=='SUPPORTED'
    bad=route_production(asset,{'REAL_PRODUCT_COMPOSITE':'CG_3D_PROVIDER'})
    assert bad['route_status']=='HOLD' and 'MODE_NOT_SUPPORTED_BY_PROVIDER' in bad['provider_contract']['errors']
    compile_asset_packages(tmp_path,[asset],{'name':'P'},{'platform_family':'x','site':'MY','market':'Malaysia'},{'visual_implications':[]},{'visible_copy_locales':['en-MY']},{'profiles':[]},source_product_assets=_test_master())
    run=build_production_run(tmp_path)
    row=run['assets'][0]
    passed=apply_production_result(run,[{'asset_id':row['asset_id'],'package_hash':row['package_hash'],'provider':row['provider'],'output_path':'out.png','production_contract_ack':True,'source_binding_hash':row['production_quality_contract']['source_binding_hash'],'qa':{'product':True,'fact':True,'claim':True,'visual':True,'culture':True,'platform':True},'quality_observations':_quality_observations(row)}])
    assert passed['status']=='COMPLETE'
    mismatch=apply_production_result(run,[{'asset_id':row['asset_id'],'package_hash':row['package_hash'],'provider':'CG_3D_PROVIDER','output_path':'out.png','production_contract_ack':True,'source_binding_hash':row['production_quality_contract']['source_binding_hash'],'qa':{'product':True,'fact':True,'claim':True,'visual':True,'culture':True,'platform':True},'quality_observations':_quality_observations(row)}])
    assert any(x['code']=='PROVIDER_ID_MISMATCH' for x in mismatch['issues'])


def test_new_exact_platform_packs_are_scope_bounded():
    pc=PlatformCompiler(ROOT/'platform_packs')
    amz=pc.compile({'platform_family':'amazon','site':'US','program':None,'category':'electronics','surfaces':['SEARCH_RESULTS','PDP','GALLERY'],'primary_locale':'en-US'},['AMZ-US-TITLE-MAX-75-NONMEDIA','AMZ-US-MAIN-IMAGE-WHITE'])
    assert amz['resolution']=='EXACT' and amz['status']=='VERIFIED_FOR_REQUEST' and amz['submission_readiness']=='ASSESSED'
    noon=pc.compile({'platform_family':'noon','site':'AE','program':None,'category':'home','surfaces':['GALLERY'],'primary_locale':'en-AE'},['NOON-AE-IMAGE-FORMAT'])
    assert noon['status']=='VERIFIED_FOR_REQUEST' and noon['submission_readiness']=='ASSESSED'
    noon_listing=pc.compile({'platform_family':'noon','site':'AE','program':None,'category':'home','surfaces':['PDP'],'primary_locale':'en-AE'})
    assert noon_listing['status']=='RESEARCH_REQUIRED' and 'PDP' in noon_listing['unsupported_surfaces']
    shp=pc.compile({'platform_family':'shopee','site':'MY','program':None,'category':'food','surfaces':['PDP'],'primary_locale':'en-MY'},['SHOPEE-MY-LISTING-ACCURACY'])
    assert shp['status']=='VERIFIED_FOR_REQUEST'
    shp_gallery=pc.compile({'platform_family':'shopee','site':'MY','program':None,'category':'food','surfaces':['GALLERY'],'primary_locale':'en-MY'})
    assert shp_gallery['status']=='RESEARCH_REQUIRED'
