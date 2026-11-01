#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
_BASELINE_CHECKER = Path(__file__).with_name("check_current_release_package_baseline.py")

_spec = importlib.util.spec_from_file_location("cbcc_current_release_checker_baseline", _BASELINE_CHECKER)
if not _spec or not _spec.loader:
    raise RuntimeError(f"Unable to load baseline CURRENT release checker: {_BASELINE_CHECKER}")
_baseline = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_baseline)

LOCKED_REQUIREMENT_RANGE = "REQ-061..REQ-090"
CANONICAL_SAME_SOURCE_INVARIANT = "Canonical same-source invariant"
LOCKED_AUTHORITY_PATHS = (
    "references/CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md",
    "references/LOCKED_IMPLEMENTATION_PLAN_CURRENT.md",
    "references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json",
    "references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md",
)
BASELINE_PROOF_TOKENS = (
    "STRATEGY_CULTURE_MATERIALIZATION_TOKEN_MISSING",
    "product_truth_audit_table",
    "assumption_decision_log",
    "visual_execution_checklist",
    "output_self_check_rows",
)

current_authority_version = _baseline.current_authority_version
current_version_family = _baseline.current_version_family
validate_override_release_version = _baseline.validate_override_release_version
_BASE_REQUIRED_RELEASE_PATHS = _baseline.required_release_paths


def required_release_paths() -> list[str]:
    """Extend the mature CURRENT checker with locked REQ-061..090 and K01 regression authorities."""
    rows = list(_BASE_REQUIRED_RELEASE_PATHS())
    for rel in LOCKED_AUTHORITY_PATHS + ("scripts/check_current_release_package_baseline.py",):
        if rel not in rows:
            rows.append(rel)
    return rows


# The mature audit calls its module-global required_release_paths(). Rebind that one seam only,
# leaving every existing v0.6.75 audit rule byte-preserved in the baseline core.
_baseline.required_release_paths = required_release_paths


def audit(plugin_zip: Path) -> dict[str, Any]:
    return _baseline.audit(plugin_zip)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a CBCC plugin ZIP against the mature CURRENT release checker plus "
            f"{LOCKED_REQUIREMENT_RANGE} / {CANONICAL_SAME_SOURCE_INVARIANT} authorities."
        )
    )
    parser.add_argument("plugin_zip")
    args = parser.parse_args()
    result = audit(Path(args.plugin_zip))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
