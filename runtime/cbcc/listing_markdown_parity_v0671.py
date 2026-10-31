from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _p(v: Any) -> bool:
    return v not in (None, '', [], {})


def _flatten(value: Any) -> list[str]:
    if isinstance(value, Mapping):
        out: list[str] = []
        for v in value.values():
            out.extend(_flatten(v))
        return out
    if isinstance(value, list):
        out = []
        for v in value:
            out.extend(_flatten(v))
        return out
    return [str(value)] if _p(value) else []


def _cell(value: Any) -> str:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = '' if value is None else str(value)
    return text.replace('|', '\\|').replace('\n', '<br>')


def render_multilingual_listing_appendix(center: Mapping[str, Any]) -> str:
    rows = [dict(x) for x in center.get('localized_copy') or [] if isinstance(x, Mapping) and _p(x.get('value'))]
    if not rows:
        return ''
    lines = [
        '', '## 多语言 Listing Canonical 对照', '',
        '> 该表直接投影 `HUMAN_DELIVERY.localized_copy`。目标市场原文、EN语义基线与中文释义不得在 MD 中静默消失。', '',
        '| Locale | 字段 | 目标市场 / 基线内容 | 中文释义 / 用途 | 状态 |',
        '|---|---|---|---|---|',
    ]
    for row in rows:
        zh = row.get('delivery_translation') or row.get('delivery_note') or '待补中文释义 / 用途'
        lines.append(f"| {_cell(row.get('locale') or '—')} | {_cell(row.get('field') or '—')} | {_cell(row.get('value'))} | {_cell(zh)} | {_cell(row.get('status') or row.get('release_status') or '—')} |")
    return '\n'.join(lines) + '\n'


def ensure_listing_markdown_canonical_parity(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    center = _read_json(package / 'HUMAN_DELIVERY.json')
    if not center or not (center.get('task_scope') or {}).get('listing_active'):
        return {'status': 'NOT_REQUIRED', 'path': None}
    path = package / '01_LISTING_UPLOAD_READY.md'
    if not path.exists():
        alt = package / 'listing/01_LISTING_UPLOAD_READY.md'
        path = alt if alt.exists() else path
    if not path.exists():
        return {'status': 'MISSING', 'path': str(path)}
    text = path.read_text(encoding='utf-8', errors='ignore')
    appendix = render_multilingual_listing_appendix(center)
    if appendix and '## 多语言 Listing Canonical 对照' not in text:
        text = text.rstrip() + '\n\n' + appendix
        path.write_text(text, encoding='utf-8')
    return {'status': 'PASS', 'path': str(path), 'localized_rows': len(center.get('localized_copy') or [])}


def audit_listing_markdown_canonical_parity(package_dir: Path | str) -> list[dict[str, Any]]:
    package = Path(package_dir)
    center = _read_json(package / 'HUMAN_DELIVERY.json')
    if not center or not (center.get('task_scope') or {}).get('listing_active'):
        return []
    path = package / '01_LISTING_UPLOAD_READY.md'
    if not path.exists():
        alt = package / 'listing/01_LISTING_UPLOAD_READY.md'
        path = alt if alt.exists() else path
    if not path.exists():
        return [{'code': 'LISTING_MARKDOWN_MISSING'}]
    text = path.read_text(encoding='utf-8', errors='ignore')
    missing = []
    for source in ('copy_center', 'localized_copy'):
        for i, row in enumerate(center.get(source) or []):
            if not isinstance(row, Mapping):
                continue
            for slot in ('value', 'delivery_translation'):
                for token in _flatten(row.get(slot)):
                    if token not in text:
                        missing.append({'source': source, 'row': i, 'field': row.get('field'), 'slot': slot, 'token': token[:180]})
    if not missing:
        return []
    return [{'code': 'LISTING_MARKDOWN_CANONICAL_FIELD_DRIFT', 'missing_count': len(missing), 'missing': missing[:100]}]
