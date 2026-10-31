from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping
import json

from .asset_execution_relevance_v0671 import relevance_issues
from .asset_package_full_lineage_v0671 import audit_full_asset_lineage
from .canonical_full_parity_v0671 import build_canonical_human_payload, finalize_static_human_projection, audit_generic_human_field_coverage
from .listing_markdown_parity_v0671 import ensure_listing_markdown_canonical_parity, audit_listing_markdown_canonical_parity
from .strategy_execution_completion_v0671 import completion_issues_v0671

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    try:
        value = yaml.safe_load(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def audit_current_full_canonical_parity(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    issues: list[dict[str, Any]] = []

    listing_materialization = ensure_listing_markdown_canonical_parity(package)
    human_projection = finalize_static_human_projection(package)
    if human_projection.get('status') not in {'PASS', 'NOT_REQUIRED'}:
        issues.append({'code': 'CANONICAL_STATIC_HUMAN_PROJECTION_FAILED_V0671', 'detail': human_projection})

    issues.extend(audit_listing_markdown_canonical_parity(package))
    root = package / 'asset_packages'
    if root.exists():
        issues.extend(audit_full_asset_lineage(root))
        for asset_dir in sorted(p for p in root.iterdir() if p.is_dir()):
            manifest = _read_yaml(asset_dir / '00_asset_manifest.yaml')
            if manifest and isinstance(manifest.get('asset_art_direction'), Mapping):
                issues.extend(relevance_issues(manifest))

    strategy = _read_json(package / 'strategy/strategy_authority.json')
    if strategy:
        issues.extend(completion_issues_v0671(strategy))

    html_path = package / 'index.html'
    payload = build_canonical_human_payload(package)
    if html_path.exists():
        issues.extend(audit_generic_human_field_coverage(payload, html_path.read_text(encoding='utf-8', errors='ignore')))

    deduped = []
    seen = set()
    for row in issues:
        key = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    return {
        'status': 'PASS' if not deduped else 'INCOMPLETE',
        'issues': deduped,
        'listing_materialization': listing_materialization,
        'human_projection': human_projection,
        'contract': 'V0671_FULL_CANONICAL_BUSINESS_OBJECT_PARITY',
        'requirements': {
            'real_static_delivery_html_projection': True,
            'listing_md_multilingual_parity': True,
            'generic_business_field_coverage': True,
            'full_asset_package_lineage': True,
            'major_decision_four_axis_why': True,
            'intersectionality_interaction_analysis': True,
            'human_typography_relevance_decisions': True,
        },
    }


def wrap_audit_host_full_package(fn: Callable[[Path], dict[str, Any]]):
    def audited(package_dir: Path):
        base = fn(Path(package_dir))
        current = audit_current_full_canonical_parity(Path(package_dir))
        issues = list(base.get('issues') or []) + list(current.get('issues') or [])
        deduped = []
        seen = set()
        for row in issues:
            key = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)
            if key not in seen:
                seen.add(key)
                deduped.append(row)
        base['issues'] = deduped
        base['status'] = 'PASS' if not deduped else 'INCOMPLETE'
        base['v0671_full_canonical_parity'] = current
        return base
    setattr(audited, '_cbcc_v0671_full_canonical_parity', True)
    return audited
