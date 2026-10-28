from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project

REQ_SECTIONS={
'01_information_completeness_assumptions_decisions','02_product_truth_value_ladder','03_platform_region_audience_culture_insight','04_marketing_core_strategy','05_visual_photography_strategy','06_platform_content_matrix','07_race_execution_table','08_culture_adaptation_checklist','09_risk_measurement_priority_next_steps'}
LEGACY_FILES={'00_asset_manifest.yaml','01_strategy.md','02_visual_spec.md','04_layout_contract.json','05_prompt_CN.txt','06_prompt_EN.txt','07_generation_guidance.txt','08_copy.md','09_production_notes.md','10_source_trace.md'}

def test_strategy_authority_and_asset_package_preservation(tmp_path):
    fx=ROOT/'tests/fixtures/kiyuu_my_tiktok'
    req=json.loads((fx/'request.json').read_text(encoding='utf-8'))
    req['visual_strategy']={'style':'Tropical Clinical Minimalism','style_why':'Serve product clarity and Malaysia beauty context.','palette':['#0F3B2E','#F4EFE3','#B7C7A3'],'platform_dimensions':{'gallery':'1:1'}}
    req['positioning']={'primary_conversion_proposition':'Daily oil-balancing hydration for oily, blemish-prone routines'}
    state=build_project(tmp_path/'p',req,ROOT/'platform_packs')
    assert state['gates']['STRATEGY_AUTHORITY']['status']=='READY_REVIEW'
    strategy=json.loads((tmp_path/'p/artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
    assert REQ_SECTIONS.issubset(strategy['sections'])
    assert strategy['positive_design_first'] is True
    assert 'WHY' in strategy['strategy_decision_contract']
    md=(tmp_path/'p/artifacts/strategy/MASTER_STRATEGY_CN.md').read_text(encoding='utf-8')
    assert '## 6. 分平台内容矩阵表' in md and '## 7. RACE传播框架执行表' in md and '## 8. 族裔文化适配检查表' in md
    idx=json.loads((tmp_path/'p/artifacts/asset_packages/ASSET_PACKAGE_INDEX.json').read_text(encoding='utf-8'))
    assert idx['legacy_alpha6_package_preserved'] is True
    for row in idx['assets']:
        d=Path(row['path'])
        assert LEGACY_FILES.issubset({x.name for x in d.iterdir()})
        assert (d/'11_strategy_authority_trace.json').exists()

def test_strategy_continues_when_submission_rule_is_unknown(tmp_path):
    req={'project_id':'UNKNOWN-V05','product':{'name':'Test Product','category':'test'},'sources':[{'source_id':'S1','kind':'USER_PROVIDED_FACT'}],
         'target':{'market':'Unknown','platform_family':'nonexistent_platform','site':'ZZ','primary_locale':'en-US','currency':'USD'},
         'shopper_questions':['What is it?','Why buy it?'],'compile_assets':False}
    state=build_project(tmp_path/'p',req,ROOT/'platform_packs')
    assert state['gates']['PLATFORM_COMPILE']['status']=='HOLD'
    assert state['gates']['STRATEGY_AUTHORITY']['status']=='READY_REVIEW'
    assert state['gates']['CONTENT_GRAPH']['status']=='READY_REVIEW'
