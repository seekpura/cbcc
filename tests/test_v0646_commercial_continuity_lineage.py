from pathlib import Path
import json

from runtime.cbcc.commerce_decision_context import (
    compile_commerce_decision_context,
    bind_asset_decision_lineage,
    audit_asset_decision_consumption,
)
from runtime.cbcc.prompt_compiler import compile_asset_prompt
from runtime.cbcc.commercial_intelligence_workspace import render_commercial_intelligence_workspace


def _fixture_context():
    domain = {
        'market': {
            'status': 'READY',
            'price_bands': [{'min': 49, 'max': 79, 'count': 18}],
            'price_valley_signals': [{'range': '69-75', 'signal': 'low direct competition'}],
            'price_configuration_matrix': [{'configuration': '30g', 'median_price': 59}],
            'segments': [{'segment': 'urban oily-skin routine users', 'signal': 'high relevance'}],
            'customer_voice': [{'theme': 'lightweight hydration', 'count': 23}],
        },
        'economics': {
            'status': 'READY',
            'currency': 'MYR',
            'pricing_economics_authority': {
                'status': 'READY',
                'price_bands': [{'min': 49, 'max': 79}],
                'price_valleys': [{'range': '69-75'}],
                'pricing_decision': {'status': 'AGENT_DECISION_SUPPLIED', 'decision': 69, 'why': 'protect contribution while staying in observed band'},
                'scenarios': [{'scenario_id': 'BASE', 'price': 69, 'contribution_before_ads': 31, 'break_even_cpa': 25, 'break_even_roas': 2.76}],
                'offer_boundary': {'discount_headroom': 8},
            },
        },
        'listing': {
            'status': 'READY',
            'compiled': {
                'objection_resolution_plan': [{'objection': 'oily skin still needs hydration', 'answer': 'balance oil control with hydration'}],
                'keywords': {'primary': ['oil control gel'], 'secondary': ['lightweight moisturiser']},
            },
        },
        'ads': {
            'status': 'READY',
            'aggregate': {'diagnosis': [{'route': 'CLICK_PACKAGE', 'reason': 'thumbnail promise weak'}]},
        },
        'feedback': {
            'status': 'READY',
            'issues': [{'category': 'MISUNDERSTANDING', 'theme': 'anti-acne interpreted as medical treatment', 'count': 7}],
        },
    }
    strategy = {
        'sections': {
            '03_platform_region_audience_culture': {
                'audience_segments': [{'segment': 'urban oily / combination skin users', 'region': 'MY', 'why': 'routine fit'}],
            },
            '04_marketing_core_strategy': {
                'positioning': {
                    'primary_conversion_proposition': 'daily oil-balancing hydration',
                    'message_hierarchy': [{'priority': 'P0', 'message': 'balance oil without skipping hydration'}],
                },
            },
            '07_race_execution_table': [
                {'stage': 'COMMUNICATION', 'objective': 'resolve first-scan relevance', 'kpi': 'CTR / qualified PDP entry'},
            ],
            '09_risk_measurement_priority_next_steps': {
                'priority_plan': {'P0': [{'action': 'repair first-scan promise'}]},
            },
        }
    }
    culture = {
        'status': 'READY',
        'language_profiles': {'primary_locale': 'ms-MY'},
        'visual_implications': ['modern urban routine; avoid stereotype-coded beauty cues'],
        'intersectionality': ['age / skin tone / modest styling handled by real audience evidence'],
    }
    return compile_commerce_decision_context(
        domain=domain,
        strategy=strategy,
        culture=culture,
        target={'market': 'MY', 'platform_family': 'TikTok Shop', 'site': 'MY'},
        decision_trace={'traces': [{'decision_intent': 'RELEVANCE', 'race_stage': 'COMMUNICATION'}]},
    )


def test_context_keeps_real_commercial_payload_not_only_status_counts():
    ctx = _fixture_context()
    assert ctx['market']['price_bands'][0]['min'] == 49
    assert ctx['market']['price_valley_signals'][0]['range'] == '69-75'
    assert ctx['pricing_economics']['pricing_decision']['decision'] == 69
    assert ctx['pricing_economics']['scenarios'][0]['break_even_roas'] == 2.76
    assert 'urban oily / combination skin users' in json.dumps(ctx['audience_culture'], ensure_ascii=False)
    assert ctx['race'][0]['stage'] == 'COMMUNICATION'
    assert ctx['listing']['objections'][0]['objection'] == 'oily skin still needs hydration'
    assert ctx['ads']['diagnosis'][0]['route'] == 'CLICK_PACKAGE'
    assert ctx['reviews']['issues'][0]['category'] == 'MISUNDERSTANDING'
    assert all('source_artifact' in row for row in ctx['lineage_index'])


def test_asset_lineage_is_relevance_filtered_but_not_summary_only():
    ctx = _fixture_context()
    paid = {
        'asset_id': 'AD-01', 'surface': 'PAID_AD', 'family': 'PAID',
        'decision_intent': 'RELEVANCE', 'race_stage': 'COMMUNICATION',
        'consumer_question': 'Why should I click this daily gel?',
        'purchase_barrier': 'looks like generic anti-acne gel',
        'strategic_job': 'repair click package',
        'offer_relevant': True,
    }
    lineage = bind_asset_decision_lineage(paid, ctx)
    assert lineage['market']['price_bands']
    assert lineage['pricing_economics']['pricing_decision']['decision'] == 69
    assert lineage['ads']['diagnosis'][0]['route'] == 'CLICK_PACKAGE'
    assert lineage['race'][0]['stage'] == 'COMMUNICATION'
    assert lineage['audience_culture']['segments']
    assert lineage['lineage_refs']

    proof = {
        'asset_id': 'PROOF-01', 'surface': 'GALLERY', 'family': 'VISUAL',
        'decision_intent': 'PROOF', 'consumer_question': 'Does this support hydration?',
        'strategic_job': 'prove product fact', 'offer_relevant': False,
    }
    proof_lineage = bind_asset_decision_lineage(proof, ctx)
    assert proof_lineage.get('pricing_economics', {}).get('pricing_decision') in (None, {})
    assert proof_lineage['audience_culture']['segments']


def test_prompt_consumes_bound_commerce_context_and_selected_photo_parameters():
    ctx = _fixture_context()
    asset = {
        'asset_id': 'AD-01', 'asset_name': 'Paid relevance hero', 'asset_type': 'IMAGE',
        'surface': 'PAID_AD', 'family': 'PAID', 'decision_intent': 'RELEVANCE',
        'race_stage': 'COMMUNICATION', 'consumer_question': 'Why should I click?',
        'purchase_barrier': 'generic promise', 'strategic_job': 'repair first-scan promise',
        'reason_to_exist': 'improve qualified click intent', 'incremental_information': 'oil balance + hydration',
        'belief_target': 'this is daily balancing care', 'success_metric': 'CTR / qualified PDP entry',
        'offer_relevant': True,
        'commerce_decision_context': bind_asset_decision_lineage({'asset_id':'AD-01','surface':'PAID_AD','family':'PAID','decision_intent':'RELEVANCE','race_stage':'COMMUNICATION','offer_relevant':True}, ctx),
        'product_presence': {'planning_state': 'PRESENT'},
        'creative_brief': {'composition': 'asymmetric close product + decisive routine evidence'},
        'visible_copy': {'target_copy': 'Balance Oil. Keep Hydration.', 'delivery_translation': '平衡油脂，保留水润。'},
    }
    photography = {
        'capture_mode': 'REAL_PHOTO', 'photographic_route': True, 'repeatable_capture': True,
        'camera': {'focal_length_mm': 85, 'working_distance': '1.2m', 'camera_height': '1.35m', 'focus_plane': 'front label', 'aperture_dof_intent': 'f/5.6 controlled depth'},
        'lighting': {'key': 'large diffused key 45deg camera-left', 'fill': 'white bounce', 'negative_fill': 'black flag camera-right', 'cct': '5200K', 'exposure_ratio_plan': '2:1', 'polarization_plan': 'cross-polarize only if label glare blocks copy', 'prelight_plan': 'lock reference frame before production'},
        'cmf': {'material': 'semi-gloss tube', 'surface_behavior': 'controlled specular rolloff'},
        'color_management': {'output_space': 'sRGB', 'white_balance': '5200K'},
    }
    bundle = compile_asset_prompt(
        asset,
        product={'name': 'Daily Gel'},
        target={'market': 'MY', 'platform_family': 'TikTok Shop', 'site': 'MY'},
        culture={'visual_implications': ['modern urban routine']},
        language_contract={'primary_locale': 'ms-MY', 'delivery_locale': 'zh-CN'},
        photography=photography,
        strategy_authority={'sections': {}},
        source_product_assets=[],
    )
    prompt = bundle['prompt_en']
    assert '85' in prompt
    assert '5200K' in prompt
    assert '2:1' in prompt
    assert 'daily oil-balancing hydration' in prompt
    assert 'COMMUNICATION' in prompt or 'first-scan' in prompt
    assert '69' in prompt  # offer-relevant paid asset may consume selected price decision
    audit = audit_asset_decision_consumption(asset, bundle)
    assert audit['status'] == 'PASS'


def test_commercial_intelligence_workspace_exposes_primary_operator_information():
    ctx = _fixture_context()
    html = render_commercial_intelligence_workspace(ctx)
    for token in ['市场 / 区域 / 人群', '价格 / 经济模型 / Offer', 'RACE / Journey', '广告诊断', '评论 / Customer Voice', '69', '2.76', 'urban oily / combination skin users']:
        assert token in html
    assert 'data-workspace-kind="commercial-intelligence"' in html
