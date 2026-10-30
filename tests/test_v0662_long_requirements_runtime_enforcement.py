from __future__ import annotations

import json
from pathlib import Path

from runtime.cbcc.strategy_depth_projection_v3 import wrap_build_master_strategy
from runtime.cbcc.full_delivery_depth_v3 import audit_full_strategy_depth_v3, audit_host_full_package
from runtime.cbcc.long_requirement_human_projection import wrap_render_master_strategy_cn


def _base_strategy():
    return {
        'delivery_mode': 'FULL',
        'human_projection': {'mode': 'FULL'},
        'sections': {
            '01_information_completeness_assumptions_decisions': {
                'pending_confirmations': [
                    {'item': f'Q{i}', 'reason': f'why-{i}', 'required_for': ['publish'], 'status': 'OPEN'}
                    for i in range(14)
                ],
                'assumptions': [{'assumption': 'A1', 'status': 'ASSUMPTION'}],
                'decision_log': [{
                    'what': 'Use the selected platform-native route',
                    'why': 'It changes how the shopper encounters the offer.',
                    'evidence': ['SRC-1'],
                    'tradeoff': 'Prioritize the selected surface over generic reuse.',
                    'execution': 'Author for the selected surface.',
                    'measurement': 'surface KPI',
                }],
            },
            '02_product_truth_value_ladder': {
                'product_facts': [{
                    'fact': 'active.salicylic_acid', 'value': '0.57%',
                    'real_selling_point': 'formula fact',
                    'perceived_benefit': 'bounded benefit',
                    'emotional_value': 'confidence only if supported',
                    'claim_boundary': 'no medical claim',
                    'evidence_grade': 'B',
                    'source_refs': ['SRC-1'],
                }],
                'claim_value_ladder': [],
            },
            '03_platform_region_audience_culture_insight': {},
            '04_marketing_core_strategy': {'framework_relationships': {}},
            '05_visual_photography_strategy': {'people_applicability': 'PERSON_PRESENT'},
            '06_platform_content_matrix': [{
                'platform': 'TikTok Shop', 'audience': 'Malaysia shopper', 'topic': 'daily balance',
                'hook': 'hook', 'script_structure': 'structure', 'visual_form': 'VIDEO', 'cta': 'CTA',
                'metric': 'CTR', 'race_stage': 'COMMUNICATION',
            }],
            '07_race_execution_table': [],
            '08_culture_adaptation_checklist': [{
                'adaptation_point': 'Language',
                'inclusive_representation': 'natural local context',
                'stereotype_taboo_risk': 'avoid stereotype',
                'result': 'TO_VERIFY',
                'modification': 'native review',
                'why': 'market fit',
            }],
            '09_risk_measurement_priority_next_steps': {},
        },
    }


def _request():
    return {
        'target': {'platform_family': 'TikTok Shop', 'market': 'Malaysia', 'site': 'MY', 'primary_locale': 'ms-MY'},
        'audience': {'primary_segment': 'urban skincare shoppers'},
        'product': {'name': 'K01', 'category': 'skincare / cosmetic', 'ingredients': {'salicylic_acid': '0.57%'}},
        'claims': [{'claim_id': 'C1', 'claim': 'oil balance', 'evidence_grade': 'B', 'source_ids': ['SRC-1']}],
        'sources': [{'source_id': 'SRC-1', 'kind': 'supplier_formula'}],
        'offer_economics': {},
    }


def test_verbatim_requirements_are_projected_into_full_strategy_runtime():
    def base(request, *args, **kwargs):
        return _base_strategy()

    wrapped = wrap_build_master_strategy(base)
    strategy = wrapped(
        _request(),
        market={},
        culture={},
        compliance={'status': 'HOLD', 'claim_issues': [{'code': 'CLAIM_EVIDENCE_GRADE_MISSING'}]},
        asset_architecture={'assets': []},
    )
    s = strategy['sections']
    info = s['01_information_completeness_assumptions_decisions']
    assert len(info['pending_confirmations']) <= 10
    assert info['pending_confirmation_total_count'] == 14
    assert info['continue_under_assumptions'] is True
    assert info['question_limit'] == 10

    decision = info['decision_log'][0]
    context = decision['context_why']
    assert set(context) >= {'platform', 'region', 'audience', 'race_ethnicity_culture'}
    for key in ('platform', 'region', 'audience', 'race_ethnicity_culture'):
        assert context[key]['why']
        assert context[key]['status']

    vis = s['05_visual_photography_strategy']
    inc = vis['inclusive_photography']
    assert inc['deep_skin_exposure_compensation_plan']
    assert inc['reflector_bounce_diffusion']

    culture_rows = s['08_culture_adaptation_checklist']
    assert culture_rows
    for row in culture_rows:
        assert set(row) >= {'script_check', 'casting_check', 'wardrobe_grooming_check', 'color_check', 'cta_check'}

    p0 = s['09_risk_measurement_priority_next_steps']['p0_compliance_claim_checklist']
    assert {row['check_area'] for row in p0} >= {
        'efficacy_claims', 'ingredients_formula', 'certifications', 'price', 'sales_volume', 'regulated_category'
    }
    for row in p0:
        assert row['priority'] == 'P0'
        assert row['status']
        assert row['action']
        assert row['why']


def test_full_depth_audit_blocks_missing_verbatim_execution_objects():
    strategy = _base_strategy()
    result = audit_full_strategy_depth_v3(strategy)
    codes = {x['code'] for x in result['issues']}
    assert 'FULL_PENDING_CONFIRMATION_LIMIT_EXCEEDED' in codes
    assert 'FULL_DECISION_CONTEXT_WHY_MISSING' in codes
    assert 'FULL_P0_COMPLIANCE_CHECKLIST_MISSING' in codes
    assert 'FULL_CULTURE_EXECUTION_CHECK_COLUMNS_MISSING' in codes
    assert 'FULL_INCLUSIVE_PHOTOGRAPHY_DIMENSION_MISSING' in codes


def test_human_strategy_projection_exposes_platform_execution_culture_checks_and_p0_compliance():
    strategy = _base_strategy()
    s = strategy['sections']
    s['06_platform_content_matrix'][0].update({
        'platform_dimensions': 'TO_VERIFY', 'duration': '15s', 'cover_first_frame': 'first-frame hook',
        'subtitle_strategy': 'BM + accessibility', 'music_rights': 'TO_VERIFY',
        'traffic_mechanism': 'TO_VERIFY', 'landing_handoff': 'PDP', 'utm_attribution': 'creator/ad tracking',
        'culture_adaptation': 'native language', 'taboo_stereotype_check': 'reviewed', 'why': 'platform-native execution',
    })
    s['08_culture_adaptation_checklist'][0].update({
        'evidence_or_assumption': 'TO_VERIFY',
        'script_check': 'review script', 'casting_check': 'review casting',
        'wardrobe_grooming_check': 'review wardrobe/grooming', 'color_check': 'review color', 'cta_check': 'review CTA',
    })
    s['09_risk_measurement_priority_next_steps']['p0_compliance_claim_checklist'] = [{
        'check_area': 'efficacy_claims', 'priority': 'P0', 'status': 'HOLD', 'evidence_refs': [],
        'action': 'Do not hard-claim before evidence resolves.', 'why': 'regulated claim risk',
    }]

    wrapped = wrap_render_master_strategy_cn(lambda strategy: '# Base\n')
    md = wrapped(strategy)
    for token in (
        '平台执行 / 本地化 / 归因', 'platform_dimensions', 'music_rights', 'utm_attribution',
        '脚本校验', '模特校验', '服化道校验', '配色校验', 'CTA校验',
        'P0 合规 / 宣称证据检查', 'efficacy_claims',
    ):
        assert token in md


def test_host_full_package_rejects_assets_shortcut_and_missing_structured_art_direction(tmp_path: Path):
    # Minimal required shell to isolate asset-path failures.
    from runtime.cbcc.full_delivery_depth_v3 import CORE_HOST_FULL_FILES
    for rel in CORE_HOST_FULL_FILES:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix == '.json':
            p.write_text('{}', encoding='utf-8')
        else:
            p.write_text('placeholder', encoding='utf-8')

    shortcut = tmp_path / 'assets' / 'A1'
    shortcut.mkdir(parents=True)
    for name in ('01_design_card.md', '05_prompt_CN.txt', '06_prompt_EN.txt', '07_visible_copy.txt', '08_production_notes.txt'):
        (shortcut / name).write_text('x', encoding='utf-8')

    (tmp_path / 'ASSET_UNIVERSE.json').write_text(json.dumps({
        'platform_capacity_is_activation_constraint_only': True,
        'assets': [{'asset_id': 'A1', 'deployment_state': 'LIVE_CANDIDATE', 'family': 'GALLERY'}],
    }), encoding='utf-8')

    result = audit_host_full_package(tmp_path)
    codes = {x['code'] for x in result['issues']}
    assert 'HOST_SHORTCUT_ASSET_PACKAGE_FORBIDDEN' in codes
    assert 'MATURE_ASSET_PACKAGES_REQUIRED' in codes
