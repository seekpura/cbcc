from __future__ import annotations
from pathlib import Path
import importlib.util, sys

ROOT=Path(__file__).parents[1]
MODULE=ROOT/'runtime/cbcc/measurement_authority.py'
spec=importlib.util.spec_from_file_location('measurement_runtime_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
FIX=ROOT/'tests/test_v0676_measurement_authority.py'
fspec=importlib.util.spec_from_file_location('measurement_fixture_runtime_v0676',FIX)
fx=importlib.util.module_from_spec(fspec); assert fspec and fspec.loader
sys.modules[fspec.name]=fx; fspec.loader.exec_module(fx)


def test_strategy_wrapper_projects_explicit_measurement_into_section09_and_preserves_experiment_evidence():
    exp=fx.experiment_result()
    def base(request,*args,**kwargs): return fx.legacy_strategy()
    out=mod.wrap_build_master_strategy(base)(fx.request(),experiment=exp)
    auth=out['measurement_authority_v0676']; s9=out['sections']['09_risk_measurement_priority_next_steps']
    assert auth['status']=='READY'; assert s9['measurement_plan'][0]['measurement_id']=='M-01'; assert s9['priority_plan']['P0'][0]['decision_ref']=='M-01'; assert s9['next_input_plan'][0]['input_id']=='NEXT-01'; assert s9['experiment']==exp
    assert s9['legacy_advisory_v0676']['ab_test_hypotheses'][0]['id']=='AB-HERO-PROP'


def test_delivery_validator_separates_measurement_business_readiness_from_strategy_compile_status():
    incomplete=mod.materialize_measurement_authority(fx.legacy_strategy(),{'delivery_mode':'FULL_PROJECT'},fx.experiment_result())
    out=mod.wrap_validate_strategy_delivery(lambda strategy:{'status':'PASS','issues':[]})(incomplete)
    assert out['status']=='INCOMPLETE'; assert out['measurement_authority_v0676_audit']['status']=='INCOMPLETE'; assert any(x['code']=='FULL_MEASUREMENT_DECISION_MISSING_V0676' for x in out['issues'])


def test_v0676_closure_installs_measurement_strategy_and_validator_wrappers_without_new_seven_tool():
    text=(ROOT/'runtime/cbcc/v0676_phase2_closure.py').read_text(encoding='utf-8')
    assert 'measurement_authority' in text
    assert 'wrap_build_master_strategy as wrap_measurement_strategy' in text
    assert 'wrap_validate_strategy_delivery as wrap_measurement_validator' in text
    assert "'_cbcc_v0676_measurement_authority'" in text
    assert "'MEASUREMENT_BUSINESS_AUTHORITY'" in text
    assert 'SEVEN_TOOL_MEASUREMENT' not in text
