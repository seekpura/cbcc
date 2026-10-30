from __future__ import annotations
from typing import Any, Mapping

from .canonical_materialization_integrity import (
    audit_asset_semantics,
    audit_prompt_lineage,
    stamp_prompt_lineage,
)


class CanonicalMaterializationError(ValueError):
    def __init__(self, issues):
        self.issues=list(issues or [])
        super().__init__('Canonical asset materialization is semantically invalid: '+str(self.issues))


def _flat_compatibility_card(asset:Mapping[str,Any])->dict[str,Any]:
    """Project named compatibility fields into the semantic guard without guessing positional shifts."""
    art=asset.get('asset_art_direction') if isinstance(asset.get('asset_art_direction'),Mapping) else {}
    card={}
    aliases={
      'visual_carrier':('visual_carrier',),
      'product_presence':('product_presence',),
      'evidence_hierarchy':('evidence_hierarchy','evidence_plane'),
      'copy_render_route':('copy_render_route',),
      'camera_optics':('camera_optics','camera','camera_position','focus_dof'),
      'lighting':('lighting','lighting_program'),
      'cmf_material_color':('cmf_material_color','cmf','material_program'),
      'output_surface':('output_surface','output_spec','canvas','format_spec'),
      'business_hypothesis':('business_hypothesis','test_hypothesis'),
      'success_metric':('success_metric','metric'),
      'portfolio_rhythm_delta':('portfolio_rhythm_delta','rhythm_delta'),
    }
    for target,keys in aliases.items():
        value=None
        for key in keys:
            if key in art and art.get(key) not in (None,'',[],{}):value=art.get(key);break
            if key in asset and asset.get(key) not in (None,'',[],{}):value=asset.get(key);break
        if value not in (None,'',[],{}):card[target]=value
    return card


def validate_canonical_asset_or_raise(asset:Mapping[str,Any])->dict[str,Any]:
    issues=audit_asset_semantics(_flat_compatibility_card(asset))
    if issues:
        raise CanonicalMaterializationError(issues)
    return dict(asset)


def finalize_prompt_lineage(asset:Mapping[str,Any], bundle:Mapping[str,Any])->dict[str,Any]:
    out=stamp_prompt_lineage(asset,bundle)
    issues=audit_prompt_lineage(asset,out)
    if issues:
        raise CanonicalMaterializationError(issues)
    return out
