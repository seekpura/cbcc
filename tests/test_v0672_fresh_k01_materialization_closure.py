from pathlib import Path
import json, re

from cbcc.commercial_continuity_authority import _commercial_prompt_lines
from cbcc.full_delivery_depth_v3 import _card_issues
from cbcc.canonical_full_package_audit_v0671 import _reconcile_legacy_issues

CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]')


def test_en_commercial_context_omits_chinese_only_values():
    lineage = {
        'positioning': {'primary_conversion_proposition': 'Lightweight hydration for oily skin'},
        'audience_culture': {'segments': ['oily-skin shoppers', '马来西亚年轻消费者'], 'visual_implications': ['keep texture light', '避免刻板印象']},
        'race': [
            {'stage':'COMMUNICATION','objective':'按平台原生方式传播','why':'同一价值需要不同表达'},
            {'stage':'EVALUATION','objective':'Measure PDP CVR','why':'Use conversion evidence'},
        ],
    }
    text='\n'.join(_commercial_prompt_lines(lineage,'EN'))
    assert not CJK.search(text), text
    assert 'Lightweight hydration for oily skin' in text
    assert 'Measure PDP CVR' in text


def test_modern_nested_design_card_satisfies_legacy_semantic_audit():
    card = {
        'commerce_task': {'consumer_question':'Will this work in my routine?','strategic_job':'Resolve routine fit','incremental_information':'Show lightweight use','business_hypothesis':'clarity reduces hesitation','success_metric':'PDP CVR'},
        'visual_carrier':'HUMAN_ROUTINE_CROP',
        'product_presence': {'planning_state':'SUPPORTING','presence_why':'Product supports routine evidence.'},
        'subject_system': {'subject_type':'PERSON'},
        'subject_action_environment_props': {'subject':'adult user','environment':'bathroom shelf','props':['towel']},
        'information_design': {'proof_plane':'routine steps'},
        'composition_camera': {'composition_grammar':'diagonal action crop'},
        'lighting_material_cmf': {'cmf': {'background':'warm ivory'}},
    }
    assert _card_issues(card,'AST-X') == []


def _gate(tmp_path: Path, required: bool):
    (tmp_path/'supporting_analysis').mkdir(parents=True, exist_ok=True)
    (tmp_path/'supporting_analysis'/'gate_scope.json').write_text(json.dumps({'gates': {'PRODUCTION': {'required_for_current_scope': required}}}), encoding='utf-8')


def test_provider_media_not_blocking_when_production_not_current_scope(tmp_path: Path):
    _gate(tmp_path, False)
    result={'status':'INCOMPLETE','issues':[{'code':'FULL_PROVIDER_RESULT_MISSING'},{'code':'FULL_ACTUAL_GENERATED_OUTPUT_MISSING'}]}
    out=_reconcile_legacy_issues(tmp_path,result)
    assert out['status']=='PASS'
    assert out['provider_media_e2e']['status']=='E2E_PENDING_NOT_REQUESTED'


def test_provider_media_remain_blocking_when_production_is_current_scope(tmp_path: Path):
    _gate(tmp_path, True)
    result={'status':'INCOMPLETE','issues':[{'code':'FULL_PROVIDER_RESULT_MISSING'}]}
    out=_reconcile_legacy_issues(tmp_path,result)
    assert out['status']=='INCOMPLETE'
    assert out['issues'][0]['code']=='FULL_PROVIDER_RESULT_MISSING'


def test_final_manifest_presence_overrides_stale_universe_count(tmp_path: Path):
    import yaml
    root=tmp_path/'asset_packages'/'AST-X'; root.mkdir(parents=True)
    (root/'00_asset_manifest.yaml').write_text(yaml.safe_dump({'asset_id':'AST-X','product_presence':{'planning_state':'REQUIRED','presence_why':'Identity proof needs product.'}}, allow_unicode=True), encoding='utf-8')
    (tmp_path/'ASSET_UNIVERSE.json').write_text(json.dumps({'assets':[{'asset_id':'AST-X'}], 'product_presence_portfolio_audit':{'total_assets':1,'structured_presence_decisions':0}}), encoding='utf-8')
    result={'status':'INCOMPLETE','issues':[{'code':'PRODUCT_PRESENCE_DECISION_NOT_STRUCTURED','structured':0,'total':1}]}
    out=_reconcile_legacy_issues(tmp_path,result)
    assert out['status']=='PASS'
    repaired=json.loads((tmp_path/'ASSET_UNIVERSE.json').read_text())['product_presence_portfolio_audit']
    assert repaired['structured_presence_decisions']==1


def test_cbcc_commercial_workspace_not_fixed_taxonomy_failure(tmp_path: Path):
    (tmp_path/'index.html').write_text('<main data-workspace-shell="cbcc-commercial-v1"><section data-route="product"></section><section data-route="market"></section><section data-route="strategy"></section><section data-route="listing"></section><section data-route="visual"></section><section data-route="assets"></section></main>', encoding='utf-8')
    result={'status':'INCOMPLETE','issues':[{'code':'FIXED_CAPABILITY_ROUTE_TAXONOMY'}]}
    out=_reconcile_legacy_issues(tmp_path,result)
    assert out['status']=='PASS'


def test_positive_materialization_runs_before_legacy_audit(tmp_path: Path, monkeypatch):
    import cbcc.canonical_full_package_audit_v0671 as mod
    sentinel=tmp_path/'CURRENT_FIRST'
    monkeypatch.setattr(mod,'audit_current_full_canonical_parity',lambda package:(sentinel.write_text('yes'),{'status':'PASS','issues':[]})[1])
    def legacy(package):
        assert sentinel.exists(), 'legacy audit ran before current positive materialization'
        return {'status':'PASS','issues':[]}
    out=mod.wrap_audit_host_full_package(legacy)(tmp_path)
    assert out['status']=='PASS'
