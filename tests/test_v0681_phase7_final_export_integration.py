from __future__ import annotations

import json
import zipfile
from pathlib import Path


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_phase7_semantic_closure_runs_after_phase6_final_projection_and_rebuilds_final_zip(tmp_path: Path, monkeypatch):
    import runtime.cbcc.commercial_delivery_continuity as continuity
    import runtime.cbcc.full_delivery_materialization as full_materialization
    import runtime.cbcc.canonical_delivery_parity_v0680 as parity
    import runtime.cbcc.delivery_family_workspace_v0680 as family_workspace

    package = tmp_path / "delivery"
    package.mkdir()
    zip_path = tmp_path / "delivery.zip"
    _write_json(
        package / "CANONICAL_HUMAN_DATA.json",
        {
            "canonical_business_objects": {
                "product_truth": {"fact": "FINAL-TRUTH"},
                "strategy_authority": {"decision": "FINAL-STRATEGY"},
            }
        },
    )
    (package / "CANONICAL_HUMAN_DATA.md").write_text("FINAL CANONICAL MARKDOWN\n", encoding="utf-8")
    (package / "index.html").write_text("<html><body>FINAL PHASE6 HTML</body></html>", encoding="utf-8")
    _write_json(package / "FULL_MATERIALIZATION_AUDIT.json", {"status": "PASS", "stage": "EARLY_PHASE7_UPSTREAM"})
    seed = {
        "status": "DELIVERY_READY",
        "package_dir": str(package),
        "zip_path": str(zip_path),
        "workspace_contract": {"phase6_seed": "PASS"},
    }
    _write_json(package / "DELIVERY_MANIFEST.json", seed)

    monkeypatch.setattr(continuity, "materialize_commerce_decision_context", lambda project_dir: {})
    monkeypatch.setattr(continuity, "compile_continuity_audit", lambda project_dir, context: {"status": "PASS"})
    monkeypatch.setattr(full_materialization, "finalize_full_delivery_materialization", lambda project_dir, manifest: dict(manifest))
    monkeypatch.setattr(parity, "finalize_export_canonical_delivery_parity", lambda manifest: {**dict(manifest), "phase6_parity_marker": "PASS"})
    monkeypatch.setattr(
        family_workspace,
        "materialize_delivery_family_workspace",
        lambda package_dir: {"status": "PASS", "families": {"longform": {"status": "PASS"}}, "issues": []},
    )

    def base_export(project_dir, output, *args, **kwargs):
        return dict(seed)

    exported = continuity.wrap_export_delivery_package(base_export)
    result = exported(tmp_path / "project", tmp_path / "out")

    assert result["phase7_final_semantic_closure"] == "PASS"
    assert result["phase6_parity_marker"] == "PASS"
    assert result["delivery_family_workspace_status"] == "PASS"
    assert result["delivery_family_workspace_families"] == ["longform"]
    assert result["workspace_contract"]["phase6_seed"] == "PASS"
    assert result["workspace_contract"]["activated_delivery_family_routes"] == "PASS"
    assert result["workspace_contract"]["phase7_final_semantic_closure"] == "PASS"
    assert result["host_native_runtime_export_parity"] == "E2E_PENDING_INSTALLED_HOST_EXPORT"
    assert result["actual_output_boundary_status"] == "E2E_PENDING"

    final_audit = json.loads((package / "FULL_MATERIALIZATION_AUDIT.json").read_text(encoding="utf-8"))
    assert final_audit["contract"] == "PHASE7_FINAL_PACKAGE_SEMANTIC_CLOSURE_V0681"
    assert final_audit["upstream_full_materialization_audit"]["stage"] == "EARLY_PHASE7_UPSTREAM"

    with zipfile.ZipFile(zip_path) as zf:
        prefix = package.name + "/"
        zipped_manifest = json.loads(zf.read(prefix + "DELIVERY_MANIFEST.json").decode("utf-8"))
        assert zipped_manifest["phase7_final_semantic_closure"] == "PASS"
        assert zipped_manifest["delivery_family_workspace_status"] == "PASS"
        assert zipped_manifest["phase6_parity_marker"] == "PASS"
