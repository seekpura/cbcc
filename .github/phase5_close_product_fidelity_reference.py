from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('.')
PROD_SHA = '32c46dc40a3e13c15855ad771c014fca77a45a94'
MAP_REL = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json'


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


consumer_map = {
    'version': '2026-11-02-phase5-product-fidelity-reference-v1',
    'phase': 'PHASE_5_COMMERCIAL_GRADE_PROMPT_COMPILER',
    'subtask': 'PRODUCT_PRESENCE_FIDELITY_REFERENCE_INDEPENDENCE',
    'production_head_sha': PROD_SHA,
    'requirements': [
        {
            'requirement_id': 'REQ-084',
            'summary': 'Product Presence remains an Agent creative decision while Product Fidelity/reference behavior remains an independent truth/production decision through the final model-facing and renderer planes.',
            'source': 'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md + PROMPT_ART_DIRECTION_MASTER_CONTRACT.md + MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md',
            'implementation_status': 'PASS_PHASE4_PHASE5_PRODUCT_PRESENCE_FIDELITY_REFERENCE_INDEPENDENCE_TARGETED_VERIFIED_E2E_PENDING',
            'upstream_authority': [
                'asset_art_direction.product_presence',
                'asset_art_direction.product_fidelity.mode',
                'source_product_assets',
            ],
            'consumers': [
                'runtime/cbcc/agent_authority_prompt_compiler.py',
                'runtime/cbcc/reference_guided_native_authority.py',
                'runtime/cbcc/integrated_render_route_authority.py',
            ],
            'evidence': [
                'tests/test_v0676_phase5_product_fidelity_reference_prompt.py',
                'tests/test_v0676_phase4_inclusion_execution_authority.py',
                'tests/test_v0635_native_reference_provider_integrity.py',
                'GitHub Actions run 41382792721',
                f'production commit {PROD_SHA}',
            ],
            'verified_behavior': [
                'Canonical per-object asset_art_direction.product_fidelity.mode outranks legacy top-level/default fidelity aliases.',
                'EXACT_PIXEL_COMPOSITE remains exact through Design Card, reference authority, integrated-render finalizer, renderer recipe and production-parameter closure.',
                'REFERENCE_GUIDED_NATIVE_LOCK remains native reference generation and preserves package identity instructions.',
                'Product ABSENT/FORBIDDEN wins over fidelity machinery: no visible reference subject, exact-pixel layer or reference-input requirement is synthesized.',
                'A visible native-reference product with no real bound source remains model-generation blocking; runtime does not invent a source binding.',
            ],
            'residual_risk': 'Fresh real K01 FULL and Provider actual media / pixel-frame QA remain pending; REQ-086 and broader Phase 5 Prompt density/surface closure remain open.',
        }
    ],
    'cross_scope_verification': {
        'focused_red': '1 failed / 3 passed after invalid lighting fixture semantics were corrected; failure was exact-pixel fidelity downgraded to REFERENCE_GUIDED_NATIVE_LOCK.',
        'focused_green': '4 passed',
        'prior_phase5_dynamic': '4 passed',
        'phase4_presence_fidelity_inclusion': 'passed',
        'native_reference_provider_integrity': 'passed',
        'phase4_regressions': 'all tests/test_v0676_phase4_*.py passed',
        'v0673_prompt_route': 'passed',
        'v0674_cross_scope': 'passed',
    },
    'invariants': [
        'Product Presence and Product Fidelity are independent axes.',
        'Canonical per-object Art Direction outranks compatibility aliases.',
        'Exact-pixel compositing is explicit-only and cannot be silently normalized into native generation.',
        'Absent product never becomes visible because a fidelity/reference path exists.',
        'Missing visible real-product reference remains blocking rather than fabricated.',
    ],
    'pending': [
        'REQ-086 scene-derived camera/lighting/CMF Prompt consumption',
        'REQ-082 broader commercial Prompt density',
        'REQ-083 remaining surface-specific Prompt closure',
        'Fresh real K01 FULL',
        'Provider actual media / Review / smallest Local Revision / provenance',
    ],
}
write_json(ROOT / MAP_REL, consumer_map)

ledger_path = ROOT / 'references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json'
ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
by_req = {row['req']: row for row in ledger['new_requirements']}
by_req['REQ-084']['status'] = 'PASS_PHASE4_PHASE5_PRODUCT_PRESENCE_FIDELITY_REFERENCE_INDEPENDENCE_TARGETED_VERIFIED_E2E_PENDING'
ledger['phase_status']['5'] = 'IN_PROGRESS_DYNAMIC_AND_PRODUCT_FIDELITY_PROMPT_CONTINUITY_VERIFIED'
phase5 = ledger.setdefault('phase_evidence', {}).setdefault('5', {})
phase5['status'] = ledger['phase_status']['5']
subtasks = list(phase5.get('verified_subtasks') or [])
for item in (
    'Canonical dynamic motion/timing/audio Prompt continuity',
    'Product Presence × Fidelity × reference independence through final Prompt/render authority',
):
    if item not in subtasks:
        subtasks.append(item)
phase5['verified_subtasks'] = subtasks
proofs = list(phase5.get('proof_objects') or [])
for item in (
    MAP_REL,
    'tests/test_v0676_phase5_product_fidelity_reference_prompt.py',
    'runtime/cbcc/agent_authority_prompt_compiler.py',
    'runtime/cbcc/reference_guided_native_authority.py',
    'runtime/cbcc/integrated_render_route_authority.py',
):
    if item not in proofs:
        proofs.append(item)
phase5['proof_objects'] = proofs
phase5['product_fidelity_reference_production_head'] = PROD_SHA
phase5['product_fidelity_reference_focused_red'] = '1 failed / 3 passed after fixture correction'
phase5['product_fidelity_reference_focused_green'] = '4 passed'
phase5['product_fidelity_reference_cross_scope'] = 'prior Phase5 dynamic + Phase4 all + native provider + v0673/v0674 passed'
phase5['remaining'] = [
    'REQ-086 scene-derived camera/lighting/CMF Prompt consumption',
    'REQ-082 broader commercial Prompt density',
    'REQ-083 remaining surface-specific Prompt closure',
    'Fresh real K01 FULL',
    'Provider actual output / Review / Local Revision / provenance',
]
write_json(ledger_path, ledger)

matrix_path = ROOT / 'references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md'
matrix = matrix_path.read_text(encoding='utf-8')
matrix = matrix.replace(
    'Phase 5 is now IN PROGRESS: canonical dynamic motion/timing/audio Prompt continuity has committed targeted proof, while broader Prompt density, Product Presence/Fidelity/reference Prompt consumption, scene-derived photography Prompt consumption, provider/FULL-output requirements remain pending until their later tasks and real-chain evidence are complete.',
    'Phase 5 is now IN PROGRESS: canonical dynamic motion/timing/audio Prompt continuity and Product Presence/Fidelity/reference independence have committed targeted proof, while broader Prompt density, scene-derived photography Prompt consumption, provider/FULL-output requirements remain pending until their later tasks and real-chain evidence are complete.'
)
matrix = matrix.replace(
    '| REQ-084 | Product Presence/Fidelity/reference independence | presence is creative; fidelity is truth/production | PARTIAL_PHASE4_IMPLEMENTED + PHASE5_PENDING + E2E_PENDING |',
    '| REQ-084 | Product Presence/Fidelity/reference independence | presence is creative; fidelity is truth/production | PHASE4_PHASE5_TARGETED_PROOF + E2E_PENDING |'
)
matrix = matrix.replace(
    'canonical dynamic motion/timing/audio Prompt continuity is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json`; broader Prompt density plus REQ-084/REQ-086 Prompt-consumption tasks remain pending.',
    'canonical dynamic motion/timing/audio Prompt continuity is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json`; Product Presence/Fidelity/reference independence is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json`; broader Prompt density plus REQ-086 Prompt-consumption work remain pending.'
)
matrix_path.write_text(matrix, encoding='utf-8')

checker_path = ROOT / 'scripts/check_current_release_package.py'
checker = checker_path.read_text(encoding='utf-8')
checker = checker.replace(
    "CURRENT_PHASE5_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json'\n",
    "CURRENT_PHASE5_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json'\nCURRENT_PHASE5_FIDELITY_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json'\n"
)
checker = checker.replace(
    '    CURRENT_PHASE5_CONSUMER_MAP,\n)',
    '    CURRENT_PHASE5_CONSUMER_MAP,\n    CURRENT_PHASE5_FIDELITY_CONSUMER_MAP,\n)'
)
checker = checker.replace(
    '        CURRENT_PHASE5_CONSUMER_MAP,\n        \'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md\',',
    '        CURRENT_PHASE5_CONSUMER_MAP,\n        CURRENT_PHASE5_FIDELITY_CONSUMER_MAP,\n        \'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md\','
)
checker_path.write_text(checker, encoding='utf-8')

test_path = ROOT / 'tests/test_current_release_package_checker.py'
test_text = test_path.read_text(encoding='utf-8')
test_text = test_text.replace(
    '            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json",\n',
    '            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json",\n            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json",\n'
)
test_path.write_text(test_text, encoding='utf-8')

print(json.dumps({
    'req084': by_req['REQ-084']['status'],
    'phase5': ledger['phase_status']['5'],
    'consumer_map': MAP_REL,
}, ensure_ascii=False, indent=2))
