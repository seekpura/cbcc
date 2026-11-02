from __future__ import annotations

import json
import zipfile
from pathlib import Path


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _center() -> dict:
    return {
        "version": "phase6-req061-test",
        "delivery_language": {"locale": "zh-CN"},
        "target": {
            "platform": "TikTok Shop",
            "site": "MY",
            "market": "Malaysia",
            "locale": "ms-MY",
            "delivery_locale": "zh-CN",
        },
        "product": {"brand": "KIYUU", "product_name": "K01"},
        "task_scope": {"listing_active": True, "families": ["LISTING", "VISUAL"]},
        "readiness": {"status": "READY_FOR_CURRENT_SCOPE", "pending_count": 0},
        "copy_center": [
            {
                "group": "商品识别",
                "field": "title",
                "label": "产品标题",
                "value": "REQ061 BM TITLE SENTINEL",
                "status": "READY",
                "required_for_current_scope": True,
                "copyable": True,
                "locale": "ms-MY",
                "delivery_translation": "REQ061 中文标题哨兵",
                "delivery_companion_status": "READY",
            },
            {
                "group": "购买决策",
                "field": "description",
                "label": "商品描述",
                "value": "REQ061 BM DESCRIPTION SENTINEL",
                "status": "READY",
                "required_for_current_scope": True,
                "copyable": True,
                "locale": "ms-MY",
                "delivery_translation": "REQ061 中文描述哨兵",
                "delivery_companion_status": "READY",
            },
        ],
        "localized_copy": [
            {
                "locale": "en-MY",
                "field": "title",
                "value": "REQ061 EN TITLE SENTINEL",
                "delivery_translation": "REQ061 中文标题哨兵",
            }
        ],
        "media_slots": [],
        "risks_and_holds": [{"risk": "REQ061 HUMAN RISK SENTINEL", "status": "TO_VERIFY"}],
    }


def _strategy() -> dict:
    return {
        "human_projection": {"mode": "FULL"},
        "sections": {
            "01_information_completeness_assumptions_decisions": {
                "decision_log": [
                    {
                        "what": "REQ061 DECISION SENTINEL",
                        "why": "same-source characterization",
                        "evidence": "fixture",
                        "tradeoff": "none",
                        "execution": "project once",
                        "measurement": "signature parity",
                    }
                ]
            },
            "02_product_truth_value_ladder": {
                "product_truth_audit_table": [
                    {
                        "item": "truth",
                        "fact_or_claim": "REQ061 TRUTH SENTINEL",
                        "evidence_grade": "A",
                        "source_refs": ["fixture"],
                    }
                ]
            },
            "03_platform_region_audience_culture_insight": {
                "context_why": {"platform": "REQ061 MARKET WHY SENTINEL"}
            },
            "04_marketing_core_strategy": {
                "value_proposition": "REQ061 VALUE PROP SENTINEL",
                "message_hierarchy": ["REQ061 MESSAGE SENTINEL"],
            },
            "05_visual_photography_strategy": {
                "visual_thesis": "REQ061 VISUAL SENTINEL"
            },
            "06_platform_content_matrix": [],
            "07_race_execution_table": [],
            "08_culture_adaptation_checklist": [],
            "09_risk_measurement_priority_next_steps": {},
        },
    }


def _package(tmp_path: Path) -> Path:
    from runtime.cbcc.delivery_html import build_delivery_html

    package = tmp_path / "package"
    package.mkdir()
    _write_json(package / "HUMAN_DELIVERY.json", _center())
    _write_json(package / "strategy/strategy_authority.json", _strategy())
    _write_json(
        package / "supporting_analysis/product_truth.json",
        {
            "ingredient": "REQ061 PRODUCT TRUTH SENTINEL",
            "source_priority": ["fixture"],
        },
    )
    _write_json(
        package / "supporting_analysis/market_analysis.json",
        {"market_signal": "REQ061 MARKET ANALYSIS SENTINEL"},
    )
    _write_json(
        package / "supporting_analysis/compliance_report.json",
        {"issues": [{"risk": "REQ061 COMPLIANCE SENTINEL"}]},
    )
    build_delivery_html(package, package / "index.html")
    return package


def test_req061_materializes_json_markdown_html_from_one_canonical_payload(tmp_path: Path):
    from runtime.cbcc.canonical_delivery_parity_v0680 import materialize_canonical_delivery_parity

    package = _package(tmp_path)
    result = materialize_canonical_delivery_parity(package)

    assert result["status"] == "PASS", result
    json_path = package / "CANONICAL_HUMAN_DATA.json"
    md_path = package / "CANONICAL_HUMAN_DATA.md"
    html_path = package / "index.html"
    audit_path = package / "CANONICAL_DELIVERY_PARITY_AUDIT.json"
    assert json_path.exists() and md_path.exists() and html_path.exists() and audit_path.exists()

    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    signature = audit["canonical_signature_sha256"]
    assert len(signature) == 64

    md = md_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")
    assert f"canonical-signature: {signature}" in md
    assert f'data-canonical-signature="{signature}"' in html

    # Representative leaves from different canonical business-object families must survive on both
    # human surfaces instead of proving Listing-only parity.
    sentinels = (
        "REQ061 BM DESCRIPTION SENTINEL",
        "REQ061 HUMAN RISK SENTINEL",
        "REQ061 PRODUCT TRUTH SENTINEL",
        "REQ061 MARKET ANALYSIS SENTINEL",
        "REQ061 COMPLIANCE SENTINEL",
        "REQ061 VALUE PROP SENTINEL",
        "REQ061 VISUAL SENTINEL",
    )
    for token in sentinels:
        assert token in md, ("markdown", token)
        assert token in html, ("html", token)


def test_req061_parity_audit_detects_markdown_drift(tmp_path: Path):
    from runtime.cbcc.canonical_delivery_parity_v0680 import (
        audit_canonical_delivery_parity,
        materialize_canonical_delivery_parity,
    )

    package = _package(tmp_path)
    assert materialize_canonical_delivery_parity(package)["status"] == "PASS"

    md_path = package / "CANONICAL_HUMAN_DATA.md"
    md_path.write_text(
        md_path.read_text(encoding="utf-8").replace("REQ061 MARKET ANALYSIS SENTINEL", ""),
        encoding="utf-8",
    )
    issues = audit_canonical_delivery_parity(package)
    assert any(issue["code"] == "MARKDOWN_CANONICAL_FIELD_DRIFT" for issue in issues), issues


def test_req061_final_export_manifest_and_zip_contain_same_source_parity_artifacts(tmp_path: Path):
    from runtime.cbcc.canonical_delivery_parity_v0680 import finalize_export_canonical_delivery_parity

    package = _package(tmp_path)
    zip_path = tmp_path / "package.zip"
    _write_json(
        package / "DELIVERY_MANIFEST.json",
        {
            "status": "DELIVERY_READY",
            "package_dir": str(package),
            "zip_path": str(zip_path),
            "workspace_contract": {"existing_contract": "PASS"},
            "files": [],
        },
    )

    result = finalize_export_canonical_delivery_parity(
        {
            "status": "DELIVERY_READY",
            "package_dir": str(package),
            "zip_path": str(zip_path),
            "workspace_contract": {"existing_contract": "PASS"},
        }
    )

    assert result["canonical_delivery_parity_status"] == "PASS"
    signature = result["canonical_delivery_signature_sha256"]
    assert len(signature) == 64
    assert result["workspace_contract"]["existing_contract"] == "PASS"
    assert result["workspace_contract"]["canonical_json_markdown_html_same_source_parity"] == "PASS"

    disk_manifest = json.loads((package / "DELIVERY_MANIFEST.json").read_text(encoding="utf-8"))
    assert disk_manifest["canonical_human_data_json"] == "CANONICAL_HUMAN_DATA.json"
    assert disk_manifest["canonical_human_data_markdown"] == "CANONICAL_HUMAN_DATA.md"
    assert disk_manifest["canonical_delivery_parity_audit"] == "CANONICAL_DELIVERY_PARITY_AUDIT.json"
    assert disk_manifest["canonical_delivery_signature_sha256"] == signature

    assert zip_path.exists()
    prefix = package.name + "/"
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        for rel in (
            "CANONICAL_HUMAN_DATA.json",
            "CANONICAL_HUMAN_DATA.md",
            "CANONICAL_DELIVERY_PARITY_AUDIT.json",
            "index.html",
            "DELIVERY_MANIFEST.json",
        ):
            assert prefix + rel in names, rel
        zipped_md = zf.read(prefix + "CANONICAL_HUMAN_DATA.md").decode("utf-8")
        zipped_html = zf.read(prefix + "index.html").decode("utf-8")
        assert f"canonical-signature: {signature}" in zipped_md
        assert f'data-canonical-signature="{signature}"' in zipped_html
