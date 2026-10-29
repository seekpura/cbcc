from __future__ import annotations

import json
from pathlib import Path

from runtime.cbcc.operator_delivery_html import inject_operator_execution


def test_operator_execution_is_injected_as_primary_workspace(tmp_path:Path):
    artifacts=tmp_path/'artifacts'; artifacts.mkdir(parents=True)
    (artifacts/'operator_execution_board.json').write_text(json.dumps({
        'commercial_thesis':{'primary_conversion_proposition':'One clear reason to buy','target_user':'target shopper','operator_read':'先做主转化任务'},
        'release_status':{'state':'PRODUCTION_READY','compliance_status':'READY','asset_compile_status':'COMPILED','production_status':'NOT_REQUESTED'},
        'launch_board':[{'priority':'P1','owner':'CREATIVE','exact_action':'Generate IMG-01','target_object':'IMG-01','artifact_or_object':'asset package','completion_check':'actual-output QA pass'}],
        'listing_release':{'packages':[]},
        'asset_production_board':{'assets':[]},
        'video_production_board':{},
        'paid_test_queue':{},
        'review_revision_queue':{},
        'economics_control_panel':{},
    },ensure_ascii=False),encoding='utf-8')
    page='<html><body><main><section id="commercial-brain"><h2>Runtime Inspector</h2></section></main></body></html>'
    out=inject_operator_execution(page,tmp_path)
    assert 'id="operator-execution"' in out
    assert '运营执行台' in out
    assert '现在做什么' in out
    assert 'Generate IMG-01' in out
    assert out.index('id="operator-execution"') < out.index('id="commercial-brain"')


def test_operator_workspace_is_idempotent(tmp_path:Path):
    artifacts=tmp_path/'artifacts'; artifacts.mkdir(parents=True)
    (artifacts/'operator_execution_board.json').write_text(json.dumps({'commercial_thesis':{},'release_status':{},'launch_board':[]}),encoding='utf-8')
    page='<html><body><main></main></body></html>'
    once=inject_operator_execution(page,tmp_path)
    twice=inject_operator_execution(once,tmp_path)
    assert twice.count('id="operator-execution"')==1
