from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

ROOT=Path(__file__).resolve().parents[1]


def _native_provider_pack(tmp_path:Path):
    packs=tmp_path/'packs'; d=packs/'AST-NATIVE'; d.mkdir(parents=True)
    master=tmp_path/'real-product.png'; data=b'real-product-reference-v0635'; master.write_bytes(data)
    sha=hashlib.sha256(data).hexdigest()
    manifest={
        'asset_id':'AST-NATIVE','asset_name':'Native reference hero','asset_type':'IMAGE','status':'ACTIVATE',
        'surface':'GALLERY','family':'VISUAL','production_mode':'AI_REFERENCE_PRODUCT',
        'product_fidelity':'REFERENCE_GUIDED_NATIVE_LOCK','priority':'P0',
        'source_product_assets':[{
            'asset_id':'MASTER-FRONT','role':'FRONT_MASTER','path':str(master),'sha256':sha,
            'ingest_status':'HASH_VERIFIED_LOCAL','pixel_lock':False,'identity_lock':True,
            'source_usage':'MODEL_REFERENCE_INPUT',
            'allowed_transforms':['REFERENCE_INPUT','NATIVE_RENDER','CAMERA_MATCH','PERSPECTIVE_MATCH','LIGHTING_MATCH','DEPTH_MATCH'],
            'identity_features':['package_geometry','package_proportions','logo','brand_wording','label_layout','recognizable_pack_print','product_color_identity','material_appearance'],
        }],
    }
    (d/'00_asset_manifest.yaml').write_text(yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False),encoding='utf-8')
    for name,data_obj in [('03_photography_contract.json',{}),('04_layout_contract.json',{}),('13_prompt_contract.json',{})]:
        (d/name).write_text(json.dumps(data_obj),encoding='utf-8')
    (packs/'ASSET_PACKAGE_INDEX.json').write_text(json.dumps({'assets':[{'asset_id':'AST-NATIVE'}]}),encoding='utf-8')
    return packs,master,sha


def test_native_reference_semantics_survive_to_portable_provider_vendor_request(tmp_path:Path):
    from cbcc.production import build_production_run, materialize_provider_jobs
    packs,master,sha=_native_provider_pack(tmp_path)
    run=build_production_run(packs)
    row=run['assets'][0]
    assert row['status']=='READY_TO_HANDOFF'
    qc=row['production_quality_contract']
    assert qc['product_reference_generation_mode']=='REFERENCE_GUIDED_NATIVE_GENERATION'
    assert qc['reference_input_required'] is True
    assert qc['native_product_generation_required'] is True
    binding=qc['source_product_bindings'][0]
    assert binding['usage_role']=='NATIVE_SUBJECT_REFERENCE'
    assert binding['source_usage']=='MODEL_REFERENCE_INPUT'
    assert binding['reference_input_required'] is True
    assert binding['native_generation_required'] is True
    assert binding['pixel_copy_required'] is False
    assert binding['fidelity_mode']=='REFERENCE_GUIDED_NATIVE_LOCK'

    jobs=tmp_path/'jobs'; result=materialize_provider_jobs(packs,run,jobs)
    assert result['job_count']==1
    job=json.loads((jobs/'AST-NATIVE'/'job.json').read_text(encoding='utf-8'))
    portable=job['source_product_bindings'][0]
    assert portable['locator']['kind']=='PACKAGE_RELATIVE_PATH'
    assert (jobs/'AST-NATIVE'/portable['locator']['value']).exists()
    assert portable['usage_role']=='NATIVE_SUBJECT_REFERENCE'
    assert portable['reference_input_required'] is True
    assert portable['native_generation_required'] is True
    assert portable['pixel_copy_required'] is False
    vendor_sources=job['adapter_transmission']['vendor_request']['source_assets']
    assert vendor_sources and vendor_sources[0]['usage_role']=='NATIVE_SUBJECT_REFERENCE'
    assert vendor_sources[0]['native_generation_required'] is True
    assert job['execution_brief']['product_reference_generation_mode']=='REFERENCE_GUIDED_NATIVE_GENERATION'
    assert job['execution_brief']['reference_input_required'] is True
    assert job['execution_brief']['native_product_generation_required'] is True
    assert 'source_binding_hash' in job['production_receipt_contract']['required']
    assert 'layer_manifest' not in job['production_receipt_contract']['required']


def test_native_provider_contract_requires_reference_semantic_binding_fields():
    from cbcc.providers import provider_contract
    c=provider_contract('AI_IMAGE_PROVIDER','AI_REFERENCE_PRODUCT',{
        'product_fidelity':'REFERENCE_GUIDED_NATIVE_LOCK'
    })
    assert c['status']=='READY'
    fields=set(c['source_binding_contract']['required_binding_fields'])
    assert {'usage_role','reference_input_required','native_generation_required','pixel_copy_required','fidelity_mode'}.issubset(fields)
    assert c['source_binding_contract']['reference_input_semantics'].startswith('For native-reference modes')


def test_executor_never_fabricates_native_reference_use_or_native_product_render_evidence():
    from cbcc.provider_executor import _quality_observations
    required=[
        'source_product_asset_ids_used','source_product_hashes_used','product_reference_input_used',
        'native_product_rendered_in_final_output','product_identity_preserved'
    ]
    job={
        'production_mode':'AI_REFERENCE_PRODUCT',
        'production_quality_contract':{'product_fidelity':'REFERENCE_GUIDED_NATIVE_LOCK'},
        'source_product_bindings':[{'asset_id':'MASTER-FRONT','sha256':'a'*64}],
        'result_contract':{'quality_observations_required':required},
    }
    obs=_quality_observations(job,{})
    assert obs['source_product_asset_ids_used']==[]
    assert obs['source_product_hashes_used']=={}
    for key in ['product_reference_input_used','native_product_rendered_in_final_output','product_identity_preserved']:
        assert obs[key]['status']=='UNVERIFIED'
        assert obs[key]['evidence'] is None

    explicit={key:{'status':'PASS','evidence':'provider-attested'} for key in required[2:]}
    explicit['source_product_asset_ids_used']=['MASTER-FRONT']
    explicit['source_product_hashes_used']={'MASTER-FRONT':'a'*64}
    out=_quality_observations(job,{'quality_observations':explicit})
    assert out==explicit


def test_external_adapter_discovery_requires_and_supports_reference_image_input():
    from cbcc.provider_bridge import build_default_adapter_registry, ProviderExecutorBridge
    registry=build_default_adapter_registry(include_reference=True)
    matches=registry.discover(
        provider='EPV_ADAPTER',production_mode='AI_REFERENCE_PRODUCT',
        required_capabilities=['REFERENCE_IMAGE_INPUT','ASSET_HANDLE_LIFECYCLE']
    )
    assert matches
    assert all('REFERENCE_IMAGE_INPUT' in row['capabilities'] for row in matches)


def test_active_skill_has_no_lower_current_authority_that_redefines_product_fidelity():
    text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
    assert '### Product Reference / Fidelity — current authority' not in text
    assert '### Product Reference / Fidelity — compatibility note superseded by v0.6.35' in text
    assert 'REFERENCE_GUIDED_NATIVE_LOCK' in text
    assert 'EXACT_PIXEL_COMPOSITE' in text


def test_provider_default_mode_table_has_one_native_mode_entry_each():
    text=(ROOT/'runtime/cbcc/providers.py').read_text(encoding='utf-8')
    prefix=text.split('PROVIDER_REGISTRY=',1)[0]
    assert prefix.count("'AI_REFERENCE_PRODUCT':'AI_IMAGE_PROVIDER'")==1
    assert prefix.count("'AI_REFERENCE_HUMAN_PRODUCT':'AI_IMAGE_PROVIDER'")==1
