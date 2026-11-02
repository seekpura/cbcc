from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('.')
MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json'
PROD = '8b3ebf11a52d14a3526004b58a1d632444b568fc'
RUN = '41380596952'

# 1) Machine execution ledger: only REQ-082/083 and Phase 5 progress are advanced.
ledger_path = ROOT / 'references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json'
ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
by_req = {row['req']: row for row in ledger.get('new_requirements', [])}
by_req['REQ-082']['status'] = 'PARTIAL_PHASE5_CANONICAL_DYNAMIC_PARAMETER_CONSUMPTION_VERIFIED_BROAD_PROMPT_DENSITY_PENDING'
by_req['REQ-083']['status'] = 'PARTIAL_PHASE5_CANONICAL_DYNAMIC_TEMPORAL_PROMPT_CONTINUITY_VERIFIED_REMAINING_PHASE5_SURFACE_PROMPT_CLOSURE_PENDING'
ledger.setdefault('phase_status', {})['5'] = 'IN_PROGRESS_DYNAMIC_PROMPT_CONTINUITY_VERIFIED'
ledger.setdefault('phase_evidence', {})['5'] = {
    'status': 'IN_PROGRESS_DYNAMIC_PROMPT_CONTINUITY_VERIFIED',
    'subtask': 'CANONICAL_DYNAMIC_TEMPORAL_PROMPT_CONTINUITY',
    'requirements_advanced': ['REQ-082', 'REQ-083'],
    'focused_red': '3 failed / 1 passed; static isolation already passed',
    'focused_green': '4 passed',
    'production_commit': PROD,
    'github_actions_run': RUN,
    'proof_objects': [
        MAP,
        'tests/test_v0676_phase5_dynamic_prompt_continuity.py',
        'runtime/cbcc/model_native_prompt_contract.py',
        'runtime/cbcc/model_native_prompt_audit_fix.py',
        'runtime/cbcc/production_parameter_closure.py',
    ],
    'verified_behaviors': [
        'Phase 4 canonical motion/timing/audio concrete values are projected into the model-facing Prompt and concrete consumption audit.',
        'Prompt semantic membrane strips governance/provenance metadata from the model-facing acting plane.',
        'Legacy flat video Prompt fields remain compatible.',
        'Manual short Prompt overrides cannot be silently repaired and falsely declared parameter-closed.',
        'Unresolved dynamic Agent decisions stay missing; Prompt runtime does not invent audio/motion/timing.',
        'Static assets do not inherit dynamic Prompt requirements.',
    ],
    'cross_scope': {
        'phase4': 'all tests/test_v0676_phase4_*.py passed',
        'fresh_k01_v0672': '43-test set passed',
        'v0673_prompt_route': 'passed',
        'v0674_regression_closure': '40 passed',
    },
    'deferred_by_plan': [
        'broader commercial Prompt density across remaining surfaces',
        'REQ-084 Product Presence/Fidelity/reference Prompt consumption',
        'REQ-086 scene-derived camera/lighting/CMF Prompt consumption',
        'Fresh real K01 FULL',
        'Provider actual media / pixel-frame Review / smallest Local Revision / provenance',
    ],
    'source_truth': 'GITHUB_BRANCH_VERIFIED_PENDING_CLEAN_MAIN_CLOSURE',
}
ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# 2) Human matrix: advance only the same two requirements and the evidence boundary.
matrix_path = ROOT / 'references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md'
matrix = matrix_path.read_text(encoding='utf-8')
matrix = matrix.replace(
    'Phase 4 requirements now have committed targeted proof, while cross-phase Prompt/provider/FULL-output requirements remain explicitly pending until their later phases and real-chain evidence are complete.',
    'Phase 4 requirements have committed targeted proof. Phase 5 is now IN PROGRESS: canonical dynamic motion/timing/audio Prompt continuity has committed targeted proof, while broader Prompt density, Product Presence/Fidelity/reference Prompt consumption, scene-derived photography Prompt consumption, provider/FULL-output requirements remain pending until their later tasks and real-chain evidence are complete.'
)
matrix = matrix.replace(
    '| REQ-082 | Commercial-grade Prompt density | lossless pixel/frame/audio-changing projection | LOCKED_NOT_YET_FULLY_IMPLEMENTED |',
    '| REQ-082 | Commercial-grade Prompt density | lossless pixel/frame/audio-changing projection | PARTIAL_PHASE5_DYNAMIC_PARAMETER_CONSUMPTION_VERIFIED + BROADER_PROMPT_DENSITY_PENDING |'
)
matrix = matrix.replace(
    '| REQ-083 | Dynamic/temporal Prompt continuity | beat/motion/audio/text timing/cover continuity | LOCKED_NOT_YET_FULLY_IMPLEMENTED |',
    '| REQ-083 | Dynamic/temporal Prompt continuity | beat/motion/audio/text timing/cover continuity | PARTIAL_PHASE5_CANONICAL_DYNAMIC_CONTINUITY_VERIFIED + REMAINING_SURFACE_PROMPT_CLOSURE_PENDING |'
)
old_boundary = 'Phase 4 Art Direction / Photography / Visual Master is closed at committed-code + targeted/cross-scope proof level and is mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE4_ART_DIRECTION_PHOTOGRAPHY_VISUAL_MASTER.json`. This does **not** close Phase 5 Prompt/temporal-prompt consumption, Fresh positive K01 FULL, Provider/Result/Review/Revision, or actual-output QA. Cross-phase rows therefore remain partial where later consumer planes are required. The existing 60-row strict Consumer Map remains historical authority for its scope until the cumulative 90-row map supersedes it.'
new_boundary = 'Phase 4 Art Direction / Photography / Visual Master is closed at committed-code + targeted/cross-scope proof level and is mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE4_ART_DIRECTION_PHOTOGRAPHY_VISUAL_MASTER.json`. Phase 5 is **IN PROGRESS**: canonical dynamic motion/timing/audio Prompt continuity is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json`; broader Prompt density plus REQ-084/REQ-086 Prompt-consumption tasks remain pending. This does **not** close Fresh positive K01 FULL, Provider/Result/Review/Revision, or actual-output QA. Cross-phase rows therefore remain partial where later consumer planes are required. The existing 60-row strict Consumer Map remains historical authority for its scope until the cumulative 90-row map supersedes it.'
if old_boundary not in matrix:
    raise SystemExit('matrix evidence boundary shape changed')
matrix = matrix.replace(old_boundary, new_boundary)
for token in (
    'PARTIAL_PHASE5_DYNAMIC_PARAMETER_CONSUMPTION_VERIFIED',
    'PARTIAL_PHASE5_CANONICAL_DYNAMIC_CONTINUITY_VERIFIED',
    'REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json',
):
    if token not in matrix:
        raise SystemExit(f'matrix closure token missing: {token}')
matrix_path.write_text(matrix, encoding='utf-8')

# 3) CURRENT package checker: Phase 5 map becomes a same-source packaged authority.
checker_path = ROOT / 'scripts/check_current_release_package.py'
checker = checker_path.read_text(encoding='utf-8')
needle = "CURRENT_PHASE4_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE4_ART_DIRECTION_PHOTOGRAPHY_VISUAL_MASTER.json'\n"
insert = needle + "CURRENT_PHASE5_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json'\n"
if 'CURRENT_PHASE5_CONSUMER_MAP =' not in checker:
    if needle not in checker:
        raise SystemExit('checker Phase4 map binding shape changed')
    checker = checker.replace(needle, insert, 1)
checker = checker.replace(
    "    CURRENT_PHASE4_CONSUMER_MAP,\n)",
    "    CURRENT_PHASE4_CONSUMER_MAP,\n    CURRENT_PHASE5_CONSUMER_MAP,\n)",
    1,
)
checker = checker.replace(
    "        CURRENT_PHASE4_CONSUMER_MAP,\n        'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md',",
    "        CURRENT_PHASE4_CONSUMER_MAP,\n        CURRENT_PHASE5_CONSUMER_MAP,\n        'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md',",
    1,
)
if checker.count('CURRENT_PHASE5_CONSUMER_MAP') < 3:
    raise SystemExit('checker Phase5 map was not bound to constant + same-source + required path')
checker_path.write_text(checker, encoding='utf-8')

# 4) Checker contract test requires the new CURRENT authority explicitly.
test_path = ROOT / 'tests/test_current_release_package_checker.py'
test = test_path.read_text(encoding='utf-8')
anchor = '            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json",\n'
if 'REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json' not in test:
    if anchor not in test:
        raise SystemExit('checker test required-path shape changed')
    test = test.replace(anchor, anchor + '            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json",\n', 1)
test_path.write_text(test, encoding='utf-8')

# 5) CURRENT release workflow watches/runs the active Phase 5 proof.
wf_path = ROOT / '.github/workflows/current-release-verification.yml'
wf = wf_path.read_text(encoding='utf-8')
if "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_*.json" not in wf:
    wf = wf.replace(
        "      - 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE4_*.json'\n",
        "      - 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE4_*.json'\n      - 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_*.json'\n",
        1,
    )
if "tests/test_v0676_phase5_*.py" not in wf:
    wf = wf.replace(
        "      - 'tests/test_v0674_*.py'\n",
        "      - 'tests/test_v0674_*.py'\n      - 'tests/test_v0676_phase5_*.py'\n",
        1,
    )
phase5_step = """      - name: Verify CURRENT Phase 5 canonical dynamic Prompt continuity\n        env: {PYTHONHASHSEED: '0', PYTHONPATH: '.:runtime'}\n        run: python -m pytest -q tests/test_v0676_phase5_dynamic_prompt_continuity.py\n"""
if 'Verify CURRENT Phase 5 canonical dynamic Prompt continuity' not in wf:
    target = "      - name: Verify prior maturity and CURRENT requirement accounting\n"
    if target not in wf:
        raise SystemExit('CURRENT workflow insertion point changed')
    wf = wf.replace(target, phase5_step + target, 1)
wf_path.write_text(wf, encoding='utf-8')

# Self-check before CI.
assert by_req['REQ-084']['status'] == 'PARTIAL_PHASE4_PRODUCT_PRESENCE_FIDELITY_REFERENCE_INDEPENDENCE_VERIFIED_PHASE5_PROMPT_PENDING'
assert by_req['REQ-086']['status'] == 'PARTIAL_PHASE4_SCENE_DERIVED_PHOTOGRAPHY_LIGHTING_CMF_VERIFIED_PHASE5_PROMPT_CONSUMPTION_PENDING'
print(json.dumps({
    'phase5_status': ledger['phase_status']['5'],
    'req082': by_req['REQ-082']['status'],
    'req083': by_req['REQ-083']['status'],
    'req084_unchanged': by_req['REQ-084']['status'],
    'req086_unchanged': by_req['REQ-086']['status'],
}, ensure_ascii=False, indent=2))
