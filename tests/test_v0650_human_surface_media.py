from __future__ import annotations

import json
from pathlib import Path

from scripts.check_v0650_human_surface_media import audit_package


def _write(root: Path, html: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / 'index.html').write_text(html, encoding='utf-8')


def test_v0649_regression_shape_fails(tmp_path: Path):
    data = {
        'product': {
            'barcode_status': 'MISSING_INPUT — Excel barcode blank; do not use barcode visible in source image without confirmation',
        },
        'market': {'evidence': [{'fact': 'TikTok Shop MY allows up to 9 square listing images and primary image should show the full front view.'}]},
        'assets': [{
            'id': 'LST-01',
            'prompt_en': 'Create a production-ready HERO asset. Shopper decision: 这到底是什么、收到什么？ Strategic job: establish identity.',
        }],
    }
    html = (
        '<html><body><h2>Message Hierarchy</h2>'
        '<img src="sources/product.png">'
        '<script id="data" type="application/json">'
        + json.dumps(data, ensure_ascii=False)
        + '</script></body></html>'
    )
    _write(tmp_path, html)
    report = audit_package(tmp_path)
    assert report['status'] == 'FAIL'
    codes = {x['code'] for x in report['issues']}
    assert 'HUMAN_OPERATOR_FIELD_NOT_CHINESE_FIRST' in codes
    assert 'LOCAL_MEDIA_NOT_STANDALONE_SAFE' in codes
    assert 'ENGLISH_ONLY_OPERATOR_HEADING' in codes
    assert 'MODEL_PROMPT_EN_CONTAINS_CHINESE_EXECUTION_PROSE' in codes


def test_chinese_surface_and_embedded_media_pass(tmp_path: Path):
    data = {
        'product': {
            'barcode_status': '待补充：Excel 条码为空，未确认前不使用包装图中的条码。',
        },
        'market': {'evidence': [{'fact': 'TikTok Shop 马来西亚站商品图最多可配置 9 张；该规则只限制激活位，不限制资产池。'}]},
        'assets': [{
            'id': 'LST-01',
            'prompt_en': 'Create a production-ready hero asset for TikTok Shop Malaysia. Preserve the verified product identity and keep the pack fully visible.',
        }],
    }
    html = (
        '<html><body><h2>信息层级（Message Hierarchy）</h2>'
        '<img src="data:image/png;base64,iVBORw0KGgo=">'
        '<script id="data" type="application/json">'
        + json.dumps(data, ensure_ascii=False)
        + '</script></body></html>'
    )
    _write(tmp_path, html)
    report = audit_package(tmp_path)
    assert report['status'] == 'PASS', report['issues']
