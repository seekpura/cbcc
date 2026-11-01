from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any, Callable, Mapping, Sequence
import json

SCHEMA = 'cbcc-information-audit-authority-v1'
DEFAULT_QUESTION_LIMIT = 10
DENSITY_FIELDS = ('what', 'why', 'evidence', 'tradeoff', 'execution', 'measurement')
LINEAGE_FIELDS = (
    'source_refs', 'source_type', 'recency', 'exact_fact', 'interpretation', 'confidence',
    'assumption_boundary', 'downstream_use', 'conflict_status', 'proof_object',
)


def _present(value: Any) -> bool:
    return value not in (None, '', [], {})


def _list(value: Any) -> list[Any]:
    if value in (None, '', {}):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set, frozenset)):
        return list(value)
    return [value]


def _dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _stable_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), default=str).encode('utf-8')
    return sha256(raw).hexdigest()


def _source_index(sources: Sequence[Mapping[str, Any]] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for raw in sources or []:
        if not isinstance(raw, Mapping):
            continue
        sid = raw.get('source_id')
        if not _present(sid):
            continue
        out[str(sid)] = deepcopy(dict(raw))
    return out


def _source_refs(raw: Mapping[str, Any]) -> list[str]:
    values = (
        raw.get('source_refs') or raw.get('source_ids') or raw.get('evidence_refs') or
        raw.get('evidence_source_ids') or []
    )
    if isinstance(raw.get('evidence'), list):
        values = list(_list(values)) + [x for x in raw.get('evidence') if isinstance(x, str)]
    return list(dict.fromkeys(str(x) for x in _list(values) if _present(x)))


def _lineage(source_refs: Sequence[str], sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    refs = list(dict.fromkeys(str(x) for x in source_refs if _present(x)))
    cards = [sources[x] for x in refs if x in sources]
    source_types = list(dict.fromkeys(
        str(card.get('kind') or card.get('source_type') or card.get('evidence_type') or 'UNSPECIFIED')
        for card in cards
    ))
    recency = [
        {
            'source_id': str(card.get('source_id')),
            'observed_at': card.get('observed_at') or card.get('updated_at') or card.get('as_of') or card.get('collected_at'),
        }
        for card in cards
    ]
    return {
        'source_refs': refs,
        'source_type': source_types or (['UNRESOLVED_SOURCE_REF'] if refs else []),
        'recency': recency,
        'traceability_status': 'SOURCE_BOUND' if refs and len(cards) == len(refs) else ('NO_SOURCE_REQUIRED' if not refs else 'SOURCE_TRACE_INCOMPLETE'),
    }


def _base_row(
    *,
    row_type: str,
    item: str,
    status: str,
    what: str,
    why: str,
    source_refs: Sequence[str],
    sources: Mapping[str, Mapping[str, Any]],
    exact_fact: Any,
    interpretation: str,
    confidence: str,
    assumption_boundary: str,
    downstream_use: Sequence[str],
    conflict_status: str,
    tradeoff: Any,
    execution: Any,
    measurement: Any,
    proof_object: str,
    evidence_extra: Any = None,
) -> dict[str, Any]:
    lineage = _lineage(source_refs, sources)
    evidence = {
        'source_refs': lineage['source_refs'],
        'source_type': lineage['source_type'],
        'recency': lineage['recency'],
        'traceability_status': lineage['traceability_status'],
    }
    if _present(evidence_extra):
        evidence['detail'] = deepcopy(evidence_extra)
    return {
        'type': row_type,
        'item': item,
        'status': status,
        'what': what,
        'why': why,
        'evidence': evidence,
        'tradeoff': deepcopy(tradeoff),
        'execution': deepcopy(execution),
        'measurement': deepcopy(measurement),
        'source_refs': lineage['source_refs'],
        'source_type': lineage['source_type'],
        'recency': lineage['recency'],
        'exact_fact': deepcopy(exact_fact),
        'interpretation': interpretation,
        'confidence': confidence,
        'assumption_boundary': assumption_boundary,
        'downstream_use': list(dict.fromkeys(str(x) for x in downstream_use if _present(x))),
        'conflict_status': conflict_status,
        'proof_object': proof_object,
        'basis': deepcopy(evidence_extra) if _present(evidence_extra) else (lineage['source_refs'] or assumption_boundary),
    }


def _missing_row(item: str, sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    return _base_row(
        row_type='MISSING_INPUT', item=item, status='MISSING_INPUT',
        what=f'缺少输入：{item}',
        why='该输入尚未提供；缺失必须保持显式，不能以默认值、竞品数据或模型猜测补齐。',
        source_refs=[], sources=sources, exact_fact=None,
        interpretation='当前只能确认此输入缺失，不能确认其真实值。', confidence='LOW',
        assumption_boundary='MISSING_INPUT_NOT_FACT', downstream_use=['DEPENDENT_DECISIONS_ONLY'],
        conflict_status='NOT_ASSESSED_MISSING_INPUT',
        tradeoff='继续不依赖该输入的工作；依赖该输入的发布、预算、经济或合规决定保持 HOLD/TO_VERIFY。',
        execution={'next_action':'COLLECT_OR_VERIFY_INPUT','input':item},
        measurement={'completion_signal':'Explicit authoritative value/source is supplied and reconciled.'},
        proof_object='strategy_authority.sections.01_information_completeness_assumptions_decisions.information_audit_items',
    )


def _question_row(raw: Mapping[str, Any], index: int, sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    item = str(raw.get('item') or raw.get('query') or raw.get('question') or raw.get('reason') or f'Pending confirmation {index}')
    required_for = [str(x) for x in _list(raw.get('required_for') or raw.get('downstream_effect')) if _present(x)]
    refs = _source_refs(raw)
    reason = str(raw.get('reason') or raw.get('why') or '该项会影响依赖它的事实、发布、预算、经济或合规决定。')
    evidence_needed = raw.get('evidence_needed') or '明确的当前权威来源或用户确认。'
    row = _base_row(
        row_type='PENDING_CONFIRMATION', item=item,
        status=str(raw.get('status') or 'TO_VERIFY').upper(),
        what=f'待确认：{item}', why=reason,
        source_refs=refs, sources=sources, exact_fact=None,
        interpretation='这是未解决输入，不是已知事实；只阻断明确依赖它的决定。', confidence='LOW',
        assumption_boundary='UNRESOLVED_INPUT_NOT_FACT',
        downstream_use=required_for or ['TO_VERIFY_DOWNSTREAM_SCOPE'],
        conflict_status=str(raw.get('conflict_status') or 'UNRESOLVED_INPUT'),
        tradeoff=raw.get('tradeoff') or '不停止无关工作；只冻结依赖该输入的具体决定。',
        execution=raw.get('execution') or {'next_action':'ASK_OR_VERIFY','evidence_needed':evidence_needed},
        measurement=raw.get('measurement') or {'completion_signal':'Question resolved by explicit evidence/user confirmation.'},
        proof_object='strategy_authority.sections.01_information_completeness_assumptions_decisions.pending_confirmations',
        evidence_extra=refs or raw.get('basis'),
    )
    row['question_id'] = str(raw.get('question_id') or f'QUESTION-{index:03d}')
    row['priority'] = str(raw.get('priority') or 'TO_VERIFY')
    row['required_for'] = required_for
    row['downstream_effect'] = deepcopy(raw.get('downstream_effect') or required_for or 'TO_VERIFY')
    row['evidence_needed'] = evidence_needed
    row['reason'] = reason
    return row


def _assumption_row(raw: Any, index: int, sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    src = _dict(raw)
    text = str(src.get('assumption') or src.get('item') or src.get('text') or raw or f'Assumption {index}')
    refs = _source_refs(src)
    downstream = [str(x) for x in _list(src.get('downstream_effect') or src.get('downstream_use')) if _present(x)]
    evidence_needed = src.get('evidence_needed') or 'MISSING_INPUT'
    status = str(src.get('status') or 'ASSUMPTION').upper()
    support_status = 'ASSUMPTION_DECLARED' if downstream and evidence_needed != 'MISSING_INPUT' else 'MISSING_SUPPORT_DETAIL'
    row = _base_row(
        row_type='ASSUMPTION', item=text, status=status,
        what=text,
        why=str(src.get('why') or src.get('basis') or '该项尚无充分事实，只作为继续不相关工作的显式假设。'),
        source_refs=refs, sources=sources, exact_fact=None,
        interpretation='规划假设，不得静默升级为产品事实、市场事实、法规事实或硬宣称。',
        confidence=str(src.get('confidence') or 'LOW').upper(),
        assumption_boundary='ASSUMPTION_NOT_FACT', downstream_use=downstream or ['TO_VERIFY'],
        conflict_status=str(src.get('conflict_status') or 'NOT_ASSESSED_ASSUMPTION'),
        tradeoff=src.get('tradeoff') or '允许规划继续，但依赖真实值的发布/预算/合规/经济决定必须补证据。',
        execution=src.get('execution') or {'use':'PLANNING_ONLY','verification_action':'Replace assumption with evidence before dependent final decision.'},
        measurement=src.get('measurement') or {'completion_signal':'Assumption is verified, rejected or replaced by authoritative evidence.'},
        proof_object='strategy_authority.sections.01_information_completeness_assumptions_decisions.assumption_decision_log',
        evidence_extra=src.get('basis') or refs,
    )
    row['assumption'] = text
    row['assumption_support_status'] = support_status
    row['downstream_effect'] = deepcopy(src.get('downstream_effect') or downstream or 'MISSING_INPUT')
    row['evidence_needed'] = evidence_needed
    return row


def _decision_row(raw: Mapping[str, Any], index: int, sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    item = str(raw.get('what') or raw.get('decision') or raw.get('item') or f'Decision {index}')
    refs = _source_refs(raw)
    downstream = [str(x) for x in _list(raw.get('downstream_use') or raw.get('required_for')) if _present(x)]
    confidence = str(raw.get('confidence') or ('MEDIUM' if refs else 'LOW')).upper()
    return _base_row(
        row_type='DECISION', item=item,
        status=str(raw.get('status') or 'DECIDED_UNDER_CURRENT_EVIDENCE').upper(),
        what=item,
        why=str(raw.get('why') or '在当前证据与显式未知边界下作出该决定。'),
        source_refs=refs, sources=sources, exact_fact=None,
        interpretation=str(raw.get('interpretation') or '这是当前经营/执行决定，不是新的外部事实。'),
        confidence=confidence,
        assumption_boundary=str(raw.get('assumption_boundary') or 'DECISION_UNDER_CURRENT_EVIDENCE_NOT_EXTERNAL_FACT'),
        downstream_use=downstream or ['CURRENT_STRATEGY'],
        conflict_status=str(raw.get('conflict_status') or 'NO_DECLARED_CONFLICT'),
        tradeoff=raw.get('tradeoff') or '按当前证据推进；若关键证据变化则重新决策。',
        execution=raw.get('execution') or 'Execute only inside the current evidence/assumption boundary.',
        measurement=raw.get('measurement') or 'Re-evaluate when new decision-changing evidence arrives.',
        proof_object='strategy_authority.sections.01_information_completeness_assumptions_decisions.assumption_decision_log',
        evidence_extra=raw.get('evidence') or refs,
    )


def _fact_rows(product_truth: Mapping[str, Any] | None, sources: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    truth = _dict(product_truth)
    rows: list[dict[str, Any]] = []
    for index, raw in enumerate(_list(truth.get('product_facts')), 1):
        if not isinstance(raw, Mapping):
            continue
        item = str(raw.get('fact') or raw.get('item') or raw.get('field') or f'Fact {index}')
        value = raw.get('value')
        refs = _source_refs(raw)
        confidence = 'MEDIUM' if refs else 'LOW'
        rows.append(_base_row(
            row_type='FACT', item=item,
            status=str(raw.get('publication_status') or raw.get('status') or raw.get('evidence_level') or 'FACT').upper(),
            what=f'已知事实：{item}',
            why=str(raw.get('why') or '该值来自当前 Product Truth 对象；这里只记录其已知状态与决策影响，不外推新功效。'),
            source_refs=refs, sources=sources, exact_fact=value,
            interpretation=str(raw.get('interpretation') or '按 Product Truth 原值使用；更强利益/功效需要独立证据。'),
            confidence=str(raw.get('confidence') or confidence).upper(),
            assumption_boundary='FACT_WITHIN_DECLARED_SOURCE_SCOPE',
            downstream_use=[str(x) for x in _list(raw.get('downstream_use')) if _present(x)] or ['PRODUCT_TRUTH_CONSUMERS'],
            conflict_status=str(raw.get('conflict_status') or 'NO_DECLARED_CONFLICT'),
            tradeoff=raw.get('tradeoff') or '保持原始事实强度，不为营销力度扩张成未验证结论。',
            execution=raw.get('execution') or 'Reuse the exact fact only in consumers whose claim boundary permits it.',
            measurement=raw.get('measurement') or 'Verify source parity whenever the fact is published or rendered.',
            proof_object='strategy_authority.sections.02_product_truth_value_ladder.product_facts',
            evidence_extra=raw.get('evidence_level') or refs,
        ))
    return rows


def _dedupe_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in rows:
        key = json.dumps(dict(raw), ensure_ascii=False, sort_keys=True, default=str)
        if key in seen:
            continue
        seen.add(key)
        out.append(deepcopy(dict(raw)))
    return out


def compile_information_audit_authority(
    info: Mapping[str, Any] | None,
    *,
    product_truth: Mapping[str, Any] | None = None,
    sources: Sequence[Mapping[str, Any]] | None = None,
    question_limit: int = DEFAULT_QUESTION_LIMIT,
) -> dict[str, Any]:
    source_index = _source_index(sources)
    base = deepcopy(_dict(info))
    limit = max(1, min(int(question_limit or DEFAULT_QUESTION_LIMIT), DEFAULT_QUESTION_LIMIT))

    pending_raw = [x for x in _list(base.get('pending_confirmations')) if isinstance(x, Mapping)]
    overflow_raw = [x for x in _list(base.get('pending_confirmations_overflow')) if isinstance(x, Mapping)]
    combined_raw = _dedupe_rows([*pending_raw, *overflow_raw])
    questions = [_question_row(row, i + 1, source_index) for i, row in enumerate(combined_raw)]

    missing_rows = [_missing_row(str(item), source_index) for item in _list(base.get('required_missing')) if _present(item)]
    assumptions = [_assumption_row(raw, i + 1, source_index) for i, raw in enumerate(_list(base.get('assumptions')))]
    decisions = [_decision_row(raw, i + 1, source_index) for i, raw in enumerate(_list(base.get('decision_log'))) if isinstance(raw, Mapping)]
    facts = _fact_rows(product_truth, source_index)

    base['schema'] = SCHEMA
    base['question_limit'] = limit
    base['pending_confirmation_total_count'] = len(questions)
    base['pending_confirmations'] = questions[:limit]
    base['pending_confirmations_overflow'] = questions[limit:]
    base['continue_under_assumptions'] = True
    base['continuation_rule'] = '最多向用户提出10个真正影响事实、发布、预算、经济或合规的关键问题；完整未解决项继续保留，其他工作在显式 ASSUMPTION / TO_VERIFY / MISSING_INPUT 边界下继续。'
    base['assumptions'] = assumptions
    base['decision_log'] = decisions
    base['assumption_decision_log'] = facts + assumptions + decisions
    base['information_audit_items'] = missing_rows + questions
    base['unresolved_items'] = missing_rows + questions + [row for row in assumptions if row.get('assumption_support_status') != 'ASSUMPTION_DECLARED']
    base['classification_counts'] = {
        'facts': len(facts),
        'missing_inputs': len(missing_rows),
        'pending_confirmations': len(questions),
        'assumptions': len(assumptions),
        'decisions': len(decisions),
    }
    base['lineage_rule'] = 'source → authority/type → recency → exact fact → interpretation → confidence → assumption boundary → downstream use → conflict → decision/tradeoff → proof object'
    base['no_fabrication_rule'] = 'MISSING_INPUT / TO_VERIFY / ASSUMPTION remain non-facts. Missing readiness facts do not stop unrelated work and are never defaulted to zero or invented.'
    base['status'] = 'INFORMATION_AUDIT_READY_WITH_OPEN_ITEMS' if (missing_rows or questions or base['unresolved_items']) else 'INFORMATION_AUDIT_READY'
    base['canonical_graph_binding'] = {
        'node_id':'INFORMATION_AUDIT',
        'authority_role':'CANONICAL_INFORMATION_AUDIT_SUBOBJECT',
        'container':'strategy_authority.json#/sections/01_information_completeness_assumptions_decisions',
    }
    hash_input = deepcopy(base)
    hash_input.pop('authority_sha256', None)
    base['authority_sha256'] = _stable_hash(hash_input)
    return base


def _is_full(strategy: Mapping[str, Any]) -> bool:
    hp = _dict(strategy.get('human_projection'))
    mode = str(hp.get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '').upper()
    return mode == 'FULL'


def wrap_build_master_strategy(fn: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    if getattr(fn, '_cbcc_v0676_information_audit_authority', False):
        return fn

    def built(request: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
        strategy = fn(request, *args, **kwargs)
        if not isinstance(strategy, dict) or not _is_full(strategy):
            return strategy
        sections = strategy.setdefault('sections', {})
        info = _dict(sections.get('01_information_completeness_assumptions_decisions'))
        truth = _dict(sections.get('02_product_truth_value_ladder'))
        sections['01_information_completeness_assumptions_decisions'] = compile_information_audit_authority(
            info,
            product_truth=truth,
            sources=[x for x in _list(request.get('sources')) if isinstance(x, Mapping)],
            question_limit=DEFAULT_QUESTION_LIMIT,
        )
        strategy['sections'] = sections
        return strategy

    setattr(built, '_cbcc_v0676_information_audit_authority', True)
    return built


def information_audit_issues(strategy: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not _is_full(strategy):
        return []
    sections = _dict(strategy.get('sections'))
    info = _dict(sections.get('01_information_completeness_assumptions_decisions'))
    issues: list[dict[str, Any]] = []
    if info.get('schema') != SCHEMA:
        issues.append({'code':'FULL_INFORMATION_AUDIT_AUTHORITY_MISSING','expected_schema':SCHEMA})
        return issues
    if int(info.get('question_limit') or 0) > DEFAULT_QUESTION_LIMIT or len(_list(info.get('pending_confirmations'))) > DEFAULT_QUESTION_LIMIT:
        issues.append({'code':'FULL_INFORMATION_AUDIT_QUESTION_LIMIT_EXCEEDED','limit':DEFAULT_QUESTION_LIMIT})
    expected_total = len(_list(info.get('pending_confirmations'))) + len(_list(info.get('pending_confirmations_overflow')))
    if int(info.get('pending_confirmation_total_count') or 0) != expected_total:
        issues.append({'code':'FULL_INFORMATION_AUDIT_UNRESOLVED_COUNT_DRIFT','expected':expected_total,'actual':info.get('pending_confirmation_total_count')})
    if info.get('continue_under_assumptions') is not True:
        issues.append({'code':'FULL_INFORMATION_AUDIT_CONTINUATION_RULE_MISSING'})

    density = set(DENSITY_FIELDS)
    lineage = set(LINEAGE_FIELDS)
    rows = [x for x in _list(info.get('pending_confirmations')) if isinstance(x, Mapping)]
    rows += [x for x in _list(info.get('pending_confirmations_overflow')) if isinstance(x, Mapping)]
    rows += [x for x in _list(info.get('assumption_decision_log')) if isinstance(x, Mapping)]
    if not rows and (_list(info.get('required_missing')) or _list(info.get('assumptions')) or _list(info.get('decision_log'))):
        issues.append({'code':'FULL_INFORMATION_AUDIT_ROWS_MISSING'})
    for index, row in enumerate(rows):
        missing = sorted((density | lineage) - set(row))
        if missing:
            issues.append({'code':'FULL_INFORMATION_AUDIT_ROW_SHALLOW_V0676','row':index,'type':row.get('type'),'fields':missing})
        if str(row.get('type') or '') in {'ASSUMPTION','PENDING_CONFIRMATION'} and _present(row.get('exact_fact')):
            issues.append({'code':'FULL_INFORMATION_AUDIT_UNKNOWN_PROMOTED_TO_FACT','row':index,'type':row.get('type')})
    return issues


def wrap_validate_strategy_delivery(fn: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    if getattr(fn, '_cbcc_v0676_information_audit_authority', False):
        return fn

    def validated(strategy: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
        result = fn(strategy, *args, **kwargs)
        if not _is_full(strategy):
            return result
        extra = information_audit_issues(strategy)
        existing = list(result.get('issues') or [])
        seen: set[str] = set()
        merged: list[dict[str, Any]] = []
        for row in [*existing, *extra]:
            key = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)
            if key in seen:
                continue
            seen.add(key)
            merged.append(row)
        result['issues'] = merged
        if extra:
            result['status'] = 'INCOMPLETE'
        result['information_audit_v0676'] = {'status':'PASS' if not extra else 'INCOMPLETE','issues':extra}
        return result

    setattr(validated, '_cbcc_v0676_information_audit_authority', True)
    return validated
