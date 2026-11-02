from pathlib import Path

p = Path('runtime/cbcc/agent_autonomy.py')
s = p.read_text(encoding='utf-8')

old = """    explicit_research = _rows(agent.get('research_requirements') or agent.get('research_plan'))
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
"""
new = """    agent_research_present = 'research_requirements' in agent or 'research_plan' in agent
    request_research_present = 'research_requirements' in request
    if agent_research_present:
        raw_research = agent.get('research_requirements') if 'research_requirements' in agent else agent.get('research_plan')
        research_requirements = _rows(raw_research)
        research_authority = 'HOST_AGENT_AUTHORED'
    elif request_research_present:
        research_requirements = _rows(request.get('research_requirements'))
        research_authority = 'USER_OR_CALLER_SUPPLIED'
    else:
        research_requirements = _derive_research_requirements(request)
        research_authority = 'DECISION_GAP_FALLBACK'
"""
if s.count(old) != 1:
    raise SystemExit(f'expected research block once, found {s.count(old)}')
s = s.replace(old, new)

old2 = """def research_requirements_from_plan(request: Mapping[str, Any], plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    research = plan.get('research') if isinstance(plan.get('research'), Mapping) else {}
    rows = _rows(research.get('requirements'))
    return rows if rows else _rows(request.get('research_requirements'))
"""
new2 = """def research_requirements_from_plan(request: Mapping[str, Any], plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    research = plan.get('research') if isinstance(plan.get('research'), Mapping) else {}
    if 'requirements' in research:
        return _rows(research.get('requirements'))
    return _rows(request.get('research_requirements'))
"""
if s.count(old2) != 1:
    raise SystemExit(f'expected plan projection block once, found {s.count(old2)}')
s = s.replace(old2, new2)

p.write_text(s, encoding='utf-8')
