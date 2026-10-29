from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable


def _rows(value: Any) -> list[dict[str, Any]]:
    return [x for x in (value or []) if isinstance(x, dict)]


def _decision_basis(assets: list[dict[str, Any]], culture: dict[str, Any] | None, target: dict[str, Any] | None) -> dict[str, Any]:
    origins = []
    signals = []
    jobs = []
    for asset in assets or []:
        origin = asset.get('decision_origin')
        if origin and origin not in origins:
            origins.append(origin)
        source = asset.get('decision_source')
        if source not in (None, '', [], {}):
            signals.append({
                'asset_id': asset.get('asset_id'),
                'decision_origin': origin,
                'decision_source': deepcopy(source),
            })
        jobs.append({
            'asset_id': asset.get('asset_id'),
            'consumer_question': asset.get('consumer_question'),
            'decision_intent': asset.get('decision_intent'),
            'purchase_barrier': asset.get('purchase_barrier'),
            'business_hypothesis': asset.get('business_hypothesis'),
            'surface': asset.get('surface'),
            'asset_family': asset.get('asset_family'),
        })
    culture = culture or {}
    target = target or {}
    return {
        'status': 'CURATION_COMMERCIAL_DECISION_BASIS',
        'decision_origins': origins,
        'decision_signals': signals,
        'asset_jobs': jobs,
        'target_context': {k: target.get(k) for k in ('market', 'platform_family', 'site', 'category') if target.get(k) not in (None, '')},
        'culture_context': {
            k: deepcopy(culture.get(k)) for k in ('race_ethnicity', 'intersectionality', 'visual_implications', 'taboo_stereotype_risks', 'taboos')
            if culture.get(k) not in (None, '', [], {})
        },
        'principle': 'Creative curation must explain which shopper/market/listing/review/culture decision signal it serves; style alone is not a sufficient origin.',
    }


def wrap_compile_creative_opportunity_universe(fn: Callable[..., dict[str, Any]]):
    def compiled(*args, **kwargs):
        out = fn(*args, **kwargs)
        assets = kwargs.get('assets') if 'assets' in kwargs else (args[3] if len(args) > 3 else [])
        culture = kwargs.get('culture') if 'culture' in kwargs else (args[5] if len(args) > 5 else {})
        target = kwargs.get('target') if 'target' in kwargs else (args[6] if len(args) > 6 else {})
        basis = _decision_basis(assets or [], culture or {}, target or {})
        out['commercial_decision_basis'] = basis
        for row in _rows(out.get('opportunities')):
            row.setdefault('commercial_decision_basis', {
                'decision_origins': deepcopy(basis.get('decision_origins') or []),
                'target_context': deepcopy(basis.get('target_context') or {}),
                'principle': basis.get('principle'),
            })
        return out
    return compiled


def wrap_compile_creative_council(fn: Callable[..., dict[str, Any]]):
    def compiled(*args, **kwargs):
        out = fn(*args, **kwargs)
        universe = kwargs.get('opportunity_universe') if 'opportunity_universe' in kwargs else None
        if universe is None and args:
            # Current signature carries opportunity_universe near the end; scan for its status rather than relying on one positional shape.
            for value in args:
                if isinstance(value, dict) and str(value.get('status') or '').startswith(('CREATIVE_OPPORTUNITY', 'AGENT_AUTHORED_CREATIVE_OPPORTUNITY')):
                    universe = value
                    break
        basis = (universe or {}).get('commercial_decision_basis') if isinstance(universe, dict) else None
        if basis:
            out['commercial_decision_basis'] = deepcopy(basis)
            if isinstance(out.get('selected_direction'), dict):
                out['selected_direction'].setdefault('commercial_decision_basis', deepcopy(basis))
            for row in _rows(out.get('alternative_directions')):
                row.setdefault('commercial_decision_basis', deepcopy(basis))
        return out
    return compiled


def wrap_apply_creative_system_to_assets(fn: Callable[..., dict[str, Any]]):
    def compiled(architecture, council, *args, **kwargs):
        out = fn(architecture, council, *args, **kwargs)
        basis = (council or {}).get('commercial_decision_basis') or ((council or {}).get('selected_direction') or {}).get('commercial_decision_basis')
        if not basis:
            return out
        for asset in out.get('assets') or []:
            if not isinstance(asset, dict):
                continue
            asset['curation_commercial_decision_basis'] = deepcopy(basis)
            art = asset.get('asset_art_direction')
            if isinstance(art, dict):
                art.setdefault('commercial_decision_basis', deepcopy(basis))
                art.setdefault('commercial_curation_status', 'CURATION_BOUND_TO_UPSTREAM_DECISION_SIGNALS')
        out['commercial_curation_continuity'] = {
            'status': 'BOUND',
            'decision_origins': deepcopy(basis.get('decision_origins') or []),
            'asset_count': len(out.get('assets') or []),
        }
        return out
    return compiled
