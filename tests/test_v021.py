from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_v021_reference_floor():
    for rel in ['references/MASTER_STRATEGY_SPEC.md','references/ASSET_COMPILER_SPEC.md','references/PRODUCTION_RUNNER_SPEC.md']:
        assert (ROOT/rel).exists()
