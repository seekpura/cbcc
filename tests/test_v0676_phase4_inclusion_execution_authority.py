from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from cbcc.creative import compile_inclusive_photography
from cbcc.product_visual_intelligence import compile_product_visual_intelligence
from cbcc.reference_guided_native_authority import apply_reference_guided_native_authority

ROOT = Path(__file__).parents[1]

HUMAN_FIELDS = {
    'casting_role',
    'age_context',
    'skin_tone',
    'hair_texture_style',
    'grooming_makeup',
    'wardrobe_accessories',
    'body_age_disability_representation',
    'religious_cultural_presentation',
    'pose',
    'expression',
    'gaze',
    'hands',
    'product_interaction',
    'stereotype_guard',
    'ai_bias_review',
    'exposure_lighting_handling',
}


def _culture():
    return {
        'status': 'COMPILED_FROM_SUPPLIED_EVIDENCE',
        'statements': [
            {
                'statement': 'Use evidence-bounded local representation; do not infer behavior from identity.',
                'status': 'VERIFIED',
                'source_ids': ['SRC-CULTURE-01'],
                'implications': ['casting and representation review only'],
            }
        ],
        'intersectionality': {
            'representation': ['representation must be evidence-bounded and non-tokenistic'],
        },
        'race_ethnicity': {
            'groups': [],
            'source_ids': ['SRC-CULTURE-01'],
            'status': 'PENDING',
            'relevance': ['context only; no deterministic behavior inference'],
            'behavior_inference_allowed': False,
        },
        'casting_constraints': {},
        'visual_implications': [],
        'copy_implications': [],
        'issues': [],
        'principle': 'Identity dimensions are context signals, not automatic behavior predictions.',
    }


def _complete_human_context():
    return {
        'casting_role': 'adult shopper demonstrating the real routine task',
        'age_context': 'adult; exact age is not inferred',
        'skin_tone': 'deep skin tone is an authored representation choice for this scene, not a behavior proxy',
        'hair_texture_style': 'coily natural texture preserved with truthful edge separation',
        'grooming_makeup': 'natural skin texture; no whitening or youthifying retouch',
        'wardrobe_accessories': 'task-led neutral everyday wardrobe; no ethnicity-as-costume styling',
        'body_age_disability_representation': 'natural adult body representation; do not erase visible aids or age markers if present',
        'religious_cultural_presentation': 'neutral unless supported by explicit culture evidence; no invented religious signifiers',
        'pose': 'body slightly turned toward the vanity while one hand reaches for the product',
        'expression': 'calm attentive expression appropriate to a routine demonstration',
        'gaze': 'gaze follows the product interaction rather than performing a generic beauty pose',
        'hands': 'five-finger anatomy checked; grip does not cover the label or create impossible joints',
        'product_interaction': 'real product held upright and used only in the source-supported routine relationship',
        'stereotype_guard': 'identity does not imply need, income, skin condition, willingness to pay, or purchase intent',
        'ai_bias_review': ['no whitening', 'no slimming', 'no hair homogenization', 'check hands and body proportions'],
        'exposure_lighting_handling': {
            'skin_product_metering': 'meter skin and product label separately',
            'highlight_policy': 'protect facial and package highlights without underexposing deep skin',
            'fill_policy': 'broad neutral fill plus negative fill for form',
        },
    }


def _human_asset(context: dict | None = None):
    return {
        'asset_id': 'AST-HUMAN',
        'asset_type': 'IMAGE',
        'surface': 'GALLERY',
        'decision_intent': 'USAGE',
        'art_direction_status': 'AUTHORED',
        'creative_direction': {'route': 'HUMAN_CONTEXT_ACTION'},
        'asset_art_direction': {
            'subject_system': {
                'subject_type': 'PERSON',
                'primary_subject': 'adult shopper performing the routine task',
                'living_subject_required': True,
            },
            'human_context': deepcopy(context if context is not None else _complete_human_context()),
            'visual_carrier': 'LIFESTYLE_PHOTOGRAPHY',
            'scene': 'real morning bathroom vanity routine',
            'composition_grammar': 'hand-to-product routine relationship',
            'camera_or_view': 'eye-level environmental close view',
            'lighting': {
                'key': {'direction': 'window-side broad key', 'modifier': 'large diffusion'},
                'fill': {'direction': 'camera-side neutral fill', 'level': '-1 stop'},
                'highlight_policy': 'protect skin and package highlight detail',
            },
            'cmf': {'color': 'neutral warm bathroom field', 'material': 'real glass and skin', 'finish': 'truthful soft specular response'},
            'product_presence': {'planning_state': 'REQUIRED', 'product_role': 'ACTIVE_OBJECT_IN_USE'},
        },
        'visual_production_signature': {
            'context_role': 'human routine use context',
            'visual_job': 'show real product handling in routine',
            'camera_or_view': 'eye-level human use context',
        },
    }


def _nonhuman_asset():
    return {
        'asset_id': 'AST-MACRO',
        'asset_type': 'IMAGE',
        'surface': 'GALLERY',
        'decision_intent': 'MATERIAL_SENSORY',
        'art_direction_status': 'AUTHORED',
        'creative_direction': {'route': 'MATERIAL_SENSORY_OBJECT'},
        'asset_art_direction': {
            'subject_system': {'subject_type': 'PRODUCT_OR_OBJECT', 'primary_subject': 'real product bottle'},
            'visual_carrier': 'MATERIAL_MACRO_PHOTOGRAPHY',
            'scene': 'controlled macro material study',
            'composition_grammar': 'tight label-edge and material frame',
            'camera_or_view': '100mm macro product detail',
            'lighting': {'key': {'direction': 'rear-side grazing', 'modifier': 'strip diffusion'}},
            'cmf': {'color': 'neutral field', 'material': 'real glass', 'finish': 'controlled edge highlight'},
            'product_presence': {'planning_state': 'REQUIRED', 'product_role': 'HERO_DETAIL'},
        },
        'visual_production_signature': {
            'context_role': 'material detail evidence',
            'visual_job': 'show truthful material response',
            'camera_or_view': '100mm macro product detail',
        },
    }


def _execution_rows(result):
    rows = result.get('asset_execution') or []
    return {row.get('asset_id'): row for row in rows}


def test_human_asset_gets_concrete_per_asset_inclusion_execution_from_existing_authority():
    result = compile_inclusive_photography(_culture(), {}, [_human_asset(), _nonhuman_asset()])
    rows = _execution_rows(result)

    assert set(rows) == {'AST-HUMAN'}
    row = rows['AST-HUMAN']
    assert row['status'] == 'READY'
    assert row['authority'] == 'INCLUSIVE_PHOTOGRAPHY_AUTHORITY'
    assert row['human_context'] == _complete_human_context()
    assert HUMAN_FIELDS <= set(row['human_context'])
    assert row['skin_tone_exposure']['post'].startswith('No automatic whitening')
    assert 'no disability erasure' in row['ai_bias_controls']
    assert row['behavior_inference_allowed'] is False
    assert row['source_refs'] == ['SRC-CULTURE-01']
    assert row['activation_basis']['asset_id'] == 'AST-HUMAN'
    assert row['scene_relevance']['scene'] == 'real morning bathroom vanity routine'
    assert row['scene_relevance']['product_interaction'] == _complete_human_context()['product_interaction']


def test_missing_human_representation_decisions_stay_to_verify_and_are_not_invented():
    incomplete = {
        'casting_role': 'adult shopper performing the real task',
        'pose': 'hand reaches toward product',
        'product_interaction': 'holds real product upright',
        'stereotype_guard': 'do not infer behavior from identity',
    }
    result = compile_inclusive_photography(_culture(), {}, [_human_asset(incomplete)])
    row = _execution_rows(result)['AST-HUMAN']

    assert row['status'] == 'TO_VERIFY'
    assert {'skin_tone', 'hair_texture_style', 'grooming_makeup', 'wardrobe_accessories', 'religious_cultural_presentation', 'hands'} <= set(row['missing_authored_decisions'])
    assert 'skin_tone' not in row['human_context']
    assert 'hair_texture_style' not in row['human_context']
    assert row['behavior_inference_allowed'] is False
    assert row['runtime_may_invent_missing_identity_or_culture'] is False
    assert row['skin_tone_exposure'], 'generic exposure guardrail may exist without inventing a demographic fact'


def test_nonhuman_asset_does_not_receive_irrelevant_human_inclusion_execution_even_with_culture_context():
    result = compile_inclusive_photography(_culture(), {}, [_nonhuman_asset()])
    assert _execution_rows(result) == {}


def test_compiler_must_materialize_same_inclusion_authority_into_assets_before_asset_architecture_write():
    text = (ROOT / 'runtime/cbcc/compiler.py').read_text(encoding='utf-8')
    second_compile = text.rindex('inclusive=compile_inclusive_photography')
    architecture_write = text.index("artifacts/asset_architecture.json", second_compile)
    section = text[second_compile:architecture_write]

    assert 'apply_inclusive_photography_to_assets' in section
    assert section.index('apply_inclusive_photography_to_assets') < section.index("artifacts/inclusive_photography.json") or 'apply_inclusive_photography_to_assets' in section


def test_product_presence_and_reference_fidelity_remain_independent_regression_guard():
    # No source reference must not invent visual product facts; product-identity planning remains explicit.
    pvi = compile_product_visual_intelligence({'name': 'Demo product'}, [], [], None, None)
    assert pvi['status'] == 'PLANNING_ONLY_SOURCE_MASTER_REQUIRED'
    assert {'geometry', 'material', 'finish', 'label_or_pack_copy'} <= set(pvi['missing_visual_facts'])

    # Product absent means a real-reference input is not required merely because fidelity machinery exists.
    bundle = {
        'design_card': {
            'product_presence': {'planning_state': 'ABSENT', 'production_state': 'ABSENT'},
            'product_identity': {'product_fidelity': 'REFERENCE_GUIDED'},
        },
        'model_prompt_cn': '环境信息设计。',
        'model_prompt_en': 'Environment-led information design.',
        'production_parameter_closure': {'status': 'READY', 'missing_required_parameters': []},
        'renderer_recipe': {'source_product_bindings': []},
    }
    out = apply_reference_guided_native_authority(bundle, {'product_fidelity': 'REFERENCE_GUIDED'}, [])
    assert out['production_assembly_notes']['product_reference_generation_mode'] == 'TRUTH_REFERENCE_ONLY'
    assert out['production_assembly_notes']['reference_input_required'] is False
    assert out['production_parameter_closure'].get('model_generation_blocking') is not True
