#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0655 as v0655

ROOT = Path(__file__).resolve().parents[1]

SOURCE_LOCK = (ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').read_text(encoding='utf-8').strip()
MEMBRANE_CONTRACT = (ROOT / 'references' / 'MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md').read_text(encoding='utf-8').strip()
CANONICAL_MAP = (ROOT / 'prompts' / 'canonical_authority_loading_map.md').read_text(encoding='utf-8').strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.58-full-art-direction-end-to-end-lock', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.58', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0655.canonical_skill(version))
    source_lock = '''\n## 0.5 SOURCE REQUIREMENT NON-REGRESSION LOCK — reread original authorities before release changes\n\nBefore any update that touches strategy, asset curation, Art Direction, Prompt, production, language, Human Workspace or runtime, load `resources/references/SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md` and reread the master authorities it names. A local bug fix is invalid if it deletes or compresses another established capability.\n'''
    full_art = '''\n## 0.6 FULL ART DIRECTION END-TO-END LOCK — people / scene / photography / CMF cannot disappear\n\nFor every production-ready visual/video asset, preserve the complete already-authored commercial world through the actual public compiler: consumer decision and WHY; subject/person/casting; action and decisive moment; scene/environment/props; visual carrier; product role/presence/fidelity; composition/spatial geometry/scale/depth/focal path/negative space; evidence; exact visible copy/type/localization; culture/inclusion; CMF/material/color; camera/lens/working distance/camera height/yaw/pitch/roll/focus/DOF/aperture/shutter/ISO when photographic grammar is selected; key/fill/negative/rim/modifier/CCT/WB/light ratio/reflection/polarization/prelight; finishing; surface/output; and motion/audio for video.\n\nThe runtime first normalizes equivalent Art Direction shapes without inventing missing choices, then compiles the full model-native prompt. Semantic membrane cleanup occurs only at the final public prompt boundary and is clause-level: it may remove Excel/source-authority, internal IDs, provider workflow, QA labels and repair routing, but it may never delete neighboring pixel/frame-changing instructions. Concrete values such as `1.2m`, `85mm`, `f/8`, `5200K`, `2:1`, casting details, scene actions and material behavior are regression fixtures.\n\n`QA / Review / smallest repair` remain separate objects after generation; they are not deleted from the project merely because they are removed from Model Prompt.\n'''
    return text + source_lock + full_art + '\n'


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0655.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.58'), encoding='utf-8')

    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').write_text(SOURCE_LOCK + '\n', encoding='utf-8')
    (refs / 'MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md').write_text(MEMBRANE_CONTRACT + '\n', encoding='utf-8')

    prompts = dest / 'prompts'
    prompts.mkdir(parents=True, exist_ok=True)
    (prompts / 'canonical_authority_loading_map.md').write_text(CANONICAL_MAP + '\n', encoding='utf-8')

    runtime = dest / 'runtime' / 'cbcc'
    runtime.mkdir(parents=True, exist_ok=True)
    for name in [
        'full_art_direction_preservation.py',
        'model_prompt_semantic_membrane.py',
        'photographic_route_agent_authority.py',
        'commercial_continuity_bootstrap.py',
    ]:
        (runtime / name).write_text((ROOT / 'runtime' / 'cbcc' / name).read_text(encoding='utf-8'), encoding='utf-8')

    scripts = dest / 'scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / 'check_v0658_art_direction_end_to_end.py').write_text(
        (ROOT / 'scripts' / 'check_v0658_art_direction_end_to_end.py').read_text(encoding='utf-8'),
        encoding='utf-8',
    )
    (dest / 'VERSION').write_text('0.6.58-full-art-direction-end-to-end-lock\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0655.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0655.plugin_manifest(version)
    manifest['version'] = '0.6.58'
    manifest['description'] = 'Cross-border ecommerce Commerce Agent with full Art Direction end-to-end preservation, final model-prompt semantic separation, open-world assets, business depth and mature workspace continuity.'
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '完整 Art Direction 端到端保留：人物/场景/摄影/灯光/CMF 不因 Prompt 清洗丢失'
    interface['longDescription'] = (
        'v0.6.58 强制每次升级先读取源需求锁；逐资产人物、动作、场景、道具、构图、证据、文案、文化、CMF、材质、摄影、灯光、finishing 与视频动态继续进入生产。'
        'Runtime 在入口归一化完整 Art Direction，在最终公共 Prompt 出口才做语义隔离；Excel/真源层级/QA/最小修复链退出 Model Prompt，但不得连带删除 85mm、1.2m、5200K、人物动作、场景与材质等真实生成参数。'
        '继续保留开放式 Asset Universe、完整业务对象密度、中文优先 routed Human Workspace 与 Prompt CN/EN。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0655.v0654.v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.58 Full Art Direction End-to-End Lock'
    release['authority_version'] = '0.6.58-full-art-direction-end-to-end-lock'
    release.setdefault('delivery_contract', {}).update({
        'source_requirement_non_regression_lock_required': True,
        'master_contracts_reread_before_release_change': True,
        'full_art_direction_normalization_before_compilation': True,
        'people_scene_props_preserved_to_model_prompt_when_relevant': True,
        'photography_camera_light_cmf_selected_values_preserved': True,
        'semantic_membrane_clause_level_not_line_drop': True,
        'semantic_membrane_final_public_prompt_boundary': True,
        'qa_review_revision_separate_but_preserved': True,
        'decimal_and_concrete_parameter_values_regression_locked': True,
        'v0655_open_world_asset_universe_preserved': True,
        'v0654_workspace_prompt_continuity_preserved': True,
        'v0653_business_object_density_preserved': True,
        'v0652_master_construction_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.58 full Art Direction end-to-end release.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0658'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
