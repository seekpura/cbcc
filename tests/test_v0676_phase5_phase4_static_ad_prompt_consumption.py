from __future__ import annotations

from runtime.cbcc.prompt_compiler import compile_asset_prompt


def _phase4_photo_asset():
    return {
        'asset_id': 'AST-P5-PHOTO',
        'asset_name': 'Phase4 scene-derived photo authority',
        'asset_type': 'IMAGE',
        'surface': 'GALLERY',
        'family': 'VISUAL',
        'production_mode': 'REAL_PHOTO',
        'art_direction_status': 'AUTHORED',
        'visible_copy': {'target_copy': 'SERUM HARIAN'},
        'asset_art_direction': {
            'visual_objective': {'en': 'Make the product identity and real-use proof legible.', 'cn': '让商品身份与真实使用证据清晰可见。'},
            'visual_carrier': 'LIFESTYLE_PHOTOGRAPHY',
            'visual_language': {'en': 'Truthful premium lifestyle photography.', 'cn': '真实克制的高质感生活方式摄影。'},
            'creative_thesis': {'en': 'Real routine, precise product proof.', 'cn': '真实日常，精确商品证据。'},
            'subject': {'en': 'The real product bottle on a morning vanity.', 'cn': '晨间梳妆台上的真实商品瓶。'},
            'environment': {'en': 'Bright morning bathroom vanity context.', 'cn': '明亮晨间浴室梳妆台语境。'},
            'composition_grammar': 'environment-led vanity identity frame with product foreground',
            'layout_geometry': 'product foreground at lower-right third; use context behind',
            'scale_depth': 'product near plane, vanity mid plane, room background',
            'negative_space': 'upper-left copy-safe negative space',
            'camera_or_view': 'eye-level three-quarter photo',
            'focal_length_mm': 85,
            'camera_position': {
                'working_distance': '1.2m',
                'camera_height': 'product center',
                'yaw': '15 degrees camera-right',
                'pitch': '-3 degrees',
                'roll': '0 degrees',
                'shot_size': 'medium close product frame',
                'perspective': 'natural compressed perspective',
            },
            'focus_dof': {
                'focus_plane': 'front label',
                'aperture': 'f/8',
                'dof': 'label and package shoulders sharp; background softly separated',
                'shutter': '1/125s',
                'iso': 100,
            },
            'lighting': {
                'key': {'direction': 'camera-left 45 degrees', 'modifier': '120cm diffusion'},
                'fill': {'direction': 'camera-right', 'level': '-1.5 stop'},
                'cct': 5200,
                'white_balance': '5200K locked',
                'exposure_ratio_plan': '2:1 key-to-fill',
                'highlight_policy': 'protect package highlights',
                'reflection': 'controlled with flags',
            },
            'cmf': {
                'color': 'warm mineral neutral + deep green accent',
                'material': 'real glass and label paper',
                'finish': 'controlled soft specular highlights',
            },
            'material_response': 'truthful glass edge and label-paper response',
            'copy_render_mode': 'MODEL_RENDER',
            'copy_zone': {'en': 'Upper-left safe zone.', 'cn': '左上安全区。'},
            'typography': {'en': 'Clean modern sans serif.', 'cn': '简洁现代无衬线。'},
            'output_spec': '1080×1350, 4:5, TikTok Shop Malaysia gallery',
            'product_presence': {
                'planning_state': 'REQUIRED',
                'production_state': 'PRESENT',
                'product_role': 'HERO_PRODUCT_FOREGROUND',
                'scale_relationship': 'product occupies about 38% of frame height and label stays readable',
                'source_reference_role': 'SUBJECT_REFERENCE',
            },
            'product_fidelity': {
                'mode': 'REFERENCE_GUIDED_NATIVE_LOCK',
                'source_asset_ids': ['SRC-PRODUCT-01'],
            },
        },
    }


def _compile(asset=None):
    return compile_asset_prompt(
        asset or _phase4_photo_asset(),
        {'name': 'K01'},
        {'market': 'MY', 'platform_family': 'TikTok Shop', 'site': 'MY', 'category': 'skincare'},
        {},
        {'primary_locale': 'ms-MY', 'delivery_locale': 'zh-CN'},
        {},
        None,
        None,
        [
            {
                'asset_id': 'SRC-PRODUCT-01',
                'role': 'FRONT',
                'provider_asset_handle': 'ref://real-product-front',
                'sha256': 'product-sha',
                'ingest_status': 'HASH_VERIFIED_LOCAL',
            }
        ],
    )


def test_phase4_scene_derived_camera_light_cmf_survive_into_model_acting_plane():
    out = _compile()
    en = out['model_prompt_en']
    for token in (
        '85', '1.2m', 'product center', 'front label', 'f/8',
        'camera-left 45 degrees', '120cm diffusion', '5200', '2:1 key-to-fill',
        'protect package highlights', 'real glass and label paper',
        'controlled soft specular highlights',
    ):
        assert token in en, token

    checks = {row['decision']: row for row in out['prompt_consumption_audit']['checks']}
    for decision in ('focal_length', 'camera_position', 'focus_dof', 'lighting', 'cmf'):
        assert decision in checks, decision
        assert checks[decision]['projected'] is True


def test_nested_phase4_product_presence_and_fidelity_survive_prompt_and_reference_binding():
    out = _compile()
    en = out['model_prompt_en']
    card = out['design_card']
    presence = card['product_presence']
    identity = card['product_identity']

    assert presence['planning_state'] == 'REQUIRED'
    assert presence['product_role'] == 'HERO_PRODUCT_FOREGROUND'
    assert '38%' in presence['scale_relationship']
    assert 'Product presence: REQUIRED' in en
    assert 'HERO_PRODUCT_FOREGROUND' in en
    assert '38%' in en

    assert identity['product_fidelity'] == 'REFERENCE_GUIDED_NATIVE_LOCK'
    assert identity['reference_input_required'] is True
    assert identity['native_subject_required'] is True
    assert out['production_assembly_notes']['reference_input_required'] is True
    assert out['renderer_recipe']['source_product_bindings'][0]['visible_subject_binding'] is True
    assert out['renderer_recipe']['source_product_bindings'][0]['locator']['value'] == 'ref://real-product-front'
    assert out['model_prompt_semantic_membrane']['reference_bound'] is True
    assert 'attached product reference' in en.lower()
    assert 'ref://real-product-front' not in en
    assert 'product-sha' not in en
