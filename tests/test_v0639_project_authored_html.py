from pathlib import Path

import cbcc.delivery_workspace as delivery_workspace
from cbcc.project_authored_html import project_authored_html


SAMPLE = '''<!doctype html><html><head><style>
.app{display:grid}.sidebar{position:sticky}.module-shell{display:grid}.module-nav{position:sticky}
</style></head><body>
<div class="app">
<aside class="sidebar"><div class="brand"><b>CBCC 电商工作台</b><span>策略 · 上架 · 创意 · 生产</span></div>
<div class="nav"><div class="nav-label">工作区</div>
<a href="#overview" data-route="overview" class="route-link"><span class="ico">⌂</span>工作台</a>
<a href="#product" data-route="product" class="route-link"><span class="ico">▣</span>产品事实</a>
<a href="#listing" data-route="listing" class="route-link"><span class="ico">≡</span>上架中心</a>
<a href="#visual" data-route="visual" class="route-link"><span class="ico">◐</span>视觉 / 摄影</a>
<a href="#assets" data-route="assets" class="route-link"><span class="ico">▦</span>资产中心</a>
</div><div class="sidebar-foot">默认中文交付</div></aside>
<div class="workspace"><header class="topbar"><div class="context"><b>KIYUU K01</b><span>TikTok Shop · 马来西亚 · 目标语言 ms-MY · 交付语言 zh-CN</span></div></header>
<section class="page" data-route="overview"><div class="page-head"><div><h1>KIYUU K01</h1><p>工作台只显示当前项目真实存在的业务对象和 Agent 识别到的下一步，不按固定报告目录展开。</p></div></div><div class="panel"><h2>当前可以做什么？</h2><div class="command-grid"><a class="command-card route-link" href="#listing" data-route="listing"><b>处理上架资料</b><span>当前项目已生成对象</span></a></div></div><div class="panel agent-frontier"><h2>Agent 决策前沿</h2><p><b>建议：</b>先检查 Listing</p></div></section>
<section class="page" data-route="product"><div class="page-head"><div><h1>产品事实与证据</h1><p>当前商品事实与证据。</p></div></div><div class="module-shell"><aside class="module-nav"><button class="subnav-btn"><span>配方</span></button></aside><div class="module-stage"></div></div></section>
<section class="page" data-route="listing"><div class="page-head"><div><h1>上架资料中心</h1><p>目标市场可直接使用的字段。</p></div></div></section>
<section class="page" data-route="visual"><div class="page-head"><div><h1>视觉世界</h1><p>当前项目视觉方向与执行。</p></div></div></section>
<section class="page" data-route="assets"><div class="page-head"><div><h1>资产宇宙</h1><p>当前资产池。</p></div></div><div class="asset-grid"><a class="asset-card"></a><a class="asset-card"></a></div></section>
</div></div></body></html>'''


def test_project_authored_html_removes_pipeline_shell():
    out = project_authored_html(SAMPLE)
    assert 'class="sidebar"' not in out
    assert 'project-object-dock' in out
    assert '<div class="nav-label">工作区</div>' not in out
    assert 'KIYUU K01 · 项目地图' in out
    assert out.count('class="route-link project-object-link') == 1
    assert 'KIYUU K01 真源' in out
    assert 'ms-MY 上架稿' in out
    assert '资产宇宙 · 2' in out
    assert '.module-shell{display:block!important}' in out
    assert '.module-nav{position:static!important;display:flex!important' in out


def test_project_authored_html_uses_full_object_map_not_next_step_cards():
    out = project_authored_html(SAMPLE)
    assert '<h2>项目地图</h2>' in out
    assert '按真实决策、发布对象与资产进入，不按步骤推进。' in out
    assert 'project-map-grid' in out
    assert 'project-map-card' in out
    assert '当前商品事实与证据。' in out
    assert '目标市场可直接使用的字段。' in out
    assert '当前项目视觉方向与执行。' in out
    assert '当前资产池。' in out
    assert 'class="command-card' not in out
    assert 'Agent 决策前沿' not in out
    assert '当前重点' in out
    assert '.strategy-index,.content-lane>header>span,.evidence-zone>header span{display:none!important}' in out


def test_project_authored_html_preserves_underlying_business_pages():
    out = project_authored_html(SAMPLE)
    assert 'data-route="product"' in out
    assert 'data-route="listing"' in out
    assert 'data-route="visual"' in out
    assert 'data-route="assets"' in out
    assert '配方' in out


def test_delivery_workspace_wires_project_authored_transform(tmp_path, monkeypatch):
    package_dir = tmp_path / 'project'
    package_dir.mkdir()
    output = package_dir / 'index.html'

    def fake_legacy(package_dir: Path, output: Path, title: str = 'CBCC Delivery') -> Path:
        output.write_text(SAMPLE, encoding='utf-8')
        return output

    monkeypatch.setattr(delivery_workspace, '_build_legacy_delivery_html', fake_legacy)
    result = delivery_workspace.build_delivery_html(package_dir, output)
    out = result.read_text(encoding='utf-8')
    assert 'cbcc-project-authored-workspace' in out
    assert 'class="sidebar"' not in out
    assert '<h2>项目地图</h2>' in out
    assert out.count('class="route-link project-object-link') == 1
