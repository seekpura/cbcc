from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any, Mapping

_CJK_RE = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')
_LOCKED_FIDELITY = {'LOCKED_PIXEL', 'LOCKED_SOURCE_COMPOSITE', 'COMPOSITE'}
_PHOTO_HINTS = ('photo','photograph','portrait','camera','lens','macro','still-life','creator','ugc','摄影','人像','镜头','微距','静物')
_VIDEO_HINTS = ('video','motion','creator','ugc','short-form','短视频','视频','动效')


def _meaningful(v: Any) -> bool:
    if v in (None, '', [], {}):
        return False
    if isinstance(v, Mapping):
        return any(_meaningful(x) for x in v.values())
    if isinstance(v, (list, tuple, set, frozenset)):
        return any(_meaningful(x) for x in v)
    return True


def _txt(v: Any) -> str:
    if not _meaningful(v):
        return ''
    if isinstance(v, Mapping):
        return '; '.join(f'{k}={_txt(x)}' for k, x in v.items() if _meaningful(x))
    if isinstance(v, (list, tuple, set, frozenset)):
        return '; '.join(_txt(x) for x in v if _meaningful(x))
    return str(v).strip()


def _blob(v: Any) -> str:
    try:
        return json.dumps(v, ensure_ascii=False).casefold()
    except Exception:
        return str(v).casefold()


def _art(asset: Mapping[str, Any], card: Mapping[str, Any]) -> dict[str, Any]:
    raw = asset.get('asset_art_direction')
    if not isinstance(raw, Mapping):
        raw = card.get('agent_art_direction')
    return deepcopy(dict(raw)) if isinstance(raw, Mapping) else {}


def _nested(art: Mapping[str, Any], *groups: str) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = [art]
    for g in groups:
        v = art.get(g)
        if isinstance(v, Mapping):
            rows.append(v)
    return rows


def _pick(art: Mapping[str, Any], keys: tuple[str, ...], groups: tuple[str, ...] = ()) -> Any:
    for row in _nested(art, *groups):
        for k in keys:
            if _meaningful(row.get(k)):
                return deepcopy(row.get(k))
    return None


def _route_flags(asset: Mapping[str, Any], card: Mapping[str, Any], art: Mapping[str, Any]) -> tuple[bool, bool, bool]:
    text = _blob({
        'asset_type': asset.get('asset_type'),
        'production_mode': asset.get('production_mode'),
        'carrier': art.get('visual_carrier') or card.get('visual_carrier') or (card.get('information_assetization') or {}).get('representation'),
        'camera': art.get('camera_or_view'),
        'lighting': art.get('lighting'),
    })
    source_only = any(x in text for x in ('source_view','source-only','native_text','document','全源图'))
    video = str(asset.get('asset_type') or '').upper() == 'VIDEO' or any(x in text for x in _VIDEO_HINTS)
    photo = (not source_only) and (any(x in text for x in _PHOTO_HINTS) or any(_meaningful(art.get(k)) for k in ('focal_length_mm','lens_family','camera_position','lighting','prelight')))
    return photo, video, source_only


def _selected_parameters(asset: Mapping[str, Any], card: Mapping[str, Any]) -> dict[str, Any]:
    art = _art(asset, card)
    photo, video, source_only = _route_flags(asset, card, art)
    params: dict[str, Any] = {}

    def add(name: str, keys: tuple[str, ...], groups: tuple[str, ...] = ()) -> None:
        v = _pick(art, keys, groups)
        if _meaningful(v):
            params[name] = v

    # Spatial / information design parameters are generation-relevant even for source-composite plates.
    add('composition_grammar', ('composition_grammar','composition','spatial_grammar'), ('composition','layout'))
    add('layout_geometry', ('layout_geometry','relative_placement','placement_relationships','geometry'), ('composition','layout'))
    add('scale_depth', ('scale_depth','scale_relationships','depth_program','depth_structure'), ('composition','layout'))
    add('product_occupancy', ('product_occupancy','product_frame_ratio','product_scale_percent','occupancy'), ('composition','layout'))
    add('focal_path', ('focal_path','eye_path','visual_path'), ('composition','layout'))
    add('negative_space', ('negative_space','copy_negative_space'), ('composition','layout'))
    add('copy_zone', ('copy_zone','text_zone','safe_zone','typography_safe_zone'), ('composition','layout','typography'))
    add('evidence_hierarchy', ('evidence_hierarchy','proof_mechanism','evidence_plane','information_hierarchy'), ('evidence','information'))
    add('palette_hex', ('palette_hex','palette','color_world','color'), ('cmf','color'))
    add('cmf', ('cmf','material_program'), ('cmf',))
    add('material_response', ('material_response','surface_behavior','material_behavior'), ('cmf','material','lighting'))
    add('post_look', ('post_look','grade','finishing_look','finish'), ('post','finishing'))

    if photo:
        add('focal_length', ('focal_length_mm','focal_length','lens'), ('camera','photography'))
        add('lens_family', ('lens_family',), ('camera','photography'))
        add('working_distance', ('working_distance','working_distance_intent','distance'), ('camera','photography'))
        add('camera_height', ('camera_height',), ('camera','photography'))
        add('yaw_pitch_roll', ('yaw_pitch_roll','orientation'), ('camera','photography'))
        # Support split azimuth/elevation/roll fields without inventing values.
        if 'yaw_pitch_roll' not in params:
            orient={k:_pick(art,(k,),('camera','photography')) for k in ('azimuth','elevation','pitch','yaw','roll','roll_deg')}
            orient={k:v for k,v in orient.items() if _meaningful(v)}
            if orient: params['yaw_pitch_roll']=orient
        add('shot_size', ('shot_size','framing','crop'), ('camera','photography'))
        add('focus_plane', ('focus_plane','focus_target'), ('camera','photography'))
        add('aperture_dof', ('aperture','f_number','dof','focus_dof','aperture_dof_intent'), ('camera','photography'))
        add('shutter', ('shutter','shutter_speed','shutter_angle'), ('camera','photography'))
        add('iso', ('iso','ISO'), ('camera','photography'))
        add('key_light', ('key_light','key','key_geometry'), ('lighting',))
        add('fill_light', ('fill_light','fill','fill_geometry'), ('lighting',))
        add('negative_fill', ('negative_fill','negative_fill_geometry'), ('lighting',))
        add('rim_light', ('rim_light','rim','edge_light'), ('lighting',))
        add('modifier_geometry', ('modifier_geometry','modifier','diffusion','softbox','bounce','reflector'), ('lighting',))
        add('light_distance', ('light_distance','modifier_distance'), ('lighting',))
        add('cct', ('cct','cct_k','color_temperature'), ('lighting',))
        add('white_balance', ('white_balance','wb'), ('lighting','color'))
        add('light_ratio', ('light_ratio','key_fill_ratio','exposure_ratio','exposure_ratio_plan'), ('lighting',))
        add('shadow_policy', ('shadow_policy','shadow'), ('lighting',))
        add('highlight_policy', ('highlight_policy','highlight_rolloff','highlight_protection'), ('lighting',))
        add('exposure_policy', ('exposure_policy','exposure','metering'), ('lighting','camera','photography'))
        add('reflection_control', ('reflection_control','reflection','flags'), ('lighting','material'))
        add('polarization', ('polarization','polarization_plan','cpl'), ('lighting','material'))
        add('prelight', ('prelight','prelight_plan','prelight_reference'), ('lighting','photography'))
        add('color_management', ('color_management','color_space','output_color_space'), ('color','cmf','photography'))
        add('skin_tone_exposure', ('skin_tone_exposure','skin_tone_metering','deep_skin_shadow_protection'), ('human','casting','photography'))
        add('wardrobe_hair_makeup', ('wardrobe_hair_makeup','wardrobe','hair_makeup','styling'), ('human','casting'))

    if video:
        add('duration_timing', ('duration','timing','beat_timing','shot_timing'), ('video','motion'))
        add('shot_sequence', ('shot_sequence','shot_plan','storyboard'), ('video','motion'))
        add('camera_motion', ('camera_motion','motion_program'), ('video','motion','camera'))
        add('subject_motion', ('subject_motion','action_motion'), ('video','motion'))
        add('fps', ('fps','frame_rate'), ('video','motion','camera'))
        add('stabilization', ('stabilization','stabilisation'), ('video','motion','camera'))
        add('transition_audio', ('transition_audio','transitions','audio_direction','music_direction'), ('video','motion','audio'))
        add('cta_hold', ('cta_hold','end_frame_hold','final_hold'), ('video','motion'))
        add('subtitle_safe_zone', ('subtitle_safe_zone','caption_safe_zone'), ('video','motion','typography'))

    params['_route']={'photographic':photo,'video':video,'source_only':source_only}
    return params


def _required_groups(params: Mapping[str, Any], asset: Mapping[str, Any], card: Mapping[str, Any]) -> dict[str, list[str]]:
    art=_art(asset,card)
    # FULL/Agent-authored visual work must explicitly close execution depth. TASK_SCOPED callers may
    # opt out only with an explicit Art Direction reason, not by silently omitting the fields.
    required=bool(asset.get('art_direction_required')) and str(art.get('execution_depth_status') or '').upper() not in {'N/A','NOT_APPLICABLE','WAIVED_WITH_REASON'}
    if not required:
        return {}
    route=params.get('_route') or {}
    groups={
        'spatial_program':['composition_grammar','layout_geometry','scale_depth','focal_path','negative_space'],
        'visual_finish':['palette_hex','material_response','post_look'],
    }
    if route.get('photographic'):
        groups.update({
            'camera_geometry':['focal_length','working_distance','camera_height','yaw_pitch_roll','shot_size'],
            'focus_exposure':['focus_plane','aperture_dof'],
            'lighting_geometry':['key_light','fill_light','negative_fill','cct','white_balance','light_ratio','shadow_policy','highlight_policy'],
            'prelight_color':['prelight','color_management'],
        })
    if route.get('video'):
        groups.update({
            'video_timing':['duration_timing','shot_sequence'],
            'video_motion':['camera_motion','subject_motion'],
            'video_finish':['transition_audio','cta_hold'],
        })
    return groups


def _missing_required(params: Mapping[str, Any], groups: Mapping[str, list[str]], art: Mapping[str, Any]) -> list[str]:
    na=art.get('execution_na') or {}
    missing=[]
    for group, keys in groups.items():
        for key in keys:
            if _meaningful(params.get(key)):
                continue
            reason = na.get(key) if isinstance(na, Mapping) else None
            if _meaningful(reason):
                continue
            missing.append(key)
    return missing


def _append_selected(prompt: str, params: Mapping[str, Any], language: str) -> tuple[str, list[str]]:
    out=prompt.rstrip()
    appended=[]
    label_cn={
        'composition_grammar':'构图语法','layout_geometry':'相对位置','scale_depth':'尺度与纵深','product_occupancy':'商品占画','focal_path':'视线动线','negative_space':'负空间','copy_zone':'文字安全区','evidence_hierarchy':'证据层级','palette_hex':'配色','cmf':'CMF','material_response':'材质响应','post_look':'完成质感','focal_length':'焦段','lens_family':'镜头类型','working_distance':'工作距离','camera_height':'机位高度','yaw_pitch_roll':'机位角度','shot_size':'景别/取景','focus_plane':'对焦平面','aperture_dof':'光圈/景深','shutter':'快门','iso':'ISO','key_light':'主光','fill_light':'补光','negative_fill':'负补光','rim_light':'轮廓光','modifier_geometry':'控光附件/尺寸','light_distance':'灯距','cct':'色温','white_balance':'白平衡','light_ratio':'光比','shadow_policy':'阴影策略','highlight_policy':'高光策略','exposure_policy':'曝光策略','reflection_control':'反射控制','polarization':'偏振','prelight':'Prelight','color_management':'色彩管理','skin_tone_exposure':'肤色曝光','wardrobe_hair_makeup':'服装/发妆','duration_timing':'时长/节拍','shot_sequence':'镜头序列','camera_motion':'镜头运动','subject_motion':'主体运动','fps':'帧率','stabilization':'稳定方式','transition_audio':'转场/音频','cta_hold':'结尾停帧','subtitle_safe_zone':'字幕安全区'
    }
    label_en={k:k.replace('_',' ') for k in label_cn}
    for key,value in params.items():
        if key.startswith('_') or not _meaningful(value):
            continue
        raw=_txt(value)
        if not raw:
            continue
        if raw in out:
            continue
        if language=='EN' and _CJK_RE.search(raw):
            continue
        label=label_cn.get(key,key) if language=='CN' else label_en.get(key,key)
        sentence=(f'{label}：{raw}。' if language=='CN' else f'{label.capitalize()}: {raw}.')
        appended.append(sentence)
    if appended:
        lead='\n执行参数：' if language=='CN' else '\nExecution parameters: '
        sep='；' if language=='CN' else '; '
        out += lead + sep.join(x.rstrip('。.') for x in appended) + ('。' if language=='CN' else '.')
    return out+'\n', appended


def _locked_composite_instruction(asset: Mapping[str, Any], card: Mapping[str, Any], params: Mapping[str, Any], language: str) -> str:
    presence=card.get('product_presence') or {}
    state=str(presence.get('planning_state') or '').upper()
    if state in {'FORBIDDEN','ABSENT','NOT_APPLICABLE','UNRESOLVED_AGENT_DECISION',''}:
        return ''
    fidelity=str((card.get('product_identity') or {}).get('product_fidelity') or asset.get('product_fidelity') or '').upper()
    if fidelity not in _LOCKED_FIDELITY:
        return ''
    occ=_txt(params.get('product_occupancy') or presence.get('scale_relationship'))
    geom=_txt(params.get('layout_geometry') or params.get('composition_grammar'))
    depth=_txt(params.get('scale_depth'))
    camera='; '.join(_txt(params.get(k)) for k in ('focal_length','working_distance','camera_height','yaw_pitch_roll') if _meaningful(params.get(k)))
    light='; '.join(_txt(params.get(k)) for k in ('key_light','fill_light','negative_fill','cct','light_ratio','shadow_policy','highlight_policy','reflection_control') if _meaningful(params.get(k)))
    values=' '.join(x for x in (occ,geom,depth,camera,light) if x)
    if language=='EN' and _CJK_RE.search(values):
        return ''
    if language=='CN':
        return ('以最终合成画面而不是空背景为目标生成环境底片：为真实锁定商品保留准确的空间包络'
                + (f'（占画/尺度：{occ}）' if occ else '')
                + (f'，位置关系：{geom}' if geom else '')
                + (f'，纵深：{depth}' if depth else '')
                + (f'。环境透视按 {camera} 匹配' if camera else '')
                + (f'；接触面、阴影接收、反射与环境光按 {light} 匹配' if light else '')
                + '。不要生成、重画或替代真实商品本体，但生成底片必须让后续真实商品合成后看起来像同一次拍摄/同一个空间。')
    return ('Generate the environment plate for the final composite, not as an unrelated empty background. Preserve an exact spatial envelope for the locked real-product layer'
            + (f' with target occupancy/scale {occ}' if occ else '')
            + (f', placement {geom}' if geom else '')
            + (f', and depth relationship {depth}' if depth else '')
            + (f'. Match scene perspective to {camera}' if camera else '')
            + (f'; build the receiving surface, contact-shadow behavior, reflections and ambient light around {light}' if light else '')
            + '. Do not render, redraw or substitute the product itself; the plate must integrate the later real-product layer as if it belonged to the same photographed scene.')


def apply_production_parameter_closure(bundle: Mapping[str, Any], asset: Mapping[str, Any]) -> dict[str, Any]:
    out=deepcopy(dict(bundle))
    card=deepcopy(dict(out.get('design_card') or {}))
    art=_art(asset,card)
    params=_selected_parameters(asset,card)
    groups=_required_groups(params,asset,card)
    missing_required=_missing_required(params,groups,art)

    cn=out.get('model_prompt_cn') or out.get('prompt_cn') or ''
    en=out.get('model_prompt_en') or out.get('prompt_en') or ''
    cn,app_cn=_append_selected(cn,params,'CN')
    en,app_en=_append_selected(en,params,'EN')

    comp_cn=_locked_composite_instruction(asset,card,params,'CN')
    comp_en=_locked_composite_instruction(asset,card,params,'EN')
    if comp_cn and comp_cn not in cn:
        cn=cn.rstrip()+'\n'+comp_cn+'\n'
    if comp_en and comp_en not in en:
        en=en.rstrip()+'\n'+comp_en+'\n'

    selected={k:v for k,v in params.items() if not k.startswith('_')}
    missing_bilingual=[k for k,v in selected.items() if _CJK_RE.search(_txt(v)) and _txt(v) not in en]
    out['model_prompt_cn']=cn
    out['prompt_cn']=cn
    out['model_prompt_en']=en
    out['prompt_en']=en

    closure={
        'authority':'AGENT_AUTHORED_PARAMETERS_RUNTIME_CLOSURE',
        'principle':'Every selected pixel/behavior-changing execution value must be consumed by the model prompt or explicitly routed elsewhere. Runtime may compile selected values but may not invent missing creative parameters.',
        'route':params.get('_route'),
        'selected_parameters':selected,
        'required_groups':groups,
        'missing_required_parameters':missing_required,
        'english_render_semantics_missing_for':missing_bilingual,
        'compiled_parameter_additions_cn':app_cn,
        'compiled_parameter_additions_en':app_en,
        'locked_source_final_composite_instruction':bool(comp_cn or comp_en),
        'status':'PASS' if not missing_required and not missing_bilingual else 'INCOMPLETE',
        'project_completion_blocking':False,
        'model_generation_blocking':bool(missing_required or missing_bilingual),
    }
    out['production_parameter_closure']=closure

    audit=deepcopy(dict(out.get('prompt_consumption_audit') or {}))
    existing=list(audit.get('missing_decisions') or [])
    existing.extend(f'execution_parameter:{x}' for x in missing_required)
    existing.extend(f'english_render_semantics:{x}' for x in missing_bilingual)
    audit['missing_decisions']=list(dict.fromkeys(existing))
    if closure['model_generation_blocking']:
        audit['status']='INCOMPLETE'
    audit['production_parameter_closure']='PASS' if not closure['model_generation_blocking'] else 'INCOMPLETE'
    out['prompt_consumption_audit']=audit

    notes=deepcopy(dict(out.get('production_assembly_notes') or {}))
    notes['production_parameter_closure_ref']='production_parameter_closure'
    notes['final_composite_geometry']=deepcopy({k:selected.get(k) for k in ('composition_grammar','layout_geometry','scale_depth','product_occupancy','focal_path','negative_space') if _meaningful(selected.get(k))})
    out['production_assembly_notes']=notes

    if closure['model_generation_blocking']:
        out['model_prompt_status']='ART_DIRECTION_EXECUTION_DEPTH_REQUIRED'
    else:
        out['model_prompt_status']='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'
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
        return apply_production_parameter_closure(bundle,asset)
    return compiled
