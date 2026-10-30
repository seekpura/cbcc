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

VERSION = '0.6.69'
AUTHORITY_VERSION = '0.6.69-strategy-culture-materialization-closure'
V0666_FLOOR_BYTES = 40612
V0666_FLOOR_SHA256 = 'c9ac4577e38ef50cdfc033fae08f96f8b3d749583de89d360f35d390f684e06a'
V0667_FLOOR_BYTES = 43534
V0667_FLOOR_SHA256 = '5840e24d590c075e5682336fb76c9a0b38655486a4d17bf3bdec8bb60cfe4fa5'
V0668_FLOOR_BYTES = 45014
V0668_FLOOR_SHA256 = '4c244d58fb4289fe9f32a38ea0eef9fbb974c9c6ac2a39b7f01618a65cea913d'

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

V0669_PATCH = r'''
## 0.18 Strategy / Culture / Execution First-Class Materialization — v0.6.69
The v0.6.68 release is the frozen mature capability floor. This release is additive: existing Asset Universe, integrated native render, Product Presence/Fidelity, Art Direction, Prompt, production packages, routed Human Workspace and release-proof behavior remain unchanged while strategy/culture/execution requirements become first-class Runtime and Human-delivery objects instead of hidden fields or prose-only rules.

For FULL strategy, `resources/runtime/cbcc/strategy_culture_materialization.py` must materialize and audit the following structured objects before Human delivery:
- `product_truth_audit_table`: 真实卖点 / 可感知利益 / 情绪价值 / 不可宣称项 + A/B/C + source/basis/tradeoff/publication rule. **C级不得作硬宣称**; C is subjective/pending only.
- `assumption_decision_log`: facts/claims, assumptions and decisions remain distinguishable with status, basis and tradeoff.
- `intersectionality_table`: race/ethnicity × gender × age × income × geography with evidence-or-assumption, stereotype guard and execution consequence.
- `framework_relationships`: RACE is the process backbone; STP/JTBD shape strategy; AIDA/FABE shape content when relevant; 4P/Funnel shape conversion decisions. Every framework row carries role + basis + tradeoff + execution rather than definitions alone.
- `visual_execution_checklist`: style/moodboard/composition/HEX+contrast/light/lens/shot/camera/scene/props/casting/wardrobe/platform dimensions plus deep-skin Prelight-dependent exposure protection, reflector/diffusion and hair/body/disability/age/AI-bias checks.
- platform Content Matrix: dimensions/duration/cover/subtitles/music rights/traffic mechanism/CTA/landing/UTM-attribution + RACE stage + culture/taboo validation + WHY; unknown current platform mechanics remain TO_VERIFY.
- `RACE传播框架执行表`: Research/Action/Communication/Evaluation with objective/actions/output/platform/culture check/KPI/WHY.
- `族裔文化适配检查表`: adaptation point, evidence/assumption, inclusive representation, stereotype/taboo risk, script/casting/wardrobe-grooming/color/CTA checks, result, modification and WHY.
- explicit `P0 / P1 / P2` resource tradeoff rows: what to keep, cut/defer, why and restore condition; “all of it” is not a tradeoff.
- `output_self_check_rows`: fabrication / WHY / culture / compliance / metric / assumption, each with status, basis and action.

P0 claim/compliance remains separate for efficacy, ingredients/formula, certifications, price, sales volume and regulated category. Regional localization continues to cover language/back-translation, holidays, payment/logistics, religion/taboos and current local law; unknown external facts remain TO_VERIFY and must not be invented.

Human Workspace remains project-authored/routed rather than nine fixed pages. The same first-class objects must be visible in Chinese-first Human surfaces/tables; file existence or hidden JSON does not count as integration. FULL audit must reject missing/shallow materialization, and the CURRENT final ZIP checker must require the materialization Runtime and bootstrap bindings.

Fresh positive Host-native K01 FULL remains required separately because an already-open Host snapshot may remain stale. Real Provider Result / actual media / Review / smallest Revision / provenance-hash evidence stays E2E-boundary evidence, not inferred from strategy materialization.
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
        raise RuntimeError(f'v0.6.67 floor drift: bytes={len(data)} sha256={digest}')
    return text


def current_v068_floor() -> str:
    text = _normalize_identity(current_v067_floor(), '0.6.68', '0.6.68-packaged-override-release-proof')
    marker = '\n## 1. FULL depth remains mandatory'
    if '## 0.17 Packaged CURRENT Override Release-Family Proof' not in text:
        text = text.replace(marker, '\n' + V0668_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    data = text.encode('utf-8'); digest = hashlib.sha256(data).hexdigest()
    if len(data) != V0668_FLOOR_BYTES or digest != V0668_FLOOR_SHA256:
        raise RuntimeError(
            f'v0.6.68 frozen Skill floor drift: bytes={len(data)} sha256={digest}; '
            f'expected bytes={V0668_FLOOR_BYTES} sha256={V0668_FLOOR_SHA256}'
        )
    return text


def canonical_skill(version: str = VERSION) -> str:
    text = _normalize_identity(current_v068_floor(), VERSION, AUTHORITY_VERSION)
    marker = '\n## 1. FULL depth remains mandatory'
    if '## 0.18 Strategy / Culture / Execution First-Class Materialization' not in text:
        text = text.replace(marker, '\n' + V0669_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
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
    return '''interface:\n  display_name: Cross-Border Commerce Creative\n  short_description: 0.6.68成熟基线之上固化策略/文化/RACE/执行表为一等交付对象\npolicy:\n  allow_implicit_invocation: true\n'''


def plugin_manifest(version: str) -> dict:
    manifest = BASE_PLUGIN_MANIFEST(version)
    manifest['version'] = VERSION
    manifest['description'] = (
        'Cross-border ecommerce Commerce Agent with frozen v0.6.68 maturity floor plus first-class '
        'Product Truth, strategy WHY, culture/intersectionality, RACE, execution, tradeoff and self-check materialization.'
    )
    manifest['keywords'] = ['ecommerce','cross-border','commerce-agent','strategy','listing','pricing','economics','creative','photography','production','ads','reviews','culture','RACE','html-delivery']
    interface = manifest['extensions']['com.openai']['interface']; interface.pop('defaultPrompt', None)
    interface['displayName'] = 'Cross-Border Commerce Creative'
    interface['shortDescription'] = '策略/文化/RACE/执行锁成为Runtime与Human一等对象；0.6.68成熟能力冻结保留'
    interface['longDescription'] = (
        'v0.6.69 在经验证的0.6.68成熟能力地板上加法闭合：产品事实四分法+A/B/C、平台/区域/人群/文化WHY、'
        '交叉性、包容摄影、平台执行、本地化、RACE/STP/JTBD/AIDA/FABE/4P关系、P0/P1/P2资源取舍、'
        '族裔文化适配表与输出前自检均成为结构化Runtime对象并进入中文Human交付；最终ZIP同时检查Runtime和bootstrap绑定。'
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
    release['release'] = 'v0.6.69 Strategy / Culture / Execution First-Class Materialization'
    release['authority_version'] = AUTHORITY_VERSION
    release.setdefault('delivery_contract', {}).update({
        'frozen_v0668_maturity_floor_required': True,
        'frozen_v0668_skill_floor_bytes': V0668_FLOOR_BYTES,
        'frozen_v0668_skill_floor_sha256': V0668_FLOOR_SHA256,
        'product_truth_four_way_first_class_materialization': True,
        'c_grade_hard_claim_forbidden': True,
        'platform_region_audience_culture_why_first_class': True,
        'intersectionality_first_class': True,
        'inclusive_photography_p0_first_class': True,
        'platform_execution_and_localization_first_class': True,
        'race_framework_execution_first_class': True,
        'culture_adaptation_table_first_class': True,
        'p0_p1_p2_tradeoff_first_class': True,
        'output_self_check_first_class': True,
        'strategy_culture_materialization_runtime_required': True,
        'strategy_culture_bootstrap_binding_required': True,
        'strict_req_001_060_effective_map_required': True,
        'current_builder_target_matches_VERSION': True,
        'packaged_current_override_release_family_must_match': True,
        'exact_verified_artifact_required_before_install': True,
        'host_skill_snapshot_parity_required_for_positive_e2e': True,
        'fresh_positive_k01_full_e2e_still_required': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.69 from the exact frozen v0.6.68 Skill floor plus first-class strategy/culture materialization.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0669'))
    args = parser.parse_args(); build(Path(args.output_dir).resolve()); return 0


if __name__ == '__main__':
    raise SystemExit(main())
