from pathlib import Path

# ---------------- review.py ----------------
p=Path('runtime/cbcc/review.py')
s=p.read_text(encoding='utf-8')
anchor="""import json, html, re
"""
insert="""import json, html, re
from .completion import evaluate_scope_completion
"""
if anchor not in s: raise SystemExit('review import anchor missing')
s=s.replace(anchor,insert,1)
old="""    blocking_review={'HOLD','REVISE_REQUESTED'}
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
"""
new="""    blocking_review={'HOLD','REVISE_REQUESTED'}
    required_missing=[]
    for x in items:
        if not x.get('required'): continue
        runtime_blocked=x.get('status') in {'MISSING','HOLD','INVALIDATED','BLOCKED','FAIL'}
        if x.get('kind')=='AUTHORITY_GATE' and not x.get('blocking_for_current_scope',True):
            runtime_blocked=False
        if runtime_blocked or x.get('review_status') in blocking_review:
            required_missing.append(x['item_id'])
    agent_next=_load_json(p/'artifacts/agent_next_action.json',{})
    completion=evaluate_scope_completion(state,items,agent_next_action=agent_next)
    review_pending=[x.get('item_id') for x in completion.get('review_pending',[]) if x.get('item_id')]
    return {
        'project_id':state.get('project_id'),'revision':state.get('revision'),'items':items,
        'required_missing':required_missing,'review_pending':review_pending,
        'blocking_actions':[x.get('action_id') for x in completion.get('blocking_actions',[]) if x.get('action_id')],
        'open_revision_requests':[x.get('revision_request_id') for x in completion.get('open_revision_requests',[]) if x.get('revision_request_id')],
        'completion':completion,'final_ready':completion.get('final_ready',False)
    }
"""
if old not in s: raise SystemExit('review completion block missing')
s=s.replace(old,new,1)
old="""    delivery=build_delivery_manifest(p,state)
    workspace={'project_id':state.get('project_id'),'runtime_version':state.get('runtime_version'),'revision':state.get('revision'),'current_stage':state.get('current_stage'),'gates':state.get('gates',{}),'pending_actions':state.get('pending_actions',[]),'local_revision_requests':state.get('local_revision_requests',[]),'delivery_summary':{'items':len(delivery['items']),'required_missing':delivery['required_missing'],'review_pending':delivery['review_pending']}}
"""
new="""    delivery=build_delivery_manifest(p,state)
    # Keep the in-memory state synchronized for callers that will persist it after workspace materialization.
    state['final_ready']=bool(delivery.get('final_ready'))
    state['completion']=delivery.get('completion') or {}
    workspace={'project_id':state.get('project_id'),'runtime_version':state.get('runtime_version'),'revision':state.get('revision'),'current_stage':state.get('current_stage'),'gates':state.get('gates',{}),'pending_actions':state.get('pending_actions',[]),'local_revision_requests':state.get('local_revision_requests',[]),'completion':delivery.get('completion') or {},'delivery_summary':{'items':len(delivery['items']),'required_missing':delivery['required_missing'],'review_pending':delivery['review_pending'],'blocking_actions':delivery.get('blocking_actions',[]),'open_revision_requests':delivery.get('open_revision_requests',[]),'final_ready':delivery.get('final_ready',False)}}
"""
if old not in s: raise SystemExit('review workspace block missing')
s=s.replace(old,new,1)
# Add reusable persistence helper before materialize_review_workspace.
anchor="""def materialize_review_workspace(project_dir: Path, state: dict[str, Any]) -> dict[str, str]:
"""
helper="""def refresh_review_workspace(project_dir: Path, project_state) -> dict[str, str]:
    \"\"\"Recompute current-scope completion, persist it, then materialize the review workspace.\"\"\"
    paths=materialize_review_workspace(project_dir,project_state.data)
    project_state.save()
    return paths


def materialize_review_workspace(project_dir: Path, state: dict[str, Any]) -> dict[str, str]:
"""
if anchor not in s: raise SystemExit('review materialize anchor missing')
s=s.replace(anchor,helper,1)
p.write_text(s,encoding='utf-8')

# ---------------- compiler.py ----------------
p=Path('runtime/cbcc/compiler.py')
s=p.read_text(encoding='utf-8')
s=s.replace('from .review import materialize_review_workspace','from .review import materialize_review_workspace, refresh_review_workspace',1)
s=s.replace("st.data['runtime_version']='0.6.26-scope-readiness'","st.data['runtime_version']='0.6.27-current-scope-completion'",1)
old="""    st.data['final_ready']=False; st.save(); materialize_review_workspace(p,st.data); return st.data
"""
new="""    # final_ready is derived from current-scope closure; never reset it as a static pipeline flag.
    refresh_review_workspace(p,st)
    return st.data
"""
if old not in s: raise SystemExit('compiler final_ready tail missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# ---------------- cli.py ----------------
p=Path('runtime/cbcc/cli.py')
s=p.read_text(encoding='utf-8')
s=s.replace('from .review import materialize_review_workspace','from .review import materialize_review_workspace, refresh_review_workspace, build_delivery_manifest',1)
old="""    elif a.cmd in {'build','resume'}:
        request_path=Path(a.request) if getattr(a,'request',None) else Path(a.project_dir)/'.cbcc/request.json'
        if not request_path.exists(): raise FileNotFoundError(f'No request available for {a.cmd}: {request_path}')
        req=json.loads(request_path.read_text(encoding='utf-8')); out=build_project(Path(a.project_dir),req,Path(a.packs_dir) if a.packs_dir else root/'platform_packs'); materialize_review_workspace(Path(a.project_dir),out)
    elif a.cmd=='revise': out={'invalidated':ProjectState.load(Path(a.project_dir)).revise(a.changed)}
    elif a.cmd=='review-build':
        st=ProjectState.load(Path(a.project_dir)); out=materialize_review_workspace(Path(a.project_dir),st.data)
"""
new="""    elif a.cmd in {'build','resume'}:
        request_path=Path(a.request) if getattr(a,'request',None) else Path(a.project_dir)/'.cbcc/request.json'
        if not request_path.exists(): raise FileNotFoundError(f'No request available for {a.cmd}: {request_path}')
        req=json.loads(request_path.read_text(encoding='utf-8')); out=build_project(Path(a.project_dir),req,Path(a.packs_dir) if a.packs_dir else root/'platform_packs')
    elif a.cmd=='revise':
        project=Path(a.project_dir); st=ProjectState.load(project); invalidated=st.revise(a.changed); refresh_review_workspace(project,st); out={'invalidated':invalidated,'final_ready':st.data.get('final_ready'),'completion':st.data.get('completion')}
    elif a.cmd=='review-build':
        project=Path(a.project_dir); st=ProjectState.load(project); out=refresh_review_workspace(project,st)
"""
if old not in s: raise SystemExit('cli build/revise/review-build block missing')
s=s.replace(old,new,1)
old="""        project=Path(a.project_dir); st=ProjectState.load(project); d=json.loads(Path(a.review_file).read_text(encoding='utf-8')); st.apply_review_decision(d); sync_local_revision_review_state(project,st.data); materialize_review_workspace(project,st.data); out=st.data
"""
new="""        project=Path(a.project_dir); st=ProjectState.load(project); d=json.loads(Path(a.review_file).read_text(encoding='utf-8')); st.apply_review_decision(d); sync_local_revision_review_state(project,st.data); refresh_review_workspace(project,st); out=st.data
"""
if old not in s: raise SystemExit('cli review-apply block missing')
s=s.replace(old,new,1)
# Provider ingest
s=s.replace("st.checkpoint('PROVIDER_INGEST',out.get('status'))\n        materialize_review_workspace(project,st.data)","st.checkpoint('PROVIDER_INGEST',out.get('status'))\n        refresh_review_workspace(project,st)",1)
# Revision compile/ingest
s=s.replace("st.data['local_revision_requests']=st.data.get('local_revision_requests',[]); st.save(); st.checkpoint('LOCAL_REVISION_COMPILE',out.get('status')); materialize_review_workspace(project,st.data)","st.data['local_revision_requests']=st.data.get('local_revision_requests',[]); st.save(); st.checkpoint('LOCAL_REVISION_COMPILE',out.get('status')); refresh_review_workspace(project,st)",1)
s=s.replace("out=ingest_local_revision_results(project,st.data,a.revision_id); st.save(); st.checkpoint('LOCAL_REVISION_INGEST',out.get('status')); materialize_review_workspace(project,st.data)","out=ingest_local_revision_results(project,st.data,a.revision_id); st.save(); st.checkpoint('LOCAL_REVISION_INGEST',out.get('status')); refresh_review_workspace(project,st)",1)
# Learning apply
s=s.replace("st.set_gate('MEASUREMENT','READY_REVIEW',[str(lp)],learning); st.set_gate('LEARNING','READY_REVIEW',[str(project/'artifacts/learning_latest.json'),str(project/'artifacts/strategy_authority.json')],applied); st.checkpoint('LEARNING_APPLY',applied.get('status')); materialize_review_workspace(project,st.data); out={'learning':learning,'strategy_apply':applied}","st.set_gate('MEASUREMENT','READY_REVIEW',[str(lp)],learning); st.set_gate('LEARNING','READY_REVIEW',[str(project/'artifacts/learning_latest.json'),str(project/'artifacts/strategy_authority.json')],applied); st.checkpoint('LEARNING_APPLY',applied.get('status')); refresh_review_workspace(project,st); out={'learning':learning,'strategy_apply':applied,'final_ready':st.data.get('final_ready'),'completion':st.data.get('completion')}",1)
old="""    elif a.cmd=='export':
        st=ProjectState.load(Path(a.project_dir)); locked=[g for g,v in st.data['gates'].items() if v['status']=='LOCKED']
        required=['EVIDENCE','PRODUCT_TRUTH','COMMERCE_ENTITY','TARGET_CONTEXT','CULTURE_CONTEXT','DECISION','CONTENT_GRAPH','PLATFORM_COMPILE','ASSET_ARCHITECTURE','CREATIVE','EXECUTION']
        for optional in ['ASSET_COMPILE','PRODUCTION']:
            if st.data['gates'][optional]['status']!='PENDING': required.append(optional)
        unresolved=[x for x in st.data['pending_actions'] if x.get('status')=='PENDING']
        final_ready=all(g in locked for g in required) and not unresolved
        manifest={'project_id':st.data['project_id'],'final_ready':final_ready,'locked_gates':locked,'pending_actions':st.data['pending_actions'],'artifacts':{g:v['artifact_paths'] for g,v in st.data['gates'].items() if v['artifact_paths']}}
        Path(a.output).write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8'); out=manifest
"""
new="""    elif a.cmd=='export':
        project=Path(a.project_dir); st=ProjectState.load(project); refresh_review_workspace(project,st)
        delivery=build_delivery_manifest(project,st.data)
        locked=[g for g,v in st.data['gates'].items() if v['status']=='LOCKED']
        manifest={
            'project_id':st.data['project_id'],'final_ready':delivery.get('final_ready',False),
            'completion':delivery.get('completion') or st.data.get('completion') or {},
            'locked_gates':locked,'pending_actions':st.data['pending_actions'],
            'required_missing':delivery.get('required_missing',[]),'review_pending':delivery.get('review_pending',[]),
            'artifacts':{g:v['artifact_paths'] for g,v in st.data['gates'].items() if v['artifact_paths']}
        }
        Path(a.output).write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8'); out=manifest
"""
if old not in s: raise SystemExit('cli export block missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

print('v0.6.27 completion integration patch applied')
