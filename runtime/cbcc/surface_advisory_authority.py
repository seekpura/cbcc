from __future__ import annotations

from copy import deepcopy
from typing import Any


def wrap_compile_surface_architecture(legacy_fn):
    """Make Surface planning informative but non-authoritative for creative decisions.

    Historical Surface logic may still suggest that a product is useful on a surface. That suggestion
    is preserved for compatibility and planning diagnostics, but it cannot become the production
    decision when Agent Art Direction is active. Final product presence belongs to per-asset Agent
    Art Direction and is re-resolved by the creative-authority layer before prompt compilation.
    """
    def compiled(
        target: dict[str, Any],
        content_objects: list[dict[str, Any]],
        assets: list[dict[str, Any]],
        platform_compile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        out=deepcopy(legacy_fn(target, content_objects, assets, platform_compile))
        enriched=[]
        for raw in out.get('assets') or []:
            asset=deepcopy(raw)
            presence=dict(asset.get('product_presence') or {})
            if presence:
                suggestion=str(presence.get('planning_state') or '').upper() or None
                presence['planning_suggestion']=suggestion
                presence['authority']='SURFACE_COMPATIBILITY_SUGGESTION_ONLY'
                presence['authoritative_for_generation']=False
                presence['requires_agent_resolution_before_generation']=True
                presence['principle']='Surface may suggest whether product presence could help, but only per-asset Agent Art Direction may decide whether the product is actually visible, absent, supporting, detail-only or hero.'
                asset['product_presence']=presence
                surface=dict(asset.get('surface_native_contract') or {})
                surface['product_presence_suggestion']=suggestion
                surface['product_presence_authority']='AGENT_ART_DIRECTION'
                surface['product_presence']=suggestion  # compatibility display only; not production authority
                asset['surface_native_contract']=surface
            enriched.append(asset)
        out['assets']=enriched

        decision_objects=[]
        for raw in out.get('decision_content_objects') or []:
            row=deepcopy(raw)
            if row.get('product_presence'):
                row['product_presence_suggestion']=row.get('product_presence')
                row['product_presence_authority']='AGENT_ART_DIRECTION'
                row['product_presence_is_production_decision']=False
            decision_objects.append(row)
        out['decision_content_objects']=decision_objects
        out['product_presence_authority']='AGENT_ART_DIRECTION'
        out['surface_product_presence_role']='PLANNING_SUGGESTION_ONLY'
        out['principle']='Information representation and Surface constraints may be planned here. Product visibility is a creative decision owned by per-asset Agent Art Direction; Surface heuristics are advisory compatibility hints only.'
        return out
    return compiled
