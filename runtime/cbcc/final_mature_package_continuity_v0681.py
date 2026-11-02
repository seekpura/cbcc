from __future__ import annotations

"""Final-byte mature package continuity for Phase 7.

The mature core-package contract already exists in full_delivery_depth_v3.audit_host_full_package.
This module reuses that checker after all later projections have mutated the package, validates paths
already declared by DELIVERY_MANIFEST, and only then rebuilds the definitive ZIP.
"""

from pathlib import Path
from typing import Any, Mapping
import json

from .full_delivery_depth_v3 import audit_host_full_package
from .full_package_semantic_closure_v0681 import (
    AUDIT_FILE,
    CANONICAL_FILE,
    DELIVERY_MANIFEST_FILE,
    _rebuild_manifest_and_zip,
)

CONTRACT = "PHASE7_FINAL_BYTE_MATURE_PACKAGE_CONTINUITY_V0681"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _manifest_declared_package_paths(manifest: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Discover top-level manifest values that declare in-package files/directories.

    This is not a second core-file registry. The core mature outputs stay authoritative in
    audit_host_full_package; this only verifies that paths already promised by the manifest still
    resolve against the final package bytes.
    """
    rows: list[tuple[str, str]] = []
    for key, raw in manifest.items():
        if key in {"package_dir", "zip_path"} or not isinstance(raw, str):
            continue
        value = raw.strip()
        if not value or "://" in value:
            continue
        path = Path(value)
        if path.is_absolute():
            continue
        suffix = path.suffix.lower()
        if value.endswith("/") or suffix in {".json", ".md", ".html", ".txt", ".yaml", ".yml"}:
            rows.append((str(key), value))
    return rows


def _canonical_listing_required(package: Path, manifest: Mapping[str, Any]) -> bool:
    declared = manifest.get("listing_upload_ready")
    if isinstance(declared, str) and declared.strip():
        return True

    payload = _read_json(package / CANONICAL_FILE)
    business = payload.get("canonical_business_objects") if isinstance(payload.get("canonical_business_objects"), Mapping) else {}
    human = business.get("human_delivery") if isinstance(business.get("human_delivery"), Mapping) else {}
    task_scope = human.get("task_scope") if isinstance(human.get("task_scope"), Mapping) else {}
    if task_scope.get("listing_active") is True:
        return True

    inactive = {"", "NOT_ACTIVE", "NOT_NEEDED", "MISSING_INPUT", "TO_VERIFY", "INACTIVE"}
    for key in ("listing", "listing_upload", "listing_ready"):
        value = human.get(key)
        if isinstance(value, Mapping):
            if str(value.get("status") or "").upper() not in inactive:
                return True
        elif value not in (None, "", [], {}, False):
            return True
    return False


def audit_final_mature_package_continuity(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    base = audit_host_full_package(package)
    issues = [dict(row) for row in (base.get("issues") or []) if isinstance(row, Mapping)]

    manifest = _read_json(package / DELIVERY_MANIFEST_FILE)
    declared_checks: list[dict[str, Any]] = []
    for field, relative in _manifest_declared_package_paths(manifest):
        resolved = package / relative
        exists = resolved.exists()
        declared_checks.append({"manifest_field": field, "path": relative, "exists": exists})
        if not exists:
            issues.append(
                {
                    "code": "FINAL_MATURE_DECLARED_PATH_MISSING",
                    "manifest_field": field,
                    "path": relative,
                }
            )

    listing_required = _canonical_listing_required(package, manifest)
    listing_path = str(manifest.get("listing_upload_ready") or "01_LISTING_UPLOAD_READY.md")
    if listing_required and not (package / listing_path).exists():
        issues.append({"code": "FINAL_MATURE_LISTING_OUTPUT_MISSING", "path": listing_path})

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for issue in issues:
        signature = json.dumps(issue, ensure_ascii=False, sort_keys=True, default=str)
        if signature not in seen:
            seen.add(signature)
            deduped.append(issue)

    return {
        "status": "PASS" if not deduped else "INCOMPLETE",
        "contract": CONTRACT,
        "checker": "runtime.cbcc.full_delivery_depth_v3.audit_host_full_package",
        "core_contract_reused": True,
        "final_package_bytes": True,
        "base_mature_audit_status": base.get("status"),
        "listing_required": listing_required,
        "listing_path": listing_path if listing_required else None,
        "declared_path_checks": declared_checks,
        "issues": deduped,
        "invariant": "Final Phase-7 PASS reuses the mature Host/FULL package checker on final bytes; canonical semantic inventory alone cannot satisfy mature package continuity.",
    }


def finalize_final_mature_package_continuity(
    package_dir: Path | str,
    *,
    semantic_result: Mapping[str, Any],
    zip_path: Path | str | None = None,
) -> dict[str, Any]:
    package = Path(package_dir)
    mature = audit_final_mature_package_continuity(package)
    mature_status = str(mature.get("status") or "INCOMPLETE")

    audit_path = package / AUDIT_FILE
    audit = _read_json(audit_path)
    existing_issues = [dict(row) for row in (audit.get("issues") or []) if isinstance(row, Mapping)]
    mature_issues = [dict(row) for row in (mature.get("issues") or []) if isinstance(row, Mapping)]
    combined = existing_issues + mature_issues
    audit["final_mature_package_continuity"] = mature_status
    audit["final_mature_package_audit"] = mature
    audit["status"] = "PASS" if not combined else "INCOMPLETE"
    audit["issues"] = combined
    audit["phase7_source_closure"] = "PASS" if not combined else "INCOMPLETE"
    _write_json(audit_path, audit)

    manifest_path = package / DELIVERY_MANIFEST_FILE
    manifest = _read_json(manifest_path)
    manifest["final_mature_package_continuity"] = mature_status
    workspace = dict(manifest.get("workspace_contract") or {})
    workspace.update(
        {
            "final_mature_package_continuity": mature_status,
            "final_mature_package_checker_reused": "runtime.cbcc.full_delivery_depth_v3.audit_host_full_package",
        }
    )
    manifest["workspace_contract"] = workspace
    _write_json(manifest_path, manifest)

    if mature_status != "PASS":
        raise RuntimeError(
            "BLOCKED Phase 7 mature package continuity failed: "
            + json.dumps(mature_issues, ensure_ascii=False)
        )

    final_zip = Path(zip_path) if zip_path is not None else None
    final_manifest = _rebuild_manifest_and_zip(package, final_zip, manifest)
    result = dict(semantic_result)
    result.update(
        {
            "status": "PASS",
            "final_mature_package_continuity": "PASS",
            "final_mature_package_contract": CONTRACT,
            "manifest": final_manifest,
        }
    )
    return result
