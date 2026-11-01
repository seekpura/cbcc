from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any, Mapping, Sequence
import json


EVIDENCE_GRADE_POLICY: dict[str, dict[str, Any]] = {
    'A': {
        'basis': 'test / certification / reproducible measurement evidence',
        'hard_claim_eligible': True,
        'publication_rule': 'May support a bounded hard claim only inside the verified evidence scope.',
    },
    'B': {
        'basis': 'supplier / specification / formula / mechanism evidence',
        'hard_claim_eligible': True,
        'publication_rule': 'May support factual or bounded mechanism wording; must not be inflated into tested efficacy.',
    },
    'C': {
        'basis': 'subjective / inferred / pending-validation evidence',
        'hard_claim_eligible': False,
        'publication_rule': 'Never release as a hard claim; keep as hypothesis, soft creative direction, or HOLD.',
    },
}

VALUE_KINDS = {
    'FACT',
    'TRUE_SELLING_POINT',
    'PERCEIVED_BENEFIT',
    'EMOTIONAL_VALUE',
    'NON_CLAIMABLE',
}


def _text(value: Any) -> str:
    return str(value if value is not None else '').strip()


def _list(value: Any) -> list[Any]:
    if value in (None, '', {}):
        return []
    return list(value) if isinstance(value, (list, tuple, set, frozenset)) else [value]


def _stable_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), default=str).encode('utf-8')
    return sha256(raw).hexdigest()


def _normalize_grade(value: Any, *, default: str = 'C') -> str:
    grade = _text(value).upper() or default
    return grade if grade in EVIDENCE_GRADE_POLICY else default


def _fact_row(raw: Mapping[str, Any], index: int) -> dict[str, Any]:
    row = deepcopy(dict(raw))
    row['kind'] = 'FACT'
    row.setdefault('fact_id', f'FACT-{index:03d}')
    row['source_ids'] = [str(x) for x in _list(row.get('source_ids')) if _text(x)]
    grade = _normalize_grade(row.get('evidence_grade'), default='B' if row['source_ids'] else 'C')
    row['evidence_grade'] = grade
    row['hard_claim_allowed'] = bool(EVIDENCE_GRADE_POLICY[grade]['hard_claim_eligible'])
    row['release_status'] = 'SUPPORTED_FACT' if row['source_ids'] else 'HOLD'
    row['reason_codes'] = [] if row['source_ids'] else ['FACT_SOURCE_REQUIRED']
    return row


def _value_row(raw: Mapping[str, Any], index: int) -> dict[str, Any]:
    row = deepcopy(dict(raw))
    kind = _text(row.get('kind')).upper()
    if kind not in VALUE_KINDS - {'FACT'}:
        raise ValueError(f'Unsupported Product Truth value kind: {kind or "<empty>"}')
    row['kind'] = kind
    row.setdefault('value_id', f'VALUE-{index:03d}')
    row['source_ids'] = [str(x) for x in _list(row.get('source_ids')) if _text(x)]
    grade = _normalize_grade(row.get('evidence_grade'))
    row['evidence_grade'] = grade
    reasons = [str(x) for x in _list(row.get('reason_codes')) if _text(x)]
    hard_eligible = bool(EVIDENCE_GRADE_POLICY[grade]['hard_claim_eligible'])
    requested = _text(row.get('release_status')).upper()

    if kind == 'NON_CLAIMABLE':
        row['release_status'] = 'HOLD'
        row['hard_claim_allowed'] = False
        reasons.append('NON_CLAIMABLE_BOUNDARY')
    elif grade == 'C':
        row['release_status'] = 'HOLD'
        row['hard_claim_allowed'] = False
        reasons.append('C_GRADE_NOT_HARD_CLAIM')
    elif not row['source_ids']:
        row['release_status'] = 'HOLD'
        row['hard_claim_allowed'] = False
        reasons.append('EVIDENCE_SOURCE_REQUIRED')
    else:
        row['hard_claim_allowed'] = hard_eligible
        row['release_status'] = requested if requested in {'APPROVED', 'SUPPORTED', 'READY_REVIEW'} else 'READY_REVIEW'

    row['reason_codes'] = list(dict.fromkeys(reasons))
    row['evidence_policy'] = deepcopy(EVIDENCE_GRADE_POLICY[grade])
    return row


def _fact_conflicts(facts: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_field: dict[str, list[Mapping[str, Any]]] = {}
    for row in facts:
        field = _text(row.get('field'))
        if field:
            by_field.setdefault(field, []).append(row)
    conflicts: list[dict[str, Any]] = []
    for field, rows in by_field.items():
        normalized: dict[str, Any] = {}
        for row in rows:
            value = row.get('value')
            key = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
            normalized[key] = value
        if len(normalized) <= 1:
            continue
        conflicts.append({
            'field': field,
            'status': 'CONFLICTING',
            'values': list(normalized.values()),
            'source_ids': list(dict.fromkeys(
                str(source_id)
                for row in rows
                for source_id in _list(row.get('source_ids'))
                if _text(source_id)
            )),
            'resolution': 'HOLD_UNTIL_SOURCE_CONFLICT_RESOLVED',
        })
    return conflicts


def _assumption_row(raw: Mapping[str, Any], index: int) -> dict[str, Any]:
    row = deepcopy(dict(raw))
    row.setdefault('assumption_id', f'ASSUMPTION-{index:03d}')
    if not _text(row.get('downstream_effect')):
        row['downstream_effect'] = 'MISSING_INPUT'
    if not _text(row.get('evidence_needed')):
        row['evidence_needed'] = 'MISSING_INPUT'
    row['status'] = (
        'ASSUMPTION_DECLARED'
        if row['downstream_effect'] != 'MISSING_INPUT' and row['evidence_needed'] != 'MISSING_INPUT'
        else 'MISSING_SUPPORT_DETAIL'
    )
    return row


def _value_kind_status(ladder: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Expose every Product Truth value layer, including explicit missing-input states."""
    out: dict[str, dict[str, Any]] = {}
    for kind in sorted(VALUE_KINDS, key=lambda x: (x != 'FACT', x)):
        rows = [row for row in ladder if _text(row.get('kind')).upper() == kind]
        if rows:
            out[kind] = {
                'status': 'READY',
                'count': len(rows),
                'why': 'Explicit authored Product Truth row(s) were supplied for this value layer.',
            }
        else:
            out[kind] = {
                'status': 'MISSING_INPUT',
                'count': 0,
                'why': (
                    f'No explicit {kind} row was supplied; runtime must not derive or invent this value layer '
                    'from Product Truth facts or adjacent market/category evidence.'
                ),
            }
    return out


def _claim_evidence_trace(ladder: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Index authored Product Truth objects to their evidence without creating new claims."""
    trace: list[dict[str, Any]] = []
    for index, row in enumerate(ladder, 1):
        source_ids = [str(x) for x in _list(row.get('source_ids')) if _text(x)]
        trace.append({
            'object_id': row.get('fact_id') or row.get('value_id') or f'PRODUCT-TRUTH-{index:03d}',
            'kind': _text(row.get('kind')).upper(),
            'evidence_grade': _normalize_grade(row.get('evidence_grade')),
            'source_ids': source_ids,
            'trace_status': 'SOURCE_BOUND' if source_ids else 'UNBOUND_HOLD',
            'release_status': row.get('release_status'),
            'hard_claim_allowed': bool(row.get('hard_claim_allowed')) if source_ids else False,
            'reason_codes': list(_list(row.get('reason_codes'))),
        })
    return trace


def compile_product_truth_evidence_authority(
    *,
    facts: Sequence[Mapping[str, Any]] | None,
    value_rows: Sequence[Mapping[str, Any]] | None,
    assumptions: Sequence[Mapping[str, Any]] | None = None,
    unknowns: Sequence[Any] | None = None,
) -> dict[str, Any]:
    """Compile Product Truth without inventing missing commercial meaning or evidence.

    The function normalizes only explicitly supplied facts/value rows. It never derives a selling
    point, perceived benefit, emotional value or prohibited claim from a product fact by itself.
    """
    fact_rows = [_fact_row(row, i + 1) for i, row in enumerate(facts or [])]
    commercial_rows = [_value_row(row, i + 1) for i, row in enumerate(value_rows or [])]
    conflicts = _fact_conflicts(fact_rows)
    normalized_assumptions = [_assumption_row(row, i + 1) for i, row in enumerate(assumptions or [])]
    normalized_unknowns = [deepcopy(x) for x in (unknowns or [])]

    ladder = fact_rows + commercial_rows
    value_kind_status = _value_kind_status(ladder)
    claim_evidence_trace = _claim_evidence_trace(ladder)
    if conflicts:
        status = 'HOLD_CONFLICTING_PRODUCT_TRUTH'
    elif any(row.get('release_status') == 'HOLD' for row in ladder):
        status = 'READY_WITH_HOLDS'
    else:
        status = 'PRODUCT_TRUTH_READY'

    authority = {
        'schema': 'cbcc-product-truth-evidence-v1',
        'status': status,
        'evidence_grade_policy': deepcopy(EVIDENCE_GRADE_POLICY),
        'value_ladder': ladder,
        'value_kind_status': value_kind_status,
        'claim_evidence_trace': claim_evidence_trace,
        'fact_conflicts': conflicts,
        'assumptions': normalized_assumptions,
        'unknowns': normalized_unknowns,
        'canonical_graph_binding': {
            'node_id': 'PRODUCT_TRUTH',
            'authority_role': 'CANONICAL_JSON_AUTHORITY',
            'projection_rule': 'Downstream strategy, listing, content, visual, prompt and package objects may project this authority but may not invent or silently upgrade Product Truth.',
        },
        'no_fabrication_rule': 'Missing facts/evidence remain UNKNOWN, MISSING_INPUT or HOLD. Market/category evidence cannot create product facts or upgrade unsupported claims.',
    }
    authority['authority_sha256'] = _stable_hash(authority)
    return authority
