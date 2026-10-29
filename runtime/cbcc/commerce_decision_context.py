from __future__ import annotations

from copy import deepcopy
from typing import Any
import json


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    if value in (None, '', {}):
        return []
    return value if isinstance(value, list) else [value]


def _nonempty(value: Any) -> bool:
    if value in (None, '', [], {}):
        return False
    if isinstance(value, dict):
        return any(_nonempty(v) for v in value.values())
    if isinstance(value, list):
        return any(_nonempty(v) for v in value)
    return True


def _copy_keys(source: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: deepcopy(source.get(key)) for key in keys if _nonempty(source.get(key))}


def _lineage_row(domain: str, artifact: str, path: str, payload: Any) -> dict[str, Any]:
    return {
        'domain': domain,
        'source_artifact': artifact,
        'source_path': path,
        'payload_present': _nonempty(payload),
    }


def compile_commerce_decision_context(
    *,
    domain: dict[str, Any] | None = None,
    strategy: dict[str, Any] | None = None,
    culture: dict[str, Any] | None = None,
    target: dict[str, Any] | None = None,
    decision_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile one rich commercial decision context shared by strategy, curation, assets and delivery.

    This object intentionally preserves real decision payloads instead of collapsing active tools into
    status/count summaries. It does not invent missing research, prices, audience facts or economics.
    """
    domain = _dict(domain)
    strategy = _dict(strategy)
    culture = _dict(culture)
    target = _dict(target)
    decision_trace = _dict(decision_trace)

    market = _dict(domain.get('market'))
    economics = _dict(domain.get('economics'))
    pricing = _dict(domain.get('pricing_economics_authority')) or _dict(economics.get('pricing_economics_authority'))
    listing = _dict(domain.get('listing'))
    compiled_listing = _dict(listing.get('compiled'))
    ads = _dict(domain.get('ads'))
    feedback = _dict(domain.get('feedback'))
    experiment = _dict(domain.get('experiment'))

    sections = _dict(strategy.get('sections'))
    audience_section = _dict(sections.get('03_platform_region_audience_culture'))
    core = _dict(sections.get('04_marketing_core_strategy'))
    positioning = _dict(core.get('positioning'))
    race_raw = sections.get('07_race_execution_table') or core.get('RACE') or core.get('race') or []
    last = _dict(sections.get('09_risk_measurement_priority_next_steps'))

    market_payload = _copy_keys(market, (
        'status', 'market_summary', 'market_structure', 'price_bands', 'price_valley_signals',
        'price_configuration_matrix', 'configuration', 'segments', 'audience_segments',
        'demand_signals', 'keyword_signals', 'search_intent', 'customer_voice', 'review_themes',
        'competitor_summary', 'competitor_patterns', 'opportunities', 'risks', 'research_quality',
    ))
    pricing_payload = _copy_keys(pricing, (
        'status', 'currency', 'price_bands', 'price_valleys', 'price_configuration_matrix',
        'scenarios', 'sku_roles', 'pricing_decision', 'offer_boundary', 'offer_boundaries',
        'listing_context', 'ads_context', 'downstream_consumers', 'missing_inputs',
    ))
    if 'currency' not in pricing_payload and economics.get('currency'):
        pricing_payload['currency'] = economics.get('currency')
    if 'status' not in pricing_payload and economics.get('status'):
        pricing_payload['status'] = economics.get('status')
    if not pricing_payload.get('scenarios') and economics.get('scenarios'):
        pricing_payload['scenarios'] = deepcopy(economics.get('scenarios'))

    strategy_audience = audience_section.get('audience_segments') or audience_section.get('segments') or []
    audience_payload = {
        'target': _copy_keys(target, ('market', 'platform_family', 'platform', 'site', 'category', 'primary_locale')),
        'segments': deepcopy(strategy_audience or market.get('audience_segments') or market.get('segments') or []),
        'race_ethnicity': deepcopy(culture.get('race_ethnicity') or []),
        'intersectionality': deepcopy(culture.get('intersectionality') or []),
        'language_profiles': deepcopy(culture.get('language_profiles') or {}),
        'visual_implications': deepcopy(culture.get('visual_implications') or []),
        'copy_implications': deepcopy(culture.get('copy_implications') or []),
        'casting_constraints': deepcopy(culture.get('casting_constraints') or []),
        'taboo_stereotype_risks': deepcopy(culture.get('taboo_stereotype_risks') or culture.get('taboos') or []),
    }
    audience_payload = {k: v for k, v in audience_payload.items() if _nonempty(v)}

    listing_payload = {
        'status': listing.get('status') or compiled_listing.get('status'),
        'objections': deepcopy(compiled_listing.get('objection_resolution_plan') or []),
        'keywords': deepcopy(compiled_listing.get('keywords') or listing.get('keywords') or {}),
        'conversion_architecture': deepcopy(compiled_listing.get('conversion_architecture') or {}),
        'final_copy_status': _dict(compiled_listing.get('final_copy_workflow')).get('status'),
    }
    listing_payload = {k: v for k, v in listing_payload.items() if _nonempty(v)}

    ad_diagnosis = _dict(ads.get('aggregate')).get('diagnosis') or ads.get('diagnosis') or []
    ads_payload = {
        'status': ads.get('status'),
        'diagnosis': deepcopy(ad_diagnosis),
        'priority_actions': deepcopy(ads.get('priority_actions') or _dict(ads.get('aggregate')).get('priority_actions') or {}),
        'economics_context': deepcopy(ads.get('pricing_economics_context') or {}),
    }
    ads_payload = {k: v for k, v in ads_payload.items() if _nonempty(v)}

    review_payload = {
        'status': feedback.get('status'),
        'issues': deepcopy(feedback.get('issues') or []),
        'themes': deepcopy(feedback.get('themes') or feedback.get('clusters') or []),
        'positive_selling_points': deepcopy(feedback.get('positive_selling_point_ranking') or []),
        'local_revision_routes': deepcopy(feedback.get('local_revision_routes') or []),
    }
    review_payload = {k: v for k, v in review_payload.items() if _nonempty(v)}

    experiment_payload = _copy_keys(experiment, (
        'status', 'hypothesis', 'result', 'decision', 'confidence', 'incrementality', 'measurement',
    ))
    positioning_payload = _copy_keys(positioning, (
        'positioning_statement', 'target_user', 'primary_conversion_proposition',
        'secondary_reasons_to_buy', 'trust_drivers', 'objection_reducers', 'message_hierarchy',
    ))
    race_payload = deepcopy(_list(race_raw))
    decision_payload = deepcopy(decision_trace.get('traces') or [])
    measurement_payload = _copy_keys(last, ('priority_plan', 'measurement_plan', 'ab_test_plan', 'performance_learning', 'next_steps'))

    lineage = [
        _lineage_row('MARKET', 'artifacts/market_analysis.json', '$', market_payload),
        _lineage_row('PRICING_ECONOMICS', 'artifacts/pricing_economics_authority.json', '$', pricing_payload),
        _lineage_row('AUDIENCE_CULTURE', 'artifacts/culture_context.json', '$', audience_payload),
        _lineage_row('POSITIONING', 'artifacts/strategy/strategy_authority.json', 'sections.04_marketing_core_strategy.positioning', positioning_payload),
        _lineage_row('RACE', 'artifacts/strategy/strategy_authority.json', 'sections.07_race_execution_table', race_payload),
        _lineage_row('LISTING', 'artifacts/listing_analysis.json', '$.compiled', listing_payload),
        _lineage_row('ADS', 'artifacts/ad_analysis.json', '$', ads_payload),
        _lineage_row('REVIEWS', 'artifacts/feedback_analysis.json', '$', review_payload),
        _lineage_row('EXPERIMENT', 'artifacts/experiment_analysis.json', '$', experiment_payload),
        _lineage_row('DECISION_TRACE', 'artifacts/decision_trace.json', '$.traces', decision_payload),
        _lineage_row('MEASUREMENT', 'artifacts/strategy/strategy_authority.json', 'sections.09_risk_measurement_priority_next_steps', measurement_payload),
    ]
    lineage = [row for row in lineage if row['payload_present']]

    return {
        'status': 'COMMERCE_DECISION_CONTEXT_COMPILED',
        'market': market_payload,
        'pricing_economics': pricing_payload,
        'audience_culture': audience_payload,
        'positioning': positioning_payload,
        'race': race_payload,
        'listing': listing_payload,
        'ads': ads_payload,
        'reviews': review_payload,
        'experiment': experiment_payload,
        'decision_trace': decision_payload,
        'measurement': measurement_payload,
        'lineage_index': lineage,
        'continuity_rule': 'Analysis payloads remain source-bound and are filtered by asset relevance; status/count summaries never replace real decision payloads.',
    }


def _asset_needs_offer(asset: dict[str, Any]) -> bool:
    if asset.get('offer_relevant') is True:
        return True
    blob = ' '.join(str(asset.get(k) or '') for k in ('decision_intent', 'strategic_job', 'consumer_question', 'purchase_barrier', 'surface', 'family')).upper()
    return any(token in blob for token in ('PRICE', 'OFFER', 'VALUE', 'PROMO', 'DISCOUNT', 'TOTAL_COST', 'PAID_AD'))


def _asset_needs_ads(asset: dict[str, Any]) -> bool:
    blob = ' '.join(str(asset.get(k) or '') for k in ('surface', 'family', 'decision_origin', 'strategic_job')).upper()
    return 'PAID' in blob or 'AD' in blob


def _asset_needs_reviews(asset: dict[str, Any]) -> bool:
    blob = ' '.join(str(asset.get(k) or '') for k in ('decision_origin', 'decision_intent', 'purchase_barrier', 'strategic_job')).upper()
    return any(token in blob for token in ('FEEDBACK', 'REVIEW', 'EXPECTATION', 'MISUNDERSTANDING', 'USAGE', 'RETURN'))


def _race_for_asset(asset: dict[str, Any], rows: list[Any]) -> list[Any]:
    stage = str(asset.get('race_stage') or '').upper()
    if not stage:
        return deepcopy(rows)
    matched = [row for row in rows if isinstance(row, dict) and str(row.get('stage') or '').upper() == stage]
    return deepcopy(matched or rows)


def bind_asset_decision_lineage(asset: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Bind the smallest rich decision context that explains why this asset exists and how it should execute."""
    context = _dict(context)
    out: dict[str, Any] = {
        'status': 'ASSET_DECISION_LINEAGE_BOUND',
        'market': deepcopy(context.get('market') or {}),
        'audience_culture': deepcopy(context.get('audience_culture') or {}),
        'positioning': deepcopy(context.get('positioning') or {}),
        'race': _race_for_asset(asset, _list(context.get('race'))),
        'listing': deepcopy(context.get('listing') or {}),
        'decision_trace': deepcopy(context.get('decision_trace') or []),
        'measurement': deepcopy(context.get('measurement') or {}),
    }
    if _asset_needs_offer(asset):
        out['pricing_economics'] = deepcopy(context.get('pricing_economics') or {})
    else:
        pricing = _dict(context.get('pricing_economics'))
        # Keep only market evidence useful for context; do not force a selected price/offer into unrelated assets.
        evidence_only = _copy_keys(pricing, ('status', 'currency', 'price_bands', 'price_valleys', 'price_configuration_matrix'))
        if evidence_only:
            out['pricing_economics'] = evidence_only
    if _asset_needs_ads(asset):
        out['ads'] = deepcopy(context.get('ads') or {})
    if _asset_needs_reviews(asset):
        out['reviews'] = deepcopy(context.get('reviews') or {})
    if context.get('experiment'):
        out['experiment'] = deepcopy(context.get('experiment'))

    active_domains = [k for k, v in out.items() if k not in {'status', 'lineage_refs'} and _nonempty(v)]
    refs = []
    for row in context.get('lineage_index') or []:
        if not isinstance(row, dict):
            continue
        key_map = {
            'MARKET': 'market', 'PRICING_ECONOMICS': 'pricing_economics', 'AUDIENCE_CULTURE': 'audience_culture',
            'POSITIONING': 'positioning', 'RACE': 'race', 'LISTING': 'listing', 'ADS': 'ads',
            'REVIEWS': 'reviews', 'EXPERIMENT': 'experiment', 'DECISION_TRACE': 'decision_trace', 'MEASUREMENT': 'measurement',
        }
        if key_map.get(str(row.get('domain'))) in active_domains:
            refs.append({k: row.get(k) for k in ('domain', 'source_artifact', 'source_path')})
    out['lineage_refs'] = refs
    out['asset_binding'] = {
        'asset_id': asset.get('asset_id'),
        'surface': asset.get('surface'),
        'decision_intent': asset.get('decision_intent'),
        'race_stage': asset.get('race_stage'),
        'offer_relevant': _asset_needs_offer(asset),
        'ads_relevant': _asset_needs_ads(asset),
        'review_relevant': _asset_needs_reviews(asset),
    }
    return out


def _flatten_text(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


def audit_asset_decision_consumption(asset: dict[str, Any], prompt_bundle: dict[str, Any]) -> dict[str, Any]:
    """Verify that a bound commercial context has real downstream consumers, not file-presence theater."""
    bound = _dict(asset.get('commerce_decision_context') or asset.get('decision_lineage'))
    if not bound:
        return {'status': 'NOT_BOUND', 'issues': [], 'checks': []}
    card = _dict(prompt_bundle.get('design_card'))
    card_context = _dict(card.get('commerce_decision_context'))
    prompt = str(prompt_bundle.get('prompt_cn') or '') + '\n' + str(prompt_bundle.get('prompt_en') or '')
    checks = [
        {'consumer': 'DESIGN_CARD', 'projected': bool(card_context), 'required': True},
        {'consumer': 'MODEL_PROMPT_COMMERCIAL_CONTEXT', 'projected': ('COMMERCE DECISION CONTEXT' in prompt or '商业决策上下文' in prompt), 'required': True},
    ]
    pricing = _dict(bound.get('pricing_economics'))
    decision = _dict(pricing.get('pricing_decision'))
    if decision.get('decision') not in (None, '') and _asset_needs_offer(asset):
        value = str(decision.get('decision'))
        checks.append({'consumer': 'SELECTED_PRICE_OR_OFFER', 'projected': value in prompt, 'required': True, 'value': value})
    positioning = _dict(bound.get('positioning'))
    proposition = positioning.get('primary_conversion_proposition')
    if proposition:
        checks.append({'consumer': 'PRIMARY_CONVERSION_PROPOSITION', 'projected': str(proposition) in prompt, 'required': True, 'value': proposition})
    missing = [x['consumer'] for x in checks if x.get('required') and not x.get('projected')]
    return {
        'status': 'PASS' if not missing else 'INCOMPLETE',
        'issues': missing,
        'checks': checks,
        'bound_domains': [k for k, v in bound.items() if k not in {'status', 'lineage_refs', 'asset_binding'} and _nonempty(v)],
        'lineage_refs': deepcopy(bound.get('lineage_refs') or []),
    }
