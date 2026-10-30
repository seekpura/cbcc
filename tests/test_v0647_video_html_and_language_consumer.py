from __future__ import annotations

import json
from pathlib import Path

from runtime.cbcc.video_delivery_workspace import apply_video_workspace_to_existing_html
from runtime.cbcc.full_delivery_package_hardening import harden_full_package_audit


def _write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def _minimal_html(path: Path):
    path.write_text(
        '<!doctype html><html><head><style>:root{--line:#ddd;--accent:#234;--soft:#eee;--muted:#777}</style></head>'
        '<body><div class="app"><div class="sidebar"><div class="sidebar-foot"></div></div>'
        '<div class="main"></div></div><script></script></body></html>',
        encoding='utf-8',
    )


def test_materialized_video_is_mounted_into_existing_commercial_workspace(tmp_path):
    package = tmp_path / 'delivery'
    _minimal_html(package / 'index.html')
    _write_json(package / 'video/VIDEO_UNIVERSE.json', {
        'status': 'COMPILED',
        'assets': [{
            'video_id': 'VID-01',
            'surface': 'SHORT_VIDEO',
            'narrative_carrier': 'CREATOR_CONTEXT_DEMO',
            'hook': 'Control oil without skipping hydration',
            'hook_zh': '控油同时保持日常补水。',
            'shots': [],
        }],
    })

    result = apply_video_workspace_to_existing_html(package)
    assert result == package / 'index.html'
    html = result.read_text(encoding='utf-8')
    assert 'data-route="video"' in html
    assert '视频 / Creator 工作台' in html
    assert 'Control oil without skipping hydration' in html
    assert '控油同时保持日常补水。' in html


def test_final_package_audit_rejects_video_foreign_copy_without_chinese_companion(tmp_path):
    package = tmp_path / 'delivery'
    _minimal_html(package / 'index.html')
    _write_json(package / 'strategy/strategy_authority.json', {'delivery_mode': 'FULL'})
    for rel, payload in (
        ('DELIVERY_MANIFEST.json', {'status': 'DELIVERY_READY'}),
        ('FULL_MATERIALIZATION_AUDIT.json', {'status': 'AUDIT_IN_PROGRESS'}),
        ('FULL_DELIVERY_DEPTH_AUDIT.json', {'status': 'PASS'}),
        ('HUMAN_LANGUAGE_AUDIT.json', {'status': 'PASS'}),
        ('DELIVERY_LANGUAGE_MATRIX_AUDIT.json', {'status': 'PASS'}),
        ('PLATFORM_SCOPE.json', {'platform_status': 'EXPLICIT', 'market_status': 'EXPLICIT'}),
        ('FULL_DELIVERY_OBJECT_MANIFEST.json', {'objects': []}),
    ):
        _write_json(package / rel, payload)
    _write_json(package / 'video/VIDEO_UNIVERSE.json', {
        'status': 'COMPILED',
        'assets': [{
            'video_id': 'VID-01',
            'hook': 'Control oil without skipping hydration',
            'shots': [{'shot': 'OPEN', 'visible_copy': 'Daily oil-balancing gel moisturiser'}],
        }],
    })
    apply_video_workspace_to_existing_html(package)

    result = harden_full_package_audit(
        lambda _: {'status': 'PASS', 'issues': []},
        lambda _: {'status': 'PASS', 'issues': []},
    )(package)
    codes = [x['code'] for x in result['issues']]
    assert 'VIDEO_HUMAN_COPY_CHINESE_COMPANION_MISSING' in codes
    assert result['status'] == 'INCOMPLETE'


def test_video_companion_and_html_consumer_can_pass_the_video_specific_checks(tmp_path):
    package = tmp_path / 'delivery'
    _minimal_html(package / 'index.html')
    _write_json(package / 'strategy/strategy_authority.json', {'delivery_mode': 'FULL'})
    for rel, payload in (
        ('DELIVERY_MANIFEST.json', {'status': 'DELIVERY_READY'}),
        ('FULL_MATERIALIZATION_AUDIT.json', {'status': 'AUDIT_IN_PROGRESS'}),
        ('FULL_DELIVERY_DEPTH_AUDIT.json', {'status': 'PASS'}),
        ('HUMAN_LANGUAGE_AUDIT.json', {'status': 'PASS'}),
        ('DELIVERY_LANGUAGE_MATRIX_AUDIT.json', {'status': 'PASS'}),
        ('PLATFORM_SCOPE.json', {'platform_status': 'EXPLICIT', 'market_status': 'EXPLICIT'}),
        ('FULL_DELIVERY_OBJECT_MANIFEST.json', {'objects': []}),
    ):
        _write_json(package / rel, payload)
    _write_json(package / 'video/VIDEO_UNIVERSE.json', {
        'status': 'COMPILED',
        'assets': [{
            'video_id': 'VID-01',
            'hook': 'Control oil without skipping hydration',
            'hook_zh': '控油同时保持日常补水。',
            'shots': [{
                'shot': 'OPEN',
                'visible_copy': 'Daily oil-balancing gel moisturiser',
                'visible_copy_zh': '日常平衡油脂的凝胶保湿产品。',
            }],
        }],
    })
    apply_video_workspace_to_existing_html(package)

    result = harden_full_package_audit(
        lambda _: {'status': 'PASS', 'issues': []},
        lambda _: {'status': 'PASS', 'issues': []},
    )(package)
    codes = {x['code'] for x in result['issues']}
    assert 'VIDEO_HUMAN_COPY_CHINESE_COMPANION_MISSING' not in codes
    assert 'VIDEO_OBJECTS_HAVE_NO_PRIMARY_HTML_CONSUMER' not in codes
