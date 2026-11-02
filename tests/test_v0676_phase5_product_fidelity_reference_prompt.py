from __future__ import annotations

from cbcc.prompt_compiler import compile_asset_prompt


def _source() -> dict:
    return {
        'asset_id': 'SRC-PRODUCT-01',
        'role': 'REAL_PRODUCT_MASTER',
        'provider_asset_handle': 'provider://real-product-master-01',
        'sha256': 'sha256-real-product-master-01',
        'ingest_status': 'READY',
        'pixel_lock': True,
        'identity_features': ['package geometry', 'logo', 'label layout', 'primary color'],
    }


def _asset(*, presence: str = 'REQUIRED', fidelity_mode: str = 'EXACT_PIXEL_COMPOSITE') -> dict:
    visible = presence not in {'ABSENT', 'FORBIDDEN', 'NOT_APPLICABLE'}
    return {
        'asset_id': 'AST-P5-FIDELITY',
        'asset_type': 'IMAGE',
        'surface': 'GALLERY',
        'production_mode': 'GENERATIVE_IMAGE',
        'art_direction_status': 'AUTHORED',
        'consumer_question': 'What exactly is the product and can I trust the package identity?',
        'strategic_job': 'Preserve real product identity without letting reference mechanics decide whether the product appears.',
        'incremental_information': 'Verified package identity in an authored commercial scene.',
        'product_presence': {
            'planning_state': presence,
            'production_state': 'PRESENT' if visible else 'ABSENT',
            'product_role': 'HERO' if visible else 'NOT_IN_FRAME',
            'source_reference_role': 'LOCKED_SOURCE_LAYER' if visible else 'TRUTH_REFERENCE_ONLY',
        },
        'asset_art_direction': {
            'visual_objective': 'Show the authored commercial scene while preserving the exact product identity decision.',
            'visual_carrier': 'PRODUCT_CONTEXT_IMAGE',
            'visual_language': 'clean commercial realism',
            'subject': 'real product package in a simple authored context' if visible else 'decision-relevant context with no product in frame',
            'environment': 'minimal realistic vanity context',
            'composition_grammar': 'single focal hierarchy',
            'layout_geometry': 'product/context relationship is explicitly authored',
            'scale_depth': 'shallow commercial depth',
            'negative_space': 'clean upper-right breathing room',
            'camera_or_view': 'eye-level three-quarter commercial view',
            'lighting': {
                'key': {'direction': 'camera-left 45 degrees', 'modifier': 'large diffusion'},
                'fill': {'direction': 'camera-right', 'level': '-1 stop'},
                'cct': 5200,
            },
            'cmf': {'color': 'neutral warm field', 'material': 'real package material', 'finish': 'truthful highlight response'},
            'product_presence': {
                'planning_state': presence,
                'production_state': 'PRESENT' if visible else 'ABSENT',
                'product_role': 'HERO' if visible else 'NOT_IN_FRAME',
                'source_reference_role': 'LOCKED_SOURCE_LAYER' if visible else 'TRUTH_REFERENCE_ONLY',
            },
            'product_fidelity': {
                'authority': 'AGENT_ASSET_ART_DIRECTION',
                'mode': fidelity_mode,
                'source_asset_ids': ['SRC-PRODUCT-01'],
                'immutable_identity_fields': ['logo', 'packaging_print', 'geometry', 'proportions'],
            },
            'output_spec': '1600x1600, 1:1, sRGB',
            'copy_render_mode': 'NO_VISIBLE_COPY',
        },
        'approved_visual_elements': ['real product identity', 'minimal vanity context'],
        'precision_boundaries': ['no package redesign', 'no invented claims'],
        'editable_layer_contract': {'editable_layers': ['environment'], 'frozen_layers': ['product identity when present']},
    }


def _compile(asset: dict, sources: list[dict] | None = None) -> dict:
    return compile_asset_prompt(
        asset,
        {'name': 'K01'},
        {'market': 'MY', 'platform_family': 'TikTok Shop', 'site': 'MY', 'category': 'skincare'},
        {},
        {'primary_locale': 'en-MY', 'delivery_locale': 'zh-CN'},
        {}, None, None,
        sources if sources is not None else [_source()],
    )


def test_canonical_exact_pixel_fidelity_is_not_downgraded_to_default_reference_guided_generation():
    out = _compile(_asset(fidelity_mode='EXACT_PIXEL_COMPOSITE'))
    identity = out['design_card']['product_identity']
    renderer = out['renderer_recipe']
    notes = out['production_assembly_notes']
    closure = out['production_parameter_closure']
    assert identity['product_fidelity'] == 'EXACT_PIXEL_COMPOSITE', identity
    assert identity['reference_generation_mode'] == 'EXACT_PIXEL_COMPOSITE', identity
    assert notes['product_reference_generation_mode'] == 'EXACT_PIXEL_COMPOSITE', notes
    assert renderer['pixel_composite_required'] is True, renderer
    assert renderer['final_output_must_contain_generated_product'] is False, renderer
    assert closure['native_product_generation_required'] is False, closure
    assert closure['exact_pixel_composite_explicit_only'] is True, closure
    assert renderer['source_product_bindings'][0]['usage_role'] == 'EXACT_PIXEL_SOURCE_LAYER'
    assert renderer['source_product_bindings'][0]['pixel_copy_required'] is True
    assert 'natively render the product inside the complete final image' not in out['model_prompt_en']


def test_canonical_native_reference_mode_remains_native_and_model_prompt_receives_identity_preservation_instruction():
    out = _compile(_asset(fidelity_mode='REFERENCE_GUIDED_NATIVE_LOCK'))
    identity = out['design_card']['product_identity']
    renderer = out['renderer_recipe']
    en = out['model_prompt_en']
    assert identity['product_fidelity'] == 'REFERENCE_GUIDED_NATIVE_LOCK'
    assert identity['reference_generation_mode'] == 'REFERENCE_GUIDED_NATIVE_GENERATION'
    assert renderer['product_generation_mode'] == 'REFERENCE_GUIDED_NATIVE_GENERATION'
    assert renderer['pixel_composite_required'] is False
    assert renderer['final_output_must_contain_generated_product'] is True
    assert renderer['source_product_bindings'][0]['usage_role'] == 'NATIVE_SUBJECT_REFERENCE'
    assert 'Preserve product identity exactly' in en
    assert 'package geometry and proportions' in en
    assert 'logo' in en
    assert 'label layout' in en


def test_product_absence_wins_over_fidelity_and_does_not_require_or_generate_a_reference_subject():
    out = _compile(_asset(presence='ABSENT', fidelity_mode='EXACT_PIXEL_COMPOSITE'))
    renderer = out['renderer_recipe']
    notes = out['production_assembly_notes']
    closure = out['production_parameter_closure']
    en = out['model_prompt_en']
    assert notes['product_reference_generation_mode'] == 'TRUTH_REFERENCE_ONLY', notes
    assert notes['reference_input_required'] is False, notes
    assert renderer['pixel_composite_required'] is False, renderer
    assert renderer['final_output_must_contain_generated_product'] is False, renderer
    assert closure['native_product_generation_required'] is False, closure
    assert closure['final_product_visibility_required'] is False, closure
    assert 'product must not appear' in en.lower()
    assert 'natively render the product' not in en


def test_missing_visible_reference_remains_blocking_and_runtime_does_not_invent_a_source_binding():
    out = _compile(_asset(fidelity_mode='REFERENCE_GUIDED_NATIVE_LOCK'), sources=[])
    assert out['production_parameter_closure']['model_generation_blocking'] is True
    assert 'real_product_reference_input' in out['production_parameter_closure']['missing_required_parameters']
    assert out['renderer_recipe']['source_product_bindings'] == []
    assert out['model_prompt_status'] == 'REAL_PRODUCT_REFERENCE_INPUT_REQUIRED'
