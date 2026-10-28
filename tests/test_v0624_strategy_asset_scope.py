from pathlib import Path
import json

from cbcc.asset_architecture import build_asset_architecture
from cbcc.strategy_depth import build_risk_priority_depth
from cbcc.compiler import build_project


def _pack(tmp_path):
    pack = tmp_path / 'packs'
    pack.mkdir(exist_ok=True)
    (pack / 'test.yaml').write_text(
        'pack_id: test\n'
        'platform_family: test_platform\n'
        'site: "*"\n'
        'status: TEST_FIXTURE_VERIFIED\n'
        'synthetic_for_test: true\n'
        'capabilities: [LISTING, SEARCH, VISUAL, VIDEO, PAID, MEASUREMENT, COMPLIANCE]\n'
        'surfaces: [PDP, GALLERY, PDP_VIDEO, PAID_AD]\n'
        'rule_atoms: []\n'
        'research_required_for: []\n',
        encoding='utf-8',
    )
    return pack


def _base_request(**extra):
    req = {
        'project_id': 'V0624',
        'planning_only': True,
        'product': {
            'name': 'Task Product',
            'category': 'general',
            'net_content': '30ml',
            'primary_conversion_proposition': 'Clear product value',
        },
        'sources': [{'source_id': 'SRC', 'kind': 'PRODUCT_TRUTH'}],
        'target': {
            'market': 'MY',
            'jurisdiction': 'MY',
            'platform_family': 'test_platform',
            'site': 'TEST',
            'primary_locale': 'en-MY',
            'visible_copy_locales': ['en-MY'],
            'surfaces': ['PDP'],
        },
        'content_families': ['LISTING'],
        'shopper_questions': ['What is it?', 'Why is it relevant?'],
    }
    req.update(extra)
    return req


def test_machine_strategy_stays_nine_sections_but_human_projection_is_task_scoped(tmp_path):
    p = tmp_path / 'proj'
    build_project(p, _base_request(), _pack(tmp_path))
    strategy = json.loads((p / 'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
    assert len(strategy['sections']) == 9
    hp = strategy['human_projection']
    assert hp['fixed_human_section_quota'] is False
    assert hp['mode'] == 'TASK_SCOPED'
    assert '07_race_execution_table' not in hp['active_sections']
    assert strategy['sections']['07_race_execution_table'] == []
    assert strategy['sections']['04_marketing_core_strategy']['frameworks']['status'] == 'NO_FRAMEWORK_REQUIRED'
    assert all('race_stage' not in row for row in strategy['sections']['06_platform_content_matrix'])
    md = (p / 'artifacts/strategy/MASTER_STRATEGY_CN.md').read_text(encoding='utf-8')
    assert '固定九段人类配额：无' in md
    assert 'RACE 执行（当前项目显式启用）' not in md
    assert '文化适配（当前任务相关）' not in md


def test_explicit_race_is_preserved_as_optional_framework(tmp_path):
    req = _base_request(agent_plan={'strategy_frameworks': ['RACE'], 'content_scope': {'families': ['LISTING']}})
    p = tmp_path / 'proj2'
    build_project(p, req, _pack(tmp_path))
    strategy = json.loads((p / 'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
    assert 'RACE' in strategy['selected_strategy_frameworks']
    assert strategy['sections']['07_race_execution_table']
    assert '07_race_execution_table' in strategy['human_projection']['active_sections']


def test_priority_and_ab_do_not_manufacture_perpetual_next_work():
    out = build_risk_priority_depth(
        {'required_missing': []}, {}, {'status': 'READY_REVIEW', 'issues': []}, {'actions': []},
        {'primary_conversion_proposition': 'X'}, [], None, {}
    )
    assert out['priority_plan']['status'] == 'CURRENT_SCOPE_CAN_STOP'
    assert out['priority_plan']['P0'] == []
    assert out['priority_plan']['P1'] == []
    assert out['priority_plan']['P2'] == []
    assert out['ab_test_hypotheses'] == []
    assert out['agent_stop_eligible'] is True

    out2 = build_risk_priority_depth(
        {'required_missing': []}, {'experiment': {'assignment_unit': 'user'}},
        {'status': 'READY_REVIEW', 'issues': []}, {'actions': []},
        {'primary_conversion_proposition': 'X'}, [], {'status': 'DESIGN'}, {}
    )
    assert out2['ab_test_status'] == 'CURRENT_EVALUATION_SCOPE'
    assert out2['priority_plan']['P2']


def test_asset_architecture_does_not_create_visual_job_without_asset_surface():
    arch = build_asset_architecture(
        'P', {}, ['What is it?'], [{'family': 'LISTING', 'surface': 'PDP', 'object_id': 'L1'}],
        None, {}, 'GENERAL_COMMERCE'
    )
    assert arch['asset_count'] == 0
    assert arch['asset_scope_active'] is False
    assert arch['decision_coverage_summary']['status'] == 'NO_ASSET_SURFACE_IN_CURRENT_SCOPE'
    assert arch['unrouted_questions']


def test_asset_relationships_are_explicit_not_auto_chained():
    jobs = [
        {'asset_id': 'A', 'family': 'VISUAL', 'surface': 'GALLERY', 'asset_type': 'IMAGE', 'consumer_question': 'Q1'},
        {'asset_id': 'B', 'family': 'VISUAL', 'surface': 'GALLERY', 'asset_type': 'IMAGE', 'consumer_question': 'Q2'},
    ]
    arch = build_asset_architecture('P', {}, ['Q1', 'Q2'], [], jobs, {}, 'GENERAL_COMMERCE')
    assert arch['relationship_mode'] == 'EXPLICIT_ONLY'
    assert arch['auto_sequence_authority'] is False
    assert all(not x.get('handoff') for x in arch['assets'])

    jobs[0]['handoff'] = 'B'
    arch2 = build_asset_architecture('P2', {}, ['Q1', 'Q2'], [], jobs, {}, 'GENERAL_COMMERCE')
    assert next(x for x in arch2['assets'] if x['consumer_question'] == 'Q1')['handoff'] == 'B'
    assert arch2['explicit_handoff_count'] == 1
