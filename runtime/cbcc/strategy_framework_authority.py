from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping
import re

FRAMEWORKS = ('RACE','STP','JTBD','AIDA','FABE','4P','FUNNEL')
RACE_ORDER = ('RESEARCH','ACTION','COMMUNICATION','EVALUATION')
DENSITY_FIELDS = ('what','why','evidence','tradeoff','execution','measurement')
_FULL_DENY={'TASK_SCOPED','TASK_SCOPE','PARTIAL','NOT_FULL','NON_FULL','SCOPED','MINIMAL'}
_FULL_EXACT={'FULL','FULL_PROJECT','FULL_DELIVERY','FULL_PACKAGE','FULL_COMMERCE','FULL_STRATEGY','FULL_WORKSPACE','FULL_E2E','END_TO_END','COMPLETE_DELIVERY','COMPLETE_PROJECT','完整交付','全量交付','完整项目','全量项目'}


def _p(v: Any) -> bool:
    return v not in (None,'',[],{})


def _d(v: Any) -> dict[str,Any]:
    return deepcopy(dict(v)) if isinstance(v,Mapping) else {}


def _l(v: Any) -> list[Any]:
    if v in (None,'',{}): return []
    return list(v) if isinstance(v,(list,tuple,set,frozenset)) else [v]


def _mode_token(v: Any) -> str:
    raw=str(v or '').strip()
    if not raw: return ''
    if re.search(r'[\u3400-\u9fff]',raw): return re.sub(r'\s+','',raw)
    return re.sub(r'[^A-Z0-9]+','_',raw.upper()).strip('_')


def _is_full(strategy: Mapping[str,Any]) -> bool:
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


def _refs(raw: Mapping[str,Any]) -> list[str]:
    vals=raw.get('source_refs') or raw.get('source_ids') or raw.get('evidence_refs') or []
    if not _p(vals):
        ev=raw.get('evidence')
        if isinstance(ev,(list,tuple,set,frozenset)):
            vals=[x for x in ev if isinstance(x,str) and str(x).strip()]
    return list(dict.fromkeys(str(x) for x in _l(vals) if _p(x)))


def _lineage(raw: Mapping[str,Any], proof: str, missing_boundary: str) -> dict[str,Any]:
    refs=_refs(raw)
    has_evidence=_p(raw.get('evidence')) or bool(refs)
    return {
        'source_refs':refs,
        'exact_fact':None,
        'confidence':str(raw.get('confidence') or ('MEDIUM' if has_evidence else 'LOW')).upper(),
        'assumption_boundary':raw.get('assumption_boundary') or (None if has_evidence else missing_boundary),
        'conflict_status':raw.get('conflict_status') or 'NO_DECLARED_CONFLICT',
        'proof_object':proof,
    }


def _density(raw: Mapping[str,Any], *, require_changed_decision: bool=False) -> tuple[str,list[str]]:
    missing=[k for k in DENSITY_FIELDS if not _p(raw.get(k))]
    if require_changed_decision and not _p(raw.get('changed_decision')):
        missing.append('changed_decision')
    return ('READY' if not missing else 'TO_VERIFY',missing)


def _decision_object(raw: Any, *, kind: str, proof: str, missing_boundary: str) -> dict[str,Any]:
    if not isinstance(raw,Mapping):
        return {
            'kind':kind,
            'what':None,'why':None,'evidence':[],'tradeoff':None,'execution':None,'measurement':None,
            'density_status':'TO_VERIFY','density_gaps':list(DENSITY_FIELDS),
            'source_refs':[],'exact_fact':None,'confidence':'LOW','assumption_boundary':missing_boundary,
            'conflict_status':'NO_DECLARED_CONFLICT','proof_object':proof,
        }
    src=_d(raw)
    nested_why=_d(src.get('why'))
    out=deepcopy(src)
    out['kind']=kind
    if not _p(out.get('what')):
        if kind=='POSITIONING' and _p(src.get('decision')): out['what']=src.get('decision')
        elif kind=='MESSAGE_HIERARCHY' and _p(src.get('message')): out['what']=src.get('message')
    if isinstance(src.get('why'),Mapping):
        out['why']=nested_why.get('why')
        for key in ('evidence','tradeoff','execution','measurement'):
            if not _p(out.get(key)) and _p(nested_why.get(key)):
                out[key]=deepcopy(nested_why.get(key))
    if not _p(out.get('evidence')):
        ev=src.get('evidence_refs') or src.get('source_refs')
        out['evidence']=deepcopy(ev) if _p(ev) else []
    for key,val in _lineage(out,proof,missing_boundary).items():
        out.setdefault(key,val)
    status,gaps=_density(out)
    out['density_status']=status
    out['density_gaps']=gaps
    return out


def _framework_row(name: str, raw: Any) -> dict[str,Any]:
    src=_d(raw)
    out=deepcopy(src)
    raw_status=str(src.get('status') or '').upper()
    application_status=raw_status if raw_status in {'APPLIED','NOT_NEEDED'} else 'TO_VERIFY'
    out['framework']=name
    out['application_status']=application_status
    if not _p(out.get('evidence')):
        ev=src.get('evidence_refs') or src.get('source_refs')
        out['evidence']=deepcopy(ev) if _p(ev) else []
    for key,val in _lineage(out,f'strategy.sections.04_marketing_core_strategy.framework_relationships.{name}',f'{name}_APPLICATION_NOT_DECISION_SPECIFIC').items():
        out.setdefault(key,val)
    status,gaps=_density(out,require_changed_decision=True)
    if application_status not in {'APPLIED','NOT_NEEDED'}:
        gaps=['application_status',*gaps]
        status='TO_VERIFY'
    out['density_status']=status
    out['density_gaps']=list(dict.fromkeys(gaps))
    return out


def _race_row(raw: Any, i: int) -> dict[str,Any]:
    src=_d(raw)
    out=deepcopy(src)
    stage=str(src.get('stage') or '').upper()
    out['stage']=stage
    if not _p(out.get('evidence')):
        ev=src.get('evidence_refs') or src.get('source_refs')
        out['evidence']=deepcopy(ev) if _p(ev) else []
    for key,val in _lineage(out,f'strategy.sections.07_race_execution_table[{i}]',f'RACE_{stage or i}_APPLIED_DECISION_NOT_AUTHORED').items():
        out.setdefault(key,val)
    status,gaps=_density(out)
    if stage not in RACE_ORDER:
        gaps=['stage',*gaps]; status='TO_VERIFY'
    out['density_status']=status
    out['density_gaps']=list(dict.fromkeys(gaps))
    return out


def materialize_strategy_framework_authority(strategy: Mapping[str,Any]) -> dict[str,Any]:
    out=deepcopy(dict(strategy))
    if not _is_full(out): return out
    sections=_d(out.get('sections'))
    core=_d(sections.get('04_marketing_core_strategy'))

    positioning=_decision_object(
        core.get('positioning'), kind='POSITIONING',
        proof='strategy.sections.04_marketing_core_strategy.positioning',
        missing_boundary='POSITIONING_NOT_AUTHORED',
    )
    value_proposition=_decision_object(
        core.get('value_proposition'), kind='VALUE_PROPOSITION',
        proof='strategy.sections.04_marketing_core_strategy.value_proposition',
        missing_boundary='VALUE_PROPOSITION_NOT_AUTHORED',
    )
    message_rows=[
        _decision_object(x,kind='MESSAGE_HIERARCHY',proof=f'strategy.sections.04_marketing_core_strategy.message_hierarchy[{i}]',missing_boundary='MESSAGE_HIERARCHY_DECISION_INCOMPLETE')
        for i,x in enumerate(_l(core.get('message_hierarchy'))) if isinstance(x,Mapping)
    ]
    framework_raw=_d(core.get('framework_relationships'))
    frameworks={name:_framework_row(name,framework_raw.get(name)) for name in FRAMEWORKS}
    race=[_race_row(x,i) for i,x in enumerate(_l(sections.get('07_race_execution_table'))) if isinstance(x,Mapping)]

    race_order=[str(x.get('stage') or '').upper() for x in race]
    framework_ready=all(x.get('density_status')=='READY' for x in frameworks.values())
    race_ready=race_order==list(RACE_ORDER) and all(x.get('density_status')=='READY' for x in race)
    ready=(
        positioning.get('density_status')=='READY' and
        value_proposition.get('density_status')=='READY' and
        bool(message_rows) and all(x.get('density_status')=='READY' for x in message_rows) and
        framework_ready and race_ready
    )
    out['strategy_framework_authority_v0676']={
        'status':'READY' if ready else 'TO_VERIFY',
        'positioning':positioning,
        'value_proposition':value_proposition,
        'message_hierarchy':message_rows,
        'frameworks':frameworks,
        'race':race,
        'required_framework_registry':list(FRAMEWORKS),
        'race_order':list(RACE_ORDER),
        'required_density_fields':list(DENSITY_FIELDS),
        'principle':'Framework names/definitions are not applied strategy. APPLIED requires a named changed decision plus decision-specific evidence, tradeoff, execution and measurement; NOT_NEEDED requires the same explicit reasoning density. Runtime does not invent missing value proposition, framework application or RACE evidence.',
    }
    return out


def strategy_framework_issues(strategy: Mapping[str,Any]) -> list[dict[str,Any]]:
    if not _is_full(strategy): return []
    auth=_d(strategy.get('strategy_framework_authority_v0676'))
    if not auth:
        return [{'code':'FULL_STRATEGY_FRAMEWORK_AUTHORITY_MISSING_V0676'}]
    issues=[]
    pos=_d(auth.get('positioning'))
    if pos.get('density_status')!='READY':
        issues.append({'code':'FULL_POSITIONING_DECISION_INCOMPLETE_V0676','fields':pos.get('density_gaps') or list(DENSITY_FIELDS)})
    vp=_d(auth.get('value_proposition'))
    if vp.get('density_status')!='READY':
        issues.append({'code':'FULL_VALUE_PROPOSITION_DECISION_INCOMPLETE_V0676','fields':vp.get('density_gaps') or list(DENSITY_FIELDS)})
    messages=[x for x in _l(auth.get('message_hierarchy')) if isinstance(x,Mapping)]
    if not messages:
        issues.append({'code':'FULL_MESSAGE_HIERARCHY_DECISION_INCOMPLETE_V0676','row':'MISSING','fields':list(DENSITY_FIELDS)})
    for i,row in enumerate(messages):
        if row.get('density_status')!='READY':
            issues.append({'code':'FULL_MESSAGE_HIERARCHY_DECISION_INCOMPLETE_V0676','row':i,'fields':row.get('density_gaps') or []})
    frameworks=_d(auth.get('frameworks'))
    for name in FRAMEWORKS:
        row=_d(frameworks.get(name))
        if row.get('density_status')!='READY' or row.get('application_status') not in {'APPLIED','NOT_NEEDED'}:
            issues.append({'code':'FULL_FRAMEWORK_APPLICATION_DENSITY_INCOMPLETE_V0676','framework':name,'fields':row.get('density_gaps') or ['application_status']})
    race=[x for x in _l(auth.get('race')) if isinstance(x,Mapping)]
    order=[str(x.get('stage') or '').upper() for x in race]
    if order!=list(RACE_ORDER):
        issues.append({'code':'FULL_RACE_APPLIED_DECISION_ORDER_INVALID_V0676','actual':order,'expected':list(RACE_ORDER)})
    for i,row in enumerate(race):
        if row.get('density_status')!='READY':
            issues.append({'code':'FULL_RACE_APPLIED_DECISION_DENSITY_INCOMPLETE_V0676','row':i,'stage':row.get('stage'),'fields':row.get('density_gaps') or []})
    return issues


def wrap_build_master_strategy(fn: Callable[...,dict[str,Any]]):
    def built(request: dict[str,Any], *args:Any, **kwargs:Any):
        return materialize_strategy_framework_authority(fn(request,*args,**kwargs))
    setattr(built,'_cbcc_v0676_strategy_framework_authority',True)
    return built


def wrap_validate_strategy_delivery(fn: Callable[[dict[str,Any]],dict[str,Any]]):
    def validated(strategy: dict[str,Any]):
        result=fn(strategy)
        if not _is_full(strategy): return result
        current=strategy_framework_issues(strategy)
        issues=list(result.get('issues') or []) + current
        dedup=[]
        for item in issues:
            if item not in dedup: dedup.append(item)
        result['issues']=dedup
        result['status']='PASS' if not dedup else 'INCOMPLETE'
        result['strategy_framework_authority_v0676_audit']={'status':'PASS' if not current else 'INCOMPLETE','issues':current}
        return result
    setattr(validated,'_cbcc_v0676_strategy_framework_authority',True)
    return validated
