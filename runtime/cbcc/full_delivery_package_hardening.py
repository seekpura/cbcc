from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable
import json
import re


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _status(data: dict[str, Any]) -> str:
    return str((data or {}).get('status') or '').upper()


def _issue(issues: list[dict[str, Any]], code: str, **extra: Any) -> None:
    issues.append({'code': code, **extra})


def _has_cjk(value: Any) -> bool:
    return bool(re.search(r'[\u3400-\u4dbf\u4e00-\u9fff]', str(value or '')))


def _foreign_human_copy(value: Any) -> bool:
    if value in (None, '', [], {}):
        return False
    text = str(value).strip()
    if _has_cjk(text):
        return False
    # Avoid treating short IDs / codes / locale names as copy. This is intentionally conservative.
    return bool(re.search(r'[A-Za-z]{3,}(?:[\s,.;:!?/&+\-]+[A-Za-z]{2,}){1,}', text))


def _companion(row: dict[str, Any], field: str) -> Any:
    direct = row.get(field + '_zh') or row.get(field + '_cn')
    if direct not in (None, '', [], {}):
        return direct
    translation = row.get('delivery_translation_zh')
    if isinstance(translation, dict):
        return translation.get(field) or translation.get('meaning') or translation.get('use')
    if translation not in (None, '', [], {}):
        return translation
    return None


def _audit_video_language_and_consumer(package: Path, issues: list[dict[str, Any]]) -> None:
    universe = _read_json(package / 'video' / 'VIDEO_UNIVERSE.json')
    rows = [x for x in universe.get('assets') or [] if isinstance(x, dict)]
    if not rows:
        return

    html_path = package / 'index.html'
    if html_path.exists():
        page = html_path.read_text(encoding='utf-8', errors='ignore')
        has_video_consumer = ('data-route="video"' in page) or ('data-canonical-lazy-root="video"' in page)
        if not has_video_consumer:
            _issue(issues, 'VIDEO_OBJECTS_HAVE_NO_PRIMARY_HTML_CONSUMER', count=len(rows))

    for i, row in enumerate(rows, start=1):
        vid = str(row.get('video_id') or row.get('id') or f'VID-{i:02d}')
        for field in ('hook', 'first_frame_copy', 'cta', 'on_screen_text', 'voiceover', 'vo', 'script'):
            value = row.get(field)
            if _foreign_human_copy(value) and not _companion(row, field):
                _issue(issues, 'VIDEO_HUMAN_COPY_CHINESE_COMPANION_MISSING', video_id=vid, field=field)
        for sidx, shot in enumerate(row.get('shots') or row.get('shot_program') or [], start=1):
            if not isinstance(shot, dict):
                continue
            value = shot.get('visible_copy') or shot.get('on_screen_text') or shot.get('copy') or shot.get('dialogue') or shot.get('subtitle')
            if _foreign_human_copy(value):
                companion = (
                    shot.get('delivery_translation_zh') or shot.get('visible_copy_zh') or
                    shot.get('on_screen_text_zh') or shot.get('copy_zh') or
                    shot.get('dialogue_zh') or shot.get('subtitle_zh')
                )
                if not companion:
                    _issue(
                        issues,
                        'VIDEO_HUMAN_COPY_CHINESE_COMPANION_MISSING',
                        video_id=vid,
                        shot=sidx,
                        field='shot_visible_copy',
                    )


def harden_full_package_audit(
    base_fn: Callable[[Path | str], dict[str, Any]],
    strategy_validator: Callable[[dict[str, Any]], dict[str, Any]],
):
    """Upgrade package completion from file-presence to object-content validation.

    This wrapper exists because the real v0.6.46 Host-native package demonstrated that a package can
    contain nine section files and still lose commercial depth, Chinese companions and machine truth.
    """
    def audited(package_dir: Path | str) -> dict[str, Any]:
        package = Path(package_dir)
        base = base_fn(package)
        issues = list(base.get('issues') or [])

        for rel in ('DELIVERY_MANIFEST.json', 'FULL_MATERIALIZATION_AUDIT.json'):
            if not (package / rel).exists():
                _issue(issues, 'FULL_DELIVERY_OBJECT_MISSING', path=rel)

        strategy = _read_json(package / 'strategy' / 'strategy_authority.json')
        if not strategy:
            _issue(issues, 'PACKAGED_STRATEGY_AUTHORITY_MISSING_OR_INVALID')
            strategy_depth = {'status': 'INCOMPLETE', 'issues': [{'code': 'STRATEGY_AUTHORITY_MISSING'}]}
        else:
            strategy_depth = strategy_validator(strategy)
            if _status(strategy_depth) != 'PASS':
                _issue(
                    issues,
                    'PACKAGED_STRATEGY_DEPTH_V3_FAILED',
                    issue_count=len(strategy_depth.get('issues') or []),
                    strategy_issues=deepcopy(strategy_depth.get('issues') or []),
                )

        depth_artifact = _read_json(package / 'FULL_DELIVERY_DEPTH_AUDIT.json')
        if depth_artifact and _status(depth_artifact) not in {'PASS', 'PASS_WITH_SUBMISSION_HOLDS'}:
            _issue(issues, 'FULL_DELIVERY_DEPTH_AUDIT_NOT_PASS', status=_status(depth_artifact))

        human_language = _read_json(package / 'HUMAN_LANGUAGE_AUDIT.json')
        if human_language and _status(human_language) != 'PASS':
            _issue(issues, 'HUMAN_LANGUAGE_AUDIT_NOT_PASS', status=_status(human_language))

        language_matrix = _read_json(package / 'DELIVERY_LANGUAGE_MATRIX_AUDIT.json')
        if language_matrix and _status(language_matrix) not in {'PASS', 'NOT_REQUIRED'}:
            _issue(issues, 'DELIVERY_LANGUAGE_MATRIX_NOT_PASS', status=_status(language_matrix))

        platform_scope = _read_json(package / 'PLATFORM_SCOPE.json')
        if platform_scope:
            platform_status = str(platform_scope.get('platform_status') or '').upper()
            market_status = str(platform_scope.get('market_status') or '').upper()
            if platform_status == 'INFERRED' or market_status == 'INFERRED':
                _issue(
                    issues,
                    'HISTORICAL_OR_INFERRED_PLATFORM_SCOPE_FORBIDDEN',
                    platform_status=platform_status,
                    market_status=market_status,
                )

        object_manifest = _read_json(package / 'FULL_DELIVERY_OBJECT_MANIFEST.json')
        if object_manifest:
            for row in object_manifest.get('objects') or []:
                if not isinstance(row, dict):
                    continue
                if str(row.get('status') or '').upper() == 'MISSING_REQUIRED_OBJECT':
                    _issue(issues, 'FULL_OBJECT_MANIFEST_REQUIRED_OBJECT_MISSING', object=row.get('object'))
                if str(row.get('status') or '').upper() == 'ACTIVE' and row.get('path'):
                    if not (package / str(row['path'])).exists():
                        _issue(
                            issues,
                            'FULL_OBJECT_MANIFEST_ACTIVE_PATH_MISSING',
                            object=row.get('object'),
                            path=row.get('path'),
                        )

        _audit_video_language_and_consumer(package, issues)

        unique: list[dict[str, Any]] = []
        seen: set[str] = set()
        for row in issues:
            sig = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)
            if sig not in seen:
                seen.add(sig)
                unique.append(row)

        out = dict(base)
        out['issues'] = unique
        out['status'] = 'PASS' if not unique else 'INCOMPLETE'
        out['strategy_depth_v3'] = strategy_depth
        out['content_validation_required'] = True
        out['file_presence_alone_is_insufficient'] = True
        out['video_language_and_html_consumer_audited'] = True
        out['contract'] = 'HOST_NATIVE_FULL_MATERIALIZATION_EQUALS_RUNTIME_EXPORT_V3_CONTENT_VALIDATED'
        return out
    return audited
