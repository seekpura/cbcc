#!/usr/bin/env python3
from pathlib import Path
import sys
from common import load_json, fail, print_report, P0, P1

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
path = root / "source_registry.json"
issues = []

if not path.exists():
    issues.append(fail(P0, "SOURCE_REGISTRY_MISSING", "source_registry.json is required", path))
else:
    data = load_json(path)
    seen = set()
    for i, row in enumerate(data):
        sid = row.get("source_id")
        if not sid:
            issues.append(fail(P0, "SOURCE_ID_MISSING", f"row {i} has no source_id", path))
            continue
        if sid in seen:
            issues.append(fail(P0, "SOURCE_ID_DUPLICATE", sid, path))
        seen.add(sid)
        if row.get("status") == "CONFLICT":
            issues.append(fail(P0, "UNRESOLVED_TRUTH_CONFLICT", sid, path))
        if row.get("status") in {"ASSUMPTION","PENDING"}:
            issues.append(fail(P1, "UNVERIFIED_SOURCE", f"{sid} is {row.get('status')}", path))

sys.exit(print_report(issues))
