from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable
import json

from .human_language_delivery import (
    _has_cjk,
    _needs_cn_companion,
    _flatten_text,
    audit_human_language_delivery,
)


# These are semantic human-copy fields, not every arbitrary JSON string. Runtime must not turn
# machine IDs/status/provider metadata into fake translation work. Agent authors the companion;
# Runtime only verifies that the companion exists in the same human object.
_SCOPE_FILES: dict[str, tuple[str, ...]] = {
    'VIDEO': ('supporting_analysis/video_creator_plan.json',),
    'ADS': ('supporting_analysis/ad_analysis.json',),
    'REVIEW': ('supporting_analysis/feedback_analysis.json',),
    'RESEARCH': (
        'supporting_analysis/market_analysis.json',
        'supporting_analysis/culture_context.json',
        'supporting_analysis/strategy_reasoning_context.json',
    ),
}

_SCOPE_FIELDS: dict[str, set[str]] = {
    'VIDEO': {
        'hook', 'first_frame_copy', 'on_screen_text', 'onscreen_text', 'screen_text', 'visible_copy',
        'subtitle', 'subtitles', 'caption', 'voiceover', 'voice_over', 'vo', 'vo_script', 'script',
        'dialogue', 'cover_text', 'thumbnail_text', 'cta', 'call_to_action', 'creator_script', 'shot_copy',
    },
    'ADS': {
        'hook', 'headline', 'title', 'primary_text', 'body', 'body_copy', 'caption', 'ad_copy',
        'visible_copy', 'cta', 'call_to_action', 'creator_script', 'script', 'offer_copy', 'landing_copy',
    },
    'REVIEW': {
        'review', 'review_text', 'review_excerpt', 'excerpt', 'quote', 'comment', 'feedback',
        'customer_voice', 'consumer_voice', 'return_reason', 'complaint', 'theme_label', 'cluster_label',
    },
    'RESEARCH': {
        'quote', 'excerpt', 'customer_voice', 'consumer_voice', 'consumer_quote', 'shopper_quote',
        'competitor_copy', 'competitor_title', 'competitor_description', 'category_label', 'segment_label',
        'positioning', 'value_proposition', 'message', 'insight', 'insight_label', 'claim_copy',
    },
}

_COMPANION_CONTAINER_KEYS = (
    'delivery_translation', 'delivery_translation_zh', 'chinese_interpretation', 'translations',
    'zh', 'zh_cn', 'zh-CN', 'cn', '中文释义', '中文说明',
)

_COMPANION_SUFFIXES = (
    '_zh', '_cn', '_zh_cn', '_zh-CN', '_delivery_translation', '_delivery_translation_zh',
    '_chinese_interpretation', '_meaning_zh', '_intent_zh',
)

_SKIP_KEYS = {
    'locale', 'language', 'delivery_locale', 'status', 'state', 'id', 'asset_id', 'source_id', 'claim_id',
    'sku', 'gtin', 'ean', 'upc', 'barcode', 'url', 'uri', 'hex', 'model', 'model_number', 'provider',
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _cn_value(value: Any) -> bool:
    if value in (None, '', [], {}):
        return False
    if isinstance(value, dict):
        return any(_cn_value(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_cn_value(v) for v in value)
    return _has_cjk(value)


def _same_object_companion(obj: dict[str, Any], key: str, foreign_field_count: int = 1) -> bool:
    for suffix in _COMPANION_SUFFIXES:
        if _cn_value(obj.get(f'{key}{suffix}')):
            return True

    for container_key in _COMPANION_CONTAINER_KEYS:
        comp = obj.get(container_key)
        if comp in (None, '', [], {}):
            continue
        if isinstance(comp, str):
            # A single object-level explanation can cover one foreign human-copy field. With multiple
            # fields, require keyed companions so operators can see what each Chinese line explains.
            if foreign_field_count == 1 and _has_cjk(comp):
                return True
            continue
        if isinstance(comp, dict):
            if _cn_value(comp.get(key)):
                return True
            # Support common normalized names without forcing one exact schema.
            for alias in (f'{key}_zh', f'{key}_cn', f'{key}_meaning', f'{key}_intent'):
                if _cn_value(comp.get(alias)):
                    return True
    return False


def _foreign_human_fields(obj: dict[str, Any], allowed: set[str]) -> list[str]:
    fields: list[str] = []
    for raw_key, value in obj.items():
        key = str(raw_key)
        low = key.casefold()
        if low in _SKIP_KEYS or low in _COMPANION_CONTAINER_KEYS:
            continue
        if any(low.endswith(s.casefold()) for s in _COMPANION_SUFFIXES):
            continue
        if low in allowed and _needs_cn_companion(value, low):
            fields.append(key)
    return fields


def _audit_structured_copy(value: Any, scope: str, path: tuple[str, ...] = ()) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    allowed = _SCOPE_FIELDS.get(scope, set())
    if isinstance(value, dict):
        foreign_fields = _foreign_human_fields(value, allowed)
        foreign_count = len(foreign_fields)
        for field in foreign_fields:
            if not _same_object_companion(value, field, foreign_count):
                issues.append({
                    'scope': scope,
                    'field': field,
                    'path': '.'.join(path + (field,)),
                    'code': f'FOREIGN_{scope}_CONTENT_WITHOUT_CN_COMPANION',
                    'value': _flatten_text(value.get(field))[:320],
                })
        for key, child in value.items():
            low = str(key).casefold()
            if low in _COMPANION_CONTAINER_KEYS or any(low.endswith(s.casefold()) for s in _COMPANION_SUFFIXES):
                continue
            issues.extend(_audit_structured_copy(child, scope, path + (str(key),)))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            issues.extend(_audit_structured_copy(child, scope, path + (str(idx),)))
    return issues


def normalize_global_chinese_interpretation(center: dict[str, Any]) -> dict[str, Any]:
    """Propagate existing companions into every human Listing projection without inventing translation."""
    out = deepcopy(center or {})
    by_field: dict[str, dict[str, Any]] = {}
    for collection in ('copy_center', 'localized_copy'):
        for row in out.get(collection) or []:
            if isinstance(row, dict) and row.get('field'):
                by_field[str(row.get('field'))] = row

    for row in out.get('preserved_listing_fields') or []:
        if not isinstance(row, dict):
            continue
        field = str(row.get('field') or '')
        source = by_field.get(field) or {}
        for key in ('delivery_translation', 'delivery_note'):
            if row.get(key) in (None, '') and source.get(key) not in (None, ''):
                row[key] = source.get(key)
        if _needs_cn_companion(row.get('value'), field):
            row['delivery_companion_status'] = 'READY' if _cn_value(row.get('delivery_translation')) else '待补中文释义'

    lang = out.setdefault('delivery_language', {})
    lang['foreign_copy_rule'] = (
        '凡运营人员可读到的目标市场外文内容，必须在同一人类对象提供中文释义 / 用途。'
        '适用于 Listing、类目、属性、描述、搜索词、FAQ、资产文案、视频、广告、评论/客服原话及研究摘录。'
    )
    lang['final_state_rule'] = 'FULL 最终交付不得以“待补中文释义”作为完成态；缺任一必需中文 companion 即 BLOCK。'
    return out


def _audit_preserved_listing(center: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for row in center.get('preserved_listing_fields') or []:
        if not isinstance(row, dict):
            continue
        field = str(row.get('field') or '')
        if _needs_cn_companion(row.get('value'), field) and not _cn_value(row.get('delivery_translation')):
            issues.append({
                'scope': 'PRESERVED_LISTING',
                'field': field,
                'code': 'FOREIGN_PRESERVED_LISTING_WITHOUT_CN_COMPANION',
                'value': _flatten_text(row.get('value'))[:320],
            })
    return issues


def _audit_supporting_human_content(package_dir: Path) -> list[dict[str, Any]]:
    package = Path(package_dir)
    issues: list[dict[str, Any]] = []
    for scope, rel_paths in _SCOPE_FILES.items():
        for rel in rel_paths:
            path = package / rel
            if not path.exists():
                continue
            data = _read_json(path)
            for issue in _audit_structured_copy(data, scope):
                issue['source_file'] = rel
                issues.append(issue)
    return issues


def audit_global_chinese_interpretation(
    package_dir: Path,
    center: dict[str, Any],
    base_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit Chinese interpretation across every human-facing commerce surface we can prove.

    The Agent authors semantic Chinese interpretation. Runtime never machine-translates arbitrary copy;
    it verifies completeness and blocks a false finished state.
    """
    base = deepcopy(base_audit or audit_human_language_delivery(package_dir, center))
    issues = list(base.get('issues') or [])
    global_issues = _audit_preserved_listing(center) + _audit_supporting_human_content(package_dir)
    issues.extend(global_issues)

    base['issues'] = issues
    base['status'] = 'PASS' if not issues else 'INCOMPLETE'
    base['global_human_content'] = {
        'status': 'PASS' if not global_issues else 'INCOMPLETE',
        'issue_count': len(global_issues),
        'scopes_checked': ['PRESERVED_LISTING', 'VIDEO', 'ADS', 'REVIEW', 'RESEARCH'],
        'rule': '所有运营可读外文内容必须在同一对象提供中文释义 / 用途；“待补中文释义”不是 FULL 完成态。',
    }
    base.setdefault('rules', {})['all_human_foreign_content'] = (
        'Listing/类目/属性/描述/搜索词/FAQ、资产 Visible Copy、视频屏显/字幕/VO、广告 Hook/标题/正文/CTA、'
        '评论/客服原话及研究摘录等，只要进入人类交付，就必须保留外文原文并在同一对象给中文释义 / 用途。'
    )
    return base


def render_preserved_listing_cn_rows(center: dict[str, Any]) -> str:
    """Reusable bilingual projection for preserved Listing data in non-Listing task views."""
    rows = []
    for item in center.get('preserved_listing_fields') or []:
        if not isinstance(item, dict) or item.get('value') in (None, '', [], {}):
            continue
        label = str(item.get('label') or item.get('field') or '字段')
        original = _flatten_text(item.get('value')).replace('|', '\\|').replace('\n', '<br>')
        zh = _flatten_text(item.get('delivery_translation') or '待补中文释义').replace('|', '\\|').replace('\n', '<br>')
        rows.append(f'| {label} | {original} | {zh} |')
    if not rows:
        return ''
    return '\n'.join([
        '### 已保留的数据（外文原文 + 中文释义）', '',
        '| 字段 | 目标市场 / 原始内容 | 中文释义 / 用途 |',
        '|---|---|---|',
        *rows,
        '',
    ])


def render_upload_center_md_with_global_cn(center: dict[str, Any], base_renderer: Callable[[dict[str, Any]], str]) -> str:
    text = base_renderer(center)
    if (center.get('task_scope') or {}).get('listing_active'):
        return text
    bilingual = render_preserved_listing_cn_rows(center)
    if not bilingual:
        return text
    marker = '### 已保留的数据\n'
    if marker in text:
        prefix = text.split(marker, 1)[0]
        return prefix.rstrip() + '\n\n' + bilingual
    return text.rstrip() + '\n\n' + bilingual
