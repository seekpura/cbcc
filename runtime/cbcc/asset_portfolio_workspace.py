from __future__ import annotations

from typing import Any
import html
import json


def _text(v: Any, limit: int = 420) -> str:
    if v in (None, '', [], {}):
        return '—'
    if isinstance(v, (dict, list)):
        v = json.dumps(v, ensure_ascii=False)
    s = str(v)
    return s if len(s) <= limit else s[:limit].rstrip() + '…'


def render_asset_portfolio_workspace(portfolio: dict[str, Any]) -> str:
    if not isinstance(portfolio, dict) or not portfolio:
        return ''
    summary = portfolio.get('summary') if isinstance(portfolio.get('summary'), dict) else portfolio
    assets = portfolio.get('assets') or []
    family_counts = summary.get('asset_family_counts') or {}
    state_counts = summary.get('deployment_state_counts') or {}
    metrics = [
        ('Asset Universe', summary.get('total_asset_candidates')),
        ('Activation Capacity', summary.get('activation_capacity')),
        ('固定总量上限', '否' if summary.get('fixed_total_asset_limit') is False else summary.get('fixed_total_asset_limit')),
        ('Capacity 仅限制 Live Set', '是' if summary.get('platform_capacity_is_activation_constraint_only') else '待确认'),
    ]
    metric_html = ''.join(
        f'<div class="ap-metric"><span>{html.escape(k)}</span><b>{html.escape(_text(v, 120))}</b></div>'
        for k, v in metrics if v not in (None, '')
    )
    families = ''.join(
        f'<div class="ap-chip"><b>{html.escape(str(k))}</b><span>{html.escape(str(v))}</span></div>'
        for k, v in sorted(family_counts.items())
    ) or '<div class="ap-empty">当前还没有资产族统计。</div>'
    states = ''.join(
        f'<div class="ap-chip"><b>{html.escape(str(k))}</b><span>{html.escape(str(v))}</span></div>'
        for k, v in sorted(state_counts.items())
    ) or '<div class="ap-empty">当前还没有部署池统计。</div>'

    rows = []
    for a in assets:
        if not isinstance(a, dict):
            continue
        rows.append(
            '<tr>'
            f'<td>{html.escape(_text(a.get("asset_id"), 90))}</td>'
            f'<td>{html.escape(_text(a.get("asset_family"), 90))}</td>'
            f'<td>{html.escape(_text(a.get("surface"), 90))}</td>'
            f'<td>{html.escape(_text(a.get("deployment_state"), 90))}</td>'
            f'<td>{html.escape(_text(a.get("variant_id"), 90))}</td>'
            f'<td>{html.escape(_text(a.get("test_hypothesis") or a.get("business_hypothesis"), 300))}</td>'
            '</tr>'
        )
    table = ''
    if rows:
        table = '<div class="ap-table"><table><thead><tr><th>Asset</th><th>Family</th><th>Surface</th><th>Pool</th><th>Variant</th><th>Hypothesis</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'

    return (
        '<section class="asset-portfolio-intelligence searchable">'
        '<header><div><span>ASSET UNIVERSE · ACTIVATION · TEST</span><h2>商业资产宇宙</h2></div>'
        '<p>平台 7/9 图或视频槽位只限制当前同时上线集合，不限制 Hero、卖点、Proof、场景、PDP/A+、广告、种草、Creator/UGC、视频、Banner、A/B 与轮换池总量。</p></header>'
        f'<div class="ap-metrics">{metric_html}</div>'
        '<h3>资产族</h3><div class="ap-chips">' + families + '</div>'
        '<h3>部署 / 测试池</h3><div class="ap-chips">' + states + '</div>'
        + table + '</section>'
    )


def asset_portfolio_css() -> str:
    return '''
.asset-portfolio-intelligence{grid-column:1/-1;background:#fff;border:1px solid var(--line,#dde3df);border-radius:16px;padding:16px;margin-top:12px}.asset-portfolio-intelligence header{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.asset-portfolio-intelligence header span{font-size:8px;letter-spacing:.08em;color:var(--accent,#23483d);font-weight:800}.asset-portfolio-intelligence h2{margin:2px 0 0;font-size:17px}.asset-portfolio-intelligence header p{max-width:760px;margin:0;color:var(--muted,#6a746f);font-size:10px}.asset-portfolio-intelligence h3{font-size:11px;margin:14px 0 6px}.ap-metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-top:12px}.ap-metric{border:1px solid var(--line,#dde3df);border-radius:12px;padding:10px;background:#f8faf8}.ap-metric span{display:block;font-size:8px;color:var(--muted,#6a746f)}.ap-metric b{display:block;margin-top:3px;font-size:14px}.ap-chips{display:flex;flex-wrap:wrap;gap:7px}.ap-chip{display:flex;gap:7px;align-items:center;border:1px solid var(--line,#dde3df);border-radius:999px;padding:6px 9px;background:#f8faf8}.ap-chip b{font-size:9px}.ap-chip span{font-size:9px;color:var(--muted,#6a746f)}.ap-table{overflow:auto;margin-top:12px;border:1px solid var(--line,#dde3df);border-radius:12px}.ap-table table{border-collapse:collapse;width:100%;min-width:880px}.ap-table th,.ap-table td{padding:8px;border-bottom:1px solid #edf0ed;text-align:left;vertical-align:top;font-size:9px}.ap-table th{background:#eef3ef;color:#2b493f}.ap-empty{font-size:9px;color:var(--muted,#6a746f)}@media(max-width:760px){.asset-portfolio-intelligence header{display:block}.asset-portfolio-intelligence header p{margin-top:6px}}
'''
