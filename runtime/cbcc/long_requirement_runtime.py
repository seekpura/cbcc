from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping

QUESTION_LIMIT = 10
P0_COMPLIANCE_AREAS = (
    'efficacy_claims',
    'ingredients_formula',
    'certifications',
    'price',
    'sales_volume',
    'regulated_category',
)
CULTURE_EXECUTION_CHECK_FIELDS = (
    'script_check',
    'casting_check',
    'wardrobe_grooming_check',
    'color_check',
    'cta_check',
)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    if value in (None, '', {}):
        return []
    return value if isinstance(value, list) else [value]


def _present(value: Any) -> bool:
    return value not in (None, '', [], {})


def _status_entry(raw: Any, fallback_why: str) -> dict[str, Any]:
    row = _dict(raw)
    return {
        'status': str(row.get('status') or ('EVIDENCED' if _present(row.get('value')) else 'TO_VERIFY')).upper(),
        'value': deepcopy(row.get('value')),
        'why': row.get('why') or fallback_why,
        'evidence_or_assumption': deepcopy(
            row.get('evidence_refs') or row.get('source_refs') or row.get('value') or row.get('status') or 'TO_VERIFY'
        ),
    }


def _decision_context_why(dimensions: Mapping[str, Any]) -> dict[str, Any]:
    platform = _status_entry(dimensions.get('platform'), '平台决定Surface、流量机制、字段、CTA与生产约束。')
    region = _status_entry(dimensions.get('market_region'), '区域决定语言、法规、支付物流和文化研究边界。')
    audience = _status_entry(dimensions.get('audience_segments'), '人群决定购买任务、信息优先级、场景与内容密度。')

    culture_sources = [
        _status_entry(dimensions.get('race_ethnicity'), '族裔只用于有依据的表征、语言与文化语境，不自动推断行为。'),
        _status_entry(dimensions.get('religion'), '宗教只在相关禁忌、节日、服饰、使用语境或法规中使用。'),
        _status_entry(dimensions.get('stereotype_taboo'), '文化禁忌与刻板印象属于传播P0边界。'),
    ]
    culture_status = 'EVIDENCED' if any(x['status'] == 'EVIDENCED' for x in culture_sources) else (
        'TO_VERIFY' if any(x['status'] == 'TO_VERIFY' for x in culture_sources) else culture_sources[0]['status']
    )
    culture = {
        'status': culture_status,
        'value': [x.get('value') for x in culture_sources if _present(x.get('value'))],
        'why': '族裔/宗教/文化只改变有证据的语言、表征、场景、禁忌与CTA；不得从身份直接推断消费行为。',
        'evidence_or_assumption': [x.get('evidence_or_assumption') for x in culture_sources],
    }
    return {
        'platform': platform,
        'region': region,
        'audience': audience,
        'race_ethnicity_culture': culture,
    }


def _has_product_fact(request: Mapping[str, Any], terms: tuple[str, ...]) -> bool:
    product = _dict(request.get('product'))
    blob = str(product).casefold()
    return any(term in blob for term in terms)


def _source_refs(request: Mapping[str, Any], terms: tuple[str, ...] = ()) -> list[str]:
    refs = []
    for row in _list(request.get('sources')):
        if not isinstance(row, dict):
            continue
        blob = ' '.join(str(row.get(k) or '') for k in ('kind', 'source_type', 'evidence_type', 'title', 'scope')).casefold()
        if terms and not any(term in blob for term in terms):
            continue
        sid = row.get('source_id')
        if sid:
            refs.append(str(sid))
    return refs


def _regulated_category_candidate(request: Mapping[str, Any]) -> bool:
    product = _dict(request.get('product'))
    text = ' '.join(str(product.get(k) or '') for k in ('category', 'product_type', 'subcategory')).casefold()
    terms = (
        'beauty', 'cosmetic', 'skincare', 'skin care', 'acne', 'medical', 'health', 'drug', 'medicine',
        'food', 'supplement', 'nutrition', 'finance', 'financial', 'investment', 'insurance',
        '美妆', '护肤', '医疗', '药', '食品', '保健', '金融',
    )
    return any(term in text for term in terms)


def _p0_compliance_checklist(request: Mapping[str, Any], compliance: Mapping[str, Any]) -> list[dict[str, Any]]:
    compliance = _dict(compliance)
    claims = [x for x in _list(request.get('claims')) if isinstance(x, dict)]
    claim_issues = _list(compliance.get('claim_issues'))
    all_sources = _source_refs(request)

    rows: list[dict[str, Any]] = []

    efficacy_claims = [
        x for x in claims
        if any(term in str(x.get('claim') or x.get('text') or x.get('name') or '').casefold()
               for term in ('effect', 'effic', 'acne', 'bright', 'whiten', 'anti', 'repair', 'treat', 'heal', '功效', '祛', '美白', '修复', '治疗'))
    ]
    efficacy_status = 'HOLD' if claim_issues else ('EVIDENCED' if efficacy_claims else 'NOT_ACTIVE')
    rows.append({
        'check_area': 'efficacy_claims', 'priority': 'P0', 'status': efficacy_status,
        'evidence_refs': sorted({str(ref) for c in efficacy_claims for ref in _list(c.get('source_ids') or c.get('evidence_source_ids'))}),
        'publication_rule': '只有证据等级与当前法规/平台规则允许的表达才能公开；C级/待验证不得硬宣称。',
        'action': '逐条对功效Claim核对证据等级、来源、当前市场法规和平台规则；不满足则HOLD或降级表达。',
        'why': '功效表达属于高风险Claim，不能由成分机理、竞品话术或创意视觉自动升级。',
    })

    ingredient_refs = _source_refs(request, ('formula', 'ingredient', 'inci', 'supplier', '配方', '成分')) or all_sources
    rows.append({
        'check_area': 'ingredients_formula', 'priority': 'P0',
        'status': 'EVIDENCED' if _has_product_fact(request, ('ingredient', 'formula', 'active', 'inci', '成分', '配方')) else 'MISSING_INPUT',
        'evidence_refs': ingredient_refs,
        'publication_rule': '成分名称、浓度、配方事实只能按真源准确表达；机理解释不得越过Claim证据边界。',
        'action': '核对INCI/成分/浓度/配方真源与所有Listing/资产可见数字；缺失时不得补写。',
        'why': '错误成分与浓度会直接造成商品事实错误和潜在监管风险。',
    })

    cert_refs = _source_refs(request, ('cert', 'certificate', 'registration', 'npra', '认证', '注册'))
    rows.append({
        'check_area': 'certifications', 'priority': 'P0',
        'status': 'EVIDENCED' if cert_refs or _has_product_fact(request, ('cert', 'registration', '认证', '注册')) else 'TO_VERIFY',
        'evidence_refs': cert_refs,
        'publication_rule': '认证/注册/检测标识必须有可核验来源、有效范围和当前状态；缺证据不展示。',
        'action': '发布前核验认证/注册/检测文件、编号、适用SKU/市场与有效状态；未知保持TO_VERIFY。',
        'why': '认证/注册属于可验证事实，错误展示会形成高风险误导。',
    })

    economics = _dict(request.get('offer_economics'))
    price = economics.get('price')
    rows.append({
        'check_area': 'price', 'priority': 'P0',
        'status': 'EVIDENCED' if _present(price) else 'MISSING_INPUT',
        'evidence_refs': ['offer_economics.price'] if _present(price) else [],
        'publication_rule': '市场价格带只是外部证据，不等于本商品建议售价；商品价格/折扣必须来自明确输入与经济边界。',
        'action': '缺真实售价/经济输入时保持UNKNOWN/MISSING_INPUT，不把竞品价带转成自身推荐价。',
        'why': '价格直接影响消费者决策、利润和广告阈值，假精确会误导经营。',
    })

    sales_refs = _source_refs(request, ('sales', 'gmv', 'orders', '销量', '销售'))
    explicit_sales = _present(request.get('sales')) or _present(request.get('sales_volume')) or bool(sales_refs)
    rows.append({
        'check_area': 'sales_volume', 'priority': 'P0',
        'status': 'EVIDENCED' if explicit_sales else 'MISSING_INPUT',
        'evidence_refs': sales_refs,
        'publication_rule': '销量/GMV/排名只能来自当前可追溯数据；市场样本、评论数或平台热度不能替代自身销量。',
        'action': '没有可追溯销量数据时不生成销量、排名、爆款等确定性文案。',
        'why': '销量/排名是强信任信号，虚构或错用会造成严重误导。',
    })

    regulated = _regulated_category_candidate(request)
    rows.append({
        'check_area': 'regulated_category', 'priority': 'P0',
        'status': ('HOLD' if compliance.get('status') == 'HOLD' else 'TO_VERIFY_CURRENT_RULES') if regulated else 'NOT_RELEVANT',
        'evidence_refs': _source_refs(request, ('regulation', 'policy', 'official', '法规', '官方')),
        'publication_rule': '医疗/美妆/食品/金融等强监管类目按目标市场当前法规与平台规则单列核验；未知不得编造。',
        'action': '若属于强监管类目，发布前查证当前目标市场法规、平台规则与Claim/素材限制；未闭环保持TO_VERIFY/HOLD。',
        'why': '强监管类目的可发布边界随市场、品类和规则变化，不能由通用经验替代当前证据。',
    })
    return rows


def _culture_execution_checks(row: Mapping[str, Any]) -> dict[str, str]:
    status = str(row.get('result') or row.get('status') or 'TO_VERIFY')
    basis = row.get('evidence_or_assumption') or row.get('evidence_status') or 'TO_VERIFY'
    suffix = f'；依据/状态：{basis}；结果：{status}'
    return {
        'script_check': '逐条检查脚本是否使用证据支持的文化/语言语境，是否出现标签化、禁忌或无依据行为推断' + suffix,
        'casting_check': '检查模特/人物角色、年龄、肤色、体型、残障与家庭/社会关系是否真实、包容且与任务相关' + suffix,
        'wardrobe_grooming_check': '检查服装、宗教/文化服饰、发质/发型、妆容和手部造型是否自然且非符号化刻板呈现' + suffix,
        'color_check': '检查配色是否服务品牌/信息/对比与真实文化语境；不得凭族裔/宗教标签机械指定颜色' + suffix,
        'cta_check': '检查CTA、Offer和行动语言是否符合目标语言、平台行为与文化/宗教边界；未知项保持TO_VERIFY' + suffix,
    }


def wrap_build_master_strategy(fn: Callable[..., dict[str, Any]]):
    def built(request: dict[str, Any], *args, **kwargs):
        strategy = fn(request, *args, **kwargs)
        mode = str(_dict(strategy.get('human_projection')).get('mode') or strategy.get('delivery_mode') or '').upper()
        if mode != 'FULL':
            return strategy

        sections = strategy.setdefault('sections', {})
        info = _dict(sections.get('01_information_completeness_assumptions_decisions'))
        pending = _list(info.get('pending_confirmations'))
        info['pending_confirmation_total_count'] = len(pending)
        info['question_limit'] = QUESTION_LIMIT
        info['pending_confirmations_overflow'] = deepcopy(pending[QUESTION_LIMIT:])
        info['pending_confirmations'] = deepcopy(pending[:QUESTION_LIMIT])
        info['continue_under_assumptions'] = True
        info['continuation_rule'] = '最多向用户提出10个真正影响事实/发布/预算的关键问题；随后在明确假设、TO_VERIFY或MISSING_INPUT边界下继续完成其余策略与生产对象。'

        culture_sec = _dict(sections.get('03_platform_region_audience_culture_insight'))
        dimensions = _dict(culture_sec.get('dimension_status'))
        context_why = _decision_context_why(dimensions)
        decisions = []
        for raw in _list(info.get('decision_log')):
            if not isinstance(raw, dict):
                continue
            row = deepcopy(raw)
            row.setdefault('context_why', deepcopy(context_why))
            decisions.append(row)
        info['decision_log'] = decisions
        sections['01_information_completeness_assumptions_decisions'] = info

        vis = _dict(sections.get('05_visual_photography_strategy'))
        people = str(vis.get('people_applicability') or '').upper() in {'PERSON_PRESENT', 'PEOPLE_PRESENT', 'HUMAN_PRESENT', 'APPLICABLE_P0'}
        if people:
            inc = _dict(vis.get('inclusive_photography'))
            inc.setdefault(
                'deep_skin_exposure_compensation_plan',
                'PRELIGHT_DEPENDENT：以实际面部/肤色测光、波形/直方图和参考帧确认；若深肤色中间调/暗部低于目标，优先通过曝光、neutral bounce/reflector与柔光调整恢复层次，并记录最终EV补偿；不得预先虚构统一固定EV。',
            )
            inc.setdefault(
                'reflector_bounce_diffusion',
                '使用大面积柔光 + 中性白/银反光板或bounce按实际肤色和背景反射控制暗部；Prelight后锁定尺寸、距离、角度和最终曝光。',
            )
            vis['inclusive_photography'] = inc
        sections['05_visual_photography_strategy'] = vis

        checklist = []
        for raw in _list(sections.get('08_culture_adaptation_checklist')):
            if not isinstance(raw, dict):
                continue
            row = deepcopy(raw)
            for key, value in _culture_execution_checks(row).items():
                row.setdefault(key, value)
            checklist.append(row)
        sections['08_culture_adaptation_checklist'] = checklist

        last = _dict(sections.get('09_risk_measurement_priority_next_steps'))
        last['p0_compliance_claim_checklist'] = _p0_compliance_checklist(request, _dict(kwargs.get('compliance')))
        self_check = _dict(last.get('output_self_check'))
        self_check.setdefault('p0_compliance_detail_check', '功效/成分/认证/价格/销量/强监管类目是否逐项有状态、证据或TO_VERIFY边界。')
        self_check.setdefault('question_limit_check', '真正向用户提出的待确认问题≤10；其余缺口进入假设/TO_VERIFY/MISSING_INPUT并继续。')
        self_check.setdefault('context_why_check', '重大决策是否分别说明平台、区域、人群、族裔文化WHY及依据/假设。')
        last['output_self_check'] = self_check
        sections['09_risk_measurement_priority_next_steps'] = last

        strategy['sections'] = sections
        strategy['verbatim_long_requirement_runtime'] = {
            'status': 'APPLIED',
            'question_limit': QUESTION_LIMIT,
            'p0_compliance_areas': list(P0_COMPLIANCE_AREAS),
            'culture_execution_check_fields': list(CULTURE_EXECUTION_CHECK_FIELDS),
            'authority': 'USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md',
        }
        return strategy
    return built
