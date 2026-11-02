from __future__ import annotations

import json
import zipfile
from pathlib import Path


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _materialize_mature_surface(package: Path) -> None:
    text_files = {
        "index.html": "<html><body>成熟交付工作区</body></html>\n",
        "00_PROJECT_HUB.md": "# 项目中心\n",
        "strategy/MASTER_STRATEGY_CN.md": "# 中文策略\n",
        "01_LISTING_UPLOAD_READY.md": "# 上架资料\n\n## 商品标题\n待真实商品数据投影。\n",
    }
    for rel, text in text_files.items():
        path = package / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    for rel in (
        "HUMAN_DELIVERY.json",
        "PLATFORM_SCOPE.json",
        "SOURCE_TRUTH_MEDIA_AUDIT.json",
        "strategy/STRATEGY_DECISION_INDEX.json",
        "strategy/COMMERCE_DECISION_CONTEXT.json",
        "strategy/COMMERCIAL_CONTINUITY_AUDIT.json",
        "supporting_analysis/product_truth.json",
        "supporting_analysis/target_context.json",
        "supporting_analysis/culture_context.json",
        "supporting_analysis/asset_architecture.json",
        "supporting_analysis/seven_agent_synthesis.json",
    ):
        _write_json(package / rel, {"status": "READY"})

    # These are audit surfaces, not generic workfiles: the mature-package checker requires an
    # explicit PASS rather than a placeholder READY status.
    for rel in (
        "FULL_DELIVERY_DEPTH_AUDIT.json",
        "HUMAN_LANGUAGE_AUDIT.json",
        "DELIVERY_LANGUAGE_MATRIX_AUDIT.json",
    ):
        _write_json(package / rel, {"status": "PASS"})

    # The packaged strategy authority must expose the canonical nine-section contract even for
    # this task-scoped lineage fixture. We intentionally leave deep FULL-only payloads out here;
    # REQ-088 is not allowed to invent strategy content merely to satisfy package shape.
    _write_json(
        package / "strategy/strategy_authority.json",
        {
            "status": "TASK_SCOPED",
            "sections": {
                "01_information_completeness_assumptions_decisions": {},
                "02_product_truth_value_ladder": {},
                "03_platform_region_audience_culture_insight": {},
                "04_marketing_core_strategy": {},
                "05_visual_photography_strategy": {},
                "06_platform_content_matrix": [],
                "07_race_execution_table": [],
                "08_culture_adaptation_checklist": [],
                "09_risk_measurement_priority_next_steps": {},
            },
        },
    )
    _write_json(
        package / "ASSET_UNIVERSE.json",
        {
            "status": "DYNAMIC_ASSET_UNIVERSE",
            "fixed_total_asset_limit": False,
            "platform_capacity_is_activation_constraint_only": True,
            "assets": [],
        },
    )


def _package(root: Path) -> Path:
    package = root / "package"
    package.mkdir(parents=True)
    finding = {
        "object_id": "RESEARCH-SEARCH-001",
        "domain": "SEARCH",
        "what": "Observed search term",
        "why": "Search evidence informs truthful Listing/Search architecture.",
        "evidence": {
            "source_ids": ["SRC-1"],
            "source_cards": [{"source_id": "SRC-1", "kind": "PLATFORM_RESEARCH", "observed_at": "2026-10-01"}],
            "as_of": "2026-10-02",
            "recency_statuses": ["WITHIN_DECLARED_FRESHNESS_WINDOW"],
            "traceability_status": "SOURCE_BOUND",
        },
        "exact_fact": {"term": "vitamin c serum", "volume": 1200},
        "interpretation": "Use only when semantically truthful for the exact SKU.",
        "confidence": "HIGH",
        "assumption_boundary": "Observed query scope only.",
        "downstream_use": ["LISTING_SEARCH"],
        "conflict_status": "NO_DECLARED_CONFLICT",
        "tradeoff": "Traffic opportunity must not override truthfulness.",
        "execution": {"listing_search": "Use only verified-relevance terms."},
        "measurement": {"next_check": ["query-to-SKU relevance"]},
    }
    business = {
        "market_analysis": {"market_research_authority": {"domains": {"SEARCH": {"findings": [finding]}}}},
        "human_delivery": {"task_scope": {"listing_active": True}, "listing": {"status": "ACTIVE"}},
        "sources": {"sources": [{"source_id": "SRC-1", "kind": "PLATFORM_RESEARCH", "observed_at": "2026-10-01"}]},
    }
    _write_json(package / "CANONICAL_HUMAN_DATA.json", {"canonical_business_objects": business})
    _materialize_mature_surface(package)
    _write_json(
        package / "DELIVERY_MANIFEST.json",
        {
            "status": "DELIVERY_READY",
            "workspace_contract": {},
            "html_index": "index.html",
            "project_hub": "00_PROJECT_HUB.md",
            "listing_upload_ready": "01_LISTING_UPLOAD_READY.md",
            "human_delivery_contract": "HUMAN_DELIVERY.json",
            "human_language_audit": "HUMAN_LANGUAGE_AUDIT.json",
            "delivery_language_matrix_audit": "DELIVERY_LANGUAGE_MATRIX_AUDIT.json",
            "platform_scope": "PLATFORM_SCOPE.json",
            "source_truth_media_audit": "SOURCE_TRUTH_MEDIA_AUDIT.json",
            "full_delivery_depth_audit": "FULL_DELIVERY_DEPTH_AUDIT.json",
            "strategy_authority": "strategy/MASTER_STRATEGY_CN.md",
            "strategy_decision_index": "strategy/STRATEGY_DECISION_INDEX.json",
            "supporting_analysis": "supporting_analysis/",
        },
    )
    _write_json(package / "FULL_MATERIALIZATION_AUDIT.json", {"status": "PASS", "legacy": True})
    return package


def test_req088_lineage_closure_is_materialized_into_final_manifest_and_zip(tmp_path: Path):
    from runtime.cbcc.phase7_lineage_semantic_closure_v0681 import materialize_phase7_lineage_and_semantics

    package = _package(tmp_path)
    zip_path = tmp_path / "final.zip"
    result = materialize_phase7_lineage_and_semantics(package, zip_path=zip_path)

    assert result["status"] == "PASS", result
    assert result["lineage_closure_status"] == "PASS"
    assert result["final_mature_package_continuity"] == "PASS"
    assert (package / "LINEAGE_CLOSURE_INDEX.json").exists()
    assert (package / "LINEAGE_CLOSURE_AUDIT.json").exists()

    audit = json.loads((package / "LINEAGE_CLOSURE_AUDIT.json").read_text(encoding="utf-8"))
    assert audit["status"] == "PASS", audit
    assert audit["business_payload_copied"] is False

    manifest = json.loads((package / "DELIVERY_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["lineage_closure_status"] == "PASS"
    assert manifest["lineage_closure_index"] == "LINEAGE_CLOSURE_INDEX.json"
    assert manifest["lineage_closure_audit"] == "LINEAGE_CLOSURE_AUDIT.json"
    assert manifest["final_mature_package_continuity"] == "PASS"
    assert manifest["workspace_contract"]["req088_resolvable_lineage_closure"] == "PASS"
    assert manifest["workspace_contract"]["final_mature_package_continuity"] == "PASS"

    with zipfile.ZipFile(zip_path) as zf:
        prefix = package.name + "/"
        names = set(zf.namelist())
        assert prefix + "LINEAGE_CLOSURE_INDEX.json" in names
        assert prefix + "LINEAGE_CLOSURE_AUDIT.json" in names
        assert prefix + "FULL_MATERIALIZATION_AUDIT.json" in names
        zipped_manifest = json.loads(zf.read(prefix + "DELIVERY_MANIFEST.json").decode("utf-8"))
        assert zipped_manifest["lineage_closure_status"] == "PASS"
        assert zipped_manifest["final_mature_package_continuity"] == "PASS"
