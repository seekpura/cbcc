#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0672 as previous

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.6.73'
AUTHORITY_VERSION = '0.6.73-bilingual-business-object-delivery-closure'
V0672_FLOOR_BYTES = 64023
V0672_FLOOR_SHA256 = '1ad5fcc7809daa72afcebfe2db452d4bc83a7a913b1d78da9ce0794bf5e319dc'

BASE_COPY_REPO_RESOURCES = base.copy_repo_resources
BASE_PLUGIN_MANIFEST = previous.plugin_manifest

V0673_PATCH = r'''
## 0.22 Bilingual Business-Object Delivery + Model Prompt Consumption Closure — v0.6.73
v0.6.72 remains the exact fresh-K01 Runtime projection floor. This release is additive and is driven by a second fresh K01 FULL run through the installed v0.6.72 authority. That run exposed downstream consumers which still assumed scalar English strings or failed to consume already-authored bilingual execution objects. The fixes preserve structured canonical data and close only the responsible rendering/consumer boundaries.

### Structured bilingual business objects remain structured
`resources/runtime/cbcc/asset_compiler.py` now treats locale-keyed objects such as `{cn,en}` as canonical semantic values rather than coercing or concatenating them as strings. Machine manifests keep the original structure. Chinese-first human guidance selects an operator-readable Chinese value only at the human rendering boundary. Semantic comparisons flatten textual leaves only for matching, preventing unhashable-dict failures without destroying canonical structure.

### Mature Listing semantics stay Chinese-first without false language failures
`resources/runtime/cbcc/human_language_delivery.py` recognizes mature Listing fields `selling_points`, `specification` and `key_ingredients` with semantic Chinese operator labels. Pure compound measurement strings such as `30 g / 1.01 oz` or `1600 px × 1600 px` are treated as language-neutral only when every alphabetic token is a known measurement unit. Ordinary Latin prose still requires a Chinese companion.

### Video visible Hook comes from authored visible copy, not an internal shopper question
`resources/runtime/cbcc/video_creator.py` keeps `shopper_question` as an internal decision object but no longer promotes it to a human-facing Hook when the asset already carries authored Visible Copy. In the absence of an explicit video-job Hook, the builder reuses `visible_copy.target_copy` / equivalent authored target-market copy and preserves the authored Chinese meaning when present. Runtime never translates missing custom copy.

### Model-native Prompt consumption closes canonical route aliases and nested bilingual execution
`resources/runtime/cbcc/model_native_prompt_contract.py` normalizes canonical aliases such as `MODEL_RENDER_INTEGRATED` to the model-native `MODEL_RENDER` route so exact Visible Copy and Typography are consumed by the same layer that audits them. Nested bilingual execution objects are resolved recursively by language rather than dropping an entire object because another locale is present. Relevance decisions such as `props.status=NOT_NEEDED` remain visible in Human/Design Card authority but do not pollute model prompts or create false missing-consumption findings.

### Fresh K01 positive evidence boundary
The fresh 20-asset K01 run must reach `PROMPT_CONSUMPTION_AUDIT = READY` with zero missing decisions for every production asset, while Human Language, Delivery Language Matrix, Full Delivery Depth, Full Canonical Parity, Workspace Prompt Continuity, Canonical Materialization and Full Materialization audits all remain PASS with zero issues. Product Presence remains independently authored per asset. Provider Result / generated media / pixel-level Review / Local Revision / provenance remain `E2E_PENDING` until genuine provider execution exists.
'''.strip()


def _normalize_identity(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', f'version: {AUTHORITY_VERSION}', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', f'# Cross-Border Commerce Creative v{VERSION}', text, count=1)
    return text


def current_v0672_floor() -> str:
    text = previous.canonical_skill()
    data = text.encode('utf-8')
    if len(data) != V0672_FLOOR_BYTES:
        raise RuntimeError(f'v0.6.72 Skill floor drift: bytes={len(data)} expected={V0672_FLOOR_BYTES}')
    digest = hashlib.sha256(data).hexdigest()
    if digest != V0672_FLOOR_SHA256:
        raise RuntimeError(f'v0.6.72 Skill floor drift: sha256={digest} expected={V0672_FLOOR_SHA256}')
    for token in (
        '## 0.21 Fresh K01 Runtime Projection Closure',
        '## 0.20 Full Canonical Human + Package Lineage Parity',
        '## 0.19 Canonical Materialization + Human Projection Parity',
        '## 1. FULL depth remains mandatory',
    ):
        if token not in text:
            raise RuntimeError(f'v0.6.72 Skill floor lost marker: {token}')
    return text


def canonical_skill(version: str = VERSION) -> str:
    text = _normalize_identity(current_v0672_floor())
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.72 Skill floor lost FULL-depth marker')
    if '## 0.22 Bilingual Business-Object Delivery + Model Prompt Consumption Closure' not in text:
        text = text.replace(marker, '\n' + V0673_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(VERSION)


def copy_repo_resources(dest: Path) -> None:
    BASE_COPY_REPO_RESOURCES(dest)
    skill = canonical_skill(VERSION)
    (dest / 'SKILL.md').write_text(skill, encoding='utf-8')
    (dest / 'VERSION').write_text(AUTHORITY_VERSION + '\n', encoding='utf-8')


def openai_yaml() -> str:
    return '''interface:\n  display_name: Cross-Border Commerce Creative\n  short_description: fresh K01闭合双语业务对象、中文交付与Model Prompt参数消费的跨境Commerce Agent\npolicy:\n  allow_implicit_invocation: true\n'''


def plugin_manifest(version: str) -> dict:
    manifest = BASE_PLUGIN_MANIFEST(VERSION)
    manifest['version'] = VERSION
    manifest['description'] = (
        'Cross-border ecommerce Commerce Agent with frozen v0.6.69 maturity, v0.6.70 semantic/prompt parity, '
        'v0.6.71 final-package/Human/00–15 lineage parity, v0.6.72 fresh-K01 Runtime projection closure, '
        'and v0.6.73 bilingual business-object/model-prompt consumption closure.'
    )
    dc = manifest.setdefault('delivery_contract', {})
    dc.update({
        'v072_fresh_k01_runtime_projection_floor_required': True,
        'structured_bilingual_business_object_preservation_required': True,
        'listing_semantic_chinese_field_titles_required': True,
        'compound_measurement_language_neutrality_required': True,
        'video_visible_copy_hook_precedence_required': True,
        'model_render_integrated_alias_normalization_required': True,
        'nested_bilingual_model_prompt_projection_required': True,
        'not_needed_execution_objects_excluded_from_model_prompt_required': True,
        'fresh_k01_prompt_consumption_ready_required': True,
        'fresh_host_k01_full_still_required_for_behavioral_closure': True,
        'provider_actual_media_e2e_required_before_media_qa_claim': True,
    })
    return manifest


def build(output_dir: Path) -> dict:
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)
    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.73 Bilingual Business-Object Delivery + Model Prompt Consumption Closure'
    release['authority_version'] = AUTHORITY_VERSION
    release.setdefault('delivery_contract', {}).update(plugin_manifest(VERSION).get('delivery_contract') or {})
    release['fresh_k01_evidence_boundary'] = {
        'twenty_asset_structural_full_materialization': 'REQUIRED_AND_POSITIVE_E2E_VERIFIED_BEFORE_RELEASE',
        'prompt_consumption': 'READY_ZERO_MISSING_DECISIONS_REQUIRED',
        'provider_actual_media': 'E2E_PENDING_UNTIL_REAL_PROVIDER_OUTPUT',
        'fresh_host_native_context': 'SEPARATE_EVIDENCE_AFTER_INSTALL',
    }
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.73 additively from the exact verified v0.6.72 Skill floor.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0673'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
