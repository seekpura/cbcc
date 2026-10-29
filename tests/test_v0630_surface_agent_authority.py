from __future__ import annotations

from cbcc.agent_autonomy import compile_agent_autonomy_plan
from cbcc.creative import apply_creative_system_to_assets
from cbcc.surface_architecture import compile_surface_architecture


def test_surface_product_presence_is_explicitly_advisory_not_generation_authority():
    asset={
        'asset_id':'AST-1',
        'asset_type':'IMAGE',
        'surface':'GALLERY',
        'family':'VISUAL',
        'decision_intent':'IDENTIFY',
        'strategic_job':'Resolve identity.',
        'visible_copy':{},
    }
    result=compile_surface_architecture(
        {'surfaces':['GALLERY']},
        [{'surface':'GALLERY','family':'VISUAL'}],
        [asset],
        {'surfaces':['GALLERY']},
    )
    out=result['assets'][0]
    assert out['product_presence']['planning_suggestion']=='REQUIRED'
    assert out['product_presence']['authority']=='SURFACE_COMPATIBILITY_SUGGESTION_ONLY'
    assert out['product_presence']['authoritative_for_generation'] is False
    assert out['surface_native_contract']['product_presence_authority']=='AGENT_ART_DIRECTION'
    assert result['product_presence_authority']=='AGENT_ART_DIRECTION'
    assert result['surface_product_presence_role']=='PLANNING_SUGGESTION_ONLY'


def test_agent_forbidden_presence_overrides_surface_required_suggestion():
    surface_asset={
        'asset_id':'AST-1',
        'asset_type':'IMAGE',
        'surface':'GALLERY',
        'family':'VISUAL',
        'decision_intent':'IDENTIFY',
        'strategic_job':'Resolve identity through a non-product evidence carrier.',
        'visible_copy':{},
        'creative_brief':{},
    }
    surface=compile_surface_architecture(
        {'surfaces':['GALLERY']},
        [{'surface':'GALLERY','family':'VISUAL'}],
        [surface_asset],
        {'surfaces':['GALLERY']},
    )
    assert surface['assets'][0]['product_presence']['planning_suggestion']=='REQUIRED'

    direction={
        'direction_id':'DIR-A',
        'decision':'SELECT',
        'require_per_asset_art_direction':True,
        'asset_art_directions':[
            {
                'asset_id':'AST-1',
                'visual_carrier':'SOURCE_EVIDENCE',
                'subject':'source evidence and label crop without a product object',
                'composition_grammar':'source-led documentary crop with evidence occupying the full frame',
                'product_presence':{
                    'planning_state':'FORBIDDEN',
                    'product_role':'ABSENT',
                    'source_reference_role':'TRUTH_REFERENCE_ONLY',
                    'presence_why':'The source evidence itself resolves the decision; adding a packshot would duplicate information.',
                },
            }
        ],
        'product_fit':1,'audience_fit':1,'platform_fit':1,'culture_fit':1,
        'differentiation':1,'production_feasibility':1,'decision_coverage':1,'opportunity_fit':1,
    }
    final=apply_creative_system_to_assets(
        {'assets':surface['assets']},
        {'selected_direction':direction,'alternative_directions':[],'directions':[direction],'direction_source':'USER_SUPPLIED'},
        None,
        None,
    )
    asset=final['assets'][0]
    assert asset['product_presence']['planning_state']=='FORBIDDEN'
    assert asset['product_presence'].get('planning_suggestion') is None
    assert asset['visual_production_signature']['authority']=='HOST_AGENT_ART_DIRECTION'
    assert asset['surface_native_contract']['product_presence']=='FORBIDDEN'


def test_top_level_agent_art_direction_input_is_not_lost():
    request={
        'target':{'platform_family':'TikTok Shop','site':'MY','market':'MY','surfaces':['GALLERY']},
        'compile_assets':True,
        'agent_plan':{
            'portfolio_curation':{
                'portfolio_thesis':'Build a varied decision journey, not a repeated packshot carousel.',
                'product_presence_rhythm':['HERO','ABSENT','SUPPORTING'],
            },
            'asset_art_directions':[
                {
                    'consumer_question':'What is the formula logic?',
                    'visual_carrier':'EVIDENCE_GRAPHIC',
                    'composition_grammar':'evidence map with no product object',
                    'product_presence':{'planning_state':'FORBIDDEN','source_reference_role':'TRUTH_REFERENCE_ONLY'},
                }
            ],
        },
    }
    plan=compile_agent_autonomy_plan(request)
    creative=plan['creative_exploration']
    assert creative['require_per_asset_art_direction'] is True
    assert creative['runtime_may_originate_art_direction'] is False
    assert creative['asset_art_directions'][0]['visual_carrier']=='EVIDENCE_GRAPHIC'
    assert plan['portfolio_curation']['product_presence_rhythm']==['HERO','ABSENT','SUPPORTING']
