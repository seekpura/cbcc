from __future__ import annotations

import hashlib
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_plugin_dist_v0668.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("cbcc_v0668_builder", BUILDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V0668PackagedOverrideReleaseProofTests(unittest.TestCase):
    def test_builder_exists_without_historical_builder_import(self):
        self.assertTrue(BUILDER.exists(), str(BUILDER))
        text = BUILDER.read_text(encoding="utf-8")
        self.assertIn("from scripts import build_plugin_dist as base", text)
        self.assertNotRegex(text, r"from scripts import build_plugin_dist_v\d+")
        self.assertNotRegex(text, r"import scripts\.build_plugin_dist_v\d+")

    def test_reconstructed_v067_floor_is_exact(self):
        builder = _load_builder()
        floor = builder.current_v067_floor().encode("utf-8")
        self.assertEqual(len(floor), 43534)
        self.assertEqual(
            hashlib.sha256(floor).hexdigest(),
            "5840e24d590c075e5682336fb76c9a0b38655486a4d17bf3bdec8bb60cfe4fa5",
        )

    def test_v068_adds_direct_packaged_override_release_proof(self):
        builder = _load_builder()
        skill = builder.canonical_skill("0.6.68")
        self.assertIn("version: 0.6.68-packaged-override-release-proof", skill)
        self.assertIn("# Cross-Border Commerce Creative v0.6.68", skill)
        self.assertIn("## 0.17 Packaged CURRENT Override Release-Family Proof", skill)
        self.assertIn("PACKAGED_CURRENT_OVERRIDE_RELEASE_VERSION_MISMATCH", skill)
        self.assertIn("Fresh positive K01 FULL", skill)


if __name__ == "__main__":
    unittest.main()
