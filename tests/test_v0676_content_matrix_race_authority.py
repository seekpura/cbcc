from __future__ import annotations
from pathlib import Path
import importlib.util, sys

MODULE=Path(__file__).parents[1]/'runtime/cbcc/content_matrix_race_authority.py'
spec=importlib.util.spec_from_file_location('content_matrix_race_authority_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)

DENSITY=('what','why','evidence','tradeoff','execution','measurement')


def decision_fields(label, source='SRC-CONTENT'):
    return {
        'what':f'{label} decision',
        'why':f'{label} changes the shopper/platform decision.',
        'evidence':[source],
        'tradeoff':f'{label} keeps one variable primary instead of mixing mechanisms.',
        'execution':f'Execute {label} exactly on the selected platform/surface.',
        'measurement':f'Measure {label} with its declared metric and attribution path.',
        'source_refs':[source],
        'source_type':'PLATFORM_RESEARCH',
        'recency':'2026-11-01',
        'exact_fact':f'{label} evidence fact',
        'interpretation':f'{label} evidence informs execution without inventing product claims.',
        'confidence':'HIGH',
        'assumption_boundary':None,
        'downstream_use':['content_matrix','race','measurement'],
        'conflict_status':'NO_DECLARED_CONFLICT',
    }


def matrix_row():
    return {
        'row_id':'CM-01',
        'platform':'TikTok Shop','site':'MY','surface':'PDP_VIDEO','content_type':'SHORT_VIDEO',
        'audience':'Adult oily-skin shopper','audience_state':'Needs fast product relevance',
        'purchase_barrier':'Unclear why this product belongs in a daily routine',
        'topic':'Daily oil-balance routine','hook':'Kawal minyak. Kekalkan hidrasi.',
        'hook_mechanism':'Direct category tension resolution',
        'script_structure':'Problem tension → product identity → bounded proof → routine fit → CTA',
        'visual_form':'Vertical product-led short video','visual_carrier':'Product + routine context + text hierarchy',
        'proof_evidence':['CLM-SA','CLM-NIA'],'cta':'See product details','metric':'PDP CTR → CVR',
        'race_stage':'COMMUNICATION','culture_adaptation':'Natural BM phrasing; no ethnicity-to-skin inference',
        'taboo_stereotype_check':'PASS_WITH_EXPLICIT_GUARD',
        'platform_dimensions':'9:16 / 1080×1920','duration':'15s','cover_first_frame':'Product identity + core tension',
        'subtitle_strategy':'BM primary + readable mobile safe zone','music_rights':'LICENSED_OR_PLATFORM_LIBRARY_ONLY',
        'traffic_mechanism':'TikTok Shop PDP/content traffic','landing_handoff':'PDP product detail','utm_attribution':'content_id=CM-01',
        **decision_fields('content row')
    }


def race_rows():
    out=[]
    for stage in ('RESEARCH','ACTION','COMMUNICATION','EVALUATION'):
        out.append({
            'stage':stage,'objective':f'{stage} objective','key_actions':[f'{stage} action'],
            'output':[f'{stage} output'],'platform':'TikTok Shop','surface':'PDP / content system',
            'culture_check':'Use evidence-backed language/representation; no identity behavior inference',
            'kpi':f'{stage} KPI','attribution':f'{stage} attribution rule','next_decision':f'{stage} next decision',
            'content_row_refs':['CM-01'] if stage=='COMMUNICATION' else [],
            **decision_fields(f'RACE {stage}')
        })
    return out


def request():
    return {
        'delivery_mode':'FULL_PROJECT',
        'sources':[{'source_id':'SRC-CONTENT','source_type':'PLATFORM_RESEARCH','as_of':'2026-11-01'}],
        'platform_content_matrix':[matrix_row()],
        'race_execution_table':race_rows(),
    }


def base_strategy():
    return {
        'delivery_mode':'FULL_PROJECT','sections':{
            '01_information_completeness_assumptions_decisions':{'sentinel':'info'},
            '02_product_truth_value_ladder':{'sentinel':'truth'},
            '03_platform_region_audience_culture_insight':{'sentinel':'culture'},
            '04_marketing_core_strategy':{'sentinel':'core'},
            '05_visual_photography_strategy':{'sentinel':'visual'},
            '06_platform_content_matrix':[],
            '07_race_execution_table':[],
            '08_culture_adaptation_checklist':{'sentinel':'check'},
            '09_risk_measurement_priority_next_steps':{'sentinel':'measurement'},
        }
    }


def test_explicit_content_matrix_and_race_are_first_class_before_asset_work():
    out=mod.materialize_content_matrix_race_authority(base_strategy(),request())
    auth=out['content_matrix_race_authority_v0676']
    assert auth['status']=='READY'
    assert auth['asset_dependency']=='NOT_REQUIRED_FOR_PHASE2_BUSINESS_AUTHORITY'
    assert len(out['sections']['06_platform_content_matrix'])==1
    assert len(out['sections']['07_race_execution_table'])==4
    row=auth['content_matrix'][0]
    assert row['density_status']=='READY'
    assert row['platform_execution_status']=='READY'
    assert row['lineage_status']=='READY'
    assert all(row[k] not in (None,'',[],{}) for k in DENSITY)
    assert mod.content_matrix_race_issues(out)==[]


def test_content_row_with_hook_but_missing_platform_execution_and_attribution_cannot_pass():
    req=request(); row=req['platform_content_matrix'][0]
    for k in ('platform_dimensions','duration','cover_first_frame','subtitle_strategy','music_rights','traffic_mechanism','landing_handoff','utm_attribution'):
        row.pop(k,None)
    out=mod.materialize_content_matrix_race_authority(base_strategy(),req)
    auth=out['content_matrix_race_authority_v0676']
    assert auth['status']=='TO_VERIFY'
    assert auth['content_matrix'][0]['platform_execution_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_CONTENT_MATRIX_PLATFORM_EXECUTION_INCOMPLETE_V0676' for x in mod.content_matrix_race_issues(out))


def test_content_row_requires_explicit_six_field_business_density_not_generic_why_only():
    req=request(); row=req['platform_content_matrix'][0]
    for k in ('what','evidence','tradeoff','execution','measurement'):
        row.pop(k,None)
    out=mod.materialize_content_matrix_race_authority(base_strategy(),req)
    cm=out['content_matrix_race_authority_v0676']['content_matrix'][0]
    assert cm['density_status']=='TO_VERIFY'
    assert set(cm['density_gaps']) >= {'what','evidence','tradeoff','execution','measurement'}


def test_content_matrix_race_stage_must_link_to_real_race_stage():
    req=request(); req['platform_content_matrix'][0]['race_stage']='REACH'
    out=mod.materialize_content_matrix_race_authority(base_strategy(),req)
    auth=out['content_matrix_race_authority_v0676']
    assert auth['content_matrix'][0]['race_link_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_CONTENT_MATRIX_RACE_LINK_INVALID_V0676' for x in mod.content_matrix_race_issues(out))


def test_race_stage_needs_platform_culture_attribution_next_decision_and_six_field_density():
    req=request(); race=req['race_execution_table'][2]
    for k in ('attribution','next_decision','tradeoff','measurement'):
        race.pop(k,None)
    out=mod.materialize_content_matrix_race_authority(base_strategy(),req)
    rr=out['content_matrix_race_authority_v0676']['race'][2]
    assert rr['execution_status']=='TO_VERIFY'
    assert rr['density_status']=='TO_VERIFY'
    codes={x['code'] for x in mod.content_matrix_race_issues(out)}
    assert 'FULL_RACE_EXECUTION_INCOMPLETE_V0676' in codes
    assert 'FULL_RACE_BUSINESS_DENSITY_INCOMPLETE_V0676' in codes


def test_missing_lineage_stays_to_verify_even_when_row_is_otherwise_complete():
    req=request(); row=req['platform_content_matrix'][0]
    for k in ('source_refs','source_type','recency','exact_fact','interpretation','confidence'):
        row.pop(k,None)
    out=mod.materialize_content_matrix_race_authority(base_strategy(),req)
    cm=out['content_matrix_race_authority_v0676']['content_matrix'][0]
    assert cm['lineage_status']=='TO_VERIFY'
    assert any(x['code']=='FULL_CONTENT_MATRIX_LINEAGE_INCOMPLETE_V0676' for x in mod.content_matrix_race_issues(out))


def test_explicit_matrix_replaces_empty_legacy_matrix_without_thinning_sibling_sections():
    before=base_strategy(); out=mod.materialize_content_matrix_race_authority(before,request())
    for key in ('01_information_completeness_assumptions_decisions','02_product_truth_value_ladder','03_platform_region_audience_culture_insight','04_marketing_core_strategy','05_visual_photography_strategy','08_culture_adaptation_checklist','09_risk_measurement_priority_next_steps'):
        assert out['sections'][key]==before['sections'][key]


def test_validator_preserves_existing_issues_and_adds_content_matrix_race_issues():
    req=request(); req['platform_content_matrix'][0].pop('utm_attribution')
    strategy=mod.materialize_content_matrix_race_authority(base_strategy(),req)
    def base_validator(value): return {'status':'INCOMPLETE','issues':[{'code':'EXISTING_ISSUE'}]}
    result=mod.wrap_validate_strategy_delivery(base_validator)(strategy)
    codes={x['code'] for x in result['issues']}
    assert 'EXISTING_ISSUE' in codes
    assert 'FULL_CONTENT_MATRIX_PLATFORM_EXECUTION_INCOMPLETE_V0676' in codes


def test_unknown_source_reference_cannot_satisfy_req088_lineage():
    req=request(); row=req['platform_content_matrix'][0]
    row['source_refs']=['SRC-NOT-IN-REGISTRY']; row['evidence']=['SRC-NOT-IN-REGISTRY']
    out=mod.materialize_content_matrix_race_authority(base_strategy(),req)
    cm=out['content_matrix_race_authority_v0676']['content_matrix'][0]
    assert cm['lineage_status']=='TO_VERIFY'
    assert cm['unresolved_source_refs']==['SRC-NOT-IN-REGISTRY']
    assert any(x['code']=='FULL_CONTENT_MATRIX_LINEAGE_INCOMPLETE_V0676' for x in mod.content_matrix_race_issues(out))
