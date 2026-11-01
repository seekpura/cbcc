from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

MODULE = Path(__file__).parents[1] / 'runtime/cbcc/context_why_authority.py'
spec = importlib.util.spec_from_file_location('context_why_authority_v0676', MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

AXES = ('platform','region','audience','race_ethnicity_culture')
DENSITY = ('what','why','evidence','tradeoff','execution','measurement')


def _strategy(mode='FULL_PROJECT', detailed=True):
    context = {}
    for axis in AXES:
        if detailed:
            context[axis] = {
                'status':'EVIDENCED',
                'what':f'{axis} changes this decision through a named mechanism',
                'why':f'{axis} decision-specific reason',
                'evidence':['SRC-1'],
                'tradeoff':f'{axis} tradeoff',
                'execution':f'{axis} execution consequence',
                'measurement':f'{axis} measurement signal',
                'basis':'SRC-1',
            }
        else:
            context[axis] = {'status':'TO_VERIFY','why':'generic project context','basis':'project_context'}
    return {
        'delivery_mode':mode,
        'sections':{
            '04_marketing_core_strategy':{
                'major_decision_context_why':[{
                    'decision':'Positioning',
                    'decision_value':{
                        'why':'decision why','evidence':['SRC-1'],'tradeoff':'decision tradeoff',
                        'execution':'decision execution','measurement':'decision metric'
                    },
                    'context_why':context,
                    'measurement':'decision metric',
                }]
            }
        }
    }


def test_full_alias_preserves_complete_decision_and_four_axis_density():
    out = mod.materialize_context_why_authority(_strategy())
    row = out['sections']['04_marketing_core_strategy']['major_decision_context_why'][0]
    assert row['density_status'] == 'READY'
    assert all(row[k] not in (None,'',[],{}) for k in DENSITY)
    for axis in AXES:
        assert all(row['context_why'][axis][k] not in (None,'',[],{}) for k in DENSITY)
    assert mod.context_why_issues(out) == []


def test_legacy_project_context_cannot_false_pass_as_decision_specific_why():
    out = mod.materialize_context_why_authority(_strategy('FULL', detailed=False))
    row = out['sections']['04_marketing_core_strategy']['major_decision_context_why'][0]
    assert row['density_status'] == 'TO_VERIFY'
    issues = mod.context_why_issues(out)
    assert any(x['code']=='FULL_MAJOR_DECISION_CONTEXT_AXIS_DENSITY_INCOMPLETE_V0676' and x['axis']=='platform' for x in issues)


def test_missing_axes_remain_to_verify_instead_of_inventing_causal_claims():
    raw = _strategy('FULL')
    raw['sections']['04_marketing_core_strategy']['major_decision_context_why'][0]['context_why'] = {}
    out = mod.materialize_context_why_authority(raw)
    row = out['sections']['04_marketing_core_strategy']['major_decision_context_why'][0]
    for axis in AXES:
        assert row['context_why'][axis]['status'] == 'TO_VERIFY'
        assert row['context_why'][axis]['evidence'] == []
        assert row['context_why'][axis]['assumption_boundary'] == 'DECISION_SPECIFIC_CONTEXT_NOT_AUTHORED'
    assert row['density_status'] == 'TO_VERIFY'


def test_task_scoped_strategy_is_unchanged():
    raw = _strategy('TASK_SCOPED')
    assert mod.materialize_context_why_authority(raw) == raw


def test_materializer_does_not_mutate_adjacent_business_objects():
    raw = _strategy('FULL')
    raw['sections']['01_information_completeness_assumptions_decisions'] = {'sentinel':'info'}
    raw['sections']['02_product_truth_value_ladder'] = {'sentinel':'truth'}
    raw['sections']['03_platform_region_audience_culture_insight'] = {'sentinel':'market-audience-culture'}
    out = mod.materialize_context_why_authority(raw)
    assert out['sections']['01_information_completeness_assumptions_decisions'] == {'sentinel':'info'}
    assert out['sections']['02_product_truth_value_ladder'] == {'sentinel':'truth'}
    assert out['sections']['03_platform_region_audience_culture_insight'] == {'sentinel':'market-audience-culture'}


def test_validator_preserves_existing_issues_and_adds_only_context_why_issues():
    raw = _strategy('FULL', detailed=False)
    compiled = mod.materialize_context_why_authority(raw)
    def base_validator(strategy):
        return {'status':'INCOMPLETE','issues':[{'code':'EXISTING_PRODUCT_TRUTH_ISSUE'}]}
    wrapped = mod.wrap_validate_strategy_delivery(base_validator)
    result = wrapped(compiled)
    codes = {x['code'] for x in result['issues']}
    assert 'EXISTING_PRODUCT_TRUTH_ISSUE' in codes
    assert 'FULL_MAJOR_DECISION_CONTEXT_AXIS_DENSITY_INCOMPLETE_V0676' in codes
    assert result['status'] == 'INCOMPLETE'
