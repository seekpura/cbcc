from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping
import re

CORE_DIMENSIONS = ('race_ethnicity','gender','age','income','geography')
CONTEXT_DIMENSIONS = ('language','religion','holiday_calendar','taboo','family_household','skin_hair_body_representation')
DENSITY_FIELDS = ('what','why','evidence','tradeoff','execution','measurement')
CULTURE_EXECUTION_CHECKS = ('script_check','casting_check','wardrobe_grooming_check','color_check','cta_check')
_FULL_DENY={'TASK_SCOPED','TASK_SCOPE','PARTIAL','NOT_FULL','NON_FULL','SCOPED','MINIMAL'}
_FULL_EXACT={'FULL','FULL_PROJECT','FULL_DELIVERY','FULL_PACKAGE','FULL_COMMERCE','FULL_STRATEGY','FULL_WORKSPACE','FULL_E2E','END_TO_END','COMPLETE_DELIVERY','COMPLETE_PROJECT','完整交付','全量交付','完整项目','全量项目'}


def _p(v: Any)->bool: return v not in (None,'',[],{})
def _d(v: Any)->dict[str,Any]: return deepcopy(dict(v)) if isinstance(v,Mapping) else {}
def _l(v: Any)->list[Any]:
    if v in (None,'',{}): return []
    return list(v) if isinstance(v,(list,tuple,set,frozenset)) else [v]

def _mode_token(v: Any)->str:
    raw=str(v or '').strip()
    if not raw: return ''
    if re.search(r'[\u3400-\u9fff]', raw): return re.sub(r'\s+','',raw)
    return re.sub(r'[^A-Z0-9]+','_',raw.upper()).strip('_')

def _is_full(strategy: Mapping[str,Any])->bool:
    try:
        from .v0674_regression_closure import is_full_strategy
        return bool(is_full_strategy(strategy))
    except (ImportError,ValueError):
        hp=_d(strategy.get('human_projection'))
        if hp.get('fixed_human_section_quota') is True: return True
        token=_mode_token(hp.get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '')
        if token in _FULL_DENY or token.startswith('NOT_FULL') or token.startswith('NON_FULL'): return False
        if token in _FULL_EXACT: return True
        if token.startswith('FULL_') and any(x in token for x in ('PROJECT','DELIVERY','PACKAGE','COMMERCE','WORKSPACE','STRATEGY','E2E')): return True
        return token in {'完整','全量'}

def _refs(raw: Mapping[str,Any])->list[str]:
    vals=raw.get('source_refs') or raw.get('source_ids') or raw.get('evidence_refs') or []
    if not _p(vals):
        ev=raw.get('evidence') or raw.get('evidence_or_assumption')
        if isinstance(ev,(list,tuple,set,frozenset)):
            vals=[x for x in ev if isinstance(x,str) and str(x).strip() and str(x).upper() not in {'TO_VERIFY','ASSUMPTION','MISSING_INPUT','UNKNOWN'}]
    return list(dict.fromkeys(str(x) for x in _l(vals) if _p(x)))

def _evidence_value(raw: Mapping[str,Any])->Any:
    if _p(raw.get('evidence')): return deepcopy(raw.get('evidence'))
    val=raw.get('evidence_or_assumption')
    return deepcopy(val) if _p(val) else []

def _explicit_unknown(value: Any)->bool:
    if isinstance(value,str):
        return value.strip().upper() in {'TO_VERIFY','ASSUMPTION','MISSING_INPUT','UNKNOWN','PENDING','NO_CULTURE_INPUT'}
    if isinstance(value,(list,tuple,set,frozenset)):
        return bool(value) and all(_explicit_unknown(x) for x in value)
    return False

def _lineage(raw: Mapping[str,Any], proof: str)->dict[str,Any]:
    refs=_refs(raw); ev=_evidence_value(raw)
    evidenced=bool(refs) or (_p(ev) and not _explicit_unknown(ev))
    return {
        'source_refs':refs,
        'exact_fact':None,
        'confidence':str(raw.get('confidence') or ('MEDIUM' if evidenced else 'LOW')).upper(),
        'assumption_boundary':raw.get('assumption_boundary') or ('EVIDENCE_BOUNDED_CULTURAL_DECISION' if evidenced else 'CULTURAL_CONTEXT_TO_VERIFY_NOT_FACT'),
        'conflict_status':raw.get('conflict_status') or 'NO_DECLARED_CONFLICT',
        'proof_object':proof,
    }

def _density_status(raw: Mapping[str,Any])->tuple[str,list[str]]:
    missing=[k for k in DENSITY_FIELDS if not _p(raw.get(k))]
    if _explicit_unknown(raw.get('evidence')) and 'evidence_decision_specific' not in missing:
        missing.append('evidence_decision_specific')
    return ('READY' if not missing else 'TO_VERIFY',missing)

def _intersection_row(raw: Mapping[str,Any], i:int)->dict[str,Any]:
    row=deepcopy(dict(raw))
    row['dimensions']=[str(x) for x in _l(row.get('dimensions')) if _p(x)]
    if not _p(row.get('evidence')) and _p(row.get('evidence_or_assumption')):
        row['evidence']=deepcopy(row.get('evidence_or_assumption'))
    for k,v in _lineage(row,f'strategy.sections.03_platform_region_audience_culture_insight.intersectionality_interaction_analysis[{i}]').items(): row.setdefault(k,v)
    row.setdefault('behavior_inference_allowed',False)
    row.setdefault('stereotype_guard','不得从身份组合直接推断需求、肤质、支付能力、价格敏感、购买意愿或生活方式。')
    status,gaps=_density_status(row)
    row['density_status']=status
    row['density_gaps']=gaps
    return row

def _culture_row(raw: Mapping[str,Any], i:int)->dict[str,Any]:
    row=deepcopy(dict(raw))
    if not _p(row.get('evidence')) and _p(row.get('evidence_or_assumption')):
        row['evidence']=deepcopy(row.get('evidence_or_assumption'))
    for k,v in _lineage(row,f'strategy.sections.08_culture_adaptation_checklist[{i}]').items(): row.setdefault(k,v)
    row.setdefault('behavior_inference_allowed',False)
    density_status,density_gaps=_density_status(row)
    check_gaps=[k for k in CULTURE_EXECUTION_CHECKS if not _p(row.get(k))]
    row['density_status']='READY' if density_status=='READY' and not check_gaps else 'TO_VERIFY'
    row['density_gaps']={'decision_density':density_gaps,'execution_checks':check_gaps}
    return row

def _dimension_coverage(insight: Mapping[str,Any], interactions: list[Mapping[str,Any]])->dict[str,dict[str,Any]]:
    table=[x for x in _l(insight.get('intersectionality_table')) if isinstance(x,Mapping)]
    out={}
    for dim in CORE_DIMENSIONS:
        evidence=[]; seen=False
        for row in table:
            if dim in {str(x) for x in _l(row.get('dimensions'))}:
                seen=True
                if _p(row.get('evidence_or_assumption')): evidence.extend(_l(row.get('evidence_or_assumption')))
        for row in interactions:
            if dim in {str(x) for x in _l(row.get('dimensions'))}:
                seen=True
                ev=row.get('evidence') or row.get('evidence_or_assumption')
                if _p(ev): evidence.extend(_l(ev))
        real=[x for x in evidence if not _explicit_unknown(x)]
        out[dim]={
            'status':'EVIDENCED' if real else 'TO_VERIFY',
            'why':'该维度仅在有目标市场证据表明会改变表征、语言、可达性或购买任务时影响执行；身份本身不构成行为因果。' if seen else 'FULL 交叉性最低维度之一，但当前没有决策级证据；保留为 TO_VERIFY，不补造人口结论。',
            'evidence':deepcopy(real),
            'exact_fact':None,
            'behavior_inference_allowed':False,
        }
    return out

def _context_coverage(insight: Mapping[str,Any])->dict[str,dict[str,Any]]:
    existing=_d(insight.get('culture_context_coverage'))
    aliases={
        'language':('language','language_profiles','back_translation'),
        'religion':('religion','religious_context'),
        'holiday_calendar':('holiday_calendar','festival_calendar','holiday'),
        'taboo':('stereotype_taboo','taboo','cultural_taboo'),
        'family_household':('family_structure','household','lifestyle'),
        'skin_hair_body_representation':('skin_hair_body_representation','representation','inclusive_representation'),
    }
    out={}
    for key in CONTEXT_DIMENSIONS:
        authored=_d(existing.get(key))
        if authored:
            status=str(authored.get('status') or ('EVIDENCED' if _p(authored.get('evidence')) else 'TO_VERIFY')).upper()
            if status not in {'EVIDENCED','TO_VERIFY','NOT_NEEDED','MISSING_INPUT'}: status='TO_VERIFY'
            out[key]=deepcopy(authored)
            out[key]['status']=status
            out[key].setdefault('why','由 Agent 按当前市场/人群/任务判断该文化语境是否相关；无依据时不得自动激活。')
            out[key].setdefault('exact_fact',None)
            out[key].setdefault('behavior_inference_allowed',False)
            continue
        explicit=None
        for alias in aliases[key]:
            if _p(insight.get(alias)):
                explicit=insight.get(alias); break
        if explicit is not None:
            out[key]={
                'status':'TO_VERIFY',
                'why':'检测到相关上游语境，但尚未形成带证据边界的决策级文化结论；需核验后再用于文案、人物、道具、颜色、CTA或媒体行为。',
                'evidence':[], 'exact_fact':None, 'behavior_inference_allowed':False,
                'upstream_context':deepcopy(explicit),
            }
        else:
            out[key]={
                'status':'TO_VERIFY',
                'why':'当前没有足够输入判断该语境是否改变商业/传播决策；保持中性并待查证，不做 tokenistic 文化填充。',
                'evidence':[], 'exact_fact':None, 'behavior_inference_allowed':False,
            }
    return out

def materialize_intersectionality_culture_authority(strategy: Mapping[str,Any])->dict[str,Any]:
    out=deepcopy(dict(strategy))
    if not _is_full(out): return out
    sections=out.setdefault('sections',{})
    insight=_d(sections.get('03_platform_region_audience_culture_insight'))
    interactions=[_intersection_row(x,i) for i,x in enumerate(_l(insight.get('intersectionality_interaction_analysis'))) if isinstance(x,Mapping)]
    insight['intersectionality_interaction_analysis']=interactions
    sections['03_platform_region_audience_culture_insight']=insight
    culture=[_culture_row(x,i) for i,x in enumerate(_l(sections.get('08_culture_adaptation_checklist'))) if isinstance(x,Mapping)]
    sections['08_culture_adaptation_checklist']=culture
    ready=bool(interactions and culture) and all(x.get('density_status')=='READY' for x in interactions) and all(x.get('density_status')=='READY' for x in culture)
    out['sections']=sections
    out['intersectionality_culture_authority_v0676']={
        'status':'READY' if ready else 'TO_VERIFY',
        'core_dimensions':list(CORE_DIMENSIONS),
        'dimension_coverage':_dimension_coverage(insight,interactions),
        'context_coverage':_context_coverage(insight),
        'culture_execution_checks':list(CULTURE_EXECUTION_CHECKS),
        'principle':'Identity/culture can change execution only through evidenced or explicitly assumed mechanisms. Unknowns remain TO_VERIFY; identity never authorizes automatic behavior inference.',
    }
    return out

def intersectionality_culture_issues(strategy: Mapping[str,Any])->list[dict[str,Any]]:
    if not _is_full(strategy): return []
    sections=_d(strategy.get('sections')); issues=[]
    insight=_d(sections.get('03_platform_region_audience_culture_insight'))
    interactions=[x for x in _l(insight.get('intersectionality_interaction_analysis')) if isinstance(x,Mapping)]
    if not interactions: issues.append({'code':'FULL_INTERSECTIONALITY_INTERACTION_MISSING_V0676'})
    for i,row in enumerate(interactions):
        dims=[str(x) for x in _l(row.get('dimensions'))]
        gaps=[k for k in DENSITY_FIELDS if not _p(row.get(k))]
        if _explicit_unknown(row.get('evidence')) and 'evidence_decision_specific' not in gaps: gaps.append('evidence_decision_specific')
        if len(dims)<2: gaps.append('dimensions>=2')
        if not _p(row.get('stereotype_guard')): gaps.append('stereotype_guard')
        if gaps: issues.append({'code':'FULL_INTERSECTIONALITY_DENSITY_INCOMPLETE_V0676','row':i,'fields':gaps})
    culture=[x for x in _l(sections.get('08_culture_adaptation_checklist')) if isinstance(x,Mapping)]
    if not culture: issues.append({'code':'FULL_CULTURE_ADAPTATION_CHECKLIST_MISSING_V0676'})
    for i,row in enumerate(culture):
        gaps=[k for k in DENSITY_FIELDS if not _p(row.get(k))]
        if _explicit_unknown(row.get('evidence')) and 'evidence_decision_specific' not in gaps: gaps.append('evidence_decision_specific')
        gaps += [k for k in CULTURE_EXECUTION_CHECKS if not _p(row.get(k))]
        if not _p(row.get('stereotype_taboo_risk')): gaps.append('stereotype_taboo_risk')
        if gaps: issues.append({'code':'FULL_CULTURE_ADAPTATION_DENSITY_INCOMPLETE_V0676','row':i,'fields':list(dict.fromkeys(gaps))})
    auth=_d(strategy.get('intersectionality_culture_authority_v0676'))
    dims=_d(auth.get('dimension_coverage'))
    missing=[d for d in CORE_DIMENSIONS if d not in dims]
    if missing: issues.append({'code':'FULL_INTERSECTIONALITY_CORE_DIMENSION_COVERAGE_MISSING_V0676','dimensions':missing})
    return issues

def wrap_build_master_strategy(fn: Callable[...,dict[str,Any]]):
    def built(request: dict[str,Any], *args:Any, **kwargs:Any):
        return materialize_intersectionality_culture_authority(fn(request,*args,**kwargs))
    setattr(built,'_cbcc_v0676_intersectionality_culture_authority',True)
    return built

def wrap_validate_strategy_delivery(fn: Callable[[dict[str,Any]],dict[str,Any]]):
    def validated(strategy: dict[str,Any]):
        result=fn(strategy)
        if not _is_full(strategy): return result
        current=intersectionality_culture_issues(strategy)
        issues=list(result.get('issues') or []) + current
        dedup=[]
        for x in issues:
            if x not in dedup: dedup.append(x)
        result['issues']=dedup
        result['status']='PASS' if not dedup else 'INCOMPLETE'
        result['intersectionality_culture_authority_v0676_audit']={'status':'PASS' if not current else 'INCOMPLETE','issues':current}
        return result
    setattr(validated,'_cbcc_v0676_intersectionality_culture_authority',True)
    return validated
