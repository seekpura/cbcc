#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any

VERSION = '0.6.71'
AUTHORITY = '0.6.71-full-canonical-human-package-lineage-parity'
REQUIRED_RUNTIME = {
    'runtime/cbcc/canonical_full_parity_v0671.py': (
        'CBCC_CANONICAL_STATIC_PROJECTION_V0671',
        'CANONICAL_HUMAN_DATA.json',
        'HTML_CANONICAL_GENERIC_FIELD_COVERAGE_INCOMPLETE_V0671',
        'CBCC_GLOBAL_SEARCH_INDEX_V0671',
        'data-canonical-path',
    ),
    'runtime/cbcc/listing_markdown_parity_v0671.py': (
        '多语言 Listing Canonical 对照',
        'LISTING_MARKDOWN_CANONICAL_FIELD_DRIFT',
    ),
    'runtime/cbcc/asset_package_full_lineage_v0671.py': (
        'CANONICAL_LINEAGE.json',
        'ASSET_PACKAGE_FULL_LINEAGE_DRIFT',
        'ASSET_PACKAGE_CANONICAL_LINEAGE_DRIFT_V0671',
    ),
    'runtime/cbcc/strategy_execution_completion_v0671.py': (
        'major_decision_context_why',
        'intersectionality_interaction_analysis',
        'FULL_MAJOR_DECISION_CONTEXT_WHY_MISSING_V0671',
    ),
    'runtime/cbcc/asset_execution_relevance_v0671.py': (
        'human_relevance_decisions',
        'typography_contract',
        'ASSET_TYPOGRAPHY_DECISION_MISSING',
    ),
    'runtime/cbcc/canonical_full_package_audit_v0671.py': (
        'V0671_FULL_CANONICAL_BUSINESS_OBJECT_PARITY',
        'full_asset_package_lineage',
        'listing_md_multilingual_parity',
    ),
}
REQUIRED_FLAGS = (
    'real_final_package_human_projection_required',
    'canonical_business_object_generic_field_coverage_required',
    'listing_markdown_multilingual_canonical_parity_required',
    'full_asset_package_00_15_lineage_required',
    'asset_visual_photography_layout_source_strategy_trace_human_visible',
    'major_decision_four_axis_context_why_required',
    'intersectionality_interaction_analysis_required',
    'human_asset_relevance_decisions_required',
    'typography_relevance_contract_required',
)


def _root(extracted: Path) -> Path:
    direct = extracted / 'cross-border-commerce-creative'
    if direct.exists():
        return direct
    candidates = [p for p in extracted.iterdir() if p.is_dir() and (p / 'plugin.json').exists()]
    if len(candidates) == 1:
        return candidates[0]
    return extracted


def audit(plugin_zip: Path) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix='cbcc-v0671-delta-') as td:
        dest = Path(td)
        with zipfile.ZipFile(plugin_zip) as zf:
            zf.extractall(dest)
        plugin = _root(dest)
        manifest = json.loads((plugin / 'plugin.json').read_text(encoding='utf-8'))
        if manifest.get('version') != VERSION:
            issues.append({'code': 'V0671_PLUGIN_VERSION_MISMATCH', 'actual': manifest.get('version')})
        dc = manifest.get('delivery_contract') or {}
        for flag in REQUIRED_FLAGS:
            if dc.get(flag) is not True:
                issues.append({'code': 'V0671_DELIVERY_CONTRACT_FLAG_MISSING', 'flag': flag})
        skill_root = plugin / 'skills/cross-border-commerce-creative'
        top = skill_root / 'SKILL.md'
        deep = skill_root / 'resources/SKILL.md'
        if not top.exists() or not deep.exists() or top.read_bytes() != deep.read_bytes():
            issues.append({'code': 'V0671_SKILL_PARITY_FAILED'})
        else:
            text = top.read_text(encoding='utf-8-sig')
            for token in (f'version: {AUTHORITY}', '# Cross-Border Commerce Creative v0.6.71', '## 0.20 Full Canonical Human + Package Lineage Parity', '## 0.19 Canonical Materialization + Human Projection Parity'):
                if token not in text:
                    issues.append({'code': 'V0671_SKILL_TOKEN_MISSING', 'token': token})
        version_file = skill_root / 'resources/VERSION'
        if not version_file.exists() or version_file.read_text(encoding='utf-8-sig').strip() != AUTHORITY:
            issues.append({'code': 'V0671_RESOURCE_VERSION_MISMATCH'})
        resources = skill_root / 'resources'
        for rel, tokens in REQUIRED_RUNTIME.items():
            path = resources / rel
            if not path.exists():
                issues.append({'code': 'V0671_RUNTIME_FILE_MISSING', 'path': rel})
                continue
            text = path.read_text(encoding='utf-8')
            for token in tokens:
                if token not in text:
                    issues.append({'code': 'V0671_RUNTIME_TOKEN_MISSING', 'path': rel, 'token': token})
        export = resources / 'runtime/cbcc/delivery_export_continuity.py'
        if not export.exists():
            issues.append({'code': 'V0671_EXPORT_BOUNDARY_MISSING'})
        else:
            text = export.read_text(encoding='utf-8')
            for token in ('FULL_CANONICAL_PARITY_AUDIT_V0671.json', '_v0671_full_canonical_export_audit', 'full_asset_package_lineage', 'canonical_business_field_coverage'):
                if token not in text:
                    issues.append({'code': 'V0671_EXPORT_TOKEN_MISSING', 'token': token})
        bootstrap = resources / 'runtime/cbcc/commercial_continuity_bootstrap.py'
        if bootstrap.exists():
            text = bootstrap.read_text(encoding='utf-8')
            ordered = [
                'complete_asset_execution_relevance(call_args[0] or {})',
                'normalize_full_art_direction(call_args[0] or {})',
                'validate_canonical_asset_or_raise(normalized_asset)',
                'existing_prompt_compile(*call_args, **kwargs)',
                'finalize_integrated_render_route(normalized_asset, out)',
                'finalize_model_prompt_bundle(out)',
                'finalize_prompt_lineage(normalized_asset, out)',
            ]
            offsets = [text.find(x) for x in ordered]
            if any(x < 0 for x in offsets) or offsets != sorted(offsets):
                issues.append({'code': 'V0671_PROMPT_BOUNDARY_ORDER_INVALID', 'offsets': offsets})
    return {'status': 'PASS' if not issues else 'FAIL', 'issue_count': len(issues), 'issues': issues, 'version': VERSION, 'authority_version': AUTHORITY}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('plugin_zip')
    args = parser.parse_args()
    result = audit(Path(args.plugin_zip))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
