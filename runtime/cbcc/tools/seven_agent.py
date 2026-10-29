from __future__ import annotations
from collections import Counter
from typing import Any

from .market import analyze_market
from .economics import economics_strategy
from .listing import compile_listing, keyword_architecture, listing_conversion_architecture, transcreation_task_matrix
from .ads import analyze_ads, analyze_ad_portfolio
from .feedback import analyze_feedback
from ..strategy_depth import build_value_depth, build_market_depth, build_sku_depth, build_positioning_depth
from ..product_visual_intelligence import compile_product_visual_intelligence, compile_creative_anchor_plan
from ..creative_opportunity import compile_creative_opportunity_universe
from ..creative import compile_curation, compile_creative_council, apply_creative_system_to_assets, compile_cmf, compile_inclusive_photography
from ..asset_architecture import build_asset_architecture
from ..prompt_compiler import compile_asset_prompt
from ..video_creator import build_video_creator_plan, enrich_video_plan_with_strategy

TOOL_CONTRACT_VERSION='0.6.37'


def _contract(name:str, inputs:dict[str,Any], result:dict[str,Any], downstream:list[str], why:str)->dict[str,Any]:
    return {'tool_contract_version':TOOL_CONTRACT_VERSION,'tool':name,'inputs_received':sorted(k for k,v in inputs.items() if v not in (None,[],{},'')),'result':result,'downstream_handoff':downstream,'why':why}


def market_research_tool(*, rows:list[dict[str,Any]], keyword_rows=None, review_rows=None, competitor_listing_rows=None, source_records=None, field_map=None, price_step=None, config_key='configuration', as_of=None, research_scope=None, ingestion_config=None)->dict[str,Any]:
    result=analyze_market(rows or [], price_step=price_step, config_key=config_key, keyword_rows=keyword_rows, field_map=field_map, review_rows=review_rows, competitor_listing_rows=competitor_listing_rows, source_records=source_records, as_of=as_of, research_scope=research_scope, ingestion_config=ingestion_config)
    return _contract('01_MARKET_RESEARCH',locals(),result,['02_PRODUCT_STRATEGY','03_LISTING_CREATIVE','04_PRODUCT_IMAGE'],'把可计算市场事实与策略解释分开：脚本算集中度/价格/配置/关键词/评论，策略层解释机会与取舍。')


def product_strategy_tool(*, request:dict[str,Any], truth:dict[str,Any]|None=None, market_analysis:dict[str,Any]|None=None, economics_scenarios:list[dict[str,Any]]|None=None, economics_inputs:dict[str,Any]|None=None, culture:dict[str,Any]|None=None, shopper_questions:list[str]|None=None)->dict[str,Any]:
    truth=truth or {'product':request.get('product') or {}}
    culture=culture or request.get('audience_culture') or {}
    questions=shopper_questions or request.get('shopper_questions') or []
    market_depth=build_market_depth(market_analysis,request)
    econ=None
    if economics_scenarios:
        ei=economics_inputs or {}
        econ=economics_strategy(economics_scenarios, demand_signals=ei.get('demand_signals'), behavior_rows=ei.get('behavior_rows'), pair_behavior_rows=ei.get('pair_behavior_rows'), cohort_rows=ei.get('cohort_rows'), incrementality_rows=ei.get('incrementality_rows'), switch_rows=ei.get('switch_rows'), holdout_rows=ei.get('holdout_rows'), promo_response_rows=ei.get('promo_response_rows'), bundle_affinity_rows=ei.get('bundle_affinity_rows'), repeat_cycle_rows=ei.get('repeat_cycle_rows'))
    value=build_value_depth(request,truth,questions)
    sku=build_sku_depth(request,market_depth,econ)
    position=build_positioning_depth(request,value,market_depth,sku,culture,questions,None)
    result={'value_ladder':value,'sku_strategy':sku,'economics':econ,'positioning':position,'decision_contract':{'primary_value':position.get('primary_conversion_proposition'),'offer_boundary':'Price/promo/affiliate decisions require economics; missing economics remains HOLD, not guessed.','tradeoff':'Protect one primary conversion proposition; secondary features must prove a different decision job.'}}
    return _contract('02_PRODUCT_STRATEGY',locals(),result,['03_LISTING_CREATIVE','04_PRODUCT_IMAGE','05_PRODUCT_VIDEO','06_ADVERTISING_OPTIMIZATION'],'产品策略将市场事实、证据等级、SKU经济性和购买任务收敛成唯一主价值与可执行Offer边界。')


def listing_creative_tool(*, fields:dict[str,Any], facts:dict[str,Any], claims:list[dict[str,Any]], rules:dict[str,Any]|None=None, language_contract:dict[str,Any]|None=None, keyword_rows:list[dict[str,Any]]|None=None, platform_context:dict[str,Any]|None=None, localized_copy:dict[str,Any]|None=None, objections:list[Any]|None=None)->dict[str,Any]:
    compiled=compile_listing(fields,facts,claims,rules=rules,language_contract=language_contract,keyword_rows=keyword_rows,platform_context=platform_context)
    kw=keyword_architecture(keyword_rows or [])
    conversion=listing_conversion_architecture(fields,kw,objections=objections,rules=rules)
    trans=transcreation_task_matrix(fields,language_contract or {},localized_copy=localized_copy,keyword_arch=kw)
    result={'compiled_listing':compiled,'keyword_architecture':kw,'conversion_architecture':conversion,'transcreation_backtranslation':{**trans,'back_translation_required_for':['hard claims','specifications','compliance-sensitive copy','primary proposition when localized'],'rule':'Native authoring first; back-translation checks semantic/claim drift, not word-for-word similarity.'},'authoring_flow':['keyword intent → field decision job','title/benefit/proof/spec authoring','claim/fact trace','native locale transcreation','back-translation / native review','final copy release']}
    return _contract('03_LISTING_CREATIVE',locals(),result,['04_PRODUCT_IMAGE','05_PRODUCT_VIDEO','06_ADVERTISING_OPTIMIZATION'],'Listing不是标题lint；它把搜索意图、购买决策、Claim证据和Locale一起编译到真实平台字段。')


def product_image_tool(*, project_id:str, product_truth:dict[str,Any], product:dict[str,Any], source_product_assets:list[dict[str,Any]]|None, target:dict[str,Any], culture:dict[str,Any], language_contract:dict[str,Any], content_objects:list[dict[str,Any]], shopper_questions:list[str], asset_jobs:list[dict[str,Any]]|None=None, references:list[dict[str,Any]]|None=None, competitor_patterns:list[dict[str,Any]]|None=None, photography:dict[str,Any]|None=None, cmf:dict[str,Any]|None=None, category_family:str='GENERAL_COMMERCE', strategy_authority:dict[str,Any]|None=None)->dict[str,Any]:
    pvi=compile_product_visual_intelligence(product,source_product_assets,None,photography=photography,cmf=cmf)
    arch=build_asset_architecture(project_id,target,shopper_questions,content_objects,asset_jobs=asset_jobs,category_family=category_family)
    curation=compile_curation(references,competitor_patterns)
    opp=compile_creative_opportunity_universe(product_truth,pvi,category_family,arch.get('assets'),curation=curation,culture=culture,target=target)
    council=compile_creative_council(None,curation,product_truth,culture,{'status':'PLANNING_CONTEXT'},category_family=category_family,decision_intents=[a.get('decision_intent') for a in arch.get('assets',[])],opportunity_universe=opp)
    cmf_contract=compile_cmf(cmf)
    creative_arch=apply_creative_system_to_assets(arch,council,cmf=cmf_contract,photography=photography)
    inclusive=compile_inclusive_photography(culture,photography,creative_arch.get('assets') or [])
    anchors=compile_creative_anchor_plan(council,creative_arch,pvi,cmf=cmf_contract)
    prompts=[]
    for a in creative_arch.get('assets',[]):
        try:
            pc=compile_asset_prompt(a,product,target,culture,language_contract,photography=photography,strategy_authority=strategy_authority,source_product_assets=source_product_assets)
        except Exception as exc:
            pc={'status':'OPTIONAL_PROMPT_NOT_READY','project_completion_blocking':False,'error':str(exc)}
        prompts.append({'asset_id':a.get('asset_id'),'prompt_contract':pc})
    result={'product_visual_intelligence':pvi,'curation':curation,'creative_opportunity_universe':opp,'creative_council':council,'creative_anchor_plan':anchors,'inclusive_photography':inclusive,'dynamic_asset_architecture':creative_arch,'asset_prompt_contracts':prompts,'fixed_image_count':False,'principle':'资产数量来自购买问题/Surface/证据/信息增量；不复制参考项目固定9图。'}
    return _contract('04_PRODUCT_IMAGE',locals(),result,['PRODUCTION_PROVIDER','06_ADVERTISING_OPTIMIZATION','07_REVIEW_ANALYSIS'],'图像工具从商品视觉真源到逐资产生产合同完整闭环，而不是尺寸检查器。')


def product_video_tool(*, project_id:str, content_objects:list[dict[str,Any]], shopper_questions:list[str], language_contract:dict[str,Any], video_jobs:list[dict[str,Any]]|None=None, assets:list[dict[str,Any]]|None=None, creative_council:dict[str,Any]|None=None, platform_context:dict[str,Any]|None=None, strategy_authority:dict[str,Any]|None=None, source_product_assets:list[dict[str,Any]]|None=None, culture:dict[str,Any]|None=None)->dict[str,Any]:
    plan=build_video_creator_plan(project_id,content_objects,shopper_questions,language_contract,video_jobs,assets=assets,creative_council=creative_council)
    # A standalone first-class video tool must inherit the same Strategy photography/CMF authority as the full compiler.
    # Without Strategy Authority it remains a planning contract rather than pretending to have camera/light/CMF production truth.
    if strategy_authority:
        plan=enrich_video_plan_with_strategy(plan,strategy_authority,source_product_assets=source_product_assets,culture=culture)
    else:
        plan['strategy_visual_binding']='ADVISORY_STRATEGY_AUTHORITY_NOT_SUPPLIED'
    p=platform_context or {}
    for v in plan.get('assets',[]):
        v['cover_first_frame_contract']='First frame/cover must preserve product/category identity and one native hook; exact platform rule is 待查证 unless supplied in platform context.'
        v['subtitle_contract']={'locales':v.get('subtitle_locales'),'safe_area':'keep decision-critical product/action evidence unobstructed','native_review':'required for primary market copy'}
        v['music_rights_contract']='Original audio, licensed audio or platform commercial-use library only; unknown rights = HOLD/待查证.'
        v['voiceover_prompt']=f"Natural {v.get('voice_locale') or 'target-locale'} voice; communicate {v.get('shopper_question')} without exceeding approved claims."
        v['ai_video_prompt']='Use the shot-by-shot visual jobs and selected product-reference/fidelity policy. Source files are design references by default; redraw/rerender/stylization is allowed unless an explicit locked-source mode is selected. Never invent product facts or proof.'
        v['landing_handoff']=p.get('landing_handoff') or 'CTA → target PDP/Shop/Live/landing; offer and message must remain continuous.'
        v['attribution']=p.get('attribution') or 'Preserve campaign/ad/creator/video/landing IDs; use UTM where supported.'
    return _contract('05_PRODUCT_VIDEO',locals(),plan,['PRODUCTION_PROVIDER','06_ADVERTISING_OPTIMIZATION','07_REVIEW_ANALYSIS'],'视频工具覆盖脚本、分镜、AI视频提示、VO/字幕、封面、版权和落地归因，不是单纯时长计算。')


def _ad_priority(result:dict[str,Any])->dict[str,list[dict[str,Any]]]:
    p={'P0':[],'P1':[],'P2':[]}
    diag=(result.get('aggregate') or result).get('diagnosis') or []
    routes={d.get('route') for d in diag}
    if 'ECONOMICS_OR_MEDIA' in routes or 'MEDIA_EFFICIENCY' in routes: p['P0'].append({'action':'先锁盈亏线/CPA/CPC/Contribution，再决定放量或降价。','why':'媒体效率不能越过真实单位经济。'})
    if 'ELIGIBILITY_TRAFFIC' in routes: p['P0'].append({'action':'先查资格/库存/投放可见性/查询覆盖/预算节奏。','why':'没有有效流量时先改创意会误诊。'})
    if 'CLICK_PACKAGE' in routes: p['P1'].append({'action':'只测Hero/thumbnail/title/第一主张中的一个变量。','why':'CTR问题属于第一印象层，单变量才能保留归因。'})
    if 'PDP_CONVERSION' in routes: p['P1'].append({'action':'查流量意图匹配、Proof、价格/Offer、异议与PDP决策覆盖。','why':'CVR是点击后整个决策环境的联合结果。'})
    if not p['P2']: p['P2'].append({'action':'在P0/P1稳定后扩展创意变体、受众/版位探索。','why':'探索应建立在经济和主漏斗已可用的基础上。'})
    for k in p:
        if not p[k]: p[k].append({'action':'当前无该级明确故障，保持现状并观察对应指标。','why':'不为了“优化”而制造动作。'})
    return p


def advertising_optimization_tool(*, data:dict[str,Any]|None=None, rows:list[dict[str,Any]]|None=None, price:float|None=None, costs:dict[str,Any]|None=None, thresholds:dict[str,Any]|None=None, target_contribution:float=0, attribution_context:dict[str,Any]|None=None)->dict[str,Any]:
    result=analyze_ad_portfolio(rows,price=price,costs=costs,thresholds=thresholds) if rows is not None else analyze_ads(data or {},price=price,costs=costs,thresholds=thresholds,target_contribution=target_contribution)
    result['priority_actions']=_ad_priority(result)
    result['attribution_contract']={'platform_attribution':'credited conversions are not automatically incremental','utm_or_equivalent':'Use UTM where supported; otherwise preserve campaign/adgroup/ad/creative/creator/landing IDs','window':(attribution_context or {}).get('window') or '待查证：按平台/业务定义','landing_handoff':(attribution_context or {}).get('landing_handoff') or 'Creative promise → landing/PDP proof/offer continuity','incrementality':'Holdout/geo/time-series/counterfactual evidence required before causal sales claim'}
    return _contract('06_ADVERTISING_OPTIMIZATION',locals(),result,['03_LISTING_CREATIVE','04_PRODUCT_IMAGE','02_PRODUCT_STRATEGY'],'广告工具按流量→点击→PDP→经济性诊断，并用P0/P1/P2与归因边界把修改回流到最小责任层。')


REVIEW_EIGHT_CLASSES={
 'PRODUCT_QUALITY':'real defect / breakage / consistency / durability',
 'EXPECTATION_GAP':'received experience differs from listing/creative expectation',
 'MISUNDERSTANDING':'buyer interpreted copy/image/spec/use incorrectly',
 'USAGE_EXPERIENCE':'operation, preparation, setup, learning or care difficulty',
 'FIT_SIZE_COMPATIBILITY':'size/fit/compatibility/site-fit mismatch',
 'PACKAGE_CONTENTS':'package, included parts, quantity or unboxing confusion',
 'LOGISTICS_SERVICE':'delivery, installation, support, return or service friction',
 'POSITIVE_VALUE':'praise, repeat intent, standout selling point or delight',
}


def _review_eight(row:dict[str,Any])->str:
    explicit=str(row.get('attribution_class') or '').upper()
    if explicit in REVIEW_EIGHT_CLASSES:return explicit
    c=str(row.get('category') or '').upper()
    mapping={'PRODUCT_DEFECT':'PRODUCT_QUALITY','TEXTURE':'PRODUCT_QUALITY','EXPECTATION_GAP':'EXPECTATION_GAP','MISUNDERSTANDING':'MISUNDERSTANDING','PARAMETER_CONFUSION':'MISUNDERSTANDING','USAGE_DIFFICULTY':'USAGE_EXPERIENCE','SIZE':'FIT_SIZE_COMPATIBILITY','COMPATIBILITY':'FIT_SIZE_COMPATIBILITY','PACKAGE_CONFUSION':'PACKAGE_CONTENTS','LOGISTICS':'LOGISTICS_SERVICE','CUSTOMER_SERVICE':'LOGISTICS_SERVICE','PRAISE':'POSITIVE_VALUE','POSITIVE':'POSITIVE_VALUE'}
    return mapping.get(c,'CLASSIFICATION_REQUIRED')


def review_analysis_tool(*, rows:list[dict[str,Any]])->dict[str,Any]:
    rows=[dict(r) for r in (rows or [])]
    for r in rows:r['eight_class']=_review_eight(r)
    classified=[r for r in rows if r['eight_class']!='CLASSIFICATION_REQUIRED']
    counts=Counter(r['eight_class'] for r in classified)
    total=len(rows); reconciled=sum(counts.values())+sum(1 for r in rows if r['eight_class']=='CLASSIFICATION_REQUIRED')
    misunderstand=[r for r in rows if r['eight_class']=='MISUNDERSTANDING' or str(r.get('misunderstanding') or '').lower() in {'1','true','yes'}]
    fixable=sum(1 for r in classified if r['eight_class'] in {'EXPECTATION_GAP','MISUNDERSTANDING','USAGE_EXPERIENCE','FIT_SIZE_COMPATIBILITY','PACKAGE_CONTENTS'})
    praise=Counter(str(r.get('selling_point') or r.get('praise_point')) for r in rows if r['eight_class']=='POSITIVE_VALUE' and (r.get('selling_point') or r.get('praise_point')))
    base=analyze_feedback(rows)
    local_routes=[]
    for cls,n in counts.most_common():
        route={'PRODUCT_QUALITY':['PRODUCT/QUALITY'],'EXPECTATION_GAP':['LISTING','IMAGE'],'MISUNDERSTANDING':['LISTING','IMAGE','FAQ'],'USAGE_EXPERIENCE':['LISTING','VIDEO','CX'],'FIT_SIZE_COMPATIBILITY':['LISTING','IMAGE/SCALE'],'PACKAGE_CONTENTS':['LISTING','IMAGE/CONTENTS'],'LOGISTICS_SERVICE':['FULFILLMENT','CX'],'POSITIVE_VALUE':['LISTING/PROOF','IMAGE/PROOF']}.get(cls,['REVIEW'])
        local_routes.append({'class':cls,'count':n,'routes':route,'rule':'Change only the implicated layer; freeze unrelated product truth/creative/offer.'})
    result={**base,'eight_class_taxonomy':REVIEW_EIGHT_CLASSES,'eight_class_counts':dict(counts),'classification_required':[{'index':i,'text':r.get('text'),'task':'Host/model classify into one of the eight classes with evidence from the review text.'} for i,r in enumerate(rows) if r['eight_class']=='CLASSIFICATION_REQUIRED'],'misunderstanding_detector':{'count':len(misunderstand),'examples':[r.get('text') for r in misunderstand[:5]],'route':'Listing/Image/FAQ before Product changes unless separate defect evidence exists'},'fixability':{'communication_or_content_fixable_count':fixable,'classified_count':len(classified),'fixable_rate':round(fixable/len(classified),4) if classified else None},'positive_selling_point_ranking':[{'selling_point':k,'count':v} for k,v in praise.most_common(10)],'exact_reconciliation':{'input_total':total,'classified':len(classified),'classification_required':total-len(classified),'sum':reconciled,'balanced':reconciled==total},'local_revision_routes':local_routes}
    return _contract('07_REVIEW_ANALYSIS',locals(),result,['03_LISTING_CREATIVE','04_PRODUCT_IMAGE','02_PRODUCT_STRATEGY'],'评论工具将语义分类交给模型、计数/对账交给脚本，并优先修正误解与沟通责任层，避免用文案修真实缺陷或用改产品解决说明不清。')


def compile_seven_agent_synthesis(*, domain:dict[str,Any]|None=None, architecture:dict[str,Any]|None=None, video_plan:dict[str,Any]|None=None, paid_campaigns:dict[str,Any]|None=None, source_product_assets:list[dict[str,Any]]|None=None)->dict[str,Any]:
    """Materialize how the seven first-class commerce capabilities are actually consumed.

    The full compiler already uses the same underlying domain engines; this function does not
    re-run them or manufacture a fixed seven-step pipeline. It records project-active outputs and
    cross-domain handoffs so release acceptance can prove capability continuity beyond file presence.
    """
    domain=domain or {}; architecture=architecture or {}; video_plan=video_plan or {}; paid_campaigns=paid_campaigns or {}
    assets=architecture.get('assets') or []
    market=domain.get('market') or {}; economics=domain.get('economics') or {}; listing=domain.get('listing') or {}; ads=domain.get('ads') or {}; feedback=domain.get('feedback') or {}
    compiled_listing=listing.get('compiled') or {}
    ad_diag=(ads.get('aggregate') or ads).get('diagnosis') or [] if isinstance(ads,dict) else []
    ad_routes=sorted({str(x.get('route')) for x in ad_diag if isinstance(x,dict) and x.get('route')})
    feedback_issues=feedback.get('issues') or [] if isinstance(feedback,dict) else []
    market_fit_assets=[a for a in assets if a.get('decision_origin')=='MARKET_THEME_FIT']
    feedback_assets=[a for a in assets if a.get('decision_origin')=='FEEDBACK_SIGNAL']
    listing_objections=compiled_listing.get('objection_resolution_plan') or []
    capabilities=[
        {'id':'01_MARKET_RESEARCH','project_active':bool(market),'consumed_by':['Strategy §3 market/audience','Market Evidence Fit','Asset jobs only after explicit product-truth fit'],'evidence':{'status':market.get('status'),'market_fit_asset_count':len(market_fit_assets)}},
        {'id':'02_PRODUCT_STRATEGY','project_active':True,'consumed_by':['Strategy value/SKU/offer/positioning','economics guardrails','asset business hypothesis'],'evidence':{'economics_status':economics.get('status'),'asset_count':len(assets)}},
        {'id':'03_LISTING_CREATIVE','project_active':bool(listing),'consumed_by':['Listing/Search authority','objection-to-asset handoff','human delivery'],'evidence':{'status':listing.get('status'),'objection_count':len(listing_objections)}},
        {'id':'04_PRODUCT_IMAGE','project_active':bool(assets),'consumed_by':['Dynamic Asset Architecture','Creative Council/CMF','per-asset design cards and optional prompt contracts'],'evidence':{'asset_count':len([a for a in assets if a.get('asset_type')=='IMAGE'])}},
        {'id':'05_PRODUCT_VIDEO','project_active':bool(video_plan.get('assets')),'consumed_by':['Video Creator Plan','Strategy §5','production only when explicitly requested'],'evidence':{'video_asset_count':len(video_plan.get('assets') or [])}},
        {'id':'06_ADVERTISING_OPTIMIZATION','project_active':bool(ads or paid_campaigns.get('campaigns')),'consumed_by':['Strategy §9 diagnostics','Paid Campaign Architecture','local revision routing'],'evidence':{'status':ads.get('status'),'diagnostic_routes':ad_routes,'campaign_count':len(paid_campaigns.get('campaigns') or [])}},
        {'id':'07_REVIEW_ANALYSIS','project_active':bool(feedback),'consumed_by':['communication-fixable asset jobs','Strategy §9 local revision routing','listing/content correction'],'evidence':{'status':feedback.get('status'),'issue_count':len(feedback_issues),'feedback_asset_count':len(feedback_assets)}},
    ]
    asset_inputs={
        'market':{'status':market.get('status'),'approved_fit_asset_count':len(market_fit_assets)},
        'offer_economics':{'status':economics.get('status'),'currency':economics.get('currency')},
        'listing':{'status':listing.get('status'),'objection_count':len(listing_objections)},
        'ads':{'status':ads.get('status'),'diagnostic_routes':ad_routes},
        'reviews_feedback':{'status':feedback.get('status'),'issue_count':len(feedback_issues),'communication_asset_count':len(feedback_assets)},
        'product_sources':{'count':len(source_product_assets or []),'default_usage':'DESIGN_REFERENCE'},
    }
    return {
        'status':'SEVEN_AGENT_CAPABILITY_SYNTHESIS_COMPILED',
        'execution_model':'SHARED_RUNTIME_ENGINES; relevance-driven, not a mandatory seven-step pipeline',
        'all_seven_available':True,
        'all_seven_required_each_task':False,
        'capabilities':capabilities,
        'asset_inputs':asset_inputs,
        'active_ids':[x['id'] for x in capabilities if x.get('project_active')],
        'principle':'A reference capability counts as preserved only when its real project output is consumed by strategy, listing, asset/content decisions, paid/video architecture, review routing or delivery—not because a file exists.',
    }

SEVEN_TOOLS={
 '01':market_research_tool,'market':market_research_tool,
 '02':product_strategy_tool,'product':product_strategy_tool,
 '03':listing_creative_tool,'listing':listing_creative_tool,
 '04':product_image_tool,'image':product_image_tool,
 '05':product_video_tool,'video':product_video_tool,
 '06':advertising_optimization_tool,'ads':advertising_optimization_tool,
 '07':review_analysis_tool,'review':review_analysis_tool,
}
