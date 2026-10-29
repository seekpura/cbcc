from __future__ import annotations

from cbcc.prompt_compiler import compile_asset_prompt


def test_prompt_compiler_projects_agent_art_direction_without_duplicate_creative_brief():
    asset={
        'asset_id':'AST-DIRECT',
        'asset_name':'Direct art direction prompt test',
        'asset_type':'IMAGE',
        'surface':'GALLERY',
        'family':'VISUAL',
        'consumer_question':'What evidence matters?',
        'strategic_job':'Make one evidence relationship immediately legible.',
        'incremental_information':'One evidence relationship.',
        'product_fidelity':'REFERENCE_GUIDED',
        'production_mode':'GRAPHIC_DESIGN',
        'asset_art_direction':{
            'visual_carrier':'EDITORIAL_EVIDENCE_FIELD',
            'visual_carrier_why':'Evidence is the subject; a product hero would distract.',
            'subject':'two verified evidence statements connected by one causal visual relationship',
            'decisive_moment':'the causal relationship is understood before secondary copy',
            'composition_grammar':'off-axis evidence spine with one quiet open field',
            'spatial_rhythm':'compact proof cluster / expansive calm field',
            'focal_path':'proof A → relationship → proof B',
            'negative_space':'large quiet field opposite the proof spine',
            'evidence_plane':'verified evidence only',
            'product_presence':{
                'planning_state':'FORBIDDEN',
                'product_role':'ABSENT',
                'source_reference_role':'TRUTH_REFERENCE_ONLY',
                'presence_why':'This asset resolves evidence rather than identity.',
            },
        },
    }
    bundle=compile_asset_prompt(
        asset,
        {'name':'Example Product','category':'beauty'},
        {'market':'MY','platform_family':'TikTok Shop','site':'MY'},
        {},
        {'delivery_locale':'zh-CN','primary_locale':'en-MY','visible_copy_locales':['en-MY']},
    )
    assert bundle['status']=='CANONICAL_PROMPT_COMPILED_AGENT_AUTHORITY'
    card=bundle['design_card']
    assert card['product_presence']['planning_state']=='FORBIDDEN'
    assert card['subject_action_environment_props']['subject'].startswith('two verified evidence statements')
    assert card['composition_camera']['composition_grammar']=='off-axis evidence spine with one quiet open field'
    assert card['information_assetization']['representation']=='EDITORIAL_EVIDENCE_FIELD'
    assert 'off-axis evidence spine with one quiet open field' in bundle['prompt_en']
    assert 'two verified evidence statements connected by one causal visual relationship' in bundle['prompt_en']
    assert not any('product' in layer for layer in bundle['renderer_recipe']['layer_plan'])
