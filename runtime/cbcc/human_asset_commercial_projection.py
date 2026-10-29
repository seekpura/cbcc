from __future__ import annotations

from typing import Any, Callable
import json


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _short(value: Any, limit: int = 1000) -> str:
    if value in (None, '', [], {}):
        return '—'
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)
    return text if len(text) <= limit else text[:limit].rstrip() + '…'


def _line(label: str, value: Any) -> str:
    if value in (None, '', [], {}):
        return ''
    return f'- **{label}**：{_short(value)}'


def _commercial_section(prompt_bundle: dict[str, Any]) -> str:
    card = _dict(prompt_bundle.get('design_card'))
    ctx = _dict(card.get('commerce_decision_context'))
    if not ctx:
        return ''
    rows = ['## 上游商业决策与血缘', '', '> 本资产只继承与当前购买问题、Surface、RACE 和商业任务相关的上游决策；未绑定的数据不会为了“显得完整”塞进画面。', '']

    positioning = _dict(ctx.get('positioning'))
    rows += [x for x in [
        _line('核心转化主张', positioning.get('primary_conversion_proposition')),
        _line('目标用户', positioning.get('target_user')),
        _line('信息层级', positioning.get('message_hierarchy')),
    ] if x]

    audience = _dict(ctx.get('audience_culture'))
    rows += [x for x in [
        _line('区域 / 平台上下文', audience.get('target')),
        _line('目标人群', audience.get('segments')),
        _line('文化 / 交叉性', audience.get('intersectionality')),
        _line('视觉执行含义', audience.get('visual_implications')),
        _line('人物 / 场景边界', audience.get('casting_constraints') or audience.get('taboo_stereotype_risks')),
    ] if x]

    market = _dict(ctx.get('market'))
    rows += [x for x in [
        _line('市场价格带', market.get('price_bands')),
        _line('价格洼地 / 空白信号', market.get('price_valleys') or market.get('price_valley_signals')),
        _line('需求 / 搜索信号', market.get('demand_signals') or market.get('keyword_signals') or market.get('search_intent')),
        _line('Customer Voice', market.get('customer_voice')),
        _line('市场机会', market.get('opportunities')),
    ] if x]

    pricing = _dict(ctx.get('pricing_economics'))
    decision = _dict(pricing.get('pricing_decision'))
    rows += [x for x in [
        _line('本资产相关 Pricing / Offer 决策', decision.get('decision')),
        _line('Pricing / Offer WHY', decision.get('why')),
        _line('经济边界', pricing.get('offer_boundaries') or pricing.get('offer_bundle_discount_boundary')),
    ] if x]

    rows += [x for x in [
        _line('RACE / Journey', ctx.get('race')),
        _line('Listing / Search 异议', _dict(ctx.get('listing')).get('objections')),
        _line('Paid Media 诊断', _dict(ctx.get('ads')).get('diagnosis')),
        _line('Review / Customer Service 信号', _dict(ctx.get('reviews')).get('issues')),
        _line('衡量 / 下一动作', ctx.get('measurement')),
    ] if x]

    refs = ctx.get('lineage_refs') or []
    if refs:
        rows += ['', '### 来源血缘', '']
        for ref in refs:
            if isinstance(ref, dict):
                rows.append(f'- `{ref.get("domain")}` ← `{ref.get("source_artifact")}` · `{ref.get("source_path")}`')
    rows += ['', '### 消费边界', '', '- 商业决策影响当前资产的购买问题、信息层级、文案、证据、场景或 Offer；摄影/灯光/CMF 与空间参数仍由本资产 Art Direction / Production Parameter Closure 独立闭环。', '- 经济公式、Runtime 状态码、无关工具数据进入 Inspector / Assembly，不进入消费者可见画面。', '']
    return '\n'.join(rows)


def wrap_human_asset_design_card(fn: Callable[..., str]):
    def rendered(asset, prompt_bundle, language_contract, *args, **kwargs):
        base = fn(asset, prompt_bundle, language_contract, *args, **kwargs)
        section = _commercial_section(prompt_bundle)
        if not section:
            return base
        marker = '\n## Model Prompt CN'
        if marker in base:
            return base.replace(marker, '\n\n' + section + '\n' + marker, 1)
        return base.rstrip() + '\n\n' + section + '\n'
    return rendered
