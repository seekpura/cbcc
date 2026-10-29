from __future__ import annotations

from typing import Any, Mapping
from copy import deepcopy


def _dict(v:Any)->dict[str,Any]:
    return dict(v) if isinstance(v,Mapping) else {}


def _list(v:Any)->list[Any]:
    if v is None: return []
    return list(v) if isinstance(v,(list,tuple)) else [v]


def _meaningful(v:Any)->bool:
    return v not in (None,'',[],{})


def _pick(m:Mapping[str,Any]|None,*keys:str,default=None):
    m=m or {}
    for k in keys:
        if _meaningful(m.get(k)): return m.get(k)
    return default


def _strategy_sections(strategy:Mapping[str,Any]|None)->dict[str,Any]:
    return _dict((strategy or {}).get('sections'))


def _commercial_thesis(strategy:Mapping[str,Any]|None)->dict[str,Any]:
    sections=_strategy_sections(strategy)
    core=_dict(sections.get('04_marketing_core_strategy'))
    positioning=_dict(core.get('positioning'))
    product_strategy=_dict(core.get('product_strategy'))
    message=_dict(core.get('message_architecture'))
    return {
        'primary_conversion_proposition':_pick(positioning,'primary_conversion_proposition','statement'),
        'target_user':_pick(positioning,'target_user','target'),
        'secondary_reasons_to_buy':_pick(positioning,'secondary_reasons_to_buy','secondary_reasons',default=[]),
        'trust_drivers':positioning.get('trust_drivers') or [],
        'objection_reducers':positioning.get('objection_reducers') or [],
        'sku_roles':product_strategy.get('sku_roles') or [],
        'message_hierarchy':_pick(positioning,'message_hierarchy',default=message.get('hierarchy') or []),
        'operator_read':'先用核心主张建立“为什么继续看/买”的理由，再用证据、规格、异议消解和 Offer 完成决策。不要让次级卖点在首屏平分注意力。',
    }


def _listing_release(domain:Mapping[str,Any]|None)->dict[str,Any]:
    listing=_dict((domain or {}).get('listing'))
    compiled=_dict(listing.get('compiled'))
    workflow=_dict(compiled.get('final_copy_workflow'))
    packages=[]
    for pkg in workflow.get('packages') or []:
        rows=[]
        for row in pkg.get('fields') or []:
            rows.append({
                'field':row.get('field'),
                'locale':row.get('locale'),
                'final_or_current_copy':row.get('authored_copy'),
                'delivery_translation_zh':row.get('delivery_translation'),
                'release_status':row.get('release_status'),
                'hard_issues':row.get('hard_issues') or [],
                'decision_job':row.get('platform_job'),
                'source_version_id':row.get('current_version_id'),
                'operator_action':('直接发布候选；完成平台最终上传检查。' if row.get('release_status')=='APPROVED_FINAL' else '按已生成 author/review task 完成该字段，不要用占位文案上线。'),
            })
        packages.append({'locale':pkg.get('locale'),'status':pkg.get('status'),'fields':rows})
    if not packages:
        fields=_dict(compiled.get('fields') or listing.get('fields'))
        if fields:
            packages=[{'locale':None,'status':'CURRENT_FIELDS_NEED_RELEASE_WORKFLOW','fields':[{'field':k,'final_or_current_copy':v,'release_status':'CURRENT_INPUT','operator_action':'进入本地化/Claim/平台字段审查后再发布。'} for k,v in fields.items() if not str(k).startswith('_')]}]
    return {
        'status':workflow.get('status') or listing.get('status') or 'NOT_SUPPLIED',
        'release_counts':workflow.get('release_counts') or {},
        'packages':packages,
        'operator_rule':'运营拿最终字段，不拿“写作建议”。目标市场文案必须保留；非中文文案同时显示中文释义/用途。',
    }


def _asset_release(asset:Mapping[str,Any],compiled_index:Mapping[str,Any]|None=None)->dict[str,Any]:
    art=_dict(asset.get('asset_art_direction'))
    copy=asset.get('visible_copy') or {}
    presence=_pick(art,'product_presence',default=asset.get('product_presence'))
    idx=_dict(compiled_index)
    activation=_pick(asset,'activation_state','portfolio_state','asset_state',default='CANDIDATE')
    return {
        'asset_id':asset.get('asset_id'),
        'asset_name':asset.get('asset_name'),
        'asset_type':asset.get('asset_type'),
        'surface':asset.get('surface'),
        'activation_state':activation,
        'shopper_question':asset.get('consumer_question'),
        'commercial_job':_pick(asset,'strategic_job','reason_to_exist','belief_target'),
        'creative_hypothesis':_pick(asset,'creative_hypothesis_id','test_hypothesis','business_hypothesis'),
        'visual_carrier':_pick(art,'visual_carrier',default=asset.get('visual_carrier')),
        'product_presence':presence,
        'visible_copy':deepcopy(copy),
        'delivery_copy_rule':'目标市场文字保持原文；人类交付同时显示中文释义/用途。',
        'source_reference_ids':[x.get('asset_id') for x in asset.get('source_product_assets') or [] if isinstance(x,Mapping)],
        'output_spec':{
            'surface':asset.get('surface'),
            'format':asset.get('format'),
            'aspect_ratio':asset.get('aspect_ratio'),
            'dimensions':asset.get('dimensions'),
        },
        'production_route':_pick(asset,'production_mode','capture_mode'),
        'compiled_package_path':idx.get('path'),
        'compiled_provider':idx.get('provider'),
        'release_status':('PRODUCTION_READY' if idx else 'NEEDS_ASSET_COMPILE'),
        'operator_action':('打开逐资产包，直接使用 Model Prompt CN/EN + Visible Copy + reference + production notes 执行；生成后按成图 QA 修复。' if idx else '先执行资产编译，物化独立 Prompt/Copy/Reference/Production 包。'),
    }


def _asset_board(architecture:Mapping[str,Any]|None,asset_compile:Mapping[str,Any]|None)->dict[str,Any]:
    arch=_dict(architecture); ac=_dict(asset_compile)
    idx={str(x.get('asset_id')):x for x in ac.get('index') or [] if isinstance(x,Mapping)}
    rows=[_asset_release(a,idx.get(str(a.get('asset_id')))) for a in arch.get('assets') or []]
    return {
        'status':'ASSET_PRODUCTION_BOARD_READY' if rows else 'NO_ASSETS',
        'asset_count':len(rows),
        'assets':rows,
        'operator_rule':'逐资产是独立生产对象；平台上线槽位≠资产总量。LIVE/TEST/ROTATION/PAID/PDP 等按运营用途管理。',
    }


def _paid_test_queue(paid_campaigns:Mapping[str,Any]|None,domain:Mapping[str,Any]|None)->dict[str,Any]:
    paid=_dict(paid_campaigns); ads=_dict((domain or {}).get('ads'))
    rows=[]
    for c in paid.get('campaigns') or []:
        rows.append({
            'campaign_id':c.get('campaign_id'),
            'objective':c.get('objective'),
            'hypothesis':_pick(c,'hypothesis','test_hypothesis','business_hypothesis'),
            'asset_ids':c.get('asset_ids') or c.get('creative_ids') or [],
            'audience_or_query_scope':_pick(c,'audience','query_scope','targeting'),
            'budget_boundary':_pick(c,'budget_boundary','economics_guardrail'),
            'primary_metric':_pick(c,'primary_metric','success_metric'),
            'decision_rule':c.get('decision_rule'),
            'operator_action':'按假设启动/调整测试；一次只改最小可归因变量组，并遵守单位经济边界。',
        })
    priority=ads.get('priority_actions') or {}
    return {
        'status':'PAID_TEST_QUEUE_READY' if rows or ads else 'NO_PAID_INPUT',
        'campaign_tests':rows,
        'ads_priority_actions':deepcopy(priority),
        'diagnosis':deepcopy(ads.get('diagnosis') or (ads.get('aggregate') or {}).get('diagnosis') or []),
        'operator_rule':'先解决 P0 经济/投放资格问题，再做创意扩量；创意测试必须有商业假设而不是近似换皮。',
    }


def _review_queue(domain:Mapping[str,Any]|None)->dict[str,Any]:
    fb=_dict((domain or {}).get('feedback'))
    actions=fb.get('revision_actions') or []
    rows=[]
    for i,a in enumerate(actions):
        rows.append({
            'revision_id':a.get('revision_id') or f'REV-{i+1:02d}',
            'category':a.get('category'),
            'priority':a.get('priority') or a.get('priority_score'),
            'routes':a.get('routes') or [],
            'exact_revision':a.get('exact_revision') or a.get('recommended_change'),
            'evidence':a.get('evidence') or a.get('evidence_examples') or [],
            'frozen_layers':a.get('frozen_layers') or [],
            'verification_metric':a.get('verification_metric'),
            'operator_action':'只修改责任层；修订后复看同一问题/退货/客服主题和转化护栏。',
        })
    return {
        'status':'REVISION_QUEUE_READY' if rows else (fb.get('status') or 'NO_FEEDBACK_INPUT'),
        'revisions':rows,
        'positive_value':deepcopy(fb.get('positive_selling_point_ranking') or []),
        'operator_rule':'真实缺陷进 Product/Quality；期望/误解优先修 Listing/Image/Video/CX。避免一条差评触发全盘重做。',
    }


def _economics_panel(domain:Mapping[str,Any]|None)->dict[str,Any]:
    dom=domain or {}; pricing=_dict(dom.get('pricing_economics_authority')); econ=_dict(dom.get('economics'))
    source=pricing or econ
    return {
        'status':source.get('status') or 'NOT_SUPPLIED',
        'pricing_decision':deepcopy(source.get('pricing_decision') or {}),
        'scenarios':deepcopy(source.get('scenarios') or econ.get('scenarios') or []),
        'sku_roles':deepcopy(source.get('sku_roles') or []),
        'offer_bundle_discount_boundary':deepcopy(source.get('offer_bundle_discount_boundary') or []),
        'missing_inputs':deepcopy(source.get('missing_inputs') or []),
        'operator_rule':'所有折扣、联盟佣金和投放扩量都先看 Contribution 与 Break-even CPA/CPC/ROAS；缺的真实成本不自动按 0。',
    }


def _release_state(compliance:Mapping[str,Any]|None,asset_compile:Mapping[str,Any]|None,production_run:Mapping[str,Any]|None)->dict[str,Any]:
    comp=_dict(compliance); ac=_dict(asset_compile); pr=_dict(production_run)
    if str(comp.get('status') or '').upper()=='HOLD': state='HOLD_COMPLIANCE'
    elif ac.get('status')=='COMPILED' and pr.get('status')=='COMPLETE': state='QA_REPAIR_OR_RELEASE'
    elif ac.get('status')=='COMPILED': state='PRODUCTION_READY'
    else: state='STRATEGY_OR_COMPILE_READY'
    return {
        'state':state,
        'compliance_status':comp.get('status'),
        'asset_compile_status':ac.get('status'),
        'production_status':pr.get('status'),
        'meaning':{
            'PUBLISH_READY':'平台常规上传检查后可发布',
            'PRODUCTION_READY':'可立即生成/拍摄/编辑',
            'TEST_READY':'可立即进入受控测试',
            'QA_REPAIR':'已生成但需要局部修复',
            'NEEDS_HARD_INPUT':'缺少会导致事实虚构/错误执行的真实输入',
            'HOLD_COMPLIANCE':'具体 Claim/法律/平台规则阻断',
            'STOP_ECONOMICS':'当前动作在已知经济输入下不可行',
        },
    }


def _launch_board(agent_next_action:Mapping[str,Any]|None,listing:dict[str,Any],assets:dict[str,Any],paid:dict[str,Any],reviews:dict[str,Any],economics:dict[str,Any],release:dict[str,Any])->list[dict[str,Any]]:
    rows=[]
    def add(priority,owner,action,target,artifact=None,metric=None,dependency=None):
        rows.append({'priority':priority,'owner':owner,'exact_action':action,'target_object':target,'artifact_or_object':artifact,'dependency':dependency,'completion_check':metric or '目标对象达到对应 Release Status；相关 Truth/Claim/平台约束通过。'})
    next_action=_dict(agent_next_action)
    if _meaningful(next_action):
        add('P0','AGENT/OPERATOR',_pick(next_action,'next_action','action','instruction',default='执行当前 Agent Next Action'),'PROJECT',artifact='agent_next_action.json')
    if listing.get('status') not in {'NOT_SUPPLIED',None}:
        add('P1','LISTING','发布或完成 Listing Release 中未完成字段；直接使用最终字段对象，不从策略报告重新摘录。','LISTING',artifact='operator_execution_board.listing_release')
    if assets.get('asset_count'):
        add('P1','CREATIVE/PRODUCTION','按 Asset Production Board 逐资产执行；先做 activation/test 优先资产，生成后做真实成图 QA。','ASSETS',artifact='operator_execution_board.asset_production_board')
    if paid.get('status')!='NO_PAID_INPUT':
        add('P1','MEDIA','按 Paid Test Queue 启动最小可归因测试；预算不得越过经济边界。','PAID',artifact='operator_execution_board.paid_test_queue')
    if reviews.get('revisions'):
        add('P1','CX/CONTENT/PRODUCT','执行 Review Revision Queue 的责任层局部修订并验证问题是否下降。','REVISION',artifact='operator_execution_board.review_revision_queue')
    if economics.get('status')!='NOT_SUPPLIED':
        add('P0','COMMERCIAL','价格/优惠/佣金/投放动作前复核 Economics Control Panel。','ECONOMICS',artifact='operator_execution_board.economics_control_panel')
    if release.get('state')=='HOLD_COMPLIANCE':
        add('P0','COMPLIANCE','仅闭环明确的合规阻断项；其他策略/制作继续推进。','COMPLIANCE',artifact='compliance_report.json')
    order={'P0':0,'P1':1,'P2':2}
    return sorted(rows,key=lambda x:order.get(str(x.get('priority')),9))


def build_operator_execution_board(*, request:Mapping[str,Any]|None=None, domain:Mapping[str,Any]|None=None, strategy:Mapping[str,Any]|None=None, architecture:Mapping[str,Any]|None=None, video_plan:Mapping[str,Any]|None=None, paid_campaigns:Mapping[str,Any]|None=None, agent_next_action:Mapping[str,Any]|None=None, compliance:Mapping[str,Any]|None=None, asset_compile:Mapping[str,Any]|None=None, production_run:Mapping[str,Any]|None=None)->dict[str,Any]:
    listing=_listing_release(domain)
    assets=_asset_board(architecture,asset_compile)
    paid=_paid_test_queue(paid_campaigns,domain)
    reviews=_review_queue(domain)
    economics=_economics_panel(domain)
    release=_release_state(compliance,asset_compile,production_run)
    return {
        'status':'OPERATOR_EXECUTION_BOARD_READY',
        'version':'0.6.37-commercial-operator-density',
        'delivery_locale':_pick((request or {}).get('target') if isinstance((request or {}).get('target'),Mapping) else {},'delivery_locale',default=(request or {}).get('delivery_locale') or 'zh-CN'),
        'commercial_thesis':_commercial_thesis(strategy),
        'launch_board':_launch_board(agent_next_action,listing,assets,paid,reviews,economics,release),
        'listing_release':listing,
        'asset_production_board':assets,
        'video_production_board':deepcopy(_dict(video_plan)),
        'paid_test_queue':paid,
        'review_revision_queue':reviews,
        'economics_control_panel':economics,
        'release_status':release,
        'operator_contract':{
            'primary_question':'运营现在具体做什么、用哪个最终对象、做到什么算完成、看什么数决定下一步？',
            'runtime_trace_is_secondary':True,
            'normal_professional_choices_are_agent_owned':True,
            'hard_blockers_only':['FACT_OR_CLAIM_WOULD_BE_INVENTED','COMPLIANCE_OR_PLATFORM_PUBLICATION_BLOCK','ECONOMICS_REQUIRED_BEFORE_SPEND_OR_DISCOUNT','EXPLICIT_LOCKED_ROUTE_MISSING_REAL_SOURCE','PROVIDER_EXECUTION_FAILURE'],
        },
    }
