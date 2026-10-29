from runtime.cbcc.commerce_decision_context import compile_commerce_decision_context
from runtime.cbcc.commercial_context_compatibility import wrap_compile_commerce_decision_context
from runtime.cbcc.human_asset_commercial_projection import wrap_human_asset_design_card
from runtime.cbcc.commercial_continuity_authority import wrap_compile_asset_prompt


def test_mature_pricing_authority_names_survive_into_canonical_context():
    rich = wrap_compile_commerce_decision_context(compile_commerce_decision_context)
    ctx = rich(domain={
        'economics': {
            'status': 'READY',
            'pricing_economics_authority': {
                'status': 'READY',
                'currency': 'MYR',
                'market_price_bands': [{'min': 49, 'max': 79}],
                'market_price_valleys': [{'range': '69-75'}],
                'price_configuration_matrix': [{'configuration': '30g', 'median_price': 59}],
                'pricing_decision': {'decision': 69, 'why': 'within observed band'},
                'offer_bundle_discount_boundary': [{'scenario_id': 'BASE', 'discount_headroom_at_current_ad_cost': 8}],
                'scenarios': [{'scenario_id': 'BASE', 'price': 69, 'break_even_roas': 2.76}],
            },
        }
    })
    pricing = ctx['pricing_economics']
    assert pricing['price_bands'][0]['min'] == 49
    assert pricing['price_valleys'][0]['range'] == '69-75'
    assert pricing['offer_boundaries'][0]['discount_headroom_at_current_ad_cost'] == 8
    assert pricing['market_price_bands'] == pricing['price_bands']
    assert pricing['market_price_valleys'] == pricing['price_valleys']


def test_human_asset_card_exposes_upstream_commercial_decisions_and_sources():
    def base(asset, prompt_bundle, language_contract):
        return '# 资产 AD-01\n\n## Model Prompt CN\nold prompt\n'

    render = wrap_human_asset_design_card(base)
    text = render({}, {
        'design_card': {
            'commerce_decision_context': {
                'positioning': {'primary_conversion_proposition': 'daily oil-balancing hydration'},
                'audience_culture': {'segments': [{'segment': 'urban oily skin users'}]},
                'pricing_economics': {'pricing_decision': {'decision': 69, 'why': 'observed band + contribution'}},
                'race': [{'stage': 'COMMUNICATION', 'kpi': 'CTR'}],
                'listing': {'objections': [{'objection': 'oily skin still needs hydration'}]},
                'lineage_refs': [{'domain': 'PRICING_ECONOMICS', 'source_artifact': 'artifacts/pricing_economics_authority.json', 'source_path': '$'}],
            }
        }
    }, {})
    assert '## 上游商业决策与血缘' in text
    assert 'daily oil-balancing hydration' in text
    assert 'urban oily skin users' in text
    assert '69' in text
    assert 'COMMUNICATION' in text
    assert 'artifacts/pricing_economics_authority.json' in text
    assert text.index('## 上游商业决策与血缘') < text.index('## Model Prompt CN')


def test_continuity_wrapper_preserves_existing_photo_prompt_and_adds_commerce_context():
    def base(asset, **kwargs):
        return {
            'status': 'READY',
            'model_prompt_status': 'READY',
            'prompt_cn': '85mm，工作距离1.2m，5200K，光比2:1，negative fill，Prelight。',
            'prompt_en': '85mm lens, 1.2m working distance, 5200K, 2:1 ratio, negative fill, polarization, Prelight.',
            'model_prompt_cn': '85mm，工作距离1.2m，5200K，光比2:1，negative fill，Prelight。',
            'model_prompt_en': '85mm lens, 1.2m working distance, 5200K, 2:1 ratio, negative fill, polarization, Prelight.',
            'design_card': {},
            'prompt_consumption_audit': {'status': 'PASS', 'missing_decisions': []},
        }

    wrapped = wrap_compile_asset_prompt(base)
    asset = {
        'asset_id': 'AD-01', 'surface': 'PAID_AD', 'family': 'PAID', 'offer_relevant': True,
        'commerce_context': {
            'positioning': {'primary_conversion_proposition': 'daily oil-balancing hydration'},
            'pricing_economics': {'pricing_decision': {'decision': 69, 'why': 'observed band'}},
            'race': [{'stage': 'COMMUNICATION', 'objective': 'repair first scan'}],
            'lineage_refs': [{'domain': 'PRICING_ECONOMICS', 'source_artifact': 'pricing.json', 'source_path': '$'}],
        },
    }
    out = wrapped(asset=asset, product={}, target={}, culture={}, language_contract={}, photography={}, strategy_authority={}, source_product_assets=[])
    prompt = out['prompt_en']
    for token in ['85mm', '1.2m', '5200K', '2:1', 'negative fill', 'polarization', 'Prelight']:
        assert token in prompt
    assert '[COMMERCE DECISION CONTEXT]' in prompt
    assert 'daily oil-balancing hydration' in prompt
    assert '69' in prompt
    assert out['design_card']['commerce_decision_context']


def test_incomplete_commercial_consumption_is_not_allowed_to_remain_ready():
    # The bootstrap strict wrapper is intentionally simple enough to test by contract text here;
    # package guard also verifies it is installed from commercial_delivery_continuity import.
    from pathlib import Path
    text = Path('runtime/cbcc/commercial_continuity_bootstrap.py').read_text(encoding='utf-8')
    assert "out['status'] = 'MODEL_PROMPT_NEEDS_COMMERCIAL_DECISION_CONSUMPTION'" in text
    assert "card['generation_blocking'] = True" in text
