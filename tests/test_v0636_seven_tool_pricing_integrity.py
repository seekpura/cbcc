from pathlib import Path

from runtime.cbcc.pricing_economics_authority import compile_pricing_economics_authority
from runtime.cbcc.seven_tool_continuity import TOOL_ORDER, compile_seven_tool_continuity


def _request(with_cvr=True):
    offer = {
        'currency': 'USD',
        'scenarios': [
            {
                'scenario_id': 'K01-BASE',
                'sku': 'K01',
                'price': 20,
                'costs': {
                    'landed_cost': 4,
                    'platform_fee': {'type': 'rate', 'value': 0.1},
                    'fulfillment': 2,
                    'affiliate_commission': {'type': 'rate', 'value': 0.1},
                    'tax': 1,
                    'refund_allowance': 1,
                    'ad_cost': 3,
                },
                'target_contribution': 2,
                'role': 'HERO',
            }
        ],
        'pricing_decision': {'decision': 20, 'why': 'Explicit strategy decision for the test fixture.'},
    }
    if with_cvr:
        offer['scenarios'][0]['click_to_order_cvr'] = 0.05
    return {'sku': 'K01', 'target': {'currency': 'USD'}, 'offer_economics': offer}


def test_strict_pricing_economics_projects_real_break_even_and_provenance():
    market = {
        'price_bands': [{'lower': 15, 'upper': 20, 'items': 4}, {'lower': 20, 'upper': 25, 'items': 2}],
        'price_valley_signals': [{'lower': 20, 'upper': 25, 'signal': 'LOW_DENSITY_BETWEEN_STRONGER_NEIGHBORS'}],
        'price_configuration_matrix': [{'configuration': '30g', 'price_band': '15-20'}],
    }
    out = compile_pricing_economics_authority(_request(), market, {'status': 'CALCULATED_FROM_INPUTS', 'currency': 'USD'})
    assert out['status'] == 'READY'
    row = out['scenarios'][0]
    assert row['status'] == 'CALCULATED_FROM_EXPLICIT_INPUTS'
    # price 20 - landed 4 - platform 2 - fulfillment 2 - affiliate 2 - tax 1 - refund 1 = 8 pre-ad
    assert row['contribution_before_ads'] == 8
    assert row['contribution_margin_rate_before_ads'] == 0.4
    assert row['break_even_cpa'] == 6
    assert row['break_even_cpc'] == 0.3
    assert round(row['break_even_roas'], 6) == round(20 / 6, 6)
    assert row['component_provenance']['platform_fee']['status'] == 'EXPLICIT_RATE'
    assert out['market_price_valleys']
    assert out['pricing_decision']['status'] == 'AGENT_DECISION_SUPPLIED'
    assert out['downstream_consumers']['listing_creative']['status'] == 'AVAILABLE'
    assert out['downstream_consumers']['advertising_optimization']['floors'][0]['break_even_cpc'] == 0.3


def test_missing_costs_and_missing_cvr_are_never_silently_zeroed():
    req = _request(with_cvr=False)
    del req['offer_economics']['scenarios'][0]['costs']['tax']
    out = compile_pricing_economics_authority(req, {}, {})
    assert out['status'] == 'PARTIAL_MISSING_INPUT'
    row = out['scenarios'][0]
    assert row['status'] == 'MISSING_INPUT'
    assert 'tax' in row['missing_inputs']
    assert row.get('break_even_cpc') is None

    req2 = _request(with_cvr=False)
    out2 = compile_pricing_economics_authority(req2, {}, {})
    row2 = out2['scenarios'][0]
    assert row2['status'] == 'CALCULATED_FROM_EXPLICIT_INPUTS'
    assert row2['break_even_cpc'] is None
    assert 'unavailable when CVR is not supplied' in row2['formula_basis']['break_even_cpc']


def test_seven_tools_are_first_class_with_runtime_consumer_output_delivery_chain():
    pricing = compile_pricing_economics_authority(_request(), {'price_bands': []}, {})
    domain = {
        'market': {'status': 'MARKET_ANALYSIS_COMPILED', 'price_bands': []},
        'pricing_economics_authority': pricing,
        'listing': {'status': 'LISTING_COMPILED'},
        'ads': {'status': 'CALCULATED_FROM_INPUTS'},
        'feedback': {'status': 'FEEDBACK_ANALYZED'},
    }
    architecture = {'assets': [{'asset_id': 'IMG-1', 'asset_type': 'IMAGE'}]}
    video = {'assets': [{'asset_id': 'VID-1', 'asset_type': 'VIDEO'}]}
    paid = {'campaigns': [{'campaign_id': 'C1'}]}
    out = compile_seven_tool_continuity(domain=domain, architecture=architecture, video_plan=video, paid_campaigns=paid, pricing_economics=pricing)
    assert out['status'] == 'SEVEN_TOOL_CONTINUITY_COMPILED'
    assert out['tool_order'] == TOOL_ORDER
    assert out['all_seven_first_class'] is True
    assert [x['id'] for x in out['capabilities']] == TOOL_ORDER
    for row in out['capabilities']:
        assert row['runtime_entry']
        assert row['real_consumers']
        assert row['business_outputs']
        assert row['human_delivery']
    product = next(x for x in out['capabilities'] if x['id'] == '02_PRODUCT_STRATEGY')
    assert 'Break-even CPA/CPC/ROAS' in product['business_outputs']
    ads = next(x for x in out['capabilities'] if x['id'] == '06_ADVERTISING_OPTIMIZATION')
    assert ads['evidence']['economic_floor_count'] == 1


def test_provider_pixel_manifest_is_explicit_exact_pixel_only_after_migration():
    text = Path('runtime/cbcc/provider_executor.py').read_text(encoding='utf-8')
    assert "if fidelity not in {'EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'}" in text
    layer_fn = text.split('def _layer_manifest', 1)[1].split('def _capture_metadata', 1)[0]
    assert "fidelity != 'LOCKED_PIXEL'" not in layer_fn


def test_human_workspace_exposes_commercial_brain_and_break_even_fields():
    text = Path('runtime/cbcc/delivery_workspace.py').read_text(encoding='utf-8')
    assert 'id="commercial-brain"' in text
    assert '七大工具 / 定价与经济性' in text
    assert 'Break-even CPA' in text
    assert 'Break-even CPC' in text
    assert 'Break-even ROAS' in text
    assert 'Pricing Decision + WHY' in text


def test_plugin_top_level_activation_mentions_seven_tools_and_pricing_integrity():
    skill = Path('SKILL.md').read_text(encoding='utf-8')
    build = Path('scripts/build_plugin_dist.py').read_text(encoding='utf-8')
    assert 'Seven First-Class Commerce Tools + Pricing/Economics Integrity' in skill
    assert 'Market Research' in skill and 'Advertising Optimization' in skill and 'Review Analysis' in skill
    assert 'Pricing Decision + WHY' in skill
    assert '缺失的成本' in skill
    assert '七大工具按一等能力执行并保持连续性' in build
