from __future__ import annotations

import re
from pathlib import Path


def patch_asset_visual_spec() -> None:
    path=Path('runtime/cbcc/asset_compiler.py')
    text=path.read_text(encoding='utf-8')
    pat=r"def _visual_spec_markdown\(asset:dict\[str,Any\], visual:dict\[str,Any\], strategy_authority:dict\[str,Any\]\|None=None\)->str:\n.*?\n(?=def compile_asset_packages)"
    new=r'''def _visual_spec_markdown(asset:dict[str,Any], visual:dict[str,Any], strategy_authority:dict[str,Any]|None=None)->str:
    master=(strategy_authority or {}).get('sections',{}).get('05_visual_photography_strategy',{})
    art=asset.get('asset_art_direction') or {}
    brief=asset.get('creative_brief') or {}
    presence=art.get('product_presence') or asset.get('product_presence') or {}

    def fmt(value:Any)->str:
        if value in (None,'',[],{}): return '—'
        if isinstance(value,dict):
            for key in ('cn','zh','zh-CN','CN'):
                if value.get(key) not in (None,'',[],{}): return str(value.get(key))
            return _jdump(value)
        if isinstance(value,list): return '；'.join(str(x) for x in value)
        return str(value)

    rows=[
        ('商业任务',asset.get('strategic_job')),
        ('消费者问题',asset.get('consumer_question')),
        ('视觉载体',art.get('visual_carrier') or asset.get('information_assetization',{}).get('representation')),
        ('创意核心',art.get('creative_thesis') or art.get('thesis')),
        ('视觉语言',art.get('visual_language') or art.get('image_language') or art.get('style')),
        ('关键瞬间',art.get('decisive_moment')),
        ('产品出现 / 角色',presence),
        ('主体',art.get('subject')),
        ('动作',art.get('action') or art.get('decisive_action')),
        ('环境',art.get('environment')),
        ('道具',art.get('props') or art.get('scene_props')),
        ('人物 / Casting',art.get('human_context') or art.get('people') or art.get('casting')),
        ('构图语法',art.get('composition_grammar') or art.get('composition') or art.get('spatial_grammar') or brief.get('composition') or master.get('composition')),
        ('空间节奏',art.get('spatial_rhythm') or art.get('space_rhythm')),
        ('相对位置 / 几何',art.get('layout_geometry') or art.get('relative_placement') or art.get('placement_relationships')),
        ('尺度 / 纵深',art.get('scale_depth') or art.get('scale_relationships') or art.get('depth_program')),
        ('产品占画',art.get('product_occupancy') or art.get('product_frame_ratio') or art.get('product_scale_percent')),
        ('焦点路径',art.get('focal_path')),
        ('负空间',art.get('negative_space') or art.get('copy_negative_space')),
        ('证据层级',art.get('evidence_hierarchy') or art.get('proof_mechanism') or art.get('evidence_plane')),
        ('文字安全区',art.get('copy_zone') or art.get('text_zone') or art.get('safe_zone')),
        ('字体 / 信息层级',art.get('typography')),
        ('输出规格',art.get('output_spec') or art.get('canvas') or art.get('format_spec')),
        ('完成质感 / Post Look',art.get('post_look') or art.get('grade') or art.get('finishing_look')),
        ('商品 Fidelity',asset.get('product_fidelity')),
        ('生产方式',asset.get('production_mode')),
    ]
    lines=['# 视觉 / Art Direction 执行合同','', '## 资产级完整视觉决策','']
    for label,value in rows:
        if value not in (None,'',[],{}): lines.append(f'- **{label}**：{fmt(value)}')

    photo_rows=[
        ('机位 / 视角',art.get('camera_or_view') or art.get('preferred_view') or art.get('view')),
        ('焦段 / 镜头',art.get('focal_length_mm') or art.get('lens')),
        ('镜头家族',art.get('lens_family')),
        ('透视 / 投影',art.get('perspective') or art.get('projection')),
        ('机位参数',art.get('camera_position')),
        ('对焦 / 景深',art.get('focus_dof')),
        ('灯光',art.get('lighting') or art.get('lighting_program') or brief.get('lighting') or master.get('lighting_framework')),
        ('Prelight',art.get('prelight') or art.get('prelight_plan')),
        ('CMF',art.get('cmf') or art.get('material_program') or brief.get('color') or master.get('cmf')),
        ('材质响应',art.get('material_response') or art.get('surface_behavior')),
        ('Palette / HEX',art.get('palette_hex') or art.get('palette') or art.get('color_world') or master.get('palette_hex')),
        ('色彩管理',art.get('color_management') or master.get('color_management')),
    ]
    if any(v not in (None,'',[],{}) for _,v in photo_rows):
        lines += ['', '## 摄影 / 灯光 / CMF（仅当前路线相关时）','']
        for label,value in photo_rows:
            if value not in (None,'',[],{}): lines.append(f'- **{label}**：{fmt(value)}')

    video_rows=[
        ('时长 / 节奏',art.get('motion_timing') or art.get('timing') or art.get('duration') or art.get('shot_timing')),
        ('镜头顺序',art.get('shot_sequence') or art.get('shot_plan') or art.get('storyboard')),
        ('镜头运动',art.get('camera_motion') or art.get('motion_program')),
        ('转场 / 音频',art.get('transition_audio') or art.get('transitions') or art.get('audio_direction')),
    ]
    if str(asset.get('asset_type') or '').upper()=='VIDEO' or any(v not in (None,'',[],{}) for _,v in video_rows):
        lines += ['', '## 动态执行（Video 相关时）','']
        for label,value in video_rows:
            if value not in (None,'',[],{}): lines.append(f'- **{label}**：{fmt(value)}')

    why_rows=[
        ('视觉载体 WHY',art.get('visual_carrier_why')),
        ('构图 WHY',art.get('composition_why')),
        ('产品出现 WHY',art.get('product_presence_why') or (presence.get('presence_why') if isinstance(presence,dict) else None)),
        ('摄影 / 媒介 WHY',art.get('media_route_why') or art.get('photography_why')),
    ]
    if any(v not in (None,'',[],{}) for _,v in why_rows):
        lines += ['', '## 为什么这样设计','']
        for label,value in why_rows:
            if value not in (None,'',[],{}): lines.append(f'- **{label}**：{fmt(value)}')

    lines += [
        '', '## 文化、事实与执行边界','',
        f"- **文化 / 人物执行**：{fmt(visual.get('culture_implications'))}",
        f"- **允许进入画面的视觉元素**：{fmt(visual.get('approved_visual_elements'))}",
        f"- **精确边界**：{fmt(visual.get('precision_boundaries'))}",
        '', '## 为什么这张资产必须存在','',
        f"这张资产用于回答：**{asset.get('consumer_question') or '当前购买决策问题'}**。产品是否出现、信息关系、构图、人物/道具/场景与可见文案都应服务这个购买判断，而不是为了补图位或复用模板。",
        '', '## 完整 Agent Art Direction 原始对象（可编辑源）','```json',_jdump(art),'```',
    ]
    return '\n'.join(str(x) for x in lines)+'\n'

'''
    text2,n=re.subn(pat,new,text,flags=re.S)
    if n!=1:
        raise SystemExit(f'asset_compiler visual spec replacement count={n}')
    path.write_text(text2,encoding='utf-8')


def patch_delivery_html() -> None:
    path=Path('runtime/cbcc/delivery_html.py')
    text=path.read_text(encoding='utf-8')

    old="aid=path.name;manifest={};yamlp=path/'00_asset_manifest.yaml';design=_read_json(path/'12_design_card.json',{})"
    new="aid=path.name;manifest={};yamlp=path/'00_asset_manifest.yaml';design=_read_json(path/'12_design_card.json',{});prompt_contract=_read_json(path/'13_prompt_contract.json',{});visible_copy_block=_read_json(path/'14_visible_copy_block.json',{});production_notes=_read_json(path/'15_production_assembly_notes.json',{});art=design.get('agent_art_direction') or {}"
    if new not in text:
        if old not in text: raise SystemExit('delivery_html formal asset anchor missing')
        text=text.replace(old,new,1)

    old="for key in ['asset_name','surface','decision_intent','consumer_question','asset_type']:"
    new="for key in ['asset_name','surface','decision_intent','consumer_question','asset_type','production_mode']:"
    if new not in text:
        if old not in text: raise SystemExit('delivery_html yaml keys anchor missing')
        text=text.replace(old,new,1)

    old="""        visual=_human_kv([
          ('决策关键瞬间',design.get('decisive_moment') or narrative.get('decisive_moment')),('画面必须可见',narrative.get('what_must_be_visible')),('主体',subject.get('subject')),('动作',subject.get('action')),('环境',subject.get('environment')),('道具',subject.get('props')),('构图语法',comp.get('composition_grammar')),('空间节奏',comp.get('spatial_rhythm')),('视角 / 机位',comp.get('camera_or_view')),('产品出现方式',(product_role.get('production_resolution') or product_role.get('planning_state')) if isinstance(product_role,dict) else product_role),('商品保真模式',identity.get('product_fidelity')),('允许进入画面的视觉元素',design.get('approved_visual_elements')),('精确执行边界',design.get('precision_boundaries')),('可编辑层',editability.get('editable_layers')),('冻结层',editability.get('frozen_layers')),('局部修订规则',editability.get('revision_rule')),('展示位置（Surface）',surface),('信息表达方式',(surfacec.get('representation') if isinstance(surfacec,dict) else None)),('文案密度',(surfacec.get('copy_budget') or {}).get('density_class') if isinstance(surfacec,dict) else None),('移动端扫描原则','第一眼只承载一个主要购买答案；次级解释移到相邻原生内容位。' if isinstance(surfacec,dict) and surfacec else None)
        ])
"""
    new="""        visual=_human_kv([
          ('视觉载体',art.get('visual_carrier') or design.get('visual_carrier')),('创意核心',art.get('creative_thesis') or art.get('thesis')),('视觉语言',art.get('visual_language') or art.get('image_language') or art.get('style')),('决策关键瞬间',art.get('decisive_moment') or design.get('decisive_moment') or narrative.get('decisive_moment')),('画面必须可见',narrative.get('what_must_be_visible')),('主体',art.get('subject') or subject.get('subject')),('动作',art.get('action') or art.get('decisive_action') or subject.get('action')),('环境',art.get('environment') or subject.get('environment')),('道具',art.get('props') or art.get('scene_props') or subject.get('props')),('人物 / Casting',art.get('human_context') or art.get('people') or art.get('casting') or subject.get('human_context')),('构图语法',art.get('composition_grammar') or art.get('composition') or comp.get('composition_grammar')),('空间节奏',art.get('spatial_rhythm') or comp.get('spatial_rhythm')),('相对位置 / 几何',art.get('layout_geometry') or art.get('relative_placement') or art.get('placement_relationships')),('尺度 / 纵深',art.get('scale_depth') or art.get('scale_relationships') or art.get('depth_program')),('产品占画',art.get('product_occupancy') or art.get('product_frame_ratio') or art.get('product_scale_percent')),('焦点路径',art.get('focal_path')),('负空间',art.get('negative_space') or art.get('copy_negative_space')),('证据层级',art.get('evidence_hierarchy') or art.get('proof_mechanism') or art.get('evidence_plane')),('文字安全区',art.get('copy_zone') or art.get('text_zone') or art.get('safe_zone')),('字体 / 信息层级',art.get('typography')),('视角 / 机位',art.get('camera_or_view') or comp.get('camera_or_view')),('产品出现方式',art.get('product_presence') or ((product_role.get('production_resolution') or product_role.get('planning_state')) if isinstance(product_role,dict) else product_role)),('商品保真模式',identity.get('product_fidelity')),('输出规格',art.get('output_spec') or art.get('canvas') or art.get('format_spec')),('完成质感 / Post Look',art.get('post_look') or art.get('grade') or art.get('finishing_look')),('允许进入画面的视觉元素',design.get('approved_visual_elements')),('精确执行边界',design.get('precision_boundaries')),('可编辑层',editability.get('editable_layers')),('冻结层',editability.get('frozen_layers')),('局部修订规则',editability.get('revision_rule')),('展示位置（Surface）',surface),('信息表达方式',(surfacec.get('representation') if isinstance(surfacec,dict) else None)),('文案密度',(surfacec.get('copy_budget') or {}).get('density_class') if isinstance(surfacec,dict) else None),('移动端扫描原则','第一眼只承载一个主要购买答案；次级解释移到相邻原生内容位。' if isinstance(surfacec,dict) and surfacec else None)
        ])
"""
    if new not in text:
        if old not in text: raise SystemExit('delivery_html visual block anchor missing')
        text=text.replace(old,new,1)

    old="""        photo_rows=[
          ('拍摄 / 合成模式',photo_exec.get('capture_mode')),('构图执行合同',photo_exec.get('composition')),('输出色彩管理',photo_exec.get('color_management')),('焦段',comp.get('focal_length_mm')),('镜头家族',comp.get('lens_family')),('方位角',comp.get('azimuth')),('俯仰 / 高度',comp.get('elevation') or comp.get('camera_height')),('对焦平面',comp.get('focus_plane')),('景深 / 光圈意图',comp.get('aperture_dof_intent')),('快门起点',comp.get('shutter_speed')),('ISO 起点',comp.get('iso')),('主光',light.get('key')),('补光',light.get('fill')),('负补光',light.get('negative_fill')),('轮廓光',light.get('rim')),('色温',light.get('cct')),('阴影策略',light.get('shadow')),('高光策略',light.get('highlight_policy')),('Prelight',light.get('prelight_plan')),('偏振',light.get('polarization_plan')),('色彩一致性',light.get('color_consistency_plan'))
        ]
"""
    new="""        photo_rows=[
          ('拍摄 / 合成模式',photo_exec.get('capture_mode') or art.get('production_route')),('构图执行合同',photo_exec.get('composition')),('输出色彩管理',art.get('color_management') or photo_exec.get('color_management')),('焦段',art.get('focal_length_mm') or art.get('lens') or comp.get('focal_length_mm')),('镜头家族',art.get('lens_family') or comp.get('lens_family')),('透视 / 投影',art.get('perspective') or art.get('projection')),('机位参数',art.get('camera_position')),('方位角',comp.get('azimuth')),('俯仰 / 高度',comp.get('elevation') or comp.get('camera_height')),('对焦 / 景深',art.get('focus_dof') or comp.get('focus_plane') or comp.get('aperture_dof_intent')),('快门起点',comp.get('shutter_speed')),('ISO 起点',comp.get('iso')),('灯光方案',art.get('lighting') or art.get('lighting_program')),('主光',light.get('key')),('补光',light.get('fill')),('负补光',light.get('negative_fill')),('轮廓光',light.get('rim')),('色温',light.get('cct')),('光比 / 曝光关系',(art.get('lighting') or {}).get('exposure_ratio_plan') if isinstance(art.get('lighting'),dict) else None),('阴影策略',light.get('shadow')),('高光策略',light.get('highlight_policy')),('Prelight',art.get('prelight') or art.get('prelight_plan') or light.get('prelight_plan')),('偏振',light.get('polarization_plan')),('CMF',art.get('cmf') or art.get('material_program') or light.get('cmf')),('材质响应',art.get('material_response') or art.get('surface_behavior') or light.get('material_response_to_show')),('Palette / HEX',art.get('palette_hex') or art.get('palette') or art.get('color_world')),('色彩一致性',light.get('color_consistency_plan'))
        ]
"""
    if new not in text:
        if old not in text: raise SystemExit('delivery_html photo block anchor missing')
        text=text.replace(old,new,1)

    old="""        if copyc:
            views.append({'key':'copy','title':'文案','html':_human_kv([('锁定的目标市场可见文案',copyc),('确定性排版规则',info.get('copy_visual_rule')),('文案预算',info.get('copy_budget')),('字体方向',info.get('typography'))])})
"""
    new="""        effective_copy=visible_copy_block or copyc
        if effective_copy:
            views.append({'key':'copy','title':'可见文案','html':_human_kv([('目标市场可见文案',effective_copy.get('target_market_copy') if isinstance(effective_copy,dict) else effective_copy),('次级文案',effective_copy.get('secondary_copy') if isinstance(effective_copy,dict) else None),('中文释义 / 用途',effective_copy.get('delivery_translation_zh') if isinstance(effective_copy,dict) else None),('文字渲染 / 装配路线',production_notes.get('copy_render_mode')),('文案预算',(effective_copy.get('copy_budget') if isinstance(effective_copy,dict) else None) or info.get('copy_budget')),('字体方向',(effective_copy.get('typography_direction') if isinstance(effective_copy,dict) else None) or info.get('typography'))])})
        if prompt_cn:
            views.append({'key':'model-prompt-cn','title':'Model Prompt CN','html':'<div class="asset-file"><div class="file-label">直接给生成模型的中文提示词</div><pre><code>'+html.escape(prompt_cn)+'</code></pre></div>'})
        if prompt_en:
            views.append({'key':'model-prompt-en','title':'Model Prompt EN','html':'<div class="asset-file"><div class="file-label">直接给生成模型的英文提示词</div><pre><code>'+html.escape(prompt_en)+'</code></pre></div>'})
        if production_notes:
            views.append({'key':'production-notes','title':'生产 / 装配说明','html':_human_kv([('文字渲染路线',production_notes.get('copy_render_mode')),('产品 Fidelity',production_notes.get('product_fidelity')),('产品出现方式',production_notes.get('product_presence')),('产品参考规则',production_notes.get('product_reference_rule')),('可编辑层',production_notes.get('editable_layers')),('冻结层',production_notes.get('frozen_layers')),('局部修订规则',production_notes.get('revision_rule')),('Provider / Route',production_notes.get('provider_route')),('装配原则',production_notes.get('assembly_principle'))])})
"""
    if new not in text:
        if old not in text: raise SystemExit('delivery_html copy block anchor missing')
        text=text.replace(old,new,1)

    old="if not f.is_file() or f.name in {'05_prompt_CN.txt','06_prompt_EN.txt'}: continue"
    new="if not f.is_file() or f.name in {'05_prompt_CN.txt','06_prompt_EN.txt','14_visible_copy_block.json','15_production_assembly_notes.json'}: continue"
    if new not in text:
        if old not in text: raise SystemExit('delivery_html file skip anchor missing')
        text=text.replace(old,new,1)

    path.write_text(text,encoding='utf-8')


def patch_delivery_contract() -> None:
    path=Path('runtime/cbcc/delivery_contract.py')
    text=path.read_text(encoding='utf-8')
    old="""        # 05 — visual strategy must be executable and asset-specific, not adjectives.
        for k in ['palette_hex','composition','lighting_framework','camera','lens','color_management','casting','platform_dimensions','shot_list','asset_parameter_reasoning','photography_rationale']:
            if not _present(vis.get(k)):
                _depth_issue(issues, 'FULL_VISUAL_EXECUTION_DEPTH_MISSING', REQUIRED_SECTIONS[4], field=k)
        if _present(vis.get('casting')) and not _present(vis.get('inclusive_photography')):
            _depth_issue(issues, 'FULL_INCLUSIVE_PHOTOGRAPHY_MISSING', REQUIRED_SECTIONS[4])
"""
    new="""        # 05 — visual strategy must preserve decision depth without forcing every carrier into photography.
        for k in ['palette_hex','composition','color_management','platform_dimensions','asset_parameter_reasoning']:
            if not _present(vis.get(k)):
                _depth_issue(issues, 'FULL_VISUAL_EXECUTION_DEPTH_MISSING', REQUIRED_SECTIONS[4], field=k)
        asset_reasoning=vis.get('asset_parameter_reasoning') or []
        if not isinstance(asset_reasoning,list) or not asset_reasoning:
            _depth_issue(issues, 'FULL_ASSET_ART_DIRECTION_REASONING_MISSING', REQUIRED_SECTIONS[4])
        else:
            for i,row in enumerate(asset_reasoning):
                if not isinstance(row,dict):
                    _depth_issue(issues, 'FULL_ASSET_ART_DIRECTION_REASONING_INVALID', REQUIRED_SECTIONS[4], row=i)
                    continue
                if not _present(row.get('asset_id')):
                    _depth_issue(issues, 'FULL_ASSET_ART_DIRECTION_ID_MISSING', REQUIRED_SECTIONS[4], row=i)
                decision_values=[row.get(k) for k in ['composition','composition_grammar','visual_carrier','camera','lighting','cmf','palette_hex','surface','product_presence','parameters','why','rationale']]
                if not any(_present(v) for v in decision_values):
                    _depth_issue(issues, 'FULL_ASSET_ART_DIRECTION_REASONING_SHALLOW', REQUIRED_SECTIONS[4], row=i)
        photo_selected=any(_present(vis.get(k)) for k in ['photography_execution','photography_rationale','camera','lens','shot_list']) or str(vis.get('production_route') or '').upper() in {'PHOTOGRAPHY','REAL_PHOTO','PHOTO_CAPTURE'}
        if photo_selected:
            for k in ['lighting_framework','camera','lens','photography_rationale']:
                if not _present(vis.get(k)):
                    _depth_issue(issues, 'FULL_PHOTOGRAPHY_ROUTE_DEPTH_MISSING', REQUIRED_SECTIONS[4], field=k)
        if _present(vis.get('casting')) and not _present(vis.get('inclusive_photography')):
            _depth_issue(issues, 'FULL_INCLUSIVE_PHOTOGRAPHY_MISSING', REQUIRED_SECTIONS[4])
"""
    if new not in text:
        if old not in text: raise SystemExit('delivery_contract visual depth anchor missing')
        text=text.replace(old,new,1)
    text=text.replace("'depth_contract':'FULL_DECISION_DEPTH_V1'","'depth_contract':'FULL_DECISION_DEPTH_V2_CARRIER_AWARE_NO_SILENT_COMPRESSION'",1)
    path.write_text(text,encoding='utf-8')


def main() -> None:
    patch_asset_visual_spec()
    patch_delivery_html()
    patch_delivery_contract()
    print('Applied v0.6.31 human workspace and depth migration.')


if __name__=='__main__':
    main()
