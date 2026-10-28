from __future__ import annotations
from pathlib import Path
import argparse,json,sys
from .state import ProjectState
from .compiler import build_project
from .audit import machine_audit
from .review import materialize_review_workspace, refresh_review_workspace, build_delivery_manifest
from .production import ingest_provider_job_results
from .provider_bridge import ExecutionPolicy
from .provider_surface import provider_execution_surface_from_environment
from .learning_loop import compile_local_revision_jobs, ingest_local_revision_results, compile_learning_cycle, apply_learning_to_strategy, sync_local_revision_review_state

def main(argv=None):
    ap=argparse.ArgumentParser(prog='cbcc')
    sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('init'); p.add_argument('--project-dir',required=True); p.add_argument('--project-id',required=True)
    p=sp.add_parser('build'); p.add_argument('--project-dir',required=True); p.add_argument('--request',required=True); p.add_argument('--packs-dir')
    p=sp.add_parser('resume'); p.add_argument('--project-dir',required=True); p.add_argument('--request'); p.add_argument('--packs-dir')
    p=sp.add_parser('revise'); p.add_argument('--project-dir',required=True); p.add_argument('--changed',nargs='+',required=True)
    p=sp.add_parser('review-build'); p.add_argument('--project-dir',required=True)
    p=sp.add_parser('review-apply'); p.add_argument('--project-dir',required=True); p.add_argument('--review-file',required=True)
    p=sp.add_parser('adapter-list'); p.add_argument('--provider'); p.add_argument('--production-mode'); p.add_argument('--capability',action='append')
    p=sp.add_parser('provider-execute'); p.add_argument('--project-dir',required=True); p.add_argument('--asset-id',action='append'); p.add_argument('--adapter-id'); p.add_argument('--max-attempts',type=int,default=3); p.add_argument('--max-polls',type=int,default=8)
    p=sp.add_parser('provider-cancel'); p.add_argument('--project-dir',required=True); p.add_argument('--asset-id',required=True); p.add_argument('--adapter-id'); p.add_argument('--reason')
    p=sp.add_parser('provider-reconcile'); p.add_argument('--project-dir',required=True); p.add_argument('--asset-id',required=True); p.add_argument('--adapter-id')
    p=sp.add_parser('provider-ingest'); p.add_argument('--project-dir',required=True)
    p=sp.add_parser('revision-compile'); p.add_argument('--project-dir',required=True); p.add_argument('--revision-request-id',action='append')
    p=sp.add_parser('revision-ingest'); p.add_argument('--project-dir',required=True); p.add_argument('--revision-id',action='append')
    p=sp.add_parser('learning-apply'); p.add_argument('--project-dir',required=True); p.add_argument('--learning-file',required=True)
    p=sp.add_parser('state'); p.add_argument('--project-dir',required=True)
    p=sp.add_parser('audit'); p.add_argument('--root',default=str(Path(__file__).resolve().parents[2])); p.add_argument('--no-pytest',action='store_true')
    p=sp.add_parser('export'); p.add_argument('--project-dir',required=True); p.add_argument('--output',required=True)
    a=ap.parse_args(argv)
    root=Path(__file__).resolve().parents[2]
    if a.cmd=='init': out=ProjectState.init(Path(a.project_dir),a.project_id).data
    elif a.cmd in {'build','resume'}:
        request_path=Path(a.request) if getattr(a,'request',None) else Path(a.project_dir)/'.cbcc/request.json'
        if not request_path.exists(): raise FileNotFoundError(f'No request available for {a.cmd}: {request_path}')
        req=json.loads(request_path.read_text(encoding='utf-8')); out=build_project(Path(a.project_dir),req,Path(a.packs_dir) if a.packs_dir else root/'platform_packs')
    elif a.cmd=='revise':
        project=Path(a.project_dir); st=ProjectState.load(project); invalidated=st.revise(a.changed); refresh_review_workspace(project,st); out={'invalidated':invalidated,'final_ready':st.data.get('final_ready'),'completion':st.data.get('completion')}
    elif a.cmd=='review-build':
        project=Path(a.project_dir); st=ProjectState.load(project); out=refresh_review_workspace(project,st)
    elif a.cmd=='review-apply':
        project=Path(a.project_dir); st=ProjectState.load(project); d=json.loads(Path(a.review_file).read_text(encoding='utf-8')); st.apply_review_decision(d); sync_local_revision_review_state(project,st.data); refresh_review_workspace(project,st); out=st.data
    elif a.cmd=='adapter-list':
        surface=provider_execution_surface_from_environment(); out=surface.list_adapters(provider=a.provider,production_mode=a.production_mode,required_capabilities=a.capability)
    elif a.cmd=='provider-execute':
        surface=provider_execution_surface_from_environment(); policy=ExecutionPolicy(max_attempts=max(1,a.max_attempts),max_polls_per_attempt=max(0,a.max_polls)); out=surface.execute_project(Path(a.project_dir),asset_ids=a.asset_id,adapter_id=a.adapter_id,policy=policy)
    elif a.cmd=='provider-cancel':
        surface=provider_execution_surface_from_environment(); requested=surface.request_cancel(Path(a.project_dir),a.asset_id,reason=a.reason); cancelled=surface.cancel_project_job(Path(a.project_dir),a.asset_id,adapter_id=a.adapter_id); out={'request':requested,'cancel':cancelled,'status':cancelled.get('status')}
    elif a.cmd=='provider-reconcile':
        surface=provider_execution_surface_from_environment(); out=surface.reconcile_project_job(Path(a.project_dir),a.asset_id,adapter_id=a.adapter_id)
    elif a.cmd=='provider-ingest':
        project=Path(a.project_dir); run_path=project/'artifacts/production_run.json'
        if not run_path.exists(): raise FileNotFoundError(f'No production run found: {run_path}')
        run=json.loads(run_path.read_text(encoding='utf-8'))
        out=ingest_provider_job_results(run,project/'artifacts/provider_jobs')
        run_path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
        st=ProjectState.load(project)
        st.set_gate('PRODUCTION','READY_REVIEW' if out.get('status')=='COMPLETE' else 'PENDING',[str(run_path),str(project/'artifacts/provider_jobs/PROVIDER_JOB_INDEX.json')],out)
        st.checkpoint('PROVIDER_INGEST',out.get('status'))
        refresh_review_workspace(project,st)
    elif a.cmd=='revision-compile':
        project=Path(a.project_dir); st=ProjectState.load(project); req_path=project/'.cbcc/request.json'; req=json.loads(req_path.read_text(encoding='utf-8')) if req_path.exists() else {}
        out=compile_local_revision_jobs(project,st.data,req.get('production_provider_preferences'),a.revision_request_id)
        st.data['local_revision_requests']=st.data.get('local_revision_requests',[]); st.save(); st.checkpoint('LOCAL_REVISION_COMPILE',out.get('status')); refresh_review_workspace(project,st)
    elif a.cmd=='revision-ingest':
        project=Path(a.project_dir); st=ProjectState.load(project); out=ingest_local_revision_results(project,st.data,a.revision_id); st.save(); st.checkpoint('LOCAL_REVISION_INGEST',out.get('status')); refresh_review_workspace(project,st)
    elif a.cmd=='learning-apply':
        project=Path(a.project_dir); st=ProjectState.load(project); cycle=json.loads(Path(a.learning_file).read_text(encoding='utf-8')); learning=compile_learning_cycle(project,st.data,cycle); applied=apply_learning_to_strategy(project,learning)
        lp=project/'artifacts/learning_cycles'/learning['cycle_id']/'learning_cycle.json'; st.set_gate('MEASUREMENT','READY_REVIEW',[str(lp)],learning); st.set_gate('LEARNING','READY_REVIEW',[str(project/'artifacts/learning_latest.json'),str(project/'artifacts/strategy_authority.json')],applied); st.checkpoint('LEARNING_APPLY',applied.get('status')); refresh_review_workspace(project,st); out={'learning':learning,'strategy_apply':applied,'final_ready':st.data.get('final_ready'),'completion':st.data.get('completion')}
    elif a.cmd=='state': out=ProjectState.load(Path(a.project_dir)).data
    elif a.cmd=='audit': out=machine_audit(Path(a.root),not a.no_pytest)
    elif a.cmd=='export':
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
    print(json.dumps(out,ensure_ascii=False,indent=2)); return 0 if not isinstance(out,dict) or out.get('pass',True) else 1
if __name__=='__main__': raise SystemExit(main())
