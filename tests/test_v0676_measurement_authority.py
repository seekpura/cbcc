from __future__ import annotations
from pathlib import Path
import importlib.util, sys

ROOT=Path(__file__).parents[1]
MODULE=ROOT/'runtime/cbcc/measurement_authority.py'
spec=importlib.util.spec_from_file_location('measurement_authority_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)

DENSITY=('what','why','evidence','tradeoff','execution','measurement')


def density(label, source='SRC-MEASURE'):
    return {
        'what':f'{label} decision','why':f'{label} is required to turn uncertainty into a bounded next decision.','evidence':[source],
        'tradeoff':f'Isolate {label}; do not change unrelated commercial layers at the same time.','execution':f'Execute the declared {label} plan exactly as specified.',
        'measurement':f'Evaluate {label} with its declared metric, guardrails and decision rule.','source_refs':[source],'source_type':'MEASUREMENT_BASELINE',
        'recency':'2026-11-01','exact_fact':f'{label} planning fact','interpretation':f'{label} informs the next commerce decision without claiming causality beyond the declared design.',
        'confidence':'HIGH','assumption_boundary':None,'downstream_use':['measurement','strategy_revision','next_input'],'conflict_status':'NO_DECLARED_CONFLICT',
    }


def measurement_row():
    return {
        'measurement_id':'M-01','business_question':'Does a single oil-balance + hydration proposition improve qualified PDP progression?','decision_object':'LISTING.HERO',
        'hypothesis':'A single first-impression proposition improves qualified progression without reducing CVR.','primary_metric':'PDP_PROGRESSION_RATE',
        'metric_definition':'qualified PDP progressions / eligible PDP sessions','desired_direction':'UP','baseline':0.21,'target_or_mde':0.03,'metric_source_ref':'SRC-MEASURE',
        'guardrails':['CVR_NOT_WORSE_THAN_BASELINE','CLAIM_COMPLIANCE_ZERO_VIOLATIONS'],'test_type':'A_B','changed_variable':'FIRST_IMPRESSION_PROPOSITION',
        'held_constants':['PRICE','SKU','AUDIENCE','PLACEMENT','PDP_BODY'],'variants':['CONTROL_CURRENT_HERO','VARIANT_SINGLE_PROPOSITION'],'deployment_pool':'ELIGIBLE_PDP_SESSIONS',
        'randomization_unit':'SESSION','sample_size_rule':'Use predeclared power/MDE inputs; do not stop from interim winner appearance.',
        'duration_or_stop_rule':'Stop only after the declared sample/power rule or a safety/compliance guardrail breach.',
        'success_rule':'Primary metric improves by at least declared MDE and guardrails remain acceptable.',
        'failure_rule':'Primary metric fails the declared MDE or a guardrail breaches; do not generalize the variant.',
        'next_decision':'If success, promote the proposition locally; if failure, preserve baseline and test the next isolated uncertainty.',
        **density('measurement'),
    }


def priority_row(priority, action):
    return {'priority':priority,'status':'ACTIVE','action':action,'decision_ref':'M-01','next_decision':f'Complete {priority} before lower priority work that depends on it.',**density(f'priority {priority}')}


def next_input_row():
    return {
        'input_id':'NEXT-01','status':'PLANNED_COLLECTION','exact_missing_input':'Post-test qualified PDP progression by variant and guardrail CVR by variant',
        'source_or_owner':'experiment instrumentation / commerce analytics owner','downstream_unblock':'M-01 result interpretation and local Strategy revision decision',
        'decision_trigger':'Collect after the declared stop rule is reached; do not infer from partial screenshots or platform attribution summaries.',**density('next input'),
    }


def request():
    return {
        'delivery_mode':'FULL_PROJECT','sources':[{'source_id':'SRC-MEASURE','source_type':'MEASUREMENT_BASELINE','as_of':'2026-11-01'}],
        'measurement_plan':{'rows':[measurement_row()],'priorities':[
            priority_row('P0','Protect truth/compliance and instrumentation integrity before interpreting lift.'),
            priority_row('P1','Run M-01 as the highest-value isolated commercial uncertainty.'),
            priority_row('P2','After P0/P1 close, expand only the next evidence-backed test pool.'),
        ],'next_inputs':[next_input_row()]}
    }


def legacy_strategy():
    return {'status':'STRATEGY_AUTHORITY_COMPILED','delivery_mode':'FULL_PROJECT','sections':{'09_risk_measurement_priority_next_steps':{
        'experiment':{'status':'ANALYZED','decision':'INCONCLUSIVE'},'ab_test_hypotheses':[{'id':'AB-HERO-PROP','hypothesis':'legacy generated suggestion'}],
        'priority_plan':{'P0':[{'action':'legacy P0','why':'generic'}],'P1':[],'P2':[],'next_information_needed':[]},
    }}}


def experiment_result():
    return {'status':'ANALYZED','decision':'INCONCLUSIVE','observed_effect':0.01,'significance':{'status':'NOT_SIGNIFICANT'}}


def test_complete_measurement_plan_is_first_class_ready_before_asset_or_production_learning():
    out=mod.materialize_measurement_authority(legacy_strategy(),request(),experiment_result()); auth=out['measurement_authority_v0676']
    assert auth['status']=='READY'; assert auth['asset_dependency']=='NOT_REQUIRED_FOR_PHASE2_BUSINESS_AUTHORITY'; assert auth['production_learning_dependency']=='NOT_REQUIRED_FOR_PHASE2_MEASUREMENT_PLAN_AUTHORITY'
    row=auth['measurement_rows'][0]
    assert row['business_contract_status']=='READY'; assert row['test_contract_status']=='READY'; assert row['density_status']=='READY'; assert row['lineage_status']=='READY'; assert row['metric_source_status']=='READY'
    assert all(row[k] not in (None,'',[],{}) for k in DENSITY); assert auth['priority_status']=='READY'; assert auth['priority_order']==['P0','P1','P2']; assert auth['next_input_status']=='READY'; assert mod.measurement_issues(out)==[]


def test_legacy_strategy_ab_priority_and_experiment_result_cannot_false_pass_missing_authored_measurement_plan():
    req=request(); req.pop('measurement_plan'); out=mod.materialize_measurement_authority(legacy_strategy(),req,experiment_result())
    assert out['measurement_authority_v0676']['status']=='TO_VERIFY'; codes={x['code'] for x in mod.measurement_issues(out)}
    assert 'FULL_MEASUREMENT_DECISION_MISSING_V0676' in codes; assert 'FULL_MEASUREMENT_PRIORITY_PLAN_INCOMPLETE_V0676' in codes; assert 'FULL_MEASUREMENT_NEXT_INPUT_PLAN_INCOMPLETE_V0676' in codes


def test_measurement_row_requires_metric_baseline_target_test_and_next_decision_contract():
    req=request(); row=req['measurement_plan']['rows'][0]
    for k in ('primary_metric','metric_definition','baseline','target_or_mde','guardrails','test_type','deployment_pool','randomization_unit','sample_size_rule','duration_or_stop_rule','success_rule','failure_rule','next_decision'): row.pop(k,None)
    out=mod.materialize_measurement_authority(legacy_strategy(),req,experiment_result()); rr=out['measurement_authority_v0676']['measurement_rows'][0]
    assert rr['business_contract_status']=='TO_VERIFY'; assert any(x['code']=='FULL_MEASUREMENT_BUSINESS_OBJECT_INCOMPLETE_V0676' for x in mod.measurement_issues(out))


def test_ab_contract_requires_changed_variable_held_constants_variants_and_no_contradiction():
    req=request(); row=req['measurement_plan']['rows'][0]; row['held_constants'].append('FIRST_IMPRESSION_PROPOSITION')
    out=mod.materialize_measurement_authority(legacy_strategy(),req,experiment_result()); rr=out['measurement_authority_v0676']['measurement_rows'][0]
    assert rr['test_contract_status']=='TO_VERIFY'; assert any(x['code']=='FULL_MEASUREMENT_AB_TEST_CONTRACT_INVALID_V0676' for x in mod.measurement_issues(out))


def test_measurement_metric_source_must_resolve_and_missing_baseline_never_becomes_zero():
    req=request(); row=req['measurement_plan']['rows'][0]; row['metric_source_ref']='SRC-NOT-IN-REGISTRY'; row.pop('baseline')
    out=mod.materialize_measurement_authority(legacy_strategy(),req,experiment_result()); rr=out['measurement_authority_v0676']['measurement_rows'][0]
    assert rr.get('baseline') is None; assert rr['metric_source_status']=='TO_VERIFY'; assert 'SRC-NOT-IN-REGISTRY' in rr['unresolved_metric_source_refs']; codes={x['code'] for x in mod.measurement_issues(out)}
    assert 'FULL_MEASUREMENT_METRIC_SOURCE_INCOMPLETE_V0676' in codes; assert 'FULL_MEASUREMENT_BUSINESS_OBJECT_INCOMPLETE_V0676' in codes


def test_p0_p1_p2_are_explicit_decisions_not_auto_generated_labels():
    req=request(); req['measurement_plan']['priorities']=[priority_row('P0','only one priority')]
    out=mod.materialize_measurement_authority(legacy_strategy(),req,experiment_result()); auth=out['measurement_authority_v0676']
    assert auth['priority_status']=='TO_VERIFY'; assert auth['priority_order']==['P0']; assert any(x['code']=='FULL_MEASUREMENT_PRIORITY_PLAN_INCOMPLETE_V0676' for x in mod.measurement_issues(out))


def test_next_input_plan_requires_exact_input_owner_unblock_trigger_and_six_field_density():
    req=request(); nxt=req['measurement_plan']['next_inputs'][0]
    for k in ('exact_missing_input','source_or_owner','downstream_unblock','decision_trigger','tradeoff'): nxt.pop(k,None)
    out=mod.materialize_measurement_authority(legacy_strategy(),req,experiment_result()); auth=out['measurement_authority_v0676']
    assert auth['next_input_status']=='TO_VERIFY'; assert any(x['code']=='FULL_MEASUREMENT_NEXT_INPUT_PLAN_INCOMPLETE_V0676' for x in mod.measurement_issues(out))


def test_experiment_output_is_consumed_as_evidence_not_recalculated_or_promoted_to_business_decision():
    exp=experiment_result(); out=mod.materialize_measurement_authority(legacy_strategy(),request(),exp); auth=out['measurement_authority_v0676']
    assert auth['experiment_evidence']==exp; assert auth['experiment_calculator_authority']=='runtime/cbcc/tools/experiment.py'; assert auth['experiment_decision_does_not_author_measurement_plan'] is True


def test_measurement_learning_handoff_does_not_claim_post_production_learning_or_phase6_projection():
    out=mod.materialize_measurement_authority(legacy_strategy(),request(),experiment_result()); b=out['measurement_authority_v0676']['boundaries']
    assert b['post_production_learning_status']=='DEFERRED_TO_LEARNING_LOOP_WHEN_REAL_RESULTS_EXIST'; assert b['human_workspace_projection']=='PENDING_PHASE6'; assert b['measurement_plan_completion_is_not_experiment_success'] is True
