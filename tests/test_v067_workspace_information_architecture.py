from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))

from cbcc.delivery_html import (
    _classify_doc,
    _master_strategy_views,
    _strategy_workspace,
    _content_workspace,
    _visual_workspace,
    _listing_workspace,
    _prompt_workspace,
    _evidence_workspace,
    build_delivery_html,
)


def _views(n=3):
    return [
        {'key':f'v{i}','title':f'主题 {i}','secondary':'','html':f'<p>内容 {i}</p>','source':f'source-{i}.md'}
        for i in range(1,n+1)
    ]


def test_content_is_first_class_route_not_strategy_bucket(tmp_path):
    assert _classify_doc(Path('CONTENT_SYSTEM.md')) == 'content'
    assert _classify_doc(Path('CONTENT_MATRIX.md')) == 'content'
    assert _classify_doc(Path('STRATEGY_MASTER.md')) == 'strategy'

    master=tmp_path/'MASTER_STRATEGY_CN.md'
    master.write_text(
        '# Master\n\n'
        '## 4. 营销核心策略\n策略正文\n\n'
        '## 6. 平台内容矩阵\n内容矩阵正文\n\n'
        '## 7. RACE 传播执行\n执行正文\n',
        encoding='utf-8',
    )
    buckets=_master_strategy_views(master,tmp_path)
    assert len(buckets['strategy']) == 1
    assert len(buckets['content']) == 2


def test_key_workspaces_have_distinct_information_architectures():
    views=_views(3)
    strategy=_strategy_workspace(views)
    content=_content_workspace(views)
    visual=_visual_workspace(views)

    center={
        'delivery_language':{'locale':'zh-CN'},
        'copy_center':[
            {'field':'title','label':'标题','value':'示例标题','status':'READY'},
            {'field':'description','label':'描述','value':'示例描述','status':'READY'},
        ],
        'localized_copy':[],
    }
    listing=_listing_workspace(center)
    prompts=_prompt_workspace([
        {'id':'A01','title':'资产一','prompt_cn':'中文一','prompt_en':'English one'},
        {'id':'A02','title':'资产二','prompt_cn':'中文二','prompt_en':'English two'},
    ])
    evidence=_evidence_workspace(
        ['<figure class="media-card">图</figure>'],
        views[:2],
        ['<li>source.xlsx</li>'],
    )

    assert 'class="strategy-board"' in strategy
    assert strategy.count('class="strategy-decision searchable"') == 3
    assert 'module-shell' not in strategy

    assert 'class="content-board"' in content
    assert content.count('class="content-lane searchable"') == 3
    assert 'module-shell' not in content

    assert 'class="visual-studio"' in visual
    assert visual.count('class="visual-thumb workspace-switch') == 3
    assert 'visual-inspector' in visual
    assert 'module-shell' not in visual

    assert 'class="listing-studio"' in listing
    assert 'class="listing-tasks"' in listing
    assert 'module-shell' not in listing

    assert 'class="prompt-lab"' in prompts
    assert prompts.count('class="prompt-asset-switch workspace-switch') == 2
    assert 'module-shell' not in prompts

    assert 'class="evidence-center"' in evidence
    assert 'evidence-media' in evidence
    assert 'evidence-docs' in evidence
    assert 'evidence-files' in evidence
    assert 'module-shell' not in evidence


def test_workspace_counts_are_dynamic_not_fixed_templates():
    assert _strategy_workspace(_views(2)).count('strategy-decision searchable') == 2
    assert _strategy_workspace(_views(5)).count('strategy-decision searchable') == 5
    assert _content_workspace(_views(1)).count('content-lane searchable') == 1
    assert _content_workspace(_views(4)).count('content-lane searchable') == 4
    assert _visual_workspace(_views(2)).count('visual-thumb workspace-switch') == 2
    assert _visual_workspace(_views(6)).count('visual-thumb workspace-switch') == 6


def test_full_delivery_exposes_content_and_specialized_workspaces(tmp_path):
    (tmp_path/'MASTER_STRATEGY_CN.md').write_text(
        '# 主策略\n\n'
        '## 4. 营销核心策略\n### 定位\n策略正文\n### 价值主张\n价值正文\n\n'
        '## 5. 视觉 / 摄影策略\n### 构图\n构图正文\n### 灯光\n灯光正文\n\n'
        '## 6. 平台内容矩阵\n### TikTok\n内容正文\n### PDP\n详情正文\n',
        encoding='utf-8',
    )
    (tmp_path/'CONTENT_SYSTEM.md').write_text('# 内容系统\n\n## UGC\nUGC 正文\n\n## LIVE\n直播正文\n',encoding='utf-8')
    (tmp_path/'SOURCE_EVIDENCE.md').write_text('# 来源\n\n## 证据 A\n证据正文\n',encoding='utf-8')
    (tmp_path/'sources').mkdir()
    (tmp_path/'sources'/'facts.txt').write_text('fact source',encoding='utf-8')
    (tmp_path/'HUMAN_DELIVERY.json').write_text(json.dumps({
        'delivery_language':{'locale':'zh-CN'},
        'target':{'market':'malaysia','platform':'tiktok_shop','locale':'ms-MY','delivery_locale':'zh-CN'},
        'product':{'product_name':'测试商品'},
        'copy_center':[{'field':'title','label':'标题','value':'测试标题','status':'READY'}],
        'localized_copy':[],
        'risks_and_holds':[],
    },ensure_ascii=False),encoding='utf-8')

    out=build_delivery_html(tmp_path)
    text=out.read_text(encoding='utf-8')
    assert 'data-route="content"' in text
    assert 'data-workspace-kind="strategy"' in text
    assert 'data-workspace-kind="content"' in text
    assert 'data-workspace-kind="visual"' in text
    assert 'data-workspace-kind="listing"' in text
    assert 'data-workspace-kind="evidence"' in text
    assert 'workspace-switch' in text
    assert '内容主题由当前策略与平台需要动态产生，不预设固定资产数量' in text
