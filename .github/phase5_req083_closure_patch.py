from __future__ import annotations

import json
from pathlib import Path

MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_TEMPORAL_PROMPT_CONTINUITY.json'
PRODUCTION = '09514f90db88591cdb0aa51528d97767cb80784c'
RUN = 41389518562
PHASE5_STATUS = 'PASS_PHASE5_COMMERCIAL_PROMPT_COMPILER_PARAMETER_CONSUMPTION_VERIFIED'


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{path}: expected one occurrence, found {count}: {old[:140]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


ledger_path = Path('references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json')
ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
rows = {row.get('req'): row for row in ledger['new_requirements']}
rows['REQ-083']['status'] = 'PASS_PHASE5_DYNAMIC_TEMPORAL_PROMPT_PRODUCTION_CONTINUITY_TARGETED_VERIFIED_E2E_PENDING'
for req in ('REQ-073', 'REQ-074', 'REQ-075'):
    rows[req]['status'] = 'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_PHASE4_DYNAMIC_ART_DIRECTION_PHASE5_TEMPORAL_PROMPT_TARGETED_VERIFIED_REAL_OUTPUT_E2E_PENDING'
ledger['phase_status']['5'] = PHASE5_STATUS
phase5 = ledger['phase_evidence']['5']
phase5['status'] = PHASE5_STATUS
phase5['subtask'] = 'DYNAMIC_TEMPORAL_SURFACE_PROMPT_AND_PRODUCTION_CONTINUITY'
for rel in (
    MAP,
    'tests/test_v0679_phase5_req083_temporal_surface_continuity.py',
    'runtime/cbcc/video_creator.py',
):
    if rel not in phase5.setdefault('proof_objects', []):
        phase5['proof_objects'].append(rel)
for behavior in (
    'Explicit subject motion, camera motion, transitions, product identity continuity, first-frame logic and cover logic survive video-job projection into canonical asset Art Direction motion authority.',
    'Explicit text timing survives into canonical timing authority; explicit VO/subtitle roles survive into canonical audio authority.',
    'The same concrete temporal decisions survive into final acting Model Prompt and Production Parameter Closure for PDP video, UGC/Creator and LIVE surfaces.',
    'Runtime fallback shots/default locale/default duration remain non-authoritative execution conveniences and are never promoted into Agent Art Direction.',
):
    if behavior not in phase5.setdefault('verified_behaviors', []):
        phase5['verified_behaviors'].append(behavior)
subtask = 'Dynamic/temporal surface continuity across PDP Video, UGC/Creator and LIVE through canonical Art Direction, acting Prompt and Production Closure'
if subtask not in phase5.setdefault('verified_subtasks', []):
    phase5['verified_subtasks'].append(subtask)
phase5['temporal_prompt_continuity'] = {
    'requirement': 'REQ-083',
    'status': 'PASS_TARGETED_E2E_PENDING',
    'production_commit': PRODUCTION,
    'focused_tests': '3/3 passed',
    'phase4_dynamic_compatibility': '4/4 passed',
    'prior_phase5_tests': '18/18 passed',
    'complete_v067_cross_scope': '344/344 passed',
    'workflow_run': RUN,
    'consumer_map': MAP,
    'surfaces': ['PDP_VIDEO', 'UGC_BRIEF', 'LIVE'],
    'verified_boundary': 'Explicit Agent-authored temporal values are losslessly preserved through canonical motion/timing/audio, final acting Prompt and Production Closure. This is not a universal fixed-template requirement and does not claim actual Provider media.',
}
phase5['deferred_by_plan'] = [
    'Phase 6 JSON/MD/HTML same-source projection',
    'Phase 7 FULL materialization/package continuity',
    'Phase 10 Fresh real K01 FULL',
    'Phase 11 installed-plugin readback and Provider actual media / Review / Local Revision / provenance',
]
phase5['remaining'] = []
phase5['remaining_phase5'] = 'NONE — locked Phase 5 Prompt compiler/parameter-consumption acceptance is targeted-verified at source and CURRENT-package level; later real-output and projection phases remain separate.'
phase5['source_truth'] = 'GITHUB_SOURCE_AND_CURRENT_PACKAGE_TARGETED_VERIFIED'
if PRODUCTION not in phase5.setdefault('source_commits', []):
    phase5['source_commits'].append(PRODUCTION)
ledger['version'] = '2026-11-02-phase5-complete-v1'
ledger['current_phase'] = 'PHASE_5_COMPLETE'
ledger['previous_phase'] = 'PHASE_4_COMPLETE'
ledger['next_phase'] = 'PHASE_6_JSON_MD_HTML_SAME_SOURCE_PROJECTION'
ledger['current_head_sha'] = PRODUCTION
ledger['current_head_sha_semantics'] = 'Latest Phase 5 production-code head proven by focused, adjacent and complete v067 cross-scope verification; durable closure documentation may be committed later.'
ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


matrix = 'references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md'
replace_once(
    matrix,
    'Phase 5 is now IN PROGRESS: canonical dynamic motion/timing/audio Prompt continuity, Product Presence/Fidelity/reference independence, scene-derived photography/lighting/CMF Prompt consumption, and broader commercial Prompt density/concrete parameter consumption have committed targeted proof, while REQ-083 remaining surface/temporal Prompt closure and provider/FULL-output requirements remain pending until their later tasks and real-chain evidence are complete.',
    'Phase 5 is COMPLETE at committed targeted source/CURRENT-package proof level: canonical dynamic motion/timing/audio, Product Presence/Fidelity/reference independence, scene-derived photography/lighting/CMF consumption, broad commercial Prompt density/concrete parameter consumption, and full explicit temporal/surface continuity all have proof. Fresh K01 FULL, Provider actual-output QA, installed-plugin readback, and later JSON/MD/HTML/FULL materialization phases remain separate and are not implied by this Phase 5 closure.',
)
replace_once(
    matrix,
    '| REQ-073 | Creator/UGC/Affiliate | creator performance/script/product handling/affiliate handoff | PARTIAL_PHASE3_PHASE4_VERIFIED + PHASE5_PENDING + E2E_PENDING |',
    '| REQ-073 | Creator/UGC/Affiliate | creator performance/script/product handling/affiliate handoff | PARTIAL_PHASE3_PHASE4_VERIFIED + PHASE5_TEMPORAL_PROMPT_TARGETED_PROOF + REAL_OUTPUT_E2E_PENDING |',
)
replace_once(
    matrix,
    '| REQ-074 | Product/PDP/Short Video | time-based commercial argument | PARTIAL_PHASE3_PHASE4_VERIFIED + PHASE5_PENDING + E2E_PENDING |',
    '| REQ-074 | Product/PDP/Short Video | time-based commercial argument | PARTIAL_PHASE3_PHASE4_VERIFIED + PHASE5_TEMPORAL_PROMPT_TARGETED_PROOF + REAL_OUTPUT_E2E_PENDING |',
)
replace_once(
    matrix,
    '| REQ-075 | LIVE commerce | host/demo/objection/offer/Q&A loop | PARTIAL_PHASE3_PHASE4_VERIFIED + PHASE5_PENDING + E2E_PENDING |',
    '| REQ-075 | LIVE commerce | host/demo/objection/offer/Q&A loop | PARTIAL_PHASE3_PHASE4_VERIFIED + PHASE5_TEMPORAL_PROMPT_TARGETED_PROOF + REAL_OUTPUT_E2E_PENDING |',
)
replace_once(
    matrix,
    '| REQ-083 | Dynamic/temporal Prompt continuity | beat/motion/audio/text timing/cover continuity | PARTIAL_PHASE5_CANONICAL_DYNAMIC_CONTINUITY_VERIFIED + REMAINING_SURFACE_PROMPT_CLOSURE_PENDING |',
    '| REQ-083 | Dynamic/temporal Prompt continuity | beat/motion/audio/text timing/cover continuity | PHASE5_DYNAMIC_TEMPORAL_PROMPT_PRODUCTION_TARGETED_PROOF + REAL_OUTPUT_E2E_PENDING |',
)
replace_once(
    matrix,
    'Phase 5 is **IN PROGRESS**: canonical dynamic motion/timing/audio Prompt continuity is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json`; Product Presence/Fidelity/reference independence is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json`; scene-derived camera/lighting/CMF Prompt consumption is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json`; broader commercial Prompt density/concrete parameter consumption is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PROMPT_DENSITY.json`; REQ-083 remaining surface/temporal Prompt closure remains pending.',
    'Phase 5 is **COMPLETE at targeted source/CURRENT-package proof level**: canonical dynamic motion/timing/audio Prompt continuity is mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_DYNAMIC_PROMPT_CONTINUITY.json`; Product Presence/Fidelity/reference independence in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PRODUCT_FIDELITY_REFERENCE.json`; scene-derived camera/lighting/CMF Prompt consumption in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json`; broad commercial Prompt density/concrete parameter consumption in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PROMPT_DENSITY.json`; and full explicit dynamic/temporal surface continuity in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_TEMPORAL_PROMPT_CONTINUITY.json`.',
)


checker = 'scripts/check_current_release_package.py'
replace_once(
    checker,
    "CURRENT_PHASE5_PROMPT_DENSITY_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PROMPT_DENSITY.json'\n",
    "CURRENT_PHASE5_PROMPT_DENSITY_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PROMPT_DENSITY.json'\nCURRENT_PHASE5_TEMPORAL_PROMPT_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_TEMPORAL_PROMPT_CONTINUITY.json'\n",
)
replace_once(
    checker,
    '    CURRENT_PHASE5_PROMPT_DENSITY_CONSUMER_MAP,\n)\n',
    '    CURRENT_PHASE5_PROMPT_DENSITY_CONSUMER_MAP,\n    CURRENT_PHASE5_TEMPORAL_PROMPT_CONSUMER_MAP,\n)\n',
)
replace_once(
    checker,
    '        CURRENT_PHASE5_PROMPT_DENSITY_CONSUMER_MAP,\n        \'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md\',',
    '        CURRENT_PHASE5_PROMPT_DENSITY_CONSUMER_MAP,\n        CURRENT_PHASE5_TEMPORAL_PROMPT_CONSUMER_MAP,\n        \'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md\',',
)

checker_test = 'tests/test_current_release_package_checker.py'
replace_once(
    checker_test,
    '            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PROMPT_DENSITY.json",\n            "references/CURRENT_CANONICAL_SKILL_BUILD.md",',
    '            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PROMPT_DENSITY.json",\n            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_TEMPORAL_PROMPT_CONTINUITY.json",\n            "references/CURRENT_CANONICAL_SKILL_BUILD.md",',
)

print('REQ-083 durable closure patch applied')
