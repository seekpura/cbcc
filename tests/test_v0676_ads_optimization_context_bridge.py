from __future__ import annotations
from pathlib import Path
import importlib.util, sys

ROOT=Path(__file__).parents[1]
MODULE=ROOT/'runtime/cbcc/ads_optimization_authority.py'
spec=importlib.util.spec_from_file_location('ads_opt_context_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)

FIX=ROOT/'tests/test_v0676_ads_optimization_authority.py'
fspec=importlib.util.spec_from_file_location('ads_opt_fixture_context_v0676',FIX)
fx=importlib.util.module_from_spec(fspec); assert fspec and fspec.loader
sys.modules[fspec.name]=fx; fspec.loader.exec_module(fx)


def test_pricing_context_bridge_hands_final_phase2_economics_to_direct_ads_analysis_once():
    req=fx.request(); req['ad_analysis']={'ad_data':{'impressions':100,'clicks':5,'orders':1,'spend':10,'revenue':59}}
    p=mod.wrap_compile_pricing_economics_for_ads_context(lambda request, market_analysis=None, legacy_economics=None: fx.pricing())
    a=mod.wrap_analyze_ads(lambda *args,**kwargs: {'status':'CALCULATED_FROM_INPUTS','metrics':{'cpa':10,'roas':5.9}})
    p(req,None,None)
    first=a({})
    assert first['phase2_business_status']=='READY'
    assert first['phase2_ads_optimization_authority']['economics_context']['break_even_cpa']==17.0
    second=a({})
    assert 'phase2_ads_optimization_authority' not in second


def test_portfolio_wrapper_prevents_internal_analyze_ads_from_consuming_context_early():
    req=fx.request(); req['ad_rows']=[{'campaign_id':'C1','impressions':100,'clicks':5,'orders':1,'spend':10,'revenue':59}]
    p=mod.wrap_compile_pricing_economics_for_ads_context(lambda request, market_analysis=None, legacy_economics=None: fx.pricing())
    direct=mod.wrap_analyze_ads(lambda *args,**kwargs: {'status':'CALCULATED_FROM_INPUTS','metrics':{'cpa':10}})
    internal=[]
    def base_portfolio(*args,**kwargs):
        inner=direct({}); internal.append(inner)
        return fx.legacy_ads()
    portfolio=mod.wrap_analyze_ad_portfolio(base_portfolio)
    p(req,None,None)
    out=portfolio([])
    assert 'phase2_ads_optimization_authority' not in internal[0]
    assert out['phase2_business_status']=='READY'
    assert out['phase2_ads_optimization_authority']['status']=='READY'


def test_request_without_ad_analysis_scope_clears_context_and_cannot_contaminate_later_ads_call():
    p=mod.wrap_compile_pricing_economics_for_ads_context(lambda request, market_analysis=None, legacy_economics=None: fx.pricing())
    a=mod.wrap_analyze_ads(lambda *args,**kwargs: {'status':'CALCULATED_FROM_INPUTS'})
    req=fx.request(); req.pop('advertising_optimization',None)
    p(req,None,None)
    out=a({})
    assert 'phase2_ads_optimization_authority' not in out


def test_explicit_ads_optimization_without_performance_data_materializes_no_data_authority_without_running_metrics_calculator():
    req=fx.request()
    assert 'ad_rows' not in req and 'ad_analysis' not in req
    p=mod.wrap_compile_pricing_economics_for_ads_context(lambda request, market_analysis=None, legacy_economics=None: fx.pricing())
    p(req,None,None)
    assert (req.get('ad_analysis') or {}).get('_phase2_no_performance_data') is True
    def must_not_run(*args,**kwargs):
        raise AssertionError('metrics calculator must not run when performance data is absent')
    a=mod.wrap_analyze_ads(must_not_run)
    out=a({})
    assert out['status']=='NO_AD_PERFORMANCE_DATA_SUPPLIED'
    assert out['phase2_business_status']=='READY'
    assert out['phase2_ads_optimization_authority']['performance_analysis']['status']=='NO_AD_PERFORMANCE_DATA_SUPPLIED'
