from __future__ import annotations
from pathlib import Path
from typing import Any
import json, html, re


def _load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def _safe_id(value:str)->str:
    return re.sub(r'[^A-Za-z0-9_.-]+','_',str(value))[:180]


def _review_state(state:dict[str,Any], item_id:str)->dict[str,Any]:
    return (state.get('item_reviews') or {}).get(item_id, {'status':'PENDING_REVIEW','note':'','revision':state.get('revision')})


def build_delivery_manifest(project_dir: Path, state: dict[str, Any]) -> dict[str, Any]:
    p=Path(project_dir)
    content=_load_json(p/'artifacts/content_graph.json', {'objects':[]})
    assets=_load_json(p/'artifacts/asset_packages/ASSET_PACKAGE_INDEX.json', {'assets':[]})
    production=_load_json(p/'artifacts/production_run.json', {'assets':[]})
    local_revisions=_load_json(p/'artifacts/local_revisions/LOCAL_REVISION_INDEX.json', {'revisions':[]})
    items=[]
    for gate, rec in state.get('gates',{}).items():
        if rec.get('status')!='PENDING' or rec.get('artifact_paths'):
            iid=f'GATE-{gate}'; rv=_review_state(state,iid)
            items.append({'item_id':iid,'kind':'AUTHORITY_GATE','name':gate,'status':rec.get('status'),'review_status':rv.get('status'),'review_note':rv.get('note',''),
                          'required':bool(rec.get('required_for_current_scope',False)),
                          'blocking_for_current_scope':bool(rec.get('blocking_for_current_scope',rec.get('required_for_current_scope',False))),
                          'scope_status':rec.get('scope_status','UNSCOPED'),'scope_reason':rec.get('scope_reason',''),
                          'artifact_paths':rec.get('artifact_paths',[]),'authority_gate':gate})
    for obj in content.get('objects',[]):
        iid=f"OBJ-{obj.get('object_id')}"; rv=_review_state(state,iid)
        items.append({'item_id':iid,'kind':'CONTENT_OBJECT','name':obj.get('kind'),'family':obj.get('family'),'status':obj.get('status','READY_REVIEW'),'review_status':rv.get('status'),'review_note':rv.get('note',''),'required':bool(obj.get('required',True)),'artifact_paths':[str(p/f"artifacts/objects/{obj.get('object_id')}.json")],'object_id':obj.get('object_id'),'authority_gate':'CONTENT_GRAPH'})
    for a in assets.get('assets',[]):
        aid=a.get('asset_id'); iid=f'ASSET-{aid}'; rv=_review_state(state,iid)
        items.append({'item_id':iid,'kind':'ASSET_PACKAGE','name':aid,'status':a.get('status','ACTIVATE'),'review_status':rv.get('status'),'review_note':rv.get('note',''),'required':a.get('status','ACTIVATE')=='ACTIVATE','artifact_paths':[str(p/f'artifacts/asset_packages/{aid}')],'asset_id':aid,'authority_gate':'ASSET_COMPILE'})
    for r in production.get('assets',[]):
        aid=r.get('asset_id'); iid=f'OUTPUT-{aid}'; rv=_review_state(state,iid); qc=r.get('production_quality_contract') or {}; edit=qc.get('editable_layer_contract') or {}
        items.append({'item_id':iid,'kind':'PRODUCTION_OUTPUT','name':aid,'status':r.get('result_status') or r.get('status'),'review_status':rv.get('status'),'review_note':rv.get('note',''),'required':True,'artifact_paths':[r.get('output_path')] if r.get('output_path') else [],'asset_id':aid,'authority_gate':'PRODUCTION',
                      'review_dimensions':qc.get('review_dimensions') or [],'quality_observations':r.get('quality_observations') or {},'visual_production_signature':qc.get('visual_production_signature') or {},'copy_visual_alignment':qc.get('copy_visual_alignment') or {},'editable_layer_contract':edit,'allowed_revision_fields':edit.get('editable_layers') or [],'frozen_revision_fields':edit.get('frozen_layers') or []})
    for r in local_revisions.get('revisions',[]):
        if r.get('status') not in {'READY_REVIEW','RESULT_REVIEW_REQUIRED','ACCEPTED'}: continue
        rid=r.get('revision_id'); aid=r.get('asset_id'); iid=f'REVISION-OUTPUT-{rid}'; rv=_review_state(state,iid)
        items.append({'item_id':iid,'kind':'LOCAL_REVISION_OUTPUT','name':rid,'status':r.get('status'),'review_status':rv.get('status'),'review_note':rv.get('note',''),'required':True,'artifact_paths':[r.get('revised_output_path')] if r.get('revised_output_path') else [],'asset_id':aid,'revision_id':rid,'revision_request_id':r.get('revision_request_id'),'parent_package_hash':r.get('parent_package_hash'),'revised_output_hash':r.get('revised_output_hash'),'authority_gate':'PRODUCTION'})
    blocking_review={'HOLD','REVISE_REQUESTED'}
    required_missing=[]
    for x in items:
        if not x.get('required'): continue
        runtime_blocked=x.get('status') in {'MISSING','HOLD','INVALIDATED'}
        if x.get('kind')=='AUTHORITY_GATE' and not x.get('blocking_for_current_scope',True):
            runtime_blocked=False
        if runtime_blocked or x.get('review_status') in blocking_review:
            required_missing.append(x['item_id'])
    review_pending=[x['item_id'] for x in items if x.get('required') and x.get('kind')!='AUTHORITY_GATE' and x.get('review_status')=='PENDING_REVIEW']
    return {'project_id':state.get('project_id'),'revision':state.get('revision'),'items':items,'required_missing':required_missing,'review_pending':review_pending,'final_ready':bool(state.get('final_ready')) and not required_missing and not review_pending}


def materialize_review_workspace(project_dir: Path, state: dict[str, Any]) -> dict[str, str]:
    p=Path(project_dir); out=p/'.cbcc/review'; items_dir=out/'items'; items_dir.mkdir(parents=True,exist_ok=True)
    delivery=build_delivery_manifest(p,state)
    workspace={'project_id':state.get('project_id'),'runtime_version':state.get('runtime_version'),'revision':state.get('revision'),'current_stage':state.get('current_stage'),'gates':state.get('gates',{}),'pending_actions':state.get('pending_actions',[]),'local_revision_requests':state.get('local_revision_requests',[]),'delivery_summary':{'items':len(delivery['items']),'required_missing':delivery['required_missing'],'review_pending':delivery['review_pending']}}
    decision={'project_id':state.get('project_id'),'revision':state.get('revision'),'accept':[],'revise':[],'hold':[],'accept_items':[],'hold_items':[],'revise_items':[],'item_revision_requests':{},'notes':{},'item_notes':{}}
    paths={
        'operator_workspace':out/'operator_workspace.json',
        'delivery_manifest':out/'delivery_manifest.json',
        'review_decision_template':out/'review_decision_template.json',
        'review_html':out/'index.html',
        'checklist':out/'checklist.md',
    }
    paths['operator_workspace'].write_text(json.dumps(workspace,ensure_ascii=False,indent=2),encoding='utf-8')
    paths['delivery_manifest'].write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf-8')
    paths['review_decision_template'].write_text(json.dumps(decision,ensure_ascii=False,indent=2),encoding='utf-8')
    # Individually addressable review contracts make object/asset review durable and machine-readable.
    for item in delivery['items']:
        contract={'project_id':state.get('project_id'),'revision':state.get('revision'),'item':item,'allowed_decisions':['ACCEPT','HOLD','REVISE'],'decision_payload':{'item_id':item['item_id'],'decision':'','note':'','revision_request':{'requested_change':'','allowed_fields':item.get('allowed_revision_fields') or []}},'review_focus':item.get('review_dimensions') or [],'frozen_revision_fields':item.get('frozen_revision_fields') or []}
        (items_dir/f"{_safe_id(item['item_id'])}.json").write_text(json.dumps(contract,ensure_ascii=False,indent=2),encoding='utf-8')
    gate_rows=[]
    for g,rec in state.get('gates',{}).items():
        gate_rows.append(f"<tr><td>{html.escape(g)}</td><td>{html.escape(str(rec.get('status')))}</td><td>{html.escape(str(rec.get('scope_status','UNSCOPED')))}</td><td>{'yes' if rec.get('blocking_for_current_scope') else 'no'}</td><td>{len(rec.get('artifact_paths',[]))}</td></tr>")
    item_rows=[]
    for x in delivery['items']:
        if x['kind']=='AUTHORITY_GATE': continue
        item_rows.append('<tr>'+''.join([
            f"<td>{html.escape(str(x.get('item_id')))}</td>",f"<td>{html.escape(str(x.get('kind')))}</td>",f"<td>{html.escape(str(x.get('family') or x.get('name') or ''))}</td>",f"<td>{html.escape(str(x.get('status')))}</td>",f"<td>{html.escape(str(x.get('review_status')))}</td>",f"<td>{html.escape(str(x.get('review_note') or ''))}</td>"])+"</tr>")
    actions=''.join(f"<li><b>{html.escape(str(a.get('action_id')))}</b> — {html.escape(str(a.get('reason') or a.get('query') or a.get('status')))}</li>" for a in state.get('pending_actions',[])) or '<li>None</li>'
    body=f'''<!doctype html><html><head><meta charset="utf-8"><title>CBCC Review Workspace</title><style>body{{font-family:system-ui,sans-serif;max-width:1280px;margin:36px auto;padding:0 20px;color:#202124}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{border:1px solid #ddd;padding:8px;text-align:left;vertical-align:top}}th{{background:#f5f5f5;position:sticky;top:0}}code{{background:#f5f5f5;padding:2px 5px}}.note{{padding:12px;background:#f7f9fc;border:1px solid #dfe6ef;border-radius:8px}}.ok{{font-weight:600}}</style></head><body><h1>CBCC Review Workspace</h1><p>Project <code>{html.escape(str(state.get('project_id')))}</code> · revision {state.get('revision')} · runtime {html.escape(str(state.get('runtime_version')))}</p><div class="note">This page is review-only. It does not mutate authority state. Production Output review follows the asset-specific product-fidelity, decision-visibility, surface, copy-visual, photography/CMF and visual-differentiation contract; local revision should target only the declared editable layers. Edit <code>review_decision_template.json</code> and apply it through the runtime review command.</div><h2>Authority Gates</h2><table><thead><tr><th>Gate</th><th>Runtime Status</th><th>Current Scope</th><th>Blocking</th><th>Artifacts</th></tr></thead><tbody>{''.join(gate_rows)}</tbody></table><h2>Addressable Review Items</h2><table><thead><tr><th>Item</th><th>Kind</th><th>Family/Name</th><th>Runtime status</th><th>Review</th><th>Note</th></tr></thead><tbody>{''.join(item_rows)}</tbody></table><h2>Pending Actions</h2><ul>{actions}</ul><h2>Delivery</h2><p>{len(delivery['items'])} addressable items · review pending: {len(delivery['review_pending'])} · required blocked/missing: {len(delivery['required_missing'])}.</p></body></html>'''
    paths['review_html'].write_text(body,encoding='utf-8')
    md=['# CBCC Review Checklist','',f"Project: `{state.get('project_id')}`",f"Revision: `{state.get('revision')}`",'', '## Authority gates']
    md += [f"- [{ 'x' if rec.get('status')=='LOCKED' else ' ' }] {g} — runtime={rec.get('status')} scope={rec.get('scope_status','UNSCOPED')} blocking={bool(rec.get('blocking_for_current_scope'))}" for g,rec in state.get('gates',{}).items()]
    md += ['', '## Content / Asset / Output review'] + [f"- [{ 'x' if x.get('review_status')=='ACCEPTED' else ' ' }] {x['item_id']} — runtime={x.get('status')} review={x.get('review_status')}" for x in delivery['items'] if x['kind']!='AUTHORITY_GATE']
    md += ['', '## Pending actions'] + ([f"- {a.get('action_id')}: {a.get('reason') or a.get('query') or a.get('status')}" for a in state.get('pending_actions',[])] or ['- None'])
    paths['checklist'].write_text('\n'.join(md)+'\n',encoding='utf-8')
    return {k:str(v) for k,v in paths.items()}
