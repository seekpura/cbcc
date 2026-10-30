#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0642 as v0642
from scripts import build_plugin_dist_v0650 as v0650

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = (ROOT / 'prompts/chinese_canonical_business_object_authority.md').read_text(encoding='utf-8').strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.51-chinese-canonical-business-objects', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.51', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = v0650.canonical_skill(version)
    text = _normalize_version(text)
    text = v0642._inject(text, AUTHORITY)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0650.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.51'), encoding='utf-8')


def openai_yaml() -> str:
    return v0650.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0650.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '全业务对象中文主层 + 目标市场资产语言 + 英文生产层 + 同对象中文释义 + 自包含媒体'
    interface['longDescription'] = (
        '项目、产品事实、市场与人群、交叉性、策略、框架、视觉摄影、资产详情、RACE、文化、本地化、合规、证据、执行与测试等所有运营对象以中文作为主层；'
        '目标市场 Listing/资产可见文案保留原文，并同对象提供英文语义基线（非英语市场）与中文释义。'
        '每个生产资产保留英文 Prompt；HTML 实际渲染必须中文可操作且媒体自包含。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.51 Chinese Canonical Business Objects'
    release['authority_version'] = '0.6.51-chinese-canonical-business-objects'
    release.setdefault('delivery_contract', {}).update({
        'global_operator_chinese_canonical': True,
        'field_whitelist_language_validation_forbidden': True,
        'explicit_foreign_first_zones_only': True,
        'same_object_chinese_companion_required': True,
        'model_prompt_en_provider_clean': True,
        'standalone_html_media_required': True,
        'human_surface_validator': 'scripts/check_v0651_chinese_canonical_surface.py',
        'v0650_surface_media_contract_preserved': True,
        'v0648_hard_rules_preserved': True,
        'mature_commercial_creative_capabilities_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.51 Chinese-canonical business-object release.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0651'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
