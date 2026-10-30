from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_current_release_package.py"


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
        self.assertEqual(checker.current_version_family(), "0.6.66")
        self.assertEqual(checker.current_authority_version(), "0.6.66-strict-consumer-current-baseline-build")

    def test_checker_requires_current_release_authorities(self):
        checker = _load_checker()
        required = set(checker.required_release_paths())
        for rel in (
            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json",
            "references/CURRENT_CANONICAL_SKILL_BUILD.md",
            "prompts/canonical_authority_loading_map_CURRENT.md",
            "scripts/build_plugin_dist_current.py",
            "scripts/check_v0664_requirement_consumer_map.py",
        ):
            self.assertIn(rel, required)

    def test_checker_has_no_fixed_expected_release_constant(self):
        text = CHECKER.read_text(encoding="utf-8")
        self.assertNotIn("EXPECTED_VERSION = '0.6.66'", text)
        self.assertNotIn('EXPECTED_VERSION = "0.6.66"', text)


if __name__ == "__main__":
    unittest.main()
