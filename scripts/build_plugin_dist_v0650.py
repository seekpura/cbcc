#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0642 as v0642
from scripts import build_plugin_dist_v0649 as v0649

ROOT = Path(__file__).resolve().parents[1]
SURFACE_AUTHORITY = (ROOT / 'prompts/human_surface_rendering_media_portability_authority.md').read_text(encoding='utf-8').strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.50-human-surface-media-portability', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.50', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = v0649.canonical_skill(version)
    text = _normalize_version(text)
    text = v0642._inject(text, SURFACE_AUTHORITY)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0649.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.50'), encoding='utf-8')


def openai_yaml() -> str:
    return v0649.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0649.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '中文实际渲染工作台 + 目标市场资产语言/英文生产层/中文释义 + 自包含媒体交付'
    interface['longDescription'] = (
        '基础策略、研究、决策、视觉策划、资产详情与运营工作台必须在最终实际渲染表面中文优先；'
        '目标市场资产语言按逐资产策展决定，每个生产资产保留英文层，所有外文同对象提供中文释义。'
        'index.html 必须可独立查看并自包含实际展示媒体，不得仅依赖相对 sources 路径。'
        '继续保留 v0.6.49 语言连续性、v0.6.48 九域硬合同以及成熟商业/创意能力。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.50 Human Surface Language + Standalone Media Portability'
    release['authority_version'] = '0.6.50-human-surface-media-portability'
    release.setdefault('delivery_contract', {}).update({
        'rendered_operator_surface_chinese_first': True,
        'presence_only_language_audit_forbidden': True,
        'same_object_chinese_companion_required': True,
        'english_asset_layer_required': True,
        'model_prompt_en_provider_readable_english': True,
        'standalone_html_media_self_contained_required': True,
        'relative_local_media_without_embedded_fallback_forbidden': True,
        'human_surface_validator': 'scripts/check_v0650_human_surface_media.py',
        'v0649_language_contract_preserved': True,
        'v0648_final_package_hard_rules_preserved': True,
        'mature_commercial_creative_capabilities_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.50 human-surface/media-portability release.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0650'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
