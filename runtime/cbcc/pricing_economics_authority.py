from __future__ import annotations

from typing import Any

VERSION = '0.6.36-seven-tool-capability-continuity'

_REQUIRED_COST_ALIASES = {
    'landed_cost': ('landed_cost', 'cogs', 'product_cost', 'unit_cost'),
    'platform_fee': ('platform_fee', 'marketplace_fee'),
    'fulfillment': ('fulfillment', 'logistics_fulfillment', 'fulfillment_cost', 'shipping_fulfillment'),
    'affiliate_commission': ('affiliate_commission', 'creator_commission', 'affiliate_cost'),
    'tax': ('tax', 'merchant_borne_tax', 'duties_tax'),
    'refund_allowance': ('refund_allowance', 'returns_refund_cost', 'return_allowance'),
}
_OPTIONAL_COST_ALIASES = {
    'payment_fee': ('payment_fee',),
    'shipping_subsidy': ('shipping_subsidy',),
    'discount_funding': ('discount_funding', 'promo_funding', 'coupon_discount'),
    'other_variable_cost': ('other_variable_cost',),
    'ad_cost': ('ad_cost', 'ad_cost_per_order'),
}


def _number(value: Any) -> float | None:
    if value in (None, ''):
        return None
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _component_amount(component: Any, revenue_basis: float) -> tuple[float | None, dict[str, Any]]:
    if component is None:
        return None, {'status': 'MISSING_INPUT'}
    if isinstance(component, bool):
        return None, {'status': 'INVALID_INPUT', 'raw': component}
    if isinstance(component, (int, float, str)):
        value = _number(component)
        return value, {'status': 'EXPLICIT_FIXED', 'type': 'fixed', 'value': value, 'raw': component}
    if not isinstance(component, dict):
        return None, {'status': 'INVALID_INPUT', 'raw': component}
    if 'value' not in component or component.get('value') in (None, ''):
        return None, {'status': 'MISSING_VALUE', 'raw': component}
    value = _number(component.get('value'))
    if value is None:
        return None, {'status': 'INVALID_VALUE', 'raw': component}
    typ = str(component.get('type') or 'fixed').lower()
    if typ == 'fixed':
        return value, {'status': 'EXPLICIT_FIXED', 'type': 'fixed', 'value': value, 'source_id': component.get('source_id'), 'basis': component.get('basis')}
    if typ == 'rate':
        basis_value = _number(component.get('base')) if component.get('base') not in (None, '') else revenue_basis
        if basis_value is None:
            return None, {'status': 'MISSING_RATE_BASE', 'raw': component}
        return basis_value * value, {'status': 'EXPLICIT_RATE', 'type': 'rate', 'value': value, 'base': basis_value, 'source_id': component.get('source_id'), 'basis': component.get('basis') or 'revenue_basis'}
    return None, {'status': 'UNSUPPORTED_TYPE', 'type': typ, 'raw': component}


def _first_present(costs: dict[str, Any], aliases: tuple[str, ...]) -> tuple[str | None, Any]:
    for key in aliases:
        if key in costs and costs.get(key) not in (None, ''):
            return key, costs.get(key)
    return None, None


def _strict_scenario(scenario: dict[str, Any], global_defaults: dict[str, Any]) -> dict[str, Any]:
    sid = scenario.get('scenario_id') or scenario.get('sku') or 'SCENARIO'
    price = _number(scenario.get('price'))
    if price is None:
        return {
            'scenario_id': sid,
            'sku': scenario.get('sku'),
            'status': 'MISSING_INPUT',
            'missing_inputs': ['price'],
            'formula_basis': 'No economics are calculated without an explicit selling price.',
        }
    costs = dict(global_defaults.get('costs') or {})
    costs.update(scenario.get('costs') or {})
    required_names = scenario.get('required_cost_components') or global_defaults.get('required_cost_components') or list(_REQUIRED_COST_ALIASES)
    resolved: dict[str, float] = {}
    provenance: dict[str, Any] = {}
    missing: list[str] = []
    invalid: list[str] = []
    alias_map = {**_REQUIRED_COST_ALIASES, **_OPTIONAL_COST_ALIASES}
    for canonical, aliases in alias_map.items():
        source_key, raw = _first_present(costs, aliases)
        if raw is None:
            if canonical in required_names:
                missing.append(canonical)
            continue
        amount, meta = _component_amount(raw, price)
        provenance[canonical] = {'source_key': source_key, **meta}
        if amount is None:
            invalid.append(canonical)
        else:
            resolved[canonical] = amount
    for name in required_names:
        if name not in alias_map and name not in costs:
            missing.append(str(name))
        elif name not in alias_map and name in costs:
            amount, meta = _component_amount(costs.get(name), price)
            provenance[name] = {'source_key': name, **meta}
            if amount is None:
                invalid.append(str(name))
            else:
                resolved[str(name)] = amount
    missing = list(dict.fromkeys(missing))
    invalid = list(dict.fromkeys(invalid))
    if missing or invalid:
        return {
            'scenario_id': sid,
            'sku': scenario.get('sku'),
            'configuration': scenario.get('configuration'),
            'price': price,
            'status': 'MISSING_INPUT',
            'missing_inputs': missing,
            'invalid_inputs': invalid,
            'resolved_components': resolved,
            'component_provenance': provenance,
            'formula_basis': 'Missing cost components are never defaulted to zero. Explicit zero is valid; absent is unresolved.',
        }
    ad_cost = resolved.get('ad_cost')
    pre_ad_components = {k: v for k, v in resolved.items() if k != 'ad_cost'}
    pre_ad_cost = sum(pre_ad_components.values())
    contribution_before_ads = price - pre_ad_cost
    contribution_after_current_ads = contribution_before_ads - ad_cost if ad_cost is not None else None
    target_contribution = _number(scenario.get('target_contribution'))
    if target_contribution is None:
        target_contribution = _number(scenario.get('minimum_contribution'))
    if target_contribution is None:
        target_contribution = _number(global_defaults.get('target_contribution'))
    if target_contribution is None:
        target_contribution = _number(global_defaults.get('minimum_contribution'))
    if target_contribution is None:
        target_contribution = 0.0
        target_basis = 'EXPLICIT_TARGET_NOT_SUPPLIED_ZERO_CONTRIBUTION_FLOOR_ONLY'
    else:
        target_basis = 'EXPLICIT_TARGET_CONTRIBUTION'
    allowable_ad_spend = contribution_before_ads - target_contribution
    break_even_cpa = max(0.0, allowable_ad_spend)
    cvr = _number(scenario.get('click_to_order_cvr'))
    if cvr is None:
        cvr = _number(global_defaults.get('click_to_order_cvr'))
    break_even_cpc = break_even_cpa * cvr if cvr is not None else None
    break_even_roas = price / break_even_cpa if break_even_cpa > 0 else None
    contribution_margin_rate = contribution_before_ads / price if price else None
    current_growth_spend = (resolved.get('affiliate_commission') or 0.0) + (ad_cost or 0.0) + (resolved.get('discount_funding') or 0.0)
    discount_headroom = max(0.0, contribution_before_ads - (ad_cost or 0.0) - target_contribution)
    waterfall = [{'name': 'revenue', 'amount': round(price, 6)}]
    waterfall.extend({'name': key, 'amount': round(-value, 6)} for key, value in pre_ad_components.items())
    waterfall.append({'name': 'contribution_before_ads', 'amount': round(contribution_before_ads, 6)})
    if ad_cost is not None:
        waterfall.append({'name': 'current_ad_cost', 'amount': round(-ad_cost, 6)})
        waterfall.append({'name': 'contribution_after_current_ads', 'amount': round(contribution_after_current_ads or 0.0, 6)})
    return {
        'scenario_id': sid,
        'sku': scenario.get('sku'),
        'configuration': scenario.get('configuration'),
        'bundle': scenario.get('bundle'),
        'offer_type': scenario.get('offer_type'),
        'role': scenario.get('role'),
        'price': round(price, 6),
        'status': 'CALCULATED_FROM_EXPLICIT_INPUTS',
        'missing_inputs': [],
        'resolved_components': {k: round(v, 6) for k, v in resolved.items()},
        'component_provenance': provenance,
        'contribution_waterfall': waterfall,
        'contribution_before_ads': round(contribution_before_ads, 6),
        'contribution_margin_rate_before_ads': round(contribution_margin_rate, 6) if contribution_margin_rate is not None else None,
        'contribution_after_current_ads': round(contribution_after_current_ads, 6) if contribution_after_current_ads is not None else None,
        'break_even_cpa': round(break_even_cpa, 6),
        'break_even_cpc': round(break_even_cpc, 6) if break_even_cpc is not None else None,
        'break_even_roas': round(break_even_roas, 6) if break_even_roas is not None else None,
        'click_to_order_cvr': cvr,
        'target_contribution': round(target_contribution, 6),
        'target_contribution_basis': target_basis,
        'discount_headroom_at_current_ad_cost': round(discount_headroom, 6),
        'current_growth_spend': round(current_growth_spend, 6),
        'formula_basis': {
            'contribution_before_ads': 'selling_price - explicit variable costs excluding ad_cost',
            'break_even_cpa': 'max(0, contribution_before_ads - target_contribution)',
            'break_even_cpc': 'break_even_cpa × explicit click_to_order_cvr; unavailable when CVR is not supplied',
            'break_even_roas': 'selling_price / break_even_cpa on the same per-order revenue basis; unavailable when allowable ad spend is zero/non-positive',
            'missing_rule': 'Absent fees/costs are unresolved, never silently treated as zero.',
        },
    }


def _pricing_decision(request: dict[str, Any], scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    source = request.get('offer_economics') or {}
    supplied = source.get('pricing_decision') or request.get('pricing_decision')
    if isinstance(supplied, dict) and supplied:
        return {
            'status': 'AGENT_DECISION_SUPPLIED',
            'decision': supplied.get('decision') or supplied.get('price') or supplied.get('recommended_price'),
            'why': supplied.get('why') or supplied.get('rationale'),
            'tradeoff': supplied.get('tradeoff'),
            'source_refs': supplied.get('source_refs') or supplied.get('source_ids') or [],
        }
    return {
        'status': 'AGENT_DECISION_REQUIRED',
        'decision': None,
        'why': None,
        'decision_requirements': [
            'Use market price bands/valleys only as evidence, never as automatic recommendation.',
            'Compare SKU/configuration role and contribution economics.',
            'State the chosen price/offer, WHY, tradeoff, and source/basis.',
        ],
        'calculated_scenario_count': sum(1 for x in scenarios if x.get('status') == 'CALCULATED_FROM_EXPLICIT_INPUTS'),
    }


def _sku_roles(scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    calculated = [x for x in scenarios if x.get('status') == 'CALCULATED_FROM_EXPLICIT_INPUTS']
    for row in scenarios:
        explicit = row.get('role')
        if explicit:
            role = explicit
            status = 'EXPLICIT_ROLE'
            why = 'Role was explicitly supplied by project strategy.'
        elif row.get('status') != 'CALCULATED_FROM_EXPLICIT_INPUTS':
            role = None
            status = 'ROLE_REQUIRES_INPUT'
            why = 'Economics are incomplete; runtime does not invent a portfolio role.'
        else:
            max_contrib = max((x.get('contribution_before_ads') or float('-inf')) for x in calculated) if calculated else None
            if max_contrib is not None and row.get('contribution_before_ads') == max_contrib:
                role = 'MARGIN_CANDIDATE'
                status = 'RUNTIME_CANDIDATE_NOT_STRATEGY_DECISION'
                why = 'Highest calculated pre-ad contribution among supplied scenarios; demand and portfolio evidence must confirm the role.'
            else:
                role = 'ASSORTMENT_CANDIDATE'
                status = 'RUNTIME_CANDIDATE_NOT_STRATEGY_DECISION'
                why = 'No explicit SKU role was supplied; economics alone cannot decide Hero/Traffic/Retention/Premium roles.'
        out.append({'scenario_id': row.get('scenario_id'), 'sku': row.get('sku'), 'role': role, 'status': status, 'why': why})
    return out


def compile_pricing_economics_authority(request: dict[str, Any], market_analysis: dict[str, Any] | None = None, legacy_economics: dict[str, Any] | None = None) -> dict[str, Any]:
    offer = request.get('offer_economics') or {}
    raw_scenarios = list(offer.get('scenarios') or [])
    if not raw_scenarios and offer.get('price') not in (None, ''):
        raw_scenarios = [{
            'scenario_id': offer.get('scenario_id') or request.get('sku') or 'BASE',
            'sku': request.get('sku'),
            'price': offer.get('price'),
            'costs': offer.get('costs') or {},
            'target_contribution': offer.get('target_contribution', offer.get('minimum_contribution')),
            'click_to_order_cvr': offer.get('click_to_order_cvr'),
            'configuration': offer.get('configuration'),
            'role': offer.get('role'),
        }]
    defaults = {
        'costs': offer.get('costs') or {},
        'required_cost_components': offer.get('required_cost_components'),
        'target_contribution': offer.get('target_contribution'),
        'minimum_contribution': offer.get('minimum_contribution'),
        'click_to_order_cvr': offer.get('click_to_order_cvr'),
    }
    scenarios = [_strict_scenario(x, defaults) for x in raw_scenarios]
    market = market_analysis or {}
    price_bands = market.get('price_bands') or []
    valleys = market.get('price_valley_signals') or []
    price_config = market.get('price_configuration_matrix') or []
    if not offer:
        status = 'NOT_SUPPLIED'
    elif not scenarios:
        status = 'MISSING_INPUT'
    elif all(x.get('status') == 'CALCULATED_FROM_EXPLICIT_INPUTS' for x in scenarios):
        status = 'READY'
    else:
        status = 'PARTIAL_MISSING_INPUT'
    missing = []
    for row in scenarios:
        for key in row.get('missing_inputs') or []:
            missing.append({'scenario_id': row.get('scenario_id'), 'input': key})
        for key in row.get('invalid_inputs') or []:
            missing.append({'scenario_id': row.get('scenario_id'), 'input': key, 'kind': 'INVALID'})
    decision = _pricing_decision(request, scenarios)
    sku_roles = _sku_roles(scenarios)
    listing_context = {
        'status': 'AVAILABLE' if scenarios else 'NOT_SUPPLIED',
        'pricing_decision': decision,
        'offer_boundaries': [
            {'scenario_id': x.get('scenario_id'), 'break_even_cpa': x.get('break_even_cpa'), 'break_even_roas': x.get('break_even_roas'), 'discount_headroom': x.get('discount_headroom_at_current_ad_cost')}
            for x in scenarios if x.get('status') == 'CALCULATED_FROM_EXPLICIT_INPUTS'
        ],
        'rule': 'Listing may communicate only the selected price/offer. Economics constrain the offer; they do not force price copy into every field or asset.',
    }
    ads_context = {
        'status': 'AVAILABLE' if any(x.get('status') == 'CALCULATED_FROM_EXPLICIT_INPUTS' for x in scenarios) else 'ECONOMICS_REQUIRED',
        'floors': [
            {'scenario_id': x.get('scenario_id'), 'sku': x.get('sku'), 'break_even_cpa': x.get('break_even_cpa'), 'break_even_cpc': x.get('break_even_cpc'), 'break_even_roas': x.get('break_even_roas'), 'target_contribution': x.get('target_contribution')}
            for x in scenarios if x.get('status') == 'CALCULATED_FROM_EXPLICIT_INPUTS'
        ],
        'rule': 'Ads may compare actual CPA/CPC/ROAS against these explicit-input floors; missing CVR keeps break-even CPC unresolved.',
    }
    return {
        'version': VERSION,
        'status': status,
        'currency': offer.get('currency') or (legacy_economics or {}).get('currency') or (request.get('target') or {}).get('currency'),
        'market_price_bands': price_bands,
        'market_price_valleys': valleys,
        'price_configuration_matrix': price_config,
        'scenarios': scenarios,
        'sku_roles': sku_roles,
        'pricing_decision': decision,
        'offer_bundle_discount_boundary': [
            {'scenario_id': x.get('scenario_id'), 'discount_headroom_at_current_ad_cost': x.get('discount_headroom_at_current_ad_cost'), 'break_even_cpa': x.get('break_even_cpa'), 'target_contribution': x.get('target_contribution')}
            for x in scenarios if x.get('status') == 'CALCULATED_FROM_EXPLICIT_INPUTS'
        ],
        'missing_inputs': missing,
        'legacy_economics_status': (legacy_economics or {}).get('status'),
        'downstream_consumers': {
            'product_strategy': {'status': 'BOUND', 'objects': ['SKU Roles', 'Price Bands', 'Price Valleys', 'Price/Configuration Matrix', 'Unit Economics', 'Contribution Margin', 'Pricing Decision + WHY']},
            'listing_creative': listing_context,
            'advertising_optimization': ads_context,
            'asset_strategy': {'status': 'BOUND_AS_CONTEXT_NOT_MANDATORY_COPY', 'rule': 'Image/video may consume offer/economic context when the purchase decision requires it; do not force price into every asset.'},
        },
        'principles': [
            'Runtime arithmetic uses explicit project inputs only.',
            'Absent costs/fees/CVR are unresolved; they are never silently defaulted to zero.',
            'Market price valleys are evidence signals, not automatic opportunities.',
            'Pricing Decision + WHY remains Agent-authored; deterministic runtime validates its economic boundaries.',
        ],
    }
