from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .models import stable_hash

VERSION = '0.6.21-commerce-agent-autonomy'


def _rows(value: Any) -> list[dict[str, Any]]:
    return [dict(row) for row in (value or []) if isinstance(row, Mapping)]


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple, set, frozenset)):
        value = [value]
    return [str(item) for item in value if str(item or '').strip()]


def _agent_input(request: Mapping[str, Any]) -> dict[str, Any]:
    raw = request.get('agent_plan') or request.get('agent_decisions') or {}
    return deepcopy(dict(raw)) if isinstance(raw, Mapping) else {}


def _research_requirement(topic: str, domain: str, reason: str, required_for: list[str], *, query: str | None = None, preferred_source: str | None = None) -> dict[str, Any]:
    row = {
        'topic': topic,
        'domain': domain,
        'reason': reason,
        'required_for': required_for,
        'query': query or f'Find current evidence that can materially change the decision about {topic}',
    }
    row['id'] = 'REQ-' + stable_hash(row)[:10].upper()
    if preferred_source:
        row['preferred_source'] = preferred_source
    return row


def _derive_research_requirements(request: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Infer decision-changing evidence gaps only; this is a fallback when the host agent has not authored a plan.

    The fallback deliberately does not define a fixed market/competitor/review checklist. A gap is created only
    when the current request lacks evidence needed for a concrete commerce decision.
    """
    target = dict(request.get('target') or {})
    requirements: list[dict[str, Any]] = []

    unknowns = _strings(request.get('unknowns'))
    if unknowns:
        requirements.append(_research_requirement(
            ' / '.join(unknowns[:4]),
            'PRODUCT_TRUTH',
            'Product Truth still contains unknowns that can change positioning, claims, listing or production.',
            ['PRODUCT_TRUTH', 'STRATEGY', 'LISTING', 'ASSET_ARCHITECTURE'],
            preferred_source='PRODUCT_SOURCE_OR_OFFICIAL_MANUFACTURER_SOURCE',
        ))

    has_market_evidence = bool(
        request.get('market_rows')
        or request.get('market_file')
        or request.get('market_keyword_rows')
        or request.get('market_review_rows')
        or request.get('competitor_listing_rows')
        or request.get('market_source_records')
        or request.get('research_source_adapters')
    )
    if target.get('market') and not has_market_evidence:
        requirements.append(_research_requirement(
            f"{target.get('market')} shopper / demand / competition evidence for the current product",
            'MARKET',
            'Cross-border positioning and asset priorities should not be inferred from Product Truth alone.',
            ['STRATEGY', 'LISTING', 'ASSET_ARCHITECTURE'],
            query=f"Research current {target.get('market')} demand, shopper language, objections and competitive patterns for this exact product/category; stop when new evidence no longer changes a material decision.",
            preferred_source='CURRENT_MARKET_AND_FIRST_PARTY_OR_PLATFORM_EVIDENCE',
        ))

    has_platform_evidence = bool(target.get('source_ids') or request.get('platform_source_ids') or request.get('platform_pack'))
    if target.get('platform_family') and target.get('site') and not has_platform_evidence:
        requirements.append(_research_requirement(
            f"Current {target.get('platform_family')} / {target.get('site')} category rules that affect this deliverable",
            'PLATFORM_RULE',
            'Only platform rules that can change listing, asset, fulfillment or claim decisions need to be researched.',
            ['TARGET_CONTEXT', 'LISTING', 'COMPLIANCE', 'PRODUCTION'],
            query=f"Verify current official {target.get('platform_family')} {target.get('site')} rules for the requested category/surfaces; collect only rules that materially constrain the current project.",
            preferred_source='OFFICIAL_CURRENT_SOURCE',
        ))

    return requirements


def compile_agent_autonomy_plan(request: Mapping[str, Any]) -> dict[str, Any]:
    """Compile the decision authority boundary for an AI commerce agent.

    Product truth, legal/compliance facts, platform hard limits and explicit user locks remain hard constraints.
    Research depth, content scope, asset count, creative exploration, photography choices and iteration depth are
    agent decisions. Runtime heuristics exist only as a compatibility fallback when the host has not authored them.
    """
    agent = _agent_input(request)
    explicit_research = _rows(agent.get('research_requirements') or agent.get('research_plan'))
    request_research = _rows(request.get('research_requirements'))
    if explicit_research:
        research_requirements = explicit_research
        research_authority = 'HOST_AGENT_AUTHORED'
    elif request_research:
        research_requirements = request_research
        research_authority = 'USER_OR_CALLER_SUPPLIED'
    else:
        research_requirements = _derive_research_requirements(request)
        research_authority = 'DECISION_GAP_FALLBACK'

    content_scope = dict(agent.get('content_scope') or {}) if isinstance(agent.get('content_scope'), Mapping) else {}
    creative_exploration = dict(agent.get('creative_exploration') or {}) if isinstance(agent.get('creative_exploration'), Mapping) else {}
    iteration_policy = dict(agent.get('iteration_policy') or {}) if isinstance(agent.get('iteration_policy'), Mapping) else {}

    stop_conditions = _strings(agent.get('research_stop_conditions')) or [
        'Stop when additional research is unlikely to change a material strategy, listing, asset, compliance or production decision.',
        'Stop when decision-critical claims and hard platform/compliance constraints have sufficient current evidence.',
        'Do not research for quota completion, source-count targets or cosmetic comprehensiveness.',
    ]

    return {
        'version': VERSION,
        'status': 'AGENT_AUTHORED' if agent else 'AUTONOMY_FALLBACK_READY',
        'authority_model': {
            'hard_constraints': [
                'PRODUCT_TRUTH_AND_SOURCE_LINEAGE',
                'EXPLICIT_USER_LOCKS',
                'CURRENT_PLATFORM_HARD_CONSTRAINTS',
                'LEGAL_COMPLIANCE_AND_CLAIM_EVIDENCE',
                'REAL_PRODUCT_PIXEL_OR_IDENTITY_LOCKS',
                'TARGET_OUTPUT_TECHNICAL_REQUIREMENTS',
            ],
            'agent_decisions': [
                'RESEARCH_SCOPE_AND_DEPTH',
                'RESEARCH_QUERY_AND_SOURCE_ROUTING',
                'CONTENT_AND_SURFACE_SCOPE',
                'ASSET_COUNT_AND_ASSET_ROLES',
                'CREATIVE_OPPORTUNITY_SEARCH',
                'DIRECTION_COUNT_AND_DIRECTION_CONTENT',
                'COMPOSITION_CAMERA_LIGHTING_CMF_WHEN_RELEVANT',
                'PRODUCTION_ROUTE',
                'ITERATION_DEPTH_AND_REPLAN',
            ],
            'heuristics_role': 'COMPATIBILITY_FALLBACK_ONLY',
        },
        'research': {
            'authority': research_authority,
            'requirements': research_requirements,
            'stop_conditions': stop_conditions,
            'fixed_source_count': None,
            'fixed_query_count': None,
            'fixed_competitor_count': None,
        },
        'content_scope': content_scope,
        'creative_exploration': creative_exploration,
        'iteration_policy': iteration_policy,
        'host_agent_trace': deepcopy(agent.get('decision_trace') or []),
        'principle': 'Freeze facts and boundaries; let the agent decide the path. Dynamic does not mean random: material decisions should preserve evidence → decision → implementation trace.',
    }


def research_requirements_from_plan(request: Mapping[str, Any], plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    research = plan.get('research') if isinstance(plan.get('research'), Mapping) else {}
    rows = _rows(research.get('requirements'))
    return rows if rows else _rows(request.get('research_requirements'))


def derive_content_families(
    request: Mapping[str, Any],
    plan: Mapping[str, Any],
    *,
    family_surface: Mapping[str, str | None],
    available_families: list[str],
) -> list[str]:
    """Select only families justified by the current task; never expand to a fixed all-family quota."""
    explicit = _strings(request.get('content_families'))
    if explicit:
        return list(dict.fromkeys(explicit))

    scope = plan.get('content_scope') if isinstance(plan.get('content_scope'), Mapping) else {}
    authored = _strings(scope.get('families') or scope.get('content_families'))
    if authored:
        return list(dict.fromkeys(authored))

    requested_surfaces = set(_strings((request.get('target') or {}).get('surfaces')))
    chosen: list[str] = []
    if requested_surfaces:
        for family in available_families:
            surface = family_surface.get(family)
            if surface and surface in requested_surfaces:
                chosen.append(family)

    for job in _rows(request.get('asset_jobs')):
        family = str(job.get('family') or '').strip()
        if family:
            chosen.append(family)

    signal_map = [
        ('VIDEO', bool(request.get('video_jobs'))),
        ('PAID', bool(request.get('paid_campaigns') or request.get('ad_rows') or request.get('ads'))),
        ('CX', bool(request.get('feedback_rows') or request.get('review_rows'))),
        ('MEASUREMENT', bool(request.get('experiment') or request.get('experiment_rows') or request.get('measurement_plan'))),
        ('COMPLIANCE', bool(request.get('claims') or request.get('compliance_requirements'))),
        ('VISUAL', bool(request.get('compile_assets') or request.get('source_product_assets') or request.get('creative_references'))),
    ]
    for family, active in signal_map:
        if active:
            chosen.append(family)

    target = request.get('target') or {}
    if not chosen and target.get('platform_family'):
        chosen.append('LISTING')

    allowed = set(available_families)
    return [family for family in dict.fromkeys(chosen) if family in allowed]


def agent_creative_opportunities(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    creative = plan.get('creative_exploration') if isinstance(plan.get('creative_exploration'), Mapping) else {}
    return _rows(creative.get('opportunities') or creative.get('mechanisms'))


def agent_creative_directions(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    creative = plan.get('creative_exploration') if isinstance(plan.get('creative_exploration'), Mapping) else {}
    return _rows(creative.get('directions'))
