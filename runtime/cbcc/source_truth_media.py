from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import re
import shutil


_IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.bmp', '.tif', '.tiff', '.avif'}
_PATH_KEYS = {
    'path', 'file', 'file_path', 'filepath', 'local_path', 'source_path', 'source_file',
    'image_path', 'image_file', 'reference_path', 'reference_file', 'asset_path', 'uri',
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _safe_name(name: str) -> str:
    stem = re.sub(r'[^A-Za-z0-9._-]+', '-', name).strip('-._') or 'source'
    return stem[:160]


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _walk_paths(value: Any, out: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).casefold() in _PATH_KEYS and isinstance(item, str) and item.strip():
                out.append(item.strip())
            else:
                _walk_paths(item, out)
    elif isinstance(value, list):
        for item in value:
            _walk_paths(item, out)


def _resolve_candidate(project: Path, raw: str) -> Path | None:
    low = raw.casefold()
    if low.startswith(('http://', 'https://', 'data:', 'plugin://', 'file://')):
        return None
    candidate = Path(raw)
    checks = [candidate] if candidate.is_absolute() else [project / candidate, project.parent / candidate]
    for item in checks:
        try:
            if item.exists() and item.is_file() and item.suffix.lower() in _IMAGE_EXTS:
                return item.resolve()
        except Exception:
            continue
    return None


def _common_source_files(project: Path) -> list[Path]:
    roots = [
        project / 'sources', project / 'source', project / 'uploads', project / 'source_assets',
        project / 'artifacts/source_assets', project / 'artifacts/source_media',
    ]
    found = []
    for root in roots:
        if not root.exists() or not root.is_dir():
            continue
        for path in root.rglob('*'):
            if path.is_file() and path.suffix.lower() in _IMAGE_EXTS:
                found.append(path.resolve())
    return found


def _write_human_status(package: Path, result: dict[str, Any]) -> None:
    source_dir = package / 'sources'
    source_dir.mkdir(parents=True, exist_ok=True)
    copied = [x for x in result.get('items') or [] if x.get('status') == 'COPIED']
    missing = [x for x in result.get('items') or [] if x.get('status') == 'MISSING_FILE']
    lines = ['# 产品真源媒体状态', '']
    if copied:
        lines.extend([
            '## 已加载真源',
            '',
            f'已将 **{len(copied)}** 个真实商品/包装源图物化到当前交付包。`index.html` 会以内嵌媒体方式读取这些文件，单独打开 HTML 不依赖原项目目录。',
            '',
        ])
        for item in copied:
            lines.append(f'- `{item.get("package_path")}` · {item.get("bytes", 0):,} bytes')
        lines.append('')
    if missing:
        lines.extend([
            '## 真源文件缺失 / 未绑定',
            '',
            '以下声明的真源文件在导出时不可解析。当前交付不得用空白图片或替代图伪装为已加载；需要重新绑定真实源文件后再进入生产。',
            '',
        ])
        for item in missing:
            lines.append(f'- `{item.get("source_path")}`')
        lines.append('')
    if not copied and not missing:
        lines.extend([
            '## 当前未声明可携带真源图',
            '',
            '当前项目没有解析到可物化的真实商品/包装源图。若本任务依赖真实商品身份，请先绑定源图。',
            '',
        ])
    lines.extend([
        '## 交付规则',
        '',
        '- 真源图用于事实、商品身份与生产参考；它不强制每个创意资产都出现商品。',
        '- 创意资产是否出现商品继续由逐资产购买决策与策展决定。',
    ])
    (source_dir / 'SOURCE_TRUTH_STATUS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def materialize_source_truth_media(project_dir: Path | str, package_dir: Path | str) -> dict[str, Any]:
    project = Path(project_dir)
    package = Path(package_dir)
    package.mkdir(parents=True, exist_ok=True)
    contract_path = project / 'artifacts/source_product_assets.json'
    contract = _read_json(contract_path)

    raw_paths: list[str] = []
    _walk_paths(contract, raw_paths)
    candidates: list[Path] = []
    unresolved: list[str] = []
    seen = set()

    for raw in raw_paths:
        resolved = _resolve_candidate(project, raw)
        if resolved is None:
            unresolved.append(raw)
            continue
        key = str(resolved)
        if key not in seen:
            candidates.append(resolved)
            seen.add(key)

    for path in _common_source_files(project):
        key = str(path)
        if key not in seen:
            candidates.append(path)
            seen.add(key)

    dest_root = package / 'sources'
    items = []
    used_names: set[str] = set()
    for idx, src in enumerate(candidates, start=1):
        base = _safe_name(src.name)
        name = base
        if name in used_names:
            name = f'{src.stem}-{idx}{src.suffix}'
        used_names.add(name)
        dest = dest_root / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        items.append({
            'source_path': str(src),
            'package_path': str(dest.relative_to(package)).replace('\\', '/'),
            'status': 'COPIED',
            'sha256': _sha(dest),
            'bytes': dest.stat().st_size,
        })

    for raw in unresolved:
        items.append({'source_path': raw, 'package_path': None, 'status': 'MISSING_FILE'})

    missing_count = sum(1 for x in items if x.get('status') == 'MISSING_FILE')
    copied_count = sum(1 for x in items if x.get('status') == 'COPIED')
    if contract and copied_count == 0:
        status = 'INCOMPLETE'
    elif missing_count:
        status = 'INCOMPLETE'
    elif copied_count:
        status = 'READY'
    else:
        status = 'NO_SOURCE_MEDIA_DECLARED'

    result = {
        'status': status,
        'copied_count': copied_count,
        'missing_count': missing_count,
        'items': items,
        'human_status_file': 'sources/SOURCE_TRUTH_STATUS.md',
        'html_policy': 'COPIED_SOURCE_IMAGES_MUST_BE_EMBEDDED_BY_HTML_RENDERER; MISSING_FILES_MUST_BE_SHOWN_AS_EXPLICIT_OPERATOR_STATE.',
    }
    (package / 'SOURCE_TRUTH_MEDIA_AUDIT.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    _write_human_status(package, result)
    return result
