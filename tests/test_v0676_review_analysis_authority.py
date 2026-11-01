from __future__ import annotations
from pathlib import Path
import importlib.util, sys

ROOT=Path(__file__).parents[1]
MODULE=ROOT/'runtime/cbcc/review_analysis_authority.py'
spec=importlib.util.spec_from_file_location('review_analysis_authority_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)

DENSITY=('what','why','evidence','tradeoff','execution','measurement')


def decision_fields(label='review root cause', source='SRC-REVIEWS'):
    return {
        'what':f'{label} decision',
        'why':'The observed complaint cluster requires a smallest-responsible-layer repair rather than a broad redesign.',
        'evidence':[source],
        'tradeoff':'Change only the implicated communication layer; freeze Product Truth and unrelated commercial decisions.',
        'execution':'Correct the expectation wording and FAQ answer; preserve unrelated product, offer and visual strategy.',
        'measurement':'Verify the same complaint class declines or no longer reproduces after the local repair.',
        'source_refs':[source],
        'source_type':'CUSTOMER_REVIEW_EXPORT',
        'recency':'2026-11-01',
        'exact_fact':'3 classified expectation-gap reviews reference the same usage expectation.',
        'interpretation':'The evidence supports a communication root-cause hypothesis, not a product-defect claim.',
        'confidence':'HIGH',
        'assumption_boundary':None,
        'downstream_use':['listing','faq','review_learning'],
        'conflict_status':'NO_DECLARED_CONFLICT',
    }


def repair_row():
    return {
        'review_decision_id':'REV-ROOT-01',
        'issue_class':'EXPECTATION_GAP',
        'issue_signal':'Repeated usage expectation mismatch',
        'root_cause_hypothesis':'Listing/FAQ wording leaves the usage boundary ambiguous.',
        'root_cause_layer':'LISTING',
        'root_cause_status':'EVIDENCE_SUPPORTED_HYPOTHESIS',
        'responsible_layer':'LISTING',
        'repair_action':'Clarify the usage boundary in the Listing and FAQ without changing Product Truth.',
        'repair_scope':['LISTING.USAGE_COPY','FAQ.USAGE_BOUNDARY'],
        'frozen_layers':['PRODUCT_TRUTH','PRICING_OFFER','UNRELATED_VISUAL_STYLE'],
        'why_not_broader_rework':'No separate evidence supports a product defect, offer problem or portfolio-wide visual failure.',
        'verification_metric':'EXPECTATION_GAP_RATE',
        'success_rule':'Same classified expectation-gap signal decreases after repair without increasing misunderstanding.',
        'failure_rule':'If the same issue persists with unchanged traffic/source mix, reopen root-cause classification before broader changes.',
        'learning_handoff':['LISTING','FAQ','MEASUREMENT_NEXT_INPUT'],
        **decision_fields(),
    }


def request():
    return {
        'delivery_mode':'FULL_PROJECT',
        'sources':[{'source_id':'SRC-REVIEWS','source_type':'CUSTOMER_REVIEW_EXPORT','as_of':'2026-11-01'}],
        'review_analysis':{'rows':[repair_row()]},
    }


def legacy_feedback():
    return {
        'status':'AGGREGATED_FROM_CLASSIFIED_INPUT',
        'summary':{'total':3,'categories':{'EXPECTATION_GAP':3},'shares':{'EXPECTATION_GAP':1.0}},
        'issues':[{'category':'EXPECTATION_GAP','count':3,'share':1.0,'severity_points':6,'routes':['LISTING','VISUAL','CREATOR'],'examples':['usage expectation mismatch']}],
        'defect_vs_communication':{'product_issue_count':0,'communication_issue_count':3,'primary_direction':'CONTENT_EXPECTATION'},
        'revision_actions':[{'category':'EXPECTATION_GAP','routes':['LISTING','VISUAL','CREATOR'],'frozen_layers':['product truth']}],
        'unclassified_count':0,
    }


def test_complete_review_analysis_is_first_class_ready_without_asset_or_production_review():
    out=mod.materialize_review_analysis_authority(legacy_feedback(),request())
    assert out['status']=='READY'
    assert out['asset_dependency']=='NOT_REQUIRED_FOR_PHASE2_BUSINESS_AUTHORITY'
    assert out['production_review_dependency']=='NOT_REQUIRED_FOR_PHASE2_CUSTOMER_REVIEW_AUTHORITY'
    row=out['repair_rows'][0]
    assert row['business_contract_status']=='READY'
    assert row['density_status']=='READY'
    assert row['lineage_status']=='READY'
    assert row['root_cause_route_status']=='READY'
    assert row['smallest_repair_status']=='READY'
    assert all(row[k] not in (None,'',[],{}) for k in DENSITY)
    assert mod.review_analysis_issues(out)==[]


def test_legacy_feedback_aggregation_cannot_false_pass_missing_agent_root_cause_repair_decision():
    req=request(); req['review_analysis']['rows']=[]
    out=mod.materialize_review_analysis_authority(legacy_feedback(),req)
    assert out['status']=='TO_VERIFY'
    assert out['repair_rows']==[]
    assert any(x['code']=='FULL_REVIEW_ROOT_CAUSE_REPAIR_DECISION_MISSING_V0676' for x in mod.review_analysis_issues(out))


def test_review_row_requires_root_cause_repair_freeze_verify_learning_contract():
    req=request(); row=req['review_analysis']['rows'][0]
    for k in ('root_cause_hypothesis','root_cause_layer','responsible_layer','repair_action','repair_scope','frozen_layers','why_not_broader_rework','verification_metric','success_rule','failure_rule','learning_handoff'):
        row.pop(k,None)
    out=mod.materialize_review_analysis_authority(legacy_feedback(),req)
    rr=out['repair_rows'][0]
    assert rr['business_contract_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_REVIEW_ROOT_CAUSE_REPAIR_OBJECT_INCOMPLETE_V0676' for x in mod.review_analysis_issues(out))


def test_review_row_requires_six_field_density_and_req088_lineage():
    req=request(); row=req['review_analysis']['rows'][0]
    row.pop('tradeoff'); row['source_refs']=['SRC-NOT-IN-REGISTRY']; row['evidence']=['SRC-NOT-IN-REGISTRY']
    out=mod.materialize_review_analysis_authority(legacy_feedback(),req)
    rr=out['repair_rows'][0]
    assert rr['density_status']=='TO_VERIFY'
    assert rr['lineage_status']=='TO_VERIFY'
    assert rr['unresolved_source_refs']==['SRC-NOT-IN-REGISTRY']
    codes={x['code'] for x in mod.review_analysis_issues(out)}
    assert 'FULL_REVIEW_DECISION_DENSITY_INCOMPLETE_V0676' in codes
    assert 'FULL_REVIEW_LINEAGE_INCOMPLETE_V0676' in codes


def test_communication_issue_cannot_default_to_product_change_without_product_defect_evidence():
    req=request(); row=req['review_analysis']['rows'][0]
    row['responsible_layer']='PRODUCT_QUALITY'; row['repair_scope']=['PRODUCT_FORMULA']
    out=mod.materialize_review_analysis_authority(legacy_feedback(),req)
    rr=out['repair_rows'][0]
    assert rr['root_cause_route_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_REVIEW_RESPONSIBLE_LAYER_CONTRADICTION_V0676' for x in mod.review_analysis_issues(out))


def test_product_quality_issue_cannot_be_declared_fixed_by_copy_only():
    req=request(); row=req['review_analysis']['rows'][0]
    row['issue_class']='PRODUCT_QUALITY'; row['root_cause_layer']='PRODUCT_QUALITY'; row['responsible_layer']='LISTING'; row['repair_scope']=['LISTING.COPY']
    out=mod.materialize_review_analysis_authority(legacy_feedback(),req)
    rr=out['repair_rows'][0]
    assert rr['root_cause_route_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_REVIEW_PRODUCT_DEFECT_COPY_ONLY_REPAIR_V0676' for x in mod.review_analysis_issues(out))


def test_smallest_repair_requires_nonempty_frozen_layers_and_no_broad_redesign_default():
    req=request(); row=req['review_analysis']['rows'][0]
    row['repair_scope']=['FULL_PROJECT_REDESIGN']; row['frozen_layers']=[]; row['why_not_broader_rework']=''
    out=mod.materialize_review_analysis_authority(legacy_feedback(),req)
    rr=out['repair_rows'][0]
    assert rr['smallest_repair_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_REVIEW_SMALLEST_REPAIR_ROUTE_INCOMPLETE_V0676' for x in mod.review_analysis_issues(out))


def test_review_local_verification_handoff_does_not_claim_global_measurement_closure():
    out=mod.materialize_review_analysis_authority(legacy_feedback(),request())
    assert out['verification_boundary']['global_measurement_status']=='DEFERRED_PHASE2_SUBTASK_12'
    assert out['verification_boundary']['local_repair_verification_contract']=='READY'
    assert out['verification_boundary']['measurement_closure_claimed'] is False
