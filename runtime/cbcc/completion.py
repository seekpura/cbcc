from __future__ import annotations

from typing import Any, Mapping


OPEN_GATE_STATUSES={'PENDING','HOLD','MISSING','INVALIDATED','BLOCKED','FAIL','RESEARCH_REQUIRED'}
OPEN_ITEM_STATUSES={'PENDING','HOLD','MISSING','INVALIDATED','BLOCKED','FAIL','REVIEW_REQUIRED','RESULT_REVIEW_REQUIRED'}
REQUIRED_REVIEW_KINDS={'CONTENT_OBJECT','ASSET_PACKAGE','PRODUCTION_OUTPUT','LOCAL_REVISION_OUTPUT'}
HARD_FRONTIER_ACTIONS={
    'AUTHOR_DECISION_OR_ASSET_SCOPE',
    'REPLAN_ASSET_ARCHITECTURE',
    'AUTHOR_OR_SELECT_CREATIVE_DIRECTION',
    'RESOLVE_COMPLIANCE_BOUNDARY',
    'PRODUCE_RESUME_OR_REPAIR',
}


def _pending(value: Any) -> bool:
    return str(value or 'PENDING').upper() not in {'RESOLVED','DONE','CLOSED','ACCEPTED','COMPLETE'}


def _gate_scope(state: Mapping[str,Any]) -> tuple[set[str],set[str]]:
    required=set(); blocking=set()
    for gate,rec in (state.get('gates') or {}).items():
        if rec.get('required_for_current_scope'):
            required.add(str(gate))
        if rec.get('blocking_for_current_scope'):
            blocking.add(str(gate))
    return required,blocking


def _action_blocks_current_scope(action: Mapping[str,Any], blocking_gates:set[str]) -> bool:
    if not _pending(action.get('status')):
        return False
    if action.get('blocking') is False:
        return False
    required_for={str(x) for x in (action.get('required_for') or []) if str(x)}
    canonical_hits=required_for & blocking_gates
    if canonical_hits:
        return True
    # If the action is explicitly routed only to canonical gates that are non-blocking/out of scope,
    # it is advisory for the current deliverable even when the underlying research row is globally "blocking".
    canonical_names={
        'EVIDENCE','PRODUCT_TRUTH','COMMERCE_ENTITY','TARGET_CONTEXT','CULTURE_CONTEXT','OFFER_ECONOMICS',
        'DECISION','PLATFORM_COMPILE','CONTENT_GRAPH','ASSET_ARCHITECTURE','CREATIVE','STRATEGY_AUTHORITY',
        'ASSET_COMPILE','EXECUTION','PRODUCTION','MEASUREMENT','LEARNING','AUDIT'
    }
    if required_for and required_for <= canonical_names:
        return False
    # Explicit `blocking=True` with no current canonical route remains conservative: the caller declared
    # that the unresolved fact is required, but did not provide enough routing metadata to safely downgrade it.
    return action.get('blocking') is True


def evaluate_scope_completion(
    state: Mapping[str,Any],
    items: list[Mapping[str,Any]],
    *,
    agent_next_action: Mapping[str,Any] | None=None,
) -> dict[str,Any]:
    """Derive completion from the current deliverable scope instead of a static pipeline flag.

    Canonical gates remain useful for lineage, but only current-scope blocking gates can block completion.
    Human review is required only for required addressable non-gate deliverables.  Advisory research and
    supporting objects stay visible without manufacturing unfinished work.
    """
    required_gates,blocking_gates=_gate_scope(state)
    gate_blockers=[]
    for gate in sorted(blocking_gates):
        rec=(state.get('gates') or {}).get(gate) or {}
        status=str(rec.get('status') or 'PENDING').upper()
        if status in OPEN_GATE_STATUSES:
            gate_blockers.append({'gate':gate,'status':status,'scope_reason':rec.get('scope_reason')})

    item_blockers=[]
    review_pending=[]
    for raw in items or []:
        item=dict(raw)
        if not item.get('required') or item.get('kind')=='AUTHORITY_GATE':
            continue
        iid=item.get('item_id')
        runtime_status=str(item.get('status') or '').upper()
        review_status=str(item.get('review_status') or 'PENDING_REVIEW').upper()
        if runtime_status in OPEN_ITEM_STATUSES:
            item_blockers.append({'item_id':iid,'kind':item.get('kind'),'status':runtime_status,'reason':'RUNTIME_NOT_READY'})
            continue
        if item.get('kind') in REQUIRED_REVIEW_KINDS and review_status!='ACCEPTED':
            review_pending.append({'item_id':iid,'kind':item.get('kind'),'review_status':review_status})

    blocking_actions=[]; advisory_actions=[]
    for raw in state.get('pending_actions') or []:
        if not isinstance(raw,Mapping) or not _pending(raw.get('status')):
            continue
        row=dict(raw)
        if _action_blocks_current_scope(row,blocking_gates):
            blocking_actions.append(row)
        else:
            advisory_actions.append(row)

    open_revisions=[]
    for raw in state.get('local_revision_requests') or []:
        if not isinstance(raw,Mapping):
            continue
        if str(raw.get('status') or 'OPEN').upper() not in {'ACCEPTED','RESOLVED','CLOSED','CANCELLED'}:
            open_revisions.append(dict(raw))

    frontier=[]; blocking_frontier=[]; advisory_frontier=[]
    agent=dict(agent_next_action or {})
    for raw in agent.get('frontier') or []:
        if not isinstance(raw,Mapping):
            continue
        row=dict(raw); frontier.append(row)
        action=str(row.get('action') or '')
        if action=='RESEARCH_OR_EVIDENCE_RESOLUTION':
            (blocking_frontier if blocking_actions else advisory_frontier).append(row)
        elif action in HARD_FRONTIER_ACTIONS:
            blocking_frontier.append(row)
        else:
            advisory_frontier.append(row)

    blocker_count=len(gate_blockers)+len(item_blockers)+len(review_pending)+len(blocking_actions)+len(open_revisions)+len(blocking_frontier)
    ready=blocker_count==0
    status='READY_CURRENT_SCOPE' if ready else 'CURRENT_SCOPE_OPEN'
    recommended=str(agent.get('recommended_next_action') or '')
    if ready and recommended.startswith('STOP_'):
        agent_alignment='ALIGNED_WITH_AGENT_STOP'
    elif ready and frontier:
        agent_alignment='READY_WITH_NONBLOCKING_AGENT_FRONTIER'
    elif ready:
        agent_alignment='READY_NO_AGENT_BLOCKER'
    elif recommended.startswith('STOP_'):
        agent_alignment='AGENT_STOP_CANNOT_OVERRIDE_CURRENT_SCOPE_BLOCKER'
    else:
        agent_alignment='OPEN_AND_AGENT_CONTINUES'

    return {
        'status':status,
        'final_ready':ready,
        'current_scope_required_gates':sorted(required_gates),
        'current_scope_blocking_gates':sorted(blocking_gates),
        'gate_blockers':gate_blockers,
        'item_blockers':item_blockers,
        'review_pending':review_pending,
        'blocking_actions':blocking_actions,
        'advisory_actions':advisory_actions,
        'open_revision_requests':open_revisions,
        'blocking_agent_frontier':blocking_frontier,
        'advisory_agent_frontier':advisory_frontier,
        'blocker_count':blocker_count,
        'agent_recommended_next_action':recommended or None,
        'agent_alignment':agent_alignment,
        'principle':'READY means the current requested scope is closed: no current-scope blocking gate, required deliverable runtime blocker, required human review, blocking action, open local revision or hard Agent frontier remains. Supporting/advisory work can remain visible without blocking.',
    }
