from __future__ import annotations

from typing import Any
import html
import json


def _nonempty(value: Any) -> bool:
    if value in (None, '', [], {}):
        return False
    if isinstance(value, dict):
        return any(_nonempty(v) for v in value.values())
    if isinstance(value, list):
        return any(_nonempty(v) for v in value)
    return True


def _pretty(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value if value is not None else '')


def _block(title: str, subtitle: str, value: Any, key: str) -> str:
    if not _nonempty(value):
        return ''
    return (
        f'<section class="ci-block searchable" data-ci-domain="{html.escape(key)}">'
        f'<header><div><span>{html.escape(subtitle)}</span><h2>{html.escape(title)}</h2></div></header>'
        f'<pre><code>{html.escape(_pretty(value))}</code></pre>'
        '</section>'
    )


def render_commercial_intelligence_workspace(context: dict[str, Any]) -> str:
    """Render operator-facing commercial decision payloads without replacing project-specific views.

    This is a stable v1 work surface, not a machine archive. Only domains with actual payloads appear.
    """
    context = context or {}
    blocks = [
        _block('市场 / 区域 / 人群', 'MARKET · AUDIENCE · CULTURE', {
            'market': context.get('market'),
            'audience_culture': context.get('audience_culture'),
            'positioning': context.get('positioning'),
        }, 'market-audience'),
        _block('价格 / 经济模型 / Offer', 'PRICING · ECONOMICS · OFFER', context.get('pricing_economics'), 'pricing-economics'),
        _block('Search / Listing / Objection', 'SEARCH · LISTING', context.get('listing'), 'listing-search'),
        _block('RACE / Journey', 'RACE · JOURNEY · HANDOFF', {
            'race': context.get('race'),
            'decision_trace': context.get('decision_trace'),
        }, 'race-journey'),
        _block('广告诊断', 'ADS · ATTRIBUTION · ECONOMICS', context.get('ads'), 'ads'),
        _block('评论 / Customer Voice', 'REVIEWS · RETURNS · CS', context.get('reviews'), 'reviews'),
        _block('实验 / Measurement / Revision', 'EXPERIMENT · MEASUREMENT', {
            'experiment': context.get('experiment'),
            'measurement': context.get('measurement'),
        }, 'measurement'),
        _block('决策血缘 / Evidence', 'LINEAGE · SOURCE', context.get('lineage_index'), 'lineage'),
    ]
    blocks = [x for x in blocks if x]
    if not blocks:
        return '<div class="empty">当前项目没有可投影的商业分析 / 决策数据。</div>'
    return (
        '<div class="commercial-intelligence" data-workspace-kind="commercial-intelligence">'
        '<div class="ci-intro"><b>商业决策工作面</b><span>分析 → 决策 → 策展 → 资产 → Prompt 使用同一决策血缘；机器状态不替代真实业务 payload。</span></div>'
        + ''.join(blocks)
        + '</div>'
    )


def commercial_intelligence_css() -> str:
    return '''
.commercial-intelligence{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.ci-intro{grid-column:1/-1;display:flex;justify-content:space-between;gap:18px;align-items:center;padding:14px 16px;border:1px solid var(--line,#dde3df);border-radius:14px;background:#fff}.ci-intro b{font-size:14px}.ci-intro span{font-size:10px;color:var(--muted,#6a746f);max-width:760px}.ci-block{min-width:0;background:#fff;border:1px solid var(--line,#dde3df);border-radius:14px;padding:14px}.ci-block header span{display:block;font-size:9px;color:var(--accent,#23483d);font-weight:800;letter-spacing:.08em}.ci-block h2{font-size:15px;margin:3px 0 10px}.ci-block pre{max-height:520px;margin:0;white-space:pre-wrap;word-break:break-word;font-size:10px;line-height:1.55}@media(max-width:900px){.commercial-intelligence{grid-template-columns:1fr}.ci-intro{display:block}.ci-intro span{display:block;margin-top:5px}}
'''
