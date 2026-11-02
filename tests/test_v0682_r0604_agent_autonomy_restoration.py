from runtime.cbcc.agent_autonomy import compile_agent_autonomy_plan, research_requirements_from_plan
from runtime.cbcc.decision_authority import derive_task_content_families


def _request(agent_plan):
    return {
        'project_id': 'r0604-autonomy',
        'target': {
            'market': 'Malaysia',
            'jurisdiction': 'Malaysia',
            'platform_family': 'TIKTOK_SHOP',
            'site': 'MY',
            'surfaces': ['GALLERY'],
        },
        'agent_plan': agent_plan,
    }


def test_explicit_empty_agent_research_scope_is_not_repopulated_by_runtime():
    request = _request({'research_requirements': []})
    plan = compile_agent_autonomy_plan(request)

    assert plan['status'] == 'AGENT_AUTHORED'
    assert plan['research']['authority'] == 'HOST_AGENT_AUTHORED'
    assert plan['research']['requirements'] == []
    assert research_requirements_from_plan(request, plan) == []


def test_explicit_empty_caller_research_scope_is_not_repopulated_by_runtime():
    request = _request({})
    request['research_requirements'] = []
    plan = compile_agent_autonomy_plan(request)

    assert plan['research']['authority'] == 'USER_OR_CALLER_SUPPLIED'
    assert plan['research']['requirements'] == []
    assert research_requirements_from_plan(request, plan) == []


def test_missing_agent_research_scope_still_allows_decision_gap_fallback():
    request = _request({})
    plan = compile_agent_autonomy_plan(request)

    assert plan['research']['authority'] == 'DECISION_GAP_FALLBACK'
    assert plan['research']['requirements'], 'missing research scope may still use compatibility fallback'


def test_explicit_empty_agent_content_family_scope_remains_empty():
    request = _request({'content_scope': {'families': []}})
    plan = compile_agent_autonomy_plan(request)

    families = derive_task_content_families(
        request,
        plan,
        available_families=['LISTING', 'SEARCH', 'VISUAL', 'VIDEO'],
    )
    assert families == []
