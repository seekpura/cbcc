from pathlib import Path

from cbcc.human_language_delivery import normalize_upload_center
from cbcc.global_chinese_interpretation import normalize_global_chinese_interpretation
from cbcc.final_chinese_interpretation_audit import audit_final_chinese_interpretation


def test_nested_model_number_does_not_force_literal_translation(tmp_path: Path):
    center = {
        'delivery_language': {'locale': 'zh-CN'},
        'task_scope': {'listing_active': True},
        'copy_center': [{
            'field': 'attributes',
            'label': '商品属性',
            'label_zh_semantic': True,
            'value': {'texture': '轻盈凝胶', 'model_number': 'K01-30G'},
        }],
        'preserved_listing_fields': [],
    }
    center = normalize_global_chinese_interpretation(normalize_upload_center(center))
    audit = audit_final_chinese_interpretation(tmp_path, center)
    assert audit['status'] == 'PASS'
