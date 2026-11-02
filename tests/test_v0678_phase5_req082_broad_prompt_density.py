from __future__ import annotations

from copy import deepcopy

from runtime.cbcc.prompt_compiler import compile_asset_prompt


def _rich_static_asset() -> dict:
    return {
        'asset_id': 'AST-P5-DENSITY',
        'asset_name': 'Broad Phase5 density fixture',
        'asset_type': 'IMAGE',
        'surface': 'GALLERY',
        'family': 'VISUAL',
        'production_mode': 'REAL_PHOTO',
        'visible_copy': {'target_copy': 'SERUM HARIAN'},
        'asset_art_direction': {
            'visual_objective': {'en': 'Make daily-use context and product proof immediately legible.', 'cn': '让日常使用语境与商品证据立即可读。'},
            'visual_carrier': 'LIFESTYLE_PHOTOGRAPHY',
            'visual_language': {'en': 'Truthful premium lifestyle photography with restrained commerce polish.', 'cn': '真实高质感生活方式摄影，商业感克制。'},
            'creative_thesis': {'en': 'Everyday credibility before persuasion.', 'cn': '先建立日常可信感，再说服。'},
            'subject': {'en': 'Real product bottle held naturally by a Malaysian adult user.', 'cn': '马来西亚成年用户自然手持真实商品瓶。'},
            'action': {'en': 'Lift the bottle, read the label, then return it to the vanity.', 'cn': '拿起瓶身、读取标签，再放回梳妆台。'},
            'environment': {'en': 'Bright lived-in morning vanity with only task-relevant objects.', 'cn': '明亮且真实使用中的晨间梳妆台，仅保留任务相关物件。'},
            'human_context': {'en': 'Adult Malaysian user presented without ethnic stereotyping.', 'cn': '成年马来西亚用户，避免族裔刻板印象。'},
            'inclusive_human': {
                'skin_tone_exposure': {'en': 'Protect natural skin-tone detail without over-brightening.', 'cn': '保留自然肤色细节，不进行过度提亮。'},
                'representation': {'en': 'Natural everyday grooming; no tokenized cultural costume.', 'cn': '自然日常梳洗，不使用符号化文化服饰。'},
            },
            'composition_grammar': 'environment-led vanity identity frame with product foreground',
            'layout_geometry': 'product at lower-right third; hand enters from left; copy safe zone upper-left',
            'scale_depth': 'product near plane, hand mid plane, vanity and room behind',
            'focal_path': 'product label -> hand-use cue -> morning context',
            'negative_space': 'upper-left 22% remains visually quiet',
            'evidence_hierarchy': 'readable product identity -> believable handling -> lived-in use context',
            'camera_or_view': 'eye-level three-quarter photo',
            'focal_length_mm': 85,
            'camera_position': {'working_distance': '1.2m', 'camera_height': 'product center', 'yaw': '15 degrees camera-right'},
            'focus_dof': {'focus_plane': 'front label', 'aperture': 'f/8', 'dof': 'label and fingers sharp; room softly separated'},
            'lighting': {
                'key': {'direction': 'camera-left 45 degrees', 'modifier': '120cm diffusion'},
                'fill': {'direction': 'camera-right', 'level': '-1.5 stop'},
                'cct': 5200,
                'highlight_policy': 'protect glass and label highlights',
            },
            'cmf': {'color': 'warm neutral + deep green accent', 'material': 'real glass and label paper', 'finish': 'soft controlled specular response'},
            'material_response': 'show truthful glass edge, paper tooth and natural skin texture',
            'copy_render_mode': 'MODEL_RENDER',
            'copy_zone': {'en': 'Upper-left safe zone.', 'cn': '左上安全区。'},
            'typography': {'en': 'Clean modern sans serif.', 'cn': '简洁现代无衬线。'},
            'output_spec': '1080×1350, 4:5, TikTok Shop Malaysia gallery',
            'product_presence': {
                'planning_state': 'REQUIRED',
                'production_state': 'PRESENT',
                'product_role': 'HERO_PRODUCT_FOREGROUND',
                'scale_relationship': 'about 38% of frame height; front label readable',
                'source_reference_role': 'SUBJECT_REFERENCE',
            },
            'product_fidelity': {'mode': 'REFERENCE_GUIDED_NATIVE_LOCK', 'source_asset_ids': ['SRC-PRODUCT-01']},
        },
        'precision_boundaries': ['do not invent efficacy outcomes', 'do not alter package identity'],
        'editable_layer_contract': {'editable_layers': ['environment'], 'frozen_layers': ['product identity']},
    }


def _compile(asset: dict) -> dict:
    return compile_asset_prompt(
        asset,
        {'name': 'K01'},
        {'market': 'MY', 'platform_family': 'TikTok Shop', 'site': 'MY', 'category': 'skincare'},
        {},
        {'primary_locale': 'ms-MY', 'delivery_locale': 'zh-CN'},
        {},
        None,
        None,
        [{
            'asset_id': 'SRC-PRODUCT-01',
            'role': 'FRONT',
            'provider_asset_handle': 'ref://real-product-front',
            'sha256': 'product-sha',
            'ingest_status': 'HASH_VERIFIED_LOCAL',
        }],
    )


def test_rich_static_art_direction_projects_geometry_material_culture_copy_and_inclusion_without_metadata_leak():
    out = _compile(_rich_static_asset())
    en = out['model_prompt_en']

    # Semantic membrane may split semicolon-delimited authored prose into separate model clauses;
    # verify every authored semantic fragment rather than byte-identical punctuation.
    for concrete in (
        'product at lower-right third',
        'product near plane',
        'product label',
        'upper-left 22%',
        'real glass and label paper',
        'paper tooth',
        'Protect natural skin-tone detail without over-brightening.',
        'Natural everyday grooming',
        'no tokenized cultural costume.',
        'SERUM HARIAN',
    ):
        assert concrete in en, concrete

    for forbidden in (
        'ref://real-product-front', 'product-sha', 'HASH_VERIFIED_LOCAL',
        'provider_asset_handle', 'authority hash', 'prompt consumption audit',
    ):
        assert forbidden not in en

    audit = out['prompt_consumption_audit']
    assert audit['status'] == 'PASS', audit
    assert audit['missing_decisions'] == [], audit


def test_short_product_background_camera_light_prompt_cannot_bypass_broad_density_audit():
    asset = _rich_static_asset()
    art = deepcopy(asset['asset_art_direction'])
    art['model_prompt_en'] = 'Photograph the product on a warm bathroom background with an 85mm camera and soft key light.'
    art['model_prompt_cn'] = '在温暖浴室背景中，用85mm镜头和柔和主光拍摄商品。'
    asset['asset_art_direction'] = art

    out = _compile(asset)
    audit = out['prompt_consumption_audit']
    missing = set(audit['missing_decisions'])

    assert audit['status'] == 'INCOMPLETE', audit
    # The locked plan explicitly rejects a short product/background/camera/light recap when the
    # authored object also contains geometry, material, culture/inclusion and evidence decisions.
    assert {'layout_geometry', 'scale_depth', 'focal_path', 'material_response', 'human_context', 'inclusive_human'} & missing, missing
    assert len(missing) >= 4, missing
