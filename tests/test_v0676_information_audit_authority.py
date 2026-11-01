from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

MODULE = Path(__file__).parents[1] / 'runtime/cbcc/information_audit_authority.py'
spec = importlib.util.spec_from_file_location('information_audit_authority_v0676', MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def source_rows():
    return [
        {'source_id':'SRC-XLSX','kind':'PRODUCT_WORKBOOK','observed_at':'2026-10-30'},
        {'source_id':'SRC-REQ','kind':'USER_REQUEST','observed_at':'2026-10-31'},
    ]


def base_info(question_count: int = 12):
    return {
        'completeness_status':'INCOMPLETE',
        'required_missing':['offer_economics.platform_fee'],
        'pending_confirmations':[
            {
                'item':f'Question {i}',
                'reason':'Needed before a dependent publication/economics decision.',
                'required_for':['ECONOMICS'] if i % 2 else ['PUBLISH'],
                'status':'TO_VERIFY',
                'evidence_needed':'Explicit current source or user confirmation.',
            }
            for i in range(1, question_count + 1)
        ],
        'assumptions':[
            {
                'assumption':'Use the supplied target market while current platform fee remains unknown.',
                'status':'ASSUMPTION',
                'basis':'Current request explicitly supplies target market but not fee.',
                'downstream_effect':['STRATEGY'],
                'evidence_needed':'Current platform fee schedule before economics publication.',
                'source_refs':['SRC-REQ'],
            }
        ],
        'decision_log':[
            {
                'what':'Continue non-economics strategy under explicit uncertainty.',
                'why':'Missing platform fee blocks margin precision, not Product Truth or research interpretation.',
                'evidence':['SRC-REQ'],
                'tradeoff':'Economics remains provisional.',
                'execution':'Continue unrelated strategy; hold exact economics recommendation.',
                'measurement':'Replace provisional economics when current fee evidence arrives.',
                'downstream_use':['STRATEGY','ECONOMICS'],
            }
        ],
    }


def product_truth():
    return {
        'product_facts':[
            {
                'fact':'net_weight',
                'value':'30g',
                'source_ids':['SRC-XLSX'],
                'evidence_level':'SOURCE_LINKED',
            }
        ]
    }


def test_question_limit_caps_user_questions_but_preserves_all_unresolved_items():
    out = mod.compile_information_audit_authority(base_info(12), product_truth=product_truth(), sources=source_rows())
    assert out['question_limit'] == 10
    assert out['pending_confirmation_total_count'] == 12
    assert len(out['pending_confirmations']) == 10
    assert len(out['pending_confirmations_overflow']) == 2
    assert len(out['unresolved_items']) >= 12
    assert out['continue_under_assumptions'] is True


def test_fact_assumption_decision_are_explicitly_separate():
    out = mod.compile_information_audit_authority(base_info(2), product_truth=product_truth(), sources=source_rows())
    kinds = {row['type'] for row in out['assumption_decision_log']}
    assert {'FACT','ASSUMPTION','DECISION'} <= kinds
    fact = next(row for row in out['assumption_decision_log'] if row['type'] == 'FACT')
    assumption = next(row for row in out['assumption_decision_log'] if row['type'] == 'ASSUMPTION')
    decision = next(row for row in out['assumption_decision_log'] if row['type'] == 'DECISION')
    assert fact['exact_fact'] == '30g'
    assert assumption['exact_fact'] is None
    assert decision['exact_fact'] is None


def test_every_assumption_decision_and_question_has_decision_density_fields():
    out = mod.compile_information_audit_authority(base_info(2), product_truth=product_truth(), sources=source_rows())
    required = {'what','why','evidence','tradeoff','execution','measurement'}
    rows = out['pending_confirmations'] + [
        row for row in out['assumption_decision_log'] if row['type'] in {'ASSUMPTION','DECISION'}
    ]
    assert rows
    assert all(required <= set(row) for row in rows)


def test_lineage_is_explicit_without_promoting_unknown_to_fact():
    out = mod.compile_information_audit_authority(base_info(1), product_truth=product_truth(), sources=source_rows())
    required = {
        'source_refs','source_type','recency','exact_fact','interpretation','confidence',
        'assumption_boundary','downstream_use','conflict_status','proof_object'
    }
    assert all(required <= set(row) for row in out['assumption_decision_log'])
    question = out['pending_confirmations'][0]
    assert required <= set(question)
    assert question['exact_fact'] is None
    assert question['confidence'] == 'LOW'
    assert question['assumption_boundary'] == 'UNRESOLVED_INPUT_NOT_FACT'


def test_missing_inputs_remain_missing_and_do_not_stop_unrelated_work():
    info = {
        'completeness_status':'INCOMPLETE',
        'required_missing':['cost','current_regulation'],
        'pending_confirmations':[],
        'assumptions':[],
        'decision_log':[],
    }
    out = mod.compile_information_audit_authority(info, product_truth={}, sources=[])
    missing = [row for row in out['information_audit_items'] if row['type'] == 'MISSING_INPUT']
    assert {row['item'] for row in missing} == {'cost','current_regulation'}
    assert all(row['exact_fact'] is None for row in missing)
    assert all(row['status'] == 'MISSING_INPUT' for row in missing)
    assert out['status'] == 'INFORMATION_AUDIT_READY_WITH_OPEN_ITEMS'
    assert out['continue_under_assumptions'] is True


def test_wrapper_enriches_real_strategy_section_without_replacing_other_sections():
    def base_builder(request, *args, **kwargs):
        return {
            'human_projection':{'mode':'FULL'},
            'sections':{
                '01_information_completeness_assumptions_decisions':base_info(3),
                '02_product_truth_value_ladder':product_truth(),
                '03_platform_region_audience_culture_insight':{'sentinel':'keep'},
            },
        }
    wrapped = mod.wrap_build_master_strategy(base_builder)
    out = wrapped({'sources':source_rows()})
    info = out['sections']['01_information_completeness_assumptions_decisions']
    assert info['schema'] == 'cbcc-information-audit-authority-v1'
    assert out['sections']['03_platform_region_audience_culture_insight'] == {'sentinel':'keep'}
    assert getattr(wrapped, '_cbcc_v0676_information_audit_authority', False) is True


def test_audit_rejects_shallow_information_object_and_accepts_compiled_object():
    shallow = {
        'human_projection':{'mode':'FULL'},
        'sections':{'01_information_completeness_assumptions_decisions':{'assumption_decision_log':[{'type':'DECISION'}]}},
    }
    codes = {row['code'] for row in mod.information_audit_issues(shallow)}
    assert 'FULL_INFORMATION_AUDIT_AUTHORITY_MISSING' in codes or 'FULL_INFORMATION_AUDIT_ROW_SHALLOW_V0676' in codes

    compiled = {
        'human_projection':{'mode':'FULL'},
        'sections':{
            '01_information_completeness_assumptions_decisions':mod.compile_information_audit_authority(
                base_info(2), product_truth=product_truth(), sources=source_rows()
            )
        },
    }
    assert mod.information_audit_issues(compiled) == []
