from __future__ import annotations
from pathlib import Path
import importlib.util, sys

MODULE = Path(__file__).parents[1] / 'runtime/cbcc/intersectionality_culture_authority.py'
spec = importlib.util.spec_from_file_location('intersectionality_culture_authority_v0676', MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

DENSITY = ('what','why','evidence','tradeoff','execution','measurement')
CHECKS = ('script_check','casting_check','wardrobe_grooming_check','color_check','cta_check')
CORE_DIMS = {'race_ethnicity','gender','age','income','geography'}


def authored_strategy(mode='FULL_PROJECT'):
    return {
        'delivery_mode': mode,
        'sections': {
            '01_information_completeness_assumptions_decisions': {'sentinel':'info'},
            '02_product_truth_value_ladder': {'sentinel':'truth'},
            '03_platform_region_audience_culture_insight': {
                'intersectionality_table': [{
                    'dimensions':['race_ethnicity','gender','age','income','geography'],
                    'implication':'Use only evidence-backed representation/access implications.',
                    'evidence_or_assumption':['SRC-CULTURE'],
                    'stereotype_guard':'Do not infer product need, willingness to pay, skin type or purchase intent from identity.',
                    'execution':'Apply only verified language/representation/access consequences.',
                }],
                'intersectionality_interaction_analysis': [{
                    'dimensions':['race_ethnicity','age'],
                    'status':'EVIDENCE_LED_INTERACTION_CHECK',
                    'what':'Test whether the intersection changes comprehension or representation risk.',
                    'why':'The intersection matters only if a measurable mechanism changes the shopper decision.',
                    'evidence':['SRC-CULTURE'],
                    'tradeoff':'Keep neutral execution where the mechanism is not evidenced.',
                    'execution':'Run native/cultural review and preserve neutral defaults outside verified implications.',
                    'measurement':'Record comprehension/representation review result and whether execution changes.',
                    'mechanism':'language/comprehension/representation risk',
                    'evidence_or_assumption':['SRC-CULTURE'],
                    'stereotype_guard':'No identity-to-behavior inference.',
                    'verification_action':'Review with current market evidence/native reviewer.',
                }],
            },
            '04_marketing_core_strategy': {'sentinel':'strategy'},
            '08_culture_adaptation_checklist': [{
                'adaptation_point':'Language + religious/taboo context',
                'status':'EVIDENCED',
                'what':'Use verified local-language wording and avoid verified taboo cues.',
                'why':'This changes comprehension and representation risk in the named market.',
                'evidence':['SRC-CULTURE'],
                'tradeoff':'Do not invent festival/religious rules that are not evidenced.',
                'execution':'Apply the verified wording/representation constraints only where relevant.',
                'measurement':'Native/cultural review before publication; record required change.',
                'evidence_or_assumption':['SRC-CULTURE'],
                'inclusive_representation':'Representative without tokenistic identity labeling.',
                'stereotype_taboo_risk':'Do not infer behavior from ethnicity/religion.',
                'script_check':'Check script against evidenced language/taboo context.',
                'casting_check':'Check casting relevance without tokenism.',
                'wardrobe_grooming_check':'Check relevant dress/grooming context only when evidenced.',
                'color_check':'Do not assign cultural meaning to colors without evidence.',
                'cta_check':'Check CTA naturalness in the target language/context.',
                'result':'READY_FOR_CULTURAL_REVIEW',
                'modification':'Apply only evidence-backed changes.',
            }],
        }
    }


def legacy_strategy():
    s = authored_strategy('FULL')
    s['sections']['03_platform_region_audience_culture_insight']['intersectionality_interaction_analysis'] = [{
        'dimensions':['race_ethnicity','gender'],
        'status':'TO_VERIFY_INTERACTION',
        'mechanism':'Verify whether language or representation changes the task.',
        'evidence_or_assumption':'TO_VERIFY',
        'stereotype_guard':'No identity-to-behavior inference.',
        'execution':'Keep neutral until verified.',
        'verification_action':'Collect current market evidence.',
    }]
    s['sections']['08_culture_adaptation_checklist'] = [{
        'adaptation_point':'证据驱动的本地化',
        'inclusive_representation':'没有证据时不引入人口/族裔刻板印象。',
        'stereotype_taboo_risk':'未知文化细节保留为研究问题。',
        'evidence_status':'NO_CULTURE_INPUT',
        'result':'BASELINE',
        'modification':'有证据后再修改。',
        'why':'与其编造文化细节，不如保持中性。',
        'script_check':'TO_VERIFY',
        'casting_check':'TO_VERIFY',
        'wardrobe_grooming_check':'TO_VERIFY',
        'color_check':'TO_VERIFY',
        'cta_check':'TO_VERIFY',
    }]
    return s


def test_authored_intersection_and_culture_rows_reach_ready_without_data_loss():
    out = mod.materialize_intersectionality_culture_authority(authored_strategy())
    inter = out['sections']['03_platform_region_audience_culture_insight']['intersectionality_interaction_analysis'][0]
    culture = out['sections']['08_culture_adaptation_checklist'][0]
    assert inter['density_status'] == 'READY'
    assert culture['density_status'] == 'READY'
    assert all(inter[k] not in (None,'',[],{}) for k in DENSITY)
    assert all(culture[k] not in (None,'',[],{}) for k in DENSITY)
    assert all(culture[k] not in (None,'',[],{}) for k in CHECKS)
    assert out['intersectionality_culture_authority_v0676']['status'] == 'READY'
    assert mod.intersectionality_culture_issues(out) == []


def test_legacy_verification_program_does_not_false_pass_as_dense_intersectionality():
    out = mod.materialize_intersectionality_culture_authority(legacy_strategy())
    inter = out['sections']['03_platform_region_audience_culture_insight']['intersectionality_interaction_analysis'][0]
    culture = out['sections']['08_culture_adaptation_checklist'][0]
    assert inter['density_status'] == 'TO_VERIFY'
    assert culture['density_status'] == 'TO_VERIFY'
    codes = {x['code'] for x in mod.intersectionality_culture_issues(out)}
    assert 'FULL_INTERSECTIONALITY_DENSITY_INCOMPLETE_V0676' in codes
    assert 'FULL_CULTURE_ADAPTATION_DENSITY_INCOMPLETE_V0676' in codes


def test_core_intersection_dimensions_are_explicit_but_missing_identity_data_is_not_invented():
    raw = authored_strategy('FULL')
    raw['sections']['03_platform_region_audience_culture_insight']['intersectionality_table'] = []
    raw['sections']['03_platform_region_audience_culture_insight']['intersectionality_interaction_analysis'] = []
    out = mod.materialize_intersectionality_culture_authority(raw)
    coverage = out['intersectionality_culture_authority_v0676']['dimension_coverage']
    assert CORE_DIMS <= set(coverage)
    assert all(coverage[d]['status'] == 'TO_VERIFY' for d in CORE_DIMS)
    assert all(coverage[d]['evidence'] == [] for d in CORE_DIMS)
    assert all(coverage[d]['behavior_inference_allowed'] is False for d in CORE_DIMS)


def test_optional_cultural_contexts_are_relevance_aware_not_tokenistic_defaults():
    out = mod.materialize_intersectionality_culture_authority(authored_strategy())
    coverage = out['intersectionality_culture_authority_v0676']['context_coverage']
    for key in ('language','religion','holiday_calendar','taboo','family_household','skin_hair_body_representation'):
        assert coverage[key]['status'] in {'EVIDENCED','TO_VERIFY','NOT_NEEDED','MISSING_INPUT'}
        assert coverage[key]['why']
    assert coverage['holiday_calendar'].get('exact_fact') is None


def test_materializer_does_not_mutate_prior_verified_business_objects():
    raw = authored_strategy('FULL')
    out = mod.materialize_intersectionality_culture_authority(raw)
    assert out['sections']['01_information_completeness_assumptions_decisions'] == {'sentinel':'info'}
    assert out['sections']['02_product_truth_value_ladder'] == {'sentinel':'truth'}
    assert out['sections']['04_marketing_core_strategy'] == {'sentinel':'strategy'}


def test_validator_preserves_existing_issues_and_non_full_is_unchanged():
    compiled = mod.materialize_intersectionality_culture_authority(legacy_strategy())
    def base_validator(strategy):
        return {'status':'INCOMPLETE','issues':[{'code':'EXISTING_CONTEXT_WHY_ISSUE'}]}
    wrapped = mod.wrap_validate_strategy_delivery(base_validator)
    result = wrapped(compiled)
    codes = {x['code'] for x in result['issues']}
    assert 'EXISTING_CONTEXT_WHY_ISSUE' in codes
    assert 'FULL_INTERSECTIONALITY_DENSITY_INCOMPLETE_V0676' in codes
    scoped = authored_strategy('TASK_SCOPED')
    assert mod.materialize_intersectionality_culture_authority(scoped) == scoped
