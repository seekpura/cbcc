#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def must(text: str, needles: list[str], label: str) -> None:
    missing = [x for x in needles if x not in text]
    if missing:
        raise SystemExit(f'{label} missing v0.6.46 contract: {missing}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('plugin_dir')
    args = ap.parse_args()
    root = Path(args.plugin_dir)
    manifest = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))
    if manifest.get('version') != '0.6.46':
        raise SystemExit(f'plugin version mismatch: {manifest.get("version")}')
    interface = manifest.get('extensions', {}).get('com.openai', {}).get('interface') or {}
    if interface.get('defaultPrompt'):
        raise SystemExit('manifest business-policy defaultPrompt must remain absent')

    skill_root = root / 'skills' / 'cross-border-commerce-creative'
    host_path = skill_root / 'SKILL.md'
    canonical_path = skill_root / 'resources' / 'SKILL.md'
    host = host_path.read_text(encoding='utf-8')
    canonical = canonical_path.read_text(encoding='utf-8')
    if host != canonical:
        raise SystemExit('Host Skill and Canonical Skill are not byte-identical')
    must(canonical, [
        'Commercial Continuity & Decision Lineage Authority',
        'CBCC Canonical Authority Loading Map',
        'Source → Analysis → Decision → Strategy → Curation → Asset',
        'Subject Presence System',
        'ANIMAL', 'PLANT', 'PRODUCT_OR_OBJECT', 'MULTI_SUBJECT',
        'Commercial Asset Universe',
        'Production Parameter Closure',
        'Pricing', 'Economics', 'RACE', 'Advertising Optimization', 'Review Analysis',
        'Asset Universe', 'cbcc-commercial-v1', 'English baseline',
    ], 'Canonical Skill')

    # Commercial depth is not a byte-count contest. Prove the Host routes into the mature specialist
    # authorities and that those authorities are present with their real production contracts.
    authority_files = {
        'resources/SKILL_AUTHORITY_v0.6.6.md': [
            'Seven first-class commerce tool contracts', 'Photography / CMF',
            'Asset package preservation — mandatory', 'RACE Research',
        ],
        'resources/prompts/canonical_authority_loading_map.md': [
            'FULL / end-to-end project mandatory authority set',
            'creative_direction_surface_prompt_compiler.md', 'dynamic_asset_curation.md',
        ],
        'resources/prompts/dynamic_asset_curation.md': [
            'There is no global target such as 6, 7, 9 or 12 assets',
            'subject / action / environment / props', 'Per-asset Art Direction contract',
        ],
        'resources/prompts/creative_direction_surface_prompt_compiler.md': [
            'lossless production-parameter closure', 'working distance', 'negative fill',
            'polarization', 'Prelight', 'Four distinct production objects',
        ],
        'resources/prompts/commercial_visual_generation_authority.md': [
            'Integrated native generation is the default', 'Actual-output commercial QA',
        ],
        'resources/prompts/commercial_delivery_stability_authority.md': [
            'CBCC Commercial Workspace Shell v1', 'English baseline', '平台、市场、主语言禁止历史污染',
        ],
        'resources/prompts/commercial_continuity_lineage_authority.md': [
            'Subject Presence System', 'Commercial Asset Universe', 'Decision Lineage',
        ],
    }
    for rel, needles in authority_files.items():
        path = skill_root / rel
        if not path.exists():
            raise SystemExit(f'missing mature authority: {rel}')
        must(path.read_text(encoding='utf-8'), needles, rel)

    openai_yaml = (skill_root / 'agents' / 'openai.yaml').read_text(encoding='utf-8')
    if 'default_prompt:' in openai_yaml:
        raise SystemExit('agents/openai.yaml regained a business default_prompt')

    runtime = skill_root / 'resources' / 'runtime' / 'cbcc'
    required = {
        'commerce_decision_context.py': ['compile_commerce_decision_context', 'bind_asset_decision_lineage', 'source_artifact'],
        'commercial_context_compatibility.py': ['market_price_bands', 'market_price_valleys', 'offer_bundle_discount_boundary'],
        'commercial_continuity_authority.py': ['wrap_compile_seven_agent_synthesis', 'wrap_compile_asset_prompt', 'COMMERCE DECISION CONTEXT'],
        'commercial_curation_lineage.py': ['CURATION_COMMERCIAL_DECISION_BASIS', 'decision_origin', 'wrap_compile_creative_council'],
        'subject_presence_authority.py': ['SUBJECT_TYPES', 'ANIMAL', 'PLANT', 'MULTI_SUBJECT', 'wrap_compile_asset_prompt'],
        'subject_agent_authority.py': ['SUBJECT_PRESENCE_SYSTEM', 'HOST_AGENT_PER_ASSET', 'wrap_apply_creative_system_to_assets'],
        'asset_portfolio_taxonomy.py': ['fixed_total_asset_limit', 'platform_capacity_is_activation_constraint_only', 'SOCIAL_SEEDING', 'CREATOR_UGC'],
        'asset_portfolio_workspace.py': ['商业资产宇宙', 'Activation Capacity', '平台 7/9 图'],
        'commercial_continuity_bootstrap.py': ['_INSTALLED', 'MODEL_PROMPT_NEEDS_COMMERCIAL_DECISION_CONSUMPTION', 'generation_blocking', 'wrap_human_asset_design_card'],
        'human_asset_commercial_projection.py': ['上游商业决策、主体系统与血缘', '主体系统（Subject Presence System）', '来源血缘', '摄影/灯光/CMF'],
        'commercial_intelligence_workspace.py': ['commercial-intelligence', '市场 / 区域 / 人群', '价格 / 经济模型 / Offer', 'BE ROAS', 'Decision Lineage / Evidence'],
        'commercial_delivery_continuity.py': ['materialize_commerce_decision_context', 'render_asset_portfolio_workspace', 'wrap_build_delivery_html', 'data-route="commerce"', '_install_commercial_continuity'],
        '__init__.py': ['commercial_continuity_authority', 'commercial_curation_lineage', 'subject_presence_authority', 'asset_portfolio_taxonomy', 'wrap_compile_seven_agent_synthesis'],
    }
    for name, needles in required.items():
        path = runtime / name
        if not path.exists():
            raise SystemExit(f'missing v0.6.46 runtime file: {name}')
        must(path.read_text(encoding='utf-8'), needles, name)

    for path in root.rglob('*'):
        if path.is_file() and (path.suffix in {'.pyc', '.pyo'} or '__pycache__' in path.parts):
            raise SystemExit(f'compiled cache leaked into plugin: {path.relative_to(root)}')

    print('v0.6.46 authority routing / commercial continuity / subject / asset-universe guard: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
