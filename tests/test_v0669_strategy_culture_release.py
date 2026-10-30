from __future__ import annotations

import hashlib
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / 'scripts' / 'build_plugin_dist_v0669.py'
EXPECTED_V068_BYTES = 45014
EXPECTED_V068_SHA256 = '4c244d58fb4289fe9f32a38ea0eef9fbb974c9c6ac2a39b7f01618a65cea913d'


def _load_builder():
    spec = importlib.util.spec_from_file_location('cbcc_v0669_builder', BUILDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V0669StrategyCultureReleaseTests(unittest.TestCase):
    def test_builder_exists_without_importing_historical_builder(self):
        self.assertTrue(BUILDER.exists(), str(BUILDER))
        text = BUILDER.read_text(encoding='utf-8')
        self.assertNotRegex(text, r'from scripts\.build_plugin_dist_v\d+')
        self.assertIn("VERSION = '0.6.69'", text)
        self.assertIn("AUTHORITY_VERSION = '0.6.69-strategy-culture-materialization-closure'", text)

    def test_reconstructed_v068_floor_is_exact(self):
        builder = _load_builder()
        text = builder.current_v068_floor()
        data = text.encode('utf-8')
        self.assertEqual(len(data), EXPECTED_V068_BYTES)
        self.assertEqual(hashlib.sha256(data).hexdigest(), EXPECTED_V068_SHA256)

    def test_v069_is_additive_and_names_first_class_materialization(self):
        builder = _load_builder()
        skill = builder.canonical_skill()
        self.assertIn('## 0.17 Packaged CURRENT Override Release-Family Proof — v0.6.68', skill)
        self.assertIn('## 0.18 Strategy / Culture / Execution First-Class Materialization — v0.6.69', skill)
        for token in (
            'product_truth_audit_table',
            'assumption_decision_log',
            'intersectionality_table',
            'visual_execution_checklist',
            'RACE传播框架执行表',
            '族裔文化适配检查表',
            'P0 / P1 / P2',
            'output_self_check_rows',
            'C级不得作硬宣称',
        ):
            self.assertIn(token, skill)
        self.assertRegex(skill, r'(?m)^version: 0\.6\.69-strategy-culture-materialization-closure$')
        self.assertRegex(skill, r'(?m)^# Cross-Border Commerce Creative v0\.6\.69$')


if __name__ == '__main__':
    unittest.main()
