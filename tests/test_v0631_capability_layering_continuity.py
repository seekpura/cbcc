from __future__ import annotations

from runtime.cbcc.prompt_compiler import compile_asset_prompt


def test_inclusive_human_photography_remains_model_facing_when_people_are_present():
    asset={
        'asset_id':'AST-HUMAN','surface':'GALLERY','family':'VISUAL','asset_type':'IMAGE','production_mode':'GENERATIVE_IMAGE',
        'decision_intent':'USAGE','consumer_question':'How does this fit a real daily routine?','strategic_job':'Show credible everyday use.',
        'product_fidelity':'REFERENCE_GUIDED','product_presence':{'planning_state':'SUPPORTING','production_state':'PRESENT','source_reference_role':'SUBJECT_REFERENCE'},
        'asset_art_direction':{
            'visual_objective':{'cn':'展示真实日常使用。','en':'Show credible everyday use in a real routine.'},
            'visual_carrier':'HUMAN_USAGE_IMAGE','visual_language':{'cn':'自然生活方式摄影。','en':'Natural lifestyle photography.'},
            'subject':{'cn':'成年马来西亚/东南亚用户与产品。','en':'An adult Malaysian / Southeast Asian user with the product.'},
            'action':{'cn':'轻柔涂抹。','en':'Gently applying the product.'},
            'composition_grammar':{'cn':'人物动作主导，产品辅助。','en':'Human action leads; product supports.'},
            'copy_render_mode':'NO_VISIBLE_COPY','output_spec':'1600×1600 px, 1:1, sRGB',
            'product_presence':{'planning_state':'SUPPORTING','production_state':'PRESENT','source_reference_role':'SUBJECT_REFERENCE'},
        },
    }
    strategy={'sections':{'05_visual_photography_strategy':{
        'camera':{'focal_length_mm':'50–85mm equivalent'},'lens':{'focal_length_mm':'50–85mm equivalent'},
        'inclusive_photography':{
            'skin_tone_exposure':{
                'metering_priority':'protect deep-skin shadow detail without flattening highlights',
                'exposure_compensation':'set from skin reference, not background average',
                'reflector_diffusion':'large soft source plus controlled bounce/reflector'
            },
            'representation':'adult Malaysian / Southeast Asian representation without stereotyping'
        },
        'photography_rationale':'Natural perspective and truthful skin rendering support daily-use credibility.'
    }}}
    out=compile_asset_prompt(
        asset,{'name':'K01','category':'skincare'}, {'market':'MY','platform_family':'TikTok Shop'},
        {'casting_constraints':['adult Malaysian / Southeast Asian representation without stereotyping']},
        {'primary_locale':'ms-MY','delivery_locale':'zh-CN'}, {}, None, strategy, []
    )
    en=out['prompt_en']
    assert 'Human representation:' in en
    assert 'deep-skin' in en
    assert 'reflector' in en.lower() or 'bounce' in en.lower()
    assert '50–85mm equivalent' in en


def test_locked_pixel_and_source_binding_remain_strict_but_outside_model_prompt():
    asset={
        'asset_id':'AST-LOCKED','surface':'GALLERY','family':'VISUAL','asset_type':'IMAGE','production_mode':'LOCKED_SOURCE_COMPOSITE',
        'decision_intent':'IDENTIFY','consumer_question':'What exactly will I receive?','strategic_job':'Show exact package identity.',
        'product_fidelity':'LOCKED_PIXEL','product_presence':{'planning_state':'REQUIRED','production_state':'PRESENT','source_reference_role':'LOCKED_SOURCE_LAYER'},
        'asset_art_direction':{
            'visual_objective':{'cn':'清楚展示真实包装身份。','en':'Show the exact package identity clearly.'},
            'visual_carrier':'LOCKED_SOURCE_COMPOSITE','visual_language':{'cn':'干净商品识别图。','en':'Clean product-identification visual.'},
            'subject':{'cn':'用户提供的真实产品图层。','en':'The user-supplied real product layer.'},
            'composition_grammar':{'cn':'真实产品层为主，背景与信息层辅助。','en':'Real product layer leads; background and information layer support.'},
            'copy_render_mode':'NO_VISIBLE_COPY','output_spec':'1600×1600 px, 1:1, sRGB',
            'product_presence':{'planning_state':'REQUIRED','production_state':'PRESENT','source_reference_role':'LOCKED_SOURCE_LAYER'},
        },
    }
    out=compile_asset_prompt(
        asset,{'name':'K01','category':'skincare'}, {'market':'MY','platform_family':'TikTok Shop'}, {},
        {'primary_locale':'ms-MY','delivery_locale':'zh-CN'}, {}, None, None,
        [{'asset_id':'P1','path':'2.png','sha256':'abc','pixel_lock':True,'fidelity_mode':'LOCKED_PIXEL'}]
    )
    assert 'LOCKED_PIXEL' not in out['prompt_en']
    notes=out['production_assembly_notes']
    assert notes['product_fidelity']=='LOCKED_PIXEL'
    assert notes['product_presence']['source_reference_role']=='LOCKED_SOURCE_LAYER'
    assert notes['source_product_bindings']
    assert any('locked' in str(x).lower() or 'product' in str(x).lower() for x in notes['layer_plan'])
