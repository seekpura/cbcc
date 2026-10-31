from pathlib import Path
import json, re

from cbcc.commercial_continuity_authority import _commercial_prompt_lines
from cbcc.full_delivery_depth_v3 import _card_issues
from cbcc.canonical_full_package_audit_v0671 import _reconcile_legacy_issues
from cbcc.html_asset_package_parity import audit_html_asset_package_parity
from cbcc.listing_markdown_parity_v0671 import ensure_listing_markdown_canonical_parity, audit_listing_markdown_canonical_parity

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


def test_legacy_materialization_accepts_already_materialized_lazy_human_workspace(tmp_path: Path, monkeypatch):
    import cbcc.canonical_materialization_package_audit as mod
    html = '<html><body><main data-workspace-shell="cbcc-commercial-v1"></main><script id="cbcc-canonical-data-v0672" type="application/json">{"assets":[]}</script><script>/* CBCC_CANONICAL_LAZY_PROJECTION_V0672 */</script></body></html>'
    (tmp_path/'index.html').write_text(html, encoding='utf-8')
    monkeypatch.setattr(mod, 'audit_human_projection_html', lambda text: [])
    monkeypatch.setattr(mod, 'audit_html_asset_package_parity', lambda package: [])
    out = mod.wrap_audit_host_full_package(lambda package:{'status':'PASS','issues':[]})(tmp_path)
    assert out['status']=='PASS'
    assert out['canonical_materialization_parity_audit']['human_positive_projection']['status']=='PASS'
    assert out['canonical_materialization_parity_audit']['human_positive_projection'].get('mode')=='LAZY_CANONICAL_ALREADY_MATERIALIZED'


def _lazy_asset_fixture(root: Path) -> Path:
    asset=root/'asset_packages'/'AST-X'; asset.mkdir(parents=True)
    (asset/'05_prompt_CN.txt').write_text('中文规范提示词',encoding='utf-8')
    (asset/'06_prompt_EN.txt').write_text('English provider prompt',encoding='utf-8')
    card={'commerce_task':{'strategic_job':'resolve'}}
    (asset/'12_design_card.json').write_text(json.dumps(card),encoding='utf-8')
    payload={'assets':[{'id':'AST-X','prompt_cn':'中文规范提示词','prompt_en':'English provider prompt','card':card}]}
    (root/'index.html').write_text('<html><body><script id="cbcc-canonical-data-v0672" type="application/json">'+json.dumps(payload,ensure_ascii=False)+'</script></body></html>',encoding='utf-8')
    return asset


def test_html_asset_parity_reads_lazy_embedded_canonical_data(tmp_path: Path):
    asset=_lazy_asset_fixture(tmp_path)
    assert audit_html_asset_package_parity(tmp_path)==[]
    (asset/'06_prompt_EN.txt').write_text('mutated provider prompt',encoding='utf-8')
    issues=audit_html_asset_package_parity(tmp_path)
    assert any(x.get('code')=='HTML_ASSET_PACKAGE_TEXT_DRIFT' and x.get('field')=='prompt_en' for x in issues)


def test_listing_materializer_refreshes_stale_canonical_appendix_idempotently(tmp_path: Path):
    bm='KIYUU Gel Kawalan Minyak, Anti-Jerawat & Pelembap 30g | Niacinamide + Asid Salisilik | Centella'
    en='KIYUU Oil Control Anti-Acne Moisturizing Gel 30g | Niacinamide + Salicylic Acid | Centella'
    center={
        'task_scope':{'listing_active':True},
        'copy_center':[{'field':'title','locale':'ms-MY','value':bm,'delivery_translation':'KIYUU 控油抗痘保湿凝胶 30g'}],
        'localized_copy':[
            {'field':'title','locale':'ms-MY','value':bm,'delivery_translation':'KIYUU 控油抗痘保湿凝胶 30g'},
            {'field':'title','locale':'en-MY','value':en,'delivery_translation':'KIYUU 控油抗痘保湿凝胶 30g'},
        ],
    }
    (tmp_path/'HUMAN_DELIVERY.json').write_text(json.dumps(center,ensure_ascii=False),encoding='utf-8')
    old='''# Upload Ready\n\n## Title — BM\nOLD BM TITLE\n\n## Title — EN\nOLD EN TITLE\n\n## 多语言 Listing Canonical 对照\n\n| Locale | 字段 | 目标市场 / 基线内容 | 中文释义 / 用途 | 状态 |\n|---|---|---|---|---|\n| ms-MY | title | OLD BM TITLE | 旧中文 | READY |\n'''
    path=tmp_path/'01_LISTING_UPLOAD_READY.md'; path.write_text(old,encoding='utf-8')
    first=ensure_listing_markdown_canonical_parity(tmp_path); bytes1=path.read_bytes()
    assert first['status']=='PASS' and bm in path.read_text(encoding='utf-8') and en in path.read_text(encoding='utf-8')
    second=ensure_listing_markdown_canonical_parity(tmp_path); bytes2=path.read_bytes()
    assert second['status']=='PASS' and bytes1==bytes2
    text=path.read_text(encoding='utf-8').replace(en,'DELETED CURRENT EN TITLE')
    path.write_text(text,encoding='utf-8')
    issues=audit_listing_markdown_canonical_parity(tmp_path)
    assert any(x.get('code')=='LISTING_MARKDOWN_CANONICAL_FIELD_DRIFT' for x in issues)
