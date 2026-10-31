from pathlib import Path
import json
import re

from cbcc.commercial_continuity_authority import _commercial_prompt_lines
from cbcc.full_delivery_depth_v3 import _card_issues
from cbcc.full_delivery_materialization import compile_export_asset_universe
from cbcc.html_asset_package_parity import audit_html_asset_package_parity
from cbcc.listing_markdown_parity_v0671 import audit_listing_markdown_canonical_parity
from cbcc.long_requirement_full_audit import wrap_audit_host_full_package
from cbcc.canonical_materialization_package_audit import wrap_audit_host_full_package as wrap_canonical_materialization


CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]')


def _write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def test_en_commerce_context_never_dumps_chinese_lineage_into_en_prompt():
    lineage = {
        'race': [{
            'stage': 'COMMUNICATION',
            'objective': '按平台原生方式传播，覆盖达人/UGC/广告/私域并完成语言本地化',
            'key_actions': 'Listing/PDP + Creator/UGC + Paid + Live/Social/CRM',
            'platform': 'tiktok_shop',
            'kpi': 'reach/CTR/engagement/CVR',
            'why': '同一价值在不同平台和人群语境中需要原生表达',
        }],
        'positioning': {'primary_conversion_proposition': '轻盈日常凝胶护理'},
    }
    text = '\n'.join(_commercial_prompt_lines(lineage, 'EN'))
    assert not CJK.search(text), text
    assert 'COMMUNICATION' in text
    assert 'tiktok_shop' in text
    assert 'reach/CTR/engagement/CVR' in text


def test_design_card_audit_consumes_named_nested_design_card_objects():
    card = {
        'commerce_task': {
            'strategic_job': 'resolve identity',
            'consumer_question': 'what is it?',
            'incremental_information': 'adds identity evidence',
            'business_hypothesis': 'clarity improves decision',
            'success_metric': 'thumbnail recognition',
        },
        'visual_carrier': 'LOCKED_SOURCE_HERO',
        'product_presence': {'planning_state': 'REQUIRED', 'presence_why': 'identity job'},
        'subject_system': {'subject_type': 'PRODUCT_OR_OBJECT'},
        'subject_action_environment_props': {
            'subject': 'product', 'environment': 'warm ivory field', 'props': ['neutral plinth'],
        },
        'information_design': {'proof_plane': 'workbook truth only'},
        'composition_camera': {'composition_grammar': 'asymmetric hero'},
        'lighting_material_cmf': {'cmf': {'material': 'matte paper', 'palette_hex': ['#fff']}},
        'agent_art_direction': {'portfolio_rhythm_delta': 'open with identity hero'},
    }
    assert _card_issues(card, 'AST-1') == []
    del card['commerce_task']['success_metric']
    issues = _card_issues(card, 'AST-1')
    assert any(x['code'] == 'ASSET_DESIGN_CARD_DECISION_MISSING' and x['decision'] == 'measurement' for x in issues)


def test_export_asset_universe_refreshes_presence_audit_after_authored_art_direction(tmp_path: Path):
    project = tmp_path / 'project'
    assets = [
        {'asset_id': 'A1', 'asset_type': 'IMAGE', 'deployment_state': 'LIVE_CANDIDATE',
         'product_presence': {'planning_state': 'REQUIRED', 'presence_why': 'identity hero'}},
        {'asset_id': 'A2', 'asset_type': 'IMAGE', 'deployment_state': 'PDP_CONTENT',
         'asset_art_direction': {'product_presence': {'planning_state': 'FORBIDDEN', 'presence_why': 'evidence-only asset'}}},
    ]
    _write_json(project / 'artifacts/asset_architecture.json', {
        'assets': assets,
        'asset_universe': {'product_presence_portfolio_audit': {'status': 'INCOMPLETE', 'total_assets': 2, 'structured_presence_decisions': 0}},
    })
    universe = compile_export_asset_universe(project)
    pa = universe['product_presence_portfolio_audit']
    assert pa['status'] == 'PASS'
    assert pa['structured_presence_decisions'] == 2
    assert pa['visible_or_optional_count'] == 1
    assert pa['absent_or_forbidden_count'] == 1


def test_html_asset_parity_reads_current_static_canonical_payload_without_const_data(tmp_path: Path):
    package = tmp_path
    aid = 'AST-1'
    asset = package / 'asset_packages' / aid
    asset.mkdir(parents=True)
    (asset / '05_prompt_CN.txt').write_text('中文 prompt', encoding='utf-8')
    (asset / '06_prompt_EN.txt').write_text('English prompt', encoding='utf-8')
    _write_json(asset / '12_design_card.json', {'asset_id': aid, 'visual_carrier': 'HERO'})
    payload = {'assets': [{'asset_id': aid, 'prompt_cn': '中文 prompt', 'prompt_en': 'English prompt', 'card': {'asset_id': aid, 'visual_carrier': 'HERO'}}]}
    _write_json(package / 'CANONICAL_HUMAN_DATA.json', payload)
    (package / 'index.html').write_text('<body><!-- CBCC_CANONICAL_STATIC_PROJECTION_V0672 --></body>', encoding='utf-8')
    issues = audit_html_asset_package_parity(package)
    assert not any(x['code'] == 'HTML_ASSET_DATA_MISSING' for x in issues), issues
    assert issues == []


def test_listing_markdown_parity_treats_markdown_escaped_pipe_as_same_value(tmp_path: Path):
    _write_json(tmp_path / 'HUMAN_DELIVERY.json', {
        'task_scope': {'listing_active': True},
        'copy_center': [{'field': 'title', 'value': 'A | B', 'delivery_translation': '甲｜乙'}],
        'localized_copy': [{'locale': 'en-MY', 'field': 'title', 'value': 'A | B', 'delivery_translation': '甲｜乙'}],
    })
    (tmp_path / '01_LISTING_UPLOAD_READY.md').write_text('## Title\nA \\| B\n\n甲｜乙\n', encoding='utf-8')
    assert audit_listing_markdown_canonical_parity(tmp_path) == []


def test_current_cbcc_saas_routes_are_not_misclassified_as_fixed_capability_report(tmp_path: Path):
    (tmp_path / 'index.html').write_text(
        '<body data-workspace-shell="cbcc-commercial-v1">' + ''.join(
            f'<section data-route="{r}"></section>' for r in ('product','market','strategy','listing','visual','assets','sources')
        ) + '<section data-route="asset/AST-1"></section></body>', encoding='utf-8')
    result = wrap_audit_host_full_package(lambda p: {'status':'PASS','issues':[]})(tmp_path)
    assert not any(x['code'] == 'FIXED_CAPABILITY_ROUTE_TAXONOMY' for x in result['issues']), result['issues']


def test_provider_media_remain_e2e_pending_when_production_run_not_requested(tmp_path: Path):
    asset = tmp_path / 'asset_packages' / 'AST-1'
    asset.mkdir(parents=True)
    (asset / '05_prompt_CN.txt').write_text('prompt', encoding='utf-8')
    _write_json(tmp_path / 'supporting_analysis/execution_contract.json', {'production_run': {'status': 'NOT_REQUESTED', 'assets': []}})
    result = wrap_audit_host_full_package(lambda p: {'status':'PASS','issues':[]})(tmp_path)
    codes = {x['code'] for x in result['issues']}
    assert 'FULL_PROVIDER_RESULT_MISSING' not in codes
    assert 'FULL_ACTUAL_GENERATED_OUTPUT_MISSING' not in codes
    assert result.get('provider_media_e2e', {}).get('status') == 'E2E_PENDING_NOT_REQUESTED'


def test_v0670_inner_human_projection_does_not_fail_after_current_static_projection_exists(tmp_path: Path):
    (tmp_path / 'index.html').write_text('<body><!-- CBCC_CANONICAL_STATIC_PROJECTION_V0672 --></body>', encoding='utf-8')
    _write_json(tmp_path / 'CANONICAL_HUMAN_DATA.json', {'assets': [], 'listing': {}})
    result = wrap_canonical_materialization(lambda p: {'status':'PASS','issues':[]})(tmp_path)
    assert not any(x['code'] == 'CANONICAL_HUMAN_POSITIVE_PROJECTION_FAILED' for x in result['issues']), result['issues']


def test_current_static_projection_is_final_html_owner_after_legacy_compatibility_audit(tmp_path: Path):
    from cbcc.canonical_full_package_audit_v0671 import wrap_audit_host_full_package as wrap_current_full
    (tmp_path / 'strategy').mkdir()
    (tmp_path / 'supporting_analysis').mkdir()
    (tmp_path / 'index.html').write_text(
        '<html><body><main>' + ''.join(f'<section class="page" data-route="{r}"></section>' for r in ('overview','listing','strategy','product','visual','content','prompts','sources')) + '</main></body></html>',
        encoding='utf-8',
    )
    _write_json(tmp_path / 'HUMAN_DELIVERY.json', {'task_scope': {'listing_active': False}, 'copy_center': [], 'localized_copy': []})
    _write_json(tmp_path / 'strategy/strategy_authority.json', {'sections': {}})
    _write_json(tmp_path / 'ASSET_UNIVERSE.json', {'total_asset_candidates': 0})

    def legacy_compat(package: Path):
        # Simulate a legacy inner compatibility layer that rewrites the HTML snapshot after current projection.
        (package / 'index.html').write_text('<html><body><main>legacy snapshot</main></body></html>', encoding='utf-8')
        return {'status': 'INCOMPLETE', 'issues': [
            {'code': 'CANONICAL_HUMAN_POSITIVE_PROJECTION_FAILED'},
            {'code': 'WORKSPACE_SEARCH_SCOPE_INCOMPLETE'},
            {'code': 'HTML_ASSET_DATA_MISSING'},
        ]}

    result = wrap_current_full(legacy_compat)(tmp_path)
    final_html = (tmp_path / 'index.html').read_text(encoding='utf-8')
    codes = {row.get('code') for row in result.get('issues') or []}
    assert result['status'] == 'PASS', result.get('issues')
    assert 'CBCC_CANONICAL_STATIC_PROJECTION_V0672' in final_html
    assert 'cbcc-canonical-payload-v0672' in final_html
    assert not ({'CANONICAL_HUMAN_POSITIVE_PROJECTION_FAILED','WORKSPACE_SEARCH_SCOPE_INCOMPLETE','HTML_ASSET_DATA_MISSING'} & codes)
