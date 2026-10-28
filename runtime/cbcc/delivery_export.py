from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import shutil
import zipfile

from .delivery_workspace import build_delivery_html
from .human_delivery import compile_upload_center, render_upload_center_md, build_project_hub_md


_SUPPORT_FILES = [
    'artifacts/strategy_reasoning_context.json','artifacts/strategy_host_authoring_request.json',
    'artifacts/source_product_assets.json','artifacts/research_source_adapter_refresh.json',
    'artifacts/research_source_adapter_state.json','artifacts/product_truth.json','artifacts/target_context.json',
    'artifacts/culture_context.json','artifacts/market_analysis.json','artifacts/offer_economics.json',
    'artifacts/listing_analysis.json','artifacts/listing_final_copy.json','artifacts/listing_copy_authoring_tasks.json',
    'artifacts/listing_copy_revision_tasks.json','artifacts/listing_copy_review_tasks.json',
    'artifacts/listing_copy_host_authoring_requests.json','artifacts/listing_copy_host_authoring_apply.json',
    'artifacts/ad_analysis.json','artifacts/feedback_analysis.json','artifacts/experiment_analysis.json',
    'artifacts/asset_architecture.json','artifacts/learning_latest.json','artifacts/production_learning_loop.json',
    'artifacts/creative_contract.json','artifacts/curation.json','artifacts/cmf_contract.json',
    'artifacts/inclusive_photography.json','artifacts/photography_validation.json','artifacts/video_creator_plan.json',
    'artifacts/compliance_report.json','artifacts/platform_compile.json','artifacts/research_gate.json',
    'artifacts/market_evidence_fit_contract.json','artifacts/strategy_revision_routing.json',
    'artifacts/capability_integration_map.json','artifacts/execution_contract.json','artifacts/production_run.json',
    'artifacts/decision_question_authority.json','artifacts/strategy_authority.json','artifacts/gate_scope.json',
    'artifacts/content_requiredness.json','artifacts/agent_next_action.json','artifacts/agent_autonomy_plan.json',
]

_EXTRA_DIRS = [
    ('artifacts/provider_jobs','provider_jobs'),
    ('artifacts/local_revisions','local_revisions'),
    ('artifacts/learning_cycles','learning_cycles'),
    ('.cbcc/review','review_workspace'),
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _copy_file_or_dir(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _resolve_output(project: Path, output: Path) -> tuple[Path, Path]:
    output = Path(output)
    if output.suffix.lower() == '.zip':
        zip_path = output
        package_dir = output.with_suffix('')
    else:
        package_dir = output
        zip_path = output.parent / f'{output.name}.zip'
    if package_dir.name == project.name:
        package_dir = package_dir.with_name(f'{project.name}_DELIVERY')
        zip_path = package_dir.with_suffix('.zip')
    return package_dir, zip_path


def export_delivery_package(project_dir: Path, output: Path) -> dict[str, Any]:
    """Materialize the actual CBCC human delivery, not merely a machine manifest.

    Output always includes a complete directory and a ZIP. The directory contains a self-contained
    offline index.html, Chinese-first human hub, Listing workspace when relevant, editable strategy
    sources, preserved per-asset packages and machine/supporting authorities.
    """
    project = Path(project_dir)
    package_dir, zip_path = _resolve_output(project, Path(output))

    required = [
        project / 'artifacts/strategy/MASTER_STRATEGY_CN.md',
        project / 'artifacts/strategy/strategy_authority.json',
    ]
    missing = [str(x) for x in required if not x.exists()]
    if missing:
        raise FileNotFoundError('BLOCKED missing strategy authority: ' + ', '.join(missing))

    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()

    shutil.copytree(project / 'artifacts/strategy', package_dir / 'strategy')

    asset_root = project / 'artifacts/asset_packages'
    if asset_root.exists():
        shutil.copytree(asset_root, package_dir / 'asset_packages')

    support = package_dir / 'supporting_analysis'
    support.mkdir(exist_ok=True)
    for rel in _SUPPORT_FILES:
        src = project / rel
        if src.exists() and src.is_file():
            shutil.copy2(src, support / src.name)

    center = compile_upload_center(project)
    (package_dir / 'HUMAN_DELIVERY.json').write_text(
        json.dumps(center, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    (package_dir / '01_LISTING_UPLOAD_READY.md').write_text(
        render_upload_center_md(center), encoding='utf-8'
    )
    (package_dir / '00_PROJECT_HUB.md').write_text(
        build_project_hub_md(center), encoding='utf-8'
    )

    build_delivery_html(package_dir, package_dir / 'index.html', title=f'{project.name} · CBCC Delivery')

    for rel, dest in _EXTRA_DIRS:
        src = project / rel
        if src.exists():
            _copy_file_or_dir(src, package_dir / dest)

    listing_final = project / 'artifacts/listing_final_copy'
    if listing_final.exists():
        suffix = 'listing_final_copy' if listing_final.is_dir() else f'listing_final_copy{listing_final.suffix}'
        _copy_file_or_dir(listing_final, package_dir / suffix)

    files = []
    for f in sorted(package_dir.rglob('*')):
        if f.is_file():
            files.append({
                'path': str(f.relative_to(package_dir)).replace('\\', '/'),
                'sha256': _sha256(f),
                'bytes': f.stat().st_size,
            })

    html_text = (package_dir / 'index.html').read_text(encoding='utf-8')
    manifest = {
        'status': 'DELIVERY_READY',
        'project': project.name,
        'package_dir': str(package_dir),
        'zip_path': str(zip_path),
        'html_index': 'index.html',
        'project_hub': '00_PROJECT_HUB.md',
        'listing_upload_ready': '01_LISTING_UPLOAD_READY.md',
        'human_delivery_contract': 'HUMAN_DELIVERY.json',
        'strategy_authority': 'strategy/MASTER_STRATEGY_CN.md',
        'strategy_decision_index': 'strategy/STRATEGY_DECISION_INDEX.json',
        'asset_package_preserved': asset_root.exists(),
        'supporting_analysis': 'supporting_analysis/',
        'workspace_contract': {
            'complete_human_html': bool(html_text.strip()),
            'chinese_first': '默认中文交付' in html_text or '交付语言' in html_text,
            'object_based_asset_workspace': 'data-workspace-kind="asset-object"' in html_text or not asset_root.exists(),
            'obsolete_phase_rail_absent': 'asset-production-rail' not in html_text and 'asset-phase' not in html_text,
        },
        'files': files,
    }
    (package_dir / 'DELIVERY_MANIFEST.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8'
    )

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(package_dir.rglob('*')):
            if f.is_file():
                zf.write(f, Path(package_dir.name) / f.relative_to(package_dir))

    manifest['zip_sha256'] = _sha256(zip_path)
    manifest['zip_bytes'] = zip_path.stat().st_size
    (package_dir / 'DELIVERY_MANIFEST.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    return manifest
