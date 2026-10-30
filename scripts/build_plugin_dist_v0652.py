#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0642 as v0642
from scripts import build_plugin_dist_v0651 as v0651

ROOT = Path(__file__).resolve().parents[1]
MASTER_CONTRACT = (ROOT / 'references' / 'MASTER_CONSTRUCTION_CONTRACT.md').read_text(encoding='utf-8').strip()
PROMPT_ART_DIRECTION_CONTRACT = (ROOT / 'references' / 'PROMPT_ART_DIRECTION_MASTER_CONTRACT.md').read_text(encoding='utf-8').strip()
NON_REGRESSION_MATRIX = (ROOT / 'references' / 'RELEASE_NON_REGRESSION_MATRIX.yaml').read_text(encoding='utf-8').strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.52-master-construction-nonregression', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.52', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = v0651.canonical_skill(version)
    text = _normalize_version(text)
    master_header = '''\n## 0.1 MASTER CONSTRUCTION CONTRACT — highest non-regression authority\n\nFor every FULL/end-to-end project and every release/repair, the complete `resources/references/MASTER_CONSTRUCTION_CONTRACT.md` is mandatory authority. It governs the whole system, not only prompts. A language, compliance, UI, media, validation or prompt repair may not reduce strategy depth, commercial density, visual/photography execution, Asset Universe, per-asset Art Direction, production parameters, Listing, Economics, Video/Creator/Ads/Reviews, or human workspace depth. `resources/references/PROMPT_ART_DIRECTION_MASTER_CONTRACT.md` is mandatory for every production-ready visual/video/creator asset and defines the complete authored world beyond photography parameters. `resources/references/RELEASE_NON_REGRESSION_MATRIX.yaml` defines the cross-dimension regressions that must remain forbidden.\n\nThe construction authorities below are included in Host authority so Host-native execution cannot silently skip them.\n'''
    text = text + master_header + '\n\n' + MASTER_CONTRACT + '\n\n' + PROMPT_ART_DIRECTION_CONTRACT + '\n'
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0651.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.52'), encoding='utf-8')
    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'MASTER_CONSTRUCTION_CONTRACT.md').write_text(MASTER_CONTRACT + '\n', encoding='utf-8')
    (refs / 'PROMPT_ART_DIRECTION_MASTER_CONTRACT.md').write_text(PROMPT_ART_DIRECTION_CONTRACT + '\n', encoding='utf-8')
    (refs / 'RELEASE_NON_REGRESSION_MATRIX.yaml').write_text(NON_REGRESSION_MATRIX + '\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0651.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0651.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '施工总纲锁定：中文不降密度，完整商业世界/人物/场景/元素/资产/Prompt/生产只加不减'
    interface['longDescription'] = (
        '以 MASTER CONSTRUCTION CONTRACT + PROMPT ART DIRECTION MASTER CONTRACT 作为 FULL 项目与后续升级的不可回退母合同。'
        '中文运营主层、Product Truth A/B/C、平台×区域×人群×族裔文化、交叉性、RACE、Pricing/Economics/Offer、Listing、'
        'Visual/Photography/CMF、人物/主体/动作/场景/元素/道具/空间/证据/文案/字体/文化/材质/动态、动态 Asset Universe、'
        '逐资产 Art Direction、Production Parameter Closure、商业级高密度 Model Prompt CN/EN、Visible Copy、Production Notes、'
        'Video/Creator/Ads/Reviews、cbcc-commercial-v1 与自包含 HTML 必须同时保留。任何修复不得通过压缩另一个维度来完成。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.52 Master Construction + Full Prompt Art Direction Non-Regression'
    release['authority_version'] = '0.6.52-master-construction-nonregression'
    release.setdefault('delivery_contract', {}).update({
        'master_construction_contract_required': True,
        'master_construction_contract_path': 'references/MASTER_CONSTRUCTION_CONTRACT.md',
        'prompt_art_direction_master_contract_required': True,
        'prompt_art_direction_master_contract_path': 'references/PROMPT_ART_DIRECTION_MASTER_CONTRACT.md',
        'release_non_regression_matrix_required': True,
        'commercial_density_non_regression_required': True,
        'prompt_and_art_direction_density_non_regression_required': True,
        'prompt_is_full_authored_commercial_world_not_camera_parameter_dump': True,
        'people_subject_action_scene_elements_props_spatial_evidence_typography_culture_material_motion_required_when_relevant': True,
        'strategy_and_nine_domain_depth_non_regression_required': True,
        'seven_first_class_tools_preserved': True,
        'dynamic_asset_universe_preserved': True,
        'production_parameter_closure_preserved': True,
        'cbcc_commercial_v1_preserved': True,
        'standalone_html_media_preserved': True,
        'v0651_chinese_canonical_preserved': True,
        'v0650_surface_media_preserved': True,
        'v0648_user_hard_rules_preserved': True,
        'mature_commercial_creative_capabilities_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.52 master construction non-regression release.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0652'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
