from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


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
        out=compile_fn(asset,product,target,culture,language_contract,locale_profiles,photography,strategy_authority,source_product_assets)
        card=deepcopy(dict(out.get('design_card') or {}))
        art=asset.get('asset_art_direction') or {}
        if isinstance(art, Mapping):
            card['agent_art_direction']=deepcopy(dict(art))
            if art.get('visual_carrier'):
                card['visual_carrier']=art.get('visual_carrier')
        card['production_mode']=asset.get('production_mode')
        card['asset_type']=asset.get('asset_type')
        card['surface']=asset.get('surface')
        out['design_card']=card
        return out
    return compiled
