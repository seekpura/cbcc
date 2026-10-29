from __future__ import annotations

import json
from pathlib import Path
import yaml


def _write_json(path:Path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')


def _make_asset(root:Path, aid:str, variant_id:str, cluster:str, state:str, surface:str='GALLERY') -> Path:
    d=root/'asset_packages'/aid
    d.mkdir(parents=True,exist_ok=True)
    manifest={
        'asset_id':aid,'asset_name':f'{cluster} {variant_id}','asset_type':'IMAGE','status':'ACTIVATE',
        'surface':surface,'family':'VISUAL','consumer_question':'Which creative hypothesis wins?',
        'decision_intent':'IDENTIFY','production_mode':'AI_REFERENCE_PRODUCT','product_fidelity':'REFERENCE_GUIDED_NATIVE_LOCK',
        'variant_id':variant_id,'variant_cluster':cluster,'deployment_state':state,
        'testing_variant':state in {'TEST_POOL','ROTATION_POOL'},'test_hypothesis':f'{variant_id} hypothesis',
        'activation_set_id':'ACT-01' if state=='LIVE_CANDIDATE' else None,
    }
    (d/'00_asset_manifest.yaml').write_text(yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False),encoding='utf-8')
    _write_json(d/'12_design_card.json',{
        'asset_id':aid,'asset_name':manifest['asset_name'],'surface':surface,'asset_type':'IMAGE',
        'commerce_task':{'decision_intent':'IDENTIFY','consumer_question':'Which creative hypothesis wins?','reason_to_exist':'测试不同 Hero 创意假设。'},
        'agent_art_direction':{
            'visual_carrier':'PHOTOGRAPHIC_COMMERCE_IMAGE','creative_thesis':{'cn':'不同 Hero 假设。','en':'Distinct hero hypothesis.'},
            'composition_grammar':{'cn':'非模板化构图。','en':'Non-template composition.'},
            'layout_geometry':'product x=64%, y=52%','scale_depth':'product 62% canvas height',
            'focal_path':'product → evidence → copy','negative_space':'upper-left breathing field',
            'product_occupancy':'62% canvas height','palette_hex':['#F6F3EC','#0B3B31'],
            'material_response':'truthful matte package response','post_look':'neutral editorial finish',
            'product_presence':{'planning_state':'HERO_REQUIRED','production_state':'PRESENT','source_reference_role':'SUBJECT_REFERENCE'},
        },
        'product_presence':{'planning_state':'HERO_REQUIRED','production_state':'PRESENT','source_reference_role':'SUBJECT_REFERENCE'},
        'product_identity':{'product_fidelity':'REFERENCE_GUIDED_NATIVE_LOCK'},
    })
    _write_json(d/'13_prompt_contract.json',{'model_prompt_status':'MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'})
    _write_json(d/'14_visible_copy_block.json',{})
    _write_json(d/'15_production_assembly_notes.json',{
        'copy_render_mode':'NO_VISIBLE_COPY','product_fidelity':'REFERENCE_GUIDED_NATIVE_LOCK',
        'product_reference_generation_mode':'REFERENCE_GUIDED_NATIVE_GENERATION',
        'reference_input_required':True,'final_output_must_contain_generated_product':True,
        'product_presence':'HERO_REQUIRED','product_reference_rule':'Use real product images as strong model reference inputs.',
    })
    (d/'05_prompt_CN.txt').write_text('真实商品参考图作为强参考输入，原生生成完整最终画面中的商品。',encoding='utf-8')
    (d/'06_prompt_EN.txt').write_text('Use the real product reference image as a strong input and natively render the product in the complete final image.',encoding='utf-8')
    return d


def test_formal_asset_preserves_variant_pool_and_native_reference_generation(tmp_path:Path):
    from cbcc.delivery_html import _formal_asset_dir
    d=_make_asset(tmp_path,'AST-H01','H01','HERO','TEST_POOL')
    a=_formal_asset_dir(d,tmp_path)
    assert a['variant_id']=='H01'
    assert a['variant_cluster']=='HERO'
    assert a['deployment_state']=='TEST_POOL'
    assert a['test_hypothesis']=='H01 hypothesis'
    production=next(v for v in a['views'] if v['key']=='production')['html']
    assert 'REFERENCE_GUIDED_NATIVE_GENERATION' in production
    assert '真实商品 Reference Input' in production
    assert '最终商品必须原生生成' in production


def test_asset_universe_workspace_groups_live_test_paid_and_pdp_without_total_slot_cap(tmp_path:Path):
    from cbcc.delivery_html import _formal_asset_dir, _asset_universe_cards
    rows=[]
    specs=[
        ('AST-H01','H01','HERO','LIVE_CANDIDATE','GALLERY'),
        ('AST-H02','H02','HERO','TEST_POOL','GALLERY'),
        ('AST-H03','H03','HERO','ROTATION_POOL','GALLERY'),
        ('AST-AD01','AD01','PAID_AD','PAID_MEDIA','PAID_AD'),
        ('AST-AP01','AP01','A_PLUS_PDP','PDP_CONTENT','A_PLUS'),
    ]
    for spec in specs:
        rows.append(_formal_asset_dir(_make_asset(tmp_path,*spec),tmp_path))
    body=_asset_universe_cards(rows)
    for label in ['当前上线候选','测试池','轮换池','广告资产','PDP / A+ / 详情']:
        assert label in body
    for vid in ['H01','H02','H03','AD01','AP01']:
        assert vid in body
    assert 'H02 hypothesis' in body


def test_asset_card_shows_variant_cluster_and_deployment_state():
    from cbcc.delivery_html import _asset_card
    html=_asset_card({
        'id':'AST-X','title':'Hero variant','original_title':'Hero variant','summary':'',
        'asset_type':'IMAGE','surface':'GALLERY','intent':'IDENTIFY','variant_cluster':'HERO',
        'variant_id':'H04','deployment_state':'TEST_POOL','test_hypothesis':'More product-dominant conversion hypothesis',
    })
    assert 'HERO' in html
    assert 'H04' in html
    assert 'TEST_POOL' in html
    assert 'More product-dominant conversion hypothesis' in html
