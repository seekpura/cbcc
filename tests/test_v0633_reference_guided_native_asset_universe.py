from pathlib import Path


def test_source_pixel_lock_means_native_reference_identity_lock_unless_exact_pixel_is_explicit(tmp_path:Path):
    from cbcc.compiler import _normalize_source_product_assets
    p=tmp_path/'product.png'; p.write_bytes(b'product-master')
    rows=_normalize_source_product_assets([
        {'asset_id':'P1','path':str(p),'pixel_lock':True},
        {'asset_id':'P2','path':str(p),'pixel_lock':True,'exact_pixel_layer':True},
    ],[tmp_path])
    assert rows[0]['fidelity_mode']=='REFERENCE_GUIDED_NATIVE_LOCK'
    assert rows[0]['pixel_lock'] is False
    assert rows[0]['source_usage']=='MODEL_REFERENCE_INPUT'
    assert 'NATIVE_RENDER' in rows[0]['allowed_transforms']
    assert rows[1]['fidelity_mode']=='EXACT_PIXEL_COMPOSITE'
    assert rows[1]['pixel_lock'] is True
    assert rows[1]['source_usage']=='EXACT_PIXEL_SOURCE_LAYER'


def test_visible_locked_real_product_is_natively_generated_from_reference_not_removed_for_composite():
    from cbcc.reference_guided_native_authority import apply_reference_guided_native_authority
    asset={
        'product_fidelity':'LOCKED_PIXEL',
        'production_mode':'AI_REFERENCE_PRODUCT',
    }
    source=[{'asset_id':'MASTER-FRONT','path':'front.png','sha256':'abc'}]
    bundle={
        'design_card':{
            'product_presence':{'planning_state':'HERO_REQUIRED','production_state':'PRESENT'},
            'product_identity':{'product_fidelity':'LOCKED_PIXEL','source_product_assets':source},
        },
        'model_prompt_cn':'创建商业商品图。\n以最终合成画面而不是空背景为目标生成环境底片：不要生成、重画或替代真实商品本体，但生成底片必须让后续真实商品合成后看起来像同一个空间。\n',
        'model_prompt_en':'Create a commercial image.\nGenerate the environment plate for the final composite, not as an unrelated empty background. Do not render, redraw or substitute the product itself; the plate must integrate the later real-product layer as if it belonged to the same photographed scene.\n',
        'renderer_recipe':{'source_product_bindings':[{'asset_id':'MASTER-FRONT','usage_role':'LOCKED_SOURCE_LAYER'}]},
        'production_parameter_closure':{'missing_required_parameters':[],'status':'PASS','model_generation_blocking':False},
    }
    out=apply_reference_guided_native_authority(bundle,asset,source)
    assert '原生生成完整最终画面中的商品' in out['model_prompt_cn']
    assert 'natively render the product inside the complete final image' in out['model_prompt_en']
    assert 'Do not render, redraw or substitute the product itself' not in out['model_prompt_en']
    assert '环境底片' not in out['model_prompt_cn']
    assert out['design_card']['product_identity']['product_fidelity']=='REFERENCE_GUIDED_NATIVE_LOCK'
    assert out['renderer_recipe']['product_generation_mode']=='REFERENCE_GUIDED_NATIVE_GENERATION'
    assert out['renderer_recipe']['source_product_bindings'][0]['usage_role']=='NATIVE_SUBJECT_REFERENCE'
    assert out['renderer_recipe']['source_product_bindings'][0]['native_generation_required'] is True
    assert out['production_assembly_notes']['pixel_composite_is_default'] is False


def test_exact_pixel_composite_requires_explicit_exact_pixel_intent():
    from cbcc.reference_guided_native_authority import apply_reference_guided_native_authority
    asset={'product_fidelity':'EXACT_PIXEL_COMPOSITE','exact_pixel_layer':True}
    source=[{'asset_id':'P','path':'p.png'}]
    bundle={'design_card':{'product_presence':{'planning_state':'REQUIRED','production_state':'PRESENT'},'product_identity':{'product_fidelity':'EXACT_PIXEL_COMPOSITE','source_product_assets':source}},'renderer_recipe':{'source_product_bindings':[{'asset_id':'P'}]},'production_parameter_closure':{}}
    out=apply_reference_guided_native_authority(bundle,asset,source)
    assert out['renderer_recipe']['product_generation_mode']=='EXACT_PIXEL_COMPOSITE'
    assert out['renderer_recipe']['pixel_composite_required'] is True
    assert out['renderer_recipe']['source_product_bindings'][0]['usage_role']=='EXACT_PIXEL_SOURCE_LAYER'


def test_twenty_explicit_assets_and_multiple_hero_variants_survive_same_question_surface_family():
    from cbcc.asset_architecture import build_asset_architecture
    jobs=[]
    for i in range(20):
        jobs.append({
            'consumer_question':'What is the clearest first reason to choose this product?',
            'decision_intent':'IDENTIFY' if i < 6 else 'PROOF',
            'surface':'GALLERY' if i < 12 else ('PAID_AD' if i < 16 else 'A_PLUS'),
            'family':'VISUAL' if i < 12 else ('PAID' if i < 16 else 'RICH_CONTENT'),
            'variant_id':f'H{i+1:02d}' if i < 6 else f'V{i+1:02d}',
            'variant_cluster':'HERO' if i < 6 else ('PAID_AD' if i < 16 and i >= 12 else 'BENEFIT'),
            'deployment_state':'TEST_POOL' if i % 2 else 'LIVE_CANDIDATE',
            'testing_variant':bool(i % 2),
            'creative_hypothesis':f'hypothesis {i+1}',
            'asset_name':f'Variant {i+1}',
        })
    out=build_asset_architecture('P1',{'target_id':'MY-TT','listing_image_capacity':9},[],[],jobs,{},'BEAUTY')
    assert out['fixed_count_authority'] is False
    assert out['asset_count']==20
    assert len(out['assets'])==20
    assert len({a['asset_id'] for a in out['assets']})==20
    assert len([a for a in out['assets'] if a.get('variant_cluster')=='HERO'])==6
    assert out['asset_universe']['fixed_total_asset_limit'] is False
    assert out['asset_universe']['platform_capacity']==9
    assert out['asset_universe']['total_asset_candidates']==20
    assert len(out['asset_universe']['clusters']['HERO'])==6
    assert len(out['asset_universe']['pools']['TEST_POOL'])==10


def test_platform_capacity_limits_activation_only_and_other_surface_families_are_supported():
    from cbcc.asset_architecture import build_asset_architecture
    jobs=[
        {'consumer_question':'hero a','decision_intent':'IDENTIFY','surface':'GALLERY','family':'VISUAL','variant_id':'H01'},
        {'consumer_question':'hero b','decision_intent':'IDENTIFY','surface':'GALLERY','family':'VISUAL','variant_id':'H02','deployment_state':'TEST_POOL'},
        {'consumer_question':'ad hook','decision_intent':'PROOF','surface':'PAID_AD','family':'PAID','variant_id':'AD01','deployment_state':'PAID_MEDIA'},
        {'consumer_question':'detail proof','decision_intent':'PROOF','surface':'A_PLUS','family':'RICH_CONTENT','variant_id':'AP01','deployment_state':'PDP_CONTENT'},
        {'consumer_question':'long detail','decision_intent':'USAGE','surface':'LONGFORM','family':'RICH_CONTENT','variant_id':'PDP01','deployment_state':'PDP_CONTENT'},
        {'consumer_question':'store message','decision_intent':'IDENTIFY','surface':'STORE_BANNER','family':'STORE','variant_id':'S01'},
    ]
    out=build_asset_architecture('P2',{'target_id':'T','gallery_capacity':1},[],[],jobs,{},'BEAUTY')
    assert out['asset_count']==6
    assert out['asset_universe']['platform_capacity_is_activation_constraint_only'] is True
    surfaces={a['surface'] for a in out['assets']}
    assert {'GALLERY','PAID_AD','A_PLUS','LONGFORM','STORE_BANNER'}.issubset(surfaces)


def test_reference_product_provider_route_requires_reference_source_binding():
    from cbcc.providers import route_production
    row=route_production({'asset_id':'A','production_mode':'AI_REFERENCE_PRODUCT','product_fidelity':'REFERENCE_GUIDED_NATIVE_LOCK'})
    assert row['provider']=='AI_IMAGE_PROVIDER'
    assert row['route_status']=='READY'
    contract=row['provider_contract']
    assert 'source_product_assets' in contract['required_inputs']
    assert contract['source_binding_contract']['required'] is True
    assert 'native_reference_result_evidence' in contract['source_binding_contract']
