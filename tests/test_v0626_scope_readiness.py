from pathlib import Path
import json

from cbcc.compiler import build_project
from cbcc.dependencies import CANONICAL_GATES
from cbcc.review import build_delivery_manifest
from cbcc.scope_readiness import compile_required_content_families, compile_gate_scope


def _pack(tmp_path):
    pack=tmp_path/'packs'; pack.mkdir(exist_ok=True)
    (pack/'test.yaml').write_text(
        'pack_id: test\n'
        'platform_family: test_platform\n'
        'site: "*"\n'
        'status: TEST_FIXTURE_VERIFIED\n'
        'synthetic_for_test: true\n'
        'capabilities: [LISTING, SEARCH, VISUAL, VIDEO, COMPLIANCE]\n'
        'surfaces: [PDP, SEARCH_RESULTS, GALLERY, PDP_VIDEO]\n'
        'rule_atoms: []\n'
        'research_required_for: []\n',encoding='utf-8')
    return pack


def _request(**extra):
    req={
        'project_id':'V0626','planning_only':True,
        'product':{'name':'Scope Product','category':'general','primary_conversion_proposition':'Clear value'},
        'sources':[{'source_id':'SRC-PROD','kind':'PRODUCT_TRUTH'}],
        'target':{'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY'],'surfaces':['PDP']},
    }
    req.update(extra); return req


def test_content_existence_is_separate_from_current_deliverable_requiredness():
    req=_request(
        compile_assets=True,
        shopper_questions=['What product proof should the shopper see?'],
        listing_input={'fields':{'title':'Scope Product'}},
    )
    active=['LISTING','VISUAL','COMPLIANCE']
    out=compile_required_content_families(req,{},active,{'shopper_questions':req['shopper_questions']})
    assert 'VISUAL' in out['required_families']
    assert 'LISTING' in out['supporting_families']
    assert 'COMPLIANCE' in out['supporting_families']
    assert out['fixed_requiredness'] is False


def test_explicit_content_scope_can_make_listing_a_required_deliverable():
    req=_request(content_families=['LISTING'])
    out=compile_required_content_families(req,{},['LISTING'],{'shopper_questions':[]})
    assert out['required_families']==['LISTING']


def test_gate_scope_preserves_all_canonical_gates_without_making_them_all_blocking():
    req=_request()
    requiredness=compile_required_content_families(req,{},[],{'shopper_questions':[]})
    out=compile_gate_scope(req,[],requiredness,{'shopper_questions':[],'decision_gaps':[]})
    assert set(out['canonical_gates_preserved'])==set(CANONICAL_GATES)
    assert out['gates']['PRODUCT_TRUTH']['required_for_current_scope'] is True
    assert out['gates']['CONTENT_GRAPH']['required_for_current_scope'] is False
    assert out['gates']['ASSET_COMPILE']['required_for_current_scope'] is False
    assert out['gates']['PRODUCTION']['required_for_current_scope'] is False
    assert out['gates']['MEASUREMENT']['required_for_current_scope'] is False
    assert out['gates']['PLATFORM_COMPILE']['required_for_current_scope'] is True
    assert out['gates']['PLATFORM_COMPILE']['blocking_for_current_scope'] is False


def test_review_manifest_ignores_hold_on_gate_outside_current_scope(tmp_path):
    state={
        'project_id':'P','revision':0,'final_ready':False,'item_reviews':{},
        'gates':{
            'PRODUCT_TRUTH':{'status':'READY_REVIEW','artifact_paths':[],'required_for_current_scope':True,'blocking_for_current_scope':True,'scope_status':'REQUIRED'},
            'OFFER_ECONOMICS':{'status':'HOLD','artifact_paths':['x'],'required_for_current_scope':False,'blocking_for_current_scope':False,'scope_status':'NOT_IN_CURRENT_SCOPE'},
        }
    }
    out=build_delivery_manifest(tmp_path,state)
    assert 'GATE-OFFER_ECONOMICS' not in out['required_missing']
    gate=next(x for x in out['items'] if x['item_id']=='GATE-OFFER_ECONOMICS')
    assert gate['required'] is False and gate['blocking_for_current_scope'] is False


def test_build_project_marks_supporting_listing_object_non_required_during_visual_asset_delivery(tmp_path):
    req=_request(
        compile_assets=True,
        shopper_questions=['What product proof should be visible?'],
        target={'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY'],'surfaces':['PDP','GALLERY']},
        listing_input={'fields':{'title':'Scope Product','attributes':{'size':'30ml'}}},
    )
    build_project(tmp_path/'proj',req,_pack(tmp_path))
    root=tmp_path/'proj'
    graph=json.loads((root/'artifacts/content_graph.json').read_text())
    by_family={x['family']:x for x in graph['objects']}
    assert by_family['VISUAL']['required'] is True
    assert by_family['LISTING']['required'] is False
    assert graph['required_object_count']==1
    scope=json.loads((root/'artifacts/gate_scope.json').read_text())
    assert scope['gates']['ASSET_COMPILE']['required_for_current_scope'] is True
    assert scope['gates']['PRODUCTION']['required_for_current_scope'] is False
    assert scope['gates']['OFFER_ECONOMICS']['required_for_current_scope'] is False
    state=json.loads((root/'.cbcc/project_state.json').read_text())
    assert state['gates']['PRODUCTION']['scope_status']=='NOT_IN_CURRENT_SCOPE'
    manifest=json.loads((root/'.cbcc/review/delivery_manifest.json').read_text())
    listing_item=next(x for x in manifest['items'] if x.get('kind')=='CONTENT_OBJECT' and x.get('family')=='LISTING')
    visual_item=next(x for x in manifest['items'] if x.get('kind')=='CONTENT_OBJECT' and x.get('family')=='VISUAL')
    assert listing_item['required'] is False
    assert visual_item['required'] is True
    assert listing_item['item_id'] not in manifest['review_pending']
    assert visual_item['item_id'] in manifest['review_pending']


def test_target_only_project_keeps_canonical_machine_gates_without_creating_scope_debt(tmp_path):
    build_project(tmp_path/'proj',_request(),_pack(tmp_path))
    root=tmp_path/'proj'
    scope=json.loads((root/'artifacts/gate_scope.json').read_text())
    state=json.loads((root/'.cbcc/project_state.json').read_text())
    assert scope['gates']['CONTENT_GRAPH']['scope_status']=='NOT_IN_CURRENT_SCOPE'
    assert scope['gates']['ASSET_ARCHITECTURE']['scope_status']=='NOT_IN_CURRENT_SCOPE'
    assert scope['gates']['CREATIVE']['scope_status']=='NOT_IN_CURRENT_SCOPE'
    assert scope['gates']['ASSET_COMPILE']['scope_status']=='NOT_IN_CURRENT_SCOPE'
    assert scope['gates']['PRODUCTION']['scope_status']=='NOT_IN_CURRENT_SCOPE'
    assert set(state['gates'])==set(CANONICAL_GATES)
