from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from runtime.cbcc.requirement_authority import (
    AUTHORITY_CLASSES,
    audit_requirement_authority,
    load_current_requirement_authority,
)

ROOT = Path(__file__).parents[1]

DIRECT_USER_REQUIREMENT_IDS = {
    'REQ-052', 'REQ-053', 'REQ-054', 'REQ-055', 'REQ-056',
    'REQ-057', 'REQ-058', 'REQ-059', 'REQ-060',
}
LATER_USER_REQUIREMENT_IDS = {
    'REQ-004',  # 用户明确反对“为了验证而验证”；验证只能是证据而非产品本身。
    'REQ-016',  # 中文为基础语言，外文同步中文释义/注释。
    'REQ-018',  # HTML 必须是完整可用 Human Workspace，而非流水席/薄摘要。
    'REQ-019',  # Asset Universe 动态策划；平台槽位只约束 Activation。
    'REQ-027',  # 真实商品普通源图默认 reference-guided；exact pixel 仅显式需要。
}


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


def test_user_attribution_sets_are_independent_source_authored_authorities():
    doc = load_current_requirement_authority(ROOT)
    assert set(doc['direct_user_requirement_ids']) == DIRECT_USER_REQUIREMENT_IDS
    assert set(doc['later_user_requirement_ids']) == LATER_USER_REQUIREMENT_IDS

    canonical_rows = {row['req'] for row in doc['requirements'] if row['authority_class'] == 'USER_CANONICAL'}
    later_rows = {row['req'] for row in doc['requirements'] if row['authority_class'] == 'USER_LATER_CLARIFICATION'}
    assert canonical_rows == DIRECT_USER_REQUIREMENT_IDS
    assert later_rows == LATER_USER_REQUIREMENT_IDS

    polluted = deepcopy(doc)
    polluted['direct_user_requirement_ids'].append('REQ-008')
    assert 'DIRECT_USER_SET_MISMATCH' in _issues(polluted)


def test_normalized_or_engineering_expansions_keep_user_lineage_without_impersonating_user():
    doc = load_current_requirement_authority(ROOT)
    expected = {
        'REQ-003': 'UC-E-01',       # auto-complete details expand the explicit max-10-and-continue lock
        'REQ-008': 'UC-H-01',       # older normalized truth rule is derived; exact direct handle is REQ-053
        'REQ-032': 'UC-H-05',       # full people execution object expands the direct inclusive-photography requirement
        'REQ-061': 'UL-03',         # canonical graph is an architecture derived from the same-source clarification
        'REQ-084': 'UL-06',         # Presence/Fidelity independent axes are architecture derived from fidelity clarification
        'REQ-086': 'UC-E-02',       # scene-derived production closure expands the direct visual execution lock
        'REQ-089': 'UL-02',         # full canonical workspace projection expands the direct HTML workspace request
    }
    for req, source in expected.items():
        row = _req(doc, req)
        assert row['authority_class'] == 'DERIVED_PRODUCT_PRINCIPLE', (req, row)
        assert source in row['derived_from'], (req, row)


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


def test_reference_guided_correction_preserves_direct_user_core_and_derived_architecture():
    doc = load_current_requirement_authority(ROOT)
    direct = _req(doc, 'REQ-027')
    assert direct['authority_class'] == 'USER_LATER_CLARIFICATION'
    assert 'UL-06' in direct['origin_refs']

    for req in ('REQ-026', 'REQ-084'):
        row = _req(doc, req)
        assert row['authority_class'] == 'DERIVED_PRODUCT_PRINCIPLE'
        assert 'UL-06' in row['derived_from']

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
