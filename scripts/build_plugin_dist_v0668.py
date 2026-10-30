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

VERSION = '0.6.68'
AUTHORITY_VERSION = '0.6.68-packaged-override-release-proof'
V0666_FLOOR_BYTES = 40612
V0666_FLOOR_SHA256 = 'c9ac4577e38ef50cdfc033fae08f96f8b3d749583de89d360f35d390f684e06a'
V0667_FLOOR_BYTES = 43534
V0667_FLOOR_SHA256 = '5840e24d590c075e5682336fb76c9a0b38655486a4d17bf3bdec8bb60cfe4fa5'

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

V0668_PATCH = r'''
## 0.17 Packaged CURRENT Override Release-Family Proof — v0.6.68
The final package checker now validates the release family declared **inside the packaged** `resources/references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json`, not only the repository source before build. `current_release_version` must equal the semantic family of the exact plugin ZIP being verified. Any mismatch or missing value is `PACKAGED_CURRENT_OVERRIDE_RELEASE_VERSION_MISMATCH` and blocks the artifact.

This closes a release-proof gap where repository freshness could be correct while a stale override file was accidentally copied into the final ZIP. The CURRENT release pipeline therefore proves all four identities at the package boundary: plugin manifest version, `resources/VERSION`, packaged CURRENT builder target, and packaged CURRENT override release family.

This is proof hardening only. All mature commercial Runtime remains additive and unchanged: Product Truth, seven tools, Economics, open Asset Universe, independent Product Presence/Fidelity, integrated native render, complete Art Direction with people/scene/camera/light/CMF/material/copy/culture, four production objects, K01 shortcut rejection, mature routed Human Workspace and actual Provider/Review/Revision completion boundaries.

Fresh positive K01 FULL through a Host context that actually loaded the current installed Skill remains required before behavioral closure. A stale Host snapshot remains `HOST_SKILL_SNAPSHOT_STALE`.
'''.strip()


def _normalize_identity(text: str, version: str, authority: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', f'version: {authority}', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', f'# Cross-Border Commerce Creative v{version}', text, count=1)
    return text


def current_v0666_floor() -> str:
    text = _normalize_identity(BASELINE.read_text(encoding='utf-8'), '0.6.66', '0.6.66-strict-consumer-current-baseline-build')
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.65 packaged baseline lost FULL-depth marker')
    if '## 0.15 Strict Requirement Consumer Accounting + Current Baseline Build' not in text:
        text = text.replace(marker, '\n' + V0666_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    data = text.encode('utf-8'); digest = hashlib.sha256(data).hexdigest()
    if len(data) != V0666_FLOOR_BYTES or digest != V0666_FLOOR_SHA256:
        raise RuntimeError(f'v0.6.66 floor drift: bytes={len(data)} sha256={digest}')
    return text


def current_v067_floor() -> str:
    text = _normalize_identity(current_v0666_floor(), '0.6.67', '0.6.67-current-release-freshness-architecture')
    marker = '\n## 1. FULL depth remains mandatory'
    if '## 0.16 CURRENT Release Freshness Architecture' not in text:
        text = text.replace(marker, '\n' + V0667_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    data = text.encode('utf-8'); digest = hashlib.sha256(data).hexdigest()
    if len(data) != V0667_FLOOR_BYTES or digest != V0667_FLOOR_SHA256:
        raise RuntimeError(
            f'v0.6.67 verified Skill floor drift: bytes={len(data)} sha256={digest}; '
            f'expected bytes={V0667_FLOOR_BYTES} sha256={V0667_FLOOR_SHA256}'
        )
    return text


def canonical_skill(version: str = VERSION) -> str:
    text = _normalize_identity(current_v067_floor(), VERSION, AUTHORITY_VERSION)
    marker = '\n## 1. FULL depth remains mandatory'
    if '## 0.17 Packaged CURRENT Override Release-Family Proof' not in text:
        text = text.replace(marker, '\n' + V0668_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(VERSION)


def copy_repo_resources(dest: Path) -> None:
    BASE_COPY_REPO_RESOURCES(dest)
    skill = canonical_skill(VERSION)
    (dest / 'SKILL.md').write_text(skill, encoding='utf-8')
    (dest / 'VERSION').write_text(AUTHORITY_VERSION + '\n', encoding='utf-8')
    refs = dest / 'references'; refs.mkdir(parents=True, exist_ok=True)
    for src in (CURRENT_BUILD_AUTHORITY, CONSUMER_MAP, CURRENT_OVERRIDES, CURRENT_MATRIX, SOURCE_LOCK, HOST_SNAPSHOT_LOCK):
        (refs / src.name).write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
    prompts = dest / 'prompts'; prompts.mkdir(parents=True, exist_ok=True)
    (prompts / CURRENT_LOADING_MAP.name).write_text(CURRENT_LOADING_MAP.read_text(encoding='utf-8'), encoding='utf-8')
    scripts = dest / 'scripts'; scripts.mkdir(parents=True, exist_ok=True)
    for src in (CURRENT_BUILDER, CONSUMER_CHECKER, CURRENT_PACKAGE_CHECKER):
        (scripts / src.name).write_text(src.read_text(encoding='utf-8'), encoding='utf-8')


def openai_yaml() -> str:
    return '''interface:\n  display_name: Cross-Border Commerce Creative\n  short_description: CURRENT最终包版本证明强化；60条需求与成熟商业Runtime继续完整保留\npolicy:\n  allow_implicit_invocation: true\n'''


def plugin_manifest(version: str) -> dict:
    manifest = BASE_PLUGIN_MANIFEST(version)
    manifest['version'] = VERSION
    manifest['description'] = 'Cross-border ecommerce Commerce Agent with packaged CURRENT release-family proof, strict REQ-001..060 accounting, integrated native render, full Art Direction and mature FULL delivery.'
    manifest['keywords'] = ['ecommerce','cross-border','commerce-agent','strategy','listing','pricing','economics','creative','photography','production','ads','reviews','culture','RACE','html-delivery']
    interface = manifest['extensions']['com.openai']['interface']; interface.pop('defaultPrompt', None)
    interface['displayName'] = 'Cross-Border Commerce Creative'
    interface['shortDescription'] = '最终ZIP直接校验CURRENT override release family；成熟商业Runtime保持加法连续'
    interface['longDescription'] = 'v0.6.68 将CURRENT override版本校验推进到最终ZIP边界：manifest、VERSION、CURRENT builder target、packaged override release family必须同版。业务Runtime保持0.6.67全部成熟能力，Fresh K01 FULL与真实Provider/Review仍按证据边界闭合。'
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
    release['release'] = 'v0.6.68 Packaged CURRENT Override Release-Family Proof'
    release['authority_version'] = AUTHORITY_VERSION
    release.setdefault('delivery_contract', {}).update({
        'packaged_current_override_release_family_must_match': True,
        'packaged_override_mismatch_code': 'PACKAGED_CURRENT_OVERRIDE_RELEASE_VERSION_MISMATCH',
        'strict_req_001_060_effective_map_required': True,
        'current_builder_target_matches_VERSION': True,
        'exact_verified_artifact_required_before_install': True,
        'verified_v0667_skill_floor_required': True,
        'verified_v0667_skill_floor_bytes': V0667_FLOOR_BYTES,
        'verified_v0667_skill_floor_sha256': V0667_FLOOR_SHA256,
        'host_skill_snapshot_parity_required_for_positive_e2e': True,
        'fresh_positive_k01_full_e2e_still_required': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.68 from the exact verified v0.6.67 Skill floor plus packaged CURRENT override proof.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0668'))
    args = parser.parse_args(); build(Path(args.output_dir).resolve()); return 0


if __name__ == '__main__':
    raise SystemExit(main())
