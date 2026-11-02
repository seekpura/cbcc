from copy import deepcopy

from runtime.cbcc.claim_authority import compile_claim_authority
from runtime.cbcc.strategy_depth import build_positioning_depth, build_sku_depth, build_value_depth


def test_explicit_c_claim_is_a_ceiling_and_cannot_become_primary_hard_claim():
    request = {
        'product': {'name': 'Demo Gel', 'category': 'beauty'},
        'sources': [
            {
                'source_id': 'SRC-PROD',
                'kind': 'USER_PROVIDED_PRODUCT_TRUTH',
                'source_type': 'PRODUCT_SPEC',
                'as_of': '2026-11-01',
            }
        ],
        'claims': [
            {
                'claim_id': 'C1',
                'claim': 'Lightweight daily hydration',
                'status': 'APPROVED',
                'evidence_grade': 'C',
                'source_ids': ['SRC-PROD'],
            }
        ],
        'shopper_questions': ['What proof supports it?'],
    }

    authority = compile_claim_authority(request['claims'], request['sources'])
    row = authority['claims'][0]
    assert row['evidence_grade'] == 'C'
    assert row['publication_status'] == 'SOFT_ONLY_NO_HARD_CLAIM'

    value = build_value_depth(request, {'product': request['product']}, request['shopper_questions'])
    positioning = build_positioning_depth(
        request,
        value,
        {},
        build_sku_depth(request, {}, {}),
        {},
        request['shopper_questions'],
    )
    assert value['claim_value_ladder'][0]['evidence_grade'] == 'C'
    assert value['claim_value_ladder'][0]['publication_status'] == 'SOFT_ONLY_NO_HARD_CLAIM'
    assert positioning['primary_conversion_proposition'] != 'Lightweight daily hydration'
