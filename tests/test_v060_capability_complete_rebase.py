from pathlib import Path
import json, sys, re

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project


def _build(tmp_path, fixture):
    req=json.loads((ROOT/'tests/fixtures/v058_multicategory'/fixture).read_text(encoding='utf-8'))
    p=tmp_path/Path(fixture).stem
    build_project(p,req,ROOT/'platform_packs')
    return p


def test_v060_creative_system_is_category_and_decision_specific(tmp_path):
    styles=[]; selected_routes=[]
    for fx in ['beauty_kiyuu.json','fashion_uniqlo_bag.json','home_ikea365_container.json']:
        p=_build(tmp_path,fx)
        strategy=json.loads((p/'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
        visual=strategy['sections']['05_visual_photography_strategy']
        styles.append(visual['style'])
        opportunity=json.loads((p/'artifacts/creative_opportunity_universe.json').read_text(encoding='utf-8'))
        assert opportunity['opportunity_count'] > 0
        assert len({x['mechanism_id'] for x in opportunity['opportunities']}) == opportunity['opportunity_count']
        council=json.loads((p/'artifacts/creative_council.json').read_text(encoding='utf-8'))
        assert len(council['directions']) > 0
        assert council['direction_source']=='CREATIVE_OPPORTUNITY_SYNTHESIS'
        assert council['selected_direction'].get('opportunity_ids')
        assert council['selected_direction'].get('opportunity_mechanisms')
        selected_routes.append(council['selected_direction']['route'])
        arch=json.loads((p/'artifacts/asset_architecture.json').read_text(encoding='utf-8'))
        assert all(a.get('race_stage')=='COMMUNICATION' for a in arch['assets'])
        assert len({(a.get('visual_expression_variant') or {}).get('variant_id') for a in arch['assets']}) >= 3
    assert len(set(styles))==3
    assert len(set(selected_routes))>=2


def test_v060_asset_package_contains_deep_design_and_model_native_production_objects(tmp_path):
    p=_build(tmp_path,'beauty_kiyuu.json')
    idx=json.loads((p/'artifacts/asset_packages/ASSET_PACKAGE_INDEX.json').read_text(encoding='utf-8'))
    assert idx['assets']
    d=p/'artifacts/asset_packages'/idx['assets'][0]['asset_id']
    for name in ['12_design_card.json','13_prompt_contract.json','14_visible_copy_block.json','15_production_assembly_notes.json','05_prompt_CN.txt','06_prompt_EN.txt']:
        assert (d/name).exists(), name
    card=json.loads((d/'12_design_card.json').read_text(encoding='utf-8'))
    contract=json.loads((d/'13_prompt_contract.json').read_text(encoding='utf-8'))
    for key in ['commerce_task','creative_system','visual_narrative','composition_camera','lighting_material_cmf','information_design','surface_contract','product_identity']:
        assert key in card
    cn=(d/'05_prompt_CN.txt').read_text(encoding='utf-8')
    en=(d/'06_prompt_EN.txt').read_text(encoding='utf-8')
    # Model prompts are judged by consumed decisions, not an arbitrary minimum line quota.
    assert cn.strip() and en.strip()
    assert 'deterministic' not in cn.casefold()
    assert 'deterministic' not in en.casefold()
    assert not re.search(r'[\u3400-\u9fff]',en)
    assert contract.get('model_prompt_cn') and contract.get('model_prompt_en')
    assert contract.get('visible_copy_block') is not None
    assert contract.get('production_assembly_notes') is not None
    assert contract.get('machine_visual_contract') and contract.get('renderer_recipe') and contract.get('qa_target_contract')


def test_v060_bound_product_reference_does_not_imply_pixel_lock_or_force_post_layout_text(tmp_path):
    # Product source files are design references by default. Exact immutable-source composition is explicit-only.
    # Copy-render route is also explicit; Runtime must not globally force deterministic post-render composition.
    p=_build(tmp_path,'beauty_kiyuu.json')
    idx=json.loads((p/'artifacts/asset_packages/ASSET_PACKAGE_INDEX.json').read_text(encoding='utf-8'))
    d=p/'artifacts/asset_packages'/idx['assets'][0]['asset_id']
    contract=json.loads((d/'13_prompt_contract.json').read_text(encoding='utf-8'))
    text_policy=contract['renderer_recipe']['text_policy']
    assert text_policy['copy_render_mode'] in {'MODEL_RENDER','POST_COMPOSITE','HYBRID','NO_VISIBLE_COPY','UNRESOLVED_AGENT_DECISION'}
    assert text_policy.get('exact_copy_mode')!='DETERMINISTIC_COMPOSITION_AFTER_RENDER'
    assert contract['machine_visual_contract']['fidelity']['real_product_master_required'] is False
    assert contract['machine_visual_contract']['fidelity']['real_product_master_substitution_allowed'] is True
