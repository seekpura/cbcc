from __future__ import annotations

from cbcc.portfolio_visual_authority import validate_portfolio_differentiation


def _review():
    return {
        'status': 'PASS',
        'adjacent_asset_review': [
            {'pair': ['AST-G08', 'AST-V01'], 'delta': 'static three-step usage system → motion-led daily routine sequence'},
        ],
        'keep_reauthor_merge_delete': [
            {'asset_id': 'AST-G08', 'decision': 'KEEP'},
            {'asset_id': 'AST-V01', 'decision': 'KEEP'},
        ],
    }


def _asset(asset_id: str, carrier: str, composition: str, rhythm_delta: str):
    return {
        'asset_id': asset_id,
        'asset_type': 'IMAGE' if asset_id == 'AST-G08' else 'VIDEO',
        'art_direction_status': 'AUTHORED',
        'asset_art_direction': {
            'visual_carrier': carrier,
            'composition_grammar': composition,
            'layout_geometry': f'{asset_id} layout',
            'scale_depth': f'{asset_id} scale',
            'negative_space': f'{asset_id} negative space',
            'camera_or_view': f'{asset_id} camera',
            'material_response': f'{asset_id} material response',
            'product_presence': {'planning_state': 'REQUIRED', 'product_role': asset_id},
            # portfolio_rhythm_delta is the canonical field used by v0.6.70+
            # prompt lineage / Human projection / semantic integrity contracts.
            'portfolio_rhythm_delta': rhythm_delta,
        },
    }


def test_canonical_portfolio_rhythm_delta_counts_as_adjacent_asset_delta():
    direction = {
        'require_portfolio_differentiation_review': True,
        'portfolio_differentiation_review': _review(),
    }
    architecture = {
        'assets': [
            _asset('AST-G08', 'editorial usage system', 'three-step modular path', 'usage still after proof frame'),
            _asset('AST-V01', 'motion-led routine sequence', 'temporal close-up sequence', 'motion sequence after static usage frame'),
        ]
    }

    result = validate_portfolio_differentiation(architecture, direction)

    assert result['status'] == 'PASS'
    assert not any(issue['type'] == 'MISSING_ADJACENT_ASSET_DELTA' for issue in result['issues'])
