from __future__ import annotations

from typing import Any
import re


_CHINA_PLATFORMS = {
    'tmall', 'taobao', 'jd', 'jd.com', 'jingdong', 'pinduoduo', 'douyin',
    'xiaohongshu', 'red', '1688', 'weidian', 'kuaishou', 'suning',
}
_CHINA_MARKETS = {'CN', 'CHINA', '中国', '中国大陆', 'MAINLAND CHINA'}
_LOCALIZED_LISTING_FIELDS = {
    'title', 'product_title', 'product_name', 'category', 'platform_category', 'category_name', 'category_path',
    'highlights', 'bullets', 'bullet_points', 'description', 'short_description', 'long_description',
    'attributes', 'attribute', 'variant', 'variation', 'variation_name', 'variation_value',
    'search_terms', 'backend_terms', 'keywords', 'usage', 'directions', 'warnings', 'cautions', 'faq',
    'package', 'package_contents', 'material', 'color', 'size', 'offer', 'shipping', 'returns', 'seller_info',
}
_TECHNICAL_FIELDS = {
    'brand', 'sku', 'gtin', 'ean', 'upc', 'barcode', 'category_id', 'product_id', 'item_id',
    'model', 'model_number', 'part_number', 'hs_code', 'url', 'uri', 'hex', 'inci',
}


def _norm(value: Any) -> str:
    return str(value or '').strip()


def _is_china_platform(scope: dict[str, Any]) -> bool:
    platform = _norm(scope.get('platform')).casefold()
    market = _norm(scope.get('market')).upper()
    locale = _norm(scope.get('primary_locale')).lower()
    return platform in _CHINA_PLATFORMS or market in _CHINA_MARKETS or locale.startswith('zh-cn')


def build_language_delivery_plan(scope: dict[str, Any]) -> dict[str, Any]:
    """Build the stable human-delivery language matrix.

    China domestic commerce: Chinese only.
    Other explicit markets: English baseline + platform primary language + Chinese interpretation.
    English-primary markets deduplicate the English/platform-primary layer.
    Unknown platform/market: English + Chinese are safe baseline layers; platform-primary remains pending.
    """
    primary = _norm(scope.get('primary_locale')) or None
    if _is_china_platform(scope):
        return {
            'mode': 'CN_ONLY',
            'required_locales': ['zh-CN'],
            'english_baseline_required': False,
            'platform_primary_locale': 'zh-CN',
            'platform_primary_status': 'RESOLVED',
            'chinese_interpretation_required': True,
            'rule': '中国平台/中国大陆市场的人类交付只要求中文。',
        }

    if not scope.get('platform') and not scope.get('market') and not primary:
        return {
            'mode': 'EN_CN_PENDING_PLATFORM_PRIMARY',
            'required_locales': ['en', 'zh-CN'],
            'english_baseline_required': True,
            'platform_primary_locale': None,
            'platform_primary_status': 'MISSING_INPUT',
            'chinese_interpretation_required': True,
            'rule': '平台/市场未指定时不得猜主语言；先保留英文基线 + 中文释义，平台主语言待明确后补齐。',
        }

    if primary and primary.lower().startswith('en'):
        return {
            'mode': 'EN_CN',
            'required_locales': [primary, 'zh-CN'],
            'english_baseline_required': True,
            'platform_primary_locale': primary,
            'platform_primary_status': 'RESOLVED',
            'chinese_interpretation_required': True,
            'rule': '平台主语言本身为英语时去重：英文原文 + 中文释义。',
        }

    if primary:
        return {
            'mode': 'EN_PLATFORM_PRIMARY_CN',
            'required_locales': ['en', primary, 'zh-CN'],
            'english_baseline_required': True,
            'platform_primary_locale': primary,
            'platform_primary_status': 'RESOLVED',
            'chinese_interpretation_required': True,
            'rule': '非中国、非英语主语言平台：英文基线 + 平台主语言 + 中文释义。',
        }

    return {
        'mode': 'EN_CN_PENDING_PLATFORM_PRIMARY',
        'required_locales': ['en', 'zh-CN'],
        'english_baseline_required': True,
        'platform_primary_locale': None,
        'platform_primary_status': 'MISSING_INPUT',
        'chinese_interpretation_required': True,
        'rule': '平台/市场已部分明确但主语言未明确：英文基线 + 中文释义先保留，平台主语言待补。',
    }


def _locale_matches(actual: str, required: str) -> bool:
    a = _norm(actual).lower().replace('_', '-')
    r = _norm(required).lower().replace('_', '-')
    if not a or not r:
        return False
    if r == 'en':
        return a == 'en' or a.startswith('en-')
    if r == 'zh-cn':
        return a in {'zh', 'zh-cn', 'zh-hans', 'cn'}
    if a == r:
        return True
    a_base = a.split('-', 1)[0]
    r_base = r.split('-', 1)[0]
    return a_base == r_base and ('-' not in a or '-' not in r)


def _has_cjk(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_has_cjk(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_has_cjk(v) for v in value)
    return bool(re.search(r'[\u3400-\u4dbf\u4e00-\u9fff]', str(value or '')))


def _is_localizable_row(row: dict[str, Any]) -> bool:
    field = _norm(row.get('field')).casefold()
    if not field or field in _TECHNICAL_FIELDS:
        return False
    if row.get('localizable') is False or row.get('translate') is False:
        return False
    if row.get('localizable') is True or row.get('translate') is True:
        return True
    return field in _LOCALIZED_LISTING_FIELDS


def audit_language_delivery(center: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """Audit Listing/localized human copy without inventing translations.

    Runtime verifies authored language layers only for human-localizable commerce fields. Technical IDs,
    brand identifiers and machine keys remain exact. Runtime never creates English/platform-primary copy
    merely to satisfy the contract.
    """
    rows = [x for x in (center.get('localized_copy') or []) if isinstance(x, dict)]
    copy_rows = [x for x in (center.get('copy_center') or []) if isinstance(x, dict)]
    listing_active = bool((center.get('task_scope') or {}).get('listing_active'))
    if not listing_active and not rows and not copy_rows:
        return {'status': 'NOT_IN_CURRENT_SCOPE', 'missing': [], 'plan': plan}

    fields = []
    for row in rows + copy_rows:
        field = _norm(row.get('field'))
        value = row.get('value')
        if _is_localizable_row(row) and field and value not in (None, '', [], {}) and field not in fields:
            fields.append(field)

    if not fields:
        return {'status': 'PASS', 'missing': [], 'plan': plan, 'audited_fields': []}

    required_locales = [x for x in (plan.get('required_locales') or []) if str(x).lower() != 'zh-cn']
    missing = []
    for field in fields:
        for locale in required_locales:
            matches = [
                r for r in rows
                if _norm(r.get('field')) == field
                and _is_localizable_row(r)
                and _locale_matches(_norm(r.get('locale')), locale)
                and r.get('value') not in (None, '', [], {})
            ]
            if not matches:
                missing.append({'field': field, 'locale': locale, 'reason': 'AUTHORED_COPY_REQUIRED'})

    if plan.get('chinese_interpretation_required'):
        for field in fields:
            candidates = [
                r for r in rows + copy_rows
                if _norm(r.get('field')) == field and _is_localizable_row(r) and r.get('value') not in (None, '', [], {})
            ]
            if candidates and not any(
                _has_cjk(r.get('value'))
                or r.get('delivery_translation') not in (None, '', '待补中文释义')
                or r.get('delivery_translation_zh') not in (None, '', '待补中文释义')
                or _locale_matches(_norm(r.get('locale')), 'zh-CN')
                for r in candidates
            ):
                missing.append({'field': field, 'locale': 'zh-CN', 'reason': 'CHINESE_INTERPRETATION_REQUIRED'})

    return {
        'status': 'PASS' if not missing else 'INCOMPLETE',
        'missing': missing,
        'plan': plan,
        'audited_fields': fields,
        'technical_fields_exempt': sorted(_TECHNICAL_FIELDS),
    }
