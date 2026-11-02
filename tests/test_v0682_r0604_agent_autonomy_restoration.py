from runtime.cbcc.agent_autonomy import (
    compile_agent_autonomy_plan,
    compile_agent_next_action,
    research_requirements_from_plan,
)
from runtime.cbcc.creative import compile_creative_council
from runtime.cbcc.decision_authority import derive_task_content_families
from runtime.cbcc.research import compile_research_gate


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


def _creative_council(directions):
    return compile_creative_council(
        directions,
        {},
        {'product': {'name': 'Demo'}},
        {},
        {},
        'GENERAL_COMMERCE',
        [],
        {
            'status': 'AGENT_AUTHORED_CREATIVE_OPPORTUNITY_UNIVERSE',
            'opportunity_count': 0,
            'opportunities': [],
        },
    )


def test_explicit_empty_agent_research_scope_is_not_repopulated_by_runtime():
    request = _request({'research_requirements': []})
    plan = compile_agent_autonomy_plan(request)

    assert plan['status'] == 'AGENT_AUTHORED'
    assert plan['research']['authority'] == 'HOST_AGENT_AUTHORED'
    assert plan['research']['requirements'] == []
    assert research_requirements_from_plan(request, plan) == []

    research_gate = compile_research_gate(research_requirements_from_plan(request, plan), [], None)
    assert research_gate['status'] == 'READY'
    assert research_gate['actions'] == []


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


def test_explicit_empty_creative_direction_scope_is_not_repopulated_by_runtime():
    council = _creative_council([])

    assert council['status'] == 'NO_DIRECTION_AVAILABLE'
    assert council['directions'] == []
    assert council['selected_direction'] is None

    plan = compile_agent_autonomy_plan(
        _request({'creative_exploration': {'directions': []}})
    )
    next_action = compile_agent_next_action(
        plan,
        request=_request({'creative_exploration': {'directions': []}}),
        asset_architecture={'assets': [{'asset_id': 'AST-1'}]},
        creative_council=council,
    )
    assert any(
        row.get('action') == 'AUTHOR_OR_SELECT_CREATIVE_DIRECTION'
        for row in next_action.get('frontier') or []
    )


def test_missing_creative_direction_scope_still_allows_compatibility_synthesis():
    council = _creative_council(None)

    assert council['status'] == 'SELECTED'
    assert council['directions']
    assert council['selected_direction']
