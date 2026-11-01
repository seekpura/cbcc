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


def _direction(asset_ids: list[str]):
    return {
        'require_portfolio_differentiation_review': True,
        'portfolio_differentiation_review': {
            'status': 'PASS',
            'adjacent_asset_review': [
                {
                    'pair': asset_ids,
                    'delta': 'explicit route-specific visual difference',
                }
            ],
            'keep_reauthor_merge_delete': [
                {'asset_id': aid, 'decision': 'KEEP'} for aid in asset_ids
            ],
        },
    }


def test_semantic_camera_or_view_alone_does_not_activate_scene_derived_photography_gate():
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

    result = validate_portfolio_differentiation(
        architecture,
        _direction(['AST-G08', 'AST-V01']),
    )

    assert result['photography_asset_count_reviewed'] == 0, result
    assert result['status'] == 'PASS', result
    assert not any(
        issue['type'] == 'MISSING_SCENE_DERIVED_PHOTOGRAPHY_EXECUTION'
        for issue in result['issues']
    ), result


def test_explicit_photographic_carrier_still_activates_scene_derived_photography_gate():
    photo = _asset(
        'AST-PHOTO',
        'IMAGE',
        'LIFESTYLE_PHOTOGRAPHY',
        'environment-led product use frame',
        'photographic use-context route',
    )
    result = validate_portfolio_differentiation(
        {'assets': [photo]},
        _direction(['AST-PHOTO']),
    )

    assert result['photography_asset_count_reviewed'] == 1, result
    issue = next(
        item for item in result['issues']
        if item['type'] == 'MISSING_SCENE_DERIVED_PHOTOGRAPHY_EXECUTION'
    )
    assert issue['asset_ids'] == ['AST-PHOTO']
    assert set(issue['missing']) == {'camera', 'lighting', 'cmf'}
    assert result['status'] == 'RETURN_TO_AGENT'
