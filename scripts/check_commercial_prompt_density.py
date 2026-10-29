#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]

# This is intentionally not a blanket "longer is better" rule. These files are first-class
# commercial authoring authorities. Adapter/checkpoint prompts may remain concise. The floors
# prevent a senior-operator playbook from silently regressing back into a few-line policy stub.
CONTRACTS={
    'prompts/commercial_visual_generation_authority.md':(8500,['Commerce objective','Integrated visible copy','Output QA','Repair routing']),
    'prompts/commercial_video_generation_authority.md':(6000,['Narrative carriers','Shot object','Output QA','Variant / creative-testing system']),
    'prompts/advertising_diagnosis.md':(5000,['Causal diagnosis order','Creative decomposition','Operator action queue','Creative test queue']),
    'prompts/feedback_revision_routing.md':(5000,['Responsibility taxonomy','Theme clustering','Revision routing','Pre/post revision verification']),
    'prompts/final_copy_local_authoring.md':(4500,['Before writing each field','Search intent coverage','Required output per field','Hard blockers']),
    'prompts/economics_offer_strategy.md':(4000,['Price architecture','Promotion decision','Paid acquisition economics','Operator decision queue']),
    'prompts/measurement_iteration.md':(3500,['Measurement object','Experiment design','Creative learning memory','Stop rules']),
    'prompts/seven_agent_orchestration.md':(3500,['Relevance-Driven','Dynamic handoffs','Operator closure','Hard blockers']),
    'prompts/operator_execution_density.md':(3500,['Launch Board','Asset Production Board','Release Status','Density check']),
    'prompts/host_copy_authoring_orchestration.md':(2200,['Authoring logic','Required return object','Hard-input rule']),
    'prompts/copy_iteration_loop.md':(1800,['Diagnose before revising','Revision rules','Stop rule']),
    'prompts/surface_production_contracts.md':(2500,['Surface adaptation logic','Required contract','QA']),
    'prompts/cmf_material_lighting.md':(3000,['Material diagnosis','Light program','Prelight','QA']),
    'prompts/production_contract_provider_binding.md':(2500,['Provider adaptation','Integrated generation rule','Result handoff','Revision integrity']),
    'prompts/asset_photography_causal_reasoning.md':(3000,['Start from the commerce job','Camera reasoning','Lighting reasoning','Anti-template rule']),
    'prompts/causal_experiment_design.md':(3000,['Decision-first framing','Design readiness order','Creative experiments','Decision states']),
    'prompts/advanced_causal_design.md':(3000,['Cluster-randomized designs','Geo / market experiments','Sequential / repeated monitoring','Decision output']),
}

FORBIDDEN_ACTIVE_RUNTIME_PHRASES={
    'runtime/cbcc/prompt_compiler.py':[
        'Exact approved text is composed deterministically after generation.',
        'do not ask the image model to retype packaging or final marketing copy',
    ],
    'runtime/cbcc/model_native_prompt_contract.py':[
        "return 'UNRESOLVED_AGENT_DECISION'",
    ],
}


def main()->int:
    failures=[]
    for rel,(minimum,required) in CONTRACTS.items():
        path=ROOT/rel
        if not path.exists():
            failures.append(f'{rel}: missing')
            continue
        text=path.read_text(encoding='utf-8')
        size=len(text.encode('utf-8'))
        if size < minimum:
            failures.append(f'{rel}: {size} bytes < commercial floor {minimum}')
        for phrase in required:
            if phrase.lower() not in text.lower():
                failures.append(f'{rel}: required commercial concept missing: {phrase}')
    for rel,phrases in FORBIDDEN_ACTIVE_RUNTIME_PHRASES.items():
        path=ROOT/rel
        if not path.exists():
            failures.append(f'{rel}: missing active runtime file')
            continue
        text=path.read_text(encoding='utf-8')
        for phrase in phrases:
            if phrase.lower() in text.lower():
                failures.append(f'{rel}: legacy global restriction leaked into active runtime: {phrase}')
    if failures:
        print('COMMERCIAL PROMPT DENSITY FAIL')
        for row in failures: print('-',row)
        return 1
    print(f'COMMERCIAL PROMPT DENSITY PASS: {len(CONTRACTS)} first-class/senior authoring authorities protected')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
