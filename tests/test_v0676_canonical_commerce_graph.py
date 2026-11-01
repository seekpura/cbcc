from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import sys

MODULE = Path(__file__).parents[1] / "runtime/cbcc/canonical_commerce_graph.py"
spec = importlib.util.spec_from_file_location("canonical_commerce_graph", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def dump(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def fixture(tmp_path: Path) -> Path:
    art = tmp_path / "artifacts"
    dump(tmp_path / "meta/request.json", {"project_id": "K01", "target": {"market": "MY"}})
    dump(art / "evidence.json", {"sources": [{"source_id": "xlsx"}]})
    dump(art / "product_truth.json", {"product": {"name": "K01"}, "claims": []})
    dump(art / "research_gate.json", {"status": "READY", "actions": []})
    dump(art / "culture_context.json", {"status": "READY"})
    dump(art / "pricing_economics_authority.json", {"status": "MISSING_INPUT"})
    dump(art / "strategy_authority.json", {"sections": {
        "01_information_completeness_assumptions_decisions": {"status": "READY"},
        "05_visual_photography_strategy": {"thesis": "editorial"},
        "06_platform_content_matrix": [{"surface": "Gallery"}],
        "07_race_execution_table": [{"stage": "Action"}],
        "08_culture_adaptation_checklist": [{"dimension": "casting"}],
        "09_risk_measurement_priority_next_steps": {"metric": "CTR"},
    }})
    dump(art / "listing.json", {"title": "target copy"})
    dump(art / "asset_architecture.json", {"status": "DYNAMIC_ASSET_ARCHITECTURE", "assets": []})
    dump(art / "video_creator_plan.json", {"status": "READY"})
    dump(art / "ad_analysis.json", {"status": "READY"})
    dump(art / "feedback_analysis.json", {"status": "READY"})
    dump(art / "compliance_report.json", {"status": "READY"})
    dump(art / "operator_execution_board.json", {"status": "READY"})
    dump(art / "execution_contract.json", {"objects": []})
    return art


def test_graph_is_relationship_authority_not_second_business_payload(tmp_path):
    art = fixture(tmp_path)
    graph = mod.build_canonical_commerce_graph(art)
    assert graph["status"] == "CANONICAL_GRAPH_READY"
    assert graph["canonical_payload_policy"] == "REFERENCE_AND_HASH_ONLY"
    assert graph["node_order"] == [s.node_id for s in mod.NODE_SPECS]
    assert graph["node_order"][:5] == ["PROJECT", "SOURCES", "INFORMATION_AUDIT", "PRODUCT_TRUTH", "RESEARCH"]
    assert graph["node_order"][-4:] == ["COMPLIANCE", "MEASUREMENT", "OPERATIONS", "PRODUCTION_REVIEW"]
    assert all("payload" not in node for node in graph["nodes"])
    assert len(graph["edges"]) == len(graph["nodes"]) - 1


def test_json_is_canonical_and_human_prompt_package_are_projection_only(tmp_path):
    graph = mod.build_canonical_commerce_graph(fixture(tmp_path))
    roles = {row["surface"]: row["role"] for row in graph["projection_surfaces"]}
    assert roles == {
        "JSON": "CANONICAL_AUTHORITY",
        "MARKDOWN": "PROJECTION_ONLY",
        "HTML": "PROJECTION_ONLY",
        "MODEL_PROMPT": "PROJECTION_ONLY",
        "ASSET_PACKAGE": "PROJECTION_ONLY",
    }


def test_graph_hash_changes_when_canonical_authority_changes(tmp_path):
    art = fixture(tmp_path)
    before = mod.build_canonical_commerce_graph(art)
    truth_path = art / "product_truth.json"
    dump(truth_path, {"product": {"name": "K01", "spec": "30g"}, "claims": []})
    after = mod.build_canonical_commerce_graph(art)
    assert before["graph_sha256"] != after["graph_sha256"]
    bnode = next(n for n in before["nodes"] if n["node_id"] == "PRODUCT_TRUTH")
    anode = next(n for n in after["nodes"] if n["node_id"] == "PRODUCT_TRUTH")
    assert bnode["authority_sha256"] != anode["authority_sha256"]


def test_required_missing_fails_closed_without_fabricating(tmp_path):
    art = fixture(tmp_path)
    (art / "product_truth.json").unlink()
    graph = mod.build_canonical_commerce_graph(art)
    assert graph["status"] == "CANONICAL_GRAPH_INCOMPLETE"
    assert "PRODUCT_TRUTH" in graph["required_missing"]
    node = next(n for n in graph["nodes"] if n["node_id"] == "PRODUCT_TRUTH")
    assert node["authority_ref"] is None
    assert node["authority_sha256"] is None


def test_materialization_is_deterministic(tmp_path):
    art = fixture(tmp_path)
    one = mod.materialize_canonical_commerce_graph(art)
    first = (art / "canonical_commerce_graph.json").read_bytes()
    two = mod.materialize_canonical_commerce_graph(art)
    second = (art / "canonical_commerce_graph.json").read_bytes()
    assert one == two
    assert first == second



def test_optional_missing_domains_are_to_verify_with_why_not_invented_not_active(tmp_path):
    art = fixture(tmp_path)
    for rel in (
        "culture_context.json", "pricing_economics_authority.json", "listing.json",
        "video_creator_plan.json", "ad_analysis.json", "feedback_analysis.json",
        "compliance_report.json", "operator_execution_board.json", "execution_contract.json",
    ):
        path = art / rel
        if path.exists():
            path.unlink()
    graph = mod.build_canonical_commerce_graph(art)
    optional_missing = [n for n in graph["nodes"] if not n["required"] and n["authority_ref"] is None]
    assert optional_missing
    assert all(n["status"] == "TO_VERIFY" for n in optional_missing)
    assert all(str(n.get("why") or "").strip() for n in optional_missing)
    assert not any(n["status"] == "NOT_ACTIVE" for n in optional_missing)


def test_first_class_business_nodes_do_not_fallback_to_strategy_or_seven_agent(tmp_path):
    art = fixture(tmp_path)
    for rel in ("listing.json", "ad_analysis.json", "feedback_analysis.json"):
        (art / rel).unlink()
    dump(art / "seven_agent_synthesis.json", {
        "listing": {"title": "must not substitute"},
        "ads": {"status": "READY"},
        "reviews": {"status": "READY"},
    })
    graph = mod.build_canonical_commerce_graph(art)
    nodes = {n["node_id"]: n for n in graph["nodes"]}
    for node_id in ("LISTING_SEARCH", "ADS", "REVIEWS"):
        assert nodes[node_id]["authority_ref"] is None
        assert nodes[node_id]["status"] == "TO_VERIFY"
        assert str(nodes[node_id].get("why") or "").strip()
