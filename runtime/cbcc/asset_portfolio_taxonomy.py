from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable


def _u(v: Any) -> str:
    return str(v or '').strip().upper()


def classify_asset_family(asset: dict[str, Any]) -> str:
    explicit = _u(asset.get('asset_family') or asset.get('portfolio_family'))
    if explicit:
        return explicit
    cluster = _u(asset.get('variant_cluster') or asset.get('asset_cluster') or asset.get('asset_role'))
    surface = _u(asset.get('surface'))
    family = _u(asset.get('family'))
    intent = _u(asset.get('decision_intent'))
    if cluster.startswith('HERO') or surface in {'LANDING_PAGE_HERO', 'PDP_HERO'}:
        return 'HERO'
    if surface == 'A_PLUS':
        return 'A_PLUS'
    if surface in {'PDP', 'LONGFORM', 'COMPARISON', 'SPECIFICATION', 'FAQ'} or family == 'RICH_CONTENT':
        return 'PDP'
    if surface == 'PAID_AD' or family == 'PAID':
        return 'AD'
    if surface in {'SOCIAL_CONTENT'} or family == 'SOCIAL':
        return 'SOCIAL_SEEDING'
    if surface in {'CREATOR', 'UGC_BRIEF'} or family == 'CREATOR_AFFILIATE':
        return 'CREATOR_UGC'
    if surface in {'SHORT_VIDEO', 'PDP_VIDEO', 'LIVE'} or _u(asset.get('asset_type')) == 'VIDEO':
        return 'VIDEO'
    if surface == 'STORE_BANNER' or family == 'STORE':
        return 'BANNER'
    if intent in {'PROOF', 'PERFORMANCE_PROOF', 'INGREDIENT_COMPOSITION', 'MATERIAL_SENSORY'}:
        return 'PROOF'
    if intent in {'USAGE', 'CARE_MAINTENANCE'}:
        return 'HOW_TO'
    if intent in {'RELEVANCE', 'PORTABILITY', 'FIT_WEAR'}:
        return 'SCENARIO'
    if intent in {'TRUST', 'PACKAGE_CONTENTS', 'WARRANTY_SERVICE', 'EXPECTATION_BOUNDARY'}:
        return 'TRUST'
    if intent in {'DIFFERENTIATION', 'BENEFIT', 'DECISION_SUPPORT'}:
        return 'BENEFIT'
    return 'OTHER'


def deployment_state(asset: dict[str, Any]) -> str:
    explicit = _u(asset.get('deployment_state') or asset.get('activation_state') or asset.get('pool_state'))
    if explicit:
        return explicit
    surface = _u(asset.get('surface'))
    if surface == 'PAID_AD':
        return 'PAID_MEDIA'
    if surface == 'A_PLUS':
        return 'APLUS_CONTENT'
    if surface in {'PDP', 'LONGFORM', 'COMPARISON', 'SPECIFICATION', 'FAQ'}:
        return 'PDP_CONTENT'
    if surface in {'SOCIAL_CONTENT', 'CREATOR', 'UGC_BRIEF'}:
        return 'SOCIAL_CONTENT'
    if asset.get('testing_variant'):
        return 'TEST_POOL'
    return 'LIVE_CANDIDATE'


def enrich_asset_portfolio_taxonomy(assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for raw in assets or []:
        a = deepcopy(raw)
        a['asset_family'] = classify_asset_family(a)
        a['deployment_state'] = deployment_state(a)
        a.setdefault('surface_role', a.get('surface') or a.get('family'))
        a.setdefault('activation_eligible', a['deployment_state'] == 'LIVE_CANDIDATE')
        a.setdefault('portfolio_rule', 'Asset family and deployment state describe business use; they do not impose a fixed asset count or fixed sequence.')
        out.append(a)
    return out


def portfolio_taxonomy_summary(assets: list[dict[str, Any]], target: dict[str, Any] | None = None) -> dict[str, Any]:
    target = target or {}
    rows = enrich_asset_portfolio_taxonomy(assets)
    fams: dict[str, int] = {}
    states: dict[str, int] = {}
    for a in rows:
        fams[a['asset_family']] = fams.get(a['asset_family'], 0) + 1
        states[a['deployment_state']] = states.get(a['deployment_state'], 0) + 1
    capacity = target.get('listing_image_capacity') or target.get('gallery_capacity') or target.get('platform_slot_capacity')
    return {
        'status': 'COMMERCIAL_ASSET_PORTFOLIO_TAXONOMY',
        'fixed_total_asset_limit': False,
        'platform_capacity_is_activation_constraint_only': True,
        'activation_capacity': capacity,
        'activation_capacity_does_not_prune_universe': True,
        'total_asset_candidates': len(rows),
        'asset_family_counts': fams,
        'deployment_state_counts': states,
        'supported_asset_families': [
            'HERO', 'BENEFIT', 'PROOF', 'SCENARIO', 'HOW_TO', 'TRUST',
            'PDP', 'A_PLUS', 'AD', 'SOCIAL_SEEDING', 'CREATOR_UGC', 'VIDEO', 'BANNER', 'OTHER'
        ],
        'supported_deployment_states': [
            'LIVE_CANDIDATE', 'TEST_POOL', 'ROTATION_POOL', 'PAID_MEDIA',
            'PDP_CONTENT', 'APLUS_CONTENT', 'SOCIAL_CONTENT', 'ARCHIVE', 'OTHER'
        ],
        'principle': 'Gallery/media capacity controls only the simultaneous activation set. It never caps Hero variants, benefit/proof/scenario assets, PDP/A+, paid ads, social/seeding, creator/UGC, video, banner, test or rotation inventory.',
    }


def wrap_build_asset_architecture(fn: Callable[..., dict[str, Any]]):
    def built(*args, **kwargs):
        out = fn(*args, **kwargs)
        target = kwargs.get('target') if 'target' in kwargs else (args[1] if len(args) > 1 else {})
        out = deepcopy(out)
        out['assets'] = enrich_asset_portfolio_taxonomy(out.get('assets') or [])
        out['commercial_asset_portfolio'] = portfolio_taxonomy_summary(out['assets'], target or {})
        if isinstance(out.get('asset_universe'), dict):
            out['asset_universe']['commercial_asset_portfolio'] = deepcopy(out['commercial_asset_portfolio'])
            out['asset_universe']['fixed_total_asset_limit'] = False
            out['asset_universe']['platform_capacity_is_activation_constraint_only'] = True
        return out
    return built
