#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0671 as previous

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.6.72'
AUTHORITY_VERSION = '0.6.72-fresh-k01-runtime-projection-closure'
V0671_FLOOR_BYTES = 60081
V0671_FLOOR_SHA256 = '07008d4d41a3e5a2736110fa54b3fdfe4da5be3190ff2eb3f307d491b6705aab'

BASE_COPY_REPO_RESOURCES = base.copy_repo_resources
BASE_PLUGIN_MANIFEST = base.plugin_manifest

V0672_PATCH = r'''
## 0.21 Fresh K01 Runtime Projection Closure — v0.6.72
v0.6.71 remains the additive final-package/Human/00–15 lineage floor. This release is driven by a fresh K01 FULL run against `KIYUU_5款产品信息_纯粹版(7).xlsx`, not by synthetic fixtures alone. It closes integration gaps where already-authored canonical data existed but a downstream Runtime consumer failed to reuse it.

### Canonical portfolio rhythm is one field, not parallel aliases
`resources/runtime/cbcc/portfolio_visual_authority.py` now consumes `portfolio_rhythm_delta` / `rhythm_delta` as canonical adjacent-asset differentiation evidence in addition to historical aliases. A real K01 portfolio no longer receives false `MISSING_ADJACENT_ASSET_DELTA` merely because Prompt/Human/lineage use the newer canonical field. Duplicate visual-signature detection and return-to-Agent behavior remain unchanged.

### Authored asset worlds positively project into the Visual Master
`resources/runtime/cbcc/canonical_visual_master_projection_v0672.py` losslessly aggregates already-authored per-asset `environment/scene` and `props` into missing project-level Visual Master scene/props slots. It never synthesizes a scene/prop and never overrides explicit project-level `visual_strategy` or `photography_contract` decisions. This closes the fresh-K01 case where all production assets had authored worlds but the final FULL strategy still reported project-level scene/props as missing.

### Authored delivery-locale copy is reused instead of requested twice
`resources/runtime/cbcc/delivery_companion_projection_v0672.py` reuses an already-authored delivery-locale field (normally `zh-CN`) as the human Chinese companion for target-market/English final-copy rows. Missing Chinese remains unresolved: Runtime does not machine-translate or infer a companion.

The same additive closure recognizes the mature Visible Copy shape `14_visible_copy_block.json → raw.chinese_meaning`, preserves authored Chinese hook/CTA companions for video/creator plans including values nested in `asset_art_direction`, and bilingualizes only Runtime-owned fixed default Creator CTA copy. Custom foreign copy without authored Chinese remains blocking.

### Bootstrap order is a release invariant
The v0.6.72 language closure may update by-value consumers only when those modules are already loaded. It must not import `cbcc.compiler` during bootstrap, because doing so would freeze an intermediate Strategy builder before v0.6.70/v0.6.71 completion wrappers install. CI explicitly proves `import cbcc` does not eagerly load compiler and that both prior strategy-completion wrappers remain in the callable closure chain.

### Human projection avoids duplicate heavy-object materialization
`resources/runtime/cbcc/canonical_human_compaction_v0672.py` preserves generic field coverage while removing duplicate copies of heavy `assets` / `asset_universe` families from the Canonical Business Object archive. Assets and Asset Universe remain fully reachable on their dedicated Human surfaces. Search and Copy continue to use safe DOM APIs and rendered canonical leaves; no user/canonical value is injected as executable HTML.

### Fresh K01 structural evidence boundary
The release regression set covers the exact defects discovered by the fresh K01 run: portfolio-delta consumption, authored scene/props aggregation, authored Chinese companion reuse, Visible Copy nested Chinese meaning, video hook/CTA companion propagation, bootstrap import order and deduplicated Human projection. The final package must still pass all v0.6.70 and v0.6.71 semantic/lineage/Human parity checks.

This is structural FULL materialization evidence, not fabricated media evidence. Actual Provider Result, generated product imagery/video, pixel-level Review, Local Revision and provenance remain `E2E_PENDING` until they genuinely occur. A fresh Host context resolving this installed release is separate Host-native evidence.
'''.strip()


def _normalize_identity(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', f'version: {AUTHORITY_VERSION}', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', f'# Cross-Border Commerce Creative v{VERSION}', text, count=1)
    return text


def current_v0671_floor() -> str:
    text = previous.canonical_skill()
    data = text.encode('utf-8')
    if len(data) != V0671_FLOOR_BYTES:
        raise RuntimeError(f'v0.6.71 Skill floor drift: bytes={len(data)} expected={V0671_FLOOR_BYTES}')
    digest = hashlib.sha256(data).hexdigest()
    if digest != V0671_FLOOR_SHA256:
        raise RuntimeError(f'v0.6.71 Skill floor drift: sha256={digest} expected={V0671_FLOOR_SHA256}')
    for token in ('## 0.20 Full Canonical Human + Package Lineage Parity', '## 0.19 Canonical Materialization + Human Projection Parity', '## 1. FULL depth remains mandatory'):
        if token not in text:
            raise RuntimeError(f'v0.6.71 Skill floor lost marker: {token}')
    return text


def canonical_skill(version: str = VERSION) -> str:
    text = _normalize_identity(current_v0671_floor())
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.71 Skill floor lost FULL-depth marker')
    if '## 0.21 Fresh K01 Runtime Projection Closure' not in text:
        text = text.replace(marker, '\n' + V0672_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(VERSION)


def copy_repo_resources(dest: Path) -> None:
    BASE_COPY_REPO_RESOURCES(dest)
    skill = canonical_skill(VERSION)
    (dest / 'SKILL.md').write_text(skill, encoding='utf-8')
    (dest / 'VERSION').write_text(AUTHORITY_VERSION + '\n', encoding='utf-8')


def openai_yaml() -> str:
    return '''interface:\n  display_name: Cross-Border Commerce Creative\n  short_description: fresh K01实跑闭合Canonical投影、语言伴随与Human全链的跨境Commerce Agent\npolicy:\n  allow_implicit_invocation: true\n'''


def plugin_manifest(version: str) -> dict:
    manifest = BASE_PLUGIN_MANIFEST(VERSION)
    manifest['version'] = VERSION
    manifest['description'] = (
        'Cross-border ecommerce Commerce Agent with frozen v0.6.69 maturity, v0.6.70 semantic/prompt parity, '
        'v0.6.71 final-package/Human/00–15 lineage parity, and v0.6.72 fresh-K01 Runtime projection closure.'
    )
    dc = manifest.setdefault('delivery_contract', {})
    dc.update({
        'v069_exact_skill_floor_required': True,
        'v070_canonical_materialization_floor_required': True,
        'v071_full_canonical_human_package_lineage_floor_required': True,
        'canonical_portfolio_rhythm_delta_consumption_required': True,
        'authored_asset_world_visual_master_projection_required': True,
        'authored_delivery_locale_companion_projection_required': True,
        'visible_copy_nested_chinese_meaning_recognition_required': True,
        'video_authored_chinese_companion_preservation_required': True,
        'bootstrap_import_order_safety_required': True,
        'canonical_human_heavy_object_single_materialization_required': True,
        'fresh_k01_structural_regression_suite_required': True,
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
    release['release'] = 'v0.6.72 Fresh K01 Runtime Projection Closure'
    release['authority_version'] = AUTHORITY_VERSION
    release.setdefault('delivery_contract', {}).update(plugin_manifest(VERSION).get('delivery_contract') or {})
    release['fresh_k01_evidence_boundary'] = {
        'structural_full_materialization': 'REQUIRED_AND_REGRESSION_TESTED',
        'provider_actual_media': 'E2E_PENDING_UNTIL_REAL_PROVIDER_OUTPUT',
        'fresh_host_native_context': 'SEPARATE_EVIDENCE_AFTER_INSTALL',
    }
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.72 additively from the exact verified v0.6.71 Skill floor.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0672'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
