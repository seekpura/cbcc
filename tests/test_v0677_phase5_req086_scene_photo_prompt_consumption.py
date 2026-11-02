from __future__ import annotations

from cbcc import prompt_compiler


def _asset() -> dict:
    return {
        'asset_id': 'AST-REQ086',
        'asset_name': 'REQ-086 scene-derived photography authority',
        'asset_type': 'IMAGE',
        'surface': 'GALLERY',
        'family': 'VISUAL',
        'production_mode': 'REAL_PHOTO',
        'product_fidelity': 'REFERENCE_GUIDED',
        'asset_art_direction': {
            'asset_id': 'AST-REQ086',
            'visual_carrier': 'LIFESTYLE_PHOTOGRAPHY',
            'scene': 'authored countertop evidence scene',
            'composition_grammar': 'authored asymmetric evidence frame',
            'camera_or_view': 'CANONICAL_THREE_QUARTER_VIEW',
            'focal_length_mm': 91,
            'camera_position': {
                'working_distance': '0.73m',
                'camera_height': 'CANONICAL_PRODUCT_SHOULDER_HEIGHT',
                'yaw': '13deg',
                'pitch': '-7deg',
                'roll': '1deg',
                'shot_size': 'CANONICAL_TIGHT_PRODUCT_FRAME',
                'perspective': 'CANONICAL_NATURAL_COMPRESSION',
            },
            'focus_dof': {
                'focus_plane': 'CANONICAL_LABEL_EDGE',
                'aperture': 'f/7.1',
                'dof': 'CANONICAL_LABEL_TO_APPLICATOR_DEPTH',
                'shutter': '1/160s',
                'iso': 125,
            },
            'lighting': {
                'key': {'direction': 'CANONICAL_REAR_LEFT_GRAZE', 'modifier': '95cm diffusion'},
                'fill': {'direction': 'CANONICAL_FRONT_RIGHT_BOUNCE', 'level': '-1.3 stop'},
                'cct': 4875,
                'white_balance': 'CANONICAL_4875K_LOCKED',
                'exposure_ratio_plan': 'CANONICAL_2_3_TO_1',
                'highlight_policy': 'CANONICAL_PROTECT_LABEL_AND_GLASS_EDGE',
                'reflection': 'CANONICAL_FLAGGED_GLASS_REFLECTION',
            },
            'cmf': {
                'color': 'CANONICAL_OBSIDIAN_TEAL_FIELD',
                'material': 'CANONICAL_REAL_GLASS_AND_LABEL_PAPER',
                'finish': 'CANONICAL_CONTROLLED_EDGE_SPECULAR',
            },
        },
    }


def _stale_strategy() -> dict:
    return {
        'sections': {
            '05_visual_photography_strategy': {
                'camera': {
                    'focal_length_mm': 35,
                    'preferred_view': 'STALE_GLOBAL_FRONT_VIEW',
                    'working_distance': 'STALE_GLOBAL_DISTANCE',
                    'focus_plane': 'STALE_GLOBAL_FOCUS',
                },
                'lighting_framework': {
                    'key': {'direction': 'STALE_GLOBAL_KEY'},
                    'cct': 5600,
                    'white_balance': 'STALE_GLOBAL_WB',
                    'highlight_policy': 'STALE_GLOBAL_HIGHLIGHT_POLICY',
                },
                'cmf': {
                    'color': 'STALE_GLOBAL_CATEGORY_PALETTE',
                    'material': 'STALE_GLOBAL_MATERIAL',
                    'finish': 'STALE_GLOBAL_FINISH',
                },
            }
        }
    }


def _compile() -> dict:
    return prompt_compiler.compile_asset_prompt(
        _asset(),
        product={'name': 'Truth Product'},
        target={'market': 'MY', 'platform_family': 'TikTok'},
        culture={},
        language_contract={'primary_locale': 'ms-MY'},
        strategy_authority=_stale_strategy(),
    )


def test_req086_canonical_asset_art_direction_overrides_stale_strategy_photography_defaults():
    result = _compile()
    photo = result['design_card']['photography_execution']

    assert photo['camera']['authority'] == 'AGENT_ASSET_ART_DIRECTION'
    assert photo['camera']['focal_length_mm'] == 91
    assert photo['camera']['preferred_view'] == 'CANONICAL_THREE_QUARTER_VIEW'
    assert photo['camera']['working_distance'] == '0.73m'
    assert photo['camera']['focus_plane'] == 'CANONICAL_LABEL_EDGE'
    assert photo['camera']['aperture'] == 'f/7.1'
    assert photo['camera']['iso'] == 125

    assert photo['lighting']['authority'] == 'AGENT_ASSET_ART_DIRECTION'
    assert photo['lighting']['white_balance'] == 'CANONICAL_4875K_LOCKED'
    assert photo['lighting']['highlight_policy'] == 'CANONICAL_PROTECT_LABEL_AND_GLASS_EDGE'
    assert photo['lighting']['reflection'] == 'CANONICAL_FLAGGED_GLASS_REFLECTION'

    assert photo['cmf']['authority'] == 'AGENT_ASSET_ART_DIRECTION'
    assert photo['cmf']['color'] == 'CANONICAL_OBSIDIAN_TEAL_FIELD'
    assert photo['cmf']['material'] == 'CANONICAL_REAL_GLASS_AND_LABEL_PAPER'
    assert photo['cmf']['finish'] == 'CANONICAL_CONTROLLED_EDGE_SPECULAR'


def test_req086_final_acting_prompt_contains_scene_derived_camera_lighting_and_cmf_values():
    result = _compile()
    prompt_en = result['prompt_en']

    for token in [
        'CANONICAL_THREE_QUARTER_VIEW',
        '0.73m',
        'CANONICAL_LABEL_EDGE',
        'f/7.1',
        'CANONICAL_4875K_LOCKED',
        'CANONICAL_PROTECT_LABEL_AND_GLASS_EDGE',
        'CANONICAL_FLAGGED_GLASS_REFLECTION',
        'CANONICAL_OBSIDIAN_TEAL_FIELD',
        'CANONICAL_REAL_GLASS_AND_LABEL_PAPER',
        'CANONICAL_CONTROLLED_EDGE_SPECULAR',
    ]:
        assert token in prompt_en

    assert 'STALE_GLOBAL_FRONT_VIEW' not in prompt_en
    assert 'STALE_GLOBAL_WB' not in prompt_en
    assert 'STALE_GLOBAL_CATEGORY_PALETTE' not in prompt_en


def test_req086_consumption_audit_proves_each_scene_derived_photography_authority():
    result = _compile()
    audit = result['prompt_consumption_audit']
    checks = {row['decision']: row for row in audit['checks']}

    assert audit['status'] == 'PASS'
    for decision in ['scene_derived_camera', 'scene_derived_lighting', 'scene_derived_cmf']:
        assert checks[decision]['required'] is True
        assert checks[decision]['projected'] is True
        assert checks[decision]['authority'] == 'AGENT_ASSET_ART_DIRECTION'
        assert checks[decision]['value']

    assert not set(['scene_derived_camera', 'scene_derived_lighting', 'scene_derived_cmf']) & set(audit['missing_decisions'])
