from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

MODULE = Path(__file__).parents[1] / 'runtime/cbcc/economics_offer_strategy_bridge.py'
spec = importlib.util.spec_from_file_location('economics_offer_strategy_bridge_v0676', MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def _phase2(status='READY'):
    if status == 'READY':
        return {
            'schema': 'cbcc-economics-offer-authority-v0.6.76',
            'status': 'READY',
            'missing_inputs': [],
            'scenario_math': {'status': 'CALCULATED'},
            'pricing_decision': {'density_status': 'READY', 'decision': 'MYR 59'},
            'offer_decision': {'density_status': 'READY', 'decision': 'No launch discount'},
        }
    return {
        'schema': 'cbcc-economics-offer-authority-v0.6.76',
        'status': 'TO_VERIFY',
        'missing_inputs': ['payment_fee'],
        'scenario_math': {'status': 'INCOMPLETE'},
        'pricing_decision': {'density_status': 'READY', 'decision': 'MYR 59'},
        'offer_decision': {'density_status': 'TO_VERIFY', 'density_gaps': ['what', 'measurement'], 'decision': None},
    }


def _economics(phase2):
    return {
        'status': 'CALCULATED_FROM_INPUTS',
        'pricing_economics_authority': {
            'status': 'READY',
            'phase2_business_status': phase2['status'],
            'phase2_economics_offer_authority': deepcopy(phase2),
        },
    }


def _base_strategy(mode='FULL_PROJECT'):
    return {
        'delivery_mode': mode,
        'sections': {
            '04_marketing_core_strategy': {'positioning': {'what': 'keep existing strategy'}},
        },
    }


def test_full_strategy_projects_exact_phase2_economics_authority_without_reauthoring():
    phase2 = _phase2('READY')
    def base(request, *args, **kwargs):
        return _base_strategy('FULL_PROJECT')
    out = mod.wrap_build_master_strategy(base)({'delivery_mode': 'FULL_PROJECT'}, economics=_economics(phase2))
    assert out['economics_offer_authority_v0676'] == phase2
    assert out['sections']['04_marketing_core_strategy']['positioning']['what'] == 'keep existing strategy'


def test_full_strategy_missing_economics_authority_fails_closed_instead_of_inventing_values():
    def base(request, *args, **kwargs):
        return _base_strategy('FULL')
    out = mod.wrap_build_master_strategy(base)({'delivery_mode': 'FULL'}, economics={'status': 'INSUFFICIENT_DATA'})
    auth = out['economics_offer_authority_v0676']
    assert auth['status'] == 'TO_VERIFY'
    assert auth['source_status'] == 'MISSING_PHASE2_ECONOMICS_OFFER_AUTHORITY'
    assert auth.get('price') is None


def test_strategy_validator_blocks_incomplete_economics_and_preserves_existing_issues():
    strategy = _base_strategy('FULL_PROJECT')
    strategy['economics_offer_authority_v0676'] = _phase2('TO_VERIFY')
    def base(value):
        return {'status': 'INCOMPLETE', 'issues': [{'code': 'EXISTING_STRATEGY_ISSUE'}], 'warnings': []}
    result = mod.wrap_validate_strategy_delivery(base)(strategy)
    codes = {x['code'] for x in result['issues']}
    assert 'EXISTING_STRATEGY_ISSUE' in codes
    assert 'FULL_ECONOMICS_OFFER_BUSINESS_READINESS_INCOMPLETE_V0676' in codes
    issue = next(x for x in result['issues'] if x['code'] == 'FULL_ECONOMICS_OFFER_BUSINESS_READINESS_INCOMPLETE_V0676')
    assert 'payment_fee' in issue['missing_inputs']
    assert result['status'] == 'INCOMPLETE'


def test_strategy_validator_accepts_ready_economics_without_erasing_base_result():
    strategy = _base_strategy('FULL')
    strategy['economics_offer_authority_v0676'] = _phase2('READY')
    def base(value):
        return {'status': 'PASS', 'issues': [], 'warnings': [{'code': 'KEEP_WARNING'}]}
    result = mod.wrap_validate_strategy_delivery(base)(strategy)
    assert result['status'] == 'PASS'
    assert result['issues'] == []
    assert result['warnings'] == [{'code': 'KEEP_WARNING'}]
    assert result['economics_offer_strategy_bridge_v0676_audit']['status'] == 'PASS'


def test_task_scoped_strategy_is_unchanged_and_not_forced_to_carry_economics():
    before = _base_strategy('TASK_SCOPED')
    def base(request, *args, **kwargs):
        return deepcopy(before)
    out = mod.wrap_build_master_strategy(base)({'delivery_mode': 'TASK_SCOPED'}, economics=_economics(_phase2('READY')))
    assert out == before
