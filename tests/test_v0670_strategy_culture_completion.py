from runtime.cbcc.strategy_culture_completion_v0670 import complete_strategy_culture_v0670, completion_issues


def _base_full():
    return {
      'human_projection':{'mode':'FULL'},
      'sections':{
        '01_information_completeness_assumptions_decisions':{'decision_log':[{'what':'use BM primary copy','why':'Malaysia listing language'}]},
        '03_platform_region_audience_culture_insight':{'context_why':{'platform':'TikTok commerce','region':'Malaysia','audience':'oily skin routine','race_ethnicity_culture':'multi-ethnic representation without stereotypes'}},
        '04_marketing_core_strategy':{'framework_relationships':{'RACE':{'role':'process','basis':'brief','tradeoff':'one variable','execution':'four stages'}}},
        '05_visual_photography_strategy':{'people_applicability':'PERSON_PRESENT','inclusive_photography':{'deep_skin_exposure_compensation_plan':'Prelight waveform check','reflector_bounce_diffusion':'neutral bounce'}},
        '07_race_execution_table':[{'stage':x,'objective':'o','key_actions':['a'],'output':['x'],'culture_check':'c','kpi':'k','why':'w'} for x in ('RESEARCH','ACTION','COMMUNICATION','EVALUATION')],
        '08_culture_adaptation_checklist':[{'adaptation_point':'language','evidence_or_assumption':'EVIDENCED','inclusive_representation':'BM primary','stereotype_taboo_risk':'none','why':'local language'}],
      }
    }


def test_completion_materializes_all_explicit_execution_dimensions_without_inventing_missing_evidence():
    out=complete_strategy_culture_v0670(_base_full(),{'platform':'TikTok Shop Malaysia'})
    s=out['sections']
    assert all(r['platform']=='TikTok Shop Malaysia' for r in s['07_race_execution_table'])
    c=s['08_culture_adaptation_checklist'][0]
    for key in ('script_check','casting_check','wardrobe_grooming_check','color_check','cta_check','result','modification','validation_result','modification_action'):
        assert c[key]
    assert s['04_marketing_core_strategy']['framework_relationships']['RACE']['measurement']
    dims=s['05_visual_photography_strategy']['inclusive_dimension_decisions']
    assert set(('deep_skin','hair_texture_style','body_representation','disability_representation','age_representation','ai_bias')) <= set(dims)
    ctx=s['01_information_completeness_assumptions_decisions']['decision_log'][0]['context_why']
    assert set(('platform','region','audience','race_ethnicity_culture')) <= set(ctx)
    assert completion_issues(out)==[]


def test_completion_audit_rejects_uncompleted_full_strategy():
    issues=completion_issues(_base_full())
    codes={x['code'] for x in issues}
    assert 'FULL_RACE_PLATFORM_MISSING' in codes
    assert 'FULL_CULTURE_EXECUTION_COLUMNS_MISSING_V0670' in codes
    assert 'FULL_FRAMEWORK_MEASUREMENT_MISSING' in codes
    assert 'FULL_INCLUSIVE_RELEVANCE_DECISION_MISSING' in codes
    assert 'FULL_DECISION_CONTEXT_WHY_MISSING_V0670' in codes
