from __future__ import annotations

from pathlib import Path
import html
import json

from .delivery_html import build_delivery_html as _build_legacy_delivery_html
from .operator_delivery_html import operator_execution_html


_OBJECT_WORKSPACE_CSS = r'''
/* Preserve the v0.6.36 routed workspace; only remove phase semantics inside asset detail. */
.asset-object-workspace{display:block!important}
.asset-object-navigator{position:static!important;top:auto!important;display:flex!important;gap:8px!important;overflow:auto!important;max-height:none!important;padding:8px!important;margin:0 0 12px!important;background:#fff!important;border:1px solid var(--line)!important;border-radius:16px!important}
.asset-object-nav-head{display:flex!important;min-width:max-content!important;align-items:center!important;gap:8px!important;padding:4px 8px!important;border:0!important;margin:0!important}
.asset-object-nav-head b{font-size:11px}.asset-object-nav-head span{font-size:9px;color:var(--muted)}
.asset-object-tab{display:block!important;min-width:max-content!important;border:1px solid var(--line)!important;background:#fff!important;text-align:left!important;border-radius:999px!important;padding:8px 12px!important;color:var(--ink)!important}
.asset-object-tab:hover{background:var(--soft)!important}.asset-object-tab.active{background:var(--accent)!important;color:#fff!important;border-color:var(--accent)!important}
.asset-object-tab-copy small{display:none!important}.asset-object-tab-copy b{display:block!important;font-size:11px!important;margin:0!important}
.asset-object-canvas{min-width:0}.asset-object-panel{background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 8px 28px rgba(20,35,28,.04)}
.asset-object-panel-head{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;padding:18px 20px;border-bottom:1px solid var(--line)}
.asset-object-panel-head span{font-size:9px;color:var(--muted);letter-spacing:.08em}.asset-object-panel-head h2{margin:2px 0 4px;font-size:20px}.asset-object-panel-head p{margin:0;color:var(--muted);max-width:860px}
.asset-object-panel-body{padding:18px 20px}
.cbcc-commerce-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px}.cbcc-commerce-card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px}.cbcc-commerce-card h3{margin:3px 0 9px}.cbcc-commerce-card p{margin:5px 0;font-size:11px}.cbcc-commerce-kicker{font-size:9px;color:var(--muted);letter-spacing:.08em}.cbcc-commerce-note{background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:12px;margin:10px 0}.cbcc-econ-table{width:100%;border-collapse:collapse;font-size:11px}.cbcc-econ-table th,.cbcc-econ-table td{padding:8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
@media(max-width:760px){.asset-object-navigator{border-radius:12px}.asset-object-tab{padding:7px 10px}.asset-object-panel-body{padding:14px}.asset-object-panel-head{padding:14px}}
'''

_REPLACEMENTS = (
    ('asset-production-workspace', 'asset-object-workspace'),
    ('asset-production-rail', 'asset-object-navigator'),
    ('asset-rail-head', 'asset-object-nav-head'),
    ('asset-phase-copy', 'asset-object-tab-copy'),
    ('asset-phase-index', 'asset-object-tab-index'),
    ('asset-phase', 'asset-object-tab'),
    ('asset-production-stage', 'asset-object-canvas'),
    ('asset-stage-head', 'asset-object-panel-head'),
    ('asset-stage-body', 'asset-object-panel-body'),
    ('asset-stage-', 'asset-object-panel-'),
    ('asset-stage', 'asset-object-panel'),
    ('当前工作视图', '资产对象'),
    ('个相关视图 · 无固定先后顺序', '个对象视图 · 自由进入'),
    ('data-workspace-kind="asset-production"', 'data-workspace-kind="asset-object"'),
)


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _transform_asset_compatibility(page: str) -> str:
    out = page
    for before, after in _REPLACEMENTS:
        out = out.replace(before, after)
    marker = '</style>'
    if marker in out:
        out = out.replace(marker, _OBJECT_WORKSPACE_CSS + marker, 1)
    return out


def _txt(value) -> str:
    if value in (None, ''):
        return '—'
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _commercial_brain_html(package_dir: Path) -> str:
    artifacts = package_dir / 'artifacts'
    continuity = _load_json(artifacts / 'seven_tool_continuity.json')
    pricing = _load_json(artifacts / 'pricing_economics_authority.json')
    if not continuity and not pricing:
        return ''

    cards = []
    for item in continuity.get('capabilities') or []:
        outputs = ' · '.join(str(x) for x in item.get('business_outputs') or []) or '—'
        consumers = ' · '.join(str(x) for x in item.get('real_consumers') or []) or '—'
        cards.append(
            '<article class="cbcc-commerce-card searchable">'
            f'<div class="cbcc-commerce-kicker">{html.escape(_txt(item.get("id")))}</div>'
            f'<h3>{html.escape(_txt(item.get("name") or item.get("id")))}</h3>'
            f'<p><b>项目状态：</b>{html.escape(_txt(item.get("project_status")))}</p>'
            f'<p><b>业务产物：</b>{html.escape(outputs)}</p>'
            f'<p><b>真实 Consumer：</b>{html.escape(consumers)}</p>'
            f'<p><b>人类交付：</b>{html.escape(_txt(item.get("human_delivery")))}</p>'
            '</article>'
        )

    rows = []
    for row in pricing.get('scenarios') or []:
        rows.append(
            '<tr>'
            f'<td>{html.escape(_txt(row.get("scenario_id")))}</td>'
            f'<td>{html.escape(_txt(row.get("sku")))}</td>'
            f'<td>{html.escape(_txt(row.get("price")))}</td>'
            f'<td>{html.escape(_txt(row.get("contribution_before_ads")))}</td>'
            f'<td>{html.escape(_txt(row.get("contribution_margin_rate_before_ads")))}</td>'
            f'<td>{html.escape(_txt(row.get("break_even_cpa")))}</td>'
            f'<td>{html.escape(_txt(row.get("break_even_cpc")))}</td>'
            f'<td>{html.escape(_txt(row.get("break_even_roas")))}</td>'
            f'<td>{html.escape(_txt(row.get("status")))}</td>'
            '</tr>'
        )

    decision = pricing.get('pricing_decision') or {}
    missing = pricing.get('missing_inputs') or []
    economics = ''
    if pricing:
        economics = (
            '<div class="panel">'
            '<div class="kicker">PRICING / ECONOMICS</div><h2>定价、单位经济与 Offer 边界</h2>'
            f'<div class="cbcc-commerce-note"><b>Pricing Decision：</b>{html.escape(_txt(decision.get("decision") or "待 Agent 决策"))}<br>'
            f'<b>WHY：</b>{html.escape(_txt(decision.get("why") or "需要基于市场证据、SKU角色与单位经济作者化"))}<br>'
            f'<b>状态：</b>{html.escape(_txt(decision.get("status") or pricing.get("status")))}</div>'
            f'<div class="cbcc-commerce-note"><b>市场价格带：</b>{html.escape(_txt(pricing.get("market_price_bands") or []))}<br>'
            f'<b>价格洼地：</b>{html.escape(_txt(pricing.get("market_price_valleys") or []))}<br>'
            f'<b>Price × Configuration：</b>{html.escape(_txt(pricing.get("price_configuration_matrix") or []))}<br>'
            f'<b>SKU Roles：</b>{html.escape(_txt(pricing.get("sku_roles") or []))}<br>'
            f'<b>Offer / Bundle / Discount Boundary：</b>{html.escape(_txt(pricing.get("offer_bundle_discount_boundary") or []))}<br>'
            f'<b>缺失输入：</b>{html.escape(_txt(missing))}</div>'
            + ('<div class="table-wrap"><table class="cbcc-econ-table"><thead><tr><th>Scenario</th><th>SKU</th><th>Price</th><th>Contribution</th><th>Margin</th><th>BE CPA</th><th>BE CPC</th><th>BE ROAS</th><th>Status</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>' if rows else '')
            + '</div>'
        )

    return (
        '<section id="commercial-brain">'
        '<div class="panel"><div class="kicker">COMMERCIAL BRAIN</div><h2>七大商业能力连续性</h2><p>商业能力与视觉生产并列；只展示当前项目真实存在的业务产物与缺口。</p>'
        f'<div class="cbcc-commerce-grid">{"".join(cards)}</div></div>'
        f'{economics}</section>'
    )


def _operations_page(package_dir: Path) -> str:
    operator = operator_execution_html(package_dir)
    commerce = _commercial_brain_html(package_dir)
    if not operator and not commerce:
        return ''
    return (
        '<section class="page" data-route="operations">'
        '<div class="page-head"><div><div class="kicker">运营工作面</div><h1>运营执行</h1>'
        '<p>把可直接执行的发布、生产、投放、复盘与经济边界集中到一个可切换工作面；它是完整项目的增量入口，不替代 Listing、策略、视觉或逐资产详情。</p></div></div>'
        f'{operator}{commerce}</section>'
    )


def _inject_operations_route(page: str, package_dir: Path) -> str:
    operations = _operations_page(package_dir)
    if not operations or 'data-route="operations"' in page:
        return page

    nav_marker = '</div><div class="sidebar-foot">'
    nav_link = '<a href="#operations" data-route="operations" class="route-link"><span class="ico">◆</span>运营执行</a>'
    if nav_marker in page:
        page = page.replace(nav_marker, nav_link + nav_marker, 1)

    # Keep the v0.6.36 routed-page model: operations is another .page, never a pre-main giant section.
    workspace_end = page.rfind('</div></div><script>')
    if workspace_end != -1:
        page = page[:workspace_end] + operations + page[workspace_end:]
    elif '</body>' in page:
        page = page.replace('</body>', operations + '</body>', 1)
    return page


def build_delivery_html(package_dir: Path, output: Path | None = None, title: str = 'CBCC Delivery') -> Path:
    """Build the complete human workspace on the v0.6.36 interaction floor.

    `delivery_html` remains the navigation/content authority: one routed primary work surface at a time,
    local subviews, per-asset detail routes, search, copy actions, responsive behavior and print projection.
    v0.6.37+ commercial/operator density is additive as a routed operations work surface. This layer must
    never flatten FULL delivery into one long page or replace the workspace with a new global shell.
    """
    package_dir = Path(package_dir)
    output = Path(output) if output else package_dir / 'index.html'
    result = _build_legacy_delivery_html(package_dir, output, title=title)
    text = result.read_text(encoding='utf-8')
    text = _transform_asset_compatibility(text)
    text = _inject_operations_route(text, package_dir)
    result.write_text(text, encoding='utf-8')
    return result
