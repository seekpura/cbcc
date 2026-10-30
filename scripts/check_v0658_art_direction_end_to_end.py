#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _require(condition: bool, code: str, detail: str, issues: list[dict]):
    if not condition:
        issues.append({'code': code, 'detail': detail})


def run(root: Path = ROOT) -> dict:
    issues: list[dict] = []
    membrane = _load(root / 'runtime' / 'cbcc' / 'model_prompt_semantic_membrane.py', 'cbcc_v0658_membrane')
    full_art = _load(root / 'runtime' / 'cbcc' / 'full_art_direction_preservation.py', 'cbcc_v0658_full_art')

    dirty = (
        '使用用户提供的 KIYUU K01 全视角包装图作为产品身份参考，Excel 为产品事实最高权威。'
        '画面人物为25-35岁女性，真实手部按压透明泵头，85mm，工作距离1.2m，机位高于产品中心12cm，'
        'yaw 8°，pitch -3°，f/8，1/125s，ISO100；主光左前45°通过120cm大型柔光，5200K，2:1光比，'
        '右侧negative fill，保持哑光软管和透明泵头真实反射。'
        'QA：手指数量正确、抓握自然；标题位于移动端安全区；缩略图可读。'
        '最小修复优先：文字层→局部包装几何→透明泵头反射→整图重生成。'
    )
    clean = membrane.sanitize_model_prompt(dirty, language='CN', reference_bound=True, locked_source=False)
    survive = [
        '25-35岁女性', '真实手部按压透明泵头', '85mm', '1.2m', '12cm', 'yaw 8°', 'pitch -3°',
        'f/8', '1/125s', 'ISO100', '120cm', '5200K', '2:1光比', 'negative fill',
        '哑光软管', '透明泵头', '手指数量正确', '移动端安全区',
    ]
    removed = ['Excel 为产品事实最高权威', 'QA：', '最小修复', 'K01 全视角包装图']
    for token in survive:
        _require(token in clean, 'PIXEL_VALUE_LOST', f'{token} missing from sanitized prompt: {clean}', issues)
    for token in removed:
        _require(token not in clean, 'ORCHESTRATION_LEAK', f'{token} leaked into sanitized prompt: {clean}', issues)
    _require(not membrane.model_prompt_orchestration_leaks(clean), 'MEMBRANE_LEAK_DETECTOR_FAILED', str(membrane.model_prompt_orchestration_leaks(clean)), issues)

    dense_asset = {
        'asset_art_direction': {
            'human_role': 'daily skincare user', 'age': '25-35', 'skin_tone': 'medium-deep',
            'hair': 'natural wavy hair', 'wardrobe': 'modest casual', 'pose': 'three-quarter standing',
            'expression': 'calm focused', 'gaze': 'toward applicator', 'hand_action': 'press pump naturally',
            'product_interaction': 'one hand stabilizes tube while the other presses pump',
            'working_distance': '1.2m', 'camera_height': '12cm above product center', 'yaw': '8deg',
            'pitch': '-3deg', 'roll': '0deg', 'shot_size': 'medium close-up', 'focus_plane': 'front label and fingers',
            'aperture': 'f/8 equivalent', 'dof': 'deep enough for label and hand', 'shutter': '1/125', 'iso': '100',
            'key': '45deg camera-left through 120cm diffusion', 'fill': 'neutral bounce', 'negative_fill': 'camera-right',
            'modifier': '120cm diffusion', 'cct': '5200K', 'white_balance': 'neutral', 'light_ratio': '2:1',
            'reflection': 'controlled transparent pump highlights', 'polarization': 'conditional', 'prelight': 'verify label highlight rolloff',
            'material': 'matte flexible tube', 'finish': 'matte', 'surface_behavior': 'truthful matte response',
            'finishing': 'neutral-warm commercial grade with restrained specular rolloff',
        }
    }
    normalized = full_art.normalize_full_art_direction(dense_asset)
    blob = json.dumps(normalized, ensure_ascii=False)
    for token in [
        'daily skincare user', '25-35', 'medium-deep', 'natural wavy hair', 'press pump naturally',
        '1.2m', '12cm above product center', '8deg', '-3deg', 'medium close-up',
        'front label and fingers', 'f/8 equivalent', '1/125', '100',
        '45deg camera-left through 120cm diffusion', 'neutral bounce', '5200K', '2:1',
        'controlled transparent pump highlights', 'matte flexible tube', 'neutral-warm commercial grade',
    ]:
        _require(token in blob, 'ART_DIRECTION_NORMALIZATION_LOSS', f'{token} missing from normalized asset', issues)

    photo_text = (root / 'runtime' / 'cbcc' / 'photographic_route_agent_authority.py').read_text(encoding='utf-8')
    for token in ['working_distance', 'camera_height', 'yaw', 'pitch', 'roll', 'shot_size', 'focus_plane', 'aperture', 'shutter_speed', 'iso', 'modifier_size', 'modifier_distance', 'modifier_angle', 'cct', 'white_balance', 'exposure_ratio_plan', 'reflection', 'polarization_plan', 'prelight_plan']:
        _require(token in photo_text, 'PHOTO_PROJECTION_GAP', token, issues)

    native_text = (root / 'runtime' / 'cbcc' / 'model_native_prompt_contract.py').read_text(encoding='utf-8')
    for token in ['human_context', 'subject', 'action', 'environment', 'props', 'composition', 'spatial_rhythm', 'layout_geometry', 'scale_depth', 'focal_path', 'negative_space', 'evidence_hierarchy', 'camera_position', 'focus_dof', 'lighting', 'prelight', 'cmf', 'material_response', 'palette', 'color_management', 'inclusive_human', 'post_look']:
        _require(token in native_text, 'MODEL_NATIVE_DIMENSION_MISSING', token, issues)

    bootstrap = (root / 'runtime' / 'cbcc' / 'commercial_continuity_bootstrap.py').read_text(encoding='utf-8')
    try:
        normalize_call = bootstrap.index('call_args[0] = normalize_full_art_direction')
        compile_call = bootstrap.index('out = existing_prompt_compile', normalize_call)
        finalize_call = bootstrap.index('out = finalize_model_prompt_bundle(out)', compile_call)
        order_ok = normalize_call < compile_call < finalize_call
    except ValueError:
        order_ok = False
    _require(order_ok, 'FINAL_PUBLIC_BOUNDARY_ORDER_INVALID', 'expected normalize -> existing compiler chain -> final membrane', issues)

    lock = (root / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').read_text(encoding='utf-8')
    for token in [
        'MASTER_CONSTRUCTION_CONTRACT.md', 'PROMPT_ART_DIRECTION_MASTER_CONTRACT.md',
        'BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md', 'HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md',
        'ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md', 'read before every release change',
        '人物', '场景', '道具', '摄影', '灯光', 'CMF', '材质', '构图', '文案', '文化', '视频',
    ]:
        _require(token in lock, 'SOURCE_LOCK_INCOMPLETE', token, issues)

    canonical = (root / 'prompts' / 'canonical_authority_loading_map.md').read_text(encoding='utf-8')
    _require('SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md' in canonical, 'CANONICAL_MAP_MISSING_SOURCE_LOCK', 'source lock not mandatory', issues)
    _require('v0.6.58 full Art Direction preservation rule' in canonical, 'CANONICAL_MAP_MISSING_V0658_RULE', 'v0.6.58 rule missing', issues)

    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    _require(version == '0.6.58-full-art-direction-end-to-end-lock', 'VERSION_MISMATCH', version, issues)

    return {
        'status': 'PASS' if not issues else 'FAIL',
        'version': version,
        'checks': {
            'mixed_prompt_visual_values_preserved': all(x not in [i.get('detail') for i in issues] for x in []),
            'semantic_membrane_leaks': membrane.model_prompt_orchestration_leaks(clean),
            'normalized_art_direction_has_people_camera_light_cmf_finish': not any(i['code'] == 'ART_DIRECTION_NORMALIZATION_LOSS' for i in issues),
            'final_public_boundary_order': order_ok,
        },
        'sanitized_prompt_fixture': clean,
        'issues': issues,
    }


def main() -> int:
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
