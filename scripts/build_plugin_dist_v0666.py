#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist as base

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'references' / 'CURRENT_PACKAGED_SKILL_BASELINE_V0665.md'
BUILD_AUTHORITY = ROOT / 'references' / 'CURRENT_CANONICAL_SKILL_BUILD_V0666.md'
CONSUMER_MAP = ROOT / 'references' / 'REQUIREMENT_CONSUMER_MAP_V0664.json'
CURRENT_MATRIX = ROOT / 'references' / 'REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md'
SOURCE_LOCK = ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md'
HOST_SNAPSHOT_LOCK = ROOT / 'references' / 'HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md'
LOADING_ADDENDUM = ROOT / 'prompts' / 'canonical_authority_loading_map_v0665_addendum.md'
CONSUMER_CHECKER = ROOT / 'scripts' / 'check_v0664_requirement_consumer_map.py'

# Freeze all original non-versioned builder functions before monkey-patching. These immutable
# references prevent the release customizations from recursively calling themselves.
BASE_COPY_REPO_RESOURCES = base.copy_repo_resources
BASE_PLUGIN_MANIFEST = base.plugin_manifest

PATCH = r'''
## 0.15 Strict Requirement Consumer Accounting + Current Baseline Build — v0.6.66
Every cumulative requirement is now accounted for through a concrete implementation map, not a generic “relevant Runtime consumer” statement. Load `resources/references/REQUIREMENT_CONSUMER_MAP_V0664.json` as the machine-level authority for REQ-001..060. Each row names concrete existing Consumer path(s), concrete downstream proof object(s), and an explicit evidence status. `resources/scripts/check_v0664_requirement_consumer_map.py` must report exactly 60 requirements and zero issues before release publication. The human `REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md` is a summary and cannot override the strict map.

Installed-plugin parity and active Host Skill snapshot parity are separate evidence. Load `resources/references/HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md`. If an already-open Host context still resolves an older Skill after the plugin has been updated, record `HOST_SKILL_SNAPSHOT_STALE`; that context cannot supply positive FULL E2E proof for the new release.

Current release construction no longer recursively regenerates the canonical Skill through historical v0.6.62/v0.6.59 builder markers. `resources/references/CURRENT_CANONICAL_SKILL_BUILD_V0666.md` defines the construction path: the BOM-normalized decoded text of the installed v0.6.65 packaged Skill is the additive textual floor; current GitHub resources are copied directly by the non-versioned base builder; the resulting current Skill is written byte-identically to top and deep Skill locations. Historical builders remain provenance only.

This build change does not weaken business Runtime. All prior requirements remain active: detailed/verbatim long requirements; Product Truth four-way+A/B/C; platform/region/audience/culture WHY; six-area P0 compliance; intersectionality and inclusive photography; platform/localization/UTM; seven tools; pricing/economics input integrity; open 12-family Asset Universe; structured Product Presence; integrated native product/copy render; complete structured Art Direction and concrete Prompt consumption; mature asset packages/four production objects; real K01 17-class negative-fixture rejection; project-authored routed workspace; and real Provider/Review/Revision/QA completion boundaries.

Fresh positive K01 FULL through a Host context that actually loaded the current installed Skill remains required before behavioral closure.
'''.strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.66-strict-consumer-current-baseline-build', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.66', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(BASELINE.read_text(encoding='utf-8'))
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('current packaged v0.6.65 Skill baseline lost FULL-depth marker')
    if '## 0.15 Strict Requirement Consumer Accounting + Current Baseline Build' not in text:
        text = text.replace(marker, '\n' + PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    # Deliberately use only the frozen non-versioned current-repository copier. Historical versioned
    # builders remain provenance and are not allowed to regenerate the current Skill authority.
    BASE_COPY_REPO_RESOURCES(dest)
    current = canonical_skill('0.6.66')
    (dest / 'SKILL.md').write_text(current, encoding='utf-8')
    (dest / 'VERSION').write_text('0.6.66-strict-consumer-current-baseline-build\n', encoding='utf-8')

    # Explicitly overwrite current authorities so the release cannot accidentally package a stale
    # same-named copy if source layout changes later.
    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    for src in (BUILD_AUTHORITY, CONSUMER_MAP, CURRENT_MATRIX, SOURCE_LOCK, HOST_SNAPSHOT_LOCK):
        (refs / src.name).write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
    prompts = dest / 'prompts'
    prompts.mkdir(parents=True, exist_ok=True)
    (prompts / LOADING_ADDENDUM.name).write_text(LOADING_ADDENDUM.read_text(encoding='utf-8'), encoding='utf-8')
    scripts = dest / 'scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / CONSUMER_CHECKER.name).write_text(CONSUMER_CHECKER.read_text(encoding='utf-8'), encoding='utf-8')


def openai_yaml() -> str:
    return '''interface:
  display_name: Cross-Border Commerce Creative
  short_description: 60条需求逐条绑定具体Consumer/Proof，当前Skill从installed成熟基线加法构建
policy:
  allow_implicit_invocation: true
'''


def plugin_manifest(version: str) -> dict:
    manifest = BASE_PLUGIN_MANIFEST(version)
    manifest['version'] = '0.6.66'
    manifest['description'] = 'Cross-border ecommerce Commerce Agent with strict REQ-001..060 consumer/proof accounting, current packaged Skill baseline construction, Host snapshot parity, integrated native render, full Art Direction and mature FULL delivery.'
    manifest['keywords'] = [
        'ecommerce','cross-border','commerce-agent','strategy','listing','pricing','economics',
        'creative','photography','production','ads','reviews','culture','RACE','html-delivery'
    ]
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['displayName'] = 'Cross-Border Commerce Creative'
    interface['shortDescription'] = '60条需求一一绑定具体Consumer/Proof；current Skill脱离历史marker链构建'
    interface['longDescription'] = (
        'v0.6.66 将REQ-001..060全部绑定到具体存在的Consumer与Proof Object，并由严格checker要求60/60、0缺口。'
        '当前canonical Skill直接以实际installed v0.6.65成熟Skill的BOM-normalized文本为加法基线，不再递归依赖v0.6.62等历史builder marker。'
        '继续保留累计/原文长要求、七工具、Economics完整性、开放资产宇宙、逐资产Product Presence、一体最终成图、完整Art Direction、'
        '成熟asset_packages、真实K01 17类阻断、项目作者化Workspace以及Provider/Review/Revision/真实输出QA完成边界。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    # Monkey-patch only the non-versioned base builder for this process. No historical versioned
    # canonical_skill/copy_repo_resources function is imported or called.
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    release = base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.66 Strict Consumer Accounting + Current Baseline Build'
    release['authority_version'] = '0.6.66-strict-consumer-current-baseline-build'
    release.setdefault('delivery_contract', {}).update({
        'strict_req_001_060_consumer_map_required': True,
        'strict_consumer_map_60_of_60_zero_issues_required': True,
        'generic_consumer_placeholders_forbidden': True,
        'current_packaged_skill_baseline_required': True,
        'historical_canonical_builder_chain_for_current_skill_forbidden': True,
        'top_skill_equals_resources_skill': True,
        'host_skill_snapshot_parity_required_for_positive_e2e': True,
        'real_k01_17_structural_negative_fixture_preserved': True,
        'four_production_objects_preserved': True,
        'fresh_positive_k01_full_e2e_still_required': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.66 from the current packaged Skill baseline without historical canonical builder recursion.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0666'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
