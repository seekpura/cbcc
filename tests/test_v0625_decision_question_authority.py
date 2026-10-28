from pathlib import Path
import json

from cbcc.compiler import build_project
from cbcc.decision_authority import (
    derive_task_content_families,
    selected_decision_frameworks,
    compile_decision_question_authority,
    compile_decision_trace_rows,
)


AVAILABLE=['LISTING','SEARCH','OFFER_PROMOTION','VISUAL','RICH_CONTENT','VIDEO','CREATOR_AFFILIATE','LIVE','PAID','SOCIAL','STORE','CX','LIFECYCLE','MEASUREMENT','COMPLIANCE']


def _pack(tmp_path):
    pack=tmp_path/'packs'; pack.mkdir(exist_ok=True)
    (pack/'test.yaml').write_text(
        'pack_id: test\n'
        'platform_family: test_platform\n'
        'site: "*"\n'
        'status: TEST_FIXTURE_VERIFIED\n'
        'synthetic_for_test: true\n'
        'capabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, PAID, MEASUREMENT, COMPLIANCE]\n'
        'surfaces: [PDP, SEARCH_RESULTS, GALLERY, PDP_VIDEO, PAID_AD]\n'
        'rule_atoms: []\n'
        'research_required_for: []\n',
        encoding='utf-8',
    )
    return pack


def _request(**extra):
    req={
        'project_id':'V0625',
        'planning_only':True,
        'product':{'name':'Decision Product','category':'general','primary_conversion_proposition':'Clear value'},
        'sources':[{'source_id':'SRC-PROD','kind':'PRODUCT_TRUTH'}],
        'target':{
            'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST',
            'primary_locale':'en-MY','visible_copy_locales':['en-MY'],'surfaces':['PDP']
        },
    }
    req.update(extra)
    return req


def test_target_surface_is_constraint_not_content_family_quota():
    req=_request()
    assert derive_task_content_families(req,{},available_families=AVAILABLE)==[]
    req2=_request(listing_input={'fields':{'title':'Decision Product'}})
    assert derive_task_content_families(req2,{},available_families=AVAILABLE)==['LISTING']
    req3=_request(content_families=[])
    assert derive_task_content_families(req3,{},available_families=AVAILABLE)==[]


def test_no_generic_questions_or_frameworks_are_invented():
    req=_request(compile_assets=True)
    q=compile_decision_question_authority(req,{},listing={},active_families=[])
    assert q['shopper_questions']==[]
    assert q['synthetic_default_questions'] is False
    assert q['decision_gaps'][0]['code']=='ASSET_DECISION_SCOPE_NOT_AUTHORED'
    assert selected_decision_frameworks(req,{})==[]
    assert compile_decision_trace_rows(q,[])==[]


def test_agent_question_and_explicit_frameworks_are_preserved_without_index_stage_mapping():
    req=_request(decision_frameworks=['RACE','AIDA'])
    plan={
        'content_scope':{'decision_questions':[{'question':'Which verified size prevents a wrong purchase?','decision_job':'VERIFY_SIZE','race_stage':'ACTION'}]},
        'strategy_frameworks':['Fogg'],
    }
    frameworks=selected_decision_frameworks(req,plan)
    assert frameworks==['RACE','AIDA']
    q=compile_decision_question_authority(req,plan,listing={},active_families=['LISTING'])
    assert q['shopper_questions']==['Which verified size prevents a wrong purchase?']
    traces=compile_decision_trace_rows(q,frameworks)
    assert traces[0]['race_stage']=='ACTION'
    assert traces[0]['decision_job']=='VERIFY_SIZE'
    assert traces[0]['origin']=='HOST_AGENT_AUTHORED'


def test_build_project_target_only_does_not_create_listing_questions_or_assets(tmp_path):
    req=_request()
    build_project(tmp_path/'proj',req,_pack(tmp_path))
    root=tmp_path/'proj/artifacts'
    q=json.loads((root/'decision_question_authority.json').read_text())
    trace=json.loads((root/'decision_trace.json').read_text())
    graph=json.loads((root/'content_graph.json').read_text())
    arch=json.loads((root/'asset_architecture.json').read_text())
    plan=json.loads((root/'agent_autonomy_plan.json').read_text())
    assert q['question_count']==0 and q['synthetic_default_questions'] is False
    assert trace['traces']==[] and trace['frameworks']==[] and trace['fixed_framework_quota'] is False
    assert graph['dynamic_count']==0
    assert arch['asset_count']==0
    assert plan['target_surfaces_are_constraints_not_content_quotas'] is True


def test_compile_assets_without_decision_scope_opens_agent_frontier_instead_of_inventing_assets(tmp_path):
    req=_request(compile_assets=True)
    build_project(tmp_path/'proj',req,_pack(tmp_path))
    root=tmp_path/'proj/artifacts'
    q=json.loads((root/'decision_question_authority.json').read_text())
    arch=json.loads((root/'asset_architecture.json').read_text())
    nxt=json.loads((root/'agent_next_action.json').read_text())
    assert q['question_count']==0
    assert q['decision_gaps'][0]['code']=='ASSET_DECISION_SCOPE_NOT_AUTHORED'
    assert arch['asset_count']==0
    assert any(x.get('action')=='AUTHOR_DECISION_OR_ASSET_SCOPE' for x in nxt['frontier'])
    assert nxt['decision_question_authority']['synthetic_default_questions'] is False


def test_explicit_asset_job_is_a_real_question_source_and_builds_only_that_asset(tmp_path):
    req=_request(
        target={
            'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST',
            'primary_locale':'en-MY','visible_copy_locales':['en-MY'],'surfaces':['GALLERY']
        },
        asset_jobs=[{
            'family':'VISUAL','surface':'GALLERY','consumer_question':'What exact product identity must the shopper recognize?',
            'strategic_job':'Make product identity legible','production_mode':'GRAPHIC_DESIGN'
        }],
    )
    build_project(tmp_path/'proj',req,_pack(tmp_path))
    root=tmp_path/'proj/artifacts'
    q=json.loads((root/'decision_question_authority.json').read_text())
    arch=json.loads((root/'asset_architecture.json').read_text())
    trace=json.loads((root/'decision_trace.json').read_text())
    assert q['shopper_questions']==['What exact product identity must the shopper recognize?']
    assert q['rows'][0]['origin']=='EXPLICIT_ASSET_JOB'
    assert arch['asset_count']==1
    assert arch['assets'][0]['consumer_question']==q['shopper_questions'][0]
    assert trace['frameworks']==[]
    assert trace['traces'][0]['race_stage'] is None
