from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('.')
MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json'
PROD = '50462319ba376b69bab7d71f7b4dc8620b83bd9d'


def replace_once(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if new in text:
        return
    if old not in text:
        raise SystemExit(f'closure marker missing in {path}: {old[:100]}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


# Human-readable matrix: advance only the targeted planes proven by this task.
matrix = 'references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md'
replace_once(
    matrix,
    'Phase 5 is now IN PROGRESS: canonical dynamic motion/timing/audio Prompt continuity and Product Presence/Fidelity/reference independence have committed targeted proof, while broader Prompt density, scene-derived photography Prompt consumption, provider/FULL-output requirements remain pending until their later tasks and real-chain evidence are complete.',
    'Phase 5 is now IN PROGRESS: canonical dynamic motion/timing/audio Prompt continuity, Product Presence/Fidelity/reference independence, and scene-derived photography/lighting/CMF Prompt consumption have committed targeted proof, while broader Prompt density, remaining surface Prompt closure, provider/FULL-output requirements remain pending until their later tasks and real-chain evidence are complete.',
)
replace_once(
    matrix,
    '| REQ-031 | Photography derived per scene | photographic route + parameter closure + Agent Art Direction | CONSUMER MAPPED + PHASE4_TARGETED_PROOF + PHASE5_PENDING + E2E_PENDING |',
    '| REQ-031 | Photography derived per scene | photographic route + parameter closure + Agent Art Direction | CONSUMER MAPPED + PHASE4_TARGETED_PROOF + PHASE5_SCENE_PHOTO_PROMPT_TARGETED_PROOF + E2E_PENDING |',
)
replace_once(
    matrix,
    '| REQ-035 | Concrete parameter consumption | parameter closure + prompt contract + continuity audit | CONSUMER MAPPED + E2E_PENDING |',
    '| REQ-035 | Concrete parameter consumption | parameter closure + prompt contract + continuity audit | CONSUMER MAPPED + PHASE5_SCENE_PHOTO_PARAMETER_TARGETED_PROOF + BROADER_PARAMETER_CONSUMPTION_PENDING + E2E_PENDING |',
)
replace_once(
    matrix,
    '| REQ-086 | Scene-derived photography/lighting/CMF closure | selected values derive from scene/material and reach acting plane | PARTIAL_PHASE4_IMPLEMENTED + PHASE5_PENDING + E2E_PENDING |',
    '| REQ-086 | Scene-derived photography/lighting/CMF closure | selected values derive from scene/material and reach acting plane | PHASE4_PHASE5_TARGETED_PROOF + E2E_PENDING |',
)
replace_once(
    matrix,
    'Product Presence/Fidelity/reference independence is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json`; broader Prompt density plus REQ-086 Prompt-consumption work remain pending.',
    'Product Presence/Fidelity/reference independence is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json`; scene-derived camera/lighting/CMF Prompt consumption is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json`; broader Prompt density and remaining surface Prompt closure remain pending.',
)


# Machine execution ledger: preserve IN_PROGRESS for Phase 5 while closing REQ-086 targeted proof.
ledger_path = ROOT / 'references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json'
ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
for row in ledger.get('new_requirements', []):
    if row.get('req') == 'REQ-086':
        row['status'] = 'PASS_PHASE4_PHASE5_SCENE_DERIVED_PHOTOGRAPHY_LIGHTING_CMF_PROMPT_CONSUMPTION_TARGETED_VERIFIED_E2E_PENDING'
        break
else:
    raise SystemExit('REQ-086 missing from execution ledger')
ledger.setdefault('phase_status', {})['5'] = 'IN_PROGRESS_DYNAMIC_PRODUCT_FIDELITY_AND_SCENE_PHOTOGRAPHY_PROMPT_CONTINUITY_VERIFIED'
phase5 = ledger.setdefault('phase_evidence', {}).setdefault('5', {})
phase5['status'] = 'IN_PROGRESS_DYNAMIC_PRODUCT_FIDELITY_AND_SCENE_PHOTOGRAPHY_PROMPT_CONTINUITY_VERIFIED'
phase5['scene_photography_prompt_consumption'] = {
    'requirement': 'REQ-086',
    'status': 'PASS_TARGETED_E2E_PENDING',
    'production_commit': PROD,
    'focused_tests': '3/3 passed',
    'phase4_adjacent_tests': '18/18 passed',
    'complete_v067_cross_scope': '334/334 passed',
    'workflow_run': 41386473797,
    'consumer_map': MAP,
    'verified_boundary': 'Per-asset authored camera/lighting/CMF override stale Strategy/runtime photography fields, reach the final acting Model Prompt, and are verified by concrete field-level consumption rows. Fresh K01 FULL and actual Provider output remain pending.'
}
proofs = phase5.setdefault('proof_objects', [])
for rel in (
    'runtime/cbcc/photographic_route_agent_authority.py',
    'runtime/cbcc/model_native_prompt_contract.py',
    'runtime/cbcc/model_native_prompt_audit_fix.py',
    'tests/test_v0677_phase5_req086_scene_photo_prompt_consumption.py',
    MAP,
):
    if rel not in proofs:
        proofs.append(rel)
behaviors = phase5.setdefault('verified_behaviors', [])
for text in (
    'Per-asset Art Direction camera/lighting/CMF fields explicitly authored by the Agent override stale Strategy/runtime photography values while compatible non-authored fill-ins may remain.',
    'Final Model Prompt consumption audit proves scene_derived_camera, scene_derived_lighting and scene_derived_cmf by concrete authored values rather than section presence.',
):
    if text not in behaviors:
        behaviors.append(text)
commits = phase5.setdefault('source_commits', [])
if PROD not in commits:
    commits.append(PROD)
ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


# CURRENT package checker: new durable consumer map must exist in source and exact built ZIP byte-for-byte.
checker = 'scripts/check_current_release_package.py'
replace_once(
    checker,
    "CURRENT_PHASE5_FIDELITY_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json'\n",
    "CURRENT_PHASE5_FIDELITY_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json'\nCURRENT_PHASE5_SCENE_PHOTOGRAPHY_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json'\n",
)
replace_once(
    checker,
    '    CURRENT_PHASE5_FIDELITY_CONSUMER_MAP,\n)\nCURRENT_RELEASE_REQS',
    '    CURRENT_PHASE5_FIDELITY_CONSUMER_MAP,\n    CURRENT_PHASE5_SCENE_PHOTOGRAPHY_CONSUMER_MAP,\n)\nCURRENT_RELEASE_REQS',
)
replace_once(
    checker,
    '        CURRENT_PHASE5_FIDELITY_CONSUMER_MAP,\n        \'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md\',',
    '        CURRENT_PHASE5_FIDELITY_CONSUMER_MAP,\n        CURRENT_PHASE5_SCENE_PHOTOGRAPHY_CONSUMER_MAP,\n        \'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md\',',
)


# Checker unit test: make omission of the new map a permanent release regression.
checker_test = 'tests/test_current_release_package_checker.py'
replace_once(
    checker_test,
    '            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json",\n            "references/CURRENT_CANONICAL_SKILL_BUILD.md",',
    '            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json",\n            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json",\n            "references/CURRENT_CANONICAL_SKILL_BUILD.md",',
)


# Permanent main verifier: execute the new focused proof, not merely package its ledger.
workflow = '.github/workflows/current-release-verification.yml'
replace_once(
    workflow,
    "      - 'tests/test_v0676_phase5_*.py'\n      - '.github/workflows/current-release-verification.yml'",
    "      - 'tests/test_v0676_phase5_*.py'\n      - 'tests/test_v0677_phase5_*.py'\n      - '.github/workflows/current-release-verification.yml'",
)
replace_once(
    workflow,
    "      - name: Verify CURRENT Phase 5 canonical dynamic Prompt continuity\n        env: {PYTHONHASHSEED: '0', PYTHONPATH: '.:runtime'}\n        run: python -m pytest -q tests/test_v0676_phase5_dynamic_prompt_continuity.py\n      - name: Verify prior maturity and CURRENT requirement accounting",
    "      - name: Verify CURRENT Phase 5 canonical dynamic Prompt continuity\n        env: {PYTHONHASHSEED: '0', PYTHONPATH: '.:runtime'}\n        run: python -m pytest -q tests/test_v0676_phase5_dynamic_prompt_continuity.py\n      - name: Verify CURRENT Phase 5 scene-derived photography Prompt consumption\n        env: {PYTHONHASHSEED: '0', PYTHONPATH: '.:runtime'}\n        run: python -m pytest -q tests/test_v0677_phase5_req086_scene_photo_prompt_consumption.py\n      - name: Verify prior maturity and CURRENT requirement accounting",
)
replace_once(
    workflow,
    "'Phase5 canonical dynamic Prompt continuity']}",
    "'Phase5 canonical dynamic Prompt continuity','Phase5 scene-derived photography Prompt consumption']}",
)

print('REQ-086 durable closure patch applied')
