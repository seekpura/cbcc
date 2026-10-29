from __future__ import annotations


def test_plugin_wrapper_and_default_prompts_use_native_reference_and_dynamic_asset_universe():
    from scripts import build_plugin_dist as b
    wrapper=b.skill_wrapper('0.6.33')
    joined='\n'.join(b.DEFAULT_PROMPTS)
    for text in (wrapper,joined):
        assert 'REFERENCE_GUIDED_NATIVE_LOCK' in text or '强模型 Reference Input' in text or '强模型输入' in text
        assert 'EXACT_PIXEL_COMPOSITE' in text
        assert 'Asset Universe' in text or '资产宇宙' in text
    assert 'LOCKED_SOURCE_COMPOSITE 仍必须围绕最终商品' not in wrapper
    assert '生成可合成底片' not in wrapper
    assert 'LOCKED_SOURCE_COMPOSITE 仍须按最终商品' not in joined
    assert '生成可合成底片' not in joined
    assert '同一消费者问题和同一 Surface 也允许 H01/H02/H03' in wrapper
    assert '平台最大图片数只限制同时上线集合' in wrapper


def test_packaged_wrapper_says_exact_pixel_composite_is_explicit_only():
    from scripts import build_plugin_dist as b
    wrapper=b.skill_wrapper('0.6.33')
    assert 'EXACT_PIXEL_COMPOSITE' in wrapper
    assert '仅在用户明确要求' in wrapper
    assert '原始源图像素层不可改变' in wrapper
    assert '原生生成完整最终画面中的同一真实商品身份' in wrapper
