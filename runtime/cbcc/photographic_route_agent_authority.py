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


def _agent_selected_photographic_route(asset:Mapping[str,Any])->bool:
    art=asset.get('asset_art_direction') or {}
    if not isinstance(art,Mapping):
        return False
    searchable={k:art.get(k) for k in (
        'visual_carrier','visual_language','image_language','style','production_route','media_route',
        'camera_or_view','focal_length_mm','lens','lens_family','camera_position','focus_dof','lighting','prelight'
    ) if art.get(k) not in (None,'',[],{})}
    text=_blob(searchable)
    if any(term in text for term in _PHOTO_TERMS):
        return True
    # Explicit camera/light decisions are themselves an Agent-authored choice of photographic grammar.
    return any(art.get(k) not in (None,'',[],{}) for k in ('focal_length_mm','lens','lens_family','camera_position','focus_dof','lighting','prelight'))


def _agent_human_context(asset:Mapping[str,Any])->Any:
    art=asset.get('asset_art_direction') or {}
    if not isinstance(art,Mapping):
        return None
    values=[art.get(k) for k in ('human_context','people','casting','subject','action') if art.get(k) not in (None,'',[],{})]
    text=_blob(values)
    if any(term in text for term in _HUMAN_TERMS):
        return art.get('human_context') or art.get('people') or art.get('casting') or art.get('subject') or art.get('action')
    return None


def wrap_derived_photo_contract(fn):
    """Let the Agent's media choice activate photography execution without making photography universal.

    A generative asset may intentionally use photographic grammar. Conversely, a graphic/illustration
    asset must not inherit camera/light fields just because the project has a photography toolbox.
    """
    def derived(asset:dict[str,Any], strategy_authority:dict[str,Any]|None, explicit:dict[str,Any]|None):
        work=deepcopy(asset)
        execution=deepcopy(dict(explicit or {}))
        art=work.get('asset_art_direction') or {}

        human=_agent_human_context(work)
        if human not in (None,'',[],{}):
            brief=deepcopy(dict(work.get('creative_brief') or {}))
            brief.setdefault('human',human)
            work['creative_brief']=brief

        if _agent_selected_photographic_route(work):
            execution['photographic_route']=True
            execution['inherit_strategy_photography']=True
            if isinstance(art,Mapping):
                camera=deepcopy(dict(execution.get('camera') or {}))
                if art.get('focal_length_mm') not in (None,'',[],{}): camera['focal_length_mm']=art.get('focal_length_mm')
                if art.get('lens_family') not in (None,'',[],{}): camera['lens_family']=art.get('lens_family')
                if art.get('camera_or_view') not in (None,'',[],{}): camera['preferred_view']=art.get('camera_or_view')
                if art.get('focus_dof') not in (None,'',[],{}): camera['dof']=art.get('focus_dof')
                if camera: execution['camera']=camera
                if isinstance(art.get('lighting'),Mapping): execution['lighting']=deepcopy(dict(art.get('lighting') or {}))
                if isinstance(art.get('cmf'),Mapping): execution['cmf']=deepcopy(dict(art.get('cmf') or {}))
                if art.get('color_management') not in (None,'',[],{}): execution['color_management']=art.get('color_management')

        return fn(work,strategy_authority,execution)
    return derived
