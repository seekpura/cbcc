from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib, json, shutil, zipfile

from .delivery_workspace import build_delivery_html
from .human_delivery import compile_upload_center, render_upload_center_md, build_project_hub_md
from .human_language_delivery import normalize_upload_center
from .global_chinese_interpretation import normalize_global_chinese_interpretation, render_upload_center_md_with_global_cn
from .final_chinese_interpretation_audit import audit_final_chinese_interpretation
from .chinese_interpretation_ui import apply_chinese_interpretation_ui
from .delivery_contract import validate_strategy_delivery
from .platform_scope import resolve_platform_scope
from .delivery_language_matrix import build_language_delivery_plan, audit_language_delivery
from .source_truth_media import materialize_source_truth_media
from .commercial_workspace_shell import apply_commercial_workspace_shell, WORKSPACE_SHELL_VERSION

_SUPPORT_FILES=[
'artifacts/strategy_reasoning_context.json','artifacts/strategy_host_authoring_request.json','artifacts/source_product_assets.json','artifacts/research_source_adapter_refresh.json','artifacts/research_source_adapter_state.json','artifacts/product_truth.json','artifacts/target_context.json','artifacts/culture_context.json','artifacts/market_analysis.json','artifacts/offer_economics.json','artifacts/listing_analysis.json','artifacts/listing_final_copy.json','artifacts/listing_copy_authoring_tasks.json','artifacts/listing_copy_revision_tasks.json','artifacts/listing_copy_review_tasks.json','artifacts/listing_copy_host_authoring_requests.json','artifacts/listing_copy_host_authoring_apply.json','artifacts/ad_analysis.json','artifacts/feedback_analysis.json','artifacts/experiment_analysis.json','artifacts/asset_architecture.json','artifacts/learning_latest.json','artifacts/production_learning_loop.json','artifacts/creative_contract.json','artifacts/curation.json','artifacts/cmf_contract.json','artifacts/inclusive_photography.json','artifacts/photography_validation.json','artifacts/video_creator_plan.json','artifacts/compliance_report.json','artifacts/platform_compile.json','artifacts/research_gate.json','artifacts/market_evidence_fit_contract.json','artifacts/strategy_revision_routing.json','artifacts/capability_integration_map.json','artifacts/execution_contract.json','artifacts/production_run.json','artifacts/decision_question_authority.json','artifacts/strategy_authority.json','artifacts/gate_scope.json','artifacts/content_requiredness.json','artifacts/agent_next_action.json','artifacts/agent_autonomy_plan.json','artifacts/seven_agent_synthesis.json']
_EXTRA_DIRS=[('artifacts/provider_jobs','provider_jobs'),('artifacts/local_revisions','local_revisions'),('artifacts/learning_cycles','learning_cycles'),('.cbcc/review','review_workspace')]

def _sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def _copy_file_or_dir(src:Path,dst:Path)->None:
    if not src.exists():return
    if src.is_dir():shutil.copytree(src,dst)
    else:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)

def _read_json(path:Path)->dict[str,Any]:
    if not path.exists():return {}
    try:
        data=json.loads(path.read_text(encoding='utf-8'));return data if isinstance(data,dict) else {}
    except Exception:return {}

def _prompt_consumption_summary(asset_root:Path)->dict[str,Any]:
    rows=[]
    if asset_root.exists():
        for contract in sorted(asset_root.glob('*/13_prompt_contract.json')):
            data=_read_json(contract);audit=data.get('prompt_consumption_audit') or {};asset_id=contract.parent.name
            rows.append({'asset_id':asset_id,'status':audit.get('status') or 'MISSING','missing_decisions':audit.get('missing_decisions') or (['PROMPT_CONSUMPTION_AUDIT_MISSING'] if not audit else []),'checks':audit.get('checks') or []})
    missing=[r for r in rows if r.get('status')!='PASS' or r.get('missing_decisions')]
    return {'status':'READY' if not missing else 'NEEDS_PROMPT_WORK','project_completion_blocking':False,'asset_count':len(rows),'assets':rows,'missing_assets':[r.get('asset_id') for r in missing],'principle':'Prompt/generation-plan readiness is advisory for the project and asset delivery. It becomes locally blocking only for an explicitly requested prompt-ready or provider-execution sub-deliverable.'}

def _full_html_depth_check(html_text:str,full:bool)->dict[str,Any]:
    if not full:return {'status':'NOT_REQUIRED_FOR_TASK_SCOPED','missing':[]}
    required=['信息完整度、待确认清单、假设与决策日志','产品真实事实审计与卖点分级表','平台 × 区域 × 人群 × 族裔文化洞察','营销框架与核心策略','视觉总策略与拍摄执行清单','分平台内容矩阵表','RACE传播框架执行表','族裔文化适配检查表','合规、文化敏感与风险清单；评估指标与A/B测试建议；P0/P1/P2执行优先级与下一步需补充信息']
    missing=[x for x in required if x not in html_text]
    return {'status':'PASS' if not missing else 'INCOMPLETE','required_visible_objects':required,'missing':missing}

def _resolve_output(project:Path,output:Path)->tuple[Path,Path]:
    output=Path(output)
    if output.suffix.lower()=='.zip':zip_path=output;package_dir=output.with_suffix('')
    else:package_dir=output;zip_path=output.parent/f'{output.name}.zip'
    if package_dir.name==project.name:package_dir=package_dir.with_name(f'{project.name}_DELIVERY');zip_path=package_dir.with_suffix('.zip')
    return package_dir,zip_path

def _apply_explicit_scope(center:dict[str,Any],scope:dict[str,Any],language_plan:dict[str,Any])->dict[str,Any]:
    target=dict(center.get('target') or {})
    target.update({'platform':scope.get('platform'),'market':scope.get('market'),'site':scope.get('site'),'locale':scope.get('primary_locale'),'platform_status':scope.get('platform_status'),'market_status':scope.get('market_status'),'primary_locale_status':scope.get('primary_locale_status')})
    center['target']=target;center['platform_scope']=scope;center['delivery_language_plan']=language_plan;return center

def export_delivery_package(project_dir:Path,output:Path)->dict[str,Any]:
    project=Path(project_dir);package_dir,zip_path=_resolve_output(project,Path(output))
    required=[project/'artifacts/strategy/MASTER_STRATEGY_CN.md',project/'artifacts/strategy/strategy_authority.json']
    missing=[str(x) for x in required if not x.exists()]
    if missing:raise FileNotFoundError('BLOCKED missing strategy authority: '+', '.join(missing))
    strategy_authority=_read_json(project/'artifacts/strategy/strategy_authority.json');depth_audit=validate_strategy_delivery(strategy_authority);full=depth_audit.get('mode')=='FULL'
    if full and depth_audit.get('status')!='PASS':raise RuntimeError('BLOCKED FULL delivery depth contract failed: '+json.dumps(depth_audit.get('issues') or [],ensure_ascii=False))
    if package_dir.exists():shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True,exist_ok=True);zip_path.parent.mkdir(parents=True,exist_ok=True)
    if zip_path.exists():zip_path.unlink()
    shutil.copytree(project/'artifacts/strategy',package_dir/'strategy')
    asset_root=project/'artifacts/asset_packages';prompt_audit=_prompt_consumption_summary(asset_root)
    if asset_root.exists():shutil.copytree(asset_root,package_dir/'asset_packages')
    (package_dir/'FULL_DELIVERY_DEPTH_AUDIT.json').write_text(json.dumps(depth_audit,ensure_ascii=False,indent=2),encoding='utf-8')
    (package_dir/'PROMPT_CONSUMPTION_AUDIT.json').write_text(json.dumps(prompt_audit,ensure_ascii=False,indent=2),encoding='utf-8')
    support=package_dir/'supporting_analysis';support.mkdir(exist_ok=True)
    for rel in _SUPPORT_FILES:
        src=project/rel
        if src.exists() and src.is_file():shutil.copy2(src,support/src.name)
    source_media_audit=materialize_source_truth_media(project,package_dir)
    scope=resolve_platform_scope(project);language_plan=build_language_delivery_plan(scope)
    center=normalize_global_chinese_interpretation(normalize_upload_center(compile_upload_center(project)));center=_apply_explicit_scope(center,scope,language_plan)
    language_matrix_audit=audit_language_delivery(center,language_plan);center['delivery_language_audit']=language_matrix_audit
    (package_dir/'HUMAN_DELIVERY.json').write_text(json.dumps(center,ensure_ascii=False,indent=2),encoding='utf-8')
    (package_dir/'DELIVERY_LANGUAGE_MATRIX_AUDIT.json').write_text(json.dumps(language_matrix_audit,ensure_ascii=False,indent=2),encoding='utf-8')
    (package_dir/'PLATFORM_SCOPE.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2),encoding='utf-8')
    (package_dir/'01_LISTING_UPLOAD_READY.md').write_text(render_upload_center_md_with_global_cn(center,render_upload_center_md),encoding='utf-8')
    (package_dir/'00_PROJECT_HUB.md').write_text(build_project_hub_md(center),encoding='utf-8')
    if (center.get('task_scope') or {}).get('listing_active') and language_matrix_audit.get('status')=='INCOMPLETE':
        raise RuntimeError('BLOCKED delivery language matrix incomplete: '+json.dumps(language_matrix_audit.get('missing') or [],ensure_ascii=False))
    html_path=build_delivery_html(package_dir,package_dir/'index.html',title=f'{project.name} · CBCC Delivery')
    rendered=apply_chinese_interpretation_ui(html_path.read_text(encoding='utf-8'));rendered=apply_commercial_workspace_shell(rendered,scope,language_plan);html_path.write_text(rendered,encoding='utf-8')
    for rel,dest in _EXTRA_DIRS:
        src=project/rel
        if src.exists():_copy_file_or_dir(src,package_dir/dest)
    listing_final=project/'artifacts/listing_final_copy'
    if listing_final.exists():_copy_file_or_dir(listing_final,package_dir/('listing_final_copy' if listing_final.is_dir() else f'listing_final_copy{listing_final.suffix}'))
    language_audit=audit_final_chinese_interpretation(package_dir,center);(package_dir/'HUMAN_LANGUAGE_AUDIT.json').write_text(json.dumps(language_audit,ensure_ascii=False,indent=2),encoding='utf-8')
    if language_audit.get('status')!='PASS':raise RuntimeError('BLOCKED global Chinese interpretation contract failed: '+json.dumps(language_audit.get('issues') or [],ensure_ascii=False))
    files=[]
    for f in sorted(package_dir.rglob('*')):
        if f.is_file():files.append({'path':str(f.relative_to(package_dir)).replace('\\','/'),'sha256':_sha256(f),'bytes':f.stat().st_size})
    html_text=(package_dir/'index.html').read_text(encoding='utf-8');html_depth=_full_html_depth_check(html_text,full)
    if full and html_depth.get('status')!='PASS':raise RuntimeError('BLOCKED FULL HTML visible depth objects missing: '+', '.join(html_depth.get('missing') or []))
    manifest={'status':'DELIVERY_READY','project':project.name,'package_dir':str(package_dir),'zip_path':str(zip_path),'html_index':'index.html','project_hub':'00_PROJECT_HUB.md','listing_upload_ready':'01_LISTING_UPLOAD_READY.md','human_delivery_contract':'HUMAN_DELIVERY.json','human_language_audit':'HUMAN_LANGUAGE_AUDIT.json','delivery_language_matrix_audit':'DELIVERY_LANGUAGE_MATRIX_AUDIT.json','platform_scope':'PLATFORM_SCOPE.json','source_truth_media_audit':'SOURCE_TRUTH_MEDIA_AUDIT.json','full_delivery_depth_audit':'FULL_DELIVERY_DEPTH_AUDIT.json','prompt_consumption_audit':'PROMPT_CONSUMPTION_AUDIT.json','strategy_authority':'strategy/MASTER_STRATEGY_CN.md','strategy_decision_index':'strategy/STRATEGY_DECISION_INDEX.json','asset_package_preserved':asset_root.exists(),'supporting_analysis':'supporting_analysis/','workspace_contract':{'shell_version':WORKSPACE_SHELL_VERSION,'complete_human_html':bool(html_text.strip()),'chinese_first':'默认中文交付' in html_text or '交付语言' in html_text or '中文释义' in html_text,'explicit_platform_scope_only':scope.get('platform_status') in {'EXPLICIT','UNSPECIFIED'},'no_silent_platform_default':scope.get('platform_status')!='INFERRED','delivery_language_matrix':language_matrix_audit.get('status'),'source_truth_media':source_media_audit.get('status'),'self_contained_source_media':source_media_audit.get('copied_count',0)==0 or 'data:image/' in html_text,'foreign_human_copy_has_chinese_companion':language_audit.get('status')=='PASS','global_human_foreign_content_has_chinese_companion':(language_audit.get('global_human_content') or {}).get('final_status')=='PASS','listing_human_field_titles_chinese_first':(language_audit.get('listing') or {}).get('status')=='PASS','asset_foreign_visible_copy_has_chinese_companion':(language_audit.get('assets') or {}).get('status')=='PASS','object_based_asset_workspace':'data-workspace-kind="asset-object"' in html_text or not asset_root.exists(),'obsolete_phase_rail_absent':'asset-production-rail' not in html_text and 'asset-phase' not in html_text,'full_decision_depth':depth_audit.get('status') if full else 'NOT_REQUIRED_FOR_TASK_SCOPED','full_visible_objects':html_depth.get('status'),'prompt_generation_readiness':prompt_audit.get('status') if asset_root.exists() else 'NO_ASSETS','prompt_generation_readiness_blocks_project_completion':False},'files':files}
    (package_dir/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(package_dir.rglob('*')):
            if f.is_file():zf.write(f,Path(package_dir.name)/f.relative_to(package_dir))
    manifest['zip_sha256']=_sha256(zip_path);manifest['zip_bytes']=zip_path.stat().st_size;(package_dir/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');return manifest
