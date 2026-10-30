from __future__ import annotations

import json
from pathlib import Path

from runtime.cbcc.full_delivery_depth_v3 import (
    audit_full_strategy_depth_v3,
    audit_host_full_package,
    audit_asset_portfolio_depth,
)


def _base_full_strategy() -> dict:
    return {
        'human_projection': {'mode': 'FULL'},
        'sections': {
            '01_information_completeness_assumptions_decisions': {
                'domain_matrix': [{'domain': 'product', 'status': 'KNOWN'}],
                'clarifying_questions': [],
                'assumptions': [{'assumption': 'x', 'impact': 'y'}],
                'decision_log': [{'what': 'x', 'why': 'y', 'evidence': 'z', 'tradeoff': 't', 'execution': 'e', 'measurement': 'm'}],
            },
            '02_product_truth_value_ladder': {
                'product_facts': [{
                    'fact': '30g', 'real_selling_point': 'portable size', 'perceived_benefit': 'easy carry',
                    'emotional_value': 'clarity', 'claim_boundary': 'size fact only', 'evidence_grade': 'B',
                    'publication_status': 'BOUNDED', 'source_refs': ['SRC-1'],
                }],
                'claim_value_ladder': [],
            },
            '03_platform_region_audience_culture_insight': {
                'platform_audience_culture_rows': [{'platform': 'P', 'region': 'R', 'audience': 'A', 'adaptation': 'D', 'stereotype_taboo_check': 'PASS', 'why': 'W'}],
                'intersectionality_table': [{'dimensions': ['age', 'income', 'geography'], 'implication': 'I', 'evidence_or_assumption': 'E', 'stereotype_guard': 'G', 'execution': 'X'}],
                'adaptation_rows': [{'dimension': 'language', 'status': 'EVIDENCED', 'action': 'A', 'why': 'W'}],
                'dimension_status': {},
            },
            '04_marketing_core_strategy': {
                'positioning': {'positioning_statement': 'P', 'why': 'W'},
                'message_hierarchy': ['M'],
                'frameworks': {'STP': {}, 'JTBD': {}, 'AIDA': {}, 'FABE': {}, '4P': {}, 'FUNNEL': {}, 'RACE': {}},
                'framework_relationships': {},
            },
            '05_visual_photography_strategy': {
                'palette_hex': {'background': '#FFFFFF'}, 'composition': {'rule': 'R'}, 'color_management': {'output': 'sRGB'},
                'platform_dimensions': [{'surface': 'PDP', 'size': '1600x1600'}],
                'asset_parameter_reasoning': [{'asset_id': 'A1', 'visual_carrier': 'INFORMATION', 'why': 'W'}],
                'people_applicability': 'NOT_USED',
            },
            '06_platform_content_matrix': [{
                'platform': 'P', 'audience': 'A', 'topic': 'T', 'hook': 'H', 'script_structure': 'S', 'visual_form': 'V',
                'cta': 'C', 'metric': 'M', 'race_stage': 'COMMUNICATION', 'culture_adaptation': 'CA',
                'taboo_stereotype_check': 'PASS', 'why': 'W', 'platform_dimensions': '1600x1600', 'duration': 'N/A',
                'cover_first_frame': 'F', 'subtitle_strategy': 'N/A', 'music_rights': 'N/A', 'traffic_mechanism': 'TM',
                'landing_handoff': 'LH', 'utm_attribution': 'UTM',
            }],
            '07_race_execution_table': [
                {'stage': stage, 'objective': 'O', 'key_actions': ['A'], 'output': ['X'], 'platform': 'P', 'culture_check': 'C', 'kpi': ['K'], 'why': 'W'}
                for stage in ['RESEARCH', 'ACTION', 'COMMUNICATION', 'EVALUATION']
            ],
            '08_culture_adaptation_checklist': [{
                'adaptation_point': 'language', 'inclusive_representation': 'I', 'stereotype_taboo_risk': 'S',
                'result': 'PASS', 'modification': 'M', 'why': 'W', 'evidence_or_assumption': 'E',
            }],
            '09_risk_measurement_priority_next_steps': {
                'priority_plan': {'P0': ['x'], 'P1': ['y'], 'P2': ['z']},
                'risks': [{'risk': 'R'}], 'ab_test_hypotheses': [{'hypothesis': 'H'}], 'next_information_needed': ['N'],
                'resource_tradeoff_plan': {'constraints': ['budget'], 'keep': ['P0'], 'cut': ['decorative'], 'why': 'W'},
                'output_self_check': {
                    'fabrication_check': True, 'why_check': True, 'culture_check': True, 'compliance_check': True,
                    'metric_check': True, 'assumption_check': True, 'language_companion_check': True,
                    'asset_universe_check': True, 'prompt_depth_check': True,
                },
            },
        },
    }


def test_heading_or_boolean_presence_is_not_full_depth():
    s = _base_full_strategy()
    # The previous regression effectively treated one generic culture paragraph as sufficient.
    s['sections']['03_platform_region_audience_culture_insight']['dimension_status'] = {
        'platform': {'status': 'EVIDENCED'}
    }
    result = audit_full_strategy_depth_v3(s)
    assert result['status'] == 'INCOMPLETE'
    codes = {x['code'] for x in result['issues']}
    assert 'FULL_MARKET_CULTURE_DIMENSION_MISSING' in codes


def test_full_depth_requires_explicit_multidimensional_market_culture_status():
    s = _base_full_strategy()
    dims = [
        'platform', 'market_region', 'subregion_geography', 'audience_segments', 'age', 'gender', 'income_spend',
        'language', 'race_ethnicity', 'religion', 'holiday_calendar', 'payment', 'logistics', 'local_regulation',
        'platform_behavior', 'search_demand', 'competition', 'price_band', 'intersectionality', 'stereotype_taboo',
    ]
    s['sections']['03_platform_region_audience_culture_insight']['dimension_status'] = {
        k: {'status': 'TO_VERIFY', 'why': 'not silently omitted'} for k in dims
    }
    rels = {}
    for key in ['RACE', 'STP', 'JTBD', 'AIDA', 'FABE', '4P', 'FUNNEL']:
        rels[key] = {'role': 'selected lens', 'why': 'explicit relation'}
    s['sections']['04_marketing_core_strategy']['framework_relationships'] = rels
    result = audit_full_strategy_depth_v3(s)
    assert result['status'] == 'PASS', result


def test_people_are_optional_but_inclusive_execution_is_required_when_used():
    s = _base_full_strategy()
    dims = [
        'platform', 'market_region', 'subregion_geography', 'audience_segments', 'age', 'gender', 'income_spend',
        'language', 'race_ethnicity', 'religion', 'holiday_calendar', 'payment', 'logistics', 'local_regulation',
        'platform_behavior', 'search_demand', 'competition', 'price_band', 'intersectionality', 'stereotype_taboo',
    ]
    s['sections']['03_platform_region_audience_culture_insight']['dimension_status'] = {k: {'status': 'TO_VERIFY', 'why': 'x'} for k in dims}
    s['sections']['04_marketing_core_strategy']['framework_relationships'] = {k: {'role': 'x', 'why': 'y'} for k in ['RACE','STP','JTBD','AIDA','FABE','4P','FUNNEL']}
    v = s['sections']['05_visual_photography_strategy']
    v['people_applicability'] = 'PERSON_PRESENT'
    v['casting'] = {'subject_type': 'PERSON'}
    result = audit_full_strategy_depth_v3(s)
    assert result['status'] == 'INCOMPLETE'
    assert any(x['code'] == 'FULL_INCLUSIVE_PHOTOGRAPHY_DIMENSION_MISSING' for x in result['issues'])

    v['inclusive_photography'] = {
        'skin_tone_exposure': 'meter and preserve tone', 'deep_skin_shadow_protection': 'protect shadows',
        'reflector_bounce_diffusion': 'neutral bounce + large diffusion', 'hair_texture': 'preserve texture',
        'body_representation': 'non-tokenized range', 'disability_representation': 'context-led when relevant',
        'age_representation': 'age-appropriate and non-tokenized', 'ai_bias_check': 'review outputs',
    }
    result = audit_full_strategy_depth_v3(s)
    assert result['status'] == 'PASS', result


def test_host_full_package_cannot_omit_machine_authorities_or_chinese_language_audits(tmp_path: Path):
    # Mimics the observed regression: attractive ZIP with strategy headings and nine LST folders, but no formal machine objects/audits.
    (tmp_path / 'index.html').write_text('<html>九域</html>', encoding='utf-8')
    (tmp_path / '00_PROJECT_HUB.md').write_text('hub', encoding='utf-8')
    (tmp_path / '01_LISTING_UPLOAD_READY.md').write_text('title_en: x\ntitle_bm: y', encoding='utf-8')
    (tmp_path / 'HUMAN_DELIVERY.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'strategy').mkdir()
    for i in range(1, 10):
        (tmp_path / 'strategy' / f'{i:02d}_S.md').write_text('# section', encoding='utf-8')
    for i in range(1, 10):
        p = tmp_path / 'asset_packages' / f'LST-{i:02d}'
        p.mkdir(parents=True)
        (p / '12_design_card.json').write_text(json.dumps({'asset_id': f'LST-{i:02d}'}), encoding='utf-8')
        (p / '05_prompt_CN.txt').write_text('短提示词', encoding='utf-8')
        (p / '06_prompt_EN.txt').write_text('Consumer decision: 我实际会收到什么？', encoding='utf-8')
    result = audit_host_full_package(tmp_path)
    assert result['status'] == 'INCOMPLETE'
    codes = {x['code'] for x in result['issues']}
    assert 'FULL_DELIVERY_OBJECT_MISSING' in codes
    assert 'LISTING_CHINESE_COMPANION_MISSING' in codes
    assert 'MODEL_PROMPT_EN_LANGUAGE_PURITY_FAILED' in codes


def test_asset_portfolio_requires_universe_and_does_not_treat_nine_live_slots_as_total(tmp_path: Path):
    universe = {
        'activation_capacity': 9,
        'fixed_total_asset_limit': False,
        'platform_capacity_is_activation_constraint_only': True,
        'assets': [
            {'asset_id': f'LST-{i:02d}', 'deployment_state': 'LIVE_CANDIDATE', 'asset_family': 'HERO'} for i in range(1, 10)
        ] + [
            {'asset_id': 'AD-01', 'deployment_state': 'PAID_MEDIA', 'asset_family': 'AD'},
            {'asset_id': 'TST-01', 'deployment_state': 'TEST_POOL', 'asset_family': 'PROOF'},
            {'asset_id': 'SOC-01', 'deployment_state': 'SOCIAL_CONTENT', 'asset_family': 'SOCIAL_SEEDING'},
            {'asset_id': 'VID-01', 'deployment_state': 'ROTATION_POOL', 'asset_family': 'VIDEO'},
        ],
    }
    result = audit_asset_portfolio_depth(universe, packaged_asset_ids={f'LST-{i:02d}' for i in range(1, 10)})
    assert result['status'] == 'INCOMPLETE'
    assert result['total_asset_candidates'] == 13
    assert result['activation_capacity'] == 9
    assert {'AD-01', 'TST-01', 'SOC-01', 'VID-01'}.issubset(set(result['missing_materialized_asset_ids']))
