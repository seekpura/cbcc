#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0670 as previous

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.6.71'
AUTHORITY_VERSION = '0.6.71-full-canonical-human-package-lineage-parity'
V0670_FLOOR_BYTES = 54752

BASE_COPY_REPO_RESOURCES = base.copy_repo_resources
BASE_PLUGIN_MANIFEST = base.plugin_manifest

V0671_PATCH = r'''
## 0.20 Full Canonical Human + Package Lineage Parity — v0.6.71
v0.6.70 remains the additive capability floor. This release closes the remaining gaps from the real v0.6.69 K01 audit by making the **real final package**, not a synthetic `const DATA` fixture, the positive Human-delivery source and by extending canonical parity across Listing MD, the complete mature asset package and major decision context.

### Real final-package → Human Workspace positive projection
`resources/runtime/cbcc/canonical_full_parity_v0671.py` reconstructs the Human payload from final package authorities: `HUMAN_DELIVERY.json`, strategy authority, supporting analysis, Asset Universe and the materialized asset package directories. It writes `CANONICAL_HUMAN_DATA.json` and augments the existing routed workspace without replacing its information architecture.

The static projection exposes authored Listing, Product Truth, Strategy, Visual/Photography, Content/RACE/Culture/Ads and a complete Canonical Business Object archive. Every meaningful leaf under the preserved business authorities receives a `data-canonical-path` projection. `HTML_CANONICAL_GENERIC_FIELD_COVERAGE_INCOMPLETE_V0671` blocks export when a preserved canonical field silently disappears from Human HTML.

Workspace search and copy are behavioral: `CBCC_GLOBAL_SEARCH_INDEX_V0671` indexes the full canonical payload and visible controls call the browser clipboard API. The v0.6.70 projector remains available for compatible function-based worlds, but v0.6.71 no longer depends on an embedded synthetic `const DATA` object for final-package closure.

### Listing MD and HTML share the same Human Delivery authority
`resources/runtime/cbcc/listing_markdown_parity_v0671.py` positively materializes `HUMAN_DELIVERY.localized_copy` into `01_LISTING_UPLOAD_READY.md`, retaining target-market/English content and Chinese meaning/use. Final audit compares `copy_center` and `localized_copy` primitive values against Listing MD; a missing canonical value is `LISTING_MARKDOWN_CANONICAL_FIELD_DRIFT`.

### Complete mature asset package lineage
The mature asset package is the actual numbered 00–15 family, not only Prompt CN/EN + Design Card. `resources/runtime/cbcc/asset_package_full_lineage_v0671.py` creates `CANONICAL_LINEAGE.json` for every production asset and binds each present numbered artifact byte-for-byte to the same canonical Art Direction lineage. Visual Spec, Photography Contract, Layout Contract, Prompt CN/EN, Copy, Production Notes, Source Trace, Strategy Trace, Design Card, Prompt Contract, Visible Copy and Production Assembly Notes are independently human-reachable. Mutation, missing files, untracked numbered files or source-lineage drift block final export.

### Major decisions consume four-axis context; intersectionality analyzes interactions
`resources/runtime/cbcc/strategy_execution_completion_v0671.py` adds decision-specific context consumption for authored positioning, value proposition, message hierarchy, framework relationships, Listing strategy, visual/photography strategy, Content Matrix decisions and P0/P1/P2 resource tradeoffs. Every major row independently records platform / region / audience / race-ethnicity-culture WHY. Project-level context may be inherited only as a context requiring a decision-specific check; missing causal evidence remains `TO_VERIFY` rather than being promoted to a conclusion.

Intersectionality no longer passes merely because race/ethnicity, gender, age, income and geography appear in one row. The release materializes interaction-analysis rows with at least two dimensions plus mechanism, evidence/assumption, stereotype guard, execution and verification action. Identity combinations are verification programs, not invented behavioral claims.

### Per-human-asset and Typography relevance decisions
`resources/runtime/cbcc/asset_execution_relevance_v0671.py` makes people and typography decisions explicit. When people are present, hair, makeup/grooming, wardrobe, body representation, disability representation, pose, expression, gaze and religious/cultural presentation are each `SELECTED`, `TO_VERIFY` or `NOT_NEEDED` with WHY. Missing identity data must never be silently invented as selected.

When visible copy is present, the asset also closes or explicitly holds family/character, weight, hierarchy, line breaking, relative scale, alignment, contrast, safe zone, mobile-thumbnail legibility and relationship to product geometry. Assets with no visible copy may mark typography dimensions `NOT_NEEDED + WHY`.

### Final FULL package boundary
`resources/runtime/cbcc/canonical_full_package_audit_v0671.py` and `resources/runtime/cbcc/delivery_export_continuity.py` positively materialize Listing/Human parity first, then block the final ZIP on: real static Human coverage, Listing MD parity, complete asset lineage, major-decision context WHY, interaction analysis and human/typography relevance. v0.6.70 semantic field-shift, Visible Copy slot and Prompt lineage guards remain active underneath this boundary.

Fresh positive Host behavior is still separate evidence: after installing the exact verified v0.6.71 artifact, a fresh Host context must run the K01 FULL project. Provider Result / actual generated media / Review / Local Revision remain `E2E_PENDING` until they genuinely occur.
'''.strip()


def _normalize_identity(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', f'version: {AUTHORITY_VERSION}', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', f'# Cross-Border Commerce Creative v{VERSION}', text, count=1)
    return text


def current_v0670_floor() -> str:
    text = previous.canonical_skill()
    data = text.encode('utf-8')
    if len(data) != V0670_FLOOR_BYTES:
        raise RuntimeError(f'v0.6.70 Skill floor drift: bytes={len(data)} expected={V0670_FLOOR_BYTES}')
    for token in ('## 0.19 Canonical Materialization + Human Projection Parity', '## 1. FULL depth remains mandatory'):
        if token not in text:
            raise RuntimeError(f'v0.6.70 Skill floor lost marker: {token}')
    return text


def canonical_skill(version: str = VERSION) -> str:
    text = _normalize_identity(current_v0670_floor())
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.70 Skill floor lost FULL-depth marker')
    if '## 0.20 Full Canonical Human + Package Lineage Parity' not in text:
        text = text.replace(marker, '\n' + V0671_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(VERSION)


def copy_repo_resources(dest: Path) -> None:
    BASE_COPY_REPO_RESOURCES(dest)
    skill = canonical_skill(VERSION)
    (dest / 'SKILL.md').write_text(skill, encoding='utf-8')
    (dest / 'VERSION').write_text(AUTHORITY_VERSION + '\n', encoding='utf-8')


def openai_yaml() -> str:
    return '''interface:\n  display_name: Cross-Border Commerce Creative\n  short_description: 真实final package到Human、Listing与00–15资产全链同源的跨境Commerce Agent\npolicy:\n  allow_implicit_invocation: true\n'''


def plugin_manifest(version: str) -> dict:
    manifest = BASE_PLUGIN_MANIFEST(VERSION)
    manifest['version'] = VERSION
    manifest['description'] = (
        'Cross-border ecommerce Commerce Agent with frozen v0.6.69 maturity floor, v0.6.70 semantic/prompt parity, '
        'and v0.6.71 real final-package Human projection, multilingual Listing parity and full 00–15 asset lineage.'
    )
    dc = manifest.setdefault('delivery_contract', {})
    dc.update({
        'v069_exact_skill_floor_required': True,
        'v070_canonical_materialization_floor_required': True,
        'real_final_package_human_projection_required': True,
        'canonical_business_object_generic_field_coverage_required': True,
        'listing_markdown_multilingual_canonical_parity_required': True,
        'full_asset_package_00_15_lineage_required': True,
        'asset_visual_photography_layout_source_strategy_trace_human_visible': True,
        'major_decision_four_axis_context_why_required': True,
        'intersectionality_interaction_analysis_required': True,
        'human_asset_relevance_decisions_required': True,
        'typography_relevance_contract_required': True,
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
    release['release'] = 'v0.6.71 Full Canonical Human + Package Lineage Parity'
    release['authority_version'] = AUTHORITY_VERSION
    release.setdefault('delivery_contract', {}).update(plugin_manifest(VERSION).get('delivery_contract') or {})
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.71 additively from the verified v0.6.70 canonical Skill floor.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0671'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
