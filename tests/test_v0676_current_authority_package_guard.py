from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

MODULE = Path(__file__).parents[1] / 'scripts/check_current_release_package.py'
spec = importlib.util.spec_from_file_location('check_current_release_package_v0676_guard', MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

MANDATORY_CURRENT_AUTHORITIES = {
    'references/CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md',
    'references/LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
    'references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json',
    'references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md',
}


def test_current_release_checker_requires_v0676_authority_and_negative_fixture():
    required = set(mod.required_release_paths())
    assert MANDATORY_CURRENT_AUTHORITIES <= required, sorted(MANDATORY_CURRENT_AUTHORITIES - required)
