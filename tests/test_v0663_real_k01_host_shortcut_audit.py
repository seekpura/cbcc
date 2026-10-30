from __future__ import annotations

import json
from pathlib import Path

from runtime.cbcc.long_requirement_full_audit import wrap_audit_host_full_package


def _base_audit(_package: Path):
    return {'status': 'PASS', 'issues': []}


def _write_old_k01_shape(root: Path) -> None:
    assets = []
    for i in range(15):
        aid = f'G{i+1:02d}'
        assets.append({
            'id': aid,
            'family': 'GALLERY' if i < 9 else 'PAID',
            'surface': 'GALLERY' if i < 9 else 'AD',
            'activation': 'LIVE',
            'job': 'conversion job',
            'barrier': 'shopper barrier',
            'belief': 'target belief',
            'carrier': 'warm-white editorial field',
            'presence': 'product anchor',
            'copy': {'bm': 'KAWAL MINYAK. KEKALKAN HIDRASI.'},
            'prompt_cn': 'legacy prompt',
            'prompt_en': 'legacy prompt',
            'notes': 'post composite product and exact text',
        })
        d = root / 'assets' / aid
        d.mkdir(parents=True, exist_ok=True)
        (d / '01_design_card.md').write_text('thin card', encoding='utf-8')
        prompt = '不要生成文字或数字。不要生成商品，只预留商品区。' if i < 13 else '背景场景。'
        (d / '05_prompt_CN.txt').write_text(prompt, encoding='utf-8')
        (d / '06_prompt_EN.txt').write_text('Do not generate text or numbers. Do not generate product.' if i < 13 else 'background scene', encoding='utf-8')
        (d / '07_visible_copy.txt').write_text('KAWAL MINYAK. KEKALKAN HIDRASI.', encoding='utf-8')
        (d / '08_production_notes.txt').write_text('商品与精确文字后期合成。', encoding='utf-8')

    project = {
        'product': {'name': 'KIYUU K01'},
        'claims': [],
        'competitors': [],
        'listing': {},
        'visual': {
            'fidelity': '商品真实图层锁定；生成模型只负责背景/场景/人物/道具；商品与精确文字走后期合成。'
        },
        'strategy': {},
        'pricing': {
            'economics': 'MISSING_INPUT: product cost / fulfillment / platform fee / affiliate / return reserve',
            'recommended_test': 'RM22.90–26.90',
        },
        'assets': assets,
        'sources': [],
    }
    (root / 'data').mkdir(parents=True, exist_ok=True)
    (root / 'data' / 'project.json').write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding='utf-8')
    (root / 'sources').mkdir(parents=True, exist_ok=True)
    (root / 'sources' / 'K01_all_views_source.jpg').write_bytes(b'input-reference-only')

    labels = [
        ('product', '产品事实'), ('market', '马来市场'), ('strategy', '成交策略'), ('listing', '上架文案'),
        ('visual', '视觉系统'), ('assets', '资产宇宙'), ('compliance', '合规证据'), ('sources', '研究来源'),
    ]
    nav = ''.join(f'<button data-route="{route}">{label}</button>' for route, label in labels)
    (root / 'index.html').write_text(f'<html><body><nav>{nav}</nav></body></html>', encoding='utf-8')


def test_real_k01_shortcut_shape_is_rejected_by_all_structural_regression_guards(tmp_path: Path):
    _write_old_k01_shape(tmp_path)
    audit = wrap_audit_host_full_package(_base_audit)
    result = audit(tmp_path)
    codes = {row['code'] for row in result['issues']}
    expected = {
        'MATURE_ASSET_PACKAGE_INCOMPLETE',
        'STRUCTURED_ASSET_ART_DIRECTION_MISSING',
        'PRODUCT_PRESENCE_DECISION_NOT_STRUCTURED',
        'PRODUCT_EVERYWHERE_PORTFOLIO_REVIEW_REQUIRED',
        'ASSET_OPPORTUNITY_SWEEP_MISSING',
        'GLOBAL_POST_COMPOSITE_POLICY',
        'GLOBAL_NO_VISIBLE_COPY_PATTERN',
        'GLOBAL_NO_PRODUCT_GENERATION_PATTERN',
        'ACTUAL_GENERATED_OUTPUT_MISSING',
        'PROVIDER_RESULT_MISSING',
        'ACTUAL_OUTPUT_REVIEW_MISSING',
        'LOCAL_REVISION_LINEAGE_MISSING',
        'INFORMATION_ASSUMPTION_DECISION_LOG_MISSING',
        'PRICING_RECOMMENDATION_AHEAD_OF_ECONOMICS',
        'HOST_SHORTCUT_ASSET_PACKAGE_FORBIDDEN',
        'FIXED_CAPABILITY_MENU_SHELL',
        'FIXED_CAPABILITY_ROUTE_TAXONOMY',
    }
    assert expected <= codes
    assert result['status'] == 'INCOMPLETE'


def test_production_ready_mature_asset_requires_all_four_production_objects(tmp_path: Path):
    asset_id = 'A01'
    d = tmp_path / 'asset_packages' / asset_id
    d.mkdir(parents=True)
    (d / '00_asset_manifest.yaml').write_text('asset_id: A01\nasset_art_direction:\n  visual_carrier: proof field\n', encoding='utf-8')
    (d / '05_prompt_CN.txt').write_text('完整中文提示词', encoding='utf-8')
    # Deliberately omit EN prompt + machine Design Card + Visible Copy + Production Notes.
    (tmp_path / 'ASSET_UNIVERSE.json').write_text(json.dumps({
        'assets': [{'asset_id': asset_id, 'deployment_state': 'LIVE_CANDIDATE'}],
        'opportunity_family_audit': [
            {'family_key': key, 'status': 'NOT_NEEDED', 'why': 'fixture'}
            for key in (
                'gallery_identity','benefit_proof_detail','scenario_human_context','howto_objection_comparison',
                'rich_pdp_source','paid_media','social_seeding','creator_affiliate','video_live',
                'store_campaign','lifecycle','test_rotation'
            )
        ],
        'product_presence_portfolio_audit': {'total_assets': 1, 'structured_presence_decisions': 1},
    }), encoding='utf-8')

    audit = wrap_audit_host_full_package(_base_audit)
    result = audit(tmp_path)
    rows = [x for x in result['issues'] if x['code'] == 'PRODUCTION_OBJECTS_INCOMPLETE']
    assert rows
    assert set(rows[0]['missing']) >= {
        '06_prompt_EN.txt', '12_design_card.json', '14_visible_copy_block.json', '15_production_assembly_notes.json'
    }
