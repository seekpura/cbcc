from __future__ import annotations

# Dedicated focused characterization for REQ-090 final-byte mature package continuity.
import json
from pathlib import Path

import pytest


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _canonical(*, listing_active: bool = False) -> dict:
    business = {
        "product_truth": {"fact": "TRUTH"},
        "strategy_authority": {"decision": "KEEP_TRUTH"},
    }
    if listing_active:
        business["human_delivery"] = {
            "task_scope": {"listing_active": True},
            "listing": {"status": "ACTIVE"},
        }
    return {"canonical_business_objects": business}


def _shortcut_package(root: Path, *, listing_active: bool = False) -> Path:
    package = root / "package"
    package.mkdir(parents=True)
    _write_json(package / "CANONICAL_HUMAN_DATA.json", _canonical(listing_active=listing_active))
    _write_json(package / "DELIVERY_MANIFEST.json", {"status": "DELIVERY_READY", "workspace_contract": {}})
    _write_json(package / "FULL_MATERIALIZATION_AUDIT.json", {"status": "PASS", "legacy": True})
    return package


def _mature_package(root: Path, *, include_listing: bool = True, listing_active: bool = True) -> Path:
    package = _shortcut_package(root, listing_active=listing_active)
    # Reuse the mature package contract owned by full_delivery_depth_v3.  This fixture intentionally
    # supplies only the minimum valid bytes needed by that existing checker; Phase 7 must not author a
    # second hand-maintained list of core files.
    text_files = {
        "index.html": "<html><body>成熟交付工作区</body></html>\n",
        "00_PROJECT_HUB.md": "# 项目中心\n",
        "strategy/MASTER_STRATEGY_CN.md": "# 中文策略\n",
    }
    for rel, text in text_files.items():
        path = package / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    json_files = [
        "HUMAN_DELIVERY.json",
        "FULL_DELIVERY_DEPTH_AUDIT.json",
        "HUMAN_LANGUAGE_AUDIT.json",
        "DELIVERY_LANGUAGE_MATRIX_AUDIT.json",
        "PLATFORM_SCOPE.json",
        "SOURCE_TRUTH_MEDIA_AUDIT.json",
        "strategy/strategy_authority.json",
        "strategy/STRATEGY_DECISION_INDEX.json",
        "strategy/COMMERCE_DECISION_CONTEXT.json",
        "strategy/COMMERCIAL_CONTINUITY_AUDIT.json",
        "supporting_analysis/product_truth.json",
        "supporting_analysis/target_context.json",
        "supporting_analysis/culture_context.json",
        "supporting_analysis/asset_architecture.json",
        "supporting_analysis/seven_agent_synthesis.json",
        "FULL_DELIVERY_OBJECT_MANIFEST.json",
    ]
    for rel in json_files:
        _write_json(package / rel, {"status": "READY"})

    _write_json(
        package / "ASSET_UNIVERSE.json",
        {
            "status": "DYNAMIC_ASSET_UNIVERSE",
            "fixed_total_asset_limit": False,
            "platform_capacity_is_activation_constraint_only": True,
            "assets": [],
        },
    )
    manifest = json.loads((package / "DELIVERY_MANIFEST.json").read_text(encoding="utf-8"))
    manifest.update(
        {
            "html_index": "index.html",
            "project_hub": "00_PROJECT_HUB.md",
            "human_delivery_contract": "HUMAN_DELIVERY.json",
            "human_language_audit": "HUMAN_LANGUAGE_AUDIT.json",
            "delivery_language_matrix_audit": "DELIVERY_LANGUAGE_MATRIX_AUDIT.json",
            "platform_scope": "PLATFORM_SCOPE.json",
            "source_truth_media_audit": "SOURCE_TRUTH_MEDIA_AUDIT.json",
            "full_delivery_depth_audit": "FULL_DELIVERY_DEPTH_AUDIT.json",
            "strategy_authority": "strategy/MASTER_STRATEGY_CN.md",
            "strategy_decision_index": "strategy/STRATEGY_DECISION_INDEX.json",
            "supporting_analysis": "supporting_analysis/",
        }
    )
    if listing_active:
        manifest["listing_upload_ready"] = "01_LISTING_UPLOAD_READY.md"
    _write_json(package / "DELIVERY_MANIFEST.json", manifest)
    if include_listing:
        (package / "01_LISTING_UPLOAD_READY.md").write_text(
            "# 上架资料\n\n## 商品标题\n待真实商品数据投影。\n",
            encoding="utf-8",
        )
    return package


def test_phase7_production_orchestrator_rejects_canonical_only_shortcut_package(tmp_path: Path):
    from runtime.cbcc.phase7_lineage_semantic_closure_v0681 import materialize_phase7_lineage_and_semantics

    package = _shortcut_package(tmp_path)
    with pytest.raises(RuntimeError, match="mature package continuity"):
        materialize_phase7_lineage_and_semantics(package, zip_path=tmp_path / "shortcut.zip")


def test_phase7_final_mature_audit_reuses_existing_host_full_checker_on_final_bytes(tmp_path: Path):
    from runtime.cbcc.final_mature_package_continuity_v0681 import audit_final_mature_package_continuity

    package = _mature_package(tmp_path)
    result = audit_final_mature_package_continuity(package)

    assert result["status"] == "PASS", result
    assert result["checker"] == "runtime.cbcc.full_delivery_depth_v3.audit_host_full_package"
    assert result["core_contract_reused"] is True
    assert result["final_package_bytes"] is True
    assert result["issues"] == []


def test_phase7_listing_activation_requires_final_listing_materialization(tmp_path: Path):
    from runtime.cbcc.final_mature_package_continuity_v0681 import audit_final_mature_package_continuity

    package = _mature_package(tmp_path, include_listing=False, listing_active=True)
    result = audit_final_mature_package_continuity(package)

    assert result["status"] == "INCOMPLETE", result
    codes = {issue["code"] for issue in result["issues"]}
    assert "FINAL_MATURE_LISTING_OUTPUT_MISSING" in codes


def test_phase7_manifest_declared_mature_paths_must_resolve_on_final_bytes(tmp_path: Path):
    from runtime.cbcc.final_mature_package_continuity_v0681 import audit_final_mature_package_continuity

    package = _mature_package(tmp_path)
    manifest_path = package / "DELIVERY_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["project_hub"] = "missing/00_PROJECT_HUB.md"
    _write_json(manifest_path, manifest)

    result = audit_final_mature_package_continuity(package)
    assert result["status"] == "INCOMPLETE", result
    assert any(
        issue["code"] == "FINAL_MATURE_DECLARED_PATH_MISSING"
        and issue.get("manifest_field") == "project_hub"
        for issue in result["issues"]
    ), result
