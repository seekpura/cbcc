from pathlib import Path

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
<section class="page" data-route="overview"><div class="page-head"><div><h1>KIYUU K01</h1><p>工作台只显示当前项目真实存在的业务对象和 Agent 识别到的下一步，不按固定报告目录展开。</p></div></div><div class="panel"><h2>当前可以做什么？</h2><div class="command-grid"><a class="command-card route-link" href="#listing" data-route="listing"><b>处理上架资料</b><span>当前项目已生成对象</span></a></div></div></section>
<section class="page" data-route="product"><div class="page-head"><div><h1>产品事实与证据</h1></div></div><div class="module-shell"><aside class="module-nav"><button class="subnav-btn"><span>配方</span></button></aside><div class="module-stage"></div></div></section>
<section class="page" data-route="listing"><div class="page-head"><div><h1>上架资料中心</h1></div></div></section>
<section class="page" data-route="visual"><div class="page-head"><div><h1>视觉世界</h1></div></div></section>
<section class="page" data-route="assets"><div class="page-head"><div><h1>资产宇宙</h1></div></div><div class="asset-grid"><a class="asset-card"></a><a class="asset-card"></a></div></section>
</div></div></body></html>'''


def test_project_authored_html_removes_pipeline_shell():
    out = project_authored_html(SAMPLE)
    assert 'class="sidebar"' not in out
    assert 'project-object-dock' in out
    assert '<div class="nav-label">工作区</div>' not in out
    assert 'KIYUU K01 · 项目地图' in out
    assert 'KIYUU K01 真源' in out
    assert 'ms-MY 上架稿' in out
    assert '资产宇宙 · 2' in out
    assert '.module-shell{display:block!important}' in out
    assert '.module-nav{position:static!important;display:flex!important' in out


def test_project_authored_html_uses_object_map_not_step_language():
    out = project_authored_html(SAMPLE)
    assert '<h2>项目地图</h2>' in out
    assert '按真实决策、发布对象与资产进入，不按步骤推进。' in out
    assert '.strategy-index,.content-lane>header>span,.evidence-zone>header span{display:none!important}' in out


def test_project_authored_html_preserves_underlying_business_pages():
    out = project_authored_html(SAMPLE)
    assert 'data-route="product"' in out
    assert 'data-route="listing"' in out
    assert 'data-route="visual"' in out
    assert 'data-route="assets"' in out
    assert '配方' in out
