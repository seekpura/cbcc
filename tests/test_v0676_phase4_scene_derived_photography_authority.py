from __future__ import annotations

from copy import deepcopy

from cbcc.portfolio_visual_authority import validate_portfolio_differentiation
from cbcc import prompt_compiler


def _review():
    return {
        'status': 'PASS',
        'adjacent_asset_review': [
            {'pair': ['AST-A', 'AST-B'], 'delta': 'identity/context scene vs material/detail scene'},
        ],
        'keep_reauthor_merge_delete': [
            {'asset_id': 'AST-A', 'decision': 'KEEP'},
            {'asset_id': 'AST-B', 'decision': 'KEEP'},
        ],
    }


def _direction():
    return {
        'require_portfolio_differentiation_review': True,
        'portfolio_differentiation_review': _review(),
    }


def _asset(
    aid: str,
    *,
    scene: str,
    carrier: str,
    composition: str,
    camera: dict | None,
    lighting: dict | None,
    cmf: dict | None,
    delta: str,
    justification: str | None = None,
):
    art = {
        'asset_id': aid,
        'visual_carrier': carrier,
        'scene': scene,
        'subject': 'real product in the authored scene',
        'composition_grammar': composition,
        'layout_geometry': f'{aid} scene-specific layout',
        'scale_depth': f'{aid} scene-specific scale/depth',
        'negative_space': f'{aid} scene-specific negative space',
        'camera_or_view': (camera or {}).get('preferred_view') or 'photographic scene view',
        'material_response': f'{aid} scene-specific material response',
        'deliberate_difference': delta,
        'product_presence': {
            'planning_state': 'REQUIRED',
            'product_role': 'HERO' if aid == 'AST-A' else 'SUPPORTING',
            'source_reference_role': 'SUBJECT_REFERENCE',
        },
    }
    if camera:
        art['focal_length_mm'] = camera.get('focal_length_mm')
        art['camera_position'] = {
            k: v for k, v in camera.items()
            if k in {'working_distance', 'camera_height', 'yaw', 'pitch', 'roll', 'shot_size', 'perspective'}
        }
        art['focus_dof'] = {
            k: v for k, v in camera.items()
            if k in {'focus_plane', 'aperture', 'dof', 'shutter', 'iso'}
        }
    if lighting:
        art['lighting'] = deepcopy(lighting)
    if cmf:
        art['cmf'] = deepcopy(cmf)
    if justification:
        art['photography_continuity_justification'] = justification
    return {
        'asset_id': aid,
        'asset_type': 'IMAGE',
        'surface': 'GALLERY',
        'family': 'VISUAL',
        'production_mode': 'REAL_PHOTO',
        'art_direction_status': 'AUTHORED',
        'asset_art_direction': art,
    }


def _preset():
    return (
        {
            'focal_length_mm': 85,
            'preferred_view': 'eye-level three-quarter photo',
            'working_distance': '1.2m',
            'camera_height': 'product center',
            'shot_size': 'medium close product frame',
            'focus_plane': 'front label',
            'aperture': 'f/8',
            'shutter': '1/125s',
            'iso': 100,
        },
        {
            'key': {'direction': 'camera-left 45 degrees', 'modifier': '120cm diffusion'},
            'fill': {'direction': 'camera-right', 'level': '-1.5 stop'},
            'cct': 5200,
            'white_balance': '5200K locked',
            'exposure_ratio_plan': '2:1 key-to-fill',
            'highlight_policy': 'protect package highlights',
            'reflection': 'controlled with flags',
        },
        {
            'color': 'warm mineral neutral + deep green accent',
            'material': 'real glass and label paper',
            'finish': 'controlled soft specular highlights',
        },
    )


def test_unrelated_scenes_reusing_identical_full_photo_preset_without_reason_return_to_agent():
    camera, lighting, cmf = _preset()
    architecture = {
        'assets': [
            _asset(
                'AST-A',
                scene='bright morning bathroom vanity routine',
                carrier='LIFESTYLE_PHOTOGRAPHY',
                composition='environment-led vanity identity frame with product foreground',
                camera=camera, lighting=lighting, cmf=cmf,
                delta='environment-led identity scene',
            ),
            _asset(
                'AST-B',
                scene='dark controlled studio macro of liquid texture and bottle material',
                carrier='MATERIAL_MACRO_PHOTOGRAPHY',
                composition='tight macro material study with liquid texture as evidence plane',
                camera=camera, lighting=lighting, cmf=cmf,
                delta='switch from human-scale environment to material macro evidence',
            ),
        ],
    }
    result = validate_portfolio_differentiation(architecture, _direction())
    assert result['status'] == 'RETURN_TO_AGENT'
    issue = next(x for x in result['issues'] if x['type'] == 'DUPLICATE_PHOTOGRAPHY_EXECUTION_SIGNATURE')
    assert issue['asset_ids'] == ['AST-A', 'AST-B']
    assert issue['action'] == 'AUTHOR_SCENE_DERIVED_PHOTOGRAPHY_OR_JUSTIFY_CONTROLLED_CONTINUITY'
    assert result['runtime_may_redesign'] is False


def test_photographic_route_missing_scene_derived_camera_light_or_cmf_returns_to_agent():
    architecture = {
        'assets': [
            _asset(
                'AST-A',
                scene='real morning routine at bathroom vanity',
                carrier='LIFESTYLE_PHOTOGRAPHY',
                composition='hand-to-product routine relationship',
                camera=None,
                lighting=None,
                cmf=None,
                delta='embodied routine scene',
            )
        ]
    }
    direction = deepcopy(_direction())
    direction['portfolio_differentiation_review']['adjacent_asset_review'] = [
        {'asset_id': 'AST-A', 'delta': 'single photographic route fixture'}
    ]
    result = validate_portfolio_differentiation(architecture, direction)
    assert result['status'] == 'RETURN_TO_AGENT'
    issue = next(x for x in result['issues'] if x['type'] == 'MISSING_SCENE_DERIVED_PHOTOGRAPHY_EXECUTION')
    assert issue['asset_ids'] == ['AST-A']
    assert set(issue['missing']) == {'camera', 'lighting', 'cmf'}
    assert result['runtime_may_redesign'] is False


def test_distinct_authored_scenes_keep_distinct_photo_execution_contracts_and_pass():
    camera_a, lighting_a, cmf_a = _preset()
    camera_b = {
        'focal_length_mm': 100,
        'preferred_view': 'top-down macro detail view',
        'working_distance': '0.45m',
        'camera_height': 'macro working distance',
        'shot_size': 'macro detail',
        'focus_plane': 'liquid meniscus and label edge',
        'aperture': 'f/11',
        'shutter': '1/160s',
        'iso': 125,
    }
    lighting_b = {
        'key': {'direction': 'rear-side grazing', 'modifier': 'strip diffusion'},
        'negative_fill': 'camera-right black flag',
        'cct': 5000,
        'white_balance': '5000K locked',
        'exposure_ratio_plan': '3:1 with controlled edge separation',
        'highlight_policy': 'trace glass edge without clipping liquid highlight',
        'reflection': 'polarizer + flag control',
    }
    cmf_b = {
        'color': 'neutral translucent liquid against controlled deep field',
        'material': 'glass + transparent serum texture',
        'finish': 'crisp edge highlight + visible liquid body',
    }
    a = _asset(
        'AST-A', scene='bright morning vanity identity scene', carrier='LIFESTYLE_PHOTOGRAPHY',
        composition='environment-led identity frame', camera=camera_a, lighting=lighting_a, cmf=cmf_a,
        delta='wide identity/context scene',
    )
    b = _asset(
        'AST-B', scene='controlled dark macro texture study', carrier='MATERIAL_MACRO_PHOTOGRAPHY',
        composition='tight macro evidence frame', camera=camera_b, lighting=lighting_b, cmf=cmf_b,
        delta='macro texture evidence scene',
    )
    execution_a = prompt_compiler._derived_photo_contract(a, None, None)
    execution_b = prompt_compiler._derived_photo_contract(b, None, None)
    assert execution_a['camera'] != execution_b['camera']
    assert execution_a['lighting'] != execution_b['lighting']
    assert execution_a['cmf'] != execution_b['cmf']
    assert execution_a.get('authority') == 'AGENT_ASSET_ART_DIRECTION'
    assert execution_b.get('authority') == 'AGENT_ASSET_ART_DIRECTION'

    result = validate_portfolio_differentiation({'assets': [a, b]}, _direction())
    assert result['status'] == 'PASS'


def test_explicit_controlled_ab_continuity_justification_allows_shared_photo_preset():
    camera, lighting, cmf = _preset()
    justification = (
        'Controlled A/B test: keep camera, lighting and CMF fixed so only the authored message/evidence '
        'plane changes; the shared preset is the experimental control, not a generic portfolio default.'
    )
    a = _asset(
        'AST-A', scene='controlled tabletop A/B variant A', carrier='CONTROLLED_TEST_PHOTOGRAPHY_A',
        composition='variant A evidence hierarchy', camera=camera, lighting=lighting, cmf=cmf,
        delta='A variant changes evidence hierarchy only', justification=justification,
    )
    b = _asset(
        'AST-B', scene='controlled tabletop A/B variant B', carrier='CONTROLLED_TEST_PHOTOGRAPHY_B',
        composition='variant B evidence hierarchy', camera=camera, lighting=lighting, cmf=cmf,
        delta='B variant changes evidence hierarchy only', justification=justification,
    )
    result = validate_portfolio_differentiation({'assets': [a, b]}, _direction())
    assert result['status'] == 'PASS'
    assert not any(x['type'] == 'DUPLICATE_PHOTOGRAPHY_EXECUTION_SIGNATURE' for x in result['issues'])
