from cbcc.prompt_compiler import compile_asset_prompt


def _strategy():
    return {
        'sections': {
            '05_visual_photography_strategy': {
                'composition': {'grammar': 'editorial negative-space portrait'},
                'camera': {},
                'lens': {
                    'focal_length_by_job': {
                        'identity_or_proof': '70–105mm equivalent',
                        'context_or_use': '50–85mm equivalent',
                    }
                },
                'lighting_framework': {
                    'key': 'large soft diffusion from camera-left/front',
                    'fill': 'neutral white reflector / bounce as needed',
                    'negative_fill': 'optional, only if facial/product separation needs it',
                    'highlight_policy': 'protect oily/specular facial highlights without underexposing skin',
                },
                'color_management': {'output_space': 'sRGB', 'white_balance': 'warm-neutral and skin-faithful'},
                'inclusive_photography': {},
                'asset_parameter_reasoning': [],
            }
        }
    }


def _human_asset():
    return {
        'asset_id': 'HUMAN-01',
        'asset_name': 'Humidity skin insight',
        'asset_type': 'IMAGE',
        'surface': 'GALLERY',
        'family': 'VISUAL',
        'consumer_question': 'Why does oily skin still need hydration?',
        'strategic_job': 'make the hydration tension legible in a humid-market context',
        'incremental_information': 'oily skin still needs hydration',
        # This test explicitly selects a real-photo route. Human presence alone must not imply it.
        'production_mode': 'REAL_PHOTO',
        'capture_mode': 'REAL_PHOTO',
        'creative_brief': {
            'subject': 'adult Malaysian / Southeast Asian model, cheek/jaw crop',
            'human': 'authentic adult human skin with visible pores and natural sebum highlights',
            'composition': 'editorial portrait crop with large negative space',
            'lighting': 'soft natural-window character with controlled highlights',
        },
        'visual_production_signature': {'context_role': 'human use / skin context'},
        'product_presence': {'planning_state': 'OPTIONAL'},
        'product_fidelity': 'REFERENCE_GUIDED',
        'editable_layer_contract': {'editable_layers': ['background','human_context'], 'frozen_layers': ['verified_product_facts']},
    }


def test_explicit_photo_human_asset_inherits_context_lens_and_p0_photo_execution():
    bundle = compile_asset_prompt(
        _human_asset(),
        {'name':'Test Product','category':'beauty'},
        {'market':'MY','platform_family':'TIKTOK_SHOP','site':'MY'},
        {'casting_constraints':['adult Malaysian / Southeast Asian representation without stereotyping'], 'intersectionality':{'age':'adult','geography':'Malaysia'}},
        {'delivery_locale':'zh-CN','primary_locale':'ms-MY','visible_copy_locales':['ms-MY']},
        strategy_authority=_strategy(),
        source_product_assets=[{'asset_id':'P1','path':'2.png','sha256':'abc','pixel_lock':False,'fidelity_mode':'REFERENCE_GUIDED'}],
    )
    card=bundle['design_card']
    assert card['composition_camera']['focal_length_mm']=='50–85mm equivalent'
    inc=card['inclusive_photography']
    assert 'reflector_diffusion' in inc['skin_tone_exposure']
    assert 'deep-skin' in inc['skin_tone_exposure']['metering_priority']
    assert 'exposure_compensation' in inc['skin_tone_exposure']
    assert '50–85mm equivalent' in bundle['prompt_en']
    assert '[INCLUSIVE HUMAN PHOTOGRAPHY]' in bundle['prompt_en']
    assert 'neutral/white reflector' in bundle['prompt_en']
    assert '深肤色' in bundle['prompt_cn'] or '肤色' in bundle['prompt_cn']
    assert bundle['prompt_consumption_audit']['status']=='PASS', bundle['prompt_consumption_audit']
    assert bundle['qa_target_contract']['relevant_parameter_trace_complete'] is True


def test_graphic_asset_does_not_reinflate_irrelevant_human_photography_toolbox():
    asset={
        'asset_id':'GRAPHIC-01','asset_name':'Formula architecture','asset_type':'IMAGE','surface':'GALLERY','family':'VISUAL',
        'consumer_question':'How is the formula structured?','strategic_job':'show formula relationship','incremental_information':'two-axis formula relationship',
        'production_mode':'GRAPHIC_DESIGN',
        'creative_brief':{'subject':'typographic evidence relationship','composition':'two continuous information fields'},
        'visual_production_signature':{'context_role':'evidence graphics'},
        'product_presence':{'planning_state':'OPTIONAL'},'product_fidelity':'REFERENCE_GUIDED',
    }
    bundle=compile_asset_prompt(
        asset, {'name':'Test Product','category':'beauty'},
        {'market':'MY','platform_family':'TIKTOK_SHOP','site':'MY'}, {},
        {'delivery_locale':'zh-CN','primary_locale':'ms-MY','visible_copy_locales':['ms-MY']},
        strategy_authority=_strategy(),
    )
    assert '[INCLUSIVE HUMAN PHOTOGRAPHY]' not in bundle['prompt_en']
    assert '50–85mm equivalent' not in bundle['prompt_en']
    assert bundle['prompt_consumption_audit']['status']=='PASS', bundle['prompt_consumption_audit']
