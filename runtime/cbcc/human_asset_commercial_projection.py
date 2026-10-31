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
    subject = _dict(card.get('subject_system'))
    if not ctx and not subject:
        return ''
    rows = ['## 上游商业决策、主体系统与血缘', '', '> 本资产只继承与当前购买问题、Surface、RACE 和商业任务相关的上游决策；未绑定的数据不会为了“显得完整”塞进画面。主体按资产任务决定，不默认人物。', '']

    if subject:
        rows += [
            '### 主体系统（Subject Presence System）', '',
            _line('主体类型', subject.get('subject_type')),
            _line('主主体', subject.get('primary_subject')),
            _line('次主体', subject.get('secondary_subjects')),
            _line('主体动作', subject.get('action')),
            _line('主体与商品关系', subject.get('subject_product_relationship')),
            _line('主体与场景关系', subject.get('subject_scene_relationship')),
            _line('主体约束', subject.get('subject_constraints')),
            _line('主体决策权威', subject.get('authority')),
            '',
        ]
        rows = [x for x in rows if x != ''] + ['']

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
        _line('主体 / 场景边界', audience.get('casting_constraints') or audience.get('taboo_stereotype_risks')),
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
    rows += ['', '### 消费边界', '', '- 商业决策影响当前资产的购买问题、信息层级、文案、证据、场景或 Offer；主体系统、摄影/灯光/CMF 与空间参数仍由本资产 Art Direction / Production Parameter Closure 独立闭环。', '- 人、动物、植物、商品/物体、环境、复合主体或无主体都是合法逐资产选择；Runtime 不从类目自动补人物。', '- 经济公式、Runtime 状态码、无关工具数据进入 Inspector / Assembly，不进入消费者可见画面。', '']
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


# Late bootstrap hook: this module is imported at the end of commercial_continuity_bootstrap.install(),
# after v0.6.70/v0.6.71/v0.6.72 prompt/package/Human wrappers are already installed. This prevents
# v0.6.73 from freezing an intermediate strategy or compiler authority.
from .final_export_closure_v0673 import install as _install_v0673_final_export_closure
_install_v0673_final_export_closure()
