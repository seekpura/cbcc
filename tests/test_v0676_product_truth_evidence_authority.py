from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

MODULE = Path(__file__).parents[1] / 'runtime/cbcc/product_truth_evidence_authority.py'
spec = importlib.util.spec_from_file_location('product_truth_evidence_authority', MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def test_value_layers_are_separate_and_not_invented():
    out = mod.compile_product_truth_evidence_authority(
        facts=[{'fact_id':'F1','field':'salicylic_acid','value':'0.57%','source_ids':['xlsx']}],
        value_rows=[
            {'kind':'TRUE_SELLING_POINT','text':'0.57% SA + 1% NIA','evidence_grade':'B','source_ids':['xlsx']},
            {'kind':'PERCEIVED_BENEFIT','text':'控油护理与补水可同时沟通','evidence_grade':'B','source_ids':['xlsx']},
            {'kind':'EMOTIONAL_VALUE','text':'不必在控油和怕干之间二选一','evidence_grade':'C','source_ids':[]},
            {'kind':'NON_CLAIMABLE','text':'治愈痘痘','evidence_grade':'C','source_ids':[]},
        ],
    )
    assert [x['kind'] for x in out['value_ladder']] == ['FACT','TRUE_SELLING_POINT','PERCEIVED_BENEFIT','EMOTIONAL_VALUE','NON_CLAIMABLE']
    assert not any('clinical' in str(x).lower() for x in out['value_ladder'])


def test_c_grade_can_never_be_hard_release_claim_even_if_upstream_approved():
    out = mod.compile_product_truth_evidence_authority(
        facts=[],
        value_rows=[{'kind':'PERCEIVED_BENEFIT','text':'feels lightweight','evidence_grade':'C','release_status':'APPROVED'}],
    )
    row = out['value_ladder'][0]
    assert row['evidence_grade'] == 'C'
    assert row['release_status'] == 'HOLD'
    assert row['hard_claim_allowed'] is False
    assert 'C_GRADE_NOT_HARD_CLAIM' in row['reason_codes']


def test_a_b_c_semantics_are_machine_explicit():
    assert mod.EVIDENCE_GRADE_POLICY['A']['hard_claim_eligible'] is True
    assert mod.EVIDENCE_GRADE_POLICY['B']['hard_claim_eligible'] is True
    assert mod.EVIDENCE_GRADE_POLICY['C']['hard_claim_eligible'] is False
    assert 'test' in mod.EVIDENCE_GRADE_POLICY['A']['basis'].lower()
    assert 'supplier' in mod.EVIDENCE_GRADE_POLICY['B']['basis'].lower()
    assert 'subjective' in mod.EVIDENCE_GRADE_POLICY['C']['basis'].lower()


def test_conflicting_fact_values_are_quarantined_not_resolved_by_guessing():
    out = mod.compile_product_truth_evidence_authority(
        facts=[
            {'fact_id':'F1','field':'net_weight','value':'30g','source_ids':['pack']},
            {'fact_id':'F2','field':'net_weight','value':'50g','source_ids':['listing']},
        ],
        value_rows=[],
    )
    assert out['fact_conflicts'][0]['field'] == 'net_weight'
    assert out['fact_conflicts'][0]['status'] == 'CONFLICTING'
    assert set(out['fact_conflicts'][0]['values']) == {'30g','50g'}
    assert out['status'] == 'HOLD_CONFLICTING_PRODUCT_TRUTH'


def test_assumptions_must_carry_downstream_effect_and_evidence_needed():
    out = mod.compile_product_truth_evidence_authority(
        facts=[], value_rows=[], assumptions=[{'assumption':'lightweight sensory feel'}],
    )
    row = out['assumptions'][0]
    assert row['status'] == 'MISSING_SUPPORT_DETAIL'
    assert row['downstream_effect'] == 'MISSING_INPUT'
    assert row['evidence_needed'] == 'MISSING_INPUT'


def test_canonical_graph_lineage_is_explicit():
    out = mod.compile_product_truth_evidence_authority(
        facts=[{'field':'size','value':'30g','source_ids':['xlsx']}], value_rows=[]
    )
    assert out['canonical_graph_binding']['node_id'] == 'PRODUCT_TRUTH'
    assert out['canonical_graph_binding']['authority_role'] == 'CANONICAL_JSON_AUTHORITY'
    assert len(out['authority_sha256']) == 64


def test_product_truth_authority_is_canonical_graph_preferred_source(tmp_path):
    graph_module = Path(__file__).parents[1] / 'runtime/cbcc/canonical_commerce_graph.py'
    gs = importlib.util.spec_from_file_location('canonical_commerce_graph_t02', graph_module)
    gm = importlib.util.module_from_spec(gs)
    assert gs and gs.loader
    sys.modules[gs.name] = gm
    gs.loader.exec_module(gm)
    art = tmp_path / 'artifacts'
    (tmp_path / 'meta').mkdir(parents=True)
    (tmp_path / 'meta/request.json').write_text('{}', encoding='utf-8')
    art.mkdir(parents=True)
    (art / 'evidence.json').write_text('{"sources":[]}', encoding='utf-8')
    (art / 'research_gate.json').write_text('{}', encoding='utf-8')
    (art / 'strategy_authority.json').write_text('{"sections":{"01_information_completeness_assumptions_decisions":{}}}', encoding='utf-8')
    (art / 'product_truth.json').write_text('{"legacy":true}', encoding='utf-8')
    authority = mod.compile_product_truth_evidence_authority(facts=[], value_rows=[])
    import json
    (art / 'product_truth_evidence_authority.json').write_text(json.dumps(authority), encoding='utf-8')
    node = next(n for n in gm.build_canonical_commerce_graph(art)['nodes'] if n['node_id']=='PRODUCT_TRUTH')
    assert node['authority_ref'] == 'product_truth_evidence_authority.json'


def test_claim_to_evidence_trace_is_explicit_and_source_bound():
    out = mod.compile_product_truth_evidence_authority(
        facts=[{'field':'salicylic_acid','value':'0.57%','source_ids':['xlsx']}],
        value_rows=[
            {'kind':'TRUE_SELLING_POINT','text':'0.57% SA','evidence_grade':'B','source_ids':['xlsx']},
            {'kind':'EMOTIONAL_VALUE','text':'feel less conflicted about oily-skin hydration','evidence_grade':'C','source_ids':[]},
        ],
    )
    trace = out['claim_evidence_trace']
    by_kind = {row['kind']: row for row in trace}
    assert by_kind['TRUE_SELLING_POINT']['source_ids'] == ['xlsx']
    assert by_kind['TRUE_SELLING_POINT']['trace_status'] == 'SOURCE_BOUND'
    assert by_kind['EMOTIONAL_VALUE']['trace_status'] == 'UNBOUND_HOLD'
    assert by_kind['EMOTIONAL_VALUE']['hard_claim_allowed'] is False


def test_missing_value_layers_are_explicit_missing_input_with_why():
    out = mod.compile_product_truth_evidence_authority(
        facts=[{'field':'size','value':'30g','source_ids':['pack']}], value_rows=[],
    )
    status = out['value_kind_status']
    assert status['FACT']['status'] == 'READY'
    for kind in ('TRUE_SELLING_POINT','PERCEIVED_BENEFIT','EMOTIONAL_VALUE','NON_CLAIMABLE'):
        assert status[kind]['status'] == 'MISSING_INPUT'
        assert status[kind]['why']
    assert 'derive' in status['TRUE_SELLING_POINT']['why'].lower()
