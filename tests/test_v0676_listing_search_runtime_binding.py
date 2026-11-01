from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).parents[1]


def test_phase2_closure_installs_real_pricing_to_listing_context_and_seven_tool_wrappers():
    text=(ROOT/'runtime/cbcc/v0676_phase2_closure.py').read_text(encoding='utf-8')
    assert 'listing_search_authority' in text
    assert 'wrap_compile_pricing_economics_for_listing_context' in text
    assert 'wrap_compile_listing' in text
    assert 'SEVEN_TOOL_LISTING_BUSINESS_READINESS_BRIDGE' in text


def test_canonical_graph_binds_the_existing_real_listing_analysis_as_first_class_listing_search_authority():
    text=(ROOT/'runtime/cbcc/canonical_commerce_graph.py').read_text(encoding='utf-8')
    assert 'NodeSpec("LISTING_SEARCH", "Listing / Search", ("listing_analysis.json", "listing.json", "listing_compile.json")' in text
