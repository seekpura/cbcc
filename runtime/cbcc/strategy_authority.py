from __future__ import annotations
from pathlib import Path
from typing import Any
import json


def _lst(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _why(what: str, why: str, evidence=None, consumer_logic='', platform_logic='', culture_logic='', business_logic='', execution='', measurement=''):
    return {
        'what': what,
        'why': why,
        'evidence': _lst(evidence),
        'consumer_logic': consumer_logic,
        'platform_logic': platform_logic,
        'culture_logic': culture_logic,
        'business_logic': business_logic,
        'execution': execution,
        'measurement': measurement,
    }


def _claim_text(c):
    return c.get('claim') or c.get('text') or c.get('name') or ''


def product_colors(product):
    vals = []
    for k in ['brand_colors', 'colors', 'packaging_colors']:
        v = product.get(k)
        if isinstance(v, list):
            vals.extend(v)
        elif v:
            vals.append(v)
    return vals


def build_information_audit(request: dict[str, Any], research_gate: dict[str, Any]) -> dict[str, Any]:
    required = {
        'product.name': (request.get('product') or {}).get('name'),
        'target.market': (request.get('target') or {}).get('market'),
        'target.platform_family': (request.get('target') or {}).get('platform_family'),
        'target.site': (request.get('target') or {}).get('site'),
    }
    missing = [k for k, v in required.items() if v in (None, '', [])]
    pending = [
        {
            'item': x.get('query') or x.get('reason'),
            'reason': x.get('reason'),
            'required_for': x.get('required_for', []),
            'status': x.get('status'),
        }
        for x in research_gate.get('actions', [])
        if x.get('status') != 'RESOLVED'
    ]
    assumptions = []
    for a in request.get('assumptions', []):
        if isinstance(a, str):
            text = a
        else:
            text = a.get('assumption') or a.get('text') or str(a)
        assumptions.append({'assumption': text, 'status': 'ASSUMPTION'})
    decisions = [
        _why(
            '在已知证据范围内继续完成正向商业策划',
            '尚未核实的提交/发布敏感信息保留为待确认，但不应阻断已有事实足以支持的市场、定位、内容、视觉与资产策划。',
            evidence=[x.get('source_id') for x in request.get('sources', []) if x.get('source_id')],
            business_logic='保证策略工作不中断，同时把‘可以策划’与‘可以最终提交/发布’分开管理。',
            execution='先完成可确定的策略与制作方案，仅对缺证据的具体提交动作保留待确认。',
            measurement='在对应信息影响发布/提交前完成核验；不影响的模块继续执行。',
        )
    ]
    return {
        'completeness_status': 'INCOMPLETE' if missing or pending else 'SUFFICIENT_FOR_CURRENT_SCOPE',
        'required_missing': missing,
        'pending_confirmations': pending,
        'assumptions': assumptions,
        'decision_log': decisions,
    }


def build_value_ladder(product: dict[str, Any], claims: list[dict[str, Any]], sources: list[dict[str, Any]]) -> dict[str, Any]:
    src_ids = [s.get('source_id') for s in sources if s.get('source_id')]
    supplied = product.get('facts') if isinstance(product.get('facts'), dict) else product
    facts = []
    for k, v in supplied.items():
        if k in {'name', 'brand', 'category'} or v in (None, '', [], {}):
            continue
        facts.append(
            {
                'fact': k,
                'value': v,
                'source_ids': src_ids,
                'evidence_level': 'SOURCE_LINKED' if src_ids else 'USER_SUPPLIED',
                'selling_point': '当该事实能改变真实购买决策时，可升级为真实卖点。',
                'perceived_benefit': '结合目标人群与JTBD翻译为可感知利益，但利益表达不能偷换原始事实。',
                'emotional_value': '只有当功能/感知利益足以支撑安心感、信心、便利或身份认同时，才升级为情绪价值。',
                'publication_status': 'FACT',
                'why': '事实只有连接到真实购买问题，并以匹配证据强度的表达出现时，才具有商业价值。',
            }
        )
    claim_rows = []
    for c in claims:
        status = str(c.get('status') or c.get('evidence_level') or 'PENDING').upper()
        claim_rows.append(
            {
                'claim': _claim_text(c),
                'type': c.get('type') or c.get('classification') or 'REAL_SELLING_POINT',
                'evidence_level': c.get('evidence_level') or status,
                'source_ids': c.get('source_ids', []),
                'publication_status': 'ACTIVE' if str(c.get('evidence_grade') or c.get('evidence_level') or '').upper() in {'A','B'} and str(c.get('publication_status') or '').upper() != 'BLOCKED' else 'PENDING_EVIDENCE',
                'why': c.get('rationale') or '宣称强度必须与证据等级和它承担的购买决策任务匹配。',
            }
        )
    return {
        'product_facts': facts,
        'claim_value_ladder': claim_rows,
        'principle': 'Fact → advantage → perceived benefit → emotional value → proof, with each layer kept distinct.',
    }


def build_product_strategy(request: dict[str, Any], market: dict[str, Any] | None, economics: dict[str, Any] | None) -> dict[str, Any]:
    skus = request.get('skus') or [
        {
            'sku': request.get('sku', 'SKU-1'),
            'name': (request.get('product') or {}).get('name'),
            'price': (request.get('offer_economics') or {}).get('price'),
        }
    ]
    price_signals = (market or {}).get('price_valley_signals', [])
    config = (market or {}).get('configuration', [])
    rows = []
    for i, s in enumerate(skus):
        explicit = s.get('role')
        if explicit:
            role = explicit
        elif len(skus) == 1:
            role = 'HERO'
        elif i == 0:
            role = 'HERO'
        elif s.get('bundle') or s.get('multipack'):
            role = 'BUNDLE'
        else:
            role = 'ASSORTMENT_SUPPORT'
        rows.append(
            {
                'sku': s.get('sku') or f'SKU-{i + 1}',
                'role': role,
                'why': s.get('role_rationale')
                or ('单SKU项目默认由该SKU承担核心转化主张；若后续有多SKU，再按需求、利润、生命周期和渠道动态分工。' if role == 'HERO' else '在利润、需求与SKU组合关系比较完成前，该角色仅作为暂定策略。'),
                'price': s.get('price'),
                'market_signal': price_signals,
                'configuration_signal': config,
            }
        )
    return {
        'sku_roles': rows,
        'portfolio_principle': 'SKU角色由需求、利润、生命周期和渠道任务动态决定，不采用固定四角色模板。',
        'economics_status': (economics or {}).get('status'),
        'opportunity_signals': {'price_valleys': price_signals, 'configurations': config},
    }


def build_positioning(request: dict[str, Any], culture: dict[str, Any], product_strategy: dict[str, Any]) -> dict[str, Any]:
    product = request.get('product') or {}
    target = request.get('target') or {}
    audience = request.get('audience') or request.get('audience_culture') or {}
    supplied = request.get('positioning') or {}
    primary = (
        supplied.get('primary_conversion_proposition')
        or product.get('primary_conversion_proposition')
        or product.get('verified_selling_point')
        or product.get('name', 'Product')
    )
    target_desc = supplied.get('target') or audience.get('primary_segment') or target.get('market', 'target market')
    frame = supplied.get('frame_of_reference') or product.get('category', 'category')
    statement = supplied.get('statement') or f"For {target_desc}, {product.get('name', 'the product')} is a {frame} whose first communication priority is: {primary}."
    secondary = supplied.get('secondary_reasons') or product.get('secondary_reasons') or []
    trust = supplied.get('trust_drivers') or product.get('trust_drivers') or []
    objections = supplied.get('objection_reducers') or product.get('objection_reducers') or []
    hierarchy = [{'priority': 'P0', 'message': primary, 'why': '首屏只保留一个核心记忆点，可降低信息竞争，让Hero与Listing首屏拥有明确任务。'}]
    for x in secondary:
        hierarchy.append({'priority': 'P1', 'message': x, 'why': '用户理解核心主张后，再用次级购买理由增强相关性、利益或证据。'})
    for x in trust + objections:
        hierarchy.append({'priority': 'P2', 'message': x, 'why': '身份识别与核心价值建立后，再用信任与异议消解推动转化。'})
    return {
        'positioning_statement': statement,
        'primary_conversion_proposition': primary,
        'secondary_reasons_to_buy': secondary,
        'trust_drivers': trust,
        'objection_reducers': objections,
        'message_hierarchy': hierarchy,
        'why': _why(
            '确定一个核心转化主张',
            '第一印象需要形成一个清晰、可记忆的继续了解理由，而不是让多个卖点平分注意力。',
            consumer_logic='降低认知负担，让用户更快判断‘这是不是适合我’。',
            platform_logic='适配搜索、商品卡、PDP首屏等注意力高度压缩的Surface。',
            culture_logic='先确定真实价值，再做本地语言、人物与文化表达；文化适配用于优化沟通，不用于创造不存在的产品价值。',
            business_logic='承担点击、快速理解并进入后续证据层的商业任务。',
            execution='标题、Hero和首屏优先表达核心主张，再按购买问题顺序展开次级理由与证据。',
            measurement='可行时用CTR、首屏理解、CVR或对应Surface指标做受控比较。',
        ),
        'product_strategy': product_strategy,
    }


def build_marketing_frameworks(positioning: dict[str, Any], questions: list[str], target: dict[str, Any], framework_plan: Any = None) -> dict[str, Any]:
    """Apply only decision frameworks selected by the user/host Agent. No framework bundle is mandatory."""
    custom = {}
    if isinstance(framework_plan, dict):
        requested = framework_plan.get('frameworks') or framework_plan.get('requested') or []
        custom = framework_plan.get('custom') or {}
    else:
        requested = framework_plan or []
    if not isinstance(requested, (list, tuple, set, frozenset)):
        requested = [requested]
    requested = [str(x).upper() for x in requested if str(x or '').strip()]
    out: dict[str, Any] = {
        'status':'FRAMEWORKS_APPLIED' if requested or custom else 'NO_FRAMEWORK_REQUIRED',
        'applied_frameworks':requested,
        'why':'Frameworks are optional lenses. The Agent selects them only when they change a concrete commerce decision; Product Truth, evidence and shopper decisions remain the authority.',
    }
    if 'STP' in requested:
        out['STP']={
            'segmentation_basis':'Use only evidence-backed segmentation variables relevant to this decision.',
            'targeting':'Prioritize the segment whose job/barrier aligns most strongly with product truth and offer.',
            'positioning':positioning.get('positioning_statement'),
        }
    if 'JTBD' in requested:
        out['JTBD']={'shopper_questions':questions,'job_statement':'Help the shopper make the next purchase decision with the minimum necessary information and proof.'}
    if '4P' in requested:
        out['4P']={
            'product':'Express real product value and SKU role.',
            'price':'Use economics + market context; do not choose price from competitor averaging alone.',
            'place':target.get('platform_family'),
            'promotion':'Let the current decision architecture determine message sequence and channel use.',
        }
    if 'FUNNEL' in requested:
        out['funnel']={'rule':'Derive stages from the observed buyer journey and current decision barriers; do not force a universal stage list.'}
    if 'RACE' in requested:
        out['RACE']=[
            {'stage':'RESEARCH','objective':'Resolve evidence gaps that can materially change current commerce decisions.','key_actions':'agent-selected research','output':'evidence + decision updates','platform':target.get('platform_family'),'kpi':'decision-changing evidence / unresolved material risk','why':'Research exists to change or validate decisions, not to complete a checklist.'},
            {'stage':'ACTION','objective':'Convert sufficient evidence into product/offer/content/creative/production choices.','key_actions':'agent-selected decision work','output':'strategy and execution contracts','platform':target.get('platform_family'),'kpi':'decision coverage / execution readiness','why':'Action is whatever decision work is needed for the current goal.'},
            {'stage':'COMMUNICATION','objective':'Execute only the surfaces and messages selected for the current buyer journey.','key_actions':'agent-selected surfaces/assets','output':'customer-facing communication','platform':target.get('platform_family'),'kpi':'surface-appropriate outcome metric','why':'Communication follows the actual asset architecture, not a channel quota.'},
            {'stage':'EVALUATION','objective':'Use observed outcomes to decide whether to stop, locally revise or replan.','key_actions':'measurement / feedback / revision routing','output':'learning + next action','platform':target.get('platform_family'),'kpi':'material learning / incremental outcome','why':'Evaluation closes the loop only where new evidence can improve the result.'},
        ]
    if isinstance(custom, dict):
        out['custom']=custom
    return out

def build_culture_insights(target: dict[str, Any], culture: dict[str, Any]) -> dict[str, Any]:
    rows = []
    re_data = culture.get('race_ethnicity') or []
    if isinstance(re_data, dict):
        re_data = [re_data]
    for r in re_data:
        rows.append(
            {
                'platform': target.get('platform_family'),
                'region': target.get('market'),
                'audience': r.get('audience') or '相关目标人群',
                'race_ethnicity': r.get('group') or r.get('race_ethnicity') or r.get('name'),
                'intersectionality': culture.get('intersectionality', []),
                'cultural_adaptation': culture.get('visual_implications', []) + culture.get('copy_implications', []),
                'stereotype_taboo_check': 'Use identity as representation/context evidence; do not infer unsupported behavior.',
                'why': r.get('relevance') or '有证据时，人物代表性、语言和文化语境应贴近真实目标市场。',
            }
        )
    if not rows:
        rows.append(
            {
                'platform': target.get('platform_family'),
                'region': target.get('market'),
                'audience': '目标人群',
                'race_ethnicity': '未提供可靠族裔事实，不做推断',
                'intersectionality': culture.get('intersectionality', []),
                'cultural_adaptation': culture.get('visual_implications', []) + culture.get('copy_implications', []),
                'stereotype_taboo_check': '不基于缺失信息做人口/族裔推断。',
                'why': '文化适配以证据为基础；缺少身份数据时，不凭空创造族裔细分。',
            }
        )
    return {
        'rows': rows,
        'language_profiles': culture.get('language_profiles', {}),
        'casting_implications': culture.get('casting_implications', []),
        'visual_implications': culture.get('visual_implications', []),
        'copy_implications': culture.get('copy_implications', []),
    }


def build_visual_strategy(request: dict[str, Any], creative: dict[str, Any], photography_validation: dict[str, Any] | None, culture: dict[str, Any]) -> dict[str, Any]:
    vs = request.get('visual_strategy') or {}
    photo = request.get('photography_contract') or {}
    palette = vs.get('palette') or (request.get('cmf') or {}).get('colors') or product_colors(request.get('product') or {})
    return {
        'creative_direction': creative.get('creative_council', {}),
        'surface_architecture': creative.get('surface_architecture', {}),
        'asset_expression_assignment': creative.get('asset_expression_assignment', {}),
        'video_creator_plan': creative.get('video_creator_plan', {}),
        'paid_campaign_architecture': creative.get('paid_campaign_architecture', {}),
        'style': vs.get('style') or '从产品真实情况、类目语境、目标人群与已选创意方向共同推导。',
        'style_why': vs.get('style_why') or '视觉风格首先服务核心主张的识别与理解，同时避开类目中已高度同质化的表达。',
        'palette_hex': palette,
        'composition': vs.get('composition') or photo.get('composition', {}),
        'lighting_framework': photo.get('lighting', {}),
        'camera': photo.get('camera', {}),
        'lens': photo.get('lens', {}),
        'focus_dof': photo.get('focus_dof', {}),
        'scene': vs.get('scene') or photo.get('scene', {}),
        'props': vs.get('props') or photo.get('props', []),
        'casting': vs.get('casting') or {'culture_implications': culture.get('casting_implications', [])},
        'wardrobe_hair_makeup': vs.get('wardrobe_hair_makeup') or photo.get('styling', {}),
        'platform_dimensions': vs.get('platform_dimensions') or {},
        'shot_list': vs.get('shot_list') or request.get('shot_list', []),
        'cmf': creative.get('cmf', {}),
        'inclusive_photography': creative.get('inclusive_photography', {}),
        'photography_validation': photography_validation,
        'why': _why(
            '把商业策略翻译成可直接拍摄/制作的视觉系统',
            '风格、机位、灯光、CMF与选角都应服务产品识别、核心主张、证据和信任，而不是为了视觉新奇而存在。',
            consumer_logic='摄影决定用户第一眼看见什么、先相信什么，因此直接影响信息优先级。',
            platform_logic='构图与信息密度必须适配目标Surface和移动端裁切/浏览场景。',
            culture_logic='人物、造型、动作和语言应遵循CultureContext，并避免刻板印象。',
            business_logic='提升整套资产一致性，并减少摄影师、设计师和生成模型的二次猜测。',
            execution='据此形成逐镜头执行任务，并继续进入逐资产独立生产包。',
            measurement='通过视觉QA与资产级CTR/CVR/互动等指标，在可受控的情况下验证。',
        ),
    }


def build_platform_content_matrix(target: dict[str, Any] | list[dict[str,Any]], culture: dict[str, Any], questions: list[str], asset_arch: dict[str, Any], positioning: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    assets = asset_arch.get('assets', [])
    targets=target if isinstance(target,list) else [target]
    for t in targets:
      for i, a in enumerate(assets):
          if a.get('consumer_question'):
              q = a['consumer_question']
          elif questions:
              q = questions[min(i, len(questions) - 1)]
          else:
              q = ''
          headline = (a.get('visible_copy') or {}).get('headline')
          hook = headline or (positioning.get('primary_conversion_proposition') if i == 0 else q)
          rows.append(
              {
                  'platform': t.get('platform_family'),
                  'site': t.get('site'),
                  'audience': 'TargetContext / AudienceContext 中的核心目标人群',
                  'topic': q,
                  'hook': hook,
                  'script_structure': a.get('script_structure') or a.get('narrative_structure') or '由当前资产的消费者问题、证据关系、Surface与交互任务动态决定；不套固定钩子/证据/CTA顺序。',
                  'visual_form': f"{a.get('asset_type')} / {a.get('surface')}",
                  'cta': (a.get('visible_copy') or {}).get('cta') or '使用与当前旅程阶段匹配的平台原生下一步动作。',
                  'metric': a.get('success_metric') or ('CTR' if a.get('surface') in {'SEARCH_RESULTS', 'PAID_AD'} else 'CVR / comprehension / engagement as appropriate'),
                  'race_stage': a.get('race_stage'),
                  'culture_adaptation': culture.get('visual_implications', []) + culture.get('copy_implications', []),
                  'taboo_stereotype_check': '依据CultureContext做适配，不从身份直接推导消费行为。',
                  'why': a.get('reason_to_exist') or f'Needed to resolve shopper question: {q}',
              }
          )
    return rows


def build_culture_checklist(culture: dict[str, Any]) -> list[dict[str, Any]]:
    points = []
    for kind, key in [('Language', 'copy_implications'), ('Visual representation', 'visual_implications'), ('Casting', 'casting_implications')]:
        for v in culture.get(key, []) or []:
            points.append(
                {
                    'adaptation_point': kind,
                    'inclusive_representation': v,
                    'stereotype_taboo_risk': '依据证据校验，并避免从身份直接推断行为。',
                    'evidence_status': culture.get('status'),
                    'result': 'APPLY_WHERE_RELEVANT',
                    'modification': '落实到选角、文案、场景与摄影合同。',
                    'why': '只有当适配能让目标用户感到更自然、更易理解或更具包容性时，才有价值。',
                }
            )
    if not points:
        points.append(
            {
                'adaptation_point': '证据驱动的本地化',
                'inclusive_representation': '没有证据时不引入人口/族裔刻板印象。',
                'stereotype_taboo_risk': '未知文化细节保留为研究问题，不编造成固定规则。',
                'evidence_status': culture.get('status'),
                'result': 'BASELINE',
                'modification': '先使用语言与平台基础规范；当文化差异会影响商业决策时，再补强目标人群证据。',
                'why': '与其编造文化细节，不如采用中性、证据驱动的基础方案。',
            }
        )
    return points


def build_ab_hypotheses(positioning:dict[str,Any], visual:dict[str,Any], content_matrix:list[dict[str,Any]]) -> list[dict[str,Any]]:
    prop=positioning.get('primary_conversion_proposition')
    rows=[]
    if prop:
        rows.append({'id':'AB-HERO-PROP','variable':'首屏核心主张表达','control':'当前/基线Hero表达','variant':f'围绕核心主张“{prop}”形成单一第一记忆点','hypothesis':'若首屏只突出一个核心购买理由，点击与首屏理解应优于多卖点并列。','primary_metric':'CTR / 首屏理解 / PDP progression（按Surface选）','why':'验证信息层级，而不是把整套视觉同时重做。','hold_constant':['价格','SKU','主要投放人群','其他非测试内容']})
    if visual.get('casting'):
        rows.append({'id':'AB-CONTEXT','variable':'人物/使用语境','control':'产品主导视觉','variant':'仅在战略需要时加入目标市场真实人物/使用语境','hypothesis':'当购买问题涉及“是否适合我/如何使用”时，真实语境可能提升相关性；若问题只需识别产品，则未必需要人物。','primary_metric':'engagement / CVR / asset interaction','why':'把“要不要模特”作为消费者问题测试，而不是固定模板。','hold_constant':['核心主张','产品本体','主要文案']})
    if len(content_matrix)>1:
        rows.append({'id':'AB-PROOF-ORDER','variable':'证据顺序','control':'核心主张后立即进入功能/成分证据','variant':'核心主张后先做适配/异议消解，再进入证据','hypothesis':'不同购买阻力可能需要不同的信息顺序。','primary_metric':'PDP progression / CVR','why':'验证Belief Sequence，而不是只比较视觉风格。','hold_constant':['产品','价格','主Claim']})
    return rows

def build_priority_plan(info: dict[str, Any], research_gate: dict[str, Any], compliance: dict[str, Any], experiment: dict[str, Any] | None) -> dict[str, Any]:
    p0 = [
        {
            'action': '发布敏感内容前，解决任何产品事实冲突或缺乏证据的硬宣称。',
            'why': '策略可以继续推进，但未经支持的硬宣称不能被包装成公开事实。',
        }
    ]
    p1 = [
        {
            'action': x.get('query') or x.get('reason'),
            'why': x.get('reason'),
            'required_for': x.get('required_for', []),
        }
        for x in research_gate.get('actions', [])
        if x.get('status') != 'RESOLVED'
    ]
    if not p1:
        p1 = [
            {
                'action': '依据已批准策略与当前目标平台/语言要求完成最终执行细节。',
                'why': '策略必须真正翻译成平台原生执行，而不是停留在泛化方案。',
            }
        ]
    p2 = [
        {
            'action': '建立Baseline后，再对创意、Listing或Offer进行受控实验。',
            'why': '优化应从真实用户响应中学习，而不是上线前无限重做。',
        }
    ]
    return {
        'P0': p0,
        'P1': p1,
        'P2': p2,
        'next_information_needed': info.get('required_missing', []) + [x.get('item') for x in info.get('pending_confirmations', []) if x.get('item')],
        'experiment_status': (experiment or {}).get('decision') or (experiment or {}).get('status'),
        'compliance_status': compliance.get('status'),
    }


def build_master_strategy(request: dict[str, Any], *, truth: dict[str, Any], research_gate: dict[str, Any], market: dict[str, Any] | None, economics: dict[str, Any] | None, culture: dict[str, Any], platform_compile: dict[str, Any], creative: dict[str, Any], photography_validation: dict[str, Any] | None, asset_architecture: dict[str, Any], compliance: dict[str, Any], experiment: dict[str, Any] | None = None) -> dict[str, Any]:
    info = build_information_audit(request, research_gate)
    value = build_value_ladder(request.get('product') or {}, request.get('claims', []), request.get('sources', []))
    product_strategy = build_product_strategy(request, market, economics)
    positioning = build_positioning(request, culture, product_strategy)
    questions = request.get('shopper_questions') or [a.get('consumer_question') for a in asset_architecture.get('assets', []) if a.get('consumer_question')]
    agent_plan=request.get('_agent_autonomy_plan') or {}
    framework_plan=(agent_plan.get('strategy_frameworks') if isinstance(agent_plan,dict) else None)
    if framework_plan is None: framework_plan=request.get('marketing_frameworks') or request.get('persuasion_frameworks')
    marketing = build_marketing_frameworks(positioning, questions, request.get('target') or {}, framework_plan)
    culture_insights = build_culture_insights(request.get('target') or {}, culture)
    visual = build_visual_strategy(request, creative, photography_validation, culture)
    content_targets=request.get('platform_content_targets') or [request.get('target') or {}]
    content_matrix = build_platform_content_matrix(content_targets, culture, questions, asset_architecture, positioning)
    culture_check = build_culture_checklist(culture)
    priority = build_priority_plan(info, research_gate, compliance, experiment)
    ab_hypotheses=build_ab_hypotheses(positioning,visual,content_matrix)
    sections = {
        '01_information_completeness_assumptions_decisions': info,
        '02_product_truth_value_ladder': value,
        '03_platform_region_audience_culture_insight': culture_insights,
        '04_marketing_core_strategy': {'product_strategy': product_strategy, 'positioning': positioning, 'frameworks': marketing},
        '05_visual_photography_strategy': visual,
        '06_platform_content_matrix': content_matrix,
        '07_race_execution_table': marketing.get('RACE', []),
        '08_culture_adaptation_checklist': culture_check,
        '09_risk_measurement_priority_next_steps': {
            'compliance': compliance,
            'research_pending': research_gate.get('actions', []),
            'experiment': experiment,
            'ab_test_hypotheses': ab_hypotheses,
            'priority_plan': priority,
        },
    }
    return {
        'status': 'STRATEGY_AUTHORITY_COMPILED',
        'positive_design_first': True,
        'governance_role': 'BACKGROUND_GUARDRAIL',
        'strategy_decision_contract': 'WHAT → WHY → EVIDENCE → CONSUMER → PLATFORM → CULTURE → BUSINESS → EXECUTION → MEASUREMENT',
        'asset_package_preservation': 'REQUIRED',
        'platform_compile_status': platform_compile.get('status'),
        'sections': sections,
    }


def _fmt(v):
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _md_table(headers, rows):
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|']
    for row in rows:
        out.append('| ' + ' | '.join(_fmt(row.get(h, '')).replace('\n', '<br>') for h in headers) + ' |')
    return '\n'.join(out)


def render_master_strategy_cn(strategy: dict[str, Any]) -> str:
    s = strategy['sections']
    out = ['# 跨境电商完整策略总案', '', '> 正向商业策划优先；证据、规则、审核作为后台护栏。每个关键决定说明为什么。', '']
    info = s['01_information_completeness_assumptions_decisions']
    out += [
        '## 1. 信息完整度、待确认清单、假设与决策日志',
        f"- 当前完整度：**{info['completeness_status']}**",
        f"- 必填缺失：{', '.join(info['required_missing']) or '无'}",
        f"- 待确认：{json.dumps(info['pending_confirmations'], ensure_ascii=False)}",
        f"- 假设：{json.dumps(info['assumptions'], ensure_ascii=False)}",
        '### 决策日志',
    ]
    for d in info['decision_log']:
        out += [
            f"- **做什么**：{d['what']}",
            f"  - **为什么**：{d['why']}",
            f"  - 依据：{_fmt(d['evidence'])}",
            f"  - 商业逻辑：{d['business_logic']}",
            f"  - 执行：{d['execution']}",
            f"  - 衡量：{d['measurement']}",
        ]
    v = s['02_product_truth_value_ladder']
    out += ['', '## 2. 产品真实事实审计与卖点分级表', '### 产品事实']
    out.append(_md_table(['fact', 'value', 'evidence_level', 'selling_point', 'perceived_benefit', 'emotional_value', 'publication_status', 'why'], v['product_facts']))
    out += ['', '### Claim / 价值分级', _md_table(['claim', 'type', 'evidence_level', 'publication_status', 'why'], v['claim_value_ladder'])]
    c = s['03_platform_region_audience_culture_insight']
    out += ['', '## 3. 平台 × 区域 × 人群 × 族裔文化洞察', _md_table(['platform', 'region', 'audience', 'race_ethnicity', 'intersectionality', 'cultural_adaptation', 'stereotype_taboo_check', 'why'], c['rows'])]
    m = s['04_marketing_core_strategy']
    pos = m['positioning']
    out += [
        '', '## 4. 营销框架与核心策略',
        '### 定位', pos['positioning_statement'],
        f"- 核心转化主张：**{pos['primary_conversion_proposition']}**",
        f"- 为什么：{pos['why']['why']}",
        '### 信息层级', _md_table(['priority', 'message', 'why'], pos['message_hierarchy']),
        '### 产品 / SKU策略', _md_table(['sku', 'role', 'why', 'price'], m['product_strategy']['sku_roles']),
        '### STP / JTBD / 4P / Funnel', f"```json\n{json.dumps(m['frameworks'], ensure_ascii=False, indent=2)}\n```",
    ]
    vis = s['05_visual_photography_strategy']
    out += [
        '', '## 5. 视觉总策略与拍摄执行清单',
        f"- 风格：{vis['style']}",
        f"- 为什么：{vis['style_why']}",
        f"- HEX/色彩：{_fmt(vis['palette_hex'])}",
        f"- 构图：{_fmt(vis['composition'])}",
        f"- 灯光摄影框架：{_fmt(vis['lighting_framework'])}",
        f"- 焦段/镜头：{_fmt(vis['lens'])}",
        f"- 景别/机位/相机：{_fmt(vis['camera'])}",
        f"- 对焦/景深：{_fmt(vis['focus_dof'])}",
        f"- 场景：{_fmt(vis['scene'])}",
        f"- 道具：{_fmt(vis['props'])}",
        f"- 模特/服化道：{_fmt(vis['casting'])} / {_fmt(vis['wardrobe_hair_makeup'])}",
        f"- 平台尺寸：{_fmt(vis['platform_dimensions'])}",
        '### 镜头表', f"```json\n{json.dumps(vis['shot_list'], ensure_ascii=False, indent=2)}\n```",
        '### 为什么这样拍', vis['why']['why'],
        f"- 消费者逻辑：{vis['why']['consumer_logic']}",
        f"- 平台逻辑：{vis['why']['platform_logic']}",
        f"- 文化逻辑：{vis['why']['culture_logic']}",
        f"- 商业逻辑：{vis['why']['business_logic']}",
    ]
    out += ['', '## 6. 分平台内容矩阵表', _md_table(['platform', 'site', 'audience', 'topic', 'hook', 'script_structure', 'visual_form', 'cta', 'metric', 'race_stage', 'culture_adaptation', 'taboo_stereotype_check', 'why'], s['06_platform_content_matrix'])]
    out += ['', '## 7. RACE传播框架执行表', _md_table(['stage', 'objective', 'key_actions', 'output', 'platform', 'culture_check', 'kpi', 'why'], s['07_race_execution_table'])]
    out += ['', '## 8. 族裔文化适配检查表', _md_table(['adaptation_point', 'inclusive_representation', 'stereotype_taboo_risk', 'evidence_status', 'result', 'modification', 'why'], s['08_culture_adaptation_checklist'])]
    last = s['09_risk_measurement_priority_next_steps']
    pr = last['priority_plan']
    out += [
        '', '## 9. 合规、文化敏感与风险清单；A/B；P0/P1/P2与下一步',
        f"- 合规状态：{last['compliance'].get('status')}",
        f"- Research Pending：{json.dumps(last['research_pending'], ensure_ascii=False)}",
        f"- 已有实验结果：{json.dumps(last['experiment'], ensure_ascii=False)}",
        '### A/B测试建议', *['- '+x['id']+'｜'+x['hypothesis']+'｜为什么：'+x['why'] for x in last.get('ab_test_hypotheses',[])],
        '### P0', *['- ' + x['action'] + ' — 为什么：' + x['why'] for x in pr['P0']],
        '### P1', *['- ' + x['action'] + ' — 为什么：' + x['why'] for x in pr['P1']],
        '### P2', *['- ' + x['action'] + ' — 为什么：' + x['why'] for x in pr['P2']],
        f"### 下一步需补充信息\n{json.dumps(pr['next_information_needed'], ensure_ascii=False)}",
        '', '## 资产包连续性',
        '完整策略只作为资产架构上游 Authority；逐资产独立生产包、Provider Job、Review Item 与 Local Revision 链继续保留，不被本总案替代。',
    ]
    return '\n'.join(out) + '\n'


def materialize_strategy(root: Path, strategy: dict[str, Any]):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / 'strategy_authority.json').write_text(json.dumps(strategy, ensure_ascii=False, indent=2), encoding='utf-8')
    (root / 'MASTER_STRATEGY_CN.md').write_text(render_master_strategy_cn(strategy), encoding='utf-8')
    (root / 'STRATEGY_DECISION_INDEX.json').write_text(json.dumps(strategy.get('decision_index', []), ensure_ascii=False, indent=2), encoding='utf-8')
    (root / 'EXECUTIVE_SUMMARY.json').write_text(json.dumps(strategy.get('executive_summary', {}), ensure_ascii=False, indent=2), encoding='utf-8')
    for key, val in strategy['sections'].items():
        (root / f'{key}.json').write_text(json.dumps(val, ensure_ascii=False, indent=2), encoding='utf-8')
    from .delivery_contract import validate_strategy_delivery
    from .delivery_html import build_delivery_html
    delivery_contract = validate_strategy_delivery(strategy)
    (root / 'DELIVERY_CONTRACT.json').write_text(json.dumps(delivery_contract, ensure_ascii=False, indent=2), encoding='utf-8')
    html_path = build_delivery_html(root, root / 'MASTER_STRATEGY_CN.html', title='CBCC 跨境电商策略与资产总览')
    return {'json': str(root / 'strategy_authority.json'), 'markdown': str(root / 'MASTER_STRATEGY_CN.md'), 'html': str(html_path), 'delivery_contract': str(root / 'DELIVERY_CONTRACT.json'), 'decision_index': str(root / 'STRATEGY_DECISION_INDEX.json'), 'executive_summary': str(root / 'EXECUTIVE_SUMMARY.json'), 'section_count': len(strategy['sections'])}


def _deep_merge(base, override):
    if isinstance(base,dict) and isinstance(override,dict):
        out=dict(base)
        for k,v in override.items(): out[k]=_deep_merge(out.get(k),v) if k in out else v
        return out
    return override if override is not None else base


def build_strategy_host_authoring_request(strategy:dict[str,Any], reasoning_context:dict[str,Any]|None=None, supplied_annotations:dict[str,Any]|None=None)->dict[str,Any]:
    """Materialize the already-supported strategy_annotations handoff as an explicit Host task.

    The deterministic runtime is authoritative for facts/calculations.  The Host/model is asked to
    deepen commercial interpretation, benefit translation and WHY without recomputing or replacing
    those authorities.
    """
    sections=strategy.get('sections') or {}; core=sections.get('04_marketing_core_strategy') or {}
    value=sections.get('02_product_truth_value_ladder') or {}; listing=core.get('listing_strategy') or {}
    generic_benefit=sum(1 for x in value.get('claim_value_ladder',[]) if str(x.get('perceived_benefit') or '').startswith('用用户语言解释'))
    hierarchy=(core.get('positioning') or {}).get('message_hierarchy') or []
    priorities={str(x.get('priority')) for x in hierarchy}
    coverage=(listing.get('decision_question_coverage') or {}).get('summary') or {}
    context=reasoning_context or {}
    selected_prompt_ids=[x.get('id') for x in context.get('selected_prompts',[]) if x.get('id')]
    return {
      'status':'HOST_STRATEGY_AUTHORING_RESPONSE_SUPPLIED' if supplied_annotations else 'HOST_STRATEGY_AUTHORING_AVAILABLE_NOT_SUPPLIED',
      'required_output_key':'strategy_annotations',
      'purpose':'在不改写 Product Truth、计算结果、来源质量、精确平台规则或 Final Copy release state 的前提下，把确定性 Strategy Authority 深化为专业商业推理。默认用中文输出，除非用户明确要求其他交付语言。',
      'quality_flags':{
        'generic_claim_benefit_rows':generic_benefit,
        'generic_message_layers_present':sorted(priorities),
        'decision_question_coverage':coverage,
        'economics_status':(core.get('product_strategy') or {}).get('economics_status'),
        'market_status':((sections.get('03_platform_region_audience_culture_insight') or {}).get('market') or {}).get('status'),
        'host_annotations_supplied':bool(supplied_annotations),
      },
      'tasks':[
        {'output_route':'value_ladder','job':'Translate supported facts/claims into Fact → Advantage/RTB → Perceived Benefit → Emotional Value only where justified. Add interpretation; do not replace fact/claim rows.'},
        {'output_route':'positioning','job':'Author a product-specific target/tension/frame/Primary Conversion Proposition/differentiation/RTB/risk-reducer synthesis from current Product Truth + scoped evidence.'},
        {'output_route':'message_hierarchy','job':'Make P0/P1/P2/P3 semantically distinct. Do not repeat the same claim as both proposition and proof.'},
        {'output_route':'listing_strategy','job':'Explain how each live consumer decision question should be resolved across title/attributes/highlights/FAQ/usage/package/PDP, using decision_question_coverage as authority.'},
        {'output_route':'visual_strategy','job':'Deepen product/category-specific visual and photography WHY while preserving supplied/derived CMF and prelight boundaries.'},
        {'output_route':'content_matrix','job':'Deepen platform/surface-native hooks and content logic without changing Product Truth or forcing a fixed asset count.'},
      ],
      'selected_professional_prompt_ids':selected_prompt_ids,
      'authority_bindings':context.get('authority_bindings') or {},
      'response_contract':{
        'delivery_language':'zh-CN by default; user explicit request overrides.',
        'foreign_language_rule':'Target-market visible copy may use the target locale, but human-facing strategy/explanation remains in the delivery language. Non-delivery-locale copy must carry a delivery-language companion explanation.',
        'decision_contract':'WHAT → WHY → EVIDENCE → CONSUMER LOGIC → PLATFORM LOGIC → CULTURE LOGIC → BUSINESS LOGIC → EXECUTION → MEASUREMENT',
        'allowed':'Interpretation, value translation, positioning, message priority, field/surface execution rationale, culture/visual/content reasoning, test hypotheses and priority explanation.',
        'protected':'Product Truth facts; claim ledger/evidence status; deterministic Market/Economics/Ads/Experiment outputs; source quality; exact platform policy; claim/source trace; Final Copy release state; existing asset package hashes.',
        'boundary':'When evidence is insufficient, write a hypothesis / pending decision rather than a stronger fact or claim.'
      },
      'supplied_annotation_keys':sorted((supplied_annotations or {}).keys()),
    }


def apply_strategy_annotations(strategy:dict[str,Any], annotations:dict[str,Any]|None)->dict[str,Any]:
    """Merge professional model/human interpretation into exact strategy sub-domains.

    Deterministic facts/calculations remain upstream authorities. Annotations deepen interpretation,
    WHY and execution, but do not silently rewrite Product Truth or calculator results.
    """
    if not annotations:
        return strategy
    # Strategy annotations deepen reasoning; they are not allowed to become a second truth/calculation source.
    protected={
      ('information','domain_matrix'),('information','required_missing'),
      ('value_ladder','product_facts'),('value_ladder','claim_value_ladder'),('value_ladder','unclaimable_without_more_evidence'),
      ('market_insights','capacity'),('market_insights','data_quality'),('market_insights','normalization'),('market_insights','concentration'),
      ('market_insights','top_price_bands'),('market_insights','price_valley_signals'),('market_insights','configuration_signals'),
      ('market_insights','keyword_demand'),('market_insights','customer_voice'),('market_insights','research_quality'),('market_insights','research_ingestion'),('market_insights','source_adapter_refresh'),
      ('product_strategy','economics_status'),('product_strategy','economics_snapshot'),('product_strategy','economics_scenarios'),('product_strategy','price_ladder'),
      ('product_strategy','portfolio_behavior_validation'),('product_strategy','interaction_behavior_validation'),('product_strategy','switch_matrix'),('product_strategy','cohort_comparability'),('product_strategy','holdout_marginal_contribution'),('product_strategy','shared_growth_budget'),
      ('listing_strategy','current_fields'),('listing_strategy','claim_source_trace'),('listing_strategy','localized_copy_audit'),('listing_strategy','terminology_memory_audit'),('listing_strategy','final_copy_workflow'),
      ('risk_measurement_priority','compliance'),('risk_measurement_priority','research_pending'),
      ('marketing','product_strategy','economics_status'),('marketing','product_strategy','economics_snapshot'),('marketing','product_strategy','economics_scenarios'),('marketing','product_strategy','shared_growth_budget'),
      ('marketing','listing_strategy','claim_source_trace'),('marketing','listing_strategy','final_copy_workflow'),
    }
    clean=json.loads(json.dumps(annotations,ensure_ascii=False))
    rejected=[]
    for path in sorted(protected):
        cur=clean
        for key in path[:-1]:
            if not isinstance(cur,dict) or key not in cur: cur=None; break
            cur=cur[key]
        if isinstance(cur,dict) and path[-1] in cur:
            rejected.append('.'.join(path)); cur.pop(path[-1],None)
    s=dict(strategy); sections=dict(s.get('sections',{}))
    routes={
      'executive_summary':('__TOP_EXECUTIVE_SUMMARY__',),
      'information':('01_information_completeness_assumptions_decisions',),
      'value_ladder':('02_product_truth_value_ladder',),
      'market_insights':('03_platform_region_audience_culture_insight','market'),
      'culture_insights':('03_platform_region_audience_culture_insight','culture'),
      'marketing':('04_marketing_core_strategy',),
      'product_strategy':('04_marketing_core_strategy','product_strategy'),
      'positioning':('04_marketing_core_strategy','positioning'),
      'listing_strategy':('04_marketing_core_strategy','listing_strategy'),
      'frameworks':('04_marketing_core_strategy','frameworks'),
      'message_hierarchy':('04_marketing_core_strategy','positioning','message_hierarchy'),
      'visual_strategy':('05_visual_photography_strategy',),
      'asset_portfolio':('05_visual_photography_strategy','asset_portfolio'),
      'content_matrix':('06_platform_content_matrix',),
      'race_execution':('07_race_execution_table',),
      'culture_checklist':('08_culture_adaptation_checklist',),
      'risk_measurement_priority':('09_risk_measurement_priority_next_steps',),
      'performance_learning':('09_risk_measurement_priority_next_steps','performance_learning'),
      'ab_hypotheses':('09_risk_measurement_priority_next_steps','ab_test_hypotheses'),
      'priority_plan':('09_risk_measurement_priority_next_steps','priority_plan'),
    }
    def merge_at(root, path, val):
        if len(path)==1:
            root[path[0]]=_deep_merge(root.get(path[0]),val) if path[0] in root else val
            return
        cur=root
        for key in path[:-1]:
            if not isinstance(cur.get(key),dict): cur[key]={}
            cur=cur[key]
        leaf=path[-1]
        cur[leaf]=_deep_merge(cur.get(leaf),val) if leaf in cur else val
    for key,val in clean.items():
        path=routes.get(key)
        if path == ('__TOP_EXECUTIVE_SUMMARY__',):
            s['executive_summary']=_deep_merge(s.get('executive_summary',{}),val)
        elif path:
            merge_at(sections,path,val)
        elif key in sections:
            sections[key]=_deep_merge(sections.get(key),val)
    s['sections']=sections
    s['strategy_annotation_application']={'status':'APPLIED_WITH_PROTECTED_BOUNDARY','supplied_keys':sorted(annotations.keys()),'applied_keys':sorted(clean.keys()),'rejected_protected_paths':rejected,'boundary':'Host/model annotations deepen interpretation/WHY/execution but cannot replace deterministic facts, calculations, exact source/policy authority or Final Copy release state.'}
    # Keep the executive layer synchronized with professional domain annotations.
    ex=s.get('executive_summary') or {}
    conclusions=ex.get('strategic_conclusions') or []
    pos=(sections.get('04_marketing_core_strategy') or {}).get('positioning') or {}
    visual=sections.get('05_visual_photography_strategy') or {}
    portfolio=visual.get('asset_portfolio') or {}
    for row in conclusions:
        if row.get('priority')==1 and pos.get('primary_conversion_proposition'):
            row['conclusion']=f"以“{pos.get('primary_conversion_proposition')}”作为统一第一购买理由。"
        if row.get('priority')==4 and visual.get('style'):
            row['conclusion']=f"视觉系统采用“{visual.get('style')}”。"
            if visual.get('style_why'): row['why']=visual.get('style_why')
        if row.get('priority')==3 and portfolio.get('asset_count') is not None:
            row['conclusion']=f"动态资产组合当前为 {portfolio.get('asset_count')} 项，数量来自购买问题而非固定图位。"
            if portfolio.get('why'): row['why']=portfolio.get('why')
    ex['strategic_conclusions']=conclusions
    ex['asset_count']=portfolio.get('asset_count',ex.get('asset_count',0))
    s['executive_summary']=ex
    # Rebuild the cross-domain decision index after professional interpretation is merged.
    try:
        from .strategy_depth import build_decision_index_depth
        s['decision_index']=build_decision_index_depth(sections)
    except Exception:
        pass
    s['annotation_status']='PROFESSIONAL_STRATEGIC_INTERPRETATION_MERGED'
    s['annotation_routes_applied']=[k for k in annotations if k in routes or k in sections]
    return s


# v0.5.4 Research + Behavior + Final Copy Depth authority: preserve public function names while deepening
# the generic scaffold with professional-team strategy synthesis.
from .strategy_depth import build_master_strategy_depth as _build_master_strategy_depth, render_master_strategy_cn_depth as _render_master_strategy_cn_depth


def build_master_strategy(request: dict[str, Any], *, truth: dict[str, Any], research_gate: dict[str, Any], market: dict[str, Any] | None, economics: dict[str, Any] | None, culture: dict[str, Any], platform_compile: dict[str, Any], creative: dict[str, Any], photography_validation: dict[str, Any] | None, asset_architecture: dict[str, Any], compliance: dict[str, Any], experiment: dict[str, Any] | None = None, listing: dict[str, Any] | None = None, ads: dict[str, Any] | None = None, feedback: dict[str, Any] | None = None, authoring_context: dict[str, Any] | None = None) -> dict[str, Any]:
    return _build_master_strategy_depth(
        request, truth=truth, research_gate=research_gate, market=market, economics=economics,
        culture=culture, platform_compile=platform_compile, creative=creative,
        photography_validation=photography_validation, asset_architecture=asset_architecture,
        compliance=compliance, experiment=experiment, listing=listing, ads=ads, feedback=feedback, authoring_context=authoring_context,
    )


def render_master_strategy_cn(strategy: dict[str, Any]) -> str:
    return _render_master_strategy_cn_depth(strategy)
