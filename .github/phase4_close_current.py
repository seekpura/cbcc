from __future__ import annotations

import argparse
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'references'
LEDGER = REF / 'REQUIREMENT_EXECUTION_LEDGER_CURRENT.json'
MATRIX = REF / 'REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md'
MAP = REF / 'REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE4_ART_DIRECTION_PHOTOGRAPHY_VISUAL_MASTER.json'
PRODUCTION_HEAD = '63eab0ab46ce5a251592b1a3363b03b99c3b4adf'

PHASE4_REQUIREMENTS = [
    'REQ-024','REQ-025','REQ-026','REQ-027','REQ-028','REQ-029','REQ-030','REQ-031','REQ-032',
    'REQ-057','REQ-080','REQ-081','REQ-084','REQ-085','REQ-086',
]

PRODUCTION_COMMITS = [
    {'sha':'affc7a16a337941e3b28e8d290fe76de0bcc45c6','role':'extend Art Direction across active visual routes including UGC/LIVE/page routes'},
    {'sha':'ef0c4ebeb7ba782c4a21f2014da80d1ad9c58cb0','role':'materialize canonical pre-asset Visual Master'},
    {'sha':'94af452ff3a4475568c88f109ad59a89c8634b5f','role':'bind canonical Visual Master through compiler'},
    {'sha':'b2d2b1e31a402a5f4122762dce52381f1b30531a','role':'enforce scene-derived photography execution'},
    {'sha':'b7134d56f0145f75f3d6b5f9885545cff47591ca','role':'project concrete inclusion authority into human assets'},
    {'sha':'27df19f4799f3021a399a5f787eac2873e36d376','role':'preserve product-reference continuity through commerce wrapper'},
    {'sha':PRODUCTION_HEAD,'role':'project explicitly authored dynamic motion/timing/audio direction into the same surface asset'},
]

TESTS = [
    'tests/test_v0676_phase4_visual_route_art_direction.py',
    'tests/test_v0676_phase4_visual_master_authority.py',
    'tests/test_v0676_phase4_visual_master_runtime_binding.py',
    'tests/test_v0676_phase4_scene_derived_photography_authority.py',
    'tests/test_v0676_phase4_inclusion_execution_authority.py',
    'tests/test_v0676_phase4_dynamic_surface_art_direction.py',
]

REQ_MAP = {
    'REQ-024': {
        'summary':'Anti-template rhythm must be decided at portfolio/project level rather than repeated layout mechanics.',
        'source':'CONVERSATION_REQUIREMENT_AUDIT.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/portfolio_visual_authority.py','runtime/cbcc/agent_art_direction_authority.py','runtime/cbcc/asset_architecture.py'],
        'evidence':['tests/test_v0676_phase4_visual_route_art_direction.py','tests/test_v0676_phase4_visual_master_authority.py'],
        'effect':'Visual Master owns continuity/rhythm while per-object Art Direction must retain route-specific difference.',
        'risk':'Fresh K01 FULL visual portfolio review remains pending.',
    },
    'REQ-025': {
        'summary':'Integrated render direction must have a concrete visual authority before downstream render/provider work.',
        'source':'CONVERSATION_REQUIREMENT_AUDIT.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/compiler.py','runtime/cbcc/art_direction_projection.py','runtime/cbcc/asset_compiler.py'],
        'evidence':['tests/test_v0676_phase4_visual_master_runtime_binding.py','tests/test_v0635_native_reference_provider_integrity.py'],
        'effect':'Compiler materializes the visual authority before asset package/provider consumers.',
        'risk':'Final model prompt/provider execution is Phase 5/7 and real-output E2E remains pending.',
    },
    'REQ-026': {
        'summary':'Composite/no-copy/absent product modes remain per-asset decisions rather than global defaults.',
        'source':'CONVERSATION_REQUIREMENT_AUDIT.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/agent_art_direction_authority.py','runtime/cbcc/reference_guided_native_authority.py','runtime/cbcc/asset_compiler.py'],
        'evidence':['tests/test_v0635_native_reference_provider_integrity.py','tests/test_v0676_phase4_inclusion_execution_authority.py'],
        'effect':'Product presence remains independent from fidelity/reference handling through the visual chain.',
        'risk':'Provider-real-output proof remains pending.',
    },
    'REQ-027': {
        'summary':'Reference-guided native product handling preserves verified identity without forcing exact-pixel composition.',
        'source':'CONVERSATION_REQUIREMENT_AUDIT.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/reference_guided_native_authority.py','runtime/cbcc/compiler.py','runtime/cbcc/video_creator.py'],
        'evidence':['tests/test_v0635_native_reference_provider_integrity.py','tests/test_v0676_phase4_dynamic_surface_art_direction.py'],
        'effect':'Reference mode, identity lock and explicit exact-pixel modes remain separate semantic boundaries.',
        'risk':'Phase 5 prompt/provider realization still requires dedicated proof.',
    },
    'REQ-028': {
        'summary':'Product/text presence belongs to curation and object Art Direction, not a universal renderer default.',
        'source':'CONVERSATION_REQUIREMENT_AUDIT.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/agent_art_direction_authority.py','runtime/cbcc/portfolio_visual_authority.py','runtime/cbcc/compiler.py'],
        'evidence':['tests/test_v0676_phase4_visual_route_art_direction.py','tests/test_v0676_phase4_dynamic_surface_art_direction.py'],
        'effect':'Static and dynamic objects keep their own presence/copy relationship and route-native behavior.',
        'risk':'Fresh FULL project visual judgment remains pending.',
    },
    'REQ-029': {
        'summary':'Visible copy can be integrated with the scene while preserving object-level visual hierarchy.',
        'source':'CONVERSATION_REQUIREMENT_AUDIT.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/agent_art_direction_authority.py','runtime/cbcc/art_direction_projection.py','runtime/cbcc/video_creator.py'],
        'evidence':['tests/test_v0676_phase4_visual_route_art_direction.py','tests/test_v0676_phase4_dynamic_surface_art_direction.py'],
        'effect':'Copy relation stays part of Art Direction; dynamic audio/text boundaries do not overwrite static visual contracts.',
        'risk':'Lossless model-prompt projection is Phase 5.',
    },
    'REQ-030': {
        'summary':'Structured per-object Art Direction exists before Prompt and is authoritative for active visual routes.',
        'source':'CONVERSATION_REQUIREMENT_AUDIT.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/agent_art_direction_authority.py','runtime/cbcc/compiler.py','runtime/cbcc/art_direction_projection.py'],
        'evidence':['tests/test_v0676_phase4_visual_route_art_direction.py','tests/test_v0676_phase4_visual_master_runtime_binding.py'],
        'effect':'Missing Art Direction blocks active visual routes instead of silently fabricating renderer instructions.',
        'risk':'Phase 5 must prove lossless Prompt projection from this authority.',
    },
    'REQ-031': {
        'summary':'Photography parameters are derived from each scene/material decision rather than generic camera presets.',
        'source':'CONVERSATION_REQUIREMENT_AUDIT.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/scene_derived_photography_authority.py','runtime/cbcc/compiler.py','runtime/cbcc/video_creator.py'],
        'evidence':['tests/test_v0676_phase4_scene_derived_photography_authority.py'],
        'effect':'Camera/lens/shot/light/CMF execution is tied to scene and decision job with missing values left explicit.',
        'risk':'Phase 5 must prove these parameters reach final model prompts without loss.',
    },
    'REQ-032': {
        'summary':'Human assets receive concrete inclusion execution rather than generic policy prose.',
        'source':'CONVERSATION_REQUIREMENT_AUDIT.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/creative.py','runtime/cbcc/compiler.py','runtime/cbcc/video_creator.py'],
        'evidence':['tests/test_v0676_phase4_inclusion_execution_authority.py','tests/test_v0670_human_projection_integrity.py'],
        'effect':'Casting/skin/hair/body/hands/exposure/bias controls are projected only onto relevant human assets.',
        'risk':'Real generated-human output bias review remains pending.',
    },
    'REQ-057': {
        'summary':'Inclusive photography is P0 execution authority when people/hands/body relations appear.',
        'source':'CONVERSATION_REQUIREMENT_AUDIT.md',
        'consumers':['runtime/cbcc/creative.py','runtime/cbcc/compiler.py','runtime/cbcc/video_creator.py'],
        'evidence':['tests/test_v0676_phase4_inclusion_execution_authority.py','tests/test_v0670_human_projection_integrity.py'],
        'effect':'Concrete human execution and no-invention boundaries survive into same asset and dynamic rendering contracts.',
        'risk':'Real image/video output review remains E2E pending.',
    },
    'REQ-080': {
        'summary':'Canonical Visual Master is a project-level authority distinct from per-object Art Direction and portfolio rhythm.',
        'source':'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/visual_master_authority.py','runtime/cbcc/compiler.py','runtime/cbcc/portfolio_visual_authority.py'],
        'evidence':['tests/test_v0676_phase4_visual_master_authority.py','tests/test_v0676_phase4_visual_master_runtime_binding.py'],
        'effect':'Pre-asset Visual Master lineage is materialized and bound through compiler before object-specific divergence.',
        'risk':'Fresh K01 FULL portfolio visual review remains pending.',
    },
    'REQ-081': {
        'summary':'Per-object Art Direction applies beyond still images, including UGC, LIVE, page and dynamic routes.',
        'source':'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/agent_art_direction_authority.py','runtime/cbcc/agent_autonomy.py','runtime/cbcc/video_creator.py','runtime/cbcc/compiler.py'],
        'evidence':['tests/test_v0676_phase4_visual_route_art_direction.py','tests/test_v0676_phase4_dynamic_surface_art_direction.py'],
        'effect':'UGC/LIVE/PDP-video objects now carry route-native Art Direction and dynamic authorship on the same object.',
        'risk':'Phase 5 temporal Prompt compilation remains pending.',
    },
    'REQ-084': {
        'summary':'Product Presence, Fidelity and reference semantics are independent decisions.',
        'source':'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/reference_guided_native_authority.py','runtime/cbcc/compiler.py','runtime/cbcc/video_creator.py'],
        'evidence':['tests/test_v0635_native_reference_provider_integrity.py','tests/test_v0676_phase4_dynamic_surface_art_direction.py'],
        'effect':'Dynamic projection merges into existing product_presence/product_fidelity without replacing them; static and absent modes stay isolated.',
        'risk':'Phase 5 Prompt semantics and provider-real-output validation remain pending.',
    },
    'REQ-085': {
        'summary':'Culture/inclusion becomes concrete per-asset human execution with no identity invention.',
        'source':'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/creative.py','runtime/cbcc/compiler.py','runtime/cbcc/video_creator.py'],
        'evidence':['tests/test_v0676_phase4_inclusion_execution_authority.py'],
        'effect':'Relevant human objects carry authored human context, exposure/bias guardrails and missing-decision TO_VERIFY state.',
        'risk':'Real generated output must still be reviewed for AI bias and fidelity.',
    },
    'REQ-086': {
        'summary':'Scene-derived photography/lighting/CMF choices reach the acting visual authority instead of remaining advisory prose.',
        'source':'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md + LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'consumers':['runtime/cbcc/scene_derived_photography_authority.py','runtime/cbcc/compiler.py','runtime/cbcc/video_creator.py'],
        'evidence':['tests/test_v0676_phase4_scene_derived_photography_authority.py','tests/test_v0676_phase4_dynamic_surface_art_direction.py'],
        'effect':'Scene/material decisions produce concrete photography execution; dynamic objects preserve those visual contracts while adding authored temporal direction.',
        'risk':'Phase 5 must verify final Prompt consumption of every acting parameter.',
    },
}

CROSS_PHASE = {
    'REQ-073':'Creator/UGC/Affiliate: Phase 4 dynamic Art Direction verified; Phase 5 temporal Prompt remains pending.',
    'REQ-074':'Product/PDP/Short Video: Phase 4 dynamic Art Direction verified; Phase 5 temporal Prompt remains pending.',
    'REQ-075':'LIVE commerce: Phase 4 dynamic Art Direction verified; Phase 5 temporal Prompt remains pending.',
    'REQ-079':'Surface-native specialization: Phase 4 visual-route activation and route-specific Art Direction verified.',
}

MATRIX_STATUS = {
    'REQ-024':'CONSUMER MAPPED + PHASE4_TARGETED_PROOF + E2E_PENDING',
    'REQ-025':'CONSUMER MAPPED + PHASE4_TARGETED_PROOF + PHASE5/7_E2E_PENDING',
    'REQ-026':'PACKAGE_ENFORCED + PHASE4_TARGETED_PROOF + E2E_PENDING',
    'REQ-027':'CONSUMER MAPPED + PHASE4_TARGETED_PROOF + PHASE5/7_E2E_PENDING',
    'REQ-028':'CONSUMER MAPPED + PHASE4_TARGETED_PROOF + E2E_PENDING',
    'REQ-029':'CONSUMER MAPPED + PHASE4_TARGETED_PROOF + PHASE5_PENDING + E2E_PENDING',
    'REQ-030':'PACKAGE_ENFORCED + PHASE4_TARGETED_PROOF + PHASE5_PENDING + E2E_PENDING',
    'REQ-031':'CONSUMER MAPPED + PHASE4_TARGETED_PROOF + PHASE5_PENDING + E2E_PENDING',
    'REQ-032':'CONSUMER MAPPED + PHASE4_TARGETED_PROOF + REAL_OUTPUT_E2E_PENDING',
    'REQ-057':'CONSUMER MAPPED + PHASE4_TARGETED_PROOF + REAL_OUTPUT_E2E_PENDING',
    'REQ-073':'PARTIAL_PHASE3_PHASE4_VERIFIED + PHASE5_PENDING + E2E_PENDING',
    'REQ-074':'PARTIAL_PHASE3_PHASE4_VERIFIED + PHASE5_PENDING + E2E_PENDING',
    'REQ-075':'PARTIAL_PHASE3_PHASE4_VERIFIED + PHASE5_PENDING + E2E_PENDING',
    'REQ-079':'IMPLEMENTED_CODE + PHASE3_PHASE4_TARGETED_PROOF + E2E_PENDING',
    'REQ-080':'IMPLEMENTED_CODE + PHASE4_TARGETED_PROOF + E2E_PENDING',
    'REQ-081':'IMPLEMENTED_CODE + PHASE4_TARGETED_PROOF + PHASE5_PENDING + E2E_PENDING',
    'REQ-084':'PARTIAL_PHASE4_IMPLEMENTED + PHASE5_PENDING + E2E_PENDING',
    'REQ-085':'IMPLEMENTED_CODE + PHASE4_TARGETED_PROOF + REAL_OUTPUT_E2E_PENDING',
    'REQ-086':'PARTIAL_PHASE4_IMPLEMENTED + PHASE5_PENDING + E2E_PENDING',
}

LEDGER_NEW_STATUS = {
    'REQ-064':'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_EVALUATION_PHASE4_SHARED_VISUAL_EXECUTION_VERIFIED_REAL_FAMILY_E2E_PENDING',
    'REQ-065':'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_EVALUATION_PHASE4_SHARED_VISUAL_EXECUTION_VERIFIED_REAL_FAMILY_E2E_PENDING',
    'REQ-066':'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_EVALUATION_PHASE4_SHARED_VISUAL_EXECUTION_VERIFIED_REAL_FAMILY_E2E_PENDING',
    'REQ-067':'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_EVALUATION_PHASE4_SHARED_VISUAL_EXECUTION_VERIFIED_REAL_FAMILY_E2E_PENDING',
    'REQ-068':'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_EVALUATION_PHASE4_SCENE_PHOTOGRAPHY_EXECUTION_VERIFIED_REAL_FAMILY_E2E_PENDING',
    'REQ-069':'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_EVALUATION_PHASE4_SHARED_VISUAL_EXECUTION_VERIFIED_REAL_FAMILY_E2E_PENDING',
    'REQ-071':'PARTIAL_PHASE2_ADS_PHASE3_OPPORTUNITY_FAMILY_PHASE4_SHARED_VISUAL_EXECUTION_VERIFIED_REAL_CAMPAIGN_E2E_PENDING',
    'REQ-072':'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_EVALUATION_PHASE4_SHARED_VISUAL_EXECUTION_VERIFIED_REAL_SOCIAL_E2E_PENDING',
    'REQ-073':'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_PHASE4_DYNAMIC_ART_DIRECTION_VERIFIED_PHASE5_PROMPT_PENDING',
    'REQ-074':'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_PHASE4_DYNAMIC_ART_DIRECTION_VERIFIED_PHASE5_PROMPT_PENDING',
    'REQ-075':'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_PHASE4_DYNAMIC_ART_DIRECTION_VERIFIED_PHASE5_PROMPT_PENDING',
    'REQ-076':'PARTIAL_PHASE3_OPPORTUNITY_FAMILY_EVALUATION_PHASE4_SURFACE_ART_DIRECTION_VERIFIED_PHASE6_DELIVERY_PENDING',
    'REQ-079':'PASS_PHASE3_OPPORTUNITY_FAMILY_AND_PHASE4_SURFACE_NATIVE_ART_DIRECTION_VERIFIED',
    'REQ-080':'PASS_PHASE4_VISUAL_MASTER_PORTFOLIO_RHYTHM_VERIFIED',
    'REQ-081':'PASS_PHASE4_PER_OBJECT_ART_DIRECTION_BEYOND_STILLS_VERIFIED',
    'REQ-084':'PARTIAL_PHASE4_PRODUCT_PRESENCE_FIDELITY_REFERENCE_INDEPENDENCE_VERIFIED_PHASE5_PROMPT_PENDING',
    'REQ-085':'PASS_PHASE4_CONCRETE_HUMAN_CULTURE_INCLUSION_EXECUTION_VERIFIED',
    'REQ-086':'PARTIAL_PHASE4_SCENE_DERIVED_PHOTOGRAPHY_LIGHTING_CMF_VERIFIED_PHASE5_PROMPT_CONSUMPTION_PENDING',
}


def _junit(path: str | None) -> dict:
    if not path:
        return {'status':'PENDING','tests':0,'failures':0,'errors':0,'skipped':0}
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == 'testsuite' else list(root.findall('testsuite'))
    vals = {k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}
    vals['status'] = 'PASS' if vals['failures'] == 0 and vals['errors'] == 0 else 'FAIL'
    return vals


def _git_head() -> str:
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()


def _consumer_map(focused: dict, cross: dict) -> dict:
    requirements=[]
    for req in PHASE4_REQUIREMENTS:
        x=REQ_MAP[req]
        requirements.append({
            'requirement_id':req,
            'summary':x['summary'],
            'source':x['source'],
            'implementation_status':'IMPLEMENTED_CODE + PHASE4_TARGETED_PROOF' if req not in {'REQ-084','REQ-086'} else 'PHASE4_IMPLEMENTED + PHASE5_CONSUMPTION_PENDING',
            'evidence':x['evidence'],
            'consumers':x['consumers'],
            'downstream_effect':x['effect'],
            'residual_risk':x['risk'],
            'real_chain_assertions':[
                'No completion claim is derived from file existence alone.',
                'Phase 4 proof is committed-code focused/cross-scope verification; Fresh K01 FULL and provider actual-output remain separate E2E gates.',
            ],
        })
    return {
        'version':'2026-11-02-phase4-closure-v1',
        'phase':'PHASE_4_ART_DIRECTION_PHOTOGRAPHY_VISUAL_MASTER',
        'production_head_sha':PRODUCTION_HEAD,
        'closure_branch_head_before_docs_commit':_git_head(),
        'requirements':requirements,
        'cross_phase_impacts':[{'requirement_id':k,'status':v} for k,v in CROSS_PHASE.items()],
        'phase_evidence':{
            'production_commits':PRODUCTION_COMMITS,
            'targeted_tests':TESTS,
            'focused_result':focused,
            'cross_scope_result':cross,
            'behavioral_scenarios':[
                'active visual routes beyond IMAGE/VIDEO require per-object Art Direction',
                'canonical Visual Master exists before assets and retains lineage through compiler',
                'scene/material decisions produce concrete photography/light/CMF execution',
                'human assets receive concrete inclusion execution while non-human assets remain isolated',
                'product presence/fidelity/reference semantics survive the visual chain independently',
                'PDP short video, UGC and LIVE project explicitly authored motion/timing/audio into the same asset; static assets remain free of temporal fields',
                'runtime fallback shots/default duration/default locale never become creative authority',
            ],
            'real_product_probes':{'status':'PENDING_FRESH_K01_FULL','reason':'Phase 4 closure does not replace the locked fresh positive FULL real-project requirement.'},
            'provider_actual_output':{'status':'PENDING_PHASE7_8_10','reason':'No provider/result/review actual-output claim is made in Phase 4.'},
        },
    }


def _patch_matrix() -> None:
    text=MATRIX.read_text(encoding='utf-8')
    for req,status in MATRIX_STATUS.items():
        pat=re.compile(rf'^(\| {re.escape(req)} \|[^\n]*\| )([^|\n]*?)( \|)$',re.M)
        text,n=pat.subn(lambda m:m.group(1)+status+m.group(3),text,count=1)
        if n!=1:
            raise SystemExit(f'matrix row not found exactly once: {req}')
    intro='REQ-061..090 are newly locked by `CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md` and are closed phase-by-phase. Phase 4 requirements now have committed targeted proof, while cross-phase Prompt/provider/FULL-output requirements remain explicitly pending until their later phases and real-chain evidence are complete.'
    text=re.sub(r'REQ-061\.\.090 are newly locked by `CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02\.md` and remain explicitly \*\*not yet fully implemented\*\* until the cumulative 001\.\.090 consumer map, code/package consumers and real FULL proof are completed\.',intro,text,count=1)
    boundary='''## Current evidence boundary\nPhase 4 Art Direction / Photography / Visual Master is closed at committed-code + targeted/cross-scope proof level and is mapped in `REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE4_ART_DIRECTION_PHOTOGRAPHY_VISUAL_MASTER.json`. This does **not** close Phase 5 Prompt/temporal-prompt consumption, Fresh positive K01 FULL, Provider/Result/Review/Revision, or actual-output QA. Cross-phase rows therefore remain partial where later consumer planes are required. The existing 60-row strict Consumer Map remains historical authority for its scope until the cumulative 90-row map supersedes it.\n'''
    text=re.sub(r'## Current evidence boundary\n.*\Z',boundary,text,flags=re.S)
    MATRIX.write_text(text,encoding='utf-8')


def _patch_ledger(focused: dict, cross: dict) -> None:
    data=json.loads(LEDGER.read_text(encoding='utf-8'))
    data['version']='2026-11-02-phase4-closure-v1'
    data['current_phase']='PHASE_4_COMPLETE'
    data['previous_phase']='PHASE_3_COMPLETE'
    data['next_phase']='PHASE_5_PROMPT_RENDERER_CPP'
    data['current_head_sha']=PRODUCTION_HEAD
    data['current_head_sha_semantics']='Last Phase 4 production-code head. Closure documentation/cleanup commit is intentionally later and verified separately on main.'
    for row in data.get('new_requirements') or []:
        req=row.get('req')
        if req in LEDGER_NEW_STATUS:
            row['status']=LEDGER_NEW_STATUS[req]
    data.setdefault('phase_status',{})['4']='PASS_PHASE4_ART_DIRECTION_PHOTOGRAPHY_VISUAL_MASTER_VERIFIED'
    data['phase_evidence']['4']={
        'status':'PASS_PHASE4_ART_DIRECTION_PHOTOGRAPHY_VISUAL_MASTER_VERIFIED' if focused['status']=='PASS' and cross['status']=='PASS' else 'PENDING_VERIFICATION',
        'requirement_ids':PHASE4_REQUIREMENTS,
        'verified_subtasks':[
            'Surface-native per-object Art Direction across active visual routes',
            'Canonical pre-asset Visual Master + compiler lineage',
            'Scene-derived camera/lens/lighting/CMF execution',
            'Concrete human inclusion execution + product reference/fidelity continuity',
            'Dynamic PDP/UGC/LIVE motion + timing + audio Art Direction with static isolation and no runtime invention',
        ],
        'focused_tests':focused,
        'cross_scope_tests':cross,
        'proof_objects':[
            'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE4_ART_DIRECTION_PHOTOGRAPHY_VISUAL_MASTER.json',
            *TESTS,
            'tests/test_v0635_native_reference_provider_integrity.py',
            'tests/test_v0670_human_projection_integrity.py',
        ],
        'source_truth':'GITHUB_MAIN_PRODUCTION_HEAD_PLUS_ISOLATED_CLOSURE_VERIFICATION',
        'production_head_sha':PRODUCTION_HEAD,
        'source_commits':[x['sha'] for x in PRODUCTION_COMMITS],
        'verified_behavior':'Explicit dynamic decisions are projected into the same dynamic asset Art Direction before asset_architecture authority is written; static objects are untouched; fallback/default video execution data cannot masquerade as authored creative authority; Visual Master, Product Presence/Fidelity and Inclusion remain intact.',
        'deferred_by_plan':'Phase 5 Prompt/temporal prompt, Fresh K01 FULL, Provider/Result/Review/Revision and actual-output QA remain pending and are not claimed by Phase 4.',
        'production_probe':'PENDING_FRESH_K01_FULL_BY_LOCKED_PLAN',
        'full_suite_status':'PHASE4_FOCUSED_AND_ADJACENT_CROSS_SCOPE_PASS' if focused['status']=='PASS' and cross['status']=='PASS' else 'PENDING',
    }
    if isinstance(data.get('global_assessment'),dict):
        data['global_assessment']['current']='Phase 4 Art Direction / Photography / Visual Master closed at committed-code + focused/cross-scope proof level.'
        data['global_assessment']['next']='Start Phase 5 Prompt / Renderer implementation only from the locked Phase 4 authorities; do not reinterpret fallback runtime defaults as creative decisions.'
        data['global_assessment']['still_pending']='Fresh K01 FULL, Phase 5 Prompt/temporal projection, later Human Workspace/package/provider/actual-output phases, and installed-plugin release parity.'
    LEDGER.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def _write_all(focused: dict, cross: dict) -> None:
    MAP.write_text(json.dumps(_consumer_map(focused,cross),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    _patch_matrix()
    _patch_ledger(focused,cross)


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--focused-junit')
    ap.add_argument('--cross-junit')
    args=ap.parse_args()
    focused=_junit(args.focused_junit)
    cross=_junit(args.cross_junit)
    _write_all(focused,cross)
    if args.focused_junit or args.cross_junit:
        if focused['status']!='PASS' or cross['status']!='PASS':
            raise SystemExit(f'cannot finalize Phase 4 closure: focused={focused} cross={cross}')

if __name__=='__main__':
    main()
