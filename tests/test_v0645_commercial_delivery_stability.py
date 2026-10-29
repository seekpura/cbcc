from pathlib import Path
import json

from runtime.cbcc.platform_scope import resolve_platform_scope
from runtime.cbcc.delivery_language_matrix import build_language_delivery_plan, audit_language_delivery
from runtime.cbcc.source_truth_media import materialize_source_truth_media
from runtime.cbcc.commercial_workspace_shell import WORKSPACE_SHELL_VERSION, apply_commercial_workspace_shell


def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def test_unspecified_platform_and_market_do_not_inherit_tiktok_malaysia(tmp_path: Path):
    _write_json(tmp_path / 'meta/request.json', {'goal': '完成商品项目'})
    _write_json(tmp_path / 'artifacts/target_context.json', {
        'target': {'platform': 'TikTok Shop', 'market': 'MY', 'locale': 'ms-MY'},
        'source': 'AUTO_DEFAULT',
    })
    _write_json(tmp_path / 'artifacts/platform_compile.json', {
        'platform': 'TikTok Shop', 'market': 'MY', 'primary_locale': 'ms-MY'
    })
    scope = resolve_platform_scope(tmp_path)
    assert scope['platform'] is None
    assert scope['market'] is None
    assert scope['platform_status'] == 'UNSPECIFIED'
    assert scope['market_status'] == 'UNSPECIFIED'
    assert 'TikTok' not in json.dumps(scope, ensure_ascii=False)
    assert 'MY' not in json.dumps(scope, ensure_ascii=False)


def test_explicit_current_request_platform_and_market_win(tmp_path: Path):
    _write_json(tmp_path / 'meta/request.json', {
        'platform': 'Shopee', 'market': 'TH', 'primary_locale': 'th-TH'
    })
    _write_json(tmp_path / 'artifacts/target_context.json', {
        'target': {'platform': 'TikTok Shop', 'market': 'MY', 'locale': 'ms-MY'}
    })
    scope = resolve_platform_scope(tmp_path)
    assert scope['platform'] == 'Shopee'
    assert scope['market'] == 'TH'
    assert scope['primary_locale'] == 'th-TH'
    assert scope['platform_status'] == 'EXPLICIT'


def test_language_plan_non_china_non_english_is_english_primary_chinese():
    plan = build_language_delivery_plan({'platform': 'Shopee', 'market': 'MY', 'primary_locale': 'ms-MY'})
    assert plan['mode'] == 'EN_PLATFORM_PRIMARY_CN'
    assert plan['required_locales'] == ['en', 'ms-MY', 'zh-CN']


def test_language_plan_english_primary_dedupes_english():
    plan = build_language_delivery_plan({'platform': 'Amazon', 'market': 'US', 'primary_locale': 'en-US'})
    assert plan['mode'] == 'EN_CN'
    assert plan['required_locales'] == ['en-US', 'zh-CN']


def test_language_plan_china_platform_is_chinese_only():
    plan = build_language_delivery_plan({'platform': 'Tmall', 'market': 'CN', 'primary_locale': 'zh-CN'})
    assert plan['mode'] == 'CN_ONLY'
    assert plan['required_locales'] == ['zh-CN']


def test_language_plan_unknown_platform_never_defaults_malay():
    plan = build_language_delivery_plan({'platform': None, 'market': None, 'primary_locale': None})
    assert plan['mode'] == 'EN_CN_PENDING_PLATFORM_PRIMARY'
    assert plan['required_locales'] == ['en', 'zh-CN']
    assert plan['platform_primary_status'] == 'MISSING_INPUT'
    assert 'ms-MY' not in plan['required_locales']


def test_language_audit_requires_english_and_platform_primary_for_non_china():
    plan = build_language_delivery_plan({'platform': 'Shopee', 'market': 'MY', 'primary_locale': 'ms-MY'})
    center = {'localized_copy': [
        {'locale': 'ms-MY', 'field': 'title', 'value': 'Gel Harian', 'delivery_translation': '日常凝胶'},
    ]}
    audit = audit_language_delivery(center, plan)
    assert audit['status'] == 'INCOMPLETE'
    assert any(x['locale'].startswith('en') and x['field'] == 'title' for x in audit['missing'])


def test_source_truth_media_is_copied_for_self_contained_html(tmp_path: Path):
    project = tmp_path / 'project'
    package = tmp_path / 'package'
    image = project / 'uploads' / 'product.png'
    image.parent.mkdir(parents=True)
    image.write_bytes(b'\x89PNG\r\n\x1a\n' + b'fake-image')
    _write_json(project / 'artifacts/source_product_assets.json', {
        'assets': [{'asset_id': 'SRC01', 'path': 'uploads/product.png', 'role': 'product_truth'}]
    })
    result = materialize_source_truth_media(project, package)
    assert result['copied_count'] == 1
    copied = package / result['items'][0]['package_path']
    assert copied.exists()
    assert copied.read_bytes() == image.read_bytes()


def test_missing_source_truth_media_is_explicit_not_silent(tmp_path: Path):
    project = tmp_path / 'project'
    package = tmp_path / 'package'
    _write_json(project / 'artifacts/source_product_assets.json', {
        'assets': [{'asset_id': 'SRC01', 'path': 'uploads/missing.png'}]
    })
    result = materialize_source_truth_media(project, package)
    assert result['status'] == 'INCOMPLETE'
    assert result['missing_count'] == 1
    assert result['items'][0]['status'] == 'MISSING_FILE'


def test_commercial_workspace_shell_is_stable_and_route_based():
    raw = '<html><head><style></style></head><body><div class="app"><div class="sidebar"><div class="brand">CBCC</div></div><div class="workspace"><section class="page active" data-route="overview"></section><section class="page" data-route="listing"></section></div></div><script></script></body></html>'
    out = apply_commercial_workspace_shell(raw, {'platform': None, 'market': None}, {'mode': 'EN_CN_PENDING_PLATFORM_PRIMARY'})
    assert WORKSPACE_SHELL_VERSION == 'cbcc-commercial-v1'
    assert 'data-workspace-shell="cbcc-commercial-v1"' in out
    assert '平台待指定' in out
    assert '市场待指定' in out
    assert '一次只显示一个一级工作面' in out
    assert 'Malaysia' not in out
    assert 'TikTok Shop' not in out
