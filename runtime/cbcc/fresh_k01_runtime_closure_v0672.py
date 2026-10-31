from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping
import re

_INSTALLED = False
_GRAPHIC_TOKEN = re.compile(r'(?:^|[_\-\s])(graphic|infographic|diagram|chart|table|orthographic)(?:$|[_\-\s])', re.I)
_SCOPE_MODIFIER = re.compile(r'(?:额外|附加|另外|其他|无关|未批准|未经批准|未授权|多余|extra|additional|other|unrelated|unapproved|unauthori[sz]ed)', re.I)
_NO_COPY = (
    re.compile(r'(?:不|不要)(?:生成|渲染|显示|添加|加入)?\s*(?:任何|所有)?\s*(?:可见)?\s*(?:文字|文本|文案)(?:\s*或\s*数字)?', re.I),
    re.compile(r'(?:不|不要)(?:生成|渲染|显示|添加|加入)?\s*(?:任何|所有)?\s*数字', re.I),
    re.compile(r'(?:无|没有)\s*(?:任何)?\s*(?:可见)?\s*(?:文字|文本|文案)', re.I),
    re.compile(r'\b(?:do\s+not|don\'t)\s+(?:generate|render|show|display|add|include)\s+(?:any\s+|all\s+)?(?:visible\s+)?(?:text|copy|words|numbers)\b', re.I),
    re.compile(r'\bno\s+(?:visible\s+)?(?:text|copy|words|numbers)\b', re.I),
    re.compile(r'\bwithout\s+(?:any\s+)?(?:visible\s+)?(?:text|copy|words|numbers)\b', re.I),
)


def _meaningful(value: Any) -> bool:
    return value not in (None, '', [], {})


def _all_not_needed(contract: Any) -> bool:
    if not isinstance(contract, Mapping) or not contract:
        return False
    rows = [v for v in contract.values() if isinstance(v, Mapping)]
    return bool(rows) and all(str(v.get('status') or '').upper() == 'NOT_NEEDED' for v in rows)


def _explicit_no_visible_copy_instruction(text: str) -> bool:
    for raw_line in str(text or '').splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _SCOPE_MODIFIER.search(line):
            continue
        if any(pattern.search(line) for pattern in _NO_COPY):
            return True
    return False


def _patch_production_parameters() -> None:
    from . import production_parameter_closure as pp
    if getattr(pp, '_cbcc_v0672_fresh_k01_closure', False):
        return
    previous_route = pp._route_flags
    previous_selected = pp._selected_parameters
    previous_required = pp._required_groups

    def route_flags(asset, card, art):
        photo, video, source_only = previous_route(asset, card, art)
        carrier = str(art.get('visual_carrier') or card.get('visual_carrier') or '').strip()
        # Token semantics: GRAPHIC_EVIDENCE_AXIS is graphic; PHOTOGRAPHIC_PRODUCT_HERO is not.
        if _GRAPHIC_TOKEN.search(carrier):
            photo = False
        return photo, video, source_only

    def selected_parameters(asset, card):
        params = previous_selected(asset, card)
        art = pp._art(asset, card)
        route = params.get('_route') or {}
        if not route.get('photographic'):
            # Canonical video/creator timing may still be authored on a non-photographic motion carrier.
            if route.get('video') and not _meaningful(params.get('duration_timing')) and _meaningful(art.get('motion_timing')):
                params['duration_timing'] = deepcopy(art.get('motion_timing'))
            return params
        camera = art.get('camera_position') if isinstance(art.get('camera_position'), Mapping) else {}
        focus = art.get('focus_dof') if isinstance(art.get('focus_dof'), Mapping) else {}
        lighting = art.get('lighting') if isinstance(art.get('lighting'), Mapping) else {}

        def fill(name: str, value: Any, *, replace: bool = False) -> None:
            if _meaningful(value) and (replace or not _meaningful(params.get(name))):
                params[name] = deepcopy(value)

        fill('working_distance', camera.get('working_distance') or camera.get('distance'))
        fill('camera_height', camera.get('camera_height'))
        orientation = {k: camera.get(k) for k in ('yaw','pitch','roll','yaw_deg','pitch_deg','roll_deg','azimuth','elevation') if _meaningful(camera.get(k))}
        fill('yaw_pitch_roll', orientation)
        fill('shot_size', camera.get('shot_size'))
        fill('focus_plane', focus.get('focus_plane'))
        # Never let the whole focus_dof object masquerade as aperture. Consume the authored scalar intent.
        aperture = focus.get('aperture') or focus.get('aperture_dof_intent') or focus.get('dof')
        fill('aperture_dof', aperture, replace=_meaningful(aperture))
        fill('shutter', focus.get('shutter') or focus.get('shutter_speed'))
        fill('iso', focus.get('iso'))
        for name, keys in {
            'key_light': ('key_light','key'), 'fill_light': ('fill_light','fill'),
            'negative_fill': ('negative_fill',), 'rim_light': ('rim_light','rim'),
            'cct': ('cct','cct_k','color_temperature'),
            'light_ratio': ('light_ratio','key_fill_ratio','exposure_ratio','exposure_ratio_plan'),
            'shadow_policy': ('shadow_policy','shadow'), 'highlight_policy': ('highlight_policy','highlight_rolloff'),
            'reflection_control': ('reflection_control','reflection'),
            'polarization': ('polarization','polarization_plan'), 'prelight': ('prelight','prelight_plan'),
        }.items():
            fill(name, next((lighting.get(k) for k in keys if _meaningful(lighting.get(k))), None))
        if route.get('video') and not _meaningful(params.get('duration_timing')) and _meaningful(art.get('motion_timing')):
            params['duration_timing'] = deepcopy(art.get('motion_timing'))
        return params

    def required_groups(params, asset, card):
        groups = deepcopy(previous_required(params, asset, card))
        if not groups:
            return groups
        # Only parameters actually selected by this asset can be mandatory. Global/system defaults
        # must not manufacture missing work for a graphic, no-human or no-motion asset.
        finish = groups.get('visual_finish')
        if isinstance(finish, list) and not _meaningful(params.get('post_look')):
            groups['visual_finish'] = [k for k in finish if k != 'post_look']
        lighting = groups.get('lighting_geometry')
        if isinstance(lighting, list) and not _meaningful(params.get('shadow_policy')):
            groups['lighting_geometry'] = [k for k in lighting if k != 'shadow_policy']
        prelight = groups.get('prelight_color')
        if isinstance(prelight, list) and not _meaningful(params.get('color_management')):
            groups['prelight_color'] = [k for k in prelight if k != 'color_management']
        if (params.get('_route') or {}).get('video'):
            for name in ('video_timing','video_motion','video_finish'):
                keys = groups.get(name)
                if not isinstance(keys, list):
                    continue
                selected = [k for k in keys if _meaningful(params.get(k))]
                if selected:
                    groups[name] = selected
                else:
                    groups.pop(name, None)
        return groups

    pp._route_flags = route_flags
    pp._selected_parameters = selected_parameters
    pp._required_groups = required_groups
    pp._cbcc_v0672_fresh_k01_closure = True


def _patch_model_native() -> None:
    from . import model_native_prompt_contract as native
    if getattr(native, '_cbcc_v0672_fresh_k01_closure', False):
        return
    previous_copy = native._visible_copy_block
    previous_fields = native._model_fields

    def visible_copy_block(asset, card):
        out = previous_copy(asset, card)
        raw = out.get('raw') if isinstance(out.get('raw'), Mapping) else {}
        if not _meaningful(out.get('delivery_translation_zh')):
            for key in ('chinese_meaning','chinese_interpretation','delivery_translation_zh','delivery_translation','zh','zh-CN','chinese'):
                if _meaningful(raw.get(key)):
                    out['delivery_translation_zh'] = deepcopy(raw.get(key))
                    break
        return out

    def model_fields(asset, card, language):
        fields, missing = previous_fields(asset, card, language)
        art = native._art(asset)
        if _all_not_needed(art.get('typography_contract')):
            fields.pop('typography', None)
        if _all_not_needed(art.get('human_relevance_decisions')):
            fields.pop('inclusive_human', None)
            fields.pop('human_context', None)

        # A project-level Photography color-management contract must not create missing EN prose
        # on an explicitly graphic asset. Only asset-authored color management applies there.
        carrier = str(art.get('visual_carrier') or '').strip()
        if _GRAPHIC_TOKEN.search(carrier) and not _meaningful(art.get('color_management')):
            fields.pop('color_management', None)
            missing = [item for item in missing if item != 'color_management']
        return fields, missing

    native._visible_copy_block = visible_copy_block
    native._model_fields = model_fields
    native._cbcc_v0672_fresh_k01_closure = True


def _patch_copy_route_audit() -> None:
    from . import long_requirement_full_audit as audit
    audit._explicit_no_visible_copy_instruction = _explicit_no_visible_copy_instruction
    audit._cbcc_v0672_fresh_k01_copy_semantics = True


def install() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    _patch_production_parameters()
    _patch_model_native()
    _patch_copy_route_audit()
