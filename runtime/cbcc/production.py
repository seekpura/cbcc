from __future__ import annotations
from pathlib import Path
from typing import Any
import json, yaml, hashlib
from .models import stable_hash
from .providers import route_production, validate_provider_result
from .provider_portability import materialize_portable_job_inputs, build_production_receipt_contract, production_receipt_template, validate_production_receipt, rebind_portable_execution_metadata


def _read_manifest(d:Path)->dict[str,Any]:
    return yaml.safe_load((d/'00_asset_manifest.yaml').read_text(encoding='utf-8')) or {}

def _read_json(path:Path, default=None):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {} if default is None else default



_REAL_PRODUCT_MODES={'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','VIDEO'}

def _sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def _source_product_bindings(manifest:dict[str,Any])->tuple[list[dict[str,Any]],list[dict[str,Any]]]:
    """Resolve production-time source bindings and re-check local-file integrity at handoff.

    Compile-time ingest status alone is not enough: a local master may move or change between
    package compilation and provider handoff. External handles remain explicit adapter bindings
    and are integrity-bound by their declared SHA256.
    """
    ready=[]; errors=[]
    for row in manifest.get('source_product_assets') or []:
        if not isinstance(row,dict):
            continue
        aid=row.get('asset_id'); handle=row.get('provider_asset_handle'); raw_path=row.get('path'); declared=str(row.get('sha256') or '').lower() or None
        locator_kind='PROVIDER_ASSET_HANDLE' if handle else ('LOCAL_FILE_PATH' if raw_path else 'UNRESOLVED')
        locator_value=handle or raw_path
        status='UNRESOLVED_AT_HANDOFF'; actual=None
        if handle and declared:
            status='READY_PROVIDER_HANDLE'
        elif raw_path:
            path=Path(str(raw_path)).expanduser()
            if path.exists() and path.is_file():
                actual=_sha256_file(path)
                status='READY_LOCAL_VERIFIED' if declared and actual==declared else ('LOCAL_HASH_MISMATCH' if declared else 'LOCAL_HASH_MISSING')
            else:
                status='LOCAL_FILE_MISSING_AT_HANDOFF'
        binding={
            'asset_id':aid,'role':row.get('role'),
            'locator':{'kind':locator_kind,'value':locator_value},
            'sha256':declared,'handoff_sha256':actual or declared,'handoff_status':status,
            'pixel_lock':bool(row.get('pixel_lock')),
            'allowed_transforms':list(row.get('allowed_transforms') or []),
            'identity_features':list(row.get('identity_features') or []),
        }
        if status in {'READY_PROVIDER_HANDLE','READY_LOCAL_VERIFIED'}:
            ready.append(binding)
        else:
            errors.append({'asset_id':aid,'status':status,'locator_kind':locator_kind})
    return ready,errors

def _usable_source_product_assets(manifest:dict[str,Any])->list[dict[str,Any]]:
    # Backward-compatible view for human/QA contracts; execution uses _source_product_bindings.
    bindings,_=_source_product_bindings(manifest)
    by_id={str(x.get('asset_id')):x for x in manifest.get('source_product_assets') or [] if isinstance(x,dict)}
    return [by_id[str(x.get('asset_id'))] for x in bindings if str(x.get('asset_id')) in by_id]

def _production_quality_contract(package_dir:Path, manifest:dict[str,Any])->dict[str,Any]:
    layout=_read_json(package_dir/'04_layout_contract.json',{})
    photo=_read_json(package_dir/'03_photography_contract.json',{})
    prompt_contract=_read_json(package_dir/'13_prompt_contract.json',{})
    fidelity=str(manifest.get('product_fidelity') or 'REFERENCE_CONSTRAINED').upper()
    mode=str(manifest.get('production_mode') or '').upper()
    signature=manifest.get('visual_production_signature') or layout.get('visual_production_signature') or {}
    edit=manifest.get('editable_layer_contract') or layout.get('editable_layer_contract') or {}
    source_bindings,source_binding_errors=_source_product_bindings(manifest)
    source_ids=[x.get('asset_id') for x in source_bindings if x.get('asset_id')]
    source_by_id={str(x.get('asset_id')):x for x in manifest.get('source_product_assets') or [] if isinstance(x,dict) and x.get('asset_id')}
    sources=[source_by_id[str(aid)] for aid in source_ids if str(aid) in source_by_id]
    real_product_required=(fidelity=='LOCKED_PIXEL' or mode in _REAL_PRODUCT_MODES) and mode not in {'AI_GENERATIVE','DOCUMENTATION'}
    preflight_errors=[]
    if real_product_required and not sources:
        preflight_errors.append('REAL_PRODUCT_MASTER_NOT_BOUND')
    if real_product_required and not source_bindings:
        preflight_errors.append('REAL_PRODUCT_MASTER_NOT_RESOLVABLE_AT_HANDOFF')
    if fidelity=='LOCKED_PIXEL' and source_bindings and not any(bool(x.get('pixel_lock')) for x in source_bindings):
        preflight_errors.append('LOCKED_PIXEL_MASTER_NOT_DECLARED')
    if fidelity=='LOCKED_PIXEL' and mode=='AI_GENERATIVE':
        preflight_errors.append('LOCKED_PIXEL_GENERATIVE_CONFLICT')
    required_observations=['decision_answer_visible','surface_contract_met','copy_visual_alignment','visual_differentiation_preserved']
    if mode in {'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','VIDEO'}:
        required_observations.append('photography_cmf_alignment')
    if fidelity=='LOCKED_PIXEL':
        required_observations += ['product_identity_preserved','source_product_asset_ids_used','source_product_hashes_used','product_layer_operation']
    return {
        'version':'0.6.12-portable-provider-package-production-receipt',
        'preflight_status':'READY' if not preflight_errors else 'HOLD',
        'preflight_errors':preflight_errors,
        'product_fidelity':fidelity,
        'production_mode':mode,
        'real_product_master_required':real_product_required,
        'source_product_assets':sources,
        'source_product_bindings':source_bindings,
        'source_product_binding_errors':source_binding_errors,
        'source_binding_hash':stable_hash(source_bindings),
        'source_product_asset_ids':source_ids,
        'locked_pixel_rule':('Use the exact supplied product master as an immutable pixel layer; preserve logo, packaging print, product color identity, geometry and proportions. Only contract-authorized placement/compositing transforms are permitted.' if fidelity=='LOCKED_PIXEL' else 'Preserve verified product identity and do not invent unsupported product detail.'),
        'visual_production_signature':signature,
        'surface_production_contracts':layout.get('surface_production_contracts') or [],
        'copy_visual_alignment':layout.get('copy_visual_alignment') or {'locked_visible_copy':layout.get('visible_copy') or {},'rule':'Visible copy must be visually attributable to the decision evidence shown.'},
        'photography_cmf_contract':{
            'status':photo.get('status') or 'SUPPLIED',
            'asset_reasoning':photo.get('asset_reasoning'),
            'capture_mode':photo.get('capture_mode'),
            'composition':photo.get('composition'),
            'camera':photo.get('camera'),
            'lighting':photo.get('lighting'),
            'color_management':photo.get('color_management'),
            'cmf':photo.get('cmf'),
        },
        'editable_layer_contract':edit,
        'canonical_prompt_contract':prompt_contract or {},
        'renderer_recipe':prompt_contract.get('renderer_recipe') or {},
        'qa_target_contract':prompt_contract.get('qa_target_contract') or {},
        'required_result_observations':list(dict.fromkeys(required_observations)),
        'review_dimensions':[
            {'dimension':'PRODUCT_FIDELITY','question':'Does the output preserve the exact product identity/master constraints?'},
            {'dimension':'DECISION_VISIBILITY','question':'Can a shopper recover the assigned decision answer from the actual output?'},
            {'dimension':'SURFACE_USABILITY','question':'Does the output work on the target surface rather than merely looking polished?'},
            {'dimension':'COPY_VISUAL_ALIGNMENT','question':'Does each locked copy line point to evidence visible in the frame?'},
            {'dimension':'PHOTOGRAPHY_CMF','question':'Do camera/light/material choices express the contract WHY without distorting product truth?'},
            {'dimension':'VISUAL_DIFFERENTIATION','question':'Does the output retain this asset decision-specific visual grammar rather than collapsing into the same layout as other assets?'},
        ],
        'principle':'This contract changes Provider execution and review targets; it is not an additional approval gate. Missing real-product masters block real-product handoff instead of being silently substituted.'
    }

def _quality_obs_state(value:Any)->tuple[str|None,Any]:
    if isinstance(value,dict):
        return str(value.get('status') or '').upper() or None, value.get('evidence') or value.get('observation') or value.get('notes')
    if value is True: return 'PASS',None
    if value is False: return 'FAIL',None
    return None,None

def _quality_result_issues(row:dict[str,Any], result:dict[str,Any])->list[str]:
    qc=row.get('production_quality_contract') or {}
    obs=result.get('quality_observations') or {}
    issues=[]
    special={'source_product_asset_ids_used','source_product_hashes_used','product_layer_operation'}
    for key in qc.get('required_result_observations') or []:
        if key not in obs or obs.get(key) in (None,'',[]):
            issues.append('QUALITY_OBSERVATION_MISSING:'+str(key)); continue
        if key not in special:
            status,evidence=_quality_obs_state(obs.get(key))
            if status not in {'PASS','PASSED','CONFIRMED','MET'}:
                issues.append('QUALITY_TARGET_NOT_CONFIRMED:'+str(key))
            elif str(qc.get('version') or '').startswith(('0.5.14','0.6.0','0.6.1','0.6.2','0.6.3','0.6.4','0.6.5','0.6.6')) and not evidence:
                issues.append('QUALITY_EVIDENCE_MISSING:'+str(key))
    fidelity=str(qc.get('product_fidelity') or '').upper()
    if fidelity=='LOCKED_PIXEL':
        identity_status,_identity_evidence=_quality_obs_state(obs.get('product_identity_preserved'))
        if identity_status not in {'PASS','PASSED','CONFIRMED','MET'}:
            issues.append('LOCKED_PIXEL_IDENTITY_NOT_CONFIRMED')
        operation=str(obs.get('product_layer_operation') or '').upper()
        if operation not in {'PLACEMENT_ONLY','COMPOSITE_LOCKED','NATIVE_CAPTURE_LOCKED'}:
            issues.append('LOCKED_PIXEL_OPERATION_INVALID')
        allowed=set(qc.get('source_product_asset_ids') or [])
        used=set(obs.get('source_product_asset_ids_used') or [])
        if allowed and (not used or not used.issubset(allowed)):
            issues.append('SOURCE_PRODUCT_ASSET_LINEAGE_MISMATCH')
        expected_hashes={str(x.get('asset_id')):str(x.get('sha256') or '') for x in qc.get('source_product_bindings') or [] if x.get('asset_id')}
        used_hashes=obs.get('source_product_hashes_used') or {}
        if isinstance(used_hashes,list):
            used_hashes={str(x.get('asset_id')):str(x.get('sha256') or '') for x in used_hashes if isinstance(x,dict) and x.get('asset_id')}
        if not isinstance(used_hashes,dict) or any(str(used_hashes.get(aid) or '')!=sha for aid,sha in expected_hashes.items() if aid in used):
            issues.append('SOURCE_PRODUCT_HASH_LINEAGE_MISMATCH')
    return list(dict.fromkeys(issues))


def _production_contract_binding(package_dir:Path)->dict[str,Any]:
    layout=_read_json(package_dir/'04_layout_contract.json',{})
    photo=_read_json(package_dir/'03_photography_contract.json',{})
    prompt_contract=_read_json(package_dir/'13_prompt_contract.json',{})
    surface=layout.get('surface_production_contracts') or []
    reasoning=(photo.get('asset_reasoning') or {}).get('shot_lighting_reasoning') if isinstance(photo,dict) else None
    return {
        'surface_production_contracts':surface,
        'platform_pack_bindings':[x.get('platform_pack_binding') for x in surface if isinstance(x,dict) and x.get('platform_pack_binding')],
        'shot_lighting_reasoning':reasoning,
        'layout_contract_hash':stable_hash(layout),
        'photography_contract_hash':stable_hash(photo),
        'prompt_contract_hash':stable_hash(prompt_contract),
        'canonical_prompt_contract':prompt_contract or {},
        'renderer_recipe':prompt_contract.get('renderer_recipe') or {},
        'binding_rule':'Provider execution is bound to the frozen asset package plus these contract hashes. Any changed contract requires a new package hash/job.'
    }

def build_production_run(asset_packages_root:Path, provider_preferences:dict[str,Any]|None=None, requested_asset_ids:list[str]|None=None, revision_scope:dict[str,Any]|None=None)->dict[str,Any]:
    """Create an execution run from frozen compiled packages without re-planning them."""
    root=Path(asset_packages_root); idx=json.loads((root/'ASSET_PACKAGE_INDEX.json').read_text(encoding='utf-8')); requested=set(requested_asset_ids or [])
    rows=[]
    for item in idx.get('assets',[]):
        aid=item['asset_id']
        if requested and aid not in requested: continue
        d=root/aid; mf=_read_manifest(d)
        package_hash=stable_hash({f.name:f.read_text(encoding='utf-8') for f in sorted(d.iterdir()) if f.is_file()})
        route=route_production(mf,provider_preferences)
        contract_binding=_production_contract_binding(d)
        quality_contract=_production_quality_contract(d,mf)
        if mf.get('status')!='ACTIVATE':
            handoff_status='SKIP_'+str(mf.get('status'))
        elif route.get('route_status')!='READY':
            handoff_status='HOLD_PROVIDER'
        elif quality_contract.get('preflight_status')!='READY':
            handoff_status='HOLD_REAL_PRODUCT_PREFLIGHT'
        else:
            handoff_status='READY_TO_HANDOFF'
        rows.append({'asset_id':aid,'package_hash':package_hash,'provider':route['provider'],'provider_contract':route.get('provider_contract'),'production_mode':mf.get('production_mode'),'status':handoff_status,
                     'production_contract_binding':contract_binding,'production_quality_contract':quality_contract,'execution_authorized':False,'revision_scope':revision_scope if revision_scope and revision_scope.get('asset_id')==aid else None,'frozen_strategy':True})
    return {'status':'RUN_COMPILED','asset_count':len(rows),'assets':rows,'replanning_allowed':False,'one_asset_one_output':True,'preflight_holds':[{'asset_id':x.get('asset_id'),'errors':(x.get('production_quality_contract') or {}).get('preflight_errors',[])} for x in rows if x.get('status')=='HOLD_REAL_PRODUCT_PREFLIGHT']}


def apply_production_result(run:dict[str,Any], results:list[dict[str,Any]])->dict[str,Any]:
    by={r.get('asset_id'):r for r in results}; out=[]; issues=[]
    for row in run.get('assets',[]):
        r=by.get(row['asset_id'])
        if not r:
            out.append({**row,'result_status':'MISSING'}); issues.append({'asset_id':row['asset_id'],'code':'MISSING_RESULT'}); continue
        contract_row=row
        if r.get('_provider_job_ingest'):
            contract_row={**row}
            if isinstance(row.get('provider_job_quality_contract'),dict): contract_row['production_quality_contract']=row['provider_job_quality_contract']
            if isinstance(row.get('provider_job_contract_binding'),dict): contract_row['production_contract_binding']=row['provider_job_contract_binding']
        local=[]
        if row.get('status')!='READY_TO_HANDOFF': local.append('PRODUCTION_PREFLIGHT_NOT_READY')
        local.extend(validate_provider_result({'provider':row.get('provider'),'provider_contract':row.get('provider_contract')},r))
        local.extend(_quality_result_issues(contract_row,r))
        local.extend(validate_production_receipt(contract_row,r))
        if r.get('package_hash') != row.get('package_hash'):
            local.append('PACKAGE_HASH_MISMATCH')
        binding=contract_row.get('production_contract_binding') or {}
        fidelity=str((contract_row.get('production_quality_contract') or {}).get('product_fidelity') or '').upper()
        if (fidelity=='LOCKED_PIXEL' and r.get('production_contract_ack') is not True) or ('production_contract_ack' in r and not r.get('production_contract_ack')):
            local.append('PRODUCTION_CONTRACT_NOT_ACKNOWLEDGED')
        if r.get('layout_contract_hash') and r.get('layout_contract_hash') != binding.get('layout_contract_hash'):
            local.append('LAYOUT_CONTRACT_HASH_MISMATCH')
        if r.get('photography_contract_hash') and r.get('photography_contract_hash') != binding.get('photography_contract_hash'):
            local.append('PHOTOGRAPHY_CONTRACT_HASH_MISMATCH')
        if r.get('prompt_contract_hash') and r.get('prompt_contract_hash') != binding.get('prompt_contract_hash'):
            local.append('PROMPT_CONTRACT_HASH_MISMATCH')
        qc=contract_row.get('production_quality_contract') or {}
        expected_source_binding_hash=qc.get('source_binding_hash')
        if str(qc.get('product_fidelity') or '').upper()=='LOCKED_PIXEL':
            if not r.get('source_binding_hash') or r.get('source_binding_hash')!=expected_source_binding_hash:
                local.append('SOURCE_BINDING_HASH_MISMATCH')
        edit=qc.get('editable_layer_contract') or {}
        frozen_layers=set(edit.get('frozen_layers') or [])
        changed_layers=set(r.get('changed_layers') or [])
        if changed_layers & frozen_layers:
            local.append('FROZEN_LAYER_MUTATION_REPORTED')
        scope=row.get('revision_scope') or {}
        if scope:
            allowed=set(scope.get('allowed_fields',[])); changed=set(r.get('changed_fields',[]))
            if changed-allowed: local.append('REVISION_SCOPE_VIOLATION')
            allowed_layers=set(scope.get('allowed_layers') or [])
            if not isinstance(r.get('changed_layers'),list): local.append('REVISION_CHANGED_LAYERS_MISSING')
            elif allowed_layers and changed_layers-allowed_layers: local.append('REVISION_LAYER_SCOPE_VIOLATION')
        qa=r.get('qa') or {}; pass_required=all(bool(qa.get(k)) for k in ['product','fact','claim','visual','culture','platform'])
        if not pass_required: local.append('QA_INCOMPLETE')
        result_status='PASS' if not local else 'REVIEW_REQUIRED'
        receipt=r.get('production_receipt') if isinstance(r.get('production_receipt'),dict) else None
        out.append({**row,'result_status':result_status,'output_path':r.get('output_path'),'qa':qa,'changed_fields':r.get('changed_fields',[]),'changed_layers':r.get('changed_layers',[]),'quality_observations':r.get('quality_observations') or {},'provider_metadata':r.get('provider_metadata') or {},'production_receipt':receipt,'production_receipt_hash':stable_hash(receipt) if receipt else None})
        for code in local: issues.append({'asset_id':row['asset_id'],'code':code})
    return {'status':'COMPLETE' if not issues else 'REVIEW_REQUIRED','assets':out,'issues':issues}


def materialize_provider_jobs(asset_packages_root:Path, run:dict[str,Any], jobs_root:Path)->dict[str,Any]:
    """Create self-contained provider job envelopes from frozen production rows.

    Local product masters are copied into each job and rebound to PACKAGE_RELATIVE_PATH. The exact
    frozen asset package is copied under inputs/asset_package for package lineage. Provider handles
    remain explicit external handles. job.json itself never needs the CBCC host's absolute path.
    """
    root=Path(asset_packages_root); jobs=Path(jobs_root); jobs.mkdir(parents=True,exist_ok=True)
    index=[]; holds=[]
    for row in run.get('assets',[]):
        if row.get('status')!='READY_TO_HANDOFF': continue
        aid=row['asset_id']; d=jobs/aid; d.mkdir(parents=True,exist_ok=True)
        package_dir=root/aid
        upstream_qc=row.get('production_quality_contract') or {}
        portable=materialize_portable_job_inputs(package_dir,d,upstream_qc.get('source_product_bindings') or [])
        if portable.get('status')!='READY':
            row['status']='HOLD_PORTABLE_PROVIDER_PACKAGE'
            row['portable_package_errors']=portable.get('errors') or []
            holds.append({'asset_id':aid,'errors':row['portable_package_errors']})
            continue
        portable_bindings=portable.get('source_product_bindings') or []
        portable_hash=portable.get('portable_source_binding_hash')

        quality=json.loads(json.dumps(upstream_qc))
        quality['source_binding_hash_upstream']=quality.get('source_binding_hash')
        quality['source_product_bindings']=portable_bindings
        quality['source_binding_hash']=portable_hash
        quality['provider_job_portability']={'status':'PORTABLE','portable_manifest_hash':portable.get('portable_manifest_hash'),'package_ref':'inputs/asset_package'}
        if isinstance(quality.get('renderer_recipe'),dict):
            quality['renderer_recipe']['source_product_bindings']=portable_bindings
        canonical=quality.get('canonical_prompt_contract') or {}
        if isinstance(canonical,dict) and isinstance(canonical.get('renderer_recipe'),dict):
            canonical['renderer_recipe']['source_product_bindings']=portable_bindings
        quality['canonical_prompt_contract']=canonical
        quality=rebind_portable_execution_metadata(quality,upstream_qc.get('source_product_bindings') or [],portable_bindings)
        quality.setdefault('provider_job_portability',{})['host_source_paths_rebound']=True

        binding=json.loads(json.dumps(row.get('production_contract_binding') or {}))
        if isinstance(binding.get('renderer_recipe'),dict):
            binding['renderer_recipe']['source_product_bindings']=portable_bindings
        bound_canonical=binding.get('canonical_prompt_contract') or {}
        if isinstance(bound_canonical,dict) and isinstance(bound_canonical.get('renderer_recipe'),dict):
            bound_canonical['renderer_recipe']['source_product_bindings']=portable_bindings
        binding['canonical_prompt_contract']=bound_canonical
        binding=rebind_portable_execution_metadata(binding,upstream_qc.get('source_product_bindings') or [],portable_bindings)

        job_id='JOB-'+stable_hash([aid,row.get('package_hash'),row.get('provider'),portable.get('portable_manifest_hash')])[:14]
        row['provider_job_quality_contract']=quality
        row['provider_job_contract_binding']=binding
        row['provider_job_source_binding_hash']=portable_hash
        row['provider_job_source_product_bindings']=portable_bindings
        row['provider_job_id']=job_id
        row['portable_job_manifest_hash']=portable.get('portable_manifest_hash')
        receipt_contract=build_production_receipt_contract(
            job_id,aid,row.get('provider'),row.get('package_hash'),portable_hash,row.get('production_mode'),quality.get('product_fidelity'),portable.get('portable_manifest_hash')
        )
        row['production_receipt_contract']=receipt_contract
        job={
            'job_id':job_id,
            'asset_id':aid,
            'provider':row.get('provider'),
            'adapter':(row.get('provider_contract') or {}).get('adapter','FILE_HANDOFF'),
            'production_mode':row.get('production_mode'),
            'package_hash':row.get('package_hash'),
            'package_ref':{'kind':'PACKAGE_RELATIVE_PATH','value':'inputs/asset_package'},
            'portable_package':{
                'manifest':'PORTABLE_JOB_MANIFEST.json',
                'portable_manifest_hash':portable.get('portable_manifest_hash'),
                'upstream_source_binding_hash':portable.get('upstream_source_binding_hash'),
                'source_binding_hash':portable_hash,
            },
            'provider_contract':row.get('provider_contract'),
            'production_contract_binding':binding,
            'production_quality_contract':quality,
            'source_product_bindings':portable_bindings,
            'source_binding_hash':portable_hash,
            'execution_brief':{
                'primary_decision_job':(quality.get('visual_production_signature') or {}).get('visual_job'),
                'visual_information_grammar':(quality.get('visual_production_signature') or {}).get('composition_grammar'),
                'decision_critical_evidence_plane':(quality.get('visual_production_signature') or {}).get('evidence_plane'),
                'differentiation_axis':(quality.get('visual_production_signature') or {}).get('differentiation_axis'),
                'locked_pixel_rule':quality.get('locked_pixel_rule'),
                'source_product_bindings':portable_bindings,
                'source_binding_hash':portable_hash,
                'copy_visual_alignment':quality.get('copy_visual_alignment'),
                'photography_cmf_contract':quality.get('photography_cmf_contract'),
                'editable_layer_contract':quality.get('editable_layer_contract'),
                'canonical_prompt_contract':quality.get('canonical_prompt_contract'),
                'renderer_recipe':quality.get('renderer_recipe'),
                'qa_target_contract':quality.get('qa_target_contract'),
            },
            'revision_scope':row.get('revision_scope'),
            'execution_policy':{
                'replanning_allowed':False,'one_asset_one_output':True,'return_same_package_hash':True,
                'contract_binding_must_not_change':True,'real_product_master_substitution_allowed':False,
                'portable_job_required':True,'host_absolute_paths_are_not_execution_locators':True,
            },
            'production_receipt_contract':receipt_contract,
            'result_contract':{
                'required':['asset_id','provider','package_hash','output_path','qa','quality_observations','production_receipt'] + (['source_binding_hash','production_contract_ack'] if str(quality.get('product_fidelity') or '').upper()=='LOCKED_PIXEL' else []) + (['changed_fields','changed_layers'] if row.get('revision_scope') else []),
                'qa_required':['product','fact','claim','visual','culture','platform'],
                'quality_observations_required':quality.get('required_result_observations',[]),
                'optional':['changed_fields','changed_layers','provider_metadata','production_contract_ack','source_binding_hash','layout_contract_hash','photography_contract_hash','prompt_contract_hash']
            }
        }
        (d/'job.json').write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
        qkeys=quality.get('required_result_observations',[])
        qobs={k:([] if k=='source_product_asset_ids_used' else ({} if k=='source_product_hashes_used' else ('' if k=='product_layer_operation' else {'status':'UNVERIFIED','evidence':None}))) for k in qkeys}
        template={
            'asset_id':aid,'provider':row.get('provider'),'package_hash':row.get('package_hash'),'output_path':'',
            'changed_fields':[],'changed_layers':[],
            'qa':{'product':False,'fact':False,'claim':False,'visual':False,'culture':False,'platform':False},
            'quality_observations':qobs,'provider_metadata':{},'production_contract_ack':False,'source_binding_hash':portable_hash,
            'layout_contract_hash':binding.get('layout_contract_hash'),'photography_contract_hash':binding.get('photography_contract_hash'),'prompt_contract_hash':binding.get('prompt_contract_hash'),
            'production_receipt':production_receipt_template(receipt_contract),
        }
        (d/'result.template.json').write_text(json.dumps(template,ensure_ascii=False,indent=2),encoding='utf-8')
        index.append({
            'asset_id':aid,'job_id':job_id,'provider':job['provider'],'adapter':job['adapter'],
            'job_path':str(d/'job.json'),'result_path':str(d/'result.json'),
            'portable_manifest_path':str(d/'PORTABLE_JOB_MANIFEST.json'),'portable_manifest_hash':portable.get('portable_manifest_hash'),
        })
    manifest={
        'status':'JOBS_MATERIALIZED' if not holds else 'JOBS_MATERIALIZED_WITH_HOLDS',
        'job_count':len(index),'jobs':index,'holds':holds,
        'authority_note':'Each provider job is a self-contained execution envelope. Local masters are copied and rebound to package-relative locators; returned external results require a production receipt that binds job/package/source/output lineage.'
    }
    (jobs/'PROVIDER_JOB_INDEX.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest

def ingest_provider_job_results(run:dict[str,Any], jobs_root:Path)->dict[str,Any]:
    """Read external provider result.json files and require portable production receipts."""
    jobs=Path(jobs_root); results=[]; missing=[]
    for row in run.get('assets',[]):
        if row.get('status')!='READY_TO_HANDOFF': continue
        rp=jobs/row['asset_id']/'result.json'
        if not rp.exists(): missing.append(row['asset_id']); continue
        try:
            result=json.loads(rp.read_text(encoding='utf-8'))
            result['_provider_job_ingest']=True
            result['_provider_job_dir']=str(rp.parent)
            results.append(result)
        except Exception as e:
            results.append({'asset_id':row['asset_id'],'provider':row.get('provider'),'package_hash':row.get('package_hash'),'output_path':None,'qa':{},'_provider_job_ingest':True,'_provider_job_dir':str(rp.parent),'_parse_error':f'{type(e).__name__}: {e}'})
    applied=apply_production_result(run,results)
    if missing:
        existing={x['asset_id'] for x in applied.get('issues',[])}
        for aid in missing:
            if aid not in existing: applied.setdefault('issues',[]).append({'asset_id':aid,'code':'PROVIDER_RESULT_NOT_RETURNED'})
        applied['status']='REVIEW_REQUIRED'
    applied['provider_results_ingested']=len(results); applied['provider_results_missing']=missing
    return applied
