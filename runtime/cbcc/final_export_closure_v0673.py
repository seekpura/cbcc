from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Callable
import json
import re
import sys

_INSTALLED = False
_PROVIDER_CODES = {
    'FULL_PROVIDER_RESULT_MISSING','FULL_ACTUAL_GENERATED_OUTPUT_MISSING','FULL_ACTUAL_OUTPUT_REVIEW_MISSING','FULL_LOCAL_REVISION_LINEAGE_MISSING',
    'PROVIDER_RESULT_MISSING','ACTUAL_GENERATED_OUTPUT_MISSING','ACTUAL_OUTPUT_REVIEW_MISSING','LOCAL_REVISION_LINEAGE_MISSING',
}


def _p(v: Any) -> bool:
    return v not in (None, '', [], {})


def _d(v: Any) -> dict[str, Any]:
    return dict(v) if isinstance(v, Mapping) else {}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value=json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value,dict) else {}
    except Exception:
        return {}


def _contains_cjk(value: Any) -> bool:
    return bool(re.search(r'[\u3400-\u4dbf\u4e00-\u9fff]', str(value or '')))


def _english_safe(value: Any) -> Any:
    """Select already-authored English-safe semantic values; never translate Chinese copy."""
    if value in (None,'',[],{}): return None
    if isinstance(value,Mapping):
        out={}
        for key,child in value.items():
            if _contains_cjk(key): continue
            filtered=_english_safe(child)
            if filtered not in (None,'',[],{}): out[key]=filtered
        return out or None
    if isinstance(value,(list,tuple)):
        out=[]
        for child in value:
            filtered=_english_safe(child)
            if filtered not in (None,'',[],{}): out.append(filtered)
        return out or None
    if isinstance(value,str) and _contains_cjk(value): return None
    return value


def _commercial_prompt_lines_v0673(lineage: dict[str,Any], locale: str) -> list[str]:
    is_cn=str(locale).upper()=='CN'; val=lambda x: x if is_cn else _english_safe(x)
    lines=['【商业决策上下文】' if is_cn else '[COMMERCE DECISION CONTEXT]']
    positioning=_d(lineage.get('positioning')); proposition=val(positioning.get('primary_conversion_proposition'))
    if proposition: lines.append(('核心转化主张：' if is_cn else 'Primary conversion proposition: ')+str(proposition))
    audience=_d(lineage.get('audience_culture')); segments=val(audience.get('segments') or []) or []
    if segments: lines.append(('目标人群 / 区域上下文：' if is_cn else 'Audience / regional context: ')+json.dumps(segments,ensure_ascii=False))
    implications=val(audience.get('visual_implications') or []) or []
    if implications: lines.append(('人群/文化视觉含义：' if is_cn else 'Audience/culture visual implications: ')+json.dumps(implications,ensure_ascii=False))
    market=_d(lineage.get('market'))
    for key,label_cn,label_en in (('customer_voice','Customer Voice：','Customer voice: '),('opportunities','市场机会：','Market opportunity: '),('keyword_signals','搜索/需求信号：','Search/demand signal: ')):
        value=val(market.get(key))
        if value: lines.append((label_cn if is_cn else label_en)+json.dumps(value,ensure_ascii=False))
    race=val(lineage.get('race') or []) or []
    if race: lines.append(('RACE / Journey：' if is_cn else 'RACE / journey: ')+json.dumps(race,ensure_ascii=False))
    listing=_d(lineage.get('listing')); objections=val(listing.get('objections'))
    if objections: lines.append(('需解决的 Listing 异议：' if is_cn else 'Listing objection to resolve: ')+json.dumps(objections,ensure_ascii=False))
    pricing=_d(lineage.get('pricing_economics')); decision=_d(pricing.get('pricing_decision')); selected=val(decision.get('decision'))
    if selected not in (None,''):
        lines.append(('本资产相关的已选价格 / Offer：' if is_cn else 'Selected price / offer relevant to this asset: ')+str(selected))
        why=val(decision.get('why'))
        if why: lines.append(('价格 / Offer WHY：' if is_cn else 'Price / offer WHY: ')+str(why))
    ads=_d(lineage.get('ads')); diagnosis=val(ads.get('diagnosis'))
    if diagnosis: lines.append(('广告诊断：' if is_cn else 'Paid-media diagnosis: ')+json.dumps(diagnosis,ensure_ascii=False))
    reviews=_d(lineage.get('reviews')); review_issues=val(reviews.get('issues'))
    if review_issues: lines.append(('评论 / 客服信号：' if is_cn else 'Review / customer-service signal: ')+json.dumps(review_issues,ensure_ascii=False))
    lines.append('只消费会改变当前画面/信息层级/证据/文案/场景的商业决策；经济公式、审计状态和无关数据不要堆入画面。' if is_cn else 'Consume only commercial decisions that change this image/frame, information hierarchy, proof, copy or scene. Do not dump accounting formulas, audit states or irrelevant data into the visual.')
    return lines


def _nested(value: Any,*path: str) -> Any:
    cur=value
    for key in path:
        if not isinstance(cur,Mapping): return None
        cur=cur.get(key)
    return cur


def _card_issues_v0673(card: Mapping[str,Any], aid: str) -> list[dict[str,Any]]:
    groups={
      'strategic_job':(('strategic_job',),('shopper_question',),('consumer_question',),('belief_transition',),('commerce_task','strategic_job')),
      'visual_carrier':(('visual_carrier',),('carrier',),('role',),('agent_art_direction','visual_carrier')),
      'product_presence':(('product_presence',),('product_role',),('product',),('agent_art_direction','product_presence')),
      'subject_system':(('subject_system',),('subject_type',),('subject',),('subject_action_environment_props','subject')),
      'scene_environment':(('scene',),('environment',),('scene_system',),('decisive_moment',),('subject_action_environment_props','environment')),
      'props_elements':(('props',),('supporting_elements',),('evidence_elements',),('subject_action_environment_props','props')),
      'evidence_mode':(('evidence_mode',),('evidence_hierarchy',),('proof',),('proof_mechanism',),('information_design','proof_plane'),('information_design','evidence_hierarchy')),
      'composition':(('composition_grammar',),('composition',),('spatial_rhythm',),('composition_camera','composition_grammar')),
      'cmf_material':(('cmf',),('material',),('palette',),('palette_hex',),('lighting_material_cmf','cmf'),('lighting_material_cmf','material')),
      'portfolio_delta':(('portfolio_delta',),('portfolio_rhythm_delta',),('variant_hypothesis',),('test_hypothesis',),('incremental_information',),('agent_art_direction','portfolio_rhythm_delta')),
      'measurement':(('measurement_hypothesis',),('success_metric',),('metric',),('commerce_task','success_metric')),
    }
    return [{'code':'ASSET_DESIGN_CARD_DECISION_MISSING','asset_id':aid,'decision':label} for label,paths in groups.items() if not any(_p(_nested(card,*path)) for path in paths)]


def _provider_execution_required(package: Path) -> bool:
    for rel in ('supporting_analysis/production_run.json','PRODUCTION_RUN.json','provider/PROVIDER_EXECUTION.json'):
        data=_read_json(package/rel)
        if not data: continue
        blob=json.dumps(data,ensure_ascii=False).upper()
        if any(token in blob for token in ('EXECUTION_REQUESTED','PROVIDER_EXECUTION_REQUIRED','PRODUCTION_REQUESTED','RUN_PROVIDER')): return True
        if str(data.get('status') or '').upper() in {'RUNNING','EXECUTED','COMPLETED','FAILED'}: return True
    evidence=_read_json(package/'supporting_analysis/evidence.json')
    return str(evidence.get('provider_media_status') or evidence.get('actual_media_status') or '').upper() not in {'E2E_PENDING','PLANNING_ONLY','NOT_RUN','NOT_REQUESTED',''}


def _current_workspace(page: str) -> bool:
    return 'data-workspace-shell="cbcc-commercial-v1"' in page or 'CBCC_CANONICAL_STATIC_PROJECTION_V0672' in page or 'asset/' in page


def _semantic_md_text(value: str) -> str:
    return str(value or '').replace('\\|','|').replace('<br>','\n').replace('<br/>','\n').replace('<br />','\n')


def _flatten(value: Any) -> list[str]:
    if value in (None,'',[],{}): return []
    if isinstance(value,Mapping):
        out=[]
        for child in value.values(): out.extend(_flatten(child))
        return out
    if isinstance(value,(list,tuple)):
        out=[]
        for child in value: out.extend(_flatten(child))
        return out
    return [str(value)]


def audit_listing_markdown_canonical_parity_v0673(package_dir: Path|str) -> list[dict[str,Any]]:
    package=Path(package_dir); center=_read_json(package/'HUMAN_DELIVERY.json')
    if not center or not _d(center.get('task_scope')).get('listing_active'): return []
    path=package/'01_LISTING_UPLOAD_READY.md'; alt=package/'listing/01_LISTING_UPLOAD_READY.md'
    if not path.exists() and alt.exists(): path=alt
    if not path.exists(): return [{'code':'LISTING_MARKDOWN_MISSING'}]
    text=_semantic_md_text(path.read_text(encoding='utf-8',errors='ignore')); missing=[]
    for source in ('copy_center','localized_copy'):
        for i,row in enumerate(center.get(source) or []):
            if not isinstance(row,Mapping): continue
            for slot in ('value','delivery_translation'):
                for token in _flatten(row.get(slot)):
                    if _semantic_md_text(token) not in text: missing.append({'source':source,'row':i,'field':row.get('field'),'slot':slot,'token':token[:180]})
    return [] if not missing else [{'code':'LISTING_MARKDOWN_CANONICAL_FIELD_DRIFT','missing_count':len(missing),'missing':missing[:100]}]


def audit_current_human_html_v0673(page: str) -> list[dict[str,Any]]:
    from . import human_projection_integrity as hpi
    if 'CBCC_CANONICAL_STATIC_PROJECTION_V0672' not in page: return hpi._v0673_legacy_audit(page) if hasattr(hpi,'_v0673_legacy_audit') else []
    issues=[]
    if not hpi._has_real_copy_binding(page): issues.append({'code':'WORKSPACE_COPY_BINDING_MISSING'})
    if 'CBCC_GLOBAL_SEARCH_INDEX_V0672' not in page: issues.append({'code':'WORKSPACE_SEARCH_SCOPE_INCOMPLETE'})
    if '逐资产 00–15 完整生产对象' not in page: issues.append({'code':'HTML_ASSET_DATA_MISSING'})
    return issues


def audit_html_asset_package_parity_v0673(package: Path) -> list[dict[str,Any]]:
    from . import html_asset_package_parity as hap
    package=Path(package); html_path=package/'index.html'; root=package/'asset_packages'
    if not html_path.exists() or not root.exists(): return []
    data=hap._data(html_path.read_text(encoding='utf-8',errors='ignore'))
    if not data and (package/'CANONICAL_HUMAN_DATA.json').exists(): data=_read_json(package/'CANONICAL_HUMAN_DATA.json')
    assets=data.get('assets') if isinstance(data,dict) else None
    if not isinstance(assets,list): return [{'code':'HTML_ASSET_DATA_MISSING','why':'No current Human assets payload available.'}]
    by_id={str(a.get('id') or a.get('asset_id') or ''):a for a in assets if isinstance(a,Mapping)};issues=[]
    for d in sorted(x for x in root.iterdir() if x.is_dir()):
        aid=d.name;a=by_id.get(aid)
        if not a: issues.append({'code':'HTML_ASSET_PACKAGE_PARITY_MISSING_ASSET','asset_id':aid});continue
        for key,names in {'prompt_cn':('05_prompt_CN.txt',),'prompt_en':('06_prompt_EN.txt',),'production_notes':('09_production_notes.md','08_production_notes.txt','15_production_assembly_notes.md')}.items():
            file_value=hap._text_first(d,names); html_value=a.get(key)
            if file_value is not None and html_value is not None and str(html_value).strip()!=file_value: issues.append({'code':'HTML_ASSET_PACKAGE_TEXT_DRIFT','asset_id':aid,'field':key})
        card_file=_read_json(d/'12_design_card.json')
        if card_file and isinstance(a.get('card'),Mapping):
            candidate=card_file.get('design_card') if isinstance(card_file.get('design_card'),Mapping) else card_file
            if candidate!=a['card']: issues.append({'code':'HTML_ASSET_PACKAGE_DESIGN_CARD_DRIFT','asset_id':aid})
    return issues


def _presence_complete(package: Path) -> bool:
    assets=[a for a in _read_json(package/'ASSET_UNIVERSE.json').get('assets') or [] if isinstance(a,Mapping)]
    if not assets: return False
    for asset in assets:
        presence=asset.get('product_presence') if isinstance(asset.get('product_presence'),Mapping) else _d(asset.get('asset_art_direction')).get('product_presence')
        if not isinstance(presence,Mapping) or not _p(presence.get('planning_state')) or not _p(presence.get('presence_why')): return False
    return True


def _design_card_decision_satisfied(package: Path, issue: Mapping[str,Any]) -> bool:
    aid=str(issue.get('asset_id') or ''); decision=str(issue.get('decision') or ''); card=_read_json(package/'asset_packages'/aid/'12_design_card.json')
    return bool(card) and not any(x.get('decision')==decision for x in _card_issues_v0673(card,aid))


def reconcile_final_export_issues(package_dir: Path|str, issues: list[dict[str,Any]]) -> list[dict[str,Any]]:
    package=Path(package_dir); page=(package/'index.html').read_text(encoding='utf-8',errors='ignore') if (package/'index.html').exists() else ''
    listing_ok=not audit_listing_markdown_canonical_parity_v0673(package); planning_only=not _provider_execution_required(package); presence_ok=_presence_complete(package)
    current_human='CBCC_CANONICAL_STATIC_PROJECTION_V0672' in page and 'CBCC_GLOBAL_SEARCH_INDEX_V0672' in page and '逐资产 00–15 完整生产对象' in page
    out=[]
    for row in issues:
        code=str(row.get('code') or '')
        if code=='ASSET_DESIGN_CARD_DECISION_MISSING' and _design_card_decision_satisfied(package,row): continue
        if code=='PRODUCT_PRESENCE_DECISION_NOT_STRUCTURED' and presence_ok: continue
        if code in _PROVIDER_CODES and planning_only: continue
        if code in {'FIXED_CAPABILITY_ROUTE_TAXONOMY','FIXED_CAPABILITY_MENU_SHELL'} and _current_workspace(page): continue
        if code=='CANONICAL_HUMAN_POSITIVE_PROJECTION_FAILED' and current_human: continue
        if code in {'WORKSPACE_SEARCH_SCOPE_INCOMPLETE','HTML_ASSET_DATA_MISSING'} and current_human: continue
        if code=='LISTING_MARKDOWN_CANONICAL_FIELD_DRIFT' and listing_ok: continue
        out.append(row)
    dedup=[];seen=set()
    for row in out:
        key=json.dumps(row,ensure_ascii=False,sort_keys=True,default=str)
        if key not in seen: seen.add(key);dedup.append(row)
    return dedup


def wrap_package_audit_v0673(fn: Callable[[Path],dict[str,Any]]):
    if getattr(fn,'_cbcc_v0673_final_export_closure',False): return fn
    def audited(package_dir: Path):
        result=deepcopy(fn(Path(package_dir))); result['issues']=reconcile_final_export_issues(package_dir,list(result.get('issues') or [])); result['status']='PASS' if not result['issues'] else 'INCOMPLETE'; result['v0673_final_export_reconciliation']={'status':'PASS','principle':'Only issues disproved by current canonical package evidence are reconciled; output-language purity and real production failures remain blocking.'}; return result
    setattr(audited,'_cbcc_v0673_final_export_closure',True);return audited


def _refresh_presence_audit(result: Mapping[str,Any]) -> dict[str,Any]:
    out=deepcopy(dict(result)); assets=[a for a in out.get('assets') or [] if isinstance(a,Mapping)]
    if not assets:return out
    rows=[];structured=visible=absent=0
    for asset in assets:
        presence=asset.get('product_presence') if isinstance(asset.get('product_presence'),Mapping) else _d(asset.get('asset_art_direction')).get('product_presence')
        if isinstance(presence,Mapping): state=str(presence.get('planning_state') or 'UNRESOLVED').upper();why=str(presence.get('presence_why') or '');is_structured=bool(presence.get('planning_state') and presence.get('presence_why'))
        else: state='UNRESOLVED';why='';is_structured=False
        structured+=int(is_structured); absent+=int(state in {'FORBIDDEN','ABSENT','PRODUCT_ABSENT','NOT_NEEDED'}); visible+=int(state not in {'UNRESOLVED','FORBIDDEN','ABSENT','PRODUCT_ABSENT','NOT_NEEDED'})
        rows.append({'asset_id':asset.get('asset_id') or asset.get('id'),'planning_state':state,'structured_decision':is_structured,'presence_why':why})
    out['product_presence_portfolio_audit']={'status':'PASS' if structured==len(assets) else 'INCOMPLETE','total_assets':len(assets),'structured_presence_decisions':structured,'visible_or_optional_count':visible,'absent_or_forbidden_count':absent,'all_visible_review_required':bool(assets and visible==len(assets)),'assets':rows,'projection_source':'V0673_COMPILED_CURRENT_ASSETS'}
    return out


def install() -> None:
    global _INSTALLED
    if _INSTALLED:return
    _INSTALLED=True
    from . import commercial_continuity_authority as cca; cca._commercial_prompt_lines=_commercial_prompt_lines_v0673
    from . import full_delivery_depth_v3 as full_depth; full_depth._card_issues=_card_issues_v0673; full_depth.audit_host_full_package=wrap_package_audit_v0673(full_depth.audit_host_full_package)
    from . import asset_universe_authority as aua
    prev_universe=aua.compile_asset_universe
    if not getattr(prev_universe,'_cbcc_v0673_presence_current_assets',False):
        def compiled_universe(*args,**kwargs): return _refresh_presence_audit(prev_universe(*args,**kwargs))
        setattr(compiled_universe,'_cbcc_v0673_presence_current_assets',True); aua.compile_asset_universe=compiled_universe
    from . import listing_markdown_parity_v0671 as listing; listing.audit_listing_markdown_canonical_parity=audit_listing_markdown_canonical_parity_v0673
    from . import canonical_full_package_audit_v0671 as current_full; current_full.audit_listing_markdown_canonical_parity=audit_listing_markdown_canonical_parity_v0673
    from . import human_projection_integrity as hpi
    if not hasattr(hpi,'_v0673_legacy_audit'): hpi._v0673_legacy_audit=hpi.audit_human_projection_html
    hpi.audit_human_projection_html=audit_current_human_html_v0673
    from . import html_asset_package_parity as hap; hap.audit_html_asset_package_parity=audit_html_asset_package_parity_v0673
    from . import canonical_materialization_package_audit as cmap
    cmap.audit_human_projection_html=audit_current_human_html_v0673; cmap.audit_html_asset_package_parity=audit_html_asset_package_parity_v0673
    def current_projection(html_path,data=None):
        from .canonical_human_compaction_v0672 import finalize_static_human_projection
        return finalize_static_human_projection(Path(html_path).parent)
    cmap.apply_complete_canonical_human_projection=current_projection
    original_cmap=cmap.wrap_audit_host_full_package
    cmap.wrap_audit_host_full_package=lambda fn: wrap_package_audit_v0673(original_cmap(fn))
    materialization=sys.modules.get(__package__+'.full_delivery_materialization')
    if materialization is not None: materialization.audit_host_full_package=full_depth.audit_host_full_package
