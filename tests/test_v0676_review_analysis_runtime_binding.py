from __future__ import annotations
from pathlib import Path
import importlib.util, sys, json

ROOT=Path(__file__).parents[1]
MODULE=ROOT/'runtime/cbcc/review_analysis_authority.py'
spec=importlib.util.spec_from_file_location('review_analysis_runtime_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
FIX=ROOT/'tests/test_v0676_review_analysis_authority.py'
fspec=importlib.util.spec_from_file_location('review_analysis_fixture_runtime_v0676',FIX)
fx=importlib.util.module_from_spec(fspec); assert fspec and fspec.loader
sys.modules[fspec.name]=fx; fspec.loader.exec_module(fx)


def test_domain_bridge_preserves_legacy_feedback_and_adds_phase2_authority():
    out=mod.compile_review_analysis_domain(fx.legacy_feedback(),fx.request())
    assert out['status']=='AGGREGATED_FROM_CLASSIFIED_INPUT'
    assert out['summary']==fx.legacy_feedback()['summary']
    assert out['phase2_business_status']=='READY'
    assert out['phase2_review_analysis_authority']['status']=='READY'


def test_seven_tool_review_bridge_separates_legacy_status_from_business_readiness():
    feedback=mod.compile_review_analysis_domain(fx.legacy_feedback(),fx.request())
    def base(**kwargs):
        return {'status':'SEVEN_TOOL_CONTINUITY_COMPILED','capabilities':[{'id':'07_REVIEW_ANALYSIS','project_status':'AGGREGATED_FROM_CLASSIFIED_INPUT','evidence':{}}]}
    out=mod.wrap_compile_seven_tool_continuity(base)(domain={'feedback':feedback})
    row=out['capabilities'][0]
    assert row['project_status']=='AGGREGATED_FROM_CLASSIFIED_INPUT'
    assert row['business_readiness_status']=='READY'
    assert row['evidence']['review_business_readiness_status']=='READY'
    assert out['review_analysis_integrity']['business_readiness_status']=='READY'


def test_canonical_graph_reviews_bind_feedback_analysis_not_production_review_workspace(tmp_path:Path):
    gpath=ROOT/'runtime/cbcc/canonical_commerce_graph.py'
    if not gpath.exists():
        return
    gspec=importlib.util.spec_from_file_location('canonical_review_v0676',gpath)
    g=importlib.util.module_from_spec(gspec); assert gspec and gspec.loader
    sys.modules[gspec.name]=g; gspec.loader.exec_module(g)
    art=tmp_path/'artifacts'; art.mkdir(parents=True)
    (tmp_path/'meta').mkdir()
    (tmp_path/'meta/request.json').write_text('{}')
    (art/'evidence.json').write_text(json.dumps({'sources':[]}))
    (art/'product_truth.json').write_text('{}')
    (art/'research_gate.json').write_text('{}')
    (art/'strategy_authority.json').write_text(json.dumps({'sections':{'01_information_completeness_assumptions_decisions':{}}}))
    (art/'feedback_analysis.json').write_text(json.dumps({'phase2_review_analysis_authority':{'status':'READY'}}))
    (art/'execution_contract.json').write_text(json.dumps({'review':'production-output-review'}))
    graph=g.build_canonical_commerce_graph(art)
    node=next(x for x in graph['nodes'] if x['node_id']=='REVIEWS')
    assert node['authority_ref']=='feedback_analysis.json'
