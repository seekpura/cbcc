from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))

from cbcc.delivery_html import _asset_page


def _asset(**overrides):
    base={
        'id':'LST-03',
        'title':'配方平衡证据',
        'original_title':'FORMULA BUILT FOR BALANCE',
        'summary':'TikTok Shop Malaysia · 配方平衡 · 购买判断',
        'surface':'PDP gallery',
        'intent':'DECISION_SUPPORT',
        'asset_type':'IMAGE',
        'prompt_cn':'中文执行提示词：保持真实商品像素，执行构图和灯光合同。',
        'prompt_en':'English execution prompt: preserve product fidelity and execute the visual contract.',
        'source_files':['asset_packages/LST-03/12_design_card.json','asset_packages/LST-03/13_prompt_contract.json'],
        'views':[
            {'key':'overview','title':'资产概览','html':'<div>Design Card 概览</div>'},
            {'key':'strategy','title':'策划与决策','html':'<div>购买障碍与目标信念</div>'},
            {'key':'visual','title':'画面与版式','html':'<div>主体 / 动作 / 构图 / Surface</div>'},
            {'key':'photo','title':'摄影 / CMF','html':'<div>50mm · key light · CCT</div>'},
            {'key':'copy','title':'文案','html':'<div>FORMULA BUILT FOR BALANCE / 中文释义</div>'},
            {'key':'production','title':'生成与生产','html':'<div>后期精确排字</div>'},
            {'key':'trace','title':'合同 / QA / 来源','html':'<div>parameter trace</div>'},
        ],
    }
    base.update(overrides)
    return base


def test_asset_page_is_a_production_workspace_not_module_shell():
    page=_asset_page(_asset())
    assert 'data-workspace-kind="asset-production"' in page
    assert 'asset-production-rail' in page
    assert 'asset-production-stage' in page
    assert 'module-shell' not in page
    assert 'subnav-btn' not in page


def test_asset_production_workspace_groups_decisions_by_work_object():
    page=_asset_page(_asset())
    for label in ['决策 / Design Card','画面执行','摄影 / CMF','文案','Prompt 执行','QA / 来源']:
        assert label in page
    # overview + strategy are one decision stage, not two report tabs.
    assert page.count('data-view="asset-stage-lst-03-decision"') == 2  # switch + panel
    assert 'Design Card 概览' in page
    assert '购买障碍与目标信念' in page


def test_cn_and_en_prompts_share_one_execution_stage():
    page=_asset_page(_asset())
    assert page.count('Prompt 执行') >= 1
    assert 'asset-lst-03-prompt-cn' in page
    assert 'asset-lst-03-prompt-en' in page
    assert '中文执行提示词：保持真实商品像素' in page
    assert 'English execution prompt: preserve product fidelity' in page
    assert 'prompt-cn' not in [x.split('data-view="',1)[1].split('"',1)[0] for x in page.split('<button class="asset-phase')[1:]]
    assert 'Prompt 是执行合同，不是独立创意来源' in page


def test_asset_stage_count_is_dynamic_from_available_content():
    minimal=_asset(
        views=[{'key':'visual','title':'画面与版式','html':'<div>only visual</div>'}],
        prompt_cn='',prompt_en='',source_files=[]
    )
    page=_asset_page(minimal)
    assert '2 个动态阶段' not in page
    assert '1 个动态阶段' in page
    assert page.count('class="asset-phase workspace-switch') == 1
    assert '画面执行' in page
    assert '摄影 / CMF' not in page
    assert 'Prompt 执行' not in page
    assert 'QA / 来源' not in page


def test_source_files_and_trace_live_in_qa_not_prompt():
    page=_asset_page(_asset())
    qa_pos=page.index('TRACE · QA')
    source_pos=page.index('asset_packages/LST-03/12_design_card.json')
    prompt_pos=page.index('EXECUTION')
    assert source_pos > qa_pos
    assert source_pos > prompt_pos
    assert '2 个源文件可追溯' in page


def test_unknown_legacy_views_remain_recoverable_in_qa():
    legacy=_asset(
        views=[{'key':'v1','title':'旧版补充说明','html':'<div>legacy content</div>'}],
        prompt_cn='',prompt_en='',source_files=[]
    )
    page=_asset_page(legacy)
    assert 'QA / 来源' in page
    assert '旧版补充说明' in page
    assert 'legacy content' in page
