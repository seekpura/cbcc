from __future__ import annotations
from typing import Any

DEFAULT_PROVIDER_BY_MODE={
    'REAL_PHOTO':'HUMAN_PHOTOGRAPHY',
    'REAL_PRODUCT_COMPOSITE':'COMPOSITE_PIPELINE',
    'AI_ENVIRONMENT_REAL_PRODUCT':'COMPOSITE_PIPELINE',
    'AI_HUMAN_REAL_PRODUCT':'COMPOSITE_PIPELINE',
    'AI_GENERATIVE':'AI_IMAGE_PROVIDER',
    'GRAPHIC_DESIGN':'HUMAN_OR_DESIGN_PROVIDER',
    'THREE_D':'CG_3D_PROVIDER',
    'VIDEO':'VIDEO_PROVIDER',
    'DOCUMENTATION':'DOCUMENT_RENDERER'
}

PROVIDER_REGISTRY={
    'HUMAN_PHOTOGRAPHY': {'modes':['REAL_PHOTO'],'locked_pixel':'NATIVE_CAPTURE','human_review':True,'adapter':'FILE_HANDOFF','outputs':['image','capture_metadata','qa']},
    'COMPOSITE_PIPELINE': {'modes':['REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT'],'locked_pixel':'SUPPORTED','human_review':True,'adapter':'FILE_HANDOFF','outputs':['image','layer_manifest','qa']},
    'AI_IMAGE_PROVIDER': {'modes':['AI_GENERATIVE'],'locked_pixel':'NOT_APPLICABLE','human_review':True,'adapter':'FILE_HANDOFF','outputs':['image','generation_metadata','qa']},
    'HUMAN_OR_DESIGN_PROVIDER': {'modes':['GRAPHIC_DESIGN'],'locked_pixel':'SUPPORTED_BY_PLACEMENT','human_review':True,'adapter':'FILE_HANDOFF','outputs':['design','export','qa']},
    'CG_3D_PROVIDER': {'modes':['THREE_D'],'locked_pixel':'REFERENCE_ONLY','human_review':True,'adapter':'FILE_HANDOFF','outputs':['render','scene_manifest','qa']},
    'VIDEO_PROVIDER': {'modes':['VIDEO'],'locked_pixel':'SUPPORTED_BY_COMPOSITE','human_review':True,'adapter':'FILE_HANDOFF','outputs':['video','edit_manifest','qa']},
    'DOCUMENT_RENDERER': {'modes':['DOCUMENTATION'],'locked_pixel':'NOT_APPLICABLE','human_review':False,'adapter':'FILE_HANDOFF','outputs':['document','qa']},
    'EPV_ADAPTER': {'modes':['REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','AI_GENERATIVE','GRAPHIC_DESIGN','THREE_D','VIDEO'],'locked_pixel':'CONTRACT_DRIVEN','human_review':True,'adapter':'EXTERNAL_ADAPTER','outputs':['provider_manifest','artifact','qa']},
}


def provider_contract(provider:str, mode:str, asset:dict[str,Any])->dict[str,Any]:
    spec=PROVIDER_REGISTRY.get(provider)
    if not spec:
        return {'status':'UNSUPPORTED_PROVIDER','provider':provider,'production_mode':mode,'errors':['PROVIDER_NOT_REGISTERED']}
    errors=[]
    if mode not in spec['modes']: errors.append('MODE_NOT_SUPPORTED_BY_PROVIDER')
    fidelity=asset.get('product_fidelity')
    if fidelity=='LOCKED_PIXEL' and spec.get('locked_pixel') in {'NOT_APPLICABLE','REFERENCE_ONLY'}:
        errors.append('LOCKED_PIXEL_PROVIDER_MISMATCH')
    required_inputs=['asset_manifest','strategy','visual_spec','source_trace','layout_contract','surface_production_contract','design_card','canonical_prompt_contract','renderer_recipe']
    real_product_mode=mode in {'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','VIDEO'}
    source_binding_required=bool(real_product_mode or fidelity=='LOCKED_PIXEL')
    if source_binding_required: required_inputs.extend(['source_product_assets','source_product_bindings'])
    if real_product_mode: required_inputs.extend(['photography_contract','shot_lighting_reasoning'])
    return {
        'status':'READY' if not errors else 'HOLD','provider':provider,'production_mode':mode,'product_fidelity':fidelity,
        'required_inputs':required_inputs,'expected_outputs':spec['outputs'],'human_review_required':spec['human_review'],
        'adapter':spec.get('adapter','FILE_HANDOFF'),'locked_pixel_support':spec['locked_pixel'],
        'source_binding_contract':{
            'required': source_binding_required,
            'resolver_precedence':['PROVIDER_ASSET_HANDLE','LOCAL_FILE_PATH'],
            'integrity_key':'sha256',
            'required_binding_fields':['asset_id','locator','sha256','pixel_lock','allowed_transforms','identity_features'],
            'locked_pixel_result_evidence':['source_product_asset_ids_used','source_product_hashes_used','product_layer_operation','product_identity_preserved'] if fidelity=='LOCKED_PIXEL' else [],
        },
        'errors':errors
    }


def route_production(asset:dict[str,Any],preferences:dict[str,Any]|None=None)->dict[str,Any]:
    preferences=preferences or {}; mode=asset.get('production_mode','GRAPHIC_DESIGN')
    requested=preferences.get(asset.get('asset_id')) or preferences.get(mode)
    provider=requested or DEFAULT_PROVIDER_BY_MODE.get(mode,'HUMAN_OR_DESIGN_PROVIDER')
    contract=provider_contract(provider,mode,asset)
    return {'asset_id':asset.get('asset_id'),'production_mode':mode,'provider':provider,
            'handoff_contract':'EXTERNAL_EXECUTION_CONTRACT','execution_authorized':False,
            'provider_contract':contract,'route_status':'READY' if contract['status']=='READY' else 'HOLD',
            'note':'Routing selects and validates a production provider contract; it does not claim the external provider executed or approved the asset.'}


def validate_provider_result(route:dict[str,Any], result:dict[str,Any])->list[str]:
    issues=[]; contract=route.get('provider_contract') or {}
    if contract.get('status')!='READY': issues.append('PROVIDER_CONTRACT_NOT_READY')
    if result.get('provider') and result.get('provider')!=route.get('provider'): issues.append('PROVIDER_ID_MISMATCH')
    if not result.get('output_path'): issues.append('OUTPUT_PATH_MISSING')
    return issues
