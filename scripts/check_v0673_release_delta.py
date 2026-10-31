#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any

VERSION = '0.6.73'
AUTHORITY = '0.6.73-bilingual-business-object-delivery-closure'
REQUIRED_FLAGS = (
    'v072_fresh_k01_runtime_projection_floor_required',
    'structured_bilingual_business_object_preservation_required',
    'listing_semantic_chinese_field_titles_required',
    'compound_measurement_language_neutrality_required',
    'video_visible_copy_hook_precedence_required',
    'model_render_integrated_alias_normalization_required',
    'nested_bilingual_model_prompt_projection_required',
    'not_needed_execution_objects_excluded_from_model_prompt_required',
    'fresh_k01_prompt_consumption_ready_required',
    'provider_actual_media_e2e_required_before_media_qa_claim',
)
REQUIRED_RUNTIME = {
    'runtime/cbcc/asset_compiler.py': (
        '_operator_text', '_semantic_text_values', "_operator_text(asset.get('strategic_job')",
    ),
    'runtime/cbcc/human_language_delivery.py': (
        "'selling_points': '卖点短句'", "'specification': '规格'", "'key_ingredients': '关键成分'",
        'compound specifications',
    ),
    'runtime/cbcc/video_creator.py': (
        '_authored_visible_hook', "authored_hook,authored_hook_cn", "'hook_cn':hook_cn",
    ),
    'runtime/cbcc/model_native_prompt_contract.py': (
        'MODEL_RENDER_INTEGRATED', 'INTEGRATED_MODEL_RENDER', 'MODEL_NATIVE_RENDER',
        'Resolve each child', "props_value", "status') or '').upper() == 'NOT_NEEDED'",
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
    with tempfile.TemporaryDirectory(prefix='cbcc-v0673-delta-') as td:
        dest = Path(td)
        with zipfile.ZipFile(plugin_zip) as zf:
            zf.extractall(dest)
        plugin = _root(dest)
        manifest = json.loads((plugin / 'plugin.json').read_text(encoding='utf-8'))
        if manifest.get('version') != VERSION:
            issues.append({'code': 'V0673_PLUGIN_VERSION_MISMATCH', 'actual': manifest.get('version')})
        dc = manifest.get('delivery_contract') or {}
        for flag in REQUIRED_FLAGS:
            if dc.get(flag) is not True:
                issues.append({'code': 'V0673_DELIVERY_CONTRACT_FLAG_MISSING', 'flag': flag})

        skill_root = plugin / 'skills/cross-border-commerce-creative'
        top = skill_root / 'SKILL.md'
        deep = skill_root / 'resources/SKILL.md'
        if not top.exists() or not deep.exists() or top.read_bytes() != deep.read_bytes():
            issues.append({'code': 'V0673_SKILL_PARITY_FAILED'})
        else:
            text = top.read_text(encoding='utf-8-sig')
            for token in (
                f'version: {AUTHORITY}', '# Cross-Border Commerce Creative v0.6.73',
                '## 0.22 Bilingual Business-Object Delivery + Model Prompt Consumption Closure',
                '## 0.21 Fresh K01 Runtime Projection Closure',
                '## 0.20 Full Canonical Human + Package Lineage Parity',
                '## 0.19 Canonical Materialization + Human Projection Parity',
            ):
                if token not in text:
                    issues.append({'code': 'V0673_SKILL_TOKEN_MISSING', 'token': token})
        version_file = skill_root / 'resources/VERSION'
        if not version_file.exists() or version_file.read_text(encoding='utf-8-sig').strip() != AUTHORITY:
            issues.append({'code': 'V0673_RESOURCE_VERSION_MISMATCH'})

        resources = skill_root / 'resources'
        for rel, tokens in REQUIRED_RUNTIME.items():
            path = resources / rel
            if not path.exists():
                issues.append({'code': 'V0673_RUNTIME_FILE_MISSING', 'path': rel})
                continue
            text = path.read_text(encoding='utf-8')
            for token in tokens:
                if token not in text:
                    issues.append({'code': 'V0673_RUNTIME_TOKEN_MISSING', 'path': rel, 'token': token})

        override = resources / 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json'
        if not override.exists():
            issues.append({'code': 'V0673_CURRENT_OVERRIDE_MISSING'})
        else:
            payload = json.loads(override.read_text(encoding='utf-8'))
            if payload.get('current_release_version') != VERSION:
                issues.append({'code': 'V0673_CURRENT_OVERRIDE_VERSION_MISMATCH', 'actual': payload.get('current_release_version')})

        current_builder = resources / 'scripts/build_plugin_dist_current.py'
        if not current_builder.exists():
            issues.append({'code': 'V0673_CURRENT_BUILDER_MISSING'})
        else:
            text = current_builder.read_text(encoding='utf-8')
            if "CURRENT_BUILDER_TARGET = '0.6.73'" not in text or 'build_plugin_dist_v0673' not in text:
                issues.append({'code': 'V0673_CURRENT_BUILDER_TARGET_MISMATCH'})

    return {'status':'PASS' if not issues else 'FAIL','issue_count':len(issues),'issues':issues,'version':VERSION,'authority_version':AUTHORITY}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('plugin_zip'); args=parser.parse_args()
    result=audit(Path(args.plugin_zip)); print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['status']=='PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
