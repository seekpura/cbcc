from cbcc.asset_execution_relevance_v0671 import complete_asset_execution_relevance
from cbcc.model_native_prompt_contract import _model_fields
from cbcc.production_parameter_closure import _selected_parameters, _route_flags, _required_groups, _missing_required


def test_no_visible_copy_overrides_global_typography_to_not_needed():
    asset = {
        'asset_id': 'AST-NOCOPY',
        'visible_copy': {'copy_render_route': 'NO_VISIBLE_COPY'},
        'asset_art_direction': {
            'visual_carrier': 'LOCKED_SOURCE_HERO',
            'typography': {
                'family': 'neo-grotesk', 'weight': '700', 'hierarchy': 'headline > support',
                'line_breaking': 'short', 'relative_scale': '1/.5', 'alignment': 'left',
                'contrast': 'high', 'safe_zone': 'mobile safe', 'mobile_legibility': '200px',
                'product_geometry_relationship': 'avoid product silhouette',
            },
        },
    }
    out = complete_asset_execution_relevance(asset)
    contract = out['asset_art_direction']['typography_contract']
    assert contract
    assert {row['status'] for row in contract.values()} == {'NOT_NEEDED'}


def test_model_fields_do_not_require_global_typography_or_inclusive_contract_when_asset_relevance_says_not_needed():
    not_needed = {'status': 'NOT_NEEDED', 'why': 'not relevant', 'execution': 'none'}
    asset = {
        'asset_art_direction': {
            'visual_carrier': 'GRAPHIC_EVIDENCE_AXIS',
            'human_relevance_decisions': {k: dict(not_needed) for k in (
                'hair_texture_style','makeup_grooming','wardrobe','body_representation',
                'disability_representation','pose','expression','gaze','religious_cultural_presentation')},
            'typography_contract': {k: dict(not_needed) for k in (
                'family_character','weight','hierarchy','line_breaking','relative_scale','alignment',
                'contrast','safe_zone','mobile_thumbnail_legibility','product_geometry_relationship')},
        },
    }
    card = {
        'information_design': {'typography': {'family': 'neo-grotesk'}},
        'inclusive_photography': {'deep_skin_shadow_protection': '深肤色保护', 'representation_principle': 'Use real audience context.'},
        'photography_execution': {'color_management': {'output_space': 'sRGB', 'product_color': '真实商品颜色必须保持'}},
    }
    fields, missing = _model_fields(asset, card, 'EN')
    assert 'typography' not in fields
    assert 'inclusive_human' not in fields
    assert 'color_management' not in missing


def test_nested_camera_focus_and_lighting_values_are_selected_for_prompt_closure():
    asset = {
        'asset_type': 'IMAGE', 'art_direction_required': True,
        'asset_art_direction': {
            'visual_carrier': 'PHOTOGRAPHIC_PRODUCT_HERO',
            'composition_grammar': 'asymmetric hero', 'layout_geometry': 'product right',
            'scale_depth': 'large product / quiet background', 'focal_path': 'product → proof',
            'negative_space': 'left open field',
            'cmf': {'palette_hex': ['#F7F6F1'], 'surface_behavior': 'matte truthful response'},
            'focal_length_mm': '85mm',
            'camera_position': {
                'working_distance': '1.2m', 'camera_height': 'subject-center', 'pitch': '-3°',
                'shot_size': 'tight product portrait', 'perspective': 'natural',
            },
            'focus_dof': {'focus_plane': 'front label', 'aperture': 'f/8', 'dof': 'pack sharp'},
            'lighting': {
                'key': 'large soft key', 'fill': 'neutral bounce', 'negative_fill': 'black flag',
                'cct': '5200K', 'white_balance': '5200K neutral', 'light_ratio': '2:1',
                'highlight_policy': 'protect white pack', 'prelight': 'verify pack highlights',
            },
        },
    }
    card = {}
    art = asset['asset_art_direction']
    params = _selected_parameters(asset, card)
    assert params['working_distance'] == '1.2m'
    assert params['camera_height'] == 'subject-center'
    assert params['yaw_pitch_roll']['pitch'] == '-3°'
    assert params['shot_size'] == 'tight product portrait'
    assert params['focus_plane'] == 'front label'
    assert params['aperture_dof'] == 'f/8'
    assert params['prelight'] == 'verify pack highlights'
    groups = _required_groups(params, asset, card)
    missing = _missing_required(params, groups, art)
    assert 'working_distance' not in missing
    assert 'camera_height' not in missing
    assert 'yaw_pitch_roll' not in missing
    assert 'shot_size' not in missing
    assert 'focus_plane' not in missing
    assert 'prelight' not in missing
    # Unselected optional variables must not become synthetic requirements.
    assert 'post_look' not in missing
    assert 'shadow_policy' not in missing
    assert 'color_management' not in missing


def test_graphic_carrier_is_not_misclassified_as_photo_by_compatibility_focal_length_slot():
    asset = {'asset_type': 'IMAGE'}
    art = {
        'visual_carrier': 'GRAPHIC_EVIDENCE_AXIS',
        'focal_length_mm': 'orthographic graphic view',
        'lighting': {'key': 'flat editorial illumination'},
    }
    photo, video, source_only = _route_flags(asset, {}, art)
    assert photo is False
    assert video is False
    assert source_only is False


def test_canonical_visible_copy_projects_exact_language_slots_and_integrated_route_is_model_render():
    from cbcc.canonical_art_direction_projection import project_named_art_direction
    from cbcc.model_native_prompt_contract import _visible_copy_block, _copy_render_mode
    asset = {
        'asset_id': 'AST-COPY',
        'asset_art_direction': {
            'copy_render_route': 'MODEL_RENDER_INTEGRATED',
            'visible_copy': {
                'copy_render_route': 'MODEL_RENDER_INTEGRATED',
                'primary_locale': 'ms-MY',
                'target_copy': 'KULIT BERMINYAK MASIH PERLUKAN HIDRASI.',
                'english_baseline': 'OILY SKIN STILL NEEDS HYDRATION.',
                'chinese_meaning': '油性肌日常护理仍需要补水。',
            },
        },
    }
    projected = project_named_art_direction(asset)
    assert projected['visible_copy']['target_copy'] == 'KULIT BERMINYAK MASIH PERLUKAN HIDRASI.'
    assert projected['visible_copy']['english_baseline'] == 'OILY SKIN STILL NEEDS HYDRATION.'
    assert projected['visible_copy']['chinese_meaning'] == '油性肌日常护理仍需要补水。'
    block = _visible_copy_block(projected, {'information_design': {}})
    assert block['target_market_copy'] == 'KULIT BERMINYAK MASIH PERLUKAN HIDRASI.'
    assert block['delivery_translation_zh'] == '油性肌日常护理仍需要补水。'
    assert block['raw']['english_baseline'] == 'OILY SKIN STILL NEEDS HYDRATION.'
    assert _copy_render_mode(projected, projected['asset_art_direction'], block) == 'MODEL_RENDER'


def test_creator_motion_timing_alias_is_consumed_as_duration_timing():
    asset = {
        'asset_type': 'IMAGE', 'art_direction_required': True,
        'asset_art_direction': {
            'visual_carrier': 'CREATOR_POV_DEMO',
            'composition_grammar': 'creator routine crop', 'layout_geometry': 'vertical action field',
            'scale_depth': 'human foreground / product support', 'focal_path': 'action → product',
            'negative_space': 'caption-safe upper field',
            'cmf': {'palette_hex': ['#F7F6F1'], 'surface_behavior': 'natural skin and product'},
            'motion_timing': '15 seconds total; 0–3s hook; 3–10s action; 10–15s handoff',
        },
    }
    params = _selected_parameters(asset, {})
    assert params['duration_timing'] == '15 seconds total; 0–3s hook; 3–10s action; 10–15s handoff'
