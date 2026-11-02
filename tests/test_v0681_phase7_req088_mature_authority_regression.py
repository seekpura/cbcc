from __future__ import annotations

import json
from pathlib import Path


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_req088_mature_information_audit_rows_do_not_double_count_nested_evidence(tmp_path: Path):
    from runtime.cbcc.information_audit_authority import compile_information_audit_authority
    from runtime.cbcc.lineage_normalization_v0681 import build_package_lineage_index

    info = compile_information_audit_authority(
        {
            "required_missing": ["current launch price"],
            "assumptions": [
                {
                    "assumption": "Use planning placeholder until current launch price is confirmed.",
                    "downstream_use": ["TO_VERIFY_PRICING"],
                    "evidence_needed": "Current price authority or explicit user confirmation.",
                }
            ],
            "decision_log": [
                {
                    "decision": "Do not publish a price claim before confirmation.",
                    "downstream_use": ["CURRENT_STRATEGY"],
                }
            ],
        },
        sources=[],
    )
    strategy = {
        "sections": {
            "01_information_completeness_assumptions_decisions": info,
        }
    }
    package = tmp_path / "package"
    package.mkdir()
    _write_json(
        package / "CANONICAL_HUMAN_DATA.json",
        {"canonical_business_objects": {"strategy_authority": strategy}},
    )

    index = build_package_lineage_index(package)
    rows = [
        row for row in index["records"]
        if row["authority_object_id"] == "canonical_business_object::strategy_authority"
    ]
    assert rows, index
    assert index["status"] == "PASS", index
    assert all(row["status"] == "PASS" for row in rows), rows
    # evidence/source descriptors are metadata owned by their parent lineage row, never standalone business lineage records.
    assert not any(row["authority_path"].endswith(".evidence") for row in rows), rows
    assert not any(".evidence." in row["authority_path"] for row in rows), rows
    # Explicit unknowns remain explicit and are not promoted to facts just to satisfy lineage closure.
    assumption_rows = [row for row in rows if "assumptions[" in row["authority_path"]]
    assert assumption_rows, rows
    assert all(row["lineage"]["exact_fact"]["resolution"] == "PASS" for row in assumption_rows)
    assert any(
        "TO_VERIFY_PRICING" in row["lineage"]["downstream_use"].get("deferred_tokens", [])
        for row in assumption_rows
    )
