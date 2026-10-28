#!/usr/bin/env python3
from pathlib import Path
import sys
from common import load_json, fail, print_report, P0, P1

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
src_path = root / "source_registry.json"
clm_path = root / "claim_ledger.json"
issues = []

if not clm_path.exists():
    issues.append(fail(P0, "CLAIM_LEDGER_MISSING", "claim_ledger.json is required", clm_path))
else:
    sources = {x["source_id"] for x in load_json(src_path)} if src_path.exists() else set()
    claims = load_json(clm_path)
    seen = set()
    for i, c in enumerate(claims):
        cid = c.get("claim_id")
        if not cid:
            issues.append(fail(P0, "CLAIM_ID_MISSING", f"row {i}", clm_path))
            continue
        if cid in seen:
            issues.append(fail(P0, "CLAIM_ID_DUPLICATE", cid, clm_path))
        seen.add(cid)
        for sid in c.get("source_ids", []):
            if sid not in sources:
                issues.append(fail(P0, "CLAIM_SOURCE_UNKNOWN", f"{cid} references missing {sid}", clm_path))
        if c.get("claim_type") == "PROHIBITED_CLAIM" and c.get("status") == "ACTIVE":
            issues.append(fail(P0, "PROHIBITED_CLAIM_ACTIVE", cid, clm_path))
        if c.get("evidence_level") == "C" and c.get("status") == "ACTIVE":
            issues.append(fail(P1, "C_LEVEL_ACTIVE", f"{cid} is C-level; do not use as hard claim", clm_path))

sys.exit(print_report(issues))
