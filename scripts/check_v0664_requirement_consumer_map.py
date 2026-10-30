#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'references' / 'REQUIREMENT_CONSUMER_MAP_V0664.json'
FORBIDDEN = (
    'current Skill/contract + relevant runtime/human/package consumer',
    'relevant runtime consumer',
    'current skill/contract',
    'TBD',
    'TODO',
)


def audit() -> dict:
    data = json.loads(MAP.read_text(encoding='utf-8'))
    rows = data.get('requirements') or []
    issues = []
    expected = {f'REQ-{i:03d}' for i in range(1, 61)}
    ids = [str(row.get('req') or '') for row in rows if isinstance(row, dict)]
    got = set(ids)
    if got != expected:
        issues.append({'code':'REQ_ID_SET_MISMATCH','missing':sorted(expected-got),'unexpected':sorted(got-expected)})
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    if duplicates:
        issues.append({'code':'REQ_DUPLICATES','ids':duplicates})

    for row in rows:
        if not isinstance(row, dict):
            issues.append({'code':'REQ_ROW_NOT_OBJECT','row':row})
            continue
        req = str(row.get('req') or '')
        consumers = row.get('consumers') or []
        proof = row.get('proof_objects') or []
        status = str(row.get('status') or '')
        blob = json.dumps(row, ensure_ascii=False)
        if any(token.casefold() in blob.casefold() for token in FORBIDDEN):
            issues.append({'code':'GENERIC_CONSUMER_PLACEHOLDER','req':req})
        if not isinstance(consumers, list) or not consumers:
            issues.append({'code':'CONSUMER_LIST_MISSING','req':req})
            continue
        missing_paths = []
        for rel in consumers:
            p = ROOT / str(rel)
            if not p.exists():
                missing_paths.append(str(rel))
        if missing_paths:
            issues.append({'code':'CONSUMER_PATH_MISSING','req':req,'paths':missing_paths})
        if not isinstance(proof, list) or not proof:
            issues.append({'code':'PROOF_OBJECT_MISSING','req':req})
        if not status:
            issues.append({'code':'STATUS_MISSING','req':req})
        if status == 'IMPLEMENTED' or status == 'PASS':
            issues.append({'code':'AMBIGUOUS_STATUS_FORBIDDEN','req':req,'status':status})

    return {
        'status':'PASS' if not issues else 'FAIL',
        'requirement_count':len(rows),
        'issue_count':len(issues),
        'issues':issues,
    }


def main() -> int:
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
