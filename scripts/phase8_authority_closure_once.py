#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = "references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE8_PROVIDER_ACTUAL_OUTPUT.json"


def patch_ledger() -> None:
    path = ROOT / "references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json"
    ledger = json.loads(path.read_text(encoding="utf-8"))
    req90 = next(row for row in ledger["new_requirements"] if row.get("req") == "REQ-090")
    req90["status"] = (
        "PARTIAL_PHASE7_SOURCE_PACKAGE_CLOSURE_AND_PHASE8_PROVIDER_BOUNDARY_ACTUAL_OUTPUT_E2E_PROVEN_"
        "FRESH_K01_PHASE10_AND_AUTHENTICATED_INSTALLED_HOST_PHASE11_PENDING"
    )
    ledger.setdefault("phase_status", {})["8"] = (
        "PASS_PHASE8_PROVIDER_RESULT_REVIEW_LOCAL_REVISION_HASH_LINEAGE_E2E_PROVEN_AT_PROVIDER_EXECUTION_BOUNDARY"
    )
    ledger.setdefault("phase_evidence", {})["8"] = {
        "status": "PASS_PHASE8_PROVIDER_RESULT_REVIEW_LOCAL_REVISION_HASH_LINEAGE_E2E_PROVEN_AT_PROVIDER_EXECUTION_BOUNDARY",
        "requirements": ["REQ-038", "REQ-039", "REQ-040", "REQ-041", "REQ-090"],
        "consumer_map": MAP_PATH,
        "proof_objects": [
            "runtime/cbcc/provider_surface.py",
            "runtime/cbcc/cli.py",
            "runtime/cbcc/provider_bridge.py",
            "runtime/cbcc/provider_executor.py",
            "runtime/cbcc/production.py",
            "runtime/cbcc/review.py",
            "runtime/cbcc/learning_loop.py",
            "runtime/cbcc/full_package_semantic_closure_v0681.py",
            "tests/test_v0682_phase8_local_revision_provider_execution.py",
            "tests/test_v0682_phase8_revision_execute_cli.py",
            "tests/test_v0682_phase8_actual_output_e2e.py",
            ".github/workflows/v0682-phase8-provider-actual-output.yml",
        ],
        "red_evidence": {
            "local_revision_execution": {
                "run": 41444026742,
                "failure": "ProviderExecutionSurface had no execute_local_revision",
            },
            "revision_execute_cli": {
                "run": 41444302599,
                "failure": "argparse rejected revision-execute",
            },
        },
        "focused_green": {
            "run": 41445447994,
            "result": "SUCCESS; actual-output lifecycle reached E2E_PROVEN",
        },
        "cross_scope_green": {
            "run": 41445805192,
            "result": "SUCCESS; v0.6.16 host surface + Phase 8 suites together",
        },
        "verified_behavior": [
            "root and local-revision jobs execute through the same provider adapter/executor boundary",
            "actual output bytes and production-receipt SHA256 are materialized and verified",
            "locked/reference product routes require provider quality/reference/source-hash evidence before COMPLETE",
            "human output review and local-revision output review remain explicit and independently addressable",
            "bounded local revision preserves changed field/layer scope and revised-output hash lineage",
            "Phase 7 audit_actual_output_boundary reaches E2E_PROVEN only after the complete lifecycle",
        ],
        "honesty_boundary": {
            "external_vendor_network_call": "NOT_CLAIMED",
            "fresh_k01_full_public_path": "PENDING_PHASE10",
            "authenticated_installed_host_native_export": "PENDING_PHASE11",
        },
        "next_phase": "PHASE9_REQUIREMENT_CONSUMER_MAP_001_090",
    }
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"missing patch marker: {label}")
    return text.replace(old, new, 1)


def patch_matrix() -> None:
    path = ROOT / "references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md"
    text = path.read_text(encoding="utf-8")
    replacements = [
        (
            "| REQ-038 | Provider→Result→Review→Revision→hash | Provider bridge/executor/transport + production + Review | E2E_PENDING |",
            "| REQ-038 | Provider→Result→Review→Revision→hash | Provider bridge/executor/transport + production + Review + nested revision execution | PASS_PHASE8_PROVIDER_BOUNDARY_E2E_PROVEN |",
            "REQ-038",
        ),
        (
            "| REQ-039 | Actual-output QA | Review + production + real-output package audit | E2E_PENDING |",
            "| REQ-039 | Actual-output QA | actual provider-boundary bytes + receipt/hash + machine evidence + human Review + package audit | PASS_PHASE8_ACTUAL_OUTPUT_QA_E2E_PROVEN |",
            "REQ-039",
        ),
        (
            "| REQ-040 | Smallest defect repair | Review + learning loop + production | CONSUMER MAPPED + E2E_PENDING |",
            "| REQ-040 | Smallest defect repair | Review → bounded Local Revision → same provider surface → revised-output review/hash | PASS_PHASE8_SMALLEST_LAYER_LOCAL_REVISION_E2E_PROVEN |",
            "REQ-040",
        ),
        (
            "| REQ-041 | Measurement/learning loop | learning + feedback + experiment | CONSUMER MAPPED + E2E_PENDING |",
            "| REQ-041 | Measurement/learning loop | learning + feedback + experiment + production/review/revision lineage | PARTIAL_PHASE2_MEASUREMENT_PHASE8_REVISION_LINEAGE_VERIFIED_REAL_LEARNING_CYCLE_E2E_PENDING |",
            "REQ-041",
        ),
        (
            "| REQ-090 | FULL package lineage + actual-output boundary | final semantic inventory + REQ-088 lineage + final-byte mature FULL-package continuity + honest Host/Provider actual-output boundary | PHASE7_SOURCE_PACKAGE_CLOSURE_AND_HOST_FALSE_PASS_GUARD_TARGETED_PROOF + REAL_PROVIDER_OUTPUT_PHASE8_PENDING + FRESH_K01_PHASE10_PENDING + INSTALLED_HOST_E2E_PHASE11_PENDING |",
            "| REQ-090 | FULL package lineage + actual-output boundary | final semantic inventory + REQ-088 lineage + final-byte mature FULL-package continuity + Provider Result/Review/Revision/hash boundary | PHASE7_SOURCE_PACKAGE_CLOSURE + PHASE8_PROVIDER_BOUNDARY_ACTUAL_OUTPUT_E2E_PROVEN + FRESH_K01_PHASE10_PENDING + INSTALLED_HOST_E2E_PHASE11_PENDING |",
            "REQ-090",
        ),
    ]
    for old, new, label in replacements:
        text = _replace_once(text, old, new, label)

    text = _replace_once(
        text,
        "Phase 7 source/package closure is now complete at targeted proof level; Fresh K01 FULL, Provider actual-output QA, and authenticated installed-plugin/Host-native readback remain later-phase evidence and are not implied by Phase 6 or Phase 7 source/package closure.",
        "Phase 7 source/package closure is complete at targeted proof level. Phase 8 is now complete at the CBCC provider execution boundary for actual Provider Result bytes → machine evidence → human Review → bounded Local Revision → second Review → receipt/output/revision hash lineage, with the exact package boundary reaching `E2E_PROVEN`. Fresh K01 FULL remains Phase 10 and authenticated installed-plugin/Host-native readback remains Phase 11; external vendor/network execution is not fabricated by this repository CI proof.",
        "intro phase boundary",
    )
    text = _replace_once(
        text,
        "Real Provider Result/Review/Revision actual-output evidence remains Phase 8, Fresh positive K01 FULL remains Phase 10, and authenticated installed-plugin/Host-native readback semantic parity remains Phase 11; none is pulled forward or implied by this Phase 7 closure.",
        "Phase 8 Provider Result/Review/Revision actual-output lifecycle is now closed at the CBCC provider execution boundary with deterministic host-callback provider execution and real materialized output/revision bytes, machine evidence, two explicit human Reviews and hash lineage. This does not claim an external vendor/network call. Fresh positive K01 FULL remains Phase 10, and authenticated installed-plugin/Host-native readback semantic parity remains Phase 11.",
        "current evidence boundary",
    )
    if "## Phase 8 authority" not in text:
        text += (
            "\n\n## Phase 8 authority\n"
            "`REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE8_PROVIDER_ACTUAL_OUTPUT.json` is the Phase 8 machine-readable authority. "
            "Permanent verification runs the Phase 8 E2E suite together with the prior v0.6.16 host-surface regression. "
            "The next locked task is Phase 9 cumulative REQ-001..090 consumer accounting; behavioral K01 and installed-host proofs remain Phases 10 and 11.\n"
        )
    path.write_text(text, encoding="utf-8")


def patch_current_verifier() -> None:
    path = ROOT / ".github/workflows/current-release-verification.yml"
    text = path.read_text(encoding="utf-8")
    if "REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE8_*.json" not in text:
        marker = "      - 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE7_*.json'\n"
        text = _replace_once(
            text,
            marker,
            marker + "      - 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE8_*.json'\n",
            "CURRENT Phase8 map path",
        )
    if "tests/test_v0682_*.py" not in text:
        marker = "      - 'tests/test_v0681_phase7_*.py'\n"
        text = _replace_once(
            text,
            marker,
            marker + "      - 'tests/test_v0616_provider_host_surface.py'\n      - 'tests/test_v0682_*.py'\n",
            "CURRENT Phase8 tests path",
        )
    if "Verify CURRENT Phase 8 Provider actual-output execution" not in text:
        step = (
            "      - name: Verify CURRENT Phase 8 Provider actual-output execution, Review, Local Revision and hash lineage\n"
            "        env: {PYTHONHASHSEED: '0', PYTHONPATH: '.:runtime'}\n"
            "        run: |\n"
            "          python -m pytest -q \\\n"
            "            tests/test_v0616_provider_host_surface.py \\\n"
            "            tests/test_v0682_*.py\n"
        )
        marker = "      - name: Verify prior maturity and CURRENT requirement accounting\n"
        text = _replace_once(text, marker, step + marker, "CURRENT Phase8 step")
    phase7 = (
        "'Phase7 final package semantic inventory + host/runtime comparator contract + actual-output E2E boundary + final export ordering + REQ-088 resolvable lineage authority bindings/no-copy invariant + mature information-audit regression + REQ-090 final-byte mature package continuity'"
    )
    if "Phase8 provider-boundary actual-output bytes" not in text:
        phase8 = (
            phase7
            + ", 'Phase8 provider-boundary actual-output bytes + machine quality/reference evidence + human output Review + bounded Local Revision execution + second Review + production receipt/output/revision hash lineage reaching E2E_PROVEN'"
        )
        text = _replace_once(text, phase7, phase8, "CURRENT verified_by Phase8")
    path.write_text(text, encoding="utf-8")


def validate() -> None:
    ledger = json.loads((ROOT / "references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json").read_text(encoding="utf-8"))
    assert ledger["phase_status"]["8"].startswith("PASS_PHASE8_")
    req90 = next(row for row in ledger["new_requirements"] if row["req"] == "REQ-090")
    assert "PHASE8_PROVIDER_BOUNDARY_ACTUAL_OUTPUT_E2E_PROVEN" in req90["status"]
    matrix = (ROOT / "references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md").read_text(encoding="utf-8")
    assert "PASS_PHASE8_PROVIDER_BOUNDARY_E2E_PROVEN" in matrix
    assert "REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE8_PROVIDER_ACTUAL_OUTPUT.json" in matrix
    workflow = (ROOT / ".github/workflows/current-release-verification.yml").read_text(encoding="utf-8")
    assert "tests/test_v0682_*.py" in workflow
    assert "Verify CURRENT Phase 8 Provider actual-output execution" in workflow


def main() -> int:
    patch_ledger()
    patch_matrix()
    patch_current_verifier()
    validate()
    print(json.dumps({"status": "PASS", "phase": 8, "next": "PHASE9_REQUIREMENT_CONSUMER_MAP_001_090"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
