from __future__ import annotations
import hashlib

from scripts import build_plugin_dist_v0670 as release


def test_v069_frozen_skill_floor_is_exact():
    text=release.current_v069_floor();data=text.encode('utf-8')
    assert len(data)==48517
    assert hashlib.sha256(data).hexdigest()=='f3ed58aafc24947e85fc268144ea787d4db5eaed66b31008f6a5cf87500cbd54'


def test_v070_skill_is_additive_and_keeps_mature_authorities():
    text=release.canonical_skill()
    assert 'version: 0.6.70-canonical-materialization-human-projection-parity' in text
    assert '# Cross-Border Commerce Creative v0.6.70' in text
    assert '## 0.18 Strategy / Culture / Execution First-Class Materialization' in text
    assert '## 0.19 Canonical Materialization + Human Projection Parity' in text
    for token in (
        'Product Truth','Asset Opportunity Universe','REFERENCE_GUIDED_NATIVE_LOCK',
        'full Art Direction','cbcc-commercial-v1','Provider Job','Review','Revision',
        'canonical_art_direction_sha256','HTML_LISTING_PROJECTION_INCOMPLETE',
    ):
        assert token in text
