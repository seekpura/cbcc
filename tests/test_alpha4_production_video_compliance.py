from pathlib import Path
import sys,json,yaml
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.video_creator import build_video_creator_plan
from cbcc.compliance import compile_compliance
from cbcc.production import build_production_run, apply_production_result
from cbcc.asset_compiler import compile_asset_packages


def _test_master():
    return [{'asset_id':'TEST-MASTER','role':'FRONT_MASTER','sha256':'a'*64,'ingest_status':'HASH_VERIFIED_LOCAL','pixel_lock':True}]

def _quality_observations(row):
    out={}
    for k in row['production_quality_contract']['required_result_observations']:
        if k=='source_product_asset_ids_used': out[k]=['TEST-MASTER']
        elif k=='product_layer_operation': out[k]='COMPOSITE_LOCKED'
        else: out[k]={'status':'PASS','evidence':'test observation for '+k}
    return out


def test_video_creator_dynamic_plan_and_timing():
    objs=[{'family':'VIDEO','surface':'PDP_VIDEO','curation_job':'Explain use'},{'family':'CREATOR_AFFILIATE','surface':'CREATOR','curation_job':'Show routine'}]
    out=build_video_creator_plan('P',objs,['How use?','Does it fit me?'],{'primary_locale':'en-MY','visible_copy_locales':['en-MY','ms-MY'],'script_subtitle_locales':['ms-MY']})
    assert out['dynamic_count']==2 and out['fixed_duration_authority'] is False
    assert out['assets'][0]['timing']['pass'] and out['assets'][0]['voice_locale']=='en-MY'


def test_compliance_binds_assets_to_approved_claim_ids_and_research():
    pc={'status':'VERIFIED_FOR_REQUEST'}
    out=compile_compliance({'product':{'name':'x'}},[{'claim_id':'C1','status':'APPROVED'}],{'status':'PASS'},[{'asset_id':'A','claim_ids':['C1']},{'asset_id':'B','claim_ids':['C2']}],pc,{'pending':[]})
    assert out['status']=='HOLD' and out['issues'][0]['claim_ids']==['C2']


def test_production_runner_preserves_frozen_package_and_requires_qa(tmp_path):
    assets=[{'asset_id':'AST-AAAAAAAAAA','asset_name':'A','asset_type':'IMAGE','status':'ACTIVATE','surface':'GALLERY','family':'VISUAL','consumer_question':'What is it?','strategic_job':'Identify product','production_mode':'REAL_PRODUCT_COMPOSITE','product_fidelity':'LOCKED_PIXEL','priority':'P0','dependencies':[],'source_ids':['S1'],'claim_ids':[],'listing_reference':[],'success_metric':'clarity'}]
    compile_asset_packages(tmp_path,assets,{'name':'P'},{'platform_family':'x','site':'MY','market':'Malaysia'},{'visual_implications':[]},{'visible_copy_locales':['en-MY']},{'profiles':[]},source_product_assets=_test_master())
    run=build_production_run(tmp_path)
    assert run['replanning_allowed'] is False and run['assets'][0]['frozen_strategy'] is True
    missing=apply_production_result(run,[])
    assert missing['status']=='REVIEW_REQUIRED'
    passed=apply_production_result(run,[{'asset_id':'AST-AAAAAAAAAA','package_hash':run['assets'][0]['package_hash'],'output_path':'A.png','qa':{'product':True,'fact':True,'claim':True,'visual':True,'culture':True,'platform':True},'quality_observations':_quality_observations(run['assets'][0])}])
    assert passed['status']=='COMPLETE' and passed['assets'][0]['result_status']=='PASS'


def test_local_revision_scope_blocks_unapproved_changes(tmp_path):
    assets=[{'asset_id':'AST-BBBBBBBBBB','asset_name':'B','asset_type':'IMAGE','status':'ACTIVATE','surface':'GALLERY','family':'VISUAL','consumer_question':'How use?','strategic_job':'Show use','production_mode':'REAL_PRODUCT_COMPOSITE','product_fidelity':'LOCKED_PIXEL','priority':'P1','dependencies':[],'source_ids':['S1'],'claim_ids':[],'listing_reference':[],'success_metric':'clarity'}]
    compile_asset_packages(tmp_path,assets,{'name':'P'},{'platform_family':'x','site':'MY','market':'Malaysia'},{'visual_implications':[]},{'visible_copy_locales':['en-MY']},{'profiles':[]},source_product_assets=_test_master())
    run=build_production_run(tmp_path,revision_scope={'asset_id':'AST-BBBBBBBBBB','allowed_fields':['spoon_presence']})
    h=run['assets'][0]['package_hash']
    bad=apply_production_result(run,[{'asset_id':'AST-BBBBBBBBBB','package_hash':h,'changed_fields':['spoon_presence','composition'],'output_path':'B.png','qa':{'product':True,'fact':True,'claim':True,'visual':True,'culture':True,'platform':True},'quality_observations':_quality_observations(run['assets'][0])}])
    assert bad['status']=='REVIEW_REQUIRED' and any(x['code']=='REVISION_SCOPE_VIOLATION' for x in bad['issues'])
    good=apply_production_result(run,[{'asset_id':'AST-BBBBBBBBBB','package_hash':h,'changed_fields':['spoon_presence'],'output_path':'B.png','qa':{'product':True,'fact':True,'claim':True,'visual':True,'culture':True,'platform':True},'quality_observations':_quality_observations(run['assets'][0])}])
    assert good['status']=='COMPLETE'
