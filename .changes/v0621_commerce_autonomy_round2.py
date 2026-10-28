from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'missing patch target: {label}')
    return text.replace(old, new, 1)


# Agent plan: add optional strategy framework selection + next-action frontier.
p = Path('runtime/cbcc/agent_autonomy.py')
text = p.read_text(encoding='utf-8')
text = replace_once(
    text,
    "    iteration_policy = dict(agent.get('iteration_policy') or {}) if isinstance(agent.get('iteration_policy'), Mapping) else {}\n\n    stop_conditions = _strings(agent.get('research_stop_conditions')) or [\n",
    "    iteration_policy = dict(agent.get('iteration_policy') or {}) if isinstance(agent.get('iteration_policy'), Mapping) else {}\n    strategy_frameworks = deepcopy(agent.get('strategy_frameworks') if agent.get('strategy_frameworks') is not None else (request.get('marketing_frameworks') if request.get('marketing_frameworks') is not None else request.get('persuasion_frameworks')))\n\n    stop_conditions = _strings(agent.get('research_stop_conditions')) or [\n",
    'agent plan strategy frameworks',
)
text = replace_once(
    text,
    "        'creative_exploration': creative_exploration,\n        'iteration_policy': iteration_policy,\n",
    "        'creative_exploration': creative_exploration,\n        'strategy_frameworks': strategy_frameworks,\n        'iteration_policy': iteration_policy,\n",
    'agent plan framework field',
)
append = r'''


def compile_agent_next_action(
    plan: Mapping[str, Any],
    *,
    request: Mapping[str, Any] | None = None,
    research_gate: Mapping[str, Any] | None = None,
    asset_architecture: Mapping[str, Any] | None = None,
    creative_council: Mapping[str, Any] | None = None,
    compliance: Mapping[str, Any] | None = None,
    production_run: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Expose a decision frontier for the host Agent instead of ending after one compile pass.

    This is not a fixed workflow. It reports unresolved material conditions and lets the host Agent choose
    the next useful action or stop when the current goal is satisfied.
    """
    request = request or {}
    research_gate = research_gate or {}
    asset_architecture = asset_architecture or {}
    creative_council = creative_council or {}
    compliance = compliance or {}
    production_run = production_run or {}

    frontier: list[dict[str, Any]] = []
    unresolved_research = [row for row in (research_gate.get('actions') or []) if row.get('status') != 'RESOLVED']
    if unresolved_research:
        frontier.append({
            'action':'RESEARCH_OR_EVIDENCE_RESOLUTION',
            'reason':'Current evidence gaps can still change one or more material decisions.',
            'items':[row.get('action_id') for row in unresolved_research],
            'agent_may_skip_when':'The host Agent determines the unresolved evidence cannot change the requested current-scope deliverable.',
        })

    coverage = asset_architecture.get('decision_coverage_summary') or {}
    if int(coverage.get('uncovered_atomic_jobs') or 0) > 0:
        frontier.append({
            'action':'REPLAN_ASSET_ARCHITECTURE',
            'reason':'At least one atomic shopper decision is not covered by a dedicated or explicitly merged asset.',
            'count':int(coverage.get('uncovered_atomic_jobs') or 0),
        })

    assets = asset_architecture.get('assets') or []
    if assets and not creative_council.get('selected_direction'):
        frontier.append({
            'action':'AUTHOR_OR_SELECT_CREATIVE_DIRECTION',
            'reason':'Assets exist but no creative direction has been selected for production.',
        })

    compliance_status = str(compliance.get('status') or '').upper()
    if compliance_status in {'HOLD','BLOCKED','FAIL','RESEARCH_REQUIRED'}:
        frontier.append({
            'action':'RESOLVE_COMPLIANCE_BOUNDARY',
            'reason':'A current compliance/claim boundary can block publication or production.',
            'status':compliance_status,
        })

    requested_production = bool(request.get('production_run'))
    production_status = str(production_run.get('status') or 'NOT_REQUESTED').upper()
    if requested_production and production_status not in {'COMPLETE','READY_REVIEW'}:
        frontier.append({
            'action':'PRODUCE_RESUME_OR_REPAIR',
            'reason':'Production was requested and is not complete.',
            'status':production_status,
        })

    iteration_policy = plan.get('iteration_policy') if isinstance(plan.get('iteration_policy'), Mapping) else {}
    explicit_stop = bool(iteration_policy.get('stop'))
    if explicit_stop:
        recommendation = 'STOP_BY_AGENT_DECISION'
    elif frontier:
        recommendation = str((iteration_policy.get('next_action') or frontier[0]['action']))
    else:
        recommendation = 'STOP_CURRENT_SCOPE_SATISFIED'

    return {
        'version': VERSION,
        'status':'ACTION_FRONTIER_OPEN' if frontier and not explicit_stop else 'CURRENT_SCOPE_SATISFIED',
        'recommended_next_action':recommendation,
        'frontier':frontier,
        'fixed_sequence':False,
        'agent_has_final_routing_authority':True,
        'stop_conditions':((plan.get('research') or {}).get('stop_conditions') if isinstance(plan.get('research'), Mapping) else []) or [],
        'principle':'Continue only while another action can materially improve correctness, commercial usefulness or execution readiness. Do not loop for quota completion.',
    }
'''
if 'def compile_agent_next_action(' not in text:
    text += append
p.write_text(text, encoding='utf-8')


# Optional persuasion frameworks: no automatic AIDA/FABE/4P bundle.
p = Path('runtime/cbcc/decision.py')
text = p.read_text(encoding='utf-8')
text = replace_once(
    text,
    "    requested=requested or ['AIDA','FABE','4P']\n    qs=[q for q in shopper_questions if str(q).strip()]\n    out={'status':'COMPILED','frameworks':{},'principle':'Frameworks annotate shopper decisions; they do not determine a fixed asset sequence.'}\n",
    "    requested=[] if requested is None else list(requested)\n    qs=[q for q in shopper_questions if str(q).strip()]\n    out={'status':'COMPILED' if requested else 'NOT_REQUESTED','frameworks':{},'requested':requested,'principle':'Frameworks are optional reasoning tools. Apply only frameworks the user/Agent selected because they change a concrete decision; they never determine a fixed asset sequence.'}\n",
    'decision optional persuasion frameworks',
)
p.write_text(text, encoding='utf-8')


# Strategy authority: make frameworks and execution narrative optional/task-derived.
p = Path('runtime/cbcc/strategy_authority.py')
text = p.read_text(encoding='utf-8')
text = text.replace('    for x in secondary[:3]:\n', '    for x in secondary:\n', 1)
text = text.replace('    for x in trust[:2] + objections[:2]:\n', '    for x in trust + objections:\n', 1)
text = text.replace("                'market_signal': price_signals[:2],\n                'configuration_signal': config[:3],\n", "                'market_signal': price_signals,\n                'configuration_signal': config,\n", 1)
text = text.replace("        'opportunity_signals': {'price_valleys': price_signals, 'configurations': config[:5]},\n", "        'opportunity_signals': {'price_valleys': price_signals, 'configurations': config},\n", 1)

start = text.index('def build_marketing_frameworks(')
end = text.index('\ndef build_culture_insights', start)
replacement = '''def build_marketing_frameworks(positioning: dict[str, Any], questions: list[str], target: dict[str, Any], framework_plan: Any = None) -> dict[str, Any]:\n    """Apply only decision frameworks selected by the user/host Agent. No framework bundle is mandatory."""\n    custom = {}\n    if isinstance(framework_plan, dict):\n        requested = framework_plan.get('frameworks') or framework_plan.get('requested') or []\n        custom = framework_plan.get('custom') or {}\n    else:\n        requested = framework_plan or []\n    if not isinstance(requested, (list, tuple, set, frozenset)):\n        requested = [requested]\n    requested = [str(x).upper() for x in requested if str(x or '').strip()]\n    out: dict[str, Any] = {\n        'status':'FRAMEWORKS_APPLIED' if requested or custom else 'NO_FRAMEWORK_REQUIRED',\n        'applied_frameworks':requested,\n        'why':'Frameworks are optional lenses. The Agent selects them only when they change a concrete commerce decision; Product Truth, evidence and shopper decisions remain the authority.',\n    }\n    if 'STP' in requested:\n        out['STP']={\n            'segmentation_basis':'Use only evidence-backed segmentation variables relevant to this decision.',\n            'targeting':'Prioritize the segment whose job/barrier aligns most strongly with product truth and offer.',\n            'positioning':positioning.get('positioning_statement'),\n        }\n    if 'JTBD' in requested:\n        out['JTBD']={'shopper_questions':questions,'job_statement':'Help the shopper make the next purchase decision with the minimum necessary information and proof.'}\n    if '4P' in requested:\n        out['4P']={\n            'product':'Express real product value and SKU role.',\n            'price':'Use economics + market context; do not choose price from competitor averaging alone.',\n            'place':target.get('platform_family'),\n            'promotion':'Let the current decision architecture determine message sequence and channel use.',\n        }\n    if 'FUNNEL' in requested:\n        out['funnel']={'rule':'Derive stages from the observed buyer journey and current decision barriers; do not force a universal stage list.'}\n    if 'RACE' in requested:\n        out['RACE']=[\n            {'stage':'RESEARCH','objective':'Resolve evidence gaps that can materially change current commerce decisions.','key_actions':'agent-selected research','output':'evidence + decision updates','platform':target.get('platform_family'),'kpi':'decision-changing evidence / unresolved material risk','why':'Research exists to change or validate decisions, not to complete a checklist.'},\n            {'stage':'ACTION','objective':'Convert sufficient evidence into product/offer/content/creative/production choices.','key_actions':'agent-selected decision work','output':'strategy and execution contracts','platform':target.get('platform_family'),'kpi':'decision coverage / execution readiness','why':'Action is whatever decision work is needed for the current goal.'},\n            {'stage':'COMMUNICATION','objective':'Execute only the surfaces and messages selected for the current buyer journey.','key_actions':'agent-selected surfaces/assets','output':'customer-facing communication','platform':target.get('platform_family'),'kpi':'surface-appropriate outcome metric','why':'Communication follows the actual asset architecture, not a channel quota.'},\n            {'stage':'EVALUATION','objective':'Use observed outcomes to decide whether to stop, locally revise or replan.','key_actions':'measurement / feedback / revision routing','output':'learning + next action','platform':target.get('platform_family'),'kpi':'material learning / incremental outcome','why':'Evaluation closes the loop only where new evidence can improve the result.'},\n        ]\n    if isinstance(custom, dict):\n        out['custom']=custom\n    return out\n\n'''
text = text[:start] + replacement + text[end+1:]

text = replace_once(
    text,
    "    marketing = build_marketing_frameworks(positioning, questions, request.get('target') or {})\n",
    "    agent_plan=request.get('_agent_autonomy_plan') or {}\n    framework_plan=(agent_plan.get('strategy_frameworks') if isinstance(agent_plan,dict) else None)\n    if framework_plan is None: framework_plan=request.get('marketing_frameworks') or request.get('persuasion_frameworks')\n    marketing = build_marketing_frameworks(positioning, questions, request.get('target') or {}, framework_plan)\n",
    'strategy agent framework plan',
)
text = replace_once(
    text,
    "        '07_race_execution_table': marketing['RACE'],\n",
    "        '07_race_execution_table': marketing.get('RACE', []),\n",
    'strategy optional RACE section',
)
text = replace_once(
    text,
    "                  'script_structure': '钩子 → 核心价值/证据 → 适配或异议消解 → CTA；按Surface和资产类型调整节奏。',\n",
    "                  'script_structure': a.get('script_structure') or a.get('narrative_structure') or '由当前资产的消费者问题、证据关系、Surface与交互任务动态决定；不套固定钩子/证据/CTA顺序。',\n",
    'strategy dynamic script structure',
)
text = replace_once(
    text,
    "                  'race_stage': 'COMMUNICATION',\n",
    "                  'race_stage': a.get('race_stage'),\n",
    'strategy no forced RACE stage',
)
p.write_text(text, encoding='utf-8')


# Compiler: persist next-action frontier after the current pass.
p = Path('runtime/cbcc/compiler.py')
text = p.read_text(encoding='utf-8')
text = replace_once(
    text,
    "    agent_creative_opportunities, agent_creative_directions,\n)",
    "    agent_creative_opportunities, agent_creative_directions, compile_agent_next_action,\n)",
    'compiler import next action',
)
marker = "    else:\n        st.set_gate('PRODUCTION','PENDING',[],production_run)\n    def _capability_row(name,input_active,input_status,consumers,downstream_ok=True):\n"
insert = "    else:\n        st.set_gate('PRODUCTION','PENDING',[],production_run)\n\n    agent_next_action=compile_agent_next_action(\n        agent_plan,request=request,research_gate=research_gate,asset_architecture=architecture,\n        creative_council=council,compliance=compliance,production_run=production_run,\n    )\n    _write(p/'artifacts/agent_next_action.json',agent_next_action)\n\n    def _capability_row(name,input_active,input_status,consumers,downstream_ok=True):\n"
text = replace_once(text, marker, insert, 'compiler persist next action')
p.write_text(text, encoding='utf-8')
