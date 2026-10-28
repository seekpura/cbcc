from pathlib import Path
import json

from cbcc.compiler import build_project
from cbcc.completion import evaluate_scope_completion
from cbcc.review import build_delivery_manifest, refresh_review_workspace
from cbcc.state import ProjectState
from cbcc.cli import main as cli_main


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
        'project_id':'V0627','planning_only':True,
        'product':{'name':'Completion Product','category':'general','primary_conversion_proposition':'Clear value'},
        'sources':[{'source_id':'SRC-PROD','kind':'PRODUCT_TRUTH'}],
        'target':{'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY'],'surfaces':['PDP']},
    }
    req.update(extra); return req


def test_completion_ignores_nonblocking_support_gate_and_advisory_action():
    state={
        'gates':{
            'PRODUCT_TRUTH':{'status':'READY_REVIEW','required_for_current_scope':True,'blocking_for_current_scope':True},
            'OFFER_ECONOMICS':{'status':'HOLD','required_for_current_scope':False,'blocking_for_current_scope':False},
            'PLATFORM_COMPILE':{'status':'HOLD','required_for_current_scope':True,'blocking_for_current_scope':False},
        },
        'pending_actions':[{'action_id':'A1','status':'PENDING','blocking':False,'required_for':['PLATFORM_COMPILE']}],
        'local_revision_requests':[],
    }
    out=evaluate_scope_completion(state,[],agent_next_action={'frontier':[{'action':'RESEARCH_OR_EVIDENCE_RESOLUTION'}],'recommended_next_action':'RESEARCH_OR_EVIDENCE_RESOLUTION'})
    assert out['final_ready'] is True
    assert out['gate_blockers']==[]
    assert not out['blocking_actions']
    assert out['advisory_actions'][0]['action_id']=='A1'
    assert out['agent_alignment']=='READY_WITH_NONBLOCKING_AGENT_FRONTIER'


def test_completion_blocks_current_scope_gate_required_review_and_open_revision():
    state={
        'gates':{'CONTENT_GRAPH':{'status':'INVALIDATED','required_for_current_scope':True,'blocking_for_current_scope':True}},
        'pending_actions':[],
        'local_revision_requests':[{'revision_request_id':'R1','status':'OPEN'}],
    }
    items=[{'item_id':'OBJ-1','kind':'CONTENT_OBJECT','required':True,'status':'PLANNED','review_status':'PENDING_REVIEW'}]
    out=evaluate_scope_completion(state,items,agent_next_action={})
    assert out['final_ready'] is False
    assert out['gate_blockers'][0]['gate']=='CONTENT_GRAPH'
    assert out['review_pending'][0]['item_id']=='OBJ-1'
    assert out['open_revision_requests'][0]['revision_request_id']=='R1'


def test_target_only_build_can_finish_current_scope_despite_advisory_research(tmp_path):
    project=tmp_path/'proj'
    out=build_project(project,_request(),_pack(tmp_path))
    assert out['final_ready'] is True
    assert out['completion']['status']=='READY_CURRENT_SCOPE'
    assert not out['completion']['blocking_actions']
    state=json.loads((project/'.cbcc/project_state.json').read_text())
    assert state['final_ready'] is True
    delivery=json.loads((project/'.cbcc/review/delivery_manifest.json').read_text())
    assert delivery['final_ready'] is True
    assert delivery['completion']['agent_alignment'] in {'READY_WITH_NONBLOCKING_AGENT_FRONTIER','ALIGNED_WITH_AGENT_STOP','READY_NO_AGENT_BLOCKER'}


def test_required_asset_delivery_becomes_ready_only_after_required_item_review(tmp_path):
    project=tmp_path/'proj'
    req=_request(
        compile_assets=True,
        shopper_questions=['What exact product proof should the shopper see?'],
        target={'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY'],'surfaces':['GALLERY']},
    )
    out=build_project(project,req,_pack(tmp_path))
    assert out['final_ready'] is False
    manifest=json.loads((project/'.cbcc/review/delivery_manifest.json').read_text())
    required_items=[x['item_id'] for x in manifest['items'] if x.get('required') and x.get('kind')!='AUTHORITY_GATE']
    assert required_items
    assert set(manifest['review_pending'])==set(required_items)

    st=ProjectState.load(project)
    st.apply_review_decision({'project_id':'V0627','revision':st.data['revision'],'accept_items':required_items})
    refresh_review_workspace(project,st)
    assert st.data['final_ready'] is True
    assert st.data['completion']['status']=='READY_CURRENT_SCOPE'
    manifest2=build_delivery_manifest(project,st.data)
    assert manifest2['review_pending']==[]
    assert manifest2['final_ready'] is True


def test_revision_of_current_scope_reopens_completion(tmp_path):
    project=tmp_path/'proj'
    req=_request(content_families=['LISTING'],listing_input={'fields':{'title':'Completion Product'}})
    build_project(project,req,_pack(tmp_path))
    st=ProjectState.load(project)
    manifest=build_delivery_manifest(project,st.data)
    required_items=[x['item_id'] for x in manifest['items'] if x.get('required') and x.get('kind')!='AUTHORITY_GATE']
    st.apply_review_decision({'project_id':'V0627','revision':st.data['revision'],'accept_items':required_items})
    refresh_review_workspace(project,st)
    assert st.data['final_ready'] is True

    st.revise(['CONTENT_GRAPH'])
    refresh_review_workspace(project,st)
    assert st.data['final_ready'] is False
    assert any(x['gate']=='CONTENT_GRAPH' for x in st.data['completion']['gate_blockers'])


def test_export_uses_same_scope_completion_authority_instead_of_static_gate_list(tmp_path):
    project=tmp_path/'proj'; export_path=tmp_path/'export.json'
    build_project(project,_request(),_pack(tmp_path))
    rc=cli_main(['export','--project-dir',str(project),'--output',str(export_path)])
    assert rc==0
    exported=json.loads(export_path.read_text())
    state=json.loads((project/'.cbcc/project_state.json').read_text())
    assert exported['final_ready'] is True
    assert exported['final_ready']==state['final_ready']
    assert exported['completion']['status']=='READY_CURRENT_SCOPE'
    assert 'required_missing' in exported and 'review_pending' in exported
