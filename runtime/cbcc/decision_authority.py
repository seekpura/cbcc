from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


ASSET_FAMILIES = {
    'VISUAL','RICH_CONTENT','VIDEO','CREATOR_AFFILIATE','LIVE','PAID','SOCIAL','STORE','CX','LIFECYCLE'
}


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple, set, frozenset)):
        value = [value]
    out: list[str] = []
    for item in value:
        text = str(item or '').strip()
        if text and text not in out:
            out.append(text)
    return out


def _rows(value: Any) -> list[dict[str, Any]]:
    return [dict(row) for row in (value or []) if isinstance(row, Mapping)]


def _norm(text: Any) -> str:
    return ' '.join(str(text or '').casefold().split())


def _scope(plan: Mapping[str, Any]) -> dict[str, Any]:
    raw = plan.get('content_scope') if isinstance(plan, Mapping) else None
    return dict(raw) if isinstance(raw, Mapping) else {}


def derive_task_content_families(
    request: Mapping[str, Any],
    plan: Mapping[str, Any],
    *,
    available_families: list[str],
) -> list[str]:
    """Derive current content families from authored tasks/signals, never from platform presence alone.

    Target surfaces constrain execution after a family exists; they do not manufacture every family that can live
    on that surface. An explicit empty content-family list is respected as an intentional empty scope.
    """
    allowed = set(available_families)

    if 'content_families' in request:
        return [x for x in _strings(request.get('content_families')) if x in allowed]

    scope = _scope(plan)
    for key in ('families', 'content_families'):
        if key in scope:
            return [x for x in _strings(scope.get(key)) if x in allowed]

    chosen: list[str] = []

    for job in _rows(request.get('asset_jobs')):
        family = str(job.get('family') or '').strip()
        if family:
            chosen.append(family)

    if request.get('listing_input'):
        chosen.append('LISTING')
    if request.get('video_jobs'):
        chosen.append('VIDEO')
    if request.get('paid_campaigns') or request.get('ad_rows') or request.get('ads'):
        chosen.append('PAID')
    if request.get('feedback_rows') or request.get('review_rows'):
        chosen.append('CX')
    if request.get('experiment') or request.get('experiment_rows') or request.get('measurement_plan'):
        chosen.append('MEASUREMENT')
    if request.get('claims') or request.get('compliance_requirements'):
        chosen.append('COMPLIANCE')
    if any(request.get(k) for k in ('source_product_assets','creative_references','creative_directions','photography_contract','visual_strategy','cmf')):
        chosen.append('VISUAL')

    authored_questions = bool(
        request.get('shopper_questions')
        or scope.get('decision_questions')
        or scope.get('shopper_questions')
        or any((row.get('consumer_question') or row.get('shopper_question') or row.get('question')) for row in _rows(request.get('asset_jobs')))
        or any((row.get('consumer_question') or row.get('shopper_question') or row.get('question')) for row in _rows(request.get('video_jobs')))
    )
    if (request.get('compile_assets') or request.get('production_run')) and authored_questions:
        # Surface is only an execution constraint after a real decision scope exists.  It never creates
        # Listing/Search/Offer work by itself, but it may select the concrete asset family needed to
        # answer an already-authored shopper question.
        surface_asset_family = {
            'GALLERY':'VISUAL', 'LONGFORM':'RICH_CONTENT', 'PDP_VIDEO':'VIDEO',
            'CREATOR':'CREATOR_AFFILIATE', 'LIVE':'LIVE', 'PAID_AD':'PAID',
            'SOCIAL_CONTENT':'SOCIAL', 'STORE_BANNER':'STORE', 'FAQ':'CX', 'CRM':'LIFECYCLE',
        }
        for surface in _strings((request.get('target') or {}).get('surfaces')):
            family = surface_asset_family.get(surface)
            if family:
                chosen.append(family)

    return [family for family in dict.fromkeys(chosen) if family in allowed]


_FRAMEWORK_ALIASES = {
    'RACE':'RACE', 'STP':'STP', 'JTBD':'JTBD', 'STP_JTBD':'STP_JTBD',
    '4P':'4P', 'FUNNEL':'Funnel', 'AIDA':'AIDA', 'FABE':'FABE', 'FOGG':'Fogg',
    'MEANS_END':'Means_End', 'MEANS-END':'Means_End', 'SIGNALING':'Signaling',
    'FIRST':'FIRST_Hero_Gate', 'FIRST_HERO_GATE':'FIRST_Hero_Gate',
    'COGNITIVE_BUDGET':'Cognitive_Budget', 'BELIEF_SEQUENCE':'Belief_Sequence',
    'COMMERCE_RESPONSE_LADDER':'Commerce_Response_Ladder',
}


def _framework_values(raw: Any) -> list[Any]:
    if raw is None:
        return []
    if isinstance(raw, str):
        import re
        return [x.strip() for x in re.split(r'[,/|]+', raw) if x.strip()]
    if isinstance(raw, Mapping):
        if isinstance(raw.get('selected'), list):
            return list(raw.get('selected') or [])
        if isinstance(raw.get('frameworks'), list):
            return list(raw.get('frameworks') or [])
        return [k for k, v in raw.items() if v not in (False, None, '', [], {})]
    if isinstance(raw, (list, tuple, set, frozenset)):
        return list(raw)
    return [raw]


def selected_decision_frameworks(request: Mapping[str, Any], plan: Mapping[str, Any]) -> list[str]:
    """Return only explicitly selected decision lenses. Runtime capability is never treated as project scope."""
    if 'decision_frameworks' in request:
        raw = request.get('decision_frameworks')
    else:
        raw = plan.get('strategy_frameworks') if isinstance(plan, Mapping) else None
    out: list[str] = []
    for value in _framework_values(raw):
        text = str(value or '').strip()
        if not text:
            continue
        key = text.upper().replace(' ', '_')
        name = _FRAMEWORK_ALIASES.get(key, text)
        if name not in out:
            out.append(name)
    return out


def compile_decision_question_authority(
    request: Mapping[str, Any],
    plan: Mapping[str, Any],
    *,
    listing: Mapping[str, Any] | None = None,
    active_families: list[str] | None = None,
) -> dict[str, Any]:
    """Compile only decision questions that are authored or grounded in a concrete current-scope signal.

    There is intentionally no generic four-question fallback. Product/market/platform context can inform a question,
    but context alone is not a license for Runtime to invent a mandatory buyer journey.
    """
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(value: Any, *, origin: str, source: Any = None, defaults: Mapping[str, Any] | None = None) -> None:
        defaults = dict(defaults or {})
        if isinstance(value, Mapping):
            row = dict(value)
            question = row.get('question') or row.get('shopper_question') or row.get('consumer_question')
        else:
            row = {}
            question = value
        question = ' '.join(str(question or '').split())
        key = _norm(question)
        if not key or key in seen:
            return
        seen.add(key)
        merged = {
            'question': question,
            'origin': origin,
            'source': deepcopy(source),
            'decision_job': row.get('decision_job') or defaults.get('decision_job') or 'RESOLVE_AUTHORED_DECISION',
            'surface': row.get('surface') or defaults.get('surface'),
            'family': row.get('family') or defaults.get('family'),
            'race_stage': row.get('race_stage') or defaults.get('race_stage'),
            'decision_intent': row.get('decision_intent') or defaults.get('decision_intent'),
            'evidence_ids': list(row.get('evidence_ids') or row.get('source_ids') or defaults.get('evidence_ids') or []),
        }
        rows.append(merged)

    for value in request.get('shopper_questions') or []:
        add(value, origin='USER_OR_CALLER_SUPPLIED')

    scope = _scope(plan)
    authored_questions = None
    for key in ('decision_questions', 'shopper_questions'):
        if key in scope:
            authored_questions = scope.get(key)
            break
    if authored_questions is not None:
        for value in authored_questions or []:
            add(value, origin='HOST_AGENT_AUTHORED')

    for trace in _rows(plan.get('host_agent_trace') if isinstance(plan, Mapping) else None):
        add(trace, origin='HOST_AGENT_DECISION_TRACE')

    for job in _rows(request.get('asset_jobs')):
        add(job, origin='EXPLICIT_ASSET_JOB', source=job, defaults={'family': job.get('family'), 'surface': job.get('surface')})
    for job in _rows(request.get('video_jobs')):
        add(job, origin='EXPLICIT_VIDEO_JOB', source=job, defaults={'family': 'VIDEO', 'surface': job.get('surface') or 'PDP_VIDEO'})

    compiled_listing = dict(listing or {})
    families = set(active_families or [])
    if 'LISTING' in families or 'CX' in families:
        for objection in compiled_listing.get('objection_resolution_plan') or []:
            if not isinstance(objection, Mapping):
                continue
            question = objection.get('question') or objection.get('objection')
            add(
                question,
                origin='CURRENT_LISTING_OBJECTION',
                source=objection,
                defaults={
                    'family': 'LISTING',
                    'decision_job': 'RESOLVE_CURRENT_LISTING_OBJECTION',
                    'decision_intent': objection.get('decision_intent'),
                },
            )

    asset_scope_requested = bool(
        set(active_families or []) & ASSET_FAMILIES
        or request.get('asset_jobs')
        or request.get('video_jobs')
        or request.get('compile_assets')
        or request.get('production_run')
    )
    decision_gaps: list[dict[str, Any]] = []
    if asset_scope_requested and not rows:
        decision_gaps.append({
            'code':'ASSET_DECISION_SCOPE_NOT_AUTHORED',
            'reason':'The current request asks for asset/production work but supplies no shopper decision question or explicit asset decision job.',
            'required_action':'Agent/user should author the decision job or asset role before asset generation; Runtime must not invent a generic four-question funnel.',
            'blocking_scope':['ASSET_ARCHITECTURE','ASSET_COMPILE','PRODUCTION'],
        })

    research_gaps = []
    for item in ((plan.get('research') or {}).get('requirements') if isinstance(plan, Mapping) and isinstance(plan.get('research'), Mapping) else []) or []:
        if isinstance(item, Mapping):
            research_gaps.append({
                'id':item.get('id'), 'topic':item.get('topic'), 'reason':item.get('reason'),
                'required_for':item.get('required_for') or [], 'blocking':bool(item.get('blocking')),
            })

    return {
        'status':'DECISION_QUESTIONS_COMPILED' if rows else 'NO_SHOPPER_QUESTION_AUTHORED',
        'authority':'EXPLICIT_OR_CURRENT_SIGNAL_ONLY',
        'rows':rows,
        'shopper_questions':[row['question'] for row in rows],
        'question_count':len(rows),
        'decision_gaps':decision_gaps,
        'research_decision_gaps':research_gaps,
        'active_families':list(active_families or []),
        'fixed_question_quota':False,
        'synthetic_default_questions':False,
        'commerce_goal_context':request.get('commerce_goal') or request.get('project_goal') or request.get('goal') or request.get('objective'),
        'principle':'Questions may be empty. Product Truth, target platform and runtime capabilities are context, not permission to manufacture a mandatory buyer journey.',
    }


def compile_decision_trace_rows(question_authority: Mapping[str, Any], selected_frameworks: list[str]) -> list[dict[str, Any]]:
    """Preserve authored questions without assigning journey/RACE stages by list index."""
    race_selected = 'RACE' in selected_frameworks
    out: list[dict[str, Any]] = []
    for row in question_authority.get('rows') or []:
        if not isinstance(row, Mapping):
            continue
        out.append({
            'race_stage': row.get('race_stage') if race_selected else None,
            'shopper_question': row.get('question'),
            'decision_job': row.get('decision_job') or 'RESOLVE_AUTHORED_DECISION',
            'evidence_ids': list(row.get('evidence_ids') or []),
            'framework_signals': {'selected_frameworks': list(selected_frameworks)},
            'rationale':'Question/stage comes from current authored or grounded scope. No stage is assigned from question position and no framework is implied by runtime capability.',
            'origin': row.get('origin'),
            'surface': row.get('surface'),
            'family': row.get('family'),
        })
    return out


def augment_agent_next_action(
    next_action: Mapping[str, Any],
    question_authority: Mapping[str, Any],
) -> dict[str, Any]:
    """Expose unresolved decision-scope gaps to the Agent instead of silently inventing questions/assets."""
    out = deepcopy(dict(next_action or {}))
    frontier = list(out.get('frontier') or [])
    for gap in question_authority.get('decision_gaps') or []:
        if not isinstance(gap, Mapping):
            continue
        frontier.insert(0, {
            'action':'AUTHOR_DECISION_OR_ASSET_SCOPE',
            'reason':gap.get('reason'),
            'code':gap.get('code'),
            'required_action':gap.get('required_action'),
            'blocking_scope':gap.get('blocking_scope') or [],
        })
    if frontier:
        out['frontier'] = frontier
        out['status'] = 'ACTION_FRONTIER_OPEN'
        current = str(out.get('recommended_next_action') or '')
        if current.startswith('STOP_') or not current:
            out['recommended_next_action'] = frontier[0]['action']
    out['decision_question_authority'] = {
        'status':question_authority.get('status'),
        'question_count':question_authority.get('question_count', 0),
        'decision_gap_count':len(question_authority.get('decision_gaps') or []),
        'synthetic_default_questions':False,
    }
    return out
