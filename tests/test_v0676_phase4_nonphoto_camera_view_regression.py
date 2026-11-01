from __future__ import annotations

from cbcc.portfolio_visual_authority import validate_portfolio_differentiation


def _asset(asset_id: str, asset_type: str, carrier: str, composition: str, delta: str):
    return {
        'asset_id': asset_id,
        'asset_type': asset_type,
        'art_direction_status': 'AUTHORED',
        'asset_art_direction': {
            'visual_carrier': carrier,
            'composition_grammar': composition,
            'layout_geometry': f'{asset_id} layout',
            'scale_depth': f'{asset_id} scale',
            'negative_space': f'{asset_id} negative space',
            # Semantic framing label only. This is not an authored photographic execution contract.
            'camera_or_view': f'{asset_id} camera',
            'material_response': f'{asset_id} material response',
            'product_presence': {'planning_state': 'REQUIRED', 'product_role': asset_id},
            'portfolio_rhythm_delta': delta,
        },
    }


def test_semantic_camera_or_view_alone_does_not_activate_scene_derived_photography_gate():
    direction = {
        'require_portfolio_differentiation_review': True,
        'portfolio_differentiation_review': {
            'status': 'PASS',
            'adjacent_asset_review': [
                {
                    'pair': ['AST-G08', 'AST-V01'],
                    'delta': 'static modular usage system -> temporal motion-led routine sequence',
                }
            ],
            'keep_reauthor_merge_delete': [
                {'asset_id': 'AST-G08', 'decision': 'KEEP'},
                {'asset_id': 'AST-V01', 'decision': 'KEEP'},
            ],
        },
    }
    architecture = {
        'assets': [
            _asset(
                'AST-G08',
                'IMAGE',
                'editorial usage system',
                'three-step modular path',
                'usage still after proof frame',
            ),
            _asset(
                'AST-V01',
                'VIDEO',
                'motion-led routine sequence',
                'temporal close-up sequence',
                'motion sequence after static usage frame',
            ),
        ]
    }

    result = validate_portfolio_differentiation(architecture, direction)

    assert result['photography_asset_count_reviewed'] == 0, result
    assert result['status'] == 'PASS', result
    assert not any(
        issue['type'] == 'MISSING_SCENE_DERIVED_PHOTOGRAPHY_EXECUTION'
        for issue in result['issues']
    ), result
