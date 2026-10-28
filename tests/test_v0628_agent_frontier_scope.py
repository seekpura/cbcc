from pathlib import Path
import json

from cbcc.agent_autonomy import compile_agent_next_action
from cbcc.compiler import build_project
from cbcc.decision_authority import augment_agent_next_action
from cbcc.human_delivery import build_project_hub_md


def _gate_scope(*blocking):
    names=['EVIDENCE','PRODUCT_TRUTH','TARGET_CONTEXT','PLATFORM_COMPILE','ASSET_ARCHITECTURE','CREATIVE','ASSET_COMPILE','EXECUTION','PRODUCTION']
    return {'gates':{name:{'blocking_for_current_scope':name in set(blocking),'required_for_current_scope':name in set(blocking)} for name in names}}


def test_advisory_research_does_not_force_another_agent_loop():
    research={'actions':[{'action_id':'A1','status':'PENDING','blocking':False,'required_for':['PLATFORM_COMPILE']}]}
    out=compile_agent_next_action({},research_gate=research,gate_scope=_gate_scope(),content_requiredness={})
    assert out['status']=='CURRENT_SCOPE_SATISFIED'
    assert out['recommended_next_action']=='STOP_CURRENT_SCOPE_SATISFIED'
    assert out['blocking_frontier']==[]
    assert out['advisory_frontier'][0]['action']=='RESEARCH_OR_EVIDENCE_RESOLUTION'
    assert out['advisory_frontier'][0]['blocking'] is False


def test_research_blocks_only_when_routed_to_current_blocking_gate():
    research={'actions':[{'action_id':'A1','status':'PENDING','blocking':True,'required_for':['PRODUCTION']}]}
    out=compile_agent_next_action({},research_gate=research,gate_scope=_gate_scope('PRODUCTION'),content_requiredness={})
    assert out['status']=='ACTION_FRONTIER_OPEN'
    assert out['recommended_next_action']=='RESEARCH_OR_EVIDENCE_RESOLUTION'
    assert out['blocking_frontier'][0]['blocking'] is True


def test_compliance_hold_is_advisory_outside_current_compliance_or_execution_scope():
    out=compile_agent_next_action({},compliance={'status':'HOLD'},gate_scope=_gate_scope(),content_requiredness={'required_families':['LISTING']})
    assert out['status']=='CURRENT_SCOPE_SATISFIED'
    assert out['blocking_frontier']==[]
    assert out['advisory_frontier'][0]['action']=='RESOLVE_COMPLIANCE_BOUNDARY'


def test_compliance_hold_blocks_required_asset_execution_scope():
    out=compile_agent_next_action({},compliance={'status':'HOLD'},gate_scope=_gate_scope('ASSET_COMPILE','EXECUTION'),content_requiredness={'required_families':['VISUAL']})
    assert out['status']=='ACTION_FRONTIER_OPEN'
    assert out['blocking_frontier'][0]['action']=='RESOLVE_COMPLIANCE_BOUNDARY'


def test_agent_stop_cannot_override_hard_production_blocker():
    plan={'iteration_policy':{'stop':True}}
    out=compile_agent_next_action(plan,request={'production_run':{}},production_run={'status':'PENDING'},gate_scope=_gate_scope('PRODUCTION'),content_requiredness={})
    assert out['status']=='ACTION_FRONTIER_OPEN'
    assert out['agent_stop_requested'] is True
    assert out['agent_stop_overridden_by_hard_blocker'] is True
    assert out['recommended_next_action']=='PRODUCE_RESUME_OR_REPAIR'


def test_decision_scope_gap_is_blocking_and_survives_advisory_frontier():
    base={'status':'CURRENT_SCOPE_SATISFIED','recommended_next_action':'STOP_CURRENT_SCOPE_SATISFIED','blocking_frontier':[],'advisory_frontier':[{'action':'RESEARCH_OR_EVIDENCE_RESOLUTION','blocking':False}],'frontier':[]}
    q={'decision_gaps':[{'code':'ASSET_DECISION_SCOPE_NOT_AUTHORED','reason':'Need a real decision job','required_action':'Author scope','blocking_scope':['ASSET_ARCHITECTURE']}], 'status':'NO_SHOPPER_QUESTION_AUTHORED','question_count':0}
    out=augment_agent_next_action(base,q)
    assert out['status']=='ACTION_FRONTIER_OPEN'
    assert out['recommended_next_action']=='AUTHOR_DECISION_OR_ASSET_SCOPE'
    assert out['blocking_frontier'][0]['action']=='AUTHOR_DECISION_OR_ASSET_SCOPE'
    assert out['advisory_frontier'][0]['blocking'] is False


def _pack(tmp_path):
    pack=tmp_path/'packs'; pack.mkdir(exist_ok=True)
    (pack/'test.yaml').write_text(
        'pack_id: test\nplatform_family: test_platform\nsite: "*"\nstatus: TEST_FIXTURE_VERIFIED\nsynthetic_for_test: true\n'
        'capabilities: [LISTING, SEARCH, VISUAL, VIDEO, COMPLIANCE]\nsurfaces: [PDP, SEARCH_RESULTS, GALLERY, PDP_VIDEO]\nrule_atoms: []\nresearch_required_for: []\n',encoding='utf-8')
    return pack


def _request(**extra):
    req={'project_id':'V0628','planning_only':True,'product':{'name':'Frontier Product','category':'general','primary_conversion_proposition':'Clear value'},'sources':[{'source_id':'SRC-PROD','kind':'PRODUCT_TRUTH'}],'target':{'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST','primary_locale':'en-MY','visible_copy_locales':['en-MY'],'surfaces':['PDP']}}
    req.update(extra); return req


def test_target_only_build_stops_current_scope_with_research_kept_advisory(tmp_path):
    project=tmp_path/'proj'
    out=build_project(project,_request(),_pack(tmp_path))
    nxt=json.loads((project/'artifacts/agent_next_action.json').read_text())
    assert nxt['status']=='CURRENT_SCOPE_SATISFIED'
    assert nxt['recommended_next_action']=='STOP_CURRENT_SCOPE_SATISFIED'
    assert nxt['blocking_frontier']==[]
    assert nxt['advisory_frontier']
    assert out['completion']['final_ready'] is True
    assert out['completion']['agent_alignment']=='ALIGNED_WITH_AGENT_STOP'


def test_human_project_hub_separates_blocking_and_advisory_next_actions():
    center={
        'product':{'product_name':'X'},'target':{'market':'MY','platform':'Test','locale':'en-MY','delivery_locale':'zh-CN'},
        'readiness':{'status':'READY_FOR_CURRENT_SCOPE','pending_count':0,'optional_gap_count':0},
        'task_scope':{
            'families':['VISUAL'],'recommended_next_action':'AUTHOR_DECISION_OR_ASSET_SCOPE',
            'blocking_frontier':[{'action':'AUTHOR_DECISION_OR_ASSET_SCOPE','reason':'缺少真实资产决策任务'}],
            'advisory_frontier':[{'action':'RESEARCH_OR_EVIDENCE_RESOLUTION','reason':'可选补充研究','blocking':False}],
            'listing_active':False,
        },
        'media_slots':[],'risks_and_holds':[],
    }
    md=build_project_hub_md(center)
    assert '当前范围必须先解决' in md
    assert '可选后续优化 / 研究（不阻断当前完成）' in md
    assert '缺少真实资产决策任务' in md and '可选补充研究' in md


def test_empty_production_config_still_counts_as_explicit_production_intent():
    out=compile_agent_next_action({},request={'production_run':{}},production_run={'status':'PENDING'},gate_scope=_gate_scope('PRODUCTION'),content_requiredness={})
    assert out['status']=='ACTION_FRONTIER_OPEN'
    assert out['blocking_frontier'][0]['action']=='PRODUCE_RESUME_OR_REPAIR'
