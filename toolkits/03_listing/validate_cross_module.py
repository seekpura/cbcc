#!/usr/bin/env python3
from pathlib import Path
import sys, re
from common import load_json, fail, print_report, P0, P1

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
issues = []

src = root / "source_registry.json"
clm = root / "claim_ledger.json"
asset = root / "master_asset_map.json"

source_ids = {x["source_id"] for x in load_json(src)} if src.exists() else set()
claim_ids = {x["claim_id"] for x in load_json(clm)} if clm.exists() else set()

if asset.exists():
    for a in load_json(asset):
        aid = a.get("asset_id", "?")
        for sid in a.get("source_ids", []):
            if sid not in source_ids:
                issues.append(fail(P0, "ASSET_SOURCE_UNKNOWN", f"{aid}: {sid}", asset))
        for cid in a.get("claim_ids", []):
            if cid not in claim_ids:
                issues.append(fail(P0, "ASSET_CLAIM_UNKNOWN", f"{aid}: {cid}", asset))
        if a.get("product_fidelity") == "LOCKED_PIXEL" and a.get("production_mode") == "AI_GENERATIVE":
            issues.append(fail(P0, "LOCKED_PIXEL_GENERATIVE_CONFLICT", aid, asset))

# Optional prompt scan.
assets_dir = root / "assets"
if assets_dir.exists():
    risky = re.compile(r"\b(best|no\.?1|guaranteed|100% effective|clinically proven)\b", re.I)
    for p in assets_dir.rglob("*.txt"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        if risky.search(text):
            issues.append(fail(P1, "PROMPT_RISK_PHRASE", "review unverified hard-claim language", p))

sys.exit(print_report(issues))
