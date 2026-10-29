from __future__ import annotations

from runtime.cbcc.prompt_compiler import compile_asset_prompt


def _compile(asset):
    return compile_asset_prompt(
        asset,
        {'name':'KIYUU K01'},
        {'market':'MY','platform_family':'TikTok Shop','site':'MY','category':'skincare'},
        {},
        {'primary_locale':'ms-MY','delivery_locale':'zh-CN'},
        {}, None, None, [],
    )


def _photo_asset():
    return {
        'asset_id':'AST-CLOSURE','asset_name':'Locked composite hero','asset_type':'IMAGE','surface':'GALLERY','family':'PDP',
        'production_mode':'GENERATIVE_IMAGE','product_fidelity':'LOCKED_SOURCE_COMPOSITE','art_direction_required':True,
        'consumer_question':'Why should this feel balanced rather than harsh?','strategic_job':'Make balance legible.',
        'visible_copy':{},
        'product_presence':{
            'planning_state':'HERO_REQUIRED','production_state':'PRESENT','product_role':'locked real-product hero',
            'scale_relationship':'68% frame height','source_reference_role':'LOCKED_SOURCE_LAYER',
        },
        'asset_art_direction':{
            'visual_objective':{'cn':'把油脂护理与轻盈补水平衡做成一个可信的产品英雄画面。','en':'Turn oil care and lightweight hydration into one credible product-hero composition.'},
            'visual_carrier':'PHOTOGRAPHIC_LOCKED_SOURCE_COMPOSITE',
            'visual_language':{'cn':'克制但有空间张力的编辑商业摄影。','en':'Restrained editorial commercial photography with spatial tension.'},
            'creative_thesis':{'cn':'平衡来自材质、空间与光比，不靠装饰。','en':'Balance is expressed through material, space and lighting ratio rather than decoration.'},
            'subject':{'cn':'真实锁定软管与外盒作为最终英雄主体。','en':'The locked real tube and carton are the final hero subject.'},
            'composition_grammar':{'cn':'非对称近大远小的双层产品关系。','en':'Asymmetric two-layer product relationship with a larger foreground tube and smaller rear carton.'},
            'layout_geometry':{'cn':'软管中心在画面x=68%、y=54%，外盒后移至x=78%、y=47%。','en':'Tube center at x=68%, y=54%; carton recedes to x=78%, y=47%.'},
            'scale_depth':{'cn':'软管约68%画高；外盒约54%画高并后退约8%视觉深度。','en':'Tube about 68% frame height; carton about 54% frame height and roughly 8% farther back in visual depth.'},
            'product_occupancy':'68% frame height',
            'focal_path':{'cn':'产品轮廓→泵头高光→左侧证据区。','en':'product silhouette → pump highlight → evidence field on the left'},
            'negative_space':{'cn':'左侧约34%连续负空间，不切成卡片。','en':'about 34% continuous negative space on the left, not broken into cards'},
            'copy_zone':{'cn':'左侧x=8–38%、y=18–74%为连续文字安全区。','en':'continuous typography-safe zone at x=8–38%, y=18–74%'},
            'evidence_hierarchy':{'cn':'产品身份第一，平衡命题第二，浓度证据第三。','en':'product identity first, balance proposition second, concentration evidence third'},
            'palette_hex':['#F6F3EC','#0B3B31','#AAB9AF'],
            'cmf':{'material':'matte white flexible tube; clear pump; warm mineral-plaster receiving surface'},
            'material_response':'matte tube receives broad low-contrast highlight; clear pump keeps one narrow controlled specular edge; receiving surface stays low sheen',
            'post_look':{'cn':'中性偏暖、低饱和，白色包装高光保留层次。','en':'neutral-warm low-saturation finish with preserved highlight separation on the white pack'},
            'camera_or_view':'eye-level slight three-quarter product view',
            'focal_length_mm':'95mm full-frame equivalent',
            'lens_family':'short telephoto product lens',
            'working_distance':'1.2 m',
            'camera_height':'12 cm above product-center height',
            'yaw_pitch_roll':{'yaw':'5 degrees right','pitch':'-3 degrees','roll':'0 degrees'},
            'shot_size':'tight product portrait with full pack uncropped',
            'focus_plane':'front label plane extending through pump shoulder',
            'aperture':'f/8 equivalent depth-of-field intent',
            'key_light':'120 cm diffused key, 45 degrees camera-left and 35 degrees above, 1.1 m from subject plane',
            'fill_light':'white bounce camera-right at roughly half key intensity',
            'negative_fill':'narrow black flag behind camera-right to hold the tube edge',
            'rim_light':'no separate rim; preserve natural pump edge from key',
            'modifier_geometry':'120 cm diffusion frame plus white bounce card',
            'light_distance':'key modifier approximately 1.1 m from subject plane',
            'cct':'5200K',
            'white_balance':'5200K neutral WB target',
            'light_ratio':'2:1 key-to-fill starting ratio',
            'shadow_policy':'soft 8–12% density contact shadow falling slightly rear-right with a feathered edge',
            'highlight_policy':'protect white-tube highlights below clipping; keep clear-pump specular narrow and readable',
            'exposure_policy':'meter for the white tube and preserve about 0.7 stop highlight headroom',
            'reflection_control':'flag uncontrolled frontal reflections; retain one narrow pump highlight',
            'polarization':'test CPL only if it does not erase the clear-pump material cue',
            'prelight':'make a product-envelope test plate first and tune contact shadow/reflection before final generation',
            'color_management':'sRGB output with neutral-WB product match and no green cast on the white tube',
            'copy_render_mode':'NO_VISIBLE_COPY',
            'output_spec':'1600×1600 px, 1:1, sRGB, TikTok Shop Malaysia',
            'product_presence':{
                'planning_state':'HERO_REQUIRED','production_state':'PRESENT','product_role':'locked real-product hero',
                'scale_relationship':'68% frame height','source_reference_role':'LOCKED_SOURCE_LAYER',
            },
        },
        'approved_visual_elements':['warm mineral-plaster receiving surface','subtle sage environmental accent'],
        'precision_boundaries':['do not redraw or retype the locked product','no invented gel texture'],
        'editable_layer_contract':{'editable_layers':['environment plate','contact shadow','copy'],'frozen_layers':['locked product pixels']},
    }


def test_locked_source_composite_prompt_consumes_full_execution_program():
    out=_compile(_photo_asset())
    assert out['status']=='CANONICAL_PROMPT_COMPILED_AGENT_AUTHORITY'
    assert out['model_prompt_status']=='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'
    closure=out['production_parameter_closure']
    assert closure['status']=='PASS'
    assert closure['locked_source_final_composite_instruction'] is True
    en=out['model_prompt_en']
    for token in [
        '95mm','1.2 m','12 cm','5 degrees right','-3 degrees','f/8','120 cm','1.1 m','5200K','2:1',
        '8–12%','0.7 stop','#F6F3EC','#0B3B31','68% frame height','x=68%','x=8–38%','product silhouette',
    ]:
        assert token in en
    assert 'final composite' in en.lower()
    assert 'do not render, redraw or substitute the product itself' in en.lower()


def test_missing_photo_execution_depth_is_not_prompt_ready():
    asset=_photo_asset()
    art=dict(asset['asset_art_direction'])
    art.pop('working_distance')
    art.pop('prelight')
    art.pop('highlight_policy')
    asset['asset_art_direction']=art
    out=_compile(asset)
    assert out['status']=='CANONICAL_PROMPT_COMPILED_AGENT_AUTHORITY'
    assert out['model_prompt_status']=='ART_DIRECTION_EXECUTION_DEPTH_REQUIRED'
    missing=out['production_parameter_closure']['missing_required_parameters']
    assert 'working_distance' in missing
    assert 'prelight' in missing
    assert 'highlight_policy' in missing
    assert out['production_parameter_closure']['model_generation_blocking'] is True


def test_non_photographic_information_asset_does_not_get_fake_camera_requirements():
    asset={
        'asset_id':'AST-GRAPHIC','asset_name':'Formula information','asset_type':'IMAGE','surface':'GALLERY',
        'production_mode':'GENERATIVE_IMAGE','product_fidelity':'REFERENCE_GUIDED','art_direction_required':True,
        'visible_copy':{},
        'product_presence':{'planning_state':'FORBIDDEN','production_state':'ABSENT','source_reference_role':'TRUTH_REFERENCE_ONLY'},
        'asset_art_direction':{
            'visual_objective':{'cn':'用信息关系解释配方平衡。','en':'Explain formula balance through information relationships.'},
            'visual_carrier':'GRAPHIC_INFORMATION_SYSTEM',
            'composition_grammar':{'cn':'斜向证据轴而非左右双栏。','en':'A diagonal evidence axis rather than a left/right split.'},
            'layout_geometry':{'cn':'主数字沿左下到右上的12度轴线分布。','en':'Primary values progress on a 12-degree axis from lower-left to upper-right.'},
            'scale_depth':{'cn':'三层二维信息深度。','en':'Three levels of flat information depth.'},
            'focal_path':{'cn':'命题→两个主数字→辅助解释。','en':'thesis → two primary values → supporting explanation'},
            'negative_space':{'cn':'右上保留呼吸区。','en':'breathing space in the upper-right'},
            'palette_hex':['#F6F3EC','#0B3B31','#AAB9AF'],
            'material_response':'flat editorial fields with one translucent vellum-like evidence layer',
            'post_look':{'cn':'印刷编辑感、无摄影模拟。','en':'print-editorial finish with no photographic simulation'},
            'copy_render_mode':'NO_VISIBLE_COPY','output_spec':'1600×1600 px, 1:1, sRGB',
            'product_presence':{'planning_state':'FORBIDDEN','production_state':'ABSENT','source_reference_role':'TRUTH_REFERENCE_ONLY'},
        },
    }
    out=_compile(asset)
    assert out['model_prompt_status']=='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'
    closure=out['production_parameter_closure']
    assert closure['route']['photographic'] is False
    assert not any(x in closure['required_groups'] for x in ('camera_geometry','focus_exposure','lighting_geometry'))
