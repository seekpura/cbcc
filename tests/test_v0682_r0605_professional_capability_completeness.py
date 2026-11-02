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


def test_context_sources_or_claim_metadata_alone_cannot_promote_claim_evidence():
    claims = [
        {
            'claim_id': 'CTX',
            'claim': 'Shoppers say the product works instantly',
            'status': 'APPROVED',
            'source_ids': ['SRC-REVIEW'],
        },
        {
            'claim_id': 'META',
            'claim': 'Contains a supported active',
            'status': 'APPROVED',
            'source_type': 'FORMULA SPEC',
        },
        {
            'claim_id': 'PROD',
            'claim': 'Contains glycerin',
            'status': 'APPROVED',
            'source_ids': ['SRC-PROD'],
        },
    ]
    sources = [
        {'source_id': 'SRC-REVIEW', 'kind': 'USER_PROVIDED_CONTEXT', 'source_type': 'CUSTOMER_REVIEW_EXPORT'},
        {'source_id': 'SRC-PROD', 'kind': 'USER_PROVIDED_PRODUCT_TRUTH', 'source_type': 'PRODUCT_SPEC'},
    ]

    out = compile_claim_authority(claims, sources)
    by_id = {row['claim_id']: row for row in out['claims']}
    assert by_id['CTX']['evidence_grade'] == 'C'
    assert by_id['CTX']['publication_status'] == 'SOFT_ONLY_NO_HARD_CLAIM'
    assert by_id['META']['evidence_grade'] == 'C'
    assert by_id['META']['publication_status'] == 'SOFT_ONLY_NO_HARD_CLAIM'
    assert by_id['PROD']['evidence_grade'] == 'B'
    assert by_id['PROD']['publication_status'] == 'BOUNDED_SUPPORTED_CLAIM'
