from __future__ import annotations

from cbcc.prompt_compiler import compile_asset_prompt


def _asset(**overrides):
    base={
        'asset_id':'AST-V0622','asset_name':'Decision asset','asset_type':'IMAGE','surface':'GALLERY','family':'VISUAL',
        'consumer_question':'What should I know?','decision_intent':'DECISION_SUPPORT','strategic_job':'Resolve one purchase decision',
        'incremental_information':'One decision-critical relationship','belief_target':'Decision-ready understanding',
        'product_fidelity':'REFERENCE_CONSTRAINED','production_mode':'GRAPHIC_DESIGN',
        'creative_brief':{'subject':'verified product','environment':'clean decision-relevant context'},
        'visual_production_signature':{},'creative_direction':{},'product_presence':{'planning_state':'OPTIONAL'},
    }
    base.update(overrides)
    return base


def _compile(asset, *, photography=None, strategy=None):
    return compile_asset_prompt(
        asset,
        {'name':'Demo'},
        {'market':'Malaysia','platform_family':'TIKTOK_SHOP','site':'MY'},
        {},
        {'primary_locale':'ms-MY','delivery_locale':'zh-CN'},
        photography=photography,
        strategy_authority=strategy or {},
        source_product_assets=[],
    )


def test_non_photographic_asset_does_not_emit_empty_camera_lighting_or_human_sections():
    out=_compile(_asset())
    en=out['prompt_en']; cn=out['prompt_cn']
    assert '[COMPOSITION / CAMERA]' not in en
    assert '[LIGHTING / MATERIAL / CMF]' not in en
    assert '[INCLUSIVE HUMAN PHOTOGRAPHY]' not in en
    assert '【构图与摄影机】' not in cn
    assert '【灯光 / 材质 / CMF】' not in cn
    assert '【包容性人物摄影】' not in cn
    assert 'Focal length / lens family:' not in en
    assert '快门 / ISO：' not in cn


def test_composite_mode_can_exist_without_inventing_real_photo_lens_or_prelight():
    out=_compile(_asset(), photography={'capture_mode':'COMPOSITE'})
    en=out['prompt_en']; cn=out['prompt_cn']
    assert 'Capture / composite mode: COMPOSITE' in en
    assert '拍摄 / 合成模式：COMPOSITE' in cn
    assert 'Focal length / lens family:' not in en
    assert 'Prelight plan:' not in en
    assert 'Prelight：' not in cn
    assert '[LIGHTING / MATERIAL / CMF]' not in en


def test_actual_real_photo_decisions_are_preserved_end_to_end():
    photo={
        'capture_mode':'REAL_PHOTO','repeatable_capture':True,
        'camera':{'perspective_contract':'front three-quarter label-readable view','camera_distance':'80cm','focus_plane':'front label plane'},
        'lighting':{'key':{'direction':'camera-left broad source','modifier':'large diffusion'},'cct':'5000K','prelight_plan':'neutral product reference frame'},
        'color_management':{'output_space':'sRGB','product_color_fidelity':'preserve verified product color'},
    }
    out=_compile(_asset(production_mode='REAL_PHOTO'),photography=photo)
    en=out['prompt_en']; machine=out['machine_visual_contract']
    assert '[COMPOSITION / CAMERA]' in en
    assert '[LIGHTING / MATERIAL / CMF]' in en
    assert 'front three-quarter label-readable view' in en
    assert '5000K' in en
    assert 'neutral product reference frame' in en
    assert machine['photography_execution']['capture_mode']=='REAL_PHOTO'
    assert machine['photography_execution']['color_management']['output_space']=='sRGB'


def test_global_strategy_photography_toolbox_does_not_leak_into_non_photo_asset_without_asset_reasoning():
    strategy={'sections':{'05_visual_photography_strategy':{
        'camera':{'focal_length_mm':85},
        'lighting_framework':{'cct':'4300K','prelight_plan':'global studio prelight'},
        'cmf':{'finish':'glossy'},
        'color_management':{'output_space':'Display-P3'},
    }}}
    out=_compile(_asset(),strategy=strategy)
    assert '85' not in out['prompt_en']
    assert '4300K' not in out['prompt_en']
    assert 'global studio prelight' not in out['prompt_en']
    assert 'Display-P3' not in out['prompt_en']


def test_parameter_trace_and_qa_only_cover_relevant_dimensions():
    out=_compile(_asset())
    locations=[row['render_location'] for row in out['parameter_trace']]
    assert 'COMPOSITION / CAMERA' not in locations
    assert 'LIGHTING / MATERIAL / CMF' not in locations
    assert 'INCLUSIVE HUMAN PHOTOGRAPHY' not in locations
    checks=out['qa_target_contract']['photography_checks']
    assert not any('camera' in row.lower() for row in checks)
    assert not any('human' in row.lower() for row in checks)


def test_renderer_layer_plan_is_task_derived_not_universal_six_layer_template():
    out=_compile(_asset())
    layers=out['renderer_recipe']['layer_plan']
    assert 'product_master_or_verified_product' in layers
    assert 'human_or_context_if_required' not in layers
    assert 'locked_typography' not in layers
    assert 'final_color_grade' not in layers
    assert len(layers) < 6


def test_prompt_projection_still_strips_runtime_identity_metadata_from_renderer_prose():
    asset=_asset(creative_direction={'creative_thesis':'For KIYUU K01, synthesize AST-XYZ-123 from evidence','direction_id':'DIR-001'})
    out=_compile(asset)
    assert 'AST-XYZ-123' not in out['prompt_en']
    assert 'DIR-001' not in out['prompt_en']
    assert 'For KIYUU K01, synthesize' not in out['prompt_en']
