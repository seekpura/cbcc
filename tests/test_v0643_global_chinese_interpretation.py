from pathlib import Path
import json

from cbcc.human_language_delivery import normalize_upload_center
from cbcc.global_chinese_interpretation import normalize_global_chinese_interpretation
from cbcc.final_chinese_interpretation_audit import audit_final_chinese_interpretation
from cbcc.chinese_interpretation_ui import apply_chinese_interpretation_ui


def _write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def _base_center(listing_active: bool = True):
    return {
        'delivery_language': {'locale': 'zh-CN'},
        'task_scope': {'listing_active': listing_active},
        'copy_center': [],
        'preserved_listing_fields': [],
    }


def _normalize(center):
    return normalize_global_chinese_interpretation(normalize_upload_center(center))


def test_listing_category_description_attributes_search_and_faq_all_require_cn_companion(tmp_path):
    center = _base_center(True)
    center['copy_center'] = [
        {'field': 'category', 'label': '平台类目', 'label_zh_semantic': True, 'value': 'Beauty > Skin Care > Moisturizers'},
        {'field': 'description', 'label': '商品描述', 'label_zh_semantic': True, 'value': 'Lightweight daily gel for oily-looking skin.'},
        {'field': 'attributes', 'label': '商品属性', 'label_zh_semantic': True, 'value': {'skin_type': 'Oily / Combination', 'texture': 'Lightweight gel'}},
        {'field': 'search_terms', 'label': '搜索词', 'label_zh_semantic': True, 'value': ['oil control gel', 'lightweight moisturiser']},
        {'field': 'faq', 'label': '常见问题', 'label_zh_semantic': True, 'value': [{'question': 'When should I use it?', 'answer': 'Use after cleansing.'}]},
    ]
    audit = audit_final_chinese_interpretation(tmp_path, _normalize(center))
    assert audit['status'] == 'INCOMPLETE'
    missing = {(x.get('scope'), x.get('field')) for x in audit['issues']}
    for field in ('category', 'description', 'attributes', 'search_terms', 'faq'):
        assert ('LISTING', field) in missing


def test_mixed_attribute_object_does_not_pass_just_because_one_leaf_is_chinese(tmp_path):
    center = _base_center(True)
    center['copy_center'] = [{
        'field': 'attributes',
        'label': '商品属性',
        'label_zh_semantic': True,
        'value': {'skin_type': '油性肌肤', 'texture': 'Lightweight gel'},
    }]
    audit = audit_final_chinese_interpretation(tmp_path, _normalize(center))
    assert audit['status'] == 'INCOMPLETE'
    assert any(x.get('scope') == 'LISTING' and x.get('field') == 'attributes' for x in audit['issues'])


def test_preserved_listing_content_still_requires_cn_if_it_is_shown_to_humans(tmp_path):
    center = _base_center(False)
    center['preserved_listing_fields'] = [
        {'field': 'category', 'label': '平台类目', 'value': 'Beauty > Skin Care'},
        {'field': 'description', 'label': '商品描述', 'value': 'Daily lightweight gel.'},
    ]
    audit = audit_final_chinese_interpretation(tmp_path, _normalize(center))
    assert audit['status'] == 'INCOMPLETE'
    assert {x.get('field') for x in audit['issues'] if x.get('scope') == 'PRESERVED_LISTING'} == {'category', 'description'}


def test_video_ads_review_and_research_foreign_human_copy_require_same_object_cn(tmp_path):
    support = tmp_path / 'supporting_analysis'
    _write(support / 'video_creator_plan.json', {
        'videos': [{'hook': 'Fresh hydration without a heavy feel', 'on_screen_text': 'LIGHTWEIGHT DAILY GEL', 'voiceover': 'Use after cleansing.'}]
    })
    _write(support / 'ad_analysis.json', {
        'creative_variants': [{'hook': 'Oily skin still needs hydration', 'headline': 'Keep it light', 'primary_text': 'A lightweight daily gel.', 'cta': 'Shop now'}]
    })
    _write(support / 'feedback_analysis.json', {
        'reviews': [{'review_excerpt': 'It feels light and absorbs fast.'}]
    })
    _write(support / 'market_analysis.json', {
        'customer_voice': [{'quote': 'I want hydration without a sticky finish.'}]
    })
    audit = audit_final_chinese_interpretation(tmp_path, _normalize(_base_center(False)))
    assert audit['status'] == 'INCOMPLETE'
    scopes = {x.get('scope') for x in audit['issues']}
    assert {'VIDEO', 'ADS', 'REVIEW', 'RESEARCH'} <= scopes


def test_same_object_cn_companions_make_global_human_copy_pass(tmp_path):
    support = tmp_path / 'supporting_analysis'
    _write(support / 'video_creator_plan.json', {
        'videos': [{
            'hook': 'Fresh hydration without a heavy feel', 'hook_zh': '清爽补水，不留厚重肤感',
            'on_screen_text': 'LIGHTWEIGHT DAILY GEL', 'on_screen_text_zh': '轻盈日用凝胶',
            'voiceover': 'Use after cleansing.', 'voiceover_zh': '洁面后使用。',
        }]
    })
    _write(support / 'ad_analysis.json', {
        'creative_variants': [{
            'hook': 'Oily skin still needs hydration', 'hook_zh': '油性肌肤同样需要补水',
            'headline': 'Keep it light', 'headline_zh': '轻盈护理',
            'primary_text': 'A lightweight daily gel.', 'primary_text_zh': '轻盈的日常凝胶。',
            'cta': 'Shop now', 'cta_zh': '立即购买（CTA 用途）',
        }]
    })
    _write(support / 'feedback_analysis.json', {
        'reviews': [{'review_excerpt': 'It feels light and absorbs fast.', 'review_excerpt_zh': '用户反馈：肤感轻盈，吸收较快。'}]
    })
    _write(support / 'market_analysis.json', {
        'customer_voice': [{'quote': 'I want hydration without a sticky finish.', 'quote_zh': '消费者希望补水同时避免黏腻肤感。'}]
    })
    center = _base_center(True)
    center['copy_center'] = [
        {'field': 'category', 'label': '平台类目', 'label_zh_semantic': True, 'value': 'Beauty > Skin Care > Moisturizers', 'delivery_translation': '美妆 > 护肤 > 保湿产品'},
        {'field': 'description', 'label': '商品描述', 'label_zh_semantic': True, 'value': 'Lightweight daily gel.', 'delivery_translation': '轻盈的日常凝胶。'},
        {'field': 'attributes', 'label': '商品属性', 'label_zh_semantic': True, 'value': {'texture': 'Lightweight gel'}, 'delivery_translation': '质地：轻盈凝胶。'},
        {'field': 'search_terms', 'label': '搜索词', 'label_zh_semantic': True, 'value': ['oil control gel'], 'delivery_translation': '搜索意图：控油凝胶。'},
        {'field': 'faq', 'label': '常见问题', 'label_zh_semantic': True, 'value': [{'question': 'When should I use it?', 'answer': 'After cleansing.'}], 'delivery_translation': '问：什么时候使用？答：洁面后使用。'},
    ]
    audit = audit_final_chinese_interpretation(tmp_path, _normalize(center))
    assert audit['status'] == 'PASS'
    assert audit['global_human_content']['final_status'] == 'PASS'


def test_formal_asset_delivery_translation_zh_reconciles_legacy_asset_audit(tmp_path):
    asset_dir = tmp_path / 'asset_packages' / 'A01'
    _write(asset_dir / '14_visible_copy_block.json', {
        'target_market_copy': 'LIGHTWEIGHT DAILY GEL',
        'delivery_translation_zh': '轻盈日用凝胶',
    })
    base_audit = {
        'status': 'INCOMPLETE',
        'issues': [{
            'scope': 'ASSET_VISIBLE_COPY',
            'asset_id': 'A01',
            'path': 'target_market_copy',
            'code': 'FOREIGN_ASSET_COPY_WITHOUT_CN_COMPANION',
            'value': 'LIGHTWEIGHT DAILY GEL',
        }],
        'assets': {'status': 'INCOMPLETE', 'issue_count': 1},
        'listing': {'status': 'PASS', 'issue_count': 0},
    }
    audit = audit_final_chinese_interpretation(tmp_path, _normalize(_base_center(False)), base_audit=base_audit)
    assert audit['status'] == 'PASS'
    assert audit['assets']['status'] == 'PASS'
    assert not audit['issues']


def test_technical_identifiers_do_not_require_literal_translation(tmp_path):
    center = _base_center(True)
    center['copy_center'] = [
        {'field': 'sku', 'label': 'SKU', 'label_zh_semantic': True, 'value': 'K01-30G'},
        {'field': 'gtin', 'label': 'GTIN 商品条码', 'label_zh_semantic': True, 'value': '1234567890123'},
        {'field': 'url', 'label': '链接', 'label_zh_semantic': True, 'value': 'https://example.com/p/1'},
    ]
    audit = audit_final_chinese_interpretation(tmp_path, _normalize(center))
    assert not [x for x in audit['issues'] if x.get('code') == 'FOREIGN_LISTING_COPY_WITHOUT_CN_COMPANION']


def test_final_contract_does_not_accept_pending_cn_interpretation_as_ready(tmp_path):
    center = _base_center(True)
    center['copy_center'] = [
        {'field': 'title', 'label': '产品标题', 'label_zh_semantic': True, 'value': 'Daily Oil-Balancing Gel', 'delivery_companion_status': '待补中文释义'}
    ]
    audit = audit_final_chinese_interpretation(tmp_path, _normalize(center))
    assert audit['status'] == 'INCOMPLETE'
    assert any(x.get('code') == 'FOREIGN_LISTING_COPY_WITHOUT_CN_COMPANION' for x in audit['issues'])


def test_localized_listing_raw_keys_are_secondary_to_chinese_human_labels():
    page = '<div class="locale-field"><strong>description</strong><span>APPROVED_FINAL</span></div>'
    out = apply_chinese_interpretation_ui(page)
    assert '<strong>商品描述<small class="heading-en">description</small></strong>' in out
