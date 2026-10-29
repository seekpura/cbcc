from __future__ import annotations

from pathlib import Path
import json

from cbcc.human_language_delivery import normalize_upload_center, audit_human_language_delivery


def _center(value: str = 'Daily Clarifying Essence', translation: str | None = None, field: str = 'title'):
    row = {
        'field': field,
        'label': field,
        'value': value,
        'status': 'READY',
        'required_for_current_scope': True,
        'delivery_translation': translation,
    }
    return {
        'delivery_language': {'locale': 'zh-CN'},
        'target': {'delivery_locale': 'zh-CN', 'locale': 'en-MY'},
        'task_scope': {'listing_active': True},
        'copy_center': [row],
        'preserved_listing_fields': [],
        'localized_copy': [],
    }


def _write_asset(package: Path, visible_copy: dict, with_cn_prompt: bool = True):
    asset = package / 'asset_packages' / 'LST-02'
    asset.mkdir(parents=True)
    (asset / '04_layout_contract.json').write_text(
        json.dumps({'visible_copy': visible_copy}, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    (asset / '06_prompt_EN.txt').write_text('Create a premium commerce asset.', encoding='utf-8')
    if with_cn_prompt:
        (asset / '05_prompt_CN.txt').write_text('制作一张中文审阅权威下的电商资产。', encoding='utf-8')
    (asset / '00_HUMAN_DESIGN_CARD_CN.md').write_text('# 资产人类设计卡（中文）\n', encoding='utf-8')


def test_listing_field_title_is_chinese_base_and_foreign_copy_requires_companion(tmp_path: Path):
    center = normalize_upload_center(_center(translation='每日净澈精华'))
    row = center['copy_center'][0]
    assert row['label'] == '产品标题'
    assert row['field_raw'] == 'title'
    audit = audit_human_language_delivery(tmp_path, center)
    assert audit['status'] == 'PASS', audit

    missing = normalize_upload_center(_center(translation=None))
    audit2 = audit_human_language_delivery(tmp_path, missing)
    assert audit2['status'] == 'INCOMPLETE'
    assert any(x['code'] == 'FOREIGN_LISTING_COPY_WITHOUT_CN_COMPANION' for x in audit2['issues'])


def test_common_platform_fields_get_semantic_chinese_titles(tmp_path: Path):
    center = normalize_upload_center(_center(value='CN', translation='原产国：中国', field='country_of_origin'))
    row = center['copy_center'][0]
    assert row['label'] == '原产国'
    assert row['label_zh_semantic'] is True
    assert audit_human_language_delivery(tmp_path, center)['status'] == 'PASS'


def test_unknown_platform_field_cannot_hide_behind_raw_english_title(tmp_path: Path):
    center = normalize_upload_center(_center(value='Some value', translation='某项平台字段内容', field='mystery_platform_field'))
    row = center['copy_center'][0]
    assert row['label'].startswith('平台字段（原字段：')
    audit = audit_human_language_delivery(tmp_path, center)
    assert audit['status'] == 'INCOMPLETE'
    assert any(x['code'] == 'LISTING_FIELD_TITLE_CN_SEMANTIC_MISSING' for x in audit['issues'])


def test_asset_foreign_visible_copy_requires_per_object_chinese_companion(tmp_path: Path):
    center = normalize_upload_center({
        'delivery_language': {'locale': 'zh-CN'},
        'target': {'delivery_locale': 'zh-CN', 'locale': 'en-MY'},
        'task_scope': {'listing_active': False},
        'copy_center': [], 'preserved_listing_fields': [], 'localized_copy': [],
    })
    _write_asset(tmp_path, {
        'headline': 'Daily Clarifying & Brightening Essence',
        'cta': 'Use daily',
        'delivery_translation': {
            'headline': '日常净澈焕亮精华',
            'cta': '每日使用',
        },
    })
    audit = audit_human_language_delivery(tmp_path, center)
    assert audit['status'] == 'PASS', audit


def test_asset_foreign_visible_copy_without_chinese_companion_blocks(tmp_path: Path):
    center = normalize_upload_center({
        'delivery_language': {'locale': 'zh-CN'},
        'target': {'delivery_locale': 'zh-CN', 'locale': 'ms-MY'},
        'task_scope': {'listing_active': False},
        'copy_center': [], 'preserved_listing_fields': [], 'localized_copy': [],
    })
    _write_asset(tmp_path, {'headline': 'Kawal minyak. Kekalkan hidrasi.'})
    audit = audit_human_language_delivery(tmp_path, center)
    assert audit['status'] == 'INCOMPLETE'
    assert any(x['code'] == 'FOREIGN_ASSET_COPY_WITHOUT_CN_COMPANION' for x in audit['issues'])


def test_english_execution_prompt_requires_chinese_canonical_prompt(tmp_path: Path):
    center = normalize_upload_center({
        'delivery_language': {'locale': 'zh-CN'},
        'task_scope': {'listing_active': False},
        'copy_center': [], 'preserved_listing_fields': [], 'localized_copy': [],
    })
    _write_asset(tmp_path, {'headline': 'Daily Essence', 'delivery_translation': {'headline': '日常精华'}}, with_cn_prompt=False)
    audit = audit_human_language_delivery(tmp_path, center)
    assert audit['status'] == 'INCOMPLETE'
    assert any(x['code'] == 'EN_PROMPT_WITHOUT_CN_CANONICAL_PROMPT' for x in audit['issues'])
