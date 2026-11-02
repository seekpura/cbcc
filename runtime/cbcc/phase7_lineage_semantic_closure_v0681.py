from __future__ import annotations

"""Final Phase-7 orchestration for REQ-088 lineage + semantic package closure.

Order is intentional: lineage files and their manifest contract are materialized first, then the
existing final semantic closer rebuilds the definitive file list and ZIP.  This prevents a late lineage
artifact from falling outside the final package while keeping the mature semantic/Host/Provider boundary
logic in its existing authority module.
"""

from pathlib import Path
from typing import Any
import json

from .lineage_normalization_v0681 import (
    LINEAGE_AUDIT_FILE,
    LINEAGE_INDEX_FILE,
    materialize_package_lineage_closure,
)
from .full_package_semantic_closure_v0681 import materialize_final_package_semantics

CONTRACT = "PHASE7_REQ088_LINEAGE_PLUS_FINAL_SEMANTIC_CLOSURE_V0681"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def materialize_phase7_lineage_and_semantics(
    package_dir: Path | str,
    *,
    zip_path: Path | str | None = None,
    host_package_dir: Path | str | None = None,
) -> dict[str, Any]:
    package = Path(package_dir)
    lineage = materialize_package_lineage_closure(package)
    lineage_status = str(lineage.get("status") or "INCOMPLETE")
    if lineage_status == "INCOMPLETE":
        raise RuntimeError(
            "BLOCKED Phase 7 REQ-088 lineage closure failed: "
            + json.dumps(lineage.get("issues") or [], ensure_ascii=False)
        )

    manifest_path = package / "DELIVERY_MANIFEST.json"
    manifest = _read_json(manifest_path)
    manifest.update(
        {
            "lineage_closure_status": lineage_status,
            "lineage_closure_index": LINEAGE_INDEX_FILE,
            "lineage_closure_audit": LINEAGE_AUDIT_FILE,
        }
    )
    workspace = dict(manifest.get("workspace_contract") or {})
    workspace.update(
        {
            "req088_resolvable_lineage_closure": lineage_status,
            "lineage_business_payload_copied": False,
            "lineage_contract_source": "information_audit_authority.LINEAGE_FIELDS",
        }
    )
    manifest["workspace_contract"] = workspace
    _write_json(manifest_path, manifest)

    semantic = materialize_final_package_semantics(
        package,
        zip_path=zip_path,
        host_package_dir=host_package_dir,
    )
    result = dict(semantic)
    result.update(
        {
            "orchestration_contract": CONTRACT,
            "lineage_closure_status": lineage_status,
            "lineage_closure_index": LINEAGE_INDEX_FILE,
            "lineage_closure_audit": LINEAGE_AUDIT_FILE,
        }
    )
    return result
