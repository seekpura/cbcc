from __future__ import annotations

import html
import re
from typing import Any, Mapping


_STYLE = r'''
<style id="cbcc-project-authored-workspace">
.app{display:block!important;min-height:100vh}
.project-object-dock{position:sticky;top:0;z-index:50;background:#10231C;color:#EDF5F1;display:grid;grid-template-columns:minmax(180px,auto) minmax(0,1fr);gap:14px;align-items:center;padding:10px 18px;border-bottom:1px solid rgba(255,255,255,.10)}
.project-object-brand b{display:block;font-size:13px}.project-object-brand span{display:block;font-size:9px;color:#9FB5AB;white-space:nowrap}
.project-object-links{display:flex;gap:7px;overflow:auto;scrollbar-width:none}.project-object-links::-webkit-scrollbar{display:none}
.project-object-link{white-space:nowrap;text-decoration:none;border:1px solid rgba(255,255,255,.14);border-radius:999px;padding:7px 11px;color:#DDE9E3;font-size:11px}
.project-object-link:hover,.project-object-link.active{background:#EDF5F1;color:#10231C;border-color:#EDF5F1}
.workspace{min-width:0}.topbar{top:51px!important}
.project-map-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}
.project-map-card{display:block;text-decoration:none;background:#fff;border:1px solid var(--line);border-radius:15px;padding:16px;min-height:126px;box-shadow:0 5px 18px rgba(20,35,28,.035);transition:.16s}
.project-map-card:hover{transform:translateY(-2px);border-color:var(--accent);box-shadow:var(--shadow)}
.project-map-card b{display:block;font-size:15px;line-height:1.3;margin-bottom:8px}.project-map-card span{display:block;color:var(--muted);font-size:11px;line-height:1.55}.project-map-card small{display:block;margin-top:12px;color:var(--accent);font-size:10px;font-weight:750}
.module-shell{display:block!important}
.module-nav{position:static!important;display:flex!important;gap:7px!important;overflow:auto!important;max-height:none!important;padding:0 0 10px!important;margin:0 0 10px!important;background:transparent!important;border:0!important;border-radius:0!important}
.subnav-btn{width:auto!important;min-width:max-content!important;border:1px solid var(--line)!important;background:#fff!important;border-radius:999px!important;padding:8px 12px!important}
.subnav-btn.active{background:var(--accent)!important;color:#fff!important}
.strategy-board{max-width:none!important;display:grid!important;grid-template-columns:repeat(auto-fit,minmax(340px,1fr))!important;gap:10px!important}
.strategy-map-head{grid-column:1/-1!important}
.strategy-decision{border:1px solid var(--line)!important;border-radius:14px!important;overflow:hidden}
.strategy-decision summary{grid-template-columns:minmax(0,1fr) auto!important}
.strategy-index,.content-lane>header>span,.evidence-zone>header span{display:none!important}
.strategy-body{padding:14px 18px 18px!important}
.asset-object-navigator{position:static!important;display:flex!important;gap:7px!important;overflow:auto!important;max-height:none!important}
.asset-object-tab-index{display:none!important}
@media(max-width:760px){.project-object-dock{grid-template-columns:1fr;padding:8px 10px}.project-object-brand span{display:none}.topbar{top:82px!important}.project-object-links{padding-bottom:2px}.project-map-grid{grid-template-columns:1fr}}
</style>
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
    if route == 'overview':
        return f'{product} · 项目地图'
    if route == 'product':
        return f'{product} 真源'
    if route == 'market':
        parts = [x for x in (market, platform) if x]
        if parts:
            return ' × '.join(parts)
    if route == 'listing' and context.get('target_locale'):
        return f'{context["target_locale"]} 上架稿'
    if route == 'strategy':
        return f'{product} · 商业决策'
    if route == 'content' and platform:
        return f'{platform} · 内容与传播'
    if route == 'visual':
        return f'{product} · 视觉世界'
    if route == 'assets':
        count = len(re.findall(r'class="asset-card\b', page))
        if count:
            return f'资产宇宙 · {count}'
    if route == 'prompts':
        count = len(re.findall(r'class="prompt-asset-switch\b', page))
        if count:
            return f'生产对象 · {count}'
    if route == 'risk' and market:
        return f'{market} · 发布边界'
    if route == 'sources':
        return '证据 / 真源库'
    title = str((pages.get(route) or {}).get('title') or '').strip()
    return title or route


def _project_map(routes: list[str], pages: Mapping[str, Mapping[str, str]], context: Mapping[str, str], page: str) -> str:
    cards: list[str] = []
    for route in routes:
        if route in {'overview', 'archive'}:
            continue
        label = _route_label(route, pages, context, page)
        description = str((pages.get(route) or {}).get('description') or '').strip()
        if not description:
            description = '打开当前项目中的这一业务对象。'
        cards.append(
            f'<a class="project-map-card route-link" href="#{html.escape(route)}" data-route="{html.escape(route)}">'
            f'<b>{html.escape(label)}</b><span>{html.escape(description)}</span><small>打开对象 →</small></a>'
        )
    return '<div class="project-map-grid">' + ''.join(cards) + '</div>'


def project_authored_html(page: str, context: Mapping[str, str] | None = None) -> str:
    """Turn the legacy capability-menu shell into a project-authored object workspace.

    The underlying business pages and their full content remain intact. This function changes only the
    presentation grammar: no left-side capability pipeline, no numbered reading implication, and no
    vertical phase rail for generic module views. The current project's real objects remain directly
    addressable through a compact object dock and project map.
    """
    if not page or 'cbcc-project-authored-workspace' in page:
        return page

    pages = _route_pages(page)
    ctx = _context_from_page(page)
    if context:
        for key, value in context.items():
            if value not in (None, ''):
                ctx[str(key)] = str(value)

    routes = _sidebar_routes(page)
    links: list[str] = []
    for route in routes:
        label = _route_label(route, pages, ctx, page)
        secondary = ' secondary-object-link' if route == 'archive' else ''
        links.append(
            f'<a href="#{html.escape(route)}" data-route="{html.escape(route)}" '
            f'class="route-link project-object-link{secondary}">{html.escape(label)}</a>'
        )

    context_line = ' · '.join(
        item for item in (ctx.get('platform'), ctx.get('market'), ctx.get('target_locale')) if item
    )
    dock = (
        '<nav class="project-object-dock">'
        '<div class="project-object-brand">'
        f'<b>{html.escape(ctx.get("product_name") or "当前项目")}</b>'
        f'<span>{html.escape(context_line)}</span>'
        '</div>'
        f'<div class="project-object-links">{"".join(links)}</div>'
        '</nav>'
    )

    sidebar = re.search(r'<aside class="sidebar">(.*?)</aside>', page, re.S)
    if sidebar:
        page = page[:sidebar.start()] + dock + page[sidebar.end():]

    page = page.replace(
        '工作台只显示当前项目真实存在的业务对象和 Agent 识别到的下一步，不按固定报告目录展开。',
        '这里是当前项目的对象地图：按真实决策、发布对象与资产进入，不按步骤推进。',
    )

    map_html = _project_map(routes, pages, ctx, page)
    command_panel = re.compile(
        r'<div class="panel"><h2>当前可以做什么？</h2><div class="command-grid">.*?</div></div>',
        re.S,
    )
    page = command_panel.sub(f'<div class="panel project-map"><h2>项目地图</h2>{map_html}</div>', page, count=1)
    page = page.replace('Agent 决策前沿', '当前重点')
    page = page.replace('<p><b>建议：</b>', '<p><b>当前重点：</b>')
    page = page.replace('当前工作视图', '当前资产对象')
    page = page.replace('个相关视图 · 无固定先后顺序', '个当前对象')

    if '</head>' in page:
        page = page.replace('</head>', _STYLE + '</head>', 1)
    return page


__all__ = ['project_authored_html']
