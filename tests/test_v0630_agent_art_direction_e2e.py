from __future__ import annotations

import json
from pathlib import Path

from cbcc.compiler import build_project


def _pack(tmp_path: Path) -> Path:
    pack=tmp_path/'packs'
    pack.mkdir(exist_ok=True)
    (pack/'test.yaml').write_text(
        'pack_id: test\n'
        'platform_family: test_platform\n'
        'site: "*"\n'
        'status: TEST_FIXTURE_VERIFIED\n'
        'synthetic_for_test: true\n'
        'capabilities: [LISTING, SEARCH, VISUAL, VIDEO, PAID, MEASUREMENT, COMPLIANCE]\n'
        'surfaces: [PDP, GALLERY, PDP_VIDEO, PAID_AD]\n'
        'rule_atoms: []\n'
        'research_required_for: []\n',
        encoding='utf-8',
    )
    return pack


def test_agent_forbidden_product_presence_survives_project_to_prompt(tmp_path):
    question='How is the formula architecture organized?'
    request={
        'project_id':'V0630-E2E',
        'planning_only':True,
        'compile_assets':True,
        'product':{
            'name':'Agent Authority Test Product',
            'category':'beauty',
            'net_content':'30 ml',
            'primary_conversion_proposition':'Clear daily formula logic',
        },
        'sources':[{'source_id':'SRC-PRODUCT','kind':'PRODUCT_TRUTH'}],
        'target':{
            'target_id':'T-MY',
            'market':'MY',
            'jurisdiction':'MY',
            'platform_family':'test_platform',
            'site':'TEST',
            'primary_locale':'en-MY',
            'visible_copy_locales':['en-MY'],
            'surfaces':['GALLERY'],
        },
        'content_families':['VISUAL'],
        'shopper_questions':[question],
        'asset_jobs':[
            {
                'family':'VISUAL',
                'surface':'GALLERY',
                'consumer_question':question,
                'decision_intent':'PROOF',
                'strategic_job':'Explain the formula architecture without repeating the product hero.',
                'reason_to_exist':'A dedicated proof asset resolves formula logic more clearly than another packshot.',
                'incremental_information':'Show the relationship among approved formula facts.',
                'business_hypothesis':'A clearer evidence relationship improves formula comprehension.',
                'production_mode':'GRAPHIC_DESIGN',
                'product_fidelity':'REFERENCE_GUIDED',
            }
        ],
        'agent_plan':{
            'portfolio_curation':{
                'portfolio_thesis':'Use the product where identity is needed; let evidence become the subject when evidence is the decision job.',
                'product_presence_rhythm':['ABSENT'],
            },
            'asset_art_directions':[
                {
                    'consumer_question':question,
                    'visual_carrier':'EDITORIAL_EVIDENCE_FIELD',
                    'visual_carrier_why':'The shopper needs to understand a relationship, not inspect the pack.',
                    'subject':'approved formula evidence arranged as one causal editorial field',
                    'decisive_moment':'the eye reads the evidence relationship before any secondary explanation',
                    'composition_grammar':'asymmetric evidence field with a strong proof spine and open counter-space',
                    'spatial_rhythm':'dense evidence cluster balanced by one large calm field',
                    'focal_path':'primary formula relationship → supporting fact → concise conclusion',
                    'evidence_plane':'approved formula facts only',
                    'negative_space':'preserve one deliberate open field for comprehension, not a product slot',
                    'product_presence':{
                        'planning_state':'FORBIDDEN',
                        'product_role':'ABSENT',
                        'presence_why':'The product was already established elsewhere; here it would dilute the proof relationship and repeat the same visual job.',
                        'source_reference_role':'TRUTH_REFERENCE_ONLY',
                    },
                }
            ],
        },
    }

    project=tmp_path/'project'
    build_project(project,request,_pack(tmp_path))

    architecture=json.loads((project/'artifacts/asset_architecture.json').read_text(encoding='utf-8'))
    assert architecture['asset_count']==1
    asset=architecture['assets'][0]
    assert asset['art_direction_status']=='AUTHORED'
    assert asset['product_presence']['planning_state']=='FORBIDDEN'
    assert asset['asset_art_direction']['visual_carrier']=='EDITORIAL_EVIDENCE_FIELD'
    assert asset['creative_brief']['composition']=='asymmetric evidence field with a strong proof spine and open counter-space'
    assert asset['visual_production_signature']['authority']=='HOST_AGENT_ART_DIRECTION'

    package_dir=project/'artifacts/asset_packages'/asset['asset_id']
    contract=json.loads((package_dir/'13_prompt_contract.json').read_text(encoding='utf-8'))
    assert contract['status']=='CANONICAL_PROMPT_COMPILED_AGENT_AUTHORITY'
    renderer=contract['renderer_recipe']
    assert renderer['ready_for_generation'] is True
    assert not any('product' in layer for layer in renderer['layer_plan'])
    assert contract['design_card']['product_identity']['visible_product_required'] is False
    assert contract['design_card']['product_presence']['planning_state']=='FORBIDDEN'
    prompt=(package_dir/'06_prompt_EN.txt').read_text(encoding='utf-8')
    assert 'Product is intentionally absent in this asset.' in prompt
    assert 'Do not add a packshot' in prompt
