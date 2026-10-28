from __future__ import annotations
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import hashlib, json
from .models import stable_hash
from .production import build_production_run, materialize_provider_jobs, ingest_provider_job_results
from .strategy_authority import materialize_strategy


def _now()->str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path:Path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return {} if default is None else default


def _write_json(path:Path, data:Any)->str:
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    return str(path)


def _file_sha256(path:Path)->str|None:
    path=Path(path)
    if not path.exists() or not path.is_file(): return None
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def _revision_index(project_dir:Path)->dict[str,Any]:
    p=Path(project_dir)/'artifacts/local_revisions/LOCAL_REVISION_INDEX.json'
    data=_read_json(p,{'status':'LOCAL_REVISION_INDEX','revisions':[]})
    data.setdefault('revisions',[])
    return data


def _save_revision_index(project_dir:Path, data:dict[str,Any])->str:
    data['status']='LOCAL_REVISION_INDEX'
    data['revision_count']=len(data.get('revisions') or [])
    return _write_json(Path(project_dir)/'artifacts/local_revisions/LOCAL_REVISION_INDEX.json',data)




def _revision_layer_for_field(field:str)->str|None:
    f=str(field or '').casefold()
    if any(x in f for x in ['headline','title','copy','text','cta','subtitle','caption','typography']): return 'typography_copy'
    if any(x in f for x in ['background','environment','scene','set']): return 'background_environment'
    if any(x in f for x in ['shadow','contact_shadow']): return 'shadow_contact'
    if any(x in f for x in ['grade','tone','color_grade','atmosphere']): return 'color_grade'
    if any(x in f for x in ['model','human','skin','hand','pose','expression']): return 'human_context'
    if any(x in f for x in ['wardrobe','hair','makeup','groom']): return 'wardrobe_grooming'
    if any(x in f for x in ['crop','camera','framing']): return 'camera_crop'
    if any(x in f for x in ['composition','layout','spacing','occupancy','position','scale']): return 'layout_spacing'
    if any(x in f for x in ['lighting','light','exposure']): return 'lighting_environment'
    if any(x in f for x in ['prop','spoon','device_context','accessory_context']): return 'prop_context'
    if any(x in f for x in ['graphic','proof','evidence','number','badge','diagram']): return 'graphic_evidence_layer'
    if any(x in f for x in ['logo','packaging','pack_text','product_geometry','product_color','product_master','product_pixel']): return 'FROZEN_PRODUCT_IDENTITY'
    return None

def _revision_scope_contract(project:Path, asset_id:str, allowed_fields:list[str])->dict[str,Any]:
    layout=_read_json(project/'artifacts/asset_packages'/asset_id/'04_layout_contract.json',{})
    contract=layout.get('editable_layer_contract') or {}
    editable=set(contract.get('editable_layers') or [])
    frozen=set(contract.get('frozen_layers') or [])
    mapped=[]; invalid=[]
    for field in allowed_fields:
        layer=_revision_layer_for_field(field)
        mapped.append({'field':field,'layer':layer})
        if layer=='FROZEN_PRODUCT_IDENTITY' or layer is None or (editable and layer not in editable):
            invalid.append({'field':field,'layer':layer,'reason':'FROZEN_OR_NOT_DECLARED_EDITABLE'})
    return {'editable_layers':sorted(editable),'frozen_layers':sorted(frozen),'field_layer_map':mapped,'invalid_fields':invalid,'allowed_layers':sorted({x['layer'] for x in mapped if x.get('layer') and x['layer']!='FROZEN_PRODUCT_IDENTITY'})}


def compile_local_revision_jobs(project_dir:Path, state:dict[str,Any], provider_preferences:dict[str,Any]|None=None, revision_request_ids:list[str]|None=None)->dict[str,Any]:
    """Turn explicit review revision requests into frozen, scope-limited provider jobs.

    The base 00–11 asset package is never mutated. A local revision is an execution overlay bound to the
    parent package hash and explicit allowed_fields. Empty scopes are held rather than widened implicitly.
    """
    project=Path(project_dir); selected=set(revision_request_ids or [])
    idx=_revision_index(project); existing={x.get('revision_request_id'):x for x in idx.get('revisions',[]) if x.get('revision_request_id')}
    compiled=[]; held=[]
    for rr in state.get('local_revision_requests',[]) or []:
        rid=rr.get('revision_request_id') or ('LRQ-'+stable_hash([rr.get('item_id'),rr.get('created_at'),rr.get('requested_change')])[:12])
        rr['revision_request_id']=rid
        if selected and rid not in selected: continue
        if rr.get('status') not in {'OPEN','RETRY_REQUESTED'}: continue
        aid=rr.get('asset_id')
        allowed=[str(x) for x in (rr.get('allowed_fields') or []) if str(x)]
        if not aid:
            rr['status']='HOLD_NO_ASSET_SCOPE'; held.append({'revision_request_id':rid,'reason':'NO_ASSET_ID'}); continue
        if not allowed:
            rr['status']='HOLD_REVISION_SCOPE_UNSPECIFIED'; held.append({'revision_request_id':rid,'asset_id':aid,'reason':'ALLOWED_FIELDS_REQUIRED'}); continue
        scope_contract=_revision_scope_contract(project,aid,allowed)
        if scope_contract.get('invalid_fields'):
            rr['status']='HOLD_REVISION_FIELD_OUTSIDE_EDITABLE_LAYERS'; rr['scope_contract']=scope_contract
            held.append({'revision_request_id':rid,'asset_id':aid,'reason':'REVISION_FIELD_OUTSIDE_EDITABLE_LAYERS','invalid_fields':scope_contract.get('invalid_fields'),'editable_layers':scope_contract.get('editable_layers'),'frozen_layers':scope_contract.get('frozen_layers')}); continue
        # One revision request creates one immutable job generation. Re-compilation requires a new request/retry status.
        if rid in existing and existing[rid].get('status') not in {'FAILED','RETRY_REQUESTED'}:
            compiled.append(existing[rid]); continue
        scope={'asset_id':aid,'allowed_fields':allowed,'allowed_layers':scope_contract.get('allowed_layers',[]),'field_layer_map':scope_contract.get('field_layer_map',[]),'frozen_layers':scope_contract.get('frozen_layers',[]),'requested_change':rr.get('requested_change'),'revision_request_id':rid,'base_revision':rr.get('base_revision')}
        run=build_production_run(project/'artifacts/asset_packages',provider_preferences,[aid],scope)
        row=(run.get('assets') or [{}])[0]
        revision_id='LR-'+stable_hash([rid,aid,row.get('package_hash'),rr.get('requested_change'),allowed])[:14]
        rev_root=project/'artifacts/local_revisions'/revision_id
        jobs=materialize_provider_jobs(project/'artifacts/asset_packages',run,rev_root/'provider_jobs')
        run['provider_jobs']=jobs; run['revision_id']=revision_id; run['revision_request_id']=rid
        _write_json(rev_root/'revision_request.json',{**rr,'revision_request_id':rid})
        _write_json(rev_root/'production_run.json',run)
        lineage={
            'revision_id':revision_id,'revision_request_id':rid,'asset_id':aid,'status':'JOB_COMPILED',
            'parent_package_hash':row.get('package_hash'),'parent_asset_package':str(project/'artifacts/asset_packages'/aid),
            'requested_change':rr.get('requested_change'),'allowed_fields':allowed,'allowed_layers':scope_contract.get('allowed_layers',[]),'field_layer_map':scope_contract.get('field_layer_map',[]),'frozen_layers':scope_contract.get('frozen_layers',[]),'freeze_rule':'All fields outside allowed_fields and all declared frozen product-identity layers remain frozen.',
            'provider':row.get('provider'),'provider_job_count':jobs.get('job_count',0),'created_at':_now(),
            'revised_output_path':None,'revised_output_hash':None,'provider_result_status':None,'review_status':'PENDING_PROVIDER_RESULT'
        }
        _write_json(rev_root/'revision_lineage.json',lineage)
        idx['revisions']=[x for x in idx.get('revisions',[]) if x.get('revision_request_id')!=rid]+[lineage]
        rr['revision_id']=revision_id; rr['status']='JOB_COMPILED'; rr['job_root']=str(rev_root/'provider_jobs')
        compiled.append(lineage)
    _save_revision_index(project,idx)
    return {'status':'LOCAL_REVISION_JOBS_COMPILED' if compiled else ('LOCAL_REVISION_HOLD' if held else 'NO_OPEN_LOCAL_REVISION_REQUESTS'),'compiled':compiled,'held':held,'count':len(compiled),'principle':'Local revisions are scope-limited overlays on immutable parent asset packages; they do not trigger broad strategy or package rewrites.'}


def ingest_local_revision_results(project_dir:Path, state:dict[str,Any], revision_ids:list[str]|None=None)->dict[str,Any]:
    project=Path(project_dir); selected=set(revision_ids or [])
    idx=_revision_index(project); out=[]
    requests={x.get('revision_request_id'):x for x in state.get('local_revision_requests',[]) or []}
    for row in idx.get('revisions',[]) or []:
        revision_id=row.get('revision_id')
        if selected and revision_id not in selected: continue
        if row.get('status') not in {'JOB_COMPILED','RESULT_REVIEW_REQUIRED','FAILED'}: continue
        rev_root=project/'artifacts/local_revisions'/str(revision_id)
        run=_read_json(rev_root/'production_run.json',{})
        if not run: continue
        applied=ingest_provider_job_results(run,rev_root/'provider_jobs')
        applied['revision_id']=revision_id; applied['revision_request_id']=row.get('revision_request_id')
        _write_json(rev_root/'provider_result_ingest.json',applied)
        result_row=next((x for x in applied.get('assets',[]) if x.get('asset_id')==row.get('asset_id')),None) or {}
        output_path=result_row.get('output_path')
        output_hash=_file_sha256(Path(output_path)) if output_path else None
        row['provider_result_status']=applied.get('status')
        row['revised_output_path']=output_path
        row['revised_output_hash']=output_hash
        row['changed_fields']=result_row.get('changed_fields',[])
        row['issues']=applied.get('issues',[])
        row['status']='READY_REVIEW' if applied.get('status')=='COMPLETE' else 'RESULT_REVIEW_REQUIRED'
        row['review_status']='PENDING_REVIEW' if applied.get('status')=='COMPLETE' else 'PROVIDER_RESULT_REVIEW_REQUIRED'
        row['result_ingested_at']=_now()
        _write_json(rev_root/'revision_lineage.json',row)
        rr=requests.get(row.get('revision_request_id'))
        if rr is not None: rr['status']='RESULT_READY_REVIEW' if applied.get('status')=='COMPLETE' else 'RESULT_REVIEW_REQUIRED'
        out.append({'revision_id':revision_id,'status':row['status'],'provider_result_status':applied.get('status'),'output_path':output_path,'output_hash':output_hash,'issues':applied.get('issues',[])})
    _save_revision_index(project,idx)
    return {'status':'LOCAL_REVISION_RESULTS_INGESTED' if out else 'NO_LOCAL_REVISION_RESULTS_INGESTED','revisions':out,'count':len(out)}


def _metric_delta(before:Any, after:Any)->dict[str,Any]:
    try:
        b=float(before); a=float(after); delta=a-b
        return {'before':b,'after':a,'delta':round(delta,8),'pct_change':round(delta/abs(b),8) if b else None}
    except Exception:
        return {'before':before,'after':after,'delta':None,'pct_change':None}


def _compare_metrics(baseline:dict[str,Any], after:dict[str,Any], directions:dict[str,str]|None=None)->list[dict[str,Any]]:
    directions=directions or {}; rows=[]
    for key in sorted(set(baseline)|set(after)):
        d=_metric_delta(baseline.get(key),after.get(key)); direction=str(directions.get(key) or 'UP').upper(); delta=d.get('delta')
        if delta is None: verdict='UNINTERPRETABLE'
        elif abs(delta)<1e-12: verdict='FLAT'
        elif (direction=='DOWN' and delta<0) or (direction!='DOWN' and delta>0): verdict='IMPROVED'
        else: verdict='WORSENED'
        rows.append({'metric':key,'desired_direction':direction,**d,'verdict':verdict})
    return rows




def _infer_production_learning_layers(cycle:dict[str,Any])->tuple[list[str],list[str],list[str]]:
    codes=[]
    for x in cycle.get('production_issue_codes') or []:
        codes.append(str(x).upper())
    for x in cycle.get('post_feedback') or []:
        if isinstance(x,dict):
            codes.extend([str(x.get('code') or '').upper(),str(x.get('category') or '').upper(),str(x.get('signal') or '').upper()])
        else:
            codes.append(str(x).upper())
    joined=' | '.join(x for x in codes if x)
    layers=[]; reasons=[]
    def add(layer,reason):
        if layer not in layers: layers.append(layer)
        reasons.append(reason)
    if any(x in joined for x in ['LOCKED_PIXEL','PRODUCT_FIDELITY','PRODUCT_IDENTITY','MASTER','LOGO','PACKAGING_PRINT','PRODUCT_GEOMETRY','PRODUCT_COLOR']):
        add('VISUAL_PRODUCT_FIDELITY_EXECUTION','Observed output implicates execution of the supplied product master, not a rewrite of Product Truth.')
    if any(x in joined for x in ['SURFACE','SAFE_ZONE','COMPOSITION','CROP','OCCUPANCY','LAYOUT','PLATFORM']):
        add('VISUAL_SURFACE_EXECUTION','Observed output implicates composition/surface execution.')
    if any(x in joined for x in ['PHOTOGRAPHY','CMF','LIGHT','EXPOSURE','REFLECTION','COLOR_MANAGEMENT','MATERIAL']):
        add('VISUAL_PHOTOGRAPHY_CMF','Observed output implicates camera/light/material/color execution.')
    if any(x in joined for x in ['COPY_VISUAL','COPY-VISUAL','COPY ALIGN','COPY_ALIGNMENT']):
        add('VISUAL_COPY_ALIGNMENT','Copy is locked; the observed failure is the visual attribution/relationship unless separate copy evidence implicates copy itself.')
    if any(x in joined for x in ['DIFFERENTIATION','SAMENESS','SAME_LAYOUT','HOMOGENEITY','HOMOGENEOUS']):
        add('VISUAL_ASSET_DIFFERENTIATION','Observed outputs collapsed distinct decision jobs into a repeated visual grammar.')
    if any(x in joined for x in ['CLAIM','FACT_DRIFT','COPY_FACT']):
        add('COPY_CLAIM_EXECUTION','Observed output may contain copy/fact execution drift; any copy/claim change still requires explicit claim/source authority.')
    freeze=['PRODUCT_TRUTH','POSITIONING','OFFER'] if layers else []
    return layers,freeze,reasons


def compile_learning_cycle(project_dir:Path, state:dict[str,Any], cycle:dict[str,Any])->dict[str,Any]:
    """Compile post-change observations into a bounded learning decision.

    Arithmetic before/after movement is descriptive. Causal credit is permitted only when explicit causal evidence is supplied.
    """
    project=Path(project_dir); strategy=_read_json(project/'artifacts/strategy_authority.json',{})
    routing=_read_json(project/'artifacts/strategy_revision_routing.json',{})
    rev_idx=_revision_index(project)
    cycle_id=cycle.get('cycle_id') or ('LC-'+stable_hash([cycle.get('revision_id'),cycle.get('baseline_metrics'),cycle.get('after_metrics'),_now()])[:14])
    revision_id=cycle.get('revision_id')
    revision=next((x for x in rev_idx.get('revisions',[]) if x.get('revision_id')==revision_id),None) if revision_id else None
    route_id=cycle.get('route_id')
    route=None
    if route_id:
        route=next((x for x in routing.get('routes',[]) if x.get('route_id')==route_id),None)
    if route is None and cycle.get('signal'):
        route=next((x for x in routing.get('routes',[]) if x.get('signal')==cycle.get('signal')),None)
    edit_layers=list(cycle.get('edit_layers') or ((route or {}).get('edit_layers') or []))
    freeze_layers=list(cycle.get('freeze_layers') or ((route or {}).get('freeze_layers') or []))
    inferred_layers=[]; inferred_freeze=[]; production_learning_reasons=[]
    if not edit_layers:
        inferred_layers,inferred_freeze,production_learning_reasons=_infer_production_learning_layers(cycle)
        edit_layers=list(inferred_layers)
        if not freeze_layers: freeze_layers=list(inferred_freeze)
    metrics=_compare_metrics(cycle.get('baseline_metrics') or {},cycle.get('after_metrics') or {},cycle.get('metric_directions'))
    improved=sum(1 for x in metrics if x['verdict']=='IMPROVED'); worsened=sum(1 for x in metrics if x['verdict']=='WORSENED')
    causal=cycle.get('causal_evidence') or {}
    causal_status=str(causal.get('status') or 'NOT_SUPPLIED').upper()
    causal_allowed=causal_status in {'VALID_CAUSAL_EVIDENCE','CAUSAL_INTERPRETATION_SUPPORTED'}
    severe_post_feedback=bool(cycle.get('product_defect_signal'))
    if not metrics and not cycle.get('post_feedback'):
        recommendation='INSUFFICIENT_POST_CHANGE_EVIDENCE'
    elif severe_post_feedback:
        recommendation='ESCALATE_PRODUCT_OR_QUALITY_LAYER'
    elif worsened and not improved:
        recommendation='ROLLBACK_OR_REVISE_SAME_LAYER'
    elif improved and not worsened:
        recommendation='KEEP_LOCAL_CHANGE_MONITOR' if not causal_allowed else 'KEEP_LOCAL_CHANGE_CAUSAL_SUPPORT'
    else:
        recommendation='CONTINUE_LOCAL_EXPERIMENT'
    report={
        'status':'LEARNING_CYCLE_COMPILED','cycle_id':cycle_id,'project_id':state.get('project_id'),'project_revision':state.get('revision'),
        'revision_id':revision_id,'revision_lineage':revision,'source_route':route,'edit_layers':edit_layers,'freeze_layers':freeze_layers,
        'baseline_metrics':cycle.get('baseline_metrics') or {},'after_metrics':cycle.get('after_metrics') or {},'metric_comparison':metrics,
        'post_feedback':cycle.get('post_feedback') or [],'production_issue_codes':cycle.get('production_issue_codes') or [],'inferred_production_learning_layers':inferred_layers,'production_learning_reasons':production_learning_reasons,'causal_evidence':causal,'causal_credit_allowed':causal_allowed,
        'recommendation':recommendation,'why':'The learning decision is bounded to the edited layer and observed symptom. Before/after movement is descriptive unless valid causal evidence is explicitly supplied.',
        'strategy_learning_contract':{'apply_to_layers':edit_layers,'freeze_layers':freeze_layers,'auto_rewrite_product_truth':False,'auto_rewrite_positioning':False,'requires_explicit_patch_for_copy_or_claim_change':True},
        'created_at':_now()
    }
    root=project/'artifacts/learning_cycles'/cycle_id; _write_json(root/'learning_cycle.json',report)
    return report


def materialize_production_learning_summary(project_dir:Path)->dict[str,Any]:
    project=Path(project_dir)
    final_copy=_read_json(project/'artifacts/listing_final_copy.json',{})
    production=_read_json(project/'artifacts/production_run.json',{})
    revisions=_revision_index(project)
    latest=_read_json(project/'artifacts/learning_latest.json',{})
    summary={
        'status':'PRODUCTION_LEARNING_LOOP_MATERIALIZED',
        'loop':['HOST_FINAL_COPY','PROVIDER_JOB','PROVIDER_RESULT','REVIEW','LOCAL_REVISION_REQUEST','REVISION_PROVIDER_JOB','REVISION_PROVIDER_RESULT','REVISION_REVIEW','POST_CHANGE_MEASUREMENT','STRATEGY_LEARNING'],
        'final_copy':{'status':final_copy.get('status'),'release_counts':final_copy.get('release_counts'),'all_final':(lambda counts: sum(counts.values())>0 and counts.get('APPROVED_FINAL',0)==sum(counts.values()))(final_copy.get('release_counts') or {})},
        'production':{'status':production.get('status'),'asset_count':len(production.get('assets') or []),'provider_results_ingested':production.get('provider_results_ingested')},
        'local_revisions':{'count':len(revisions.get('revisions') or []),'accepted':sum(1 for x in revisions.get('revisions',[]) if x.get('status')=='ACCEPTED'),'revisions':revisions.get('revisions',[])},
        'learning':{'cycle_id':latest.get('cycle_id'),'recommendation':latest.get('recommendation'),'causal_credit_allowed':latest.get('causal_credit_allowed'),'edit_layers':latest.get('edit_layers'),'freeze_layers':latest.get('freeze_layers')},
        'principle':'Each step is explicit. Generated copy is not final without exact review; Provider completion is not review acceptance; local revisions do not mutate parent 00–11 packages; before/after movement is not causal credit without valid causal evidence.'
    }
    _write_json(project/'artifacts/production_learning_loop.json',summary)
    return summary

def apply_learning_to_strategy(project_dir:Path, learning:dict[str,Any])->dict[str,Any]:
    """Append a learning ledger and local-layer overlays without rewriting unrelated strategy authority."""
    project=Path(project_dir); strategy=_read_json(project/'artifacts/strategy_authority.json',{})
    if not strategy: return {'status':'NO_STRATEGY_AUTHORITY'}
    sections=strategy.setdefault('sections',{})
    s9=sections.setdefault('09_risk_measurement_priority_next_steps',{})
    perf=s9.setdefault('performance_learning',{})
    ledger=perf.setdefault('learning_ledger',[])
    entry={k:learning.get(k) for k in ['cycle_id','revision_id','edit_layers','freeze_layers','metric_comparison','causal_credit_allowed','recommendation','why','created_at']}
    if not any(x.get('cycle_id')==entry.get('cycle_id') for x in ledger): ledger.append(entry)
    overlay={'cycle_id':learning.get('cycle_id'),'recommendation':learning.get('recommendation'),'edit_layers':learning.get('edit_layers',[]),'freeze_layers':learning.get('freeze_layers',[]),'evidence':learning.get('metric_comparison',[]),'causal_credit_allowed':learning.get('causal_credit_allowed'),'rule':'Only the listed edit layers may change from this learning cycle; frozen layers remain authoritative until separate evidence implicates them.'}
    marketing=sections.setdefault('04_marketing_core_strategy',{})
    visual=sections.setdefault('05_visual_photography_strategy',{})
    def _append_overlay_once(rows:list[dict[str,Any]])->None:
        if not any(x.get('cycle_id')==overlay.get('cycle_id') for x in rows): rows.append(overlay)
    for layer in learning.get('edit_layers') or []:
        key=str(layer).upper()
        if any(x in key for x in ['LISTING','TITLE','PDP','FAQ','USAGE_CONTENT']):
            _append_overlay_once(marketing.setdefault('listing_strategy',{}).setdefault('learning_revision_overlays',[]))
        elif any(x in key for x in ['MESSAGE','POSITION','PROPOSITION']):
            _append_overlay_once(marketing.setdefault('positioning',{}).setdefault('learning_revision_overlays',[]))
        elif any(x in key for x in ['OFFER','PRICE','COUPON','BUNDLE']):
            _append_overlay_once(marketing.setdefault('product_strategy',{}).setdefault('learning_revision_overlays',[]))
        elif any(x in key for x in ['VISUAL','HERO','CREATIVE','PHOTO']):
            _append_overlay_once(visual.setdefault('learning_revision_overlays',[]))
    strategy.setdefault('learning_history',[]).append({'cycle_id':learning.get('cycle_id'),'recommendation':learning.get('recommendation'),'applied_at':_now()})
    strategy['runtime_strategy_depth']='0.6.10-visual-execution-copy-continuity'
    # Add an explicit decision-index record even if deterministic index builders do not know the new overlay shape.
    strategy.setdefault('decision_index',[]).append({'decision_id':'DEC-LEARN-'+str(learning.get('cycle_id')),'domain':'LEARNING','what':learning.get('recommendation'),'why':learning.get('why'),'evidence':[x.get('metric') for x in learning.get('metric_comparison',[])],'execution':'Apply only to '+', '.join(learning.get('edit_layers') or [])+'; freeze '+', '.join(learning.get('freeze_layers') or []),'measurement':'Re-check the original symptom after the local revision; causal credit only when the supplied causal evidence supports it.'})
    materialize_strategy(project/'artifacts/strategy',strategy)
    _write_json(project/'artifacts/strategy_authority.json',strategy)
    _write_json(project/'artifacts/learning_latest.json',learning)
    summary=materialize_production_learning_summary(project)
    cmap_path=project/'artifacts/capability_integration_map.json'; cmap=_read_json(cmap_path,{})
    for row in cmap.get('capabilities',[]) or []:
        if row.get('capability')=='POST_PRODUCTION_LEARNING_LOOP':
            row.update({'project_input_active':True,'input_status':'LEARNING_APPLIED','runtime_wiring_status':'INTEGRATED_ACTIVE','integrated':True})
    if cmap:
        cmap['learning_loop_status']=summary.get('status'); cmap['integration_gaps']=[x.get('capability') for x in cmap.get('capabilities',[]) if x.get('runtime_wiring_status')=='INTEGRATION_GAP']; _write_json(cmap_path,cmap)
    return {'status':'STRATEGY_AUTHORITY_LEARNING_APPLIED','cycle_id':learning.get('cycle_id'),'edit_layers':learning.get('edit_layers',[]),'freeze_layers':learning.get('freeze_layers',[]),'recommendation':learning.get('recommendation'),'loop_summary':summary}


def sync_local_revision_review_state(project_dir:Path, state:dict[str,Any])->dict[str,Any]:
    """Mirror review acceptance/revision state into the revision lineage index without changing the immutable base package."""
    project=Path(project_dir); idx=_revision_index(project); reviews=state.get('item_reviews') or {}; changed=[]
    requests={x.get('revision_request_id'):x for x in state.get('local_revision_requests',[]) or []}
    for row in idx.get('revisions',[]) or []:
        iid='REVISION-OUTPUT-'+str(row.get('revision_id'))
        rv=reviews.get(iid)
        if rv:
            row['review_status']=rv.get('status'); row['review_note']=rv.get('note'); row['reviewed_at']=rv.get('updated_at')
            if rv.get('status')=='ACCEPTED': row['status']='ACCEPTED'
            elif rv.get('status')=='REVISE_REQUESTED': row['status']='REVISE_REQUESTED'
            elif rv.get('status')=='HOLD': row['status']='HOLD'
            changed.append(row.get('revision_id'))
        rr=requests.get(row.get('revision_request_id'))
        if rr and rr.get('status')=='ACCEPTED': row['status']='ACCEPTED'; row['review_status']='ACCEPTED'
        _write_json(project/'artifacts/local_revisions'/str(row.get('revision_id'))/'revision_lineage.json',row)
    _save_revision_index(project,idx)
    return {'status':'LOCAL_REVISION_REVIEW_STATE_SYNCED','revision_ids':changed}
