from runtime.cbcc.commercial_intelligence_workspace import render_commercial_intelligence_workspace
from runtime.cbcc.asset_portfolio_workspace import render_asset_portfolio_workspace


def test_commercial_html_exposes_operator_information():
    html = render_commercial_intelligence_workspace({
        'market': {'price_bands': ['30-60'], 'customer_voice': ['lightweight']},
        'audience_culture': {'segments': ['urban pet owner'], 'target': {'market': 'MY'}},
        'pricing_economics': {'pricing_decision': {'decision': 49, 'why': 'fit'}, 'scenarios': [{'scenario_id': 'BASE', 'price': 49, 'break_even_roas': 2.3}]},
        'race': [{'stage': 'ACTION', 'objective': 'first scan'}],
        'listing': {'objections': ['too sticky']},
        'ads': {'diagnosis': ['CLICK_PACKAGE']},
        'reviews': {'issues': ['usage confusion']},
    })
    for token in ['市场与受众决策', '价格 / 经济模型 / Offer', 'RACE / Search / Listing', '广告诊断', '评论 / Customer Voice', '49', '2.3']:
        assert token in html


def test_asset_portfolio_html_states_capacity_is_not_total():
    html = render_asset_portfolio_workspace({'summary': {
        'total_asset_candidates': 20,
        'activation_capacity': 9,
        'fixed_total_asset_limit': False,
        'platform_capacity_is_activation_constraint_only': True,
        'asset_family_counts': {'HERO': 3, 'A_PLUS': 3, 'AD': 4, 'SOCIAL_SEEDING': 4},
        'deployment_state_counts': {'LIVE_CANDIDATE': 9, 'TEST_POOL': 5, 'PAID_MEDIA': 4},
    }})
    assert 'Asset Universe' in html and '20' in html
    assert 'Activation Capacity' in html and '9' in html
    assert '不限制' in html
