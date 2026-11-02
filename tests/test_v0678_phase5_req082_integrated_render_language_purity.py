from __future__ import annotations

from cbcc.integrated_render_route_authority import finalize_integrated_render_route


def _bundle():
    return {
        'model_prompt_en': 'Commercial hero frame.',
        'model_prompt_cn': '商业主视觉画面。',
        'prompt_en': 'Commercial hero frame.',
        'prompt_cn': '商业主视觉画面。',
        'renderer_recipe': {},
        'design_card': {},
    }


def _asset(typography):
    return {
        'asset_id': 'AST-P5-TYPE',
        'visible_copy': {'target_copy': 'SERUM HARIAN'},
        'asset_art_direction': {
            'copy_render_route': 'MODEL_RENDER_INTEGRATED',
            'typography': typography,
        },
    }


def test_integrated_render_selects_each_authored_typography_locale_without_dict_dump():
    out = finalize_integrated_render_route(
        _asset({'cn': '深绿无衬线', 'en': 'Forest-green sans serif.'}),
        _bundle(),
    )

    en = out['model_prompt_en']
    cn = out['model_prompt_cn']
    assert 'Typography/layout execution: Forest-green sans serif.' in en
    assert '深绿无衬线' not in en
    assert "{'cn':" not in en
    assert '排版执行：深绿无衬线' in cn
    assert 'Forest-green sans serif.' not in cn
    assert "{'cn':" not in cn
    assert 'SERUM HARIAN' in en and 'SERUM HARIAN' in cn


def test_chinese_only_typography_is_not_relabelled_or_machine_translated_into_english_prompt():
    out = finalize_integrated_render_route(
        _asset({'cn': '深绿无衬线'}),
        _bundle(),
    )

    en = out['model_prompt_en']
    cn = out['model_prompt_cn']
    assert '深绿无衬线' not in en
    assert 'Typography/layout execution:' not in en
    assert '排版执行：深绿无衬线' in cn
    assert 'SERUM HARIAN' in en and 'SERUM HARIAN' in cn


def test_neutral_structured_typography_keeps_structure_without_cross_locale_values():
    typography = {
        'font_family': {'cn': '思源黑体', 'en': 'Inter'},
        'weight': '600',
        'alignment': 'left',
    }
    out = finalize_integrated_render_route(_asset(typography), _bundle())

    en = out['model_prompt_en']
    cn = out['model_prompt_cn']
    assert 'font_family: Inter' in en
    assert '思源黑体' not in en
    assert 'weight: 600' in en
    assert 'font_family: 思源黑体' in cn
    assert 'font_family: Inter' not in cn
