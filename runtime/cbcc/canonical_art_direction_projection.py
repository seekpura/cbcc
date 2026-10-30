from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .full_art_direction_preservation import normalize_full_art_direction


def _meaningful(v:Any)->bool:
    return v not in (None,'',[],{})

def _setdefault(out:dict[str,Any], key:str, value:Any)->None:
    if _meaningful(value) and not _meaningful(out.get(key)):
        out[key]=deepcopy(value)

def _first(src:Mapping[str,Any], *keys:str)->Any:
    for key in keys:
        v=src.get(key)
        if _meaningful(v): return v
    return None

def _presence(value:Any)->dict[str,Any]:
    if isinstance(value,Mapping):
        out=deepcopy(dict(value))
        if out.get('state') and not out.get('planning_state'): out['planning_state']=out['state']
        if out.get('why') and not out.get('presence_why'): out['presence_why']=out['why']
        return out
    if _meaningful(value): return {'planning_state':str(value)}
    return {}

def project_named_art_direction(asset:Mapping[str,Any])->dict[str,Any]:
    """Make named `asset_art_direction` the positive single source consumed by legacy compiler fields.

    This is not a positional-shift repair. Values are copied by semantic key only, never by index/order.
    Existing authored structured values win; the projection only fills missing compatibility fields.
    """
    out=normalize_full_art_direction(asset)
    art=out.get('asset_art_direction')
    if not isinstance(art,Mapping): return out
    art=dict(art)

    direct={
      'consumer_question':('consumer_question','shopper_question'),
      'decision_intent':('decision_intent',),
      'purchase_barrier':('purchase_barrier','barrier'),
      'entry_state':('entry_state',),
      'belief_target':('target_belief','belief_target','belief_shift'),
      'exit_state':('exit_state',),
      'race_stage':('race_stage',),
      'strategic_job':('strategic_job','job'),
      'reason_to_exist':('reason_to_exist','why'),
      'incremental_information':('incremental_information','incremental_value','first_scan_answer'),
      'business_hypothesis':('business_hypothesis','hypothesis'),
      'success_metric':('success_metric','metric'),
      'handoff':('handoff',),
      'product_fidelity':('product_fidelity',),
      'precision_boundaries':('precision_boundaries',),
      'approved_visual_elements':('approved_visual_elements',),
      'editable_layer_contract':('editable_layer_contract',),
      'information_assetization':('information_assetization',),
    }
    for target,aliases in direct.items(): _setdefault(out,target,_first(art,*aliases))

    art_presence=_presence(_first(art,'product_presence','presence'))
    if art_presence:
        base=_presence(out.get('product_presence'))
        for k,v in art_presence.items():
            if not _meaningful(base.get(k)): base[k]=deepcopy(v)
        out['product_presence']=base

    brief=dict(out.get('creative_brief') or {})
    brief_map={
      'subject':('subject',), 'action':('action','decisive_moment'), 'environment':('environment','scene_environment'),
      'props':('props','supporting_elements'), 'human':('human_context','people','casting'),
      'composition':('composition','composition_grammar','layout_geometry'),
      'camera_or_view':('camera_or_view','perspective'), 'crop':('crop',), 'product_orientation':('product_orientation',),
      'safe_zone':('safe_zone','copy_zone'), 'typography':('typography',),
      'creative_thesis':('creative_thesis',), 'image_language':('image_language',), 'verbal_thesis':('verbal_thesis',),
    }
    for target,aliases in brief_map.items():
        if not _meaningful(brief.get(target)):
            v=_first(art,*aliases)
            if _meaningful(v): brief[target]=deepcopy(v)
    if brief: out['creative_brief']=brief

    sig=dict(out.get('visual_production_signature') or {})
    if not _meaningful(sig.get('visual_job')): sig['visual_job']=_first(art,'visual_carrier','hero_moment','decisive_moment')
    if not _meaningful(sig.get('evidence_plane')): sig['evidence_plane']=_first(art,'evidence_hierarchy','proof_hierarchy')
    if not _meaningful(sig.get('composition_grammar')): sig['composition_grammar']=_first(art,'composition','composition_grammar')
    if not _meaningful(sig.get('camera_or_view')): sig['camera_or_view']=_first(art,'camera_or_view','perspective')
    if sig: out['visual_production_signature']=sig

    surface=dict(out.get('surface_native_contract') or {})
    output=_first(art,'output_surface','output_spec','canvas','format_spec')
    if _meaningful(output) and not _meaningful(surface.get('output_spec')): surface['output_spec']=deepcopy(output)
    safe=_first(art,'safe_zone','copy_zone')
    if _meaningful(safe) and not _meaningful(surface.get('safe_zone')): surface['safe_zone']=deepcopy(safe)
    if surface: out['surface_native_contract']=surface

    # Exact copy stays one canonical object. Copy route is a route enum, never copy prose.
    visible=deepcopy(out.get('visible_copy') or {})
    route=_first(art,'copy_render_route')
    if isinstance(visible,Mapping):
        visible=dict(visible)
        if _meaningful(route) and not _meaningful(visible.get('copy_render_route')): visible['copy_render_route']=route
        out['visible_copy']=visible

    # Structured photography contract from the same named Art Direction.
    cam_pos=dict(art.get('camera_position') or {})
    focus=dict(art.get('focus_dof') or {})
    camera={}
    focal=_first(art,'focal_length_mm','focal_length','lens_focal_length')
    lens=_first(art,'lens_family','lens')
    if _meaningful(focal): camera['focal_length_mm']=deepcopy(focal)
    if _meaningful(lens): camera['lens_family']=deepcopy(lens)
    keymap={
      'working_distance':'working_distance','camera_height':'camera_height','yaw':'yaw_deg','pitch':'pitch_deg','roll':'roll_deg',
      'shot_size':'shot_size','perspective':'projection'
    }
    for src,dst in keymap.items():
        if _meaningful(cam_pos.get(src)): camera[dst]=deepcopy(cam_pos[src])
    if _meaningful(focus.get('focus_plane')): camera['focus_plane']=deepcopy(focus['focus_plane'])
    if _meaningful(focus.get('aperture')): camera['aperture_dof_intent']=deepcopy(focus['aperture'])
    if _meaningful(focus.get('dof')):
        camera['dof']=deepcopy(focus['dof'])
        if not _meaningful(camera.get('aperture_dof_intent')): camera['aperture_dof_intent']=deepcopy(focus['dof'])
    if _meaningful(focus.get('shutter')): camera['shutter_speed']=deepcopy(focus['shutter'])
    if _meaningful(focus.get('iso')): camera['iso']=deepcopy(focus['iso'])

    lighting=deepcopy(art.get('lighting') or {}) if isinstance(art.get('lighting'),Mapping) else {}
    # downstream has historical names; keep the physical selection and aliases together losslessly.
    if _meaningful(lighting.get('light_ratio')) and not _meaningful(lighting.get('exposure_ratio_plan')):
        lighting['exposure_ratio_plan']=deepcopy(lighting['light_ratio'])
    if _meaningful(lighting.get('prelight')) and not _meaningful(lighting.get('prelight_plan')):
        lighting['prelight_plan']=deepcopy(lighting['prelight'])
    if _meaningful(lighting.get('polarization')) and not _meaningful(lighting.get('polarization_plan')):
        lighting['polarization_plan']=deepcopy(lighting['polarization'])
    if _meaningful(lighting.get('shadow_policy')) and not _meaningful(lighting.get('shadow')):
        lighting['shadow']=deepcopy(lighting['shadow_policy'])

    composition={
      'layout_geometry':_first(art,'layout_geometry','composition','composition_grammar'),
      'scale_depth':_first(art,'scale_depth'), 'product_occupancy':_first(art,'product_occupancy'),
      'focal_path':_first(art,'focal_path'), 'negative_space':_first(art,'negative_space'),
      'crop':_first(art,'crop'), 'safe_zone':_first(art,'safe_zone','copy_zone'),
    }
    composition={k:deepcopy(v) for k,v in composition.items() if _meaningful(v)}
    cmf=deepcopy(art.get('cmf') or {}) if isinstance(art.get('cmf'),Mapping) else ({'description':deepcopy(art.get('cmf'))} if _meaningful(art.get('cmf')) else {})
    inclusive=deepcopy(_first(art,'inclusive_photography','human_context') or {})
    photo={
      'status':'CANONICAL_ART_DIRECTION_PROJECTION',
      'capture_mode':_first(art,'capture_mode'), 'camera':camera, 'composition':composition,
      'lighting':lighting, 'cmf':cmf, 'color_management':deepcopy(art.get('color_management')),
      'inclusive_photography':inclusive, 'prelight_required':bool(_first(art,'prelight_required') or lighting.get('prelight_plan')),
      'repeatable_capture':bool(_first(art,'repeatable_capture')),
    }
    photo={k:v for k,v in photo.items() if _meaningful(v) or k in {'prelight_required','repeatable_capture'}}
    out['canonical_photography_contract']=photo
    return out


def canonical_photography_contract(asset:Mapping[str,Any])->dict[str,Any]:
    value=asset.get('canonical_photography_contract')
    return deepcopy(dict(value)) if isinstance(value,Mapping) else {}
