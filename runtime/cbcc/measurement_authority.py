from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping
import re

DENSITY_FIELDS=('what','why','evidence','tradeoff','execution','measurement')
MEASUREMENT_BUSINESS_FIELDS=(
    'business_question','decision_object','hypothesis','primary_metric','metric_definition','desired_direction',
    'baseline','target_or_mde','metric_source_ref','attribution_method','observation_window','analysis_unit',
    'guardrails','learning_handoff','next_decision',
)
AB_TEST_FIELDS=(
    'test_type','changed_variable','held_constants','variants','deployment_pool','randomization_unit',
    'sample_size_rule','duration_or_stop_rule','sequential_monitoring_policy','success_rule','failure_rule',
)
PRIORITY_FIELDS=('priority','status','action','decision_ref','next_decision')
NEXT_INPUT_FIELDS=('input_id','status','decision_ref','exact_missing_input','source_or_owner','downstream_unblock','decision_trigger')
PRIORITY_ORDER=('P0','P1','P2')
_FULL_DENY={'TASK_SCOPED','TASK_SCOPE','PARTIAL','NOT_FULL','NON_FULL','SCOPED','MINIMAL'}
_FULL_EXACT={'FULL','FULL_PROJECT','FULL_DELIVERY','FULL_PACKAGE','FULL_COMMERCE','FULL_STRATEGY','FULL_WORKSPACE','FULL_E2E','END_TO_END','COMPLETE_DELIVERY','COMPLETE_PROJECT','完整交付','全量交付','完整项目','全量项目'}


def _p(v:Any)->bool: return v not in (None,'',[],{})
def _d(v:Any)->dict[str,Any]: return deepcopy(dict(v)) if isinstance(v,Mapping) else {}
def _l(v:Any)->list[Any]:
    if v in (None,'',{}): return []
    return list(v) if isinstance(v,(list,tuple,set,frozenset)) else [v]

def _mode_token(v:Any)->str:
    raw=str(v or '').strip()
    if not raw:return ''
    if re.search(r'[\u3400-\u9fff]',raw):return re.sub(r'\s+','',raw)
    return re.sub(r'[^A-Z0-9]+','_',raw.upper()).strip('_')

def _is_full(strategy:Mapping[str,Any],request:Mapping[str,Any]|None=None)->bool:
    merged=_d(strategy)
    if isinstance(request,Mapping):
        for key in ('human_projection','delivery_mode','scope_mode'):
            if key in request:merged[key]=request[key]
    hp=_d(merged.get('human_projection'))
    if hp.get('fixed_human_section_quota') is True:return True
    token=_mode_token(hp.get('mode') or merged.get('delivery_mode') or merged.get('scope_mode') or '')
    if token in _FULL_DENY or token.startswith('NOT_FULL') or token.startswith('NON_FULL'):return False
    if token in _FULL_EXACT:return True
    if token.startswith('FULL_') and any(x in token for x in ('PROJECT','DELIVERY','PACKAGE','COMMERCE','WORKSPACE','STRATEGY','E2E')):return True
    return token in {'完整','全量'}

def _source_index(request:Mapping[str,Any])->dict[str,dict[str,Any]]:
    out={}
    for row in _l(request.get('sources')):
        if not isinstance(row,Mapping):continue
        sid=row.get('source_id') or row.get('id')
        if _p(sid):out[str(sid)]=deepcopy(dict(row))
    return out

def _refs(raw:Mapping[str,Any])->list[str]:
    vals=raw.get('source_refs') or raw.get('source_ids') or raw.get('evidence_refs') or []
    if not _p(vals):
        ev=raw.get('evidence')
        if isinstance(ev,(list,tuple,set,frozenset)):
            vals=[x for x in ev if isinstance(x,str) and str(x).strip()]
    return list(dict.fromkeys(str(x) for x in _l(vals) if _p(x)))

def _lineage(raw:Mapping[str,Any],sources:Mapping[str,Mapping[str,Any]],proof:str,missing_boundary:str)->dict[str,Any]:
    refs=_refs(raw); unresolved=[x for x in refs if x not in sources]
    first=_d(sources.get(refs[0])) if refs and refs[0] in sources else {}
    explicit_assumption=_p(raw.get('assumption_boundary'))
    exact_fact=deepcopy(raw.get('exact_fact')) if 'exact_fact' in raw else None
    out={
        'source_refs':refs,
        'source_type':raw.get('source_type') or first.get('source_type') or first.get('authority') or first.get('kind'),
        'recency':raw.get('recency') or first.get('as_of') or first.get('published_at') or first.get('date'),
        'exact_fact':exact_fact,
        'interpretation':raw.get('interpretation'),
        'confidence':str(raw.get('confidence') or ('MEDIUM' if refs else 'LOW')).upper(),
        'assumption_boundary':raw.get('assumption_boundary') if explicit_assumption else (missing_boundary if not refs else None),
        'downstream_use':deepcopy(raw.get('downstream_use') or []),
        'conflict_status':raw.get('conflict_status') or 'NO_DECLARED_CONFLICT',
        'proof_object':raw.get('proof_object') or proof,
        'unresolved_source_refs':unresolved,
    }
    gaps=[]
    if unresolved:gaps.append('unresolved_source_refs')
    if not refs and not explicit_assumption:gaps.append('source_refs_or_explicit_assumption_boundary')
    for key in ('source_type','recency','interpretation','confidence','downstream_use','conflict_status','proof_object'):
        if not _p(out.get(key)):gaps.append(key)
    if not _p(exact_fact) and not explicit_assumption:gaps.append('exact_fact_or_explicit_assumption_boundary')
    out['lineage_gaps']=gaps; out['lineage_status']='READY' if not gaps else 'TO_VERIFY'
    return out

def _density(raw:Mapping[str,Any])->tuple[str,list[str]]:
    gaps=[k for k in DENSITY_FIELDS if not _p(raw.get(k))]
    return ('READY' if not gaps else 'TO_VERIFY',gaps)

def _measurement_plan(request:Mapping[str,Any])->dict[str,Any]:
    for key in ('measurement_plan','measurement_authority','measurement'):
        if isinstance(request.get(key),Mapping):return _d(request.get(key))
    return {}

def _normalize_measurement(raw:Any,i:int,sources:Mapping[str,Mapping[str,Any]])->dict[str,Any]:
    src=_d(raw); out=deepcopy(src); out.setdefault('measurement_id',f'M-{i+1:02d}')
    gaps=[k for k in MEASUREMENT_BUSINESS_FIELDS if not _p(src.get(k))]
    out['business_contract_gaps']=gaps; out['business_contract_status']='READY' if not gaps else 'TO_VERIFY'
    dg=_density(src); out['density_status']=dg[0]; out['density_gaps']=dg[1]
    for k,v in _lineage(src,sources,f'measurement_authority.measurement_rows[{i}]','MEASUREMENT_DECISION_NOT_SOURCE_BOUND').items():out[k]=deepcopy(v)
    metric_ref=str(src.get('metric_source_ref') or '')
    unresolved_metric=[] if metric_ref and metric_ref in sources else ([metric_ref] if metric_ref else ['metric_source_ref'])
    out['unresolved_metric_source_refs']=unresolved_metric
    out['metric_source_status']='READY' if not unresolved_metric else 'TO_VERIFY'
    test_gaps=[k for k in AB_TEST_FIELDS if not _p(src.get(k))]
    changed=str(src.get('changed_variable') or '').upper()
    held={str(x).upper() for x in _l(src.get('held_constants')) if _p(x)}
    variants=[str(x) for x in _l(src.get('variants')) if _p(x)]
    if changed and changed in held:test_gaps.append('changed_variable_is_held_constant')
    if len(set(variants))<2:test_gaps.append('at_least_two_distinct_variants')
    if str(src.get('test_type') or '').upper() not in {'A_B','AB','A/B','MULTIVARIATE'}:test_gaps.append('test_type')
    out['test_contract_gaps']=list(dict.fromkeys(test_gaps)); out['test_contract_status']='READY' if not out['test_contract_gaps'] else 'TO_VERIFY'
    out['row_status']='READY' if all(out.get(k)=='READY' for k in ('business_contract_status','density_status','lineage_status','metric_source_status','test_contract_status')) else 'TO_VERIFY'
    return out

def _normalize_priority(raw:Any,i:int,sources:Mapping[str,Mapping[str,Any]],measurement_ids:set[str])->dict[str,Any]:
    src=_d(raw); out=deepcopy(src); out['priority']=str(src.get('priority') or '').upper(); out['status']=str(src.get('status') or '').upper()
    gaps=[k for k in PRIORITY_FIELDS if not _p(out.get(k))]
    if out['status'] not in {'ACTIVE','NOT_NEEDED','HOLD'}:gaps.append('status')
    dg=_density(src); out['density_status']=dg[0]; out['density_gaps']=dg[1]
    for k,v in _lineage(src,sources,f'measurement_authority.priorities[{i}]','MEASUREMENT_PRIORITY_NOT_SOURCE_BOUND').items():out[k]=deepcopy(v)
    decision_ref=str(src.get('decision_ref') or '')
    out['decision_link_status']='READY' if decision_ref in measurement_ids else 'TO_VERIFY'
    out['decision_link_gaps']=[] if out['decision_link_status']=='READY' else ['decision_ref_not_found']
    out['priority_contract_gaps']=list(dict.fromkeys(gaps))
    out['priority_contract_status']='READY' if not out['priority_contract_gaps'] and out['priority'] in PRIORITY_ORDER else 'TO_VERIFY'
    out['row_status']='READY' if all(out.get(k)=='READY' for k in ('priority_contract_status','density_status','lineage_status','decision_link_status')) else 'TO_VERIFY'
    return out

def _normalize_next_input(raw:Any,i:int,sources:Mapping[str,Mapping[str,Any]],measurement_ids:set[str])->dict[str,Any]:
    src=_d(raw); out=deepcopy(src); out.setdefault('input_id',f'NEXT-{i+1:02d}')
    gaps=[k for k in NEXT_INPUT_FIELDS if not _p(out.get(k))]
    dg=_density(src); out['density_status']=dg[0]; out['density_gaps']=dg[1]
    for k,v in _lineage(src,sources,f'measurement_authority.next_inputs[{i}]','MEASUREMENT_NEXT_INPUT_NOT_SOURCE_BOUND').items():out[k]=deepcopy(v)
    decision_ref=str(src.get('decision_ref') or '')
    out['decision_link_status']='READY' if decision_ref in measurement_ids else 'TO_VERIFY'
    out['decision_link_gaps']=[] if out['decision_link_status']=='READY' else ['decision_ref_not_found']
    exact=str(src.get('exact_missing_input') or '').strip()
    generic=re.sub(r'[^a-z0-9\u3400-\u9fff]+',' ',exact.lower()).strip()
    generic_tokens={'need more data','more data','additional data','need data','data needed','更多数据','需要更多数据','补充数据'}
    out['exact_input_status']='READY' if exact and generic not in generic_tokens and len(exact)>=12 else 'TO_VERIFY'
    if out['exact_input_status']!='READY':gaps.append('exact_missing_input_not_specific')
    out['next_input_contract_gaps']=list(dict.fromkeys(gaps))
    out['next_input_contract_status']='READY' if not out['next_input_contract_gaps'] else 'TO_VERIFY'
    out['row_status']='READY' if all(out.get(k)=='READY' for k in ('next_input_contract_status','density_status','lineage_status','decision_link_status','exact_input_status')) else 'TO_VERIFY'
    return out


def _ab_projection(row:Mapping[str,Any])->dict[str,Any]:
    return {
        'id':row.get('measurement_id'),
        'hypothesis':row.get('hypothesis'),
        'variable':row.get('changed_variable'),
        'variants':deepcopy(row.get('variants') or []),
        'hold_constant':deepcopy(row.get('held_constants') or []),
        'deployment_pool':row.get('deployment_pool'),
        'metric':row.get('primary_metric'),
        'guardrail':deepcopy(row.get('guardrails') or []),
        'next_decision_rule':row.get('next_decision'),
        'measurement_authority_ref':row.get('measurement_id'),
    }

def _priority_projection(row:Mapping[str,Any])->dict[str,Any]:
    out=deepcopy(dict(row))
    out.setdefault('measure',out.get('measurement'))
    return out

def measurement_issues(strategy:Mapping[str,Any])->list[dict[str,Any]]:
    auth=_d(strategy.get('measurement_authority_v0676'))
    if not auth:
        if not _is_full(strategy):return []
        return [{'code':'FULL_MEASUREMENT_AUTHORITY_MISSING_V0676'}]
    issues=[]
    rows=[x for x in _l(auth.get('measurement_rows')) if isinstance(x,Mapping)]
    if not rows:issues.append({'code':'FULL_MEASUREMENT_DECISION_MISSING_V0676'})
    for i,row in enumerate(rows):
        if row.get('business_contract_status')!='READY':issues.append({'code':'FULL_MEASUREMENT_BUSINESS_OBJECT_INCOMPLETE_V0676','row':i,'fields':row.get('business_contract_gaps') or []})
        if row.get('density_status')!='READY':issues.append({'code':'FULL_MEASUREMENT_DECISION_DENSITY_INCOMPLETE_V0676','row':i,'fields':row.get('density_gaps') or []})
        if row.get('lineage_status')!='READY':issues.append({'code':'FULL_MEASUREMENT_LINEAGE_INCOMPLETE_V0676','row':i,'fields':row.get('lineage_gaps') or []})
        if row.get('metric_source_status')!='READY':issues.append({'code':'FULL_MEASUREMENT_METRIC_SOURCE_INCOMPLETE_V0676','row':i,'refs':row.get('unresolved_metric_source_refs') or []})
        if row.get('test_contract_status')!='READY':issues.append({'code':'FULL_MEASUREMENT_AB_TEST_CONTRACT_INVALID_V0676','row':i,'fields':row.get('test_contract_gaps') or []})
    if auth.get('measurement_id_uniqueness_status')!='READY':issues.append({'code':'FULL_MEASUREMENT_ID_DUPLICATE_V0676','duplicates':auth.get('duplicate_measurement_ids') or []})
    if auth.get('priority_status')!='READY':issues.append({'code':'FULL_MEASUREMENT_PRIORITY_PLAN_INCOMPLETE_V0676','actual':auth.get('priority_order') or [],'expected':list(PRIORITY_ORDER)})
    if auth.get('next_input_status')!='READY':issues.append({'code':'FULL_MEASUREMENT_NEXT_INPUT_PLAN_INCOMPLETE_V0676'})
    dedup=[]
    for item in issues:
        if item not in dedup:dedup.append(item)
    return dedup

def materialize_measurement_authority(strategy:Mapping[str,Any],request:Mapping[str,Any]|None=None,experiment:Mapping[str,Any]|None=None)->dict[str,Any]:
    out=deepcopy(dict(strategy)); req=_d(request)
    if not _is_full(out,req):return out
    sections=_d(out.get('sections')); s9=_d(sections.get('09_risk_measurement_priority_next_steps'))
    legacy={'ab_test_hypotheses':deepcopy(s9.get('ab_test_hypotheses') or []),'priority_plan':deepcopy(s9.get('priority_plan') or {}),'experiment':deepcopy(s9.get('experiment'))}
    plan=_measurement_plan(req); sources=_source_index(req)
    rows=[_normalize_measurement(x,i,sources) for i,x in enumerate(_l(plan.get('rows') or plan.get('measurement_rows'))) if isinstance(x,Mapping)]
    measurement_id_list=[str(x.get('measurement_id')) for x in rows if _p(x.get('measurement_id'))]
    measurement_ids=set(measurement_id_list)
    duplicate_measurement_ids=sorted({x for x in measurement_id_list if measurement_id_list.count(x)>1})
    measurement_id_uniqueness_status='READY' if not duplicate_measurement_ids else 'TO_VERIFY'
    priorities=[_normalize_priority(x,i,sources,measurement_ids) for i,x in enumerate(_l(plan.get('priorities') or plan.get('priority_rows'))) if isinstance(x,Mapping)]
    next_inputs=[_normalize_next_input(x,i,sources,measurement_ids) for i,x in enumerate(_l(plan.get('next_inputs') or plan.get('next_input_plan'))) if isinstance(x,Mapping)]
    priority_order=[str(x.get('priority') or '').upper() for x in priorities]
    priority_status='READY' if priority_order==list(PRIORITY_ORDER) and all(x.get('row_status')=='READY' for x in priorities) else 'TO_VERIFY'
    next_input_status='READY' if bool(next_inputs) and all(x.get('row_status')=='READY' for x in next_inputs) else 'TO_VERIFY'
    exp=deepcopy(dict(experiment)) if isinstance(experiment,Mapping) else deepcopy(s9.get('experiment'))
    s9['legacy_advisory_v0676']=legacy
    s9['measurement_plan']=deepcopy(rows)
    s9['ab_test_hypotheses']=[_ab_projection(x) for x in rows]
    s9['priority_plan']={p:[_priority_projection(x) for x in priorities if x.get('priority')==p] for p in PRIORITY_ORDER}
    s9['priority_plan']['next_information_needed']=[x.get('exact_missing_input') for x in next_inputs if _p(x.get('exact_missing_input'))]
    s9['next_input_plan']=deepcopy(next_inputs)
    if exp is not None:s9['experiment']=deepcopy(exp)
    sections['09_risk_measurement_priority_next_steps']=s9; out['sections']=sections
    auth={
        'schema':'cbcc-measurement-authority-v0.6.76','status':'TO_VERIFY',
        'asset_dependency':'NOT_REQUIRED_FOR_PHASE2_BUSINESS_AUTHORITY',
        'production_learning_dependency':'NOT_REQUIRED_FOR_PHASE2_MEASUREMENT_PLAN_AUTHORITY',
        'measurement_rows':rows,
        'measurement_id_uniqueness_status':measurement_id_uniqueness_status,
        'duplicate_measurement_ids':duplicate_measurement_ids,
        'priorities':priorities,'priority_order':priority_order,'priority_status':priority_status,
        'next_inputs':next_inputs,'next_input_status':next_input_status,
        'experiment_evidence':exp,'experiment_calculator_authority':'runtime/cbcc/tools/experiment.py','experiment_decision_does_not_author_measurement_plan':True,
        'legacy_strategy_advisory':legacy,
        'boundaries':{
            'post_production_learning_status':'DEFERRED_TO_LEARNING_LOOP_WHEN_REAL_RESULTS_EXIST',
            'human_workspace_projection':'PENDING_PHASE6',
            'measurement_plan_completion_is_not_experiment_success':True,
            'real_k01_full':'PENDING_PHASE10','built_plugin_readback':'PENDING_PHASE11','provider_actual_output':'E2E_PENDING',
        },
        'principle':'Measurement is a first-class business authority. It defines the decision question, metric truth, baseline/target, isolated test, P0/P1/P2 priorities, stop/success/failure rules, exact next input and learning handoff. Deterministic experiment statistics remain in tools.experiment and observed results never author missing business decisions.',
    }
    out['measurement_authority_v0676']=auth
    auth['issues']=measurement_issues(out); auth['status']='READY' if not auth['issues'] else 'TO_VERIFY'
    return out

def wrap_build_master_strategy(fn:Callable[...,dict[str,Any]]):
    def built(request:dict[str,Any],*args:Any,**kwargs:Any):
        strategy=fn(request,*args,**kwargs)
        exp=kwargs.get('experiment')
        if exp is None:
            exp=_d(_d(strategy.get('sections')).get('09_risk_measurement_priority_next_steps')).get('experiment')
        return materialize_measurement_authority(strategy,request,exp)
    setattr(built,'_cbcc_v0676_measurement_authority',True)
    return built

def wrap_validate_strategy_delivery(fn:Callable[[dict[str,Any]],dict[str,Any]]):
    def validated(strategy:dict[str,Any]):
        result=fn(strategy)
        if not _d(strategy.get('measurement_authority_v0676')) and not _is_full(strategy):return result
        current=measurement_issues(strategy)
        issues=list(result.get('issues') or [])+current
        dedup=[]
        for item in issues:
            if item not in dedup:dedup.append(item)
        result['issues']=dedup; result['status']='PASS' if not dedup else 'INCOMPLETE'
        result['measurement_authority_v0676_audit']={'status':'PASS' if not current else 'INCOMPLETE','issues':current}
        return result
    setattr(validated,'_cbcc_v0676_measurement_authority',True)
    return validated
