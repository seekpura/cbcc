from __future__ import annotations

import json
from pathlib import Path

from runtime.cbcc.full_delivery_package_hardening import harden_full_package_audit


def _write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')


def test_package_hardening_rejects_shallow_strategy_even_when_files_exist(tmp_path):
    package = tmp_path / 'delivery'
    package.mkdir()
    _write(package / 'strategy/strategy_authority.json', {'delivery_mode': 'FULL', 'sections': {}})
    _write(package / 'FULL_DELIVERY_DEPTH_AUDIT.json', {'status': 'PASS'})
    _write(package / 'HUMAN_LANGUAGE_AUDIT.json', {'status': 'PASS'})
    _write(package / 'DELIVERY_LANGUAGE_MATRIX_AUDIT.json', {'status': 'PASS'})
    _write(package / 'PLATFORM_SCOPE.json', {'platform_status': 'EXPLICIT', 'market_status': 'EXPLICIT'})
    _write(package / 'FULL_DELIVERY_OBJECT_MANIFEST.json', {'objects': []})
    _write(package / 'DELIVERY_MANIFEST.json', {'status': 'DELIVERY_READY'})
    _write(package / 'FULL_MATERIALIZATION_AUDIT.json', {'status': 'AUDIT_IN_PROGRESS'})

    def base(_):
        return {'status': 'PASS', 'issues': []}

    def strategy_validator(_):
        return {'status': 'INCOMPLETE', 'issues': [{'code': 'FULL_MARKET_CULTURE_DIMENSION_MISSING'}]}

    result = harden_full_package_audit(base, strategy_validator)(package)
    assert result['status'] == 'INCOMPLETE'
    assert any(x['code'] == 'PACKAGED_STRATEGY_DEPTH_V3_FAILED' for x in result['issues'])


def test_package_hardening_rejects_failed_language_and_missing_active_object(tmp_path):
    package = tmp_path / 'delivery'
    package.mkdir()
    _write(package / 'strategy/strategy_authority.json', {'delivery_mode': 'FULL'})
    _write(package / 'FULL_DELIVERY_DEPTH_AUDIT.json', {'status': 'PASS'})
    _write(package / 'HUMAN_LANGUAGE_AUDIT.json', {'status': 'INCOMPLETE'})
    _write(package / 'DELIVERY_LANGUAGE_MATRIX_AUDIT.json', {'status': 'INCOMPLETE'})
    _write(package / 'PLATFORM_SCOPE.json', {'platform_status': 'EXPLICIT', 'market_status': 'EXPLICIT'})
    _write(package / 'FULL_DELIVERY_OBJECT_MANIFEST.json', {
        'objects': [{'object': 'MARKET', 'status': 'ACTIVE', 'path': 'supporting_analysis/market_analysis.json'}]
    })
    _write(package / 'DELIVERY_MANIFEST.json', {'status': 'DELIVERY_READY'})
    _write(package / 'FULL_MATERIALIZATION_AUDIT.json', {'status': 'AUDIT_IN_PROGRESS'})

    result = harden_full_package_audit(
        lambda _: {'status': 'PASS', 'issues': []},
        lambda _: {'status': 'PASS', 'issues': []},
    )(package)
    codes = {x['code'] for x in result['issues']}
    assert 'HUMAN_LANGUAGE_AUDIT_NOT_PASS' in codes
    assert 'DELIVERY_LANGUAGE_MATRIX_NOT_PASS' in codes
    assert 'FULL_OBJECT_MANIFEST_ACTIVE_PATH_MISSING' in codes
    assert result['status'] == 'INCOMPLETE'
