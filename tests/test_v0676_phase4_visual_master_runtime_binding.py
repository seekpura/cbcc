from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_compiler_binds_phase3_lineage_then_materializes_visual_master_before_asset_architecture():
    text = (ROOT / 'runtime/cbcc/compiler.py').read_text(encoding='utf-8')

    assert 'bind_visual_master_upstream' in text
    assert 'visual_master_ref' in text
    assert "artifacts/visual_master.json" in text
    assert "architecture_target['phase4_visual_master']" in text

    phase3_at = text.index('phase3_opportunity_family_evaluation=compile_opportunity_family_evaluation')
    master_write_at = text.index("artifacts/visual_master.json")
    build_at = text.index('architecture=build_asset_architecture')
    assert phase3_at < master_write_at < build_at

    prebuild = text[phase3_at:build_at]
    assert 'bind_visual_master_upstream' in prebuild
    assert 'phase3_opportunity_family_evaluation' in prebuild
    assert "architecture_target['phase4_visual_master']" in prebuild


def test_compiler_creative_contract_reuses_same_visual_master_and_reference():
    text = (ROOT / 'runtime/cbcc/compiler.py').read_text(encoding='utf-8')
    build_at = text.index('architecture=build_asset_architecture')
    creative_at = text.index("creative={'design_system_status", build_at)
    section = text[build_at:creative_at + 5000]

    assert "'visual_master':phase4_visual_master" in section or "'visual_master': phase4_visual_master" in section
    assert "'visual_master_ref':visual_master_ref(phase4_visual_master)" in section or "'visual_master_ref': visual_master_ref(phase4_visual_master)" in section
    assert 'portfolio_visual_program' not in section.split("creative={'design_system_status", 1)[1], (
        'Creative Contract should consume the canonical master/ref rather than serialize a second independent Portfolio Visual Program.'
    )


def test_visual_master_upstream_lineage_is_reference_metadata_not_a_second_visual_program():
    text = (ROOT / 'runtime/cbcc/visual_master_authority.py').read_text(encoding='utf-8')
    assert 'def bind_visual_master_upstream' in text
    assert "'phase3_opportunity_family_evaluation'" in text
    assert "'needed_family_ids'" in text
    assert "'upstream_lineage'" in text
    assert 'portfolio_visual_program' in text
    assert 'runtime_may_invent_visual_strategy' in text
