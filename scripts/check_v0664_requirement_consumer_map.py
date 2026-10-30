#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'references' / 'REQUIREMENT_CONSUMER_MAP_V0664.json'
CURRENT_OVERRIDES = ROOT / 'references' / 'REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json'
VERSION_FILE = ROOT / 'VERSION'
CURRENT_BUILDER = ROOT / 'scripts' / 'build_plugin_dist_current.py'
GENERIC_PHRASES = (
    'current Skill/contract + relevant runtime/human/package consumer',
    'relevant runtime consumer',
    'current skill/contract',
)
PACKAGED_PREFIX = 'skills/cross-border-commerce-creative/'
CURRENT_RELEASE_REQS = ('REQ-046', 'REQ-047', 'REQ-048')
CURRENT_RELEASE_STATUSES = {
    'REQ-046': 'RELEASE_PROCESS_ENFORCED_CURRENT',
    'REQ-047': 'RELEASE_PROCESS_ENFORCED_CURRENT',
    'REQ-048': 'RELEASE_EVIDENCE_REQUIRED_CURRENT',
}


def _consumer_exists(rel: str) -> bool:
    direct = ROOT / rel
    if direct.exists():
        return True
    if rel.startswith(PACKAGED_PREFIX):
        source_equivalent = ROOT / rel[len(PACKAGED_PREFIX):]
        if source_equivalent.exists():
            return True
    return False


def _has_generic_placeholder(consumers: list, proof: list) -> bool:
    blob = json.dumps({'consumers': consumers, 'proof_objects': proof}, ensure_ascii=False)
    lowered = blob.casefold()
    if any(phrase.casefold() in lowered for phrase in GENERIC_PHRASES):
        return True
    return bool(re.search(r'(?<![A-Za-z0-9_])(?:TBD|TODO)(?![A-Za-z0-9_])', blob, re.I))


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain a JSON object')
    return value


def _current_version_family() -> str:
    text = VERSION_FILE.read_text(encoding='utf-8').strip()
    match = re.match(r'^(\d+\.\d+\.\d+)', text)
    return match.group(1) if match else ''


def _current_builder_target() -> str:
    text = CURRENT_BUILDER.read_text(encoding='utf-8')
    match = re.search(r"(?m)^CURRENT_BUILDER_TARGET\s*=\s*['\"](\d+\.\d+\.\d+)['\"]", text)
    return match.group(1) if match else ''


def _override_document() -> dict:
    return _load_json(CURRENT_OVERRIDES)


def _override_release_version() -> str:
    return str(_override_document().get('current_release_version') or '')


def effective_requirement_rows() -> list[dict]:
    """Return the one effective REQ-001..060 map after CURRENT release-process overrides."""
    base = _load_json(MAP)
    rows = [dict(row) for row in (base.get('requirements') or []) if isinstance(row, dict)]
    by_req = {str(row.get('req') or ''): row for row in rows}

    overrides_doc = _override_document()
    overrides = overrides_doc.get('overrides') or []
    for row in overrides:
        if not isinstance(row, dict):
            continue
        req = str(row.get('req') or '')
        if req:
            by_req[req] = dict(row)

    return [by_req[f'REQ-{i:03d}'] for i in range(1, 61) if f'REQ-{i:03d}' in by_req]


def _override_ids() -> list[str]:
    doc = _override_document()
    return [str(row.get('req') or '') for row in (doc.get('overrides') or []) if isinstance(row, dict)]


def audit() -> dict:
    issues = []

    try:
        rows = effective_requirement_rows()
        override_ids = _override_ids()
        override_release_version = _override_release_version()
    except Exception as exc:
        return {
            'status': 'FAIL',
            'requirement_count': 0,
            'issue_count': 1,
            'issues': [{'code': 'CURRENT_REQUIREMENT_MAP_LOAD_FAILED', 'error': str(exc)}],
            'current_overrides_applied': [],
            'current_version_family': _current_version_family() if VERSION_FILE.exists() else '',
            'current_override_release_version': '',
            'current_builder_target': _current_builder_target() if CURRENT_BUILDER.exists() else '',
        }

    expected = {f'REQ-{i:03d}' for i in range(1, 61)}
    ids = [str(row.get('req') or '') for row in rows if isinstance(row, dict)]
    got = set(ids)
    if got != expected:
        issues.append({'code':'REQ_ID_SET_MISMATCH','missing':sorted(expected-got),'unexpected':sorted(got-expected)})
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    if duplicates:
        issues.append({'code':'REQ_DUPLICATES','ids':duplicates})

    expected_overrides = list(CURRENT_RELEASE_REQS)
    if override_ids != expected_overrides:
        issues.append({'code':'CURRENT_OVERRIDE_SET_MISMATCH','expected':expected_overrides,'actual':override_ids})

    version_family = _current_version_family()
    builder_target = _current_builder_target()
    if not version_family:
        issues.append({'code':'CURRENT_VERSION_FAMILY_UNRESOLVED'})
    if not override_release_version:
        issues.append({'code':'CURRENT_OVERRIDE_RELEASE_VERSION_UNRESOLVED'})
    elif version_family and override_release_version != version_family:
        issues.append({
            'code':'CURRENT_OVERRIDE_RELEASE_VERSION_MISMATCH',
            'version_family':version_family,
            'override_release_version':override_release_version,
        })
    if not builder_target:
        issues.append({'code':'CURRENT_BUILDER_TARGET_UNRESOLVED'})
    elif version_family and builder_target != version_family:
        issues.append({'code':'CURRENT_BUILDER_VERSION_MISMATCH','version_family':version_family,'builder_target':builder_target})

    rows_by_req = {str(row.get('req') or ''): row for row in rows if isinstance(row, dict)}
    for req, expected_status in CURRENT_RELEASE_STATUSES.items():
        row = rows_by_req.get(req) or {}
        status = str(row.get('status') or '')
        consumers = [str(x) for x in (row.get('consumers') or [])]
        if status != expected_status:
            issues.append({'code':'CURRENT_RELEASE_STATUS_STALE','req':req,'expected':expected_status,'actual':status})
        if re.search(r'(?:PROVED|ENFORCED)[_-]?\d{3,4}', status, re.I):
            issues.append({'code':'HISTORICAL_RELEASE_STATUS_FORBIDDEN','req':req,'status':status})
        if req in {'REQ-046','REQ-047'} and 'scripts/build_plugin_dist_current.py' not in consumers:
            issues.append({'code':'CURRENT_BUILDER_CONSUMER_MISSING','req':req})
        if any(re.search(r'build_plugin_dist_v\d+', rel) for rel in consumers):
            issues.append({'code':'HISTORICAL_BUILDER_CONSUMER_FORBIDDEN','req':req,'consumers':consumers})

    for row in rows:
        if not isinstance(row, dict):
            issues.append({'code':'REQ_ROW_NOT_OBJECT','row':row})
            continue
        req = str(row.get('req') or '')
        consumers = row.get('consumers') or []
        proof = row.get('proof_objects') or []
        status = str(row.get('status') or '')
        if _has_generic_placeholder(consumers, proof):
            issues.append({'code':'GENERIC_CONSUMER_PLACEHOLDER','req':req})
        if not isinstance(consumers, list) or not consumers:
            issues.append({'code':'CONSUMER_LIST_MISSING','req':req})
            continue
        missing_paths = [str(rel) for rel in consumers if not _consumer_exists(str(rel))]
        if missing_paths:
            issues.append({'code':'CONSUMER_PATH_MISSING','req':req,'paths':missing_paths})
        if not isinstance(proof, list) or not proof:
            issues.append({'code':'PROOF_OBJECT_MISSING','req':req})
        if not status:
            issues.append({'code':'STATUS_MISSING','req':req})
        if status in {'IMPLEMENTED','PASS'}:
            issues.append({'code':'AMBIGUOUS_STATUS_FORBIDDEN','req':req,'status':status})

    return {
        'status':'PASS' if not issues else 'FAIL',
        'requirement_count':len(rows),
        'issue_count':len(issues),
        'issues':issues,
        'current_overrides_applied':override_ids,
        'current_version_family':version_family,
        'current_override_release_version':override_release_version,
        'current_builder_target':builder_target,
    }


def main() -> int:
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
