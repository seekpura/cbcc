from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping
import re

AXES=('platform','region','audience','race_ethnicity_culture')
DENSITY_FIELDS=('what','why','evidence','tradeoff','execution','measurement')
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
    if re.search(r'[\u3400-\u9fff]',raw): return re.sub(r'\s+','',raw)
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

def _nested(v: Any, key: str)->Any:
    if isinstance(v,Mapping): return v.get(key)
    return None

def _decision_density(row: Mapping[str,Any])->dict[str,Any]:
    dv=_d(row.get('decision_value'))
    why_obj=dv.get('why') if isinstance(dv.get('why'),Mapping) else {}
    why_val=row.get('why') or (_nested(dv.get('why'),'why') if isinstance(dv.get('why'),Mapping) else dv.get('why'))
    evidence=row.get('evidence') or dv.get('evidence') or dv.get('evidence_refs') or dv.get('source_refs') or _nested(why_obj,'evidence')
    return {
        'what': row.get('what') or row.get('decision'),
        'why': why_val,
        'evidence': deepcopy(evidence) if _p(evidence) else [],
        'tradeoff': row.get('tradeoff') or dv.get('tradeoff') or _nested(why_obj,'tradeoff'),
        'execution': row.get('execution') or dv.get('execution') or _nested(why_obj,'execution'),
        'measurement': row.get('measurement') or dv.get('measurement') or _nested(why_obj,'measurement'),
    }

def _axis(axis: str, decision: str, raw: Any)->dict[str,Any]:
    old=_d(raw)
    if not old:
        return {
            'status':'TO_VERIFY',
            'what':None,'why':None,'evidence':[],'tradeoff':None,'execution':None,'measurement':None,
            'basis':None,
            'assumption_boundary':'DECISION_SPECIFIC_CONTEXT_NOT_AUTHORED',
            'decision_specificity':'MISSING',
            'proof_object':f'major_decision_context_why:{decision}:{axis}',
        }
    status=str(old.get('status') or 'TO_VERIFY').upper()
    basis=old.get('basis')
    evidence=old.get('evidence') or old.get('evidence_refs') or old.get('source_refs') or []
    inherited = status=='INHERITED_PROJECT_CONTEXT_REQUIRES_DECISION_CHECK' or str(basis or '').lower()=='project_context'
    out=deepcopy(old)
    out['status']=status
    out.setdefault('what',None)
    out.setdefault('why',None)
    out['evidence']=deepcopy(evidence) if _p(evidence) else []
    out.setdefault('tradeoff',None)
    out.setdefault('execution',None)
    out.setdefault('measurement',None)
    out.setdefault('basis',basis)
    out.setdefault('assumption_boundary', 'PROJECT_CONTEXT_IS_NOT_DECISION_SPECIFIC_CAUSAL_EVIDENCE' if inherited else ('DECISION_SPECIFIC_CONTEXT_TO_VERIFY' if status.startswith('TO_VERIFY') else None))
    out['decision_specificity']='REQUIRES_DECISION_SPECIFIC_CHECK' if inherited else ('AUTHORED' if all(_p(out.get(k)) for k in DENSITY_FIELDS) else 'INCOMPLETE')
    out.setdefault('proof_object',f'major_decision_context_why:{decision}:{axis}')
    return out

def materialize_context_why_authority(strategy: Mapping[str,Any])->dict[str,Any]:
    out=deepcopy(dict(strategy))
    if not _is_full(out): return out
    sections=out.setdefault('sections',{})
    core=_d(sections.get('04_marketing_core_strategy'))
    rows=[]
    for raw in _l(core.get('major_decision_context_why')):
        if not isinstance(raw,Mapping): continue
        row=deepcopy(dict(raw))
        decision=str(row.get('decision') or row.get('what') or 'UNNAMED_MAJOR_DECISION')
        density=_decision_density(row)
        for key,val in density.items():
            if not _p(row.get(key)): row[key]=deepcopy(val)
        ctx=_d(row.get('context_why'))
        row['context_why']={axis:_axis(axis,decision,ctx.get(axis)) for axis in AXES}
        row_missing=[k for k in DENSITY_FIELDS if not _p(row.get(k))]
        axis_incomplete=[]
        for axis in AXES:
            a=row['context_why'][axis]
            missing=[k for k in DENSITY_FIELDS if not _p(a.get(k))]
            if missing or a.get('decision_specificity')=='REQUIRES_DECISION_SPECIFIC_CHECK':
                axis_incomplete.append({'axis':axis,'missing':missing,'decision_specificity':a.get('decision_specificity')})
        row['density_status']='READY' if not row_missing and not axis_incomplete else 'TO_VERIFY'
        row['density_gaps']={'decision':row_missing,'context_axes':axis_incomplete}
        row['authority']='REQ-010/REQ-054 Platform×Region×Audience×Culture WHY'
        rows.append(row)
    core['major_decision_context_why']=rows
    sections['04_marketing_core_strategy']=core
    out['sections']=sections
    out['context_why_authority_v0676']={
        'status':'READY' if rows and all(r.get('density_status')=='READY' for r in rows) else 'TO_VERIFY',
        'required_axes':list(AXES),
        'required_density_fields':list(DENSITY_FIELDS),
        'principle':'Project-level context may inform a decision but cannot substitute for decision-specific causal WHY. Unknown external facts remain TO_VERIFY rather than being invented.',
    }
    return out

def context_why_issues(strategy: Mapping[str,Any])->list[dict[str,Any]]:
    if not _is_full(strategy): return []
    core=_d(_d(strategy.get('sections')).get('04_marketing_core_strategy'))
    rows=[x for x in _l(core.get('major_decision_context_why')) if isinstance(x,Mapping)]
    if not rows: return [{'code':'FULL_MAJOR_DECISION_CONTEXT_WHY_MISSING_V0676'}]
    issues=[]
    for i,row in enumerate(rows):
        missing=[k for k in DENSITY_FIELDS if not _p(row.get(k))]
        if missing:
            issues.append({'code':'FULL_MAJOR_DECISION_DENSITY_INCOMPLETE_V0676','row':i,'fields':missing})
        ctx=_d(row.get('context_why'))
        for axis in AXES:
            a=_d(ctx.get(axis))
            miss=[k for k in DENSITY_FIELDS if not _p(a.get(k))]
            inherited=a.get('decision_specificity')=='REQUIRES_DECISION_SPECIFIC_CHECK'
            if miss or inherited:
                issues.append({'code':'FULL_MAJOR_DECISION_CONTEXT_AXIS_DENSITY_INCOMPLETE_V0676','row':i,'axis':axis,'fields':miss,'decision_specificity':a.get('decision_specificity') or 'MISSING'})
    return issues

def wrap_build_master_strategy(fn: Callable[...,dict[str,Any]]):
    def built(request: dict[str,Any], *args: Any, **kwargs: Any):
        return materialize_context_why_authority(fn(request,*args,**kwargs))
    setattr(built,'_cbcc_v0676_context_why_authority',True)
    return built

def wrap_validate_strategy_delivery(fn: Callable[[dict[str,Any]],dict[str,Any]]):
    def validated(strategy: dict[str,Any]):
        result=fn(strategy)
        if not _is_full(strategy): return result
        current=context_why_issues(strategy)
        issues=list(result.get('issues') or []) + current
        seen=[]
        for item in issues:
            if item not in seen: seen.append(item)
        result['issues']=seen
        result['status']='PASS' if not seen else 'INCOMPLETE'
        result['context_why_authority_v0676_audit']={'status':'PASS' if not current else 'INCOMPLETE','issues':current}
        return result
    setattr(validated,'_cbcc_v0676_context_why_authority',True)
    return validated
