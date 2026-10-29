from __future__ import annotations

from runtime.cbcc.commercial_operator_density_authority import apply_commercial_operator_density_authority


def _bundle(copy='KAWAL MINYAK. KEKALKAN HIDRASI.'):
    return {
        'status':'COPY_RENDER_MODE_REQUIRED',
        'model_prompt_status':'COPY_RENDER_MODE_REQUIRED',
        'model_prompt_cn':'创建完整商业画面。按已设计的信息层级保留清晰文字区和足够负空间；画面中不要生成营销文字。',
        'model_prompt_en':'Create a complete commercial image. Preserve the authored typography zone and clean negative space; generate no marketing text inside the image.',
        'visible_copy_block':{
            'target_market_copy':copy,
            'delivery_translation_zh':'控油，同时保持水润。',
        },
        'design_card':{
            'product_presence':{'planning_state':'REQUIRED','production_state':'PRESENT'},
            'information_design':{'typography':'compact high-contrast sans-serif, two lines'},
        },
        'production_assembly_notes':{},
        'renderer_recipe':{'deterministic_text_composition':True},
    }


def test_visible_copy_autoresolves_to_integrated_model_render():
    asset={'asset_id':'IMG-01','visible_copy':{'target_market_copy':'KAWAL MINYAK. KEKALKAN HIDRASI.'}}
    out=apply_commercial_operator_density_authority(_bundle(),asset)
    assert out['production_assembly_notes']['copy_render_mode']=='MODEL_RENDER'
    assert out['production_assembly_notes']['copy_render_mode_source']=='AUTONOMOUS_INTEGRATED_RENDER_DEFAULT'
    assert 'KAWAL MINYAK. KEKALKAN HIDRASI.' in out['model_prompt_en']
    assert 'integrated part of the finished commercial image' in out['model_prompt_en']
    assert 'generate no marketing text inside the image' not in out['model_prompt_en'].lower()
    assert '画面中不要生成营销文字' not in out['model_prompt_cn']
    assert out['model_prompt_status']=='MODEL_NATIVE_PROMPT_READY'
    assert out['renderer_recipe']['text_policy']['model_prompt_contains_exact_copy'] is True
    assert 'deterministic_text_composition' not in out['renderer_recipe']
    assert out['operator_release']['normal_creative_choices_are_operator_gates'] is False
    assert out['operator_release']['release_state']=='READY_FOR_PRODUCTION_OR_VISUAL_QA'


def test_explicit_post_composite_remains_a_valid_specialist_route():
    asset={
        'asset_id':'IMG-02',
        'asset_art_direction':{'copy_render_mode':'POST_COMPOSITE'},
        'visible_copy':{'target_market_copy':'EXACT COPY'},
    }
    bundle=_bundle('EXACT COPY')
    out=apply_commercial_operator_density_authority(bundle,asset)
    assert out['production_assembly_notes']['copy_render_mode']=='POST_COMPOSITE'
    assert out['production_assembly_notes']['copy_render_mode_source']=='EXPLICIT_AGENT_OR_PROJECT_DECISION'
    assert 'generate no marketing text inside the image' in out['model_prompt_en'].lower()
    assert 'integrated part of the finished commercial image' not in out['model_prompt_en']
    assert out['renderer_recipe']['text_policy']['post_composite_explicit_only'] is True


def test_no_visible_copy_does_not_create_a_copy_gate():
    asset={'asset_id':'IMG-03'}
    bundle=_bundle('')
    bundle['visible_copy_block']={}
    out=apply_commercial_operator_density_authority(bundle,asset)
    assert out['production_assembly_notes']['copy_render_mode']=='NO_VISIBLE_COPY'
    assert out['operator_release']['release_state']=='READY_FOR_PRODUCTION_OR_VISUAL_QA'


def test_output_qa_is_pixel_result_oriented_not_receipt_oriented():
    out=apply_commercial_operator_density_authority(_bundle(),{'asset_id':'IMG-04'})
    qa=out['commercial_visual_qa_contract']
    ids={row['id'] for row in qa['checks']}
    assert qa['requires_actual_output_inspection'] is True
    assert {'COMMERCE_FIRST_SCAN','PRODUCT_IDENTITY','VISIBLE_COPY_ACCURACY','COMPOSITION_CROP','MATERIAL_PHYSICS','ARTIFACT_SCAN','PLATFORM_READY'} <= ids
    assert 'EXPLICIT_POST_COMPOSITE_IF_NOW_JUSTIFIED' in qa['repair_routes']


def test_product_presence_is_not_globally_forced_by_commerce_authority():
    bundle=_bundle('')
    bundle['visible_copy_block']={}
    bundle['design_card']['product_presence']={'planning_state':'FORBIDDEN','production_state':'ABSENT'}
    out=apply_commercial_operator_density_authority(bundle,{'asset_id':'IMG-05'})
    assert out['design_card']['product_presence']['planning_state']=='FORBIDDEN'
    qa={row['id']:row for row in out['commercial_visual_qa_contract']['checks']}
    assert qa['PRODUCT_IDENTITY']['required'] is False
    assert out['commercial_authority']['product_presence_rule'].startswith('Per-asset Art Direction')


def test_bilingual_production_semantics_do_not_leak_delivery_language_into_english_prompt():
    bundle=_bundle()
    asset={
        'asset_id':'IMG-06',
        'visible_copy':{'target_market_copy':'KAWAL MINYAK. KEKALKAN HIDRASI.'},
        'asset_art_direction':{
            'typography':{'cn':'深绿高对比无衬线，两行。','en':'Forest-green high-contrast sans serif, two lines.'}
        },
    }
    out=apply_commercial_operator_density_authority(bundle,asset)
    assert 'Forest-green high-contrast sans serif, two lines.' in out['model_prompt_en']
    assert '深绿高对比无衬线' not in out['model_prompt_en']
    assert '深绿高对比无衬线，两行。' in out['model_prompt_cn']
    assert '控油，同时保持水润。' not in out['model_prompt_en']
