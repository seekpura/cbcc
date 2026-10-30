from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_current_release_package.py"


def _expected_authority() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def _expected_version_family() -> str:
    match = re.match(r"^(\d+\.\d+\.\d+)", _expected_authority())
    assert match
    return match.group(1)


def _load_checker():
    spec = importlib.util.spec_from_file_location("cbcc_current_release_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CurrentReleasePackageCheckerTests(unittest.TestCase):
    def test_checker_exists_and_derives_current_version(self):
        self.assertTrue(CHECKER.exists(), str(CHECKER))
        checker = _load_checker()
        self.assertEqual(checker.current_version_family(), _expected_version_family())
        self.assertEqual(checker.current_authority_version(), _expected_authority())

    def test_checker_requires_current_release_authorities(self):
        checker = _load_checker()
        required = set(checker.required_release_paths())
        for rel in (
            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json",
            "references/CURRENT_CANONICAL_SKILL_BUILD.md",
            "prompts/canonical_authority_loading_map_CURRENT.md",
            "scripts/build_plugin_dist_current.py",
            "scripts/check_v0664_requirement_consumer_map.py",
            "runtime/cbcc/strategy_culture_materialization.py",
        ):
            self.assertIn(rel, required)

    def test_checker_has_no_fixed_expected_release_constant(self):
        text = CHECKER.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"EXPECTED_VERSION\s*=\s*['\"]\d+\.\d+\.\d+['\"]")
        self.assertNotRegex(text, r"EXPECTED_AUTHORITY\s*=\s*['\"]\d+\.\d+\.\d+")

    def test_packaged_override_release_family_is_checked_directly(self):
        checker = _load_checker()
        expected = _expected_version_family()

        self.assertEqual(
            checker.validate_override_release_version({"current_release_version": expected}, expected),
            [],
        )
        issues = checker.validate_override_release_version(
            {"current_release_version": "0.6.66"}, expected
        )
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["code"], "PACKAGED_CURRENT_OVERRIDE_RELEASE_VERSION_MISMATCH")
        self.assertEqual(issues[0]["actual"], "0.6.66")
        self.assertEqual(issues[0]["expected"], expected)

    def test_final_package_checker_proves_strategy_culture_materialization_tokens(self):
        text = CHECKER.read_text(encoding="utf-8")
        for token in (
            "STRATEGY_CULTURE_MATERIALIZATION_TOKEN_MISSING",
            "product_truth_audit_table",
            "assumption_decision_log",
            "visual_execution_checklist",
            "output_self_check_rows",
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
