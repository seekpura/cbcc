from pathlib import Path
import hashlib, json, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))

from cbcc.asset_compiler import compile_asset_packages
from cbcc.production import build_production_run, materialize_provider_jobs, apply_production_result


def _asset():
    return {
        'asset_id':'AST-V0611-BIND','asset_name':'Provider binding proof','asset_type':'IMAGE','status':'ACTIVATE',
        'surface':'GALLERY','family':'VISUAL','consumer_question':'What is this product?','strategic_job':'Identify exact product',
        'production_mode':'REAL_PRODUCT_COMPOSITE','product_fidelity':'LOCKED_PIXEL','priority':'P0','dependencies':[],
        'source_ids':['SRC-1'],'claim_ids':[],'listing_reference':[],'success_metric':'identity clarity',
    }


def _master(path:Path):
    data=b'v0611-real-product-master'
    path.write_bytes(data)
    return [{
        'asset_id':'MASTER-V0611','role':'FRONT_MASTER','path':str(path),
        'sha256':hashlib.sha256(data).hexdigest(),'ingest_status':'HASH_VERIFIED_LOCAL','pixel_lock':True,
        'allowed_transforms':['PROPORTIONAL_SCALE','PLACEMENT','MASK_OR_CROP','COMPOSITE'],
        'identity_features':['logo','packaging_print','color','geometry','proportions'],
    }]


def _compile(root:Path, master:Path):
    compile_asset_packages(
        root,[_asset()],{'name':'P'},{'platform_family':'x','site':'MY','market':'Malaysia'},
        {'visual_implications':[]},{'visible_copy_locales':['en-MY']},{'profiles':[]},
        source_product_assets=_master(master),
    )


def _quality(job:dict):
    bindings=job['source_product_bindings']
    hashes={x['asset_id']:x['sha256'] for x in bindings}
    out={}
    for key in job['result_contract']['quality_observations_required']:
        if key=='source_product_asset_ids_used': out[key]=list(hashes)
        elif key=='source_product_hashes_used': out[key]=hashes
        elif key=='product_layer_operation': out[key]='COMPOSITE_LOCKED'
        else: out[key]={'status':'PASS','evidence':'provider evidence for '+key}
    return out


def _result(job:dict, **overrides):
    result={
        'asset_id':job['asset_id'],'provider':job['provider'],'package_hash':job['package_hash'],'output_path':'out.png',
        'changed_fields':[],'changed_layers':[],
        'qa':{'product':True,'fact':True,'claim':True,'visual':True,'culture':True,'platform':True},
        'production_contract_ack':True,'source_binding_hash':job['source_binding_hash'],
        'quality_observations':_quality(job),
        'production_receipt':{
            'job_id':job['job_id'],'asset_id':job['asset_id'],'provider':job['provider'],'package_hash':job['package_hash'],
            'portable_manifest_hash':job['portable_package']['portable_manifest_hash'],'source_binding_hash':job['source_binding_hash'],
            'output_artifacts':[{'uri':'fixture://provider-output/'+job['asset_id'],'sha256':'b'*64,'role':'FINAL'}],
            'layer_manifest':[{'layer_id':'product-'+str(i),'role':'PRODUCT_MASTER','source_asset_id':x['asset_id'],'source_sha256':x['sha256'],'operation':'COMPOSITE_LOCKED','frozen':True} for i,x in enumerate(job.get('source_product_bindings') or [])],
            'capture_metadata':{},
        },
        '_provider_job_ingest':True,
    }
    result.update(overrides)
    return result


def test_locked_pixel_provider_job_carries_resolvable_source_binding_and_hash_lineage(tmp_path):
    root=tmp_path/'packs'; master=tmp_path/'master.png'; _compile(root,master)
    package=root/_asset()['asset_id']
    prompt=json.loads((package/'13_prompt_contract.json').read_text(encoding='utf-8'))
    renderer_bindings=prompt['renderer_recipe']['source_product_bindings']
    assert renderer_bindings[0]['asset_id']=='MASTER-V0611'
    assert renderer_bindings[0]['locator']=={'kind':'LOCAL_FILE_PATH','value':str(master)}
    assert renderer_bindings[0]['pixel_lock'] is True

    run=build_production_run(root); row=run['assets'][0]
    assert row['status']=='READY_TO_HANDOFF'
    jobs=tmp_path/'jobs'; materialize_provider_jobs(root,run,jobs)
    job=json.loads((jobs/row['asset_id']/'job.json').read_text(encoding='utf-8'))
    binding=job['source_product_bindings'][0]
    assert binding['handoff_status']=='READY_PACKAGE_VERIFIED'
    assert binding['locator']['kind']=='PACKAGE_RELATIVE_PATH'
    assert (jobs/row['asset_id']/binding['locator']['value']).exists()
    assert binding['handoff_sha256']==binding['sha256']
    assert job['execution_brief']['source_product_bindings']==job['source_product_bindings']
    assert job['execution_brief']['source_binding_hash']==job['source_binding_hash']
    assert 'source_product_bindings' in job['provider_contract']['required_inputs']
    assert job['provider_contract']['source_binding_contract']['integrity_key']=='sha256'
    assert set(job['provider_contract']['source_binding_contract']['locked_pixel_result_evidence']) >= {'source_product_asset_ids_used','source_product_hashes_used','product_layer_operation'}

    template=json.loads((jobs/row['asset_id']/'result.template.json').read_text(encoding='utf-8'))
    assert template['source_binding_hash']==job['source_binding_hash']
    assert template['quality_observations']['source_product_hashes_used']=={}

    passed=apply_production_result(run,[_result(job)])
    assert passed['status']=='COMPLETE'

    wrong=_result(job)
    wrong['quality_observations']['source_product_hashes_used']={'MASTER-V0611':'0'*64}
    reviewed=apply_production_result(run,[wrong])
    assert reviewed['status']=='REVIEW_REQUIRED'
    assert any(x['code']=='SOURCE_PRODUCT_HASH_LINEAGE_MISMATCH' for x in reviewed['issues'])

    wrong_binding=apply_production_result(run,[_result(job,source_binding_hash='wrong')])
    assert any(x['code']=='SOURCE_BINDING_HASH_MISMATCH' for x in wrong_binding['issues'])


def test_local_source_is_reverified_at_provider_handoff_instead_of_trusting_compile_time_status(tmp_path):
    root=tmp_path/'packs'; master=tmp_path/'master.png'; _compile(root,master)
    master.unlink()
    run=build_production_run(root); row=run['assets'][0]
    assert row['status']=='HOLD_REAL_PRODUCT_PREFLIGHT'
    qc=row['production_quality_contract']
    assert 'REAL_PRODUCT_MASTER_NOT_RESOLVABLE_AT_HANDOFF' in qc['preflight_errors']
    assert qc['source_product_bindings']==[]
    assert qc['source_product_binding_errors'][0]['status']=='LOCAL_FILE_MISSING_AT_HANDOFF'
    jobs=materialize_provider_jobs(root,run,tmp_path/'jobs')
    assert jobs['job_count']==0


def test_local_revision_result_cannot_report_mutating_frozen_product_layer(tmp_path):
    root=tmp_path/'packs'; master=tmp_path/'master.png'; _compile(root,master)
    scope={
        'asset_id':'AST-V0611-BIND','allowed_fields':['headline_copy'],'allowed_layers':['typography_copy'],
        'frozen_layers':['product_master_pixels','logo','packaging_print','product_geometry','product_color_identity'],
    }
    run=build_production_run(root,revision_scope=scope); row=run['assets'][0]
    jobs=tmp_path/'jobs'; materialize_provider_jobs(root,run,jobs)
    job=json.loads((jobs/row['asset_id']/'job.json').read_text(encoding='utf-8'))
    bad=_result(job,changed_fields=['headline_copy'],changed_layers=['product_master_pixels'])
    reviewed=apply_production_result(run,[bad])
    codes={x['code'] for x in reviewed['issues']}
    assert 'FROZEN_LAYER_MUTATION_REPORTED' in codes
    assert 'REVISION_LAYER_SCOPE_VIOLATION' in codes

    missing_layers=_result(job,changed_fields=['headline_copy'])
    missing_layers.pop('changed_layers')
    reviewed=apply_production_result(run,[missing_layers])
    assert any(x['code']=='REVISION_CHANGED_LAYERS_MISSING' for x in reviewed['issues'])


def test_real_kiyuu_three_asset_provider_jobs_bind_same_verified_product_master(tmp_path):
    from cbcc.compiler import build_project
    fixture=ROOT/'tests/fixtures/kiyuu_my_tiktok'
    request=json.loads((fixture/'request.json').read_text(encoding='utf-8'))
    master=tmp_path/'kiyuu-k01-master.png'
    data=b'kiyuu-k01-real-master-test-fixture'
    master.write_bytes(data)
    request['source_product_assets']=[{
        'asset_id':'KIYUU-K01-MASTER-FRONT','role':'PRODUCT_FRONT_MASTER','path':str(master),'pixel_lock':True,
        'sha256':hashlib.sha256(data).hexdigest(),
        'allowed_transforms':['PROPORTIONAL_SCALE','PLACEMENT','MASK_OR_CROP','COMPOSITE'],
        'identity_features':['logo','packaging_print','color','geometry','proportions'],
    }]
    request['production_run']={'run':True}
    project=tmp_path/'kiyuu-project'
    build_project(project,request,fixture)
    index=json.loads((project/'artifacts/provider_jobs/PROVIDER_JOB_INDEX.json').read_text(encoding='utf-8'))
    assert index['job_count']==3
    for row in index['jobs']:
        job=json.loads(Path(row['job_path']).read_text(encoding='utf-8'))
        assert job['source_product_bindings'][0]['asset_id']=='KIYUU-K01-MASTER-FRONT'
        assert job['source_product_bindings'][0]['handoff_status']=='READY_PACKAGE_VERIFIED'
        assert job['source_product_bindings'][0]['sha256']==hashlib.sha256(data).hexdigest()
        assert job['execution_brief']['source_product_bindings']==job['source_product_bindings']
        assert job['provider_contract']['source_binding_contract']['required'] is True
        assert 'source_product_bindings' in job['provider_contract']['required_inputs']
        assert 'source_binding_hash' in job['result_contract']['required']
