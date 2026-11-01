from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping
import re

_FULL_DENY = {'TASK_SCOPED','TASK_SCOPE','PARTIAL','NOT_FULL','NON_FULL','SCOPED','MINIMAL'}
_FULL_EXACT = {'FULL','FULL_PROJECT','FULL_DELIVERY','FULL_PACKAGE','FULL_COMMERCE','FULL_STRATEGY','FULL_WORKSPACE','FULL_E2E','END_TO_END','COMPLETE_DELIVERY','COMPLETE_PROJECT','完整交付','全量交付','完整项目','全量项目'}


def _d(value: Any) -> dict[str, Any]:
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}


def _mode_token(value: Any) -> str:
    raw = str(value or '').strip()
    if not raw:
        return ''
    if re.search(r'[\u3400-\u9fff]', raw):
        return re.sub(r'\s+', '', raw)
    return re.sub(r'[^A-Z0-9]+', '_', raw.upper()).strip('_')


def _is_full(strategy: Mapping[str, Any]) -> bool:
    try:
        from .v0674_regression_closure import is_full_strategy
        return bool(is_full_strategy(strategy))
    except (ImportError, ValueError):
        hp = _d(strategy.get('human_projection'))
        if hp.get('fixed_human_section_quota') is True:
            return True
        token = _mode_token(hp.get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '')
        if token in _FULL_DENY or token.startswith('NOT_FULL') or token.startswith('NON_FULL'):
            return False
        if token in _FULL_EXACT:
            return True
        if token.startswith('FULL_') and any(x in token for x in ('PROJECT','DELIVERY','PACKAGE','COMMERCE','WORKSPACE','STRATEGY','E2E')):
            return True
        return token in {'完整','全量'}


def _phase2_from_economics(economics: Any) -> dict[str, Any]:
    econ = _d(economics)
    strict = _d(econ.get('pricing_economics_authority'))
    phase2 = _d(strict.get('phase2_economics_offer_authority'))
    if phase2:
        return phase2
    # Allow a caller that already supplies the strict authority itself, without re-authoring it.
    phase2 = _d(econ.get('phase2_economics_offer_authority'))
    if phase2:
        return phase2
    if str(econ.get('schema') or '') == 'cbcc-economics-offer-authority-v0.6.76':
        return econ
    return {}


def _missing_projection() -> dict[str, Any]:
    return {
        'schema': 'cbcc-economics-offer-authority-v0.6.76',
        'status': 'TO_VERIFY',
        'source_status': 'MISSING_PHASE2_ECONOMICS_OFFER_AUTHORITY',
        'missing_inputs': [],
        'scenario_math': {'status': 'INCOMPLETE'},
        'pricing_decision': {
            'density_status': 'TO_VERIFY',
            'density_gaps': ['what','why','evidence','tradeoff','execution','measurement','decision'],
            'decision': None,
        },
        'offer_decision': {
            'density_status': 'TO_VERIFY',
            'density_gaps': ['what','why','evidence','tradeoff','execution','measurement','decision','status'],
            'decision': None,
        },
        'principle': 'FULL Strategy must consume the already-materialized Phase 2 Pricing/Economics/Offer authority. Missing authority stays TO_VERIFY; this bridge never calculates or invents a price, fee, CVR, offer or market conclusion.',
    }


def project_economics_offer_into_strategy(strategy: Mapping[str, Any], economics: Any = None) -> dict[str, Any]:
    out = deepcopy(dict(strategy))
    if not _is_full(out):
        return out
    phase2 = _phase2_from_economics(economics)
    out['economics_offer_authority_v0676'] = deepcopy(phase2) if phase2 else _missing_projection()
    out['economics_offer_projection_v0676'] = {
        'status': 'BOUND_SAME_SOURCE' if phase2 else 'TO_VERIFY',
        'authority_ref': 'economics.pricing_economics_authority.phase2_economics_offer_authority',
        'rule': 'Projection only: Strategy does not re-author economics math, pricing decisions or offer decisions.',
    }
    return out


def strategy_economics_offer_issues(strategy: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not _is_full(strategy):
        return []
    auth = _d(strategy.get('economics_offer_authority_v0676'))
    if not auth:
        return [{'code': 'FULL_ECONOMICS_OFFER_AUTHORITY_MISSING_V0676'}]
    if auth.get('source_status') == 'MISSING_PHASE2_ECONOMICS_OFFER_AUTHORITY':
        return [{'code': 'FULL_ECONOMICS_OFFER_AUTHORITY_MISSING_V0676'}]
    pricing = _d(auth.get('pricing_decision'))
    offer = _d(auth.get('offer_decision'))
    scenario_math = _d(auth.get('scenario_math'))
    ready = (
        str(auth.get('status') or '').upper() == 'READY'
        and str(scenario_math.get('status') or '').upper() == 'CALCULATED'
        and pricing.get('density_status') == 'READY'
        and offer.get('density_status') == 'READY'
    )
    if ready:
        return []
    return [{
        'code': 'FULL_ECONOMICS_OFFER_BUSINESS_READINESS_INCOMPLETE_V0676',
        'missing_inputs': list(auth.get('missing_inputs') or []),
        'scenario_math_status': scenario_math.get('status'),
        'pricing_density_gaps': list(pricing.get('density_gaps') or []),
        'offer_density_gaps': list(offer.get('density_gaps') or []),
        'authority_status': auth.get('status'),
    }]


def wrap_build_master_strategy(fn: Callable[..., dict[str, Any]]):
    def built(request: dict[str, Any], *args: Any, **kwargs: Any):
        strategy = fn(request, *args, **kwargs)
        economics = kwargs.get('economics')
        return project_economics_offer_into_strategy(strategy, economics)
    setattr(built, '_cbcc_v0676_economics_offer_strategy_bridge', True)
    return built


def wrap_validate_strategy_delivery(fn: Callable[[dict[str, Any]], dict[str, Any]]):
    def validated(strategy: dict[str, Any]):
        result = fn(strategy)
        if not _is_full(strategy):
            return result
        current = strategy_economics_offer_issues(strategy)
        issues = list(result.get('issues') or []) + current
        dedup: list[dict[str, Any]] = []
        for item in issues:
            if item not in dedup:
                dedup.append(item)
        result['issues'] = dedup
        if current:
            result['status'] = 'INCOMPLETE'
        result['economics_offer_strategy_bridge_v0676_audit'] = {
            'status': 'PASS' if not current else 'INCOMPLETE',
            'issues': current,
        }
        return result
    setattr(validated, '_cbcc_v0676_economics_offer_strategy_bridge', True)
    return validated
