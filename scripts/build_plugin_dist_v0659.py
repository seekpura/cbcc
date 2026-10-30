#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0658 as v0658

ROOT = Path(__file__).resolve().parents[1]
PARITY_LOCK = (ROOT / 'references' / 'AUTHORITY_SOURCE_PARITY_LOCK.md').read_text(encoding='utf-8').strip()
SOURCE_LOCK = (ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').read_text(encoding='utf-8').strip()
VALIDATOR = ROOT / 'scripts' / 'check_v0659_authority_source_parity.py'


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.59-authority-source-parity-lock', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.59', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0658.canonical_skill(version))
    header = '''\n## 0.7 AUTHORITY SOURCE PARITY LOCK — current Skill must be identical in both packaged locations\n\n`resources/references/AUTHORITY_SOURCE_PARITY_LOCK.md` is mandatory. The current packaged top-level `SKILL.md` and packaged `resources/SKILL.md` must be the same current canonical authority, not a current wrapper plus a stale historical deep Skill. `plugin.json`, both Skill front-matter versions and `resources/VERSION` must identify the same release family.\n\nGitHub root `SKILL.md` is retained as a mature baseline source layer used in additive construction; it is not sufficient evidence of current release authority by itself. The latest release builder must overwrite the copied baseline inside packaged resources with the current generated canonical Skill. After installation, re-read both Skill paths from the actual plugin before claiming release parity.\n\nThis packaging/source-resolution rule cannot simplify the authority content. People/subject/action/scene/props, composition/evidence/copy/culture, camera/lighting/CMF/material/finishing, Video/Creator/LIVE, open-world Asset Universe, business-object density and mature routed Human Workspace remain additive requirements.\n'''
    return text + header + '\n\n' + PARITY_LOCK + '\n'


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0658.copy_repo_resources(dest)
    # Critical: overwrite the copied mature baseline with the exact current canonical Skill.
    current = canonical_skill('0.6.59')
    (dest / 'SKILL.md').write_text(current, encoding='utf-8')
    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'AUTHORITY_SOURCE_PARITY_LOCK.md').write_text(PARITY_LOCK + '\n', encoding='utf-8')
    (refs / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').write_text(SOURCE_LOCK + '\n', encoding='utf-8')
    scripts = dest / 'scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / VALIDATOR.name).write_text(VALIDATOR.read_text(encoding='utf-8'), encoding='utf-8')
    (dest / 'VERSION').write_text('0.6.59-authority-source-parity-lock\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0658.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0658.plugin_manifest(version)
    manifest['version'] = '0.6.59'
    manifest['description'] = 'Cross-border ecommerce Commerce Agent with current-authority source parity, full Art Direction end-to-end preservation, open-world assets, full business depth and mature workspace continuity.'
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '权威源一致性锁：当前 Skill / resources Skill / VERSION 同版，完整能力更新前强制读源需求'
    interface['longDescription'] = (
        'v0.6.59 修复实际安装包中顶层 Skill 已更新但 resources/SKILL.md 仍旧版的权威歧义。'
        '当前 canonical Skill 同时写入顶层与 resources；plugin manifest、两处 Skill、resources/VERSION 必须同一版本家族，安装后重新读取验证。'
        '继续保留 v0.6.58 完整 Art Direction：人物、场景、道具、构图、文案、文化、摄影、灯光、CMF、材质、finishing、Video/Creator/LIVE；'
        '继续保留开放式 Asset Universe、完整业务对象密度和 cbcc-commercial-v1 routed Human Workspace。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    # Reuse the whole additive builder chain; only add source-parity enforcement.
    base = v0658.v0655.v0654.v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.59 Authority Source Parity Lock'
    release['authority_version'] = '0.6.59-authority-source-parity-lock'
    release.setdefault('delivery_contract', {}).update({
        'authority_source_parity_lock_required': True,
        'top_skill_equals_resources_skill': True,
        'plugin_skill_version_family_equals_resources_version': True,
        'latest_builder_overwrites_copied_baseline_skill': True,
        'installed_plugin_authority_parity_recheck_required': True,
        'source_requirement_non_regression_lock_preserved': True,
        'v0658_full_art_direction_end_to_end_preserved': True,
        'v0655_open_world_asset_universe_preserved': True,
        'v0654_workspace_prompt_continuity_preserved': True,
        'v0653_business_object_density_preserved': True,
        'v0652_master_construction_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.59 authority source parity release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0659'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
