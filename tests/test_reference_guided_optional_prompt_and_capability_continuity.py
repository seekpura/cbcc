from pathlib import Path
import json

from cbcc.compiler import _normalize_source_product_assets
from cbcc.asset_architecture import build_asset_architecture, _editable_layer_contract
from cbcc.asset_compiler import validate_asset_packages, REQUIRED_ASSET_FILES, OPTIONAL_PRODUCTION_FILES
from cbcc.delivery_export import _prompt_consumption_summary
from cbcc.tools.seven_agent import compile_seven_agent_synthesis, SEVEN_TOOLS


def test_source_product_assets_are_reference_guided_by_default(tmp_path):
    src=tmp_path/'p.png'; src.write_bytes(b'product-reference')
    rows=_normalize_source_product_assets([{'path':str(src)}],[tmp_path])
    assert rows[0]['pixel_lock'] is False
    assert rows[0]['identity_lock'] is False
    assert rows[0]['fidelity_mode']=='REFERENCE_GUIDED'
    assert rows[0]['source_usage']=='DESIGN_REFERENCE'
    assert 'RERENDER' in rows[0]['allowed_transforms']


def test_legacy_pixel_lock_means_native_identity_lock_not_exact_pixel_composite(tmp_path):
    src=tmp_path/'p.png'; src.write_bytes(b'product-reference')
    rows=_normalize_source_product_assets([{'path':str(src),'pixel_lock':True}],[tmp_path])
    assert rows[0]['pixel_lock'] is False
    assert rows[0]['identity_lock'] is True
    assert rows[0]['fidelity_mode']=='REFERENCE_GUIDED_NATIVE_LOCK'
    assert rows[0]['source_usage']=='MODEL_REFERENCE_INPUT'
    assert 'NATIVE_RENDER' in rows[0]['allowed_transforms']


def test_dynamic_gallery_asset_defaults_native_reference_lock_not_pixel_layer():
    target={'target_id':'T','surfaces':['GALLERY']}
    objects=[{'family':'VISUAL','surface':'GALLERY','curation_job':'Resolve identity','source_ids':[],'claim_ids':[]}]
    arch=build_asset_architecture('P',target,['What is this product?'],objects)
    assert arch['assets']
    assert arch['assets'][0]['product_fidelity']=='REFERENCE_GUIDED_NATIVE_LOCK'
    assert arch['assets'][0]['production_mode']=='AI_REFERENCE_PRODUCT'
    edit=_editable_layer_contract('AI_REFERENCE_PRODUCT','REFERENCE_GUIDED_NATIVE_LOCK')
    assert 'product_master_pixels' not in edit['frozen_layers']
    assert 'verified_product_facts' in edit['frozen_layers']


def test_prompt_generation_files_do_not_block_asset_package_validation(tmp_path):
    root=tmp_path/'assets'; d=root/'AST-1'; d.mkdir(parents=True)
    for name in REQUIRED_ASSET_FILES:
        p=d/name; p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('{}' if p.suffix in {'.json','.yaml'} else '# ok\n',encoding='utf-8')
    (root/'ASSET_PACKAGE_INDEX.json').write_text(json.dumps({'assets':[{'asset_id':'AST-1'}]}),encoding='utf-8')
    result=validate_asset_packages(root)
    assert result['pass'] is True
    assert result['prompt_generation_files_block_asset_delivery'] is False
    assert set(result['assets'][0]['optional_production_missing'])==set(OPTIONAL_PRODUCTION_FILES)


def test_prompt_consumption_is_advisory_for_project_completion(tmp_path):
    d=tmp_path/'AST-1'; d.mkdir()
    (d/'13_prompt_contract.json').write_text(json.dumps({'prompt_consumption_audit':{'status':'INCOMPLETE','missing_decisions':['camera']}}),encoding='utf-8')
    result=_prompt_consumption_summary(tmp_path)
    assert result['status']=='NEEDS_PROMPT_WORK'
    assert result['project_completion_blocking'] is False
    assert result['missing_assets']==['AST-1']


def test_seven_first_class_capabilities_are_synthesized_from_real_outputs():
    assert {str(i).zfill(2) for i in range(1,8)}.issubset(set(SEVEN_TOOLS))
    syn=compile_seven_agent_synthesis(
        domain={'market':{'status':'READY'},'economics':{'status':'READY','currency':'MYR'},'listing':{'status':'READY','compiled':{'objection_resolution_plan':[{'objection':'x'}]}},'ads':{'status':'READY','diagnosis':[{'route':'CLICK_PACKAGE'}]},'feedback':{'status':'READY','issues':[{'category':'MISUNDERSTANDING'}]}},
        architecture={'assets':[{'asset_id':'A','asset_type':'IMAGE','decision_origin':'FEEDBACK_SIGNAL'}]},
        video_plan={'assets':[{'asset_id':'V'}]},
        paid_campaigns={'campaigns':[{'id':'C'}]},
        source_product_assets=[{'asset_id':'P','source_usage':'DESIGN_REFERENCE'}],
    )
    assert syn['all_seven_available'] is True
    assert syn['all_seven_required_each_task'] is False
    assert len(syn['capabilities'])==7
    assert syn['asset_inputs']['product_sources']['default_usage']=='DESIGN_REFERENCE'
    assert '07_REVIEW_ANALYSIS' in syn['active_ids']
