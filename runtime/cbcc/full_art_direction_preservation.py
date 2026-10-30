from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def _meaningful(value: Any) -> bool:
    return value not in (None, '', [], {})


def _dict(value: Any) -> dict[str, Any]:
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}


def _merge_preserve(base: Any, additions: dict[str, Any]) -> dict[str, Any]:
    if isinstance(base, Mapping):
        out = deepcopy(dict(base))
    elif _meaningful(base):
        out = {'description': deepcopy(base)}
    else:
        out = {}
    for key, value in additions.items():
        if _meaningful(value) and key not in out:
            out[key] = deepcopy(value)
    return out


def _first(art: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value = art.get(key)
        if _meaningful(value):
            return value
    return None


def normalize_full_art_direction(asset: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize already-authored Art Direction without inventing creative decisions.

    The historical runtime accepts several compatibility shapes. This bridge preserves the complete
    authored commercial world by collecting equivalent top-level values into the structured fields
    consumed by downstream Design Card / model-native prompt code. It is intentionally additive:
    existing structured values win, and no missing creative choice is fabricated.
    """
    out = deepcopy(dict(asset))
    raw = out.get('asset_art_direction')
    if not isinstance(raw, Mapping):
        return out
    art = deepcopy(dict(raw))

    # Human/casting layer. Keep a previously authored human_context/people/casting object intact,
    # then add explicit person execution details when they exist elsewhere in the Art Direction.
    human = _merge_preserve(
        _first(art, 'human_context', 'people', 'casting'),
        {
            'role': _first(art, 'human_role', 'person_role', 'casting_role'),
            'age': _first(art, 'age', 'age_range'),
            'gender_presentation': _first(art, 'gender_presentation', 'gender'),
            'skin_tone': _first(art, 'skin_tone', 'complexion'),
            'hair': _first(art, 'hair', 'hair_style', 'hair_texture'),
            'makeup': _first(art, 'makeup', 'grooming'),
            'wardrobe': _first(art, 'wardrobe', 'clothing'),
            'accessories': _first(art, 'accessories'),
            'body_type': _first(art, 'body_type', 'body'),
            'disability': _first(art, 'disability', 'assistive_device'),
            'religious_cultural_presentation': _first(art, 'religious_cultural_presentation', 'cultural_presentation'),
            'pose': _first(art, 'pose', 'posture'),
            'expression': _first(art, 'expression', 'facial_expression'),
            'gaze': _first(art, 'gaze', 'eye_line'),
            'hand_action': _first(art, 'hand_action', 'hand_gesture', 'handling'),
            'product_interaction': _first(art, 'product_interaction', 'human_product_interaction'),
            'scene_relationship': _first(art, 'human_scene_relationship', 'subject_scene_relationship'),
        },
    )
    if human:
        art['human_context'] = human

    # Camera geometry. Normalize values selected at top level into the camera_position object used
    # by model-native prompt rendering and photography execution.
    camera = _merge_preserve(
        art.get('camera_position'),
        {
            'working_distance': _first(art, 'working_distance', 'camera_distance', 'distance'),
            'camera_height': _first(art, 'camera_height', 'camera_height_relative'),
            'yaw': _first(art, 'yaw', 'camera_yaw', 'azimuth'),
            'pitch': _first(art, 'pitch', 'camera_pitch', 'elevation'),
            'roll': _first(art, 'roll', 'camera_roll', 'roll_deg'),
            'shot_size': _first(art, 'shot_size', 'framing', 'shot_scale'),
            'perspective': _first(art, 'perspective', 'projection'),
        },
    )
    if camera:
        art['camera_position'] = camera

    focus = _merge_preserve(
        art.get('focus_dof'),
        {
            'focus_plane': _first(art, 'focus_plane', 'focus_target'),
            'aperture': _first(art, 'aperture', 'f_stop'),
            'dof': _first(art, 'dof', 'depth_of_field', 'aperture_dof_intent'),
            'shutter': _first(art, 'shutter', 'shutter_speed'),
            'iso': _first(art, 'iso', 'ISO'),
            'motion_behavior': _first(art, 'motion_behavior', 'motion_blur_policy'),
        },
    )
    if focus:
        art['focus_dof'] = focus

    # Lighting program. Top-level physical lighting selections are preserved even when the original
    # author used a flat schema instead of nested `lighting`.
    lighting = _merge_preserve(
        _first(art, 'lighting', 'lighting_program'),
        {
            'key': _first(art, 'key', 'key_light'),
            'fill': _first(art, 'fill', 'fill_light'),
            'negative_fill': _first(art, 'negative_fill'),
            'rim': _first(art, 'rim', 'rim_light'),
            'modifier': _first(art, 'modifier', 'modifier_geometry'),
            'modifier_size': _first(art, 'modifier_size'),
            'modifier_distance': _first(art, 'modifier_distance'),
            'modifier_angle': _first(art, 'modifier_angle'),
            'cct': _first(art, 'cct', 'CCT'),
            'white_balance': _first(art, 'white_balance', 'wb', 'WB'),
            'light_ratio': _first(art, 'light_ratio', 'exposure_ratio', 'exposure_ratio_plan'),
            'shadow_policy': _first(art, 'shadow_policy', 'shadow'),
            'highlight_policy': _first(art, 'highlight_policy'),
            'reflection': _first(art, 'reflection', 'reflection_control'),
            'polarization': _first(art, 'polarization', 'polarization_plan'),
            'prelight': _first(art, 'prelight', 'prelight_plan'),
            'background_light': _first(art, 'background_light'),
        },
    )
    if lighting:
        art['lighting'] = lighting
    if not _meaningful(art.get('prelight')) and _meaningful(lighting.get('prelight')):
        art['prelight'] = deepcopy(lighting.get('prelight'))

    # CMF / physical material response.
    cmf = _merge_preserve(
        _first(art, 'cmf', 'material_program'),
        {
            'material': _first(art, 'material'),
            'finish': _first(art, 'finish'),
            'surface_behavior': _first(art, 'surface_behavior'),
            'microtexture': _first(art, 'microtexture'),
            'transparency': _first(art, 'transparency', 'translucency'),
            'reflection': _first(art, 'material_reflection'),
            'refraction': _first(art, 'refraction'),
            'highlight_behavior': _first(art, 'highlight_behavior'),
            'subsurface': _first(art, 'subsurface'),
            'deformation': _first(art, 'deformation'),
            'contact_behavior': _first(art, 'contact_behavior'),
            'palette_hex': _first(art, 'palette_hex', 'palette'),
        },
    )
    if cmf:
        art['cmf'] = cmf

    # Finishing is model-visible and must not disappear into QA or production metadata.
    if not _meaningful(art.get('post_look')):
        finish = _first(art, 'finishing', 'finishing_look', 'final_grade', 'grade', 'post_finish')
        if _meaningful(finish):
            art['post_look'] = deepcopy(finish)

    # Preserve detailed spatial/typographic fields under names already consumed downstream.
    aliases = {
        'layout_geometry': ('layout_geometry', 'relative_placement', 'placement_relationships'),
        'scale_depth': ('scale_depth', 'scale_relationships', 'depth_program'),
        'product_occupancy': ('product_occupancy', 'product_frame_ratio', 'product_scale_percent'),
        'focal_path': ('focal_path', 'eye_path'),
        'negative_space': ('negative_space', 'copy_negative_space'),
        'copy_zone': ('copy_zone', 'text_zone', 'safe_zone'),
        'evidence_hierarchy': ('evidence_hierarchy', 'proof_hierarchy', 'evidence_plane'),
        'typography': ('typography', 'type_system', 'type_direction'),
        'material_response': ('material_response', 'surface_response'),
        'color_management': ('color_management',),
    }
    for target, keys in aliases.items():
        if not _meaningful(art.get(target)):
            value = _first(art, *keys)
            if _meaningful(value):
                art[target] = deepcopy(value)

    out['asset_art_direction'] = art
    return out


def wrap_compile_asset_prompt(compile_fn):
    """Normalize full Art Direction before any downstream compiler/wrapper sees the asset."""
    def compiled(*args, **kwargs):
        if args:
            call_args = list(args)
            call_args[0] = normalize_full_art_direction(call_args[0] or {})
            return compile_fn(*call_args, **kwargs)
        call_kwargs = dict(kwargs)
        if 'asset' in call_kwargs:
            call_kwargs['asset'] = normalize_full_art_direction(call_kwargs.get('asset') or {})
        return compile_fn(**call_kwargs)
    return compiled
