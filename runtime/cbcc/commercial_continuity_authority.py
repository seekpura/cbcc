from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable
import json

from .commerce_decision_context import (
    compile_commerce_decision_context,
    bind_asset_decision_lineage,
    audit_asset_decision_consumption,
)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _nonempty(value: Any) -> bool:
    if value in (None, '', [], {}):
        return False
    if isinstance(value, dict):
        return any(_nonempty(v) for v in value.values())
    if isinstance(value, list):
        return any(_nonempty(v) for v in value)
    return True


def _merge_context(base: dict[str, Any], supplement: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base or {})
    for key, value in (supplement or {}).items():
        if key == 'lineage_index':
            rows = list(out.get(key) or []) + list(value or [])
            seen = set()
            merged = []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                sig = (row.get('domain'), row.get('source_artifact'), row.get('source_path'))
                if sig in seen:
                    continue
                seen.add(sig)
                merged.append(row)
            out[key] = merged
        elif _nonempty(value):
            if isinstance(value, dict) and isinstance(out.get(key), dict):
                merged = deepcopy(out.get(key))
                for sub_key, sub_value in value.items():
                    if _nonempty(sub_value):
                        merged[sub_key] = deepcopy(sub_value)
                out[key] = merged
            else:
                out[key] = deepcopy(value)
    return out


def wrap_compile_seven_agent_synthesis(fn: Callable[..., dict[str, Any]]):
    """Replace summary-only asset handoff with the real commercial decision payload."""
    def compiled(*args, **kwargs):
        out = fn(*args, **kwargs)
        domain = kwargs.get('domain') if 'domain' in kwargs else (args[0] if args else None)
        architecture = kwargs.get('architecture') if 'architecture' in kwargs else (args[1] if len(args) > 1 else None)
        context = compile_commerce_decision_context(domain=_dict(domain))
        out['asset_input_summary'] = deepcopy(out.get('asset_inputs') or {})
        out['asset_inputs'] = context
        out['commerce_decision_context'] = context
        out['continuity_upgrade'] = 'RICH_PAYLOAD_NOT_STATUS_COUNT_SUMMARY'

        # The compiler passes architecture by reference and later serializes it. Bind rich lineage now so
        # asset compilation cannot silently lose Market/Pricing/Listing/Ads/Review decisions.
        architecture = _dict(architecture)
        for asset in architecture.get('assets') or []:
            if not isinstance(asset, dict):
                continue
            lineage = bind_asset_decision_lineage(asset, context)
            asset['commerce_context'] = lineage
            asset['decision_lineage'] = lineage
            art = asset.get('asset_art_direction')
            if isinstance(art, dict):
                art.setdefault('commercial_decision_basis', {
                    'lineage_refs': deepcopy(lineage.get('lineage_refs') or []),
                    'consumer_question': asset.get('consumer_question'),
                    'purchase_barrier': asset.get('purchase_barrier'),
                    'decision_intent': asset.get('decision_intent'),
                })
                art.setdefault('commercial_continuity_status', 'BOUND_TO_UPSTREAM_DECISION_LINEAGE')
            else:
                asset['commercial_continuity_status'] = 'AGENT_CURATION_DECISION_BINDING_REQUIRED'
        return out
    return compiled


def _argument(args, kwargs, index: int, name: str, default=None):
    if name in kwargs:
        return kwargs.get(name)
    return args[index] if len(args) > index else default


def _commercial_prompt_lines(lineage: dict[str, Any], locale: str) -> list[str]:
    is_cn = locale.upper() == 'CN'
    title = '【商业决策上下文】' if is_cn else '[COMMERCE DECISION CONTEXT]'
    lines = [title]
    positioning = _dict(lineage.get('positioning'))
    proposition = positioning.get('primary_conversion_proposition')
    if proposition:
        lines.append(('核心转化主张：' if is_cn else 'Primary conversion proposition: ') + str(proposition))
    audience = _dict(lineage.get('audience_culture'))
    segments = audience.get('segments') or []
    if segments:
        lines.append(('目标人群 / 区域上下文：' if is_cn else 'Audience / regional context: ') + json.dumps(segments, ensure_ascii=False))
    visual_implications = audience.get('visual_implications') or []
    if visual_implications:
        lines.append(('人群/文化视觉含义：' if is_cn else 'Audience/culture visual implications: ') + json.dumps(visual_implications, ensure_ascii=False))
    market = _dict(lineage.get('market'))
    for key, label_cn, label_en in (
        ('customer_voice', 'Customer Voice：', 'Customer voice: '),
        ('opportunities', '市场机会：', 'Market opportunity: '),
        ('keyword_signals', '搜索/需求信号：', 'Search/demand signal: '),
    ):
        if market.get(key):
            lines.append((label_cn if is_cn else label_en) + json.dumps(market.get(key), ensure_ascii=False))
    race = lineage.get('race') or []
    if race:
        lines.append(('RACE / Journey：' if is_cn else 'RACE / journey: ') + json.dumps(race, ensure_ascii=False))
    listing = _dict(lineage.get('listing'))
    if listing.get('objections'):
        lines.append(('需解决的 Listing 异议：' if is_cn else 'Listing objection to resolve: ') + json.dumps(listing.get('objections'), ensure_ascii=False))
    pricing = _dict(lineage.get('pricing_economics'))
    decision = _dict(pricing.get('pricing_decision'))
    if decision.get('decision') not in (None, ''):
        lines.append(('本资产相关的已选价格 / Offer：' if is_cn else 'Selected price / offer relevant to this asset: ') + str(decision.get('decision')))
        if decision.get('why'):
            lines.append(('价格 / Offer WHY：' if is_cn else 'Price / offer WHY: ') + str(decision.get('why')))
    ads = _dict(lineage.get('ads'))
    if ads.get('diagnosis'):
        lines.append(('广告诊断：' if is_cn else 'Paid-media diagnosis: ') + json.dumps(ads.get('diagnosis'), ensure_ascii=False))
    reviews = _dict(lineage.get('reviews'))
    if reviews.get('issues'):
        lines.append(('评论 / 客服信号：' if is_cn else 'Review / customer-service signal: ') + json.dumps(reviews.get('issues'), ensure_ascii=False))
    lines.append('只消费会改变当前画面/信息层级/证据/文案/场景的商业决策；经济公式、审计状态和无关数据不要堆入画面。' if is_cn else 'Consume only commercial decisions that change this image/frame, information hierarchy, proof, copy or scene. Do not dump accounting formulas, audit states or irrelevant data into the visual.')
    return lines


def wrap_compile_asset_prompt(fn: Callable[..., dict[str, Any]]):
    """Project rich commercial lineage into Design Card + model prompt without deleting visual parameters."""
    def compiled(*args, **kwargs):
        raw_asset = _argument(args, kwargs, 0, 'asset', {})
        asset = deepcopy(raw_asset or {})
        target = _argument(args, kwargs, 2, 'target', {})
        culture = _argument(args, kwargs, 3, 'culture', {})
        strategy = _argument(args, kwargs, 7, 'strategy_authority', {})

        base_context = _dict(asset.get('commerce_context') or asset.get('commerce_decision_context') or asset.get('decision_lineage'))
        strategy_context = compile_commerce_decision_context(
            domain={}, strategy=_dict(strategy), culture=_dict(culture), target=_dict(target), decision_trace={}
        )
        context = _merge_context(base_context, strategy_context)
        lineage = bind_asset_decision_lineage(asset, context)
        asset['commerce_decision_context'] = lineage
        asset['commerce_context'] = lineage
        asset['decision_lineage'] = lineage

        call_args = list(args)
        if call_args:
            call_args[0] = asset
            out = fn(*call_args, **kwargs)
        else:
            call_kwargs = dict(kwargs)
            call_kwargs['asset'] = asset
            out = fn(**call_kwargs)

        card = out.setdefault('design_card', {})
        card['commerce_decision_context'] = deepcopy(lineage)
        card['decision_lineage_refs'] = deepcopy(lineage.get('lineage_refs') or [])

        cn = str(out.get('model_prompt_cn') or out.get('prompt_cn') or '').rstrip()
        en = str(out.get('model_prompt_en') or out.get('prompt_en') or '').rstrip()
        cn_section = '\n'.join(_commercial_prompt_lines(lineage, 'CN'))
        en_section = '\n'.join(_commercial_prompt_lines(lineage, 'EN'))
        if '【商业决策上下文】' not in cn:
            cn = (cn + '\n\n' + cn_section).strip() + '\n'
        if '[COMMERCE DECISION CONTEXT]' not in en:
            en = (en + '\n\n' + en_section).strip() + '\n'
        out['prompt_cn'] = cn
        out['prompt_en'] = en
        out['model_prompt_cn'] = cn
        out['model_prompt_en'] = en

        audit_asset = deepcopy(asset)
        audit_asset['commerce_decision_context'] = lineage
        continuity = audit_asset_decision_consumption(audit_asset, out)
        out['commerce_decision_consumption_audit'] = continuity
        existing = _dict(out.get('prompt_consumption_audit'))
        if existing:
            existing['commerce_decision_continuity'] = continuity
            if continuity.get('status') != 'PASS':
                existing['status'] = 'INCOMPLETE'
                existing['missing_decisions'] = list(dict.fromkeys(list(existing.get('missing_decisions') or []) + ['commerce_decision_continuity']))
            out['prompt_consumption_audit'] = existing
        if continuity.get('status') != 'PASS' and out.get('model_prompt_status') in (None, '', 'PASS', 'READY', 'CANONICAL_PROMPT_COMPILED_AGENT_AUTHORITY'):
            out['model_prompt_status'] = 'MODEL_PROMPT_NEEDS_COMMERCIAL_DECISION_CONSUMPTION'
        return out
    return compiled
