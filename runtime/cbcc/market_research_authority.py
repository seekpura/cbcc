from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any, Callable, Mapping, Sequence
import json


SCHEMA = 'cbcc-market-research-authority-v1'
REQUIRED_DOMAINS = (
    'DEMAND', 'SEARCH', 'COMPETITION', 'PRICE_BAND',
    'REVIEWS', 'NEGATIVE_REVIEWS', 'OPPORTUNITY', 'RISK',
)
NEGATIVE_LABELS = {
    'NEGATIVE', 'NEG', 'BAD', 'COMPLAINT', 'ISSUE', 'PROBLEM',
    '1_STAR', '2_STAR', 'ONE_STAR', 'TWO_STAR',
}


def _present(value: Any) -> bool:
    return value not in (None, '', [], {})


def _list(value: Any) -> list[Any]:
    if value in (None, '', {}):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set, frozenset)):
        return list(value)
    return [value]


def _stable_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), default=str).encode('utf-8')
    return sha256(raw).hexdigest()


def _source_index(market: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    quality = market.get('research_quality') if isinstance(market.get('research_quality'), Mapping) else {}
    out: dict[str, dict[str, Any]] = {}
    for raw in _list(quality.get('sources')):
        if not isinstance(raw, Mapping) or not _present(raw.get('source_id')):
            continue
        row = deepcopy(dict(raw))
        out[str(row['source_id'])] = row
    return out


def _dataset_index(market: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    quality = market.get('research_quality') if isinstance(market.get('research_quality'), Mapping) else {}
    out: dict[str, dict[str, Any]] = {}
    for raw in _list(quality.get('datasets')):
        if isinstance(raw, Mapping) and _present(raw.get('dataset')):
            out[str(raw['dataset'])] = deepcopy(dict(raw))
    return out


def _dataset_source_ids(market: Mapping[str, Any], dataset: str) -> list[str]:
    row = _dataset_index(market).get(dataset) or {}
    return [str(x) for x in _list(row.get('source_ids')) if _present(x)]


def _nested_source_ids(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key == 'source_ids':
                found.extend(str(x) for x in _list(item) if _present(x))
            elif key == 'source_id' and _present(item):
                found.append(str(item))
            else:
                found.extend(_nested_source_ids(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(_nested_source_ids(item))
    return list(dict.fromkeys(found))


def _source_cards(source_ids: Sequence[str], source_index: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for sid in source_ids:
        src = source_index.get(str(sid))
        if not src:
            continue
        cards.append({
            'source_id': str(sid),
            'kind': src.get('kind'),
            'title': src.get('title'),
            'url': src.get('url'),
            'observed_at': src.get('observed_at'),
            'age_days': src.get('age_days'),
            'freshness_status': src.get('freshness_status'),
            'representativeness_status': src.get('representativeness_status'),
            'scope_mismatches': deepcopy(src.get('scope_mismatches') or []),
            'source_quality_status': src.get('source_quality_status'),
            'source_quality_score': src.get('source_quality_score'),
            'source_quality_tier': src.get('source_quality_tier'),
        })
    return cards


def _confidence(source_ids: Sequence[str], cards: Sequence[Mapping[str, Any]]) -> str:
    if not source_ids or len(cards) != len(set(str(x) for x in source_ids)):
        return 'LOW'
    if any(str(card.get('freshness_status') or '') in {'OUTSIDE_DECLARED_FRESHNESS_WINDOW', 'OBSERVATION_AFTER_AS_OF_REVIEW'} for card in cards):
        return 'LOW'
    if any(card.get('scope_mismatches') for card in cards):
        return 'LOW'
    documented = all(str(card.get('representativeness_status') or '') == 'REPRESENTATIVENESS_DOCUMENTED_NOT_PROVEN' for card in cards)
    quality_declared = all(str(card.get('source_quality_status') or '') in {'EXPLICIT_SCORE_SUPPLIED', 'EXPLICIT_TIER_SUPPLIED'} for card in cards)
    fresh = all(str(card.get('freshness_status') or '') == 'WITHIN_DECLARED_FRESHNESS_WINDOW' for card in cards)
    return 'HIGH' if documented and quality_declared and fresh else 'MEDIUM'


def _evidence(source_ids: Sequence[str], source_index: Mapping[str, Mapping[str, Any]], as_of: Any) -> dict[str, Any]:
    ids = list(dict.fromkeys(str(x) for x in source_ids if _present(x)))
    cards = _source_cards(ids, source_index)
    return {
        'source_ids': ids,
        'source_cards': cards,
        'as_of': as_of,
        'recency_statuses': sorted({str(card.get('freshness_status') or 'DATE_NOT_SUPPLIED') for card in cards}),
        'traceability_status': 'SOURCE_BOUND' if ids and len(cards) == len(ids) else 'SOURCE_TRACE_INCOMPLETE',
    }


def _finding(
    *,
    object_id: str,
    domain: str,
    what: str,
    why: str,
    exact_fact: Any,
    interpretation: str,
    source_ids: Sequence[str],
    source_index: Mapping[str, Mapping[str, Any]],
    as_of: Any,
    tradeoff: str,
    execution: Any,
    measurement: Any,
    assumption_boundary: str,
    downstream_use: Sequence[str],
    conflict_status: str = 'NO_DECLARED_CONFLICT',
    status: str | None = None,
) -> dict[str, Any]:
    evidence = _evidence(source_ids, source_index, as_of)
    confidence = _confidence(evidence['source_ids'], evidence['source_cards'])
    resolved_status = status or ('EVIDENCED' if _present(exact_fact) and evidence['traceability_status'] == 'SOURCE_BOUND' else 'TO_VERIFY')
    return {
        'object_id': object_id,
        'domain': domain,
        'status': resolved_status,
        'what': what,
        'why': why,
        'evidence': evidence,
        'tradeoff': tradeoff,
        'execution': deepcopy(execution),
        'measurement': deepcopy(measurement),
        'exact_fact': deepcopy(exact_fact),
        'interpretation': interpretation,
        'confidence': confidence,
        'assumption_boundary': assumption_boundary,
        'downstream_use': list(downstream_use),
        'conflict_status': conflict_status,
    }


def _missing(domain: str, needed: Sequence[str], downstream_use: Sequence[str]) -> dict[str, Any]:
    return {
        'object_id': f'RESEARCH-{domain}-MISSING',
        'domain': domain,
        'status': 'TO_VERIFY',
        'what': f'{domain} research evidence is not currently supplied.',
        'why': 'The FULL research contract requires this domain to be explicit; silence would incorrectly look like analysis completion.',
        'evidence': {'source_ids': [], 'source_cards': [], 'as_of': None, 'recency_statuses': [], 'traceability_status': 'MISSING_INPUT'},
        'tradeoff': 'Proceed only with unrelated verified evidence; do not infer this domain from another dataset.',
        'execution': {'missing_input': list(needed), 'next_action': 'COLLECT_OR_VERIFY_RESEARCH_EVIDENCE'},
        'measurement': {'completion_signal': 'Required evidence supplied with source/time/scope metadata.'},
        'exact_fact': None,
        'interpretation': 'No market conclusion is authorized for this domain.',
        'confidence': 'LOW',
        'assumption_boundary': 'UNKNOWN/TO_VERIFY. No market size, search volume, rank, sales or buyer-population claim may be invented.',
        'downstream_use': list(downstream_use),
        'conflict_status': 'NOT_ASSESSED_MISSING_EVIDENCE',
    }


def _domain(findings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [deepcopy(dict(x)) for x in findings]
    if not rows:
        return {'status': 'MISSING_INPUT', 'findings': []}
    statuses = {str(x.get('status') or '') for x in rows}
    if 'EVIDENCED' in statuses:
        status = 'EVIDENCED'
    elif 'RESEARCH_HYPOTHESIS' in statuses:
        status = 'RESEARCH_HYPOTHESIS'
    elif 'TO_VERIFY' in statuses:
        status = 'TO_VERIFY'
    else:
        status = next(iter(statuses), 'MISSING_INPUT')
    return {'status': status, 'finding_count': len(rows), 'findings': rows}


def compile_market_research_authority(market_analysis: Mapping[str, Any] | None) -> dict[str, Any]:
    market = deepcopy(dict(market_analysis or {}))
    quality = market.get('research_quality') if isinstance(market.get('research_quality'), Mapping) else {}
    as_of = quality.get('as_of')
    sources = _source_index(market)
    domains: dict[str, dict[str, Any]] = {}

    demand_sources = _dataset_source_ids(market, 'market_rows')
    capacity = market.get('market_capacity') if isinstance(market.get('market_capacity'), Mapping) else {}
    if _present(capacity) and int(market.get('row_count') or 0) > 0:
        domains['DEMAND'] = _domain([_finding(
            object_id='RESEARCH-DEMAND-001', domain='DEMAND',
            what='Observed demand/capacity signal inside the supplied market sample.',
            why='Supplied units/revenue describe the analyzed sample and can inform prioritization, but must not be restated as total market size.',
            exact_fact={'row_count': market.get('row_count'), 'sample_units': capacity.get('units'), 'sample_revenue': capacity.get('revenue'), 'scope': capacity.get('scope') or 'SUPPLIED_SAMPLE_ONLY'},
            interpretation='Use only as a sample-scoped demand signal; validate representativeness before generalizing.',
            source_ids=demand_sources, source_index=sources, as_of=as_of,
            tradeoff='Broader generalization increases strategic confidence only if sampling scope supports it; otherwise preserve the sample boundary.',
            execution={'strategy': 'Use as directional demand evidence only.', 'listing': 'Do not convert sample demand into consumer-facing popularity claims.'},
            measurement={'next_check': ['sample-frame coverage', 'freshness', 'repeat collection consistency']},
            assumption_boundary='SUPPLIED_SAMPLE_ONLY; no population market-size claim.',
            downstream_use=['STRATEGY', 'ECONOMICS', 'OFFER', 'MEASUREMENT'],
        )])
    else:
        domains['DEMAND'] = _domain([_missing('DEMAND', ['market_rows with units/revenue and source metadata'], ['STRATEGY','ECONOMICS','OFFER'])])

    search_rows: list[dict[str, Any]] = []
    for index, row in enumerate(_list((market.get('keyword_demand') or {}).get('top_terms')), 1):
        if not isinstance(row, Mapping) or not _present(row.get('term')):
            continue
        sids = [str(x) for x in _list(row.get('source_ids')) if _present(x)] or _dataset_source_ids(market, 'keyword_rows')
        search_rows.append(_finding(
            object_id=f'RESEARCH-SEARCH-{index:03d}', domain='SEARCH',
            what=f"Observed search term: {row.get('term')}",
            why='Search evidence can expose shopper language and intent, but relevance to the exact SKU remains a Product Truth decision.',
            exact_fact={'term': row.get('term'), 'volume': row.get('volume'), 'avg_competition': row.get('avg_competition'), 'avg_rank': row.get('avg_rank'), 'intent': row.get('intent'), 'records': row.get('records')},
            interpretation='Use only where the term is semantically truthful for the SKU; high demand alone does not authorize a claim or keyword.',
            source_ids=sids, source_index=sources, as_of=as_of,
            tradeoff='Traffic opportunity must be balanced against semantic relevance and claim integrity.',
            execution={'listing_search': 'Route verified-relevance terms into Listing/Search architecture; otherwise HOLD.', 'content': 'Use intent to frame decision questions, not unsupported promises.'},
            measurement={'next_check': ['query-to-SKU relevance', 'search CTR/CVR after activation', 'term freshness']},
            assumption_boundary='Observed search metrics apply only to the supplied source/query scope and date.',
            downstream_use=['LISTING_SEARCH', 'CONTENT_MATRIX', 'PAID', 'MEASUREMENT'],
        ))
    domains['SEARCH'] = _domain(search_rows or [_missing('SEARCH', ['keyword/search rows with explicit source IDs'], ['LISTING_SEARCH','CONTENT_MATRIX','PAID'])])

    comp_sources = list(dict.fromkeys(_dataset_source_ids(market, 'market_rows') + _dataset_source_ids(market, 'competitor_listing_rows')))
    concentration = market.get('concentration') if isinstance(market.get('concentration'), Mapping) else {}
    competitor_intel = market.get('competitor_listing_intelligence') if isinstance(market.get('competitor_listing_intelligence'), Mapping) else {}
    if _present(concentration) or _list(competitor_intel.get('competitors')):
        domains['COMPETITION'] = _domain([_finding(
            object_id='RESEARCH-COMPETITION-001', domain='COMPETITION',
            what='Observed competition structure and competitor-message evidence in the supplied sample.',
            why='Concentration and observed competitor messaging shape differentiation strategy, but neither proves market dominance outside the sampled scope.',
            exact_fact={'concentration': deepcopy(concentration), 'competitor_count_observed': len(_list(competitor_intel.get('competitors'))), 'message_theme_summary': deepcopy(_list(competitor_intel.get('message_theme_summary'))[:20])},
            interpretation='Use to identify crowded versus fragmented structures and observed message sameness; verify current platform/category coverage before selecting a differentiation territory.',
            source_ids=comp_sources, source_index=sources, as_of=as_of,
            tradeoff='Differentiation can improve distinctiveness but must stay inside own Product Truth and avoid unsupported comparative superiority.',
            execution={'strategy': 'Map observed competitor structures/themes to truthful differentiation options.', 'visual': 'Treat visual/content sameness as research input, not an automatic style prescription.'},
            measurement={'next_check': ['competitor sample coverage', 'message/proof overlap', 'share-of-search or platform response after activation']},
            assumption_boundary='Competitor structure describes supplied listings/market rows only; it is not a complete census unless the source declares one.',
            downstream_use=['POSITIONING', 'MESSAGE_HIERARCHY', 'LISTING_SEARCH', 'VISUAL_MASTER', 'PAID'],
        )])
    else:
        domains['COMPETITION'] = _domain([_missing('COMPETITION', ['market/competitor rows with seller or listing evidence'], ['POSITIONING','MESSAGE_HIERARCHY','VISUAL_MASTER'])])

    price_sources = _dataset_source_ids(market, 'market_rows')
    price_summary = market.get('price_summary') if isinstance(market.get('price_summary'), Mapping) else {}
    bands = _list(market.get('price_bands'))
    matrix = _list(market.get('price_configuration_matrix'))
    if _present(price_summary) and any(_present(v) for v in price_summary.values()):
        domains['PRICE_BAND'] = _domain([_finding(
            object_id='RESEARCH-PRICE-001', domain='PRICE_BAND',
            what='Observed price-band and price×configuration structure in the supplied sample.',
            why='Price context helps frame offer architecture and competitive position, but own-SKU pricing still requires unit economics.',
            exact_fact={'price_summary': deepcopy(price_summary), 'price_bands': deepcopy(bands[:30]), 'price_configuration_matrix': deepcopy(matrix[:30])},
            interpretation='Use for category context and hypotheses only; do not convert a market price band into an own-SKU price recommendation without economics.',
            source_ids=price_sources, source_index=sources, as_of=as_of,
            tradeoff='Market fit and margin protection are separate constraints; neither overrides the other.',
            execution={'economics': 'Pass observed bands into Economics/Offer as context, not recommendation.', 'listing': 'Use configuration language only where Product Truth matches.'},
            measurement={'next_check': ['contribution margin at candidate price', 'configuration response', 'price-band freshness']},
            assumption_boundary='Observed prices/configurations reflect supplied rows only and may exclude promotions, shipping or off-platform effects.',
            downstream_use=['ECONOMICS', 'OFFER', 'SKU_STRATEGY', 'MEASUREMENT'],
        )])
    else:
        domains['PRICE_BAND'] = _domain([_missing('PRICE_BAND', ['market rows with price/configuration and source metadata'], ['ECONOMICS','OFFER','SKU_STRATEGY'])])

    review_findings: list[dict[str, Any]] = []
    negative_findings: list[dict[str, Any]] = []
    for index, row in enumerate(_list((market.get('customer_voice') or {}).get('theme_summary')), 1):
        if not isinstance(row, Mapping) or not _present(row.get('theme')) or str(row.get('theme')) == 'UNCLASSIFIED':
            continue
        sids = [str(x) for x in _list(row.get('source_ids')) if _present(x)] or _dataset_source_ids(market, 'review_rows')
        base = _finding(
            object_id=f'RESEARCH-REVIEW-{index:03d}', domain='REVIEWS',
            what=f"Observed supplied review theme: {row.get('theme')}",
            why='Repeated explicit review labels can reveal buyer language, objections and expectation gaps without pretending the sample represents the full market.',
            exact_fact={'theme': row.get('theme'), 'weighted_mentions': row.get('weighted_mentions'), 'records': row.get('records'), 'dominant_sentiment': row.get('dominant_sentiment'), 'sentiment_mix': deepcopy(row.get('sentiment_mix') or {})},
            interpretation='Treat as sampled customer voice. Product-fit and root-cause claims require separate verification.',
            source_ids=sids, source_index=sources, as_of=as_of,
            tradeoff='Addressing a repeated concern can improve relevance, but overgeneralizing sampled reviews creates false certainty.',
            execution={'review_analysis': 'Route theme to root-cause/expectation analysis.', 'content': 'Translate only verified concerns into FAQ/objection/content jobs.'},
            measurement={'next_check': ['theme recurrence in new samples', 'post-fix complaint rate', 'conversion/return impact where available']},
            assumption_boundary='No causal claim or population frequency is authorized from supplied labels alone.',
            downstream_use=['REVIEW_ANALYSIS', 'FAQ_OBJECTION', 'CONTENT_MATRIX', 'LISTING_SEARCH', 'MEASUREMENT'],
        )
        review_findings.append(base)
        sentiment = str(row.get('dominant_sentiment') or '').strip().upper().replace(' ', '_')
        if sentiment in NEGATIVE_LABELS:
            neg = deepcopy(base)
            neg['object_id'] = f'RESEARCH-NEGATIVE-REVIEW-{index:03d}'
            neg['domain'] = 'NEGATIVE_REVIEWS'
            neg['what'] = f"Explicitly negative supplied review theme: {row.get('theme')}"
            neg['why'] = 'The source explicitly labels this theme negative; it is eligible for unmet-job/expectation-gap investigation without inferring sentiment from free text.'
            neg['execution'] = {'review_analysis': 'Investigate root cause and expectation mismatch.', 'strategy': 'Use only if Product Truth can truthfully address the concern.'}
            neg['downstream_use'] = ['REVIEW_ANALYSIS', 'POSITIONING', 'FAQ_OBJECTION', 'LOCAL_REVISION']
            negative_findings.append(neg)
    domains['REVIEWS'] = _domain(review_findings or [_missing('REVIEWS', ['review rows with explicit theme/category labels and source IDs'], ['REVIEW_ANALYSIS','FAQ_OBJECTION','CONTENT_MATRIX'])])
    domains['NEGATIVE_REVIEWS'] = _domain(negative_findings or [_missing('NEGATIVE_REVIEWS', ['review rows with explicit negative sentiment/polarity labels'], ['REVIEW_ANALYSIS','POSITIONING','FAQ_OBJECTION'])])

    opportunity_findings: list[dict[str, Any]] = []
    for index, row in enumerate(_list(market.get('opportunity_map')), 1):
        if not isinstance(row, Mapping):
            continue
        sids = _nested_source_ids(row.get('signal'))
        finding = _finding(
            object_id=str(row.get('opportunity_id') or f'RESEARCH-OPPORTUNITY-{index:03d}'), domain='OPPORTUNITY',
            what=f"Research opportunity hypothesis: {row.get('type') or 'UNCLASSIFIED'}",
            why=str(row.get('why') or 'This is a bounded hypothesis derived from supplied research signals.'),
            exact_fact={'type': row.get('type'), 'signal': deepcopy(row.get('signal')), 'decision_status': row.get('decision_status')},
            interpretation=str(row.get('interpretation') or 'Validate before recommendation.'),
            source_ids=sids, source_index=sources, as_of=as_of,
            tradeoff='Pursuing the hypothesis may improve differentiation/relevance, but only after Product Truth, economics, compliance and sample-scope checks.',
            execution={'cross_checks_required': deepcopy(row.get('cross_checks_required') or []), 'next_action': 'VALIDATE_HYPOTHESIS_BEFORE_ACTIVATION'},
            measurement={'decision_rule': 'Promote only when required cross-checks pass and a measurable downstream hypothesis exists.'},
            assumption_boundary='RESEARCH_HYPOTHESIS_NOT_RECOMMENDATION.',
            downstream_use=['STRATEGY', 'LISTING_SEARCH', 'CONTENT_MATRIX', 'ASSET_OPPORTUNITY_UNIVERSE'],
            status='RESEARCH_HYPOTHESIS',
        )
        if str(row.get('data_confidence') or '').upper() in {'LOW','MEDIUM','HIGH'}:
            finding['confidence'] = str(row.get('data_confidence')).upper()
        opportunity_findings.append(finding)
    domains['OPPORTUNITY'] = _domain(opportunity_findings or [_missing('OPPORTUNITY', ['cross-checked demand/search/competition/review evidence'], ['STRATEGY','CONTENT_MATRIX','ASSET_OPPORTUNITY_UNIVERSE'])])

    risk_findings: list[dict[str, Any]] = []
    stale = [str(x) for x in _list(quality.get('stale_by_declared_threshold')) if _present(x)]
    mismatch = [str(x) for x in _list(quality.get('scope_mismatch_source_ids')) if _present(x)]
    unresolved = [str(x) for x in _list(quality.get('unresolved_source_ids')) if _present(x)]
    risky = list(dict.fromkeys(stale + mismatch + unresolved))
    if risky:
        risk_findings.append(_finding(
            object_id='RESEARCH-RISK-SOURCE-QUALITY', domain='RISK',
            what='Research source freshness/scope/traceability risk detected.',
            why='Stale, mismatched or unresolved evidence can distort strategic weighting and must remain visible instead of being averaged away.',
            exact_fact={'stale_source_ids': stale, 'scope_mismatch_source_ids': mismatch, 'unresolved_source_ids': unresolved},
            interpretation='Down-weight or re-verify affected findings before material downstream decisions.',
            source_ids=risky, source_index=sources, as_of=as_of,
            tradeoff='Using weak evidence preserves speed but reduces decision confidence; refreshing evidence costs time but protects strategy quality.',
            execution={'next_action': 'REFRESH_OR_REPLACE_AFFECTED_SOURCES', 'affected_source_ids': risky},
            measurement={'completion_signal': 'Affected sources become current, scope-matched and traceable or are explicitly excluded.'},
            assumption_boundary='No affected evidence may be silently upgraded to current/representative.',
            downstream_use=['ALL_RESEARCH_CONSUMERS', 'DECISION_LOG', 'MEASUREMENT'],
        ))
    else:
        all_source_ids = list(sources)
        if all_source_ids:
            risk_findings.append(_finding(
                object_id='RESEARCH-RISK-SOURCE-QUALITY', domain='RISK',
                what='Research source-quality review for current supplied evidence.',
                why='Even when no declared stale/scope/traceability issue exists, representativeness remains bounded by source metadata.',
                exact_fact={'stale_source_ids': [], 'scope_mismatch_source_ids': [], 'unresolved_source_ids': [], 'representativeness_principle': quality.get('representativeness_principle') or 'Representativeness is not inferred from row count.'},
                interpretation='No declared source-quality blocker is present; retain sample-boundary caveats.',
                source_ids=all_source_ids, source_index=sources, as_of=as_of,
                tradeoff='Confidence can remain usable while still refusing unsupported population generalization.',
                execution={'next_action': 'PRESERVE_SOURCE_SCOPE_AND_RECENCY_IN_DOWNSTREAM_DECISIONS'},
                measurement={'next_check': ['source freshness at decision time', 'sample-frame changes']},
                assumption_boundary='Absence of a declared issue is not proof of population representativeness.',
                downstream_use=['ALL_RESEARCH_CONSUMERS', 'DECISION_LOG', 'MEASUREMENT'],
            ))
    domains['RISK'] = _domain(risk_findings or [_missing('RISK', ['research source/recency/scope metadata'], ['ALL_RESEARCH_CONSUMERS','DECISION_LOG'])])

    authority = {
        'schema': SCHEMA,
        'status': 'RESEARCH_AUTHORITY_READY' if any(d.get('status') in {'EVIDENCED','RESEARCH_HYPOTHESIS'} for d in domains.values()) else 'RESEARCH_INPUT_REQUIRED',
        'contract': 'Market/search/competition/price-band/review opportunity research with source authority, recency, exact fact, interpretation, confidence, assumption boundary, downstream use, conflict, tradeoff, execution and measurement.',
        'as_of': as_of,
        'domains': {name: domains[name] for name in REQUIRED_DOMAINS},
        'source_ledger': list(sources.values()),
        'lineage_rule': 'source → authority/type → recency → exact fact → interpretation → confidence → assumption boundary → downstream use → conflict → decision/tradeoff → proof object',
        'no_fabrication_rule': 'Missing research stays UNKNOWN/TO_VERIFY/MISSING_INPUT. Never invent market size, search volume, rank, sales, review prevalence or competitor dominance.',
        'canonical_graph_binding': {
            'node_id': 'RESEARCH',
            'authority_role': 'CANONICAL_RESEARCH_SUBOBJECT',
            'container': 'market_analysis.json#/research_authority',
        },
    }
    authority['authority_sha256'] = _stable_hash(authority)
    return authority


def wrap_analyze_market(fn: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    if getattr(fn, '_cbcc_v0676_market_research_authority', False):
        return fn

    def compiled(*args: Any, **kwargs: Any) -> dict[str, Any]:
        out = fn(*args, **kwargs)
        result = deepcopy(dict(out or {}))
        result['research_authority'] = compile_market_research_authority(result)
        result['research_authority_status'] = result['research_authority']['status']
        return result

    setattr(compiled, '_cbcc_v0676_market_research_authority', True)
    return compiled
