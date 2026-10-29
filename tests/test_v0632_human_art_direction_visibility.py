from __future__ import annotations

import json
from pathlib import Path

from cbcc.delivery_html import _formal_asset_dir


def test_human_asset_workspace_exposes_execution_depth_and_closure(tmp_path: Path):
    package=tmp_path/'delivery'; asset=package/'artifacts'/'asset_packages'/'AST-VISIBLE'; asset.mkdir(parents=True)
    (asset/'00_asset_manifest.yaml').write_text('asset_name: Hero\nasset_type: IMAGE\nsurface: GALLERY\ndecision_intent: IDENTIFY\n',encoding='utf-8')
    design={
        'asset_name':'Hero','asset_type':'IMAGE','surface':'GALLERY',
        'commerce_task':{'decision_intent':'IDENTIFY','consumer_question':'What is this?','reason_to_exist':'建立第一眼身份与购买理由。'},
        'visual_narrative':{'what_must_be_visible':'商品身份、空间张力与平衡命题。'},
        'product_identity':{'product_fidelity':'LOCKED_SOURCE_COMPOSITE'},
        'agent_art_direction':{
            'visual_carrier':'PHOTOGRAPHIC_LOCKED_SOURCE_COMPOSITE','decisive_moment':'泵头高光引导到证据区',
            'subject':'真实锁定商品','composition_grammar':'asymmetric depth stack','layout_geometry':'tube x=68%, carton x=78%',
            'scale_depth':'tube 68% height; carton 54% height, 8% farther back','product_occupancy':'68% frame height',
            'focal_path':'silhouette → pump highlight → evidence','negative_space':'left 34% continuous field',
            'evidence_hierarchy':'identity → proposition → concentration proof','copy_zone':'x=8–38%, y=18–74%',
            'focal_length_mm':'95mm full-frame equivalent','lens_family':'short telephoto product lens','working_distance':'1.2 m',
            'camera_height':'12 cm above product center','yaw_pitch_roll':{'yaw':'5°','pitch':'-3°','roll':'0°'},'shot_size':'tight product portrait',
            'focus_plane':'front label through pump shoulder','aperture':'f/8 equivalent','key_light':'120 cm key 45° left/35° above at 1.1 m',
            'fill_light':'white bounce at half key','negative_fill':'black flag camera-right','modifier_geometry':'120 cm diffusion + white bounce','light_distance':'1.1 m',
            'cct':'5200K','white_balance':'5200K neutral','light_ratio':'2:1','exposure_policy':'protect 0.7 stop highlight headroom',
            'shadow_policy':'8–12% soft rear-right contact shadow','highlight_policy':'white tube below clipping','reflection_control':'retain narrow pump highlight',
            'polarization':'CPL test only if material remains truthful','prelight':'product-envelope test plate','cmf':{'surface':'warm mineral plaster'},
            'material_response':'matte tube broad highlight, clear pump narrow specular','palette_hex':['#F6F3EC','#0B3B31'],'color_management':'sRGB neutral product-white match',
            'post_look':'neutral-warm low saturation','deliberate_difference':'opening large depth-led identity hero','design_why':'先用真实体量与光线建立信任，再让证据进入视线。',
        },
    }
    (asset/'12_design_card.json').write_text(json.dumps(design,ensure_ascii=False),encoding='utf-8')
    closure={
        'status':'PASS','route':{'photographic':True,'video':False},
        'selected_parameters':{'focal_length':'95mm full-frame equivalent','working_distance':'1.2 m','cct':'5200K','light_ratio':'2:1','prelight':'product-envelope test plate'},
        'missing_required_parameters':[],'english_render_semantics_missing_for':[],'locked_source_final_composite_instruction':True,
    }
    (asset/'13_prompt_contract.json').write_text(json.dumps({'production_parameter_closure':closure},ensure_ascii=False),encoding='utf-8')
    (asset/'15_production_assembly_notes.json').write_text(json.dumps({'copy_render_mode':'NO_VISIBLE_COPY','product_fidelity':'LOCKED_SOURCE_COMPOSITE'},ensure_ascii=False),encoding='utf-8')
    (asset/'05_prompt_CN.txt').write_text('中文模型提示词',encoding='utf-8')
    (asset/'06_prompt_EN.txt').write_text('English model prompt',encoding='utf-8')

    row=_formal_asset_dir(asset,package)
    body='\n'.join(str(v.get('html') or '') for v in row['views'])
    for token in ['1.2 m','12 cm above product center','5°','f/8 equivalent','120 cm key','5200K','2:1','0.7 stop','8–12%','#F6F3EC','product-envelope test plate','参数闭环状态','锁图复合底片闭环','opening large depth-led identity hero']:
        assert token in body
