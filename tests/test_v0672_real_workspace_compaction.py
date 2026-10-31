from pathlib import Path
import json
from cbcc.canonical_human_lazy_projection_v0672 import finalize_static_human_projection


def _fixture(root: Path) -> Path:
    (root/'asset_packages'/'AST-X').mkdir(parents=True); (root/'strategy').mkdir(); (root/'supporting_analysis').mkdir()
    heavy='LEGACY_DUPLICATE_TOKEN|'*50000
    routes=['overview','product','market','listing','strategy','content','visual','prompts','risk','sources','archive','asset/AST-X']
    (root/'index.html').write_text('<html><body><main data-workspace-shell="cbcc-commercial-v1">'+''.join(f'<section class="page" data-route="{r}">{heavy if r != "overview" else "small"}</section>' for r in routes)+'</main></body></html>',encoding='utf-8')
    (root/'HUMAN_DELIVERY.json').write_text(json.dumps({'task_scope':{'listing_active':False},'copy_center':[],'localized_copy':[]}),encoding='utf-8')
    (root/'strategy'/'strategy_authority.json').write_text('{"sections":{}}',encoding='utf-8'); (root/'ASSET_UNIVERSE.json').write_text('{"total_asset_candidates":1}',encoding='utf-8')
    a=root/'asset_packages'/'AST-X'; (a/'00_asset_manifest.yaml').write_text('asset_id: AST-X\n',encoding='utf-8')
    for name in ('00_HUMAN_DESIGN_CARD_CN.md','01_strategy.md','02_visual_spec.md','05_prompt_CN.txt','06_prompt_EN.txt','07_generation_guidance.txt','08_copy.md','09_production_notes.md','10_source_trace.md'):(a/name).write_text('UNIQUE_ASSET_VALUE',encoding='utf-8')
    for name,obj in {'03_photography_contract.json':{},'04_layout_contract.json':{},'11_strategy_authority_trace.json':{},'12_design_card.json':{},'13_prompt_contract.json':{'unique':'UNIQUE_ASSET_VALUE'},'14_visible_copy_block.json':{},'15_production_assembly_notes.json':{},'CANONICAL_LINEAGE.json':{}}.items():(a/name).write_text(json.dumps(obj),encoding='utf-8')
    return root


def test_real_routed_workspace_compacts_legacy_duplicates_and_keeps_full_data(tmp_path: Path):
    package=_fixture(tmp_path); result=finalize_static_human_projection(package); text=(package/'index.html').read_text(encoding='utf-8')
    assert result['status']=='PASS'; assert result['projection_mode']=='SELF_CONTAINED_LAZY_SINGLE_MATERIALIZATION'
    assert 'LEGACY_DUPLICATE_TOKEN' not in text
    for route in ('product','market','listing','strategy','content','visual','prompts','risk','sources','archive','asset/AST-X'):assert f'data-route="{route}"' in text
    assert 'cbcc-canonical-data-v0672' in text and 'CBCC_CANONICAL_LAZY_PROJECTION_V0672' in text
    assert 'data-canonical-mount="assets[0]"' in text and '#asset/AST-X' in text
    assert 'replaceChildren' in text and 'textContent' in text and 'innerHTML' not in text
    assert len(text.encode('utf-8')) < 3_500_000
    assert text.count('UNIQUE_ASSET_VALUE') < 40


def test_lazy_projection_is_idempotent(tmp_path: Path):
    package=_fixture(tmp_path); first=finalize_static_human_projection(package); size1=(package/'index.html').stat().st_size
    second=finalize_static_human_projection(package); size2=(package/'index.html').stat().st_size
    assert first['status']=='PASS' and second['status']=='PASS'
    assert second['legacy_route_compaction']['status']=='ALREADY_APPLIED'
    assert size1==size2
