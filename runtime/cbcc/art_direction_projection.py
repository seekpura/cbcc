from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def _value(art: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value=art.get(key)
        if value not in (None, '', [], {}):
            return deepcopy(value)
    return None


def project_art_direction_into_asset(asset: Mapping[str, Any]) -> dict[str, Any]:
    """Project Agent-authored Art Direction into the execution-shaped asset contract.

    This function does not invent creative decisions. It only copies already-authored values into the
    compatibility fields consumed by the historical Design Card builder and renderer compiler.
    """
    out=deepcopy(dict(asset))
    art=out.get('asset_art_direction')
    if not isinstance(art, Mapping):
        return out
    art=dict(art)
    out['art_direction_required']=True
    out['art_direction_status']='AUTHORED'

    presence=art.get('product_presence')
    if isinstance(presence, Mapping):
        out['product_presence']=deepcopy(dict(presence))
    elif art.get('product_presence_state'):
        out['product_presence']={
            'planning_state':str(art.get('product_presence_state')).upper(),
            'product_role':art.get('product_role'),
            'presence_why':art.get('presence_why'),
            'scale_relationship':art.get('scale_relationship'),
            'identity_requirement':art.get('identity_requirement'),
            'source_reference_role':art.get('source_reference_role'),
        }

    if isinstance(art.get('information_assetization'), Mapping):
        out['information_assetization']=deepcopy(dict(art.get('information_assetization') or {}))
    elif art.get('visual_carrier'):
        out['information_assetization']={
            'representation':art.get('visual_carrier'),
            'authority':'HOST_AGENT_ART_DIRECTION',
            'reason':art.get('visual_carrier_why') or art.get('why'),
        }

    brief=dict(out.get('creative_brief') or {})
    mappings={
        'subject':_value(art,'subject'),
        'action':_value(art,'action','decisive_action','decisive_moment'),
        'environment':_value(art,'environment'),
        'props':_value(art,'props','scene_props'),
        'human':_value(art,'human_context','people','casting'),
        'composition':_value(art,'composition_grammar','composition','spatial_grammar'),
        'camera_or_view':_value(art,'camera_or_view','preferred_view','view'),
        'lighting':_value(art,'lighting'),
        'color':_value(art,'cmf','color','color_world'),
        'typography':_value(art,'typography'),
        'scene_props':_value(art,'scene_props','props'),
        'image_language':_value(art,'image_language','visual_language'),
        'proof_mechanism':_value(art,'proof_mechanism','evidence_hierarchy','evidence_plane'),
        'verbal_thesis':_value(art,'verbal_thesis'),
        'negative_space':_value(art,'negative_space','copy_negative_space'),
        'focal_path':_value(art,'focal_path'),
        'decisive_moment':_value(art,'decisive_moment'),
    }
    for key,value in mappings.items():
        if value not in (None,'',[],{}):
            brief[key]=value
    out['creative_brief']=brief

    sig=dict(out.get('visual_production_signature') or {})
    sig_mappings={
        'visual_job':_value(art,'visual_job','decisive_moment','objective'),
        'composition_grammar':mappings.get('composition'),
        'camera_or_view':mappings.get('camera_or_view'),
        'context_role':_value(art,'context_role','environment_role'),
        'evidence_plane':_value(art,'evidence_plane','evidence_hierarchy'),
        'differentiation_axis':_value(art,'differentiation_axis','deliberate_difference'),
        'spatial_rhythm':_value(art,'spatial_rhythm','space_rhythm'),
        'focal_path':mappings.get('focal_path'),
        'negative_space':mappings.get('negative_space'),
    }
    for key,value in sig_mappings.items():
        if value not in (None,'',[],{}):
            sig[key]=value
    sig['authority']='HOST_AGENT_ART_DIRECTION'
    out['visual_production_signature']=sig
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
        projected=project_art_direction_into_asset(asset)
        return compile_fn(
            projected,
            product,
            target,
            culture,
            language_contract,
            locale_profiles,
            photography,
            strategy_authority,
            source_product_assets,
        )
    return compiled
