from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_v0664_requirement_consumer_map.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("cbcc_requirement_consumer_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_current_release_overrides_are_consumed_and_reported():
    checker = _load_checker()
    result = checker.audit()

    assert result["current_overrides_applied"] == ["REQ-046", "REQ-047", "REQ-048"]
    assert result["current_version_family"] == "0.6.66"
    assert result["status"] == "PASS", result


def test_release_process_rows_are_current_not_historical():
    checker = _load_checker()
    rows = {row["req"]: row for row in checker.effective_requirement_rows()}

    assert rows["REQ-046"]["status"] == "RELEASE_PROCESS_ENFORCED_CURRENT"
    assert rows["REQ-047"]["status"] == "RELEASE_PROCESS_ENFORCED_CURRENT"
    assert rows["REQ-048"]["status"] == "RELEASE_EVIDENCE_REQUIRED_CURRENT"

    for req in ("REQ-046", "REQ-047", "REQ-048"):
        blob = " ".join(rows[req]["consumers"] + rows[req]["proof_objects"] + [rows[req]["status"]])
        assert "PROVED_0663" not in blob
        assert "build_plugin_dist_v0663.py" not in blob


def test_current_builder_and_loading_authorities_exist():
    for rel in (
        "scripts/build_plugin_dist_current.py",
        "references/CURRENT_CANONICAL_SKILL_BUILD.md",
        "prompts/canonical_authority_loading_map_CURRENT.md",
    ):
        assert (ROOT / rel).exists(), rel
