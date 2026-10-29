from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .human_language_delivery import _has_cjk, _needs_cn_companion, _flatten_text
from .global_chinese_interpretation import audit_global_chinese_interpretation


_IDENTIFIER_FIELDS = {
    'brand', 'sku', 'seller_sku', 'parent_sku', 'variation_sku', 'category_id', 'gtin', 'ean', 'upc',
    'barcode', 'hs_code', 'model_number', 'part_number', 'tax_code', 'url', 'uri', 'asin', 'id',
}


def _has_cn_companion(row: dict[str, Any]) -> bool:
    for key in (
        'delivery_translation', 'delivery_translation_zh', 'chinese_interpretation',
        'zh', 'zh_cn', 'zh-CN', 'cn', '中文释义', '中文说明',
    ):
        value = row.get(key)
        if value not in (None, '', [], {}) and _has_cjk(value):
            return True
    return False


def _value_needs_cn(value: Any, field: str | None = None) -> bool:
    """Check foreign human content recursively instead of accepting a mixed object because one leaf is Chinese."""
    if value in (None, '', [], {}):
        return False
    if field and str(field).casefold() in _IDENTIFIER_FIELDS:
        return False
    if isinstance(value, dict):
        return any(_value_needs_cn(v, str(k)) for k, v in value.items())
    if isinstance(value, (list, tuple, set)):
        return any(_value_needs_cn(v, field) for v in value)
    return _needs_cn_companion(value, field)


def _listing_rows_issues(center: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    collections = (
        ('copy_center', 'LISTING'),
        ('localized_copy', 'LISTING'),
        ('preserved_listing_fields', 'PRESERVED_LISTING'),
    )
    for collection, scope in collections:
        for idx, row in enumerate(center.get(collection) or []):
            if not isinstance(row, dict):
                continue
            field = str(row.get('field') or '')
            value = row.get('value')
            if not _value_needs_cn(value, field) or _has_cn_companion(row):
                continue
            issues.append({
                'scope': scope,
                'field': field,
                'locale': row.get('locale'),
                'path': f'{collection}.{idx}.{field}',
                'code': 'FOREIGN_LISTING_COPY_WITHOUT_CN_COMPANION' if scope == 'LISTING' else 'FOREIGN_PRESERVED_LISTING_WITHOUT_CN_COMPANION',
                'value': _flatten_text(value)[:320],
            })
    return issues


def _issue_key(issue: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(issue.get('scope') or ''),
        str(issue.get('field') or ''),
        str(issue.get('locale') or ''),
        str(issue.get('code') or ''),
    )


def audit_final_chinese_interpretation(
    package_dir: Path,
    center: dict[str, Any],
    base_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Final delivery audit: global scopes + recursive Listing/localized leaf completeness."""
    base = deepcopy(audit_global_chinese_interpretation(package_dir, center, base_audit=base_audit))
    issues = list(base.get('issues') or [])
    existing = {_issue_key(x) for x in issues}
    for issue in _listing_rows_issues(center):
        key = _issue_key(issue)
        if key not in existing:
            issues.append(issue)
            existing.add(key)

    base['issues'] = issues
    base['status'] = 'PASS' if not issues else 'INCOMPLETE'

    listing_issues = [x for x in issues if x.get('scope') in {'LISTING', 'PRESERVED_LISTING'}]
    base['listing'] = dict(base.get('listing') or {})
    base['listing']['status'] = 'PASS' if not listing_issues else 'INCOMPLETE'
    base['listing']['issue_count'] = len(listing_issues)
    base['listing']['recursive_leaf_check'] = True

    base['global_human_content'] = dict(base.get('global_human_content') or {})
    base['global_human_content']['final_status'] = 'PASS' if not issues else 'INCOMPLETE'
    base['global_human_content']['recursive_listing_leaf_check'] = True
    return base
