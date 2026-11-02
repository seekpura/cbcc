from __future__ import annotations

import json
from pathlib import Path

MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PROMPT_DENSITY.json'
PRODUCTION = 'b1a8571a6008345808c892a10975ca40188efed3'
RUN = 41388592372


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{path}: expected one occurrence, found {count}: {old[:120]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


# Machine execution ledger.
ledger_path = Path('references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json')
ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
req082 = next(row for row in ledger['new_requirements'] if row.get('req') == 'REQ-082')
req082['status'] = 'PASS_PHASE5_COMMERCIAL_GRADE_PROMPT_DENSITY_AND_CONCRETE_PARAMETER_CONSUMPTION_TARGETED_VERIFIED_E2E_PENDING'
phase5 = ledger['phase_execution']['5']
phase5['status'] = 'IN_PROGRESS_DYNAMIC_PRODUCT_FIDELITY_SCENE_PHOTOGRAPHY_AND_BROAD_PROMPT_DENSITY_VERIFIED'
phase5['subtask'] = 'COMMERCIAL_GRADE_PROMPT_DENSITY_AND_CONCRETE_PARAMETER_CONSUMPTION'
proofs = phase5.setdefault('proof_objects', [])
for rel in (
    MAP,
    'tests/test_v0678_phase5_req082_broad_prompt_density.py',
    'tests/test_v0678_phase5_req082_static_ad_prompt_consumption.py',
    'tests/test_v0678_phase5_req082_integrated_render_language_purity.py',
    'runtime/cbcc/integrated_render_route_authority.py',
):
    if rel not in proofs:
        proofs.append(rel)
behaviors = phase5.setdefault('verified_behaviors', [])
for behavior in (
    'Rich static Art Direction geometry, scale/depth, focal path, material response, human/culture/inclusion semantics and locked visible copy survive into the final acting Prompt as concrete semantic values.',
    'A manually supplied short product/background/camera/light Prompt cannot bypass broad-density consumption auditing; unresolved concrete decisions keep the Prompt INCOMPLETE.',
    'Integrated typography selects already-authored semantics per Prompt language and never dumps locale mappings/Python dict syntax or relabels Chinese-only typography as English.',
):
    if behavior not in behaviors:
        behaviors.append(behavior)
phase5['deferred_by_plan'] = [
    'REQ-083 remaining surface-specific and temporal Prompt continuity',
    'Fresh real K01 FULL',
    'Provider actual media / pixel-frame Review / smallest Local Revision / provenance',
]
phase5['remaining'] = [
    'REQ-083 remaining surface-specific and temporal Prompt continuity',
    'Fresh real K01 FULL',
    'Provider actual output / Review / Local Revision / provenance',
]
verified = phase5.setdefault('verified_subtasks', [])
subtask = 'Commercial-grade broad Prompt density, concrete static parameter consumption and bilingual integrated typography semantic purity'
if subtask not in verified:
    verified.append(subtask)
phase5['commercial_prompt_density'] = {
    'requirement': 'REQ-082',
    'status': 'PASS_TARGETED_E2E_PENDING',
    'production_commit': PRODUCTION,
    'broad_density_tests': '2/2 passed',
    'static_art_direction_consumption_tests': '2/2 passed',
    'integrated_typography_semantic_purity_tests': '3/3 passed',
    'phase5_adjacent_tests': '7/7 passed',
    'complete_v067_cross_scope': '341/341 passed',
    'workflow_run': RUN,
    'consumer_map': MAP,
    'verified_boundary': 'Broad static Prompt density and concrete consumption are targeted-verified through the acting Prompt plane, including bilingual integrated typography purity. REQ-083 remaining temporal/surface continuity, Fresh K01 FULL and actual Provider output remain pending.',
}
phase5['source_truth'] = 'GITHUB_SOURCE_AND_CURRENT_PACKAGE_TARGETED_VERIFIED'
commits = phase5.setdefault('source_commits', [])
if PRODUCTION not in commits:
    commits.append(PRODUCTION)
ledger['version'] = '2026-11-02-phase5-in-progress-v2'
ledger['current_phase'] = 'PHASE_5_IN_PROGRESS'
ledger['previous_phase'] = 'PHASE_4_COMPLETE'
ledger['next_phase'] = 'PHASE_5_REMAINING_REQ_083_PROMPT_CONTINUITY'
ledger['current_head_sha'] = PRODUCTION
ledger['current_head_sha_semantics'] = 'Latest Phase 5 production-code head proven by focused, adjacent and complete v067 cross-scope verification; durable closure documentation may be committed later.'
ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


# Human-readable matrix: advance only what this targeted proof actually establishes.
matrix = 'references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md'
replace_once(
    matrix,
    'Phase 5 is now IN PROGRESS: canonical dynamic motion/timing/audio Prompt continuity, Product Presence/Fidelity/reference independence, and scene-derived photography/lighting/CMF Prompt consumption have committed targeted proof, while broader Prompt density, remaining surface Prompt closure, provider/FULL-output requirements remain pending until their later tasks and real-chain evidence are complete.',
    'Phase 5 is now IN PROGRESS: canonical dynamic motion/timing/audio Prompt continuity, Product Presence/Fidelity/reference independence, scene-derived photography/lighting/CMF Prompt consumption, and broader commercial Prompt density/concrete parameter consumption have committed targeted proof, while REQ-083 remaining surface/temporal Prompt closure and provider/FULL-output requirements remain pending until their later tasks and real-chain evidence are complete.',
)
replace_once(
    matrix,
    '| REQ-029 | Visible Copy may be integrated | integrated render + Prompt compiler + asset compiler | CONSUMER MAPPED + PHASE4_TARGETED_PROOF + PHASE5_PENDING + E2E_PENDING |',
    '| REQ-029 | Visible Copy may be integrated | integrated render + Prompt compiler + asset compiler | CONSUMER MAPPED + PHASE4_TARGETED_PROOF + PHASE5_PROMPT_TARGETED_PROOF + E2E_PENDING |',
)
replace_once(
    matrix,
    '| REQ-034 | Prompt not camera/style-only | model-native contract/audit + compiler | CONSUMER MAPPED + E2E_PENDING |',
    '| REQ-034 | Prompt not camera/style-only | model-native contract/audit + compiler | CONSUMER MAPPED + PHASE5_PROMPT_DENSITY_TARGETED_PROOF + E2E_PENDING |',
)
replace_once(
    matrix,
    '| REQ-035 | Concrete parameter consumption | parameter closure + prompt contract + continuity audit | CONSUMER MAPPED + PHASE5_SCENE_PHOTO_PARAMETER_TARGETED_PROOF + BROADER_PARAMETER_CONSUMPTION_PENDING + E2E_PENDING |',
    '| REQ-035 | Concrete parameter consumption | parameter closure + prompt contract + continuity audit | CONSUMER MAPPED + PHASE5_DYNAMIC_SCENE_STATIC_BROAD_PARAMETER_TARGETED_PROOF + E2E_PENDING |',
)
replace_once(
    matrix,
    '| REQ-082 | Commercial-grade Prompt density | lossless pixel/frame/audio-changing projection | PARTIAL_PHASE5_DYNAMIC_PARAMETER_CONSUMPTION_VERIFIED + BROADER_PROMPT_DENSITY_PENDING |',
    '| REQ-082 | Commercial-grade Prompt density | lossless pixel/frame/audio-changing projection | PHASE5_COMMERCIAL_PROMPT_DENSITY_TARGETED_PROOF + E2E_PENDING |',
)
replace_once(
    matrix,
    'scene-derived camera/lighting/CMF Prompt consumption is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json`; broader Prompt density and remaining surface Prompt closure remain pending.',
    'scene-derived camera/lighting/CMF Prompt consumption is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json`; broader commercial Prompt density/concrete parameter consumption is verified and mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PROMPT_DENSITY.json`; REQ-083 remaining surface/temporal Prompt closure remains pending.',
)


# CURRENT release package must carry the new source-of-truth map byte-for-byte.
checker = 'scripts/check_current_release_package.py'
replace_once(
    checker,
    "CURRENT_PHASE5_SCENE_PHOTOGRAPHY_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json'\n",
    "CURRENT_PHASE5_SCENE_PHOTOGRAPHY_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json'\nCURRENT_PHASE5_PROMPT_DENSITY_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PROMPT_DENSITY.json'\n",
)
replace_once(
    checker,
    '    CURRENT_PHASE5_SCENE_PHOTOGRAPHY_CONSUMER_MAP,\n)\n',
    '    CURRENT_PHASE5_SCENE_PHOTOGRAPHY_CONSUMER_MAP,\n    CURRENT_PHASE5_PROMPT_DENSITY_CONSUMER_MAP,\n)\n',
)
replace_once(
    checker,
    '        CURRENT_PHASE5_SCENE_PHOTOGRAPHY_CONSUMER_MAP,\n        \'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md\',',
    '        CURRENT_PHASE5_SCENE_PHOTOGRAPHY_CONSUMER_MAP,\n        CURRENT_PHASE5_PROMPT_DENSITY_CONSUMER_MAP,\n        \'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md\',',
)

checker_test = 'tests/test_current_release_package_checker.py'
replace_once(
    checker_test,
    '            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json",\n            "references/CURRENT_CANONICAL_SKILL_BUILD.md",',
    '            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_SCENE_PHOTOGRAPHY_PROMPT.json",\n            "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE5_PROMPT_DENSITY.json",\n            "references/CURRENT_CANONICAL_SKILL_BUILD.md",',
)

print('REQ-082 durable closure patch applied')
