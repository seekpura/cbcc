import json

from runtime.cbcc.agent_autonomy import (
    agent_creative_directions,
    agent_creative_opportunities,
    compile_agent_autonomy_plan,
    compile_agent_next_action,
    research_requirements_from_plan,
)
from runtime.cbcc.asset_architecture import build_asset_architecture
from runtime.cbcc.campaign_architecture import compile_paid_campaign_architecture
from runtime.cbcc.compiler import build_project
from runtime.cbcc.creative import compile_creative_council
from runtime.cbcc.creative_opportunity import compile_creative_opportunity_universe
from runtime.cbcc.decision_authority import derive_task_content_families
from runtime.cbcc.research import compile_research_gate
from runtime.cbcc.video_creator import build_video_creator_plan


def _request(agent_plan):
    return {
        'project_id': 'r0604-autonomy',
        'target': {
            'market': 'Malaysia',
            'jurisdiction': 'Malaysia',
            'platform_family': 'TIKTOK_SHOP',
            'site': 'MY',
            'surfaces': ['GALLERY'],
        },
        'agent_plan': agent_plan,
    }


def test_explicit_empty_agent_research_scope_is_not_repopulated_by_runtime():
    request = _request({'research_requirements': []})
    plan = compile_agent_autonomy_plan(request)

    assert plan['status'] == 'AGENT_AUTHORED'
    assert plan['research']['authority'] == 'HOST_AGENT_AUTHORED'
    assert plan['research']['requirements'] == []
    assert research_requirements_from_plan(request, plan) == []

    research_gate = compile_research_gate(research_requirements_from_plan(request, plan), [], None)
    assert research_gate['status'] == 'READY'
    assert research_gate['actions'] == []


def test_explicit_empty_caller_research_scope_is_not_repopulated_by_runtime():
    request = _request({})
    request['research_requirements'] = []
    plan = compile_agent_autonomy_plan(request)

    assert plan['research']['authority'] == 'USER_OR_CALLER_SUPPLIED'
    assert plan['research']['requirements'] == []
    assert research_requirements_from_plan(request, plan) == []


def test_missing_agent_research_scope_still_allows_decision_gap_fallback():
    request = _request({})
    plan = compile_agent_autonomy_plan(request)

    assert plan['research']['authority'] == 'DECISION_GAP_FALLBACK'
    assert plan['research']['requirements'], 'missing research scope may still use compatibility fallback'


def test_explicit_empty_research_stop_conditions_are_not_replaced_by_runtime_defaults():
    explicit = compile_agent_autonomy_plan(_request({'research_stop_conditions': []}))
    missing = compile_agent_autonomy_plan(_request({}))

    assert explicit['research']['stop_conditions'] == []
    assert missing['research']['stop_conditions'], 'missing stop conditions may use compatibility defaults'


def test_explicit_empty_agent_content_family_scope_remains_empty():
    request = _request({'content_scope': {'families': []}})
    plan = compile_agent_autonomy_plan(request)

    families = derive_task_content_families(
        request,
        plan,
        available_families=['LISTING', 'SEARCH', 'VISUAL', 'VIDEO'],
    )
    assert families == []


def test_explicit_empty_agent_opportunity_universe_is_not_autopopulated():
    plan = compile_agent_autonomy_plan(_request({'creative_exploration': {'opportunities': []}}))
    authored = agent_creative_opportunities(plan)
    assert authored == []

    universe = compile_creative_opportunity_universe(
        {'product': {'name': 'Demo'}}, {}, 'GENERAL_COMMERCE', [], {}, {},
        {'market': 'Malaysia', 'platform_family': 'TIKTOK_SHOP', 'site': 'MY'},
        agent_opportunities=authored,
    )
    assert universe['status'] == 'AGENT_AUTHORED_CREATIVE_OPPORTUNITY_UNIVERSE'
    assert universe['opportunity_count'] == 0
    assert universe['opportunities'] == []


def test_explicit_empty_agent_direction_set_is_not_autosynthesized_or_selected():
    plan = compile_agent_autonomy_plan(_request({'creative_exploration': {'directions': []}}))
    authored = agent_creative_directions(plan)
    assert authored == []

    council = compile_creative_council(
        authored, {}, {'product': {'name': 'Demo'}}, {}, {}, 'GENERAL_COMMERCE', [],
        {'status': 'AGENT_AUTHORED_CREATIVE_OPPORTUNITY_UNIVERSE', 'opportunity_count': 0, 'opportunities': []},
    )
    assert council['status'] == 'NO_DIRECTION_AVAILABLE'
    assert council['direction_source'] == 'USER_SUPPLIED'
    assert council['directions'] == []
    assert council['selected_direction'] is None

    next_action = compile_agent_next_action(
        plan,
        request=_request({'creative_exploration': {'directions': []}}),
        asset_architecture={'assets': [{'asset_id': 'AST-1'}]},
        creative_council=council,
    )
    assert any(row['action'] == 'AUTHOR_OR_SELECT_CREATIVE_DIRECTION' for row in next_action['frontier'])


def test_missing_agent_direction_set_still_allows_compatibility_synthesis():
    council = compile_creative_council(
        None, {}, {'product': {'name': 'Demo'}}, {}, {}, 'GENERAL_COMMERCE', [], None,
    )
    assert council['status'] == 'SELECTED'
    assert council['directions']


def test_explicit_empty_asset_jobs_do_not_generate_assets_but_missing_jobs_may_autocurate():
    target = {'target_id': 'T', 'surfaces': ['GALLERY']}
    content = [{'object_id': 'O1', 'family': 'VISUAL', 'surface': 'GALLERY', 'required': True}]

    explicit = build_asset_architecture('P', target, ['What is it?'], content, [], {}, 'GENERAL_COMMERCE')
    missing = build_asset_architecture('P2', target, ['What is it?'], content, None, {}, 'GENERAL_COMMERCE')

    assert explicit['asset_count'] == 0
    assert explicit['asset_scope_active'] is False
    assert missing['asset_count'] > 0
    assert missing['asset_scope_active'] is True


def test_explicit_empty_video_jobs_do_not_generate_video_but_missing_jobs_may_derive():
    content = [{'object_id': 'O1', 'family': 'VIDEO', 'surface': 'PDP_VIDEO', 'curation_job': 'Explain the decision'}]
    language = {'primary_locale': 'en-MY'}

    explicit = build_video_creator_plan('P', content, ['Why?'], language, [], assets=[])
    missing = build_video_creator_plan('P2', content, ['Why?'], language, None, assets=[])

    assert explicit['dynamic_count'] == 0
    assert explicit['status'] == 'NOT_REQUIRED'
    assert missing['dynamic_count'] > 0
    assert missing['status'] == 'COMPILED'


def test_explicit_empty_paid_campaigns_do_not_generate_campaigns_but_missing_may_derive():
    assets = [{'asset_id': 'A1', 'family': 'PAID', 'surface': 'PAID_AD', 'consumer_question': 'Why now?', 'decision_intent': 'RELEVANCE'}]

    explicit = compile_paid_campaign_architecture('P', {'target_id': 'T'}, assets, {}, explicit=[])
    missing = compile_paid_campaign_architecture('P2', {'target_id': 'T'}, assets, {}, explicit=None)

    assert explicit['dynamic_count'] == 0
    assert explicit['status'] == 'NOT_REQUIRED'
    assert missing['dynamic_count'] > 0
    assert missing['status'] == 'COMPILED'


def test_compiler_preserves_per_asset_art_direction_without_direction_list(tmp_path):
    question = 'What proof should the shopper understand?'
    request = {
        'project_id': 'r0604-art-only',
        'sku': 'SKU-1',
        'product': {'name': 'Demo Serum', 'category': 'Beauty'},
        'target': {
            'target_id': 'T1',
            'market': 'Malaysia',
            'jurisdiction': 'Malaysia',
            'platform_family': 'TIKTOK_SHOP',
            'site': 'MY',
            'category': 'Beauty',
            'surfaces': ['GALLERY'],
            'primary_locale': 'en-MY',
            'support_locales': ['ms-MY'],
            'visible_copy_locales': ['en-MY', 'ms-MY'],
            'delivery_locale': 'zh-CN',
        },
        'agent_plan': {
            'research_requirements': [],
            'content_scope': {'families': ['VISUAL']},
            'creative_exploration': {
                'asset_art_directions': [{
                    'consumer_question': question,
                    'visual_carrier': 'EDITORIAL_EVIDENCE_FIELD',
                    'subject': 'verified evidence field',
                    'composition_grammar': 'asymmetric evidence field with open negative space',
                    'product_presence': {
                        'planning_state': 'FORBIDDEN',
                        'source_reference_role': 'TRUTH_REFERENCE_ONLY',
                    },
                }],
            },
        },
        'asset_jobs': [{
            'consumer_question': question,
            'surface': 'GALLERY',
            'family': 'VISUAL',
            'strategic_job': 'Resolve proof question',
        }],
        'compile_assets': False,
        'planning_only': True,
    }
    packs = tmp_path / 'packs'
    packs.mkdir()
    project = tmp_path / 'project'

    build_project(project, request, packs)

    council = json.loads((project / 'artifacts' / 'creative_council.json').read_text(encoding='utf-8'))
    architecture = json.loads((project / 'artifacts' / 'asset_architecture.json').read_text(encoding='utf-8'))
    asset = architecture['assets'][0]

    assert council['selected_direction']['direction_id'] == 'DIR-AGENT-ASSET-AUTHORITY'
    assert council['selected_direction']['source'] == 'HOST_AGENT_AUTHORED'
    assert asset['art_direction_status'] == 'AUTHORED'
    assert asset['asset_art_direction']['composition_grammar'] == 'asymmetric evidence field with open negative space'
    assert asset['product_presence']['planning_state'] == 'FORBIDDEN'
