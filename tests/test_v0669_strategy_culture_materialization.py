from __future__ import annotations

from runtime.cbcc.strategy_depth_projection_v3 import wrap_build_master_strategy as wrap_depth
from runtime.cbcc.long_requirement_runtime import wrap_build_master_strategy as wrap_long
from runtime.cbcc.long_requirement_human_projection import wrap_render_master_strategy_cn as wrap_long_human
from runtime.cbcc.strategy_culture_materialization import (
    wrap_build_master_strategy as wrap_materialization,
    wrap_render_master_strategy_cn as wrap_materialization_human,
    strategy_materialization_issues,
)


def _base_strategy():
    return {
        'delivery_mode': 'FULL',
        'human_projection': {'mode': 'FULL'},
        'sections': {
            '01_information_completeness_assumptions_decisions': {
                'pending_confirmations': [{'item': 'current platform algorithm', 'status': 'OPEN'}],
                'assumptions': [{'assumption': 'audience income band is not supplied', 'status': 'ASSUMPTION'}],
                'decision_log': [{
                    'what': 'Use TikTok Shop MY as the first conversion surface',
                    'why': 'The selected project target is TikTok Shop Malaysia.',
                    'evidence': ['USER_TARGET'],
                    'tradeoff': 'Prioritize platform-native commerce assets before cross-platform reuse.',
                    'execution': 'Build TikTok-native listing/content/creative execution.',
                    'measurement': 'CTR/CVR and content-to-PDP progression.',
                }],
            },
            '02_product_truth_value_ladder': {
                'product_facts': [{
                    'fact': 'active.salicylic_acid', 'value': '0.57%', 'evidence_level': 'B',
                    'source_ids': ['SRC-FORMULA'], 'publication_status': 'FACT',
                }],
                'claim_value_ladder': [{
                    'claim': 'feels lighter in daily use', 'classification': 'SUBJECTIVE_EXPERIENCE',
                    'evidence_level': 'C', 'source_ids': ['SRC-UGC'], 'publication_status': 'PENDING_EVIDENCE',
                }],
            },
            '03_platform_region_audience_culture_insight': {'rows': []},
            '04_marketing_core_strategy': {'frameworks': {'applied_frameworks': ['STP','JTBD','AIDA','FABE','4P','FUNNEL','RACE']}},
            '05_visual_photography_strategy': {
                'style': 'editorial commerce', 'style_why': 'Prioritize fast mobile comprehension.',
                'palette_hex': {'primary': '#17382C', 'secondary': '#DDE8DF', 'background': '#F7F3E8', 'text': '#16211B'},
                'composition': 'mobile-first hierarchy with one dominant focal path',
                'lighting_framework': {'direction': 'soft 3/4 key', 'cct': '5200K', 'ratio': '2:1', 'quality': 'soft'},
                'lens': '50–85mm family', 'camera': {'shot_size': 'medium/detail by asset', 'height': 'product eye level'},
                'scene': 'clean daily skincare context', 'props': ['neutral tray'],
                'casting': ['only when shopper question needs human context'],
                'wardrobe_hair_makeup': 'natural, market-appropriate, non-stereotyped',
                'platform_dimensions': ['1600x1600 still', '9:16 short video'], 'shot_list': [],
                'why': {'why': 'Execution follows the purchase question.', 'consumer_logic': 'reduce ambiguity', 'platform_logic': 'mobile-first', 'culture_logic': 'evidence-led inclusion', 'business_logic': 'conversion clarity'},
            },
            '06_platform_content_matrix': [{
                'platform': 'TikTok Shop', 'site': 'MY', 'audience': 'urban skincare shopper',
                'topic': 'daily balance', 'hook': 'oily skin still needs hydration',
                'script_structure': 'problem → bounded proof → routine fit', 'visual_form': 'VIDEO',
                'cta': 'View product details', 'metric': 'CTR/CVR', 'race_stage': 'COMMUNICATION',
            }],
            '07_race_execution_table': [],
            '08_culture_adaptation_checklist': [{
                'adaptation_point': 'language and representation', 'inclusive_representation': 'natural local context',
                'stereotype_taboo_risk': 'do not infer behavior from ethnicity', 'result': 'TO_VERIFY',
                'modification': 'native review before publish', 'why': 'avoid unsupported cultural assumptions',
            }],
            '09_risk_measurement_priority_next_steps': {
                'priority_plan': {'P0': [{'action': 'claim evidence'}], 'P1': [{'action': 'platform-native execution'}], 'P2': [{'action': 'additional tests'}]},
            },
        },
    }


def _request():
    return {
        'target': {'platform_family': 'TikTok Shop', 'platform': 'TikTok Shop', 'market': 'Malaysia', 'site': 'MY', 'primary_locale': 'ms-MY'},
        'audience': {'primary_segment': 'urban skincare shopper'},
        'product': {'name': 'K01', 'category': 'skincare / cosmetic'},
        'claims': [
            {'claim': 'oil balance', 'evidence_grade': 'B', 'source_ids': ['SRC-FORMULA']},
            {'claim': 'feels lighter in daily use', 'evidence_grade': 'C', 'source_ids': ['SRC-UGC'], 'type': 'SUBJECTIVE_EXPERIENCE'},
        ],
        'sources': [
            {'source_id': 'SRC-FORMULA', 'kind': 'supplier_formula'},
            {'source_id': 'SRC-UGC', 'kind': 'subjective_ugc'},
        ],
        'resource_constraints': {'budget': 'limited', 'timeline': 'limited'},
    }


def _build():
    def base(request, *args, **kwargs):
        return _base_strategy()
    wrapped = wrap_materialization(wrap_long(wrap_depth(base)))
    return wrapped(_request(), market={}, culture={}, compliance={'status': 'TO_VERIFY'}, asset_architecture={'assets': []})


def test_full_strategy_materializes_user_strategy_culture_execution_objects():
    s = _build()['sections']

    truth = s['02_product_truth_value_ladder']
    audit_rows = truth['product_truth_audit_table']
    assert audit_rows
    required_truth = {
        'item', 'fact_or_claim', 'real_selling_point', 'perceived_benefit', 'emotional_value',
        'non_claimable', 'evidence_grade', 'source_refs', 'publication_rule', 'basis', 'tradeoff'
    }
    assert all(required_truth <= set(row) for row in audit_rows)
    c_rows = [row for row in audit_rows if row['evidence_grade'] == 'C']
    assert c_rows and all('NO_HARD_CLAIM' in row['publication_rule'] for row in c_rows)

    info = s['01_information_completeness_assumptions_decisions']
    log = info['assumption_decision_log']
    assert log and all({'type','item','status','basis','tradeoff'} <= set(row) for row in log)

    intersectionality = s['03_platform_region_audience_culture_insight']['intersectionality_table']
    assert intersectionality
    assert {'race_ethnicity','gender','age','income','geography'} <= set(intersectionality[0]['dimensions'])
    assert all({'implication','evidence_or_assumption','stereotype_guard','execution'} <= set(row) for row in intersectionality)

    framework = s['04_marketing_core_strategy']['framework_relationships']
    for key in ('RACE','STP','JTBD','AIDA','FABE','4P','FUNNEL'):
        assert {'role','basis','tradeoff','execution'} <= set(framework[key])

    visual = s['05_visual_photography_strategy']['visual_execution_checklist']
    for key in (
        'style_keywords','moodboard_direction','composition_rules','palette_hex_and_contrast','lighting',
        'lens_focal_length','shot_size','camera_position','scene','props','casting_wardrobe_grooming','platform_dimensions'
    ):
        assert visual[key]

    matrix = s['06_platform_content_matrix']
    required_matrix = {
        'platform','audience','topic','hook','script_structure','visual_form','cta','metric','race_stage',
        'culture_adaptation','taboo_stereotype_check','platform_dimensions','duration','cover_first_frame',
        'subtitle_strategy','music_rights','traffic_mechanism','landing_handoff','utm_attribution','why'
    }
    assert matrix and all(required_matrix <= set(row) for row in matrix)

    race = s['07_race_execution_table']
    assert [row['stage'] for row in race] == ['RESEARCH','ACTION','COMMUNICATION','EVALUATION']
    assert all({'objective','key_actions','output','platform','culture_check','kpi','why'} <= set(row) for row in race)

    culture = s['08_culture_adaptation_checklist']
    required_culture = {
        'adaptation_point','evidence_or_assumption','inclusive_representation','stereotype_taboo_risk',
        'script_check','casting_check','wardrobe_grooming_check','color_check','cta_check','result','modification','why'
    }
    assert culture and all(required_culture <= set(row) for row in culture)

    last = s['09_risk_measurement_priority_next_steps']
    priority_rows = last['resource_tradeoff_plan']['priority_rows']
    assert [row['priority'] for row in priority_rows] == ['P0','P1','P2']
    assert all({'keep','cut_or_defer','why','restore_condition'} <= set(row) for row in priority_rows)
    self_check = last['output_self_check_rows']
    assert [row['check'] for row in self_check] == ['fabrication','why','culture','compliance','metric','assumption']
    assert all({'status','basis','action'} <= set(row) for row in self_check)
    assert strategy_materialization_issues(_build()) == []


def test_human_projection_exposes_all_first_class_strategy_tables():
    strategy = _build()
    renderer = wrap_materialization_human(wrap_long_human(lambda strategy: '# Base strategy\n'))
    md = renderer(strategy)
    required_titles = (
        '产品事实审计：真实卖点 / 可感知利益 / 情绪价值 / 不可宣称项',
        '假设与决策日志（事实 / 假设 / 决策）',
        '交叉性分析：族裔 × 性别 × 年龄 × 收入 × 地域',
        '框架关系与决策理由',
        '视觉总策略与拍摄执行清单',
        'RACE传播框架执行表',
        '族裔文化适配检查表',
        'P0 / P1 / P2 资源取舍表',
        '输出前自检表',
    )
    for title in required_titles:
        assert title in md, title

    for token in ('RACE阶段', '族裔文化适配/禁忌校验', '音乐版权', 'UTM/归因', '深肤色', '反光板/柔光'):
        assert token in md, token


def test_missing_first_class_strategy_objects_are_audited_as_incomplete():
    issues = strategy_materialization_issues(_base_strategy())
    codes = {row['code'] for row in issues}
    required_codes = {
        'FULL_PRODUCT_TRUTH_AUDIT_TABLE_MISSING',
        'FULL_ASSUMPTION_DECISION_LOG_MISSING',
        'FULL_INTERSECTIONALITY_TABLE_MISSING',
        'FULL_FRAMEWORK_RELATIONSHIP_SHALLOW',
        'FULL_VISUAL_EXECUTION_CHECKLIST_MISSING',
        'FULL_CONTENT_MATRIX_EXECUTION_COLUMNS_MISSING',
        'FULL_RACE_EXECUTION_ORDER_INVALID',
        'FULL_CULTURE_ADAPTATION_ROW_SHALLOW',
        'FULL_RESOURCE_TRADEOFF_PRIORITY_ROWS_MISSING',
        'FULL_OUTPUT_SELF_CHECK_ROWS_MISSING',
    }
    assert required_codes <= codes
