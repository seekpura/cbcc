from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import zipfile

from . import delivery_export as legacy


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _semantic_full_html_depth_check(html_text: str, full: bool) -> dict[str, Any]:
    """Validate semantic human coverage without dictating headings, pages or IA."""
    if not full:
        return {'status': 'NOT_REQUIRED_FOR_TASK_SCOPED', 'missing': []}
    groups = {
        'information_assumptions_decisions': ('信息完整度', '待确认', '假设', '决策日志'),
        'product_truth': ('产品事实', 'Product Truth', '宣称', '证据'),
        'market_audience_culture': ('市场与人群', '市场', '人群', '族裔', '文化'),
        'strategy_frameworks': ('营销策略', '策略', '定位', '价值主张', 'STP', 'JTBD'),
        'visual_execution': ('视觉与摄影', '视觉', '摄影', 'CMF', 'Shot List'),
        'content_matrix': ('内容矩阵', 'Content Matrix', 'Hook', '脚本'),
        'race': ('RACE',),
        'culture_adaptation': ('文化适配', '文化校验', '禁忌', '包容性'),
        'risk_measurement_priority': ('风险与合规', '合规', '风险', 'P0', 'A/B'),
    }
    missing = []
    for name, alternatives in groups.items():
        if not any(token in html_text for token in alternatives):
            missing.append(name)
    return {
        'status': 'PASS' if not missing else 'INCOMPLETE',
        'semantic_groups': list(groups),
        'missing': missing,
        'layout_contract': 'semantic coverage only; no fixed headings/pages/sections',
    }


def audit_workspace_prompt_continuity(package_dir: Path) -> dict[str, Any]:
    package_dir = Path(package_dir)
    hp = package_dir / 'index.html'
    issues: list[dict[str, Any]] = []
    if not hp.exists():
        return {'status': 'FAIL', 'issue_count': 1, 'issues': [{'code': 'INDEX_MISSING'}]}
    text = hp.read_text(encoding='utf-8', errors='replace')
    assets_root = package_dir / 'asset_packages'
    all_assets: list[str] = []
    prompt_assets: list[str] = []
    if assets_root.exists():
        for d in sorted(assets_root.iterdir()):
            if not d.is_dir():
                continue
            all_assets.append(d.name)
            if (d / '05_prompt_CN.txt').exists() or (d / '06_prompt_EN.txt').exists():
                prompt_assets.append(d.name)

    current_shell = 'data-workspace-shell="cbcc-commercial-v1"' in text
    legacy_routed = (
        'hashchange' in text and 'location.hash' in text and
        ('asset/' in text or 'data-route="asset/' in text) and
        ('id="main"' in text or 'class="workspace"' in text)
    )
    if not (current_shell or legacy_routed):
        issues.append({'code': 'MATURE_ROUTED_WORKSPACE_LOST'})

    if all_assets:
        missing_routes = [aid for aid in all_assets if f'asset/{aid}' not in text]
        if missing_routes:
            issues.append({'code': 'ASSET_DETAIL_ROUTES_MISSING', 'assets': missing_routes})

    if prompt_assets:
        cn = any(x in text for x in ('Model Prompt CN', 'prompt_cn', '中文模型提示词', '中文规范生产提示词'))
        en = any(x in text for x in ('Model Prompt EN', 'prompt_en', '英文模型提示词', '英文 / 生成模型执行提示词'))
        if not cn:
            issues.append({'code': 'PROMPT_CN_NOT_PROJECTED_TO_HUMAN_HTML'})
        if not en:
            issues.append({'code': 'PROMPT_EN_NOT_PROJECTED_TO_HUMAN_HTML'})
        prompt_surface = any(x in text for x in ('data-route="prompts"', '提示词工作台', 'Prompt Lab', 'prompt-lab'))
        per_asset_prompt = ('asset/' in text) and cn and en
        if not (prompt_surface or per_asset_prompt):
            issues.append({'code': 'PROMPT_INTERACTIVE_SURFACE_MISSING'})

    numbered_hits = sum(1 for s in (
        '01 信息完整度', '02 产品事实审计', '03 平台 × 区域 × 人群 × 族裔文化',
        '04 营销框架与核心策略', '05 视觉总策略', '06 分平台内容矩阵',
        '07 RACE', '08 族裔文化', '09 合规'
    ) if s in text)
    if numbered_hits >= 6 and not current_shell and not ('asset/' in text):
        issues.append({'code': 'FIXED_NINE_SECTION_REPLACEMENT_SHELL'})

    return {
        'status': 'PASS' if not issues else 'FAIL',
        'issue_count': len(issues),
        'asset_count': len(all_assets),
        'prompt_asset_count': len(prompt_assets),
        'workspace_signature': 'cbcc-commercial-v1' if current_shell else ('legacy-mature-routed' if legacy_routed else 'unknown/replaced'),
        'issues': issues,
    }


def _rezip(package_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(package_dir.rglob('*')):
            if f.is_file():
                zf.write(f, Path(package_dir.name) / f.relative_to(package_dir))


def _canonical_materialization_export_audit(package_dir: Path) -> dict[str, Any]:
    """Run the same semantic boundary before the final ZIP is re-created.

    Validation never rewrites the workspace or guesses shifted fields. A failed package returns to the
    Agent/runtime authoring layer so the canonical business objects are corrected and re-rendered.
    """
    from .canonical_materialization_package_audit import wrap_audit_host_full_package
    empty = lambda _p: {'status': 'PASS', 'issues': []}
    return wrap_audit_host_full_package(empty)(Path(package_dir))


def export_delivery_package(project_dir: Path, output: Path) -> dict[str, Any]:
    """Run mature export, then block final ZIP on workspace + canonical materialization parity."""
    original = legacy._full_html_depth_check
    legacy._full_html_depth_check = _semantic_full_html_depth_check
    try:
        manifest = legacy.export_delivery_package(project_dir, output)
    finally:
        legacy._full_html_depth_check = original

    package_dir = Path(manifest['package_dir'])
    zip_path = Path(manifest['zip_path'])

    workspace_audit = audit_workspace_prompt_continuity(package_dir)
    workspace_audit_path = package_dir / 'WORKSPACE_PROMPT_CONTINUITY_AUDIT.json'
    workspace_audit_path.write_text(json.dumps(workspace_audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if workspace_audit.get('status') != 'PASS':
        raise RuntimeError('BLOCKED workspace/prompt continuity failed: ' + json.dumps(workspace_audit.get('issues') or [], ensure_ascii=False))

    canonical_audit = _canonical_materialization_export_audit(package_dir)
    canonical_audit_path = package_dir / 'CANONICAL_MATERIALIZATION_PARITY_AUDIT.json'
    canonical_audit_path.write_text(json.dumps(canonical_audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if canonical_audit.get('status') != 'PASS':
        raise RuntimeError('BLOCKED canonical materialization / Human projection parity failed: ' + json.dumps(canonical_audit.get('issues') or [], ensure_ascii=False))

    manifest_path = package_dir / 'DELIVERY_MANIFEST.json'
    latest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else dict(manifest)
    latest['workspace_prompt_continuity_audit'] = 'WORKSPACE_PROMPT_CONTINUITY_AUDIT.json'
    latest['canonical_materialization_parity_audit'] = 'CANONICAL_MATERIALIZATION_PARITY_AUDIT.json'
    latest.setdefault('workspace_contract', {}).update({
        'workspace_prompt_continuity': 'PASS',
        'canonical_human_projection_parity': 'PASS',
        'asset_semantic_domain_integrity': 'PASS',
        'prompt_canonical_lineage': 'PASS',
        'prompt_files_human_projected': True,
        'asset_detail_routes_preserved': True,
        'exact_heading_layout_lock_removed': True,
    })
    manifest_path.write_text(json.dumps(latest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    _rezip(package_dir, zip_path)
    latest['zip_sha256'] = _sha256(zip_path)
    latest['zip_bytes'] = zip_path.stat().st_size
    manifest_path.write_text(json.dumps(latest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return latest
