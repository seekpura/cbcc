from __future__ import annotations

import json
from pathlib import Path

from scripts import build_plugin_dist_v0649 as v0649


def test_canonical_skill_restores_language_continuity_contract():
    text = v0649.canonical_skill('0.6.49')
    required = [
        'Base project / operator content is Chinese-first',
        'Asset visible language is decided by curation',
        'Every asset delivery object must contain an English layer',
        'Every non-Chinese asset/content layer must have Chinese translation or explanation',
        'The required English layer does not mean English must be rendered in the final image/video',
        'Model Prompt EN',
        'Visible Copy Block',
    ]
    for token in required:
        assert token in text


def test_release_manifest_exposes_language_contract(tmp_path: Path):
    release = v0649.build(tmp_path / 'dist')
    contract = release['delivery_contract']
    assert contract['chinese_base_operator_content_required'] is True
    assert contract['asset_visible_language_authored_per_asset'] is True
    assert contract['english_layer_required_per_asset'] is True
    assert contract['non_chinese_same_object_chinese_companion_required'] is True
    assert contract['english_layer_does_not_force_visible_english'] is True

    manifest = json.loads((tmp_path / 'dist' / 'release_manifest.json').read_text(encoding='utf-8'))
    assert manifest['version'] == '0.6.49'
    assert manifest['authority_version'] == '0.6.49-chinese-base-asset-language-continuity'
