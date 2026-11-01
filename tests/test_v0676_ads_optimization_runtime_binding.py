from __future__ import annotations
from pathlib import Path
import importlib.util, sys, json

ROOT=Path(__file__).parents[1]
MODULE=ROOT/'runtime/cbcc/ads_optimization_authority.py'
spec=importlib.util.spec_from_file_location('ads_optimization_runtime_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)

FIX=ROOT/'tests/test_v0676_ads_optimization_authority.py'
fspec=importlib.util.spec_from_file_location('ads_opt_fixture_v0676',FIX)
fx=importlib.util.module_from_spec(fspec); assert fspec and fspec.loader
sys.modules[fspec.name]=fx; fspec.loader.exec_module(fx)


def test_domain_compiler_preserves_mature_ads_payload_and_adds_phase2_business_authority():
    out=mod.compile_ads_optimization_domain(fx.legacy_ads(),fx.request(),fx.pricing())
    assert out['status']=='PORTFOLIO_CALCULATED'
    assert out['rows']==fx.legacy_ads()['rows']
    assert out['phase2_business_status']=='READY'
    assert out['phase2_ads_optimization_authority']['status']=='READY'


def test_seven_tool_bridge_separates_ads_legacy_status_from_business_readiness():
    ads=mod.compile_ads_optimization_domain(fx.legacy_ads(),fx.request(),fx.pricing())
    domain={'ads':ads}
    def base(**kwargs):
        return {'status':'SEVEN_TOOL_CONTINUITY_COMPILED','capabilities':[{'id':'06_ADVERTISING_OPTIMIZATION','project_status':'PORTFOLIO_CALCULATED','evidence':{}}]}
    out=mod.wrap_compile_seven_tool_continuity(base)(domain=domain)
    row=out['capabilities'][0]
    assert row['project_status']=='PORTFOLIO_CALCULATED'
    assert row['business_readiness_status']=='READY'
    assert row['evidence']['ads_business_readiness_status']=='READY'
    assert out['ads_optimization_integrity']['business_readiness_status']=='READY'


def test_phase2_closure_installs_ads_context_analyzers_and_seven_tool_readiness_bridge():
    text=(ROOT/'runtime/cbcc/v0676_phase2_closure.py').read_text(encoding='utf-8')
    assert 'ads_optimization_authority' in text
    assert 'wrap_compile_pricing_economics_for_ads_context' in text
    assert 'wrap_analyze_ads' in text
    assert 'wrap_analyze_ad_portfolio' in text
    assert 'SEVEN_TOOL_ADS_BUSINESS_READINESS_BRIDGE' in text
    assert 'ADS_OPTIMIZATION_ECONOMICS_CONTEXT_BRIDGE' in text


def test_canonical_graph_prefers_enriched_ad_analysis_over_paid_campaign_architecture(tmp_path:Path):
    gpath=ROOT/'runtime/cbcc/canonical_commerce_graph.py'
    gspec=importlib.util.spec_from_file_location('canonical_ads_v0676',gpath)
    g=importlib.util.module_from_spec(gspec); assert gspec and gspec.loader
    sys.modules[gspec.name]=g; gspec.loader.exec_module(g)
    art=tmp_path/'artifacts'; art.mkdir(parents=True)
    (tmp_path/'meta').mkdir()
    (tmp_path/'meta/request.json').write_text('{}')
    (art/'evidence.json').write_text(json.dumps({'sources':[]}))
    (art/'product_truth.json').write_text('{}')
    (art/'research_gate.json').write_text('{}')
    (art/'strategy_authority.json').write_text(json.dumps({'sections':{'01_information_completeness_assumptions_decisions':{}}}))
    (art/'ad_analysis.json').write_text(json.dumps({'phase2_ads_optimization_authority':{'status':'READY'}}))
    (art/'paid_campaign_architecture.json').write_text(json.dumps({'status':'COMPILED'}))
    graph=g.build_canonical_commerce_graph(art)
    node=next(x for x in graph['nodes'] if x['node_id']=='ADS')
    assert node['authority_ref']=='ad_analysis.json'
