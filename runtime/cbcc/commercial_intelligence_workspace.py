from __future__ import annotations

from typing import Any
import html
import json


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    if value in (None, '', {}):
        return []
    return value if isinstance(value, list) else [value]


def _nonempty(value: Any) -> bool:
    if value in (None, '', [], {}):
        return False
    if isinstance(value, dict):
        return any(_nonempty(v) for v in value.values())
    if isinstance(value, list):
        return any(_nonempty(v) for v in value)
    return True


def _text(value: Any, limit: int = 820) -> str:
    if value in (None, '', [], {}):
        return '—'
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    value = str(value)
    return value if len(value) <= limit else value[:limit].rstrip() + '…'


def _metric(label: str, value: Any, note: str = '') -> str:
    if value in (None, '', [], {}):
        return ''
    return (
        '<div class="ci-metric">'
        f'<span>{html.escape(label)}</span><b>{html.escape(_text(value, 180))}</b>'
        + (f'<small>{html.escape(note)}</small>' if note else '')
        + '</div>'
    )


def _facts(title: str, kicker: str, rows: list[tuple[str, Any]], key: str) -> str:
    body = ''.join(
        f'<div class="ci-fact"><span>{html.escape(label)}</span><div>{html.escape(_text(value))}</div></div>'
        for label, value in rows if _nonempty(value)
    )
    if not body:
        return ''
    return (
        f'<section class="ci-block searchable" data-ci-domain="{html.escape(key)}">'
        f'<header><span>{html.escape(kicker)}</span><h2>{html.escape(title)}</h2></header>'
        f'<div class="ci-facts">{body}</div></section>'
    )


def _rows_table(headers: list[str], rows: list[list[Any]], empty: str = '') -> str:
    if not rows:
        return f'<div class="ci-empty">{html.escape(empty)}</div>' if empty else ''
    th = ''.join(f'<th>{html.escape(x)}</th>' for x in headers)
    tr = []
    for row in rows:
        tr.append('<tr>' + ''.join(f'<td>{html.escape(_text(value, 360))}</td>' for value in row) + '</tr>')
    return f'<div class="ci-table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{"".join(tr)}</tbody></table></div>'


def _market_block(context: dict[str, Any]) -> str:
    market = _dict(context.get('market'))
    audience = _dict(context.get('audience_culture'))
    positioning = _dict(context.get('positioning'))
    if not any(map(_nonempty, (market, audience, positioning))):
        return ''
    metrics = ''.join([
        _metric('市场 / 平台', _dict(audience.get('target')).get('market') or _dict(audience.get('target')).get('site')),
        _metric('核心转化主张', positioning.get('primary_conversion_proposition')),
        _metric('价格带', market.get('price_bands')),
        _metric('价格洼地', market.get('price_valleys') or market.get('price_valley_signals')),
    ])
    facts = _facts('市场 / 区域 / 人群', 'MARKET · AUDIENCE · CULTURE', [
        ('目标人群', audience.get('segments')),
        ('Customer Voice', market.get('customer_voice')),
        ('需求 / 搜索信号', market.get('demand_signals') or market.get('keyword_signals') or market.get('search_intent')),
        ('市场机会', market.get('opportunities')),
        ('竞争模式', market.get('competitor_patterns') or market.get('competitor_summary')),
        ('文化 / 交叉性', audience.get('intersectionality') or audience.get('race_ethnicity')),
        ('视觉执行含义', audience.get('visual_implications')),
        ('Copy 执行含义', audience.get('copy_implications')),
        ('人物 / 刻板印象边界', audience.get('casting_constraints') or audience.get('taboo_stereotype_risks')),
    ], 'market-audience')
    return f'<section class="ci-zone ci-zone-wide"><div class="ci-zone-head"><div><span>01</span><h2>市场与受众决策</h2></div></div><div class="ci-metrics">{metrics}</div>{facts}</section>'


def _pricing_block(context: dict[str, Any]) -> str:
    pricing = _dict(context.get('pricing_economics'))
    if not _nonempty(pricing):
        return ''
    decision = _dict(pricing.get('pricing_decision'))
    scenarios = []
    for row in _list(pricing.get('scenarios')):
        if isinstance(row, dict):
            scenarios.append([
                row.get('scenario_id'), row.get('sku'), row.get('price'), row.get('contribution_before_ads'),
                row.get('contribution_margin_rate_before_ads'), row.get('break_even_cpa'), row.get('break_even_cpc'),
                row.get('break_even_roas'), row.get('status'),
            ])
    metrics = ''.join([
        _metric('Pricing Decision', decision.get('decision'), decision.get('status') or ''),
        _metric('Currency', pricing.get('currency')),
        _metric('Price Bands', pricing.get('price_bands') or pricing.get('market_price_bands')),
        _metric('Price Valleys', pricing.get('price_valleys') or pricing.get('market_price_valleys')),
    ])
    decision_html = _facts('Pricing Decision + WHY', 'STRATEGY DECISION', [
        ('决策', decision.get('decision')),
        ('WHY', decision.get('why')),
        ('Tradeoff', decision.get('tradeoff')),
        ('SKU Roles', pricing.get('sku_roles')),
        ('Offer / Bundle / Discount Boundary', pricing.get('offer_boundaries') or pricing.get('offer_bundle_discount_boundary')),
        ('缺失输入', pricing.get('missing_inputs')),
    ], 'pricing-decision')
    table = _rows_table(
        ['Scenario', 'SKU', 'Price', 'Contribution', 'Margin', 'BE CPA', 'BE CPC', 'BE ROAS', 'Status'],
        scenarios,
        '当前没有可计算 Scenario；缺失输入保持 MISSING_INPUT。',
    )
    return (
        '<section class="ci-zone ci-zone-wide"><div class="ci-zone-head"><div><span>02</span><h2>价格 / 经济模型 / Offer</h2></div>'
        '<small>市场价格证据 ≠ 自动定价建议；只显示显式输入与可追溯计算。</small></div>'
        f'<div class="ci-metrics">{metrics}</div>{decision_html}{table}</section>'
    )


def _race_listing_block(context: dict[str, Any]) -> str:
    race = _list(context.get('race'))
    listing = _dict(context.get('listing'))
    traces = _list(context.get('decision_trace'))
    if not any(map(_nonempty, (race, listing, traces))):
        return ''
    race_rows = []
    for row in race:
        if isinstance(row, dict):
            race_rows.append([
                row.get('stage'), row.get('objective'), row.get('action') or row.get('execution'),
                row.get('surface') or row.get('channel'), row.get('handoff'), row.get('kpi') or row.get('metric'),
            ])
    race_table = _rows_table(['Stage', 'Objective', 'Action', 'Surface', 'Handoff', 'KPI'], race_rows)
    listing_html = _facts('Search / Listing / Objection', 'LISTING · SEARCH', [
        ('关键词 / Search Intent', listing.get('keywords')),
        ('转化结构', listing.get('conversion_architecture')),
        ('待解决异议', listing.get('objections')),
        ('Final Copy 状态', listing.get('final_copy_status')),
        ('Decision Trace', traces),
    ], 'listing-search')
    return f'<section class="ci-zone"><div class="ci-zone-head"><div><span>03</span><h2>RACE / Journey / Listing</h2></div></div>{race_table}{listing_html}</section>'


def _signal_block(title: str, kicker: str, data: dict[str, Any], fields: list[tuple[str, str]], key: str, index: str) -> str:
    if not _nonempty(data):
        return ''
    body = _facts(title, kicker, [(label, data.get(field)) for label, field in fields], key)
    return f'<section class="ci-zone"><div class="ci-zone-head"><div><span>{index}</span><h2>{html.escape(title)}</h2></div></div>{body}</section>' if body else ''


def _lineage_block(context: dict[str, Any]) -> str:
    rows = []
    for item in _list(context.get('lineage_index')):
        if isinstance(item, dict):
            rows.append([item.get('domain'), item.get('source_artifact'), item.get('source_path'), item.get('payload_present')])
    if not rows:
        return ''
    return (
        '<section class="ci-zone ci-zone-wide"><div class="ci-zone-head"><div><span>07</span><h2>Decision Lineage / Evidence</h2></div>'
        '<small>下游资产必须能追到真实上游来源；文件存在不等于被消费。</small></div>'
        + _rows_table(['Domain', 'Source Artifact', 'Source Path', 'Payload'], rows)
        + '</section>'
    )


def render_commercial_intelligence_workspace(context: dict[str, Any]) -> str:
    """Render real operator objects, not a raw JSON archive."""
    context = context or {}
    blocks = [
        _market_block(context),
        _pricing_block(context),
        _race_listing_block(context),
        _signal_block('广告诊断', 'ADS · ATTRIBUTION · ECONOMICS', _dict(context.get('ads')), [
            ('诊断', 'diagnosis'), ('P0/P1/P2 / Priority', 'priority_actions'), ('经济约束', 'economics_context'),
        ], 'ads', '04'),
        _signal_block('评论 / Customer Voice', 'REVIEWS · RETURNS · CS', _dict(context.get('reviews')), [
            ('问题 / 主题', 'issues'), ('聚类', 'themes'), ('正向卖点', 'positive_selling_points'), ('最小修订路由', 'local_revision_routes'),
        ], 'reviews', '05'),
        _signal_block('实验 / Measurement / Revision', 'EXPERIMENT · MEASUREMENT', {
            'experiment': context.get('experiment'), 'measurement': context.get('measurement')
        }, [('Experiment', 'experiment'), ('Measurement / Next Action', 'measurement')], 'measurement', '06'),
        _lineage_block(context),
    ]
    blocks = [x for x in blocks if x]
    if not blocks:
        return '<div class="empty">当前项目没有可投影的商业分析 / 决策数据。</div>'
    return (
        '<div class="commercial-intelligence" data-workspace-kind="commercial-intelligence">'
        '<div class="ci-intro"><div><b>商业决策工作面</b><span>Source → Analysis → Decision → Strategy → Curation → Asset → Prompt → Measurement</span></div>'
        '<p>这里展示运营真正需要做判断的数据；Runtime 状态、内部 hash 和工程追踪留在 Inspector。</p></div>'
        + ''.join(blocks) + '</div>'
    )


def commercial_intelligence_css() -> str:
    return '''
.commercial-intelligence{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.ci-intro{grid-column:1/-1;display:flex;justify-content:space-between;gap:20px;align-items:flex-start;padding:16px 18px;border:1px solid var(--line,#dde3df);border-radius:16px;background:#fff}.ci-intro b{display:block;font-size:15px}.ci-intro span,.ci-intro p{font-size:10px;color:var(--muted,#6a746f);margin:4px 0 0;max-width:760px}.ci-zone{min-width:0;background:#f8faf8;border:1px solid var(--line,#dde3df);border-radius:16px;padding:14px}.ci-zone-wide{grid-column:1/-1}.ci-zone-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;margin-bottom:10px}.ci-zone-head>div{display:flex;align-items:center;gap:8px}.ci-zone-head span{font:800 9px ui-monospace,monospace;color:var(--accent,#23483d)}.ci-zone-head h2{font-size:16px;margin:0}.ci-zone-head small{font-size:9px;color:var(--muted,#6a746f);max-width:520px}.ci-metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;margin:0 0 10px}.ci-metric{background:#fff;border:1px solid var(--line,#dde3df);border-radius:12px;padding:10px}.ci-metric span{display:block;font-size:8px;color:var(--muted,#6a746f);text-transform:uppercase;letter-spacing:.05em}.ci-metric b{display:block;font-size:13px;margin-top:4px;word-break:break-word}.ci-metric small{display:block;margin-top:4px;color:var(--muted,#6a746f);font-size:8px}.ci-block{background:#fff;border:1px solid var(--line,#dde3df);border-radius:12px;padding:12px;margin-top:8px}.ci-block header span{display:block;font-size:8px;color:var(--accent,#23483d);font-weight:800;letter-spacing:.06em}.ci-block h2{font-size:13px;margin:2px 0 8px}.ci-fact{display:grid;grid-template-columns:minmax(120px,.32fr) minmax(0,1fr);gap:10px;padding:8px 0;border-top:1px solid #edf0ed}.ci-fact:first-child{border-top:0}.ci-fact>span{font-size:9px;color:var(--muted,#6a746f)}.ci-fact>div{font-size:10px;word-break:break-word;white-space:pre-wrap}.ci-table-wrap{overflow:auto;background:#fff;border:1px solid var(--line,#dde3df);border-radius:12px}.ci-table-wrap table{border-collapse:collapse;width:100%;min-width:760px}.ci-table-wrap th,.ci-table-wrap td{padding:8px 9px;border-bottom:1px solid #edf0ed;text-align:left;vertical-align:top;font-size:9px}.ci-table-wrap th{background:#eef3ef;color:#2b493f}.ci-empty{padding:12px;border:1px dashed var(--line,#dde3df);background:#fff;border-radius:10px;font-size:10px;color:var(--muted,#6a746f)}@media(max-width:900px){.commercial-intelligence{grid-template-columns:1fr}.ci-zone-wide{grid-column:auto}.ci-intro{display:block}.ci-fact{grid-template-columns:1fr;gap:3px}}
'''
