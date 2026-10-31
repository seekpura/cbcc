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
    heavy = {f'field_{i:05d}': ('X' * 180) + str(i) for i in range(6500)}
    for name, obj in {
        '03_photography_contract.json': {}, '04_layout_contract.json': {}, '11_strategy_authority_trace.json': {},
        '12_design_card.json': {}, '13_prompt_contract.json': {'large_unique_contract': heavy},
        '14_visible_copy_block.json': {}, '15_production_assembly_notes.json': {}, 'CANONICAL_LINEAGE.json': {},
    }.items():
        (asset / name).write_text(json.dumps(obj), encoding='utf-8')
    return root


def test_final_human_projection_keeps_heavy_assets_single_embedded_and_lazy(tmp_path: Path):
    package = _fixture(tmp_path)
    result = finalize_static_human_projection(package)
    html = (package / 'index.html').read_text(encoding='utf-8')
    data_bytes = (package / 'CANONICAL_HUMAN_DATA.json').stat().st_size
    html_bytes = len(html.encode('utf-8'))

    assert result['status'] == 'PASS'
    assert result['projection_mode'] == 'LAZY_SINGLE_EMBEDDED_CANONICAL_PAYLOAD'
    assert 'id="cbcc-canonical-payload-v0672"' in html
    assert 'data-canonical-lazy-root="assets"' in html
    assert 'data-canonical-lazy-root="universe"' in html
    assert 'data-canonical-lazy-root="canonical_business_objects"' in html
    assert 'CBCC_CANONICAL_LAZY_INSPECTOR_V0672' in html
    assert 'const CBCC_CANONICAL_HUMAN=window.CBCC_CANONICAL_HUMAN_V0672' in html
    assert 'createTextNode' in html and 'textContent' in html
    # Heavy 00–15 leaves must not become one static DOM node per leaf.
    assert 'data-canonical-path="assets[0].prompt_contract.large_unique_contract.field_00001"' not in html
    # The self-contained HTML may embed the canonical payload once, but must not explode it into markup.
    assert html_bytes < data_bytes * 1.8 + 500_000


def test_lazy_projection_audit_fails_if_embedded_payload_is_removed(tmp_path: Path):
    package = _fixture(tmp_path)
    assert finalize_static_human_projection(package)['status'] == 'PASS'
    html_path = package / 'index.html'
    text = html_path.read_text(encoding='utf-8')
    start = text.index('<script type="application/json" id="cbcc-canonical-payload-v0672"')
    end = text.index('</script>', start) + len('</script>')
    html_path.write_text(text[:start] + text[end:], encoding='utf-8')

    from cbcc.canonical_human_compaction_v0672 import build_canonical_human_payload, audit_generic_human_field_coverage
    payload = build_canonical_human_payload(package)
    issues = audit_generic_human_field_coverage(payload, html_path.read_text(encoding='utf-8'))
    assert any(i['code'] == 'HTML_CANONICAL_LAZY_PAYLOAD_MISSING_V0672' for i in issues)


def test_existing_projection_refreshes_single_payload_after_package_authority_changes(tmp_path: Path):
    package = _fixture(tmp_path)
    first = finalize_static_human_projection(package)
    assert first['status'] == 'PASS'
    (package / 'ASSET_UNIVERSE.json').write_text(json.dumps({'total_asset_candidates': 2, 'product_presence_portfolio_audit': {'status': 'PASS'}}, ensure_ascii=False), encoding='utf-8')
    second = finalize_static_human_projection(package)
    html = (package / 'index.html').read_text(encoding='utf-8')
    assert second['status'] == 'PASS', second['issues']
    assert html.count('id="cbcc-canonical-payload-v0672"') == 1
    from cbcc.canonical_human_compaction_v0672 import build_canonical_human_payload, audit_generic_human_field_coverage
    assert audit_generic_human_field_coverage(build_canonical_human_payload(package), html) == []


def test_legacy_heavy_archive_video_and_asset_routes_are_compacted_to_lazy_views(tmp_path: Path):
    package = _fixture(tmp_path)
    # Add video authority and deliberately huge legacy static route bodies that duplicate package objects.
    (package / 'supporting_analysis' / 'video_creator_plan.json').write_text(json.dumps({
        'assets': [{'video_id': 'VID-1', 'hook': 'Routine hook', 'shots': [{'job': 'show use'}]}]
    }), encoding='utf-8')
    heavy = 'LEGACY_HEAVY_DUPLICATE_' + ('Z' * 50_000)
    base = '<html><body><main>' + ''.join(f'<section class="page" data-route="{r}"></section>' for r in ('overview','listing','strategy','product','visual','content','prompts','sources'))
    base += f'<section class="page" data-route="archive"><pre>{heavy}</pre></section>'
    base += f'<section class="page" data-route="video"><pre>{heavy}</pre></section>'
    base += f'<section class="page asset-page" data-route="asset/AST-X"><pre>{heavy}</pre></section>'
    base += '</main></body></html>'
    (package / 'index.html').write_text(base, encoding='utf-8')

    result = finalize_static_human_projection(package)
    html = (package / 'index.html').read_text(encoding='utf-8')
    assert result['status'] == 'PASS'
    assert 'LEGACY_HEAVY_DUPLICATE_' not in html
    assert 'data-route="archive"' in html and 'data-canonical-lazy-root="canonical_business_objects"' in html
    assert 'data-route="video"' in html and 'data-canonical-lazy-root="video"' in html
    assert 'data-route="asset/AST-X"' in html and 'data-cbcc-asset-route-index="0"' in html
    assert 'window.addEventListener(\'hashchange\'' in html
