from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping
import json

_APPENDIX_MARKER = '## 多语言 Listing Canonical 对照'


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


def _plain(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return '' if value is None else str(value)


def render_multilingual_listing_appendix(center: Mapping[str, Any]) -> str:
    rows = [dict(x) for x in center.get('localized_copy') or [] if isinstance(x, Mapping) and _p(x.get('value'))]
    if not rows:
        return ''
    lines = [
        '', _APPENDIX_MARKER, '',
        '> 该区直接投影 `HUMAN_DELIVERY.localized_copy`。目标市场原文、EN语义基线与中文释义不得在 MD 中静默消失。',
        '> 使用块式原文而不是 Markdown 表格，避免标题、描述、FAQ 中的 `|`、换行或长文本被转义后失去连续原文。', '',
    ]
    for row in rows:
        locale = _plain(row.get('locale') or '—')
        field = _plain(row.get('field') or '—')
        value = _plain(row.get('value'))
        zh = _plain(row.get('delivery_translation') or row.get('delivery_note') or '待补中文释义 / 用途')
        status = _plain(row.get('status') or row.get('release_status') or '—')
        lines += [
            f'### {field} · {locale}', '',
            value, '',
            f'- **中文释义 / 用途**：{zh}',
            f'- **状态**：{status}', '',
        ]
    return '\n'.join(lines).rstrip() + '\n'


def _refresh_appendix(text: str, appendix: str) -> str:
    if not appendix:
        return text
    if _APPENDIX_MARKER in text:
        prefix = text.split(_APPENDIX_MARKER, 1)[0].rstrip()
        return prefix + '\n\n' + appendix.lstrip('\n')
    return text.rstrip() + '\n\n' + appendix.lstrip('\n')


def wrap_render_upload_center_md(fn: Callable[[dict[str, Any]], str]):
    """Make multilingual canonical Listing rows part of the renderer itself."""
    if getattr(fn, '_cbcc_v0671_multilingual_listing_parity', False):
        return fn

    def rendered(center: dict[str, Any]) -> str:
        base = fn(center)
        return _refresh_appendix(base, render_multilingual_listing_appendix(center))

    setattr(rendered, '_cbcc_v0671_multilingual_listing_parity', True)
    return rendered


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
    refreshed = _refresh_appendix(text, render_multilingual_listing_appendix(center))
    if refreshed != text:
        path.write_text(refreshed, encoding='utf-8')
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
    # Legacy table projections may contain escaped pipes; current block projection preserves exact text.
    comparable = text.replace('\\|', '|')
    missing = []
    for source in ('copy_center', 'localized_copy'):
        for i, row in enumerate(center.get(source) or []):
            if not isinstance(row, Mapping):
                continue
            for slot in ('value', 'delivery_translation'):
                for token in _flatten(row.get(slot)):
                    if token not in comparable:
                        missing.append({'source': source, 'row': i, 'field': row.get('field'), 'slot': slot, 'token': token[:180]})
    if not missing:
        return []
    return [{'code': 'LISTING_MARKDOWN_CANONICAL_FIELD_DRIFT', 'missing_count': len(missing), 'missing': missing[:100]}]
