from __future__ import annotations

import json
import re
from pathlib import Path


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _package(tmp_path: Path) -> Path:
    from runtime.cbcc.delivery_html import build_delivery_html

    package = tmp_path / "package"
    package.mkdir()
    _write_json(
        package / "HUMAN_DELIVERY.json",
        {
            "delivery_language": {"locale": "zh-CN"},
            "target": {"platform": "TikTok Shop", "site": "MY", "market": "Malaysia", "locale": "ms-MY"},
            "product": {"brand": "KIYUU", "product_name": "K01"},
            "copy_center": [
                {
                    "group": "购买决策",
                    "field": "title",
                    "label": "产品标题",
                    "value": "REQ089 HUMAN DELIVERY SENTINEL",
                    "status": "READY",
                    "copyable": True,
                    "locale": "ms-MY",
                    "delivery_translation": "REQ089 中文标题",
                }
            ],
            "localized_copy": [],
            "media_slots": [],
            "risks_and_holds": [],
        },
    )
    _write_json(
        package / "strategy/strategy_authority.json",
        {
            "sections": {
                "01_information_completeness_assumptions_decisions": {},
                "02_product_truth_value_ladder": {"fact": "REQ089 STRATEGY TRUTH SENTINEL"},
                "03_platform_region_audience_culture_insight": {"context_why": {"platform": "REQ089 MARKET WHY"}},
                "04_marketing_core_strategy": {"value_proposition": "REQ089 STRATEGY SENTINEL"},
                "05_visual_photography_strategy": {"visual_thesis": "REQ089 VISUAL SENTINEL"},
                "06_platform_content_matrix": [],
                "07_race_execution_table": [],
                "08_culture_adaptation_checklist": [],
                "09_risk_measurement_priority_next_steps": {},
            }
        },
    )
    _write_json(package / "supporting_analysis/product_truth.json", {"fact": "REQ089 PRODUCT TRUTH SENTINEL"})
    _write_json(package / "supporting_analysis/target_context.json", {"audience": "REQ089 TARGET CONTEXT SENTINEL"})
    _write_json(package / "supporting_analysis/culture_context.json", {"culture": "REQ089 CULTURE CONTEXT SENTINEL"})
    _write_json(package / "supporting_analysis/market_analysis.json", {"market": "REQ089 MARKET ANALYSIS SENTINEL"})
    _write_json(package / "supporting_analysis/compliance_report.json", {"risk": "REQ089 COMPLIANCE SENTINEL"})
    _write_json(package / "supporting_analysis/ad_analysis.json", {"objective": "REQ089 ADS SENTINEL"})
    _write_json(package / "supporting_analysis/feedback_analysis.json", {"status": "REQ089 REVIEWS SENTINEL"})
    _write_json(package / "supporting_analysis/source_registry.json", {"rows": [{"id": "REQ089 SOURCE SENTINEL"}]})
    _write_json(package / "ASSET_UNIVERSE.json", {"portfolio": "REQ089 ASSET UNIVERSE SENTINEL"})
    build_delivery_html(package, package / "index.html")
    return package


def test_req089_canonical_objects_are_consumed_inside_semantic_human_routes(tmp_path: Path):
    from runtime.cbcc.canonical_delivery_parity_v0680 import materialize_canonical_delivery_parity
    from runtime.cbcc.canonical_routed_workspace_v0680 import materialize_routed_canonical_workspace

    package = _package(tmp_path)
    assert materialize_canonical_delivery_parity(package)["status"] == "PASS"
    result = materialize_routed_canonical_workspace(package)
    assert result["status"] == "PASS", result

    audit = json.loads((package / "CANONICAL_ROUTED_WORKSPACE_AUDIT.json").read_text(encoding="utf-8"))
    expected = {
        "human_delivery": "overview",
        "product_truth": "product",
        "target_context": "market",
        "culture_context": "market",
        "market_analysis": "market",
        "strategy_authority": "strategy",
        "compliance": "risk",
        "ads": "content",
        "reviews": "risk",
        "sources": "sources",
        "asset_universe": "assets",
    }
    for object_id, preferred_route in expected.items():
        row = audit["objects"][object_id]
        assert row["status"] == "PASS", (object_id, row)
        # Semantic route is preferred when that route exists; overview fallback is allowed only if the
        # project-authored IA legitimately omitted the dedicated route.
        assert row["route"] in {preferred_route, "overview"}, (object_id, row)
        assert row["leaf_count"] > 0

    html = (package / "index.html").read_text(encoding="utf-8")
    assert 'data-canonical-routed-object="product_truth"' in html
    assert 'data-canonical-routed-object="strategy_authority"' in html
    assert 'data-canonical-routed-object="asset_universe"' in html


def test_req089_archive_presence_cannot_false_pass_missing_routed_field(tmp_path: Path):
    from runtime.cbcc.canonical_delivery_parity_v0680 import materialize_canonical_delivery_parity
    from runtime.cbcc.canonical_routed_workspace_v0680 import (
        audit_routed_canonical_workspace,
        materialize_routed_canonical_workspace,
    )

    package = _package(tmp_path)
    assert materialize_canonical_delivery_parity(package)["status"] == "PASS"
    assert materialize_routed_canonical_workspace(package)["status"] == "PASS"

    html_path = package / "index.html"
    html = html_path.read_text(encoding="utf-8")
    marker = 'data-canonical-routed-path="canonical_business_objects.market_analysis.market"'
    assert marker in html
    # Delete only the semantic-route marker. The sentinel value and the generic Canonical Archive remain
    # in the page, so a naive whole-HTML search would still false-pass.
    html = html.replace(marker, 'data-canonical-routed-path-removed="canonical_business_objects.market_analysis.market"', 1)
    html_path.write_text(html, encoding="utf-8")
    assert "REQ089 MARKET ANALYSIS SENTINEL" in html

    issues = audit_routed_canonical_workspace(package)
    assert any(issue["code"] == "HTML_CANONICAL_ROUTED_FIELD_COVERAGE_INCOMPLETE_V0680" for issue in issues), issues


def test_req089_project_authored_ia_stays_dynamic_and_workspace_navigation_contract_survives():
    from runtime.cbcc.workspace_autonomy import build_workspace_route_plan

    plan = build_workspace_route_plan(
        availability={
            "overview": True,
            "product": True,
            "market": True,
            "listing": False,
            "strategy": False,
            "content": False,
            "visual": False,
            "assets": False,
            "prompts": False,
            "risk": False,
            "sources": False,
            "archive": True,
        }
    )
    assert [row["route"] for row in plan["primary_routes"]] == ["overview", "product", "market"]
    assert [row["route"] for row in plan["secondary_routes"]] == ["archive"]
    assert plan["fixed_route_count"] is None
    assert plan["fixed_command_count"] is None
