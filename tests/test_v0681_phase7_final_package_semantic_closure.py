from __future__ import annotations

import json
import zipfile
from pathlib import Path


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _package(root: Path, *, value: str = "SEMANTIC-V1", include_unknown: bool = True) -> Path:
    package = root / "package"
    package.mkdir(parents=True)
    business = {
        "product_truth": {"fact": "PRODUCT-TRUTH-V1"},
        "strategy_authority": {"decision": value},
    }
    if include_unknown:
        business["crm_lifecycle_authority"] = {
            "object_id": "CRM-LIFECYCLE-01",
            "decision": "POST_PURCHASE_KEEP",
            "what": "retain the customer after delivery",
        }
    canonical = {
        "canonical_business_objects": business,
        "projection_contract": {"version": "0.6.80"},
    }
    _write_json(package / "CANONICAL_HUMAN_DATA.json", canonical)
    (package / "CANONICAL_HUMAN_DATA.md").write_text("# Canonical\n" + json.dumps(canonical, ensure_ascii=False), encoding="utf-8")
    (package / "index.html").write_text("<html><body>FINAL HUMAN WORKSPACE</body></html>", encoding="utf-8")
    _write_json(package / "DELIVERY_MANIFEST.json", {"status": "DELIVERY_READY", "workspace_contract": {}})
    _write_json(package / "FULL_DELIVERY_OBJECT_MANIFEST.json", {"status": "FULL_DELIVERY_OBJECT_MANIFEST", "objects": []})
    _write_json(package / "FULL_MATERIALIZATION_AUDIT.json", {"status": "PASS", "legacy": True})
    return package


def test_phase7_final_object_manifest_is_derived_from_actual_canonical_objects(tmp_path: Path):
    from runtime.cbcc.full_package_semantic_closure_v0681 import (
        audit_final_semantic_inventory,
        materialize_final_package_semantics,
    )

    package = _package(tmp_path)
    result = materialize_final_package_semantics(package)
    assert result["status"] == "PASS", result

    manifest = json.loads((package / "FULL_DELIVERY_OBJECT_MANIFEST.json").read_text(encoding="utf-8"))
    rows = {row["object_id"]: row for row in manifest["semantic_objects"]}
    unknown_id = "canonical_business_object::crm_lifecycle_authority"
    assert unknown_id in rows
    assert rows[unknown_id]["semantic_sha256"]
    assert rows[unknown_id]["source_path"] == "CANONICAL_HUMAN_DATA.json#canonical_business_objects.crm_lifecycle_authority"

    # Removing one row must fail even though the canonical JSON bytes still exist in the package.
    manifest["semantic_objects"] = [row for row in manifest["semantic_objects"] if row["object_id"] != unknown_id]
    _write_json(package / "FULL_DELIVERY_OBJECT_MANIFEST.json", manifest)
    issues = audit_final_semantic_inventory(package)
    assert any(issue["code"] == "FINAL_SEMANTIC_OBJECT_UNACCOUNTED" and issue["object_id"] == unknown_id for issue in issues), issues


def test_phase7_host_runtime_parity_compares_semantics_not_file_layout(tmp_path: Path):
    from runtime.cbcc.full_package_semantic_closure_v0681 import compare_export_semantics

    host = _package(tmp_path / "host", value="SAME")
    runtime = _package(tmp_path / "runtime", value="SAME")
    # Different non-semantic file bytes must not create a false mismatch.
    (host / "00_PROJECT_HUB.md").write_text("host presentation\n", encoding="utf-8")
    (runtime / "00_PROJECT_HUB.md").write_text("runtime presentation with different formatting\n", encoding="utf-8")

    same = compare_export_semantics(host, runtime)
    assert same["status"] == "PASS", same
    assert same["host_semantic_signature_sha256"] == same["runtime_semantic_signature_sha256"]

    canonical = json.loads((runtime / "CANONICAL_HUMAN_DATA.json").read_text(encoding="utf-8"))
    canonical["canonical_business_objects"]["strategy_authority"]["decision"] = "DIFFERENT"
    _write_json(runtime / "CANONICAL_HUMAN_DATA.json", canonical)
    different = compare_export_semantics(host, runtime)
    assert different["status"] == "INCOMPLETE", different
    assert "canonical_business_object::strategy_authority" in different["changed_object_ids"]


def test_phase7_actual_output_boundary_stays_pending_for_planning_only_provider_jobs(tmp_path: Path):
    from runtime.cbcc.full_package_semantic_closure_v0681 import audit_actual_output_boundary

    package = _package(tmp_path)
    _write_json(
        package / "provider_jobs/PROVIDER_JOB_INDEX.json",
        {
            "status": "JOBS_MATERIALIZED",
            "jobs": [{"asset_id": "A-01", "job_id": "JOB-01", "result_path": "provider_jobs/A-01/result.json"}],
        },
    )
    # A materialized job or template is not an actual Provider Result.
    _write_json(package / "provider_jobs/A-01/result.template.json", {"asset_id": "A-01", "output_path": ""})

    boundary = audit_actual_output_boundary(package)
    assert boundary["status"] == "E2E_PENDING"
    row = boundary["assets"][0]
    assert row["asset_id"] == "A-01"
    assert row["provider_result"] == "MISSING"
    assert row["review"] == "MISSING"
    assert row["local_revision"] == "MISSING"
    assert row["lineage_hash"] == "MISSING"


def test_phase7_finalizer_rewrites_final_manifest_zip_without_fake_host_or_output_pass(tmp_path: Path):
    from runtime.cbcc.full_package_semantic_closure_v0681 import materialize_final_package_semantics

    package = _package(tmp_path)
    zip_path = tmp_path / "final.zip"
    _write_json(package / "provider_jobs/PROVIDER_JOB_INDEX.json", {"status": "JOBS_MATERIALIZED", "jobs": [{"asset_id": "A-01", "job_id": "JOB-01"}]})

    result = materialize_final_package_semantics(package, zip_path=zip_path)
    assert result["status"] == "PASS"
    assert result["host_native_runtime_export_parity"] == "E2E_PENDING_INSTALLED_HOST_EXPORT"
    assert result["actual_output_boundary_status"] == "E2E_PENDING"
    assert zip_path.exists()

    disk_manifest = json.loads((package / "DELIVERY_MANIFEST.json").read_text(encoding="utf-8"))
    assert disk_manifest["phase7_final_semantic_closure"] == "PASS"
    assert disk_manifest["host_native_runtime_export_parity"] == "E2E_PENDING_INSTALLED_HOST_EXPORT"
    assert disk_manifest["actual_output_boundary_status"] == "E2E_PENDING"
    assert disk_manifest["full_delivery_object_manifest"] == "FULL_DELIVERY_OBJECT_MANIFEST.json"
    assert disk_manifest["full_materialization_audit"] == "FULL_MATERIALIZATION_AUDIT.json"

    with zipfile.ZipFile(zip_path) as zf:
        prefix = package.name + "/"
        names = set(zf.namelist())
        assert prefix + "FULL_DELIVERY_OBJECT_MANIFEST.json" in names
        assert prefix + "FULL_MATERIALIZATION_AUDIT.json" in names
        assert prefix + "DELIVERY_MANIFEST.json" in names
        zipped_manifest = json.loads(zf.read(prefix + "DELIVERY_MANIFEST.json").decode("utf-8"))
        assert zipped_manifest["host_native_runtime_export_parity"] == "E2E_PENDING_INSTALLED_HOST_EXPORT"
        assert zipped_manifest["actual_output_boundary_status"] == "E2E_PENDING"
