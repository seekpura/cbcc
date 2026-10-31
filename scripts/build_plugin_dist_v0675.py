#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0674 as previous

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.6.75'
AUTHORITY_VERSION = '0.6.75-formal-full-package-identity-closure'
V0674_FLOOR_BYTES = 71400
V0674_FLOOR_SHA256 = '8d5e62a0486c83712b61c31010b83b7bc59af0439e7546ba02f48627caecefc8'

BASE_COPY_REPO_RESOURCES = base.copy_repo_resources
BASE_PLUGIN_MANIFEST = previous.plugin_manifest

V0675_PATCH = r'''
## 0.24 Formal Full-Package Identity Closure — v0.6.75
v0.6.74 is the exact verified cross-scope regression capability floor. This release introduces **no new commerce, strategy, creative, Listing, Prompt, media, Provider or Human Workspace behavior**. Its only purpose is to publish the already-verified v0.6.74 capability set as one complete installable plugin release after an earlier partial overlay consumed the 0.6.74 semantic version in the host release history.

### Exact v0.6.74 floor is immutable
The canonical v0.6.74 Skill must reconstruct to exactly **71,400 UTF-8 bytes / SHA256 `8d5e62a0486c83712b61c31010b83b7bc59af0439e7546ba02f48627caecefc8`** before v0.6.75 identity normalization is permitted. This preserves every cumulative authority through v0.6.74, including the v0.6.70 semantic/Human fixes, v0.6.71 full package lineage, v0.6.72 fresh-K01 runtime projection closure, v0.6.73 bilingual business-object/model-prompt consumption, and v0.6.74 cross-scope regression closure.

### Complete-package installation is the release object
The release artifact must be the full plugin ZIP produced by the CURRENT builder, not an incremental overlay ZIP. Manifest version, both canonical Skills, `resources/VERSION`, CURRENT builder target and CURRENT requirement override must all identify v0.6.75. The exact ZIP must pass CURRENT checks plus cumulative v0.6.70→v0.6.74 floor checks before installation.

### No behavioral rebase
All v0.6.74 runtime behavior remains unchanged: FULL alias semantics, explicit platform/market/locale precedence, visible-copy locale replacement, Listing three-state lifecycle, escaped Markdown pipe handling, YAML no-anchor serialization, Source Ledger materialization, Prompt provenance-only cleanup and cached-consumer rebinding. Mature Product Truth, seven commerce tools, Pricing/Economics, open Asset Universe, Product Presence, full Art Direction, integrated rendering, bilingual production objects, 00–15 package lineage and `cbcc-commercial-v1` remain additive and intact.

### Evidence boundary
Installed readback must prove the full v0.6.75 identity after update. Fresh real K01 FULL against the exact `KIYUU_5款产品信息_纯粹版(7).xlsx` remains required for behavioral closure because release/package verification cannot substitute for the real product-truth run. Provider Result / actual media / pixel-frame Review / smallest Local Revision / provenance remain `E2E_PENDING` until genuinely produced.
'''.strip()


def _normalize_identity(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', f'version: {AUTHORITY_VERSION}', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', f'# Cross-Border Commerce Creative v{VERSION}', text, count=1)
    return text


def current_v0674_floor() -> str:
    text = previous.canonical_skill()
    data = text.encode('utf-8')
    if len(data) != V0674_FLOOR_BYTES:
        raise RuntimeError(f'v0.6.74 Skill floor drift: bytes={len(data)} expected={V0674_FLOOR_BYTES}')
    digest = hashlib.sha256(data).hexdigest()
    print(json.dumps({'v0674_skill_floor_bytes': len(data), 'v0674_skill_floor_sha256': digest}, ensure_ascii=False))
    if digest != V0674_FLOOR_SHA256:
        raise RuntimeError(f'v0.6.74 Skill floor drift: sha256={digest} expected={V0674_FLOOR_SHA256}')
    for token in (
        '## 0.23 Cross-Scope Regression Closure',
        '## 0.22 Bilingual Business-Object Delivery + Model Prompt Consumption Closure',
        '## 0.21 Fresh K01 Runtime Projection Closure',
        '## 0.20 Full Canonical Human + Package Lineage Parity',
        '## 0.19 Canonical Materialization + Human Projection Parity',
        '## 1. FULL depth remains mandatory',
    ):
        if token not in text:
            raise RuntimeError(f'v0.6.74 Skill floor lost marker: {token}')
    return text


def canonical_skill(version: str = VERSION) -> str:
    text = _normalize_identity(current_v0674_floor())
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.74 Skill floor lost FULL-depth marker')
    if '## 0.24 Formal Full-Package Identity Closure' not in text:
        text = text.replace(marker, '\n' + V0675_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(VERSION)


def copy_repo_resources(dest: Path) -> None:
    BASE_COPY_REPO_RESOURCES(dest)
    skill = canonical_skill(VERSION)
    (dest / 'SKILL.md').write_text(skill, encoding='utf-8')
    (dest / 'VERSION').write_text(AUTHORITY_VERSION + '\n', encoding='utf-8')


def openai_yaml() -> str:
    return '''interface:\n  display_name: Cross-Border Commerce Creative\n  short_description: 0.6.75完整发布v0.6.74已验证能力并闭合安装身份\npolicy:\n  allow_implicit_invocation: true\n'''


def plugin_manifest(version: str) -> dict:
    manifest = BASE_PLUGIN_MANIFEST(VERSION)
    manifest['version'] = VERSION
    manifest['description'] = (
        'Cross-border ecommerce Commerce Agent preserving all verified v0.6.69–v0.6.74 capabilities, '
        'with v0.6.75 formal full-package identity closure for exact complete-release installation.'
    )
    manifest.setdefault('delivery_contract', {})['v075_verified_full_package_identity_closure_required'] = True
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
    release['release'] = 'v0.6.75 Formal Full-Package Identity Closure'
    release['authority_version'] = AUTHORITY_VERSION
    release.setdefault('delivery_contract', {}).update(plugin_manifest(VERSION).get('delivery_contract') or {})
    release['v0675_evidence_boundary'] = {
        'v0674_exact_skill_floor': {'bytes': V0674_FLOOR_BYTES, 'sha256': V0674_FLOOR_SHA256},
        'business_runtime_delta_from_v0674': 'NONE',
        'full_verified_plugin_zip_required': True,
        'fresh_k01_full_after_install': 'REQUIRED_FOR_BEHAVIORAL_CLOSURE',
        'provider_actual_media': 'E2E_PENDING_UNTIL_REAL_PROVIDER_OUTPUT',
    }
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.75 additively from the exact verified v0.6.74 Skill floor.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0675'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
