from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from runtime.cbcc.requirement_authority import (
    AUTHORITY_CLASSES,
    audit_requirement_authority,
    load_current_requirement_authority,
)

ROOT = Path(__file__).parents[1]


def _issues(document: dict) -> set[str]:
    return {str(row.get('code')) for row in audit_requirement_authority(document, root=ROOT).get('issues', [])}


def _req(document: dict, req: str) -> dict:
    return next(row for row in document['requirements'] if row['req'] == req)


def test_current_requirement_authority_has_exact_classes_and_req_001_090_once():
    doc = load_current_requirement_authority(ROOT)
    assert tuple(doc['authority_classes']) == AUTHORITY_CLASSES
    ids = [row['req'] for row in doc['requirements']]
    assert ids == [f'REQ-{i:03d}' for i in range(1, 91)]
    assert len(ids) == len(set(ids)) == 90
    audit = audit_requirement_authority(doc, root=ROOT)
    assert audit['status'] == 'PASS', audit['issues']


def test_req013_is_derived_from_price_truth_not_rewritten_as_user_canonical():
    doc = load_current_requirement_authority(ROOT)
    row = _req(doc, 'REQ-013')
    assert row['authority_class'] == 'DERIVED_PRODUCT_PRINCIPLE'
    assert 'UC-H-03' in row['derived_from']
    assert '竞品' in row['current_interpretation'] or 'competitor' in row['current_interpretation'].lower()
    assert '不可编造' in row['current_interpretation'] or 'not fabricate' in row['current_interpretation'].lower()

    polluted = deepcopy(doc)
    bad = _req(polluted, 'REQ-013')
    bad['authority_class'] = 'USER_CANONICAL'
    bad['origin_refs'] = ['UC-H-03']
    assert 'DIRECT_USER_ATTRIBUTION_MISMATCH' in _issues(polluted)


def test_derived_and_engineering_rules_require_explicit_lineage():
    doc = load_current_requirement_authority(ROOT)
    derived_or_guard = [
        row for row in doc['requirements']
        if row['authority_class'] in {'DERIVED_PRODUCT_PRINCIPLE', 'ENGINEERING_GUARD'}
    ]
    assert derived_or_guard
    assert all(row['derived_from'] for row in derived_or_guard)

    polluted = deepcopy(doc)
    row = next(r for r in polluted['requirements'] if r['authority_class'] in {'DERIVED_PRODUCT_PRINCIPLE', 'ENGINEERING_GUARD'})
    row['derived_from'] = []
    assert 'DERIVED_LINEAGE_MISSING' in _issues(polluted)


def test_rejected_deprecated_rules_cannot_have_active_business_consumers():
    doc = load_current_requirement_authority(ROOT)
    assert doc['rejected_deprecated']
    polluted = deepcopy(doc)
    polluted['rejected_deprecated'][0]['active_business_consumers'] = ['runtime/cbcc/strategy_authority.py']
    assert 'REJECTED_RULE_HAS_ACTIVE_BUSINESS_CONSUMER' in _issues(polluted)


def test_tests_and_workflows_are_proof_only_not_business_authority():
    doc = load_current_requirement_authority(ROOT)
    polluted = deepcopy(doc)
    row = polluted['requirements'][0]
    row.setdefault('business_consumers', []).append('tests/test_fake_business_authority.py')
    assert 'TEST_PATH_AS_BUSINESS_CONSUMER' in _issues(polluted)


def test_machine_strategy_consumer_is_not_silently_promoted_to_human_projection():
    doc = load_current_requirement_authority(ROOT)
    row = _req(doc, 'REQ-062')
    assert 'runtime/cbcc/strategy_authority.py' in row['business_consumers']
    assert row['human_projection'] == ['NOT_DIRECT_HUMAN_FACING']


def test_reference_guided_correction_has_later_user_origin_and_supersedes_global_pixel_lock():
    doc = load_current_requirement_authority(ROOT)
    for req in ('REQ-027', 'REQ-084'):
        row = _req(doc, req)
        assert row['authority_class'] == 'USER_LATER_CLARIFICATION'
        assert 'UL-06' in row['origin_refs']
    deprecated = {row['authority_id']: row for row in doc['rejected_deprecated']}
    global_lock = deprecated['DEPRECATED-GLOBAL-PIXEL-LOCK']
    assert {'REQ-026', 'REQ-027', 'REQ-084'} <= set(global_lock['superseded_by'])
    assert global_lock['active_business_consumers'] == []


def test_all_p0_direct_user_anchors_have_runtime_and_human_consumption():
    doc = load_current_requirement_authority(ROOT)
    anchors = {row['source_id']: row for row in doc['user_source_anchors']}
    p0 = [row for row in anchors.values() if row.get('priority') == 'P0']
    assert p0
    for anchor in p0:
        bound = [_req(doc, req) for req in anchor['bound_requirements']]
        assert any(row.get('business_consumers') for row in bound), anchor['source_id']
        assert any(any(str(path) != 'NOT_DIRECT_HUMAN_FACING' for path in row.get('human_projection', [])) for row in bound), anchor['source_id']


def test_authority_overlay_is_not_a_second_business_decision_engine():
    doc = load_current_requirement_authority(ROOT)
    assert doc['rules']['authority_overlay_does_not_author_business_strategy'] is True
    assert doc['rules']['existing_requirement_ledgers_remain_semantic_sources'] is True
    assert doc['rules']['consumer_maps_remain_execution_wiring_authority'] is True
