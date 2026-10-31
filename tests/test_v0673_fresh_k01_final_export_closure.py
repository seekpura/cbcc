from __future__ import annotations

from pathlib import Path
import json

import cbcc
from cbcc import full_delivery_depth_v3 as full_depth
from cbcc import asset_universe_authority
from cbcc.commercial_continuity_authority import _commercial_prompt_lines
from cbcc.listing_markdown_parity_v0671 import audit_listing_markdown_canonical_parity
from cbcc.human_projection_integrity import audit_human_projection_html
from cbcc.html_asset_package_parity import audit_html_asset_package_parity


def _current_card():
    return {
        'commerce_task': {'strategic_job': 'Resolve the shopper decision', 'success_metric': 'PDP CVR'},
        'visual_carrier': 'EDITORIAL_EVIDENCE',
        'product_presence': {'planning_state': 'REQUIRED', 'presence_why': 'Identity is needed here.'},
        'subject_system': {'subject': 'KIYUU gel'},
        'subject_action_environment_props': {'environment': 'warm ivory studio', 'props': ['verified carton']},
        'information_design': {'proof_plane': 'formula structure'},
        'composition_camera': {'composition_grammar': 'asymmetric editorial split'},
        'lighting_material_cmf': {'cmf': {'material': 'warm ivory matte'}},
        'agent_art_direction': {'portfolio_rhythm_delta': 'hero → evidence'},
    }


def test_en_commerce_context_keeps_authored_english_and_drops_cjk_without_translation():
    lineage = {
        'positioning': {'primary_conversion_proposition': 'Lightweight oil-balancing hydration'},
        'audience_culture': {
            'segments': [
                {'name': 'Oily-skin shoppers', 'why': 'Need lightweight hydration'},
                {'name': '马来西亚油皮消费者', 'why': '需要轻盈补水'},
            ],
            'visual_implications': ['natural skin texture', '避免刻板族裔符号'],
        },
        'race': [
            {'stage': 'COMMUNICATION', 'objective': 'Explain routine use'},
            {'stage': '传播', 'objective': '按平台原生方式传播'},
        ],
    }
    text = '\n'.join(_commercial_prompt_lines(lineage, 'EN'))
    assert 'Lightweight oil-balancing hydration' in text
    assert 'Oily-skin shoppers' in text
    assert 'Explain routine use' in text
    assert '马来西亚油皮消费者' not in text
    assert '传播' not in text
    assert not any('\u3400' <= ch <= '\u9fff' for ch in text)


def test_current_nested_design_card_satisfies_semantic_decision_audit():
    assert full_depth._card_issues(_current_card(), 'AST-1') == []


def _planning_package(tmp_path: Path, *, execution_requested: bool = False) -> Path:
    asset = tmp_path / 'asset_packages' / 'AST-1'
    asset.mkdir(parents=True)
    (asset / '05_prompt_CN.txt').write_text('CN prompt', encoding='utf-8')
    (asset / '06_prompt_EN.txt').write_text('EN prompt', encoding='utf-8')
    (asset / '12_design_card.json').write_text(json.dumps(_current_card(), ensure_ascii=False), encoding='utf-8')
    (tmp_path / 'ASSET_UNIVERSE.json').write_text(json.dumps({
        'assets': [{
            'asset_id': 'AST-1', 'deployment_state': 'ACTIVE',
            'product_presence': {'planning_state': 'REQUIRED', 'presence_why': 'Identity is needed here.'},
        }],
        'product_presence_portfolio_audit': {'total_assets': 1, 'structured_presence_decisions': 1},
        'opportunity_family_audit': [],
    }, ensure_ascii=False), encoding='utf-8')
    support = tmp_path / 'supporting_analysis'
    support.mkdir()
    (support / 'evidence.json').write_text(json.dumps({'provider_media_status': 'E2E_PENDING'}), encoding='utf-8')
    if execution_requested:
        (support / 'production_run.json').write_text(json.dumps({'status': 'EXECUTION_REQUESTED'}), encoding='utf-8')
    return tmp_path


def test_planning_only_full_keeps_provider_media_e2e_pending_without_false_blocker(tmp_path: Path):
    codes = {x.get('code') for x in full_depth.audit_host_full_package(_planning_package(tmp_path)).get('issues', [])}
    assert 'FULL_PROVIDER_RESULT_MISSING' not in codes
    assert 'FULL_ACTUAL_GENERATED_OUTPUT_MISSING' not in codes


def test_provider_execution_request_still_requires_real_provider_media(tmp_path: Path):
    codes = {x.get('code') for x in full_depth.audit_host_full_package(_planning_package(tmp_path, execution_requested=True)).get('issues', [])}
    assert 'FULL_PROVIDER_RESULT_MISSING' in codes
    assert 'FULL_ACTUAL_GENERATED_OUTPUT_MISSING' in codes


def test_routed_business_workspace_is_not_fixed_taxonomy_by_route_names_alone(tmp_path: Path):
    (tmp_path / 'index.html').write_text(
        '<main data-workspace-shell="cbcc-commercial-v1">' +
        ''.join(f'<section data-route="{x}"></section>' for x in ['product','market','strategy','listing','visual','assets','sources']) +
        '<div>asset/G01</div></main>', encoding='utf-8')
    result = full_depth.audit_host_full_package(tmp_path)
    assert not any(x.get('code') == 'FIXED_CAPABILITY_ROUTE_TAXONOMY' for x in result.get('issues', []))


def test_asset_universe_presence_audit_uses_compiled_current_assets():
    out = asset_universe_authority.compile_asset_universe([
        {
            'asset_id': 'AST-1', 'asset_type': 'IMAGE', 'surface': 'GALLERY', 'family': 'LISTING',
            'product_presence': {'planning_state': 'REQUIRED', 'presence_why': 'Identity is needed here.'},
        }
    ], {})
    audit = out['product_presence_portfolio_audit']
    assert audit['total_assets'] == 1
    assert audit['structured_presence_decisions'] == 1
    assert audit['status'] == 'PASS'


def test_listing_parity_treats_markdown_escaped_pipe_as_same_text(tmp_path: Path):
    center = {
        'task_scope': {'listing_active': True},
        'copy_center': [{
            'field': 'title',
            'value': 'KIYUU Gel 30g | Niacinamide + Salicylic Acid',
            'delivery_translation': 'KIYUU 凝胶 30g｜烟酰胺+水杨酸',
        }],
        'localized_copy': [],
    }
    (tmp_path / 'HUMAN_DELIVERY.json').write_text(json.dumps(center, ensure_ascii=False), encoding='utf-8')
    (tmp_path / '01_LISTING_UPLOAD_READY.md').write_text(
        'KIYUU Gel 30g \\| Niacinamide + Salicylic Acid\nKIYUU 凝胶 30g｜烟酰胺+水杨酸', encoding='utf-8')
    assert audit_listing_markdown_canonical_parity(tmp_path) == []


def test_v0672_static_human_workspace_passes_current_human_integrity_audit():
    html = '''
    CBCC_CANONICAL_STATIC_PROJECTION_V0672
    <div>逐资产 00–15 完整生产对象</div>
    <script>
    window.CBCC_GLOBAL_SEARCH_INDEX_V0672=[];
    document.addEventListener('click',e=>{const b=e.target.closest('.cbcc-copy-v0672');navigator.clipboard.writeText('x')});
    </script>
    '''
    assert audit_human_projection_html(html) == []


def test_html_asset_parity_accepts_current_canonical_human_data_file(tmp_path: Path):
    (tmp_path / 'index.html').write_text('CBCC_CANONICAL_STATIC_PROJECTION_V0672', encoding='utf-8')
    asset = tmp_path / 'asset_packages' / 'AST-1'
    asset.mkdir(parents=True)
    (asset / '05_prompt_CN.txt').write_text('CN', encoding='utf-8')
    (asset / '06_prompt_EN.txt').write_text('EN', encoding='utf-8')
    card = {'asset_id': 'AST-1'}
    (asset / '12_design_card.json').write_text(json.dumps(card), encoding='utf-8')
    (tmp_path / 'CANONICAL_HUMAN_DATA.json').write_text(json.dumps({
        'assets': [{'asset_id': 'AST-1', 'prompt_cn': 'CN', 'prompt_en': 'EN', 'card': card}]
    }), encoding='utf-8')
    assert audit_html_asset_package_parity(tmp_path) == []
