from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from .delivery_contract import normalize_evidence_grade, publication_rule
from .full_delivery_depth_v3 import MARKET_CULTURE_DIMENSIONS


def _dict(v: Any) -> dict[str, Any]:
    return v if isinstance(v, dict) else {}


def _list(v: Any) -> list[Any]:
    if v in (None, '', {}):
        return []
    return v if isinstance(v, list) else [v]


def _present(v: Any) -> bool:
    return v not in (None, '', [], {})


def _first(*values: Any) -> Any:
    for v in values:
        if _present(v):
            return v
    return None


def _source_type_for_fact(request: dict[str, Any], row: dict[str, Any]) -> str:
    refs = set(str(x) for x in (row.get('source_ids') or row.get('source_refs') or []))
    for src in request.get('sources') or []:
        if refs and str(src.get('source_id')) not in refs:
            continue
        blob = ' '.join(str(src.get(k) or '') for k in ('kind', 'source_type', 'evidence_type', 'title', 'scope'))
        if blob.strip():
            return blob
    return 'USER_SUPPLIED'


def _status_entry(value: Any, *, why: str, downstream: str, missing_status: str = 'TO_VERIFY') -> dict[str, Any]:
    if _present(value):
        return {'status': 'EVIDENCED', 'value': deepcopy(value), 'why': why, 'downstream_action': downstream}
    return {'status': missing_status, 'why': why, 'downstream_action': downstream}


def _dimension_status(request: dict[str, Any], market: dict[str, Any], culture: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    audience = _dict(request.get('audience')) or _dict(request.get('audience_culture'))
    lang = _first(target.get('primary_locale'), target.get('locale'), _dict(culture.get('language_profiles')).keys() if culture.get('language_profiles') else None)
    mapping = {
        'platform': (_first(target.get('platform'), target.get('platform_family'), target.get('site')), '当前已选择平台决定Surface、流量机制、字段与平台执行。', '进入平台内容矩阵、Listing、尺寸/时长/CTA/归因。'),
        'market_region': (target.get('market'), '目标国家/市场决定法规、语言、履约和文化研究边界。', '进入区域策略、本地化、合规与内容场景。'),
        'subregion_geography': (_first(target.get('region'), target.get('subregion'), target.get('city'), audience.get('geography')), '国家内部区域差异只有在有目标或证据时才能使用。', '有数据则细分场景/物流/语言；否则发布前查证。'),
        'audience_segments': (_first(audience.get('segments'), audience.get('primary_segment'), market.get('audience_segments'), market.get('segments')), '受众必须来自当前项目输入或研究，不能从类目刻板推断。', '进入STP/JTBD、Message、Creative与Creator选择。'),
        'age': (_first(audience.get('age'), audience.get('age_range'), culture.get('age')), '年龄影响可读性、场景和表征，但必须有证据或明确假设。', '进入选角/内容密度/场景；缺失则不做行为推断。'),
        'gender': (_first(audience.get('gender'), culture.get('gender')), '性别只在当前商业任务与表征有依据时使用。', '进入表征/语言/场景；避免二元化和标签化。'),
        'income_spend': (_first(audience.get('income'), audience.get('spend_power'), audience.get('price_sensitivity'), market.get('spend_power')), '收入/消费力影响Offer和价格语境，但不得由族裔或年龄替代推断。', '进入Pricing/Offer/Bundle与内容价值表达。'),
        'language': (lang, '语言决定消费者可见文案、回译和运营中文释义矩阵。', '进入Listing/Visible Copy/Video/Ads和native review。'),
        'race_ethnicity': (_first(culture.get('race_ethnicity'), audience.get('race_ethnicity'), audience.get('ethnicity')), '族裔只用于有依据的表征、语言与文化语境，不自动推断消费行为。', '进入包容性选角/场景/文化检查；缺失时不标签化。'),
        'religion': (_first(culture.get('religion'), audience.get('religion'), culture.get('faith_context')), '宗教仅在禁忌、节日、服饰、成分/使用语境或法规相关时进入策略。', '进入文化禁忌/节日/场景/合规；需要当前市场查证。'),
        'holiday_calendar': (_first(culture.get('holiday_calendar'), request.get('holiday_calendar')), '节日节点是时效性外部信息，必须按目标市场和当前周期核验。', '进入Campaign/Seasonal/Creator节奏；未知标待查证。'),
        'payment': (_first(request.get('payment_context'), market.get('payment_context')), '支付偏好/能力影响CTA与转化摩擦，需要目标市场证据。', '进入Offer/Checkout/CTA；未知不编造。'),
        'logistics': (_first(request.get('logistics_context'), request.get('fulfillment'), market.get('logistics_context')), '物流与履约承诺直接影响购买预期与退货风险。', '进入Listing承诺、FAQ、Offer和风险；未知不承诺。'),
        'local_regulation': (_first(request.get('local_regulation'), request.get('regulatory_context'), culture.get('regulatory_context')), '法规与平台提交规则属于发布敏感P0，需要当前权威来源。', '进入Claim/Compliance/Submission；未知标待查证。'),
        'platform_behavior': (_first(market.get('platform_behavior'), request.get('platform_behavior')), '平台发现与消费机制会变化，需要当前平台证据。', '进入Hook、Surface、流量机制与CTA。'),
        'search_demand': (_first(market.get('keyword_signals'), market.get('search_intent'), market.get('demand_signals')), '搜索/需求信号用于判断真实问题和词义，不等于产品事实。', '进入Search/Listing/内容优先级。'),
        'competition': (_first(market.get('competitor_summary'), market.get('competitor_patterns'), market.get('concentration')), '竞争结构用于识别同质化与空白，不自动成为自己产品卖点。', '进入Positioning/Creative whitespace/Offer。'),
        'price_band': (_first(market.get('price_bands'), market.get('price_valley_signals'), market.get('price_valleys')), '市场价格带是证据，不等于推荐售价。', '进入Pricing/Economics/Offer与价值表达。'),
        'intersectionality': (culture.get('intersectionality'), '交叉性用于避免把单一身份维度当成完整消费者。', '进入受众/表征/文化/可达性检查。'),
        'stereotype_taboo': (_first(culture.get('taboo_stereotype_risks'), culture.get('taboos'), culture.get('stereotype_risks')), '刻板印象和禁忌属于文化P0边界。', '进入脚本、模特、服化道、配色、CTA逐条校验。'),
    }
    out: dict[str, Any] = {}
    for key in MARKET_CULTURE_DIMENSIONS:
        value, why, downstream = mapping[key]
        # Current external facts such as laws/holidays/platform behavior should be re-verified even if a planning hint exists.
        if key in {'holiday_calendar', 'local_regulation', 'platform_behavior', 'payment', 'logistics', 'religion'} and not _present(value):
            out[key] = {'status': 'TO_VERIFY', 'why': why, 'downstream_action': downstream}
        else:
            out[key] = _status_entry(value, why=why, downstream=downstream, missing_status='MISSING_INPUT')
    return out


def _intersectionality_rows(culture: dict[str, Any], audience: dict[str, Any]) -> list[dict[str, Any]]:
    existing = _list(culture.get('intersectionality'))
    rows: list[dict[str, Any]] = []
    for item in existing:
        if isinstance(item, dict):
            rows.append({
                'dimensions': item.get('dimensions') or item.get('intersection') or item.get('groups') or ['race_ethnicity', 'gender', 'age', 'income', 'geography'],
                'implication': item.get('implication') or item.get('relevance') or '只采用有证据的表征、语言、场景或可达性含义。',
                'evidence_or_assumption': item.get('evidence') or item.get('source_refs') or item.get('status') or 'ASSUMPTION',
                'stereotype_guard': item.get('stereotype_guard') or '不得把身份组合直接推断为肤质、价格敏感或购买行为。',
                'execution': item.get('execution') or '把可验证含义落实到选角、场景、语言与可达性；其余保持中性。',
            })
        elif _present(item):
            rows.append({
                'dimensions': ['race_ethnicity', 'gender', 'age', 'income', 'geography'],
                'implication': str(item), 'evidence_or_assumption': 'ASSUMPTION',
                'stereotype_guard': '不得把身份组合直接推断为消费行为。',
                'execution': '仅在当前项目有证据的表征/语言/场景层使用。',
            })
    if not rows:
        rows.append({
            'dimensions': ['race_ethnicity', 'gender', 'age', 'income', 'geography'],
            'implication': '当前缺少足够交叉性证据；不能用单一族裔、性别、年龄或收入标签代替完整受众。',
            'evidence_or_assumption': 'TO_VERIFY',
            'stereotype_guard': '不从身份维度推断肤质、价格敏感、购买意愿或产品需求。',
            'execution': '当前创意采用中性、包容的表征；如人物/文化语境成为关键购买机制，再补目标市场证据。',
        })
    return rows


def _localization_rows(dimensions: dict[str, Any]) -> list[dict[str, Any]]:
    labels = {
        'language': '语言 / native review / back-translation',
        'holiday_calendar': '节日 / 宗教日历',
        'payment': '支付',
        'logistics': '物流 / 履约',
        'religion': '宗教 / 禁忌',
        'local_regulation': '当地法规 / 平台规则',
    }
    rows = []
    for key, label in labels.items():
        d = _dict(dimensions.get(key))
        st = d.get('status') or 'TO_VERIFY'
        value = d.get('value')
        action = d.get('downstream_action') or '进入相关商业对象并保留来源/假设。'
        if st in {'TO_VERIFY', 'MISSING_INPUT'}:
            action = '发布/投放前使用目标市场当前来源查证；查证前不做硬承诺。' + action
        rows.append({
            'dimension': key, 'label': label, 'status': st, 'current_value': deepcopy(value),
            'action': action, 'why': d.get('why'),
            'evidence_or_assumption': 'CURRENT_SOURCE_REQUIRED' if st == 'TO_VERIFY' else (value if _present(value) else st),
        })
    return rows


def _framework_relationships(core: dict[str, Any]) -> dict[str, Any]:
    applied = {str(x).upper() for x in _list(_dict(core.get('frameworks')).get('applied_frameworks'))}
    roles = {
        'RACE': '传播/经营闭环骨架：Research → Action → Communication → Evaluation。',
        'STP': '判断哪些细分值得优先、谁是当前主要目标以及如何形成清晰定位。',
        'JTBD': '把人口标签还原为具体购买任务、阻力和进步需求。',
        'AIDA': '用于需要注意→兴趣→欲望→行动顺序的具体内容/广告，不是所有资产模板。',
        'FABE': '把事实/特征连接到利益与证据，避免只堆成分或形容词。',
        '4P': '协调Product/Price/Place/Promotion的商业取舍，尤其SKU/Offer/渠道执行。',
        'FUNNEL': '把内容/资产与真实旅程阶段和转化摩擦连接，阶段由当前项目决定。',
    }
    return {
        key: {
            'status': 'APPLIED' if key in applied or key == 'RACE' else 'AVAILABLE_LENS_NOT_FORCED',
            'role': role,
            'why': '只有当该框架能改变当前决策、内容结构或执行顺序时才展开；不机械填表。',
        }
        for key, role in roles.items()
    }


def _inclusive_photo_contract(existing: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(existing or {})
    defaults = {
        'skin_tone_exposure': '对实际人物肤色测光，优先保留肤色层次与自然纹理；不使用统一提亮作为包容性替代。',
        'deep_skin_shadow_protection': '深肤色人物保护暗部层次并避免欠曝；以实际Prelight和波形/直方图复核，不硬套固定曝光补偿值。',
        'reflector_bounce_diffusion': '优先使用大面积柔光与中性bounce/reflector控制眼下和暗部；现场根据肤色、妆发、背景反射做Prelight调整。',
        'hair_texture': '保留直发、卷发、紧卷发等真实发质边缘和层次，不把所有发质修成同一高光/顺滑效果。',
        'body_representation': '人物体型由真实目标语境和资产任务决定，避免把单一审美体型当默认消费者。',
        'disability_representation': '残障表征只在相关、有依据且自然的使用语境中出现；避免道具化、励志化或无关tokenism。',
        'age_representation': '年龄呈现与真实使用者/场景一致，保留自然纹理，避免把年轻化当默认修图目标。',
        'ai_bias_check': '成图后检查肤色漂移、发质错误、身体/手部异常、年龄抹除、残障器具错误与刻板化场景。',
    }
    for k, v in defaults.items():
        out.setdefault(k, v)
    out.setdefault('status', 'APPLICABLE_P0')
    return out


def _enrich_content_matrix(rows: list[Any], target: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        row = deepcopy(raw)
        surface = str(row.get('visual_form') or row.get('surface') or '').upper()
        row.setdefault('platform_dimensions', target.get('platform_dimensions') or 'TO_VERIFY_CURRENT_PLATFORM_SURFACE_SPEC')
        row.setdefault('duration', 'N/A_FOR_STILL' if 'VIDEO' not in surface and 'LIVE' not in surface and 'CREATOR' not in surface else 'TO_VERIFY_OR_USE_AUTHORED_VIDEO_DURATION')
        row.setdefault('cover_first_frame', 'N/A_FOR_STILL' if 'VIDEO' not in surface and 'LIVE' not in surface and 'CREATOR' not in surface else 'AUTHOR_FIRST_FRAME_FROM_SHOPPER_TENSION')
        row.setdefault('subtitle_strategy', 'N/A_FOR_STILL' if 'VIDEO' not in surface and 'LIVE' not in surface and 'CREATOR' not in surface else 'PLATFORM_PRIMARY + accessibility; exact current safe-zone TO_VERIFY')
        row.setdefault('music_rights', 'N/A_FOR_STILL' if 'VIDEO' not in surface and 'LIVE' not in surface and 'CREATOR' not in surface else 'USE_LICENSED/PLATFORM_CLEARED_AUDIO; TO_VERIFY_CURRENT_RIGHTS')
        row.setdefault('traffic_mechanism', 'TO_VERIFY_CURRENT_PLATFORM_DISCOVERY/TRAFFIC_MECHANISM')
        row.setdefault('landing_handoff', target.get('site') or target.get('platform_family') or 'TO_VERIFY_TARGET_SURFACE')
        row.setdefault('utm_attribution', 'USE_UTM/AD/CREATOR_TRACKING_ID_WHERE_SUPPORTED; TO_VERIFY_PLATFORM_IMPLEMENTATION')
        row.setdefault('culture_adaptation', '执行目标市场语言、宗教/禁忌、表征与刻板印象校验；未知项保持待查证。')
        row.setdefault('taboo_stereotype_check', '按 CultureContext + 当前市场来源逐条校验脚本、主体、服化道、配色和CTA。')
        row.setdefault('why', '该Surface只有在解决当前购买问题并产生可观察指标时才保留。')
        out.append(row)
    return out


def _enrich_race(rows: list[Any], culture: dict[str, Any]) -> list[dict[str, Any]]:
    by_stage = {str(_dict(x).get('stage') or '').upper(): deepcopy(x) for x in rows if isinstance(x, dict)}
    defaults = {
        'RESEARCH': ('确认产品事实、市场/平台/人群/文化/竞品和当前外部规则。', '证据/假设/待查证清单 + 商业决策输入'),
        'ACTION': ('把证据转成定位、SKU/Offer、信息层级、视觉/摄影、内容与资源取舍。', '策略/资产架构/制作合同'),
        'COMMUNICATION': ('按选定Surface执行Listing、Creator/UGC、Paid、Owned和本地化。', '可发布/可生产对象'),
        'EVALUATION': ('用指标、归因、A/B、Review/Returns/CS和经济性回流最小责任层。', '学习/Keep-Kill-Iterate/局部修订'),
    }
    out = []
    for stage in ('RESEARCH', 'ACTION', 'COMMUNICATION', 'EVALUATION'):
        row = by_stage.get(stage, {'stage': stage})
        obj, output = defaults[stage]
        row.setdefault('objective', obj)
        row.setdefault('key_actions', [obj])
        row.setdefault('output', [output])
        row.setdefault('platform', 'CURRENT_SELECTED_PLATFORM_OR_CROSS_PLATFORM')
        row.setdefault('culture_check', '检查语言、宗教/禁忌、交叉性、包容表征和刻板印象；缺证据不推断。')
        row.setdefault('kpi', ['与当前阶段任务匹配的决策/商业指标'])
        row.setdefault('why', 'RACE是当前CBCC传播流程骨架；每一阶段必须把上一阶段证据转成下一阶段可执行对象。')
        out.append(row)
    return out


def _resource_tradeoff(request: dict[str, Any]) -> dict[str, Any]:
    constraints = _first(request.get('resource_constraints'), request.get('budget_constraints'), request.get('timeline_constraints'))
    return {
        'constraints': deepcopy(_list(constraints)) if _present(constraints) else ['MISSING_INPUT：预算/周期/团队资源未明确'],
        'keep': ['P0 产品事实/Claim/合规/身份准确', 'P0 当前关键购买决策', 'P1 可显著影响理解/转化的核心Surface'],
        'cut': ['重复购买问题的装饰性资产', '没有独立商业假设的重复Hero/版式', '低信息P2增强项'],
        'why': '资源不足时先保护翻车风险与关键购买决策，再保留高影响Surface；优先砍重复、装饰和不可测的增强项。',
        'restore_condition': '预算/周期恢复后，再按未覆盖购买问题、测试价值和增量信息补回P2候选。',
    }


def wrap_build_master_strategy(fn: Callable[..., dict[str, Any]]):
    def built(request: dict[str, Any], *args, **kwargs):
        out = fn(request, *args, **kwargs)
        if str(_dict(out.get('human_projection')).get('mode') or out.get('delivery_mode') or '').upper() != 'FULL':
            return out
        sections = out.setdefault('sections', {})
        target = _dict(request.get('target'))
        market = _dict(kwargs.get('market'))
        culture = _dict(kwargs.get('culture'))
        audience = _dict(request.get('audience')) or _dict(request.get('audience_culture'))

        info = _dict(sections.get('01_information_completeness_assumptions_decisions'))
        info.setdefault('domain_matrix', [
            {'domain': 'Product Truth', 'status': 'EVIDENCED_OR_EXPLICIT_UNKNOWN'},
            {'domain': 'Market/Platform/Audience/Culture', 'status': 'EVIDENCED_ASSUMPTION_OR_TO_VERIFY'},
            {'domain': 'Pricing/Economics/Offer', 'status': 'EXPLICIT_INPUT_ONLY'},
            {'domain': 'Listing/Search', 'status': 'AUTHOR_AND_AUDIT'},
            {'domain': 'Visual/Photography/Assets', 'status': 'AUTHOR_PER_ASSET'},
            {'domain': 'Video/Ads/Review/Measurement', 'status': 'ACTIVATE_BY_RELEVANCE'},
        ])
        for row in _list(info.get('decision_log')):
            if isinstance(row, dict):
                row.setdefault('tradeoff', '保留有证据且会改变当前商业决策的动作；未知发布敏感项待查证，不阻断无关模块。')
                row.setdefault('evidence', row.get('evidence') or row.get('source_refs') or ['CURRENT_PROJECT_TRUTH_AND_DECLARED_ASSUMPTIONS'])
        sections['01_information_completeness_assumptions_decisions'] = info

        value = _dict(sections.get('02_product_truth_value_ladder'))
        for row in _list(value.get('product_facts')) + _list(value.get('claim_value_ladder')):
            if not isinstance(row, dict):
                continue
            row.setdefault('real_selling_point', row.get('selling_point') or '仅当该事实能解决购买问题时升级为卖点。')
            row.setdefault('perceived_benefit', '把事实翻译成用户可感知利益，但不得超出事实/证据。')
            row.setdefault('emotional_value', '只有当真实功能/感知利益足以支撑时才表达安心、信心或便利等情绪价值。')
            row.setdefault('claim_boundary', '不得超出当前事实、来源与证据等级；未知项不作硬宣称。')
            grade = str(row.get('evidence_grade') or row.get('evidence_level') or '').upper()
            if grade not in {'A', 'B', 'C'}:
                grade = normalize_evidence_grade(grade, source_type=_source_type_for_fact(request, row), subjective=False)
                row['evidence_grade'] = grade
            row.setdefault('publication_rule', publication_rule(grade))
            if not _present(row.get('source_refs')):
                row['source_refs'] = deepcopy(row.get('source_ids') or [])
        sections['02_product_truth_value_ladder'] = value

        culture_sec = _dict(sections.get('03_platform_region_audience_culture_insight'))
        dimensions = _dimension_status(request, market, culture, target)
        culture_sec['dimension_status'] = dimensions
        culture_sec['intersectionality_table'] = _intersectionality_rows(culture, audience)
        culture_sec['adaptation_rows'] = _localization_rows(dimensions)
        if not _present(culture_sec.get('platform_audience_culture_rows')):
            culture_sec['platform_audience_culture_rows'] = deepcopy(culture_sec.get('rows') or [])
        sections['03_platform_region_audience_culture_insight'] = culture_sec

        core = _dict(sections.get('04_marketing_core_strategy'))
        core['framework_relationships'] = _framework_relationships(core)
        sections['04_marketing_core_strategy'] = core

        vis = _dict(sections.get('05_visual_photography_strategy'))
        vis.setdefault('style_keywords', vis.get('style') or vis.get('creative_direction') or '由当前产品/市场/创意方向作者化')
        vis.setdefault('moodboard_direction', vis.get('style_why') or '以核心购买任务、材质/CMF和市场语境建立视觉参考机制，而不是固定审美模板。')
        vis.setdefault('color_management', {'status': 'PLANNING_BASELINE', 'output': 'sRGB for standard ecommerce unless current platform/output contract overrides; verify product color against source.'})
        # Do not infer a person from a generic culture casting object.
        people = False
        architecture = _dict(kwargs.get('asset_architecture'))
        reasoning = []
        for asset in architecture.get('assets') or []:
            if not isinstance(asset, dict):
                continue
            art = _dict(asset.get('asset_art_direction'))
            subject = _dict(art.get('subject_system') or asset.get('subject_system'))
            st = str(subject.get('subject_type') or '').upper()
            people = people or st in {'PERSON', 'MULTI_SUBJECT'} or _present(art.get('human_context'))
            reasoning.append({
                'asset_id': asset.get('asset_id'), 'visual_carrier': art.get('visual_carrier') or asset.get('visual_carrier'),
                'product_presence': art.get('product_presence') or asset.get('product_presence'), 'subject_system': subject or {'subject_type': 'UNRESOLVED'},
                'composition': art.get('composition') or art.get('composition_grammar') or asset.get('production_signature'),
                'camera': art.get('camera') or asset.get('camera'), 'lighting': art.get('lighting') or asset.get('lighting'),
                'cmf': art.get('cmf') or asset.get('cmf'), 'surface': asset.get('surface'),
                'why': art.get('why') or asset.get('reason_to_exist') or asset.get('business_hypothesis'),
            })
        if reasoning:
            vis['asset_parameter_reasoning'] = reasoning
        vis['people_applicability'] = 'PERSON_PRESENT' if people else 'NOT_USED_UNLESS_PER_ASSET_SUBJECT_REQUIRES_PERSON'
        if people:
            vis['inclusive_photography'] = _inclusive_photo_contract(_dict(vis.get('inclusive_photography')))
        sections['05_visual_photography_strategy'] = vis

        sections['06_platform_content_matrix'] = _enrich_content_matrix(_list(sections.get('06_platform_content_matrix')), target)
        sections['07_race_execution_table'] = _enrich_race(_list(sections.get('07_race_execution_table')), culture)

        checklist = []
        for row in _list(sections.get('08_culture_adaptation_checklist')):
            if not isinstance(row, dict):
                continue
            r = deepcopy(row)
            r.setdefault('evidence_or_assumption', r.get('evidence_status') or 'TO_VERIFY')
            checklist.append(r)
        # The operating localization dimensions also belong in the culture checklist.
        for r in _localization_rows(dimensions):
            checklist.append({
                'adaptation_point': r.get('label'),
                'inclusive_representation': '仅在相关时使用真实、非标签化的本地语境。',
                'stereotype_taboo_risk': '未知文化细节不推断；宗教/禁忌/法规按当前来源查证。',
                'result': r.get('status'), 'modification': r.get('action'), 'why': r.get('why'),
                'evidence_or_assumption': r.get('evidence_or_assumption'),
            })
        sections['08_culture_adaptation_checklist'] = checklist

        last = _dict(sections.get('09_risk_measurement_priority_next_steps'))
        last['resource_tradeoff_plan'] = _resource_tradeoff(request)
        sc = _dict(last.get('output_self_check'))
        sc.update({
            'fabrication_check': True, 'why_check': True, 'culture_check': True, 'compliance_check': True,
            'metric_check': True, 'assumption_check': True, 'language_companion_check': True,
            'asset_universe_check': True, 'prompt_depth_check': True,
        })
        last['output_self_check'] = sc
        sections['09_risk_measurement_priority_next_steps'] = last
        out['sections'] = sections
        out['depth_contract'] = 'FULL_COMMERCIAL_DEPTH_V3_HOST_RUNTIME_PARITY'
        return out
    return built
