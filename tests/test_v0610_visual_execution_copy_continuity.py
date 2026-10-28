from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.compiler import build_project
from cbcc.delivery_html import build_delivery_html
from cbcc.prompt_compiler import compile_asset_prompt


def _asset():
    return {
        'asset_id': 'AST-VISUAL-CONTINUITY',
        'asset_name': 'Visual Continuity Proof',
        'asset_type': 'IMAGE',
        'surface': 'GALLERY',
        'family': 'VISUAL',
        'production_mode': 'REAL_PRODUCT_COMPOSITE',
        'product_fidelity': 'LOCKED_PIXEL',
        'consumer_question': 'What is this product?',
        'strategic_job': 'Identify the exact product without changing its identity.',
        'visible_copy': {'en-MY': 'Daily gel moisturiser', 'ms-MY': 'Gel pelembap harian'},
        'approved_visual_elements': ['real locked product layer', 'warm neutral set', 'controlled shadow'],
        'precision_boundaries': ['do not regenerate the package', 'keep exact product color'],
        'editable_layer_contract': {
            'editable_layers': ['background_environment', 'shadow_contact', 'typography_copy'],
            'frozen_layers': ['product_master_pixels', 'logo', 'packaging_print', 'product_geometry', 'product_color_identity'],
            'revision_rule': 'Only the requested editable layers may change; frozen product identity remains untouched.',
        },
        'creative_brief': {
            'composition': 'single hero product with deliberate mobile-safe negative space',
            'color': 'warm neutral white + authentic brand green',
        },
    }


def test_visual_execution_boundaries_flow_to_render_prompt_without_rendering_locked_copy():
    asset = _asset()
    out = compile_asset_prompt(
        asset,
        {'name': 'Test product'},
        {'market': 'Malaysia', 'platform_family': 'tiktok_shop'},
        {},
        {'primary_locale': 'en-MY'},
        photography={'capture_mode': 'COMPOSITE'},
        source_product_assets=[{'asset_id': 'REAL-1', 'pixel_lock': True}],
    )

    card = out['design_card']
    assert card['approved_visual_elements'] == asset['approved_visual_elements']
    assert card['precision_boundaries'] == asset['precision_boundaries']
    assert card['editable_layer_contract'] == asset['editable_layer_contract']
    assert card['product_identity']['product_fidelity'] == 'LOCKED_PIXEL'
    assert out['machine_visual_contract']['approved_visual_elements'] == asset['approved_visual_elements']
    assert out['renderer_recipe']['local_revision_contract'] == asset['editable_layer_contract']
    assert out['deterministic_copy_overlay'] == asset['visible_copy']

    for prompt in (out['prompt_cn'], out['prompt_en']):
        for required in [
            'real locked product layer', 'warm neutral set', 'controlled shadow',
            'do not regenerate the package', 'product_master_pixels', 'product_color_identity', 'LOCKED_PIXEL',
        ]:
            assert required in prompt
        # Exact marketing copy remains a deterministic overlay, not image-model text generation.
        assert 'Daily gel moisturiser' not in prompt
        assert 'Gel pelembap harian' not in prompt

    trace = [x for x in out['parameter_trace'] if x.get('render_location') == 'VISUAL EXECUTION BOUNDARIES / EDITABILITY']
    assert len(trace) == 1
    assert trace[0]['value']['approved_visual_elements'] == asset['approved_visual_elements']
    assert trace[0]['value']['editable_layer_contract'] == asset['editable_layer_contract']


def test_real_kiyuu_fixture_surfaces_visual_boundaries_and_locked_copy_in_human_workspace(tmp_path):
    fixture = ROOT / 'tests' / 'fixtures' / 'kiyuu_my_tiktok'
    request = json.loads((fixture / 'request.json').read_text(encoding='utf-8'))
    build_project(tmp_path, request, fixture)

    package_root = tmp_path / 'artifacts' / 'asset_packages'
    packages = sorted(p for p in package_root.iterdir() if p.is_dir())
    assert len(packages) == 3

    expected_by_name = {row['asset_name']: row for row in request['asset_jobs']}
    for package in packages:
        design = json.loads((package / '12_design_card.json').read_text(encoding='utf-8'))
        prompt = json.loads((package / '13_prompt_contract.json').read_text(encoding='utf-8'))
        expected = expected_by_name[design['asset_name']]

        assert design['approved_visual_elements'] == expected['approved_visual_elements']
        assert design['editable_layer_contract']['frozen_layers']
        assert design['product_identity']['product_fidelity'] == 'LOCKED_PIXEL'
        for key in ('canonical_prompt_cn', 'canonical_prompt_en'):
            text = prompt[key]
            for required in expected['approved_visual_elements']:
                assert required in text
            assert 'product_master_pixels' in text
            assert 'LOCKED_PIXEL' in text

        overlay = prompt['deterministic_copy_overlay']
        assert overlay == (expected.get('visible_copy') or {})
        for exact_copy in overlay.values():
            assert exact_copy not in prompt['canonical_prompt_cn']
            assert exact_copy not in prompt['canonical_prompt_en']

    html = build_delivery_html(tmp_path, tmp_path / 'index.html').read_text(encoding='utf-8')
    assert html.count('允许进入画面的视觉元素') >= len(packages)
    assert html.count('冻结层') >= len(packages)
    assert html.count('商品保真模式') >= len(packages)
    # Two fixture assets carry locked visible copy; they must be visible as structured Copy workbench content.
    assert html.count('锁定的目标市场可见文案') >= 2
    assert 'Daily gel moisturiser' in html
    assert '0.57% SA · 1% Nia · 2% Pan' in html
