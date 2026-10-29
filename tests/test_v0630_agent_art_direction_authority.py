from __future__ import annotations

from cbcc.agent_authority_prompt_compiler import compile_asset_prompt
from cbcc.agent_autonomy import compile_agent_autonomy_plan, agent_creative_directions, compile_agent_next_action
from cbcc.creative import apply_creative_system_to_assets


def _target():
    return {
        'target_id':'T1',
        'market':'MY',
        'platform_family':'TikTok Shop',
        'site':'MY',
        'category':'Beauty',
        'surfaces':['GALLERY'],
    }


def _lang():
    return {
        'primary_locale':'en-MY',
        'support_locales':['ms-MY'],
        'visible_copy_locales':['en-MY','ms-MY'],
        'delivery_locale':'zh-CN',
    }


def _base_asset(asset_id='AST-1'):
    return {
        'asset_id':asset_id,
        'asset_name':asset_id,
        'asset_type':'IMAGE',
        'surface':'GALLERY',
        'family':'VISUAL',
        'consumer_question':'What should the shopper understand here?',
        'decision_intent':'PROOF',
        'strategic_job':'Resolve the shopper decision with evidence.',
        'incremental_information':'One new decision-critical fact.',
        'belief_target':'The shopper understands the evidence.',
        'entry_state':'uncertain',
        'exit_state':'decision-ready',
        'product_fidelity':'REFERENCE_GUIDED',
        'creative_direction':{
            'direction_id':'DIR-AGENT',
            'direction_name':'Agent direction',
            'require_per_asset_art_direction':True,
            'creative_thesis':'Shared system only; asset art direction owns composition.',
            'typography':'shared typography tokens',
            'color_world':{'logic':'shared continuity only'},
        },
        'editable_layer_contract':{},
        'visible_copy':{},
    }


def test_forbidden_product_presence_never_creates_product_layer():
    asset=_base_asset()
    asset['asset_art_direction']={
        'asset_id':'AST-1',
        'visual_carrier':'EVIDENCE_GRAPHIC',
        'subject':'verified evidence plane and botanical support structure',
        'composition_grammar':'evidence field with a vertical proof spine and open negative space',
        'product_presence':{
            'planning_state':'FORBIDDEN',
            'product_role':'ABSENT',
            'presence_why':'The decision is carried entirely by evidence; a packshot would add no information.',
            'source_reference_role':'TRUTH_REFERENCE_ONLY',
        },
    }
    asset['product_presence']=asset['asset_art_direction']['product_presence']
    bundle=compile_asset_prompt(asset,{'name':'Example Product'},_target(),{},_lang(),source_product_assets=[{
        'asset_id':'PRODUCT-REF','role':'PRODUCT_MASTER','path':'product.png','pixel_lock':False,
    }])
    assert bundle['status']=='CANONICAL_PROMPT_COMPILED_AGENT_AUTHORITY'
    assert bundle['renderer_recipe']['ready_for_generation'] is True
    assert not any('product' in layer for layer in bundle['renderer_recipe']['layer_plan'])
    assert bundle['design_card']['product_identity']['visible_product_required'] is False
    assert bundle['renderer_recipe']['source_product_bindings'][0]['usage_role']=='TRUTH_REFERENCE_ONLY'
    assert bundle['renderer_recipe']['source_product_bindings'][0]['visible_subject_binding'] is False
    assert 'Product is intentionally absent in this asset.' in bundle['prompt_en']


def test_missing_agent_art_direction_blocks_instead_of_inventing_product_or_layout():
    asset=_base_asset()
    bundle=compile_asset_prompt(asset,{'name':'Example Product'},_target(),{},_lang())
    assert bundle['status']=='AGENT_ART_DIRECTION_REQUIRED'
    assert bundle['renderer_recipe']['ready_for_generation'] is False
    assert bundle['renderer_recipe']['blocked_reason']=='MISSING_AGENT_ART_DIRECTION_OR_PRODUCT_PRESENCE'
    assert not any('product' in layer for layer in bundle['renderer_recipe']['layer_plan'])
    assert bundle['design_card']['product_presence']['planning_state']=='UNRESOLVED_AGENT_DECISION'
    assert 'Do not place' in bundle['prompt_en']


def test_per_asset_art_direction_beats_direction_level_fallback_and_preserves_difference():
    architecture={
        'assets':[
            {
                **_base_asset('AST-1'),
                'creative_brief':{'composition':'legacy centered packshot'},
                'visual_production_signature':{'composition_grammar':'legacy centered product hero'},
            },
            {
                **_base_asset('AST-2'),
                'creative_brief':{'composition':'legacy centered packshot'},
                'visual_production_signature':{'composition_grammar':'legacy centered product hero'},
            },
        ]
    }
    direction={
        'direction_id':'DIR-AGENT',
        'direction_name':'Agent direction',
        'decision':'SELECT',
        'source':'HOST_AGENT_AUTHORED',
        'require_per_asset_art_direction':True,
        'creative_thesis':'Shared continuity only.',
        'composition_grammar':'THIS DIRECTION-LEVEL COMPOSITION MUST NOT OVERRIDE ASSETS',
        'photography':'shared lighting family',
        'asset_art_directions':[
            {
                'asset_id':'AST-1',
                'visual_carrier':'EDITORIAL_EVIDENCE_FIELD',
                'subject':'ingredient evidence and copy hierarchy',
                'composition_grammar':'asymmetric editorial evidence field; no product object',
                'spatial_rhythm':'dense-left / open-right evidence rhythm',
                'evidence_plane':'formula facts',
                'product_presence':{
                    'planning_state':'FORBIDDEN',
                    'source_reference_role':'TRUTH_REFERENCE_ONLY',
                    'presence_why':'Product would duplicate the hero and weaken the proof asset.',
                },
            },
            {
                'asset_id':'AST-2',
                'visual_carrier':'HUMAN_ROUTINE_MOMENT',
                'subject':'hand and skin routine moment',
                'action':'apply one measured drop in the routine',
                'composition_grammar':'tight action crop with diagonal hand-to-skin focal path',
                'camera_or_view':'close three-quarter routine view',
                'product_presence':{
                    'planning_state':'SUPPORTING',
                    'product_role':'small traceable routine object, not hero',
                    'source_reference_role':'SUBJECT_REFERENCE',
                    'presence_why':'The action needs traceability to the product without turning into another packshot.',
                },
            },
        ],
    }
    council={'selected_direction':direction,'alternative_directions':[],'directions':[direction],'direction_source':'USER_SUPPLIED'}
    out=apply_creative_system_to_assets(architecture,council,{'color':{'continuity':'shared'}},None)
    a1,a2=out['assets']
    assert a1['art_direction_status']=='AUTHORED'
    assert a2['art_direction_status']=='AUTHORED'
    assert a1['creative_brief']['composition']=='asymmetric editorial evidence field; no product object'
    assert a2['creative_brief']['composition']=='tight action crop with diagonal hand-to-skin focal path'
    assert a1['creative_brief']['composition'] != a2['creative_brief']['composition']
    assert a1['product_presence']['planning_state']=='FORBIDDEN'
    assert a2['product_presence']['planning_state']=='SUPPORTING'
    assert a1['visual_production_signature']['authority']=='HOST_AGENT_ART_DIRECTION'
    assert a2['visual_production_signature']['authority']=='HOST_AGENT_ART_DIRECTION'
    assert 'THIS DIRECTION-LEVEL COMPOSITION' not in a1['creative_brief']['composition']
    assert 'THIS DIRECTION-LEVEL COMPOSITION' not in a2['creative_brief']['composition']
    assert out['creative_system_assignment']['agent_authored_art_direction_count']==2
    assert out['creative_system_assignment']['missing_agent_art_direction_count']==0


def test_agent_plan_promotes_per_asset_art_direction_to_first_class_authority():
    request={
        'target':_target(),
        'compile_assets':True,
        'agent_plan':{
            'creative_exploration':{
                'asset_art_directions':[
                    {
                        'asset_id':'AST-1',
                        'visual_carrier':'SOURCE_EVIDENCE',
                        'composition_grammar':'documentary evidence crop',
                        'product_presence':{'planning_state':'FORBIDDEN','source_reference_role':'TRUTH_REFERENCE_ONLY'},
                    }
                ]
            }
        }
    }
    plan=compile_agent_autonomy_plan(request)
    assert plan['authority_model']['creative_authority']=='HOST_AGENT'
    assert plan['authority_model']['runtime_creative_role']=='VALIDATE_SERIALIZE_COMPILE_EXECUTE_ONLY'
    assert plan['creative_exploration']['require_per_asset_art_direction'] is True
    directions=agent_creative_directions(plan)
    assert directions
    assert directions[0]['require_per_asset_art_direction'] is True
    assert directions[0]['asset_art_directions'][0]['asset_id']=='AST-1'


def test_missing_art_direction_is_a_blocking_agent_frontier_not_a_runtime_design_task():
    plan={
        'creative_exploration':{'require_per_asset_art_direction':True},
        'iteration_policy':{},
        'research':{'stop_conditions':[]},
    }
    architecture={'assets':[{'asset_id':'AST-1','asset_type':'IMAGE','art_direction_status':'MISSING_AGENT_DECISION'}], 'decision_coverage_summary':{}}
    result=compile_agent_next_action(
        plan,
        request={},
        research_gate={},
        asset_architecture=architecture,
        creative_council={'selected_direction':{'direction_id':'DIR-AGENT'}},
        compliance={},
        production_run={},
        gate_scope={},
        content_requiredness={},
    )
    assert result['status']=='ACTION_FRONTIER_OPEN'
    assert result['recommended_next_action']=='AUTHOR_PER_ASSET_ART_DIRECTION'
    assert result['blocking_frontier'][0]['action']=='AUTHOR_PER_ASSET_ART_DIRECTION'
    assert result['blocking_frontier'][0]['items']==['AST-1']
