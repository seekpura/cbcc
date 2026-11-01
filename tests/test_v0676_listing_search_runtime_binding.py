from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).parents[1]


def test_phase2_closure_installs_listing_and_seven_tool_authority_wrappers():
    text=(ROOT/'runtime/cbcc/v0676_phase2_closure.py').read_text(encoding='utf-8')
    assert 'listing_search_authority' in text
    assert 'wrap_compile_listing' in text
    assert 'SEVEN_TOOL_LISTING_BUSINESS_READINESS_BRIDGE' in text


def test_compiler_passes_real_phase2_context_and_materializes_dedicated_listing_authority():
    text=(ROOT/'runtime/cbcc/compiler.py').read_text(encoding='utf-8')
    assert 'phase2_context=' in text
    assert "'pricing_economics':pricing_economics" in text
    assert "'market_analysis':domain.get('market')" in text
    assert "artifacts/listing_search_authority.json" in text


def test_canonical_graph_prefers_dedicated_phase2_listing_search_authority():
    text=(ROOT/'runtime/cbcc/canonical_commerce_graph.py').read_text(encoding='utf-8')
    assert 'NodeSpec("LISTING_SEARCH", "Listing / Search", ("listing_search_authority.json", "listing_analysis.json", "listing.json", "listing_compile.json")' in text
