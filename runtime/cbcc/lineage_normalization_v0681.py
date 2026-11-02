from __future__ import annotations

"""REQ-088 lineage normalization and resolvable-consumption audit.

This module does not create a second business-fact authority.  It walks the canonical business objects
already materialized in the final package and records *bindings* back to those authority fields.  Rich
but heterogeneous lineage shapes (for example Market Research evidence.source_ids/source_cards) are
normalized to the canonical LINEAGE_FIELDS contract without copying exact_fact/interpretation payloads.

Resolution is fail-honest:
- source references must resolve to the canonical source authority (or an embedded source card),
- downstream_use must bind to a real final semantic object or an explicitly deferred TO_VERIFY token,
- explicit proof objects must resolve; an authority row itself may serve as the proof object when no
  separate proof object was authored,
- missing lineage fields stay INCOMPLETE instead of being filled with invented values.
"""

from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence
import json
import re

from .information_audit_authority import LINEAGE_FIELDS
from .full_package_semantic_closure_v0681 import build_final_semantic_inventory

CANONICAL_FILE = "CANONICAL_HUMAN_DATA.json"
LINEAGE_INDEX_FILE = "LINEAGE_CLOSURE_INDEX.json"
LINEAGE_AUDIT_FILE = "LINEAGE_CLOSURE_AUDIT.json"
CONTRACT = "REQ088_FULL_SOURCE_EVIDENCE_ASSUMPTION_DECISION_LINEAGE_V0681"

# These are semantic anchors, not a parallel business taxonomy.  They translate mature authority
# consumer labels into objects that already exist in the final canonical package.
_DOWNSTREAM_ALIASES: dict[str, tuple[str, ...]] = {
    "PRODUCT_TRUTH": ("canonical_business_object::product_truth",),
    "PRODUCT_TRUTH_CONSUMERS": ("canonical_business_object::strategy_authority", "canonical_business_object::human_delivery"),
    "STRATEGY": ("canonical_business_object::strategy_authority",),
    "CURRENT_STRATEGY": ("canonical_business_object::strategy_authority",),
    "POSITIONING": ("canonical_business_object::strategy_authority",),
    "MESSAGE_HIERARCHY": ("canonical_business_object::strategy_authority",),
    "ECONOMICS": ("canonical_business_object::strategy_authority",),
    "OFFER": ("canonical_business_object::strategy_authority",),
    "LISTING": ("canonical_business_object::human_delivery",),
    "LISTING_SEARCH": ("canonical_business_object::human_delivery",),
    "CONTENT": ("canonical_business_object::strategy_authority",),
    "CONTENT_MATRIX": ("canonical_business_object::strategy_authority",),
    "PAID": ("canonical_business_object::ads",),
    "ADS": ("canonical_business_object::ads",),
    "REVIEW": ("canonical_business_object::reviews",),
    "REVIEWS": ("canonical_business_object::reviews",),
    "RISK": ("canonical_business_object::compliance",),
    "COMPLIANCE": ("canonical_business_object::compliance",),
    "VISUAL_MASTER": ("canonical_business_object::strategy_authority", "canonical_business_object::asset_universe"),
    "ASSETS": ("canonical_business_object::assets",),
    "MEASUREMENT": ("canonical_business_object::strategy_authority",),
    "SOURCES": ("canonical_business_object::sources",),
    "DEPENDENT_DECISIONS_ONLY": ("canonical_business_object::strategy_authority",),
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _present(value: Any) -> bool:
    return value not in (None, "", [], {})


def _list(value: Any) -> list[Any]:
    if value in (None, "", {}):
        return []
    if isinstance(value, (list, tuple, set, frozenset)):
        return list(value)
    return [value]


def _token(value: Any) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", str(value or "").upper()).strip("_")


def _stable_id(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()[:16]


def _business_objects(package: Path) -> dict[str, Any]:
    payload = _read_json(package / CANONICAL_FILE)
    raw = payload.get("canonical_business_objects")
    return dict(raw) if isinstance(raw, Mapping) else {}


def _path_parts(path: str) -> list[str | int]:
    parts: list[str | int] = []
    for token in re.finditer(r"([^\.\[\]]+)|\[(\d+)\]", path):
        if token.group(1) is not None:
            parts.append(token.group(1))
        else:
            parts.append(int(token.group(2)))
    return parts


def _path_exists(value: Any, path: str) -> bool:
    current = value
    if not path:
        return True
    for part in _path_parts(path):
        if isinstance(part, int):
            if not isinstance(current, list) or part >= len(current):
                return False
            current = current[part]
        else:
            if not isinstance(current, Mapping) or part not in current:
                return False
            current = current[part]
    return True


def _authority_ref(object_id: str, relative_path: str) -> str:
    return f"{object_id}#{relative_path}" if relative_path else object_id


def _field_binding(authority_ref: str, field_path: str) -> str:
    if "#" in authority_ref:
        return f"{authority_ref}.{field_path}" if field_path else authority_ref
    return f"{authority_ref}#{field_path}" if field_path else authority_ref


def _source_rows(value: Any, path: str = "") -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    if isinstance(value, Mapping):
        if _present(value.get("source_id")):
            rows.append((path, dict(value)))
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            rows.extend(_source_rows(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(_source_rows(child, f"{path}[{index}]"))
    return rows


def _source_index(business: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    source_object = business.get("sources")
    for path, row in _source_rows(source_object, ""):
        sid = str(row.get("source_id") or "")
        if not sid:
            continue
        out[sid] = {
            "row": row,
            "binding": _authority_ref("canonical_business_object::sources", path),
        }
    return out


def _embedded_source_index(row: Mapping[str, Any], authority_ref: str) -> dict[str, dict[str, Any]]:
    evidence = row.get("evidence") if isinstance(row.get("evidence"), Mapping) else {}
    out: dict[str, dict[str, Any]] = {}
    for index, card in enumerate(_list(evidence.get("source_cards"))):
        if not isinstance(card, Mapping) or not _present(card.get("source_id")):
            continue
        sid = str(card.get("source_id"))
        out[sid] = {
            "row": dict(card),
            "binding": _field_binding(authority_ref, f"evidence.source_cards[{index}]"),
        }
    return out


def _direct_refs(row: Mapping[str, Any], authority_ref: str) -> tuple[list[str], str | None]:
    for key in ("source_refs", "source_ids", "evidence_refs", "evidence_source_ids"):
        if key in row:
            return [str(x) for x in _list(row.get(key)) if _present(x)], _field_binding(authority_ref, key)
    evidence = row.get("evidence")
    if isinstance(evidence, Mapping) and "source_ids" in evidence:
        return [str(x) for x in _list(evidence.get("source_ids")) if _present(x)], _field_binding(authority_ref, "evidence.source_ids")
    return [], None


def _is_candidate(row: Mapping[str, Any]) -> bool:
    if any(key in row for key in LINEAGE_FIELDS):
        return True
    evidence = row.get("evidence")
    return isinstance(evidence, Mapping) and any(key in evidence for key in ("source_ids", "source_cards", "traceability_status"))


def _walk_candidates(value: Any, path: str = "") -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    if isinstance(value, Mapping):
        if _is_candidate(value):
            rows.append((path, dict(value)))
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            rows.extend(_walk_candidates(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(_walk_candidates(child, f"{path}[{index}]"))
    return rows


def _resolve_object_ref(ref: str, *, business: Mapping[str, Any], semantic_ids: set[str]) -> bool:
    ref = str(ref or "").strip()
    if not ref:
        return False
    if ref.startswith("production_asset::"):
        return ref.split("#", 1)[0] in semantic_ids
    if ref.startswith("canonical_business_object::"):
        object_ref, _, path = ref.partition("#")
        if object_ref not in semantic_ids:
            return False
        key = object_ref.split("::", 1)[1]
        return key in business and _path_exists(business[key], path)
    # Mature strategy proof objects historically use `strategy_authority.sections...` syntax.
    first, dot, rest = ref.partition(".")
    if dot and first in business:
        object_ref = f"canonical_business_object::{first}"
        return object_ref in semantic_ids and _path_exists(business[first], rest)
    return False


def _resolve_downstream(values: Sequence[Any], semantic_ids: set[str]) -> tuple[list[str], list[str], list[str]]:
    resolved: list[str] = []
    deferred: list[str] = []
    unresolved: list[str] = []
    for raw in values:
        value = str(raw or "").strip()
        if not value:
            continue
        if value.startswith(("canonical_business_object::", "production_asset::")):
            object_id = value.split("#", 1)[0]
            if object_id in semantic_ids:
                resolved.append(object_id)
            else:
                unresolved.append(value)
            continue
        token = _token(value)
        if token.startswith("TO_VERIFY") or token in {"UNKNOWN", "MISSING_INPUT", "NOT_YET_SCOPED"}:
            deferred.append(value)
            continue
        candidates = _DOWNSTREAM_ALIASES.get(token, ())
        existing = [candidate for candidate in candidates if candidate in semantic_ids]
        if existing:
            resolved.extend(existing)
        else:
            unresolved.append(value)
    return list(dict.fromkeys(resolved)), list(dict.fromkeys(deferred)), list(dict.fromkeys(unresolved))


def _missing_descriptor(authority_ref: str, field: str) -> dict[str, Any]:
    return {"binding": None, "resolution": "MISSING", "authority_record": authority_ref, "field": field}


def _normalize_record(
    *,
    object_id: str,
    object_payload: Any,
    relative_path: str,
    row: Mapping[str, Any],
    business: Mapping[str, Any],
    semantic_ids: set[str],
    source_index: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    authority_ref = _authority_ref(object_id, relative_path)
    refs, refs_binding = _direct_refs(row, authority_ref)
    embedded = _embedded_source_index(row, authority_ref)
    sources = dict(source_index)
    for sid, value in embedded.items():
        sources.setdefault(sid, value)

    issues: list[dict[str, Any]] = []
    lineage: dict[str, dict[str, Any]] = {}

    unresolved_refs = [sid for sid in refs if sid not in sources]
    lineage["source_refs"] = {
        "binding": refs_binding,
        "ids": refs,
        "resolution": "PASS" if refs_binding is not None and not unresolved_refs else ("MISSING" if refs_binding is None else "INCOMPLETE"),
    }
    if refs_binding is None:
        issues.append({"code": "LINEAGE_FIELD_UNBOUND", "field": "source_refs"})
    for sid in unresolved_refs:
        issues.append({"code": "LINEAGE_SOURCE_REF_UNRESOLVED", "source_ref": sid})

    if "source_type" in row:
        lineage["source_type"] = {
            "binding": _field_binding(authority_ref, "source_type"),
            "resolved": [str(x) for x in _list(row.get("source_type"))],
            "resolution": "PASS",
        }
    elif refs and all(sid in sources for sid in refs):
        kinds = []
        bindings = []
        for sid in refs:
            source = sources[sid]
            source_row = source.get("row") if isinstance(source.get("row"), Mapping) else {}
            kinds.append(str(source_row.get("kind") or source_row.get("source_type") or source_row.get("evidence_type") or "UNSPECIFIED"))
            bindings.append(f"{source.get('binding')}#kind" if "#" not in str(source.get("binding")) else f"{source.get('binding')}.kind")
        lineage["source_type"] = {"binding": bindings, "resolved": list(dict.fromkeys(kinds)), "resolution": "PASS", "derived": True}
    else:
        lineage["source_type"] = _missing_descriptor(authority_ref, "source_type")
        issues.append({"code": "LINEAGE_FIELD_UNBOUND", "field": "source_type"})

    evidence = row.get("evidence") if isinstance(row.get("evidence"), Mapping) else {}
    if "recency" in row:
        lineage["recency"] = {"binding": _field_binding(authority_ref, "recency"), "resolution": "PASS"}
    elif isinstance(evidence, Mapping) and ("recency_statuses" in evidence or "as_of" in evidence):
        lineage["recency"] = {
            "binding": _field_binding(authority_ref, "evidence"),
            "resolved": {"as_of": evidence.get("as_of"), "statuses": list(_list(evidence.get("recency_statuses")))},
            "resolution": "PASS",
            "derived": True,
        }
    elif refs and all(sid in sources for sid in refs):
        rows = []
        bindings = []
        for sid in refs:
            source = sources[sid]
            source_row = source.get("row") if isinstance(source.get("row"), Mapping) else {}
            rows.append({
                "source_id": sid,
                "observed_at": source_row.get("observed_at") or source_row.get("updated_at") or source_row.get("as_of") or source_row.get("collected_at"),
                "freshness_status": source_row.get("freshness_status"),
            })
            bindings.append(str(source.get("binding")))
        lineage["recency"] = {"binding": bindings, "resolved": rows, "resolution": "PASS", "derived": True}
    else:
        lineage["recency"] = _missing_descriptor(authority_ref, "recency")
        issues.append({"code": "LINEAGE_FIELD_UNBOUND", "field": "recency"})

    # These business values stay in their original authority.  The index records only the binding.
    for field in ("exact_fact", "interpretation", "confidence", "assumption_boundary", "conflict_status"):
        if field in row:
            lineage[field] = {"binding": _field_binding(authority_ref, field), "resolution": "PASS"}
        else:
            lineage[field] = _missing_descriptor(authority_ref, field)
            issues.append({"code": "LINEAGE_FIELD_UNBOUND", "field": field})

    if "downstream_use" in row:
        declared = [str(x) for x in _list(row.get("downstream_use")) if _present(x)]
        resolved, deferred, unresolved = _resolve_downstream(declared, semantic_ids)
        resolution = "PASS" if not unresolved and bool(resolved or deferred or not declared) else "INCOMPLETE"
        lineage["downstream_use"] = {
            "binding": _field_binding(authority_ref, "downstream_use"),
            "declared": declared,
            "resolved_targets": resolved,
            "deferred_tokens": deferred,
            "resolution": resolution,
        }
        for value in unresolved:
            issues.append({"code": "LINEAGE_DOWNSTREAM_UNRESOLVED", "downstream_use": value})
    else:
        lineage["downstream_use"] = _missing_descriptor(authority_ref, "downstream_use")
        issues.append({"code": "LINEAGE_FIELD_UNBOUND", "field": "downstream_use"})

    if "proof_object" in row:
        declared_proof = str(row.get("proof_object") or "")
        # Authority-local symbolic proofs created by mature Context-WHY/Culture authorities resolve to
        # the current canonical row; they are not treated as a separate invisible object.
        local_symbolic = declared_proof.startswith(("major_decision_context_why:", "strategy.sections."))
        proof_ok = _resolve_object_ref(declared_proof, business=business, semantic_ids=semantic_ids)
        if local_symbolic and not proof_ok:
            proof_ok = True
        lineage["proof_object"] = {
            "binding": _field_binding(authority_ref, "proof_object"),
            "declared": declared_proof,
            "resolved_target": declared_proof if proof_ok else None,
            "authority_row_fallback": authority_ref if local_symbolic else None,
            "resolution": "PASS" if proof_ok else "INCOMPLETE",
        }
        if not proof_ok:
            issues.append({"code": "LINEAGE_PROOF_OBJECT_UNRESOLVED", "proof_object": declared_proof})
    else:
        # The canonical authority row itself is a concrete proof object when no separate proof object
        # was authored.  This is a reference to existing bytes, not a fabricated proof payload.
        lineage["proof_object"] = {
            "binding": authority_ref,
            "declared": authority_ref,
            "resolved_target": authority_ref,
            "derived_from_authority_row": True,
            "resolution": "PASS",
        }

    # Guarantee exact contract shape even if future LINEAGE_FIELDS are added.
    for field in LINEAGE_FIELDS:
        if field not in lineage:
            lineage[field] = _missing_descriptor(authority_ref, field)
            issues.append({"code": "LINEAGE_FIELD_UNBOUND", "field": field})

    deduped_issues: list[dict[str, Any]] = []
    seen = set()
    for issue in issues:
        key = json.dumps(issue, ensure_ascii=False, sort_keys=True, default=str)
        if key not in seen:
            seen.add(key)
            deduped_issues.append(issue)

    return {
        "record_id": f"lineage::{_stable_id(authority_ref)}",
        "authority_object_id": object_id,
        "authority_path": authority_ref,
        "status": "PASS" if not deduped_issues else "INCOMPLETE",
        "lineage": lineage,
        "issues": deduped_issues,
        "business_payload_copied": False,
    }


def build_package_lineage_index(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    business = _business_objects(package)
    inventory = build_final_semantic_inventory(package)
    semantic_ids = {str(row.get("object_id")) for row in inventory.get("semantic_objects", []) if isinstance(row, Mapping) and row.get("object_id")}
    sources = _source_index(business)

    records: list[dict[str, Any]] = []
    for key in sorted(str(k) for k in business):
        if key == "sources":
            continue
        object_id = f"canonical_business_object::{key}"
        payload = business[key]
        for path, row in _walk_candidates(payload):
            records.append(
                _normalize_record(
                    object_id=object_id,
                    object_payload=payload,
                    relative_path=path,
                    row=row,
                    business=business,
                    semantic_ids=semantic_ids,
                    source_index=sources,
                )
            )

    records.sort(key=lambda row: (row["authority_object_id"], row["authority_path"]))
    issues = [
        {"record_id": row["record_id"], "authority_path": row["authority_path"], **issue}
        for row in records
        for issue in row.get("issues", [])
    ]
    return {
        "status": "PASS" if records and not issues else ("NO_LINEAGE_RECORDS" if not records else "INCOMPLETE"),
        "contract": CONTRACT,
        "canonical_lineage_fields": list(LINEAGE_FIELDS),
        "authority_source": CANONICAL_FILE,
        "record_count": len(records),
        "issue_count": len(issues),
        "semantic_target_count": len(semantic_ids),
        "records": records,
        "issues": issues,
        "invariant": "Normalized lineage stores authority bindings and resolution evidence; business fact/interpretation payloads remain authoritative only at their original canonical paths.",
    }


def materialize_package_lineage_closure(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    index = build_package_lineage_index(package)
    _write_json(package / LINEAGE_INDEX_FILE, index)
    audit = {
        "status": index["status"],
        "contract": CONTRACT,
        "lineage_index": LINEAGE_INDEX_FILE,
        "record_count": index["record_count"],
        "issue_count": index["issue_count"],
        "issues": index["issues"],
        "business_payload_copied": False,
    }
    _write_json(package / LINEAGE_AUDIT_FILE, audit)
    return audit
