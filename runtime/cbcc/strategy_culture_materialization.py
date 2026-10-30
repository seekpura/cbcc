from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Callable, Mapping

from .delivery_contract import normalize_evidence_grade, publication_rule


REQUIRED_INTERSECTION_DIMENSIONS = ['race_ethnicity', 'gender', 'age', 'income', 'geography']
FRAMEWORK_ORDER = ('RACE', 'STP', 'JTBD', 'AIDA', 'FABE', '4P', 'FUNNEL')
RACE_ORDER = ('RESEARCH', 'ACTION', 'COMMUNICATION', 'EVALUATION')
SELF_CHECK_ORDER = ('fabrication', 'why', 'culture', 'compliance', 'metric', 'assumption')


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _l(value: Any) -> list[Any]:
    if value in (None, '', {}):
        return []
    return value if isinstance(value, list) else [value]


def _p(value: Any) -> bool:
    return value not in (None, '', [], {})


def _refs(row: Mapping[str, Any]) -> list[str]:
    values = row.get('source_refs') or row.get('source_ids') or row.get('evidence_refs') or row.get('evidence') or []
    return [str(x) for x in _l(values) if _p(x)]


def _grade(row: Mapping[str, Any]) -> str:
    explicit = str(row.get('evidence_grade') or row.get('evidence_level') or '').strip().upper()
    if explicit in {'A', 'B', 'C'}:
        return explicit
    subjective = any(
        token in str(row.get(key) or '').upper()
        for key in ('classification', 'type', 'status', 'evidence_level')
        for token in ('SUBJECTIVE', 'UGC', 'SENSORY', 'HYPOTHESIS', 'EXPERIENCE')
    )
    source_type = ' '.join(_refs(row))
    return normalize_evidence_grade(explicit, source_type=source_type, subjective=subjective)


def _product_truth_rows(section: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in _l(section.get('product_facts')):
        if not isinstance(raw, dict):
            continue
        grade = _grade(raw)
        item = str(raw.get('fact') or raw.get('item') or raw.get('name') or 'PRODUCT_FACT')
        refs = _refs(raw)
        rows.append({
            'item': item,
            'fact_or_claim': raw.get('value') if _p(raw.get('value')) else item,
            'real_selling_point': raw.get('real_selling_point') or raw.get('selling_point') or '仅当该事实改变购买决策时升级为真实卖点。',
            'perceived_benefit': raw.get('perceived_benefit') or '需由真实购买问题翻译，不从事实直接跳成功效。',
            'emotional_value': raw.get('emotional_value') or '只有在功能/感知利益真实支撑时才使用，不自动添加。',
            'non_claimable': raw.get('claim_boundary') or '可以陈述事实本身；更强效果、比较、时长或安全性需要独立证据。',
            'evidence_grade': grade,
            'source_refs': refs,
            'publication_rule': publication_rule(grade),
            'basis': refs or [raw.get('evidence_level') or raw.get('publication_status') or 'USER_SUPPLIED_OR_PROJECT_TRUTH'],
            'tradeoff': '保留事实强度；不为了营销力度把规格/配方事实外推成未验证功效。',
        })
    for raw in _l(section.get('claim_value_ladder')):
        if not isinstance(raw, dict):
            continue
        grade = _grade(raw)
        item = str(raw.get('claim') or raw.get('item') or raw.get('claim_id') or 'CLAIM')
        refs = _refs(raw)
        rule = publication_rule(grade)
        non_claimable = raw.get('claim_boundary') or (
            'C级仅可作为主观体验/待验证假设，不得作硬宣称。'
            if grade == 'C'
            else '不得超出当前证据支持的范围、时长、比较或结果强度。'
        )
        rows.append({
            'item': item,
            'fact_or_claim': item,
            'real_selling_point': raw.get('real_selling_point') or ('待验证，不作为硬卖点。' if grade == 'C' else item),
            'perceived_benefit': raw.get('perceived_benefit') or raw.get('consumer_value') or '用消费者语言解释与购买问题的关系，并保持证据边界。',
            'emotional_value': raw.get('emotional_value') or '只有当已支持利益足以支撑安心、便利或信心时才升级。',
            'non_claimable': non_claimable,
            'evidence_grade': grade,
            'source_refs': refs,
            'publication_rule': rule,
            'basis': refs or [raw.get('evidence_level') or raw.get('publication_status') or 'TO_VERIFY'],
            'tradeoff': (
                '保留为体验/假设和测试语言，不进入硬宣称、核心功效或确定性结果。'
                if grade == 'C'
                else '按当前证据强度使用；不以更激进措辞换取短期点击。'
            ),
        })
    return rows


def _assumption_decision_rows(info: dict[str, Any], truth_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in truth_rows:
        rows.append({
            'type': 'FACT_OR_CLAIM',
            'item': row.get('item'),
            'status': row.get('evidence_grade'),
            'basis': row.get('basis'),
            'tradeoff': row.get('tradeoff'),
        })
    for raw in _l(info.get('assumptions')):
        if isinstance(raw, dict):
            item = raw.get('assumption') or raw.get('item') or raw.get('text')
            status = raw.get('status') or 'ASSUMPTION'
            basis = raw.get('basis') or raw.get('source_refs') or '当前缺少足够事实来源，仅作为继续工作的显式假设。'
            tradeoff = raw.get('tradeoff') or '可用于规划，不得静默升级成事实；影响发布/预算/合规前必须补证据。'
        else:
            item, status, basis, tradeoff = raw, 'ASSUMPTION', '显式假设', '不作为公开事实。'
        rows.append({'type': 'ASSUMPTION', 'item': item, 'status': status, 'basis': basis, 'tradeoff': tradeoff})
    for raw in _l(info.get('decision_log')):
        if not isinstance(raw, dict):
            continue
        rows.append({
            'type': 'DECISION',
            'item': raw.get('what') or raw.get('decision') or '策略决策',
            'status': 'DECIDED_UNDER_CURRENT_EVIDENCE',
            'basis': raw.get('evidence') or raw.get('why') or 'CURRENT_PROJECT_EVIDENCE',
            'tradeoff': raw.get('tradeoff') or '保留能改变当前商业结果的动作，未知发布敏感项保持待查证。',
        })
    return rows


def _intersectionality(section: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [deepcopy(x) for x in _l(section.get('intersectionality_table')) if isinstance(x, dict)]
    if not rows:
        rows = [{
            'dimensions': list(REQUIRED_INTERSECTION_DIMENSIONS),
            'implication': '当前交叉性证据不足，不能用单一族裔/性别/年龄/收入/地域标签代替完整受众。',
            'evidence_or_assumption': 'TO_VERIFY',
            'stereotype_guard': '不从身份组合直接推断肤质、价格敏感、购买能力、购买意愿或生活方式。',
            'execution': '先采用中性、包容的语言/表征；当人物或文化语境影响购买机制时再补目标市场证据。',
        }]
    for row in rows:
        dims = [str(x) for x in _l(row.get('dimensions'))]
        for required in REQUIRED_INTERSECTION_DIMENSIONS:
            if required not in dims:
                dims.append(required)
        row['dimensions'] = dims
        row.setdefault('implication', '只采用有证据的表征、语言、场景或可达性含义。')
        row.setdefault('evidence_or_assumption', 'TO_VERIFY')
        row.setdefault('stereotype_guard', '不得把身份组合直接推断为消费行为。')
        row.setdefault('execution', '把可验证含义落实到选角、场景、语言与可达性；其余保持中性。')
    return rows


def _frameworks(core: dict[str, Any]) -> dict[str, dict[str, Any]]:
    existing = _d(core.get('framework_relationships'))
    roles = {
        'RACE': ('传播流程骨架：Research → Action → Communication → Evaluation。', '用户明确要求RACE作为传播骨架；它组织流程而不替代策略判断。', '不把RACE当渠道清单；每阶段必须有真实输入、输出和指标。', '物化RACE执行表并让内容矩阵标注RACE阶段。'),
        'STP': ('确定细分、优先目标与定位。', '基于市场/人群证据选择真正值得优先的细分。', '不把人口标签当购买动机；证据不足的细分保持待验证。', '把目标细分连接到定位、消息层级、渠道和资产任务。'),
        'JTBD': ('把受众标签还原成购买任务、阻力和进步需求。', '购买行为需要由任务/障碍解释，而不是由族裔或人口属性直接推断。', '不强行给所有人同一个Job；按真实购买问题拆分。', '让资产、Listing和内容逐项回答消费者问题。'),
        'AIDA': ('在需要注意→兴趣→欲望→行动的内容中组织说服顺序。', '适用于明确需要顺序推进的广告/视频/页面段落。', '不把每张图都套四步；单资产只承担必要阶段。', '按当前Surface选择需要的AIDA阶段和CTA。'),
        'FABE': ('把Feature连接Advantage/Benefit/Evidence。', '避免只堆成分、参数或空泛利益。', 'Benefit/Evidence不能超过Product Truth证据强度。', '用于Claim、Listing、证据资产和脚本中的事实→利益→证据转换。'),
        '4P': ('协调Product / Price / Place / Promotion商业取舍。', '产品、价格、渠道和传播必须共同满足当前商业目标。', '缺单位经济时不凭竞品均价下定价结论。', '把SKU/Offer、平台、价格输入和传播机制放进同一决策。'),
        'FUNNEL': ('把内容/资产映射到真实购买旅程与转化摩擦。', '不同Surface承担不同理解、信任、异议和转化任务。', '不强制固定漏斗阶段数量；阶段随当前项目定义。', '让内容矩阵、资产Universe、CTA和指标与实际旅程节点对应。'),
    }
    out: dict[str, dict[str, Any]] = {}
    for key in FRAMEWORK_ORDER:
        old = _d(existing.get(key))
        role, basis, tradeoff, execution = roles[key]
        out[key] = deepcopy(old)
        out[key].setdefault('role', role)
        out[key].setdefault('basis', basis)
        out[key].setdefault('tradeoff', tradeoff)
        out[key].setdefault('execution', execution)
        out[key].setdefault('status', old.get('status') or ('PROCESS_BACKBONE' if key == 'RACE' else 'DECISION_LENS'))
    return out


def _visual_checklist(vis: dict[str, Any]) -> dict[str, Any]:
    camera = _d(vis.get('camera'))
    lighting = vis.get('lighting_framework') or vis.get('lighting') or 'TO_VERIFY：由逐资产拍摄任务闭合方向、CCT、光比与柔硬。'
    palette = vis.get('palette_hex') or vis.get('palette') or 'TO_VERIFY：需基于品牌/产品/Surface确定HEX。'
    contrast = vis.get('contrast') or vis.get('contrast_ratio') or 'TO_VERIFY：最终文字/背景组合需做可读性与对比度复核。'
    inclusive = _d(vis.get('inclusive_photography'))
    return {
        'style_keywords': vis.get('style_keywords') or vis.get('style') or 'TO_VERIFY',
        'moodboard_direction': vis.get('moodboard_direction') or vis.get('style') or 'TO_VERIFY：从已选视觉世界与购买任务派生。',
        'composition_rules': vis.get('composition_rules') or vis.get('composition') or 'TO_VERIFY：逐资产按焦点路径和移动端层级闭合。',
        'palette_hex_and_contrast': {'palette': deepcopy(palette), 'contrast': contrast},
        'lighting': deepcopy(lighting),
        'lens_focal_length': vis.get('lens') or camera.get('lens') or 'TO_VERIFY：逐资产摄影合同闭合焦段/镜头族。',
        'shot_size': camera.get('shot_size') or vis.get('shot_size') or 'TO_VERIFY：逐资产按购买问题选择景别。',
        'camera_position': deepcopy(camera) if camera else 'TO_VERIFY：逐资产闭合机位高度、yaw/pitch/roll与工作距离。',
        'scene': vis.get('scene') or 'TO_VERIFY：由当前购买语境决定。',
        'props': vis.get('props') or 'NONE_UNLESS_STRATEGICALLY_NEEDED',
        'casting_wardrobe_grooming': {
            'casting': deepcopy(vis.get('casting') or '按资产任务决定；人物出现不作为默认。'),
            'wardrobe_hair_makeup': deepcopy(vis.get('wardrobe_hair_makeup') or '按目标市场与场景证据闭合，避免刻板印象。'),
        },
        'platform_dimensions': deepcopy(vis.get('platform_dimensions') or 'TO_VERIFY_CURRENT_SURFACE_SPEC'),
        'deep_skin_exposure_compensation': inclusive.get('deep_skin_exposure_compensation_plan') or inclusive.get('deep_skin_shadow_protection') or 'Prelight-dependent：按实际深肤色人物测光保护暗部层次，不硬套固定曝光补偿。',
        'reflector_diffusion_plan': inclusive.get('reflector_bounce_diffusion') or 'Prelight-dependent：使用中性反光板/bounce/大面积柔光，按肤色、背景反射与妆发现场调整。',
        'hair_body_disability_age_ai_bias': {
            'hair_texture': inclusive.get('hair_texture') or '保留真实发质与边缘层次。',
            'body_representation': inclusive.get('body_representation') or '避免把单一审美体型当默认消费者。',
            'disability_representation': inclusive.get('disability_representation') or '仅在相关自然语境中呈现，避免tokenism。',
            'age_representation': inclusive.get('age_representation') or '年龄呈现与真实使用者/场景一致。',
            'ai_bias_check': inclusive.get('ai_bias_check') or '检查肤色漂移、发质、身体/手部、年龄与残障器具错误。',
        },
    }


def _tradeoff_rows(last: dict[str, Any]) -> list[dict[str, Any]]:
    current = _d(last.get('resource_tradeoff_plan'))
    plan = _d(last.get('priority_plan'))
    constraints = current.get('constraints') or ['MISSING_INPUT：预算/周期/团队资源未完整量化时，按P0/P1/P2做明确取舍。']
    defaults = {
        'P0': {
            'keep': '产品事实、Claim证据、合规、身份/包装准确、关键发布边界。',
            'cut_or_defer': '任何无证据硬宣称、会掩盖事实边界的创意增强、非必要装饰重复。',
            'why': 'P0不做会翻车：可能造成错误宣称、违规、误购或重大信任损失。',
            'restore_condition': '只有补齐证据/合规/真实输入后，才恢复被Hold的发布表达。',
        },
        'P1': {
            'keep': '最能改变理解/点击/转化的核心Listing、Hero、关键证据、主要内容与必要本地化。',
            'cut_or_defer': '低优先Surface、多余变体、没有独立假设的重复内容。',
            'why': 'P1直接影响效果；资源不足时保留高影响购买决策链。',
            'restore_condition': '预算/周期恢复或核心Surface数据稳定后，再扩展次级Surface与测试。',
        },
        'P2': {
            'keep': '在P0/P1稳定后保留有清晰增量信息或实验价值的加分项。',
            'cut_or_defer': '纯装饰、低信息、不可测或与现有资产高度重复的增强项。',
            'why': 'P2是加分项，不应挤占事实、合规与核心转化链资源。',
            'restore_condition': '当资源充足且能提出独立商业假设/指标时再补回。',
        },
    }
    rows = []
    for priority in ('P0', 'P1', 'P2'):
        base = defaults[priority]
        rows.append({
            'priority': priority,
            'keep': base['keep'],
            'cut_or_defer': base['cut_or_defer'],
            'why': base['why'],
            'restore_condition': base['restore_condition'],
            'current_actions': deepcopy(plan.get(priority) or []),
            'constraints': deepcopy(constraints),
        })
    return rows


def _self_check_rows(sections: dict[str, Any]) -> list[dict[str, Any]]:
    info = _d(sections.get('01_information_completeness_assumptions_decisions'))
    truth = _d(sections.get('02_product_truth_value_ladder'))
    insight = _d(sections.get('03_platform_region_audience_culture_insight'))
    matrix = [x for x in _l(sections.get('06_platform_content_matrix')) if isinstance(x, dict)]
    last = _d(sections.get('09_risk_measurement_priority_next_steps'))
    p0 = [x for x in _l(last.get('p0_compliance_claim_checklist')) if isinstance(x, dict)]
    truth_rows = [x for x in _l(truth.get('product_truth_audit_table')) if isinstance(x, dict)]
    culture_rows = [x for x in _l(sections.get('08_culture_adaptation_checklist')) if isinstance(x, dict)]
    unknown_culture = any(str(x.get('evidence_or_assumption') or x.get('result') or '').upper() in {'TO_VERIFY','MISSING_INPUT','ASSUMPTION'} for x in culture_rows)
    decisions = [x for x in _l(info.get('decision_log')) if isinstance(x, dict)]
    checks = {
        'fabrication': (
            'PASS_WITH_EXPLICIT_UNKNOWNS' if truth_rows and all(_p(x.get('evidence_grade')) and _p(x.get('basis')) for x in truth_rows) else 'TO_VERIFY',
            '产品事实/宣称必须绑定证据等级与依据；未知项显式保留。',
            '发现无来源或未知外部规则时标TO_VERIFY，不补写确定性事实。',
        ),
        'why': (
            'PASS' if decisions and all(_p(x.get('why')) for x in decisions) else 'INCOMPLETE',
            '关键决策需要WHY及平台/区域/人群/文化背景。',
            '补齐缺失决策的依据、取舍、执行和指标。',
        ),
        'culture': (
            'TO_VERIFY' if unknown_culture else ('PASS' if _p(insight.get('intersectionality_table')) and culture_rows else 'INCOMPLETE'),
            '交叉性、族裔文化适配、禁忌与刻板印象必须逐项校验。',
            '文化证据不足时保持TO_VERIFY并安排native/current-source review。',
        ),
        'compliance': (
            'PASS_OR_HOLD_EXPLICIT' if p0 and all(_p(x.get('status')) for x in p0) else 'INCOMPLETE',
            '功效、成分、认证、价格、销量、强监管品类必须P0单列。',
            '发布前闭合所有HOLD/TO_VERIFY；不得编造认证、销量或法规。',
        ),
        'metric': (
            'PASS' if matrix and all(_p(x.get('metric')) for x in matrix) else 'INCOMPLETE',
            '策略与内容需要可观察指标、归因或A/B学习回路。',
            '为缺指标的Surface补主要指标与归因方法。',
        ),
        'assumption': (
            'PASS' if 'assumption_decision_log' in info else 'INCOMPLETE',
            '事实、假设和决策必须分开；假设不能静默升级。',
            '把所有假设显式进入日志，并记录转事实所需证据。',
        ),
    }
    return [{'check': key, 'status': checks[key][0], 'basis': checks[key][1], 'action': checks[key][2]} for key in SELF_CHECK_ORDER]


def materialize_strategy_culture(strategy: dict[str, Any], request: dict[str, Any] | None = None) -> dict[str, Any]:
    out = strategy
    if str(_d(out.get('human_projection')).get('mode') or out.get('delivery_mode') or out.get('scope_mode') or '').upper() != 'FULL':
        return out
    sections = out.setdefault('sections', {})

    truth = sections.setdefault('02_product_truth_value_ladder', {})
    truth_rows = _product_truth_rows(truth)
    truth['product_truth_audit_table'] = truth_rows

    info = sections.setdefault('01_information_completeness_assumptions_decisions', {})
    info['assumption_decision_log'] = _assumption_decision_rows(info, truth_rows)

    insight = sections.setdefault('03_platform_region_audience_culture_insight', {})
    insight['intersectionality_table'] = _intersectionality(insight)

    core = sections.setdefault('04_marketing_core_strategy', {})
    core['framework_relationships'] = _frameworks(core)

    vis = sections.setdefault('05_visual_photography_strategy', {})
    vis['visual_execution_checklist'] = _visual_checklist(vis)

    last = sections.setdefault('09_risk_measurement_priority_next_steps', {})
    tradeoff = _d(last.get('resource_tradeoff_plan'))
    tradeoff['priority_rows'] = _tradeoff_rows(last)
    if request and _p(request.get('resource_constraints')):
        tradeoff['constraints'] = deepcopy(request.get('resource_constraints'))
    last['resource_tradeoff_plan'] = tradeoff
    last['output_self_check_rows'] = _self_check_rows(sections)

    out['strategy_culture_materialization'] = {
        'status': 'MATERIALIZED',
        'objects': [
            'product_truth_audit_table', 'assumption_decision_log', 'intersectionality_table',
            'framework_relationships', 'visual_execution_checklist', 'platform_content_matrix',
            'race_execution_table', 'culture_adaptation_checklist', 'resource_tradeoff_plan', 'output_self_check_rows',
        ],
        'principle': 'Source requirements are first-class strategy/human objects, not hidden fields or prose-only rules.',
    }
    return out


def wrap_build_master_strategy(fn: Callable[..., dict[str, Any]]):
    def built(request: dict[str, Any], *args, **kwargs):
        strategy = fn(request, *args, **kwargs)
        return materialize_strategy_culture(strategy, request)
    setattr(built, '_cbcc_v0669_strategy_culture_materialization', True)
    return built


def _cell(value: Any) -> str:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = '' if value is None else str(value)
    return text.replace('|', '\\|').replace('\n', '<br>')


def _table(headers: list[tuple[str, str]], rows: list[dict[str, Any]]) -> str:
    out = ['| ' + ' | '.join(label for label, _ in headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|']
    for row in rows:
        out.append('| ' + ' | '.join(_cell(row.get(key)) for _, key in headers) + ' |')
    return '\n'.join(out)


def _human_blocks(strategy: dict[str, Any]) -> str:
    s = _d(strategy.get('sections'))
    truth = _d(s.get('02_product_truth_value_ladder'))
    info = _d(s.get('01_information_completeness_assumptions_decisions'))
    insight = _d(s.get('03_platform_region_audience_culture_insight'))
    core = _d(s.get('04_marketing_core_strategy'))
    vis = _d(s.get('05_visual_photography_strategy'))
    matrix = [x for x in _l(s.get('06_platform_content_matrix')) if isinstance(x, dict)]
    race = [x for x in _l(s.get('07_race_execution_table')) if isinstance(x, dict)]
    culture = [x for x in _l(s.get('08_culture_adaptation_checklist')) if isinstance(x, dict)]
    last = _d(s.get('09_risk_measurement_priority_next_steps'))
    blocks: list[str] = []

    blocks += ['', '### 产品事实审计：真实卖点 / 可感知利益 / 情绪价值 / 不可宣称项', _table([
        ('项目','item'),('事实/宣称','fact_or_claim'),('真实卖点','real_selling_point'),('可感知利益','perceived_benefit'),
        ('情绪价值','emotional_value'),('不可宣称项','non_claimable'),('证据等级','evidence_grade'),('依据','basis'),('取舍','tradeoff'),('发布规则','publication_rule')
    ], [x for x in _l(truth.get('product_truth_audit_table')) if isinstance(x, dict)])]

    blocks += ['', '### 假设与决策日志（事实 / 假设 / 决策）', _table([
        ('类型','type'),('事项','item'),('状态','status'),('依据','basis'),('取舍','tradeoff')
    ], [x for x in _l(info.get('assumption_decision_log')) if isinstance(x, dict)])]

    inter = [x for x in _l(insight.get('intersectionality_table')) if isinstance(x, dict)]
    blocks += ['', '### 交叉性分析：族裔 × 性别 × 年龄 × 收入 × 地域', _table([
        ('交叉维度','dimensions'),('含义','implication'),('依据/假设','evidence_or_assumption'),('刻板印象防线','stereotype_guard'),('执行','execution')
    ], inter)]

    framework_rows = []
    for key in FRAMEWORK_ORDER:
        row = {'framework': key, **_d(_d(core.get('framework_relationships')).get(key))}
        framework_rows.append(row)
    blocks += ['', '### 框架关系与决策理由', _table([
        ('框架','framework'),('角色','role'),('依据','basis'),('取舍','tradeoff'),('执行','execution')
    ], framework_rows)]

    checklist = _d(vis.get('visual_execution_checklist'))
    visual_rows = [{'item': key, 'execution': value} for key, value in checklist.items()]
    blocks += ['', '### 视觉总策略与拍摄执行清单', _table([('执行项','item'),('当前执行','execution')], visual_rows),
               '- 深肤色曝光补偿：' + _cell(checklist.get('deep_skin_exposure_compensation')),
               '- 反光板/柔光方案：' + _cell(checklist.get('reflector_diffusion_plan'))]

    blocks += ['', '### 分平台内容矩阵：RACE阶段 + 族裔文化适配/禁忌校验 + 平台执行', _table([
        ('平台','platform'),('人群','audience'),('选题','topic'),('钩子','hook'),('脚本结构','script_structure'),('视觉形式','visual_form'),
        ('CTA','cta'),('指标','metric'),('RACE阶段','race_stage'),('族裔文化适配/禁忌校验','taboo_stereotype_check'),
        ('尺寸','platform_dimensions'),('时长','duration'),('封面/首帧','cover_first_frame'),('字幕','subtitle_strategy'),('音乐版权','music_rights'),
        ('流量机制','traffic_mechanism'),('落地页','landing_handoff'),('UTM/归因','utm_attribution'),('WHY','why')
    ], matrix)]

    blocks += ['', '### RACE传播框架执行表', _table([
        ('阶段','stage'),('目标','objective'),('关键动作','key_actions'),('输出物','output'),('平台','platform'),('文化校验','culture_check'),('指标','kpi'),('WHY','why')
    ], race)]

    blocks += ['', '### 族裔文化适配检查表', _table([
        ('文化适配点','adaptation_point'),('依据/假设','evidence_or_assumption'),('包容性表征','inclusive_representation'),
        ('刻板印象与禁忌','stereotype_taboo_risk'),('脚本校验','script_check'),('模特校验','casting_check'),
        ('服化道校验','wardrobe_grooming_check'),('配色校验','color_check'),('CTA校验','cta_check'),('结果','result'),('修改动作','modification'),('WHY','why')
    ], culture)]

    priorities = [x for x in _l(_d(last.get('resource_tradeoff_plan')).get('priority_rows')) if isinstance(x, dict)]
    blocks += ['', '### P0 / P1 / P2 资源取舍表', _table([
        ('优先级','priority'),('保什么','keep'),('砍/延后什么','cut_or_defer'),('为什么','why'),('恢复条件','restore_condition'),('当前动作','current_actions')
    ], priorities)]

    checks = [x for x in _l(last.get('output_self_check_rows')) if isinstance(x, dict)]
    blocks += ['', '### 输出前自检表', _table([
        ('检查项','check'),('状态','status'),('依据','basis'),('动作','action')
    ], checks)]
    return '\n'.join(blocks) + '\n'


def wrap_render_master_strategy_cn(fn: Callable[[dict[str, Any]], str]):
    def rendered(strategy: dict[str, Any]) -> str:
        base = fn(strategy)
        if str(_d(strategy.get('human_projection')).get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '').upper() != 'FULL':
            return base
        return base.rstrip() + '\n' + _human_blocks(strategy)
    setattr(rendered, '_cbcc_v0669_strategy_culture_materialization', True)
    return rendered


def _missing(row: Mapping[str, Any], fields: set[str]) -> list[str]:
    return sorted(key for key in fields if not _p(row.get(key)))


def strategy_materialization_issues(strategy: dict[str, Any]) -> list[dict[str, Any]]:
    if str(_d(strategy.get('human_projection')).get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '').upper() != 'FULL':
        return []
    s = _d(strategy.get('sections'))
    issues: list[dict[str, Any]] = []

    truth_rows = [x for x in _l(_d(s.get('02_product_truth_value_ladder')).get('product_truth_audit_table')) if isinstance(x, dict)]
    truth_fields = {'item','fact_or_claim','real_selling_point','perceived_benefit','emotional_value','non_claimable','evidence_grade','source_refs','publication_rule','basis','tradeoff'}
    if not truth_rows:
        issues.append({'code':'FULL_PRODUCT_TRUTH_AUDIT_TABLE_MISSING'})
    for i, row in enumerate(truth_rows):
        miss = _missing(row, truth_fields)
        if miss:
            issues.append({'code':'FULL_PRODUCT_TRUTH_AUDIT_ROW_SHALLOW','row':i,'fields':miss})
        if str(row.get('evidence_grade') or '').upper() == 'C' and 'NO_HARD_CLAIM' not in str(row.get('publication_rule') or ''):
            issues.append({'code':'C_LEVEL_HARD_CLAIM_FORBIDDEN_IN_MATERIALIZATION','row':i})

    info = _d(s.get('01_information_completeness_assumptions_decisions'))
    if not _p(info.get('assumption_decision_log')):
        issues.append({'code':'FULL_ASSUMPTION_DECISION_LOG_MISSING'})

    inter = [x for x in _l(_d(s.get('03_platform_region_audience_culture_insight')).get('intersectionality_table')) if isinstance(x, dict)]
    if not inter:
        issues.append({'code':'FULL_INTERSECTIONALITY_TABLE_MISSING'})
    for i, row in enumerate(inter):
        dims = set(str(x) for x in _l(row.get('dimensions')))
        if not set(REQUIRED_INTERSECTION_DIMENSIONS).issubset(dims):
            issues.append({'code':'FULL_INTERSECTIONALITY_DIMENSIONS_MISSING','row':i,'dimensions':sorted(dims)})
        miss = _missing(row, {'implication','evidence_or_assumption','stereotype_guard','execution'})
        if miss:
            issues.append({'code':'FULL_INTERSECTIONALITY_ROW_SHALLOW','row':i,'fields':miss})

    relationships = _d(_d(s.get('04_marketing_core_strategy')).get('framework_relationships'))
    for key in FRAMEWORK_ORDER:
        miss = _missing(_d(relationships.get(key)), {'role','basis','tradeoff','execution'})
        if miss:
            issues.append({'code':'FULL_FRAMEWORK_RELATIONSHIP_SHALLOW','framework':key,'fields':miss})

    visual = _d(_d(s.get('05_visual_photography_strategy')).get('visual_execution_checklist'))
    visual_fields = {'style_keywords','moodboard_direction','composition_rules','palette_hex_and_contrast','lighting','lens_focal_length','shot_size','camera_position','scene','props','casting_wardrobe_grooming','platform_dimensions','deep_skin_exposure_compensation','reflector_diffusion_plan'}
    miss_visual = _missing(visual, visual_fields)
    if miss_visual:
        issues.append({'code':'FULL_VISUAL_EXECUTION_CHECKLIST_MISSING','fields':miss_visual})

    matrix_fields = {'platform','audience','topic','hook','script_structure','visual_form','cta','metric','race_stage','culture_adaptation','taboo_stereotype_check','platform_dimensions','duration','cover_first_frame','subtitle_strategy','music_rights','traffic_mechanism','landing_handoff','utm_attribution','why'}
    for i, row in enumerate([x for x in _l(s.get('06_platform_content_matrix')) if isinstance(x, dict)]):
        miss = _missing(row, matrix_fields)
        if miss:
            issues.append({'code':'FULL_CONTENT_MATRIX_EXECUTION_COLUMNS_MISSING','row':i,'fields':miss})

    race = [x for x in _l(s.get('07_race_execution_table')) if isinstance(x, dict)]
    if [str(x.get('stage') or '').upper() for x in race] != list(RACE_ORDER):
        issues.append({'code':'FULL_RACE_EXECUTION_ORDER_INVALID'})
    for i, row in enumerate(race):
        miss = _missing(row, {'stage','objective','key_actions','output','platform','culture_check','kpi','why'})
        if miss:
            issues.append({'code':'FULL_RACE_EXECUTION_ROW_SHALLOW','row':i,'fields':miss})

    culture_fields = {'adaptation_point','evidence_or_assumption','inclusive_representation','stereotype_taboo_risk','script_check','casting_check','wardrobe_grooming_check','color_check','cta_check','result','modification','why'}
    culture_rows = [x for x in _l(s.get('08_culture_adaptation_checklist')) if isinstance(x, dict)]
    if not culture_rows:
        issues.append({'code':'FULL_CULTURE_ADAPTATION_TABLE_MISSING'})
    for i, row in enumerate(culture_rows):
        miss = _missing(row, culture_fields)
        if miss:
            issues.append({'code':'FULL_CULTURE_ADAPTATION_ROW_SHALLOW','row':i,'fields':miss})

    last = _d(s.get('09_risk_measurement_priority_next_steps'))
    priorities = [x for x in _l(_d(last.get('resource_tradeoff_plan')).get('priority_rows')) if isinstance(x, dict)]
    if [str(x.get('priority') or '') for x in priorities] != ['P0','P1','P2']:
        issues.append({'code':'FULL_RESOURCE_TRADEOFF_PRIORITY_ROWS_MISSING'})
    for i, row in enumerate(priorities):
        miss = _missing(row, {'priority','keep','cut_or_defer','why','restore_condition'})
        if miss:
            issues.append({'code':'FULL_RESOURCE_TRADEOFF_ROW_SHALLOW','row':i,'fields':miss})

    checks = [x for x in _l(last.get('output_self_check_rows')) if isinstance(x, dict)]
    if [str(x.get('check') or '') for x in checks] != list(SELF_CHECK_ORDER):
        issues.append({'code':'FULL_OUTPUT_SELF_CHECK_ROWS_MISSING'})
    for i, row in enumerate(checks):
        miss = _missing(row, {'check','status','basis','action'})
        if miss:
            issues.append({'code':'FULL_OUTPUT_SELF_CHECK_ROW_SHALLOW','row':i,'fields':miss})
    return issues


def wrap_audit_full_strategy_depth_v3(fn: Callable[..., dict[str, Any]]):
    def audited(strategy: dict[str, Any], base_result=None):
        result = fn(strategy, base_result)
        issues = list(result.get('issues') or [])
        issues.extend(strategy_materialization_issues(strategy))
        seen = set()
        deduped = []
        for issue in issues:
            key = json.dumps(issue, ensure_ascii=False, sort_keys=True, default=str)
            if key not in seen:
                seen.add(key)
                deduped.append(issue)
        result['issues'] = deduped
        if str(result.get('mode') or _d(strategy.get('human_projection')).get('mode') or strategy.get('delivery_mode') or '').upper() == 'FULL':
            result['status'] = 'PASS' if not deduped else 'INCOMPLETE'
        result['strategy_culture_materialization_audit'] = {
            'status': 'PASS' if not strategy_materialization_issues(strategy) else 'INCOMPLETE',
            'required_first_class_objects': 10,
        }
        return result
    setattr(audited, '_cbcc_v0669_strategy_culture_materialization_audit', True)
    return audited
