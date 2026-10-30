from __future__ import annotations

# Release-contract characterization for the real observed v0.6.46 package regression.
# The actual uploaded ZIP is not committed; these assertions encode the failure modes it exposed.

from runtime.cbcc.full_delivery_depth_v3 import CORE_HOST_FULL_FILES


def test_full_contract_keeps_language_scope_source_and_commercial_authorities():
    required = set(CORE_HOST_FULL_FILES)
    assert 'HUMAN_LANGUAGE_AUDIT.json' in required
    assert 'DELIVERY_LANGUAGE_MATRIX_AUDIT.json' in required
    assert 'PLATFORM_SCOPE.json' in required
    assert 'SOURCE_TRUTH_MEDIA_AUDIT.json' in required
    assert 'strategy/strategy_authority.json' in required
    assert 'strategy/COMMERCE_DECISION_CONTEXT.json' in required
    assert 'strategy/COMMERCIAL_CONTINUITY_AUDIT.json' in required
    assert 'supporting_analysis/product_truth.json' in required
    assert 'supporting_analysis/culture_context.json' in required
    assert 'supporting_analysis/asset_architecture.json' in required
    assert 'ASSET_UNIVERSE.json' in required
    assert 'FULL_DELIVERY_OBJECT_MANIFEST.json' in required


def test_full_contract_is_not_nine_gallery_packages():
    # Explicit guard against reverting completion semantics to a 7/9-image gallery count.
    text = '\n'.join(CORE_HOST_FULL_FILES)
    assert 'LST-09' not in text
    assert 'ASSET_UNIVERSE.json' in text
