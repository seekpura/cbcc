from __future__ import annotations
from pathlib import Path
from typing import Any
import json, yaml
from .models import stable_hash
from .providers import route_production, validate_provider_result


def _read_manifest(d:Path)->dict[str,Any]:
    return yaml.safe_load((d/'00_asset_manifest.yaml').read_text(encoding='utf-8')) or {}

def _read_json(path:Path, default=None):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {} if default is None else default



_REAL_PRODUCT_MODES={'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','VIDEO'}

def _usable_source_product_assets(manifest:dict[str,Any])->list[dict[str,Any]]:
    out=[]
    for row in manifest.get('source_product_assets') or []:
        if not isinstance(row,dict): continue
        status=str(row.get('ingest_status') or '').upper()
        if row.get('sha256') and status in {'HASH_VERIFIED_LOCAL','EXTERNAL_HANDLE_HASH_DECLARED'}:
            out.append(row)
    return out

def _production_quality_contract(package_dir:Path, manifest:dict[str,Any])->dict[str,Any]:
    layout=_read_json(package_dir/'04_layout_contract.json',{})
    photo=_read_json(package_dir/'03_photography_contract.json',{})
    prompt_contract=_read_json(package_dir/'13_prompt_contract.json',{})
    fidelity=str(manifest.get('product_fidelity') or 'REFERENCE_CONSTRAINED').upper()
    mode=str(manifest.get('production_mode') or '').upper()
    signature=manifest.get('visual_production_signature') or layout.get('visual_production_signature') or {}
    edit=manifest.get('editable_layer_contract') or layout.get('editable_layer_contract') or {}
    sources=_usable_source_product_assets(manifest)
    source_ids=[x.get('asset_id') for x in sources if x.get('asset_id')]
    real_product_required=(fidelity=='LOCKED_PIXEL' or mode in _REAL_PRODUCT_MODES) and mode not in {'AI_GENERATIVE','DOCUMENTATION'}
    preflight_errors=[]
    if real_product_required and not sources:
        preflight_errors.append('REAL_PRODUCT_MASTER_NOT_BOUND')
    if fidelity=='LOCKED_PIXEL' and sources and not any(bool(x.get('pixel_lock')) for x in sources):
        preflight_errors.append('LOCKED_PIXEL_MASTER_NOT_DECLARED')
    if fidelity=='LOCKED_PIXEL' and mode=='AI_GENERATIVE':
        preflight_errors.append('LOCKED_PIXEL_GENERATIVE_CONFLICT')
    required_observations=['decision_answer_visible','surface_contract_met','copy_visual_alignment','visual_differentiation_preserved']
    if mode in {'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','VIDEO'}:
        required_observations.append('photography_cmf_alignment')
    if fidelity=='LOCKED_PIXEL':
        required_observations += ['product_identity_preserved','source_product_asset_ids_used','product_layer_operation']
    return {
        'version':'0.6.7-semantic-workspaces',
        'preflight_status':'READY' if not preflight_errors else 'HOLD',
        'preflight_errors':preflight_errors,
        'product_fidelity':fidelity,
        'production_mode':mode,
        'real_product_master_required':real_product_required,
        'source_product_assets':sources,
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
    special={'source_product_asset_ids_used','product_layer_operation'}
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
        local=[]
        if row.get('status')!='READY_TO_HANDOFF': local.append('PRODUCTION_PREFLIGHT_NOT_READY')
        local.extend(validate_provider_result({'provider':row.get('provider'),'provider_contract':row.get('provider_contract')},r))
        local.extend(_quality_result_issues(row,r))
        if r.get('package_hash') != row.get('package_hash'):
            local.append('PACKAGE_HASH_MISMATCH')
        binding=row.get('production_contract_binding') or {}
        if 'production_contract_ack' in r and not r.get('production_contract_ack'):
            local.append('PRODUCTION_CONTRACT_NOT_ACKNOWLEDGED')
        if r.get('layout_contract_hash') and r.get('layout_contract_hash') != binding.get('layout_contract_hash'):
            local.append('LAYOUT_CONTRACT_HASH_MISMATCH')
        if r.get('photography_contract_hash') and r.get('photography_contract_hash') != binding.get('photography_contract_hash'):
            local.append('PHOTOGRAPHY_CONTRACT_HASH_MISMATCH')
        if r.get('prompt_contract_hash') and r.get('prompt_contract_hash') != binding.get('prompt_contract_hash'):
            local.append('PROMPT_CONTRACT_HASH_MISMATCH')
        scope=row.get('revision_scope') or {}
        if scope:
            allowed=set(scope.get('allowed_fields',[])); changed=set(r.get('changed_fields',[]))
            if changed-allowed: local.append('REVISION_SCOPE_VIOLATION')
        qa=r.get('qa') or {}; pass_required=all(bool(qa.get(k)) for k in ['product','fact','claim','visual','culture','platform'])
        if not pass_required: local.append('QA_INCOMPLETE')
        result_status='PASS' if not local else 'REVIEW_REQUIRED'
        out.append({**row,'result_status':result_status,'output_path':r.get('output_path'),'qa':qa,'changed_fields':r.get('changed_fields',[]),'quality_observations':r.get('quality_observations') or {},'provider_metadata':r.get('provider_metadata') or {}})
        for code in local: issues.append({'asset_id':row['asset_id'],'code':code})
    return {'status':'COMPLETE' if not issues else 'REVIEW_REQUIRED','assets':out,'issues':issues}


def materialize_provider_jobs(asset_packages_root:Path, run:dict[str,Any], jobs_root:Path)->dict[str,Any]:
    """Create provider-neutral filesystem job envelopes from frozen production rows.

    This is an execution adapter boundary: external/human providers can consume job.json and
    return result.json without receiving authority-state internals or permission to re-plan.
    """
    root=Path(asset_packages_root); jobs=Path(jobs_root); jobs.mkdir(parents=True,exist_ok=True)
    index=[]
    for row in run.get('assets',[]):
        if row.get('status')!='READY_TO_HANDOFF': continue
        aid=row['asset_id']; d=jobs/aid; d.mkdir(parents=True,exist_ok=True)
        package_dir=root/aid
        job={
            'job_id':'JOB-'+stable_hash([aid,row.get('package_hash'),row.get('provider')])[:14],
            'asset_id':aid,
            'provider':row.get('provider'),
            'adapter':(row.get('provider_contract') or {}).get('adapter','FILE_HANDOFF'),
            'production_mode':row.get('production_mode'),
            'package_hash':row.get('package_hash'),
            'package_dir':str(package_dir),
            'provider_contract':row.get('provider_contract'),
            'production_contract_binding':row.get('production_contract_binding'),
            'production_quality_contract':row.get('production_quality_contract'),
            'execution_brief':{
                'primary_decision_job':((row.get('production_quality_contract') or {}).get('visual_production_signature') or {}).get('visual_job'),
                'visual_information_grammar':((row.get('production_quality_contract') or {}).get('visual_production_signature') or {}).get('composition_grammar'),
                'decision_critical_evidence_plane':((row.get('production_quality_contract') or {}).get('visual_production_signature') or {}).get('evidence_plane'),
                'differentiation_axis':((row.get('production_quality_contract') or {}).get('visual_production_signature') or {}).get('differentiation_axis'),
                'locked_pixel_rule':(row.get('production_quality_contract') or {}).get('locked_pixel_rule'),
                'copy_visual_alignment':(row.get('production_quality_contract') or {}).get('copy_visual_alignment'),
                'photography_cmf_contract':(row.get('production_quality_contract') or {}).get('photography_cmf_contract'),
                'editable_layer_contract':(row.get('production_quality_contract') or {}).get('editable_layer_contract'),
                'canonical_prompt_contract':(row.get('production_quality_contract') or {}).get('canonical_prompt_contract'),
                'renderer_recipe':(row.get('production_quality_contract') or {}).get('renderer_recipe'),
                'qa_target_contract':(row.get('production_quality_contract') or {}).get('qa_target_contract'),
            },
            'revision_scope':row.get('revision_scope'),
            'execution_policy':{'replanning_allowed':False,'one_asset_one_output':True,'return_same_package_hash':True,'contract_binding_must_not_change':True,'real_product_master_substitution_allowed':False},
            'result_contract':{
                'required':['asset_id','provider','package_hash','output_path','qa','quality_observations'],
                'qa_required':['product','fact','claim','visual','culture','platform'],
                'quality_observations_required':(row.get('production_quality_contract') or {}).get('required_result_observations',[]),
                'optional':['changed_fields','provider_metadata','layer_manifest','capture_metadata','production_contract_ack','layout_contract_hash','photography_contract_hash','prompt_contract_hash']
            }
        }
        (d/'job.json').write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
        qkeys=(row.get('production_quality_contract') or {}).get('required_result_observations',[])
        qobs={k:([] if k=='source_product_asset_ids_used' else ('' if k=='product_layer_operation' else {'status':'UNVERIFIED','evidence':None})) for k in qkeys}
        (d/'result.template.json').write_text(json.dumps({'asset_id':aid,'provider':row.get('provider'),'package_hash':row.get('package_hash'),'output_path':'','changed_fields':[],'qa':{'product':False,'fact':False,'claim':False,'visual':False,'culture':False,'platform':False},'quality_observations':qobs,'provider_metadata':{},'production_contract_ack':False,'layout_contract_hash':(row.get('production_contract_binding') or {}).get('layout_contract_hash'),'photography_contract_hash':(row.get('production_contract_binding') or {}).get('photography_contract_hash'),'prompt_contract_hash':(row.get('production_contract_binding') or {}).get('prompt_contract_hash')},ensure_ascii=False,indent=2),encoding='utf-8')
        index.append({'asset_id':aid,'job_id':job['job_id'],'provider':job['provider'],'adapter':job['adapter'],'job_path':str(d/'job.json'),'result_path':str(d/'result.json')})
    manifest={'status':'JOBS_MATERIALIZED','job_count':len(index),'jobs':index,'authority_note':'Jobs are frozen execution envelopes carrying asset-specific real-product, visual, surface, copy and photography/CMF production contracts. Provider completion is not inferred until a result is explicitly ingested; provider completion is still not independent review acceptance.'}
    (jobs/'PROVIDER_JOB_INDEX.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest


def ingest_provider_job_results(run:dict[str,Any], jobs_root:Path)->dict[str,Any]:
    """Read explicit provider result.json files and apply the same production validation contract."""
    jobs=Path(jobs_root); results=[]; missing=[]
    for row in run.get('assets',[]):
        if row.get('status')!='READY_TO_HANDOFF': continue
        rp=jobs/row['asset_id']/'result.json'
        if not rp.exists(): missing.append(row['asset_id']); continue
        try: results.append(json.loads(rp.read_text(encoding='utf-8')))
        except Exception as e: results.append({'asset_id':row['asset_id'],'provider':row.get('provider'),'package_hash':row.get('package_hash'),'output_path':None,'qa':{},'_parse_error':f'{type(e).__name__}: {e}'})
    applied=apply_production_result(run,results)
    if missing:
        existing={x['asset_id'] for x in applied.get('issues',[])}
        for aid in missing:
            if aid not in existing: applied.setdefault('issues',[]).append({'asset_id':aid,'code':'PROVIDER_RESULT_NOT_RETURNED'})
        applied['status']='REVIEW_REQUIRED'
    applied['provider_results_ingested']=len(results); applied['provider_results_missing']=missing
    return applied
