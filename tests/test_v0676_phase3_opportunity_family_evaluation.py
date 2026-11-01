from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).parents[1]
MODULE = ROOT / 'runtime/cbcc/opportunity_family_authority.py'
spec = importlib.util.spec_from_file_location('phase3_opportunity_family_authority_v0676', MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


LOCKED_FAMILIES = [
    'F01_HERO_IDENTITY',
    'F02_SELLING_POINT',
    'F03_LIFESTYLE_SCENARIO',
    'F04_HUMAN_INTERACTION',
    'F05_NEGATIVE_COUNTEREXAMPLE',
    'F06_EXPECTATION_MANAGEMENT',
    'F07_BRAND_IP_MEMORY',
    'F08_PACKAGING_UNBOXING_CONTENTS',
    'F09_SIZE_COMPATIBILITY_COMPARISON',
    'F10_INGREDIENT_FORMULA_MATERIAL_TEXTURE_DETAIL_MACRO',
    'F11_HOW_TO_ROUTINE_STEP',
    'F12_FAQ_OBJECTION',
    'F13_COMPARISON',
    'F14_A_PLUS_PDP_LONGFORM',
    'F15_PAID_MEDIA_PERFORMANCE_CREATIVE',
    'F16_SOCIAL_SEEDING_ORGANIC',
    'F17_CREATOR_UGC_AFFILIATE',
    'F18_PRODUCT_PDP_SHORT_VIDEO',
    'F19_LIVE_COMMERCE',
    'F20_STORE_BANNER_LANDING_CAMPAIGN_SEASONAL',
    'F21_CRM_LIFECYCLE_POST_PURCHASE',
    'F22_TEST_ROTATION_AB_MULTIVARIATE',
    'F23_SOURCE_DOCUMENT_SYSTEM_INFORMATION',
]


def complete_decisions():
    rows = {}
    for row in mod.OPPORTUNITY_FAMILY_REGISTRY:
        fid = row['family_id']
        rows[fid] = {
            'status': 'NOT_NEEDED',
            'why': f'{fid} was evaluated against the current commerce scope.',
            'why_not': f'{fid} is deliberately outside this fixture scope.',
        }
    rows['F01_HERO_IDENTITY'] = {
        'status': 'NEEDED',
        'why': 'The listing needs a truthful first-impression identity object.',
        'satisfying_objects': ['ASSET-HERO-01'],
    }
    rows['F02_SELLING_POINT'] = {
        'status': 'NEEDED',
        'why': 'The same hero object can carry a source-bound primary selling point without creating a quota.',
        'satisfying_objects': ['ASSET-HERO-01'],
    }
    return rows


def test_registry_matches_locked_23_families_in_order():
    assert [x['family_id'] for x in mod.OPPORTUNITY_FAMILY_REGISTRY] == LOCKED_FAMILIES
    assert len(mod.OPPORTUNITY_FAMILY_REGISTRY) == 23


def test_missing_decisions_never_make_a_family_disappear_or_auto_mark_not_needed():
    out = mod.compile_opportunity_family_evaluation({}, context={'delivery_mode': 'FULL_PROJECT'})
    assert len(out['families']) == 23
    assert [x['family_id'] for x in out['families']] == LOCKED_FAMILIES
    assert out['status'] == 'TO_VERIFY'
    assert all(x['status'] == 'TO_VERIFY' for x in out['families'])
    assert any(x['code'] == 'PHASE3_OPPORTUNITY_FAMILY_DECISION_REQUIRED_V0676' for x in out['issues'])


def test_needed_and_not_needed_are_explicit_reasoned_pre_asset_decisions():
    out = mod.compile_opportunity_family_evaluation(complete_decisions(), context={'delivery_mode': 'FULL_PROJECT'})
    assert out['status'] == 'READY'
    hero = out['families'][0]
    assert hero['status'] == 'NEEDED'
    assert hero['needed'] is True
    assert hero['why']
    assert hero['satisfying_objects'] == ['ASSET-HERO-01']
    lifecycle = next(x for x in out['families'] if x['family_id'] == 'F21_CRM_LIFECYCLE_POST_PURCHASE')
    assert lifecycle['status'] == 'NOT_NEEDED'
    assert lifecycle['needed'] is False
    assert lifecycle['why_not']


def test_needed_requires_planned_satisfying_object_and_not_needed_requires_why_not():
    decisions = complete_decisions()
    decisions['F03_LIFESTYLE_SCENARIO'] = {'status': 'NEEDED', 'why': 'Scenario is relevant but no object has been planned yet.'}
    decisions['F21_CRM_LIFECYCLE_POST_PURCHASE'] = {'status': 'NOT_NEEDED', 'why': 'Evaluated.'}
    out = mod.compile_opportunity_family_evaluation(decisions, context={'delivery_mode': 'FULL_PROJECT'})
    by_id = {x['family_id']: x for x in out['families']}
    assert by_id['F03_LIFESTYLE_SCENARIO']['decision_status'] == 'TO_VERIFY'
    assert by_id['F21_CRM_LIFECYCLE_POST_PURCHASE']['decision_status'] == 'TO_VERIFY'
    codes = {x['code'] for x in out['issues']}
    assert 'PHASE3_NEEDED_FAMILY_SATISFIER_REQUIRED_V0676' in codes
    assert 'PHASE3_NOT_NEEDED_REASON_REQUIRED_V0676' in codes


def test_one_planned_object_may_satisfy_multiple_families_without_quota_semantics():
    out = mod.compile_opportunity_family_evaluation(complete_decisions(), context={'delivery_mode': 'FULL_PROJECT'})
    needed = [x for x in out['families'] if x['status'] == 'NEEDED']
    assert [x['family_id'] for x in needed] == ['F01_HERO_IDENTITY', 'F02_SELLING_POINT']
    assert all(x['satisfying_objects'] == ['ASSET-HERO-01'] for x in needed)
    assert out['fixed_asset_quota_per_family'] is False
    assert out['one_family_one_asset_required'] is False


def test_post_asset_fulfillment_fails_closed_when_needed_object_is_absent():
    evaluation = mod.compile_opportunity_family_evaluation(complete_decisions(), context={'delivery_mode': 'FULL_PROJECT'})
    ok = mod.audit_opportunity_family_fulfillment(evaluation, [{'asset_id': 'ASSET-HERO-01'}])
    assert ok['status'] == 'READY'
    assert ok['needed_family_count'] == 2
    assert ok['fulfilled_needed_family_count'] == 2
    missing = mod.audit_opportunity_family_fulfillment(evaluation, [{'asset_id': 'ASSET-OTHER-01'}])
    assert missing['status'] == 'TO_VERIFY'
    assert set(missing['unfulfilled_family_ids']) == {'F01_HERO_IDENTITY', 'F02_SELLING_POINT'}


def test_asset_architecture_wrapper_places_evaluation_in_target_before_base_builder_runs():
    observed = {}

    def base(project_id, target, questions, content_objects, asset_jobs=None, decision_context=None, category_family='GENERAL_COMMERCE'):
        observed['evaluation'] = target.get('phase3_opportunity_family_evaluation')
        return {'status': 'DYNAMIC_ASSET_ARCHITECTURE', 'assets': [{'asset_id': 'ASSET-HERO-01'}]}

    wrapped = mod.wrap_build_asset_architecture(base)
    out = wrapped(
        'P1',
        {'opportunity_family_decisions': complete_decisions(), 'delivery_mode': 'FULL_PROJECT'},
        [],
        [],
    )
    assert observed['evaluation']['status'] == 'READY'
    assert observed['evaluation']['evaluation_stage'] == 'PRE_ASSET_ARCHITECTURE'
    assert out['phase3_opportunity_family_evaluation']['status'] == 'READY'
    assert out['opportunity_family_fulfillment']['status'] == 'READY'
