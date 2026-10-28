from __future__ import annotations

from pathlib import Path
import ast

from cbcc.agent_autonomy import (
    compile_agent_autonomy_plan,
    derive_content_families,
    research_requirements_from_plan,
)
from cbcc.creative import compile_creative_council, apply_creative_system_to_assets
from cbcc.creative_opportunity import compile_creative_opportunity_universe


FAMILY_SURFACE = {
    'LISTING':'PDP','SEARCH':'SEARCH_RESULTS','OFFER_PROMOTION':'PDP','VISUAL':'GALLERY',
    'RICH_CONTENT':'LONGFORM','VIDEO':'PDP_VIDEO','CREATOR_AFFILIATE':'CREATOR','LIVE':'LIVE',
    'PAID':'PAID_AD','SOCIAL':'SOCIAL_CONTENT','STORE':'STORE_BANNER','CX':'FAQ','LIFECYCLE':'CRM',
    'MEASUREMENT':None,'COMPLIANCE':None,
}
FAMILIES = list(FAMILY_SURFACE)


def test_agent_plan_owns_research_scope_and_has_no_fixed_research_quota():
    request = {
        'target': {'market':'Malaysia','platform_family':'TIKTOK_SHOP','site':'MY','surfaces':['GALLERY']},
        'agent_plan': {
            'research_requirements': [
                {'topic':'specific shopper objection','domain':'CUSTOMER','required_for':['STRATEGY']},
            ],
            'research_stop_conditions':['Stop when the objection no longer changes positioning.'],
        },
    }
    plan = compile_agent_autonomy_plan(request)
    assert plan['status'] == 'AGENT_AUTHORED'
    assert plan['research']['authority'] == 'HOST_AGENT_AUTHORED'
    assert research_requirements_from_plan(request, plan)[0]['topic'] == 'specific shopper objection'
    assert plan['research']['fixed_source_count'] is None
    assert plan['research']['fixed_query_count'] is None
    assert plan['research']['fixed_competitor_count'] is None


def test_fallback_research_discovers_material_gaps_instead_of_requiring_user_checklist():
    request = {
        'unknowns':['net weight'],
        'target': {'market':'Malaysia','platform_family':'TIKTOK_SHOP','site':'MY'},
    }
    plan = compile_agent_autonomy_plan(request)
    domains = {row['domain'] for row in plan['research']['requirements']}
    assert 'PRODUCT_TRUTH' in domains
    assert 'MARKET' in domains
    assert 'PLATFORM_RULE' in domains
    assert plan['research']['authority'] == 'DECISION_GAP_FALLBACK'


def test_content_scope_is_task_derived_not_default_all_families():
    request = {
        'target': {'platform_family':'TIKTOK_SHOP','surfaces':['GALLERY']},
        'compile_assets': True,
    }
    plan = compile_agent_autonomy_plan(request)
    families = derive_content_families(request, plan, family_surface=FAMILY_SURFACE, available_families=FAMILIES)
    assert 'VISUAL' in families
    assert len(families) < len(FAMILIES)
    assert 'LIVE' not in families
    assert 'CRM' not in families


def test_agent_authored_content_scope_is_not_expanded_by_runtime():
    request = {
        'target': {'platform_family':'TIKTOK_SHOP','surfaces':['GALLERY','PDP_VIDEO']},
        'agent_plan': {'content_scope': {'families':['VIDEO']}},
    }
    plan = compile_agent_autonomy_plan(request)
    assert derive_content_families(request, plan, family_surface=FAMILY_SURFACE, available_families=FAMILIES) == ['VIDEO']


def test_agent_authored_creative_opportunity_universe_preserves_arbitrary_count_and_mechanisms():
    opportunities = [
        {'mechanism_id':'AGENT-A','mechanism_name':'A','domain':'CUSTOM-A','score':0.91},
        {'mechanism_id':'AGENT-B','mechanism_name':'B','domain':'CUSTOM-B','score':0.83},
    ]
    out = compile_creative_opportunity_universe(
        {'product':{'name':'Demo'}}, {}, 'BEAUTY_PERSONAL_CARE', [], {}, {}, {},
        agent_opportunities=opportunities,
    )
    assert out['status'] == 'AGENT_AUTHORED_CREATIVE_OPPORTUNITY_UNIVERSE'
    assert out['opportunity_count'] == 2
    assert [x['mechanism_id'] for x in out['opportunities']] == ['AGENT-A','AGENT-B']
    assert out['search_domains'] == ['CUSTOM-A','CUSTOM-B']
    assert 'quota' in out['selection_rule'].lower()


def test_creative_council_does_not_enforce_three_to_five_directions_when_agent_supplies_two():
    directions = [
        {'direction_name':'One','creative_thesis':'x','product_fit':0.9,'audience_fit':0.9,'platform_fit':0.9,'culture_fit':0.9,'differentiation':0.9,'production_feasibility':0.9},
        {'direction_name':'Two','creative_thesis':'y','product_fit':0.88,'audience_fit':0.88,'platform_fit':0.88,'culture_fit':0.88,'differentiation':0.95,'production_feasibility':0.88},
    ]
    council = compile_creative_council(directions, {}, {'product':{'name':'Demo'}}, {}, {}, 'GENERAL_COMMERCE', [], {'status':'AGENT_AUTHORED_CREATIVE_OPPORTUNITY_UNIVERSE','opportunity_count':2})
    assert len(council['directions']) == 2
    assert council['minimum_material_difference_contract']['required_differences'] == 'TASK_DEPENDENT'
    assert 'No fixed mechanism or direction count' in council['search_before_selection_trace']['rule']


def test_asset_expression_uses_decision_signature_not_fixed_intent_layout_rotation():
    architecture = {'assets':[{
        'asset_id':'AST-1','decision_intent':'USAGE','surface':'GALLERY',
        'visual_production_signature':{
            'composition_grammar':'custom evidence diagonal built from this task',
            'camera_or_view':'macro contact point selected by current evidence',
            'context_role':'only the actual tool interaction',
        },
        'creative_brief':{},
    }]}
    council = {'selected_direction':{'direction_id':'DIR-1','route':'ANY','creative_thesis':'demo'},'alternative_directions':[],'directions':[{'direction_id':'DIR-1'}]}
    out = apply_creative_system_to_assets(architecture, council)
    expr = out['assets'][0]['visual_expression_variant']
    assert expr['composition_grammar'] == 'custom evidence diagonal built from this task'
    assert expr['preferred_view'] == 'macro contact point selected by current evidence'
    assert expr['spatial_rhythm'] == 'DECISION_DERIVED'
    assert expr['authority'] == 'AGENT_OR_ASSET_DECISION_SIGNATURE'


def test_commerce_autonomy_module_has_no_transport_or_mcp_dependency():
    source = Path('runtime/cbcc/agent_autonomy.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
    joined = ' '.join(imports).lower()
    assert 'mcp' not in joined
    assert 'plugin_http' not in joined
    assert 'action_transports' not in joined


def test_compiler_no_longer_uses_default_all_family_expansion():
    source = Path('runtime/cbcc/compiler.py').read_text(encoding='utf-8')
    assert "families=request.get('content_families') or DEFAULT_FAMILIES" not in source
    assert 'derive_content_families(' in source
    assert 'agent_autonomy_plan.json' in source
