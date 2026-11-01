from __future__ import annotations

from copy import deepcopy

from cbcc.agent_autonomy import compile_agent_autonomy_plan
from cbcc.asset_architecture import build_asset_architecture
from cbcc.creative import apply_creative_system_to_assets


def _target():
    return {
        'target_id': 'T-P4-VM',
        'market': 'MY',
        'platform_family': 'TikTok Shop',
        'site': 'MY',
        'category': 'Beauty',
        'surfaces': ['GALLERY'],
    }


def _program():
    return {
        'visual_territory': 'credible product truth with tactile editorial tension',
        'carrier_mix': ['real-product hero', 'human routine crop', 'material macro'],
        'product_presence_rhythm': ['hero', 'supporting', 'absent'],
        'scale_density_rhythm': 'large sparse hero -> intimate routine -> tight macro',
        'composition_rhythm': 'asymmetric depth -> embodied diagonal -> near-abstract detail',
        'continuity_tokens': ['truthful product identity', 'controlled green accent'],
        'deliberate_breaks': ['routine route changes the carrier from object-led to embodied action'],
        'delete_merge_logic': 'merge only when shopper job and visual mechanism are materially identical',
        'mechanism_bindings': ['editorial depth', 'embodied routine', 'material interruption'],
    }


def _review():
    return {
        'status': 'PASS_AFTER_REAUTHOR',
        'adjacent_asset_review': [
            {'pair': ['AST-HERO', 'AST-ROUTINE'], 'delta': 'object-led identity vs embodied routine'},
        ],
        'keep_reauthor_merge_delete': [
            {'asset_id': 'AST-HERO', 'decision': 'KEEP'},
        ],
    }


def _authored_art(asset_id: str):
    return {
        'asset_id': asset_id,
        'visual_carrier': 'REAL_PRODUCT_HERO',
        'composition_grammar': 'asymmetric product depth with evidence breathing field',
        'layout_geometry': 'product right / evidence left',
        'scale_depth': 'large product foreground with restrained depth',
        'negative_space': 'left evidence field',
        'material_response': 'truthful glass and liquid highlight control',
        'deliberate_difference': 'opening identity hero',
        'product_presence': {
            'planning_state': 'REQUIRED',
            'product_role': 'hero',
            'presence_why': 'Identity is the decision job of this asset.',
        },
    }


def test_portfolio_program_is_materialized_as_pre_asset_canonical_visual_master():
    program = _program()
    plan = compile_agent_autonomy_plan({
        'target': _target(),
        'product': {'name': 'Example Product'},
        'audience_culture': {'market': 'MY'},
        'compile_assets': True,
        'agent_plan': {
            'portfolio_visual_program': deepcopy(program),
            'portfolio_differentiation_review': _review(),
            'asset_art_directions': [_authored_art('AST-HERO')],
        },
    })

    master = plan['creative_exploration'].get('visual_master')
    assert master, plan['creative_exploration']
    assert master['status'] == 'READY'
    assert master['authority'] == 'HOST_AGENT'
    assert master['authority_stage'] == 'PRE_ASSET_ARCHITECTURE'
    assert master['source_authority'] == 'PORTFOLIO_VISUAL_PROGRAM'
    assert master['portfolio_visual_program'] == program
    assert master['visual_master_id'].startswith('VM-')
    assert master['authority_hash']
    assert master['runtime_may_invent_visual_strategy'] is False
    assert master['per_asset_art_direction_must_adapt_not_copy'] is True
    assert master['target_context']['market'] == 'MY'
    assert master['target_context']['platform_family'] == 'TikTok Shop'


def test_asset_architecture_consumes_one_pre_asset_master_without_copying_a_second_visual_system():
    master = {
        'schema_version': 'cbcc-visual-master-v0.6.76',
        'status': 'READY',
        'authority': 'HOST_AGENT',
        'authority_stage': 'PRE_ASSET_ARCHITECTURE',
        'source_authority': 'PORTFOLIO_VISUAL_PROGRAM',
        'visual_master_id': 'VM-LOCKED-01',
        'authority_hash': 'hash-locked-01',
        'portfolio_visual_program': _program(),
        'runtime_may_invent_visual_strategy': False,
        'per_asset_art_direction_must_adapt_not_copy': True,
    }
    target = _target()
    target['phase4_visual_master'] = deepcopy(master)
    architecture = build_asset_architecture(
        'P4-VM',
        target,
        ['What is this product?'],
        [],
        [{
            'asset_name': 'Hero',
            'consumer_question': 'What is this product?',
            'surface': 'GALLERY',
            'family': 'VISUAL',
            'decision_intent': 'IDENTIFY',
            'strategic_job': 'Resolve product identity.',
        }],
        {},
        'BEAUTY',
    )

    assert architecture['phase4_visual_master']['visual_master_id'] == 'VM-LOCKED-01'
    assert architecture['phase4_visual_master']['portfolio_visual_program'] == _program()
    assert len(architecture['assets']) == 1
    ref = architecture['assets'][0]['visual_master_ref']
    assert ref == {
        'visual_master_id': 'VM-LOCKED-01',
        'authority_hash': 'hash-locked-01',
        'authority_stage': 'PRE_ASSET_ARCHITECTURE',
    }
    assert 'portfolio_visual_program' not in architecture['assets'][0], 'Assets should reference the canonical master, not duplicate it.'


def test_creative_assignment_keeps_same_visual_master_reference_while_per_asset_art_direction_stays_authoritative():
    master = {
        'schema_version': 'cbcc-visual-master-v0.6.76',
        'status': 'READY',
        'authority': 'HOST_AGENT',
        'authority_stage': 'PRE_ASSET_ARCHITECTURE',
        'source_authority': 'PORTFOLIO_VISUAL_PROGRAM',
        'visual_master_id': 'VM-LOCKED-02',
        'authority_hash': 'hash-locked-02',
        'portfolio_visual_program': _program(),
        'runtime_may_invent_visual_strategy': False,
        'per_asset_art_direction_must_adapt_not_copy': True,
    }
    art = _authored_art('AST-HERO')
    architecture = {
        'phase4_visual_master': deepcopy(master),
        'assets': [{
            'asset_id': 'AST-HERO',
            'asset_name': 'Hero',
            'asset_type': 'IMAGE',
            'surface': 'GALLERY',
            'family': 'VISUAL',
            'consumer_question': 'What is this product?',
            'decision_intent': 'IDENTIFY',
            'strategic_job': 'Resolve product identity.',
            'visual_master_ref': {
                'visual_master_id': 'VM-LOCKED-02',
                'authority_hash': 'hash-locked-02',
                'authority_stage': 'PRE_ASSET_ARCHITECTURE',
            },
        }],
    }
    direction = {
        'direction_id': 'DIR-P4-VM',
        'decision': 'SELECT',
        'source': 'HOST_AGENT_AUTHORED',
        'require_per_asset_art_direction': True,
        'require_portfolio_differentiation_review': True,
        'portfolio_visual_program': _program(),
        'portfolio_differentiation_review': _review(),
        'asset_art_directions': [art],
    }
    council = {
        'selected_direction': direction,
        'directions': [direction],
        'alternative_directions': [],
        'direction_source': 'USER_SUPPLIED',
    }

    out = apply_creative_system_to_assets(architecture, council, {}, None)
    assignment = out['creative_system_assignment']
    assert assignment['visual_master_ref'] == {
        'visual_master_id': 'VM-LOCKED-02',
        'authority_hash': 'hash-locked-02',
        'authority_stage': 'PRE_ASSET_ARCHITECTURE',
    }
    assert out['assets'][0]['visual_master_ref'] == assignment['visual_master_ref']
    assert out['assets'][0]['asset_art_direction']['composition_grammar'] == art['composition_grammar']
    assert out['assets'][0]['asset_art_direction']['deliberate_difference'] == 'opening identity hero'
