from __future__ import annotations
from pathlib import Path
import importlib.util, sys

MODULE=Path(__file__).parents[1]/'runtime/cbcc/ads_optimization_authority.py'
spec=importlib.util.spec_from_file_location('ads_optimization_authority_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)

DENSITY=('what','why','evidence','tradeoff','execution','measurement')


def decision_fields(label, source='SRC-ADS'):
    return {
        'what':f'{label} decision','why':f'{label} changes the current paid-media constraint.','evidence':[source],
        'tradeoff':f'Change only the responsible {label} layer; hold unrelated variables constant.',
        'execution':f'Execute one controlled {label} change.','measurement':f'Measure {label} with declared primary/guardrail metrics.',
        'source_refs':[source],'source_type':'ADS_PERFORMANCE','recency':'2026-11-01','exact_fact':f'{label} evidence fact',
        'interpretation':f'{label} evidence informs the optimization decision without claiming causality beyond attribution evidence.',
        'confidence':'HIGH','assumption_boundary':None,'downstream_use':['ads_optimization','listing','offer','creative'],
        'conflict_status':'NO_DECLARED_CONFLICT'
    }


def optimization_row():
    return {
        'optimization_id':'ADS-OPT-01','objective':'Acquire qualified PDP traffic within contribution boundary',
        'funnel_state':'CLICK_TO_PDP','audience_state':'Qualified oily-skin shopper with low product familiarity',
        'consumer_tension':'Needs a fast reason to click without exaggerated efficacy claims',
        'creative_hypothesis':'A single oil-balance + hydration tension should improve qualified click intent.',
        'creative_mechanism':'Tension-to-proof first impression','proof':['CLM-SA','CLM-NIA'],
        'offer':'No automatic launch discount','landing_handoff':'PDP listing','spend_boundary':'Do not scale above available CPA/CPC/ROAS economics boundaries',
        'economics_boundary_ref':'phase2_economics_offer_authority.break_even',
        'attribution':'Platform-attributed conversion is directional; incremental lift requires counterfactual evidence.',
        'test_structure':'A/B one first-impression variable; hold audience, price, PDP and placement constant where possible.',
        'test_variable':'first_impression_hook','hold_constant':['audience','price','PDP','placement'],
        'success_rule':'CTR improves without material CVR or contribution-per-click deterioration.',
        'failure_rule':'Stop or reroute if CTR lift is offset by worse CVR, CPA or contribution-per-click.',
        'failure_diagnosis':'If CTR improves but contribution-per-click/CVR deteriorates, route to traffic-quality/message-match before scaling.',
        'repair_route':'FIRST_IMPRESSION_CREATIVE_ONLY','learning_handoff':['listing','creative','offer'],
        **decision_fields('ads optimization')
    }


def request():
    return {
        'delivery_mode':'FULL_PROJECT',
        'sources':[{'source_id':'SRC-ADS','source_type':'ADS_PERFORMANCE','as_of':'2026-11-01'}],
        'advertising_optimization':{'rows':[optimization_row()]}
    }


def legacy_ads():
    return {
        'status':'PORTFOLIO_CALCULATED',
        'aggregate':{'metrics':{'impressions':10000,'clicks':300,'orders':15,'spend':180,'revenue':885,'ctr':0.03,'cvr':0.05,'cpc':0.6,'cpa':12.0,'roas':4.9167}},
        'rows':[{'id':'CMP-1','analysis':{'metrics':{'ctr':0.03,'cvr':0.05,'cpc':0.6,'cpa':12.0,'roas':4.9167},'diagnosis':[],'budget_headroom':{'status':'CALCULATED','scale_signal':'HEADROOM'}}}],
        'diagnosis_required':[],'scale_candidates':[{'id':'CMP-1'}]
    }


def pricing(ready=True, cpc_ready=True):
    phase2={
        'status':'READY' if ready else 'TO_VERIFY',
        'break_even':{
            'cpa':{'status':'AVAILABLE' if ready else 'MISSING_INPUT','value':17.0 if ready else None},
            'cpc':{'status':'AVAILABLE' if ready and cpc_ready else 'MISSING_INPUT','value':0.68 if ready and cpc_ready else None},
            'roas':{'status':'AVAILABLE' if ready else 'MISSING_INPUT','value':3.47 if ready else None},
        },
        'pricing_decision':{'density_status':'READY' if ready else 'TO_VERIFY','decision':'MYR 59'},
        'offer_decision':{'density_status':'READY' if ready else 'TO_VERIFY','decision':'No automatic launch discount'}
    }
    return {'phase2_business_status':phase2['status'],'phase2_economics_offer_authority':phase2}


def test_complete_ads_optimization_authority_is_ready_before_asset_or_paid_campaign_work():
    out=mod.materialize_ads_optimization_authority(legacy_ads(),request(),pricing())
    assert out['status']=='READY'
    assert out['asset_dependency']=='NOT_REQUIRED_FOR_PHASE2_BUSINESS_AUTHORITY'
    assert out['paid_campaign_dependency']=='NOT_REQUIRED_FOR_PHASE2_BUSINESS_AUTHORITY'
    row=out['optimization_rows'][0]
    assert row['density_status']=='READY'
    assert row['business_contract_status']=='READY'
    assert row['lineage_status']=='READY'
    assert all(row[k] not in (None,'',[],{}) for k in DENSITY)
    assert out['economics_context']['status']=='READY'
    assert out['economics_context']['break_even_cpa']==17.0
    assert out['economics_context']['break_even_cpc']==0.68
    assert out['economics_context']['break_even_roas']==3.47
    assert mod.ads_optimization_issues(out)==[]


def test_metrics_and_diagnosis_do_not_false_pass_missing_authored_optimization_decision():
    req=request(); req['advertising_optimization']['rows']=[]
    out=mod.materialize_ads_optimization_authority(legacy_ads(),req,pricing())
    assert out['status']=='TO_VERIFY'
    assert out['optimization_rows']==[]
    assert any(x['code']=='FULL_ADS_OPTIMIZATION_DECISION_MISSING_V0676' for x in mod.ads_optimization_issues(out))


def test_ads_row_requires_objective_audience_creative_offer_landing_attribution_test_repair_learning_contract():
    req=request(); row=req['advertising_optimization']['rows'][0]
    for k in ('audience_state','creative_hypothesis','creative_mechanism','landing_handoff','attribution','test_structure','repair_route','learning_handoff'):
        row.pop(k,None)
    out=mod.materialize_ads_optimization_authority(legacy_ads(),req,pricing())
    rr=out['optimization_rows'][0]
    assert rr['business_contract_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_ADS_OPTIMIZATION_BUSINESS_OBJECT_INCOMPLETE_V0676' for x in mod.ads_optimization_issues(out))


def test_ads_row_requires_six_field_decision_density():
    req=request(); row=req['advertising_optimization']['rows'][0]
    for k in ('what','evidence','tradeoff','execution','measurement'):
        row.pop(k,None)
    out=mod.materialize_ads_optimization_authority(legacy_ads(),req,pricing())
    rr=out['optimization_rows'][0]
    assert rr['density_status']=='TO_VERIFY'
    assert set(rr['density_gaps']) >= {'what','evidence','tradeoff','execution','measurement'}


def test_ads_cannot_scale_from_legacy_metrics_when_phase2_economics_is_incomplete():
    out=mod.materialize_ads_optimization_authority(legacy_ads(),request(),pricing(False))
    assert out['economics_context']['status']=='TO_VERIFY'
    assert out['economics_context']['break_even_cpa'] is None
    assert out['status']=='TO_VERIFY'
    assert any(x['code']=='FULL_ADS_ECONOMICS_BOUNDARY_INCOMPLETE_V0676' for x in mod.ads_optimization_issues(out))


def test_missing_cvr_keeps_break_even_cpc_unavailable_without_blocking_available_cpa_roas_truth():
    out=mod.materialize_ads_optimization_authority(legacy_ads(),request(),pricing(True,False))
    econ=out['economics_context']
    assert econ['break_even_cpa']==17.0
    assert econ['break_even_roas']==3.47
    assert econ['break_even_cpc'] is None
    assert econ['break_even_cpc_status']=='MISSING_INPUT'
    assert out['status']=='READY'


def test_unknown_source_ref_cannot_satisfy_ads_req088_lineage():
    req=request(); row=req['advertising_optimization']['rows'][0]
    row['source_refs']=['SRC-NOT-IN-REGISTRY']; row['evidence']=['SRC-NOT-IN-REGISTRY']
    out=mod.materialize_ads_optimization_authority(legacy_ads(),req,pricing())
    rr=out['optimization_rows'][0]
    assert rr['lineage_status']=='TO_VERIFY'
    assert rr['unresolved_source_refs']==['SRC-NOT-IN-REGISTRY']
    assert any(x['code']=='FULL_ADS_OPTIMIZATION_LINEAGE_INCOMPLETE_V0676' for x in mod.ads_optimization_issues(out))


def test_platform_attribution_does_not_become_incrementality_claim_without_counterfactual():
    out=mod.materialize_ads_optimization_authority(legacy_ads(),request(),pricing())
    assert out['attribution_boundary']['incrementality_status']=='NOT_ESTABLISHED'
    assert out['attribution_boundary']['causal_sales_claim_allowed'] is False
