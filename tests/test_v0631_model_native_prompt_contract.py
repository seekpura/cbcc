from __future__ import annotations

import re

from runtime.cbcc.prompt_compiler import compile_asset_prompt


def _asset():
    return {
        'asset_id':'AST-NATIVE','asset_name':'Native prompt','asset_type':'IMAGE','surface':'GALLERY','family':'PDP',
        'production_mode':'GENERATIVE_IMAGE','product_fidelity':'REFERENCE_GUIDED',
        'consumer_question':'How should this feel at first scan?','strategic_job':'Make balance immediately legible.',
        'visible_copy':{'target_copy':'KAWAL MINYAK. KEKALKAN HIDRASI.','delivery_translation':'控油，同时保持水润。'},
        'product_presence':{'planning_state':'SUPPORTING','production_state':'PRESENT','product_role':'small identity anchor','scale_relationship':'28% canvas height','source_reference_role':'SUBJECT_REFERENCE'},
        'asset_art_direction':{
            'visual_objective':{'cn':'让消费者一眼理解日常油水平衡。','en':'Make daily oil-and-hydration balance understandable at first scan.'},
            'visual_carrier':'EDITORIAL_COMMERCE_IMAGE',
            'visual_language':{'cn':'克制编辑型电商视觉。','en':'Restrained editorial-commerce visual language.'},
            'creative_thesis':{'cn':'平衡而非强攻。','en':'Balance, not battle.'},
            'subject':{'cn':'油水平衡关系和小型产品锚点。','en':'An oil-and-hydration balance relationship with a small product anchor.'},
            'composition_grammar':{'cn':'信息主场，产品右下小锚点。','en':'Information-led field with a small product anchor in the lower-right.'},
            'spatial_rhythm':{'cn':'大留白，两级信息。','en':'Generous negative space with two information levels.'},
            'layout_geometry':{'cn':'主信息约60%，产品约28%高度。','en':'Primary information occupies about 60% of the field; product is about 28% of canvas height.'},
            'scale_depth':{'cn':'二维信息为主，轻微产品纵深。','en':'Primarily flat information plane with slight product depth.'},
            'focal_path':{'cn':'主命题→证据→产品。','en':'proposition → evidence → product identity'},
            'negative_space':{'cn':'顶部和左下留白。','en':'Clean negative space at top and lower-left.'},
            'product_occupancy':'28% canvas height',
            'evidence_hierarchy':{'cn':'平衡→配方→产品身份。','en':'balance → formula evidence → product identity'},
            'camera_or_view':'eye-level front / subtle 5-degree three-quarter view','focal_length_mm':'85mm full-frame equivalent',
            'lens_family':'short telephoto product lens','working_distance':'1.0 m','camera_height':'8 cm above product-center height',
            'yaw_pitch_roll':{'yaw':'5 degrees','pitch':'-2 degrees','roll':'0 degrees'},'shot_size':'tight product portrait',
            'focus_plane':'front label plane','focus_dof':'f/8-equivalent label-sharp moderate depth of field',
            'lighting':{'key':'large 100 cm soft key 45 degrees front-side-above at 1.0 m','fill':'white bounce at half-key intensity','negative_fill':'narrow negative fill camera-right','cct':'5000K','white_balance':'5000K neutral WB','exposure_ratio_plan':'2:1','shadow_policy':'soft restrained contact shadow','highlight_policy':'protect white-pack highlights below clipping'},
            'prelight':'test frame to tune label highlight and pump reflection','color_management':'sRGB with neutral product-white match',
            'cmf':{'material':'matte flexible tube + transparent pump','surface_behavior':'controlled transparent-pump highlight'},
            'palette_hex':['#F6F4EE','#0B3B32','#DCE7E0','#1C2D29'],
            'copy_zone':{'cn':'左侧主信息区。','en':'Main typography zone on the left.'},
            'typography':{'cn':'深绿无衬线。','en':'Forest-green sans serif.'},
            'copy_render_mode':'MODEL_RENDER','output_spec':'1600×1600 px, 1:1, sRGB, TikTok Shop Malaysia',
            'post_look':{'cn':'自然克制。','en':'Natural restrained finish.'},
            'product_presence':{'planning_state':'SUPPORTING','production_state':'PRESENT','product_role':'small identity anchor','scale_relationship':'28% canvas height','source_reference_role':'SUBJECT_REFERENCE'},
        },
        'approved_visual_elements':['verified formula evidence'],'precision_boundaries':['no invented tests or certifications'],
        'editable_layer_contract':{'editable_layers':['background','information graphics','copy'],'frozen_layers':['verified product facts']},
    }


def _compile(asset):
    return compile_asset_prompt(asset,{'name':'K01'},{'market':'MY','platform_family':'TikTok Shop','site':'MY','category':'skincare'}, {}, {'primary_locale':'ms-MY','delivery_locale':'zh-CN'}, {}, None, None, [{'asset_id':'MASTER-FRONT','role':'FRONT','provider_asset_handle':'ref://master-front','sha256':'abc123','ingest_status':'HASH_VERIFIED_LOCAL'}])


def test_model_prompt_is_pure_and_parameter_complete_while_package_status_stays_compatible():
    out=_compile(_asset())
    assert out['status']=='CANONICAL_PROMPT_COMPILED_AGENT_AUTHORITY'
    assert out['model_prompt_status']=='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'
    en=out['model_prompt_en']
    assert not re.search(r'[\u3400-\u9fff]',en)
    for forbidden in ['deterministic','renderer recipe','renderer layer','machine contract','post-layout','prompt consumption audit']:
        assert forbidden not in en.lower()
    for value in ['1600×1600','85mm','28%','#F6F4EE','#0B3B32','5000K','2:1','lower-right','KAWAL MINYAK. KEKALKAN HIDRASI.']:
        assert value in en
    assert '控油，同时保持水润。' not in en
    assert out['visible_copy_block']['delivery_translation_zh']=='控油，同时保持水润。'
    assert out['production_assembly_notes']['copy_render_mode']=='MODEL_RENDER'
    assert out['prompt_consumption_audit']['status']=='PASS'


def test_chinese_only_semantics_are_not_mislabeled_as_english_ready():
    asset=_asset(); asset['asset_art_direction']=dict(asset['asset_art_direction'])
    asset['asset_art_direction']['composition_grammar']='左侧证据，右侧留白，产品仅小锚点'
    out=_compile(asset)
    assert not re.search(r'[\u3400-\u9fff]',out['model_prompt_en'])
    assert out['model_prompt_status']=='BILINGUAL_RENDER_SEMANTICS_REQUIRED'
    assert 'composition' in out['prompt_consumption_audit']['missing_decisions']


def test_copy_render_route_is_agent_decision_not_global_post_composite_default():
    asset=_asset(); asset['asset_art_direction']=dict(asset['asset_art_direction']); asset['asset_art_direction'].pop('copy_render_mode')
    out=_compile(asset)
    assert out['model_prompt_status']=='COPY_RENDER_MODE_REQUIRED'
    assert out['production_assembly_notes']['copy_render_mode']=='UNRESOLVED_AGENT_DECISION'
    assert 'deterministic' not in out['model_prompt_en'].lower()


def test_forbidden_product_stays_absent_in_prompt_and_layer_plan():
    asset=_asset(); art=dict(asset['asset_art_direction'])
    art['product_presence']={'planning_state':'FORBIDDEN','production_state':'ABSENT','source_reference_role':'TRUTH_REFERENCE_ONLY'}
    art['subject']={'cn':'纯信息关系。','en':'A pure information relationship with no product subject.'}
    asset['asset_art_direction']=art; asset['product_presence']=art['product_presence']
    out=_compile(asset)
    assert 'must not appear in frame' in out['model_prompt_en']
    assert not any('product_subject' in str(x) or 'locked_product' in str(x) for x in out['production_assembly_notes']['layer_plan'])


def test_video_prompt_consumes_motion_timing_and_shot_sequence():
    asset=_asset(); asset.update({'asset_id':'VID-NATIVE','asset_type':'VIDEO','surface':'SHORT_VIDEO','production_mode':'GENERATIVE_VIDEO'})
    art=dict(asset['asset_art_direction']); art.update({
        'visual_carrier':'SHORT_VIDEO','output_spec':'1080×1920, 9:16, sRGB, TikTok Shop Malaysia',
        'motion_timing':'18 seconds total; 0–3s hook, 3–11s proof/use, 11–16s product/result, 16–18s CTA hold',
        'shot_sequence':'macro pump detail → application gesture → routine context → clean product close',
        'camera_motion':'slow controlled push-in on hook; locked proof shot; gentle 10-degree arc on product close',
        'transition_audio':'hard cut at 3s; soft match cut at 11s; clean rhythmic audio bed',
    }); asset['asset_art_direction']=art
    out=_compile(asset)
    for token in ['1080×1920','18 seconds','0–3s','macro pump detail','slow controlled push-in']:
        assert token in out['model_prompt_en']
