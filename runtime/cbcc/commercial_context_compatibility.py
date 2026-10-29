from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _has_pricing_payload(value: dict[str, Any]) -> bool:
    return any(v not in (None, '', [], {}) for v in value.values())


def wrap_compile_commerce_decision_context(fn: Callable[..., dict[str, Any]]):
    """Normalize mature pricing-authority names without replacing payload or provenance.

    Historical Pricing Authority uses market_price_bands / market_price_valleys /
    offer_bundle_discount_boundary. Commerce Decision Context exposes canonical aliases while preserving
    original values and source lineage, so a naming migration cannot silently erase pricing evidence.
    """
    def compiled(*args, **kwargs):
        out = fn(*args, **kwargs)
        domain = kwargs.get('domain') if 'domain' in kwargs else None
        domain = _dict(domain)
        economics = _dict(domain.get('economics'))
        pricing_source = _dict(domain.get('pricing_economics_authority')) or _dict(economics.get('pricing_economics_authority'))
        pricing = dict(out.get('pricing_economics') or {})

        aliases = {
            'price_bands': pricing_source.get('market_price_bands') or pricing_source.get('price_bands'),
            'price_valleys': pricing_source.get('market_price_valleys') or pricing_source.get('price_valleys'),
            'price_configuration_matrix': pricing_source.get('price_configuration_matrix'),
            'offer_boundaries': pricing_source.get('offer_bundle_discount_boundary') or pricing_source.get('offer_boundaries') or pricing_source.get('offer_boundary'),
            'pricing_decision': pricing_source.get('pricing_decision'),
            'scenarios': pricing_source.get('scenarios'),
            'sku_roles': pricing_source.get('sku_roles'),
            'downstream_consumers': pricing_source.get('downstream_consumers'),
            'missing_inputs': pricing_source.get('missing_inputs'),
        }
        for key, value in aliases.items():
            if value not in (None, '', [], {}):
                pricing[key] = deepcopy(value)
        for original in ('market_price_bands', 'market_price_valleys', 'offer_bundle_discount_boundary'):
            if pricing_source.get(original) not in (None, '', [], {}):
                pricing[original] = deepcopy(pricing_source.get(original))
        if pricing_source.get('currency') not in (None, ''):
            pricing['currency'] = pricing_source.get('currency')
        if pricing_source.get('status') not in (None, ''):
            pricing['status'] = pricing_source.get('status')
        out['pricing_economics'] = pricing

        # If the base compiler could not recognize the mature field aliases, it may also have omitted
        # the PRICING_ECONOMICS lineage row. Restoring values without restoring provenance would still
        # be a continuity failure, so keep the source edge synchronized with the canonical payload.
        lineage = [x for x in (out.get('lineage_index') or []) if isinstance(x, dict)]
        if _has_pricing_payload(pricing) and not any(x.get('domain') == 'PRICING_ECONOMICS' for x in lineage):
            lineage.append({
                'domain': 'PRICING_ECONOMICS',
                'source_artifact': 'artifacts/pricing_economics_authority.json',
                'source_path': '$',
                'payload_present': True,
            })
        out['lineage_index'] = lineage

        market = dict(out.get('market') or {})
        if market.get('price_valley_signals') and not market.get('price_valleys'):
            market['price_valleys'] = deepcopy(market.get('price_valley_signals'))
        out['market'] = market
        return out
    return compiled
