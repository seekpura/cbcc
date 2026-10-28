from pathlib import Path
import re

# ---- strategy_depth.py: append final authority overrides without deleting mature depth ----
p=Path('runtime/cbcc/strategy_depth.py')
s=p.read_text(encoding='utf-8')
marker='# ---------------------------------------------------------------------------\n# v0.6.24 Task-scoped Strategy / Asset authority\n'
if marker not in s:
    s += r'''

# ---------------------------------------------------------------------------
# v0.6.24 Task-scoped Strategy / Asset authority
# Machine compatibility keeps the nine canonical section keys. Human strategy,
# optional thinking frameworks, experiments and next-actions are projections of
# the current commerce task rather than universal quotas.
# ---------------------------------------------------------------------------
_V0624_ORIG_RISK = build_risk_priority_depth
_V0624_ORIG_MASTER = build_master_strategy_depth
_V0624_ORIG_RENDER = render_master_strategy_cn_depth


def _v0624_rows(value):
    if value is None: return []
    return value if isinstance(value,list) else [value]


def _v0624_framework_names(request:dict[str,Any]) -> list[str]:
    plan=request.get('_agent_autonomy_plan') or {}
    raw=plan.get('strategy_frameworks') if isinstance(plan,dict) else None
    if raw is None: raw=request.get('marketing_frameworks') if request.get('marketing_frameworks') is not None else request.get('persuasion_frameworks')
    if raw is None: return []
    if isinstance(raw,str): raw=[x.strip() for x in re.split(r'[,/|]+',raw) if x.strip()]
    elif isinstance(raw,dict):
        if isinstance(raw.get('selected'),list): raw=raw.get('selected')
        elif isinstance(raw.get('frameworks'),list): raw=raw.get('frameworks')
        else: raw=[k for k,v in raw.items() if v not in (False,None,'',[],{})]
    elif not isinstance(raw,(list,tuple,set)): raw=[raw]
    aliases={
      'FUNNEL':'Funnel','MEANS_END':'Means_End','MEANS-END':'Means_End','SIGNALING':'Signaling',
      'FIRST':'FIRST_Hero_Gate','FIRST_HERO_GATE':'FIRST_Hero_Gate','COGNITIVE_BUDGET':'Cognitive_Budget',
      'BELIEF_SEQUENCE':'Belief_Sequence','COMMERCE_RESPONSE_LADDER':'Commerce_Response_Ladder',
      '4P':'4P','STP':'STP','JTBD':'JTBD','AIDA':'AIDA','FABE':'FABE','FOGG':'Fogg','RACE':'RACE'
    }
    out=[]
    for x in raw:
        key=str(x or '').strip().upper().replace(' ','_')
        name=aliases.get(key,str(x).strip())
        if name and name not in out: out.append(name)
    return out


def _v0624_evaluation_requested(request:dict[str,Any], frameworks:list[str]|None=None) -> bool:
    plan=request.get('_agent_autonomy_plan') or {}
    iteration=plan.get('iteration_policy') if isinstance(plan,dict) and isinstance(plan.get('iteration_policy'),dict) else {}
    signals=[request.get('experiment'),request.get('measurement_plan'),request.get('ab_test'),request.get('ab_testing'),request.get('evaluation_plan'),request.get('ad_analysis'),request.get('feedback_rows')]
    if any(bool(x) for x in signals): return True
    if any(bool(v) for k,v in iteration.items() if any(t in str(k).casefold() for t in ['test','experiment','measure','evaluate'])): return True
    return any(str(x).upper() in {'EVALUATION','EXPERIMENT','A/B','AB_TEST'} for x in (frameworks or []))


def build_risk_priority_depth(info:dict[str,Any], request:dict[str,Any], compliance:dict[str,Any], research_gate:dict[str,Any], positioning:dict[str,Any], assets:list[dict[str,Any]], experiment:dict[str,Any]|None, market_depth:dict[str,Any]|None=None):
    base=_V0624_ORIG_RISK(info,request,compliance,research_gate,positioning,assets,experiment,market_depth)
    frameworks=_v0624_framework_names(request)
    pending=[x for x in (research_gate.get('actions') or []) if x.get('status')!='RESOLVED']
    p0=[]
    if compliance.get('status')=='HOLD':
        for issue in (compliance.get('issues') or [])[:12]:
            p0.append({'action':f"解决当前合规阻断：{issue.get('code') or issue.get('issue') or issue.get('scope') or 'COMPLIANCE_HOLD'}",'why':'这是当前已观测到的真实合规/证据阻断，不是通用检查清单。','source_issue':issue})
        if not p0:
            p0.append({'action':'解决当前 Compliance HOLD 后再执行受影响的发布/生产动作。','why':'HOLD 已真实存在；只修受影响范围，不扩写成全项目重做。'})
    p1=[]
    for row in pending:
        p1.append({'action':row.get('query') or row.get('reason') or '解决当前研究缺口','why':row.get('reason') or '该缺口仍会改变当前商业决策。','required_for':row.get('required_for') or []})
    p2=[]
    if _v0624_evaluation_requested(request,frameworks):
        if experiment:
            p2.append({'action':'按已声明的实验/测量设计完成当前评估并把结论路由到最小责任层。','why':'当前任务显式包含 Evaluation / Experiment，因此测量是本轮工作而不是默认未来配额。'})
        elif request.get('ad_analysis') or request.get('feedback_rows') or request.get('measurement_plan'):
            p2.append({'action':'按当前已提供的广告/反馈/测量信号执行局部评估与修订。','why':'只有当前任务真实存在评估信号时才形成评估动作。'})
    base['priority_plan']={
      'P0':p0,'P1':p1,'P2':p2,
      'next_information_needed':[x.get('action') for x in p1 if x.get('action')],
      'status':'ACTION_REQUIRED' if (p0 or p1 or p2) else 'CURRENT_SCOPE_CAN_STOP',
      'synthetic_fallback_actions':False,
      'principle':'No action is created merely to keep P0/P1/P2 non-empty. The current Agent may stop when material unresolved conditions are absent.'
    }
    if not _v0624_evaluation_requested(request,frameworks):
        base['ab_test_hypotheses']=[]
        base['ab_test_status']='NOT_IN_CURRENT_SCOPE'
    else:
        base['ab_test_status']='CURRENT_EVALUATION_SCOPE'
    base['agent_stop_eligible']=not bool(p0 or p1 or p2)
    return base


def _v0624_human_projection(request:dict[str,Any], strategy:dict[str,Any], frameworks:list[str]) -> dict[str,Any]:
    s=strategy.get('sections') or {}; plan=request.get('_agent_autonomy_plan') or {}
    scope=plan.get('content_scope') if isinstance(plan,dict) and isinstance(plan.get('content_scope'),dict) else {}
    families=[]
    for src in [request.get('content_families'),scope.get('families'),scope.get('content_families')]:
        for x in _v0624_rows(src):
            name=str(x or '').strip()
            if name and name not in families: families.append(name)
    full=bool(request.get('full_strategy') or request.get('full_delivery')) or str(request.get('strategy_delivery_mode') or request.get('delivery_mode') or '').upper() in {'FULL','FULL_STRATEGY','SIGNATURE'}
    active=[]; reasons={}
    def add(key,reason):
        if key not in active: active.append(key); reasons[key]=reason
    info=s.get('01_information_completeness_assumptions_decisions') or {}
    value=s.get('02_product_truth_value_ladder') or {}
    third=s.get('03_platform_region_audience_culture_insight') or {}
    core=s.get('04_marketing_core_strategy') or {}
    visual=s.get('05_visual_photography_strategy') or {}
    content=s.get('06_platform_content_matrix') or []
    last=s.get('09_risk_measurement_priority_next_steps') or {}
    if full or info.get('pending_confirmations') or info.get('assumptions') or info.get('clarifying_questions'):
        add('01_information_completeness_assumptions_decisions','当前存在真实信息缺口/假设，或用户要求完整策略。')
    if full or value.get('product_facts') or value.get('claim_value_ladder'):
        add('02_product_truth_value_ladder','产品事实与 Claim 是当前商业决策的硬边界。')
    market_inputs=any(request.get(k) for k in ['market_rows','market_file','market_keyword_rows','market_review_rows','competitor_listing_rows','market_competitor_listing_rows','research_source_adapters'])
    culture_inputs=bool(request.get('audience_culture'))
    if full or market_inputs or culture_inputs:
        add('03_platform_region_audience_culture_insight','当前任务存在真实市场/竞品/受众/文化输入。')
    if full or core:
        add('04_marketing_core_strategy','定位、SKU/Offer 或当前 Listing 决策是策略核心对象。')
    visual_scope=bool({'VISUAL','VIDEO','CREATOR_AFFILIATE','PAID'} & set(families)) or any(request.get(k) for k in ['compile_assets','asset_jobs','photography_contract','visual_strategy','creative_directions','creative_references','source_product_assets'])
    if full or visual_scope:
        add('05_visual_photography_strategy','当前任务需要视觉/摄影/创意/资产执行。')
    if full or (content and (visual_scope or bool({'LISTING','VIDEO','CREATOR_AFFILIATE','PAID'} & set(families)))):
        add('06_platform_content_matrix','当前任务存在实际 Surface / 内容对象。')
    if full or 'RACE' in frameworks:
        add('07_race_execution_table','RACE 被用户/Agent 显式选为本项目思考工具。')
    if full or culture_inputs:
        add('08_culture_adaptation_checklist','当前任务有真实受众/文化证据或明确文化适配需求。')
    pr=last.get('priority_plan') or {}
    risk_active=bool(last.get('risk_register') and any(str(x.get('severity') or '').upper().startswith('P0') for x in last.get('risk_register') or []))
    eval_active=_v0624_evaluation_requested(request,frameworks)
    if full or risk_active or eval_active or any(pr.get(k) for k in ['P0','P1','P2']):
        add('09_risk_measurement_priority_next_steps','当前存在真实风险/未解决动作/评估任务。')
    if not active:
        add('04_marketing_core_strategy','当前策略任务只需要核心商业决策。')
    return {
      'mode':'FULL' if full else 'TASK_SCOPED',
      'active_sections':active,
      'omitted_sections':[k for k in s if k not in active],
      'section_reasons':reasons,
      'machine_sections_preserved':len(s),
      'content_families':families,
      'selected_frameworks':frameworks,
      'fixed_human_section_quota':False,
      'principle':'Machine schema stays complete for compatibility and lineage. Human strategy only renders material decisions for the current commerce task.'
    }


def build_master_strategy_depth(request:dict[str,Any], **kwargs):
    strategy=_V0624_ORIG_MASTER(request,**kwargs)
    s=strategy.get('sections') or {}; core=s.get('04_marketing_core_strategy') or {}
    frameworks=_v0624_framework_names(request)
    generated=core.get('frameworks') or {}
    if frameworks:
        kept={}
        for name in frameworks:
            if name=='RACE': continue
            if name in generated: kept[name]=generated[name]
        kept['status']='SELECTED_FRAMEWORKS_APPLIED'
        kept['applied_frameworks']=[x for x in frameworks if x!='RACE']
        kept['principle']='Frameworks are optional decision lenses; only Agent/user-selected lenses remain in current Strategy Authority.'
        core['frameworks']=kept
    else:
        core['frameworks']={'status':'NO_FRAMEWORK_REQUIRED','applied_frameworks':[],'principle':'No framework is inserted merely because the runtime knows it.'}
    s['04_marketing_core_strategy']=core
    if 'RACE' not in frameworks:
        s['07_race_execution_table']=[]
        for row in s.get('06_platform_content_matrix') or []:
            if isinstance(row,dict):
                row.pop('race_stage',None)
                row['framework_context']=[]
    else:
        for row in s.get('06_platform_content_matrix') or []:
            if isinstance(row,dict): row['framework_context']=['RACE']
    strategy['sections']=s
    strategy['selected_strategy_frameworks']=frameworks
    strategy['human_projection']=_v0624_human_projection(request,strategy,frameworks)
    strategy['runtime_strategy_depth']='0.6.24-task-scoped-strategy-asset'
    strategy['framework_quota_authority']=False
    return strategy


def _v0624_prune_numbered_sections(md:str, active:list[str]) -> str:
    key_by_num={
      '1':'01_information_completeness_assumptions_decisions','2':'02_product_truth_value_ladder',
      '3':'03_platform_region_audience_culture_insight','4':'04_marketing_core_strategy',
      '5':'05_visual_photography_strategy','6':'06_platform_content_matrix','7':'07_race_execution_table',
      '8':'08_culture_adaptation_checklist','9':'09_risk_measurement_priority_next_steps'}
    heading_names={
      '1':'信息完整度 / 假设 / 决策','2':'产品真相与价值边界','3':'市场 / 平台 / 人群 / 文化洞察',
      '4':'核心商业策略','5':'视觉 / 摄影 / CMF / 资产策略','6':'平台内容与 Surface 执行',
      '7':'RACE 执行（当前项目显式启用）','8':'文化适配（当前任务相关）','9':'风险 / 评估 / 下一动作'}
    matches=list(re.finditer(r'(?m)^## ([1-9])\.\s.*$',md))
    if not matches: return md
    prefix=md[:matches[0].start()]
    blocks=[]
    for i,m in enumerate(matches):
        num=m.group(1); end=matches[i+1].start() if i+1<len(matches) else len(md)
        if key_by_num[num] in active:
            block=md[m.start():end]
            block=re.sub(r'(?m)^## '+num+r'\.\s.*$', '## '+heading_names[num], block, count=1)
            blocks.append(block.rstrip())
    prefix=re.sub(r'(?m)^> .*$', '> 当前视图按本轮 Commerce 目标动态投影；机器层仍保留完整 Strategy Authority、证据与追溯结构。',prefix,count=1)
    return prefix.rstrip()+'\n\n'+'\n\n'.join(blocks)+'\n'


def render_master_strategy_cn_depth(strategy:dict[str,Any]):
    md=_V0624_ORIG_RENDER(strategy)
    hp=strategy.get('human_projection') or {}
    active=hp.get('active_sections') or list((strategy.get('sections') or {}).keys())
    md=_v0624_prune_numbered_sections(md,active)
    summary='、'.join(hp.get('active_sections') or [])
    insert=f"\n> 人类策略投影：{hp.get('mode') or 'TASK_SCOPED'}；当前显示 {len(active)} 个相关决策域；固定九段人类配额：无。\n"
    if '\n## ' in md:
        pos=md.find('\n## '); md=md[:pos]+insert+md[pos:]
    if '资产包连续性' not in md:
        md += '\n## 生产与追溯连续性\n机器层九段 Strategy Authority、逐资产 00–13 包、Provider / Review / Revision / Hash lineage 继续保留；人类视图的动态化不删除真源与追溯。\n'
    return md
'''
    p.write_text(s,encoding='utf-8')

# ---- asset_architecture.py: no invented asset surface, no invented sequence ----
p=Path('runtime/cbcc/asset_architecture.py')
s=p.read_text(encoding='utf-8')
s=s.replace("    if questions and not candidates:\n        candidates=[{'family':'VISUAL','surface':'GALLERY','content_object_id':None}]\n", "    # v0.6.24: no visual/video candidate means no asset scope. Shopper questions stay in strategy/listing\n    # until an actual Surface/family or explicit asset job activates production.\n")
s=s.replace("    for i,a in enumerate(assets[:-1]):\n        if not a.get('handoff'): a['handoff']=assets[i+1]['asset_id']\n", "    # v0.6.24: list order is presentation order only. Asset relationships are explicit; no A→B→C auto-chain.\n")
old="""    decision_audit=_decision_question_audit(questions,assets)
    return {'assets':assets,'asset_count':len(assets),'fixed_count_authority':False,'architecture_principle':'Every asset must earn its role by shopper question, surface need and incremental information.','curation_principle':'Merge only assets that solve the same decision job on the same surface; do not force a target count.','category_family':category_family,'category_execution_profile':profile,'decision_question_audit':decision_audit,'market_theme_jobs_considered':len(market_jobs),'explicit_asset_jobs_authoritative':bool(explicit_jobs)}
"""
new="""    decision_audit=_decision_question_audit(questions,assets)
    asset_scope_active=bool(explicit_jobs or candidates)
    if not asset_scope_active:
        decision_audit['unrouted_questions']=list(decision_audit.get('uncovered_questions') or [])
        decision_audit['uncovered_questions']=[]
        decision_audit['coverage_status']='NO_ASSET_SURFACE_IN_CURRENT_SCOPE'
        decision_audit['principle']='Shopper questions may remain in Strategy/Listing without becoming image/video jobs. Asset production begins only when an actual Surface/family or explicit job exists.'
    explicit_handoffs=sum(1 for a in assets if a.get('handoff'))
    return {'assets':assets,'asset_count':len(assets),'fixed_count_authority':False,'architecture_principle':'Every asset must earn its role by shopper question, surface need and incremental information.','curation_principle':'Merge only assets that solve the same decision job on the same surface; do not force a target count.','category_family':category_family,'category_execution_profile':profile,'decision_question_audit':decision_audit,'market_theme_jobs_considered':len(market_jobs),'explicit_asset_jobs_authoritative':bool(explicit_jobs),'asset_scope_active':asset_scope_active,'relationship_mode':'EXPLICIT_ONLY','explicit_handoff_count':explicit_handoffs,'auto_sequence_authority':False}
"""
if old not in s:
    raise SystemExit('asset architecture return block not found')
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')

# ---- compiler version ----
p=Path('runtime/cbcc/compiler.py')
s=p.read_text(encoding='utf-8')
s=s.replace("st.data['runtime_version']='0.6.23-task-scoped-delivery'","st.data['runtime_version']='0.6.24-task-scoped-strategy-asset'")
p.write_text(s,encoding='utf-8')

# ---- targeted tests ----
Path('tests/test_v0624_strategy_asset_scope.py').write_text(r'''from pathlib import Path
import json
from cbcc.asset_architecture import build_asset_architecture
from cbcc.strategy_depth import build_risk_priority_depth
from cbcc.compiler import build_project


def _pack(tmp_path):
    pack=tmp_path/'packs'; pack.mkdir(exist_ok=True)
    (pack/'test.yaml').write_text('''"''pack_id: test
platform_family: test_platform
site: "*"
status: TEST_FIXTURE_VERIFIED
synthetic_for_test: true
capabilities: [LISTING, SEARCH, VISUAL, VIDEO, PAID, MEASUREMENT, COMPLIANCE]
surfaces: [PDP, GALLERY, PDP_VIDEO, PAID_AD]
rule_atoms: []
research_required_for: []
''"''')
    return pack


def _base_request(**extra):
    req={
      'project_id':'V0624','planning_only':True,
      'product':{'name':'Task Product','category':'general','net_content':'30ml','primary_conversion_proposition':'Clear product value'},
      'sources':[{'source_id':'SRC','kind':'PRODUCT_TRUTH'}],
      'target':{'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY'],'surfaces':['PDP']},
      'content_families':['LISTING'],
      'shopper_questions':['What is it?','Why is it relevant?'],
    }
    req.update(extra); return req


def test_machine_strategy_stays_nine_sections_but_human_projection_is_task_scoped(tmp_path):
    p=tmp_path/'proj'; build_project(p,_base_request(),_pack(tmp_path))
    strategy=json.loads((p/'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
    assert len(strategy['sections'])==9
    hp=strategy['human_projection']
    assert hp['fixed_human_section_quota'] is False
    assert hp['mode']=='TASK_SCOPED'
    assert '07_race_execution_table' not in hp['active_sections']
    assert strategy['sections']['07_race_execution_table']==[]
    assert strategy['sections']['04_marketing_core_strategy']['frameworks']['status']=='NO_FRAMEWORK_REQUIRED'
    assert all('race_stage' not in row for row in strategy['sections']['06_platform_content_matrix'])
    md=(p/'artifacts/strategy/MASTER_STRATEGY_CN.md').read_text(encoding='utf-8')
    assert '固定九段人类配额：无' in md
    assert 'RACE 执行（当前项目显式启用）' not in md
    assert '文化适配（当前任务相关）' not in md


def test_explicit_race_is_preserved_as_optional_framework(tmp_path):
    req=_base_request(agent_plan={'strategy_frameworks':['RACE'],'content_scope':{'families':['LISTING']}})
    p=tmp_path/'proj2'; build_project(p,req,_pack(tmp_path))
    strategy=json.loads((p/'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
    assert 'RACE' in strategy['selected_strategy_frameworks']
    assert strategy['sections']['07_race_execution_table']
    assert '07_race_execution_table' in strategy['human_projection']['active_sections']


def test_priority_and_ab_do_not_manufacture_perpetual_next_work():
    out=build_risk_priority_depth({'required_missing':[]},{}, {'status':'READY_REVIEW','issues':[]},{'actions':[]},{'primary_conversion_proposition':'X'},[],None,{})
    assert out['priority_plan']['status']=='CURRENT_SCOPE_CAN_STOP'
    assert out['priority_plan']['P0']==[] and out['priority_plan']['P1']==[] and out['priority_plan']['P2']==[]
    assert out['ab_test_hypotheses']==[]
    assert out['agent_stop_eligible'] is True
    out2=build_risk_priority_depth({'required_missing':[]},{'experiment':{'assignment_unit':'user'}}, {'status':'READY_REVIEW','issues':[]},{'actions':[]},{'primary_conversion_proposition':'X'},[],{'status':'DESIGN'}, {})
    assert out2['ab_test_status']=='CURRENT_EVALUATION_SCOPE'
    assert out2['priority_plan']['P2']


def test_asset_architecture_does_not_create_visual_job_without_asset_surface():
    arch=build_asset_architecture('P',{},['What is it?'],[{'family':'LISTING','surface':'PDP','object_id':'L1'}],None,{},'GENERAL_COMMERCE')
    assert arch['asset_count']==0
    assert arch['asset_scope_active'] is False
    assert arch['decision_question_audit']['coverage_status']=='NO_ASSET_SURFACE_IN_CURRENT_SCOPE'
    assert arch['decision_question_audit']['unrouted_questions']


def test_asset_relationships_are_explicit_not_auto_chained():
    jobs=[
      {'asset_id':'A','family':'VISUAL','surface':'GALLERY','asset_type':'IMAGE','consumer_question':'Q1'},
      {'asset_id':'B','family':'VISUAL','surface':'GALLERY','asset_type':'IMAGE','consumer_question':'Q2'},
    ]
    arch=build_asset_architecture('P',{},['Q1','Q2'],[],jobs,{},'GENERAL_COMMERCE')
    assert arch['relationship_mode']=='EXPLICIT_ONLY' and arch['auto_sequence_authority'] is False
    assert all(not x.get('handoff') for x in arch['assets'])
    jobs[0]['handoff']='B'
    arch2=build_asset_architecture('P2',{},['Q1','Q2'],[],jobs,{},'GENERAL_COMMERCE')
    assert next(x for x in arch2['assets'] if x['asset_id']=='A')['handoff']=='B'
    assert arch2['explicit_handoff_count']==1
''',encoding='utf-8')

print('v0.6.24 patch staged')
