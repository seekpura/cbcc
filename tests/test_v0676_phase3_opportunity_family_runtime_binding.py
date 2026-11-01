from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).parents[1]


def load_module(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_matrix_helper_preserves_pre_asset_evaluation_and_post_asset_fulfillment():
    mod = load_module('phase3_matrix_runtime_v0676', 'runtime/cbcc/opportunity_family_authority.py')
    evaluation = mod.compile_opportunity_family_evaluation(
        {
            row['family_id']: {
                'status':'NOT_NEEDED',
                'why':'evaluated',
                'why_not':'outside current fixture scope',
            }
            for row in mod.OPPORTUNITY_FAMILY_REGISTRY
        },
        context={'delivery_mode':'FULL_PROJECT'},
    )
    fulfillment = mod.audit_opportunity_family_fulfillment(evaluation, [])
    matrix = mod.compile_asset_universe_matrix(evaluation, {'status':'OPEN_WORLD_ASSET_OPPORTUNITY_UNIVERSE'}, fulfillment)
    assert matrix['status'] == 'READY'
    assert matrix['evaluation_stage'] == 'PRE_ASSET_ARCHITECTURE_WITH_POST_ASSET_FULFILLMENT'
    assert matrix['opportunity_family_evaluation']['family_count'] == 23
    assert matrix['opportunity_family_fulfillment']['status'] == 'READY'
    assert matrix['asset_universe']['status'] == 'OPEN_WORLD_ASSET_OPPORTUNITY_UNIVERSE'


def test_phase3_runtime_closure_is_installed_after_phase2_without_replacing_mature_architecture():
    init_text = (ROOT / 'runtime/cbcc/__init__.py').read_text(encoding='utf-8')
    assert 'v0676_phase3_closure' in init_text
    assert 'apply_v0676_phase3_patches' in init_text
    assert init_text.index('apply_v0676_phase2_patches()') < init_text.index('apply_v0676_phase3_patches()')
    closure = (ROOT / 'runtime/cbcc/v0676_phase3_closure.py').read_text(encoding='utf-8')
    assert 'wrap_build_asset_architecture' in closure
    assert '_cbcc_v0676_phase3_opportunity_family' in closure


def test_compiler_materializes_pre_asset_matrix_before_build_and_finalizes_same_artifact_after_build():
    text = (ROOT / 'runtime/cbcc/compiler.py').read_text(encoding='utf-8')
    assert 'compile_opportunity_family_evaluation' in text
    assert 'compile_asset_universe_matrix' in text
    assert text.count("artifacts/asset_universe_matrix.json") >= 2
    build_at = text.index('architecture=build_asset_architecture')
    first_matrix_write = text.index("artifacts/asset_universe_matrix.json")
    second_matrix_write = text.index("artifacts/asset_universe_matrix.json", first_matrix_write + 1)
    assert first_matrix_write < build_at < second_matrix_write
    assert 'phase3_opportunity_family_evaluation' in text[first_matrix_write:build_at]
    assert 'opportunity_family_fulfillment' in text[build_at:second_matrix_write + 300]


def test_commerce_context_carries_phase3_evaluation_and_fulfillment_to_human_portfolio():
    text = (ROOT / 'runtime/cbcc/commercial_delivery_continuity.py').read_text(encoding='utf-8')
    assert "'phase3_opportunity_family_evaluation': architecture.get('phase3_opportunity_family_evaluation')" in text
    assert "'opportunity_family_fulfillment': architecture.get('opportunity_family_fulfillment')" in text


def test_human_asset_portfolio_workspace_exposes_family_decisions_and_deliberate_omissions():
    workspace = load_module('phase3_asset_portfolio_workspace_v0676', 'runtime/cbcc/asset_portfolio_workspace.py')
    portfolio = {
        'summary': {'total_asset_candidates':1, 'fixed_total_asset_limit':False},
        'phase3_opportunity_family_evaluation': {
            'status':'READY',
            'families':[
                {
                    'family_id':'F01_HERO_IDENTITY','family':'Hero / Identity','status':'NEEDED','decision_status':'READY',
                    'why':'The listing needs a truthful first-impression identity object.','why_not':None,'satisfying_objects':['ASSET-HERO-01']
                },
                {
                    'family_id':'F21_CRM_LIFECYCLE_POST_PURCHASE','family':'CRM / Lifecycle / Post-purchase','status':'NOT_NEEDED','decision_status':'READY',
                    'why':'The family was explicitly evaluated.','why_not':'Lifecycle is outside the current launch scope.','satisfying_objects':[]
                },
            ],
        },
        'opportunity_family_fulfillment': {
            'status':'READY',
            'rows':[{'family_id':'F01_HERO_IDENTITY','fulfillment_status':'FULFILLED','matched_asset_ids':['ASSET-HERO-01']}],
        },
        'assets':[{'asset_id':'ASSET-HERO-01','asset_family':'HERO','surface':'GALLERY','deployment_state':'LIVE_CANDIDATE'}],
    }
    html = workspace.render_asset_portfolio_workspace(portfolio)
    assert '机会族评估' in html
    assert 'F01_HERO_IDENTITY' in html
    assert 'Hero / Identity' in html
    assert 'NEEDED' in html
    assert 'ASSET-HERO-01' in html
    assert 'Lifecycle is outside the current launch scope.' in html
    assert 'FULFILLED' in html


def test_legacy_12_axis_family_audit_contract_remains_unchanged():
    legacy = load_module('legacy_family_audit_v0676', 'runtime/cbcc/asset_universe_family_audit.py')
    assert [x[0] for x in legacy.FAMILY_AXES] == [
        'gallery_identity','benefit_proof_detail','scenario_human_context','howto_objection_comparison',
        'rich_pdp_source','paid_media','social_seeding','creator_affiliate','video_live','store_campaign','lifecycle','test_rotation',
    ]
