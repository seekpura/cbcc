from __future__ import annotations

from typing import Any, Mapping


VISUAL_PRODUCTION_SURFACES = frozenset({
    'SEARCH_RESULTS', 'LISTING_PRIMARY', 'PDP_HERO', 'GALLERY', 'PDP', 'LONGFORM', 'A_PLUS',
    'PDP_VIDEO', 'SHORT_VIDEO', 'CREATOR', 'LIVE', 'PAID_AD', 'SOCIAL_CONTENT', 'STORE_BANNER',
    'LANDING_PAGE_HERO', 'COMPARISON', 'SPECIFICATION', 'UGC_BRIEF',
})

VISUAL_PRODUCTION_ASSET_TYPES = frozenset({
    'IMAGE', 'VIDEO', 'MOTION', 'ANIMATION', 'UGC', 'CREATOR', 'LIVE', 'PAGE', 'LANDING_PAGE',
    'BANNER', 'CAROUSEL', 'INTERACTIVE', 'HTML', 'PDP_VIDEO', 'SHORT_VIDEO',
})


def _token(value: Any) -> str:
    return str(value or '').strip().upper().replace('-', '_').replace(' ', '_')


def is_visual_production_asset(asset: Mapping[str, Any] | None) -> bool:
    """Return whether an architecture object participates in visual Art Direction.

    Visual authority follows the active delivery route, not only the historical IMAGE/VIDEO
    asset-type pair. A UGC brief, LIVE object or landing-page object can therefore require
    Art Direction even when its serializer uses a non-image asset_type.
    """
    row = asset if isinstance(asset, Mapping) else {}
    if row.get('visual_route_active') is False:
        return False
    asset_type = _token(row.get('asset_type'))
    surface = _token(row.get('surface'))
    return asset_type in VISUAL_PRODUCTION_ASSET_TYPES or surface in VISUAL_PRODUCTION_SURFACES
