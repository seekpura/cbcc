from __future__ import annotations
from pathlib import Path
import json, re
from typing import Any, Callable

QUESTION_LIMIT=10
P0_AREAS={'efficacy_claims','ingredients_formula','certifications','price','sales_volume','regulated_category'}
CULTURE_CHECK_FIELDS={'script_check','casting_check','wardrobe_grooming_check','color_check','cta_check'}
FAMILY_KEYS={'gallery_identity','benefit_proof_detail','scenario_human_context','howto_objection_comparison','rich_pdp_source','paid_media','social_seeding','creator_affiliate','video_live','store_campaign','lifecycle','test_rotation'}

def _p(v:Any)->bool:return v not in (None,'',[],{})
def _d(v:Any)->dict[str,Any]:return v if isinstance(v,dict) else {}
def _l(v:Any)->list[Any]:return [] if v in (None,'',{}) else (v if isinstance(v,list) else [v])
def _sig(row:dict[str,Any])->str:return json.dumps(row,ensure_ascii=False,sort_keys=True,default=str)
def _dedupe(rows:list[dict[str,Any]])->list[dict[str,Any]]:
    out=[];seen=set()
    for row in rows:
        key=_sig(row)
        if key not in seen:seen.add(key);out.append(row)
    return out

def _pricing_recommendation_present(ps:dict[str,Any])->bool:
    for key in ('recommended_test','recommended_price','price_recommendation','pricing_decision','recommended_range'):
        v=ps.get(key)
        if not _p(v):continue
        text=json.dumps(v,ensure_ascii=False).upper() if isinstance(v,(dict,list)) else str(v).upper()
        if any(t in text for t in ('RECOMMEND','建议','测试价','PRICE','RM','$','AED','USD')):return True
    return False

def wrap_audit_full_strategy_depth_v3(fn:Callable[...,dict[str,Any]]):
    def audited(strategy:dict[str,Any],base_result=None):
        result=fn(strategy,base_result)
        if str(result.get('mode') or '').upper()!='FULL':return result
        issues=list(result.get('issues') or []); sections=_d(strategy.get('sections')); info=_d(sections.get('01_information_completeness_assumptions_decisions')); pending=_l(info.get('pending_confirmations'))
        if len(pending)>QUESTION_LIMIT:issues.append({'code':'FULL_PENDING_CONFIRMATION_LIMIT_EXCEEDED','count':len(pending),'limit':QUESTION_LIMIT})
        if info.get('question_limit') not in (None,QUESTION_LIMIT):issues.append({'code':'FULL_PENDING_CONFIRMATION_LIMIT_INVALID','value':info.get('question_limit'),'expected':QUESTION_LIMIT})
        if info.get('continue_under_assumptions') is not True:issues.append({'code':'FULL_CONTINUE_UNDER_ASSUMPTIONS_MISSING'})
        for i,row in enumerate(_l(info.get('decision_log'))):
            if not isinstance(row,dict):continue
            context=_d(row.get('context_why')); missing=[k for k in ('platform','region','audience','race_ethnicity_culture') if not _p(context.get(k))]
            if missing:issues.append({'code':'FULL_DECISION_CONTEXT_WHY_MISSING','row':i,'fields':missing})
            else:
                shallow=[k for k in ('platform','region','audience','race_ethnicity_culture') if not _p(_d(context.get(k)).get('why')) or not _p(_d(context.get(k)).get('status'))]
                if shallow:issues.append({'code':'FULL_DECISION_CONTEXT_WHY_SHALLOW','row':i,'fields':shallow})
        vis=_d(sections.get('05_visual_photography_strategy')); people=str(vis.get('people_applicability') or '').upper() in {'PERSON_PRESENT','PEOPLE_PRESENT','HUMAN_PRESENT','APPLICABLE_P0'}
        if people:
            inc=_d(vis.get('inclusive_photography'))
            for field in ('deep_skin_exposure_compensation_plan','reflector_bounce_diffusion'):
                if not _p(inc.get(field)):issues.append({'code':'FULL_INCLUSIVE_PHOTOGRAPHY_DIMENSION_MISSING','section':'05_visual_photography_strategy','dimension':field})
        for i,row in enumerate(_l(sections.get('08_culture_adaptation_checklist'))):
            if not isinstance(row,dict):continue
            missing=sorted(f for f in CULTURE_CHECK_FIELDS if not _p(row.get(f)))
            if missing:issues.append({'code':'FULL_CULTURE_EXECUTION_CHECK_COLUMNS_MISSING','section':'08_culture_adaptation_checklist','row':i,'fields':missing})
        last=_d(sections.get('09_risk_measurement_priority_next_steps')); p0=[x for x in _l(last.get('p0_compliance_claim_checklist')) if isinstance(x,dict)]
        if not p0:issues.append({'code':'FULL_P0_COMPLIANCE_CHECKLIST_MISSING','section':'09_risk_measurement_priority_next_steps'})
        else:
            areas={str(x.get('check_area') or '') for x in p0}; missing_areas=sorted(P0_AREAS-areas)
            if missing_areas:issues.append({'code':'FULL_P0_COMPLIANCE_CHECK_AREAS_MISSING','areas':missing_areas})
            for i,row in enumerate(p0):
                missing=[k for k in ('check_area','priority','status','action','why') if not _p(row.get(k))]
                if missing:issues.append({'code':'FULL_P0_COMPLIANCE_CHECK_ROW_SHALLOW','row':i,'fields':missing})
                if row.get('priority')!='P0':issues.append({'code':'FULL_P0_COMPLIANCE_PRIORITY_INVALID','row':i,'value':row.get('priority')})
        core=_d(sections.get('04_marketing_core_strategy')); ps=_d(core.get('product_strategy')); econ=str(ps.get('economics_status') or '').upper()
        if econ in {'','MISSING_INPUT','INSUFFICIENT_DATA','NOT_SUPPLIED','UNKNOWN'} and _pricing_recommendation_present(ps):issues.append({'code':'FULL_PRICING_RECOMMENDATION_AHEAD_OF_ECONOMICS','economics_status':econ or 'UNKNOWN','rule':'市场价格带证据与自身Pricing Decision必须分离；缺关键单位经济输入时保持UNKNOWN/MISSING_INPUT。'})
        result['issues']=_dedupe(issues); result['status']='PASS' if not result['issues'] else 'INCOMPLETE'; result['verbatim_long_requirement_audit']={'question_limit':QUESTION_LIMIT,'required_p0_areas':sorted(P0_AREAS),'required_culture_check_fields':sorted(CULTURE_CHECK_FIELDS)}
        return result
    return audited

def _read_json(path:Path)->dict[str,Any]:
    try:
        v=json.loads(path.read_text(encoding='utf-8')); return v if isinstance(v,dict) else {}
    except Exception:return {}
def _has_production_ready_assets(package:Path)->bool:
    root=package/'asset_packages'; return root.exists() and any((d/'05_prompt_CN.txt').exists() or (d/'06_prompt_EN.txt').exists() for d in root.iterdir() if d.is_dir())
def _prompt_route_contradictions(asset_dir:Path)->list[dict[str,Any]]:
    issues=[];card=_read_json(asset_dir/'12_design_card.json');prompt=''
    for name in ('05_prompt_CN.txt','06_prompt_EN.txt'):
        p=asset_dir/name
        if p.exists():prompt+=p.read_text(encoding='utf-8',errors='ignore')+'\n'
    if not prompt:return issues
    copy_route=str(_d(card.get('information_design')).get('copy_render_route') or '').upper(); locked=_d(card.get('information_design')).get('locked_visible_copy')
    no_text=bool(re.search(r'不生成[^。\n]{0,40}(?:文字|数字)|不要生成[^。\n]{0,40}(?:文字|数字)|do not generate[^.\n]{0,50}(?:text|numbers)',prompt,re.I)); explicit_post=copy_route in {'POST_COMPOSITE','NO_VISIBLE_COPY','DETERMINISTIC_COMPOSITION_AFTER_RENDER'}
    if _p(locked) and no_text and not explicit_post:issues.append({'code':'PROMPT_COPY_ROUTE_CONTRADICTION','asset_id':asset_dir.name,'copy_render_route':copy_route or 'UNRESOLVED'})
    presence=_d(card.get('product_presence'));state=str(presence.get('planning_state') or '').upper();fidelity=str(_d(card.get('product_identity')).get('product_fidelity') or '').upper();no_product=bool(re.search(r'不生成[^。\n]{0,40}(?:商品|产品)|不要生成[^。\n]{0,40}(?:商品|产品)|do not generate[^.\n]{0,50}(?:product)',prompt,re.I));visible=state in {'HERO_REQUIRED','REQUIRED','SUPPORTING','DETAIL_ONLY','OPTIONAL'};pixel=fidelity in {'EXACT_PIXEL_COMPOSITE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}
    if visible and no_product and not pixel:issues.append({'code':'PROMPT_PRODUCT_ROUTE_CONTRADICTION','asset_id':asset_dir.name,'product_presence':state,'product_fidelity':fidelity})
    return issues

def _project_shortcut_audit(package: Path) -> list[dict[str, Any]]:
    """Audit Host-authored FULL project shortcuts such as the real 2026-10-30 K01 package."""
    issues: list[dict[str, Any]] = []
    project_path = package / 'data' / 'project.json'
    project = _read_json(project_path) if project_path.exists() else {}
    assets = [x for x in _l(project.get('assets')) if isinstance(x, dict)]
    shortcut_root = package / 'assets'
    mature_root = package / 'asset_packages'

    if shortcut_root.exists() and not mature_root.exists():
        incomplete = []
        required = {'00_asset_manifest.yaml','01_strategy.md','02_visual_spec.md','03_photography_contract.json','04_layout_contract.json','08_copy.md','09_production_notes.md','10_source_trace.md','11_strategy_authority_trace.json','12_design_card.json','14_visible_copy_block.json','15_production_assembly_notes.json'}
        for d in sorted(x for x in shortcut_root.iterdir() if x.is_dir()):
            files = {x.name for x in d.iterdir() if x.is_file()}
            missing = sorted(required - files)
            if missing:
                incomplete.append({'asset_id': d.name, 'file_count': len(files), 'missing_count': len(missing)})
        if incomplete:
            issues.append({'code':'MATURE_ASSET_PACKAGE_INCOMPLETE','affected':len(incomplete),'examples':incomplete[:3]})

    if assets:
        missing_art = [str(a.get('id') or a.get('asset_id') or '') for a in assets if not isinstance(a.get('asset_art_direction'), dict) or not a.get('asset_art_direction')]
        if missing_art:
            issues.append({'code':'STRUCTURED_ASSET_ART_DIRECTION_MISSING','affected':len(missing_art),'assets':missing_art})

        structured = 0; visible = 0; absent = 0
        for a in assets:
            presence = a.get('product_presence')
            if isinstance(presence, dict) and presence.get('planning_state') and presence.get('presence_why'):
                structured += 1
                state = str(presence.get('planning_state') or '').upper()
            else:
                state = str(a.get('presence') or presence or '').upper()
            if state in {'FORBIDDEN','ABSENT','PRODUCT_ABSENT','NOT_NEEDED'}:
                absent += 1
            elif state:
                visible += 1
        if structured < len(assets):
            issues.append({'code':'PRODUCT_PRESENCE_DECISION_NOT_STRUCTURED','structured':structured,'total':len(assets)})
        if visible == len(assets) and assets:
            issues.append({'code':'PRODUCT_EVERYWHERE_PORTFOLIO_REVIEW_REQUIRED','total':len(assets),'rule':'all-visible is only valid when every asset has an independent structured presence_why and the portfolio explains why absent/detail/evidence-only carriers are weaker'})

        if not any(k in project for k in ('asset_opportunity_universe','asset_universe_audit','family_coverage','opportunity_sweep')) and not (package/'ASSET_UNIVERSE.json').exists():
            issues.append({'code':'ASSET_OPPORTUNITY_SWEEP_MISSING'})

    visual = _d(project.get('visual'))
    fidelity = str(visual.get('fidelity') or '')
    if re.search(r'后期合成|只负责背景|exact composite|post.?composite|real source crop', fidelity, re.I):
        issues.append({'code':'GLOBAL_POST_COMPOSITE_POLICY','value':fidelity})

    prompt_root = shortcut_root if shortcut_root.exists() else mature_root
    asset_prompts: dict[str,str] = {}
    if prompt_root.exists():
        for d in sorted(x for x in prompt_root.iterdir() if x.is_dir()):
            text=''
            for name in ('05_prompt_CN.txt','06_prompt_EN.txt'):
                q=d/name
                if q.exists(): text += q.read_text(encoding='utf-8',errors='ignore')+'\n'
            if text: asset_prompts[d.name]=text
    no_text=[]; no_product=[]
    for aid,text in asset_prompts.items():
        if re.search(r'不生成[^。\n]{0,50}(?:文字|数字)|不要生成[^。\n]{0,50}(?:文字|数字)|do not generate[^.\n]{0,70}(?:text|numbers)',text,re.I): no_text.append(aid)
        if re.search(r'不生成[^。\n]{0,50}(?:商品|产品)|不要生成[^。\n]{0,50}(?:商品|产品)|do not generate[^.\n]{0,70}(?:product)',text,re.I): no_product.append(aid)
    if asset_prompts and len(no_text) >= max(3,int(len(asset_prompts)*0.6)):
        issues.append({'code':'GLOBAL_NO_VISIBLE_COPY_PATTERN','affected':len(no_text),'total':len(asset_prompts),'assets':no_text})
    if asset_prompts and len(no_product) >= max(3,int(len(asset_prompts)*0.4)):
        issues.append({'code':'GLOBAL_NO_PRODUCT_GENERATION_PATTERN','affected':len(no_product),'total':len(asset_prompts),'assets':no_product})

    files=[x for x in package.rglob('*') if x.is_file()]
    media_ext={'.png','.jpg','.jpeg','.webp','.mp4','.mov','.webm'}
    generated=[x for x in files if x.suffix.casefold() in media_ext and not any(part.casefold() in {'source','sources','input','inputs','reference','references'} for part in x.parts)]
    if assets and not generated: issues.append({'code':'ACTUAL_GENERATED_OUTPUT_MISSING'})
    if assets and not any('provider' in x.name.casefold() and 'result' in x.name.casefold() for x in files): issues.append({'code':'PROVIDER_RESULT_MISSING'})
    if assets and not any('review' in x.name.casefold() for x in files): issues.append({'code':'ACTUAL_OUTPUT_REVIEW_MISSING'})
    if assets and not any('revision' in x.name.casefold() for x in files): issues.append({'code':'LOCAL_REVISION_LINEAGE_MISSING'})

    if project and not any(k in project for k in ('information_completeness','assumptions','decision_log','unknowns')):
        issues.append({'code':'INFORMATION_ASSUMPTION_DECISION_LOG_MISSING'})
    pricing=_d(project.get('pricing'))
    if pricing and re.search(r'MISSING_INPUT|UNKNOWN',str(pricing.get('economics') or ''),re.I) and _p(pricing.get('recommended_test')):
        issues.append({'code':'PRICING_RECOMMENDATION_AHEAD_OF_ECONOMICS','recommended_test':pricing.get('recommended_test')})
    return issues

def _production_object_audit(mature: Path, active_ids: list[str]) -> list[dict[str, Any]]:
    issues=[]
    required = ('05_prompt_CN.txt','06_prompt_EN.txt','12_design_card.json','14_visible_copy_block.json','15_production_assembly_notes.json')
    for aid in active_ids:
        d=mature/aid
        if not d.exists():
            continue
        missing=[name for name in required if not (d/name).exists()]
        if missing:
            issues.append({'code':'PRODUCTION_OBJECTS_INCOMPLETE','asset_id':aid,'missing':missing})
    return issues

def wrap_audit_host_full_package(fn:Callable[[Path],dict[str,Any]]):
    def audited(package_dir:Path):
        package=Path(package_dir);result=fn(package);issues=list(result.get('issues') or []);issues.extend(_project_shortcut_audit(package));shortcut=package/'assets';mature=package/'asset_packages'
        if shortcut.exists() and not mature.exists():issues.append({'code':'HOST_SHORTCUT_ASSET_PACKAGE_FORBIDDEN','path':'assets/','expected':'asset_packages/'})
        universe=_read_json(package/'ASSET_UNIVERSE.json');active=[x for x in _l(universe.get('assets')) if isinstance(x,dict) and str(x.get('deployment_state') or x.get('pool') or '').upper() not in {'ARCHIVE','NOT_NEEDED'}]
        if active and not mature.exists():issues.append({'code':'MATURE_ASSET_PACKAGES_REQUIRED','active_asset_count':len(active)})
        if mature.exists(): issues.extend(_production_object_audit(mature,[str(x.get('asset_id') or x.get('id') or '') for x in active]))
        family=[x for x in _l(universe.get('opportunity_family_audit')) if isinstance(x,dict)]
        if active and not family:issues.append({'code':'ASSET_OPPORTUNITY_FAMILY_AUDIT_MISSING'})
        elif family:
            seen={str(x.get('family_key') or '') for x in family};missing=sorted(FAMILY_KEYS-seen)
            if missing:issues.append({'code':'ASSET_OPPORTUNITY_FAMILY_AUDIT_INCOMPLETE','missing_family_keys':missing})
            for row in family:
                if str(row.get('status') or '').upper() not in {'COVERED','NOT_NEEDED','TO_VERIFY','MISSING_INPUT'} or not _p(row.get('why')):issues.append({'code':'ASSET_OPPORTUNITY_FAMILY_DECISION_INVALID','family_key':row.get('family_key')})
        pa=_d(universe.get('product_presence_portfolio_audit'))
        if active and not pa:issues.append({'code':'PRODUCT_PRESENCE_PORTFOLIO_AUDIT_MISSING'})
        elif pa and pa.get('structured_presence_decisions')!=pa.get('total_assets'):issues.append({'code':'PRODUCT_PRESENCE_DECISION_NOT_STRUCTURED','structured':pa.get('structured_presence_decisions'),'total':pa.get('total_assets')})
        if mature.exists():
            try:
                from .asset_compiler import validate_asset_packages
                validation=validate_asset_packages(mature)
                if not validation.get('pass'):issues.append({'code':'MATURE_ASSET_PACKAGE_VALIDATION_FAILED','errors':validation.get('errors') or []})
            except Exception as exc:issues.append({'code':'MATURE_ASSET_PACKAGE_VALIDATION_ERROR','error':str(exc)})
            for d in sorted(x for x in mature.iterdir() if x.is_dir()):
                manifest=d/'00_asset_manifest.yaml'
                if manifest.exists() and not re.search(r'(?m)^asset_art_direction:\s*(?!\{\}\s*$|null\s*$)',manifest.read_text(encoding='utf-8',errors='ignore')):issues.append({'code':'STRUCTURED_ASSET_ART_DIRECTION_NOT_MATERIALIZED','asset_id':d.name})
                issues.extend(_prompt_route_contradictions(d))
        if _has_production_ready_assets(package):
            files=[p for p in package.rglob('*') if p.is_file()]
            if not any('provider' in p.name.casefold() and 'result' in p.name.casefold() for p in files):issues.append({'code':'FULL_PROVIDER_RESULT_MISSING'})
            if not any('review' in p.name.casefold() for p in files):issues.append({'code':'FULL_ACTUAL_OUTPUT_REVIEW_MISSING'})
            if not any('revision' in p.name.casefold() for p in files):issues.append({'code':'FULL_LOCAL_REVISION_LINEAGE_MISSING'})
            media_ext={'.png','.jpg','.jpeg','.webp','.mp4','.mov','.webm'};generated=[p for p in files if p.suffix.casefold() in media_ext and not any(part.casefold() in {'sources','source','input','inputs','references'} for part in p.parts)]
            if not generated:issues.append({'code':'FULL_ACTUAL_GENERATED_OUTPUT_MISSING'})
        html=package/'index.html'
        if html.exists():
            page=html.read_text(encoding='utf-8',errors='ignore');fixed=['产品事实','马来市场','成交策略','上架文案','视觉系统','资产宇宙','合规证据','研究来源'];hits=[x for x in fixed if x in page]
            if len(hits)>=7:issues.append({'code':'FIXED_CAPABILITY_MENU_SHELL','labels':hits})
            routes=set(re.findall(r'data-route=["\']([^"\']+)',page,re.I)); capability={'product','market','strategy','listing','visual','assets','compliance','sources','research'}; taxonomy=sorted(r for r in routes if r.casefold() in capability)
            if len(taxonomy)>=6: issues.append({'code':'FIXED_CAPABILITY_ROUTE_TAXONOMY','routes':taxonomy})
            if mature.exists() and not any(t in page for t in ('完整逐资产 Art Direction','asset_art_direction','Art Direction')):issues.append({'code':'FULL_ART_DIRECTION_NOT_PROJECTED_TO_HTML'})
        result['issues']=_dedupe(issues);result['status']='PASS' if not result['issues'] else 'INCOMPLETE';result['verbatim_long_requirement_package_audit']=True;return result
    return audited
