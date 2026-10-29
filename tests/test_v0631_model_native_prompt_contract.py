from __future__ import annotations

import re

from runtime.cbcc.prompt_compiler import compile_asset_prompt


def _base_asset(**overrides):
    asset={
        'asset_id':'AST-PROMPT-NATIVE-01',
        'asset_name':'Prompt native proof',
        'asset_type':'IMAGE',
        'surface':'GALLERY',
        'family':'PDP',
        'production_mode':'GENERATIVE_IMAGE',
        'product_fidelity':'REFERENCE_GUIDED',
        'consumer_question':'How should this feel at first scan?',
        'strategic_job':'Make the daily-use value immediately legible.',
        'belief_target':'Balanced daily care with credible evidence.',
        'incremental_information':'A clear balance relationship, not another packshot.',
        'art_direction_required':True,
        'product_presence':{
            'planning_state':'SUPPORTING',
            'production_state':'PRESENT',
            'product_role':'small supporting identity anchor',
            'scale_relationship':'about 28% of canvas height',
            'source_reference_role':'SUBJECT_REFERENCE',
        },
        'visible_copy':{
            'target_copy':'KAWAL MINYAK. KEKALKAN HIDRASI.',
            'delivery_translation':'控油，同时保持水润。',
        },
        'asset_art_direction':{
            'visual_objective':{'cn':'让消费者一眼理解日常油水平衡，而不是强攻祛痘。','en':'Make daily oil-and-hydration balance understandable at first scan, without aggressive acne-war imagery.'},
            'visual_carrier':'EDITORIAL_COMMERCE_IMAGE',
            'visual_language':{'cn':'克制的编辑型电商视觉，温暖象牙白底，深绿信息系统。','en':'Restrained editorial-commerce visual language on warm ivory with a forest-green information system.'},
            'creative_thesis':{'cn':'平衡而非强攻。','en':'Balance, not battle.'},
            'decisive_moment':{'cn':'视线先读到油水平衡关系，再看到产品作为身份锚点。','en':'The eye reads the oil-versus-hydration balance relationship first, then the product as an identity anchor.'},
            'subject':{'cn':'油水平衡的信息关系与少量产品锚点。','en':'An oil-and-hydration balance relationship with a small supporting product anchor.'},
            'composition_grammar':{'cn':'左侧信息主场，右下产品作为小锚点，不做左右五五分。','en':'Information-led field with a small product anchor in the lower-right; avoid an equal split.'},
            'spatial_rhythm':{'cn':'大留白、单一主焦点、两级信息层。','en':'Generous negative space, one primary focal point, two information levels.'},
            'layout_geometry':{'cn':'主信息占左侧约60%，产品锚点右下约28%画布高度。','en':'Primary information occupies roughly 60% of the left field; product anchor sits lower-right at about 28% of canvas height.'},
            'scale_depth':{'cn':'二维信息层为主，产品只提供轻微纵深。','en':'Primarily a flat information plane with only slight depth from the supporting product.'},
            'focal_path':{'cn':'主命题 → 平衡证据 → 产品身份。','en':'main proposition → balance evidence → product identity'},
            'negative_space':{'cn':'顶部与左下保留干净留白。','en':'Keep clean negative space at the top and lower-left.'},
            'product_occupancy':'28% canvas height',
            'evidence_hierarchy':{'cn':'第一层油水平衡，第二层配方证据，第三层产品身份。','en':'Level 1: oil/hydration balance; level 2: formula evidence; level 3: product identity.'},
            'camera_or_view':'eye-level front / subtle 5-degree three-quarter view',
            'focal_length_mm':'85mm full-frame equivalent',
            'focus_dof':'label plane sharp; moderate depth of field',
            'lighting':{'key':'large soft key 45 degrees front-side-above','fill':'white bounce','negative_fill':'narrow negative fill for tube edge','cct':'5000K starting point','exposure_ratio_plan':'about 2:1 starting contrast, lock after reference frame'},
            'cmf':{'material':'matte flexible tube + transparent pump','surface_behavior':'truthful matte body and controlled transparent-pump highlight'},
            'palette_hex':['#F6F4EE','#0B3B32','#DCE7E0','#1C2D29'],
            'copy_zone':{'cn':'左侧主信息区，避开产品轮廓。','en':'Main typography zone on the left, clear of the product silhouette.'},
            'typography':{'cn':'深绿无衬线，标题强、说明轻。','en':'Forest-green sans serif; strong headline, lighter explanatory tier.'},
            'copy_render_mode':'MODEL_RENDER',
            'output_spec':'1600×1600 px, 1:1, sRGB, mobile-first TikTok Shop Malaysia',
            'post_look':{'cn':'自然、克制、低塑料感，不加假性实验室光效。','en':'Natural, restrained finish with low plasticity and no fake laboratory glow.'},
            'product_presence':{
                'planning_state':'SUPPORTING','production_state':'PRESENT',
                'product_role':'small supporting identity anchor','scale_relationship':'about 28% of canvas height',
                'source_reference_role':'SUBJECT_REFERENCE',
            },
        },
        'approved_visual_elements':['verified formula evidence','clean information relationship'],
        'precision_boundaries':['no invented tests or certifications'],
        'editable_layer_contract':{'editable_layers':['background','information graphics','copy'],'frozen_layers':['verified product facts']},
    }
    asset.update(overrides)
    return asset


def _compile(asset):
    return compile_asset_prompt(
        asset,
        product={'name':'K01','verified_facts':['30g gel']},
        target={'market':'MY','platform_family':'TikTok Shop','site':'MY','category':'skincare'},
        culture={},
        language_contract={'primary_locale':'ms-MY','delivery_locale':'zh-CN'},
        locale_profiles={},
        photography=None,
        strategy_authority=None,
        source_product_assets=[],
    )


def test_english_model_prompt_is_language_pure_and_not_runtime_contract_prose():
    out=_compile(_base_asset())
    en=out['model_prompt_en']
    assert not re.search(r'[\u3400-\u9fff]',en)
    lower=en.lower()
    for forbidden in ['deterministic','renderer recipe','renderer layer','machine contract','post-layout','prompt consumption audit']:
        assert forbidden not in lower
    assert out['prompt_en']==en
    assert out['status']=='MODEL_NATIVE_PROMPT_READY'
    assert out['prompt_consumption_audit']['status']=='PASS'


def test_exact_market_copy_can_be_model_rendered_without_chinese_delivery_translation_leaking():
    out=_compile(_base_asset())
    assert 'KAWAL MINYAK. KEKALKAN HIDRASI.' in out['model_prompt_en']
    assert '控油，同时保持水润。' not in out['model_prompt_en']
    assert out['visible_copy_block']['delivery_translation_zh']=='控油，同时保持水润。'
    assert out['production_assembly_notes']['copy_render_mode']=='MODEL_RENDER'


def test_concrete_pixel_parameters_are_projected_not_generic_field_names():
    out=_compile(_base_asset())
    joined=out['model_prompt_en']
    for value in ['1600×1600','85mm','28%','#F6F4EE','#0B3B32','5000K','2:1','lower-right']:
        assert value in joined
    assert out['prompt_consumption_audit']['status']=='PASS'


def test_chinese_only_art_direction_does_not_masquerade_as_english_prompt():
    asset=_base_asset()
    asset['asset_art_direction']=dict(asset['asset_art_direction'])
    asset['asset_art_direction']['composition_grammar']='左侧证据，右侧留白，产品仅小锚点'
    out=_compile(asset)
    assert not re.search(r'[\u3400-\u9fff]',out['model_prompt_en'])
    assert out['prompt_consumption_audit']['status']=='INCOMPLETE'
    assert 'composition' in out['prompt_consumption_audit']['missing_decisions']
    assert out['status']=='BILINGUAL_RENDER_SEMANTICS_REQUIRED'


def test_copy_render_mode_is_not_silently_forced_to_post_composite():
    asset=_base_asset()
    asset['asset_art_direction']=dict(asset['asset_art_direction'])
    asset['asset_art_direction'].pop('copy_render_mode')
    out=_compile(asset)
    assert out['status']=='COPY_RENDER_MODE_REQUIRED'
    assert 'copy_render_mode' in out['prompt_consumption_audit']['missing_decisions']
    assert 'deterministic' not in out['model_prompt_en'].lower()


def test_graphic_asset_does_not_receive_fake_shutter_or_iso():
    asset=_base_asset(production_mode='GRAPHIC_DESIGN')
    art=dict(asset['asset_art_direction'])
    art.pop('camera_or_view',None); art.pop('focal_length_mm',None); art.pop('focus_dof',None); art.pop('lighting',None)
    art['visual_carrier']='GRAPHIC_INFORMATION_DESIGN'
    art['model_prompt_en']='Create a 1600×1600 mobile-first graphic information design. Use a warm-ivory field, forest-green hierarchy, a two-tier evidence relationship, generous negative space, and the exact market headline “KAWAL MINYAK. KEKALKAN HIDRASI.” Keep verified facts truthful and avoid invented scientific symbols.'
    art['model_prompt_cn']='创建 1600×1600 移动端优先的信息图形资产。使用暖象牙白底、深绿信息层级、两级证据关系与大留白，准确呈现马来文标题“KAWAL MINYAK. KEKALKAN HIDRASI.”；保持事实真实，不添加虚构科学符号。'
    asset['asset_art_direction']=art
    out=_compile(asset)
    assert 'Shutter' not in out['model_prompt_en'] and 'ISO' not in out['model_prompt_en']


def test_video_prompt_consumes_timing_motion_and_shot_sequence():
    asset=_base_asset(asset_id='VID-NATIVE-01',asset_type='VIDEO',surface='SHORT_VIDEO',production_mode='GENERATIVE_VIDEO')
    art=dict(asset['asset_art_direction'])
    art.update({
        'visual_carrier':'SHORT_VIDEO',
        'motion_timing':'18 seconds total; 0–3s hook, 3–11s proof/use, 11–16s product/result, 16–18s CTA hold',
        'shot_sequence':'macro pump detail → lightweight application gesture → balanced-skin routine context → clean product close',
        'camera_motion':'slow controlled push-in on hook; locked-off proof shot; gentle 10-degree arc on product close',
        'transition_audio':'hard visual cut at 3s, soft match cut at 11s; clean rhythmic audio bed, no medical SFX',
        'output_spec':'1080×1920, 9:16, sRGB, TikTok Shop Malaysia',
    })
    asset['asset_art_direction']=art
    out=_compile(asset)
    for token in ['18 seconds','0–3s','macro pump detail','slow controlled push-in','1080×1920']:
        assert token in out['model_prompt_en']


def test_forbidden_product_presence_remains_absent_in_model_and_production_layers():
    asset=_base_asset()
    art=dict(asset['asset_art_direction'])
    art['product_presence']={'planning_state':'FORBIDDEN','production_state':'ABSENT','source_reference_role':'TRUTH_REFERENCE_ONLY'}
    art['subject']={'cn':'纯信息关系。','en':'A pure information relationship with no product subject.'}
    asset['asset_art_direction']=art
    asset['product_presence']=art['product_presence']
    out=_compile(asset)
    assert 'must not appear in frame' in out['model_prompt_en']
    assert not any('product_subject' in str(x) or 'locked_product' in str(x) for x in out['production_assembly_notes']['layer_plan'])
