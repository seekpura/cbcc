from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any, Mapping

_CJK_RE = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')
_ENGINEERING_JARGON = (
    'deterministic', 'renderer recipe', 'renderer layer', 'machine contract',
    'post-layout', 'after render', 'after generation', 'prompt consumption audit',
    'provider transport', 'authority hash', 'layer plan',
)


def _meaningful(value: Any) -> bool:
    if value in (None, '', [], {}):
        return False
    if isinstance(value, Mapping):
        return any(_meaningful(v) for v in value.values())
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_meaningful(v) for v in value)
    return True


def _txt(value: Any) -> str:
    if value in (None, '', [], {}):
        return ''
    if isinstance(value, Mapping):
        return '; '.join(f'{k}={_txt(v)}' for k, v in value.items() if _meaningful(v))
    if isinstance(value, (list, tuple, set, frozenset)):
        return '; '.join(_txt(v) for v in value if _meaningful(v))
    return str(value).strip()


def _first(mapping: Mapping[str, Any] | None, *keys: str) -> Any:
    mapping = mapping or {}
    for key in keys:
        value = mapping.get(key)
        if _meaningful(value):
            return value
    return None


def _lang(value: Any, language: str, missing: list[str], field: str) -> Any:
    """Read an Agent-authored bilingual semantic value without runtime translation.

    Runtime may serialize bilingual Art Direction, but must not pretend Chinese creative prose is an
    English model prompt. Bilingual dicts may use cn/zh/zh-CN and en/EN keys. Language-neutral
    numbers, HEX values, camera values and enum-like tokens are reusable in either prompt.
    """
    if not _meaningful(value):
        return None
    if isinstance(value, Mapping):
        if language == 'EN':
            for key in ('en', 'EN', 'en-US', 'en-GB'):
                if _meaningful(value.get(key)):
                    return value.get(key)
        else:
            for key in ('cn', 'zh', 'zh-CN', 'CN'):
                if _meaningful(value.get(key)):
                    return value.get(key)
        # A structured execution object is language-neutral when its leaf prose is language-neutral.
        rendered = _txt(value)
        if language == 'EN' and _CJK_RE.search(rendered):
            missing.append(field)
            return None
        return value
    if isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        out=[]
        for idx, item in enumerate(value):
            resolved=_lang(item, language, missing, f'{field}[{idx}]')
            if _meaningful(resolved):
                out.append(resolved)
        return out or None
    text=str(value).strip()
    if language == 'EN' and _CJK_RE.search(text):
        missing.append(field)
        return None
    return value


def _art(asset: Mapping[str, Any]) -> dict[str, Any]:
    value=asset.get('asset_art_direction')
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}


def _visible_copy_block(asset: Mapping[str, Any], card: Mapping[str, Any]) -> dict[str, Any]:
    raw=asset.get('visible_copy')
    if not isinstance(raw, Mapping):
        raw={'target_copy': raw} if _meaningful(raw) else {}
    raw=deepcopy(dict(raw))
    return {
        'target_market_copy': _first(raw, 'target_copy', 'copy', 'text', 'headline', 'bm', 'ms-MY', 'en', 'EN'),
        'secondary_copy': _first(raw, 'secondary_copy', 'subheadline', 'proof', 'cta'),
        'delivery_translation_zh': _first(raw, 'delivery_translation', 'zh', 'zh-CN', 'chinese'),
        'raw': raw,
        'copy_budget': deepcopy(((card.get('information_design') or {}).get('copy_budget') or {})),
        'typography_direction': deepcopy(((card.get('information_design') or {}).get('typography') or {})),
    }


def _copy_render_mode(asset: Mapping[str, Any], art: Mapping[str, Any], copy_block: Mapping[str, Any]) -> str:
    explicit=_first(art, 'copy_render_mode', 'text_render_mode', 'visible_copy_render_mode')
    if explicit:
        return str(explicit).upper()
    if not _meaningful(copy_block.get('target_market_copy')) and not _meaningful(copy_block.get('secondary_copy')):
        return 'NO_VISIBLE_COPY'
    # Choosing whether exact copy is rendered by the model or composed later is a production decision.
    # Runtime does not silently choose POST_COMPOSITE for every asset/provider.
    return 'UNRESOLVED_AGENT_DECISION'


def _presence_text(card: Mapping[str, Any], language: str) -> str:
    presence=card.get('product_presence') or {}
    state=str(presence.get('planning_state') or '').upper()
    role=_txt(presence.get('product_role'))
    scale=_txt(presence.get('scale_relationship'))
    if language == 'CN':
        if state in {'FORBIDDEN','ABSENT','NOT_APPLICABLE'}:
            return '产品不出现在画面中；不要加入包装、角落商品、剪影或隐约商品形状。'
        if state:
            bits=[f'产品出现状态：{state}']
            if role: bits.append(f'产品角色：{role}')
            if scale: bits.append(f'尺度关系：{scale}')
            return '；'.join(bits)+'。'
        return ''
    if state in {'FORBIDDEN','ABSENT','NOT_APPLICABLE'}:
        return 'The product must not appear in frame; do not add a packshot, corner product, silhouette or implied product shape.'
    if state:
        bits=[f'Product presence: {state}']
        if role and not _CJK_RE.search(role): bits.append(f'product role: {role}')
        if scale and not _CJK_RE.search(scale): bits.append(f'scale relationship: {scale}')
        return '; '.join(bits)+'.'
    return ''


def _output_spec(asset: Mapping[str, Any], art: Mapping[str, Any], card: Mapping[str, Any]) -> Any:
    return _first(art, 'output_spec', 'canvas', 'format_spec') or _first(card.get('surface_contract') or {}, 'output_spec', 'canvas', 'dimensions', 'size', 'aspect_ratio')


def _model_fields(asset: Mapping[str, Any], card: Mapping[str, Any], language: str) -> tuple[dict[str, Any], list[str]]:
    art=_art(asset)
    missing: list[str]=[]
    sae=card.get('subject_action_environment_props') or {}
    cam=card.get('composition_camera') or {}
    lm=card.get('lighting_material_cmf') or {}
    photo=card.get('photography_execution') or {}
    info=card.get('information_design') or {}
    inc=card.get('inclusive_photography') or {}
    system=card.get('creative_system') or {}

    def L(value: Any, field: str) -> Any:
        return _lang(value, language, missing, field)

    fields={
        'output_spec': L(_output_spec(asset, art, card), 'output_spec'),
        'visual_objective': L(_first(art, 'visual_objective', 'objective', 'decision_answer') or card.get('visual_objective'), 'visual_objective'),
        'visual_carrier': L(_first(art, 'visual_carrier') or (card.get('information_assetization') or {}).get('representation'), 'visual_carrier'),
        'visual_language': L(_first(art, 'image_language', 'visual_language', 'style') or system.get('image_language'), 'visual_language'),
        'creative_thesis': L(_first(art, 'creative_thesis', 'thesis') or system.get('creative_thesis'), 'creative_thesis'),
        'decisive_moment': L(_first(art, 'decisive_moment', 'visual_job') or card.get('decisive_moment'), 'decisive_moment'),
        'subject': L(_first(art, 'subject') or sae.get('subject'), 'subject'),
        'action': L(_first(art, 'action', 'decisive_action') or sae.get('action'), 'action'),
        'environment': L(_first(art, 'environment') or sae.get('environment'), 'environment'),
        'props': L(_first(art, 'props', 'scene_props') or sae.get('props'), 'props'),
        'human_context': L(_first(art, 'human_context', 'people', 'casting') or sae.get('human_context'), 'human_context'),
        'composition': L(_first(art, 'composition_grammar', 'composition', 'spatial_grammar') or cam.get('composition_grammar'), 'composition'),
        'spatial_rhythm': L(_first(art, 'spatial_rhythm', 'space_rhythm') or cam.get('spatial_rhythm'), 'spatial_rhythm'),
        'layout_geometry': L(_first(art, 'layout_geometry', 'relative_placement', 'placement_relationships'), 'layout_geometry'),
        'scale_depth': L(_first(art, 'scale_depth', 'scale_relationships', 'depth_program'), 'scale_depth'),
        'focal_path': L(_first(art, 'focal_path'), 'focal_path'),
        'negative_space': L(_first(art, 'negative_space', 'copy_negative_space'), 'negative_space'),
        'product_occupancy': L(_first(art, 'product_occupancy', 'product_frame_ratio', 'product_scale_percent'), 'product_occupancy'),
        'evidence_hierarchy': L(_first(art, 'evidence_hierarchy', 'proof_mechanism', 'evidence_plane'), 'evidence_hierarchy'),
        'camera_view': L(_first(art, 'camera_or_view', 'preferred_view', 'view') or cam.get('camera_or_view'), 'camera_view'),
        'focal_length': L(_first(art, 'focal_length_mm', 'lens') or cam.get('focal_length_mm'), 'focal_length'),
        'lens_family': L(_first(art, 'lens_family') or cam.get('lens_family'), 'lens_family'),
        'perspective': L(_first(art, 'perspective', 'projection') or cam.get('projection'), 'perspective'),
        'camera_position': L(_first(art, 'camera_position') or {k:cam.get(k) for k in ('azimuth','elevation','roll_deg','distance','camera_height') if _meaningful(cam.get(k))}, 'camera_position'),
        'focus_dof': L(_first(art, 'focus_dof') or {k:cam.get(k) for k in ('focus_plane','aperture_dof_intent') if _meaningful(cam.get(k))}, 'focus_dof'),
        'lighting': L(_first(art, 'lighting', 'lighting_program') or {k:lm.get(k) for k in ('key','fill','negative_fill','rim','cct','shadow','highlight_policy','exposure_ratio_plan','reflection','polarization_plan') if _meaningful(lm.get(k))}, 'lighting'),
        'prelight': L(_first(art, 'prelight', 'prelight_plan') or lm.get('prelight_plan'), 'prelight'),
        'cmf': L(_first(art, 'cmf', 'material_program') or lm.get('cmf'), 'cmf'),
        'material_response': L(_first(art, 'material_response', 'surface_behavior') or lm.get('material_response_to_show'), 'material_response'),
        'palette': L(_first(art, 'palette_hex', 'palette', 'color_world', 'color') or (photo.get('cmf') or {}).get('palette_hex') if isinstance(photo.get('cmf'), Mapping) else _first(art, 'palette_hex', 'palette', 'color_world', 'color'), 'palette'),
        'color_management': L(_first(art, 'color_management') or photo.get('color_management'), 'color_management'),
        'typography': L(_first(art, 'typography') or info.get('typography'), 'typography'),
        'copy_zone': L(_first(art, 'copy_zone', 'text_zone', 'safe_zone') or cam.get('safe_zone'), 'copy_zone'),
        'inclusive_human': L(_first(art, 'inclusive_human', 'representation') or inc, 'inclusive_human'),
        'motion_timing': L(_first(art, 'motion_timing', 'timing', 'duration', 'shot_timing'), 'motion_timing'),
        'shot_sequence': L(_first(art, 'shot_sequence', 'shot_plan', 'storyboard'), 'shot_sequence'),
        'camera_motion': L(_first(art, 'camera_motion', 'motion_program'), 'camera_motion'),
        'transition_audio': L(_first(art, 'transition_audio', 'transitions', 'audio_direction'), 'transition_audio'),
        'post_look': L(_first(art, 'post_look', 'grade', 'finishing_look'), 'post_look'),
        'approved_visual_elements': L(card.get('approved_visual_elements'), 'approved_visual_elements'),
        'precision_boundaries': L(card.get('precision_boundaries'), 'precision_boundaries'),
    }
    return {k:v for k,v in fields.items() if _meaningful(v)}, list(dict.fromkeys(missing))


def _render_prompt(asset: Mapping[str, Any], card: Mapping[str, Any], language: str, copy_block: Mapping[str, Any], copy_mode: str) -> tuple[str, list[str]]:
    art=_art(asset)
    explicit=_first(art, 'model_prompt_en' if language=='EN' else 'model_prompt_cn', 'generation_prompt_en' if language=='EN' else 'generation_prompt_cn')
    if explicit:
        text=str(explicit).strip()
        missing=[]
        if language=='EN' and _CJK_RE.search(text):
            missing=['model_prompt_en_language_purity']
        return text+'\n', missing

    f, missing=_model_fields(asset, card, language)
    is_video=str(asset.get('asset_type') or '').upper()=='VIDEO' or 'VIDEO' in str(f.get('visual_carrier') or '').upper()
    presence=_presence_text(card, language)

    if language=='CN':
        rows=[]
        rows.append('创建一条可直接用于当前生成模型的商业视觉。' if not is_video else '创建一条可直接用于当前视频生成模型的商业短视频。')
        if f.get('output_spec'): rows.append(f"输出：{_txt(f['output_spec'])}。")
        if f.get('visual_objective'): rows.append(f"视觉目标：{_txt(f['visual_objective'])}。")
        if f.get('visual_carrier'): rows.append(f"视觉载体：{_txt(f['visual_carrier'])}。")
        if f.get('visual_language'): rows.append(f"视觉语言：{_txt(f['visual_language'])}。")
        if f.get('creative_thesis'): rows.append(f"创意核心：{_txt(f['creative_thesis'])}。")
        if f.get('decisive_moment'): rows.append(f"关键瞬间：{_txt(f['decisive_moment'])}。")
        scene=[]
        for k,label in [('subject','主体'),('action','动作'),('environment','环境'),('props','道具'),('human_context','人物')]:
            if f.get(k): scene.append(f"{label}：{_txt(f[k])}")
        if scene: rows.append('场景与主体：'+'；'.join(scene)+'。')
        if presence: rows.append(presence)
        comp=[]
        for k,label in [('composition','构图'),('spatial_rhythm','空间节奏'),('layout_geometry','相对位置'),('scale_depth','尺度与纵深'),('product_occupancy','产品占画'),('focal_path','视线动线'),('negative_space','留白')]:
            if f.get(k): comp.append(f"{label}：{_txt(f[k])}")
        if comp: rows.append('构图与空间：'+'；'.join(comp)+'。')
        if f.get('evidence_hierarchy'): rows.append(f"证据层级：{_txt(f['evidence_hierarchy'])}。")
        camera=[]
        for k,label in [('camera_view','视角'),('focal_length','焦段'),('lens_family','镜头'),('perspective','透视'),('camera_position','机位'),('focus_dof','对焦/景深')]:
            if f.get(k): camera.append(f"{label}：{_txt(f[k])}")
        if camera: rows.append('摄影机：'+'；'.join(camera)+'。')
        light=[]
        for k,label in [('lighting','灯光'),('prelight','预打光'),('cmf','CMF'),('material_response','材质响应'),('palette','配色'),('color_management','色彩管理')]:
            if f.get(k): light.append(f"{label}：{_txt(f[k])}")
        if light: rows.append('光线、材质与色彩：'+'；'.join(light)+'。')
        if f.get('inclusive_human'): rows.append(f"人物呈现：{_txt(f['inclusive_human'])}。")
        if is_video:
            video=[]
            for k,label in [('motion_timing','时长/节奏'),('shot_sequence','镜头顺序'),('camera_motion','镜头运动'),('transition_audio','转场/音频')]:
                if f.get(k): video.append(f"{label}：{_txt(f[k])}")
            if video: rows.append('动态执行：'+'；'.join(video)+'。')
        if f.get('post_look'): rows.append(f"完成质感：{_txt(f['post_look'])}。")
        if copy_mode in {'MODEL_RENDER','HYBRID'} and _meaningful(copy_block.get('target_market_copy')):
            rows.append(f"画面可见文字必须准确呈现：\"{_txt(copy_block.get('target_market_copy'))}\"。")
            if _meaningful(copy_block.get('secondary_copy')): rows.append(f"次级文字：\"{_txt(copy_block.get('secondary_copy'))}\"。")
        elif copy_mode=='POST_COMPOSITE':
            rows.append('按已设计的信息层级保留清晰文字区和足够负空间；画面中不要生成营销文字。')
        elif copy_mode=='UNRESOLVED_AGENT_DECISION' and _meaningful(copy_block.get('target_market_copy')):
            missing.append('copy_render_mode')
        if f.get('copy_zone'): rows.append(f"文字安全区：{_txt(f['copy_zone'])}。")
        if f.get('typography') and copy_mode in {'MODEL_RENDER','HYBRID'}: rows.append(f"文字视觉方向：{_txt(f['typography'])}。")
        constraints=[]
        if f.get('approved_visual_elements'): constraints.append('只使用这些已批准视觉元素：'+_txt(f['approved_visual_elements']))
        if f.get('precision_boundaries'): constraints.append('严格边界：'+_txt(f['precision_boundaries']))
        if constraints: rows.append('约束：'+'；'.join(constraints)+'。')
        rows.append('保持产品事实、包装身份、成分/规格和已批准宣称真实；不要虚构检测、认证、疗效、前后对比、材质或不存在的产品细节。')
        return '\n'.join(rows).strip()+'\n', list(dict.fromkeys(missing))

    rows=[]
    rows.append('Create a production-ready commercial visual for the selected generation model.' if not is_video else 'Create a production-ready commercial short video for the selected video generation model.')
    if f.get('output_spec'): rows.append(f"Output: {_txt(f['output_spec'])}.")
    if f.get('visual_objective'): rows.append(f"Visual objective: {_txt(f['visual_objective'])}.")
    if f.get('visual_carrier'): rows.append(f"Visual carrier: {_txt(f['visual_carrier'])}.")
    if f.get('visual_language'): rows.append(f"Visual language: {_txt(f['visual_language'])}.")
    if f.get('creative_thesis'): rows.append(f"Creative idea: {_txt(f['creative_thesis'])}.")
    if f.get('decisive_moment'): rows.append(f"Decisive moment: {_txt(f['decisive_moment'])}.")
    scene=[]
    for k,label in [('subject','subject'),('action','action'),('environment','environment'),('props','props'),('human_context','people/casting')]:
        if f.get(k): scene.append(f"{label}: {_txt(f[k])}")
    if scene: rows.append('Scene and subject — '+'; '.join(scene)+'.')
    if presence: rows.append(presence)
    comp=[]
    for k,label in [('composition','composition'),('spatial_rhythm','spatial rhythm'),('layout_geometry','relative placement'),('scale_depth','scale/depth'),('product_occupancy','product occupancy'),('focal_path','eye path'),('negative_space','negative space')]:
        if f.get(k): comp.append(f"{label}: {_txt(f[k])}")
    if comp: rows.append('Composition and space — '+'; '.join(comp)+'.')
    if f.get('evidence_hierarchy'): rows.append(f"Evidence hierarchy: {_txt(f['evidence_hierarchy'])}.")
    camera=[]
    for k,label in [('camera_view','view'),('focal_length','focal length'),('lens_family','lens'),('perspective','perspective'),('camera_position','camera position'),('focus_dof','focus/DOF')]:
        if f.get(k): camera.append(f"{label}: {_txt(f[k])}")
    if camera: rows.append('Camera — '+'; '.join(camera)+'.')
    light=[]
    for k,label in [('lighting','lighting'),('prelight','prelight reference'),('cmf','CMF'),('material_response','material response'),('palette','palette'),('color_management','color management')]:
        if f.get(k): light.append(f"{label}: {_txt(f[k])}")
    if light: rows.append('Lighting, material and color — '+'; '.join(light)+'.')
    if f.get('inclusive_human'): rows.append(f"Human representation: {_txt(f['inclusive_human'])}.")
    if is_video:
        video=[]
        for k,label in [('motion_timing','duration/rhythm'),('shot_sequence','shot sequence'),('camera_motion','camera motion'),('transition_audio','transitions/audio')]:
            if f.get(k): video.append(f"{label}: {_txt(f[k])}")
        if video: rows.append('Motion execution — '+'; '.join(video)+'.')
    if f.get('post_look'): rows.append(f"Finishing look: {_txt(f['post_look'])}.")
    if copy_mode in {'MODEL_RENDER','HYBRID'} and _meaningful(copy_block.get('target_market_copy')):
        rows.append(f"Render this exact visible market copy: \"{_txt(copy_block.get('target_market_copy'))}\".")
        if _meaningful(copy_block.get('secondary_copy')): rows.append(f"Secondary visible copy: \"{_txt(copy_block.get('secondary_copy'))}\".")
    elif copy_mode=='POST_COMPOSITE':
        rows.append('Preserve the authored typography zone and clean negative space; generate no marketing text inside the image.')
    elif copy_mode=='UNRESOLVED_AGENT_DECISION' and _meaningful(copy_block.get('target_market_copy')):
        missing.append('copy_render_mode')
    if f.get('copy_zone'): rows.append(f"Typography safe zone: {_txt(f['copy_zone'])}.")
    if f.get('typography') and copy_mode in {'MODEL_RENDER','HYBRID'}: rows.append(f"Typography direction: {_txt(f['typography'])}.")
    constraints=[]
    if f.get('approved_visual_elements'): constraints.append('use only approved visual elements: '+_txt(f['approved_visual_elements']))
    if f.get('precision_boundaries'): constraints.append('hard boundaries: '+_txt(f['precision_boundaries']))
    if constraints: rows.append('Constraints — '+'; '.join(constraints)+'.')
    rows.append('Keep verified product facts, packaging identity, ingredients/specifications and approved claims truthful. Do not invent tests, certifications, efficacy, before/after results, materials or nonexistent product details.')
    text='\n'.join(rows).strip()+'\n'
    if _CJK_RE.search(text):
        missing.append('english_model_prompt_language_purity')
    return text, list(dict.fromkeys(missing))


def _production_notes(asset: Mapping[str, Any], card: Mapping[str, Any], bundle: Mapping[str, Any], copy_block: Mapping[str, Any], copy_mode: str) -> dict[str, Any]:
    renderer=deepcopy(dict(bundle.get('renderer_recipe') or {}))
    product=deepcopy(dict(card.get('product_identity') or {}))
    editable=deepcopy(dict(card.get('editable_layer_contract') or {}))
    return {
        'copy_render_mode': copy_mode,
        'visible_copy_block': deepcopy(dict(copy_block)),
        'product_fidelity': product.get('product_fidelity') or asset.get('product_fidelity'),
        'product_presence': deepcopy(dict(card.get('product_presence') or {})),
        'product_reference_rule': product.get('rule'),
        'source_product_bindings': deepcopy(renderer.get('source_product_bindings') or []),
        'editable_layers': deepcopy(editable.get('editable_layers') or []),
        'frozen_layers': deepcopy(editable.get('frozen_layers') or []),
        'revision_rule': editable.get('revision_rule'),
        'layer_plan': deepcopy(renderer.get('layer_plan') or []),
        'provider_route': renderer.get('route'),
        'assembly_principle': 'Production/assembly instructions are separate from model prompts. Copy composition, locked-source compositing, editable layers and provider execution must not pollute the model-facing prompt.',
    }


def _flatten_selected(asset: Mapping[str, Any], card: Mapping[str, Any], copy_mode: str) -> list[dict[str, Any]]:
    art=_art(asset)
    fields, _=_model_fields(asset, card, 'CN')
    rows=[]
    for key,value in fields.items():
        rows.append({'decision':key,'selected_value':deepcopy(value),'projection_target':'MODEL_PROMPT'})
    presence=card.get('product_presence') or {}
    if _meaningful(presence): rows.append({'decision':'product_presence','selected_value':deepcopy(dict(presence)),'projection_target':'MODEL_PROMPT_AND_PRODUCTION_NOTES'})
    if _meaningful(asset.get('visible_copy')):
        rows.append({'decision':'visible_copy','selected_value':deepcopy(asset.get('visible_copy')),'projection_target':'MODEL_PROMPT' if copy_mode in {'MODEL_RENDER','HYBRID'} else 'VISIBLE_COPY_BLOCK_AND_PRODUCTION_NOTES'})
        rows.append({'decision':'copy_render_mode','selected_value':copy_mode,'projection_target':'PRODUCTION_NOTES'})
    for key in ('source_reference_role','production_route','fidelity','editable_layers','frozen_layers'):
        value=_first(art,key)
        if _meaningful(value): rows.append({'decision':key,'selected_value':deepcopy(value),'projection_target':'PRODUCTION_NOTES'})
    return rows


def _contains_value(text: str, value: Any) -> bool:
    if not _meaningful(value):
        return True
    if isinstance(value, Mapping):
        leaves=[v for v in value.values() if _meaningful(v)]
        return all(_contains_value(text,v) for v in leaves[:12])
    if isinstance(value, (list, tuple)):
        return all(_contains_value(text,v) for v in list(value)[:12])
    raw=str(value).strip()
    if not raw:
        return True
    return raw in text


def _audit(asset: Mapping[str, Any], card: Mapping[str, Any], prompt_cn: str, prompt_en: str, notes: Mapping[str, Any], copy_mode: str, lang_missing: list[str]) -> dict[str, Any]:
    selected=_flatten_selected(asset,card,copy_mode)
    notes_text=json.dumps(notes,ensure_ascii=False,sort_keys=True)
    checks=[]
    for row in selected:
        target=row['projection_target']
        value=row['selected_value']
        if target=='MODEL_PROMPT':
            ok=_contains_value(prompt_cn,value) or _contains_value(prompt_en,value)
        elif target=='PRODUCTION_NOTES':
            ok=_contains_value(notes_text,value)
        elif target=='VISIBLE_COPY_BLOCK_AND_PRODUCTION_NOTES':
            ok=_contains_value(notes_text,value)
        else:
            ok=_contains_value(prompt_cn,value) or _contains_value(prompt_en,value) or _contains_value(notes_text,value)
        checks.append({**row,'projected':bool(ok)})
    english_pure=not bool(_CJK_RE.search(prompt_en))
    jargon=[term for term in _ENGINEERING_JARGON if term in prompt_en.casefold() or term in prompt_cn.casefold()]
    checks.append({'decision':'english_model_prompt_language_purity','required':True,'projected':english_pure,'selected_value':'NO_CJK_IN_EN_MODEL_INSTRUCTIONS'})
    checks.append({'decision':'model_prompt_engineering_jargon_separation','required':True,'projected':not jargon,'selected_value':'NO_RUNTIME_ASSEMBLY_JARGON_IN_MODEL_PROMPT','found':jargon})
    missing=[x['decision'] for x in checks if x.get('required',True) and not x.get('projected')]
    missing.extend(lang_missing)
    if copy_mode=='UNRESOLVED_AGENT_DECISION' and _meaningful(asset.get('visible_copy')):
        missing.append('copy_render_mode')
    missing=list(dict.fromkeys(missing))
    return {
        'status':'PASS' if not missing else 'INCOMPLETE',
        'authority':'MODEL_NATIVE_PROMPT_CONSUMPTION',
        'principle':'Audit concrete selected values, language purity and model/assembly separation. Generic field-name presence is not evidence of parameter consumption.',
        'checks':checks,
        'missing_decisions':missing,
        'english_language_pure':english_pure,
        'engineering_jargon_in_model_prompt':jargon,
    }


def apply_model_native_prompt_contract(bundle: Mapping[str, Any], asset: Mapping[str, Any]) -> dict[str, Any]:
    out=deepcopy(dict(bundle))
    card=out.get('design_card') or {}
    copy_block=_visible_copy_block(asset,card)
    copy_mode=_copy_render_mode(asset,_art(asset),copy_block)
    prompt_cn,missing_cn=_render_prompt(asset,card,'CN',copy_block,copy_mode)
    prompt_en,missing_en=_render_prompt(asset,card,'EN',copy_block,copy_mode)
    notes=_production_notes(asset,card,out,copy_block,copy_mode)
    audit=_audit(asset,card,prompt_cn,prompt_en,notes,copy_mode,list(dict.fromkeys(missing_cn+missing_en)))

    out['model_prompt_cn']=prompt_cn
    out['model_prompt_en']=prompt_en
    # Backward-compatible aliases now point ONLY to model-facing prompts.
    out['prompt_cn']=prompt_cn
    out['prompt_en']=prompt_en
    out['visible_copy_block']=copy_block
    out['production_assembly_notes']=notes
    out['prompt_consumption_audit']=audit
    out['deterministic_copy_overlay']=copy_block.get('raw') or {}

    renderer=dict(out.get('renderer_recipe') or {})
    renderer['text_policy']={
        'copy_render_mode':copy_mode,
        'visible_copy_present':bool(_meaningful(copy_block.get('target_market_copy')) or _meaningful(copy_block.get('secondary_copy'))),
        'copy_block_ref':'visible_copy_block',
        'model_prompt_contains_exact_copy':copy_mode in {'MODEL_RENDER','HYBRID'},
        'assembly_notes_ref':'production_assembly_notes',
    }
    renderer.pop('deterministic_text_composition',None)
    out['renderer_recipe']=renderer

    unresolved=list(audit.get('missing_decisions') or [])
    hard_language_gap=any(x in unresolved for x in ('model_prompt_en_language_purity','english_model_prompt_language_purity')) or any(str(x).startswith(('visual_objective','subject','action','environment','composition','creative_thesis','visual_language')) for x in unresolved)
    if hard_language_gap:
        out['status']='BILINGUAL_RENDER_SEMANTICS_REQUIRED'
    elif 'copy_render_mode' in unresolved:
        out['status']='COPY_RENDER_MODE_REQUIRED'
    elif unresolved and str(out.get('status') or '').startswith('CANONICAL_PROMPT'):
        out['status']='MODEL_PROMPT_NEEDS_AGENT_DECISIONS'
    elif not unresolved and str(out.get('status') or '') not in {'AGENT_ART_DIRECTION_REQUIRED'}:
        out['status']='MODEL_NATIVE_PROMPT_READY'
    return out


def wrap_compile_asset_prompt(compile_fn):
    def compiled(
        asset: dict[str, Any],
        product: dict[str, Any],
        target: dict[str, Any],
        culture: dict[str, Any],
        language_contract: dict[str, Any],
        locale_profiles: dict[str, Any] | None = None,
        photography: dict[str, Any] | None = None,
        strategy_authority: dict[str, Any] | None = None,
        source_product_assets: list[dict[str, Any]] | None = None,
    ):
        bundle=compile_fn(asset,product,target,culture,language_contract,locale_profiles,photography,strategy_authority,source_product_assets)
        return apply_model_native_prompt_contract(bundle,asset)
    return compiled
