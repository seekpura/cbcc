from __future__ import annotations

import json
from pathlib import Path

PATH = Path('references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json')


def main() -> None:
    data = json.loads(PATH.read_text(encoding='utf-8'))
    rows = data.get('new_requirements')
    if not isinstance(rows, list):
        raise SystemExit('new_requirements missing or invalid')

    wanted = {
        'REQ-088': 'PARTIAL_PHASE2_LINEAGE_PHASE7_FINAL_SEMANTIC_IDENTITY_BOUNDARY_TARGETED_VERIFIED_FULL_SOURCE_EVIDENCE_ASSUMPTION_DECISION_LINEAGE_PENDING',
        'REQ-090': 'PARTIAL_PHASE7_FINAL_PACKAGE_SEMANTIC_INVENTORY_ACTUAL_OUTPUT_BOUNDARY_TARGETED_VERIFIED_HOST_PARITY_AND_FULL_LINEAGE_PENDING',
    }
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        req = str(row.get('req') or '')
        if req in wanted:
            row['status'] = wanted[req]
            seen.add(req)
    if seen != set(wanted):
        raise SystemExit(f'missing Phase 7 requirement rows: {sorted(set(wanted)-seen)}')

    phase_status = data.setdefault('phase_status', {})
    phase_status['7'] = 'IN_PROGRESS_FINAL_PACKAGE_SEMANTIC_CLOSURE_TARGETED_VERIFIED_REQ088_REQ090_REMAINING'

    evidence = data.setdefault('phase_evidence', {})
    evidence['7'] = {
        'status': 'IN_PROGRESS_FINAL_PACKAGE_SEMANTIC_CLOSURE_TARGETED_VERIFIED',
        'verified_subtasks': [
            'Final semantic object inventory is derived from final CANONICAL_HUMAN_DATA business objects and production asset packages rather than a static hand-list.',
            'Host-native/Runtime source-level comparator uses canonical object IDs and semantic SHA-256 values rather than file layout or headings.',
            'One Runtime package cannot self-certify installed Host-native parity; final manifest records E2E_PENDING_INSTALLED_HOST_EXPORT without a second package.',
            'Provider planning/job templates cannot self-certify actual-output QA; final package exposes E2E_PENDING until Result→Review→Local Revision→lineage/hash is real.',
            'Phase 7 semantic closure runs after all Phase 6 final projections and rebuilds the final DELIVERY_MANIFEST / ZIP.',
        ],
        'focused_red': 'GitHub Actions run 41406191109: 4 failed because full_package_semantic_closure_v0681 did not exist.',
        'focused_green': 'GitHub Actions run 41406484829: 5/5 passed including final export ordering and ZIP integration.',
        'current_release_regression': 'GitHub Actions run 41406565002: SUCCESS with permanent Phase 7 semantic-closure gate plus build, release floors and artifact upload.',
        'proof_objects': [
            'runtime/cbcc/full_package_semantic_closure_v0681.py',
            'runtime/cbcc/commercial_delivery_continuity.py',
            'tests/test_v0681_phase7_final_package_semantic_closure.py',
            'tests/test_v0681_phase7_final_export_integration.py',
            'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE7_FINAL_PACKAGE_SEMANTICS.json',
            'FULL_DELIVERY_OBJECT_MANIFEST.json',
            'FULL_MATERIALIZATION_AUDIT.json',
            'DELIVERY_MANIFEST.json',
            'final delivery ZIP',
        ],
        'remaining_phase7': [
            'REQ-088 complete Source/Evidence/Assumption/Decision lineage chain with downstream-use and proof-object coverage.',
            'REQ-090 full package continuity coverage for all active semantic objects and lineage objects.',
            'Independent Host-native package semantic comparison when a real Host-native export is available; do not fabricate this from Runtime-only output.',
        ],
        'deferred_by_plan': [
            'Fresh K01 FULL remains Phase 10.',
            'Installed-plugin readback and Provider actual-output E2E remain Phase 11 / later proof boundary.',
        ],
        'source_truth': 'GITHUB_BRANCH_PHASE7_IN_PROGRESS_TARGETED_VERIFIED',
        'production_head_sha': '9000474846de7534be8409a9bbfc32c70fa31038',
        'current_gate_head_sha': '34d51aefb4b4b05e8dfc34842c059c3b28b4d71a',
    }

    data['version'] = '2026-11-02-phase7-in-progress-v1'
    data['current_phase'] = 'PHASE_7_IN_PROGRESS'
    data['previous_phase'] = 'PHASE_6_COMPLETE'
    data['next_phase'] = 'PHASE_7_REQ088_FULL_LINEAGE_CLOSURE'
    data['current_head_sha'] = '9000474846de7534be8409a9bbfc32c70fa31038'
    data['current_head_sha_semantics'] = (
        'Latest Phase 7 production-code boundary for final package semantic closure; later focused tests, CI, consumer-map and ledger commits do not change this production semantics boundary.'
    )
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
