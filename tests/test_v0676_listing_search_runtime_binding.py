from __future__ import annotations
from pathlib import Path
import importlib.util
import json
import sys

ROOT=Path(__file__).parents[1]


def test_phase2_closure_installs_real_pricing_to_listing_context_and_seven_tool_wrappers():
    text=(ROOT/'runtime/cbcc/v0676_phase2_closure.py').read_text(encoding='utf-8')
    assert 'listing_search_authority' in text
    assert 'wrap_compile_pricing_economics_for_listing_context' in text
    assert 'wrap_compile_listing' in text
    assert 'SEVEN_TOOL_LISTING_BUSINESS_READINESS_BRIDGE' in text


def test_canonical_graph_prefers_existing_real_listing_analysis_over_legacy_aliases(tmp_path: Path):
    path=ROOT/'runtime/cbcc/canonical_commerce_graph.py'
    spec=importlib.util.spec_from_file_location('canonical_graph_listing_v0676',path)
    mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
    sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
    art=tmp_path/'artifacts'; art.mkdir(parents=True)
    (tmp_path/'meta').mkdir()
    (tmp_path/'meta/request.json').write_text('{}',encoding='utf-8')
    (art/'evidence.json').write_text(json.dumps({'sources':[]}),encoding='utf-8')
    (art/'product_truth.json').write_text('{}',encoding='utf-8')
    (art/'strategy_authority.json').write_text(json.dumps({'sections':{'01_information_completeness_assumptions_decisions':{}}}),encoding='utf-8')
    (art/'listing_analysis.json').write_text(json.dumps({'compiled':{'phase2_listing_search_authority':{'status':'READY'}}}),encoding='utf-8')
    (art/'listing.json').write_text(json.dumps({'title':'legacy alias must not win'}),encoding='utf-8')
    graph=mod.build_canonical_commerce_graph(art)
    listing=next(row for row in graph['nodes'] if row['node_id']=='LISTING_SEARCH')
    assert listing['status']=='CANONICAL_AUTHORITY_BOUND'
    assert listing['authority_ref']=='listing_analysis.json'
