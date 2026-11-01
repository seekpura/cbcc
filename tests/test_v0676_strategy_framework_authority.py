from __future__ import annotations
from pathlib import Path
import importlib.util, sys

MODULE=Path(__file__).parents[1]/'runtime/cbcc/strategy_framework_authority.py'
spec=importlib.util.spec_from_file_location('strategy_framework_authority_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)

DENSITY=('what','why','evidence','tradeoff','execution','measurement')
FRAMEWORKS=('RACE','STP','JTBD','AIDA','FABE','4P','FUNNEL')


def authored(mode='FULL_PROJECT'):
    framework_rows={}
    for key in FRAMEWORKS:
        framework_rows[key]={
            'status':'APPLIED' if key in {'RACE','STP','JTBD','FABE'} else 'NOT_NEEDED',
            'changed_decision':f'{key} changed a named current-project decision' if key in {'RACE','STP','JTBD','FABE'} else f'{key} not needed for current decision scope',
            'what':f'{key} application decision',
            'why':f'{key} is used or explicitly not used because of current evidence and task',
            'evidence':['SRC-STRATEGY'],
            'tradeoff':f'{key} tradeoff',
            'execution':f'{key} execution consequence',
            'measurement':f'{key} measurement signal',
        }
    race=[]
    for stage in ('RESEARCH','ACTION','COMMUNICATION','EVALUATION'):
        race.append({
            'stage':stage,'objective':f'{stage} objective','key_actions':[f'{stage} action'],
            'output':[f'{stage} output'],'platform':'TikTok Shop','culture_check':'culture check','kpi':[f'{stage} KPI'],
            'what':f'{stage} current-project decision','why':f'{stage} reason','evidence':['SRC-STRATEGY'],
            'tradeoff':f'{stage} tradeoff','execution':f'{stage} execution','measurement':f'{stage} KPI',
        })
    return {
      'delivery_mode':mode,
      'sections':{
        '01_information_completeness_assumptions_decisions':{'sentinel':'info'},
        '02_product_truth_value_ladder':{'sentinel':'truth'},
        '03_platform_region_audience_culture_insight':{'sentinel':'culture'},
        '04_marketing_core_strategy':{
          'positioning':{
            'positioning_statement':'Positioning statement',
            'what':'Prioritize one named segment/job and differentiation frame.',
            'why':'Current evidence supports this positioning route.','evidence':['SRC-STRATEGY'],
            'tradeoff':'Do not target every segment equally.','execution':'Use this frame in first-screen strategy.',
            'measurement':'Comprehension / CTR / CVR where applicable.'
          },
          'value_proposition':{
            'statement':'Evidence-bounded value proposition',
            'what':'Lead with a verified value promise.','why':'It maps Product Truth to the priority job.',
            'evidence':['SRC-STRATEGY'],'tradeoff':'Avoid unsupported stronger efficacy language.',
            'execution':'Use as value spine across listing/content.','measurement':'Message comprehension and conversion.'
          },
          'message_hierarchy':[
            {'priority':'P0','message':'Primary message','what':'Lead with primary message','why':'It resolves first barrier',
             'evidence':['SRC-STRATEGY'],'tradeoff':'Defer secondary detail','execution':'First screen/hero first','measurement':'First-scan comprehension'}
          ],
          'framework_relationships':framework_rows,
        },
        '07_race_execution_table':race,
        '08_culture_adaptation_checklist':{'sentinel':'culture-check'},
      }
    }


def legacy_generic():
    s=authored('FULL')
    s['sections']['04_marketing_core_strategy']['framework_relationships']={
      key:{'status':'PROCESS_BACKBONE' if key=='RACE' else 'DECISION_LENS','role':'generic role','basis':'generic basis',
           'tradeoff':'generic tradeoff','execution':'generic execution','measurement':'bind a metric later'}
      for key in FRAMEWORKS
    }
    s['sections']['04_marketing_core_strategy']['value_proposition']=None
    s['sections']['04_marketing_core_strategy']['message_hierarchy']=[{'priority':'P0','message':'Primary','why':'generic why'}]
    return s


def test_authored_strategy_decisions_and_framework_applications_reach_ready():
    out=mod.materialize_strategy_framework_authority(authored())
    auth=out['strategy_framework_authority_v0676']
    assert auth['status']=='READY'
    assert auth['positioning']['density_status']=='READY'
    assert auth['value_proposition']['density_status']=='READY'
    assert auth['message_hierarchy'][0]['density_status']=='READY'
    for key,row in auth['frameworks'].items():
        assert row['application_status'] in {'APPLIED','NOT_NEEDED'}
        assert row['density_status']=='READY'
    assert all(row['density_status']=='READY' for row in auth['race'])
    assert mod.strategy_framework_issues(out)==[]


def test_generic_framework_definitions_cannot_false_pass_as_applied_decisions():
    out=mod.materialize_strategy_framework_authority(legacy_generic())
    auth=out['strategy_framework_authority_v0676']
    assert auth['status']=='TO_VERIFY'
    for key in FRAMEWORKS:
        assert auth['frameworks'][key]['density_status']=='TO_VERIFY'
    codes={x['code'] for x in mod.strategy_framework_issues(out)}
    assert 'FULL_FRAMEWORK_APPLICATION_DENSITY_INCOMPLETE_V0676' in codes
    assert 'FULL_VALUE_PROPOSITION_DECISION_INCOMPLETE_V0676' in codes
    assert 'FULL_MESSAGE_HIERARCHY_DECISION_INCOMPLETE_V0676' in codes


def test_missing_value_proposition_is_explicit_unknown_not_invented_copy():
    raw=authored('FULL')
    raw['sections']['04_marketing_core_strategy'].pop('value_proposition')
    out=mod.materialize_strategy_framework_authority(raw)
    vp=out['strategy_framework_authority_v0676']['value_proposition']
    assert vp['density_status']=='TO_VERIFY'
    assert vp['what'] is None
    assert vp['exact_fact'] is None
    assert vp['assumption_boundary']=='VALUE_PROPOSITION_NOT_AUTHORED'


def test_explicit_not_needed_framework_is_valid_only_with_real_reason_and_tradeoff():
    raw=authored('FULL')
    row=raw['sections']['04_marketing_core_strategy']['framework_relationships']['AIDA']
    assert row['status']=='NOT_NEEDED'
    out=mod.materialize_strategy_framework_authority(raw)
    assert out['strategy_framework_authority_v0676']['frameworks']['AIDA']['density_status']=='READY'
    raw2=authored('FULL'); raw2['sections']['04_marketing_core_strategy']['framework_relationships']['AIDA']={'status':'NOT_NEEDED','why':'not needed'}
    out2=mod.materialize_strategy_framework_authority(raw2)
    assert out2['strategy_framework_authority_v0676']['frameworks']['AIDA']['density_status']=='TO_VERIFY'


def test_race_definition_rows_need_decision_evidence_and_tradeoff_not_only_stage_labels():
    raw=authored('FULL')
    raw['sections']['07_race_execution_table']=[
      {'stage':s,'objective':'generic objective','key_actions':['generic'],'output':['generic'],'platform':'platform','culture_check':'check','kpi':['metric'],'why':'RACE definition'}
      for s in ('RESEARCH','ACTION','COMMUNICATION','EVALUATION')
    ]
    out=mod.materialize_strategy_framework_authority(raw)
    assert all(x['density_status']=='TO_VERIFY' for x in out['strategy_framework_authority_v0676']['race'])
    assert any(x['code']=='FULL_RACE_APPLIED_DECISION_DENSITY_INCOMPLETE_V0676' for x in mod.strategy_framework_issues(out))


def test_prior_verified_siblings_and_existing_validator_issues_are_preserved_and_non_full_unchanged():
    raw=authored('FULL')
    out=mod.materialize_strategy_framework_authority(raw)
    assert out['sections']['01_information_completeness_assumptions_decisions']=={'sentinel':'info'}
    assert out['sections']['02_product_truth_value_ladder']=={'sentinel':'truth'}
    assert out['sections']['03_platform_region_audience_culture_insight']=={'sentinel':'culture'}
    assert out['sections']['08_culture_adaptation_checklist']=={'sentinel':'culture-check'}
    def base(strategy): return {'status':'INCOMPLETE','issues':[{'code':'EXISTING_INTERSECTIONALITY_ISSUE'}]}
    result=mod.wrap_validate_strategy_delivery(base)(mod.materialize_strategy_framework_authority(legacy_generic()))
    codes={x['code'] for x in result['issues']}
    assert 'EXISTING_INTERSECTIONALITY_ISSUE' in codes
    assert 'FULL_FRAMEWORK_APPLICATION_DENSITY_INCOMPLETE_V0676' in codes
    scoped=authored('TASK_SCOPED')
    assert mod.materialize_strategy_framework_authority(scoped)==scoped
