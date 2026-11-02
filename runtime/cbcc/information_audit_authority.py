from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any, Callable, Mapping, Sequence
import json
import re

SCHEMA = 'cbcc-information-audit-authority-v1'
DEFAULT_QUESTION_LIMIT = 10
DENSITY_FIELDS = ('what','why','evidence','tradeoff','execution','measurement')
LINEAGE_FIELDS = ('source_refs','source_type','recency','exact_fact','interpretation','confidence','assumption_boundary','downstream_use','conflict_status','proof_object')
_FULL_DENY = {'TASK_SCOPED','TASK_SCOPE','PARTIAL','NOT_FULL','NON_FULL','SCOPED','MINIMAL'}
_FULL_EXACT = {'FULL','FULL_PROJECT','FULL_DELIVERY','FULL_PACKAGE','FULL_COMMERCE','FULL_STRATEGY','FULL_WORKSPACE','FULL_E2E','END_TO_END','COMPLETE_DELIVERY','COMPLETE_PROJECT','完整交付','全量交付','完整项目','全量项目'}


def _p(v: Any) -> bool: return v not in (None,'',[],{})
def _l(v: Any) -> list[Any]:
    if v in (None,'',{}): return []
    return list(v) if isinstance(v,(list,tuple,set,frozenset)) else [v]
def _d(v: Any) -> dict[str,Any]: return dict(v) if isinstance(v,Mapping) else {}
def _hash(v: Any) -> str: return sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()


def _mode_token(v: Any) -> str:
    raw=str(v or '').strip()
    if not raw: return ''
    if re.search(r'[\u3400-\u9fff]',raw): return re.sub(r'\s+','',raw)
    return re.sub(r'[^A-Z0-9]+','_',raw.upper()).strip('_')


def _is_full(strategy: Mapping[str,Any]) -> bool:
    # Reuse the mature v0.6.74 FULL semantics inside the real package; keep an identical standalone
    # fallback so the authority module stays directly unit-testable without importing the whole package.
    try:
        from .v0674_regression_closure import is_full_strategy
        return bool(is_full_strategy(strategy))
    except (ImportError, ValueError):
        hp=_d(strategy.get('human_projection'))
        if hp.get('fixed_human_section_quota') is True: return True
        token=_mode_token(hp.get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '')
        if token in _FULL_DENY or token.startswith('NOT_FULL') or token.startswith('NON_FULL'): return False
        if token in _FULL_EXACT: return True
        if token.startswith('FULL_') and any(x in token for x in ('PROJECT','DELIVERY','PACKAGE','COMMERCE','WORKSPACE','STRATEGY','E2E')): return True
        return token in {'完整','全量'}


def _source_index(sources: Sequence[Mapping[str,Any]]|None) -> dict[str,dict[str,Any]]:
    return {str(x['source_id']):deepcopy(dict(x)) for x in (sources or []) if isinstance(x,Mapping) and _p(x.get('source_id'))}


def _refs(raw: Mapping[str,Any]) -> list[str]:
    values=raw.get('source_refs') or raw.get('source_ids') or raw.get('evidence_refs') or raw.get('evidence_source_ids') or []
    if isinstance(raw.get('evidence'),list): values=[*_l(values),*[x for x in raw['evidence'] if isinstance(x,str)]]
    return list(dict.fromkeys(str(x) for x in _l(values) if _p(x)))


def _lineage(refs: Sequence[str], source_index: Mapping[str,Mapping[str,Any]]) -> dict[str,Any]:
    ids=list(dict.fromkeys(str(x) for x in refs if _p(x)))
    cards=[source_index[x] for x in ids if x in source_index]
    return {
        'source_refs':ids,
        'source_type':list(dict.fromkeys(str(x.get('kind') or x.get('source_type') or x.get('evidence_type') or 'UNSPECIFIED') for x in cards)) or (['UNRESOLVED_SOURCE_REF'] if ids else []),
        'recency':[{'source_id':str(x.get('source_id')),'observed_at':x.get('observed_at') or x.get('updated_at') or x.get('as_of') or x.get('collected_at')} for x in cards],
        'traceability_status':'SOURCE_BOUND' if ids and len(cards)==len(ids) else ('NO_SOURCE_REQUIRED' if not ids else 'SOURCE_TRACE_INCOMPLETE'),
    }


def _row(*, row_type:str, item:str, status:str, what:str, why:str, refs:Sequence[str], source_index:Mapping[str,Mapping[str,Any]], exact_fact:Any,
         interpretation:str, confidence:str, assumption_boundary:str, downstream_use:Sequence[str], conflict_status:str,
         tradeoff:Any, execution:Any, measurement:Any, proof_object:str, basis:Any=None) -> dict[str,Any]:
    lin=_lineage(refs,source_index)
    evidence={k:deepcopy(lin[k]) for k in ('source_refs','source_type','recency','traceability_status')}
    if _p(basis): evidence['detail']=deepcopy(basis)
    return {
        'type':row_type,'item':item,'status':status,'what':what,'why':why,'evidence':evidence,'tradeoff':deepcopy(tradeoff),'execution':deepcopy(execution),'measurement':deepcopy(measurement),
        'source_refs':lin['source_refs'],'source_type':lin['source_type'],'recency':lin['recency'],'exact_fact':deepcopy(exact_fact),'interpretation':interpretation,'confidence':confidence,
        'assumption_boundary':assumption_boundary,'downstream_use':list(dict.fromkeys(str(x) for x in downstream_use if _p(x))),'conflict_status':conflict_status,'proof_object':proof_object,
        'basis':deepcopy(basis) if _p(basis) else (lin['source_refs'] or assumption_boundary),
    }


def _missing(item:str, source_index:Mapping[str,Mapping[str,Any]]) -> dict[str,Any]:
    return _row(row_type='MISSING_INPUT',item=item,status='MISSING_INPUT',what=f'缺少输入：{item}',why='该输入尚未提供；缺失必须保持显式，不能以默认值、竞品数据或模型猜测补齐。',refs=[],source_index=source_index,exact_fact=None,
        interpretation='当前只能确认此输入缺失，不能确认其真实值。',confidence='LOW',assumption_boundary='MISSING_INPUT_NOT_FACT',downstream_use=['DEPENDENT_DECISIONS_ONLY'],conflict_status='NOT_ASSESSED_MISSING_INPUT',
        tradeoff='继续不依赖该输入的工作；依赖该输入的发布、预算、经济或合规决定保持 HOLD/TO_VERIFY。',execution={'next_action':'COLLECT_OR_VERIFY_INPUT','input':item},measurement={'completion_signal':'Explicit authoritative value/source is supplied and reconciled.'},proof_object='strategy_authority.sections.01_information_completeness_assumptions_decisions.information_audit_items')


def _question(raw:Mapping[str,Any], i:int, source_index:Mapping[str,Mapping[str,Any]]) -> dict[str,Any]:
    item=str(raw.get('item') or raw.get('query') or raw.get('question') or raw.get('reason') or f'Pending confirmation {i}')
    required=[str(x) for x in _l(raw.get('required_for') or raw.get('downstream_effect')) if _p(x)]
    refs=_refs(raw); reason=str(raw.get('reason') or raw.get('why') or '该项会影响依赖它的事实、发布、预算、经济或合规决定。'); needed=raw.get('evidence_needed') or '明确的当前权威来源或用户确认。'
    out=_row(row_type='PENDING_CONFIRMATION',item=item,status=str(raw.get('status') or 'TO_VERIFY').upper(),what=f'待确认：{item}',why=reason,refs=refs,source_index=source_index,exact_fact=None,
        interpretation='这是未解决输入，不是已知事实；只阻断明确依赖它的决定。',confidence='LOW',assumption_boundary='UNRESOLVED_INPUT_NOT_FACT',downstream_use=required or ['TO_VERIFY_DOWNSTREAM_SCOPE'],conflict_status=str(raw.get('conflict_status') or 'UNRESOLVED_INPUT'),
        tradeoff=raw.get('tradeoff') or '不停止无关工作；只冻结依赖该输入的具体决定。',execution=raw.get('execution') or {'next_action':'ASK_OR_VERIFY','evidence_needed':needed},measurement=raw.get('measurement') or {'completion_signal':'Question resolved by explicit evidence/user confirmation.'},proof_object='strategy_authority.sections.01_information_completeness_assumptions_decisions.pending_confirmations',basis=refs or raw.get('basis'))
    out.update({'question_id':str(raw.get('question_id') or f'QUESTION-{i:03d}'),'priority':str(raw.get('priority') or 'TO_VERIFY'),'required_for':required,'downstream_effect':deepcopy(raw.get('downstream_effect') or required or 'TO_VERIFY'),'evidence_needed':needed,'reason':reason})
    return out


def _assumption(raw:Any, i:int, source_index:Mapping[str,Mapping[str,Any]]) -> dict[str,Any]:
    src=_d(raw); text=str(src.get('assumption') or src.get('item') or src.get('text') or raw or f'Assumption {i}'); refs=_refs(src)
    downstream=[str(x) for x in _l(src.get('downstream_effect') or src.get('downstream_use')) if _p(x)]; needed=src.get('evidence_needed') or 'MISSING_INPUT'
    out=_row(row_type='ASSUMPTION',item=text,status=str(src.get('status') or 'ASSUMPTION').upper(),what=text,why=str(src.get('why') or src.get('basis') or '该项尚无充分事实，只作为继续不相关工作的显式假设。'),refs=refs,source_index=source_index,exact_fact=None,
        interpretation='规划假设，不得静默升级为产品事实、市场事实、法规事实或硬宣称。',confidence=str(src.get('confidence') or 'LOW').upper(),assumption_boundary='ASSUMPTION_NOT_FACT',downstream_use=downstream or ['TO_VERIFY'],conflict_status=str(src.get('conflict_status') or 'NOT_ASSESSED_ASSUMPTION'),
        tradeoff=src.get('tradeoff') or '允许规划继续，但依赖真实值的发布/预算/合规/经济决定必须补证据。',execution=src.get('execution') or {'use':'PLANNING_ONLY','verification_action':'Replace assumption with evidence before dependent final decision.'},measurement=src.get('measurement') or {'completion_signal':'Assumption is verified, rejected or replaced by authoritative evidence.'},proof_object='strategy_authority.sections.01_information_completeness_assumptions_decisions.assumption_decision_log',basis=src.get('basis') or refs)
    out.update({'assumption':text,'assumption_support_status':'ASSUMPTION_DECLARED' if downstream and needed!='MISSING_INPUT' else 'MISSING_SUPPORT_DETAIL','downstream_effect':deepcopy(src.get('downstream_effect') or downstream or 'MISSING_INPUT'),'evidence_needed':needed})
    return out


def _decision(raw:Mapping[str,Any], i:int, source_index:Mapping[str,Mapping[str,Any]]) -> dict[str,Any]:
    item=str(raw.get('what') or raw.get('decision') or raw.get('item') or f'Decision {i}'); refs=_refs(raw); downstream=[str(x) for x in _l(raw.get('downstream_use') or raw.get('required_for')) if _p(x)]
    return _row(row_type='DECISION',item=item,status=str(raw.get('status') or 'DECIDED_UNDER_CURRENT_EVIDENCE').upper(),what=item,why=str(raw.get('why') or '在当前证据与显式未知边界下作出该决定。'),refs=refs,source_index=source_index,exact_fact=None,
        interpretation=str(raw.get('interpretation') or '这是当前经营/执行决定，不是新的外部事实。'),confidence=str(raw.get('confidence') or ('MEDIUM' if refs else 'LOW')).upper(),assumption_boundary=str(raw.get('assumption_boundary') or 'DECISION_UNDER_CURRENT_EVIDENCE_NOT_EXTERNAL_FACT'),downstream_use=downstream or ['CURRENT_STRATEGY'],conflict_status=str(raw.get('conflict_status') or 'NO_DECLARED_CONFLICT'),
        tradeoff=raw.get('tradeoff') or '按当前证据推进；若关键证据变化则重新决策。',execution=raw.get('execution') or 'Execute only inside the current evidence/assumption boundary.',measurement=raw.get('measurement') or 'Re-evaluate when new decision-changing evidence arrives.',proof_object='strategy_authority.sections.01_information_completeness_assumptions_decisions.assumption_decision_log',basis=raw.get('evidence') or refs)


def _facts(product_truth:Mapping[str,Any]|None, source_index:Mapping[str,Mapping[str,Any]]) -> list[dict[str,Any]]:
    out=[]
    for i,raw in enumerate(_l(_d(product_truth).get('product_facts')),1):
        if not isinstance(raw,Mapping): continue
        item=str(raw.get('fact') or raw.get('item') or raw.get('field') or f'Fact {i}'); refs=_refs(raw)
        out.append(_row(row_type='FACT',item=item,status=str(raw.get('publication_status') or raw.get('status') or raw.get('evidence_level') or 'FACT').upper(),what=f'已知事实：{item}',why=str(raw.get('why') or '该值来自当前 Product Truth 对象；这里只记录其已知状态与决策影响，不外推新功效。'),refs=refs,source_index=source_index,exact_fact=raw.get('value'),
            interpretation=str(raw.get('interpretation') or '按 Product Truth 原值使用；更强利益/功效需要独立证据。'),confidence=str(raw.get('confidence') or ('MEDIUM' if refs else 'LOW')).upper(),assumption_boundary='FACT_WITHIN_DECLARED_SOURCE_SCOPE',downstream_use=[str(x) for x in _l(raw.get('downstream_use')) if _p(x)] or ['PRODUCT_TRUTH_CONSUMERS'],conflict_status=str(raw.get('conflict_status') or 'NO_DECLARED_CONFLICT'),
            tradeoff=raw.get('tradeoff') or '保持原始事实强度，不为营销力度扩张成未验证结论。',execution=raw.get('execution') or 'Reuse the exact fact only in consumers whose claim boundary permits it.',measurement=raw.get('measurement') or 'Verify source parity whenever the fact is published or rendered.',proof_object='strategy_authority.sections.02_product_truth_value_ladder.product_facts',basis=raw.get('evidence_level') or refs))
    return out


def _dedupe(rows:Sequence[Mapping[str,Any]]) -> list[dict[str,Any]]:
    seen=set(); out=[]
    for raw in rows:
        key=json.dumps(dict(raw),ensure_ascii=False,sort_keys=True,default=str)
        if key not in seen: seen.add(key); out.append(deepcopy(dict(raw)))
    return out


def compile_information_audit_authority(info:Mapping[str,Any]|None, *, product_truth:Mapping[str,Any]|None=None, sources:Sequence[Mapping[str,Any]]|None=None, question_limit:int=DEFAULT_QUESTION_LIMIT) -> dict[str,Any]:
    base=deepcopy(_d(info)); source_index=_source_index(sources); limit=max(1,min(int(question_limit or DEFAULT_QUESTION_LIMIT),DEFAULT_QUESTION_LIMIT))
    pending=[x for x in _l(base.get('pending_confirmations')) if isinstance(x,Mapping)]; overflow=[x for x in _l(base.get('pending_confirmations_overflow')) if isinstance(x,Mapping)]
    questions=[_question(x,i+1,source_index) for i,x in enumerate(_dedupe([*pending,*overflow]))]
    missing=[_missing(str(x),source_index) for x in _l(base.get('required_missing')) if _p(x)]
    assumptions=[_assumption(x,i+1,source_index) for i,x in enumerate(_l(base.get('assumptions')))]
    decisions=[_decision(x,i+1,source_index) for i,x in enumerate(_l(base.get('decision_log'))) if isinstance(x,Mapping)]
    facts=_facts(product_truth,source_index)
    base.update({
        'schema':SCHEMA,'question_limit':limit,'pending_confirmation_total_count':len(questions),'pending_confirmations':questions[:limit],'pending_confirmations_overflow':questions[limit:],'continue_under_assumptions':True,
        'continuation_rule':'最多向用户提出10个真正影响事实、发布、预算、经济或合规的关键问题；完整未解决项继续保留，其他工作在显式 ASSUMPTION / TO_VERIFY / MISSING_INPUT 边界下继续。',
        'assumptions':assumptions,'decision_log':decisions,'assumption_decision_log':facts+assumptions+decisions,'information_audit_items':missing+questions,
        'unresolved_items':missing+questions+[x for x in assumptions if x.get('assumption_support_status')!='ASSUMPTION_DECLARED'],
        'classification_counts':{'facts':len(facts),'missing_inputs':len(missing),'pending_confirmations':len(questions),'assumptions':len(assumptions),'decisions':len(decisions)},
        'lineage_rule':'source → authority/type → recency → exact fact → interpretation → confidence → assumption boundary → downstream use → conflict → decision/tradeoff → proof object',
        'no_fabrication_rule':'MISSING_INPUT / TO_VERIFY / ASSUMPTION remain non-facts. Missing readiness facts do not stop unrelated work and are never defaulted to zero or invented.',
        'status':'INFORMATION_AUDIT_READY_WITH_OPEN_ITEMS' if (missing or questions or any(x.get('assumption_support_status')!='ASSUMPTION_DECLARED' for x in assumptions)) else 'INFORMATION_AUDIT_READY',
        'canonical_graph_binding':{'node_id':'INFORMATION_AUDIT','authority_role':'CANONICAL_INFORMATION_AUDIT_SUBOBJECT','container':'strategy_authority.json#/sections/01_information_completeness_assumptions_decisions'},
    })
    payload=deepcopy(base); payload.pop('authority_sha256',None); base['authority_sha256']=_hash(payload); return base


def wrap_build_master_strategy(fn:Callable[...,dict[str,Any]]) -> Callable[...,dict[str,Any]]:
    if getattr(fn,'_cbcc_v0676_information_audit_authority',False): return fn
    def built(request:dict[str,Any],*args:Any,**kwargs:Any)->dict[str,Any]:
        strategy=fn(request,*args,**kwargs)
        if not isinstance(strategy,dict) or not _is_full(strategy): return strategy
        sections=strategy.setdefault('sections',{}); info=_d(sections.get('01_information_completeness_assumptions_decisions')); truth=_d(sections.get('02_product_truth_value_ladder'))
        sections['01_information_completeness_assumptions_decisions']=compile_information_audit_authority(info,product_truth=truth,sources=[x for x in _l(request.get('sources')) if isinstance(x,Mapping)])
        return strategy
    setattr(built,'_cbcc_v0676_information_audit_authority',True); return built


def information_audit_issues(strategy:Mapping[str,Any]) -> list[dict[str,Any]]:
    if not _is_full(strategy): return []
    info=_d(_d(strategy.get('sections')).get('01_information_completeness_assumptions_decisions')); issues=[]
    if info.get('schema')!=SCHEMA: return [{'code':'FULL_INFORMATION_AUDIT_AUTHORITY_MISSING','expected_schema':SCHEMA}]
    if int(info.get('question_limit') or 0)>DEFAULT_QUESTION_LIMIT or len(_l(info.get('pending_confirmations')))>DEFAULT_QUESTION_LIMIT: issues.append({'code':'FULL_INFORMATION_AUDIT_QUESTION_LIMIT_EXCEEDED','limit':DEFAULT_QUESTION_LIMIT})
    expected=len(_l(info.get('pending_confirmations')))+len(_l(info.get('pending_confirmations_overflow')))
    if int(info.get('pending_confirmation_total_count') or 0)!=expected: issues.append({'code':'FULL_INFORMATION_AUDIT_UNRESOLVED_COUNT_DRIFT','expected':expected,'actual':info.get('pending_confirmation_total_count')})
    if info.get('continue_under_assumptions') is not True: issues.append({'code':'FULL_INFORMATION_AUDIT_CONTINUATION_RULE_MISSING'})
    rows=[x for k in ('information_audit_items','pending_confirmations','pending_confirmations_overflow','assumption_decision_log') for x in _l(info.get(k)) if isinstance(x,Mapping)]
    if not rows and (_l(info.get('required_missing')) or _l(info.get('assumptions')) or _l(info.get('decision_log'))): issues.append({'code':'FULL_INFORMATION_AUDIT_ROWS_MISSING'})
    required=set(DENSITY_FIELDS)|set(LINEAGE_FIELDS)
    for i,row in enumerate(rows):
        missing=sorted(required-set(row))
        if missing: issues.append({'code':'FULL_INFORMATION_AUDIT_ROW_SHALLOW_V0676','row':i,'type':row.get('type'),'fields':missing})
        if str(row.get('type') or '') in {'ASSUMPTION','PENDING_CONFIRMATION'} and _p(row.get('exact_fact')): issues.append({'code':'FULL_INFORMATION_AUDIT_UNKNOWN_PROMOTED_TO_FACT','row':i,'type':row.get('type')})
    return issues


def wrap_validate_strategy_delivery(fn:Callable[...,dict[str,Any]]) -> Callable[...,dict[str,Any]]:
    if getattr(fn,'_cbcc_v0676_information_audit_authority',False): return fn
    def validated(strategy:dict[str,Any],*args:Any,**kwargs:Any)->dict[str,Any]:
        result=fn(strategy,*args,**kwargs)
        if not _is_full(strategy): return result
        extra=information_audit_issues(strategy); seen=set(); merged=[]
        for row in [*list(result.get('issues') or []),*extra]:
            key=json.dumps(row,ensure_ascii=False,sort_keys=True,default=str)
            if key not in seen: seen.add(key); merged.append(row)
        result['issues']=merged
        if extra: result['status']='INCOMPLETE'
        result['information_audit_v0676']={'status':'PASS' if not extra else 'INCOMPLETE','issues':extra}; return result
    setattr(validated,'_cbcc_v0676_information_audit_authority',True); return validated
