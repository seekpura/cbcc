from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_v0664_requirement_consumer_map.py"


def _expected_version_family() -> str:
    authority = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    match = re.match(r"^(\d+\.\d+\.\d+)", authority)
    assert match, authority
    return match.group(1)


def _load_checker():
    spec = importlib.util.spec_from_file_location("cbcc_requirement_consumer_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CurrentRequirementFreshnessTests(unittest.TestCase):
    def test_current_release_overrides_are_consumed_and_reported(self):
        checker = _load_checker()
        result = checker.audit()
        expected = _expected_version_family()

        self.assertEqual(result["current_overrides_applied"], ["REQ-046", "REQ-047", "REQ-048"])
        self.assertEqual(result["current_version_family"], expected)
        self.assertEqual(result["current_override_release_version"], expected)
        self.assertEqual(result["current_builder_target"], expected)
        self.assertEqual(result["status"], "PASS", result)

    def test_release_process_rows_are_current_not_historical(self):
        checker = _load_checker()
        rows = {row["req"]: row for row in checker.effective_requirement_rows()}

        self.assertEqual(rows["REQ-046"]["status"], "RELEASE_PROCESS_ENFORCED_CURRENT")
        self.assertEqual(rows["REQ-047"]["status"], "RELEASE_PROCESS_ENFORCED_CURRENT")
        self.assertEqual(rows["REQ-048"]["status"], "RELEASE_EVIDENCE_REQUIRED_CURRENT")

        for req in ("REQ-046", "REQ-047", "REQ-048"):
            blob = " ".join(rows[req]["consumers"] + rows[req]["proof_objects"] + [rows[req]["status"]])
            self.assertNotIn("PROVED_0663", blob)
            self.assertNotIn("build_plugin_dist_v0663.py", blob)

    def test_current_builder_and_loading_authorities_exist(self):
        for rel in (
            "scripts/build_plugin_dist_current.py",
            "references/CURRENT_CANONICAL_SKILL_BUILD.md",
            "prompts/canonical_authority_loading_map_CURRENT.md",
        ):
            self.assertTrue((ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
