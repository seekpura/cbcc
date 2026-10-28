from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project
from cbcc.state import ProjectState
from cbcc.review import materialize_review_workspace
from cbcc.platform import PlatformCompiler
from cbcc.asset_compiler import compile_asset_packages
from cbcc.production import build_production_run, materialize_provider_jobs, ingest_provider_job_results


def _test_master_record():
    return [{'asset_id':'TEST-MASTER','role':'FRONT_MASTER','sha256':'a'*64,'ingest_status':'HASH_VERIFIED_LOCAL','pixel_lock':True}]

def _bind_test_master(req,tmp_path):
    master=tmp_path/'test-product-master.bin'; master.write_bytes(b'test-product-master')
    req['source_product_assets']=[{'asset_id':'TEST-MASTER','role':'FRONT_MASTER','path':str(master),'pixel_lock':True,'note':'TEST FIXTURE ONLY'}]
    return req

def _quality_observations(job):
    out={}
    for k in job['result_contract']['quality_observations_required']:
        if k=='source_product_asset_ids_used': out[k]=['TEST-MASTER']
        elif k=='product_layer_operation': out[k]='COMPOSITE_LOCKED'
        else: out[k]={'status':'PASS','evidence':'test observation for '+k}
    return out


def _asset():
    return {'asset_id':'AST-ALPHA6','asset_name':'Alpha6','asset_type':'IMAGE','status':'ACTIVATE','surface':'GALLERY','family':'VISUAL','consumer_question':'What is it?','strategic_job':'Identify','production_mode':'REAL_PRODUCT_COMPOSITE','product_fidelity':'LOCKED_PIXEL','priority':'P0','dependencies':[],'source_ids':['SRC-1'],'claim_ids':[],'listing_reference':[],'success_metric':'clarity'}


def test_item_level_review_is_addressable_and_persists_local_revision(tmp_path):
    fx=ROOT/'tests/fixtures/kiyuu_my_tiktok'; req=json.loads((fx/'request.json').read_text(encoding='utf-8'))
    proj=tmp_path/'proj'; out=build_project(proj,req,fx); paths=materialize_review_workspace(proj,out)
    manifest=json.loads(Path(paths['delivery_manifest']).read_text(encoding='utf-8'))
    obj=next(x for x in manifest['items'] if x['kind']=='CONTENT_OBJECT')
    asset=next(x for x in manifest['items'] if x['kind']=='ASSET_PACKAGE')
    st=ProjectState.load(proj)
    result=st.apply_review_decision({
        'project_id':st.data['project_id'],'revision':st.data['revision'],
        'accept_items':[obj['item_id']],
        'revise_items':[{'item_id':asset['item_id'],'requested_change':'remove spoon only','allowed_fields':['spoon_presence'],'note':'keep all other fields frozen'}]
    })
    assert obj['item_id'] in result['accepted_items'] and asset['item_id'] in result['revised_items']
    assert st.data['item_reviews'][obj['item_id']]['status']=='ACCEPTED'
    rr=st.data['local_revision_requests'][-1]
    assert rr['asset_id']==asset['asset_id'] and rr['allowed_fields']==['spoon_presence'] and rr['status']=='OPEN'
    paths=materialize_review_workspace(proj,st.data)
    manifest2=json.loads(Path(paths['delivery_manifest']).read_text(encoding='utf-8'))
    assert next(x for x in manifest2['items'] if x['item_id']==asset['item_id'])['review_status']=='REVISE_REQUESTED'
    item_contract=proj/'.cbcc/review/items'/f"{asset['item_id']}.json"
    assert item_contract.exists()


def test_provider_filesystem_job_envelope_and_ingest(tmp_path):
    root=tmp_path/'packs'; compile_asset_packages(root,[_asset()],{'name':'P'},{'platform_family':'x','site':'MY','market':'Malaysia'},{'visual_implications':[]},{'visible_copy_locales':['en-MY']},{'profiles':[]},source_product_assets=_test_master_record())
    run=build_production_run(root)
    jobs=tmp_path/'jobs'; job_index=materialize_provider_jobs(root,run,jobs)
    assert job_index['job_count']==1
    row=run['assets'][0]; job=json.loads((jobs/row['asset_id']/'job.json').read_text(encoding='utf-8'))
    assert job['execution_policy']['replanning_allowed'] is False and job['package_hash']==row['package_hash']
    result={'asset_id':row['asset_id'],'provider':row['provider'],'package_hash':row['package_hash'],'output_path':'final.png','changed_fields':[],'qa':{'product':True,'fact':True,'claim':True,'visual':True,'culture':True,'platform':True},'quality_observations':_quality_observations(job)}
    (jobs/row['asset_id']/'result.json').write_text(json.dumps(result),encoding='utf-8')
    ingested=ingest_provider_job_results(run,jobs)
    assert ingested['status']=='COMPLETE' and ingested['provider_results_ingested']==1


def test_layered_exact_platform_packs_and_category_requirements():
    pc=PlatformCompiler(ROOT/'platform_packs')
    my=pc.compile({'platform_family':'tiktok_shop','site':'MY','program':'cross_border','category':'beauty','surfaces':['PDP','GALLERY'],'primary_locale':'en-MY','visible_copy_locales':['en-MY','ms-MY'],'require_category_pack':True},['TTS-MY-BM-TITLE-DESCRIPTION','TTS-BEAUTY-GLOBAL-LISTING-ACCURACY'])
    assert my['status']=='VERIFIED_FOR_REQUEST' and my['category_overlay_applied']
    assert 'tiktok-shop-my-current-2026-10-27' in my['applied_pack_ids'] and 'tiktok-shop-my-beauty-overlay-2026-10-27' in my['applied_pack_ids']
    # Malaysia listing target omitting Bahasa Melayu is a known target-contract mismatch, not a research guess.
    my_bad=pc.compile({'platform_family':'tiktok_shop','site':'MY','program':'cross_border','category':'beauty','surfaces':['PDP'],'primary_locale':'en-MY','visible_copy_locales':['en-MY']},['TTS-MY-BM-TITLE-DESCRIPTION'])
    assert my_bad['status']=='TARGET_CONTRACT_MISMATCH' and 'VISIBLE_COPY_LOCALE_REQUIRED:ms-MY' in my_bad['contract_issues']
    us=pc.compile({'platform_family':'tiktok_shop','site':'US','program':None,'category':'beauty','surfaces':['PDP','CREATOR'],'primary_locale':'en-US','visible_copy_locales':['en-US'],'require_category_pack':True},['TTS-US-BEAUTY-SHELF-LIFE','TTS-US-BEAUTY-CREATOR-AUTHENTICITY'])
    assert us['status']=='VERIFIED_FOR_REQUEST' and us['category_overlay_applied'] and len(us['applied_pack_ids'])==2
    no_overlay=pc.compile({'platform_family':'tiktok_shop','site':'US','program':None,'category':'electronics','surfaces':['PDP'],'primary_locale':'en-US','visible_copy_locales':['en-US'],'require_category_pack':True})
    assert no_overlay['status']=='RESEARCH_REQUIRED' and any('CATEGORY_PACK:electronics' in a['reason'] for a in no_overlay['research_actions'])
    amz=pc.compile({'platform_family':'amazon','site':'US','program':None,'category':'cosmetics','surfaces':['PDP','GALLERY'],'primary_locale':'en-US','visible_copy_locales':['en-US'],'require_category_pack':True},['AMZ-US-COSMETICS-PDP-ATTRIBUTES'])
    assert amz['status']=='VERIFIED_FOR_REQUEST' and 'amazon-us-cosmetics-overlay-2026-10-27' in amz['applied_pack_ids']


def _e2e_request(project_id,platform_family,site,market,category,surfaces,locale,visible,required_rules):
    return {
      'project_id':project_id,'sku':'SKU-1','product':{'name':'Verified Test Product','capacity':'50 ml'},'claims':[],
      'sources':[{'source_id':'SRC-1','kind':'PRODUCT_SOURCE'}],
      'target':{'target_id':'T1','market':market,'jurisdiction':site,'platform_family':platform_family,'site':site,'program':None,'surfaces':surfaces,'category':category,'primary_locale':locale,'visible_copy_locales':visible,'require_category_pack':True},
      'required_platform_rules':required_rules,
      'shopper_questions':['What is it?','Why choose it?','What evidence supports it?'],
      'audience_culture':{'statements':[{'statement':'Use only evidence-backed local context.','status':'ASSUMPTION','source_ids':[],'implications':[]}]},
      'cmf':{'color':'truth-bound','material':'verified','finish':'truth-bound'},
      'creative_directions':[{'direction_id':'TRUTH_FIRST','product_fit':5,'audience_fit':4,'platform_fit':5,'culture_fit':4,'differentiation':4,'production_feasibility':5,'decision':'SELECT'}],
      'compile_assets':True,'planning_only':False,
    }


def test_category_overlay_golden_e2e_matrix(tmp_path):
    cases=[
      _e2e_request('TTS-MY-BEAUTY','tiktok_shop','MY','Malaysia','beauty',['PDP','GALLERY'],'en-MY',['en-MY','ms-MY'],['TTS-MY-BM-TITLE-DESCRIPTION','TTS-BEAUTY-GLOBAL-LISTING-ACCURACY']),
      _e2e_request('TTS-US-BEAUTY','tiktok_shop','US','United States','beauty',['PDP','CREATOR'],'en-US',['en-US'],['TTS-US-BEAUTY-QUALIFICATION','TTS-US-BEAUTY-CREATOR-AUTHENTICITY']),
      _e2e_request('AMZ-US-COS','amazon','US','United States','cosmetics',['PDP','GALLERY'],'en-US',['en-US'],['AMZ-US-COSMETICS-PDP-ATTRIBUTES']),
    ]
    for i,req in enumerate(cases):
        proj=tmp_path/f'overlay{i}'; out=build_project(proj,req,ROOT/'platform_packs')
        assert out['gates']['PLATFORM_COMPILE']['status']=='READY_REVIEW'
        pc=json.loads((proj/'artifacts/platform_compile.json').read_text(encoding='utf-8'))
        assert pc['category_overlay_applied'] and pc['submission_readiness']=='ASSESSED'
        comp=json.loads((proj/'artifacts/asset_compile.json').read_text(encoding='utf-8'))
        assert comp['validation']['pass']


def test_provider_ingest_cli_lifecycle(tmp_path, capsys):
    from cbcc.cli import main as cli_main
    fx=ROOT/'tests/fixtures/kiyuu_my_tiktok'; req=json.loads((fx/'request.json').read_text(encoding='utf-8'))
    req['production_run']={'asset_ids':[]}
    _bind_test_master(req,tmp_path)
    proj=tmp_path/'provider-cli'; build_project(proj,req,fx)
    idx=json.loads((proj/'artifacts/provider_jobs/PROVIDER_JOB_INDEX.json').read_text(encoding='utf-8'))
    assert idx['job_count']>0
    for row in idx['jobs']:
        job=json.loads(Path(row['job_path']).read_text(encoding='utf-8'))
        result={'asset_id':job['asset_id'],'provider':job['provider'],'package_hash':job['package_hash'],'output_path':str(proj/f"outputs/{job['asset_id']}.png"),'changed_fields':[],'qa':{'product':True,'fact':True,'claim':True,'visual':True,'culture':True,'platform':True},'quality_observations':_quality_observations(job)}
        Path(row['result_path']).write_text(json.dumps(result),encoding='utf-8')
    assert cli_main(['provider-ingest','--project-dir',str(proj)])==0
    out=json.loads((proj/'artifacts/production_run.json').read_text(encoding='utf-8'))
    assert out['status']=='COMPLETE' and out['provider_results_missing']==[]
    st=ProjectState.load(proj)
    assert st.data['gates']['PRODUCTION']['status']=='READY_REVIEW'
