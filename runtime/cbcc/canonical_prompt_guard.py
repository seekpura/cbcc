from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping

from .canonical_materialization_integrity import (
    audit_asset_semantics,
    audit_prompt_lineage,
    canonical_art_direction_hash,
    stamp_prompt_lineage,
)
from .canonical_art_direction_projection import project_named_art_direction, canonical_photography_contract


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
    projected=project_named_art_direction(asset)
    issues=audit_asset_semantics(_flat_compatibility_card(projected))
    if issues:
        raise CanonicalMaterializationError(issues)
    # The bootstrap historically ignores this function's return value. Mutate the working dict so
    # the positive named projection is still the exact object consumed by the captured compiler.
    if isinstance(asset,dict):
        asset.clear(); asset.update(deepcopy(projected)); return asset
    return projected


def finalize_prompt_lineage(asset:Mapping[str,Any], bundle:Mapping[str,Any])->dict[str,Any]:
    out=stamp_prompt_lineage(asset,bundle)
    h=canonical_art_direction_hash(asset)
    lineage=out.setdefault('canonical_prompt_lineage',{})
    lineage['prompt_cn_source_sha256']=h
    lineage['prompt_en_source_sha256']=h
    lineage['design_card_source_sha256']=h
    lineage['projection_rule']='CN_PROMPT_EN_PROMPT_DESIGN_CARD_FROM_ONE_NAMED_ART_DIRECTION'
    card=out.setdefault('design_card',{})
    card['canonical_prompt_lineage']=deepcopy(lineage)
    contract=out.setdefault('prompt_contract',{})
    contract['canonical_prompt_lineage']=deepcopy(lineage)
    issues=audit_prompt_lineage(asset,out)
    if issues:
        raise CanonicalMaterializationError(issues)
    return out


# Positive wrapper installed at import time. commercial_continuity_bootstrap imports this module
# before capturing `existing_prompt_compile`, so the captured compiler already consumes the same
# named Art Direction and its derived photography contract for both CN and EN Prompt projections.
def _install_positive_prompt_projection()->None:
    from . import prompt_compiler as pc
    current=pc.compile_asset_prompt
    if getattr(current,'_cbcc_v0670_positive_named_art_projection',False):return
    def projected_compile(*args,**kwargs):
        if args:
            call_args=list(args)
            projected=project_named_art_direction(call_args[0] or {})
            call_args[0]=projected
            photo=canonical_photography_contract(projected)
            # signature: asset, product, target, culture, language_contract, locale_profiles=None, photography=None, ...
            if photo:
                if len(call_args)>=7:
                    if call_args[6] in (None,'',{},[]):call_args[6]=photo
                elif len(call_args)==6:
                    call_args.append(photo)
                elif len(call_args)==5:
                    call_args.extend([None,photo])
                else:
                    kwargs=dict(kwargs);kwargs.setdefault('photography',photo)
            return current(*call_args,**kwargs)
        call_kwargs=dict(kwargs)
        if 'asset' in call_kwargs:
            projected=project_named_art_direction(call_kwargs.get('asset') or {})
            call_kwargs['asset']=projected
            photo=canonical_photography_contract(projected)
            if photo and call_kwargs.get('photography') in (None,'',{},[]):call_kwargs['photography']=photo
        return current(**call_kwargs)
    setattr(projected_compile,'_cbcc_v0670_positive_named_art_projection',True)
    pc.compile_asset_prompt=projected_compile

_install_positive_prompt_projection()
