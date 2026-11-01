from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping
import re

DENSITY_FIELDS=('what','why','evidence','tradeoff','execution','measurement')
RACE_ORDER=('RESEARCH','ACTION','COMMUNICATION','EVALUATION')
CONTENT_FIELDS=(
    'platform','site','surface','content_type','audience','audience_state','purchase_barrier','topic',
    'hook','hook_mechanism','script_structure','visual_form','visual_carrier','proof_evidence','cta','metric',
    'race_stage','culture_adaptation','taboo_stereotype_check',
)
PLATFORM_EXECUTION_FIELDS=(
    'platform_dimensions','duration','cover_first_frame','subtitle_strategy','music_rights',
    'traffic_mechanism','landing_handoff','utm_attribution',
)
RACE_EXECUTION_FIELDS=(
    'stage','objective','key_actions','output','platform','surface','culture_check','kpi','attribution','next_decision',
)
_FULL_DENY={'TASK_SCOPED','TASK_SCOPE','PARTIAL','NOT_FULL','NON_FULL','SCOPED','MINIMAL'}
_FULL_EXACT={'FULL','FULL_PROJECT','FULL_DELIVERY','FULL_PACKAGE','FULL_COMMERCE','FULL_STRATEGY','FULL_WORKSPACE','FULL_E2E','END_TO_END','COMPLETE_DELIVERY','COMPLETE_PROJECT','完整交付','全量交付','完整项目','全量项目'}


def _p(v:Any)->bool:
    return v not in (None,'',[],{})


def _d(v:Any)->dict[str,Any]:
    return deepcopy(dict(v)) if isinstance(v,Mapping) else {}


def _l(v:Any)->list[Any]:
    if v in (None,'',{}): return []
    return list(v) if isinstance(v,(list,tuple,set,frozenset)) else [v]


def _mode_token(v:Any)->str:
    raw=str(v or '').strip()
    if not raw: return ''
    if re.search(r'[\u3400-\u9fff]',raw): return re.sub(r'\s+','',raw)
    return re.sub(r'[^A-Z0-9]+','_',raw.upper()).strip('_')


def _is_full(strategy:Mapping[str,Any], request:Mapping[str,Any]|None=None)->bool:
    merged=_d(strategy)
    if isinstance(request,Mapping):
        for key in ('human_projection','delivery_mode','scope_mode'):
            if key in request: merged[key]=request[key]
    hp=_d(merged.get('human_projection'))
    if hp.get('fixed_human_section_quota') is True: return True
    token=_mode_token(hp.get('mode') or merged.get('delivery_mode') or merged.get('scope_mode') or '')
    if token in _FULL_DENY or token.startswith('NOT_FULL') or token.startswith('NON_FULL'): return False
    if token in _FULL_EXACT: return True
    if token.startswith('FULL_') and any(x in token for x in ('PROJECT','DELIVERY','PACKAGE','COMMERCE','WORKSPACE','STRATEGY','E2E')): return True
    return token in {'完整','全量'}


def _source_index(request:Mapping[str,Any])->dict[str,dict[str,Any]]:
    out={}
    for row in _l(request.get('sources')):
        if not isinstance(row,Mapping): continue
        sid=row.get('source_id') or row.get('id')
        if _p(sid): out[str(sid)]=deepcopy(dict(row))
    return out


def _refs(raw:Mapping[str,Any])->list[str]:
    vals=raw.get('source_refs') or raw.get('source_ids') or raw.get('evidence_refs') or []
    if not _p(vals):
        ev=raw.get('evidence')
        if isinstance(ev,(list,tuple,set,frozenset)):
            vals=[x for x in ev if isinstance(x,str) and str(x).strip()]
    return list(dict.fromkeys(str(x) for x in _l(vals) if _p(x)))


def _lineage(raw:Mapping[str,Any], sources:Mapping[str,Mapping[str,Any]], proof:str, missing_boundary:str)->dict[str,Any]:
    refs=_refs(raw)
    unresolved=[ref for ref in refs if ref not in sources]
    first=_d(sources.get(refs[0])) if refs and refs[0] in sources else {}
    source_type=raw.get('source_type') or first.get('source_type') or first.get('authority') or first.get('kind')
    recency=raw.get('recency') or first.get('as_of') or first.get('published_at') or first.get('date')
    exact_fact=deepcopy(raw.get('exact_fact')) if 'exact_fact' in raw else None
    explicit_assumption=_p(raw.get('assumption_boundary'))
    assumption_boundary=raw.get('assumption_boundary')
    if not refs and not explicit_assumption: assumption_boundary=missing_boundary
    confidence=str(raw.get('confidence') or ('MEDIUM' if refs else 'LOW')).upper()
    interpretation=raw.get('interpretation')
    downstream=deepcopy(raw.get('downstream_use') or [])
    conflict=raw.get('conflict_status') or 'NO_DECLARED_CONFLICT'
    proof_object=raw.get('proof_object') or proof
    out={
        'source_refs':refs,'source_type':source_type,'recency':recency,'exact_fact':exact_fact,
        'interpretation':interpretation,'confidence':confidence,'assumption_boundary':assumption_boundary,
        'downstream_use':downstream,'conflict_status':conflict,'proof_object':proof_object,
        'unresolved_source_refs':unresolved,
    }
    gaps=[]
    if unresolved: gaps.append('unresolved_source_refs')
    if not refs and not explicit_assumption: gaps.append('source_refs_or_explicit_assumption_boundary')
    for key in ('source_type','recency','interpretation','confidence','downstream_use','conflict_status','proof_object'):
        if not _p(out.get(key)): gaps.append(key)
    if not _p(exact_fact) and not explicit_assumption: gaps.append('exact_fact_or_explicit_assumption_boundary')
    out['lineage_gaps']=gaps
    out['lineage_status']='READY' if not gaps else 'TO_VERIFY'
    return out


def _density(raw:Mapping[str,Any])->tuple[str,list[str]]:
    gaps=[key for key in DENSITY_FIELDS if not _p(raw.get(key))]
    return ('READY' if not gaps else 'TO_VERIFY',gaps)


def _normalize_content_row(raw:Any, i:int, sources:Mapping[str,Mapping[str,Any]], race_stages:set[str])->dict[str,Any]:
    src=_d(raw); out=deepcopy(src)
    out.setdefault('row_id',f'CM-{i+1:02d}')
    density_status,density_gaps=_density(src)
    out['density_status']=density_status; out['density_gaps']=density_gaps
    contract_gaps=[k for k in CONTENT_FIELDS if not _p(src.get(k))]
    out['content_contract_gaps']=contract_gaps
    out['content_contract_status']='READY' if not contract_gaps else 'TO_VERIFY'
    exec_gaps=[k for k in PLATFORM_EXECUTION_FIELDS if not _p(src.get(k))]
    out['platform_execution_gaps']=exec_gaps
    out['platform_execution_status']='READY' if not exec_gaps else 'TO_VERIFY'
    stage=str(src.get('race_stage') or '').upper()
    out['race_stage']=stage
    out['race_link_status']='READY' if stage in RACE_ORDER and stage in race_stages else 'TO_VERIFY'
    for key,val in _lineage(src,sources,f'strategy.sections.06_platform_content_matrix[{i}]','CONTENT_MATRIX_DECISION_NOT_SOURCE_BOUND').items():
        out[key]=deepcopy(val)
    out['row_status']='READY' if all(out.get(k)=='READY' for k in ('density_status','content_contract_status','platform_execution_status','race_link_status','lineage_status')) else 'TO_VERIFY'
    return out


def _normalize_race_row(raw:Any, i:int, sources:Mapping[str,Mapping[str,Any]])->dict[str,Any]:
    src=_d(raw); out=deepcopy(src)
    stage=str(src.get('stage') or '').upper(); out['stage']=stage
    density_status,density_gaps=_density(src)
    out['density_status']=density_status; out['density_gaps']=density_gaps
    exec_gaps=[k for k in RACE_EXECUTION_FIELDS if not _p(src.get(k))]
    out['execution_gaps']=exec_gaps
    out['execution_status']='READY' if not exec_gaps else 'TO_VERIFY'
    out['stage_status']='READY' if stage in RACE_ORDER else 'TO_VERIFY'
    for key,val in _lineage(src,sources,f'strategy.sections.07_race_execution_table[{i}]',f'RACE_{stage or i}_DECISION_NOT_SOURCE_BOUND').items():
        out[key]=deepcopy(val)
    out['row_status']='READY' if all(out.get(k)=='READY' for k in ('density_status','execution_status','stage_status','lineage_status')) else 'TO_VERIFY'
    return out


def _request_rows(request:Mapping[str,Any], aliases:tuple[str,...])->tuple[bool,list[Any],str|None]:
    for key in aliases:
        if key in request:
            return True,_l(request.get(key)),key
    return False,[],None


def materialize_content_matrix_race_authority(strategy:Mapping[str,Any], request:Mapping[str,Any]|None=None)->dict[str,Any]:
    out=deepcopy(dict(strategy)); req=_d(request)
    if not _is_full(out,req): return out
    sections=_d(out.get('sections'))
    explicit_matrix,matrix_rows,matrix_key=_request_rows(req,('platform_content_matrix','content_matrix','platform_content_matrix_rows'))
    explicit_race,race_rows,race_key=_request_rows(req,('race_execution_table','race_plan','race_execution_rows'))
    if not explicit_matrix: matrix_rows=_l(sections.get('06_platform_content_matrix'))
    if not explicit_race: race_rows=_l(sections.get('07_race_execution_table'))
    sources=_source_index(req)
    normalized_race=[_normalize_race_row(row,i,sources) for i,row in enumerate(race_rows) if isinstance(row,Mapping)]
    race_stages={str(row.get('stage') or '').upper() for row in normalized_race}
    normalized_matrix=[_normalize_content_row(row,i,sources,race_stages) for i,row in enumerate(matrix_rows) if isinstance(row,Mapping)]
    sections['06_platform_content_matrix']=normalized_matrix
    sections['07_race_execution_table']=normalized_race
    out['sections']=sections
    order=[str(row.get('stage') or '').upper() for row in normalized_race]
    ready=(
        bool(normalized_matrix)
        and order==list(RACE_ORDER)
        and all(row.get('row_status')=='READY' for row in normalized_matrix)
        and all(row.get('row_status')=='READY' for row in normalized_race)
    )
    out['content_matrix_race_authority_v0676']={
        'schema':'cbcc-content-matrix-race-authority-v0.6.76',
        'status':'READY' if ready else 'TO_VERIFY',
        'asset_dependency':'NOT_REQUIRED_FOR_PHASE2_BUSINESS_AUTHORITY',
        'content_matrix':deepcopy(normalized_matrix),
        'race':deepcopy(normalized_race),
        'race_order':list(RACE_ORDER),
        'required_density_fields':list(DENSITY_FIELDS),
        'required_content_fields':list(CONTENT_FIELDS),
        'required_platform_execution_fields':list(PLATFORM_EXECUTION_FIELDS),
        'required_race_execution_fields':list(RACE_EXECUTION_FIELDS),
        'source_mode':{
            'content_matrix':'EXPLICIT_REQUEST' if explicit_matrix else 'EXISTING_STRATEGY_SECTION',
            'content_matrix_key':matrix_key,
            'race':'EXPLICIT_REQUEST' if explicit_race else 'EXISTING_STRATEGY_SECTION',
            'race_key':race_key,
        },
        'principle':'Phase 2 Content Matrix/RACE is a first-class commercial execution object authored before asset/prompt work. Every major row requires business-decision density, source/assumption lineage, platform-native execution, culture guard, valid RACE linkage and attribution; runtime never invents missing hooks, scripts, rights, dimensions, traffic or attribution.',
    }
    out['content_matrix_race_authority_v0676']['issues']=content_matrix_race_issues(out)
    return out


def content_matrix_race_issues(strategy:Mapping[str,Any])->list[dict[str,Any]]:
    auth=_d(strategy.get('content_matrix_race_authority_v0676'))
    if not auth:
        if not _is_full(strategy): return []
        return [{'code':'FULL_CONTENT_MATRIX_RACE_AUTHORITY_MISSING_V0676'}]
    issues=[]
    matrix=[x for x in _l(auth.get('content_matrix')) if isinstance(x,Mapping)]
    race=[x for x in _l(auth.get('race')) if isinstance(x,Mapping)]
    if not matrix: issues.append({'code':'FULL_CONTENT_MATRIX_EMPTY_V0676'})
    for i,row in enumerate(matrix):
        if row.get('content_contract_status')!='READY':
            issues.append({'code':'FULL_CONTENT_MATRIX_BUSINESS_OBJECT_INCOMPLETE_V0676','row':i,'fields':row.get('content_contract_gaps') or []})
        if row.get('density_status')!='READY':
            issues.append({'code':'FULL_CONTENT_MATRIX_BUSINESS_DENSITY_INCOMPLETE_V0676','row':i,'fields':row.get('density_gaps') or list(DENSITY_FIELDS)})
        if row.get('platform_execution_status')!='READY':
            issues.append({'code':'FULL_CONTENT_MATRIX_PLATFORM_EXECUTION_INCOMPLETE_V0676','row':i,'fields':row.get('platform_execution_gaps') or list(PLATFORM_EXECUTION_FIELDS)})
        if row.get('race_link_status')!='READY':
            issues.append({'code':'FULL_CONTENT_MATRIX_RACE_LINK_INVALID_V0676','row':i,'race_stage':row.get('race_stage')})
        if row.get('lineage_status')!='READY':
            issues.append({'code':'FULL_CONTENT_MATRIX_LINEAGE_INCOMPLETE_V0676','row':i,'fields':row.get('lineage_gaps') or []})
    order=[str(x.get('stage') or '').upper() for x in race]
    if order!=list(RACE_ORDER):
        issues.append({'code':'FULL_RACE_EXECUTION_ORDER_INVALID_V0676','actual':order,'expected':list(RACE_ORDER)})
    for i,row in enumerate(race):
        if row.get('density_status')!='READY':
            issues.append({'code':'FULL_RACE_BUSINESS_DENSITY_INCOMPLETE_V0676','row':i,'stage':row.get('stage'),'fields':row.get('density_gaps') or list(DENSITY_FIELDS)})
        if row.get('execution_status')!='READY':
            issues.append({'code':'FULL_RACE_EXECUTION_INCOMPLETE_V0676','row':i,'stage':row.get('stage'),'fields':row.get('execution_gaps') or list(RACE_EXECUTION_FIELDS)})
        if row.get('lineage_status')!='READY':
            issues.append({'code':'FULL_RACE_LINEAGE_INCOMPLETE_V0676','row':i,'stage':row.get('stage'),'fields':row.get('lineage_gaps') or []})
    dedup=[]
    for item in issues:
        if item not in dedup: dedup.append(item)
    return dedup


def wrap_build_master_strategy(fn:Callable[...,dict[str,Any]]):
    def built(request:dict[str,Any], *args:Any, **kwargs:Any):
        return materialize_content_matrix_race_authority(fn(request,*args,**kwargs),request)
    setattr(built,'_cbcc_v0676_content_matrix_race_authority',True)
    return built


def wrap_validate_strategy_delivery(fn:Callable[[dict[str,Any]],dict[str,Any]]):
    def validated(strategy:dict[str,Any]):
        result=fn(strategy)
        if not _d(strategy.get('content_matrix_race_authority_v0676')) and not _is_full(strategy): return result
        current=content_matrix_race_issues(strategy)
        issues=list(result.get('issues') or [])+current
        dedup=[]
        for item in issues:
            if item not in dedup: dedup.append(item)
        result['issues']=dedup
        result['status']='PASS' if not dedup else 'INCOMPLETE'
        result['content_matrix_race_authority_v0676_audit']={'status':'PASS' if not current else 'INCOMPLETE','issues':current}
        return result
    setattr(validated,'_cbcc_v0676_content_matrix_race_authority',True)
    return validated