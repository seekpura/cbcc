from runtime.cbcc.commercial_continuity_authority import wrap_compile_asset_prompt
from runtime.cbcc.subject_presence_authority import wrap_compile_asset_prompt as wrap_subject


def test_commercial_and_subject_wrappers_do_not_replace_selected_photography_values():
    def base(asset, product, target, culture, language_contract, locale_profiles=None, photography=None, strategy_authority=None, source_product_assets=None):
        return {
            'design_card': {
                'composition_camera': {'focal_length_mm': '85mm', 'distance': '1.2m'},
                'lighting_material_cmf': {'cct': '5200K', 'exposure_ratio_plan': '2:1'},
            },
            'prompt_cn': '焦段 85mm；工作距离 1.2m；5200K；光比 2:1',
            'prompt_en': '85mm; working distance 1.2m; 5200K; ratio 2:1',
            'model_prompt_status': 'READY',
        }
    compile_prompt = wrap_subject(wrap_compile_asset_prompt(base))
    asset = {
        'asset_id': 'AD01', 'surface': 'PAID_AD', 'offer_relevant': True,
        'commerce_context': {
            'status': 'ASSET_DECISION_LINEAGE_BOUND',
            'pricing_economics': {'pricing_decision': {'decision': 69, 'why': 'margin + market fit'}},
            'positioning': {'primary_conversion_proposition': 'Lightweight daily balance'},
            'lineage_refs': [],
        },
        'asset_art_direction': {'subject_system': {'subject_type': 'ANIMAL', 'primary_subject': 'cat', 'action': 'calm grooming moment'}},
    }
    out = compile_prompt(asset, {}, {'market': 'MY'}, {}, {}, strategy_authority={})
    merged = out['prompt_cn'] + out['prompt_en']
    for token in ['85mm', '1.2m', '5200K', '2:1', '69', 'Lightweight daily balance', 'ANIMAL', 'cat']:
        assert token in merged
