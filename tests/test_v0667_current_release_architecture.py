from __future__ import annotations

import hashlib
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_plugin_dist_v0667.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("cbcc_v0667_builder", BUILDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V0667CurrentReleaseArchitectureTests(unittest.TestCase):
    def test_builder_exists_and_does_not_import_historical_versioned_builder(self):
        self.assertTrue(BUILDER.exists(), str(BUILDER))
        text = BUILDER.read_text(encoding="utf-8")
        self.assertIn("from scripts import build_plugin_dist as base", text)
        self.assertNotRegex(text, r"from scripts import build_plugin_dist_v\d+")
        self.assertNotRegex(text, r"import scripts\.build_plugin_dist_v\d+")

    def test_reconstructed_v0666_floor_matches_verified_installed_skill(self):
        builder = _load_builder()
        floor = builder.current_v0666_floor().encode("utf-8")
        self.assertEqual(len(floor), 40612)
        self.assertEqual(
            hashlib.sha256(floor).hexdigest(),
            "c9ac4577e38ef50cdfc033fae08f96f8b3d749583de89d360f35d390f684e06a",
        )

    def test_v0667_skill_is_additive_and_current_release_aware(self):
        builder = _load_builder()
        skill = builder.canonical_skill("0.6.67")
        self.assertIn("version: 0.6.67-current-release-freshness-architecture", skill)
        self.assertIn("# Cross-Border Commerce Creative v0.6.67", skill)
        self.assertIn("## 0.15 Strict Requirement Consumer Accounting + Current Baseline Build", skill)
        self.assertIn("## 0.16 CURRENT Release Freshness Architecture", skill)
        self.assertIn("REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json", skill)
        self.assertIn("check_current_release_package.py", skill)
        self.assertIn("build_plugin_dist_current.py", skill)
        self.assertIn("Fresh positive K01 FULL", skill)


if __name__ == "__main__":
    unittest.main()
