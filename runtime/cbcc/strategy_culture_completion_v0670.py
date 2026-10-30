from __future__ import annotations
from copy import deepcopy
from typing import Any, Callable


def _d(v:Any)->dict[str,Any]:return v if isinstance(v,dict) else {}
def _l(v:Any)->list[Any]:return [] if v in (None,'',{}) else (v if isinstance(v,list) else [v])
def _p(v:Any)->bool:return v not in (None,'',[],{})


def _context_block(value:Any, fallback_why:str)->dict[str,Any]:
    if isinstance(value,dict):
        out=deepcopy(value);out.setdefault('status','EVIDENCED' if _p(out.get('why')) else 'TO_VERIFY');out.setdefault('why',fallback_why);return out
    if _p(value):return {'status':'EVIDENCED_OR_AUTHORED','why':value}
    return {'status':'TO_VERIFY','why':fallback_why}


def complete_strategy_culture_v0670(strategy:dict[str,Any],request:dict[str,Any]|None=None)->dict[str,Any]:
    out=deepcopy(strategy)
    mode=str(_d(out.get('human_projection')).get('mode') or out.get('delivery_mode') or out.get('scope_mode') or '').upper()
    if mode!='FULL':return out
    s=out.setdefault('sections',{}); request=request or {}
    insight=_d(s.get('03_platform_region_audience_culture_insight'))
    info=_d(s.get('01_information_completeness_assumptions_decisions'))
    core=_d(s.get('04_marketing_core_strategy'))
    vis=_d(s.get('05_visual_photography_strategy'))

    # Every major decision keeps the same four context WHY axes. Missing evidence stays TO_VERIFY.
    source_context=_d(insight.get('context_why') or insight.get('platform_region_audience_culture_why'))
    fallbacks={
      'platform':'待查证当前平台机制/规则如何改变该决策，不得用通用电商逻辑代替。',
      'region':'待查证当前区域语言、法规、支付物流、节日与宗教语境如何改变该决策。',
      'audience':'待查证当前购买任务/人群状态如何改变该决策，不从人口标签直接推断需求。',
      'race_ethnicity_culture':'待查证族裔/语言/宗教/表征/禁忌影响；不得标签化或刻板印象化。',
    }
    decisions=[]
    for raw in _l(info.get('decision_log')):
        if not isinstance(raw,dict):continue
        row=deepcopy(raw);ctx=_d(row.get('context_why'))
        for key in ('platform','region','audience','race_ethnicity_culture'):
            ctx[key]=_context_block(ctx.get(key) if _p(ctx.get(key)) else source_context.get(key),fallbacks[key])
        row['context_why']=ctx;decisions.append(row)
    if decisions:info['decision_log']=decisions
    s['01_information_completeness_assumptions_decisions']=info

    platform=(request.get('platform') or request.get('target_platform') or insight.get('platform') or insight.get('primary_platform') or 'TO_VERIFY_CURRENT_PLATFORM')
    race=[]
    for raw in _l(s.get('07_race_execution_table')):
        if not isinstance(raw,dict):continue
        row=deepcopy(raw);row.setdefault('platform',platform);race.append(row)
    if race:s['07_race_execution_table']=race

    culture=[]
    for raw in _l(s.get('08_culture_adaptation_checklist')):
        if not isinstance(raw,dict):continue
        row=deepcopy(raw)
        row.setdefault('script_check','TO_VERIFY：逐条检查语言、Claim、羞辱/标签化、宗教/文化暗示与目标市场自然度。')
        row.setdefault('casting_check','APPLICABLE_IF_HUMAN：校验年龄、肤色、发质、体型、残障与族裔/宗教呈现是否自然且不把身份映射为需求。')
        row.setdefault('wardrobe_grooming_check','APPLICABLE_IF_HUMAN：服装、妆发、发质与宗教/文化呈现按真实场景校验，避免tokenism。')
        row.setdefault('color_check','TO_VERIFY：检查颜色在当前文化/节日/宗教语境及可读性中的含义，不套用刻板颜色。')
        row.setdefault('cta_check','TO_VERIFY：CTA需符合当地语言、平台动作、支付物流真实能力与禁忌。')
        row.setdefault('result',row.get('validation_result') or 'TO_VERIFY')
        row.setdefault('modification',row.get('modification_action') or '若任一校验失败，修改对应责任层，不用泛化创意覆盖问题。')
        row['validation_result']=row.get('result')
        row['modification_action']=row.get('modification')
        culture.append(row)
    if culture:s['08_culture_adaptation_checklist']=culture

    relationships=_d(core.get('framework_relationships'))
    for key,row in list(relationships.items()):
        if not isinstance(row,dict):continue
        row=deepcopy(row)
        row.setdefault('measurement',row.get('metric') or '按该框架实际改变的决策绑定可观察指标/归因/A-B学习，不以框架出现本身作为完成。')
        relationships[key]=row
    core['framework_relationships']=relationships;s['04_marketing_core_strategy']=core

    inc=_d(vis.get('inclusive_photography'));people=str(vis.get('people_applicability') or '').upper()
    human_applicable=people in {'PERSON_PRESENT','PEOPLE_PRESENT','HUMAN_PRESENT','APPLICABLE_P0'} or bool(inc)
    dims={
      'deep_skin':{'relevance':'APPLICABLE_IF_HUMAN' if human_applicable else 'NOT_NEEDED_NO_HUMAN','why':'人物出现时必须保护深肤色暗部层次，曝光补偿仅作Prelight条件起点。','execution':inc.get('deep_skin_exposure_compensation_plan') or inc.get('deep_skin_shadow_protection') or 'Prelight测光 + neutral bounce/diffusion + waveform/histogram复核。'},
      'hair_texture_style':{'relevance':'APPLICABLE_IF_HUMAN' if human_applicable else 'NOT_NEEDED_NO_HUMAN','why':'发质/造型是人物真实表征的一部分，不应被AI统一成单一审美。','execution':inc.get('hair_texture') or '保留真实发质、发际线和边缘层次；造型服从真实人物/场景。'},
      'body_representation':{'relevance':'APPLICABLE_IF_HUMAN' if human_applicable else 'NOT_NEEDED_NO_HUMAN','why':'避免把单一体型作为默认消费者。','execution':inc.get('body_representation') or '按真实人群/场景自然选择，不以体型暗示功效、收入或自律。'},
      'disability_representation':{'relevance':'RELEVANCE_DECISION_REQUIRED_IF_HUMAN' if human_applicable else 'NOT_NEEDED_NO_HUMAN','why':'残障呈现应来自真实使用/可达性语境，不能为了“多元”token化。','execution':inc.get('disability_representation') or '相关时自然呈现辅助器具/动作并检查AI结构错误；不相关时明确NOT_NEEDED+WHY。'},
      'age_representation':{'relevance':'APPLICABLE_IF_HUMAN' if human_applicable else 'NOT_NEEDED_NO_HUMAN','why':'年龄应与真实使用者、平台合规和场景一致。','execution':inc.get('age_representation') or '保持真实年龄纹理，不做过度磨皮或把年龄映射为能力/需求。'},
      'ai_bias':{'relevance':'APPLICABLE_IF_HUMAN' if human_applicable else 'NOT_NEEDED_NO_HUMAN','why':'AI生成需显式检查肤色、发质、身体/手部、年龄与辅助器具偏差。','execution':inc.get('ai_bias_check') or '输出后逐项检查并走最小责任层修复。'},
    }
    vis['inclusive_dimension_decisions']=dims;s['05_visual_photography_strategy']=vis
    out['strategy_culture_completion_v0670']={'status':'COMPLETED_WITH_EXPLICIT_TO_VERIFY','race_platform':True,'culture_execution_columns':True,'framework_measurement':True,'decision_context_why':True,'inclusive_dimension_relevance':True}
    return out


def wrap_build_master_strategy(fn:Callable[...,dict[str,Any]]):
    def built(request:dict[str,Any],*args,**kwargs):
        return complete_strategy_culture_v0670(fn(request,*args,**kwargs),request)
    setattr(built,'_cbcc_v0670_strategy_culture_completion',True);return built


def wrap_render_master_strategy_cn(fn:Callable[[dict[str,Any]],str]):
    def rendered(strategy:dict[str,Any])->str:
        base=fn(strategy)
        mode=str(_d(strategy.get('human_projection')).get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '').upper()
        if mode!='FULL':return base
        s=_d(strategy.get('sections'));core=_d(s.get('04_marketing_core_strategy'));vis=_d(s.get('05_visual_photography_strategy'));info=_d(s.get('01_information_completeness_assumptions_decisions'))
        lines=['','### v0.6.70 决策执行闭合','', '| 对象 | Measurement / Context WHY / Relevance |','|---|---|']
        for key,row in _d(core.get('framework_relationships')).items():
            lines.append(f"| {key} | {str(_d(row).get('measurement') or '—').replace('|','\\|')} |")
        for key,row in _d(vis.get('inclusive_dimension_decisions')).items():
            value=f"{row.get('relevance')}；WHY={row.get('why')}；执行={row.get('execution')}" if isinstance(row,dict) else str(row)
            lines.append(f"| Inclusive/{key} | {value.replace('|','\\|')} |")
        for i,row in enumerate(_l(info.get('decision_log'))):
            if isinstance(row,dict):lines.append(f"| Decision {i+1} Context WHY | {str(row.get('context_why') or '—').replace('|','\\|')} |")
        return base.rstrip()+'\n'+'\n'.join(lines)+'\n'
    setattr(rendered,'_cbcc_v0670_strategy_culture_completion',True);return rendered


def completion_issues(strategy:dict[str,Any])->list[dict[str,Any]]:
    mode=str(_d(strategy.get('human_projection')).get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '').upper()
    if mode!='FULL':return []
    s=_d(strategy.get('sections'));issues=[]
    for i,row in enumerate([x for x in _l(s.get('07_race_execution_table')) if isinstance(x,dict)]):
        if not _p(row.get('platform')):issues.append({'code':'FULL_RACE_PLATFORM_MISSING','row':i})
    required={'script_check','casting_check','wardrobe_grooming_check','color_check','cta_check','result','modification','validation_result','modification_action'}
    for i,row in enumerate([x for x in _l(s.get('08_culture_adaptation_checklist')) if isinstance(x,dict)]):
        miss=sorted(k for k in required if not _p(row.get(k)))
        if miss:issues.append({'code':'FULL_CULTURE_EXECUTION_COLUMNS_MISSING_V0670','row':i,'fields':miss})
    for key,row in _d(_d(s.get('04_marketing_core_strategy')).get('framework_relationships')).items():
        if not _p(_d(row).get('measurement')):issues.append({'code':'FULL_FRAMEWORK_MEASUREMENT_MISSING','framework':key})
    dims=_d(_d(s.get('05_visual_photography_strategy')).get('inclusive_dimension_decisions'))
    for key in ('deep_skin','hair_texture_style','body_representation','disability_representation','age_representation','ai_bias'):
        if not _p(dims.get(key)):issues.append({'code':'FULL_INCLUSIVE_RELEVANCE_DECISION_MISSING','dimension':key})
    for i,row in enumerate([x for x in _l(_d(s.get('01_information_completeness_assumptions_decisions')).get('decision_log')) if isinstance(x,dict)]):
        ctx=_d(row.get('context_why'));missing=[k for k in ('platform','region','audience','race_ethnicity_culture') if not _p(ctx.get(k))]
        if missing:issues.append({'code':'FULL_DECISION_CONTEXT_WHY_MISSING_V0670','row':i,'fields':missing})
    return issues


def wrap_audit_full_strategy_depth_v3(fn:Callable[...,dict[str,Any]]):
    def audited(strategy:dict[str,Any],base_result=None):
        result=fn(strategy,base_result);issues=list(result.get('issues') or [])+completion_issues(strategy)
        result['issues']=issues;result['status']='PASS' if not issues else 'INCOMPLETE';result['strategy_culture_completion_v0670_audit']={'status':'PASS' if not completion_issues(strategy) else 'INCOMPLETE'};return result
    setattr(audited,'_cbcc_v0670_strategy_culture_completion',True);return audited
