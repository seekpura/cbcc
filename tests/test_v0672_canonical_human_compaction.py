from __future__ import annotations

from pathlib import Path
import json

from cbcc.canonical_human_compaction_v0672 import finalize_static_human_projection


def _fixture(root: Path) -> Path:
    (root / 'asset_packages' / 'AST-X').mkdir(parents=True)
    (root / 'strategy').mkdir()
    (root / 'supporting_analysis').mkdir()
    (root / 'index.html').write_text('<html><body><main>' + ''.join(f'<section class="page" data-route="{r}"></section>' for r in ('overview','listing','strategy','product','visual','content','prompts','sources')) + '</main></body></html>', encoding='utf-8')
    (root / 'HUMAN_DELIVERY.json').write_text('{"task_scope":{"listing_active":false},"copy_center":[],"localized_copy":[]}', encoding='utf-8')
    (root / 'strategy' / 'strategy_authority.json').write_text('{"sections":{}}', encoding='utf-8')
    (root / 'ASSET_UNIVERSE.json').write_text('{"total_asset_candidates":1}', encoding='utf-8')
    asset = root / 'asset_packages' / 'AST-X'
    (asset / '00_asset_manifest.yaml').write_text('asset_id: AST-X\n', encoding='utf-8')
    for name in ('00_HUMAN_DESIGN_CARD_CN.md','01_strategy.md','02_visual_spec.md','05_prompt_CN.txt','06_prompt_EN.txt','07_generation_guidance.txt','08_copy.md','09_production_notes.md','10_source_trace.md'):
        (asset / name).write_text('中文测试' if 'CN' in name or name.endswith('.md') else 'english test', encoding='utf-8')
    for name, obj in {
        '03_photography_contract.json': {}, '04_layout_contract.json': {}, '11_strategy_authority_trace.json': {},
        '12_design_card.json': {}, '13_prompt_contract.json': {'large_unique_contract': 'X' * 1_000_000},
        '14_visible_copy_block.json': {}, '15_production_assembly_notes.json': {}, 'CANONICAL_LINEAGE.json': {},
    }.items():
        (asset / name).write_text(json.dumps(obj), encoding='utf-8')
    return root


def test_final_human_projection_materializes_heavy_canonical_value_once(tmp_path: Path):
    package = _fixture(tmp_path)
    result = finalize_static_human_projection(package)
    html = (package / 'index.html').read_text(encoding='utf-8')
    assert result['status'] == 'PASS'
    assert result['projection_mode'] == 'DEDUPLICATED_SINGLE_MATERIALIZATION'
    assert len(html.encode('utf-8')) < 4_500_000
    assert html.count('X' * 1000) < 1100
    assert 'CBCC_CANONICAL_STATIC_PROJECTION_V0672' in html
    assert 'replaceChildren' in html and 'textContent' in html
