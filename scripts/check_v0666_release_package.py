#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from pathlib import Path

EXPECTED_VERSION = '0.6.66'
EXPECTED_AUTHORITY = '0.6.66-strict-consumer-current-baseline-build'


def audit(plugin_zip: Path) -> dict:
    issues: list[dict] = []
    def add(code: str, **data) -> None:
        issues.append({'code': code, **data})

    if not plugin_zip.exists():
        return {'status': 'FAIL', 'issues': [{'code': 'PLUGIN_ZIP_MISSING', 'path': str(plugin_zip)}]}

    with tempfile.TemporaryDirectory(prefix='cbcc-v0666-check-') as td:
        with zipfile.ZipFile(plugin_zip) as zf:
            zf.extractall(td)
        plugin = Path(td) / 'cross-border-commerce-creative'
        skill_root = plugin / 'skills' / 'cross-border-commerce-creative'
        res = skill_root / 'resources'
        top = skill_root / 'SKILL.md'
        deep = res / 'SKILL.md'

        try:
            manifest = json.loads((plugin / 'plugin.json').read_text(encoding='utf-8'))
        except Exception as exc:
            manifest = {}
            add('PLUGIN_MANIFEST_READ_FAILED', error=str(exc))

        if manifest.get('version') != EXPECTED_VERSION:
            add('PLUGIN_VERSION_MISMATCH', actual=manifest.get('version'), expected=EXPECTED_VERSION)
        if not top.exists() or not deep.exists():
            add('SKILL_FILE_MISSING', top=top.exists(), deep=deep.exists())
        elif top.read_bytes() != deep.read_bytes():
            add('TOP_DEEP_SKILL_DRIFT')
        if top.exists():
            text = top.read_text(encoding='utf-8')
            for token in (
                f'version: {EXPECTED_AUTHORITY}',
                '# Cross-Border Commerce Creative v0.6.66',
                '## 0.15 Strict Requirement Consumer Accounting + Current Baseline Build',
                'HOST_SKILL_SNAPSHOT_STALE',
                '## 0.10 One-to-One Long-Requirement Runtime Enforcement',
                '## 0.12 Real K01 Host-Shortcut Audit Closure',
                '## 1. FULL depth remains mandatory',
            ):
                if token not in text:
                    add('SKILL_AUTHORITY_TOKEN_MISSING', token=token)
        version_path = res / 'VERSION'
        if not version_path.exists() or version_path.read_text(encoding='utf-8').strip() != EXPECTED_AUTHORITY:
            add('RESOURCE_VERSION_MISMATCH', actual=version_path.read_text(encoding='utf-8').strip() if version_path.exists() else None)

        required = [
            res / 'references' / 'CONVERSATION_REQUIREMENT_AUDIT.md',
            res / 'references' / 'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md',
            res / 'references' / 'USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md',
            res / 'references' / 'CURRENT_PACKAGED_SKILL_BASELINE_V0665.md',
            res / 'references' / 'CURRENT_CANONICAL_SKILL_BUILD_V0666.md',
            res / 'references' / 'REQUIREMENT_CONSUMER_MAP_V0664.json',
            res / 'references' / 'REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md',
            res / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md',
            res / 'references' / 'HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md',
            res / 'references' / 'REAL_K01_HOST_SHORTCUT_AUDIT_CLOSURE_V0663.md',
            res / 'prompts' / 'canonical_authority_loading_map_v0665_addendum.md',
            res / 'scripts' / 'check_v0664_requirement_consumer_map.py',
            res / 'runtime' / 'cbcc' / 'long_requirement_runtime.py',
            res / 'runtime' / 'cbcc' / 'long_requirement_human_projection.py',
            res / 'runtime' / 'cbcc' / 'asset_universe_family_audit.py',
            res / 'runtime' / 'cbcc' / 'integrated_render_route_authority.py',
            res / 'runtime' / 'cbcc' / 'long_requirement_full_audit.py',
            res / 'runtime' / 'cbcc' / 'full_art_direction_preservation.py',
            res / 'runtime' / 'cbcc' / 'commercial_continuity_bootstrap.py',
        ]
        missing = [str(p.relative_to(res)) for p in required if not p.exists()]
        if missing:
            add('REQUIRED_RELEASE_FILE_MISSING', files=missing)

        consumer_path = res / 'references' / 'REQUIREMENT_CONSUMER_MAP_V0664.json'
        if consumer_path.exists():
            consumer = json.loads(consumer_path.read_text(encoding='utf-8'))
            rows = consumer.get('requirements') or []
            if len(rows) != 60:
                add('CONSUMER_MAP_COUNT_MISMATCH', actual=len(rows), expected=60)
            ids = {str(x.get('req') or '') for x in rows if isinstance(x, dict)}
            expected_ids = {f'REQ-{i:03d}' for i in range(1, 61)}
            if ids != expected_ids:
                add('CONSUMER_MAP_ID_SET_MISMATCH', missing=sorted(expected_ids-ids), unexpected=sorted(ids-expected_ids))

        audit_path = res / 'runtime' / 'cbcc' / 'long_requirement_full_audit.py'
        if audit_path.exists():
            audit_text = audit_path.read_text(encoding='utf-8')
            for token in ('_project_shortcut_audit', 'PRODUCTION_OBJECTS_INCOMPLETE', 'GLOBAL_POST_COMPOSITE_POLICY', 'FIXED_CAPABILITY_ROUTE_TAXONOMY'):
                if token not in audit_text:
                    add('REAL_K01_AUDIT_TOKEN_MISSING', token=token)

        integrated_path = res / 'runtime' / 'cbcc' / 'integrated_render_route_authority.py'
        if integrated_path.exists():
            integrated = integrated_path.read_text(encoding='utf-8')
            for token in ('MODEL_RENDER_INTEGRATED', 'REFERENCE_GUIDED_NATIVE_LOCK'):
                if token not in integrated:
                    add('INTEGRATED_RENDER_TOKEN_MISSING', token=token)

        bootstrap_path = res / 'runtime' / 'cbcc' / 'commercial_continuity_bootstrap.py'
        if bootstrap_path.exists():
            bootstrap = bootstrap_path.read_text(encoding='utf-8')
            order = [
                bootstrap.find('normalize_full_art_direction'),
                bootstrap.find('finalize_integrated_render_route'),
                bootstrap.find('finalize_model_prompt_bundle'),
            ]
            if any(i < 0 for i in order) or not (order[0] < order[1] < order[2]):
                add('PROMPT_BOUNDARY_ORDER_INVALID', offsets=order)

        result = {
            'status': 'PASS' if not issues else 'FAIL',
            'issue_count': len(issues),
            'issues': issues,
            'plugin_version': manifest.get('version'),
            'authority_version': EXPECTED_AUTHORITY,
            'top_skill_bytes': top.stat().st_size if top.exists() else None,
            'required_file_count': len(required),
            'requirement_count': 60,
            'historical_canonical_chain': False,
        }
        return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('plugin_zip')
    args = ap.parse_args()
    result = audit(Path(args.plugin_zip))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
