from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_membrane():
    path = ROOT / 'runtime' / 'cbcc' / 'model_prompt_semantic_membrane.py'
    spec = importlib.util.spec_from_file_location('cbcc_membrane_test', path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_mixed_orchestration_line_does_not_delete_visual_world():
    membrane = _load_membrane()
    dirty = (
        '使用用户提供的 KIYUU K01 全视角包装图作为产品身份参考，Excel 为产品事实最高权威。'
        '画面人物为25-35岁女性，真实手部按压透明泵头，85mm，工作距离1.2m，机位略高于产品中心，'
        '主光左前45度大型柔光，5200K，2:1光比，保留哑光软管与透明泵头真实反射。'
        'QA：手指数量正确、抓握自然；标题位于移动端安全区；缩略图可读。'
        '最小修复优先：文字层→局部包装几何→透明泵头反射→整图重生成。'
    )
    clean = membrane.sanitize_model_prompt(
        dirty,
        language='CN',
        reference_bound=True,
        locked_source=False,
    )
    for token in ['25-35岁女性', '真实手部按压透明泵头', '85mm', '1.2m', '5200K', '2:1光比', '哑光软管', '透明泵头', '手指数量正确', '移动端安全区']:
        assert token in clean, (token, clean)
    for token in ['Excel 为产品事实最高权威', 'QA：', '最小修复', 'K01 全视角包装图']:
        assert token not in clean, (token, clean)


def test_model_native_contract_has_full_art_direction_dimensions():
    text = (ROOT / 'runtime' / 'cbcc' / 'model_native_prompt_contract.py').read_text(encoding='utf-8')
    required = [
        'human_context', 'subject', 'action', 'environment', 'props',
        'composition', 'spatial_rhythm', 'layout_geometry', 'scale_depth', 'focal_path', 'negative_space',
        'evidence_hierarchy', 'typography', 'copy_zone',
        'camera_view', 'focal_length', 'lens_family', 'working_distance', 'camera_position', 'focus_dof',
        'shutter_iso', 'lighting', 'modifier_geometry', 'prelight', 'cmf', 'material_response', 'palette', 'color_management',
        'inclusive_human', 'post_look',
    ]
    for token in required:
        assert token in text, token


def test_photographic_route_projects_selected_camera_light_values_not_only_view():
    text = (ROOT / 'runtime' / 'cbcc' / 'photographic_route_agent_authority.py').read_text(encoding='utf-8')
    for token in [
        'working_distance', 'camera_height', 'yaw', 'pitch', 'roll', 'shot_size',
        'focus_plane', 'aperture', 'shutter', 'iso',
        'modifier', 'cct', 'white_balance', 'light_ratio', 'reflection', 'polarization', 'prelight',
    ]:
        assert token in text, token


def test_final_semantic_membrane_is_last_prompt_mutation_before_public_compiler():
    text = (ROOT / 'runtime' / 'cbcc' / '__init__.py').read_text(encoding='utf-8')
    marker = '_model_prompt_semantic_membrane.wrap_compile_asset_prompt('
    assert marker in text
    membrane_pos = text.rindex(marker)
    public_pos = text.index('_legacy_prompt_compiler.compile_asset_prompt = _agent_authority_prompt_compiler.compile_asset_prompt')
    assert membrane_pos < public_pos
    tail = text[membrane_pos:public_pos]
    assert tail.count('wrap_compile_asset_prompt(') == 1, tail


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
