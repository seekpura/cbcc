from __future__ import annotations

from typing import Any, Mapping

from .dependencies import CANONICAL_GATES


ASSET_FAMILIES={'VISUAL','RICH_CONTENT','VIDEO','CREATOR_AFFILIATE','LIVE','PAID','SOCIAL','STORE','CX','LIFECYCLE'}


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value,(list,tuple,set,frozenset)):
        value=[value]
    out=[]
    for item in value:
        text=str(item or '').strip()
        if text and text not in out:
            out.append(text)
    return out


def _scope(plan: Mapping[str,Any] | None) -> dict[str,Any]:
    raw=(plan or {}).get('content_scope')
    return dict(raw) if isinstance(raw,Mapping) else {}


def compile_required_content_families(
    request: Mapping[str,Any],
    agent_plan: Mapping[str,Any] | None,
    active_families: list[str],
    question_authority: Mapping[str,Any] | None=None,
) -> dict[str,Any]:
    """Separate active/preserved content capability from current deliverable requiredness.

    A family may be active because data exists (for example Listing input or Claims) while still being a supporting
    authority rather than a user-facing deliverable in the current task.  Requiredness therefore needs its own
    contract instead of inheriting `family exists => required=True`.
    """
    active=list(dict.fromkeys(active_families or []))
    scope=_scope(agent_plan)
    explicit_required=[]
    explicit_optional=set(_strings(scope.get('optional_families') or scope.get('supporting_families')))

    if 'required_families' in scope:
        explicit_required.extend(_strings(scope.get('required_families')))
    elif 'families' in scope or 'content_families' in scope:
        explicit_required.extend(_strings(scope.get('families') or scope.get('content_families')))
    elif 'content_families' in request:
        explicit_required.extend(_strings(request.get('content_families')))

    reasons: dict[str,list[str]]={family:[] for family in active}
    required=set()
    for family in explicit_required:
        if family in active and family not in explicit_optional:
            required.add(family); reasons.setdefault(family,[]).append('EXPLICIT_CURRENT_DELIVERABLE_FAMILY')

    for job in request.get('asset_jobs') or []:
        if isinstance(job,Mapping):
            family=str(job.get('family') or '').strip()
            if family in active:
                required.add(family); reasons.setdefault(family,[]).append('EXPLICIT_ASSET_JOB')
    if request.get('video_jobs') and 'VIDEO' in active:
        required.add('VIDEO'); reasons.setdefault('VIDEO',[]).append('EXPLICIT_VIDEO_JOB')
    if request.get('paid_campaigns') and 'PAID' in active:
        required.add('PAID'); reasons.setdefault('PAID',[]).append('EXPLICIT_PAID_CAMPAIGN')
    if request.get('measurement_plan') and 'MEASUREMENT' in active:
        required.add('MEASUREMENT'); reasons.setdefault('MEASUREMENT',[]).append('EXPLICIT_MEASUREMENT_DELIVERABLE')
    if request.get('compliance_requirements') and 'COMPLIANCE' in active:
        required.add('COMPLIANCE'); reasons.setdefault('COMPLIANCE',[]).append('EXPLICIT_COMPLIANCE_DELIVERABLE')

    questions=bool((question_authority or {}).get('shopper_questions'))
    production_intent=bool(request.get('compile_assets') or request.get('production_run'))
    if production_intent and questions:
        for family in active:
            if family in ASSET_FAMILIES and family not in explicit_optional:
                required.add(family); reasons.setdefault(family,[]).append('ASSET_PRODUCTION_SCOPE_WITH_AUTHORED_DECISION')

    rows=[]
    for family in active:
        is_required=family in required
        rows.append({
            'family':family,
            'active':True,
            'required_for_current_scope':is_required,
            'role':'CURRENT_DELIVERABLE' if is_required else 'SUPPORTING_AUTHORITY',
            'reasons':reasons.get(family) or ['ACTIVE_DATA_OR_CAPABILITY_NOT_CURRENT_DELIVERABLE'],
        })
    return {
        'status':'CONTENT_REQUIREDNESS_COMPILED',
        'active_families':active,
        'required_families':[x for x in active if x in required],
        'supporting_families':[x for x in active if x not in required],
        'rows':rows,
        'fixed_requiredness':False,
        'principle':'Content existence and current-deliverable requiredness are separate. Supporting data may remain in the graph without becoming review/readiness debt.',
    }


def compile_gate_scope(
    request: Mapping[str,Any],
    active_families: list[str],
    requiredness: Mapping[str,Any],
    question_authority: Mapping[str,Any] | None=None,
) -> dict[str,Any]:
    """Keep canonical gates for lineage while making requiredness/blocking current-scope aware."""
    active=set(active_families or [])
    required_families=set(requiredness.get('required_families') or [])
    questions=bool((question_authority or {}).get('shopper_questions'))
    decision_gaps=bool((question_authority or {}).get('decision_gaps'))
    compile_assets=bool(request.get('compile_assets'))
    production=bool(request.get('production_run'))
    measurement=bool(request.get('measurement_plan') or request.get('experiment') or request.get('ad_analysis') or request.get('feedback_rows'))
    learning=bool(request.get('learning_cycle') or request.get('learning_input') or request.get('apply_learning'))
    culture=bool(request.get('audience_culture'))
    economics=bool(request.get('offer_economics') or request.get('ad_analysis') or request.get('paid_campaigns'))
    content=bool(active)
    asset_scope=bool(required_families & ASSET_FAMILIES) or compile_assets or production
    creative=asset_scope or any(request.get(k) for k in ('creative_directions','creative_references','visual_strategy','photography_contract','cmf'))

    required={
        'EVIDENCE':True,
        'PRODUCT_TRUTH':True,
        'COMMERCE_ENTITY':True,
        'TARGET_CONTEXT':True,
        'CULTURE_CONTEXT':culture,
        'OFFER_ECONOMICS':economics,
        'DECISION':questions or decision_gaps,
        'PLATFORM_COMPILE':bool((request.get('target') or {}).get('platform_family')),
        'CONTENT_GRAPH':content,
        'ASSET_ARCHITECTURE':asset_scope,
        'CREATIVE':creative,
        'STRATEGY_AUTHORITY':True,
        'ASSET_COMPILE':compile_assets,
        'EXECUTION':compile_assets or production,
        'PRODUCTION':production,
        'MEASUREMENT':measurement,
        'LEARNING':learning,
        'AUDIT':False,
    }
    reasons={
        'EVIDENCE':'Project truth/evidence lineage is a core authority.',
        'PRODUCT_TRUTH':'Product Truth is a core hard boundary.',
        'COMMERCE_ENTITY':'Canonical product/SKU identity is core project context.',
        'TARGET_CONTEXT':'Market/platform/locale target is core project context.',
        'CULTURE_CONTEXT':'Required only when current task supplies or requests audience/culture evidence.',
        'OFFER_ECONOMICS':'Required only when current task includes economics, paid/offer decisions, or ad economics.',
        'DECISION':'Required only when current scope has authored shopper decisions or an unresolved decision-scope gap.',
        'PLATFORM_COMPILE':'Required as platform evidence context when a platform target exists; planning-only research gaps need not block strategy.',
        'CONTENT_GRAPH':'Required only when current task activates at least one content family.',
        'ASSET_ARCHITECTURE':'Required only for current asset/production scope.',
        'CREATIVE':'Required only for current creative/visual/asset scope.',
        'STRATEGY_AUTHORITY':'Strategy Authority remains the core commercial synthesis artifact.',
        'ASSET_COMPILE':'Required only when asset compilation is explicitly requested.',
        'EXECUTION':'Required only when compiled assets or production execution are requested.',
        'PRODUCTION':'Required only when production_run is explicitly requested.',
        'MEASUREMENT':'Required only when current task includes measurement/experiment/ads/feedback evaluation.',
        'LEARNING':'Required only when a learning/apply-learning cycle is requested.',
        'AUDIT':'Canonical audit gate is preserved for lineage but is not a default deliverable.',
    }
    rows={}
    for gate in CANONICAL_GATES:
        req=bool(required.get(gate,False))
        blocking=req
        if gate=='PLATFORM_COMPILE' and request.get('planning_only'):
            blocking=False
        rows[gate]={
            'required_for_current_scope':req,
            'blocking_for_current_scope':blocking,
            'scope_status':'REQUIRED' if req else 'NOT_IN_CURRENT_SCOPE',
            'scope_reason':reasons.get(gate,'Current task did not activate this canonical gate.'),
        }
    return {
        'status':'GATE_SCOPE_COMPILED',
        'gates':rows,
        'required_gates':[g for g in CANONICAL_GATES if rows[g]['required_for_current_scope']],
        'blocking_gates':[g for g in CANONICAL_GATES if rows[g]['blocking_for_current_scope']],
        'canonical_gates_preserved':list(CANONICAL_GATES),
        'fixed_gate_requiredness':False,
        'principle':'Canonical gates remain available for audit/dependency lineage. Only current-scope gates can create readiness debt; planning context may be required without being blocking.',
    }
