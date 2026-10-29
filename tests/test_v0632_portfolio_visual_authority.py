from __future__ import annotations

from cbcc.agent_autonomy import compile_agent_autonomy_plan, agent_creative_directions, compile_agent_next_action
from cbcc.portfolio_visual_authority import validate_portfolio_differentiation


def _target():
    return {'market':'MY','platform_family':'TikTok Shop','site':'MY','category':'Beauty','surfaces':['GALLERY']}


def _program():
    return {
        'visual_territory':'clinical calm with editorial tension; evidence feels tactile rather than card-based',
        'carrier_mix':['locked-source hero','graphic evidence axis','human routine crop','material macro'],
        'product_presence_rhythm':['hero','absent','supporting','absent'],
        'scale_density_rhythm':'large sparse hero → dense evidence → tight human crop → sparse macro',
        'composition_rhythm':'asymmetric depth → diagonal evidence axis → cropped human gesture → near-abstract macro field',
        'continuity_tokens':['forest green as accent, not full-frame default','warm mineral neutral only where material story needs it'],
        'deliberate_breaks':['asset 2 removes product entirely','asset 4 abandons left/right copy-product grammar'],
        'delete_merge_logic':'merge any two assets that answer the same shopper question with the same evidence plane',
        'mechanism_bindings':['editorial diagonal evidence spine','macro material interruption','human gesture crop'],
    }


def _review():
    return {
        'status':'PASS_AFTER_REAUTHOR',
        'adjacent_asset_review':[
            {'pair':['AST-1','AST-2'],'delta':'hero depth vs no-product diagonal evidence field'},
            {'pair':['AST-2','AST-3'],'delta':'flat information system vs human action crop'},
        ],
        'keep_reauthor_merge_delete':[
            {'asset_id':'AST-1','decision':'KEEP'},
            {'asset_id':'AST-2','decision':'REAUTHOR_THEN_KEEP'},
        ],
    }


def _next(plan, architecture=None):
    return compile_agent_next_action(
        plan,
        request={}, research_gate={}, asset_architecture=architecture or {'assets':[],'decision_coverage_summary':{}},
        creative_council={'selected_direction':{'direction_id':'DIR-AGENT'}}, compliance={}, production_run={},
        gate_scope={}, content_requiredness={},
    )


def test_visual_agent_plan_requires_portfolio_program_review_and_parameter_closure():
    plan=compile_agent_autonomy_plan({'target':_target(),'compile_assets':True,'agent_plan':{'creative_exploration':{}}})
    c=plan['creative_exploration']
    assert c['require_portfolio_visual_program'] is True
    assert c['require_portfolio_differentiation_review'] is True
    assert c['require_production_parameter_closure'] is True
    decisions=plan['authority_model']['agent_decisions']
    assert 'PORTFOLIO_VISUAL_PROGRAM_AND_RHYTHM' in decisions
    assert 'PORTFOLIO_VISUAL_DIFFERENTIATION_REVIEW' in decisions
    assert 'PRODUCTION_PARAMETER_CLOSURE' in decisions
    result=_next(plan)
    actions=[x['action'] for x in result['blocking_frontier']]
    assert 'AUTHOR_PORTFOLIO_VISUAL_PROGRAM' in actions
    assert 'REVIEW_PORTFOLIO_VISUAL_DIFFERENTIATION' in actions


def test_top_level_agent_portfolio_program_and_review_survive_into_direction():
    plan=compile_agent_autonomy_plan({
        'target':_target(),'compile_assets':True,
        'agent_plan':{
            'portfolio_visual_program':_program(),
            'portfolio_differentiation_review':_review(),
            'asset_art_directions':[
                {'asset_id':'AST-1','visual_carrier':'LOCKED_SOURCE_HERO','composition_grammar':'asymmetric depth stack','deliberate_difference':'large depth-led hero','product_presence':{'planning_state':'HERO_REQUIRED'}},
            ],
        },
    })
    c=plan['creative_exploration']
    assert not c['portfolio_visual_program_missing']
    assert not c['portfolio_differentiation_review_missing']
    directions=agent_creative_directions(plan)
    assert directions
    d=directions[0]
    assert d['portfolio_visual_program']['carrier_mix'][1]=='graphic evidence axis'
    assert d['portfolio_differentiation_review']['status']=='PASS_AFTER_REAUTHOR'
    assert d['require_portfolio_differentiation_review'] is True


def _asset(aid, *, carrier='LOCKED_SOURCE_HERO', role='hero', comp='left copy right product', layout='product right 68%', scale='68% height', neg='left 35%', camera='85mm front', material='warm ivory matte', delta=None):
    art={
        'visual_carrier':carrier,
        'composition_grammar':comp,
        'layout_geometry':layout,
        'scale_depth':scale,
        'negative_space':neg,
        'camera_or_view':camera,
        'material_response':material,
        'product_presence':{'planning_state':'REQUIRED','product_role':role},
    }
    if delta: art['deliberate_difference']=delta
    return {'asset_id':aid,'asset_type':'IMAGE','art_direction_status':'AUTHORED','asset_art_direction':art}


def test_duplicate_visual_signatures_return_to_agent_instead_of_runtime_redesign():
    direction={
        'require_portfolio_differentiation_review':True,
        'portfolio_differentiation_review':_review(),
    }
    architecture={'assets':[
        _asset('AST-1'),
        _asset('AST-2',delta='supposed different copy, but same actual visual grammar'),
        _asset('AST-3',delta='supposed different claim, but same actual visual grammar'),
    ]}
    validation=validate_portfolio_differentiation(architecture,direction)
    assert validation['status']=='RETURN_TO_AGENT'
    assert validation['runtime_may_redesign'] is False
    assert any(x['type']=='DUPLICATE_VISUAL_SIGNATURE' for x in validation['issues'])
    assert validation['duplicate_signature_groups']==[['AST-1','AST-2','AST-3']]


def test_materially_different_assets_with_authored_adjacent_deltas_pass_runtime_validation():
    direction={'require_portfolio_differentiation_review':True,'portfolio_differentiation_review':_review()}
    architecture={'assets':[
        _asset('AST-1',carrier='LOCKED_SOURCE_HERO',role='hero',comp='asymmetric two-layer depth stack',layout='product x=70%, evidence trace x=12%',scale='large 68%',neg='open left crescent',camera='95mm eye level',material='warm mineral plaster',delta='opening identity hero'),
        _asset('AST-2',carrier='GRAPHIC_EVIDENCE_AXIS',role='absent',comp='12-degree diagonal evidence axis',layout='values travel lower-left to upper-right',scale='flat three-level information depth',neg='upper-right breathing field',camera='',material='vellum-like translucent evidence plane',delta='remove product and switch to diagonal information carrier'),
        _asset('AST-3',carrier='HUMAN_ROUTINE_CROP',role='supporting',comp='tight diagonal hand-to-skin action crop',layout='face exits upper edge; hand crosses lower-right',scale='human crop dominates, product small',neg='narrow upper-left copy notch',camera='50mm close three-quarter',material='natural skin + matte towel',delta='switch from flat evidence to embodied routine action'),
    ]}
    validation=validate_portfolio_differentiation(architecture,direction)
    assert validation['status']=='PASS'
    assert not validation['duplicate_signature_groups']
    assert not validation['issues']
