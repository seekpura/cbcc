from __future__ import annotations

from cbcc.agent_autonomy import compile_agent_autonomy_plan, compile_agent_next_action
from cbcc.decision import compile_persuasion_frameworks
from cbcc.strategy_authority import build_marketing_frameworks, build_platform_content_matrix


def test_persuasion_frameworks_are_not_auto_injected():
    out = compile_persuasion_frameworks(['Why buy this?'], {'name':'Demo'})
    assert out['status'] == 'NOT_REQUESTED'
    assert out['frameworks'] == {}
    assert out['requested'] == []


def test_marketing_frameworks_are_optional_and_agent_selected():
    none = build_marketing_frameworks({'positioning_statement':'Demo'}, ['Q'], {'platform_family':'TIKTOK_SHOP'}, None)
    assert none['status'] == 'NO_FRAMEWORK_REQUIRED'
    assert 'RACE' not in none
    assert 'STP' not in none

    race = build_marketing_frameworks({'positioning_statement':'Demo'}, ['Q'], {'platform_family':'TIKTOK_SHOP'}, ['RACE'])
    assert race['status'] == 'FRAMEWORKS_APPLIED'
    assert len(race['RACE']) == 4
    assert 'STP' not in race
    assert '4P' not in race


def test_agent_plan_can_choose_frameworks_without_runtime_expanding_them():
    plan = compile_agent_autonomy_plan({'agent_plan':{'strategy_frameworks':['JTBD']}})
    assert plan['strategy_frameworks'] == ['JTBD']
    out = build_marketing_frameworks({'positioning_statement':'Demo'}, ['Q1','Q2'], {}, plan['strategy_frameworks'])
    assert 'JTBD' in out
    assert 'RACE' not in out
    assert '4P' not in out


def test_content_matrix_does_not_force_fixed_hook_proof_cta_sequence_or_race_stage():
    assets = [{
        'asset_id':'A1','asset_type':'IMAGE','surface':'GALLERY','consumer_question':'How does it fit?',
        'script_structure':'Show the actual fit relation first, then the single boundary that matters.',
        'race_stage':None,
        'visible_copy':{},'reason_to_exist':'Resolve fit uncertainty',
    }]
    rows = build_platform_content_matrix(
        {'platform_family':'TIKTOK_SHOP','site':'MY'}, {}, ['How does it fit?'], {'assets':assets}, {'primary_conversion_proposition':'Demo'}
    )
    assert rows[0]['script_structure'].startswith('Show the actual fit relation')
    assert rows[0]['race_stage'] is None


def test_next_action_frontier_reports_material_gaps_without_fixed_sequence():
    plan = compile_agent_autonomy_plan({})
    out = compile_agent_next_action(
        plan,
        request={'production_run':True},
        research_gate={'actions':[{'action_id':'RA-1','status':'PENDING'}]},
        asset_architecture={'assets':[{'asset_id':'A1'}],'decision_coverage_summary':{'uncovered_atomic_jobs':1}},
        creative_council={'selected_direction':None},
        compliance={'status':'HOLD'},
        production_run={'status':'PENDING'},
    )
    actions = [row['action'] for row in out['frontier']]
    assert 'RESEARCH_OR_EVIDENCE_RESOLUTION' in actions
    assert 'REPLAN_ASSET_ARCHITECTURE' in actions
    assert 'AUTHOR_OR_SELECT_CREATIVE_DIRECTION' in actions
    assert 'RESOLVE_COMPLIANCE_BOUNDARY' in actions
    assert 'PRODUCE_RESUME_OR_REPAIR' in actions
    assert out['fixed_sequence'] is False
    assert out['agent_has_final_routing_authority'] is True


def test_next_action_can_stop_when_current_scope_is_satisfied():
    plan = compile_agent_autonomy_plan({'agent_plan':{'iteration_policy':{}}})
    out = compile_agent_next_action(
        plan,
        request={},
        research_gate={'actions':[]},
        asset_architecture={'assets':[],'decision_coverage_summary':{'uncovered_atomic_jobs':0}},
        creative_council={},
        compliance={'status':'PASS'},
        production_run={'status':'NOT_REQUESTED'},
    )
    assert out['status'] == 'CURRENT_SCOPE_SATISFIED'
    assert out['recommended_next_action'] == 'STOP_CURRENT_SCOPE_SATISFIED'
