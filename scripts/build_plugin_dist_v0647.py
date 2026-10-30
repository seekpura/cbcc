#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0642 as v0642
from scripts import build_plugin_dist_v0646 as v0646

ROOT = Path(__file__).resolve().parents[1]
FULL_MATERIALIZATION_AUTHORITY = (ROOT / 'prompts/full_delivery_materialization_authority.md').read_text(encoding='utf-8').strip()
AUTHORITY_LOADING_MAP = (ROOT / 'prompts/canonical_authority_loading_map.md').read_text(encoding='utf-8').strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.47-full-delivery-depth-recovery', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.47', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = v0646.canonical_skill(version)
    text = _normalize_version(text)
    text = v0642._inject(text, FULL_MATERIALIZATION_AUTHORITY)
    # v0646 captured the loading-map file at import time. Re-inject the current v0.6.47 map so the
    # current FULL authority set is visible even when an older map section remains for history.
    text = v0642._inject(text, AUTHORITY_LOADING_MAP)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    base.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.47'), encoding='utf-8')


def openai_yaml() -> str:
    return '''interface:
  display_name: Cross-Border Commerce Creative
  short_description: 跨境电商商业级全链路策略、策展、资产生产与完整交付
policy:
  allow_implicit_invocation: true
'''


def plugin_manifest(version: str) -> dict:
    manifest = v0646.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '商业级跨境电商策略、深度研究、创意资产宇宙与完整运营交付'
    interface['longDescription'] = (
        'FULL 项目保持 Product Truth、Market/Region/Audience/Culture、Pricing/Economics/Offer、RACE、'
        'Listing/Search、Visual/Photography、Image/Video/Ads/Social/PDP/A+ Asset Universe、Reviews、Measurement 的完整连续性。'
        'v0.6.47 强制 Host-native 与 Runtime Export 同一文件/深度/语言合同，禁止九图裁剪、标题式假完成和外文无中文释义。'
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
    release['release'] = 'v0.6.47 FULL Commercial Depth & Host Materialization Recovery'
    release['authority_version'] = '0.6.47-full-delivery-depth-recovery'
    release.setdefault('delivery_contract', {}).update({
        'host_native_full_materialization_equals_runtime_export': True,
        'full_depth_v3_not_heading_boolean_presence': True,
        'market_region_audience_culture_dimension_matrix_required': True,
        'intersectionality_localization_religion_holiday_payment_logistics_regulation_explicit': True,
        'resource_tradeoff_required': True,
        'english_platform_primary_chinese_companion_required': True,
        'model_prompt_en_language_purity_required': True,
        'asset_universe_export_required': True,
        'activation_capacity_never_prunes_asset_universe': True,
        'active_video_paid_social_test_objects_must_materialize': True,
        'machine_authorities_and_supporting_analysis_preserved': True,
        'per_asset_design_card_depth_required': True,
        'portfolio_template_overreuse_audited': True,
        'v0646_commercial_decision_lineage_preserved': True,
        'v0645_workspace_platform_language_source_media_preserved': True,
        'v0642_routed_workspace_and_activation_boundary_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.47 FULL commercial-depth recovery release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0647'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
