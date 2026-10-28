#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FIX="$ROOT/tests/fixtures/minimal_valid"
python "$ROOT/validators/validate_sources.py" "$FIX"
python "$ROOT/validators/validate_claims.py" "$FIX"
python "$ROOT/validators/validate_asset_map.py" "$FIX"
python "$ROOT/validators/validate_cross_module.py" "$FIX"
echo "SMOKE PASS"
