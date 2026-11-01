from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).parents[1]
GRAPH_MODULE = ROOT / 'runtime/cbcc/canonical_commerce_graph.py'
spec = importlib.util.spec_from_file_location('canonical_commerce_graph_v0676_market_binding', GRAPH_MODULE)
graph_mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = graph_mod
spec.loader.exec_module(graph_mod)


def dump(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')


def test_runtime_package_init_wraps_real_market_analyzer():
    text = (ROOT / 'runtime/cbcc/__init__.py').read_text(encoding='utf-8')
    assert 'market_research_authority as _market_research_authority' in text
    assert '_market.analyze_market = _market_research_authority.wrap_analyze_market(' in text


def test_canonical_graph_prefers_enriched_market_analysis_over_research_gate(tmp_path):
    art = tmp_path / 'artifacts'
    dump(tmp_path / 'meta/request.json', {'project_id':'P'})
    dump(art / 'evidence.json', {'sources':[]})
    dump(art / 'product_truth_evidence_authority.json', {'status':'PRODUCT_TRUTH_READY'})
    dump(art / 'strategy_authority.json', {'sections':{'01_information_completeness_assumptions_decisions':{}}})
    dump(art / 'market_analysis.json', {'research_authority': {'schema':'cbcc-market-research-authority-v1'}})
    dump(art / 'research_gate.json', {'status':'READY'})
    graph = graph_mod.build_canonical_commerce_graph(art)
    research = next(row for row in graph['nodes'] if row['node_id'] == 'RESEARCH')
    assert research['authority_ref'] == 'market_analysis.json'
