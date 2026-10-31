from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping
import hashlib
import json
import re


LINEAGE_FILE = 'CANONICAL_LINEAGE.json'
_MATURE_FILE = re.compile(r'^\d{2}_.+')


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _lineage(contract: Mapping[str, Any]) -> dict[str, Any]:
    direct = contract.get('canonical_prompt_lineage')
    if isinstance(direct, Mapping) and direct.get('canonical_art_direction_sha256'):
        return dict(direct)
    card = contract.get('design_card')
    if isinstance(card, Mapping):
        nested = card.get('canonical_prompt_lineage')
        if isinstance(nested, Mapping) and nested.get('canonical_art_direction_sha256'):
            return dict(nested)
    return {}


def _numbered_files(asset_dir: Path) -> list[Path]:
    return sorted(p for p in asset_dir.iterdir() if p.is_file() and _MATURE_FILE.match(p.name))


def _source_lineage(asset_dir: Path) -> dict[str, Any]:
    for name in ('13_prompt_contract.json', '12_design_card.json'):
        path = asset_dir / name
        if path.exists():
            row = _lineage(_read_json(path))
            if row:
                return row
    return {}


def materialize_full_asset_lineage(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    if not root.exists():
        return {'status': 'NOT_FOUND', 'assets': [], 'issues': [{'code': 'ASSET_PACKAGE_ROOT_MISSING'}]}
    assets = []
    issues = []
    for asset_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        files = _numbered_files(asset_dir)
        if not files:
            continue
        lineage = _source_lineage(asset_dir)
        canonical_hash = str(lineage.get('canonical_art_direction_sha256') or '')
        if not canonical_hash:
            issues.append({'code': 'ASSET_PACKAGE_CANONICAL_LINEAGE_MISSING_V0671', 'asset_id': asset_dir.name})
        file_map = {
            path.name: {
                'sha256': _sha256(path),
                'bytes': path.stat().st_size,
                'canonical_source': canonical_hash or None,
            }
            for path in files
        }
        manifest = {
            'schema_version': 'cbcc-full-asset-package-lineage-v0.6.71',
            'asset_id': asset_dir.name,
            'canonical_art_direction_sha256': canonical_hash or None,
            'prompt_lineage': lineage,
            'files': file_map,
            'file_count': len(file_map),
            'principle': 'Every mature numbered asset artifact is bound to its exact bytes and the same canonical Art Direction lineage. Mutation after materialization is a blocking drift.',
        }
        (asset_dir / LINEAGE_FILE).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        assets.append({'asset_id': asset_dir.name, 'file_count': len(file_map), 'canonical_art_direction_sha256': canonical_hash or None})
    return {'status': 'PASS' if not issues else 'INCOMPLETE', 'assets': assets, 'issues': issues}


def audit_full_asset_lineage(root: Path | str) -> list[dict[str, Any]]:
    root = Path(root)
    if not root.exists():
        return [{'code': 'ASSET_PACKAGE_ROOT_MISSING'}]
    issues: list[dict[str, Any]] = []
    for asset_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        files = _numbered_files(asset_dir)
        if not files:
            continue
        lineage_path = asset_dir / LINEAGE_FILE
        if not lineage_path.exists():
            issues.append({'code': 'ASSET_PACKAGE_FULL_LINEAGE_MISSING', 'asset_id': asset_dir.name})
            continue
        manifest = _read_json(lineage_path)
        recorded = manifest.get('files') if isinstance(manifest.get('files'), Mapping) else {}
        actual_names = {p.name for p in files}
        recorded_names = set(recorded)
        for name in sorted(actual_names - recorded_names):
            issues.append({'code': 'ASSET_PACKAGE_FULL_LINEAGE_UNTRACKED_FILE', 'asset_id': asset_dir.name, 'file': name})
        for name in sorted(recorded_names - actual_names):
            issues.append({'code': 'ASSET_PACKAGE_FULL_LINEAGE_FILE_MISSING', 'asset_id': asset_dir.name, 'file': name})
        for path in files:
            row = recorded.get(path.name) if isinstance(recorded.get(path.name), Mapping) else {}
            if not row:
                continue
            sha = _sha256(path)
            size = path.stat().st_size
            if str(row.get('sha256') or '') != sha or int(row.get('bytes') or -1) != size:
                issues.append({'code': 'ASSET_PACKAGE_FULL_LINEAGE_DRIFT', 'asset_id': asset_dir.name, 'file': path.name, 'expected_sha256': row.get('sha256'), 'actual_sha256': sha, 'expected_bytes': row.get('bytes'), 'actual_bytes': size})
        current = _source_lineage(asset_dir)
        canonical = str(manifest.get('canonical_art_direction_sha256') or '')
        if not canonical:
            issues.append({'code': 'ASSET_PACKAGE_CANONICAL_LINEAGE_MISSING_V0671', 'asset_id': asset_dir.name})
        elif str(current.get('canonical_art_direction_sha256') or '') != canonical:
            issues.append({'code': 'ASSET_PACKAGE_CANONICAL_LINEAGE_DRIFT_V0671', 'asset_id': asset_dir.name, 'expected': canonical, 'actual': current.get('canonical_art_direction_sha256')})
        for field in ('prompt_cn_source_sha256', 'prompt_en_source_sha256', 'design_card_source_sha256'):
            value = current.get(field)
            if value and str(value) != canonical:
                issues.append({'code': 'ASSET_PACKAGE_CANONICAL_LINEAGE_DRIFT_V0671', 'asset_id': asset_dir.name, 'field': field, 'expected': canonical, 'actual': value})
    return issues


def wrap_compile_asset_packages(fn: Callable[..., dict[str, Any]], complete_asset_rows: Callable[[list[Mapping[str, Any]]], list[dict[str, Any]]] | None = None):
    def compiled(root: Path, assets: list[dict[str, Any]], *args, **kwargs):
        source_assets = complete_asset_rows(assets) if complete_asset_rows else assets
        result = fn(root, source_assets, *args, **kwargs)
        lineage = materialize_full_asset_lineage(Path(root))
        result = dict(result or {})
        result['full_asset_package_lineage_v0671'] = lineage
        index = Path(root) / 'ASSET_PACKAGE_INDEX.json'
        if index.exists():
            data = _read_json(index)
            additive = list(data.get('additive_capability_files') or [])
            if LINEAGE_FILE not in additive:
                additive.append(LINEAGE_FILE)
            data['additive_capability_files'] = additive
            data['full_asset_package_lineage'] = {'schema_version': 'cbcc-full-asset-package-lineage-v0.6.71', 'required': True}
            index.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return result
    setattr(compiled, '_cbcc_v0671_full_asset_lineage', True)
    return compiled
