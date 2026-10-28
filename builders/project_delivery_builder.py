#!/usr/bin/env python3
from pathlib import Path
import sys, json, shutil, zipfile, hashlib

# Make the packaged runtime available when this builder is called directly.
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT/'runtime') not in sys.path: sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.delivery_html import build_delivery_html
from cbcc.human_delivery import compile_upload_center, render_upload_center_md, build_project_hub_md


def sha256(path:Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

project=Path(sys.argv[1]) if len(sys.argv)>1 else Path('project')
out=Path(sys.argv[2]) if len(sys.argv)>2 else Path('dist')
out.mkdir(parents=True,exist_ok=True)
required=[project/'artifacts/strategy/MASTER_STRATEGY_CN.md',project/'artifacts/strategy/strategy_authority.json']
missing=[str(x) for x in required if not x.exists()]
if missing: raise SystemExit('BLOCKED missing strategy authority: '+', '.join(missing))

pkg=out/f'{project.name}_DELIVERY'
if pkg.exists(): shutil.rmtree(pkg)
pkg.mkdir(parents=True)
# Strategy is the human-facing top layer.
shutil.copytree(project/'artifacts/strategy',pkg/'strategy')
# Preserve independent asset packages exactly as compiled.
asset_root=project/'artifacts/asset_packages'
if asset_root.exists(): shutil.copytree(asset_root,pkg/'asset_packages')
# Add strategy evidence / deterministic analyses in a human-readable package structure.
support=pkg/'supporting_analysis'; support.mkdir(exist_ok=True)
for rel in [
    'artifacts/strategy_reasoning_context.json','artifacts/strategy_host_authoring_request.json','artifacts/source_product_assets.json','artifacts/research_source_adapter_refresh.json','artifacts/research_source_adapter_state.json','artifacts/product_truth.json','artifacts/target_context.json','artifacts/culture_context.json',
    'artifacts/market_analysis.json','artifacts/offer_economics.json','artifacts/listing_analysis.json','artifacts/listing_final_copy.json','artifacts/listing_copy_authoring_tasks.json','artifacts/listing_copy_revision_tasks.json','artifacts/listing_copy_review_tasks.json','artifacts/listing_copy_host_authoring_requests.json','artifacts/listing_copy_host_authoring_apply.json','artifacts/ad_analysis.json','artifacts/feedback_analysis.json','artifacts/experiment_analysis.json',
    'artifacts/asset_architecture.json','artifacts/learning_latest.json','artifacts/production_learning_loop.json','artifacts/creative_contract.json','artifacts/curation.json','artifacts/cmf_contract.json','artifacts/inclusive_photography.json','artifacts/photography_validation.json',
    'artifacts/video_creator_plan.json','artifacts/compliance_report.json','artifacts/platform_compile.json','artifacts/research_gate.json','artifacts/market_evidence_fit_contract.json','artifacts/strategy_revision_routing.json','artifacts/capability_integration_map.json','artifacts/execution_contract.json','artifacts/production_run.json'
]:
    src=project/rel
    if src.exists() and src.is_file(): shutil.copy2(src,support/src.name)
# Human-first delivery: one project hub + one upload-ready listing center + deep files preserved.
center=compile_upload_center(project)
(pkg/'HUMAN_DELIVERY.json').write_text(json.dumps(center,ensure_ascii=False,indent=2),encoding='utf-8')
(pkg/'01_LISTING_UPLOAD_READY.md').write_text(render_upload_center_md(center),encoding='utf-8')
(pkg/'00_PROJECT_HUB.md').write_text(build_project_hub_md(center),encoding='utf-8')
# Complete designed HTML report: all human-facing content is embedded; source files remain editable authority.
build_delivery_html(pkg, pkg/'index.html', title=f'{project.name} · CBCC Delivery')

# Provider jobs and review workspace remain separately inspectable.
for rel,dest in [('artifacts/provider_jobs','provider_jobs'),('artifacts/local_revisions','local_revisions'),('artifacts/learning_cycles','learning_cycles'),('.cbcc/review','review_workspace'),('artifacts/listing_final_copy','listing_final_copy')]:
    src=project/rel
    if src.exists() and src.is_dir(): shutil.copytree(src,pkg/dest)
manifest={'html_index':'index.html','project_hub':'00_PROJECT_HUB.md','listing_upload_ready':'01_LISTING_UPLOAD_READY.md','human_delivery_contract':'HUMAN_DELIVERY.json','strategy_authority':'strategy/MASTER_STRATEGY_CN.md','strategy_decision_index':'strategy/STRATEGY_DECISION_INDEX.json','asset_package_preserved':asset_root.exists(),'supporting_analysis':'supporting_analysis/','listing_final_copy':'listing_final_copy/' if (pkg/'listing_final_copy').exists() else None,'provider_jobs':'provider_jobs/' if (pkg/'provider_jobs').exists() else None,'local_revisions':'local_revisions/' if (pkg/'local_revisions').exists() else None,'learning_cycles':'learning_cycles/' if (pkg/'learning_cycles').exists() else None,'review_workspace':'review_workspace/' if (pkg/'review_workspace').exists() else None,'files':[]}
for f in sorted(pkg.rglob('*')):
    if f.is_file(): manifest['files'].append({'path':str(f.relative_to(pkg)),'sha256':sha256(f),'bytes':f.stat().st_size})
(pkg/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
zip_path=out/f'{pkg.name}.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for f in pkg.rglob('*'):
        if f.is_file(): z.write(f,f.relative_to(pkg.parent))
print(zip_path)
