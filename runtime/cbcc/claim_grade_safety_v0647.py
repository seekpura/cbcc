from __future__ import annotations

from typing import Any, Callable


def _present(v: Any) -> bool:
    return v not in (None, '', [], {})


def wrap_build_master_strategy(fn: Callable[..., dict[str, Any]]):
    """Keep A/B/C evidence conservative after depth projection.

    Product pack/spec facts may legitimately be B-level bounded facts, but a claim with no linked evidence
    must remain C / pending rather than being promoted merely because it was user-supplied.
    """
    def built(*args, **kwargs):
        out = fn(*args, **kwargs)
        sections = out.get('sections') or {}
        value = sections.get('02_product_truth_value_ladder') or {}
        for row in value.get('claim_value_ladder') or []:
            if not isinstance(row, dict):
                continue
            refs = row.get('source_refs') or row.get('source_ids') or row.get('evidence_refs') or []
            if not _present(refs):
                row['evidence_grade'] = 'C'
                row['publication_status'] = 'PENDING_EVIDENCE'
                row['publication_rule'] = 'SOFT_EXPERIENCE_OR_HYPOTHESIS_ONLY_NO_HARD_CLAIM'
                row.setdefault('claim_boundary', '缺少可追溯A/B证据；仅可作为待验证假设/软性体验表达，不得作硬宣称。')
        return out
    return built
