from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping
import json,re


def _meaningful(v:Any)->bool:return v not in (None,'',[],{})
def _dict(v:Any)->dict[str,Any]:return dict(v) if isinstance(v,Mapping) else {}
def _cjk(text:str)->bool:return bool(re.search(r'[\u3400-\u9fff]',text or ''))

def _localized(v:Any,lang:str)->str:
    if not _meaningful(v):return ''
    if isinstance(v,Mapping):
        keys=('en','EN','en-US','english') if lang=='en' else ('cn','zh','zh-CN','CN','chinese')
        for key in keys:
            if _meaningful(v.get(key)):return _localized(v.get(key),lang)
        # Technical dictionaries are rendered losslessly; prose authors may provide cn/en companions.
        return json.dumps(v,ensure_ascii=False,sort_keys=True,default=str)
    if isinstance(v,(list,tuple)):return '；'.join(_localized(x,lang) for x in v if _meaningful(x))
    return str(v)

def _flat(prefix:str,obj:Any)->list[tuple[str,Any]]:
    if not _meaningful(obj):return []
    if isinstance(obj,Mapping):
        rows=[]
        for k,v in obj.items():
            if _meaningful(v):rows.extend(_flat(f'{prefix}.{k}' if prefix else str(k),v))
        return rows
    return [(prefix,obj)]

LABELS={
 'focal_length_mm':('焦段','Focal length'), 'lens_family':('镜头家族','Lens family'),
 'camera_position.working_distance':('工作距离','Working distance'),'camera_position.camera_height':('机位高度','Camera height'),
 'camera_position.yaw':('Yaw / 水平转角','Yaw'),'camera_position.pitch':('Pitch / 俯仰角','Pitch'),'camera_position.roll':('Roll / 横滚角','Roll'),
 'camera_position.shot_size':('景别','Shot size'),'camera_position.perspective':('透视','Perspective'),
 'focus_dof.focus_plane':('对焦平面','Focus plane'),'focus_dof.aperture':('光圈','Aperture'),'focus_dof.dof':('景深意图','Depth-of-field intent'),
 'focus_dof.shutter':('快门','Shutter'),'focus_dof.iso':('ISO','ISO'),'focus_dof.motion_behavior':('运动/拖影','Motion behavior'),
 'lighting.key':('主光','Key light'),'lighting.fill':('补光','Fill light'),'lighting.negative_fill':('负补光','Negative fill'),'lighting.rim':('轮廓光','Rim light'),'lighting.background_light':('背景光','Background light'),
 'lighting.modifier':('控光附件','Modifier'),'lighting.modifier_size':('控光附件尺寸','Modifier size'),'lighting.modifier_distance':('控光附件距离','Modifier distance'),'lighting.modifier_angle':('控光附件角度','Modifier angle'),
 'lighting.cct':('色温','CCT'),'lighting.white_balance':('白平衡','White balance'),'lighting.light_ratio':('光比','Light ratio'),
 'lighting.shadow_policy':('阴影策略','Shadow policy'),'lighting.highlight_policy':('高光策略','Highlight policy'),'lighting.reflection':('反射控制','Reflection control'),'lighting.polarization':('偏振','Polarization'),'lighting.prelight':('Prelight','Prelight'),
 'cmf.material':('材质','Material'),'cmf.finish':('表面处理','Finish'),'cmf.surface_behavior':('表面响应','Surface behavior'),'cmf.microtexture':('微纹理','Microtexture'),'cmf.transparency':('透明/半透明','Transparency'),'cmf.reflection':('材质反射','Material reflection'),'cmf.refraction':('折射','Refraction'),'cmf.highlight_behavior':('材质高光','Highlight behavior'),'cmf.subsurface':('次表面表现','Subsurface'),'cmf.deformation':('形变','Deformation'),'cmf.contact_behavior':('接触行为','Contact behavior'),'cmf.palette_hex':('HEX配色','HEX palette'),
 'human_context.role':('人物角色','Human role'),'human_context.age':('年龄','Age'),'human_context.gender_presentation':('性别呈现','Gender presentation'),'human_context.skin_tone':('肤色','Skin tone'),'human_context.hair':('发质/发型','Hair texture/style'),'human_context.makeup':('妆容/修饰','Makeup/grooming'),'human_context.wardrobe':('服装','Wardrobe'),'human_context.accessories':('配饰','Accessories'),'human_context.body_type':('体型','Body representation'),'human_context.disability':('残障/辅助器具','Disability/assistive device'),'human_context.religious_cultural_presentation':('宗教/文化呈现','Religious/cultural presentation'),'human_context.pose':('姿态','Pose'),'human_context.expression':('表情','Expression'),'human_context.gaze':('视线','Gaze'),'human_context.hand_action':('手部动作','Hand action'),'human_context.product_interaction':('人与商品交互','Product interaction'),'human_context.scene_relationship':('人物-场景关系','Human-scene relationship'),
 'typography':('字体/信息层级','Typography/information hierarchy'),'layout_geometry':('布局几何','Layout geometry'),'scale_depth':('尺度/纵深','Scale/depth'),'product_occupancy':('产品占画','Product occupancy'),'focal_path':('焦点路径','Focal path'),'negative_space':('负空间','Negative space'),'copy_zone':('文字/安全区','Copy/safe zone'),'post_look':('最终质感/调色','Finishing/grade'),'output_spec':('输出规格','Output specification')
}

def _selected_rows(asset:Mapping[str,Any])->list[tuple[str,Any]]:
    art=_dict(asset.get('asset_art_direction'))
    rows=[]
    for root in ('focal_length_mm','lens_family','camera_position','focus_dof','lighting','cmf','human_context','typography','layout_geometry','scale_depth','product_occupancy','focal_path','negative_space','copy_zone','post_look','output_spec'):
        if _meaningful(art.get(root)):rows.extend(_flat(root,art.get(root)))
    # Preserve stable ordering by the explicit LABELS contract, then any authored extension fields.
    order={k:i for i,k in enumerate(LABELS)}
    rows.sort(key=lambda x:(order.get(x[0],999),x[0]))
    return rows

def _append(prompt:str, rows:list[tuple[str,Any]],lang:str)->tuple[str,list[str],list[str]]:
    prompt=str(prompt or ''); lines=[];consumed=[];missing_en=[]
    for path,value in rows:
        label=LABELS.get(path,(path,path))[1 if lang=='en' else 0]
        text=_localized(value,lang).strip()
        if not text:continue
        if lang=='en' and _cjk(text) and isinstance(value,Mapping) and not any(_meaningful(value.get(k)) for k in ('en','EN','en-US','english')):
            missing_en.append(path)
        # Avoid duplicating values already clearly projected by the mature compiler.
        if text in prompt:
            consumed.append(path);continue
        lines.append(f'- {label}: {text}');consumed.append(path)
    if not lines:return prompt,consumed,missing_en
    header='\n\n[SELECTED EXECUTION PARAMETERS — AUTHORITATIVE]\n' if lang=='en' else '\n\n【已选执行参数｜以资产策划为准】\n'
    return prompt.rstrip()+header+'\n'.join(lines)+'\n',consumed,missing_en

def project_selected_execution_parameters(asset:Mapping[str,Any],bundle:Mapping[str,Any])->dict[str,Any]:
    out=deepcopy(dict(bundle));rows=_selected_rows(asset)
    cn=out.get('model_prompt_cn') or out.get('prompt_cn') or ''
    en=out.get('model_prompt_en') or out.get('prompt_en') or ''
    cn2,cn_paths,_=_append(cn,rows,'cn');en2,en_paths,missing_en=_append(en,rows,'en')
    # Keep canonical/model aliases synchronized before the final semantic membrane.
    if 'model_prompt_cn' in out:out['model_prompt_cn']=cn2
    if 'model_prompt_en' in out:out['model_prompt_en']=en2
    out['prompt_cn']=cn2;out['prompt_en']=en2
    audit={'status':'PASS' if not missing_en else 'NEEDS_ENGLISH_EXECUTION_COMPANION','selected_paths':[p for p,_ in rows],'projected_cn':cn_paths,'projected_en':en_paths,'missing_en_companion':missing_en,'principle':'Only Agent-selected model-visible execution values are projected; absent photography/people/type decisions are never invented.'}
    out['selected_execution_projection_audit']=audit
    card=out.setdefault('design_card',{});card['selected_execution_projection_audit']=audit
    return out
