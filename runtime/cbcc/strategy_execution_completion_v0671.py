from __future__ import annotations

from copy import deepcopy
from itertools import combinations
from typing import Any, Callable, Mapping
import json


_AXES = ('platform', 'region', 'audience', 'race_ethnicity_culture')
_REQUIRED_INTERSECTION = ('race_ethnicity', 'gender', 'age', 'income', 'geography')


def _d(v: Any) -> dict[str, Any]:
    return dict(v) if isinstance(v, Mapping) else {}


def _l(v: Any) -> list[Any]:
    if v in (None, '', {}):
        return []
    return list(v) if isinstance(v, (list, tuple)) else [v]


def _p(v: Any) -> bool:
    return v not in (None, '', [], {})


def _axis_block(axis: str, decision: str, existing: Any, inherited: Any) -> dict[str, Any]:
    if isinstance(existing, Mapping) and _p(existing.get('why')):
        return deepcopy(dict(existing))
    if _p(existing) and not isinstance(existing, Mapping):
        return {'status': 'AUTHORED_DECISION_CONTEXT', 'why': str(existing), 'basis': 'decision_specific'}
    if isinstance(inherited, Mapping):
        inherited_why = inherited.get('why') or inherited.get('basis')
    else:
        inherited_why = inherited
    labels = {
        'platform': '平台机制/Surface',
        'region': '区域语言、法规、支付物流与节日宗教语境',
        'audience': '购买任务、人群状态与真实摩擦',
        'race_ethnicity_culture': '族裔、语言、宗教与表征/禁忌',
    }
    if _p(inherited_why):
        return {
            'status': 'INHERITED_PROJECT_CONTEXT_REQUIRES_DECISION_CHECK',
            'why': f'{inherited_why}；针对“{decision}”仍需确认该{labels[axis]}是否实际改变决策，不把项目级背景当成自动结论。',
            'basis': 'project_context',
        }
    return {
        'status': 'TO_VERIFY',
        'why': f'待查证{labels[axis]}如何改变“{decision}”；证据不足时不得用通用电商经验或身份刻板印象补结论。',
        'basis': 'missing_decision_specific_evidence',
    }


def _major_decisions(sections: Mapping[str, Any]) -> list[tuple[str, Any, Any]]:
    core = _d(sections.get('04_marketing_core_strategy'))
    vis = _d(sections.get('05_visual_photography_strategy'))
    last = _d(sections.get('09_risk_measurement_priority_next_steps'))
    rows: list[tuple[str, Any, Any]] = []
    candidates = [
        ('定位 / Positioning', core.get('positioning'), _d(core.get('positioning')).get('context_why')),
        ('价值主张 / Value Proposition', core.get('value_proposition'), core.get('value_proposition_context_why')),
        ('信息层级 / Message Hierarchy', core.get('message_hierarchy'), core.get('message_hierarchy_context_why')),
        ('营销框架关系', core.get('framework_relationships'), core.get('framework_context_why')),
        ('Listing 策略', core.get('listing_strategy'), _d(core.get('listing_strategy')).get('context_why')),
        ('视觉与摄影总策略', vis, vis.get('context_why')),
        ('P0/P1/P2 资源取舍', _d(last.get('resource_tradeoff_plan')), _d(last.get('resource_tradeoff_plan')).get('context_why')),
    ]
    for label, value, ctx in candidates:
        if _p(value):
            rows.append((label, value, ctx))
    for i, row in enumerate(_l(sections.get('06_platform_content_matrix'))):
        if not isinstance(row, Mapping):
            continue
        label = f"内容矩阵 {row.get('asset_id') or row.get('platform') or row.get('surface') or i+1} / {row.get('topic') or row.get('hook') or '执行决策'}"
        rows.append((label, row, row.get('context_why')))
    return rows


def _interaction_rows(insight: Mapping[str, Any]) -> list[dict[str, Any]]:
    existing = [deepcopy(dict(x)) for x in _l(insight.get('intersectionality_interaction_analysis')) if isinstance(x, Mapping)]
    if existing:
        return existing
    source = [x for x in _l(insight.get('intersectionality_table')) if isinstance(x, Mapping)]
    dims: list[str] = []
    basis = 'TO_VERIFY'
    guard = '不得把身份组合直接推断为需求、消费能力、价格敏感或生活方式。'
    for row in source:
        for dim in _l(row.get('dimensions')):
            d = str(dim)
            if d and d not in dims:
                dims.append(d)
        if _p(row.get('evidence_or_assumption')):
            basis = row.get('evidence_or_assumption')
        if _p(row.get('stereotype_guard')):
            guard = str(row.get('stereotype_guard'))
    for required in _REQUIRED_INTERSECTION:
        if required not in dims:
            dims.append(required)
    # Interaction rows are verification programs, not demographic claims. This avoids inventing causal
    # behavior while still forcing the Agent to reason about intersections instead of listing five labels.
    pairs = list(combinations(dims[:5], 2))[:6]
    rows = []
    for a, b in pairs:
        rows.append({
            'dimensions': [a, b],
            'status': 'TO_VERIFY_INTERACTION' if str(basis).upper() in {'TO_VERIFY', 'ASSUMPTION', 'MISSING_INPUT'} else 'EVIDENCE_LED_INTERACTION_CHECK',
            'mechanism': f'验证 {a} × {b} 是否通过语言、可达性、支付物流、场景、价格感知、内容理解或表征风险等可观察机制改变购买任务；不从身份本身推断行为。',
            'evidence_or_assumption': deepcopy(basis),
            'stereotype_guard': guard,
            'execution': '只有被当前目标市场证据支持的交叉影响才进入选角、文案、Offer、渠道或视觉执行；其余维持中性并显式待确认。',
            'verification_action': '使用目标市场当前来源、native/cultural review、用户/评论信号或分层实验验证具体机制，并记录是否需要修改责任层。',
        })
    return rows


def complete_strategy_execution_v0671(strategy: Mapping[str, Any], request: Mapping[str, Any] | None = None) -> dict[str, Any]:
    out = deepcopy(dict(strategy))
    mode = str(_d(out.get('human_projection')).get('mode') or out.get('delivery_mode') or out.get('scope_mode') or '').upper()
    if mode != 'FULL':
        return out
    sections = out.setdefault('sections', {})
    insight = _d(sections.get('03_platform_region_audience_culture_insight'))
    source_context = _d(insight.get('context_why') or insight.get('platform_region_audience_culture_why'))
    core = _d(sections.get('04_marketing_core_strategy'))

    decision_rows = []
    for label, value, existing_ctx in _major_decisions(sections):
        existing = _d(existing_ctx)
        ctx = {axis: _axis_block(axis, label, existing.get(axis), source_context.get(axis)) for axis in _AXES}
        decision_rows.append({
            'decision': label,
            'decision_value': deepcopy(value),
            'context_why': ctx,
            'measurement': _d(value).get('measurement') if isinstance(value, Mapping) else None,
            'principle': '四轴 WHY 是该决策的语境消费记录；缺少决策级证据时明确 TO_VERIFY，不复制项目背景冒充因果结论。',
        })
    core['major_decision_context_why'] = decision_rows
    sections['04_marketing_core_strategy'] = core

    insight['intersectionality_interaction_analysis'] = _interaction_rows(insight)
    sections['03_platform_region_audience_culture_insight'] = insight
    out['strategy_execution_completion_v0671'] = {
        'status': 'COMPLETED_WITH_EXPLICIT_UNKNOWNS',
        'major_decision_four_axis_why': True,
        'intersectionality_interaction_analysis': True,
        'principle': '重大策略逐条消费平台/区域/人群/族裔文化语境；交叉性必须分析交互机制或明确验证任务，而不是只列身份维度。',
    }
    return out


def completion_issues_v0671(strategy: Mapping[str, Any]) -> list[dict[str, Any]]:
    mode = str(_d(strategy.get('human_projection')).get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '').upper()
    if mode != 'FULL':
        return []
    sections = _d(strategy.get('sections'))
    issues: list[dict[str, Any]] = []
    core = _d(sections.get('04_marketing_core_strategy'))
    major = [x for x in _l(core.get('major_decision_context_why')) if isinstance(x, Mapping)]
    expected = len(_major_decisions(sections))
    if expected and len(major) < expected:
        issues.append({'code': 'FULL_MAJOR_DECISION_CONTEXT_WHY_MISSING_V0671', 'expected': expected, 'actual': len(major)})
    for i, row in enumerate(major):
        ctx = _d(row.get('context_why'))
        missing = [axis for axis in _AXES if not _p(_d(ctx.get(axis)).get('why'))]
        if missing:
            issues.append({'code': 'FULL_MAJOR_DECISION_CONTEXT_WHY_SHALLOW_V0671', 'row': i, 'fields': missing})

    insight = _d(sections.get('03_platform_region_audience_culture_insight'))
    interactions = [x for x in _l(insight.get('intersectionality_interaction_analysis')) if isinstance(x, Mapping)]
    if len(interactions) < 3:
        issues.append({'code': 'FULL_INTERSECTIONALITY_INTERACTION_ANALYSIS_MISSING_V0671', 'count': len(interactions)})
    for i, row in enumerate(interactions):
        dims = _l(row.get('dimensions'))
        missing = [k for k in ('mechanism', 'evidence_or_assumption', 'stereotype_guard', 'execution', 'verification_action') if not _p(row.get(k))]
        if len(dims) < 2:
            missing.append('dimensions>=2')
        if missing:
            issues.append({'code': 'FULL_INTERSECTIONALITY_INTERACTION_ROW_SHALLOW_V0671', 'row': i, 'fields': missing})
    return issues


def wrap_build_master_strategy(fn: Callable[..., dict[str, Any]]):
    def built(request: dict[str, Any], *args, **kwargs):
        return complete_strategy_execution_v0671(fn(request, *args, **kwargs), request)
    setattr(built, '_cbcc_v0671_strategy_execution_completion', True)
    return built


def wrap_render_master_strategy_cn(fn: Callable[[dict[str, Any]], str]):
    def rendered(strategy: dict[str, Any]) -> str:
        base = fn(strategy)
        mode = str(_d(strategy.get('human_projection')).get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '').upper()
        if mode != 'FULL':
            return base
        sections = _d(strategy.get('sections'))
        core = _d(sections.get('04_marketing_core_strategy'))
        insight = _d(sections.get('03_platform_region_audience_culture_insight'))
        lines = ['', '### v0.6.71 重大决策四轴 Context WHY', '']
        for row in _l(core.get('major_decision_context_why')):
            if isinstance(row, Mapping):
                lines += [f"#### {row.get('decision')}", '```json', json.dumps(row.get('context_why') or {}, ensure_ascii=False, indent=2), '```', '']
        lines += ['### v0.6.71 交叉性 Interaction Analysis', '']
        for row in _l(insight.get('intersectionality_interaction_analysis')):
            if isinstance(row, Mapping):
                lines += [f"- **{' × '.join(str(x) for x in _l(row.get('dimensions')))}**：{row.get('mechanism')}｜依据/状态：{row.get('evidence_or_assumption')}｜执行：{row.get('execution')}｜验证：{row.get('verification_action')}"]
        return base.rstrip() + '\n' + '\n'.join(lines) + '\n'
    setattr(rendered, '_cbcc_v0671_strategy_execution_completion', True)
    return rendered
