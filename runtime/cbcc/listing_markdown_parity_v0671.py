from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping
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
        for v in value.values(): out.extend(_flatten(v))
        return out
    if isinstance(value, list):
        out: list[str] = []
        for v in value: out.extend(_flatten(v))
        return out
    return [str(value)] if _p(value) else []


def _cell(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else ('' if value is None else str(value))
    return text.replace('|', '\\|').replace('\n', '<br>')


def render_multilingual_listing_appendix(center: Mapping[str, Any]) -> str:
    rows = [dict(x) for x in center.get('localized_copy') or [] if isinstance(x, Mapping) and _p(x.get('value'))]
    if not rows: return ''
    lines = ['', '## 多语言 Listing Canonical 对照', '', '> 该表直接投影 `HUMAN_DELIVERY.localized_copy`。目标市场原文、EN语义基线与中文释义不得在 MD 中静默消失。', '', '| Locale | 字段 | 目标市场 / 基线内容 | 中文释义 / 用途 | 状态 |', '|---|---|---|---|---|']
    for row in rows:
        zh = row.get('delivery_translation') or row.get('delivery_note') or '待补中文释义 / 用途'
        lines.append(f"| {_cell(row.get('locale') or '—')} | {_cell(row.get('field') or '—')} | {_cell(row.get('value'))} | {_cell(zh)} | {_cell(row.get('status') or row.get('release_status') or '—')} |")
    return '\n'.join(lines) + '\n'


def wrap_render_upload_center_md(fn: Callable[[dict[str, Any]], str]):
    if getattr(fn, '_cbcc_v0671_multilingual_listing_parity', False): return fn
    def rendered(center: dict[str, Any]) -> str:
        base = fn(center); appendix = render_multilingual_listing_appendix(center)
        if not appendix: return base
        marker = '## 多语言 Listing Canonical 对照'
        if marker in base:
            return base.split(marker, 1)[0].rstrip() + '\n\n' + appendix.lstrip()
        return base.rstrip() + '\n\n' + appendix
    setattr(rendered, '_cbcc_v0671_multilingual_listing_parity', True)
    return rendered


def ensure_listing_markdown_canonical_parity(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir); center = _read_json(package / 'HUMAN_DELIVERY.json')
    if not center or not (center.get('task_scope') or {}).get('listing_active'): return {'status': 'NOT_REQUIRED', 'path': None}
    path = package / '01_LISTING_UPLOAD_READY.md'
    if not path.exists():
        alt = package / 'listing/01_LISTING_UPLOAD_READY.md'; path = alt if alt.exists() else path
    if not path.exists(): return {'status': 'MISSING', 'path': str(path)}
    text = path.read_text(encoding='utf-8', errors='ignore'); appendix = render_multilingual_listing_appendix(center)
    if appendix:
        marker = '## 多语言 Listing Canonical 对照'
        refreshed = text.split(marker, 1)[0].rstrip() + '\n\n' + appendix.lstrip() if marker in text else text.rstrip() + '\n\n' + appendix
        if refreshed != text: path.write_text(refreshed, encoding='utf-8')
    return {'status': 'PASS', 'path': str(path), 'localized_rows': len(center.get('localized_copy') or [])}


def audit_listing_markdown_canonical_parity(package_dir: Path | str) -> list[dict[str, Any]]:
    package = Path(package_dir); center = _read_json(package / 'HUMAN_DELIVERY.json')
    if not center or not (center.get('task_scope') or {}).get('listing_active'): return []
    path = package / '01_LISTING_UPLOAD_READY.md'
    if not path.exists():
        alt = package / 'listing/01_LISTING_UPLOAD_READY.md'; path = alt if alt.exists() else path
    if not path.exists(): return [{'code': 'LISTING_MARKDOWN_MISSING'}]
    comparable = path.read_text(encoding='utf-8', errors='ignore').replace('\\|', '|')
    missing = []
    for source in ('copy_center', 'localized_copy'):
        for i, row in enumerate(center.get(source) or []):
            if not isinstance(row, Mapping): continue
            for slot in ('value', 'delivery_translation'):
                for token in _flatten(row.get(slot)):
                    if token not in comparable: missing.append({'source': source, 'row': i, 'field': row.get('field'), 'slot': slot, 'token': token[:180]})
    return [] if not missing else [{'code': 'LISTING_MARKDOWN_CANONICAL_FIELD_DRIFT', 'missing_count': len(missing), 'missing': missing[:100]}]
