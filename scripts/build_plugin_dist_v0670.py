#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0669 as previous

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.6.70'
AUTHORITY_VERSION = '0.6.70-canonical-materialization-human-projection-parity'
V0669_FLOOR_BYTES = 48517
V0669_FLOOR_SHA256 = 'f3ed58aafc24947e85fc268144ea787d4db5eaed66b31008f6a5cf87500cbd54'

BASE_COPY_REPO_RESOURCES = base.copy_repo_resources
BASE_PLUGIN_MANIFEST = base.plugin_manifest

V0670_PATCH = r'''
## 0.19 Canonical Materialization + Human Projection Parity — v0.6.70
The exact verified v0.6.69 packaged Skill is the additive capability floor. This release closes real K01 delivery drift without redesigning the mature routed workspace or weakening any v0.6.68/v0.6.69 business capability.

### Named canonical Art Direction is the single source for both Prompts
Production assets may no longer enter compilation through a semantically shifted positional object. Before Prompt compilation, `resources/runtime/cbcc/canonical_prompt_guard.py` validates named Art Direction domains. Cross-domain values such as Product Presence enums in `visual_carrier`, `POST_COMPOSITE` in evidence, visible copy in `copy_render_route`, Kelvin lighting prose in camera, output dimensions in CMF, or source-route enums in portfolio rhythm are `ASSET_SCHEMA_SEMANTIC_MISMATCH` and block generation. Runtime never guesses how to shift corrupted values back; the Agent must re-materialize the named canonical object.

The final Prompt chain is:
`named Agent Art Direction → normalize_full_art_direction → semantic asset guard → mature Prompt compiler → per-asset integrated render authority → final semantic membrane → canonical Art Direction lineage stamp`.
`Model Prompt CN` and `Model Prompt EN` therefore share one `canonical_art_direction_sha256`. A changed Art Direction with a stale Prompt bundle is `PROMPT_CANONICAL_LINEAGE_MISMATCH`.

`Visible Copy Block` language slots are also semantic contracts. Render route must be a recognized route enum; exact target-market copy, English semantic baseline and Chinese meaning/use cannot be shifted into each other's slots. A language-slot shift is `VISIBLE_COPY_LANGUAGE_SLOT_MISMATCH`.

### Human Workspace must consume authored canonical objects, not merely embed them in JSON
`resources/runtime/cbcc/human_projection_integrity.py` audits visible renderer consumption separately from embedded DATA. When canonical objects exist, Human HTML must expose the authored Listing, Strategy, Market, Visual, Content Matrix, RACE, Culture, Compliance, Ads, Review, Sources and per-asset Art Direction fields. In particular, Listing English description, key points, attributes, package contents and FAQ may not silently disappear while remaining hidden in DATA.

The Content Matrix retains cover, subtitles, music rights, traffic mechanism and landing handoff. RACE rows carry platform. Culture rows independently expose script, casting, wardrobe/grooming, color, CTA, validation result and modification action. Output self-check explicitly covers fabrication, WHY, culture, compliance, metrics and assumptions. Source URLs, review evidence status, P0/P1/P2 tradeoff and visual execution detail remain human-visible when authored.

Copy/search are behavioral, not self-declared booleans: a visible copy control must invoke clipboard/copy behavior; workspace search must cover business objects beyond `DATA.assets` when those objects are present.

### Strategy/culture completion is relevance-aware, not stereotype padding
FULL strategy completion preserves the v0.6.69 first-class objects and closes missing execution fields. Every major decision carries separate platform/region/audience/race-ethnicity-culture Context WHY; missing external evidence stays `TO_VERIFY`. Framework rows carry measurement. Inclusive photography keeps explicit relevance decisions for deep skin, hair texture/style, body representation, disability, age and AI bias. Disability or other identity dimensions are not inserted tokenistically: relevant human assets require an explicit decision + WHY; non-human/not-relevant cases remain `NOT_NEEDED + WHY`.

### Final package / ZIP boundary
`resources/runtime/cbcc/canonical_materialization_package_audit.py` is the final FULL package boundary. It audits mature asset directories, Visible Copy slots, Prompt contract route + canonical lineage, and Human Workspace projection. `resources/runtime/cbcc/delivery_export_continuity.py` runs this parity audit **before re-zipping**. Validation never rewrites corrupted fields or hides missing content; it blocks export and returns the work to the responsible authoring layer.

The 2026-10-31 v0.6.69 K01 package is a frozen semantic negative fixture for this release: the known G08/V01/A01/A02/S01/S02/R01/L01/T01/T02 positional-shift family and the observed Human HTML omissions must no longer pass FULL materialization.

All mature rules remain active: Product Truth four-way+A/B/C, P0 compliance, Economics input integrity, open Asset Universe, independent Product Presence/Fidelity, integrated native product/copy render, full people/scene/camera/light/CMF/material/typography Art Direction, four production objects, Provider/Review/Revision boundary and project-authored `cbcc-commercial-v1` interaction model.
'''.strip()


def _normalize_identity(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', f'version: {AUTHORITY_VERSION}', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', f'# Cross-Border Commerce Creative v{VERSION}', text, count=1)
    return text


def current_v069_floor() -> str:
    text = previous.canonical_skill()
    data = text.encode('utf-8')
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != V0669_FLOOR_BYTES or digest != V0669_FLOOR_SHA256:
        raise RuntimeError(
            f'v0.6.69 frozen Skill floor drift: bytes={len(data)} sha256={digest}; '
            f'expected bytes={V0669_FLOOR_BYTES} sha256={V0669_FLOOR_SHA256}'
        )
    return text


def canonical_skill(version: str = VERSION) -> str:
    text = _normalize_identity(current_v069_floor())
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.69 frozen Skill floor lost FULL-depth marker')
    if '## 0.19 Canonical Materialization + Human Projection Parity' not in text:
        text = text.replace(marker, '\n' + V0670_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(VERSION)


def copy_repo_resources(dest: Path) -> None:
    BASE_COPY_REPO_RESOURCES(dest)
    skill = canonical_skill(VERSION)
    (dest / 'SKILL.md').write_text(skill, encoding='utf-8')
    (dest / 'VERSION').write_text(AUTHORITY_VERSION + '\n', encoding='utf-8')


def openai_yaml() -> str:
    return '''interface:\n  display_name: Cross-Border Commerce Creative\n  short_description: Canonical Art Direction→Prompt单源、HTML完整投影与语义防串位的跨境Commerce Agent\npolicy:\n  allow_implicit_invocation: true\n'''


def plugin_manifest(version: str) -> dict:
    manifest = BASE_PLUGIN_MANIFEST(VERSION)
    manifest['version'] = VERSION
    manifest['description'] = (
        'Cross-border ecommerce Commerce Agent with frozen v0.6.69 maturity floor plus canonical Art Direction→CN/EN Prompt lineage, '
        'semantic field-shift blocking, complete Human Workspace projection and strategy/culture execution completion.'
    )
    dc = manifest.setdefault('delivery_contract', {})
    dc.update({
        'v069_exact_skill_floor_required': True,
        'canonical_named_art_direction_required': True,
        'asset_semantic_domain_guard_required': True,
        'visible_copy_language_slot_guard_required': True,
        'prompt_cn_en_single_canonical_lineage_required': True,
        'human_projection_field_consumption_required': True,
        'listing_en_description_keypoints_attributes_package_faq_human_visible_when_authored': True,
        'content_matrix_full_platform_execution_human_visible': True,
        'race_platform_required': True,
        'culture_script_casting_wardrobe_color_cta_result_modification_required': True,
        'output_self_check_six_dimensions_required': True,
        'inclusive_dimension_relevance_decisions_required': True,
        'copy_behavior_must_be_bound': True,
        'workspace_search_business_object_scope_required': True,
        'canonical_materialization_audit_before_final_zip': True,
        'fresh_host_k01_full_still_required_for_behavioral_closure': True,
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
    release['release'] = 'v0.6.70 Canonical Materialization + Human Projection Parity'
    release['authority_version'] = AUTHORITY_VERSION
    release.setdefault('delivery_contract', {}).update(plugin_manifest(VERSION).get('delivery_contract') or {})
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.70 additively from the exact verified v0.6.69 Skill floor.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0670'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
