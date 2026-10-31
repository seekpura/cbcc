#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any

VERSION = '0.6.72'
AUTHORITY = '0.6.72-fresh-k01-runtime-projection-closure'
REQUIRED_FLAGS = (
    'v071_full_canonical_human_package_lineage_floor_required',
    'canonical_portfolio_rhythm_delta_consumption_required',
    'authored_asset_world_visual_master_projection_required',
    'authored_delivery_locale_companion_projection_required',
    'visible_copy_nested_chinese_meaning_recognition_required',
    'video_authored_chinese_companion_preservation_required',
    'bootstrap_import_order_safety_required',
    'canonical_human_heavy_object_single_materialization_required',
    'fresh_k01_structural_regression_suite_required',
    'provider_actual_media_e2e_required_before_media_qa_claim',
)
REQUIRED_RUNTIME = {
    'runtime/cbcc/portfolio_visual_authority.py': (
        "'portfolio_rhythm_delta'", "'rhythm_delta'", 'DUPLICATE_VISUAL_SIGNATURE',
    ),
    'runtime/cbcc/canonical_visual_master_projection_v0672.py': (
        'AUTHORED_ASSET_ART_DIRECTIONS', 'environment_system', 'prop_system', 'no new scene fact is invented',
    ),
    'runtime/cbcc/delivery_companion_projection_v0672.py': (
        'READY_AUTHORED_DELIVERY_LOCALE_COPY', 'chinese_meaning', 'asset_art_direction',
        'Runtime only bilingualizes its own fixed default Creator CTA', 'sys.modules.get',
        'install_fresh_k01_runtime_closure',
    ),
    'runtime/cbcc/canonical_human_compaction_v0672.py': (
        'CBCC_CANONICAL_STATIC_PROJECTION_V0672', 'deduplicated_heavy_object_families',
        'single embedded canonical payload + lazy DOM inspector', 'textContent', 'replaceChildren',
    ),
    'runtime/cbcc/canonical_human_lazy_projection_v0672.py': (
        'CBCC_CANONICAL_LAZY_PROJECTION_V0672', 'data-canonical-mount', 'cbcc-canonical-data-v0672',
        'textContent', 'replaceChildren',
    ),
    'runtime/cbcc/fresh_k01_runtime_closure_v0672.py': (
        '_GRAPHIC_TOKEN', 'camera_position', 'focus_dof', 'motion_timing', 'chinese_meaning',
        'typography_contract', 'human_relevance_decisions', '_explicit_no_visible_copy_instruction',
        'GLOBAL_NO_VISIBLE_COPY_PATTERN', 'install',
    ),
    'runtime/cbcc/compliance.py': (
        'research_blocking_pending', 'PLANNING_ONLY_RESEARCH_PENDING',
    ),
    'runtime/cbcc/canonical_full_package_audit_v0671.py': (
        'canonical_human_lazy_projection_v0672', 'build_canonical_human_payload', 'finalize_static_human_projection',
    ),
    'runtime/cbcc/html_asset_package_parity.py': (
        'cbcc-canonical-data-v0672', 'CANONICAL_HUMAN_DATA.json',
    ),
    'runtime/cbcc/listing_markdown_parity_v0671.py': (
        '多语言 Listing Canonical 对照', '使用块式原文', '_refresh_appendix',
    ),
}


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
    with tempfile.TemporaryDirectory(prefix='cbcc-v0672-delta-') as td:
        dest = Path(td)
        with zipfile.ZipFile(plugin_zip) as zf:
            zf.extractall(dest)
        plugin = _root(dest)
        manifest = json.loads((plugin / 'plugin.json').read_text(encoding='utf-8'))
        if manifest.get('version') != VERSION:
            issues.append({'code': 'V0672_PLUGIN_VERSION_MISMATCH', 'actual': manifest.get('version')})
        dc = manifest.get('delivery_contract') or {}
        for flag in REQUIRED_FLAGS:
            if dc.get(flag) is not True:
                issues.append({'code': 'V0672_DELIVERY_CONTRACT_FLAG_MISSING', 'flag': flag})

        skill_root = plugin / 'skills/cross-border-commerce-creative'
        top = skill_root / 'SKILL.md'
        deep = skill_root / 'resources/SKILL.md'
        if not top.exists() or not deep.exists() or top.read_bytes() != deep.read_bytes():
            issues.append({'code': 'V0672_SKILL_PARITY_FAILED'})
        else:
            text = top.read_text(encoding='utf-8-sig')
            for token in (
                f'version: {AUTHORITY}', '# Cross-Border Commerce Creative v0.6.72',
                '## 0.21 Fresh K01 Runtime Projection Closure',
                '## 0.20 Full Canonical Human + Package Lineage Parity',
                '## 0.19 Canonical Materialization + Human Projection Parity',
            ):
                if token not in text:
                    issues.append({'code': 'V0672_SKILL_TOKEN_MISSING', 'token': token})
        version_file = skill_root / 'resources/VERSION'
        if not version_file.exists() or version_file.read_text(encoding='utf-8-sig').strip() != AUTHORITY:
            issues.append({'code': 'V0672_RESOURCE_VERSION_MISMATCH'})

        resources = skill_root / 'resources'
        for rel, tokens in REQUIRED_RUNTIME.items():
            path = resources / rel
            if not path.exists():
                issues.append({'code': 'V0672_RUNTIME_FILE_MISSING', 'path': rel})
                continue
            text = path.read_text(encoding='utf-8')
            for token in tokens:
                if token not in text:
                    issues.append({'code': 'V0672_RUNTIME_TOKEN_MISSING', 'path': rel, 'token': token})

        language = resources / 'runtime/cbcc/delivery_companion_projection_v0672.py'
        if language.exists():
            text = language.read_text(encoding='utf-8')
            if 'from . import compiler' in text or 'import cbcc.compiler' in text:
                issues.append({'code': 'V0672_BOOTSTRAP_EARLY_COMPILER_IMPORT_PRESENT'})

        bootstrap = resources / 'runtime/cbcc/commercial_continuity_bootstrap.py'
        if not bootstrap.exists():
            issues.append({'code': 'V0672_BOOTSTRAP_MISSING'})
        else:
            text = bootstrap.read_text(encoding='utf-8')
            for token in (
                'wrap_visual_master_projection_v0672', 'wrap_delivery_companion_projection_v0672',
                '_cbcc_v0672_visual_master_projection', '_cbcc_v0672_delivery_companion_projection',
            ):
                if token not in text:
                    issues.append({'code': 'V0672_BOOTSTRAP_TOKEN_MISSING', 'token': token})

        override = resources / 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json'
        if not override.exists():
            issues.append({'code': 'V0672_CURRENT_OVERRIDE_MISSING'})
        else:
            payload = json.loads(override.read_text(encoding='utf-8'))
            if payload.get('current_release_version') != VERSION:
                issues.append({'code': 'V0672_CURRENT_OVERRIDE_VERSION_MISMATCH', 'actual': payload.get('current_release_version')})

    return {
        'status': 'PASS' if not issues else 'FAIL',
        'issue_count': len(issues),
        'issues': issues,
        'version': VERSION,
        'authority_version': AUTHORITY,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('plugin_zip')
    args = parser.parse_args()
    result = audit(Path(args.plugin_zip))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
