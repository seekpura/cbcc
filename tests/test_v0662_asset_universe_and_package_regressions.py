from __future__ import annotations

import json
from pathlib import Path

from runtime.cbcc.asset_universe_authority import compile_asset_universe
from runtime.cbcc.asset_universe_family_audit import wrap_compile_asset_universe
from runtime.cbcc.long_requirement_full_audit import wrap_audit_host_full_package


def test_open_world_family_sweep_never_silently_omits_relevant_axes():
    base = wrap_compile_asset_universe(compile_asset_universe)
    assets = [
        {
            'asset_id': 'H01', 'surface': 'GALLERY', 'family': 'GALLERY', 'decision_intent': 'IDENTIFY',
            'deployment_state': 'LIVE_CANDIDATE',
            'product_presence': {'planning_state': 'HERO_REQUIRED', 'presence_why': 'identity job'},
        },
        {
            'asset_id': 'C01', 'surface': 'CREATOR', 'family': 'CREATOR_AFFILIATE', 'decision_intent': 'USAGE',
            'deployment_state': 'CREATOR',
            'product_presence': {'planning_state': 'SUPPORTING', 'presence_why': 'real-use handling proof'},
        },
    ]
    target = {
        'asset_family_decisions': {
            'lifecycle': {'status': 'NOT_NEEDED', 'why': 'launch-stage project; no post-purchase program in current scope'},
            'store_campaign': {'status': 'MISSING_INPUT', 'why': 'store campaign calendar not supplied'},
        }
    }
    universe = base(assets, target)
    audit = universe['opportunity_family_audit']
    assert {row['family_key'] for row in audit} == {
        'gallery_identity', 'benefit_proof_detail', 'scenario_human_context', 'howto_objection_comparison',
        'rich_pdp_source', 'paid_media', 'social_seeding', 'creator_affiliate', 'video_live',
        'store_campaign', 'lifecycle', 'test_rotation'
    }
    assert next(x for x in audit if x['family_key'] == 'gallery_identity')['status'] == 'COVERED'
    assert next(x for x in audit if x['family_key'] == 'lifecycle')['status'] == 'NOT_NEEDED'
    assert next(x for x in audit if x['family_key'] == 'store_campaign')['status'] == 'MISSING_INPUT'
    assert all(row.get('why') for row in audit)


def test_product_presence_is_structured_per_asset_not_global_default():
    base = wrap_compile_asset_universe(compile_asset_universe)
    assets = [
        {
            'asset_id': 'H01', 'surface': 'GALLERY', 'family': 'GALLERY',
            'product_presence': {'planning_state': 'HERO_REQUIRED', 'presence_why': 'identity recognition'},
        },
        {
            'asset_id': 'I01', 'surface': 'PDP', 'family': 'RICH_CONTENT',
            'product_presence': {'planning_state': 'FORBIDDEN', 'presence_why': 'information-only category insight is stronger without another packshot'},
        },
    ]
    universe = base(assets, {})
    presence = universe['product_presence_portfolio_audit']
    assert presence['structured_presence_decisions'] == 2
    assert presence['visible_or_optional_count'] == 1
    assert presence['absent_or_forbidden_count'] == 1
    assert presence['all_visible_review_required'] is False


def _base_package_audit(_package: Path):
    return {'status': 'PASS', 'issues': []}


def _write_asset_package(root: Path, asset_id: str, *, copy_route: str, presence: str, fidelity: str, prompt: str):
    d = root / 'asset_packages' / asset_id
    d.mkdir(parents=True, exist_ok=True)
    (d / '00_asset_manifest.yaml').write_text(
        'asset_id: ' + asset_id + '\nasset_art_direction:\n  visual_carrier: editorial field\n', encoding='utf-8'
    )
    (d / '05_prompt_CN.txt').write_text(prompt, encoding='utf-8')
    (d / '06_prompt_EN.txt').write_text('provider-readable execution prompt', encoding='utf-8')
    (d / '12_design_card.json').write_text(json.dumps({
        'information_design': {
            'copy_render_route': copy_route,
            'locked_visible_copy': {'target_copy': 'KAWAL MINYAK. KEKALKAN HIDRASI.'},
        },
        'product_presence': {'planning_state': presence},
        'product_identity': {'product_fidelity': fidelity},
    }, ensure_ascii=False), encoding='utf-8')


def test_full_package_rejects_legacy_no_text_and_no_product_prompt_when_route_is_integrated(tmp_path: Path):
    _write_asset_package(
        tmp_path, 'A01',
        copy_route='MODEL_RENDER_INTEGRATED', presence='REQUIRED', fidelity='REFERENCE_GUIDED_NATIVE_LOCK',
        prompt='不要生成文字或数字。不要生成商品，只预留商品区。',
    )
    (tmp_path / 'ASSET_UNIVERSE.json').write_text(json.dumps({
        'assets': [{'asset_id': 'A01', 'deployment_state': 'LIVE_CANDIDATE'}],
        'opportunity_family_audit': [
            {'family_key': key, 'status': 'NOT_NEEDED', 'why': 'fixture'}
            for key in (
                'gallery_identity', 'benefit_proof_detail', 'scenario_human_context', 'howto_objection_comparison',
                'rich_pdp_source', 'paid_media', 'social_seeding', 'creator_affiliate', 'video_live',
                'store_campaign', 'lifecycle', 'test_rotation'
            )
        ],
        'product_presence_portfolio_audit': {
            'total_assets': 1, 'structured_presence_decisions': 1,
        },
    }), encoding='utf-8')
    audited = wrap_audit_host_full_package(_base_package_audit)
    result = audited(tmp_path)
    codes = {row['code'] for row in result['issues']}
    assert 'PROMPT_COPY_ROUTE_CONTRADICTION' in codes
    assert 'PROMPT_PRODUCT_ROUTE_CONTRADICTION' in codes


def test_full_package_does_not_flag_explicit_exact_pixel_post_composite_route(tmp_path: Path):
    _write_asset_package(
        tmp_path, 'A02',
        copy_route='POST_COMPOSITE', presence='REQUIRED', fidelity='EXACT_PIXEL_COMPOSITE',
        prompt='不要生成文字。不要生成商品；精确商品像素层后期合成。',
    )
    (tmp_path / 'ASSET_UNIVERSE.json').write_text(json.dumps({
        'assets': [{'asset_id': 'A02', 'deployment_state': 'LIVE_CANDIDATE'}],
        'opportunity_family_audit': [
            {'family_key': key, 'status': 'NOT_NEEDED', 'why': 'fixture'}
            for key in (
                'gallery_identity', 'benefit_proof_detail', 'scenario_human_context', 'howto_objection_comparison',
                'rich_pdp_source', 'paid_media', 'social_seeding', 'creator_affiliate', 'video_live',
                'store_campaign', 'lifecycle', 'test_rotation'
            )
        ],
        'product_presence_portfolio_audit': {'total_assets': 1, 'structured_presence_decisions': 1},
    }), encoding='utf-8')
    audited = wrap_audit_host_full_package(_base_package_audit)
    result = audited(tmp_path)
    codes = {row['code'] for row in result['issues']}
    assert 'PROMPT_COPY_ROUTE_CONTRADICTION' not in codes
    assert 'PROMPT_PRODUCT_ROUTE_CONTRADICTION' not in codes
