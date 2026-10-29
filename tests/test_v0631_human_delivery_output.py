from __future__ import annotations

import json
import re
from pathlib import Path

from runtime.cbcc.prompt_compiler import compile_asset_prompt
from runtime.cbcc.asset_compiler import _visual_spec_markdown
from runtime.cbcc.delivery_html import _formal_asset_dir, _asset_page
from runtime.cbcc.delivery_contract import validate_strategy_delivery


def _asset():
    return {
        'asset_id':'AST-HUMAN-DEPTH','asset_name':'油水平衡证据资产','asset_type':'IMAGE','surface':'GALLERY','family':'PDP',
        'production_mode':'GENERATIVE_IMAGE','product_fidelity':'REFERENCE_GUIDED','decision_intent':'PROOF',
        'consumer_question':'为什么这款日常凝胶能同时表达控油与保湿？','strategic_job':'用一个可读的信息关系解释油水平衡。',
        'visible_copy':{'target_copy':'KAWAL MINYAK. KEKALKAN HIDRASI.','delivery_translation':'控油，同时保持水润。'},
        'product_presence':{'planning_state':'SUPPORTING','production_state':'PRESENT','product_role':'small identity anchor','scale_relationship':'28% canvas height','source_reference_role':'SUBJECT_REFERENCE'},
        'asset_art_direction':{
            'visual_carrier':'EDITORIAL_COMMERCE_IMAGE',
            'visual_carrier_why':{'cn':'购买问题是理解平衡关系，因此信息关系应先于产品展示。','en':'The decision job is to understand balance, so the information relationship leads before the product.'},
            'creative_thesis':{'cn':'平衡而非强攻。','en':'Balance, not battle.'},
            'visual_language':{'cn':'克制的编辑型电商视觉。','en':'Restrained editorial-commerce visual language.'},
            'visual_objective':{'cn':'第一眼读懂油水平衡。','en':'Make oil-and-hydration balance legible at first scan.'},
            'decisive_moment':{'cn':'先读平衡关系，再看到产品身份。','en':'Read the balance relationship first, then the product identity.'},
            'subject':{'cn':'油水平衡信息关系与小型产品锚点。','en':'Oil-and-hydration information relationship with a small product anchor.'},
            'composition_grammar':{'cn':'信息主场，产品右下小锚点。','en':'Information-led field with a small product anchor in the lower-right.'},
            'composition_why':{'cn':'避免再次变成大产品 Hero。','en':'Avoid collapsing back into another large product hero.'},
            'spatial_rhythm':{'cn':'大留白、两级信息。','en':'Generous negative space with two information tiers.'},
            'layout_geometry':{'cn':'左侧信息约60%，产品右下。','en':'About 60% information field on the left, product lower-right.'},
            'scale_depth':{'cn':'二维信息为主，产品仅轻微纵深。','en':'Primarily flat information plane with slight product depth.'},
            'product_occupancy':'28% canvas height',
            'focal_path':{'cn':'主命题 → 配方证据 → 产品身份。','en':'proposition → formula evidence → product identity'},
            'negative_space':{'cn':'顶部与左下保持干净。','en':'Keep the top and lower-left clean.'},
            'evidence_hierarchy':{'cn':'平衡关系第一，配方第二，产品身份第三。','en':'Balance relationship first, formula evidence second, product identity third.'},
            'camera_or_view':'eye-level front / subtle 5-degree three-quarter view',
            'focal_length_mm':'85mm full-frame equivalent',
            'focus_dof':'label plane sharp; moderate depth of field',
            'lighting':{'key':'large soft key 45 degrees front-side-above','fill':'white bounce','negative_fill':'narrow negative fill','cct':'5000K','exposure_ratio_plan':'2:1'},
            'cmf':{'material':'matte flexible tube + transparent pump','surface_behavior':'controlled transparent-pump highlight'},
            'palette_hex':['#F6F4EE','#0B3B32','#DCE7E0','#1C2D29'],
            'copy_zone':{'cn':'左侧信息区，避开产品轮廓。','en':'Left information zone, clear of the product silhouette.'},
            'typography':{'cn':'深绿无衬线，两级层级。','en':'Forest-green sans serif with two hierarchy levels.'},
            'copy_render_mode':'MODEL_RENDER',
            'output_spec':'1600×1600 px, 1:1, sRGB, TikTok Shop Malaysia',
            'post_look':{'cn':'自然、克制、低塑料感。','en':'Natural restrained finish with low plasticity.'},
            'product_presence':{'planning_state':'SUPPORTING','production_state':'PRESENT','product_role':'small identity anchor','scale_relationship':'28% canvas height','source_reference_role':'SUBJECT_REFERENCE','presence_why':'product verifies identity without dominating the proof relationship'},
        },
        'approved_visual_elements':['verified formula evidence'],'precision_boundaries':['no invented tests or certifications'],
        'editable_layer_contract':{'editable_layers':['background','information graphics','copy'],'frozen_layers':['verified product facts'],'revision_rule':'revise local layer only'},
        'culture_implications':['Malaysia mobile-first commerce; no medicalized acne-war imagery'],
    }


def _bundle(asset):
    return compile_asset_prompt(
        asset,
        {'name':'K01','category':'skincare','verified_facts':['30g gel']},
        {'market':'MY','platform_family':'TikTok Shop','site':'MY','category':'skincare'},
        {}, {'primary_locale':'ms-MY','delivery_locale':'zh-CN'}, {}, None, None, []
    )


def test_rich_art_direction_survives_model_prompt_asset_spec_and_html(tmp_path:Path):
    asset=_asset(); bundle=_bundle(asset)
    assert bundle['model_prompt_status']=='MODEL_NATIVE_PROMPT_READY'
    assert not re.search(r'[\u3400-\u9fff]',bundle['prompt_en'])
    assert 'deterministic' not in bundle['prompt_en'].lower()

    package=tmp_path/'delivery'; adir=package/'asset_packages'/asset['asset_id']; adir.mkdir(parents=True)
    (adir/'00_asset_manifest.yaml').write_text(
        '\n'.join([
            f"asset_name: {asset['asset_name']}",f"surface: {asset['surface']}",f"decision_intent: {asset['decision_intent']}",
            f"consumer_question: {asset['consumer_question']}",f"asset_type: {asset['asset_type']}",f"production_mode: {asset['production_mode']}"
        ])+'\n',encoding='utf-8'
    )
    (adir/'05_prompt_CN.txt').write_text(bundle['prompt_cn'],encoding='utf-8')
    (adir/'06_prompt_EN.txt').write_text(bundle['prompt_en'],encoding='utf-8')
    (adir/'12_design_card.json').write_text(json.dumps(bundle['design_card'],ensure_ascii=False,indent=2),encoding='utf-8')
    (adir/'13_prompt_contract.json').write_text(json.dumps({'model_prompt_status':bundle['model_prompt_status']},ensure_ascii=False),encoding='utf-8')
    (adir/'14_visible_copy_block.json').write_text(json.dumps(bundle['visible_copy_block'],ensure_ascii=False,indent=2),encoding='utf-8')
    (adir/'15_production_assembly_notes.json').write_text(json.dumps(bundle['production_assembly_notes'],ensure_ascii=False,indent=2),encoding='utf-8')
    visual={'approved_visual_elements':asset['approved_visual_elements'],'precision_boundaries':asset['precision_boundaries'],'culture_implications':asset['culture_implications']}
    visual_md=_visual_spec_markdown(asset,visual,None)
    (adir/'02_visual_spec.md').write_text(visual_md,encoding='utf-8')

    for token in ['视觉载体','产品占画','焦点路径','85mm','5000K','28%','#0B3B32','完整 Agent Art Direction 原始对象']:
        assert token in visual_md

    formal=_formal_asset_dir(adir,package)
    page=_asset_page(formal)
    for token in ['Model Prompt CN｜中文模型提示词','Model Prompt EN｜英文模型提示词','生产 / 装配说明','文字渲染 / 装配路线','视觉载体','产品占画','焦点路径','85mm','5000K','28%','#0B3B32']:
        assert token in page
    assert '确定性排版规则' not in page
    assert 'Prompt 是执行合同' not in page
    assert 'deterministic post-layout text' not in page.lower()
    assert '控油，同时保持水润。' in page
    assert 'KAWAL MINYAK. KEKALKAN HIDRASI.' in page


def _minimal_full_strategy(*, asset_reasoning):
    return {
        'human_projection':{'mode':'FULL'},
        'sections':{
            '01_information_completeness_assumptions_decisions':{
                'domain_matrix':[{'domain':'product','status':'known'}],
                'clarifying_questions':[],
                'decision_log':[{'what':'positioning','why':'decision reason','execution':'execute','measurement':'measure'}],
            },
            '02_product_truth_value_ladder':{
                'product_facts':[{'fact':'30g','evidence_grade':'B','real_selling_point':'portable','perceived_benefit':'easy routine','emotional_value':'simple','claim_boundary':'size fact only'}],
                'claim_value_ladder':[],
            },
            '03_platform_region_audience_culture_insight':{
                'platform_audience_culture_rows':[{'platform':'TikTok Shop','region':'MY','audience':'adult skincare users','adaptation':'mobile-first BM','stereotype_taboo_check':'no ethnic stereotyping','why':'local commerce behavior'}],
                'intersectionality_table':[{'age':'adult','region':'MY'}],
                'adaptation_rows':[{'language':'BM first'}],
            },
            '04_marketing_core_strategy':{
                'positioning':{'statement':'daily balance','why':'routine relevance'},
                'message_hierarchy':['balance','formula','identity'],
                'frameworks':{'STP':'adult oily skin','JTBD':'daily balance'},
            },
            '05_visual_photography_strategy':{
                'palette_hex':['#F6F4EE','#0B3B32'],
                'composition':'dynamic per-asset composition authored by Agent',
                'color_management':'sRGB',
                'platform_dimensions':['1600x1600'],
                'asset_parameter_reasoning':asset_reasoning,
            },
            '06_platform_content_matrix':[{
                'platform':'TikTok Shop','audience':'adult skincare users','topic':'daily balance','hook':'oily skin still needs hydration','script_structure':'hook-proof-use','visual_form':'editorial commerce','cta':'view product','metric':'CTR/CVR','race_stage':'COMMUNICATION','culture_adaptation':'BM first','taboo_stereotype_check':'pass','why':'decision fit',
                'platform_dimensions':'1080x1920','duration':'18s','cover_first_frame':'balance hook','subtitle_strategy':'BM first','music_rights':'licensed/platform library','traffic_mechanism':'organic/shop discovery','landing_handoff':'PDP','utm_attribution':'platform analytics'
            }],
            '07_race_execution_table':[
                {'stage':'RESEARCH','objective':'learn','key_actions':['research'],'output':'insights','platform':'TikTok Shop','culture_check':'MY/BM','kpi':'evidence quality','why':'ground decisions'},
                {'stage':'ACTION','objective':'build','key_actions':['build'],'output':'assets','platform':'TikTok Shop','culture_check':'MY/BM','kpi':'production readiness','why':'materialize'},
                {'stage':'COMMUNICATION','objective':'publish','key_actions':['publish'],'output':'content','platform':'TikTok Shop','culture_check':'MY/BM','kpi':'CTR','why':'reach shoppers'},
                {'stage':'EVALUATION','objective':'learn','key_actions':['evaluate'],'output':'learning','platform':'TikTok Shop','culture_check':'MY/BM','kpi':'CVR','why':'iterate'},
            ],
            '08_culture_adaptation_checklist':[{'adaptation_point':'BM first','inclusive_representation':'adult Malaysian context','stereotype_taboo_risk':'avoid ethnic shorthand','result':'pass','modification':'use neutral contemporary context','why':'relevance without stereotyping'}],
            '09_risk_measurement_priority_next_steps':{
                'priority_plan':{'P0':['truth'],'P1':['creative'],'P2':['optimization']},
                'output_self_check':{'fabrication_check':'pass','why_check':'pass','culture_check':'pass','compliance_check':'pass','metric_check':'pass','assumption_check':'pass'},
                'ab_test_hypotheses':[{'test':'balance vs ingredient hook'}],
                'next_information_needed':['real performance data'],
                'risk_register':[{'risk':'claim overreach'}],
            },
        }
    }


def test_full_depth_is_carrier_aware_but_rejects_shallow_asset_art_direction():
    graphic=_minimal_full_strategy(asset_reasoning=[{'asset_id':'AST-GRAPHIC','visual_carrier':'GRAPHIC_INFORMATION_DESIGN','composition_grammar':'evidence-led asymmetric field','product_presence':'FORBIDDEN','why':'proof relation does not need packshot'}])
    report=validate_strategy_delivery(graphic)
    codes=[x['code'] for x in report['issues']]
    assert 'FULL_PHOTOGRAPHY_ROUTE_DEPTH_MISSING' not in codes
    assert 'FULL_ASSET_ART_DIRECTION_REASONING_SHALLOW' not in codes

    shallow=_minimal_full_strategy(asset_reasoning=[{'asset_id':'AST-THIN'}])
    report2=validate_strategy_delivery(shallow)
    codes2=[x['code'] for x in report2['issues']]
    assert 'FULL_ASSET_ART_DIRECTION_REASONING_SHALLOW' in codes2
