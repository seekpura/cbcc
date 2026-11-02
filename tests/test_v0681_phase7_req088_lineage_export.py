from __future__ import annotations

import json
import zipfile
from pathlib import Path


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
        "human_delivery": {"listing": {"status": "ACTIVE"}},
        "sources": {"sources": [{"source_id": "SRC-1", "kind": "PLATFORM_RESEARCH", "observed_at": "2026-10-01"}]},
    }
    _write_json(package / "CANONICAL_HUMAN_DATA.json", {"canonical_business_objects": business})
    _write_json(package / "DELIVERY_MANIFEST.json", {"status": "DELIVERY_READY", "workspace_contract": {}})
    _write_json(package / "FULL_MATERIALIZATION_AUDIT.json", {"status": "PASS", "legacy": True})
    return package


def test_req088_lineage_closure_is_materialized_into_final_manifest_and_zip(tmp_path: Path):
    from runtime.cbcc.phase7_lineage_semantic_closure_v0681 import materialize_phase7_lineage_and_semantics

    package = _package(tmp_path)
    zip_path = tmp_path / "final.zip"
    result = materialize_phase7_lineage_and_semantics(package, zip_path=zip_path)

    assert result["status"] == "PASS", result
    assert result["lineage_closure_status"] == "PASS"
    assert (package / "LINEAGE_CLOSURE_INDEX.json").exists()
    assert (package / "LINEAGE_CLOSURE_AUDIT.json").exists()

    audit = json.loads((package / "LINEAGE_CLOSURE_AUDIT.json").read_text(encoding="utf-8"))
    assert audit["status"] == "PASS", audit
    assert audit["business_payload_copied"] is False

    manifest = json.loads((package / "DELIVERY_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["lineage_closure_status"] == "PASS"
    assert manifest["lineage_closure_index"] == "LINEAGE_CLOSURE_INDEX.json"
    assert manifest["lineage_closure_audit"] == "LINEAGE_CLOSURE_AUDIT.json"
    assert manifest["workspace_contract"]["req088_resolvable_lineage_closure"] == "PASS"

    with zipfile.ZipFile(zip_path) as zf:
        prefix = package.name + "/"
        names = set(zf.namelist())
        assert prefix + "LINEAGE_CLOSURE_INDEX.json" in names
        assert prefix + "LINEAGE_CLOSURE_AUDIT.json" in names
        zipped_manifest = json.loads(zf.read(prefix + "DELIVERY_MANIFEST.json").decode("utf-8"))
        assert zipped_manifest["lineage_closure_status"] == "PASS"
