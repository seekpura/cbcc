#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0652 as v0652

ROOT = Path(__file__).resolve().parents[1]
BUSINESS_DENSITY_CONTRACT = (ROOT / 'references' / 'BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md').read_text(encoding='utf-8').strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.53-full-business-object-density', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.53', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = v0652.canonical_skill(version)
    text = _normalize_version(text)
    header = '''\n## 0.2 BUSINESS OBJECT DENSITY MASTER CONTRACT — global, not prompt-only\n\nFor every FULL project, `resources/references/BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md` is mandatory authority. It applies to Product Truth, Research, Market/Audience/Culture, Intersectionality, Strategy/Frameworks, Pricing/Economics/Offer, Listing/Search, Content Matrix, Visual Master, Asset Universe, Art Direction, Prompt/Production, Video/Creator/LIVE, Advertising Optimization, Review Analysis, RACE, Localization, Compliance/Risk, Measurement/A-B, Evidence/Sources, Operations and Human Workspace.\n\nNo module may be reduced to headings, summary cards, generic bullets or a few conclusions merely because another dimension was repaired. Chinese-canonical rendering, prompt cleanup, compliance, UI simplification and media portability must preserve full business-object depth.\n'''
    return text + header + '\n\n' + BUSINESS_DENSITY_CONTRACT + '\n'


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0652.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.53'), encoding='utf-8')
    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md').write_text(BUSINESS_DENSITY_CONTRACT + '\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0652.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0652.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '全业务对象密度锁：中文、策略、Listing、视觉、资产、Prompt、视频、经济、广告、评论全部只加不减'
    interface['longDescription'] = (
        '以 MASTER CONSTRUCTION、BUSINESS OBJECT DENSITY、PROMPT/ART DIRECTION 三层母合同锁定 FULL 项目。'
        'Product Truth、Research、市场人群文化、交叉性、Strategy/Frameworks、Pricing/Economics/Offer、Listing/Search、Content Matrix、'
        'Visual Master、Asset Universe、逐资产 Art Direction、Prompt/Production、Video/Creator/LIVE、Ads、Reviews、RACE、本地化、合规、'
        'Measurement、Evidence、Operations 与中文 Human Workspace 都必须保留真实业务深度；任何修复不得把另一模块压成摘要、卡片或几句结论。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    # Preserve the entire v0.6.52 builder chain and add only the new global density layer.
    base = v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.53 Full Business Object Density Non-Regression'
    release['authority_version'] = '0.6.53-full-business-object-density'
    release.setdefault('delivery_contract', {}).update({
        'business_object_density_contract_required': True,
        'business_object_density_contract_path': 'references/BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md',
        'all_business_domains_non_regression_required': True,
        'summary_collapse_forbidden': True,
        'strategy_framework_density_required': True,
        'pricing_economics_offer_density_required': True,
        'listing_search_density_required': True,
        'content_matrix_execution_density_required': True,
        'visual_master_density_required': True,
        'asset_art_direction_density_required': True,
        'prompt_production_density_required': True,
        'video_creator_live_density_required': True,
        'ads_reviews_density_required': True,
        'race_localization_compliance_measurement_density_required': True,
        'evidence_operations_workspace_density_required': True,
        'v0652_master_construction_preserved': True,
        'v0651_chinese_canonical_preserved': True,
        'mature_capability_ledger_preserved': True,
        'mature_commercial_creative_capabilities_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.53 full business-object density release.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0653'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
