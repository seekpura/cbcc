from __future__ import annotations

import json
from pathlib import Path


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_req088_export_wrapper_must_call_lineage_semantic_orchestrator(tmp_path: Path, monkeypatch):
    import runtime.cbcc.commercial_delivery_continuity as continuity
    import runtime.cbcc.full_delivery_materialization as full_materialization
    import runtime.cbcc.canonical_delivery_parity_v0680 as parity
    import runtime.cbcc.delivery_family_workspace_v0680 as family_workspace
    import runtime.cbcc.full_package_semantic_closure_v0681 as semantic
    import runtime.cbcc.phase7_lineage_semantic_closure_v0681 as orchestrator

    package = tmp_path / "delivery"
    package.mkdir()
    zip_path = tmp_path / "delivery.zip"
    _write_json(package / "CANONICAL_HUMAN_DATA.json", {"canonical_business_objects": {"product_truth": {"fact": "TRUTH"}}})
    seed = {
        "status": "DELIVERY_READY",
        "package_dir": str(package),
        "zip_path": str(zip_path),
        "workspace_contract": {},
    }
    _write_json(package / "DELIVERY_MANIFEST.json", seed)

    monkeypatch.setattr(continuity, "materialize_commerce_decision_context", lambda project_dir: {})
    monkeypatch.setattr(continuity, "compile_continuity_audit", lambda project_dir, context: {"status": "PASS"})
    monkeypatch.setattr(full_materialization, "finalize_full_delivery_materialization", lambda project_dir, manifest: dict(manifest))
    monkeypatch.setattr(parity, "finalize_export_canonical_delivery_parity", lambda manifest: dict(manifest))
    monkeypatch.setattr(
        family_workspace,
        "materialize_delivery_family_workspace",
        lambda package_dir: {"status": "PASS", "families": {}, "issues": []},
    )

    called = {"orchestrator": 0}

    def expected_orchestrator(package_dir, *, zip_path=None, host_package_dir=None):
        called["orchestrator"] += 1
        return {"status": "PASS", "manifest": {**seed, "req088_orchestrated": "PASS"}}

    def forbidden_old_semantic(*args, **kwargs):
        raise AssertionError("export wrapper bypassed REQ-088 lineage and called the old semantic finalizer directly")

    monkeypatch.setattr(orchestrator, "materialize_phase7_lineage_and_semantics", expected_orchestrator)
    monkeypatch.setattr(semantic, "materialize_final_package_semantics", forbidden_old_semantic)

    exported = continuity.wrap_export_delivery_package(lambda project_dir, output, *args, **kwargs: dict(seed))
    result = exported(tmp_path / "project", tmp_path / "out")

    assert called["orchestrator"] == 1
    assert result["req088_orchestrated"] == "PASS"
