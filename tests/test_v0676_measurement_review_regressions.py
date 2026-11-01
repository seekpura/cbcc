from __future__ import annotations
from pathlib import Path
import importlib.util, sys

ROOT=Path(__file__).parents[1]
MODULE=ROOT/'runtime/cbcc/measurement_authority.py'
spec=importlib.util.spec_from_file_location('measurement_review_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
FIX=ROOT/'tests/test_v0676_measurement_authority.py'
fspec=importlib.util.spec_from_file_location('measurement_fixture_review_v0676',FIX)
fx=importlib.util.module_from_spec(fspec); assert fspec and fspec.loader
sys.modules[fspec.name]=fx; fspec.loader.exec_module(fx)


def test_measurement_requires_attribution_observation_analysis_and_learning_handoff():
    req=fx.request(); row=req['measurement_plan']['rows'][0]
    for key in ('attribution_method','observation_window','analysis_unit','sequential_monitoring_policy','learning_handoff'): row.pop(key,None)
    out=mod.materialize_measurement_authority(fx.legacy_strategy(),req,fx.experiment_result()); rr=out['measurement_authority_v0676']['measurement_rows'][0]
    assert rr['business_contract_status']=='TO_VERIFY'; assert any(x['code']=='FULL_MEASUREMENT_BUSINESS_OBJECT_INCOMPLETE_V0676' for x in mod.measurement_issues(out))


def test_priority_decision_ref_must_resolve_to_real_measurement_id():
    req=fx.request(); req['measurement_plan']['priorities'][0]['decision_ref']='M-NOT-REAL'
    out=mod.materialize_measurement_authority(fx.legacy_strategy(),req,fx.experiment_result()); p0=out['measurement_authority_v0676']['priorities'][0]
    assert p0['decision_link_status']=='TO_VERIFY'; assert any(x['code']=='FULL_MEASUREMENT_PRIORITY_PLAN_INCOMPLETE_V0676' for x in mod.measurement_issues(out))


def test_next_input_must_link_real_measurement_decision_and_reject_generic_more_data():
    req=fx.request(); nxt=req['measurement_plan']['next_inputs'][0]; nxt['decision_ref']='M-NOT-REAL'; nxt['exact_missing_input']='need more data'
    out=mod.materialize_measurement_authority(fx.legacy_strategy(),req,fx.experiment_result()); nn=out['measurement_authority_v0676']['next_inputs'][0]
    assert nn['decision_link_status']=='TO_VERIFY'; assert nn['exact_input_status']=='TO_VERIFY'; assert out['measurement_authority_v0676']['next_input_status']=='TO_VERIFY'


def test_priority_status_must_be_explicit_active_or_not_needed_not_arbitrary_text():
    req=fx.request(); req['measurement_plan']['priorities'][1]['status']='SOMETHING'
    out=mod.materialize_measurement_authority(fx.legacy_strategy(),req,fx.experiment_result()); p1=out['measurement_authority_v0676']['priorities'][1]
    assert p1['priority_contract_status']=='TO_VERIFY'


def test_unknown_lineage_source_cannot_be_hidden_by_valid_metric_source():
    req=fx.request(); row=req['measurement_plan']['rows'][0]; row['source_refs']=['SRC-NOT-IN-REGISTRY']; row['evidence']=['SRC-NOT-IN-REGISTRY']; row['metric_source_ref']='SRC-MEASURE'
    out=mod.materialize_measurement_authority(fx.legacy_strategy(),req,fx.experiment_result()); rr=out['measurement_authority_v0676']['measurement_rows'][0]
    assert rr['metric_source_status']=='READY'; assert rr['lineage_status']=='TO_VERIFY'; assert rr['unresolved_source_refs']==['SRC-NOT-IN-REGISTRY']


def test_measurement_plan_ready_does_not_claim_experiment_result_or_causal_learning():
    out=mod.materialize_measurement_authority(fx.legacy_strategy(),fx.request(),None); auth=out['measurement_authority_v0676']
    assert auth['status']=='READY'; assert auth['experiment_evidence']==fx.legacy_strategy()['sections']['09_risk_measurement_priority_next_steps']['experiment']; assert auth['boundaries']['measurement_plan_completion_is_not_experiment_success'] is True; assert auth['boundaries']['post_production_learning_status']=='DEFERRED_TO_LEARNING_LOOP_WHEN_REAL_RESULTS_EXIST'


def test_strategy_section09_keeps_legacy_ab_projection_schema_while_full_authority_stays_lossless():
    out=mod.materialize_measurement_authority(fx.legacy_strategy(),fx.request(),fx.experiment_result()); s9=out['sections']['09_risk_measurement_priority_next_steps']; row=s9['ab_test_hypotheses'][0]
    required={'id','hypothesis','variable','variants','hold_constant','deployment_pool','metric','guardrail','next_decision_rule','measurement_authority_ref'}
    assert required.issubset(row); assert row['id']=='M-01'; assert row['measurement_authority_ref']=='M-01'; assert out['measurement_authority_v0676']['measurement_rows'][0]['attribution_method']=='FIRST_PARTY_SESSION_EXPERIMENT'
    assert s9['legacy_advisory_v0676']['ab_test_hypotheses'][0]['id']=='AB-HERO-PROP'; assert s9['priority_plan']['P0'][0]['measure']==s9['priority_plan']['P0'][0]['measurement']


def test_duplicate_measurement_ids_cannot_false_pass_priority_and_next_input_links():
    req=fx.request()
    duplicate=dict(req['measurement_plan']['rows'][0])
    duplicate['business_question']='Second distinct measurement question'
    duplicate['hypothesis']='Second hypothesis sharing an invalid duplicate identifier.'
    req['measurement_plan']['rows'].append(duplicate)
    out=mod.materialize_measurement_authority(fx.legacy_strategy(),req,fx.experiment_result())
    auth=out['measurement_authority_v0676']
    assert auth['measurement_id_uniqueness_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_MEASUREMENT_ID_DUPLICATE_V0676' for x in mod.measurement_issues(out))


def test_measurement_materialization_preserves_unrelated_strategy_siblings():
    base=fx.legacy_strategy()
    base['sections']['04_marketing_core_strategy']={'marker':'KEEP-CORE'}
    base['sections']['06_platform_content_matrix']=[{'marker':'KEEP-CONTENT'}]
    base['sections']['07_race_execution_table']=[{'marker':'KEEP-RACE'}]
    base['review_analysis_authority_v0676']={'marker':'KEEP-REVIEW'}
    base['phase2_economics_offer_authority']={'marker':'KEEP-ECON'}
    out=mod.materialize_measurement_authority(base,fx.request(),fx.experiment_result())
    assert out['sections']['04_marketing_core_strategy']=={'marker':'KEEP-CORE'}
    assert out['sections']['06_platform_content_matrix']==[{'marker':'KEEP-CONTENT'}]
    assert out['sections']['07_race_execution_table']==[{'marker':'KEEP-RACE'}]
    assert out['review_analysis_authority_v0676']=={'marker':'KEEP-REVIEW'}
    assert out['phase2_economics_offer_authority']=={'marker':'KEEP-ECON'}
