from pathlib import Path
import importlib.util, sys

ROOT=Path(__file__).parents[1]
FIX=ROOT/'tests/test_v0676_content_matrix_race_authority.py'
spec=importlib.util.spec_from_file_location('cmr_fixture_v0676',FIX)
fx=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=fx; spec.loader.exec_module(fx)
mod=fx.mod


def test_runtime_generated_missing_boundary_does_not_turn_unsourced_row_into_valid_assumption_lineage():
    req=fx.request(); row=req['platform_content_matrix'][0]
    row.pop('source_refs',None)
    row['evidence']='DECLARED_BUT_NOT_SOURCE_BOUND'
    out=mod.materialize_content_matrix_race_authority(fx.base_strategy(),req)
    cm=out['content_matrix_race_authority_v0676']['content_matrix'][0]
    assert cm['lineage_status']=='TO_VERIFY'
    assert 'source_refs_or_explicit_assumption_boundary' in cm['lineage_gaps']


def test_attached_full_authority_is_still_validated_when_root_strategy_omits_delivery_mode_marker():
    base=fx.base_strategy(); base.pop('delivery_mode',None)
    req=fx.request(); req['platform_content_matrix'][0].pop('utm_attribution')
    out=mod.materialize_content_matrix_race_authority(base,req)
    assert 'content_matrix_race_authority_v0676' in out
    issues=mod.content_matrix_race_issues(out)
    assert any(x['code']=='FULL_CONTENT_MATRIX_PLATFORM_EXECUTION_INCOMPLETE_V0676' for x in issues)
