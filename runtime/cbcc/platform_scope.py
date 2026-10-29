from __future__ import annotations

from pathlib import Path
from typing import Any
import json


_EXPLICIT_SOURCES = {
    'USER', 'USER_INPUT', 'REQUEST', 'CURRENT_REQUEST', 'SOURCE', 'SOURCE_FILE',
    'PROJECT_INPUT', 'EXPLICIT', 'CONFIRMED', 'VERIFIED',
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _first(*values):
    for value in values:
        if value not in (None, '', [], {}):
            return value
    return None


def _nested_request_target(request: dict[str, Any]) -> dict[str, Any]:
    for key in ('target', 'commerce_target', 'market_target'):
        value = request.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _explicit_context_values(request: dict[str, Any]) -> dict[str, Any]:
    nested = _nested_request_target(request)
    language = nested.get('language') if isinstance(nested.get('language'), dict) else {}
    return {
        'platform': _first(
            request.get('platform'), request.get('target_platform'), request.get('platform_family'),
            nested.get('platform'), nested.get('target_platform'), nested.get('platform_family'),
        ),
        'market': _first(
            request.get('market'), request.get('target_market'), request.get('country'), request.get('country_code'),
            nested.get('market'), nested.get('target_market'), nested.get('country'), nested.get('country_code'),
        ),
        'site': _first(request.get('site'), request.get('site_id'), nested.get('site'), nested.get('site_id')),
        'primary_locale': _first(
            request.get('primary_locale'), request.get('locale'),
            nested.get('primary_locale'), nested.get('locale'), language.get('primary_locale'),
        ),
    }


def _target_is_explicit(target_context: dict[str, Any]) -> bool:
    target = target_context.get('target') if isinstance(target_context.get('target'), dict) else target_context
    flags = [
        target_context.get('explicit'), target_context.get('user_selected'), target_context.get('confirmed'),
        target.get('explicit') if isinstance(target, dict) else None,
        target.get('user_selected') if isinstance(target, dict) else None,
        target.get('confirmed') if isinstance(target, dict) else None,
    ]
    if any(value is True for value in flags):
        return True
    source = str(_first(
        target_context.get('source'), target_context.get('provenance'), target_context.get('scope_source'),
        target.get('source') if isinstance(target, dict) else None,
        target.get('provenance') if isinstance(target, dict) else None,
    ) or '').strip().upper()
    return source in _EXPLICIT_SOURCES


def _explicit_target_context_values(target_context: dict[str, Any]) -> dict[str, Any]:
    if not _target_is_explicit(target_context):
        return {}
    target = target_context.get('target') if isinstance(target_context.get('target'), dict) else target_context
    language = target.get('language') if isinstance(target.get('language'), dict) else {}
    return {
        'platform': _first(target.get('platform'), target.get('platform_family')),
        'market': _first(target.get('market'), target.get('country'), target.get('country_code')),
        'site': _first(target.get('site'), target.get('site_id')),
        'primary_locale': _first(target.get('primary_locale'), target.get('locale'), language.get('primary_locale')),
    }


def resolve_platform_scope(project_dir: Path | str) -> dict[str, Any]:
    """Resolve only the current project's explicitly supplied platform/market scope.

    Historical examples, platform compiler defaults and inferred target_context values must never become
    silent current-project truth. Inference/recommendation can exist elsewhere, but the human delivery
    remains UNSPECIFIED until the user/current source explicitly establishes the scope.
    """
    project = Path(project_dir)
    request = _read_json(project / 'meta/request.json')
    target_context = _read_json(project / 'artifacts/target_context.json')

    request_values = _explicit_context_values(request)
    target_values = _explicit_target_context_values(target_context)

    platform = _first(request_values.get('platform'), target_values.get('platform'))
    market = _first(request_values.get('market'), target_values.get('market'))
    site = _first(request_values.get('site'), target_values.get('site'))
    primary_locale = _first(request_values.get('primary_locale'), target_values.get('primary_locale'))

    platform_source = 'CURRENT_REQUEST' if request_values.get('platform') else ('EXPLICIT_TARGET_CONTEXT' if target_values.get('platform') else None)
    market_source = 'CURRENT_REQUEST' if request_values.get('market') else ('EXPLICIT_TARGET_CONTEXT' if target_values.get('market') else None)
    locale_source = 'CURRENT_REQUEST' if request_values.get('primary_locale') else ('EXPLICIT_TARGET_CONTEXT' if target_values.get('primary_locale') else None)

    return {
        'platform': platform,
        'market': market,
        'site': site,
        'primary_locale': primary_locale,
        'platform_status': 'EXPLICIT' if platform else 'UNSPECIFIED',
        'market_status': 'EXPLICIT' if market else 'UNSPECIFIED',
        'primary_locale_status': 'EXPLICIT' if primary_locale else 'UNSPECIFIED',
        'platform_source': platform_source,
        'market_source': market_source,
        'primary_locale_source': locale_source,
        'rule': '当前请求/明确项目输入优先；未明确的平台、市场或主语言保持 UNSPECIFIED。禁止从历史项目、示例、platform_compile 或自动默认值继承 TikTok/Malaysia 等上下文。',
    }
