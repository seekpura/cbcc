from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def test_root_skill_has_no_legacy_composite_default_authority():
    text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
    assert 'LOCKED_SOURCE_COMPOSITE 不是空背景生成' not in text
    assert '真实商品锁定默认是 Reference-Guided Native Generation，不是后期像素合成' in text
    assert 'EXACT_PIXEL_COMPOSITE' in text
    assert text.count('## Reference-Guided Native Product + Dynamic Asset Universe Authority') == 1


def test_packaged_wrapper_has_one_dynamic_asset_universe_authority_and_no_ambiguous_product_reference_line():
    from scripts import build_plugin_dist as b
    wrapper=b.skill_wrapper('0.6.34')
    assert wrapper.count('## Dynamic Asset Universe + Native Product Reference') == 1
    assert '产品图、包装图和源文件默认是设计参考，可按已选创意方向重绘/重渲染/风格化' not in wrapper
    assert '当 Product Presence 要求真实商品可见时，真实商品图/包装图作为强模型 Reference Input' in wrapper
    assert '生成可合成底片' not in wrapper
    assert 'LOCKED_SOURCE_COMPOSITE 仍必须围绕最终商品' not in wrapper


def test_version_is_v0634_cleanup():
    assert (ROOT/'VERSION').read_text(encoding='utf-8').strip()=='0.6.34-native-reference-authority-cleanup'
