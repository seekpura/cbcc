#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / 'VERSION'
CURRENT_OVERRIDE_FILE = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json'
CURRENT_BUILD_AUTHORITY = 'references/CURRENT_CANONICAL_SKILL_BUILD.md'
CURRENT_LOADING_MAP = 'prompts/canonical_authority_loading_map_CURRENT.md'
CURRENT_BUILDER = 'scripts/build_plugin_dist_current.py'
STRICT_REQUIREMENT_CHECKER = 'scripts/check_v0664_requirement_consumer_map.py'
CURRENT_RELEASE_REQS = ('REQ-046', 'REQ-047', 'REQ-048')
CURRENT_RELEASE_STATUSES = {
    'REQ-046': 'RELEASE_PROCESS_ENFORCED_CURRENT',
    'REQ-047': 'RELEASE_PROCESS_ENFORCED_CURRENT',
    'REQ-048': 'RELEASE_EVIDENCE_REQUIRED_CURRENT',
}


def current_authority_version() -> str:
    return VERSION_FILE.read_text(encoding='utf-8').strip()


def current_version_family() -> str:
    match = re.match(r'^(\d+\.\d+\.\d+)', current_authority_version())
    return match.group(1) if match else ''


def required_release_paths() -> list[str]:
    """Paths required under packaged resources/ for every CURRENT release."""
    return [
        'references/CONVERSATION_REQUIREMENT_AUDIT.md',
        'references/CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md',
        'references/USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md',
        'references/REQUIREMENT_CONSUMER_MAP_V0664.json',
        CURRENT_OVERRIDE_FILE,
        'references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md',
        'references/SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md',
        'references/HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md',
        CURRENT_BUILD_AUTHORITY,
        'references/MASTER_CONSTRUCTION_CONTRACT.md',
        'references/PROMPT_ART_DIRECTION_MASTER_CONTRACT.md',
        'references/BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md',
        'references/HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md',
        'references/ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md',
        'references/MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md',
        CURRENT_LOADING_MAP,
        CURRENT_BUILDER,
        STRICT_REQUIREMENT_CHECKER,
        'scripts/check_current_release_package.py',
        'runtime/cbcc/long_requirement_runtime.py',
        'runtime/cbcc/long_requirement_human_projection.py',
        'runtime/cbcc/strategy_culture_materialization.py',
        'runtime/cbcc/asset_universe_family_audit.py',
        'runtime/cbcc/integrated_render_route_authority.py',
        'runtime/cbcc/long_requirement_full_audit.py',
        'runtime/cbcc/full_art_direction_preservation.py',
        'runtime/cbcc/model_prompt_semantic_membrane.py',
        'runtime/cbcc/commercial_continuity_bootstrap.py',
    ]


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain a JSON object')
    return value


def _builder_target(text: str) -> str:
    match = re.search(r"(?m)^CURRENT_BUILDER_TARGET\s*=\s*['\"](\d+\.\d+\.\d+)['\"]", text)
    return match.group(1) if match else ''


def validate_override_release_version(document: dict[str, Any], expected: str) -> list[dict[str, Any]]:
    """Validate the release family declared inside the packaged CURRENT override document itself."""
    actual = str(document.get('current_release_version') or '')
    if actual == expected:
        return []
    return [{
        'code': 'PACKAGED_CURRENT_OVERRIDE_RELEASE_VERSION_MISMATCH',
        'actual': actual or 'MISSING',
        'expected': expected,
    }]


def _effective_requirement_rows(resources: Path) -> list[dict[str, Any]]:
    base = _load_json(resources / 'references' / 'REQUIREMENT_CONSUMER_MAP_V0664.json')
    current = _load_json(resources / CURRENT_OVERRIDE_FILE)
    by_req = {
        str(row.get('req') or ''): dict(row)
        for row in (base.get('requirements') or [])
        if isinstance(row, dict) and row.get('req')
    }
    for row in current.get('overrides') or []:
        if isinstance(row, dict) and row.get('req'):
            by_req[str(row['req'])] = dict(row)
    return [by_req[f'REQ-{i:03d}'] for i in range(1, 61) if f'REQ-{i:03d}' in by_req]


def _resolve_plugin_root(extracted: Path) -> Path:
    direct = extracted / 'cross-border-commerce-creative'
    if direct.exists():
        return direct
    candidates = [p for p in extracted.iterdir() if p.is_dir() and (p / 'plugin.json').exists()]
    if len(candidates) == 1:
        return candidates[0]
    if (extracted / 'plugin.json').exists():
        return extracted
    return direct


def audit(plugin_zip: Path) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []

    def add(code: str, **data: Any) -> None:
        issues.append({'code': code, **data})

    version = current_version_family()
    authority = current_authority_version()
    if not version:
        add('CURRENT_VERSION_FAMILY_UNRESOLVED', authority_version=authority)

    if not plugin_zip.exists():
        return {
            'status': 'FAIL',
            'issue_count': 1,
            'issues': [{'code': 'PLUGIN_ZIP_MISSING', 'path': str(plugin_zip)}],
            'plugin_version': None,
            'authority_version': authority,
        }

    try:
        with tempfile.TemporaryDirectory(prefix='cbcc-current-release-check-') as td:
            extracted = Path(td)
            with zipfile.ZipFile(plugin_zip) as zf:
                bad = zf.testzip()
                if bad:
                    add('PLUGIN_ZIP_CORRUPT_MEMBER', member=bad)
                zf.extractall(extracted)

            plugin = _resolve_plugin_root(extracted)
            skill_root = plugin / 'skills' / 'cross-border-commerce-creative'
            resources = skill_root / 'resources'
            top = skill_root / 'SKILL.md'
            deep = resources / 'SKILL.md'

            try:
                manifest = _load_json(plugin / 'plugin.json')
            except Exception as exc:
                manifest = {}
                add('PLUGIN_MANIFEST_READ_FAILED', error=str(exc))

            if manifest.get('version') != version:
                add('PLUGIN_VERSION_MISMATCH', actual=manifest.get('version'), expected=version)

            if not top.exists() or not deep.exists():
                add('SKILL_FILE_MISSING', top=top.exists(), deep=deep.exists())
            elif top.read_bytes() != deep.read_bytes():
                add('TOP_DEEP_SKILL_DRIFT')

            if top.exists():
                skill_text = top.read_text(encoding='utf-8-sig')
                if f'version: {authority}' not in skill_text:
                    add('SKILL_AUTHORITY_VERSION_MISMATCH', expected=authority)
                if f'# Cross-Border Commerce Creative v{version}' not in skill_text:
                    add('SKILL_TITLE_VERSION_MISMATCH', expected=version)
                for token in (
                    'Strict Requirement Consumer Accounting',
                    'HOST_SKILL_SNAPSHOT_STALE',
                    'One-to-One Long-Requirement Runtime Enforcement',
                    'Real K01 Host-Shortcut Audit Closure',
                    'FULL depth remains mandatory',
                ):
                    if token not in skill_text:
                        add('SKILL_AUTHORITY_TOKEN_MISSING', token=token)

            version_path = resources / 'VERSION'
            packaged_authority = version_path.read_text(encoding='utf-8-sig').strip() if version_path.exists() else None
            if packaged_authority != authority:
                add('RESOURCE_VERSION_MISMATCH', actual=packaged_authority, expected=authority)

            required = required_release_paths()
            missing = [rel for rel in required if not (resources / rel).exists()]
            if missing:
                add('REQUIRED_CURRENT_RELEASE_FILE_MISSING', files=missing)

            current_builder_path = resources / CURRENT_BUILDER
            if current_builder_path.exists():
                target = _builder_target(current_builder_path.read_text(encoding='utf-8'))
                if target != version:
                    add('PACKAGED_CURRENT_BUILDER_VERSION_MISMATCH', actual=target, expected=version)
            else:
                target = ''

            base_map_path = resources / 'references' / 'REQUIREMENT_CONSUMER_MAP_V0664.json'
            override_path = resources / CURRENT_OVERRIDE_FILE
            if base_map_path.exists() and override_path.exists():
                override_doc = _load_json(override_path)
                issues.extend(validate_override_release_version(override_doc, version))
                rows = _effective_requirement_rows(resources)
                ids = [str(row.get('req') or '') for row in rows]
                expected_ids = [f'REQ-{i:03d}' for i in range(1, 61)]
                if ids != expected_ids:
                    add('EFFECTIVE_REQUIREMENT_ID_SET_MISMATCH', actual=ids)
                by_req = {str(row.get('req') or ''): row for row in rows}
                for req, expected_status in CURRENT_RELEASE_STATUSES.items():
                    row = by_req.get(req) or {}
                    status = str(row.get('status') or '')
                    if status != expected_status:
                        add('CURRENT_RELEASE_STATUS_STALE', req=req, actual=status, expected=expected_status)
                    consumers = [str(x) for x in (row.get('consumers') or [])]
                    if any(re.search(r'build_plugin_dist_v\d+', item) for item in consumers):
                        add('HISTORICAL_BUILDER_CONSUMER_FORBIDDEN', req=req, consumers=consumers)
            else:
                rows = []

            full_audit = resources / 'runtime' / 'cbcc' / 'long_requirement_full_audit.py'
            if full_audit.exists():
                text = full_audit.read_text(encoding='utf-8')
                for token in (
                    '_project_shortcut_audit',
                    'PRODUCTION_OBJECTS_INCOMPLETE',
                    'GLOBAL_POST_COMPOSITE_POLICY',
                    'FIXED_CAPABILITY_ROUTE_TAXONOMY',
                ):
                    if token not in text:
                        add('REAL_K01_AUDIT_TOKEN_MISSING', token=token)

            strategy_materialization = resources / 'runtime' / 'cbcc' / 'strategy_culture_materialization.py'
            if strategy_materialization.exists():
                text = strategy_materialization.read_text(encoding='utf-8')
                for token in (
                    'product_truth_audit_table',
                    'assumption_decision_log',
                    'intersectionality_table',
                    'framework_relationships',
                    'visual_execution_checklist',
                    'output_self_check_rows',
                    'FULL_PRODUCT_TRUTH_AUDIT_TABLE_MISSING',
                    'FULL_RESOURCE_TRADEOFF_PRIORITY_ROWS_MISSING',
                ):
                    if token not in text:
                        add('STRATEGY_CULTURE_MATERIALIZATION_TOKEN_MISSING', token=token)

            integrated = resources / 'runtime' / 'cbcc' / 'integrated_render_route_authority.py'
            if integrated.exists():
                text = integrated.read_text(encoding='utf-8')
                for token in ('MODEL_RENDER_INTEGRATED', 'REFERENCE_GUIDED_NATIVE_LOCK'):
                    if token not in text:
                        add('INTEGRATED_RENDER_TOKEN_MISSING', token=token)

            bootstrap = resources / 'runtime' / 'cbcc' / 'commercial_continuity_bootstrap.py'
            if bootstrap.exists():
                text = bootstrap.read_text(encoding='utf-8')
                offsets = [
                    text.find('normalize_full_art_direction'),
                    text.find('finalize_integrated_render_route'),
                    text.find('finalize_model_prompt_bundle'),
                ]
                if any(i < 0 for i in offsets) or not (offsets[0] < offsets[1] < offsets[2]):
                    add('PROMPT_BOUNDARY_ORDER_INVALID', offsets=offsets)
                for token in (
                    'wrap_strategy_culture_materialization',
                    'wrap_strategy_culture_human',
                    'wrap_strategy_culture_audit',
                ):
                    if token not in text:
                        add('STRATEGY_CULTURE_BOOTSTRAP_BINDING_MISSING', token=token)

            return {
                'status': 'PASS' if not issues else 'FAIL',
                'issue_count': len(issues),
                'issues': issues,
                'plugin_version': manifest.get('version'),
                'authority_version': authority,
                'current_builder_target': target,
                'top_skill_bytes': top.stat().st_size if top.exists() else None,
                'required_file_count': len(required),
                'requirement_count': len(rows),
                'current_release_rows': list(CURRENT_RELEASE_REQS),
            }
    except zipfile.BadZipFile as exc:
        add('PLUGIN_ZIP_INVALID', error=str(exc))
    except Exception as exc:
        add('CURRENT_RELEASE_CHECK_EXCEPTION', error=str(exc))

    return {
        'status': 'FAIL',
        'issue_count': len(issues),
        'issues': issues,
        'plugin_version': None,
        'authority_version': authority,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate a CBCC plugin ZIP against the current VERSION and CURRENT release authorities.')
    parser.add_argument('plugin_zip')
    args = parser.parse_args()
    result = audit(Path(args.plugin_zip))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
