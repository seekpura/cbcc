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

    family_eval = portfolio.get('phase3_opportunity_family_evaluation') if isinstance(portfolio.get('phase3_opportunity_family_evaluation'), dict) else {}
    family_fulfillment = portfolio.get('opportunity_family_fulfillment') if isinstance(portfolio.get('opportunity_family_fulfillment'), dict) else {}
    fulfillment_by_id = {str(x.get('family_id')): x for x in (family_fulfillment.get('rows') or []) if isinstance(x, dict)}
    family_rows = []
    for row in family_eval.get('families') or []:
        if not isinstance(row, dict):
            continue
        fid = str(row.get('family_id') or '')
        frow = fulfillment_by_id.get(fid) or {}
        status = str(row.get('status') or 'TO_VERIFY')
        fulfill_status = str(frow.get('fulfillment_status') or ('NOT_REQUIRED_DELIBERATE_OMISSION' if status == 'NOT_NEEDED' else 'TO_VERIFY'))
        satisfiers = _text(row.get('satisfying_objects'), 320)
        matched = _text(frow.get('matched_asset_ids'), 240)
        family_rows.append(
            '<tr>'
            f'<td>{html.escape(fid)}</td>'
            f'<td>{html.escape(_text(row.get("family"), 140))}</td>'
            f'<td>{html.escape(status)}</td>'
            f'<td>{html.escape(_text(row.get("why"), 360))}</td>'
            f'<td>{html.escape(_text(row.get("why_not"), 360))}</td>'
            f'<td>{html.escape(satisfiers)}</td>'
            f'<td>{html.escape(fulfill_status)}</td>'
            f'<td>{html.escape(matched)}</td>'
            '</tr>'
        )
    family_table = ''
    if family_rows:
        family_table = (
            '<h3>机会族评估</h3>'
            '<div class="cbcc-commerce-note">23 类机会族必须在资产创建前逐一判断；NOT_NEEDED 必须是有理由的主动省略。一个对象可以满足多个机会族，不形成固定配额。</div>'
            '<div class="ap-table"><table><thead><tr><th>ID</th><th>机会族</th><th>决策</th><th>为什么</th><th>为什么不做</th><th>计划满足对象</th><th>履约</th><th>实际资产</th></tr></thead><tbody>'
            + ''.join(family_rows) + '</tbody></table></div>'
        )

    return (
        '<section class="asset-portfolio-intelligence searchable">'
        '<header><div><span>ASSET UNIVERSE · ACTIVATION · TEST</span><h2>商业资产宇宙</h2></div>'
        '<p>平台 7/9 图或视频槽位只限制当前同时上线集合，不限制 Hero、卖点、Proof、场景、PDP/A+、广告、种草、Creator/UGC、视频、Banner、A/B 与轮换池总量。</p></header>'
        f'<div class="ap-metrics">{metric_html}</div>'
        '<h3>资产族</h3><div class="ap-chips">' + families + '</div>'
        '<h3>部署 / 测试池</h3><div class="ap-chips">' + states + '</div>'
        + family_table + table + '</section>'
    )


def asset_portfolio_css() -> str:
    return '''
.asset-portfolio-intelligence{grid-column:1/-1;background:#fff;border:1px solid var(--line,#dde3df);border-radius:16px;padding:16px;margin-top:12px}.asset-portfolio-intelligence header{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.asset-portfolio-intelligence header span{font-size:8px;letter-spacing:.08em;color:var(--accent,#23483d);font-weight:800}.asset-portfolio-intelligence h2{margin:2px 0 0;font-size:17px}.asset-portfolio-intelligence header p{max-width:760px;margin:0;color:var(--muted,#6a746f);font-size:10px}.asset-portfolio-intelligence h3{font-size:11px;margin:14px 0 6px}.ap-metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-top:12px}.ap-metric{border:1px solid var(--line,#dde3df);border-radius:12px;padding:10px;background:#f8faf8}.ap-metric span{display:block;font-size:8px;color:var(--muted,#6a746f)}.ap-metric b{display:block;margin-top:3px;font-size:14px}.ap-chips{display:flex;flex-wrap:wrap;gap:7px}.ap-chip{display:flex;gap:7px;align-items:center;border:1px solid var(--line,#dde3df);border-radius:999px;padding:6px 9px;background:#f8faf8}.ap-chip b{font-size:9px}.ap-chip span{font-size:9px;color:var(--muted,#6a746f)}.ap-table{overflow:auto;margin-top:12px;border:1px solid var(--line,#dde3df);border-radius:12px}.ap-table table{border-collapse:collapse;width:100%;min-width:880px}.ap-table th,.ap-table td{padding:8px;border-bottom:1px solid #edf0ed;text-align:left;vertical-align:top;font-size:9px}.ap-table th{background:#eef3ef;color:#2b493f}.ap-empty{font-size:9px;color:var(--muted,#6a746f)}@media(max-width:760px){.asset-portfolio-intelligence header{display:block}.asset-portfolio-intelligence header p{margin-top:6px}}
'''
