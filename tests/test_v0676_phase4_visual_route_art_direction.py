from __future__ import annotations

from cbcc.agent_autonomy import compile_agent_autonomy_plan, compile_agent_next_action
from cbcc.portfolio_visual_authority import validate_portfolio_differentiation


VISUAL_ROUTE_CASES = [
    ('AST-UGC', 'BRIEF', 'UGC_BRIEF'),
    ('AST-LIVE', 'LIVE', 'LIVE'),
    ('AST-LANDING', 'PAGE', 'LANDING_PAGE_HERO'),
]


def _target():
    return {
        'market': 'MY',
        'platform_family': 'TikTok Shop',
        'site': 'MY',
        'category': 'Beauty',
        'surfaces': ['UGC_BRIEF', 'LIVE', 'LANDING_PAGE_HERO'],
    }


def _plan():
    return compile_agent_autonomy_plan({
        'target': _target(),
        'compile_assets': True,
        'agent_plan': {
            'creative_exploration': {
                'portfolio_visual_program': {
                    'visual_territory': 'credible product truth expressed through route-native visual worlds',
                    'carrier_mix': ['creator routine', 'live demonstration', 'landing editorial system'],
                    'product_presence_rhythm': ['supporting', 'hero', 'hero'],
                    'scale_density_rhythm': 'intimate creator crop -> live demonstration field -> spacious landing hierarchy',
                    'composition_rhythm': 'handheld routine -> demonstration table -> editorial landing sequence',
                    'continuity_tokens': ['truthful product identity', 'controlled green accent'],
                    'deliberate_breaks': ['creator route uses embodied action', 'landing route uses spatial information hierarchy'],
                    'delete_merge_logic': 'merge only when shopper job and visual mechanism are materially identical',
                    'mechanism_bindings': ['embodied routine', 'live proof', 'editorial information world'],
                },
                'portfolio_differentiation_review': {
                    'status': 'PASS_AFTER_REAUTHOR',
                    'adjacent_asset_review': [{'pair': ['AST-UGC', 'AST-LIVE'], 'delta': 'creator intimacy vs live proof'}],
                    'keep_reauthor_merge_delete': [{'asset_id': 'AST-UGC', 'decision': 'KEEP'}],
                },
            }
        },
    })


def _next(plan, architecture):
    return compile_agent_next_action(
        plan,
        request={},
        research_gate={},
        asset_architecture=architecture,
        creative_council={'selected_direction': {'direction_id': 'DIR-P4'}},
        compliance={},
        production_run={},
        gate_scope={},
        content_requiredness={},
    )


def test_active_visual_routes_beyond_image_video_block_when_art_direction_is_missing():
    plan = _plan()
    architecture = {
        'assets': [
            {
                'asset_id': aid,
                'asset_type': asset_type,
                'surface': surface,
                'art_direction_status': 'MISSING_AGENT_DECISION',
            }
            for aid, asset_type, surface in VISUAL_ROUTE_CASES
        ],
        'decision_coverage_summary': {},
    }

    result = _next(plan, architecture)
    blockers = [row for row in result.get('blocking_frontier') or [] if row.get('action') == 'AUTHOR_PER_ASSET_ART_DIRECTION']

    assert blockers, result
    assert set(blockers[0]['items']) == {'AST-UGC', 'AST-LIVE', 'AST-LANDING'}
    assert result['recommended_next_action'] == 'AUTHOR_PER_ASSET_ART_DIRECTION'


def _authored(aid, asset_type, surface, *, composition, carrier, delta):
    return {
        'asset_id': aid,
        'asset_type': asset_type,
        'surface': surface,
        'art_direction_status': 'AUTHORED',
        'asset_art_direction': {
            'visual_carrier': carrier,
            'composition_grammar': composition,
            'layout_geometry': composition,
            'scale_depth': 'route-specific scale program',
            'negative_space': 'route-specific breathing field',
            'material_response': 'truthful product and environment response',
            'deliberate_difference': delta,
            'product_presence': {'planning_state': 'REQUIRED', 'product_role': 'route-native product role'},
        },
    }


def test_portfolio_visual_validation_reviews_non_image_video_visual_routes():
    direction = {
        'require_portfolio_differentiation_review': True,
        'portfolio_differentiation_review': {
            'status': 'PASS_AFTER_REAUTHOR',
            'adjacent_asset_review': [{'pair': ['AST-UGC', 'AST-LIVE'], 'delta': 'claimed difference'}],
            'keep_reauthor_merge_delete': [{'asset_id': 'AST-UGC', 'decision': 'KEEP'}],
        },
    }
    # Deliberately duplicate the actual visual signature. The validator must not ignore these
    # merely because their delivery route is UGC / LIVE rather than IMAGE / VIDEO.
    architecture = {
        'assets': [
            _authored('AST-UGC', 'BRIEF', 'UGC_BRIEF', composition='same visual grammar', carrier='ROUTE_VISUAL', delta='claimed creator difference'),
            _authored('AST-LIVE', 'LIVE', 'LIVE', composition='same visual grammar', carrier='ROUTE_VISUAL', delta='claimed live difference'),
        ]
    }

    validation = validate_portfolio_differentiation(architecture, direction)

    assert validation['asset_count_reviewed'] == 2
    assert validation['status'] == 'RETURN_TO_AGENT'
    assert validation['duplicate_signature_groups'] == [['AST-UGC', 'AST-LIVE']]
