from pathlib import Path

ROOT=Path(__file__).parents[1]


def test_phase2_closure_installs_content_matrix_before_strategy_framework_and_validator():
    text=(ROOT/'runtime/cbcc/v0676_phase2_closure.py').read_text(encoding='utf-8')
    assert 'content_matrix_race_authority' in text
    assert 'wrap_build_master_strategy as wrap_content_matrix_race_strategy' in text
    assert 'wrap_validate_strategy_delivery as wrap_content_matrix_race_validator' in text
    assert 'CONTENT_MATRIX_RACE_BUSINESS_AUTHORITY' in text
    # Content/RACE must materialize the final section rows before the existing Strategy/Framework
    # wrapper snapshots section 07 into its own applied-RACE authority.
    assert text.index('wrap_content_matrix_race_strategy') < text.index("'_cbcc_v0676_strategy_framework_authority'")


def test_canonical_graph_keeps_content_matrix_and_race_as_strategy_section_authorities_not_duplicate_payloads():
    text=(ROOT/'runtime/cbcc/canonical_commerce_graph.py').read_text(encoding='utf-8')
    assert 'NodeSpec("CONTENT_MATRIX", "Content Matrix", ("strategy_authority.json",), "/sections/06_platform_content_matrix"' in text
    assert 'NodeSpec("RACE", "RACE", ("strategy_authority.json",), "/sections/07_race_execution_table"' in text
