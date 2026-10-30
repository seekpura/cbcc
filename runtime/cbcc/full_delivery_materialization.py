from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
import hashlib
import json
import shutil
import zipfile

from .asset_portfolio_taxonomy import enrich_asset_portfolio_taxonomy, portfolio_taxonomy_summary
from .full_delivery_depth_v3 import audit_host_full_package


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _target(project: Path) -> dict[str, Any]:
    raw = _read_json(project / 'artifacts/target_context.json')
    return raw.get('target') if isinstance(raw.get('target'), dict) else raw


def compile_export_asset_universe(project: Path) -> dict[str, Any]:
    arch = _read_json(project / 'artifacts/asset_architecture.json')
    assets = enrich_asset_portfolio_taxonomy(arch.get('assets') or [])
    target = _target(project)
    summary = portfolio_taxonomy_summary(assets, target)
    base = deepcopy(arch.get('asset_universe') or {})
    base.update({
        'status': base.get('status') or 'DYNAMIC_ASSET_UNIVERSE',
        'fixed_total_asset_limit': False,
        'platform_capacity_is_activation_constraint_only': True,
        'activation_capacity': summary.get('activation_capacity') or base.get('platform_capacity'),
        'platform_capacity': summary.get('activation_capacity') or base.get('platform_capacity'),
        'activation_capacity_does_not_prune_universe': True,
        'total_asset_candidates': len(assets),
        'assets': assets,
        'asset_family_counts': summary.get('asset_family_counts') or {},
        'deployment_state_counts': summary.get('deployment_state_counts') or {},
        'principle': 'Platform gallery/video capacity limits the simultaneous Activation Set only; all useful Hero/PDP/A+/Paid/Social/Creator/Video/Test/Rotation candidates remain in the exported Asset Universe.',
    })
    return base


def _copy_machine_authorities(project: Path, package: Path) -> list[str]:
    """Preserve current top-level machine authorities instead of a hand-picked lossy subset."""
    artifacts = project / 'artifacts'
    support = package / 'supporting_analysis'
    support.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    if artifacts.exists():
        for src in sorted(artifacts.glob('*.json')):
            if not src.is_file():
                continue
            dst = support / src.name
            shutil.copy2(src, dst)
            copied.append(str(dst.relative_to(package)).replace('\\', '/'))
    # Stable strategy authority aliases used by human delivery and downstream consumers.
    strategy = package / 'strategy'
    strategy.mkdir(parents=True, exist_ok=True)
    aliases = {
        artifacts / 'strategy_authority.json': strategy / 'strategy_authority.json',
        artifacts / 'strategy_decision_index.json': strategy / 'STRATEGY_DECISION_INDEX.json',
        artifacts / 'commerce_decision_context.json': strategy / 'COMMERCE_DECISION_CONTEXT.json',
        artifacts / 'commercial_continuity_audit.json': strategy / 'COMMERCIAL_CONTINUITY_AUDIT.json',
    }
    for src, dst in aliases.items():
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            copied.append(str(dst.relative_to(package)).replace('\\', '/'))
    return copied


def materialize_video_objects(project: Path, package: Path) -> dict[str, Any]:
    plan = _read_json(project / 'artifacts/video_creator_plan.json')
    rows = [x for x in (plan.get('assets') or []) if isinstance(x, dict)]
    if not rows:
        return {'status': 'NOT_ACTIVE', 'count': 0, 'paths': []}
    root = package / 'video'
    root.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    universe = {
        'status': plan.get('status') or 'COMPILED',
        'dynamic_count': len(rows),
        'fixed_five_beat_template': False,
        'assets': rows,
        'principle': plan.get('principle') or 'Video/Creator/Live objects are decision-led and remain separate from gallery image capacity.',
    }
    _write_json(root / 'VIDEO_UNIVERSE.json', universe)
    paths.append('video/VIDEO_UNIVERSE.json')
    for i, row in enumerate(rows, start=1):
        video_id = str(row.get('video_id') or row.get('id') or f'VID-{i:02d}')
        folder = root / video_id
        folder.mkdir(parents=True, exist_ok=True)
        _write_json(folder / 'video_design_card.json', row)
        paths.append(str((folder / 'video_design_card.json').relative_to(package)).replace('\\', '/'))
        # Human-readable shot object without inventing a translation. Values remain exactly authored upstream.
        lines = [
            f'# {video_id}｜视频生产对象', '',
            f'- Family：{row.get("family") or "—"}',
            f'- Surface：{row.get("surface") or "—"}',
            f'- Narrative Carrier：{row.get("narrative_carrier") or "—"}',
            f'- Duration：{row.get("duration_seconds") or "—"}',
            f'- Hook / Shopper Question：{row.get("hook") or row.get("shopper_question") or "—"}', '',
            '## Shot Program / 镜头程序',
        ]
        for shot in row.get('shots') or []:
            if not isinstance(shot, dict):
                continue
            lines += [
                f'### {shot.get("shot") or "SHOT"}',
                f'- seconds：{shot.get("seconds") or "—"}',
                f'- job：{shot.get("job") or "—"}',
                f'- visual：{shot.get("visual") or "—"}',
            ]
        lines += ['', '## Language / Rights / Handoff', f'- Voice locale：{row.get("voice_locale") or "—"}', f'- Subtitle locales：{row.get("subtitle_locales") or "—"}', f'- CTA：{row.get("cta") or "—"}', f'- Creator contract：{json.dumps(row.get("creator_contract"), ensure_ascii=False) if row.get("creator_contract") else "N/A"}']
        (folder / 'video_production_object.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        paths.append(str((folder / 'video_production_object.md').relative_to(package)).replace('\\', '/'))
    return {'status': 'MATERIALIZED', 'count': len(rows), 'paths': paths}


def _object_manifest(project: Path, package: Path, universe: dict[str, Any], video: dict[str, Any]) -> dict[str, Any]:
    support = package / 'supporting_analysis'
    objects = [
        ('PRODUCT_TRUTH', support / 'product_truth.json'),
        ('TARGET_SCOPE', support / 'target_context.json'),
        ('MARKET', support / 'market_analysis.json'),
        ('AUDIENCE_CULTURE', support / 'culture_context.json'),
        ('PRICING_ECONOMICS', support / 'pricing_economics_authority.json'),
        ('LISTING', support / 'listing_analysis.json'),
        ('ADS', support / 'ad_analysis.json'),
        ('REVIEWS', support / 'feedback_analysis.json'),
        ('EXPERIMENT', support / 'experiment_analysis.json'),
        ('ASSET_ARCHITECTURE', support / 'asset_architecture.json'),
        ('SEVEN_TOOL_SYNTHESIS', support / 'seven_agent_synthesis.json'),
        ('COMMERCE_DECISION_CONTEXT', package / 'strategy/COMMERCE_DECISION_CONTEXT.json'),
        ('COMMERCIAL_CONTINUITY_AUDIT', package / 'strategy/COMMERCIAL_CONTINUITY_AUDIT.json'),
        ('ASSET_UNIVERSE', package / 'ASSET_UNIVERSE.json'),
        ('VIDEO_CREATOR', package / 'video/VIDEO_UNIVERSE.json'),
    ]
    rows = []
    for name, path in objects:
        exists = path.exists()
        rows.append({
            'object': name,
            'status': 'ACTIVE' if exists else ('NOT_ACTIVE_OR_MISSING_INPUT' if name not in {'PRODUCT_TRUTH', 'TARGET_SCOPE', 'ASSET_ARCHITECTURE', 'SEVEN_TOOL_SYNTHESIS', 'ASSET_UNIVERSE'} else 'MISSING_REQUIRED_OBJECT'),
            'path': str(path.relative_to(package)).replace('\\', '/') if exists else None,
        })
    return {
        'status': 'FULL_DELIVERY_OBJECT_MANIFEST',
        'host_runtime_parity_required': True,
        'machine_truth_preserved': True,
        'asset_universe': {
            'total_asset_candidates': universe.get('total_asset_candidates'),
            'activation_capacity': universe.get('activation_capacity'),
            'fixed_total_asset_limit': False,
        },
        'video_materialization': video,
        'objects': rows,
        'principle': 'An inactive or missing-input domain is named explicitly; it is never hidden by omitting the object from the delivery contract.',
    }


def _rewrite_delivery_manifest(package: Path, zip_path: Path, materialization: dict[str, Any]) -> dict[str, Any]:
    path = package / 'DELIVERY_MANIFEST.json'
    manifest = _read_json(path)
    manifest['status'] = 'DELIVERY_READY' if materialization.get('status') == 'PASS' else 'DELIVERY_INCOMPLETE'
    manifest['full_materialization_audit'] = 'FULL_MATERIALIZATION_AUDIT.json'
    manifest['full_delivery_object_manifest'] = 'FULL_DELIVERY_OBJECT_MANIFEST.json'
    manifest['asset_universe'] = 'ASSET_UNIVERSE.json'
    manifest['host_native_runtime_export_parity'] = materialization.get('status')
    files = []
    for f in sorted(package.rglob('*')):
        if f.is_file() and f.name != 'DELIVERY_MANIFEST.json':
            files.append({'path': str(f.relative_to(package)).replace('\\', '/'), 'sha256': _sha256(f), 'bytes': f.stat().st_size})
    manifest['files'] = files
    _write_json(path, manifest)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(package.rglob('*')):
            if f.is_file():
                zf.write(f, Path(package.name) / f.relative_to(package))
    manifest['zip_sha256'] = _sha256(zip_path)
    manifest['zip_bytes'] = zip_path.stat().st_size
    _write_json(path, manifest)
    # Rewrite one final time so the ZIP contains the same manifest fields as the folder.
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(package.rglob('*')):
            if f.is_file():
                zf.write(f, Path(package.name) / f.relative_to(package))
    manifest['zip_sha256'] = _sha256(zip_path)
    manifest['zip_bytes'] = zip_path.stat().st_size
    _write_json(path, manifest)
    return manifest


def finalize_full_delivery_materialization(project_dir: Path | str, export_manifest: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_dir)
    package = Path(export_manifest.get('package_dir') or '')
    zip_path = Path(export_manifest.get('zip_path') or '')
    if not package.exists():
        raise FileNotFoundError(f'FULL delivery package directory missing after export: {package}')

    _copy_machine_authorities(project, package)
    universe = compile_export_asset_universe(project)
    _write_json(package / 'ASSET_UNIVERSE.json', universe)
    video = materialize_video_objects(project, package)
    obj_manifest = _object_manifest(project, package, universe, video)
    _write_json(package / 'FULL_DELIVERY_OBJECT_MANIFEST.json', obj_manifest)
    # Create the audit artifact before auditing because the FULL contract requires its own visible file.
    _write_json(package / 'FULL_MATERIALIZATION_AUDIT.json', {'status': 'AUDIT_IN_PROGRESS', 'contract': 'HOST_NATIVE_FULL_MATERIALIZATION_EQUALS_RUNTIME_EXPORT_V3'})

    audit = audit_host_full_package(package)
    audit['object_manifest'] = 'FULL_DELIVERY_OBJECT_MANIFEST.json'
    audit['asset_universe'] = {
        'total_asset_candidates': universe.get('total_asset_candidates'),
        'activation_capacity': universe.get('activation_capacity'),
        'fixed_total_asset_limit': False,
    }
    _write_json(package / 'FULL_MATERIALIZATION_AUDIT.json', audit)
    manifest = _rewrite_delivery_manifest(package, zip_path, audit)

    if audit.get('status') != 'PASS':
        raise RuntimeError('BLOCKED FULL materialization contract failed: ' + json.dumps(audit.get('issues') or [], ensure_ascii=False))
    return manifest
