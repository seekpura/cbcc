from pathlib import Path
import json

from cbcc.human_delivery import compile_upload_center, build_project_hub_md
from cbcc.tools.listing import listing_conversion_architecture


def _write(path:Path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')


def _base_project(tmp_path:Path):
    _write(tmp_path/'artifacts/product_truth.json',{'product':{'brand':'KIYUU','product_name':'K01 Gel','sku':'K01'}})
    _write(tmp_path/'artifacts/target_context.json',{'market':'MY','platform_family':'TikTok Shop','site':'MY','language':{'primary_locale':'en-MY','delivery_locale':'zh-CN'}})
    _write(tmp_path/'artifacts/platform_compile.json',{})
    return tmp_path


def test_visual_only_scope_does_not_manufacture_listing_holds(tmp_path):
    p=_base_project(tmp_path)
    _write(p/'meta/request.json',{'project_id':'V','content_families':['VISUAL'],'compile_assets':True,'goal':'制作商品视觉资产'})
    _write(p/'artifacts/agent_autonomy_plan.json',{'content_scope':{'families':['VISUAL']}})
    _write(p/'artifacts/agent_next_action.json',{'status':'ACTION_FRONTIER_OPEN','recommended_next_action':'REPLAN_ASSET_ARCHITECTURE','frontier':[{'action':'REPLAN_ASSET_ARCHITECTURE','reason':'资产需要继续规划'}]})
    center=compile_upload_center(p)
    assert center['task_scope']['listing_active'] is False
    assert center['readiness']['status']=='NOT_IN_CURRENT_SCOPE'
    assert center['copy_center']==[]
    preserved={x['field'] for x in center['preserved_listing_fields']}
    assert {'brand','product_name','sku'} <= preserved
    for field in ['price','shipping','returns','seller_info']:
        assert field not in preserved
    hub=build_project_hub_md(center)
    assert 'Listing 字段不参与项目 readiness' in hub
    assert 'REPLAN_ASSET_ARCHITECTURE' in hub


def test_listing_scope_only_blocks_current_required_fields(tmp_path):
    p=_base_project(tmp_path)
    _write(p/'meta/request.json',{'project_id':'L','content_families':['LISTING'],'listing_input':{'fields':{'title':'KIYUU K01 Gel'}}})
    _write(p/'artifacts/agent_autonomy_plan.json',{'content_scope':{'families':['LISTING']}})
    _write(p/'artifacts/listing_analysis.json',{'compiled':{'fields':{'title':'KIYUU K01 Gel'},'field_contracts':[{'field':'title','required':True},{'field':'shipping','required':True}],'localization_transcreation':{'primary_locale':'en-MY'}}})
    center=compile_upload_center(p)
    rows={x['field']:x for x in center['copy_center']}
    assert center['task_scope']['listing_active'] is True
    assert center['readiness']['status']=='READY_WITH_HOLDS'
    assert center['readiness']['pending_fields']==['shipping']
    assert rows['shipping']['required_for_current_scope'] is True
    for optional in ['price','returns','seller_info']:
        assert optional not in rows


def test_listing_scope_without_platform_requirement_does_not_invent_offer_ops(tmp_path):
    p=_base_project(tmp_path)
    _write(p/'meta/request.json',{'project_id':'L2','content_families':['LISTING'],'listing_input':{'fields':{'title':'KIYUU K01 Gel','description':'Daily gel'}}})
    _write(p/'artifacts/agent_autonomy_plan.json',{'content_scope':{'families':['LISTING']}})
    _write(p/'artifacts/listing_analysis.json',{'compiled':{'fields':{'title':'KIYUU K01 Gel','description':'Daily gel'},'field_contracts':[{'field':'title','required':True}],'localization_transcreation':{'primary_locale':'en-MY'}}})
    center=compile_upload_center(p)
    assert center['readiness']['status']=='READY_FOR_CURRENT_SCOPE'
    fields={x['field'] for x in center['copy_center']}
    assert 'title' in fields and 'description' in fields
    assert not ({'price','shipping','returns','seller_info'} & fields)


def test_listing_conversion_architecture_projects_only_active_fields():
    arch=listing_conversion_architecture({'title':'A','description':'B'}, {}, [], {})
    assert arch['click_layer']['fields']==['title']
    assert arch['post_purchase_prevention']['fields']==[]
    assert arch['fixed_field_quota'] is None
    arch2=listing_conversion_architecture({'title':'A','faq':'Q'}, {}, [], {'shipping':{'required':True}})
    assert arch2['post_purchase_prevention']['fields']==['faq','shipping']
    assert 'price' not in arch2['click_layer']['fields']
