from __future__ import annotations

from pathlib import Path

from runtime.cbcc.integrated_render_route_authority import finalize_integrated_render_route

ROOT = Path(__file__).resolve().parents[1]


def test_cumulative_requirement_ledger_contains_current_hard_requirements():
    text = (ROOT / 'references' / 'CONVERSATION_REQUIREMENT_AUDIT.md').read_text(encoding='utf-8')
    required = [
        'REQ-001',  # additive-only
        'REQ-004',  # validation is evidence
        'REQ-006',  # seven tools
        'REQ-013',  # economics integrity
        'REQ-018',  # complete HTML
        'REQ-019',  # open-world universe
        'REQ-022',  # presence/fidelity independent
        'REQ-025',  # integrated final render default
        'REQ-027',  # reference-guided native product
        'REQ-030',  # structured Art Direction before Prompt
        'REQ-031',  # scene-derived photography
        'REQ-035',  # concrete prompt consumption audit
        'REQ-037',  # no five-file shortcut
        'REQ-038',  # provider/result/review/revision/hash
        'REQ-039',  # actual-output QA
        'REQ-043',  # no permanent capability menu
        'REQ-046',  # re-read cumulative long requirements
        'REQ-049',  # real FULL regression fixture
        'REQ-050',  # K01 negative fixture
    ]
    missing = [req for req in required if req not in text]
    assert missing == []


def test_source_non_regression_lock_requires_cumulative_ledger():
    text = (ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').read_text(encoding='utf-8')
    assert 'CONVERSATION_REQUIREMENT_AUDIT.md' in text
    assert 'actual FULL project materialization path' in text
    assert 'Product Presence and copy-render route' in text


def test_integrated_copy_and_native_product_reference_override_legacy_post_copy_default():
    asset = {
        'asset_id': 'A1',
        'visible_copy': {
            'target_copy': 'KAWAL MINYAK. KEKALKAN HIDRASI.',
            'delivery_translation': '控油，同时保持补水。',
        },
        'product_presence': {
            'planning_state': 'REQUIRED',
            'presence_why': 'product identity is decision-critical',
        },
        'asset_art_direction': {
            'copy_render_route': 'MODEL_RENDER_INTEGRATED',
            'typography': 'large BM headline integrated in the upper-left information field',
        },
    }
    bundle = {
        'prompt_cn': (
            '【Surface / 信息设计】\n'
            '生成画面时为锁定文案预留清晰版式区，但不要让图像模型重写包装文字或最终营销文案；'
            '精确文案在后期确定性合成。\n'
        ),
        'prompt_en': (
            '[SURFACE / INFORMATION DESIGN]\n'
            'Reserve deliberate layout zones for locked copy, but do not ask the image model to retype packaging '
            'or final marketing copy. Exact approved text is composed deterministically after generation.\n'
        ),
        'renderer_recipe': {
            'source_product_bindings': [
                {'locator': {'kind': 'LOCAL_FILE_PATH', 'value': '/tmp/product.jpg'}}
            ],
            'text_policy': {
                'exact_copy_mode': 'DETERMINISTIC_COMPOSITION_AFTER_RENDER',
                'image_model_may_rewrite_locked_copy': False,
            },
            'deterministic_text_composition': True,
        },
        'design_card': {
            'product_identity': {'product_fidelity': 'REFERENCE_GUIDED'},
            'information_design': {},
        },
    }

    out = finalize_integrated_render_route(asset, bundle)

    assert 'KAWAL MINYAK. KEKALKAN HIDRASI.' in out['prompt_cn']
    assert 'KAWAL MINYAK. KEKALKAN HIDRASI.' in out['prompt_en']
    assert '确定性合成' not in out['prompt_cn']
    assert 'deterministically after generation' not in out['prompt_en']
    assert out['renderer_recipe']['text_policy']['exact_copy_mode'] == 'MODEL_RENDER_INTEGRATED'
    assert out['renderer_recipe']['deterministic_text_composition'] is False
    assert out['design_card']['product_identity']['product_fidelity'] == 'REFERENCE_GUIDED_NATIVE_LOCK'
    assert out['renderer_recipe']['source_product_bindings'][0]['visible_subject_binding'] is True


def test_explicit_post_composite_is_preserved_as_a_per_asset_choice():
    asset = {
        'asset_id': 'A2',
        'copy_render_route': 'POST_COMPOSITE',
        'product_presence': {
            'planning_state': 'REQUIRED',
            'presence_why': 'explicit professional composite route',
        },
        'product_fidelity': 'EXACT_PIXEL_COMPOSITE',
        'asset_art_direction': {},
        'visible_copy': {'target_copy': 'EXACT COPY'},
    }
    bundle = {
        'prompt_cn': '背景生成。\n',
        'prompt_en': 'Generate the background.\n',
        'renderer_recipe': {
            'source_product_bindings': [],
            'text_policy': {'exact_copy_mode': 'DETERMINISTIC_COMPOSITION_AFTER_RENDER'},
            'deterministic_text_composition': True,
        },
        'design_card': {'product_identity': {'product_fidelity': 'EXACT_PIXEL_COMPOSITE'}, 'information_design': {}},
    }
    out = finalize_integrated_render_route(asset, bundle)
    assert out['renderer_recipe']['text_policy']['exact_copy_mode'] == 'DETERMINISTIC_COMPOSITION_AFTER_RENDER'
    assert out['renderer_recipe']['deterministic_text_composition'] is True
    assert out['design_card']['product_identity']['product_fidelity'] == 'EXACT_PIXEL_COMPOSITE'
