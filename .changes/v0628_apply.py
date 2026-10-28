from pathlib import Path

# ---------------- agent_autonomy.py ----------------
p=Path('runtime/cbcc/agent_autonomy.py')
s=p.read_text(encoding='utf-8')
append=r'''

# v0.6.28 — current-scope frontier authority.
_compile_agent_next_action_v0627 = compile_agent_next_action


def _v0628_frontier_item_blocks(action:Mapping[str,Any], blocking_gates:set[str])->bool:
    if str(action.get('status') or 'PENDING').upper()=='RESOLVED':
        return False
    if action.get('blocking') is False:
        return False
    required_for={str(x) for x in (action.get('required_for') or []) if str(x)}
    if required_for & blocking_gates:
        return True
    canonical={
        'EVIDENCE','PRODUCT_TRUTH','COMMERCE_ENTITY','TARGET_CONTEXT','CULTURE_CONTEXT','OFFER_ECONOMICS',
        'DECISION','PLATFORM_COMPILE','CONTENT_GRAPH','ASSET_ARCHITECTURE','CREATIVE','STRATEGY_AUTHORITY',
        'ASSET_COMPILE','EXECUTION','PRODUCTION','MEASUREMENT','LEARNING','AUDIT'
    }
    if required_for and required_for <= canonical:
        return False
    return action.get('blocking') is True


def compile_agent_next_action(
    plan: Mapping[str, Any],
    *,
    request: Mapping[str, Any] | None = None,
    research_gate: Mapping[str, Any] | None = None,
    asset_architecture: Mapping[str, Any] | None = None,
    creative_council: Mapping[str, Any] | None = None,
    compliance: Mapping[str, Any] | None = None,
    production_run: Mapping[str, Any] | None = None,
    gate_scope: Mapping[str, Any] | None = None,
    content_requiredness: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile a blocking vs advisory frontier for the *current* requested scope.

    Advisory work remains discoverable without forcing another loop.  An Agent stop request cannot override
    current hard blockers such as required compliance, required asset decisions, or incomplete requested production.
    """
    request=request or {}; research_gate=research_gate or {}; asset_architecture=asset_architecture or {}
    creative_council=creative_council or {}; compliance=compliance or {}; production_run=production_run or {}
    gate_scope=gate_scope or {}; content_requiredness=content_requiredness or {}
    gate_rows=gate_scope.get('gates') if isinstance(gate_scope.get('gates'),Mapping) else {}
    blocking_gates={str(g) for g,m in gate_rows.items() if isinstance(m,Mapping) and m.get('blocking_for_current_scope')}
    required_families={str(x) for x in (content_requiredness.get('required_families') or [])}

    blocking_frontier=[]; advisory_frontier=[]
    unresolved_research=[row for row in (research_gate.get('actions') or []) if row.get('status')!='RESOLVED']
    blocking_research=[row for row in unresolved_research if _v0628_frontier_item_blocks(row,blocking_gates)]
    advisory_research=[row for row in unresolved_research if row not in blocking_research]
    if blocking_research:
        blocking_frontier.append({
            'action':'RESEARCH_OR_EVIDENCE_RESOLUTION',
            'reason':'Current-scope blocking evidence can still change a required deliverable or hard boundary.',
            'items':[row.get('action_id') for row in blocking_research],
            'blocking':True,
        })
    if advisory_research:
        advisory_frontier.append({
            'action':'OPTIONAL_RESEARCH_OR_EVIDENCE_REFRESH',
            'reason':'Additional evidence may improve confidence or a future scope, but is not required to close the current deliverable.',
            'items':[row.get('action_id') for row in advisory_research],
            'blocking':False,
        })

    coverage=asset_architecture.get('decision_coverage_summary') or {}
    uncovered=int(coverage.get('uncovered_atomic_jobs') or 0)
    if uncovered>0:
        row={'action':'REPLAN_ASSET_ARCHITECTURE','reason':'At least one atomic shopper decision is not covered by a dedicated or explicitly merged asset.','count':uncovered}
        (blocking_frontier if 'ASSET_ARCHITECTURE' in blocking_gates else advisory_frontier).append({**row,'blocking':'ASSET_ARCHITECTURE' in blocking_gates})

    assets=asset_architecture.get('assets') or []
    if assets and not creative_council.get('selected_direction'):
        row={'action':'AUTHOR_OR_SELECT_CREATIVE_DIRECTION','reason':'Assets exist but no creative direction has been selected for production.'}
        (blocking_frontier if 'CREATIVE' in blocking_gates else advisory_frontier).append({**row,'blocking':'CREATIVE' in blocking_gates})

    compliance_status=str(compliance.get('status') or '').upper()
    compliance_problem=compliance_status in {'HOLD','BLOCKED','FAIL','RESEARCH_REQUIRED'}
    compliance_required=('COMPLIANCE' in required_families) or bool({'ASSET_COMPILE','EXECUTION','PRODUCTION'} & blocking_gates)
    if compliance_problem:
        row={'action':'RESOLVE_COMPLIANCE_BOUNDARY','reason':'A compliance/claim boundary remains unresolved.','status':compliance_status}
        (blocking_frontier if compliance_required else advisory_frontier).append({**row,'blocking':compliance_required})

    requested_production=bool(request.get('production_run'))
    production_status=str(production_run.get('status') or 'NOT_REQUESTED').upper()
    if requested_production and production_status not in {'COMPLETE','READY_REVIEW'}:
        row={'action':'PRODUCE_RESUME_OR_REPAIR','reason':'Production was requested and is not complete.','status':production_status}
        (blocking_frontier if 'PRODUCTION' in blocking_gates else advisory_frontier).append({**row,'blocking':'PRODUCTION' in blocking_gates})

    iteration_policy=plan.get('iteration_policy') if isinstance(plan.get('iteration_policy'),Mapping) else {}
    explicit_stop=bool(iteration_policy.get('stop'))
    if blocking_frontier:
        recommendation=str(iteration_policy.get('next_action') or blocking_frontier[0]['action'])
        if recommendation.startswith('STOP_'):
            recommendation=blocking_frontier[0]['action']
        status='ACTION_FRONTIER_OPEN'
    else:
        recommendation='STOP_BY_AGENT_DECISION' if explicit_stop else 'STOP_CURRENT_SCOPE_SATISFIED'
        status='CURRENT_SCOPE_SATISFIED'

    return {
        'version':'0.6.28-agent-frontier-scope',
        'status':status,
        'recommended_next_action':recommendation,
        'blocking_frontier':blocking_frontier,
        'advisory_frontier':advisory_frontier,
        'frontier':blocking_frontier+advisory_frontier,
        'blocking_frontier_count':len(blocking_frontier),
        'advisory_frontier_count':len(advisory_frontier),
        'agent_stop_requested':explicit_stop,
        'agent_stop_overridden_by_hard_blocker':bool(explicit_stop and blocking_frontier),
        'fixed_sequence':False,
        'agent_has_final_routing_authority':True,
        'hard_constraints_override_agent_stop':True,
        'stop_conditions':((plan.get('research') or {}).get('stop_conditions') if isinstance(plan.get('research'),Mapping) else []) or [],
        'principle':'Blocking frontier means the current requested scope cannot close safely/correctly. Advisory frontier is optional learning or future-scope improvement and must not force another loop. Continue only for material current-scope blockers.',
    }
'''
if '0.6.28 — current-scope frontier authority' not in s:
    s += append
p.write_text(s,encoding='utf-8')

# ---------------- decision_authority.py ----------------
p=Path('runtime/cbcc/decision_authority.py')
s=p.read_text(encoding='utf-8')
old="""    out = deepcopy(dict(next_action or {}))
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
"""
new="""    out = deepcopy(dict(next_action or {}))
    blocking = list(out.get('blocking_frontier') or [])
    advisory = list(out.get('advisory_frontier') or [])
    if not blocking and not advisory:
        # Backward-compatible input from older frontier shape.
        blocking = [dict(x) for x in (out.get('frontier') or []) if isinstance(x,Mapping) and x.get('blocking') is not False]
        advisory = [dict(x) for x in (out.get('frontier') or []) if isinstance(x,Mapping) and x.get('blocking') is False]
    for gap in question_authority.get('decision_gaps') or []:
        if not isinstance(gap, Mapping):
            continue
        blocking.insert(0, {
            'action':'AUTHOR_DECISION_OR_ASSET_SCOPE',
            'reason':gap.get('reason'),
            'code':gap.get('code'),
            'required_action':gap.get('required_action'),
            'blocking_scope':gap.get('blocking_scope') or [],
            'blocking':True,
        })
    out['blocking_frontier']=blocking
    out['advisory_frontier']=advisory
    out['frontier']=blocking+advisory
    out['blocking_frontier_count']=len(blocking)
    out['advisory_frontier_count']=len(advisory)
    if blocking:
        out['status']='ACTION_FRONTIER_OPEN'
        current=str(out.get('recommended_next_action') or '')
        if current.startswith('STOP_') or not current:
            out['recommended_next_action']=blocking[0]['action']
    else:
        out['status']='CURRENT_SCOPE_SATISFIED'
        out['recommended_next_action']='STOP_BY_AGENT_DECISION' if out.get('agent_stop_requested') else 'STOP_CURRENT_SCOPE_SATISFIED'
"""
if old not in s: raise SystemExit('decision authority frontier block missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# ---------------- completion.py ----------------
p=Path('runtime/cbcc/completion.py')
s=p.read_text(encoding='utf-8')
old="""    frontier=[]; blocking_frontier=[]; advisory_frontier=[]
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
"""
new="""    frontier=[]; blocking_frontier=[]; advisory_frontier=[]
    agent=dict(agent_next_action or {})
    if 'blocking_frontier' in agent or 'advisory_frontier' in agent:
        blocking_frontier=[dict(x) for x in (agent.get('blocking_frontier') or []) if isinstance(x,Mapping)]
        advisory_frontier=[dict(x) for x in (agent.get('advisory_frontier') or []) if isinstance(x,Mapping)]
        frontier=blocking_frontier+advisory_frontier
    else:
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
"""
if old not in s: raise SystemExit('completion frontier block missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# ---------------- compiler.py ----------------
p=Path('runtime/cbcc/compiler.py')
s=p.read_text(encoding='utf-8')
s=s.replace("st.data['runtime_version']='0.6.27-current-scope-completion'","st.data['runtime_version']='0.6.28-agent-frontier-scope'",1)
old="""    agent_next_action=compile_agent_next_action(
        agent_plan,request=request,research_gate=research_gate,asset_architecture=architecture,
        creative_council=council,compliance=compliance,production_run=production_run,
    )
"""
new="""    agent_next_action=compile_agent_next_action(
        agent_plan,request=request,research_gate=research_gate,asset_architecture=architecture,
        creative_council=council,compliance=compliance,production_run=production_run,
        gate_scope=gate_scope,content_requiredness=content_requiredness,
    )
"""
if old not in s: raise SystemExit('compiler agent next action call missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# ---------------- human_delivery.py ----------------
p=Path('runtime/cbcc/human_delivery.py')
s=p.read_text(encoding='utf-8')
old="""    frontier=list(next_action.get('frontier') or [])
    return {
        'listing_active':listing_active,
        'listing_submission_sensitive':submission_sensitive,
        'families':families,
        'frontier':frontier,
        'recommended_next_action':next_action.get('recommended_next_action'),
        'scope_status':next_action.get('status'),
"""
new="""    blocking_frontier=list(next_action.get('blocking_frontier') or [])
    advisory_frontier=list(next_action.get('advisory_frontier') or [])
    frontier=list(next_action.get('frontier') or (blocking_frontier+advisory_frontier))
    return {
        'listing_active':listing_active,
        'listing_submission_sensitive':submission_sensitive,
        'families':families,
        'frontier':frontier,
        'blocking_frontier':blocking_frontier,
        'advisory_frontier':advisory_frontier,
        'blocking_frontier_count':len(blocking_frontier),
        'advisory_frontier_count':len(advisory_frontier),
        'recommended_next_action':next_action.get('recommended_next_action'),
        'scope_status':next_action.get('status'),
"""
if old not in s: raise SystemExit('human delivery scope frontier block missing')
s=s.replace(old,new,1)
old="""    frontier=scope.get('frontier') or []
    if frontier:
        lines += ['## Agent 识别的高价值下一动作','']
        for item in frontier:
            lines.append(f"- **{item.get('action') or 'NEXT'}**：{item.get('reason') or '继续处理当前未解决条件。'}")
        lines.append('')
"""
new="""    blocking_frontier=scope.get('blocking_frontier') or []
    advisory_frontier=scope.get('advisory_frontier') or []
    if blocking_frontier:
        lines += ['## 当前范围必须先解决','']
        for item in blocking_frontier:
            lines.append(f"- **{item.get('action') or 'NEXT'}**：{item.get('reason') or '该条件会阻断当前范围完成。'}")
        lines.append('')
    if advisory_frontier:
        lines += ['## 可选后续优化 / 研究（不阻断当前完成）','']
        for item in advisory_frontier:
            lines.append(f"- **{item.get('action') or 'OPTIONAL'}**：{item.get('reason') or '可用于提高后续置信度或扩展范围。'}")
        lines.append('')
"""
if old not in s: raise SystemExit('human hub frontier block missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

print('v0.6.28 agent frontier scope patch applied')
