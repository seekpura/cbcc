from pathlib import Path
import json, sys, hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.asset_compiler import compile_asset_packages
from cbcc.production import build_production_run, materialize_provider_jobs, apply_production_result
from cbcc.learning_loop import compile_local_revision_jobs, compile_learning_cycle


def _asset(aid='AST-V0514-HERO', intent='IDENTIFY', topic='What is it?'):
    return {
        'asset_id':aid,'asset_name':'V0514','asset_type':'IMAGE','status':'ACTIVATE','surface':'GALLERY','family':'VISUAL',
        'consumer_question':topic,'strategic_job':'Identify product','decision_intent':intent,'decision_topic':topic,
        'production_mode':'REAL_PRODUCT_COMPOSITE','product_fidelity':'LOCKED_PIXEL','priority':'P0','dependencies':[],
        'source_ids':['S1'],'claim_ids':[],'listing_reference':[],'success_metric':'clarity'
    }


def _bound_master():
    return [{
        'asset_id':'MASTER-01','role':'FRONT_MASTER','path':'/test/master.png','sha256':'a'*64,
        'ingest_status':'HASH_VERIFIED_LOCAL','pixel_lock':True,
        'allowed_transforms':['PROPORTIONAL_SCALE','PLACEMENT','MASK_OR_CROP','COMPOSITE'],
        'identity_features':['logo','packaging_print','color','geometry','proportions']
    }]


def _compile(root:Path, with_master:bool):
    compile_asset_packages(
        root,[_asset()],{'name':'P'},{'platform_family':'x','site':'MY','market':'Malaysia'},
        {'visual_implications':[]},{'visible_copy_locales':['en-MY']},{'profiles':[]},
        source_product_assets=_bound_master() if with_master else []
    )


def _quality_pass(job:dict):
    out={}
    for k in job['result_contract']['quality_observations_required']:
        if k=='source_product_asset_ids_used': out[k]=['MASTER-01']
        elif k=='product_layer_operation': out[k]='COMPOSITE_LOCKED'
        else: out[k]={'status':'PASS','evidence':'provider observation recorded for '+k}
    return out


def test_locked_pixel_without_exact_master_is_held_before_provider_handoff(tmp_path):
    root=tmp_path/'packs'; _compile(root,False)
    run=build_production_run(root)
    row=run['assets'][0]
    assert row['status']=='HOLD_REAL_PRODUCT_PREFLIGHT'
    assert 'REAL_PRODUCT_MASTER_NOT_BOUND' in row['production_quality_contract']['preflight_errors']
    jobs=materialize_provider_jobs(root,run,tmp_path/'jobs')
    assert jobs['job_count']==0


def test_bound_master_creates_asset_specific_executable_provider_contract(tmp_path):
    root=tmp_path/'packs'; _compile(root,True)
    run=build_production_run(root); row=run['assets'][0]
    assert row['status']=='READY_TO_HANDOFF'
    jobs=materialize_provider_jobs(root,run,tmp_path/'jobs'); assert jobs['job_count']==1
    job=json.loads((tmp_path/'jobs'/row['asset_id']/'job.json').read_text())
    assert job['production_quality_contract']['source_product_asset_ids']==['MASTER-01']
    assert 'identity-led' in job['execution_brief']['visual_information_grammar']
    assert job['execution_policy']['real_product_master_substitution_allowed'] is False
    assert set(job['production_quality_contract']['editable_layer_contract']['frozen_layers']) >= {'product_master_pixels','logo','packaging_print','product_geometry','product_color_identity'}


def test_provider_quality_result_requires_observation_evidence_not_boolean_checkboxes(tmp_path):
    root=tmp_path/'packs'; _compile(root,True)
    run=build_production_run(root); row=run['assets'][0]
    base={'asset_id':row['asset_id'],'provider':row['provider'],'package_hash':row['package_hash'],'output_path':'out.png',
          'qa':{'product':True,'fact':True,'claim':True,'visual':True,'culture':True,'platform':True}}
    weak={**base,'quality_observations':{k:(['MASTER-01'] if k=='source_product_asset_ids_used' else ('COMPOSITE_LOCKED' if k=='product_layer_operation' else True)) for k in row['production_quality_contract']['required_result_observations']}}
    reviewed=apply_production_result(run,[weak])
    assert reviewed['status']=='REVIEW_REQUIRED'
    assert any(x['code'].startswith('QUALITY_EVIDENCE_MISSING:') for x in reviewed['issues'])
    jobs=materialize_provider_jobs(root,run,tmp_path/'jobs')
    job=json.loads((tmp_path/'jobs'/row['asset_id']/'job.json').read_text())
    strong={**base,'quality_observations':_quality_pass(job)}
    passed=apply_production_result(run,[strong])
    assert passed['status']=='COMPLETE' and passed['assets'][0]['result_status']=='PASS'


def test_local_revision_maps_leaf_fields_to_editable_layers_and_blocks_product_identity(tmp_path):
    project=tmp_path/'project'; root=project/'artifacts/asset_packages'; _compile(root,True)
    state={'project_id':'P','revision':0,'local_revision_requests':[
        {'revision_request_id':'LRQ-OK','asset_id':'AST-V0514-HERO','status':'OPEN','allowed_fields':['headline_copy','composition','spoon_presence'],'requested_change':'local execution only'},
        {'revision_request_id':'LRQ-BLOCK','asset_id':'AST-V0514-HERO','status':'OPEN','allowed_fields':['logo'],'requested_change':'must not change product identity'},
    ]}
    out=compile_local_revision_jobs(project,state)
    assert any(x['revision_request_id']=='LRQ-OK' for x in out['compiled'])
    blocked=next(x for x in out['held'] if x['revision_request_id']=='LRQ-BLOCK')
    assert blocked['reason']=='REVISION_FIELD_OUTSIDE_EDITABLE_LAYERS'
    ok=next(x for x in out['compiled'] if x['revision_request_id']=='LRQ-OK')
    assert set(ok['allowed_layers']) >= {'typography_copy','layout_spacing','prop_context'}


def test_production_failure_learning_routes_to_visual_execution_layer_not_product_truth(tmp_path):
    state={'project_id':'P','revision':0}
    cycle=compile_learning_cycle(tmp_path,state,{
        'cycle_id':'LC-V0514','production_issue_codes':['LOCKED_PIXEL_IDENTITY_NOT_CONFIRMED','SAME_LAYOUT','COPY_VISUAL_ALIGNMENT'],
        'post_feedback':[{'code':'PHOTOGRAPHY_CMF_MISMATCH'}]
    })
    assert set(cycle['edit_layers']) >= {'VISUAL_PRODUCT_FIDELITY_EXECUTION','VISUAL_ASSET_DIFFERENTIATION','VISUAL_COPY_ALIGNMENT','VISUAL_PHOTOGRAPHY_CMF'}
    assert set(cycle['freeze_layers']) >= {'PRODUCT_TRUTH','POSITIONING','OFFER'}
