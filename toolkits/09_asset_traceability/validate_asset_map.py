#!/usr/bin/env python3
from pathlib import Path
import sys
from common import load_json, fail, print_report, P0, P1

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
path = root / "master_asset_map.json"
issues = []

if not path.exists():
    issues.append(fail(P0, "ASSET_MAP_MISSING", "master_asset_map.json is required", path))
else:
    assets = load_json(path)
    seen = set()
    signatures = {}
    for i, a in enumerate(assets):
        aid = a.get("asset_id")
        if not aid:
            issues.append(fail(P0, "ASSET_ID_MISSING", f"row {i}", path)); continue
        if aid in seen:
            issues.append(fail(P0, "ASSET_ID_DUPLICATE", aid, path))
        seen.add(aid)
        for req in ["consumer_question","strategic_job","production_mode","product_fidelity","status","priority"]:
            if not a.get(req):
                issues.append(fail(P0, "ASSET_FIELD_MISSING", f"{aid}: {req}", path))
        if a.get("status") == "ACTIVATE" and not a.get("source_ids"):
            issues.append(fail(P0, "ACTIVE_ASSET_NO_SOURCE", aid, path))
        sig = (a.get("consumer_question","").strip().lower(), a.get("strategic_job","").strip().lower())
        if sig in signatures:
            issues.append(fail(P1, "POSSIBLE_DUPLICATE_ASSET", f"{aid} overlaps {signatures[sig]}", path))
        else:
            signatures[sig] = aid

sys.exit(print_report(issues))
