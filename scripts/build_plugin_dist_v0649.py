#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0642 as v0642
from scripts import build_plugin_dist_v0648 as v0648

ROOT = Path(__file__).resolve().parents[1]
LANGUAGE_AUTHORITY = (ROOT / 'prompts/human_language_asset_continuity_authority.md').read_text(encoding='utf-8').strip()
FINAL_ZIP_LOCK = (ROOT / 'prompts/full_delivery_final_zip_hard_rule_lock.md').read_text(encoding='utf-8').strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.49-chinese-base-asset-language-continuity', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.49', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = v0648.canonical_skill(version)
    text = _normalize_version(text)
    text = v0642._inject(text, LANGUAGE_AUTHORITY)
    text = v0642._inject(text, FINAL_ZIP_LOCK)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0648.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.49'), encoding='utf-8')


def openai_yaml() -> str:
    return v0648.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0648.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '中文运营底座 + 目标市场资产语言 + 英文生产层 + 中文释义的跨境电商全链路 Agent'
    interface['longDescription'] = (
        '基础策略、研究、决策与运营工作台中文优先；资产最终可见语言由平台/市场/人群/策划逐资产决定，'
        '但每个生产资产必须保留英文层，所有非中文人类可见内容必须同对象提供中文翻译或用途说明。'
        '继续保留 Product Truth A/B/C、九域、RACE、文化交叉性、Pricing/Economics、Listing、Asset Universe、'
        'Visual/Video/Ads/Reviews、Host-native parity、最终真实包验收与 cbcc-commercial-v1。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.49 Chinese Base + Asset Language Continuity Restore'
    release['authority_version'] = '0.6.49-chinese-base-asset-language-continuity'
    release.setdefault('delivery_contract', {}).update({
        'chinese_base_operator_content_required': True,
        'asset_visible_language_authored_per_asset': True,
        'english_layer_required_per_asset': True,
        'non_chinese_same_object_chinese_companion_required': True,
        'english_layer_does_not_force_visible_english': True,
        'target_non_english_requires_target_plus_english_baseline_plus_chinese': True,
        'target_english_requires_english_plus_chinese': True,
        'model_prompt_cn_and_en_required_for_production_assets': True,
        'visible_copy_block_preserves_exact_target_locale': True,
        'listing_operator_labels_chinese_first': True,
        'v0648_final_package_hard_rules_preserved': True,
        'v0647_host_runtime_parity_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.49 Chinese-base + asset-language-continuity release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0649'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
