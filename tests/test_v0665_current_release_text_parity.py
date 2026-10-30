from __future__ import annotations

from scripts import build_plugin_dist_v0664 as v0664


def test_current_canonical_skill_has_no_stale_hard_coded_release_proof_version():
    text = v0664.canonical_skill('0.6.64')
    assert 'Before claiming v0.6.62 behavior complete:' not in text
    assert 'Before claiming v0.6.63 behavior complete:' not in text
    assert 'Before claiming current installed release behavior complete:' in text


def test_release_proof_boundary_remains_semantically_intact_after_generic_wording():
    text = v0664.canonical_skill('0.6.64')
    for token in (
        'installed `plugin.json`',
        'top and deep Skills must be byte-identical and current',
        'fresh real K01 FULL project',
        'Provider/Review/Revision/QA',
    ):
        assert token in text
