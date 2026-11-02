from __future__ import annotations

import json
import zipfile
from pathlib import Path


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _asset(package: Path, asset_id: str, surface: str, token: str) -> None:
    root = package / "asset_packages" / asset_id
    root.mkdir(parents=True, exist_ok=True)
    (root / "00_asset_manifest.yaml").write_text(
        f"asset_id: {asset_id}\nsurface: {surface}\nfamily: {surface}\n", encoding="utf-8"
    )
    (root / "01_strategy.md").write_text(token + " STRATEGY\n", encoding="utf-8")
    (root / "05_prompt_CN.txt").write_text(token + " PROMPT CN\n", encoding="utf-8")
    (root / "06_prompt_EN.txt").write_text(token + " PROMPT EN\n", encoding="utf-8")
    _write_json(root / "12_design_card.json", {"asset_id": asset_id, "surface": surface, "decision": token})


def _package(tmp_path: Path, *, with_crm: bool = True) -> Path:
    from runtime.cbcc.delivery_html import build_delivery_html

    package = tmp_path / "package"
    package.mkdir()
    _write_json(
        package / "HUMAN_DELIVERY.json",
        {
            "target": {"platform": "TikTok Shop", "market": "Malaysia", "locale": "ms-MY"},
            "product": {"brand": "KIYUU", "product_name": "K01"},
            "copy_center": [{"field": "title", "value": "PHASE6 FAMILY ROUTE TITLE", "locale": "ms-MY"}],
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
                "02_product_truth_value_ladder": {},
                "03_platform_region_audience_culture_insight": {},
                "04_marketing_core_strategy": {},
                "05_visual_photography_strategy": {},
                "06_platform_content_matrix": [],
                "07_race_execution_table": [],
                "08_culture_adaptation_checklist": [],
                "09_risk_measurement_priority_next_steps": {},
            }
        },
    )
    _asset(package, "LF-01", "LONGFORM", "REQ070 LONGFORM SENTINEL")
    _asset(package, "STORE-01", "STORE_BANNER", "REQ076 STORE SENTINEL")
    if with_crm:
        _asset(package, "CRM-01", "POST_PURCHASE", "REQ077 CRM SENTINEL")
    build_delivery_html(package, package / "index.html")
    return package


def test_phase6_activated_delivery_families_get_dynamic_human_workspace_lenses(tmp_path: Path):
    from runtime.cbcc.canonical_delivery_parity_v0680 import materialize_canonical_delivery_parity
    from runtime.cbcc.canonical_routed_workspace_v0680 import materialize_routed_canonical_workspace
    from runtime.cbcc.delivery_family_workspace_v0680 import materialize_delivery_family_workspace

    package = _package(tmp_path)
    assert materialize_canonical_delivery_parity(package)["status"] == "PASS"
    assert materialize_routed_canonical_workspace(package)["status"] == "PASS"
    result = materialize_delivery_family_workspace(package)
    assert result["status"] == "PASS", result

    assert set(result["families"]) == {"longform", "store_landing", "crm"}
    assert result["families"]["longform"]["requirement_id"] == "REQ-070"
    assert result["families"]["store_landing"]["requirement_id"] == "REQ-076"
    assert result["families"]["crm"]["requirement_id"] == "REQ-077"
    assert result["families"]["longform"]["object_count"] == 1
    assert result["families"]["store_landing"]["object_count"] == 1
    assert result["families"]["crm"]["object_count"] == 1

    html = (package / "index.html").read_text(encoding="utf-8")
    for family, token in (
        ("longform", "REQ070 LONGFORM SENTINEL"),
        ("store_landing", "REQ076 STORE SENTINEL"),
        ("crm", "REQ077 CRM SENTINEL"),
    ):
        assert f'data-delivery-family="{family}"' in html
        assert token in html


def test_phase6_delivery_family_lenses_are_not_a_fixed_menu(tmp_path: Path):
    from runtime.cbcc.canonical_delivery_parity_v0680 import materialize_canonical_delivery_parity
    from runtime.cbcc.canonical_routed_workspace_v0680 import materialize_routed_canonical_workspace
    from runtime.cbcc.delivery_family_workspace_v0680 import materialize_delivery_family_workspace

    package = _package(tmp_path, with_crm=False)
    assert materialize_canonical_delivery_parity(package)["status"] == "PASS"
    assert materialize_routed_canonical_workspace(package)["status"] == "PASS"
    result = materialize_delivery_family_workspace(package)
    assert result["status"] == "PASS"
    assert set(result["families"]) == {"longform", "store_landing"}
    html = (package / "index.html").read_text(encoding="utf-8")
    assert 'data-delivery-family="crm"' not in html
    assert "CRM / Lifecycle / Post-purchase" not in html


def test_phase6_delivery_family_audit_does_not_accept_archive_only_presence(tmp_path: Path):
    from runtime.cbcc.canonical_delivery_parity_v0680 import materialize_canonical_delivery_parity
    from runtime.cbcc.canonical_routed_workspace_v0680 import materialize_routed_canonical_workspace
    from runtime.cbcc.delivery_family_workspace_v0680 import (
        audit_delivery_family_workspace,
        materialize_delivery_family_workspace,
    )

    package = _package(tmp_path)
    assert materialize_canonical_delivery_parity(package)["status"] == "PASS"
    assert materialize_routed_canonical_workspace(package)["status"] == "PASS"
    assert materialize_delivery_family_workspace(package)["status"] == "PASS"

    html_path = package / "index.html"
    html = html_path.read_text(encoding="utf-8")
    marker = 'data-delivery-family-object="LF-01"'
    assert marker in html and "REQ070 LONGFORM SENTINEL" in html
    html_path.write_text(html.replace(marker, 'data-delivery-family-object-removed="LF-01"', 1), encoding="utf-8")
    issues = audit_delivery_family_workspace(package)
    assert any(issue["code"] == "DELIVERY_FAMILY_ROUTED_OBJECT_MISSING_V0680" for issue in issues), issues


def test_phase6_final_export_manifest_and_zip_consume_delivery_family_workspace(tmp_path: Path, monkeypatch):
    import runtime.cbcc.commercial_delivery_continuity as continuity
    import runtime.cbcc.full_delivery_materialization as full_materialization

    package = _package(tmp_path)
    zip_path = tmp_path / "phase6-family-delivery.zip"
    seed_manifest = {
        "package_dir": str(package),
        "zip_path": str(zip_path),
        "workspace_contract": {},
    }
    _write_json(package / "DELIVERY_MANIFEST.json", seed_manifest)

    monkeypatch.setattr(continuity, "materialize_commerce_decision_context", lambda project_dir: {})
    monkeypatch.setattr(continuity, "compile_continuity_audit", lambda project_dir, context: {"status": "PASS"})
    monkeypatch.setattr(
        full_materialization,
        "finalize_full_delivery_materialization",
        lambda project_dir, manifest: dict(manifest),
    )

    def base_export(project_dir, output, *args, **kwargs):
        return dict(seed_manifest)

    exported = continuity.wrap_export_delivery_package(base_export)
    result = exported(tmp_path / "project", tmp_path / "output")

    assert result["delivery_family_workspace_status"] == "PASS"
    assert set(result["delivery_family_workspace_families"]) == {"crm", "longform", "store_landing"}
    assert result["workspace_contract"]["activated_delivery_family_routes"] == "PASS"
    assert result["workspace_contract"]["delivery_family_menu_is_fixed"] is False
    assert result["delivery_family_workspace_audit"] == "DELIVERY_FAMILY_WORKSPACE_AUDIT.json"
    assert zip_path.exists()

    disk_manifest = json.loads((package / "DELIVERY_MANIFEST.json").read_text(encoding="utf-8"))
    assert disk_manifest["delivery_family_workspace_status"] == "PASS"
    assert any(row["path"] == "DELIVERY_FAMILY_WORKSPACE_AUDIT.json" for row in disk_manifest["files"])

    prefix = package.name + "/"
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        assert prefix + "DELIVERY_FAMILY_WORKSPACE_AUDIT.json" in names
        assert prefix + "DELIVERY_MANIFEST.json" in names
        assert prefix + "index.html" in names
        zipped_html = zf.read(prefix + "index.html").decode("utf-8")
        assert 'data-delivery-family="longform"' in zipped_html
        assert 'data-delivery-family="store_landing"' in zipped_html
        assert 'data-delivery-family="crm"' in zipped_html
