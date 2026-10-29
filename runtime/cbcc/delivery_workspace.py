from __future__ import annotations

from pathlib import Path
import html
import json

from .delivery_html import build_delivery_html as _build_legacy_delivery_html


_OBJECT_WORKSPACE_CSS = r'''
/* Human delivery regression repair: asset pages are object workspaces, not phase rails. */
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


def _transform_to_object_workspace(page: str) -> str:
    out = page
    for before, after in _REPLACEMENTS:
        out = out.replace(before, after)
    marker = '</style>'
    if marker in out:
        out = out.replace(marker, _OBJECT_WORKSPACE_CSS + marker, 1)
    return out


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _commercial_brain_html(package_dir: Path) -> str:
    artifacts = package_dir / 'artifacts'
    continuity = _load_json(artifacts / 'seven_tool_continuity.json')
    pricing = _load_json(artifacts / 'pricing_economics_authority.json')
    if not continuity and not pricing:
        return ''
    capabilities = continuity.get('capabilities') or []
    cards = []
    for item in capabilities:
        cards.append(
            '<article class="cbcc-commerce-card">'
            f'<div class="cbcc-commerce-kicker">{html.escape(str(item.get("id") or ""))}</div>'
            f'<h3>{html.escape(str(item.get("name") or item.get("id") or ""))}</h3>'
            f'<p><b>状态：</b>{html.escape(str(item.get("project_status") or ""))}</p>'
            f'<p><b>Runtime：</b>{html.escape(str(item.get("runtime_entry") or ""))}</p>'
            f'<p><b>真实 Consumer：</b>{html.escape(" · ".join(str(x) for x in item.get("real_consumers") or []))}</p>'
            f'<p><b>业务产物：</b>{html.escape(" · ".join(str(x) for x in item.get("business_outputs") or []))}</p>'
            f'<p><b>人类交付：</b>{html.escape(str(item.get("human_delivery") or ""))}</p>'
            '</article>'
        )
    scenario_rows = []
    for row in pricing.get('scenarios') or []:
        scenario_rows.append(
            '<tr>'
            f'<td>{html.escape(str(row.get("scenario_id") or ""))}</td>'
            f'<td>{html.escape(str(row.get("sku") or ""))}</td>'
            f'<td>{html.escape(str(row.get("price") if row.get("price") is not None else "—"))}</td>'
            f'<td>{html.escape(str(row.get("contribution_before_ads") if row.get("contribution_before_ads") is not None else "—"))}</td>'
            f'<td>{html.escape(str(row.get("contribution_margin_rate_before_ads") if row.get("contribution_margin_rate_before_ads") is not None else "—"))}</td>'
            f'<td>{html.escape(str(row.get("break_even_cpa") if row.get("break_even_cpa") is not None else "—"))}</td>'
            f'<td>{html.escape(str(row.get("break_even_cpc") if row.get("break_even_cpc") is not None else "待显式 CVR"))}</td>'
            f'<td>{html.escape(str(row.get("break_even_roas") if row.get("break_even_roas") is not None else "—"))}</td>'
            f'<td>{html.escape(str(row.get("status") or ""))}</td>'
            '</tr>'
        )
    decision = pricing.get('pricing_decision') or {}
    missing = pricing.get('missing_inputs') or []
    style = """<style id="cbcc-commerce-brain-style">
#commercial-brain{padding:28px 0}.cbcc-commerce-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.cbcc-commerce-card{border:1px solid var(--line,#ddd);border-radius:16px;padding:16px;background:#fff}.cbcc-commerce-card h3{margin:4px 0 10px}.cbcc-commerce-card p{margin:6px 0;font-size:12px;line-height:1.55}.cbcc-commerce-kicker{font-size:10px;letter-spacing:.08em;color:var(--muted,#666)}.cbcc-econ-table{width:100%;border-collapse:collapse;margin-top:12px;font-size:11px}.cbcc-econ-table th,.cbcc-econ-table td{border-bottom:1px solid var(--line,#ddd);padding:8px;text-align:left;vertical-align:top}.cbcc-commerce-note{border:1px solid var(--line,#ddd);border-radius:14px;padding:14px;margin:12px 0;background:var(--soft,#f7f7f7)}</style>"""
    return style + '<section id="commercial-brain" class="section"><div class="section-head"><div><div class="eyebrow">COMMERCIAL BRAIN</div><h2>七大工具 / 定价与经济性</h2><p>商业能力与视觉生产并列；这里展示真实 Runtime Consumer、业务产物与经济边界。</p></div></div>' + '<div class="cbcc-commerce-grid">' + ''.join(cards) + '</div>' + '<div class="cbcc-commerce-note"><b>Pricing Decision + WHY：</b> ' + html.escape(str(decision.get('decision') or '待 Agent 决策')) + '<br><b>WHY：</b> ' + html.escape(str(decision.get('why') or '需基于市场证据、SKU角色与单位经济作者化')) + '<br><b>状态：</b> ' + html.escape(str(decision.get('status') or pricing.get('status') or 'NOT_SUPPLIED')) + '</div>' + '<div class="cbcc-commerce-note"><b>市场价格带：</b> ' + html.escape(json.dumps(pricing.get('market_price_bands') or [], ensure_ascii=False)) + '<br><b>价格洼地：</b> ' + html.escape(json.dumps(pricing.get('market_price_valleys') or [], ensure_ascii=False)) + '<br><b>Price × Configuration：</b> ' + html.escape(json.dumps(pricing.get('price_configuration_matrix') or [], ensure_ascii=False)) + '</div>' + '<div class="cbcc-commerce-note"><b>SKU Roles：</b> ' + html.escape(json.dumps(pricing.get('sku_roles') or [], ensure_ascii=False)) + '<br><b>Offer / Bundle / Discount Boundary：</b> ' + html.escape(json.dumps(pricing.get('offer_bundle_discount_boundary') or [], ensure_ascii=False)) + '<br><b>缺失输入：</b> ' + html.escape(json.dumps(missing, ensure_ascii=False)) + '</div>' + '<div style="overflow:auto"><table class="cbcc-econ-table"><thead><tr><th>Scenario</th><th>SKU</th><th>Price</th><th>Contribution before Ads</th><th>Margin</th><th>Break-even CPA</th><th>Break-even CPC</th><th>Break-even ROAS</th><th>Status</th></tr></thead><tbody>' + ''.join(scenario_rows) + '</tbody></table></div></section>'


def _inject_commercial_brain(page: str, package_dir: Path) -> str:
    block = _commercial_brain_html(package_dir)
    if not block or 'id="commercial-brain"' in page:
        return page
    marker = '</main>' if '</main>' in page else '</body>'
    return page.replace(marker, block + marker, 1)


def build_delivery_html(package_dir: Path, output: Path | None = None, title: str = 'CBCC Delivery') -> Path:
    """Build the complete offline human workspace.

    The legacy renderer remains the content authority. This final presentation layer removes the
    obsolete phase/rail metaphor from asset pages and exposes the same complete content as freely
    addressable work objects. No content is discarded and no planning/execution order is implied.
    """
    package_dir = Path(package_dir)
    output = Path(output) if output else package_dir / 'index.html'
    result = _build_legacy_delivery_html(package_dir, output, title=title)
    text = result.read_text(encoding='utf-8')
    text = _transform_to_object_workspace(text)
    text = _inject_commercial_brain(text, package_dir)
    result.write_text(text, encoding='utf-8')
    return result
