from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping
import re


_HUMAN_DIMS = {
    'hair_texture_style': ('hair', 'hair_texture', 'hairstyle'),
    'makeup_grooming': ('makeup', 'grooming', 'makeup_grooming'),
    'wardrobe': ('wardrobe', 'clothing'),
    'body_representation': ('body_type', 'body_representation'),
    'disability_representation': ('disability', 'assistive_device', 'disability_representation'),
    'pose': ('pose',),
    'expression': ('expression',),
    'gaze': ('gaze',),
    'religious_cultural_presentation': ('religious_cultural_presentation', 'cultural_presentation'),
}

_TYPE_DIMS = {
    'family_character': ('family_character', 'family', 'character'),
    'weight': ('weight',),
    'hierarchy': ('hierarchy',),
    'line_breaking': ('line_breaking', 'line_breaks'),
    'relative_scale': ('relative_scale', 'scale'),
    'alignment': ('alignment',),
    'contrast': ('contrast',),
    'safe_zone': ('safe_zone',),
    'mobile_thumbnail_legibility': ('mobile_thumbnail_legibility', 'thumbnail_legibility'),
    'product_geometry_relationship': ('product_geometry_relationship', 'product_relation'),
}


def _present(v: Any) -> bool:
    return v not in (None, '', [], {})


def _first(mapping: Mapping[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if _present(mapping.get(key)):
            return mapping.get(key)
    return None


def _human_applicable(asset: Mapping[str, Any], art: Mapping[str, Any]) -> bool:
    human = art.get('human_context')
    if isinstance(human, Mapping) and any(_present(v) for v in human.values()):
        return True
    if _present(art.get('people')) or _present(art.get('casting')):
        return True
    blob = ' '.join(str(art.get(k) or '') for k in ('subject', 'action', 'decisive_moment')).lower()
    return bool(re.search(r'\b(person|people|adult|woman|man|model|user|hand|hands|face|skin)\b|人物|成人|女性|男性|模特|用户|手部|手|面部|皮肤', blob))


def _visible_copy_required(asset: Mapping[str, Any], art: Mapping[str, Any]) -> bool:
    copy = asset.get('visible_copy') if isinstance(asset.get('visible_copy'), Mapping) else {}
    route = str(copy.get('copy_render_route') or art.get('copy_render_route') or '').upper().strip()
    if route == 'NO_VISIBLE_COPY':
        return False
    return any(_present(copy.get(k)) for k in ('target_copy', 'copy', 'text', 'headline', 'english_baseline', 'chinese_meaning')) or route not in {'', 'NO_VISIBLE_COPY'}


def complete_asset_execution_relevance(asset: Mapping[str, Any]) -> dict[str, Any]:
    out = deepcopy(dict(asset))
    art = deepcopy(out.get('asset_art_direction') if isinstance(out.get('asset_art_direction'), Mapping) else {})
    human = art.get('human_context') if isinstance(art.get('human_context'), Mapping) else {}
    human_needed = _human_applicable(out, art)

    decisions: dict[str, Any] = {}
    existing = art.get('human_relevance_decisions') if isinstance(art.get('human_relevance_decisions'), Mapping) else {}
    for dim, aliases in _HUMAN_DIMS.items():
        if isinstance(existing.get(dim), Mapping) and existing[dim].get('status') and existing[dim].get('why'):
            decisions[dim] = deepcopy(existing[dim])
            continue
        value = _first(human, aliases)
        if not _present(value):
            value = _first(art, aliases)
        if _present(value):
            decisions[dim] = {
                'status': 'SELECTED',
                'why': '该维度已由逐资产 Art Direction 明确选择；生产模型与后期不得静默替换。',
                'execution': deepcopy(value),
            }
        elif human_needed:
            decisions[dim] = {
                'status': 'TO_VERIFY',
                'why': '人物已进入画面，该表征维度必须被显式判断；证据不足时保持待确认，不能让模型默认补成某一身份或审美。',
                'execution': '保持中性，不把缺失信息自动推断为特定族裔、宗教、残障、体型、妆发或行为特征。',
            }
        else:
            decisions[dim] = {
                'status': 'NOT_NEEDED',
                'why': '当前资产没有人物主体，因此该人物表征维度不进入生产执行。',
                'execution': '不添加人物以满足形式上的多元标签。',
            }
    art['human_relevance_decisions'] = decisions

    typography = art.get('typography') if isinstance(art.get('typography'), Mapping) else {}
    existing_type = art.get('typography_contract') if isinstance(art.get('typography_contract'), Mapping) else {}
    type_required = _visible_copy_required(out, art)
    type_contract: dict[str, Any] = {}
    for dim, aliases in _TYPE_DIMS.items():
        if isinstance(existing_type.get(dim), Mapping) and existing_type[dim].get('status') and existing_type[dim].get('why'):
            type_contract[dim] = deepcopy(existing_type[dim])
            continue
        value = _first(typography, aliases)
        if _present(value):
            type_contract[dim] = {
                'status': 'SELECTED',
                'why': '该排版变量已由资产策划选择，必须进入对应文字生产/后期执行。',
                'execution': deepcopy(value),
            }
        elif type_required:
            type_contract[dim] = {
                'status': 'TO_VERIFY',
                'why': '当前资产存在可见文案；该排版变量会影响移动端阅读与商品几何关系，缺失时必须显式保持待确认。',
                'execution': '不得由模型以默认字体、默认换行或默认安全区静默替代策划决策。',
            }
        else:
            type_contract[dim] = {
                'status': 'NOT_NEEDED',
                'why': '当前资产没有可见文案，因此该排版变量不进入本资产生产。',
                'execution': '不为无文案资产添加装饰文字。',
            }
    art['typography_contract'] = type_contract
    out['asset_art_direction'] = art
    return out


def relevance_issues(asset: Mapping[str, Any]) -> list[dict[str, Any]]:
    art = asset.get('asset_art_direction') if isinstance(asset.get('asset_art_direction'), Mapping) else {}
    issues: list[dict[str, Any]] = []
    human = art.get('human_relevance_decisions') if isinstance(art.get('human_relevance_decisions'), Mapping) else {}
    for dim in _HUMAN_DIMS:
        row = human.get(dim) if isinstance(human.get(dim), Mapping) else {}
        if row.get('status') not in {'SELECTED', 'NOT_NEEDED', 'TO_VERIFY'} or not _present(row.get('why')):
            issues.append({'code': 'ASSET_HUMAN_RELEVANCE_DECISION_MISSING', 'asset_id': asset.get('asset_id'), 'dimension': dim})
    typ = art.get('typography_contract') if isinstance(art.get('typography_contract'), Mapping) else {}
    for dim in _TYPE_DIMS:
        row = typ.get(dim) if isinstance(typ.get(dim), Mapping) else {}
        if row.get('status') not in {'SELECTED', 'NOT_NEEDED', 'TO_VERIFY'} or not _present(row.get('why')):
            issues.append({'code': 'ASSET_TYPOGRAPHY_DECISION_MISSING', 'asset_id': asset.get('asset_id'), 'dimension': dim})
    return issues


def wrap_compile_asset_prompt(fn: Callable[..., dict[str, Any]]):
    def compiled(asset: Mapping[str, Any], *args, **kwargs):
        return fn(complete_asset_execution_relevance(asset), *args, **kwargs)
    setattr(compiled, '_cbcc_v0671_asset_execution_relevance', True)
    return compiled


def complete_asset_rows(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [complete_asset_execution_relevance(row) for row in rows]
