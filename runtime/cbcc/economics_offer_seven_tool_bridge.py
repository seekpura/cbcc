from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping


def _d(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _l(value: Any) -> list[Any]:
    if value in (None, '', {}):
        return []
    return list(value) if isinstance(value, (list, tuple, set, frozenset)) else [value]


def wrap_compile_seven_tool_continuity(fn: Callable[..., dict[str, Any]]):
    def compiled(*args: Any, **kwargs: Any):
        result = fn(*args, **kwargs)
        domain = _d(kwargs.get('domain'))
        pricing = _d(kwargs.get('pricing_economics') or domain.get('pricing_economics_authority'))
        phase2 = _d(pricing.get('phase2_economics_offer_authority'))
        if not phase2:
            return result

        business_status = pricing.get('phase2_business_status') or phase2.get('status')
        calculation_status = pricing.get('status')
        integrity = _d(result.get('pricing_economics_integrity'))
        integrity['calculation_status'] = calculation_status
        integrity['business_readiness_status'] = business_status
        integrity['status'] = business_status
        integrity['missing_inputs'] = deepcopy(phase2.get('missing_inputs') or [])
        integrity['pricing_decision_status'] = _d(phase2.get('pricing_decision')).get('density_status')
        integrity['offer_decision_status'] = _d(phase2.get('offer_decision')).get('density_status')
        result['pricing_economics_integrity'] = integrity

        for row in _l(result.get('capabilities')):
            if isinstance(row, dict) and row.get('id') == '02_PRODUCT_STRATEGY':
                evidence = row.setdefault('evidence', {})
                evidence['calculation_status'] = calculation_status
                evidence['pricing_status'] = business_status
                evidence['pricing_decision_status'] = _d(phase2.get('pricing_decision')).get('density_status')
                evidence['offer_decision_status'] = _d(phase2.get('offer_decision')).get('density_status')
                evidence['missing_inputs'] = deepcopy(phase2.get('missing_inputs') or [])
        return result

    setattr(compiled, '_cbcc_v0676_economics_offer_authority', True)
    return compiled
