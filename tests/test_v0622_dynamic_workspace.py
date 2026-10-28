from __future__ import annotations

from pathlib import Path
import json

from cbcc.workspace_autonomy import build_workspace_route_plan, relevant_asset_view_keys
from cbcc.delivery_html import build_delivery_html


def test_primary_navigation_only_contains_business_objects_that_exist():
    plan=build_workspace_route_plan(
        availability={'assets':True,'prompts':True,'archive':True,'market':False,'content':False,'visual':False},
        agent_next_action={},
    )
    routes=[row['route'] for row in plan['primary_routes']]
    assert routes == ['overview','assets','prompts']
    assert [row['route'] for row in plan['secondary_routes']] == ['archive']
    assert plan['fixed_route_count'] is None
    assert plan['fixed_command_count'] is None


def test_agent_frontier_promotes_real_next_action_without_fixed_command_quota():
    plan=build_workspace_route_plan(
        availability={'risk':True,'assets':True,'visual':True,'listing':False},
        agent_next_action={'frontier':[
            {'action':'RESOLVE_COMPLIANCE_BOUNDARY','reason':'A claim boundary blocks publication.'},
            {'action':'AUTHOR_OR_SELECT_CREATIVE_DIRECTION','reason':'Creative direction is unresolved.'},
        ]},
    )
    assert plan['commands'][0]['route']=='risk'
    assert plan['commands'][0]['source']=='AGENT_FRONTIER'
    assert plan['commands'][1]['route']=='visual'
    assert any(row['route']=='assets' for row in plan['commands'])


def test_asset_views_are_independent_lenses_and_empty_photography_is_removed():
    asset={
        'views':[
            {'key':'overview','html':'<div>decision</div>'},
            {'key':'photo','html':'<div class="empty">暂无已确认内容。</div>'},
            {'key':'visual','html':'<div>visual</div>'},
        ],
        'prompt_cn':'do it',
        'source_files':['a.json'],
    }
    assert relevant_asset_view_keys(asset)==['overview','visual','prompt','qa']


def test_agent_can_override_asset_view_order_without_runtime_expansion():
    asset={
        'views':[{'key':'overview','html':'A'},{'key':'visual','html':'B'},{'key':'copy','html':'C'}],
        'agent_view_order':['copy','overview'],
    }
    assert relevant_asset_view_keys(asset)==['copy','overview','visual']


def test_minimal_human_delivery_does_not_render_empty_fixed_workspace_routes(tmp_path:Path):
    package=tmp_path/'delivery'; package.mkdir()
    (package/'HUMAN_DELIVERY.json').write_text(json.dumps({
        'delivery_language':{'locale':'zh-CN'},
        'target':{'market':'Malaysia','platform':'TikTok Shop','locale':'ms-MY','delivery_locale':'zh-CN'},
        'product':{'product_name':'示例商品'},
        'readiness':{'status':'READY','pending_count':0},
        'copy_center':[], 'localized_copy':[], 'risks_and_holds':[],
    },ensure_ascii=False),encoding='utf-8')
    output=build_delivery_html(package)
    html=output.read_text(encoding='utf-8')
    assert 'data-route="overview"' in html
    assert 'href="#market"' not in html
    assert 'href="#content"' not in html
    assert 'href="#visual"' not in html
    assert 'href="#prompts"' not in html
    assert '工作台只显示当前项目真实存在的业务对象' in html


def test_asset_workspace_text_does_not_claim_a_mandatory_pipeline():
    source=Path('runtime/cbcc/delivery_html.py').read_text(encoding='utf-8')
    assert '生产顺序：先核对 Design Card、画面、摄影 / CMF 与文案约束，再执行 Prompt' not in source
    assert '无固定先后顺序' in source
    assert '不预设 Hook / CTA / 固定传播阶段' in source
