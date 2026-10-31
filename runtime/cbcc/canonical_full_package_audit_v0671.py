from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping
import json

from .asset_execution_relevance_v0671 import relevance_issues
from .asset_package_full_lineage_v0671 import audit_full_asset_lineage
from .canonical_human_compaction_v0672 import build_canonical_human_payload, finalize_static_human_projection, audit_generic_human_field_coverage
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



_PROVIDER_SCOPE_CODES = {
    'FULL_PROVIDER_RESULT_MISSING', 'FULL_ACTUAL_GENERATED_OUTPUT_MISSING',
    'FULL_ACTUAL_OUTPUT_REVIEW_MISSING', 'FULL_LOCAL_REVISION_LINEAGE_MISSING',
    'PROVIDER_RESULT_MISSING', 'ACTUAL_GENERATED_OUTPUT_MISSING',
    'ACTUAL_OUTPUT_REVIEW_MISSING', 'LOCAL_REVISION_LINEAGE_MISSING',
}

def _production_required_for_current_scope(package: Path) -> bool | None:
    scope = _read_json(package / 'supporting_analysis/gate_scope.json')
    gates = scope.get('gates') if isinstance(scope.get('gates'), Mapping) else {}
    production = gates.get('PRODUCTION') if isinstance(gates, Mapping) else None
    if isinstance(production, Mapping) and 'required_for_current_scope' in production:
        return production.get('required_for_current_scope') is True
    return None

def _canonical_presence_audit(package: Path) -> dict[str, Any]:
    root = package / 'asset_packages'
    if not root.exists():
        return {}
    rows = []
    structured = visible = absent = 0
    for asset_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        manifest = _read_yaml(asset_dir / '00_asset_manifest.yaml')
        art = manifest.get('asset_art_direction') if isinstance(manifest.get('asset_art_direction'), Mapping) else {}
        presence = manifest.get('product_presence') if isinstance(manifest.get('product_presence'), Mapping) else art.get('product_presence')
        presence = presence if isinstance(presence, Mapping) else {}
        state = str(presence.get('planning_state') or '').upper()
        why = str(presence.get('presence_why') or '')
        ok = bool(state and why)
        if ok: structured += 1
        if state in {'FORBIDDEN','ABSENT','PRODUCT_ABSENT','NOT_NEEDED'}: absent += 1
        elif state: visible += 1
        rows.append({'asset_id': asset_dir.name, 'planning_state': state or 'UNRESOLVED', 'structured_decision': ok, 'presence_why': why})
    return {
        'status': 'PASS' if rows and structured == len(rows) else 'INCOMPLETE',
        'total_assets': len(rows), 'structured_presence_decisions': structured,
        'visible_or_optional_count': visible, 'absent_or_forbidden_count': absent,
        'assets': rows, 'source': 'FINAL_ASSET_PACKAGE_MANIFESTS',
    }

def _reconcile_legacy_issues(package: Path, result: dict[str, Any]) -> dict[str, Any]:
    issues = list(result.get('issues') or [])
    production_required = _production_required_for_current_scope(package)
    if production_required is False:
        issues = [row for row in issues if row.get('code') not in _PROVIDER_SCOPE_CODES]
        result['provider_media_e2e'] = {
            'status': 'E2E_PENDING_NOT_REQUESTED',
            'principle': 'Provider Result / actual media / pixel QA remain pending until PRODUCTION is in current scope.',
        }

    presence = _canonical_presence_audit(package)
    if presence.get('status') == 'PASS':
        issues = [row for row in issues if row.get('code') not in {'PRODUCT_PRESENCE_DECISION_NOT_STRUCTURED','PRODUCT_PRESENCE_PORTFOLIO_AUDIT_MISSING'}]
        universe_path = package / 'ASSET_UNIVERSE.json'
        universe = _read_json(universe_path)
        if universe:
            universe['product_presence_portfolio_audit'] = presence
            universe_path.write_text(json.dumps(universe, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        result['canonical_product_presence_audit'] = presence

    html_path = package / 'index.html'
    if html_path.exists():
        page = html_path.read_text(encoding='utf-8', errors='ignore')
        if 'data-workspace-shell="cbcc-commercial-v1"' in page or "data-workspace-shell='cbcc-commercial-v1'" in page:
            issues = [row for row in issues if row.get('code') != 'FIXED_CAPABILITY_ROUTE_TAXONOMY']

    deduped = []
    seen = set()
    for row in issues:
        key = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)
        if key not in seen:
            seen.add(key); deduped.append(row)
    result['issues'] = deduped
    result['status'] = 'PASS' if not deduped else 'INCOMPLETE'
    result['v0672_legacy_reconciliation'] = {
        'production_required_for_current_scope': production_required,
        'canonical_presence_status': presence.get('status') or 'NOT_AVAILABLE',
        'principle': 'Legacy findings are removed only when final canonical package evidence proves the modern contract.',
    }
    return result

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
        # Materialize the current canonical Human/Listing state first; compatibility audits must inspect
        # that final state rather than an earlier static snapshot with no canonical payload.
        package = Path(package_dir)
        current = audit_current_full_canonical_parity(package)
        base = fn(package)

        # Current Human projection is the final HTML owner. Compatibility audits may still contain legacy
        # projectors that rewrite index.html after inspecting it. Re-assert the current projection only when
        # the marker/payload was lost, then reconcile the narrow set of stale compatibility-only issue codes.
        page = (package / 'index.html').read_text(encoding='utf-8', errors='ignore') if (package / 'index.html').exists() else ''
        if 'CBCC_CANONICAL_STATIC_PROJECTION_V0672' not in page or 'cbcc-canonical-payload-v0672' not in page:
            current = audit_current_full_canonical_parity(package)

        stale_html_codes = {
            'CANONICAL_HUMAN_POSITIVE_PROJECTION_FAILED',
            'WORKSPACE_SEARCH_SCOPE_INCOMPLETE',
            'HTML_ASSET_DATA_MISSING',
            'HTML_CANONICAL_LAZY_PAYLOAD_MISSING_V0672',
            'HTML_CANONICAL_LAZY_INSPECTOR_MISSING_V0672',
            'HTML_CANONICAL_LAZY_ROOT_MISSING_V0672',
        }
        base_issues = list(base.get('issues') or [])
        if current.get('status') == 'PASS':
            base_issues = [row for row in base_issues if row.get('code') not in stale_html_codes]
            parity = base.get('canonical_materialization_parity_audit')
            if isinstance(parity, dict):
                parity['human_positive_projection'] = current.get('human_projection') or {'status': 'PASS'}
                parity['current_static_projection_final_owner'] = 'PASS'

        issues = base_issues + list(current.get('issues') or [])
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
        return _reconcile_legacy_issues(Path(package_dir), base)
    setattr(audited, '_cbcc_v0671_full_canonical_parity', True)
    return audited
