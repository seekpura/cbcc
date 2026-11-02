from __future__ import annotations

import json
from pathlib import Path

PATH = Path('references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json')

STATUS_BY_REQ = {
    'REQ-061': 'PARTIAL_PHASE1_GRAPH_AUTHORITY_PHASE6_JSON_MD_HTML_SAME_SOURCE_PROJECTION_VERIFIED_PHASE7_LINEAGE_E2E_PENDING',
    'REQ-070': 'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_PHASE6_LONGFORM_DELIVERY_ROUTE_TARGETED_VERIFIED_PHASE7_PACKAGE_CONTINUITY_PENDING',
    'REQ-076': 'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_PHASE4_SURFACE_ART_DIRECTION_PHASE6_STORE_LANDING_DELIVERY_ROUTE_TARGETED_VERIFIED_REAL_FAMILY_E2E_PENDING',
    'REQ-077': 'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_PHASE6_CRM_LIFECYCLE_DELIVERY_ROUTE_TARGETED_VERIFIED_REAL_FAMILY_E2E_PENDING',
    'REQ-089': 'PASS_PHASE6_HUMAN_WORKSPACE_FULL_CANONICAL_ROUTING_TARGETED_VERIFIED_FRESH_K01_PENDING_PHASE10',
}


def main() -> None:
    data = json.loads(PATH.read_text(encoding='utf-8'))

    rows = data.get('new_requirements')
    if not isinstance(rows, list):
        raise SystemExit('new_requirements missing or invalid')

    seen: set[str] = set()
    for row in rows:
        req = str(row.get('req') or '') if isinstance(row, dict) else ''
        if req in STATUS_BY_REQ:
            row['status'] = STATUS_BY_REQ[req]
            seen.add(req)
    missing = sorted(set(STATUS_BY_REQ) - seen)
    if missing:
        raise SystemExit(f'required Phase 6 ledger rows missing: {missing}')

    phase_status = data.setdefault('phase_status', {})
    if not isinstance(phase_status, dict):
        raise SystemExit('phase_status invalid')
    phase_status['6'] = 'PASS_PHASE6_JSON_MD_HTML_SAME_SOURCE_ROUTED_HUMAN_WORKSPACE_AND_ACTIVATED_DELIVERY_FAMILIES_VERIFIED'

    phase_evidence = data.setdefault('phase_evidence', {})
    if not isinstance(phase_evidence, dict):
        raise SystemExit('phase_evidence invalid')
    phase_evidence['6'] = {
        'status': 'PASS_PHASE6_DELIVERY_PARITY_AND_HUMAN_WORKSPACE_TARGETED_VERIFIED',
        'verified_subtasks': [
            'REQ-061 canonical JSON / complete Markdown / HTML same-source projection with deterministic semantic signature',
            'REQ-089 canonical business objects consumed inside semantic Human Workspace routes; Archive cannot false-pass routed coverage',
            'REQ-070 activated A+ / PDP / Longform / Specification / Source-document delivery-family lens',
            'REQ-076 activated Store / Banner / Landing / Campaign / Seasonal delivery-family lens',
            'REQ-077 activated CRM / Lifecycle / Post-purchase delivery-family lens',
            'Final DELIVERY_MANIFEST and ZIP consume canonical parity, routed-workspace and delivery-family audits',
            'Dynamic IA remains project-authored: absent families do not become fixed navigation entries',
        ],
        'focused_red': {
            'req061': 'GitHub Actions run 41402373737: 2 failed before canonical_delivery_parity_v0680 existed',
            'req089': 'GitHub Actions run 41403382215: 2 failed / 1 passed before routed canonical consumer existed',
            'delivery_families': 'GitHub Actions run 41403877395: 3 failed before delivery_family_workspace_v0680 existed',
        },
        'focused_green': {
            'req061': 'GitHub Actions run 41402749660: 3/3 passed including final ZIP/Manifest assertions',
            'req089': 'GitHub Actions run 41403642950: 4/4 passed including final export/ZIP consumption',
            'delivery_families': 'GitHub Actions run 41404690731: 4/4 passed including final Manifest/ZIP/index.html consumption',
        },
        'current_release_regression': 'GitHub Actions run 41404789717: SUCCESS with permanent Phase 6 REQ-061 + REQ-089 + delivery-family gates, build, all release floors and artifact upload',
        'production_head_sha': 'e2b6ae1237f75e959b81e2254e41ac23a9396306',
        'current_gate_head_sha': 'ad2cef840b16687b0c9ee03d9b54726302790b08',
        'proof_objects': [
            'runtime/cbcc/canonical_delivery_parity_v0680.py',
            'runtime/cbcc/canonical_routed_workspace_v0680.py',
            'runtime/cbcc/delivery_family_workspace_v0680.py',
            'runtime/cbcc/commercial_delivery_continuity.py',
            'tests/test_v0680_phase6_req061_same_source_projection.py',
            'tests/test_v0680_phase6_req089_routed_canonical_workspace.py',
            'tests/test_v0680_phase6_delivery_family_routes.py',
            'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE6_CANONICAL_DELIVERY_PARITY.json',
            'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE6_ROUTED_HUMAN_WORKSPACE.json',
            'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE6_DELIVERY_FAMILIES.json',
            'CANONICAL_HUMAN_DATA.json',
            'CANONICAL_HUMAN_DATA.md',
            'CANONICAL_DELIVERY_PARITY_AUDIT.json',
            'CANONICAL_ROUTED_WORKSPACE_AUDIT.json',
            'DELIVERY_FAMILY_WORKSPACE_AUDIT.json',
            'DELIVERY_MANIFEST.json',
            'index.html',
            'final delivery ZIP',
        ],
        'verified_behaviors': [
            'Canonical JSON remains the authority; Markdown and HTML are lossless projections rather than independently authored business summaries.',
            'JSON / Markdown / HTML carry one deterministic canonical semantic signature and parity failure blocks export.',
            'Canonical objects must appear inside semantic Human Workspace routes; generic Archive/search presence is explicitly insufficient.',
            'Object-family delivery lenses are activated only by real canonical asset metadata and never form a fixed capability menu.',
            'Longform, Store/Landing and CRM family objects survive into routed HTML, delivery audits, DELIVERY_MANIFEST and final ZIP.',
            'Targeted Phase 6 closure preserves earlier Phase 1-5 release floors and the CURRENT plugin build/upload path.',
        ],
        'deferred_by_plan': [
            'Phase 7 REQ-088 full Source / Evidence / Assumption / Decision lineage closure',
            'Phase 7 REQ-090 FULL materialization/package continuity',
            'Phase 10 Fresh K01 FULL end-to-end evidence',
            'Phase 11 installed-plugin readback and Provider actual media / Review / Local Revision / provenance proof',
        ],
        'source_truth': 'GITHUB_BRANCH_PHASE6_TARGETED_VERIFIED',
    }

    data['version'] = '2026-11-02-phase6-complete-v1'
    data['current_phase'] = 'PHASE_6_COMPLETE'
    data['previous_phase'] = 'PHASE_5_COMPLETE'
    data['next_phase'] = 'PHASE_7_FULL_MATERIALIZATION_PACKAGE_CONTINUITY'
    data['current_head_sha'] = 'e2b6ae1237f75e959b81e2254e41ac23a9396306'
    data['current_head_sha_semantics'] = (
        'Latest Phase 6 production-code boundary; later focused tests, consumer maps, CI-gate and ledger-only commits '
        'do not change Phase 6 production semantics.'
    )

    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
