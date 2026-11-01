from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

MODULE = Path(__file__).parents[1] / 'runtime/cbcc/economics_offer_seven_tool_bridge.py'
spec = importlib.util.spec_from_file_location('economics_offer_seven_tool_bridge_v0676', MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def test_business_readiness_overrides_calculation_ready_in_seven_tool_evidence_only():
    pricing = {
        'status': 'READY',
        'phase2_business_status': 'TO_VERIFY',
        'phase2_economics_offer_authority': {
            'status': 'TO_VERIFY',
            'missing_inputs': ['payment_fee'],
            'pricing_decision': {'density_status': 'READY'},
            'offer_decision': {'density_status': 'TO_VERIFY'},
        },
    }

    def base(**kwargs):
        return {
            'status': 'SEVEN_TOOL_CONTINUITY_COMPILED',
            'capabilities': [
                {'id': '02_PRODUCT_STRATEGY', 'evidence': {'pricing_status': 'READY'}},
                {'id': '03_LISTING_CREATIVE', 'evidence': {'sentinel': 'keep'}},
            ],
            'pricing_economics_integrity': {'status': 'READY', 'missing_inputs': []},
        }

    out = mod.wrap_compile_seven_tool_continuity(base)(domain={}, pricing_economics=pricing)
    integrity = out['pricing_economics_integrity']
    assert integrity['calculation_status'] == 'READY'
    assert integrity['business_readiness_status'] == 'TO_VERIFY'
    assert integrity['status'] == 'TO_VERIFY'
    assert integrity['missing_inputs'] == ['payment_fee']
    assert integrity['pricing_decision_status'] == 'READY'
    assert integrity['offer_decision_status'] == 'TO_VERIFY'

    product = out['capabilities'][0]['evidence']
    assert product['calculation_status'] == 'READY'
    assert product['pricing_status'] == 'TO_VERIFY'
    assert product['missing_inputs'] == ['payment_fee']
    assert out['capabilities'][1]['evidence'] == {'sentinel': 'keep'}


def test_no_phase2_authority_leaves_mature_seven_tool_output_unchanged():
    baseline = {'status': 'SEVEN_TOOL_CONTINUITY_COMPILED', 'capabilities': [], 'pricing_economics_integrity': {'status': 'READY'}}
    def base(**kwargs): return dict(baseline)
    assert mod.wrap_compile_seven_tool_continuity(base)(domain={}, pricing_economics={'status':'READY'}) == baseline
