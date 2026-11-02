from __future__ import annotations

import json
from pathlib import Path


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _package(root: Path, *, business_objects: dict) -> Path:
    package = root / "package"
    package.mkdir(parents=True)
    _write_json(
        package / "CANONICAL_HUMAN_DATA.json",
        {"canonical_business_objects": business_objects, "projection_contract": {"version": "0.6.81"}},
    )
    _write_json(package / "DELIVERY_MANIFEST.json", {"status": "DELIVERY_READY", "workspace_contract": {}})
    return package


def _market_finding(*, proof_object=None, downstream_use=None) -> dict:
    row = {
        "object_id": "RESEARCH-SEARCH-001",
        "domain": "SEARCH",
        "what": "Observed search term",
        "why": "Search evidence informs truthful Listing/Search architecture.",
        "evidence": {
            "source_ids": ["SRC-1"],
            "source_cards": [
                {
                    "source_id": "SRC-1",
                    "kind": "PLATFORM_RESEARCH",
                    "observed_at": "2026-10-01",
                    "freshness_status": "WITHIN_DECLARED_FRESHNESS_WINDOW",
                }
            ],
            "as_of": "2026-10-02",
            "recency_statuses": ["WITHIN_DECLARED_FRESHNESS_WINDOW"],
            "traceability_status": "SOURCE_BOUND",
        },
        "exact_fact": {"term": "vitamin c serum", "volume": 1200},
        "interpretation": "Use only when semantically truthful for the exact SKU.",
        "confidence": "HIGH",
        "assumption_boundary": "Observed query scope only.",
        "downstream_use": downstream_use or ["LISTING_SEARCH"],
        "conflict_status": "NO_DECLARED_CONFLICT",
        "tradeoff": "Traffic opportunity must not override truthfulness.",
        "execution": {"listing_search": "Use only verified-relevance terms."},
        "measurement": {"next_check": ["query-to-SKU relevance"]},
    }
    if proof_object is not None:
        row["proof_object"] = proof_object
    return row


def _sources() -> dict:
    return {
        "sources": [
            {
                "source_id": "SRC-1",
                "kind": "PLATFORM_RESEARCH",
                "observed_at": "2026-10-01",
                "freshness_status": "WITHIN_DECLARED_FRESHNESS_WINDOW",
            }
        ]
    }


def test_req088_market_nested_lineage_normalizes_without_copying_business_fact(tmp_path: Path):
    from runtime.cbcc.information_audit_authority import LINEAGE_FIELDS
    from runtime.cbcc.lineage_normalization_v0681 import build_package_lineage_index

    market = {
        "market_research_authority": {
            "domains": {"SEARCH": {"findings": [_market_finding()]}}
        }
    }
    package = _package(
        tmp_path,
        business_objects={
            "market_analysis": market,
            "human_delivery": {"listing": {"status": "ACTIVE"}},
            "sources": _sources(),
        },
    )

    index = build_package_lineage_index(package)
    rows = [row for row in index["records"] if row["authority_object_id"] == "canonical_business_object::market_analysis"]
    assert len(rows) == 1, index
    row = rows[0]
    assert set(row["lineage"]) == set(LINEAGE_FIELDS)
    assert row["status"] == "PASS", row
    assert row["lineage"]["source_refs"]["ids"] == ["SRC-1"]
    assert row["lineage"]["source_type"]["resolved"] == ["PLATFORM_RESEARCH"]
    assert row["lineage"]["recency"]["resolved"]["as_of"] == "2026-10-02"
    assert row["lineage"]["downstream_use"]["resolved_targets"] == ["canonical_business_object::human_delivery"]
    assert row["lineage"]["proof_object"]["resolution"] == "PASS"
    # The normalized index points back to the authority field instead of re-authoring the business fact payload.
    exact = row["lineage"]["exact_fact"]
    assert "value" not in exact
    assert exact["binding"].endswith(".exact_fact")


def test_req088_shallow_lineage_stays_incomplete_instead_of_becoming_fake_pass(tmp_path: Path):
    from runtime.cbcc.lineage_normalization_v0681 import build_package_lineage_index

    shallow = {
        "what": "Audience context decision",
        "why": "Existing context changes execution.",
        "evidence": ["SRC-1"],
        "source_refs": ["SRC-1"],
        "confidence": "MEDIUM",
        "assumption_boundary": "EVIDENCE_BOUNDED_DECISION",
        "conflict_status": "NO_DECLARED_CONFLICT",
        "proof_object": "canonical_business_object::strategy_authority#sections.04_marketing_core_strategy.major_decision_context_why[0]",
        "tradeoff": "Keep uncertainty explicit.",
        "execution": {"next": "VERIFY"},
        "measurement": {"signal": "evidence refreshed"},
    }
    strategy = {
        "sections": {
            "04_marketing_core_strategy": {
                "major_decision_context_why": [shallow]
            }
        }
    }
    package = _package(
        tmp_path,
        business_objects={"strategy_authority": strategy, "sources": _sources()},
    )

    index = build_package_lineage_index(package)
    rows = [row for row in index["records"] if row["authority_object_id"] == "canonical_business_object::strategy_authority"]
    assert len(rows) == 1, index
    row = rows[0]
    assert row["status"] == "INCOMPLETE", row
    missing = {(issue["code"], issue.get("field")) for issue in row["issues"]}
    assert ("LINEAGE_FIELD_UNBOUND", "exact_fact") in missing
    assert ("LINEAGE_FIELD_UNBOUND", "interpretation") in missing
    assert ("LINEAGE_FIELD_UNBOUND", "downstream_use") in missing
    # Source type/recency may be resolved from the source authority, but that must not hide unrelated missing lineage.
    assert row["lineage"]["source_type"]["resolution"] == "PASS"
    assert row["lineage"]["recency"]["resolution"] == "PASS"


def test_req088_unresolvable_proof_and_downstream_are_rejected(tmp_path: Path):
    from runtime.cbcc.lineage_normalization_v0681 import build_package_lineage_index

    finding = _market_finding(
        proof_object="canonical_business_object::missing_authority#ghost.path",
        downstream_use=["NON_EXISTENT_CONSUMER"],
    )
    market = {"market_research_authority": {"domains": {"SEARCH": {"findings": [finding]}}}}
    package = _package(tmp_path, business_objects={"market_analysis": market, "sources": _sources()})

    index = build_package_lineage_index(package)
    row = [row for row in index["records"] if row["authority_object_id"] == "canonical_business_object::market_analysis"][0]
    codes = {issue["code"] for issue in row["issues"]}
    assert row["status"] == "INCOMPLETE"
    assert "LINEAGE_PROOF_OBJECT_UNRESOLVED" in codes
    assert "LINEAGE_DOWNSTREAM_UNRESOLVED" in codes


def test_req088_direct_canonical_and_production_targets_resolve(tmp_path: Path):
    from runtime.cbcc.lineage_normalization_v0681 import build_package_lineage_index

    strategy_row = {
        "what": "Activate paid asset",
        "why": "Verified strategy decision.",
        "evidence": ["SRC-1"],
        "source_refs": ["SRC-1"],
        "source_type": ["PLATFORM_RESEARCH"],
        "recency": [{"source_id": "SRC-1", "observed_at": "2026-10-01"}],
        "exact_fact": None,
        "interpretation": "This is a decision under current evidence, not a new external fact.",
        "confidence": "MEDIUM",
        "assumption_boundary": "DECISION_UNDER_CURRENT_EVIDENCE_NOT_EXTERNAL_FACT",
        "downstream_use": ["canonical_business_object::ads", "production_asset::A-01"],
        "conflict_status": "NO_DECLARED_CONFLICT",
        "proof_object": "canonical_business_object::strategy_authority#decision_log[0]",
        "tradeoff": "Re-evaluate when evidence changes.",
        "execution": {"action": "ACTIVATE"},
        "measurement": {"signal": "response"},
    }
    package = _package(
        tmp_path,
        business_objects={
            "strategy_authority": {"decision_log": [strategy_row]},
            "ads": {"status": "READY"},
            "sources": _sources(),
        },
    )
    _write_json(package / "asset_packages/A-01/CANONICAL_LINEAGE.json", {"asset_id": "A-01", "authority": "strategy"})

    index = build_package_lineage_index(package)
    row = [row for row in index["records"] if row["authority_object_id"] == "canonical_business_object::strategy_authority"][0]
    assert row["status"] == "PASS", row
    assert row["lineage"]["proof_object"]["resolution"] == "PASS"
    assert row["lineage"]["downstream_use"]["resolved_targets"] == [
        "canonical_business_object::ads",
        "production_asset::A-01",
    ]
