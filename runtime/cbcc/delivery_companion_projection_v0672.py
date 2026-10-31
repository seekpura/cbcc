from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping


def _meaningful(value: Any) -> bool:
    return value not in (None, '', [], {})


def _norm_locale(value: Any) -> str:
    return str(value or '').strip().lower().replace('_', '-')


def _locale_matches(actual: Any, required: Any) -> bool:
    a = _norm_locale(actual)
    r = _norm_locale(required)
    if not a or not r:
        return False
    if a == r:
        return True
    zh_aliases = {'zh', 'zh-cn', 'zh-hans', 'cn'}
    if r in zh_aliases and a in zh_aliases:
        return True
    if r.startswith('en') and a.startswith('en'):
        return True
    return a.split('-', 1)[0] == r.split('-', 1)[0]


def _delivery_payload(localized_copy: Mapping[str, Any], delivery_locale: str) -> dict[str, Any]:
    for locale, payload in localized_copy.items():
        if _locale_matches(locale, delivery_locale) and isinstance(payload, Mapping):
            return dict(payload)
    return {}


def apply_authored_delivery_locale_companions(result: Mapping[str, Any], language_contract: Mapping[str, Any] | None, localized_copy: Mapping[str, Any] | None) -> dict[str, Any]:
    out = deepcopy(dict(result))
    contract = language_contract or {}
    delivery_locale = str(contract.get('delivery_locale') or 'zh-CN')
    delivery = _delivery_payload(localized_copy or {}, delivery_locale)
    if not delivery:
        return out
    for package in out.get('packages') or []:
        if not isinstance(package, dict) or _locale_matches(package.get('locale'), delivery_locale):
            continue
        for row in package.get('fields') or []:
            if not isinstance(row, dict):
                continue
            field = str(row.get('field') or '')
            companion = delivery.get(field)
            if not field or not _meaningful(companion) or _meaningful(row.get('delivery_translation')):
                continue
            row['delivery_translation'] = deepcopy(companion)
            row['delivery_note'] = row.get('delivery_note') or f'直接复用已作者化 {delivery_locale} 同字段作为人类交付 companion；未执行机器翻译。'
            row['delivery_companion_status'] = 'READY_AUTHORED_DELIVERY_LOCALE_COPY'
    out['delivery_companion_projection_v0672'] = {
        'status': 'APPLIED',
        'delivery_locale': delivery_locale,
        'principle': 'Only authored delivery-locale copy is reused; missing companions remain unresolved.',
    }
    return out


def wrap_final_copy_release_workflow(fn: Callable[..., dict[str, Any]]):
    if getattr(fn, '_cbcc_v0672_delivery_companion_projection', False):
        return fn

    def compiled(fields, language_contract, localized_copy, *args, **kwargs):
        result = fn(fields, language_contract, localized_copy, *args, **kwargs)
        return apply_authored_delivery_locale_companions(result, language_contract, localized_copy)

    setattr(compiled, '_cbcc_v0672_delivery_companion_projection', True)
    return compiled
