from __future__ import annotations

"""Phase 7 final-package semantic closure.

Earlier materialization layers remain responsible for creating the package.  This module runs only on
final package bytes and answers three different questions without conflating them:

1. Which canonical business / production objects actually exist, and what are their semantic hashes?
2. Would a Host-native package and Runtime package contain the same semantic objects?
3. Has real Provider Result -> Review -> Local Revision -> lineage/hash evidence actually happened?

The last two are deliberately fail-honest.  A single Runtime export cannot prove installed Host-native
parity, and a materialized provider job/template cannot prove actual-output QA.
"""

from pathlib import Path
from typing import Any, Mapping
import hashlib
import json
import zipfile

CANONICAL_FILE = "CANONICAL_HUMAN_DATA.json"
OBJECT_MANIFEST_FILE = "FULL_DELIVERY_OBJECT_MANIFEST.json"
AUDIT_FILE = "FULL_MATERIALIZATION_AUDIT.json"
DELIVERY_MANIFEST_FILE = "DELIVERY_MANIFEST.json"
CONTRACT = "PHASE7_FINAL_PACKAGE_SEMANTIC_CLOSURE_V0681"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _semantic_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical_semantic_rows(package: Path) -> list[dict[str, Any]]:
    payload = _read_json(package / CANONICAL_FILE)
    business = payload.get("canonical_business_objects") if isinstance(payload.get("canonical_business_objects"), Mapping) else {}
    rows: list[dict[str, Any]] = []
    for key in sorted(str(k) for k in business):
        value = business[key]
        rows.append(
            {
                "object_id": f"canonical_business_object::{key}",
                "object_kind": "CANONICAL_BUSINESS_OBJECT",
                "semantic_sha256": _semantic_sha(value),
                "source_path": f"{CANONICAL_FILE}#canonical_business_objects.{key}",
            }
        )
    return rows


def _asset_semantic_rows(package: Path) -> list[dict[str, Any]]:
    root = package / "asset_packages"
    if not root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for asset_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        lineage_path = asset_dir / "CANONICAL_LINEAGE.json"
        if lineage_path.exists():
            lineage = _read_json(lineage_path)
            semantic = lineage if lineage else {"file_sha256": _file_sha(lineage_path)}
            source = str(lineage_path.relative_to(package)).replace("\\", "/")
        else:
            semantic_files: list[dict[str, Any]] = []
            for name in (
                "00_asset_manifest.yaml",
                "12_design_card.json",
                "13_prompt_contract.json",
                "14_visible_copy_block.json",
                "15_production_assembly_notes.json",
            ):
                path = asset_dir / name
                if path.exists() and path.is_file():
                    semantic_files.append({"path": name, "sha256": _file_sha(path)})
            if not semantic_files:
                continue
            semantic = semantic_files
            source = str(asset_dir.relative_to(package)).replace("\\", "/")
        rows.append(
            {
                "object_id": f"production_asset::{asset_dir.name}",
                "object_kind": "PRODUCTION_ASSET_PACKAGE",
                "semantic_sha256": _semantic_sha(semantic),
                "source_path": source,
            }
        )
    return rows


def _semantic_rows(package: Path) -> list[dict[str, Any]]:
    rows = _canonical_semantic_rows(package) + _asset_semantic_rows(package)
    return sorted(rows, key=lambda row: row["object_id"])


def _signature(rows: list[dict[str, Any]]) -> str:
    compact = [{"object_id": row["object_id"], "semantic_sha256": row["semantic_sha256"]} for row in rows]
    return _semantic_sha(compact)


def build_final_semantic_inventory(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    rows = _semantic_rows(package)
    return {
        "status": "FULL_DELIVERY_OBJECT_MANIFEST",
        "contract": CONTRACT,
        "inventory_source": "FINAL_PACKAGE_BYTES",
        "hand_listed_object_registry": False,
        "semantic_object_count": len(rows),
        "semantic_signature_sha256": _signature(rows),
        "semantic_objects": rows,
        "invariant": "Every canonical business object present in the final canonical payload is automatically accounted for; new object families cannot disappear behind a static manifest list.",
    }


def audit_final_semantic_inventory(package_dir: Path | str) -> list[dict[str, Any]]:
    package = Path(package_dir)
    expected = build_final_semantic_inventory(package)
    recorded = _read_json(package / OBJECT_MANIFEST_FILE)
    if not recorded:
        return [{"code": "FINAL_SEMANTIC_OBJECT_MANIFEST_MISSING", "path": OBJECT_MANIFEST_FILE}]
    expected_rows = {row["object_id"]: row for row in expected["semantic_objects"]}
    recorded_rows = {
        str(row.get("object_id")): row
        for row in (recorded.get("semantic_objects") or [])
        if isinstance(row, Mapping) and row.get("object_id")
    }
    issues: list[dict[str, Any]] = []
    for object_id, row in expected_rows.items():
        got = recorded_rows.get(object_id)
        if got is None:
            issues.append({"code": "FINAL_SEMANTIC_OBJECT_UNACCOUNTED", "object_id": object_id})
            continue
        if str(got.get("semantic_sha256") or "") != str(row.get("semantic_sha256") or ""):
            issues.append(
                {
                    "code": "FINAL_SEMANTIC_OBJECT_HASH_DRIFT",
                    "object_id": object_id,
                    "expected": row.get("semantic_sha256"),
                    "recorded": got.get("semantic_sha256"),
                }
            )
    for object_id in sorted(set(recorded_rows) - set(expected_rows)):
        issues.append({"code": "FINAL_SEMANTIC_OBJECT_ORPHANED", "object_id": object_id})
    if str(recorded.get("semantic_signature_sha256") or "") != expected["semantic_signature_sha256"]:
        issues.append(
            {
                "code": "FINAL_SEMANTIC_SIGNATURE_DRIFT",
                "expected": expected["semantic_signature_sha256"],
                "recorded": recorded.get("semantic_signature_sha256"),
            }
        )
    return issues


def compare_export_semantics(host_package_dir: Path | str, runtime_package_dir: Path | str) -> dict[str, Any]:
    host = build_final_semantic_inventory(host_package_dir)
    runtime = build_final_semantic_inventory(runtime_package_dir)
    host_rows = {row["object_id"]: row["semantic_sha256"] for row in host["semantic_objects"]}
    runtime_rows = {row["object_id"]: row["semantic_sha256"] for row in runtime["semantic_objects"]}
    host_ids = set(host_rows)
    runtime_ids = set(runtime_rows)
    changed = sorted(object_id for object_id in host_ids & runtime_ids if host_rows[object_id] != runtime_rows[object_id])
    host_only = sorted(host_ids - runtime_ids)
    runtime_only = sorted(runtime_ids - host_ids)
    status = "PASS" if not (changed or host_only or runtime_only) else "INCOMPLETE"
    return {
        "status": status,
        "comparison_contract": "HOST_NATIVE_RUNTIME_SEMANTIC_OBJECT_SIGNATURE_PARITY",
        "host_semantic_signature_sha256": host["semantic_signature_sha256"],
        "runtime_semantic_signature_sha256": runtime["semantic_signature_sha256"],
        "changed_object_ids": changed,
        "host_only_object_ids": host_only,
        "runtime_only_object_ids": runtime_only,
        "file_layout_is_authority": False,
    }


def _review_items(package: Path) -> dict[str, dict[str, Any]]:
    delivery = _read_json(package / "review_workspace/delivery_manifest.json")
    return {
        str(row.get("item_id")): dict(row)
        for row in (delivery.get("items") or [])
        if isinstance(row, Mapping) and row.get("item_id")
    }


def _revision_rows(package: Path) -> list[dict[str, Any]]:
    index = _read_json(package / "local_revisions/LOCAL_REVISION_INDEX.json")
    return [dict(row) for row in (index.get("revisions") or []) if isinstance(row, Mapping)]


def audit_actual_output_boundary(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    jobs = _read_json(package / "provider_jobs/PROVIDER_JOB_INDEX.json")
    job_rows = [dict(row) for row in (jobs.get("jobs") or []) if isinstance(row, Mapping)]
    production = _read_json(package / "supporting_analysis/production_run.json")
    production_rows = {
        str(row.get("asset_id")): dict(row)
        for row in (production.get("assets") or [])
        if isinstance(row, Mapping) and row.get("asset_id")
    }
    review_items = _review_items(package)
    revisions = _revision_rows(package)
    rows: list[dict[str, Any]] = []

    for job in job_rows:
        aid = str(job.get("asset_id") or "")
        result_path = package / "provider_jobs" / aid / "result.json"
        result = _read_json(result_path)
        run_row = production_rows.get(aid, {})
        receipt = result.get("production_receipt") if isinstance(result.get("production_receipt"), Mapping) else {}
        artifacts = [row for row in (receipt.get("output_artifacts") or []) if isinstance(row, Mapping)]
        receipt_artifact_hashes = [str(row.get("sha256") or "") for row in artifacts if row.get("sha256")]
        result_pass = bool(result) and str(run_row.get("result_status") or "").upper() == "PASS" and bool(receipt_artifact_hashes)

        output_review = review_items.get(f"OUTPUT-{aid}", {})
        review_pass = str(output_review.get("review_status") or "").upper() == "ACCEPTED"

        asset_revisions = [row for row in revisions if str(row.get("asset_id") or "") == aid]
        accepted_revisions = [row for row in asset_revisions if str(row.get("status") or "").upper() == "ACCEPTED" and row.get("revised_output_hash")]
        revision_pass = False
        revision_hashes: list[str] = []
        for revision in accepted_revisions:
            rid = str(revision.get("revision_id") or "")
            revision_review = review_items.get(f"REVISION-OUTPUT-{rid}", {})
            if str(revision_review.get("review_status") or "").upper() == "ACCEPTED":
                revision_pass = True
                revision_hashes.append(str(revision.get("revised_output_hash")))

        lineage_pass = bool(
            result_pass
            and run_row.get("production_receipt_hash")
            and receipt_artifact_hashes
            and revision_hashes
        )
        rows.append(
            {
                "asset_id": aid,
                "job_id": job.get("job_id"),
                "provider_result": "PASS" if result_pass else "MISSING",
                "review": "PASS" if review_pass else "MISSING",
                "local_revision": "PASS" if revision_pass else "MISSING",
                "lineage_hash": "PASS" if lineage_pass else "MISSING",
                "production_receipt_hash": run_row.get("production_receipt_hash"),
                "provider_output_sha256": receipt_artifact_hashes,
                "revised_output_sha256": revision_hashes,
            }
        )

    proven = bool(rows) and all(
        row["provider_result"] == "PASS"
        and row["review"] == "PASS"
        and row["local_revision"] == "PASS"
        and row["lineage_hash"] == "PASS"
        for row in rows
    )
    return {
        "status": "E2E_PROVEN" if proven else "E2E_PENDING",
        "contract": "PROVIDER_RESULT_REVIEW_LOCAL_REVISION_LINEAGE_HASH",
        "provider_job_count": len(job_rows),
        "assets": rows,
        "planning_or_job_materialization_is_actual_output": False,
        "rule": "Provider job planning/templates never satisfy actual-output QA. E2E_PROVEN requires real result receipt/output hashes, accepted output review, accepted local revision review, and revision lineage hash for every materialized provider job.",
    }


def _rebuild_manifest_and_zip(package: Path, zip_path: Path | None, manifest: dict[str, Any]) -> dict[str, Any]:
    manifest_path = package / DELIVERY_MANIFEST_FILE
    files: list[dict[str, Any]] = []
    for path in sorted(package.rglob("*")):
        if path.is_file() and path.name != DELIVERY_MANIFEST_FILE:
            files.append(
                {
                    "path": str(path.relative_to(package)).replace("\\", "/"),
                    "sha256": _file_sha(path),
                    "bytes": path.stat().st_size,
                }
            )
    manifest["files"] = files
    manifest.pop("zip_sha256", None)
    manifest.pop("zip_bytes", None)
    _write_json(manifest_path, manifest)

    if zip_path is None:
        return manifest
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    # Two passes preserve the established CBCC convention: ZIP contains a manifest with all semantic
    # closure fields, while the disk manifest records the latest ZIP hash/bytes without pretending a
    # self-referential ZIP hash can be embedded in the same exact ZIP bytes.
    for _ in range(2):
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(package.rglob("*")):
                if path.is_file():
                    archive.write(path, Path(package.name) / path.relative_to(package))
        manifest["zip_sha256"] = _file_sha(zip_path)
        manifest["zip_bytes"] = zip_path.stat().st_size
        _write_json(manifest_path, manifest)
    return manifest


def materialize_final_package_semantics(
    package_dir: Path | str,
    *,
    zip_path: Path | str | None = None,
    host_package_dir: Path | str | None = None,
) -> dict[str, Any]:
    package = Path(package_dir)
    if not package.exists():
        raise FileNotFoundError(f"Final delivery package missing: {package}")
    if not _read_json(package / CANONICAL_FILE):
        raise RuntimeError(f"BLOCKED Phase 7 final semantic closure: {CANONICAL_FILE} missing or invalid")

    upstream_audit = _read_json(package / AUDIT_FILE)
    inventory = build_final_semantic_inventory(package)
    _write_json(package / OBJECT_MANIFEST_FILE, inventory)
    semantic_issues = audit_final_semantic_inventory(package)
    actual_output = audit_actual_output_boundary(package)
    if host_package_dir is None:
        parity: dict[str, Any] = {
            "status": "E2E_PENDING_INSTALLED_HOST_EXPORT",
            "comparison_contract": "HOST_NATIVE_RUNTIME_SEMANTIC_OBJECT_SIGNATURE_PARITY",
            "runtime_semantic_signature_sha256": inventory["semantic_signature_sha256"],
            "reason": "No independently materialized Host-native package was supplied to this finalizer. Source-level comparator exists, but installed-host parity is not fabricated from one Runtime package.",
        }
    else:
        parity = compare_export_semantics(host_package_dir, package)

    audit = {
        "status": "PASS" if not semantic_issues else "INCOMPLETE",
        "contract": CONTRACT,
        "final_semantic_inventory": "PASS" if not semantic_issues else "INCOMPLETE",
        "final_semantic_signature_sha256": inventory["semantic_signature_sha256"],
        "semantic_object_count": inventory["semantic_object_count"],
        "host_native_runtime_export_parity": parity.get("status"),
        "host_runtime_parity": parity,
        "actual_output_boundary_status": actual_output["status"],
        "actual_output_boundary": actual_output,
        "issues": semantic_issues,
        "upstream_full_materialization_audit": upstream_audit if upstream_audit.get("contract") != CONTRACT else upstream_audit.get("upstream_full_materialization_audit", {}),
        "phase7_source_closure": "PASS" if not semantic_issues else "INCOMPLETE",
        "e2e_boundary": "E2E_PROVEN" if actual_output["status"] == "E2E_PROVEN" and parity.get("status") == "PASS" else "E2E_PENDING",
    }
    _write_json(package / AUDIT_FILE, audit)
    if semantic_issues:
        raise RuntimeError("BLOCKED Phase 7 final semantic inventory failed: " + json.dumps(semantic_issues, ensure_ascii=False))

    delivery = _read_json(package / DELIVERY_MANIFEST_FILE)
    delivery.update(
        {
            "full_delivery_object_manifest": OBJECT_MANIFEST_FILE,
            "full_materialization_audit": AUDIT_FILE,
            "phase7_final_semantic_closure": "PASS",
            "final_semantic_signature_sha256": inventory["semantic_signature_sha256"],
            "host_native_runtime_export_parity": parity.get("status"),
            "actual_output_boundary_status": actual_output["status"],
            "phase7_e2e_boundary": audit["e2e_boundary"],
        }
    )
    workspace = dict(delivery.get("workspace_contract") or {})
    workspace.update(
        {
            "phase7_final_semantic_closure": "PASS",
            "final_semantic_object_inventory_dynamic": True,
            "host_runtime_semantic_comparator_implemented": True,
            "host_native_runtime_export_parity": parity.get("status"),
            "actual_output_boundary_status": actual_output["status"],
            "provider_planning_is_actual_output": False,
        }
    )
    delivery["workspace_contract"] = workspace
    final_zip = Path(zip_path) if zip_path is not None else None
    final_manifest = _rebuild_manifest_and_zip(package, final_zip, delivery)
    return {
        "status": "PASS",
        "contract": CONTRACT,
        "final_semantic_signature_sha256": inventory["semantic_signature_sha256"],
        "semantic_object_count": inventory["semantic_object_count"],
        "host_native_runtime_export_parity": parity.get("status"),
        "actual_output_boundary_status": actual_output["status"],
        "phase7_e2e_boundary": audit["e2e_boundary"],
        "manifest": final_manifest,
    }
