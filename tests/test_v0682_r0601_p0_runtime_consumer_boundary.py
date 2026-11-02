from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from runtime.cbcc.requirement_authority import (
    audit_requirement_authority,
    load_current_requirement_authority,
)

ROOT = Path(__file__).parents[1]


def _req(document: dict, req: str) -> dict:
    return next(row for row in document['requirements'] if row['req'] == req)


def _issue_codes(document: dict) -> set[str]:
    result = audit_requirement_authority(document, root=ROOT)
    return {str(row.get('code')) for row in result.get('issues', [])}


def test_p0_user_anchor_requires_actual_runtime_consumer_not_reference_or_script():
    """A P0 user requirement is not runtime-consumed merely because a reference/script path exists."""
    document = load_current_requirement_authority(ROOT)
    anchor = next(
        row for row in document['user_source_anchors']
        if row.get('source_id') == 'UC-H-01' and row.get('priority') == 'P0'
    )
    polluted = deepcopy(document)
    replacement_paths = [
        'references/USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md',
        'scripts/check_current_release_package.py',
    ]
    for index, req in enumerate(anchor['bound_requirements']):
        _req(polluted, req)['business_consumers'] = [replacement_paths[index % len(replacement_paths)]]

    assert 'P0_USER_SOURCE_RUNTIME_CONSUMER_MISSING' in _issue_codes(polluted)


def test_business_consumer_plane_contains_only_runtime_paths():
    document = load_current_requirement_authority(ROOT)
    offenders = [
        (row['req'], path)
        for row in document['requirements']
        for path in row.get('business_consumers', [])
        if not str(path).startswith('runtime/')
    ]
    assert offenders == []
