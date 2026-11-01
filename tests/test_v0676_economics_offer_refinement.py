from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

MODULE = Path(__file__).parents[1] / 'runtime/cbcc/economics_offer_refinement_v0676.py'
spec = importlib.util.spec_from_file_location('economics_offer_refinement_v0676', MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def _base(target=False):
    return {
        'status':'READY',
        'input_integrity':{
            'price':{'status':'EXPLICIT','exact_fact':59,'assumption_boundary':None,'downstream_use':['listing']},
            'payment_fee':{'status':'EXPLICIT','exact_fact':0.0,'assumption_boundary':None,'downstream_use':['ads']},
            'target_contribution':{'status':'EXPLICIT' if target else 'BASELINE_ONLY','exact_fact':8 if target else None,'assumption_boundary':None,'downstream_use':['ads']},
        },
        'pricing_decision':{'density_status':'READY','what':'price','why':'why','exact_fact':'MYR59','assumption_boundary':None,'confidence':'MEDIUM'},
        'offer_decision':{'density_status':'READY','what':'offer','why':'why','exact_fact':'no discount','assumption_boundary':None,'confidence':'MEDIUM'},
        'break_even':{
            'cpa':{'status':'AVAILABLE','value':17,'required_inputs':['price']},
            'cpc':{'status':'AVAILABLE','value':0.68,'required_inputs':['break_even_cpa','click_to_order_cvr']},
            'roas':{'status':'AVAILABLE','value':3.47,'required_inputs':['price']},
        },
    }


def test_zero_target_is_labeled_baseline_and_lineage_is_completed():
    request={'offer_economics':{'price':59,'payment_fee':0.0,'pricing_decision':{'source_refs':['SRC-P']},'offer_decision':{'source_refs':['SRC-O']}}}
    out=mod.refine_economics_offer_authority(_base(False),request)
    assert all(out['break_even'][x]['status']=='BASELINE_ZERO_CONTRIBUTION_FLOOR_ONLY' for x in ('cpa','cpc','roas'))
    assert out['req088_lineage_status']=='READY'
    for row in list(out['input_integrity'].values())+[out['pricing_decision'],out['offer_decision']]:
        assert all(k in row for k in mod.LINEAGE_FIELDS)
    assert mod.refinement_issues(out)==[]


def test_explicit_target_keeps_operating_boundary_available():
    request={'offer_economics':{'price':59,'target_contribution':8}}
    out=mod.refine_economics_offer_authority(_base(True),request)
    assert out['break_even']['cpa']['status']=='AVAILABLE'
    assert out['break_even']['roas']['status']=='AVAILABLE'
