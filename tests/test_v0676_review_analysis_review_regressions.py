from __future__ import annotations
from pathlib import Path
import importlib.util, sys

ROOT=Path(__file__).parents[1]
MODULE=ROOT/'runtime/cbcc/review_analysis_authority.py'
spec=importlib.util.spec_from_file_location('review_analysis_review_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
FIX=ROOT/'tests/test_v0676_review_analysis_authority.py'
fspec=importlib.util.spec_from_file_location('review_analysis_fixture_review_v0676',FIX)
fx=importlib.util.module_from_spec(fspec); assert fspec and fspec.loader
sys.modules[fspec.name]=fx; fspec.loader.exec_module(fx)


def test_authored_issue_class_must_align_with_observed_class_when_feedback_data_exists():
    req=fx.request(); req['review_analysis']['rows'][0]['issue_class']='MISUNDERSTANDING'
    out=mod.materialize_review_analysis_authority(fx.legacy_feedback(),req)
    row=out['repair_rows'][0]
    assert row['evidence_alignment_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_REVIEW_EVIDENCE_CLASS_ALIGNMENT_INCOMPLETE_V0676' for x in mod.review_analysis_issues(out))


def test_review_frequency_cannot_be_promoted_to_confirmed_causal_root_cause_without_causal_evidence():
    req=fx.request(); row=req['review_analysis']['rows'][0]
    row['root_cause_status']='CONFIRMED_CAUSE'
    row.pop('causal_evidence_refs',None)
    out=mod.materialize_review_analysis_authority(fx.legacy_feedback(),req)
    rr=out['repair_rows'][0]
    assert rr['causal_boundary_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_REVIEW_CAUSAL_ROOT_CAUSE_OVERCLAIM_V0676' for x in mod.review_analysis_issues(out))


def test_repair_scope_cannot_contradict_responsible_layer_even_when_route_label_is_allowed():
    req=fx.request(); row=req['review_analysis']['rows'][0]
    row['responsible_layer']='LISTING'
    row['repair_scope']=['PRODUCT_FORMULA']
    out=mod.materialize_review_analysis_authority(fx.legacy_feedback(),req)
    rr=out['repair_rows'][0]
    assert rr['root_cause_route_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_REVIEW_RESPONSIBLE_LAYER_CONTRADICTION_V0676' for x in mod.review_analysis_issues(out))


def test_positive_value_uses_preserve_learn_decision_not_fake_defect_repair():
    req=fx.request(); row=req['review_analysis']['rows'][0]
    row.update({
        'issue_class':'POSITIVE_VALUE',
        'decision_type':'PRESERVE_LEARN',
        'issue_signal':'Repeated praise for lightweight daily-use feel',
        'preservation_action':'Preserve this proven value cue in Listing/creative learning without turning praise into an unverified efficacy claim.',
        'learning_handoff':['LISTING','CREATIVE','MEASUREMENT_NEXT_INPUT'],
        'exact_fact':'3 classified positive reviews praise the same lightweight daily-use cue.',
        'interpretation':'Repeated praise is a value-learning signal, not a defect/root-cause or efficacy proof.',
    })
    for key in ('root_cause_hypothesis','root_cause_layer','root_cause_status','responsible_layer','repair_action','repair_scope','why_not_broader_rework'):
        row.pop(key,None)
    legacy=fx.legacy_feedback()
    legacy['issues']=[{'category':'POSITIVE_VALUE','count':3,'share':1.0,'severity_points':3,'routes':['LISTING/PROOF'],'examples':['lightweight daily-use feel']}]
    legacy['summary']={'total':3,'categories':{'POSITIVE_VALUE':3},'shares':{'POSITIVE_VALUE':1.0}}
    out=mod.materialize_review_analysis_authority(legacy,req)
    rr=out['repair_rows'][0]
    assert rr['decision_type']=='PRESERVE_LEARN'
    assert rr['business_contract_status']=='READY'
    assert rr['smallest_repair_status']=='NOT_APPLICABLE_POSITIVE_VALUE'
    assert rr['row_status']=='READY'
    assert out['status']=='READY'


def test_production_review_metadata_cannot_substitute_for_customer_review_root_cause_decision():
    req={'delivery_mode':'FULL_PROJECT','production_review':{'status':'ACCEPTED','quality_observations':{'copy':'PASS'}}}
    out=mod.materialize_review_analysis_authority({},req)
    assert out['status']=='TO_VERIFY'
    assert out['production_review_dependency']=='NOT_REQUIRED_FOR_PHASE2_CUSTOMER_REVIEW_AUTHORITY'
    assert any(x['code']=='FULL_REVIEW_ROOT_CAUSE_REPAIR_DECISION_MISSING_V0676' for x in mod.review_analysis_issues(out))


def test_unknown_root_cause_status_cannot_false_pass_as_evidence_supported_hypothesis():
    req=fx.request(); req['review_analysis']['rows'][0]['root_cause_status']='CONFIRMED_BY_REVIEW_COUNT'
    out=mod.materialize_review_analysis_authority(fx.legacy_feedback(),req)
    rr=out['repair_rows'][0]
    assert rr['causal_boundary_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_REVIEW_CAUSAL_ROOT_CAUSE_OVERCLAIM_V0676' for x in mod.review_analysis_issues(out))


def test_responsible_layer_cannot_also_be_frozen_by_same_repair_decision():
    req=fx.request(); row=req['review_analysis']['rows'][0]
    row['responsible_layer']='LISTING'; row['frozen_layers']=['LISTING','PRODUCT_TRUTH']
    out=mod.materialize_review_analysis_authority(fx.legacy_feedback(),req)
    rr=out['smallest_repair_status']
    assert rr=='TO_VERIFY'
    assert any(x['code']=='FULL_REVIEW_SMALLEST_REPAIR_ROUTE_INCOMPLETE_V0676' for x in mod.review_analysis_issues(out))
