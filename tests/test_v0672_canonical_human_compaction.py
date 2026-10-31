from __future__ import annotations

from pathlib import Path
import json

from cbcc.canonical_human_compaction_v0672 import finalize_static_human_projection as finalize_legacy_projection
from cbcc.canonical_human_lazy_projection_v0672 import finalize_static_human_projection as finalize_lazy_projection


def _fixture(root: Path, *, heavy_legacy: bool = False) -> Path:
    (root / 'asset_packages' / 'AST-X').mkdir(parents=True)
    (root / 'strategy').mkdir()
    (root / 'supporting_analysis').mkdir()
    routes = ('overview','product','market','listing','strategy','content','visual','prompts','risk','sources','archive','asset/AST-X')
    if heavy_legacy:
        heavy = 'LEGACY_DUPLICATE_TOKEN|' * 50000
        body = ''.join(f'<section class="page" data-route="{r}">{heavy if r != "overview" else "small"}</section>' for r in routes)
        shell = '<html><body><main data-workspace-shell="cbcc-commercial-v1">' + body + '</main></body></html>'
    else:
        shell = '<html><body><main>' + ''.join(f'<section class="page" data-route="{r}"></section>' for r in ('overview','listing','strategy','product','visual','content','prompts','sources')) + '</main></body></html>'
    (root / 'index.html').write_text(shell, encoding='utf-8')
    (root / 'HUMAN_DELIVERY.json').write_text('{"task_scope":{"listing_active":false},"copy_center":[],"localized_copy":[]}', encoding='utf-8')
    (root / 'strategy' / 'strategy_authority.json').write_text('{"sections":{}}', encoding='utf-8')
    (root / 'ASSET_UNIVERSE.json').write_text('{"total_asset_candidates":1}', encoding='utf-8')
    asset = root / 'asset_packages' / 'AST-X'
    (asset / '00_asset_manifest.yaml').write_text('asset_id: AST-X\n', encoding='utf-8')
    for name in ('00_HUMAN_DESIGN_CARD_CN.md','01_strategy.md','02_visual_spec.md','05_prompt_CN.txt','06_prompt_EN.txt','07_generation_guidance.txt','08_copy.md','09_production_notes.md','10_source_trace.md'):
        value = 'UNIQUE_ASSET_VALUE' if heavy_legacy else ('中文测试' if 'CN' in name or name.endswith('.md') else 'english test')
        (asset / name).write_text(value, encoding='utf-8')
    for name, obj in {
        '03_photography_contract.json': {}, '04_layout_contract.json': {}, '11_strategy_authority_trace.json': {},
        '12_design_card.json': {}, '13_prompt_contract.json': {'large_unique_contract': 'X' * 1_000_000} if not heavy_legacy else {'unique':'UNIQUE_ASSET_VALUE'},
        '14_visible_copy_block.json': {}, '15_production_assembly_notes.json': {}, 'CANONICAL_LINEAGE.json': {},
    }.items():
        (asset / name).write_text(json.dumps(obj), encoding='utf-8')
    return root


def test_final_human_projection_materializes_heavy_canonical_value_once(tmp_path: Path):
    package = _fixture(tmp_path)
    result = finalize_legacy_projection(package)
    html = (package / 'index.html').read_text(encoding='utf-8')
    assert result['status'] == 'PASS'
    assert result['projection_mode'] == 'DEDUPLICATED_SINGLE_MATERIALIZATION'
    assert len(html.encode('utf-8')) < 4_500_000
    assert html.count('X' * 1000) < 1100
    assert 'CBCC_CANONICAL_STATIC_PROJECTION_V0672' in html
    assert 'replaceChildren' in html and 'textContent' in html


def test_real_routed_workspace_uses_lazy_single_materialization(tmp_path: Path):
    package = _fixture(tmp_path, heavy_legacy=True)
    result = finalize_lazy_projection(package)
    html = (package / 'index.html').read_text(encoding='utf-8')
    assert result['status'] == 'PASS'
    assert result['projection_mode'] == 'SELF_CONTAINED_LAZY_SINGLE_MATERIALIZATION'
    assert 'LEGACY_DUPLICATE_TOKEN' not in html
    for route in ('product','market','listing','strategy','content','visual','prompts','risk','sources','archive','asset/AST-X'):
        assert f'data-route="{route}"' in html
    assert 'cbcc-canonical-data-v0672' in html and 'CBCC_CANONICAL_LAZY_PROJECTION_V0672' in html
    assert 'data-canonical-mount="assets[0]"' in html and '#asset/AST-X' in html
    assert 'replaceChildren' in html and 'textContent' in html and 'innerHTML' not in html
    assert len(html.encode('utf-8')) < 3_500_000
    assert html.count('UNIQUE_ASSET_VALUE') < 40


def test_lazy_projection_is_idempotent(tmp_path: Path):
    package = _fixture(tmp_path, heavy_legacy=True)
    first = finalize_lazy_projection(package)
    size1 = (package / 'index.html').stat().st_size
    second = finalize_lazy_projection(package)
    size2 = (package / 'index.html').stat().st_size
    assert first['status'] == 'PASS' and second['status'] == 'PASS'
    assert second['legacy_route_compaction']['status'] == 'ALREADY_APPLIED'
    assert size1 == size2
