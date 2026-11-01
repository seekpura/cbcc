from __future__ import annotations
from pathlib import Path
import importlib.util, sys, pytest

ROOT=Path(__file__).parents[1]
MODULE=ROOT/'runtime/cbcc/ads_optimization_authority.py'
spec=importlib.util.spec_from_file_location('ads_opt_review_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
FIX=ROOT/'tests/test_v0676_ads_optimization_authority.py'
fspec=importlib.util.spec_from_file_location('ads_opt_fixture_review_v0676',FIX)
fx=importlib.util.module_from_spec(fspec); assert fspec and fspec.loader
sys.modules[fspec.name]=fx; fspec.loader.exec_module(fx)


def test_ads_offer_must_match_verified_phase2_offer_decision():
    req=fx.request(); req['advertising_optimization']['rows'][0]['offer']='20% launch discount'
    out=mod.materialize_ads_optimization_authority(fx.legacy_ads(),req,fx.pricing())
    row=out['optimization_rows'][0]
    assert row['offer_alignment_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_ADS_OFFER_ALIGNMENT_INCOMPLETE_V0676' for x in mod.ads_optimization_issues(out))


def test_ads_test_contract_requires_machine_auditable_variable_isolation_and_decision_rules():
    req=fx.request(); row=req['advertising_optimization']['rows'][0]
    for k in ('test_variable','hold_constant','success_rule','failure_rule'):
        row.pop(k,None)
    out=mod.materialize_ads_optimization_authority(fx.legacy_ads(),req,fx.pricing())
    rr=out['optimization_rows'][0]
    assert rr['business_contract_status']=='TO_VERIFY'
    assert set(rr['business_contract_gaps']) >= {'test_variable','hold_constant','success_rule','failure_rule'}


def test_ads_spend_boundary_requires_explicit_binding_to_phase2_economics_authority():
    req=fx.request(); req['advertising_optimization']['rows'][0].pop('economics_boundary_ref')
    out=mod.materialize_ads_optimization_authority(fx.legacy_ads(),req,fx.pricing())
    rr=out['optimization_rows'][0]
    assert rr['economics_binding_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_ADS_ECONOMICS_BINDING_INCOMPLETE_V0676' for x in mod.ads_optimization_issues(out))


def test_ads_context_is_cleared_when_direct_analyzer_raises():
    req=fx.request(); req['ad_analysis']={'ad_data':{'impressions':1}}
    p=mod.wrap_compile_pricing_economics_for_ads_context(lambda request, market_analysis=None, legacy_economics=None: fx.pricing())
    boom=mod.wrap_analyze_ads(lambda *args,**kwargs: (_ for _ in ()).throw(RuntimeError('boom')))
    p(req,None,None)
    with pytest.raises(RuntimeError): boom({})
    safe=mod.wrap_analyze_ads(lambda *args,**kwargs: {'status':'CALCULATED_FROM_INPUTS'})
    assert 'phase2_ads_optimization_authority' not in safe({})


def test_pricing_bridge_clears_prior_ads_context_before_upstream_exception():
    req=fx.request(); req['ad_analysis']={'ad_data':{'impressions':1}}
    seed=mod.wrap_compile_pricing_economics_for_ads_context(lambda request, market_analysis=None, legacy_economics=None: fx.pricing())
    seed(req,None,None)
    fail=mod.wrap_compile_pricing_economics_for_ads_context(lambda *args,**kwargs: (_ for _ in ()).throw(RuntimeError('pricing boom')))
    with pytest.raises(RuntimeError): fail(req,None,None)
    safe=mod.wrap_analyze_ads(lambda *args,**kwargs: {'status':'CALCULATED_FROM_INPUTS'})
    assert 'phase2_ads_optimization_authority' not in safe({})


def test_no_performance_stub_does_not_claim_platform_attribution_available():
    req=fx.request()
    legacy={'status':'NO_AD_PERFORMANCE_DATA_SUPPLIED','metrics':{},'incrementality':{'status':'NOT_ESTABLISHED','signals':{}}}
    out=mod.materialize_ads_optimization_authority(legacy,req,fx.pricing())
    assert out['attribution_boundary']['platform_attribution_status']=='NOT_SUPPLIED'


def test_authored_incrementality_label_cannot_bypass_missing_counterfactual_evidence():
    req=fx.request()
    req['advertising_optimization']['incrementality_decision']={'status':'ESTABLISHED','evidence':['SRC-ADS']}
    out=mod.materialize_ads_optimization_authority(fx.legacy_ads(),req,fx.pricing())
    assert out['attribution_boundary']['incrementality_status']!='ESTABLISHED'
    assert out['attribution_boundary']['causal_sales_claim_allowed'] is False


def test_internal_no_performance_stub_is_removed_from_original_request_after_consumption():
    req=fx.request()
    p=mod.wrap_compile_pricing_economics_for_ads_context(lambda request, market_analysis=None, legacy_economics=None: fx.pricing())
    p(req,None,None)
    assert (req.get('ad_analysis') or {}).get('_phase2_no_performance_data') is True
    a=mod.wrap_analyze_ads(lambda *args,**kwargs: (_ for _ in ()).throw(AssertionError('calculator must not run')))
    out=a({})
    assert out['phase2_business_status']=='READY'
    assert 'ad_analysis' not in req
