from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Mapping

_PHOTO_TERMS=('photo','photograph','photographic','camera','lens','portrait','lifestyle photography','real-photo','摄影','拍摄','镜头','人像摄影','生活方式摄影')
_HUMAN_TERMS=('human','person','people','model','portrait','face','hand','body','skin','hair','user','人物','人像','模特','面部','脸','手','身体','皮肤','发质','用户')


def _blob(value:Any)->str:
    try:
        return json.dumps(value,ensure_ascii=False).casefold()
    except Exception:
        return str(value).casefold()


def _meaningful(value:Any)->bool:
    return value not in (None,'',[],{})


def _first(art:Mapping[str,Any],*keys:str)->Any:
    for key in keys:
        value=art.get(key)
        if _meaningful(value):
            return value
    return None


def _merge_selected(base:Any, additions:dict[str,Any])->dict[str,Any]:
    out=deepcopy(dict(base)) if isinstance(base,Mapping) else {}
    for key,value in additions.items():
        if _meaningful(value) and key not in out:
            out[key]=deepcopy(value)
    return out


def _agent_selected_photographic_route(asset:Mapping[str,Any])->bool:
    art=asset.get('asset_art_direction') or {}
    if not isinstance(art,Mapping):
        return False
    searchable={k:art.get(k) for k in (
        'visual_carrier','visual_language','image_language','style','production_route','media_route',
        'camera_or_view','focal_length_mm','lens','lens_family','camera_position','working_distance','camera_height',
        'yaw','pitch','roll','shot_size','focus_dof','focus_plane','aperture','shutter','iso','lighting','prelight'
    ) if _meaningful(art.get(k))}
    text=_blob(searchable)
    if any(term in text for term in _PHOTO_TERMS):
        return True
    return any(_meaningful(art.get(k)) for k in (
        'focal_length_mm','lens','lens_family','camera_position','working_distance','camera_height','yaw','pitch','roll',
        'shot_size','focus_dof','focus_plane','aperture','shutter','iso','lighting','prelight'
    ))


def _agent_human_context(asset:Mapping[str,Any])->Any:
    art=asset.get('asset_art_direction') or {}
    if not isinstance(art,Mapping):
        return None
    values=[art.get(k) for k in ('human_context','people','casting','subject','action') if _meaningful(art.get(k))]
    text=_blob(values)
    if any(term in text for term in _HUMAN_TERMS):
        return art.get('human_context') or art.get('people') or art.get('casting') or art.get('subject') or art.get('action')
    return None


def wrap_derived_photo_contract(fn):
    """Consume the complete Agent-selected photographic execution program when photographic grammar is active."""
    def derived(asset:dict[str,Any], strategy_authority:dict[str,Any]|None, explicit:dict[str,Any]|None):
        work=deepcopy(asset)
        execution=deepcopy(dict(explicit or {}))
        art=work.get('asset_art_direction') or {}

        human=_agent_human_context(work)
        if _meaningful(human):
            brief=deepcopy(dict(work.get('creative_brief') or {}))
            brief.setdefault('human',human)
            work['creative_brief']=brief

        if _agent_selected_photographic_route(work):
            execution['photographic_route']=True
            execution['inherit_strategy_photography']=True
            if isinstance(art,Mapping):
                camera_position=art.get('camera_position') if isinstance(art.get('camera_position'),Mapping) else {}
                focus_dof=art.get('focus_dof') if isinstance(art.get('focus_dof'),Mapping) else {}
                camera=_merge_selected(execution.get('camera'), {
                    'focal_length_mm':_first(art,'focal_length_mm','focal_length'),
                    'lens_family':_first(art,'lens_family','lens'),
                    'preferred_view':_first(art,'camera_or_view','preferred_view','view'),
                    'working_distance':_first(art,'working_distance') or camera_position.get('working_distance'),
                    'camera_height':_first(art,'camera_height') or camera_position.get('camera_height'),
                    'yaw':_first(art,'yaw','camera_yaw') or camera_position.get('yaw'),
                    'pitch':_first(art,'pitch','camera_pitch') or camera_position.get('pitch'),
                    'roll':_first(art,'roll','camera_roll') or camera_position.get('roll'),
                    'shot_size':_first(art,'shot_size') or camera_position.get('shot_size'),
                    'perspective':_first(art,'perspective','projection') or camera_position.get('perspective'),
                    'focus_plane':_first(art,'focus_plane') or focus_dof.get('focus_plane'),
                    'aperture':_first(art,'aperture','f_stop') or focus_dof.get('aperture'),
                    'dof':_first(art,'dof','depth_of_field') or focus_dof.get('dof'),
                    'shutter_speed':_first(art,'shutter','shutter_speed') or focus_dof.get('shutter'),
                    'iso':_first(art,'iso','ISO') or focus_dof.get('iso'),
                })
                if camera:
                    execution['camera']=camera

                lighting_source=art.get('lighting') if isinstance(art.get('lighting'),Mapping) else {}
                lighting=_merge_selected(execution.get('lighting'), {
                    'key':_first(art,'key','key_light') or lighting_source.get('key'),
                    'fill':_first(art,'fill','fill_light') or lighting_source.get('fill'),
                    'negative_fill':_first(art,'negative_fill') or lighting_source.get('negative_fill'),
                    'rim':_first(art,'rim','rim_light') or lighting_source.get('rim'),
                    'modifier':_first(art,'modifier','modifier_geometry') or lighting_source.get('modifier'),
                    'modifier_size':_first(art,'modifier_size') or lighting_source.get('modifier_size'),
                    'modifier_distance':_first(art,'modifier_distance') or lighting_source.get('modifier_distance'),
                    'modifier_angle':_first(art,'modifier_angle') or lighting_source.get('modifier_angle'),
                    'cct':_first(art,'cct','CCT') or lighting_source.get('cct'),
                    'white_balance':_first(art,'white_balance','wb','WB') or lighting_source.get('white_balance'),
                    'exposure_ratio_plan':_first(art,'light_ratio','exposure_ratio','exposure_ratio_plan') or lighting_source.get('light_ratio') or lighting_source.get('exposure_ratio_plan'),
                    'shadow':_first(art,'shadow_policy','shadow') or lighting_source.get('shadow_policy') or lighting_source.get('shadow'),
                    'highlight_policy':_first(art,'highlight_policy') or lighting_source.get('highlight_policy'),
                    'reflection':_first(art,'reflection','reflection_control') or lighting_source.get('reflection'),
                    'polarization_plan':_first(art,'polarization','polarization_plan') or lighting_source.get('polarization') or lighting_source.get('polarization_plan'),
                    'prelight_plan':_first(art,'prelight','prelight_plan') or lighting_source.get('prelight'),
                })
                if lighting:
                    execution['lighting']=lighting

                if isinstance(art.get('cmf'),Mapping):
                    execution['cmf']=deepcopy(dict(art.get('cmf') or {}))
                if _meaningful(art.get('color_management')):
                    execution['color_management']=deepcopy(art.get('color_management'))
                if _meaningful(art.get('inclusive_human')) and not _meaningful(execution.get('inclusive_photography')):
                    execution['inclusive_photography']=deepcopy(art.get('inclusive_human'))
                if _meaningful(art.get('post_look')):
                    execution['post_look']=deepcopy(art.get('post_look'))

        return fn(work,strategy_authority,execution)
    return derived
