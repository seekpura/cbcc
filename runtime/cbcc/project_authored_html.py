from __future__ import annotations

import html
import re
from typing import Any, Mapping


_STYLE = r'''
<style id="cbcc-project-authored-workspace">
.app{display:block!important;min-height:100vh}
.project-object-dock{position:sticky;top:0;z-index:70;background:#10231C;color:#EDF5F1;display:grid;grid-template-columns:minmax(180px,1fr) auto;gap:16px;align-items:center;padding:10px 18px;border-bottom:1px solid rgba(255,255,255,.10)}
.project-object-brand b{display:block;font-size:13px}.project-object-brand span{display:block;font-size:9px;color:#9FB5AB;white-space:nowrap}.project-object-actions{display:flex;align-items:center;gap:7px}
.project-home-link,.project-switcher-toggle{appearance:none;white-space:nowrap;text-decoration:none;border:1px solid rgba(255,255,255,.14);border-radius:999px;padding:7px 11px;color:#DDE9E3;background:transparent;font:inherit;font-size:11px;cursor:pointer}.project-home-link:hover,.project-home-link.active,.project-switcher-toggle:hover{background:#EDF5F1;color:#10231C;border-color:#EDF5F1}.project-switcher-count{opacity:.7;margin-left:5px}
.workspace{min-width:0}.topbar{top:51px!important}
.project-home-launch{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 0 2px;border-top:1px solid var(--line)}.project-home-launch-copy b{display:block;font-size:12px}.project-home-launch-copy span{display:block;color:var(--muted);font-size:10px;margin-top:3px}.project-home-launch .project-switcher-toggle{color:var(--accent);border-color:var(--line);background:#fff;font-weight:750}
.project-object-switcher{position:fixed;inset:0;z-index:120;display:none;background:rgba(9,19,15,.42);backdrop-filter:blur(4px);padding:18px}.project-object-switcher.open{display:grid;place-items:center}.project-object-sheet{width:min(760px,100%);max-height:min(78vh,760px);overflow:hidden;background:var(--panel,#fff);border:1px solid var(--line,#ddd);border-radius:22px;box-shadow:0 28px 90px rgba(5,20,14,.24);display:grid;grid-template-rows:auto auto minmax(0,1fr)}.project-object-sheet-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;padding:20px 22px 12px}.project-object-sheet-head h2{margin:0 0 4px;font-size:21px}.project-object-sheet-head p{margin:0;color:var(--muted);font-size:11px}.project-switcher-close{appearance:none;border:1px solid var(--line);background:#fff;border-radius:999px;width:34px;height:34px;cursor:pointer}.project-object-search-wrap{padding:0 22px 12px}.project-object-search{width:100%;border:1px solid var(--line);background:var(--soft,#f7f8f7);border-radius:12px;padding:11px 13px;font:inherit;color:var(--ink)}.project-object-list{overflow:auto;padding:0 12px 16px}.project-switcher-item{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:14px;padding:13px 10px;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink)}.project-switcher-item:hover{background:var(--soft,#f7f8f7);border-radius:12px}.project-switcher-item b{display:block;font-size:13px}.project-switcher-item span{display:block;margin-top:4px;color:var(--muted);font-size:10px;line-height:1.45}.project-switcher-item small{align-self:center;color:var(--accent);font-size:10px}.project-switcher-empty{display:none;padding:18px;color:var(--muted);font-size:11px}
.module-shell{display:block!important}
.module-nav{position:static!important;display:flex!important;gap:7px!important;overflow:auto!important;max-height:none!important;padding:0 0 10px!important;margin:0 0 10px!important;background:transparent!important;border:0!important;border-radius:0!important}.subnav-btn{width:auto!important;min-width:max-content!important;border:1px solid var(--line)!important;background:#fff!important;border-radius:999px!important;padding:8px 12px!important}.subnav-btn.active{background:var(--accent)!important;color:#fff!important}
.strategy-board{max-width:none!important;display:grid!important;grid-template-columns:repeat(auto-fit,minmax(340px,1fr))!important;gap:10px!important}.strategy-map-head{grid-column:1/-1!important}.strategy-decision{border:1px solid var(--line)!important;border-radius:14px!important;overflow:hidden}.strategy-decision summary{grid-template-columns:minmax(0,1fr) auto!important}.strategy-index,.content-lane>header>span,.evidence-zone>header span{display:none!important}.strategy-body{padding:14px 18px 18px!important}
.asset-object-navigator{position:static!important;display:flex!important;gap:7px!important;overflow:auto!important;max-height:none!important}.asset-object-tab-index{display:none!important}
@media(max-width:760px){.project-object-dock{grid-template-columns:minmax(0,1fr) auto;padding:8px 10px}.project-object-brand span{display:none}.topbar{top:55px!important}.project-home-link{display:none}.project-object-switcher{padding:8px}.project-object-sheet{max-height:90vh;border-radius:18px}.project-home-launch{align-items:flex-start;flex-direction:column}}
</style>
'''

_SCRIPT = r'''
<script id="cbcc-project-object-switcher-script">
(function(){
  const switcher=document.getElementById('project-object-switcher');
  if(!switcher)return;
  const search=switcher.querySelector('.project-object-search');
  const items=[...switcher.querySelectorAll('.project-switcher-item')];
  const empty=switcher.querySelector('.project-switcher-empty');
  const open=()=>{switcher.classList.add('open');switcher.setAttribute('aria-hidden','false');if(search){search.value='';items.forEach(x=>x.hidden=false);setTimeout(()=>search.focus(),0)}if(empty)empty.style.display='none'};
  const close=()=>{switcher.classList.remove('open');switcher.setAttribute('aria-hidden','true')};
  document.querySelectorAll('[data-project-switcher-toggle]').forEach(x=>x.addEventListener('click',open));
  switcher.querySelectorAll('[data-project-switcher-close]').forEach(x=>x.addEventListener('click',close));
  switcher.addEventListener('click',e=>{if(e.target===switcher)close()});
  items.forEach(x=>x.addEventListener('click',close));
  document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});
  if(search)search.addEventListener('input',()=>{const q=search.value.trim().toLowerCase();let n=0;items.forEach(item=>{const show=!q||item.textContent.toLowerCase().includes(q);item.hidden=!show;if(show)n++});if(empty)empty.style.display=n?'none':'block'});
})();
</script>
'''


def _strip_tags(value: Any) -> str:
    raw = re.sub(r'<[^>]+>', '', str(value or ''))
    return re.sub(r'\s+', ' ', html.unescape(raw)).strip()


def _route_pages(page: str) -> dict[str, dict[str, str]]:
    starts = list(re.finditer(r'<section class="page(?: [^"]*)?" data-route="([^"]+)">', page))
    out: dict[str, dict[str, str]] = {}
    for index, match in enumerate(starts):
        start = match.start()
        end = starts[index + 1].start() if index + 1 < len(starts) else len(page)
        block = page[start:end]
        heading = re.search(r'<h1>(.*?)</h1>', block, re.S)
        description = re.search(r'<div class="page-head">.*?<p>(.*?)</p>', block, re.S)
        out[match.group(1)] = {
            'title': _strip_tags(heading.group(1)) if heading else match.group(1),
            'description': _strip_tags(description.group(1)) if description else '',
            'html': block,
        }
    return out


def _context_from_page(page: str) -> dict[str, str]:
    result = {'product_name': '', 'platform': '', 'market': '', 'target_locale': ''}
    match = re.search(r'<div class="context">\s*<b>(.*?)</b>.*?<span>(.*?)</span>\s*</div>', page, re.S)
    if match:
        result['product_name'] = _strip_tags(match.group(1))
        parts = [part.strip() for part in _strip_tags(match.group(2)).split('·') if part.strip()]
        ordinary: list[str] = []
        for part in parts:
            if part.startswith('目标语言'):
                result['target_locale'] = part.replace('目标语言', '', 1).strip()
            elif part.startswith('交付语言'):
                continue
            else:
                ordinary.append(part)
        if ordinary:
            result['platform'] = ordinary[0]
        if len(ordinary) > 1:
            result['market'] = ordinary[1]
    if not result['product_name']:
        overview = _route_pages(page).get('overview') or {}
        result['product_name'] = str(overview.get('title') or '当前项目')
    return result


def _sidebar_routes(page: str) -> list[str]:
    sidebar = re.search(r'<aside class="sidebar">(.*?)</aside>', page, re.S)
    if not sidebar:
        return []
    routes: list[str] = []
    for match in re.finditer(r'<a[^>]+data-route="([^"]+)"[^>]*>.*?</a>', sidebar.group(1), re.S):
        route = match.group(1)
        if route not in routes:
            routes.append(route)
    return routes


def _route_label(route: str, pages: Mapping[str, Mapping[str, str]], context: Mapping[str, str], page: str) -> str:
    product = context.get('product_name') or '当前项目'
    platform = context.get('platform') or ''
    market = context.get('market') or ''
    if route == 'overview': return '项目主页'
    if route == 'product': return f'{product} 真源'
    if route == 'market':
        parts = [x for x in (market, platform) if x]
        if parts: return ' × '.join(parts)
    if route == 'listing' and context.get('target_locale'): return f'{context["target_locale"]} 上架稿'
    if route == 'strategy': return f'{product} · 商业决策'
    if route == 'content' and platform: return f'{platform} · 内容与传播'
    if route == 'visual': return f'{product} · 视觉世界'
    if route == 'assets':
        count = len(re.findall(r'class="asset-card\b', page))
        if count: return f'资产宇宙 · {count}'
    if route == 'prompts':
        count = len(re.findall(r'class="prompt-asset-switch\b', page))
        if count: return f'生产对象 · {count}'
    if route == 'risk' and market: return f'{market} · 发布边界'
    if route == 'sources': return '证据 / 真源库'
    title = str((pages.get(route) or {}).get('title') or '').strip()
    return title or route


def _switcher(routes: list[str], pages: Mapping[str, Mapping[str, str]], context: Mapping[str, str], page: str) -> str:
    items: list[str] = []
    for route in routes:
        if route in {'overview', 'archive'}:
            continue
        label = _route_label(route, pages, context, page)
        desc = str((pages.get(route) or {}).get('description') or '').strip() or '打开当前项目中的这一对象。'
        items.append(
            f'<a class="project-switcher-item route-link" href="#{html.escape(route)}" data-route="{html.escape(route)}" data-object-label="{html.escape(label)}">'
            f'<div><b>{html.escape(label)}</b><span>{html.escape(desc)}</span></div><small>打开 →</small></a>'
        )
    return (
        '<div class="project-object-switcher" id="project-object-switcher" aria-hidden="true">'
        '<div class="project-object-sheet" role="dialog" aria-modal="true" aria-label="当前项目对象">'
        '<div class="project-object-sheet-head"><div><h2>当前项目对象</h2><p>按对象进入，不按流程推进。</p></div><button class="project-switcher-close" type="button" data-project-switcher-close aria-label="关闭">×</button></div>'
        '<div class="project-object-search-wrap"><input class="project-object-search" type="search" placeholder="搜索 Listing、视觉、资产、证据…" aria-label="搜索项目对象"></div>'
        f'<div class="project-object-list">{"".join(items)}<div class="project-switcher-empty">没有匹配对象。</div></div>'
        '</div></div>'
    )


def project_authored_html(page: str, context: Mapping[str, str] | None = None) -> str:
    """Convert the legacy capability menu into a non-sequential SaaS object switcher.

    Full business pages remain untouched. The permanent shell carries project identity and a neutral object
    switcher rather than exposing the system capability catalog as navigation. Current priority remains a
    separate project-home concern and never defines a universal route order.
    """
    if not page or 'cbcc-project-authored-workspace' in page:
        return page

    pages = _route_pages(page)
    ctx = _context_from_page(page)
    if context:
        for key, value in context.items():
            if value not in (None, ''): ctx[str(key)] = str(value)
    routes = _sidebar_routes(page)
    objects = [r for r in routes if r not in {'overview', 'archive'}]

    context_line = ' · '.join(item for item in (ctx.get('platform'), ctx.get('market'), ctx.get('target_locale')) if item)
    dock = (
        '<nav class="project-object-dock">'
        f'<div class="project-object-brand"><b>{html.escape(ctx.get("product_name") or "当前项目")}</b><span>{html.escape(context_line)}</span></div>'
        '<div class="project-object-actions">'
        '<a href="#overview" data-route="overview" class="route-link project-home-link">项目主页</a>'
        f'<button type="button" class="project-switcher-toggle" data-project-switcher-toggle>项目对象<span class="project-switcher-count">{len(objects)}</span></button>'
        '</div></nav>'
    )

    sidebar = re.search(r'<aside class="sidebar">(.*?)</aside>', page, re.S)
    if sidebar:
        page = page[:sidebar.start()] + dock + page[sidebar.end():]

    page = page.replace(
        '工作台只显示当前项目真实存在的业务对象和 Agent 识别到的下一步，不按固定报告目录展开。',
        '这是当前项目主页。完整对象通过对象切换器自由进入；当前重点独立显示，不形成步骤顺序。',
    )

    launch = (
        '<div class="project-home-launch">'
        '<div class="project-home-launch-copy"><b>浏览当前项目对象</b><span>Listing、商业决策、视觉、资产与证据按当前项目实际存在情况提供。</span></div>'
        f'<button type="button" class="project-switcher-toggle" data-project-switcher-toggle>打开对象切换器 <span class="project-switcher-count">{len(objects)}</span></button>'
        '</div>'
    )
    command_panel = re.compile(r'<div class="panel"><h2>当前可以做什么？</h2><div class="command-grid">.*?</div></div>', re.S)
    page = command_panel.sub(launch, page, count=1)
    page = page.replace('Agent 决策前沿', '当前重点')
    page = page.replace('<p><b>建议：</b>', '<p><b>当前重点：</b>')
    page = page.replace('当前工作视图', '当前资产对象')
    page = page.replace('个相关视图 · 无固定先后顺序', '个当前对象')

    switcher = _switcher(routes, pages, ctx, page)
    if '<div class="workspace">' in page:
        page = page.replace('<div class="workspace">', switcher + '<div class="workspace">', 1)
    elif '<body>' in page:
        page = page.replace('<body>', '<body>' + switcher, 1)

    if '</head>' in page: page = page.replace('</head>', _STYLE + '</head>', 1)
    if '</body>' in page: page = page.replace('</body>', _SCRIPT + '</body>', 1)
    return page


__all__ = ['project_authored_html']
