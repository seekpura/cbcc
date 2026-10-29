#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0642 as v0642
from scripts import build_plugin_dist_v0644 as v0644
from scripts import build_plugin_dist_v0645 as v0645

ROOT = Path(__file__).resolve().parents[1]
CONTINUITY_AUTHORITY = (ROOT / 'prompts/commercial_continuity_lineage_authority.md').read_text(encoding='utf-8').strip()
AUTHORITY_LOADING_MAP = (ROOT / 'prompts/canonical_authority_loading_map.md').read_text(encoding='utf-8').strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.46-commercial-continuity-lineage-recovery', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.46', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    """Build one complete Host/Canonical routing authority from the repository root truth.

    Capability preservation is proven by: current Host routing + mature specialist authorities + real
    downstream consumers. The builder keeps the mature root Skill and injects current precedence rules;
    it never replaces the Skill with a thin wrapper or a manifest default prompt.
    """
    text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    text = _normalize_version(text)
    for section in (
        v0642.RECOVERY_AUTHORITY,
        v0644.CHINESE_INTERPRETATION_AUTHORITY,
        v0644.AUTHORITY_BOUNDARY,
        v0645.AUTHORITY,
        CONTINUITY_AUTHORITY,
        AUTHORITY_LOADING_MAP,
    ):
        text = v0642._inject(text, section)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    base.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.46'), encoding='utf-8')


def openai_yaml() -> str:
    return '''interface:
  display_name: Cross-Border Commerce Creative
  short_description: 跨境电商策略、内容、创意、生产与商业连续性交付
policy:
  allow_implicit_invocation: true
'''


def plugin_manifest(version: str) -> dict:
    manifest = v0645.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '跨境电商全链路商业决策、创意生产与可追溯运营工作台'
    interface['longDescription'] = (
        '从 Product Truth、Market/Audience、Pricing/Economics/Offer、Strategy/RACE、Listing/Search、'
        'Visual/Photography、Image/Video Assets、Ads、Reviews 到 Measurement/Revision。v0.6.46 强制 Canonical 路由、'
        '成熟深度 authority 消费、Commerce Decision Context 与逐资产 Decision Lineage，使分析、策展、设计卡、Prompt 和中文优先 HTML 使用同一商业来源链。'
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
    release['release'] = 'v0.6.46 Commercial Continuity & Decision Lineage Recovery'
    release['authority_version'] = '0.6.46-commercial-continuity-lineage-recovery'
    release.setdefault('delivery_contract', {}).update({
        'full_root_canonical_is_packaged': True,
        'host_and_canonical_byte_identical': True,
        'mandatory_deep_authority_loading_map': True,
        'mature_specialist_authorities_preserved': True,
        'authority_preservation_requires_real_consumers': True,
        'commerce_decision_context_required': True,
        'per_asset_decision_lineage_required': True,
        'subject_presence_system_per_asset': True,
        'asset_universe_not_capped_by_activation_capacity': True,
        'market_pricing_audience_race_listing_ads_review_payload_preserved': True,
        'photography_parameter_closure_preserved': True,
        'commercial_intelligence_primary_html_surface': True,
        'status_count_summary_cannot_substitute_payload': True,
        'v0645_workspace_platform_language_source_media_preserved': True,
        'v0644_default_prompt_boundary_preserved': True,
        'v0642_asset_universe_and_routed_workspace_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.46 commercial-continuity release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0646'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
