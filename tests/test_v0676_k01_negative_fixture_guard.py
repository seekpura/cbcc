from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_real_k01_negative_fixture_is_frozen_as_must_fail_acceptance():
    text = (ROOT / 'references' / 'K01_2026-10-30_REAL_OUTPUT_REGRESSION.md').read_text(encoding='utf-8')
    for token in [
        'NEGATIVE_FIXTURE / MUST_FAIL_FULL_ACCEPTANCE',
        'Every one of the 15 asset directories contains only five files',
        '01_design_card.md', '05_prompt_CN.txt', '06_prompt_EN.txt', '07_visible_copy.txt', '08_production_notes.txt',
        'A release must reject an equivalent project as FULL-complete',
        'no five-file Host shortcut may replace the mature asset package',
    ]:
        assert token in text, token


def test_equivalent_five_file_host_shortcut_is_rejected_by_full_auditor(tmp_path):
    full_depth = _load(ROOT / 'runtime' / 'cbcc' / 'full_delivery_depth_v3.py', 'cbcc_v0676_negative_full_depth')
    package = tmp_path / 'package'
    asset = package / 'asset_packages' / 'G01'
    asset.mkdir(parents=True)
    for name in ('01_design_card.md', '05_prompt_CN.txt', '06_prompt_EN.txt', '07_visible_copy.txt', '08_production_notes.txt'):
        (asset / name).write_text('shortcut', encoding='utf-8')

    result = full_depth.audit_host_full_package(package)
    assert result['status'] == 'INCOMPLETE'
    codes = {row['code'] for row in result['issues']}
    assert 'FULL_DELIVERY_OBJECT_MISSING' in codes
    assert 'ASSET_UNIVERSE_EXPORT_MISSING' in codes


def test_current_release_checker_requires_negative_fixture_in_built_plugin():
    checker = (ROOT / 'scripts' / 'check_current_release_package.py').read_text(encoding='utf-8')
    assert 'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md' in checker
