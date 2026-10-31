#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0673 as previous

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.6.74'
AUTHORITY_VERSION = '0.6.74-cross-scope-regression-closure'
V0673_FLOOR_BYTES = 67365
# Bootstrap proof pass discovers the exact v0.6.73 canonical Skill digest.
# The final release MUST hard-lock the observed SHA256 before publication.
V0673_FLOOR_SHA256 = ''

BASE_COPY_REPO_RESOURCES = base.copy_repo_resources
BASE_PLUGIN_MANIFEST = previous.plugin_manifest

V0674_PATCH = r'''
## 0.23 Cross-Scope Regression Closure — v0.6.74
v0.6.73 remains the exact bilingual business-object / Model Prompt consumption capability floor. This release is strictly additive: it closes cross-scope consumer regressions found by deep v0.6.73 package audit without replacing Product Truth, seven commerce tools, Pricing/Economics, open Asset Universe, Product Presence, complete Art Direction, model-native Prompt, mature asset packages, Provider/Review boundaries, or the project-authored `cbcc-commercial-v1` Human Workspace.

### FULL aliases are semantic aliases, not literal-string traps
FULL-depth consumers recognize explicit complete-project aliases including `FULL_STRATEGY`, `FULL_E2E`, `FULL_PROJECT`, `FULL_DELIVERY`, `FULL_PACKAGE`, `FULL_COMMERCE` and equivalent explicit complete-delivery forms. `TASK_SCOPED`, `PARTIAL`, `NOT_FULL`, `NON_FULL` and incidental words remain non-FULL. Cached consumers such as final delivery export must be rebound after prior bootstrap wrappers so the final validator uses the same semantics.

### Current explicit platform / market / locale scope wins
Human target summaries, Listing lifecycle and visible-copy locale selection must consume the current explicit request/target scope. Historical `target_context`, prior fixtures or platform compilation defaults may not silently reintroduce an old platform, market, site or locale. A target switch such as MY → SG / US must replace stale `visible_copy_locales`; an unspecified current target remains unspecified rather than inferred from historical localized copy.

### Listing lifecycle distinguishes strategy, review and publication
The canonical project-level Listing lifecycle is exactly `STRATEGY_READY`, `COPY_REVIEW_REQUIRED`, or `PUBLISH_READY` when Listing is active. Existing field-level statuses and legacy readiness strings remain compatibility metadata and are not overwritten. Lifecycle evaluation is scoped to the current explicit target / visible locale set: unrelated historical locale drafts cannot block a valid current locale, and a final copy from another locale cannot make the current target publish-ready. `PUBLISH_READY` additionally requires submission-sensitive scope, no blocking required fields, final-approved current-target copy, and the required Chinese companion when delivery language differs.

### Human/package serialization must not corrupt authored content
Escaped Markdown table pipes (`\\|`) remain literal cell content instead of creating false columns. YAML materialization suppresses anchors/aliases so repeated object identity does not leak serializer implementation details into asset manifests. Source Truth media audit is also projected into a normalized Source Ledger that preserves copied/missing/unresolved status, package path, source path, bytes and hash without implying that a filename equals an available source.

### Model Prompt provenance membrane removes metadata, not the picture
Internal source IDs, evidence IDs, hashes, artifact paths and provenance assignments remain outside model-facing Prompt text. Removal is metadata-shaped and clause-local: when metadata shares a clause with real pixel/frame instructions, only the metadata is removed. Normal visual language such as “compression artifacts”, “provenance-inspired”, “material lineage”, reference-image use, camera perspective, contact shadow, lighting, CMF/material and other image/video-changing decisions must survive.

### Release evidence boundary remains strict
The v0.6.74 focused regression suite proves these narrow closures only. A formal release still requires one release family across manifests, both canonical Skills, `resources/VERSION`, CURRENT builder and CURRENT override; cumulative v0.6.70–v0.6.73 floors; exact-ZIP v0.6.74 checks; installed readback; and a fresh real K01 FULL run through a Host context that actually resolves the installed release. Provider Result / actual media / pixel-frame Review / smallest Local Revision / provenance remain `E2E_PENDING` until genuinely produced.
'''.strip()


def _normalize_identity(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', f'version: {AUTHORITY_VERSION}', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', f'# Cross-Border Commerce Creative v{VERSION}', text, count=1)
    return text


def current_v0673_floor() -> str:
    text = previous.canonical_skill()
    data = text.encode('utf-8')
    if len(data) != V0673_FLOOR_BYTES:
        raise RuntimeError(f'v0.6.73 Skill floor drift: bytes={len(data)} expected={V0673_FLOOR_BYTES}')
    digest = hashlib.sha256(data).hexdigest()
    print(json.dumps({'v0673_skill_floor_bytes': len(data), 'v0673_skill_floor_sha256': digest}, ensure_ascii=False))
    if V0673_FLOOR_SHA256 and digest != V0673_FLOOR_SHA256:
        raise RuntimeError(f'v0.6.73 Skill floor drift: sha256={digest} expected={V0673_FLOOR_SHA256}')
    for token in (
        '## 0.22 Bilingual Business-Object Delivery + Model Prompt Consumption Closure',
        '## 0.21 Fresh K01 Runtime Projection Closure',
        '## 0.20 Full Canonical Human + Package Lineage Parity',
        '## 0.19 Canonical Materialization + Human Projection Parity',
        '## 1. FULL depth remains mandatory',
    ):
        if token not in text:
            raise RuntimeError(f'v0.6.73 Skill floor lost marker: {token}')
    return text


def canonical_skill(version: str = VERSION) -> str:
    text = _normalize_identity(current_v0673_floor())
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.73 Skill floor lost FULL-depth marker')
    if '## 0.23 Cross-Scope Regression Closure' not in text:
        text = text.replace(marker, '\n' + V0674_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(VERSION)


def copy_repo_resources(dest: Path) -> None:
    BASE_COPY_REPO_RESOURCES(dest)
    skill = canonical_skill(VERSION)
    (dest / 'SKILL.md').write_text(skill, encoding='utf-8')
    (dest / 'VERSION').write_text(AUTHORITY_VERSION + '\n', encoding='utf-8')


def openai_yaml() -> str:
    return '''interface:\n  display_name: Cross-Border Commerce Creative\n  short_description: 0.6.74闭合跨平台/语言/Listing/Prompt/来源序列化回归的跨境Commerce Agent\npolicy:\n  allow_implicit_invocation: true\n'''


def plugin_manifest(version: str) -> dict:
    manifest = BASE_PLUGIN_MANIFEST(VERSION)
    manifest['version'] = VERSION
    manifest['description'] = (
        'Cross-border ecommerce Commerce Agent with frozen v0.6.69 maturity, v0.6.70 semantic/prompt parity, '
        'v0.6.71 final-package/Human/00–15 lineage parity, v0.6.72 fresh-K01 Runtime projection closure, '
        'v0.6.73 bilingual business-object/model-prompt consumption closure, plus v0.6.74 cross-scope regression closure.'
    )
    dc = manifest.setdefault('delivery_contract', {})
    dc.update({
        'v074_explicit_platform_locale_scope_required': True,
        'v074_full_alias_closure_required': True,
        'v074_listing_release_state_required': True,
        'v074_markdown_escaped_pipe_required': True,
        'v074_prompt_provenance_membrane_required': True,
        'v074_source_ledger_required': True,
        'v074_yaml_no_anchor_required': True,
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
    release['release'] = 'v0.6.74 Cross-Scope Regression Closure'
    release['authority_version'] = AUTHORITY_VERSION
    release.setdefault('delivery_contract', {}).update(plugin_manifest(VERSION).get('delivery_contract') or {})
    release['v0674_evidence_boundary'] = {
        'focused_regression_suite': 'REQUIRED',
        'cumulative_v0670_v0673_floors': 'REQUIRED',
        'fresh_k01_full_after_install': 'REQUIRED_FOR_BEHAVIORAL_CLOSURE',
        'provider_actual_media': 'E2E_PENDING_UNTIL_REAL_PROVIDER_OUTPUT',
    }
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.74 additively from the exact verified v0.6.73 Skill floor.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0674'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
