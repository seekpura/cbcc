#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys

root = Path(__file__).resolve().parents[1]
fixture = root / "tests" / "fixtures" / "minimal_valid"

scripts = [
    root / "validators" / "validate_sources.py",
    root / "validators" / "validate_claims.py",
    root / "validators" / "validate_asset_map.py",
    root / "validators" / "validate_cross_module.py",
]

failed = []
for script in scripts:
    p = subprocess.run([sys.executable, str(script), str(fixture)], capture_output=True, text=True)
    print(f"== {script.name} ==")
    print(p.stdout.strip())
    if p.returncode == 2:
        failed.append(script.name)

if failed:
    raise SystemExit("P0 smoke failures: " + ", ".join(failed))
print("SMOKE PASS")
