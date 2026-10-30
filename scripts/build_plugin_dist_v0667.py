#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from scripts import build_plugin_dist as base

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'references' / 'CURRENT_PACKAGED_SKILL_BASELINE_V0665.md'
CURRENT_BUILD_AUTHORITY = ROOT / 'references' / 'CURRENT_CANONICAL_SKILL_BUILD.md'
CONSUMER_MAP = ROOT / 'references' / 'REQUIREMENT_CONSUMER_MAP_V0664.json'
CURRENT_OVERRIDES = ROOT / 'references' / 'REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json'
CURRENT_MATRIX = ROOT / 'references' / 'REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md'
SOURCE_LOCK = ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md'
HOST_SNAPSHOT_LOCK = ROOT / 'references' / 'HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md'
CURRENT_LOADING_MAP = ROOT / 'prompts' / 'canonical_authority_loading_map_CURRENT.md'
CURRENT_BUILDER = ROOT / 'scripts' / 'build_plugin_dist_current.py'
CONSUMER_CHECKER = ROOT / 'scripts' / 'check_v0664_requirement_consumer_map.py'
CURRENT_PACKAGE_CHECKER = ROOT / 'scripts' / 'check_current_release_package.py'

VERSION = '0.6.67'
AUTHORITY_VERSION = '0.6.67-current-release-freshness-architecture'
V0666_FLOOR_BYTES = 40612
V0666_FLOOR_SHA256 = 'c9ac4577e38ef50cdfc033fae08f96f8b3d749583de89d360f35d390f684e06a'

BASE_COPY_REPO_RESOURCES = base.copy_repo_resources
BASE_PLUGIN_MANIFEST = base.plugin_manifest

V0666_PATCH = r'''
## 0.15 Strict Requirement Consumer Accounting + Current Baseline Build — v0.6.66
Every cumulative requirement is now accounted for through a concrete implementation map, not a generic “relevant Runtime consumer” statement. Load `resources/references/REQUIREMENT_CONSUMER_MAP_V0664.json` as the machine-level authority for REQ-001..060. Each row names concrete existing Consumer path(s), concrete downstream proof object(s), and an explicit evidence status. `resources/scripts/check_v0664_requirement_consumer_map.py` must report exactly 60 requirements and zero issues before release publication. The human `REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md` is a summary and cannot override the strict map.

Installed-plugin parity and active Host Skill snapshot parity are separate evidence. Load `resources/references/HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md`. If an already-open Host context still resolves an older Skill after the plugin has been updated, record `HOST_SKILL_SNAPSHOT_STALE`; that context cannot supply positive FULL E2E proof for the new release.

Current release construction no longer recursively regenerates the canonical Skill through historical v0.6.62/v0.6.59 builder markers. `resources/references/CURRENT_CANONICAL_SKILL_BUILD_V0666.md` defines the construction path: the BOM-normalized decoded text of the installed v0.6.65 packaged Skill is the additive textual floor; current GitHub resources are copied directly by the non-versioned base builder; the resulting current Skill is written byte-identically to top and deep Skill locations. Historical builders remain provenance only.

This build change does not weaken business Runtime. All prior requirements remain active: detailed/verbatim long requirements; Product Truth four-way+A/B/C; platform/region/audience/culture WHY; six-area P0 compliance; intersectionality and inclusive photography; platform/localization/UTM; seven tools; pricing/economics input integrity; open 12-family Asset Universe; structured Product Presence; integrated native product/copy render; complete structured Art Direction and concrete Prompt consumption; mature asset packages/four production objects; real K01 17-class negative-fixture rejection; project-authored routed workspace; and real Provider/Review/Revision/QA completion boundaries.

Fresh positive K01 FULL through a Host context that actually loaded the current installed Skill remains required before behavioral closure.
'''.strip()

V0667_PATCH = r'''
## 0.16 CURRENT Release Freshness Architecture — v0.6.67
`CURRENT` is now a machine-enforced release layer rather than a filename convention. The effective REQ-001..060 authority is the historical complete base `resources/references/REQUIREMENT_CONSUMER_MAP_V0664.json` plus the release-process overrides in `resources/references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json`. The CURRENT override file must declare the same semantic release family as `resources/VERSION`, and its REQ-046/047/048 rows must use release-agnostic statuses and concrete CURRENT consumers. A stale historical status such as `INSTALLED_PARITY_PROVED_0663` is a release failure even when all paths still exist.

Current release construction and proof use stable entrypoints:
- `resources/scripts/build_plugin_dist_current.py` — CURRENT builder launcher; its `CURRENT_BUILDER_TARGET` must match the semantic family in `resources/VERSION`;
- `resources/scripts/check_v0664_requirement_consumer_map.py` — effective 60-row Consumer/Proof/freshness checker;
- `resources/scripts/check_current_release_package.py` — version-agnostic final ZIP checker derived from CURRENT `VERSION` rather than a hard-coded historical version;
- `resources/references/CURRENT_CANONICAL_SKILL_BUILD.md` and `resources/prompts/canonical_authority_loading_map_CURRENT.md` — stable CURRENT construction/loading authorities.

Versioned builders and workflows remain historical provenance and regression evidence. They do not define the health of a later CURRENT release. The current release pipeline must build through the stable CURRENT builder, validate the exact produced ZIP through the stable CURRENT package checker, record SHA256/bytes, and upload that exact verified artifact before installation.

The v0.6.67 Skill is additive over the exact verified v0.6.66 packaged Skill floor. Release construction must first reconstruct that floor to 40,612 UTF-8 bytes and SHA256 `c9ac4577e38ef50cdfc033fae08f96f8b3d749583de89d360f35d390f684e06a`; any mismatch blocks the build. This protects the mature Product Truth, seven tools, Economics, open Asset Universe, per-asset Product Presence, integrated native render, full Art Direction, complete camera/lighting/CMF/material/people/scene/copy/culture execution, four production objects, K01 shortcut audit and routed Human Workspace from being lost while release plumbing changes.

Installed-plugin parity and active Host Skill snapshot parity remain separate evidence. An already-open conversation that still resolves an older Skill is `HOST_SKILL_SNAPSHOT_STALE` and cannot prove the new release by positive Host-native FULL execution.

Fresh positive K01 FULL through a Host context that actually loaded the current installed Skill remains required before behavioral closure. Real Provider Result / actual media / Review / smallest Revision / provenance-hash evidence remains `E2E_PENDING` until it exists.
'''.strip()


def _normalize_identity(text: str, version: str, authority: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', f'version: {authority}', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', f'# Cross-Border Commerce Creative v{version}', text, count=1)
    return text


def current_v0666_floor() -> str:
    """Reconstruct and prove the exact verified installed/CI v0.6.66 Skill floor without importing a versioned builder."""
    text = _normalize_identity(
        BASELINE.read_text(encoding='utf-8'),
        '0.6.66',
        '0.6.66-strict-consumer-current-baseline-build',
    )
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.65 packaged baseline lost FULL-depth marker')
    if '## 0.15 Strict Requirement Consumer Accounting + Current Baseline Build' not in text:
        text = text.replace(marker, '\n' + V0666_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)

    data = text.encode('utf-8')
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != V0666_FLOOR_BYTES or digest != V0666_FLOOR_SHA256:
        raise RuntimeError(
            f'v0.6.66 verified Skill floor drift: bytes={len(data)} sha256={digest}; '
            f'expected bytes={V0666_FLOOR_BYTES} sha256={V0666_FLOOR_SHA256}'
        )
    return text


def canonical_skill(version: str = VERSION) -> str:
    text = _normalize_identity(current_v0666_floor(), VERSION, AUTHORITY_VERSION)
    marker = '\n## 1. FULL depth remains mandatory'
    if '## 0.16 CURRENT Release Freshness Architecture' not in text:
        text = text.replace(marker, '\n' + V0667_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(VERSION)


def copy_repo_resources(dest: Path) -> None:
    BASE_COPY_REPO_RESOURCES(dest)
    skill = canonical_skill(VERSION)
    (dest / 'SKILL.md').write_text(skill, encoding='utf-8')
    (dest / 'VERSION').write_text(AUTHORITY_VERSION + '\n', encoding='utf-8')

    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    for src in (
        CURRENT_BUILD_AUTHORITY,
        CONSUMER_MAP,
        CURRENT_OVERRIDES,
        CURRENT_MATRIX,
        SOURCE_LOCK,
        HOST_SNAPSHOT_LOCK,
    ):
        (refs / src.name).write_text(src.read_text(encoding='utf-8'), encoding='utf-8')

    prompts = dest / 'prompts'
    prompts.mkdir(parents=True, exist_ok=True)
    (prompts / CURRENT_LOADING_MAP.name).write_text(CURRENT_LOADING_MAP.read_text(encoding='utf-8'), encoding='utf-8')

    scripts = dest / 'scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    for src in (CURRENT_BUILDER, CONSUMER_CHECKER, CURRENT_PACKAGE_CHECKER):
        (scripts / src.name).write_text(src.read_text(encoding='utf-8'), encoding='utf-8')


def openai_yaml() -> str:
    return '''interface:\n  display_name: Cross-Border Commerce Creative\n  short_description: CURRENT发布链版本新鲜度强校验；60条需求继续逐条绑定真实Consumer/Proof\npolicy:\n  allow_implicit_invocation: true\n'''


def plugin_manifest(version: str) -> dict:
    manifest = BASE_PLUGIN_MANIFEST(version)
    manifest['version'] = VERSION
    manifest['description'] = (
        'Cross-border ecommerce Commerce Agent with CURRENT release-freshness architecture, strict '
        'REQ-001..060 consumer/proof accounting, integrated native render, full Art Direction and mature FULL delivery.'
    )
    manifest['keywords'] = [
        'ecommerce','cross-border','commerce-agent','strategy','listing','pricing','economics',
        'creative','photography','production','ads','reviews','culture','RACE','html-delivery'
    ]
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['displayName'] = 'Cross-Border Commerce Creative'
    interface['shortDescription'] = 'CURRENT发布链动态校验；版本/Builder/Override/Package Proof必须同一release family'
    interface['longDescription'] = (
        'v0.6.67 将CURRENT从命名约定升级为机器校验的发布层：VERSION、CURRENT builder、CURRENT requirement override、'
        '最终包检查和exact artifact proof必须同一release family；历史versioned workflow仅作溯源。业务Runtime继续完整保留：'
        '60条需求Consumer/Proof、七工具、Economics、开放资产宇宙、逐资产Product Presence、一体最终成图、完整Art Direction、'
        '成熟asset_packages、真实K01 17类阻断、项目作者化Workspace与Provider/Review/Revision/真实输出QA完成边界。'
    )
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
    release['release'] = 'v0.6.67 CURRENT Release Freshness Architecture'
    release['authority_version'] = AUTHORITY_VERSION
    release.setdefault('delivery_contract', {}).update({
        'strict_req_001_060_effective_map_required': True,
        'current_override_release_version_matches_VERSION': True,
        'current_builder_target_matches_VERSION': True,
        'version_agnostic_current_package_checker_required': True,
        'exact_verified_artifact_required_before_install': True,
        'historical_versioned_workflow_not_current_authority': True,
        'verified_v0666_skill_floor_required': True,
        'verified_v0666_skill_floor_bytes': V0666_FLOOR_BYTES,
        'verified_v0666_skill_floor_sha256': V0666_FLOOR_SHA256,
        'host_skill_snapshot_parity_required_for_positive_e2e': True,
        'fresh_positive_k01_full_e2e_still_required': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.67 from the exact verified v0.6.66 Skill floor plus CURRENT release-freshness authority.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0667'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
