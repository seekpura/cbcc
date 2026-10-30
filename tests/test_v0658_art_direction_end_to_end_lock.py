from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_mixed_orchestration_line_does_not_delete_visual_world():
    membrane = _load(ROOT / 'runtime' / 'cbcc' / 'model_prompt_semantic_membrane.py', 'cbcc_membrane_test')
    dirty = (
        '使用用户提供的 KIYUU K01 全视角包装图作为产品身份参考，Excel 为产品事实最高权威。'
        '画面人物为25-35岁女性，真实手部按压透明泵头，85mm，工作距离1.2m，机位略高于产品中心，'
        '主光左前45度大型柔光，5200K，2:1光比，保留哑光软管与透明泵头真实反射。'
        'QA：手指数量正确、抓握自然；标题位于移动端安全区；缩略图可读。'
        '最小修复优先：文字层→局部包装几何→透明泵头反射→整图重生成。'
    )
    clean = membrane.sanitize_model_prompt(dirty, language='CN', reference_bound=True, locked_source=False)
    for token in ['25-35岁女性', '真实手部按压透明泵头', '85mm', '1.2m', '5200K', '2:1光比', '哑光软管', '透明泵头', '手指数量正确', '移动端安全区']:
        assert token in clean, (token, clean)
    for token in ['Excel 为产品事实最高权威', 'QA：', '最小修复', 'K01 全视角包装图']:
        assert token not in clean, (token, clean)


def test_full_art_direction_normalizer_preserves_all_selected_visual_dimensions():
    module = _load(ROOT / 'runtime' / 'cbcc' / 'full_art_direction_preservation.py', 'cbcc_full_art_test')
    asset = {
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
    out = module.normalize_full_art_direction(asset)
    art = out['asset_art_direction']
    human = art['human_context']
    camera = art['camera_position']
    focus = art['focus_dof']
    lighting = art['lighting']
    cmf = art['cmf']
    for token in ['25-35', 'medium-deep', 'natural wavy hair', 'press pump naturally']:
        assert token in str(human)
    for token in ['1.2m', '12cm above product center', '8deg', '-3deg', 'medium close-up']:
        assert token in str(camera)
    for token in ['front label and fingers', 'f/8 equivalent', '1/125', '100']:
        assert token in str(focus)
    for token in ['45deg camera-left', 'neutral bounce', '5200K', '2:1', 'controlled transparent pump highlights']:
        assert token in str(lighting)
    assert 'matte flexible tube' in str(cmf)
    assert art['post_look'].startswith('neutral-warm')


def test_model_native_contract_still_renders_people_scene_camera_light_cmf_and_finish():
    text = (ROOT / 'runtime' / 'cbcc' / 'model_native_prompt_contract.py').read_text(encoding='utf-8')
    for token in [
        'subject', 'action', 'environment', 'props', 'human_context',
        'composition', 'spatial_rhythm', 'layout_geometry', 'scale_depth', 'focal_path', 'negative_space',
        'evidence_hierarchy', 'camera_position', 'focus_dof', 'lighting', 'prelight', 'cmf',
        'material_response', 'palette', 'color_management', 'inclusive_human', 'post_look',
    ]:
        assert token in text, token


def test_photographic_route_projects_selected_camera_light_values_not_only_view():
    text = (ROOT / 'runtime' / 'cbcc' / 'photographic_route_agent_authority.py').read_text(encoding='utf-8')
    for token in [
        'working_distance', 'camera_height', 'yaw', 'pitch', 'roll', 'shot_size',
        'focus_plane', 'aperture', 'shutter', 'iso',
        'modifier', 'cct', 'white_balance', 'light_ratio', 'reflection', 'polarization', 'prelight',
    ]:
        assert token in text, token


def test_final_public_compiler_normalizes_art_direction_then_runs_semantic_membrane_last():
    text = (ROOT / 'runtime' / 'cbcc' / 'commercial_continuity_bootstrap.py').read_text(encoding='utf-8')
    for token in ['normalize_full_art_direction', 'finalize_model_prompt_bundle', 'existing_prompt_compile']:
        assert token in text, token
    normalize_call = text.index('call_args[0] = normalize_full_art_direction')
    compile_call = text.index('out = existing_prompt_compile', normalize_call)
    finalize_call = text.index('out = finalize_model_prompt_bundle(out)', compile_call)
    assert normalize_call < compile_call < finalize_call


def test_source_requirement_lock_is_mandatory_and_names_original_authorities():
    lock = (ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').read_text(encoding='utf-8')
    for token in [
        'MASTER_CONSTRUCTION_CONTRACT.md',
        'PROMPT_ART_DIRECTION_MASTER_CONTRACT.md',
        'BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md',
        'HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md',
        'ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md',
        'read before every release change',
        '人物', '场景', '道具', '摄影', '灯光', 'CMF', '材质', '构图', '文案', '文化', '视频',
    ]:
        assert token in lock, token
