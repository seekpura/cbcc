from __future__ import annotations
from collections import Counter
from pathlib import Path
import json,re

MARKET_CULTURE_DIMENSIONS=[
 'platform','market_region','subregion_geography','audience_segments','age','gender','income_spend','language',
 'race_ethnicity','religion','holiday_calendar','payment','logistics','local_regulation','platform_behavior',
 'search_demand','competition','price_band','intersectionality','stereotype_taboo']
DIMENSION_STATUSES={'EVIDENCED','ASSUMPTION','TO_VERIFY','MISSING_INPUT','NOT_RELEVANT'}
FRAMEWORK_RELATIONS=['RACE','STP','JTBD','AIDA','FABE','4P','FUNNEL']
INCLUSIVE_PERSON_FIELDS=['skin_tone_exposure','deep_skin_shadow_protection','reflector_bounce_diffusion','hair_texture','body_representation','disability_representation','age_representation','ai_bias_check']
CORE_HOST_FULL_FILES=[
 'index.html','00_PROJECT_HUB.md','HUMAN_DELIVERY.json','FULL_DELIVERY_DEPTH_AUDIT.json','HUMAN_LANGUAGE_AUDIT.json',
 'DELIVERY_LANGUAGE_MATRIX_AUDIT.json','PLATFORM_SCOPE.json','SOURCE_TRUTH_MEDIA_AUDIT.json','strategy/MASTER_STRATEGY_CN.md',
 'strategy/strategy_authority.json','strategy/STRATEGY_DECISION_INDEX.json','strategy/COMMERCE_DECISION_CONTEXT.json',
 'strategy/COMMERCIAL_CONTINUITY_AUDIT.json','supporting_analysis/product_truth.json','supporting_analysis/target_context.json',
 'supporting_analysis/culture_context.json','supporting_analysis/asset_architecture.json','supporting_analysis/seven_agent_synthesis.json',
 'ASSET_UNIVERSE.json','FULL_DELIVERY_OBJECT_MANIFEST.json']

def _p(v): return v not in (None,'',[],{})
def _d(v): return v if isinstance(v,dict) else {}
def _l(v): return [] if v in (None,'',{}) else (v if isinstance(v,list) else [v])
def _status(v): return str(v.get('status') if isinstance(v,dict) else v or '').upper()
def _issue(rows,code,section=None,**extra):
    x={'code':code}
    if section:x['section']=section
    x.update(extra);rows.append(x)
def _full(s):
    hp=_d(s.get('human_projection'));return str(hp.get('mode') or s.get('delivery_mode') or '').upper()=='FULL' or hp.get('fixed_human_section_quota') is True
def _reason(v): return isinstance(v,dict) and any(_p(v.get(k)) for k in ('why','evidence','evidence_refs','assumption','source_refs','basis'))
def _people(vis):
    if str(vis.get('people_applicability') or '').upper() in {'PERSON_PRESENT','PEOPLE_PRESENT','HUMAN_PRESENT','APPLICABLE_P0'}: return True
    for row in _l(vis.get('asset_parameter_reasoning')):
        if isinstance(row,dict):
            st=str(_d(row.get('subject_system')).get('subject_type') or row.get('subject_type') or '').upper()
            if st in {'PERSON','MULTI_SUBJECT'} or any(_p(row.get(k)) for k in ('human_context','people','hands','body_relation')): return True
    return False

def audit_full_strategy_depth_v3(strategy,base_result=None):
    if not _full(strategy): return {'status':'NOT_REQUIRED_FOR_TASK_SCOPED','mode':'TASK_SCOPED','issues':[],'warnings':[],'depth_contract':'FULL_COMMERCIAL_DEPTH_V3_HOST_RUNTIME_PARITY'}
    issues=list((base_result or {}).get('issues') or []);warnings=list((base_result or {}).get('warnings') or []);s=_d(strategy.get('sections'))
    info=_d(s.get('01_information_completeness_assumptions_decisions'))
    if not _p(info.get('assumptions')):_issue(issues,'FULL_ASSUMPTION_LOG_MISSING','01_information_completeness_assumptions_decisions')
    for i,r in enumerate(_l(info.get('decision_log'))):
        if not isinstance(r,dict):_issue(issues,'FULL_DECISION_LOG_INVALID','01_information_completeness_assumptions_decisions',row=i);continue
        miss=[k for k in ('what','why','evidence','tradeoff','execution','measurement') if not _p(r.get(k))]
        if miss:_issue(issues,'FULL_DECISION_LOG_DEPTH_MISSING','01_information_completeness_assumptions_decisions',row=i,fields=miss)
    val=_d(s.get('02_product_truth_value_ladder'))
    for i,r in enumerate(_l(val.get('product_facts'))+_l(val.get('claim_value_ladder'))):
        if not isinstance(r,dict):continue
        req=['real_selling_point','perceived_benefit','emotional_value','claim_boundary','evidence_grade']
        if not any(_p(r.get(k)) for k in ('source_refs','source_ids','evidence_refs')):req.append('source_refs')
        miss=[k for k in req if not _p(r.get(k))]
        if miss:_issue(issues,'FULL_PRODUCT_TRUTH_VALUE_DEPTH_MISSING','02_product_truth_value_ladder',row=i,fields=miss)
        if str(r.get('evidence_grade') or '').upper()=='C' and str(r.get('publication_status') or '').upper() in {'HARD','HARD_CLAIM','ACTIVE_HARD'}:_issue(issues,'FULL_C_LEVEL_HARD_CLAIM_FORBIDDEN','02_product_truth_value_ladder',row=i)
    cul=_d(s.get('03_platform_region_audience_culture_insight'));dims=_d(cul.get('dimension_status'))
    for k in MARKET_CULTURE_DIMENSIONS:
        if k not in dims:_issue(issues,'FULL_MARKET_CULTURE_DIMENSION_MISSING','03_platform_region_audience_culture_insight',dimension=k);continue
        if _status(dims[k]) not in DIMENSION_STATUSES:_issue(issues,'FULL_MARKET_CULTURE_DIMENSION_STATUS_INVALID','03_platform_region_audience_culture_insight',dimension=k,status=_status(dims[k]))
        if isinstance(dims[k],dict) and not _reason(dims[k]):_issue(issues,'FULL_MARKET_CULTURE_DIMENSION_BASIS_MISSING','03_platform_region_audience_culture_insight',dimension=k)
    inter=_l(cul.get('intersectionality_table'))
    if not inter:_issue(issues,'FULL_INTERSECTIONALITY_TABLE_MISSING','03_platform_region_audience_culture_insight')
    for i,r in enumerate(inter):
        if not isinstance(r,dict):continue
        miss=[k for k in ('dimensions','implication','evidence_or_assumption','stereotype_guard','execution') if not _p(r.get(k))]
        if miss:_issue(issues,'FULL_INTERSECTIONALITY_ROW_SHALLOW','03_platform_region_audience_culture_insight',row=i,fields=miss)
    req_loc={'language','holiday_calendar','payment','logistics','religion','local_regulation'};seen=set()
    for i,r in enumerate(_l(cul.get('adaptation_rows') or cul.get('localization_operating_table'))):
        if not isinstance(r,dict):continue
        dim=str(r.get('dimension') or r.get('adaptation_point') or '').lower();seen.add(dim)
        miss=[k for k in ('status','action','why') if not _p(r.get(k))]
        if not any(_p(r.get(k)) for k in ('evidence_or_assumption','evidence_refs')):miss.append('evidence_or_assumption')
        if miss:_issue(issues,'FULL_LOCALIZATION_OPERATING_ROW_SHALLOW','03_platform_region_audience_culture_insight',row=i,fields=miss)
    for k in sorted(req_loc-seen):
        _issue(issues,'FULL_LOCALIZATION_OPERATING_DIMENSION_MISSING','03_platform_region_audience_culture_insight',dimension=k,status=_status(dims.get(k)) or 'MISSING')
    rel=_d(_d(s.get('04_marketing_core_strategy')).get('framework_relationships'))
    for k in FRAMEWORK_RELATIONS:
        if not isinstance(rel.get(k),dict) or not _p(rel[k].get('role')) or not _p(rel[k].get('why')):_issue(issues,'FULL_FRAMEWORK_RELATION_MISSING','04_marketing_core_strategy',framework=k)
    vis=_d(s.get('05_visual_photography_strategy'));groups={'style_moodboard':('style_keywords','moodboard_direction','creative_direction','visual_thesis'),'composition':('composition','composition_rules'),'palette_contrast':('palette_hex','palette','color_system'),'lighting':('lighting_framework','lighting'),'lens_camera':('camera','lens','photography_execution'),'scene':('scene','scene_system','environment_system'),'props':('props','prop_system','supporting_elements'),'subject_casting':('subject_system','casting','people_applicability'),'platform_dimensions':('platform_dimensions',),'shot_list':('shot_list','asset_parameter_reasoning')}
    app=_d(vis.get('visual_execution_status'))
    for label,keys in groups.items():
        if any(_p(vis.get(k)) for k in keys):continue
        if _status(app.get(label)) in {'NOT_RELEVANT','NOT_APPLICABLE','TO_VERIFY','MISSING_INPUT'}:continue
        _issue(issues,'FULL_VISUAL_EXECUTION_DIMENSION_MISSING','05_visual_photography_strategy',dimension=label)
    if _people(vis):
        inc=_d(vis.get('inclusive_photography'))
        for k in INCLUSIVE_PERSON_FIELDS:
            if not _p(inc.get(k)):_issue(issues,'FULL_INCLUSIVE_PHOTOGRAPHY_DIMENSION_MISSING','05_visual_photography_strategy',dimension=k)
    fields=['platform','audience','topic','hook','script_structure','visual_form','cta','metric','race_stage','culture_adaptation','taboo_stereotype_check','platform_dimensions','duration','cover_first_frame','subtitle_strategy','music_rights','traffic_mechanism','landing_handoff','utm_attribution','why']
    for i,r in enumerate(_l(s.get('06_platform_content_matrix'))):
        if isinstance(r,dict):
            miss=[k for k in fields if not _p(r.get(k))]
            if miss:_issue(issues,'FULL_CONTENT_MATRIX_DEPTH_MISSING','06_platform_content_matrix',row=i,fields=miss)
    race=_l(s.get('07_race_execution_table'));expected=['RESEARCH','ACTION','COMMUNICATION','EVALUATION'];actual=[str(_d(r).get('stage') or '').upper() for r in race]
    if actual!=expected:_issue(issues,'FULL_RACE_STAGES_INCOMPLETE','07_race_execution_table',expected=expected,actual=actual)
    for i,r in enumerate(race):
        if isinstance(r,dict):
            miss=[k for k in ('stage','objective','key_actions','output','platform','culture_check','kpi','why') if not _p(r.get(k))]
            if miss:_issue(issues,'FULL_RACE_ROW_DEPTH_MISSING','07_race_execution_table',row=i,fields=miss)
    for i,r in enumerate(_l(s.get('08_culture_adaptation_checklist'))):
        if isinstance(r,dict):
            miss=[k for k in ('adaptation_point','inclusive_representation','stereotype_taboo_risk','result','modification','why') if not _p(r.get(k))]
            if not any(_p(r.get(k)) for k in ('evidence_or_assumption','evidence_refs')):miss.append('evidence_or_assumption')
            if miss:_issue(issues,'FULL_CULTURE_CHECKLIST_DEPTH_MISSING','08_culture_adaptation_checklist',row=i,fields=miss)
    last=_d(s.get('09_risk_measurement_priority_next_steps'));trade=_d(last.get('resource_tradeoff_plan'))
    for k in ('constraints','keep','cut','why'):
        if not _p(trade.get(k)):_issue(issues,'FULL_RESOURCE_TRADEOFF_MISSING','09_risk_measurement_priority_next_steps',field=k)
    sc=_d(last.get('output_self_check'))
    for k in ('fabrication_check','why_check','culture_check','compliance_check','metric_check','assumption_check','language_companion_check','asset_universe_check','prompt_depth_check'):
        if k not in sc:_issue(issues,'FULL_OUTPUT_SELF_CHECK_MISSING','09_risk_measurement_priority_next_steps',field=k)
    unique=[];seen=set()
    for x in issues:
        sig=json.dumps(x,ensure_ascii=False,sort_keys=True,default=str)
        if sig not in seen:seen.add(sig);unique.append(x)
    return {'status':'PASS' if not unique else 'INCOMPLETE','mode':'FULL','issues':unique,'warnings':warnings,'required_market_culture_dimensions':MARKET_CULTURE_DIMENSIONS,'required_framework_relationships':FRAMEWORK_RELATIONS,'depth_contract':'FULL_COMMERCIAL_DEPTH_V3_HOST_RUNTIME_PARITY'}

def audit_asset_portfolio_depth(universe,packaged_asset_ids=None):
    u=_d(universe);assets=[x for x in _l(u.get('assets')) if isinstance(x,dict)];pack=set(packaged_asset_ids or set());issues=[];cap=u.get('activation_capacity') or u.get('gallery_capacity') or u.get('platform_slot_capacity')
    if u.get('fixed_total_asset_limit') is True:_issue(issues,'ASSET_UNIVERSE_TOTAL_LIMIT_FORBIDDEN')
    if u.get('platform_capacity_is_activation_constraint_only') is not True:_issue(issues,'ACTIVATION_CAPACITY_BOUNDARY_MISSING')
    need={str(x.get('asset_id') or x.get('id')) for x in assets if (x.get('asset_id') or x.get('id')) and str(x.get('deployment_state') or x.get('pool') or '').upper() not in {'ARCHIVE','NOT_NEEDED'}}
    missing=sorted(need-pack) if pack else []
    if missing:_issue(issues,'ASSET_UNIVERSE_CANDIDATES_NOT_MATERIALIZED',missing_asset_ids=missing)
    if pack and not assets:_issue(issues,'ASSET_UNIVERSE_EMPTY_WHILE_PACKAGES_EXIST',packaged_count=len(pack))
    return {'status':'PASS' if not issues else 'INCOMPLETE','issues':issues,'total_asset_candidates':len(assets),'activation_capacity':cap,'missing_materialized_asset_ids':missing,'asset_family_counts':dict(Counter(str(x.get('asset_family') or x.get('family') or 'OTHER') for x in assets)),'deployment_state_counts':dict(Counter(str(x.get('deployment_state') or x.get('pool') or 'UNSPECIFIED') for x in assets))}

def _read_json(p):
    try:
        d=json.loads(Path(p).read_text(encoding='utf-8'));return d if isinstance(d,dict) else {}
    except Exception:return {}
def _ids(p):
    ids=set()
    for d in (Path(p)/'asset_packages',Path(p)/'video'):
        if d.exists():ids.update(x.name for x in d.iterdir() if x.is_dir())
    return ids
def _path_value(obj, path):
    cur=obj
    for key in path:
        if not isinstance(cur,dict):return None
        cur=cur.get(key)
    return cur

def _card_issues(card,aid):
    # v0.6.70+ Design Card is intentionally object-shaped. Audit semantic decisions from their
    # named objects instead of assuming every field is flattened at the card root.
    groups={
      'strategic_job':(
          ('strategic_job',),('shopper_question',),('consumer_question',),('belief_transition',),
          ('commerce_task','strategic_job'),('commerce_task','consumer_question'),('visual_narrative','shopper_question'),
      ),
      'visual_carrier':(('visual_carrier',),('carrier',),('role',),('agent_art_direction','visual_carrier')),
      'product_presence':(('product_presence',),('product_role',),('product',),('agent_art_direction','product_presence')),
      'subject_system':(('subject_system',),('subject_type',),('subject',),('subject_action_environment_props','subject')),
      'scene_environment':(('scene',),('environment',),('scene_system',),('decisive_moment',),('subject_action_environment_props','environment')),
      'props_elements':(('props',),('supporting_elements',),('evidence_elements',),('subject_action_environment_props','props')),
      'evidence_mode':(('evidence_mode',),('evidence_hierarchy',),('proof',),('proof_mechanism',),('information_design','proof_plane'),('agent_art_direction','evidence_hierarchy')),
      'composition':(('composition_grammar',),('composition',),('spatial_rhythm',),('composition_camera','composition_grammar'),('photography_execution','composition')),
      'cmf_material':(('cmf',),('material',),('palette',),('palette_hex',),('lighting_material_cmf','cmf'),('photography_execution','cmf')),
      'portfolio_delta':(('portfolio_delta',),('variant_hypothesis',),('test_hypothesis',),('incremental_information',),('agent_art_direction','portfolio_rhythm_delta'),('commerce_task','incremental_information')),
      'measurement':(('measurement_hypothesis',),('success_metric',),('metric',),('commerce_task','success_metric')),
    };out=[]
    for label,paths in groups.items():
        if not any(_p(_path_value(card,path)) for path in paths):_issue(out,'ASSET_DESIGN_CARD_DECISION_MISSING',asset_id=aid,decision=label)
    return out

def _listing_sections(text):
    out=[];matches=list(re.finditer(r'^##\s+(.+?)\s*$',text,flags=re.M))
    for i,m in enumerate(matches):
        start=m.end();end=matches[i+1].start() if i+1<len(matches) else len(text)
        out.append((m.group(1).strip(),text[start:end].strip()))
    return out

def _foreign_listing_companion_gaps(text):
    sections=_listing_sections(text);heads=[h.casefold() for h,_ in sections];gaps=[]
    def norm(h):
        x=h.casefold().strip();x=re.sub(r'\s*[—-]\s*(en|bm|ms|my|malay|english)\s*$','',x);x=re.sub(r'_(en|bm|ms|my)$','',x);return x.strip()
    def is_foreign(h):return bool(re.search(r'(?:_(?:en|bm|ms|my)$|\s*[—-]\s*(?:en|bm|ms|my|malay|english)\s*$)',h.casefold()))
    for h,body in sections:
        low=h.casefold();base=norm(h)
        if is_foreign(h):
            if re.search(r'[\u3400-\u4dbf\u4e00-\u9fff]',body):continue
            candidates={base+'_zh',base+'_cn',base+' — 中文',base+' - 中文',base+' 中文释义',base+' 中文说明',base+' 中文用途'}
            if not any(c in heads for c in candidates):gaps.append(h)
        elif 'search terms' in low or 'keywords' in low:
            if re.search(r'(?mi)^\s*(?:en|bm|ms|malay|english)\s*:',body) and not re.search(r'(?mi)^\s*(?:zh|cn|中文|中文释义|中文用途)\s*:',body):gaps.append(h)
        elif base in {'category','category path','category_path','attributes','faq','usage','warnings','package contents'}:
            if re.search(r'[A-Za-z]{4,}',body) and not re.search(r'[\u3400-\u4dbf\u4e00-\u9fff]',body):gaps.append(h)
    return sorted(set(gaps))

def _cn_only_package(p):
    for rel in ('DELIVERY_LANGUAGE_MATRIX_AUDIT.json','PLATFORM_SCOPE.json','supporting_analysis/target_context.json'):
        d=_read_json(p/rel);blob=json.dumps(d,ensure_ascii=False).upper()
        if 'CN_ONLY' in blob:return True
        if any(x in blob for x in ('"MARKET": "CN"','"COUNTRY": "CN"','CHINA DOMESTIC','中国大陆')):return True
    return False

def audit_host_full_package(package_dir):
    p=Path(package_dir);issues=[]
    for rel in CORE_HOST_FULL_FILES:
        if not (p/rel).exists():_issue(issues,'FULL_DELIVERY_OBJECT_MISSING',path=rel)
    seen_listing=set()
    for lp in (p/'01_LISTING_UPLOAD_READY.md',p/'listing/01_LISTING_UPLOAD_READY.md'):
        if lp.exists():
            for field in _foreign_listing_companion_gaps(lp.read_text(encoding='utf-8',errors='ignore')):
                sig=(str(lp.relative_to(p)),field)
                if sig not in seen_listing:
                    seen_listing.add(sig);_issue(issues,'LISTING_CHINESE_COMPANION_MISSING',path=sig[0],field=field)
    ar=p/'asset_packages'
    if ar.exists():
        if not _cn_only_package(p):
            for en in ar.glob('*/06_prompt_EN.txt'):
                if re.search(r'[\u3400-\u4dbf\u4e00-\u9fff]',en.read_text(encoding='utf-8',errors='ignore')):_issue(issues,'MODEL_PROMPT_EN_LANGUAGE_PURITY_FAILED',asset_id=en.parent.name,path=str(en.relative_to(p)))
        for card in ar.glob('*/12_design_card.json'):issues.extend(_card_issues(_read_json(card),card.parent.name))
    uni=_read_json(p/'ASSET_UNIVERSE.json')
    if uni:
        port=audit_asset_portfolio_depth(uni,_ids(p));issues.extend(port.get('issues') or [])
    else:
        port={'status':'INCOMPLETE','issues':[{'code':'ASSET_UNIVERSE_EXPORT_MISSING'}]};issues.extend(port['issues'])
    if ar.exists():
        notes=[x.read_text(encoding='utf-8',errors='ignore').strip() for x in ar.glob('*/09_production_notes.md')];meas=[]
        for x in ar.glob('*/12_design_card.json'):
            m=_read_json(x).get('measurement_hypothesis')
            if _p(m):meas.append(str(m).strip())
        if len(notes)>=5:
            n=Counter(notes).most_common(1)[0][1]
            if n/len(notes)>=.7:_issue(issues,'PORTFOLIO_PRODUCTION_NOTES_OVER_REUSED',duplicate_ratio=round(n/len(notes),3))
        if len(meas)>=5:
            n=Counter(meas).most_common(1)[0][1]
            if n/len(meas)>=.7:_issue(issues,'PORTFOLIO_MEASUREMENT_HYPOTHESIS_OVER_REUSED',duplicate_ratio=round(n/len(meas),3))
    return {'status':'PASS' if not issues else 'INCOMPLETE','issues':issues,'asset_portfolio':port,'contract':'HOST_NATIVE_FULL_MATERIALIZATION_EQUALS_RUNTIME_EXPORT_V3'}
