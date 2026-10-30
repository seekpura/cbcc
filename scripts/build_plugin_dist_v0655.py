#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0654 as v0654

ROOT = Path(__file__).resolve().parents[1]
OPEN_WORLD_CONTRACT = (ROOT / 'references' / 'ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md').read_text(encoding='utf-8').strip()
DYNAMIC_CURATION = (ROOT / 'prompts' / 'dynamic_asset_curation.md').read_text(encoding='utf-8').strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.55-open-world-asset-universe', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.55', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0654.canonical_skill(version))
    header = '''\n## 0.4 OPEN-WORLD ASSET UNIVERSE — candidate universe before activation pruning\n\nFor every FULL project, `resources/references/ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md` and the current `resources/prompts/dynamic_asset_curation.md` are mandatory. The Agent must build the complete commercially justified Asset Opportunity Universe before choosing platform-constrained Activation Sets. Do not optimize the universe for `smallest sufficient`, `fewest assets possible`, 7/9/10 gallery slots, or any other implicit top-N target.\n\nSeparate three objects: Asset Opportunity Universe; Production Portfolio; Activation Set(s). Relevant Gallery/Hero, Benefit/Proof, Scenario/Lifestyle, How-to/Comparison, A+/PDP, Paid, Social, Creator/UGC, Video/LIVE, Store/Banner, Lifecycle and Test/Rotation/A-B opportunities are inspected as 0..N families. A relevant family may be absent only with explicit NOT_NEEDED / TO_VERIFY / MISSING_INPUT + WHY.\n\nMultiple assets may answer the same shopper question on the same surface when they embody distinct creative, evidence, audience/culture, offer/CTA, product-presence, scene/action, visual-mechanism, copy-hierarchy or motion hypotheses. Platform capacity constrains only the current simultaneous Live/Activation Set and never total candidate generation.\n'''
    return text + header + '\n\n' + OPEN_WORLD_CONTRACT + '\n'


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0654.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.55'), encoding='utf-8')
    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md').write_text(OPEN_WORLD_CONTRACT + '\n', encoding='utf-8')
    prompts = dest / 'prompts'
    prompts.mkdir(parents=True, exist_ok=True)
    (prompts / 'dynamic_asset_curation.md').write_text(DYNAMIC_CURATION + '\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0654.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0654.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '开放式资产宇宙：先完整展开场景/A+/广告/A-B/视频等候选，再按平台槽位选 Live Set'
    interface['longDescription'] = (
        '在 v0.6.54 成熟工作台与 Prompt 连续性基础上，修复资产宇宙被“最少够用”思想隐性压缩的问题。'
        'FULL 项目先构建完整 Asset Opportunity Universe，再形成 Production Portfolio 与平台受限 Activation Set。'
        'Gallery/Hero、Benefit/Proof、Scenario/Lifestyle、How-to/Comparison、A+/PDP、Paid、Social、Creator/UGC、Video/LIVE、Store/Banner、Lifecycle、Test/Rotation/A-B 均按相关性 0..N 动态展开；'
        '平台 7/9/10 图只限制同时上线集合，不限制总候选、测试、广告、A+、场景或视频资产。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0654.v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.55 Open-World Asset Opportunity Universe'
    release['authority_version'] = '0.6.55-open-world-asset-universe'
    release.setdefault('delivery_contract', {}).update({
        'asset_universe_open_world_contract_required': True,
        'asset_universe_open_world_contract_path': 'references/ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md',
        'dynamic_asset_curation_open_world_required': True,
        'asset_opportunity_universe_before_activation_required': True,
        'production_portfolio_separate_from_activation_set': True,
        'platform_capacity_activation_only': True,
        'minimum_asset_optimization_forbidden': True,
        'fixed_asset_count_forbidden': True,
        'relevant_family_opportunity_sweep_required': True,
        'silent_family_omission_forbidden': True,
        'same_question_distinct_ab_hypotheses_preserved': True,
        'paid_a_plus_scenario_social_creator_video_test_rotation_not_gallery_capped': True,
        'v0654_workspace_prompt_continuity_preserved': True,
        'v0653_business_object_density_preserved': True,
        'v0652_master_construction_preserved': True,
        'mature_commercial_creative_capabilities_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.55 open-world asset universe release.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0655'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
