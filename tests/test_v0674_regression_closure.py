from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'runtime' / 'cbcc' / 'v0674_regression_closure.py'


def _load():
    spec = importlib.util.spec_from_file_location('v0674_regression_closure', MOD)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_full_alias_family_is_strict_but_not_only_literal_full():
    m = _load()
    yes = [
        {'delivery_mode': 'FULL'},
        {'delivery_mode': 'FULL_PROJECT'},
        {'scope_mode': 'full-delivery'},
        {'human_projection': {'mode': 'FULL_PACKAGE'}},
        {'human_projection': {'mode': '完整交付'}},
        {'human_projection': {'fixed_human_section_quota': True}},
    ]
    no = [
        {'delivery_mode': 'TASK_SCOPED'},
        {'delivery_mode': 'PARTIAL'},
        {'delivery_mode': 'NOT_FULL'},
        {'delivery_mode': 'NON_FULL'},
        {},
    ]
    assert all(m.is_full_strategy(x) for x in yes)
    assert not any(m.is_full_strategy(x) for x in no)


def test_markdown_table_split_preserves_escaped_pipe_as_cell_content():
    m = _load()
    line = r'| 产品标题 | A \| B | 甲｜乙 | 是 | READY |'
    cells = m.split_markdown_table_row(line)
    assert cells == ['产品标题', 'A | B', '甲｜乙', '是', 'READY']


def test_markdown_table_split_handles_even_backslashes_before_real_delimiter():
    m = _load()
    line = r'| 路径 | C:\\temp\\ | READY |'
    cells = m.split_markdown_table_row(line)
    assert cells == ['路径', 'C:\\temp\\', 'READY']


def test_yaml_dump_has_no_anchors_for_shared_object_identity():
    m = _load()
    shared = {'planning_state': 'REQUIRED', 'presence_why': 'identity'}
    payload = {'product_presence': shared, 'nested': {'same_presence': shared}}
    text = m.safe_dump_no_aliases(payload)
    assert '&id' not in text
    assert '*id' not in text
    import yaml
    assert yaml.safe_load(text)['nested']['same_presence']['planning_state'] == 'REQUIRED'


def test_listing_three_state_strategy_ready_preserves_legacy_status():
    m = _load()
    center = {
        'task_scope': {'listing_active': True, 'listing_submission_sensitive': False},
        'readiness': {'status': 'READY_WITH_HOLDS', 'pending_count': 1},
        'copy_center': [{'field': 'category', 'value': 'Beauty', 'status': '待查证'}],
        'localized_copy': [],
    }
    out = m.apply_listing_three_state(center)
    assert out['canonical_listing_state'] == 'STRATEGY_READY'
    assert out['readiness']['status'] == 'READY_WITH_HOLDS'
    assert out['listing_status_contract']['legacy_status'] == 'READY_WITH_HOLDS'
    assert out['listing_status_contract']['allowed_states'] == ['STRATEGY_READY','COPY_REVIEW_REQUIRED','PUBLISH_READY']


def test_listing_three_state_copy_review_required_when_target_copy_is_not_final():
    m = _load()
    center = {
        'task_scope': {'listing_active': True, 'listing_submission_sensitive': True},
        'target': {'locale': 'en-US', 'visible_copy_locales': ['en-US'], 'delivery_locale': 'zh-CN'},
        'readiness': {'status': 'READY_FOR_CURRENT_SCOPE', 'pending_count': 0},
        'copy_center': [{'field': 'title', 'value': 'Title', 'status': 'READY', 'delivery_companion_status': 'READY'}],
        'localized_copy': [{'field': 'title', 'locale': 'en-US', 'value': 'Title', 'status': 'DRAFT_REVIEW_REQUIRED', 'delivery_translation': '标题'}],
    }
    out = m.apply_listing_three_state(center)
    assert out['canonical_listing_state'] == 'COPY_REVIEW_REQUIRED'


def test_listing_three_state_publish_ready_requires_submission_scope_and_final_copy():
    m = _load()
    center = {
        'task_scope': {'listing_active': True, 'listing_submission_sensitive': True},
        'target': {'locale': 'en-US', 'visible_copy_locales': ['en-US'], 'delivery_locale': 'zh-CN'},
        'readiness': {'status': 'READY_FOR_CURRENT_SCOPE', 'pending_count': 0},
        'copy_center': [{'field': 'title', 'value': 'Title', 'status': 'READY', 'delivery_companion_status': 'READY'}],
        'localized_copy': [{'field': 'title', 'locale': 'en-US', 'value': 'Title', 'status': 'APPROVED_FINAL', 'delivery_translation': '标题'}],
    }
    out = m.apply_listing_three_state(center)
    assert out['canonical_listing_state'] == 'PUBLISH_READY'


def test_listing_three_state_final_foreign_copy_without_cn_companion_is_not_publish_ready():
    m = _load()
    center = {
        'task_scope': {'listing_active': True, 'listing_submission_sensitive': True},
        'target': {'locale': 'ms-MY', 'delivery_locale': 'zh-CN'},
        'delivery_language': {'locale': 'zh-CN'},
        'readiness': {'status': 'READY_FOR_CURRENT_SCOPE', 'pending_count': 0},
        'copy_center': [{'field': 'title', 'value': 'Tajuk', 'status': 'READY'}],
        'localized_copy': [{'field': 'title', 'locale': 'ms-MY', 'delivery_locale': 'zh-CN', 'value': 'Tajuk', 'status': 'APPROVED_FINAL'}],
    }
    out = m.apply_listing_three_state(center)
    assert out['canonical_listing_state'] == 'COPY_REVIEW_REQUIRED'
    assert 'chinese_companion_missing' in out['listing_status_contract']['reasons']


def test_listing_three_state_inactive_scope_has_no_fake_fourth_state():
    m = _load()
    center = {
        'task_scope': {'listing_active': False, 'listing_submission_sensitive': False},
        'readiness': {'status': 'NOT_IN_CURRENT_SCOPE', 'pending_count': 0},
        'copy_center': [], 'localized_copy': [],
    }
    out = m.apply_listing_three_state(center)
    assert out['canonical_listing_state'] is None
    assert out['listing_status_contract']['applicability'] == 'NOT_IN_CURRENT_SCOPE'
    assert out['listing_status_contract']['legacy_status'] == 'NOT_IN_CURRENT_SCOPE'


def test_prompt_provenance_membrane_removes_only_internal_metadata_clauses():
    m = _load()
    raw = (
        'Create a clean ecommerce hero with warm ivory negative space.\n'
        'source_ids: SRC-001, SRC-002; claim_ids: CLM-01.\n'
        'canonical_art_direction_sha256: abcdef123456; authority_hash: deadbeef.\n'
        'Use the attached product reference images to preserve real package geometry.\n'
        'Keep a soft contact shadow and 50 mm natural perspective.\n'
    )
    cleaned = m.strip_prompt_provenance_metadata(raw)
    assert 'source_ids' not in cleaned
    assert 'claim_ids' not in cleaned
    assert 'canonical_art_direction_sha256' not in cleaned
    assert 'authority_hash' not in cleaned
    assert 'attached product reference images' in cleaned
    assert 'soft contact shadow' in cleaned


def test_prompt_provenance_detector_catches_cn_and_en_internal_lineage():
    m = _load()
    bad = '来源ID：SRC-1；证据ID：E-1；谱系：sha256=abc；provenance: internal.'
    issues = m.prompt_provenance_leaks(bad)
    assert issues
    assert all(x['code'] == 'PROVENANCE_METADATA' for x in issues)


def test_source_ledger_materialization_is_explicit_and_idempotent(tmp_path: Path):
    m = _load()
    result = {
        'status': 'INCOMPLETE',
        'copied_count': 1,
        'missing_count': 1,
        'items': [
            {'source_path': '/truth/2.png', 'package_path': 'sources/2.png', 'status': 'COPIED', 'sha256': 'a'*64, 'bytes': 123},
            {'source_path': '/truth/6.png', 'package_path': None, 'status': 'MISSING_FILE'},
        ],
    }
    first = m.materialize_source_ledger(tmp_path, result)
    before = (tmp_path/'sources'/'SOURCE_LEDGER.json').read_bytes()
    second = m.materialize_source_ledger(tmp_path, result)
    after = (tmp_path/'sources'/'SOURCE_LEDGER.json').read_bytes()
    assert first['status'] == 'INCOMPLETE'
    assert first == second
    assert before == after
    data = json.loads(before)
    assert data['counts'] == {'COPIED': 1, 'MISSING_FILE': 1}
    md = (tmp_path/'sources'/'SOURCE_LEDGER.md').read_text(encoding='utf-8')
    assert '来源台账' in md and 'MISSING_FILE' in md and '2.png' in md


def test_explicit_target_overlay_never_reintroduces_stale_platform():
    m = _load()
    stale = {'platform': 'tiktok_shop', 'market': 'MY', 'site': 'MY', 'locale': 'ms-MY', 'category': 'beauty'}
    scope = {'platform': 'amazon', 'market': 'US', 'site': 'US', 'primary_locale': 'en-US',
             'platform_status': 'EXPLICIT', 'market_status': 'EXPLICIT', 'primary_locale_status': 'EXPLICIT'}
    out = m.apply_explicit_target_scope(stale, scope)
    assert out['platform'] == 'amazon'
    assert out['market'] == 'US'
    assert out['site'] == 'US'
    assert out['locale'] == 'en-US'
    assert out['category'] == 'beauty'


def test_unspecified_explicit_scope_clears_stale_platform_market_and_locale():
    m = _load()
    stale = {'platform': 'tiktok_shop', 'market': 'MY', 'site': 'MY', 'locale': 'ms-MY', 'category': 'beauty'}
    scope = {'platform': None, 'market': None, 'site': None, 'primary_locale': None,
             'platform_status': 'UNSPECIFIED', 'market_status': 'UNSPECIFIED', 'primary_locale_status': 'UNSPECIFIED'}
    out = m.apply_explicit_target_scope(stale, scope)
    assert out['platform'] is None
    assert out['market'] is None
    assert out['site'] is None
    assert out['locale'] is None
    assert out['category'] == 'beauty'


def test_full_alias_lowercase_and_spacing_normalize():
    m=_load()
    assert m.is_full_strategy({'delivery_mode':' full project '})
    assert m.is_full_strategy({'delivery_mode':'full/package'})


def test_full_alias_does_not_accept_incidental_full_word():
    m=_load()
    assert not m.is_full_strategy({'delivery_mode':'NOT_FULL_PROJECT'})
    assert not m.is_full_strategy({'delivery_mode':'non full delivery'})
    assert not m.is_full_strategy({'delivery_mode':'BEAUTIFUL'})


def test_markdown_table_split_preserves_two_escaped_pipes_in_one_cell():
    m=_load()
    cells=m.split_markdown_table_row(r'| 文案 | A \| B \| C | READY |')
    assert cells==['文案','A | B | C','READY']


def test_markdown_wrapper_prevents_legacy_splitter_from_seeing_literal_pipe():
    m=_load()
    def legacy(md):
        # Deliberately emulate the v0.6.73 raw table split, then render cells.
        return '<td>' + '</td><td>'.join(x.strip() for x in md.strip().strip('|').split('|')) + '</td>'
    wrapped=m.wrap_markdown_to_html(legacy)
    rendered=wrapped(r'| A | X \| Y | B |')
    assert '<td>X | Y</td>' in rendered
    assert rendered.count('<td>')==3


def test_markdown_wrapper_is_idempotent():
    m=_load()
    f=lambda text:text
    once=m.wrap_markdown_to_html(f)
    twice=m.wrap_markdown_to_html(once)
    assert once is twice


def test_yaml_no_alias_dump_preserves_unicode_and_order():
    m=_load()
    payload={'中文字段':'值','second':{'x':1}}
    text=m.safe_dump_no_aliases(payload,allow_unicode=True,sort_keys=False)
    assert '中文字段' in text
    assert text.index('中文字段') < text.index('second')


def test_listing_three_state_non_submission_scope_never_claims_publish_ready():
    m=_load()
    center={
        'task_scope':{'listing_active':True,'listing_submission_sensitive':False},
        'target':{'locale':'en-US','visible_copy_locales':['en-US'],'delivery_locale':'zh-CN'},
        'readiness':{'status':'READY_FOR_CURRENT_SCOPE','pending_count':0},
        'copy_center':[{'field':'title','value':'x','status':'READY','delivery_companion_status':'READY'}],
        'localized_copy':[{'field':'title','locale':'en-US','value':'x','status':'APPROVED_FINAL','delivery_translation':'标题'}],
    }
    out=m.apply_listing_three_state(center)
    assert out['canonical_listing_state']=='COPY_REVIEW_REQUIRED'
    assert 'submission_scope_not_validated' in out['listing_status_contract']['reasons']


def test_listing_three_state_does_not_mutate_input_object():
    m=_load()
    original={
        'task_scope':{'listing_active':True,'listing_submission_sensitive':False},
        'readiness':{'status':'READY_WITH_HOLDS','pending_count':1},
        'copy_center':[{'field':'category','value':'Beauty','status':'待查证'}],
        'localized_copy':[],
    }
    out=m.apply_listing_three_state(original)
    assert 'canonical_listing_state' not in original
    assert out['readiness']['status']=='READY_WITH_HOLDS'


def test_prompt_provenance_strip_preserves_plain_word_source_when_pixel_relevant():
    m=_load()
    raw='Use a soft side light source and preserve the attached product reference images.'
    cleaned=m.strip_prompt_provenance_metadata(raw)
    assert 'light source' in cleaned
    assert 'attached product reference images' in cleaned


def test_prompt_provenance_detector_ignores_normal_reference_instruction():
    m=_load()
    assert m.prompt_provenance_leaks('Use the attached product reference images and match real geometry.')==[]


def test_source_ledger_no_declared_sources_has_explicit_empty_state(tmp_path:Path):
    m=_load()
    ledger=m.materialize_source_ledger(tmp_path,{'status':'NO_SOURCE_MEDIA_DECLARED','items':[]})
    assert ledger['counts']=={}
    md=(tmp_path/'sources'/'SOURCE_LEDGER.md').read_text(encoding='utf-8')
    assert 'NO_SOURCE_DECLARED' in md


def test_explicit_scope_can_switch_from_my_to_sg_without_locale_leak():
    m=_load()
    stale={'platform':'tiktok_shop','market':'MY','site':'MY','locale':'ms-MY'}
    sg={'platform':'shopee','market':'SG','site':'SG','primary_locale':'en-SG','platform_status':'EXPLICIT','market_status':'EXPLICIT','primary_locale_status':'EXPLICIT'}
    out=m.apply_explicit_target_scope(stale,sg)
    assert (out['platform'],out['market'],out['site'],out['locale'])==('shopee','SG','SG','en-SG')


def test_explicit_scope_preserves_non_scope_business_fields():
    m=_load()
    base={'category':'beauty','category_id':'123','delivery_locale':'zh-CN','platform':'old'}
    scope={'platform':'amazon','platform_status':'EXPLICIT','market_status':'UNSPECIFIED','primary_locale_status':'UNSPECIFIED'}
    out=m.apply_explicit_target_scope(base,scope)
    assert out['category']=='beauty' and out['category_id']=='123' and out['delivery_locale']=='zh-CN'



def test_listing_three_state_markdown_projection_is_visible():
    m=_load()
    center={
        'canonical_listing_state':'COPY_REVIEW_REQUIRED',
        'listing_status_contract':{'legacy_status':'READY_WITH_HOLDS','reasons':['copy_review_required']},
    }
    wrapped=m.wrap_render_upload_center_md(lambda c:'# 上架资料中心\n\n正文\n')
    text=wrapped(center)
    assert 'COPY_REVIEW_REQUIRED' in text
    assert 'READY_WITH_HOLDS' in text


def test_listing_three_state_html_projection_is_visible():
    m=_load()
    center={
        'canonical_listing_state':'PUBLISH_READY',
        'listing_status_contract':{'legacy_status':'READY_FOR_CURRENT_SCOPE','reasons':[]},
    }
    wrapped=m.wrap_listing_workspace(lambda c:'<div>listing</div>')
    text=wrapped(center)
    assert 'data-listing-state="PUBLISH_READY"' in text
    assert 'PUBLISH_READY' in text and 'READY_FOR_CURRENT_SCOPE' in text

def test_apply_patch_rebinds_cached_consumers_and_is_idempotent(tmp_path:Path, monkeypatch):
    import importlib, sys, types, shutil
    src=MOD
    pkg=tmp_path/'fakecbcc'; pkg.mkdir(); (pkg/'__init__.py').write_text('',encoding='utf-8')
    shutil.copy2(src,pkg/'v0674_regression_closure.py')
    monkeypatch.syspath_prepend(str(tmp_path))

    def mod(name, **attrs):
        x=types.ModuleType(f'fakecbcc.{name}')
        for k,v in attrs.items(): setattr(x,k,v)
        sys.modules[x.__name__]=x
        return x

    old_validator=lambda strategy:{'mode':'TASK_SCOPED'}
    dc=mod('delivery_contract',_full_mode=lambda s:False,validate_strategy_delivery=old_validator)
    fd=mod('full_delivery_depth_v3',_full=lambda s:False)
    dh=mod('delivery_html',markdown_to_html=lambda x:'<p>'+x+'</p>',_listing_workspace=lambda c:'<div>listing</div>')
    hd=mod('human_delivery',_target_summary=lambda p:{'platform':'stale','market':'MY','locale':'ms-MY'},compile_upload_center=lambda p:{'task_scope':{'listing_active':True,'listing_submission_sensitive':False},'readiness':{'status':'READY_FOR_CURRENT_SCOPE','pending_count':0},'copy_center':[{'field':'title','value':'x','status':'READY'}],'localized_copy':[]},render_upload_center_md=lambda c:'# 上架资料中心\n',build_project_hub_md=lambda c:'# 项目总控台\n')
    ps=mod('platform_scope',resolve_platform_scope=lambda p:{'platform':'amazon','market':'US','site':'US','primary_locale':'en-US','platform_status':'EXPLICIT','market_status':'EXPLICIT','primary_locale_status':'EXPLICIT'})
    de=mod('delivery_export',compile_upload_center=hd.compile_upload_center,render_upload_center_md=hd.render_upload_center_md,build_project_hub_md=hd.build_project_hub_md,materialize_source_truth_media=lambda *a,**k:{},validate_strategy_delivery=lambda s:{'mode':'STALE'})
    stm=mod('source_truth_media',materialize_source_truth_media=lambda project,package:{'status':'NO_SOURCE_MEDIA_DECLARED','items':[]})
    import yaml
    ac=mod('asset_compiler',yaml=yaml)
    mp=mod('model_prompt_semantic_membrane',sanitize_model_prompt=lambda p:p,model_prompt_orchestration_leaks=lambda p:[])
    ss=mod('strategy_sources',_active_domains=lambda req:{str((req.get('target') or {}).get('platform_family') or 'none')})

    patch=importlib.import_module('fakecbcc.v0674_regression_closure')
    first=patch.apply_v0674_patches(); second=patch.apply_v0674_patches()
    assert first['status']=='INSTALLED' and second['status']=='ALREADY_INSTALLED'
    assert dc._full_mode({'delivery_mode':'FULL_PROJECT'}) is True
    assert de.validate_strategy_delivery is dc.validate_strategy_delivery
    assert hd._target_summary(tmp_path)['platform']=='amazon'
    compiled_center=de.compile_upload_center(tmp_path)
    assert compiled_center['canonical_listing_state']=='STRATEGY_READY'
    assert 'STRATEGY_READY' in de.render_upload_center_md(compiled_center)
    assert 'data-listing-state=\"STRATEGY_READY\"' in dh._listing_workspace(compiled_center)
    outdir=tmp_path/'pkg'; stm.materialize_source_truth_media(tmp_path,outdir)
    assert (outdir/'sources'/'SOURCE_LEDGER.json').exists()
    shared={'a':1}; text=ac.yaml.safe_dump({'x':shared,'y':shared})
    assert '&id' not in text and '*id' not in text
    assert 'source_ids' not in mp.sanitize_model_prompt('source_ids: S1; Keep soft shadow.')
    assert ss._active_domains({'platform':'shopee'})=={'shopee'}


def test_full_alias_recognizes_real_project_full_strategy_mode():
    m=_load()
    assert m.is_full_strategy({'delivery_mode':'FULL_STRATEGY'}) is True
    assert m.is_full_strategy({'scope_mode':'FULL_E2E'}) is True


def test_prompt_provenance_does_not_strip_visual_artifact_language():
    m=_load()
    raw='Avoid JPEG compression artifacts and halo artifacts around the product edge.'
    cleaned=m.strip_prompt_provenance_metadata(raw)
    assert 'compression artifacts' in cleaned
    assert 'halo artifacts' in cleaned
    assert m.prompt_provenance_leaks(raw)==[]


def test_prompt_provenance_does_not_strip_singular_visual_artifact_instruction():
    m=_load()
    raw='Avoid any compression artifact on fine package typography.'
    cleaned=m.strip_prompt_provenance_metadata(raw)
    assert 'compression artifact' in cleaned
    assert m.prompt_provenance_leaks(raw)==[]


def test_prompt_provenance_mixed_clause_preserves_pixel_instruction_after_metadata_prefix():
    m=_load()
    raw='source_ids: SRC-001, Keep a soft contact shadow and 50 mm natural perspective.'
    cleaned=m.strip_prompt_provenance_metadata(raw)
    assert 'source_ids' not in cleaned
    assert 'soft contact shadow' in cleaned
    assert '50 mm natural perspective' in cleaned


def test_prompt_provenance_key_words_require_metadata_shape_not_natural_language():
    m=_load()
    raw='Build a provenance-inspired museum display with visible material lineage and a clean product pedestal.'
    cleaned=m.strip_prompt_provenance_metadata(raw)
    assert 'provenance-inspired' in cleaned
    assert 'material lineage' in cleaned
    assert m.prompt_provenance_leaks(raw)==[]


def test_listing_lifecycle_ignores_final_copy_from_unrelated_locale():
    m=_load()
    center={
        'task_scope':{'listing_active':True,'listing_submission_sensitive':True},
        'target':{'locale':'ms-MY','visible_copy_locales':['ms-MY'],'delivery_locale':'zh-CN'},
        'readiness':{'status':'READY_FOR_CURRENT_SCOPE','pending_count':0},
        'copy_center':[],
        'localized_copy':[{'field':'title','locale':'en-US','value':'Title','status':'APPROVED_FINAL','delivery_translation':'标题'}],
    }
    out=m.apply_listing_three_state(center)
    assert out['canonical_listing_state']=='STRATEGY_READY'
    assert 'no_target_copy_for_review' in out['listing_status_contract']['reasons']


def test_listing_lifecycle_unrelated_draft_does_not_block_current_target_final():
    m=_load()
    center={
        'task_scope':{'listing_active':True,'listing_submission_sensitive':True},
        'target':{'locale':'ms-MY','visible_copy_locales':['ms-MY'],'delivery_locale':'zh-CN'},
        'readiness':{'status':'READY_FOR_CURRENT_SCOPE','pending_count':0},
        'copy_center':[],
        'localized_copy':[
            {'field':'title','locale':'ms-MY','value':'Tajuk','status':'APPROVED_FINAL','delivery_translation':'标题'},
            {'field':'title','locale':'en-US','value':'Draft','status':'DRAFT_REVIEW_REQUIRED','delivery_translation':'英文草稿'},
        ],
    }
    out=m.apply_listing_three_state(center)
    assert out['canonical_listing_state']=='PUBLISH_READY'


def test_explicit_target_scope_replaces_stale_visible_copy_locales():
    m=_load()
    stale={'platform':'tiktok_shop','market':'MY','locale':'ms-MY','visible_copy_locales':['ms-MY','en-MY']}
    scope={'platform':'amazon','market':'US','primary_locale':'en-US','visible_copy_locales':['en-US'],
           'platform_status':'EXPLICIT','market_status':'EXPLICIT','primary_locale_status':'EXPLICIT'}
    out=m.apply_explicit_target_scope(stale,scope)
    assert out['visible_copy_locales']==['en-US']


def test_platform_scope_wrapper_preserves_current_explicit_dual_visible_locales(tmp_path:Path):
    m=_load()
    (tmp_path/'meta').mkdir()
    (tmp_path/'meta'/'request.json').write_text(json.dumps({
        'target':{'platform':'tiktok_shop','market':'MY','language':{'primary_locale':'ms-MY','visible_copy_locales':['ms-MY','en-MY']}}
    }),encoding='utf-8')
    old=lambda p:{'platform':'tiktok_shop','market':'MY','site':'MY','primary_locale':'ms-MY','platform_status':'EXPLICIT','market_status':'EXPLICIT','primary_locale_status':'EXPLICIT','primary_locale_source':'CURRENT_REQUEST'}
    wrapped=m.wrap_resolve_platform_scope(old)
    scope=wrapped(tmp_path)
    assert scope['visible_copy_locales']==['ms-MY','en-MY']


def test_platform_scope_wrapper_current_request_visible_locales_win_over_stale_target_context(tmp_path:Path):
    m=_load()
    (tmp_path/'meta').mkdir(); (tmp_path/'artifacts').mkdir()
    (tmp_path/'meta'/'request.json').write_text(json.dumps({
        'target':{'platform':'amazon','market':'US','language':{'primary_locale':'en-US','visible_copy_locales':['en-US']}}
    }),encoding='utf-8')
    (tmp_path/'artifacts'/'target_context.json').write_text(json.dumps({
        'explicit':True,'target':{'platform':'tiktok_shop','market':'MY','language':{'primary_locale':'ms-MY','visible_copy_locales':['ms-MY','en-MY']}}
    }),encoding='utf-8')
    old=lambda p:{'platform':'amazon','market':'US','site':'US','primary_locale':'en-US','platform_status':'EXPLICIT','market_status':'EXPLICIT','primary_locale_status':'EXPLICIT','primary_locale_source':'CURRENT_REQUEST'}
    scope=m.wrap_resolve_platform_scope(old)(tmp_path)
    assert scope['visible_copy_locales']==['en-US']
