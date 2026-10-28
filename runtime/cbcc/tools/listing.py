from __future__ import annotations
from collections import defaultdict, Counter
from typing import Any
import re


def _norm(s): return re.sub(r'\s+',' ',str(s or '')).strip()


def lint_title(title,max_chars=None,required_terms=None,forbidden_terms=None,max_bytes=None):
    issues=[]; title=_norm(title); required_terms=required_terms or []; forbidden_terms=forbidden_terms or []
    if max_chars is not None and len(title)>max_chars: issues.append(f'length {len(title)}>{max_chars}')
    b=len(title.encode('utf-8'))
    if max_bytes is not None and b>max_bytes: issues.append(f'bytes {b}>{max_bytes}')
    low=title.casefold()
    for t in required_terms:
        if str(t).casefold() not in low: issues.append(f'missing required term: {t}')
    for t in forbidden_terms:
        if str(t).casefold() in low: issues.append(f'contains disallowed term: {t}')
    return {'pass':not issues,'issues':issues,'length':len(title),'bytes_utf8':b}


def spec_consistency(left:dict,right:dict,fields):
    return [{'field':f,'left':left.get(f),'right':right.get(f)} for f in fields if left.get(f)!=right.get(f)]


def _score_keyword(r):
    if r.get('priority') is not None: return float(r['priority'])
    v=float(r.get('volume') or 0); c=float(r.get('competition') or 0)
    return v/(1+c) if v else 0.0


def _keyword_role(cluster:str)->str:
    return {
        'CORE':'TITLE_OR_PRIMARY','CATEGORY':'TITLE_OR_PRIMARY','PRODUCT':'TITLE_OR_PRIMARY',
        'PARAMETER':'TITLE_OR_ATTRIBUTE','SPEC':'ATTRIBUTE_OR_DETAIL','AUDIENCE':'BULLET_OR_PDP',
        'FEATURE':'BULLET_OR_DETAIL','BENEFIT':'BULLET_OR_DETAIL','SCENE':'PDP_OR_CREATIVE',
        'USE_CASE':'PDP_OR_CREATIVE','ACCESSORY':'ATTRIBUTE_OR_PACKAGE','RISK':'FAQ_OR_OBJECTION',
        'QUESTION':'FAQ_OR_PDP','BRAND':'TITLE_IF_REQUIRED','LOCAL':'LOCALIZATION_SUPPORT'
    }.get(cluster,'SUPPORT')


def _funnel_role(cluster:str)->str:
    return {
        'CORE':'SEARCH_RELEVANCE','CATEGORY':'SEARCH_RELEVANCE','PRODUCT':'SEARCH_RELEVANCE','BRAND':'SEARCH_RELEVANCE',
        'PARAMETER':'FIT_VERIFY','SPEC':'FIT_VERIFY','AUDIENCE':'RELATE','FEATURE':'BELIEVE','BENEFIT':'RELATE',
        'SCENE':'RELATE','USE_CASE':'RELATE','ACCESSORY':'RISK_REDUCTION','RISK':'RISK_REDUCTION','QUESTION':'RISK_REDUCTION',
    }.get(cluster,'SUPPORT')


def keyword_architecture(rows:list[dict[str,Any]]) -> dict[str,Any]:
    """Aggregate already classified keyword evidence; semantic classification stays upstream."""
    groups=defaultdict(list)
    for r in rows:
        term=_norm(r.get('term') or r.get('keyword') or r.get('query'))
        if not term: continue
        group=str(r.get('cluster') or r.get('intent') or 'UNCLASSIFIED').upper()
        groups[group].append({'term':term,'volume':r.get('volume') or r.get('search_volume'),'competition':r.get('competition'),'priority_score':round(_score_keyword(r),6),'source_id':r.get('source_id'),'role':_keyword_role(group),'decision_stage':_funnel_role(group)})
    for k in groups: groups[k].sort(key=lambda x:x['priority_score'],reverse=True)
    return {'status':'AGGREGATED_FROM_CLASSIFIED_INPUT','clusters':dict(groups),'unclassified_count':len(groups.get('UNCLASSIFIED',[])),'intent_summary':[{ 'cluster':k,'term_count':len(v),'volume':round(sum(float(x.get('volume') or 0) for x in v),6),'top_terms':[x['term'] for x in v[:5]],'role':_keyword_role(k),'decision_stage':_funnel_role(k)} for k,v in sorted(groups.items(),key=lambda kv:sum(float(x.get('volume') or 0) for x in kv[1]),reverse=True)]}


def _collect_numbers(text:str):
    return re.findall(r'(?<![A-Za-z])\d+(?:\.\d+)?\s*(?:%|ml|mL|g|kg|oz|cm|mm|in|inch|hours?|hrs?|W|V|mAh)?',text or '')


def trace_copy(copy_text:str, allowed_facts:dict[str,Any], allowed_claims:list[dict[str,Any]]) -> dict[str,Any]:
    fact_blob=' '.join(str(v) for v in allowed_facts.values())
    claim_blob=' '.join(str(c.get('claim',c.get('text',''))) for c in allowed_claims if str(c.get('evidence_grade') or c.get('evidence_level') or '').upper() in {'A','B'} and str(c.get('publication_status') or '').upper()!='BLOCKED')
    unsupported_numbers=[n for n in _collect_numbers(copy_text) if n.casefold() not in fact_blob.casefold() and n.casefold() not in claim_blob.casefold()]
    return {'pass':not unsupported_numbers,'unsupported_numeric_tokens':unsupported_numbers,'note':'Numeric trace is deterministic. Semantic claim entailment remains a review task.'}


def _field_contract(field,value,rules,source_ids,claim_ids,language_contract=None):
    r=rules.get(field,{}) if isinstance(rules,dict) else {}
    return {'field':field,'required':bool(r.get('required',False)),'value_supplied':value not in (None,'',[]),'max_chars':r.get('max_chars'),'max_bytes':r.get('max_bytes'),
            'required_terms':r.get('required_terms',[]),'source_ids':source_ids,'claim_ids':claim_ids,'visible_copy_locales':(language_contract or {}).get('visible_copy_locales',[])}


def keyword_priority_plan(architecture:dict[str,Any], top_n:int=30)->list[dict[str,Any]]:
    out=[]
    for cluster,rows in (architecture.get('clusters') or {}).items():
        for r in rows[:top_n]:
            out.append({'term':r['term'],'cluster':cluster,'priority_score':r.get('priority_score'),'role':_keyword_role(cluster),'decision_stage':_funnel_role(cluster),'source_id':r.get('source_id'),'why':f"该词被归入 {cluster}；其使用位置应服务 {_funnel_role(cluster)}，而不是仅为提高词频。"})
    out.sort(key=lambda x:x.get('priority_score') or 0,reverse=True)
    return out[:top_n]


def field_decision_map(fields:dict[str,Any], rules:dict[str,Any]|None=None) -> list[dict[str,Any]]:
    rules=rules or {}
    role_map={
        'title':('IDENTIFY + SEARCH','准确识别产品、承接核心搜索意图，并允许一个第一购买理由。'),
        'brand':('IDENTIFY','确认品牌/产品身份。'),
        'attributes':('VERIFY FIT','用结构化事实降低规格/兼容/变体误购。'),
        'highlights':('RELATE + BELIEVE','把次级利益与理由-to-believe按优先级展开。'),
        'bullets':('RELATE + BELIEVE','把次级利益与理由-to-believe按优先级展开。'),
        'description':('BELIEVE + CONTEXT','提供需要更深解释的产品逻辑、使用语境和证据。'),
        'faq':('REDUCE RISK','提前回答高频异议、误解和退货驱动问题。'),
        'usage':('USE / APPLICATION','解释如何使用、频率、步骤或注意事项（仅限有依据内容）。'),
        'package':('REDUCE RISK','说明包装内容物、规格、数量和交付预期。'),
        'primary_image':('IDENTIFY + CLICK','移动端第一眼识别产品，不承担完整详情页信息。'),
    }
    names=[k for k in fields if not str(k).startswith('_')]
    for k,v in rules.items():
        if isinstance(v,dict) and v.get('required') and k not in names: names.append(k)
    out=[]
    for field in names:
        key=str(field).casefold(); job,why=role_map.get(key,('DECISION SUPPORT','该字段应有明确增量信息任务，避免与其他字段长句重复。'))
        out.append({'field':field,'decision_job':job,'value_supplied':fields.get(field) not in (None,'',[]),'why':why,'platform_constraint':rules.get(field,{}) if isinstance(rules.get(field,{}),dict) else {},'incremental_information_rule':'只放该字段对下一购买判断有新增价值的信息；必要的核心Claim重复需显式说明原因。'})
    return out


def objection_resolution_plan(objections:list[Any]|None) -> list[dict[str,Any]]:
    out=[]
    for i,o in enumerate(objections or []):
        if isinstance(o,str):
            text=o; category='GENERAL'; evidence=[]; preferred=None
        else:
            text=o.get('objection') or o.get('question') or o.get('text') or str(o); category=str(o.get('category') or 'GENERAL').upper(); evidence=o.get('source_ids',[])+o.get('claim_ids',[]); preferred=o.get('field')
        field=preferred or ({'PACKAGE':'package','USAGE':'usage','COMPATIBILITY':'attributes','SIZE':'attributes','RISK':'faq'}.get(category,'faq'))
        out.append({'objection_id':f'OBJ-{i+1:02d}','objection':text,'category':category,'recommended_field':field,'evidence_refs':evidence,'answer_contract':'Answer with product truth / approved claim / explicit expectation boundary. Do not solve uncertainty with stronger marketing language.','why':'异议只在最合适字段解决一次，其他Surface按需要引用结论，避免全Listing重复。'})
    return out


def localization_transcreation_contract(language_contract:dict[str,Any]|None, notes:Any=None) -> dict[str,Any]:
    language_contract=language_contract or {}
    delivery_locale=language_contract.get('delivery_locale') or 'zh-CN'
    return {
        'primary_locale':language_contract.get('primary_locale'),
        'visible_copy_locales':language_contract.get('visible_copy_locales',[]),
        'support_locales':language_contract.get('support_locales',[]),
        'delivery_locale':delivery_locale,
        'principles':['先保留产品事实和消息层级，再按目标语言重写自然表达；不做逐词直译。','数字、规格、Claim强度与警示边界跨语言保持等价。','标题长度/搜索词顺序/CTA按目标Surface重编排，不复制源语言语序。','人类交付默认使用 delivery_locale；任何非 delivery_locale 的目标市场文案必须同时提供 delivery_locale 释义/用途说明，搜索词可解释搜索意图而非机械直译。'],
        'project_notes':notes or [],
        'why':'跨境Listing的目标不是“翻译完成”，而是让相同价值与事实在本地语言中保持自然、可搜索、可理解和不夸大；同时让项目使用者无需掌握目标语言也能评审和执行。'
    }



def _visible_locales(language_contract:dict[str,Any]|None)->list[str]:
    lc=language_contract or {}; vals=lc.get('visible_copy_locales') or []
    if not vals and lc.get('primary_locale'): vals=[lc.get('primary_locale')]
    out=[]
    for x in vals:
        if x and x not in out: out.append(x)
    return out


def transcreation_task_matrix(fields:dict[str,Any], language_contract:dict[str,Any]|None, localized_copy:dict[str,Any]|None=None, keyword_arch:dict[str,Any]|None=None) -> dict[str,Any]:
    """Create locale × field authoring tasks while preserving factual/message invariants."""
    locales=_visible_locales(language_contract); primary=(language_contract or {}).get('primary_locale'); delivery_locale=(language_contract or {}).get('delivery_locale') or 'zh-CN'
    localized_copy=localized_copy or {}; keyword_arch=keyword_arch or {}
    rows=[]
    for locale in locales:
        supplied=localized_copy.get(locale,{}) if isinstance(localized_copy.get(locale,{}),dict) else {}
        for field,value in fields.items():
            if str(field).startswith('_'): continue
            target_value=supplied.get(field)
            status='SOURCE_LOCALE' if locale==primary and target_value in (None,'') else ('SUPPLIED_FOR_REVIEW' if target_value not in (None,'',[]) else 'TO_AUTHOR')
            rows.append({
                'locale':locale,'field':field,'source_value':value,'target_value':target_value,'status':status,
                'delivery_locale':delivery_locale,'delivery_companion_required':str(locale).casefold()!=str(delivery_locale).casefold(),
                'delivery_companion_instruction':'同时提供简洁准确的中文释义/用途说明；搜索词解释搜索意图，不要求逐词翻译。' if str(delivery_locale).casefold().startswith('zh') else f'Provide a concise companion explanation in {delivery_locale}.',
                'semantic_invariants':['Product identity/spec must remain factually equivalent','Claim strength/evidence boundary must not increase','Numbers/pack contents/usage constraints must remain equivalent'],
                'native_adaptation':['Rewrite syntax and information order for the locale; do not translate word-by-word','Use locally natural product/category wording when supported by search/market evidence','Preserve platform field job and cognitive priority'],
                'search_intent_input':[x.get('term') for x in (keyword_arch.get('top_terms') or [])[:12]],
                'why':'Transcreation must keep the same commercial meaning and evidence strength while changing phrasing, order and local idiom to fit the target language/surface.'
            })
    return {'status':'TRANSCREATION_TASKS_COMPILED' if locales else 'NO_VISIBLE_LOCALES','primary_locale':primary,'delivery_locale':delivery_locale,'locales':locales,'tasks':rows,'principle':'Meaning equivalence + native commerce phrasing + platform fit; never word-for-word translation by default. Human delivery must include a delivery-locale companion for non-delivery-locale copy.'}


def localized_copy_audit(fields:dict[str,Any], language_contract:dict[str,Any]|None, localized_copy:dict[str,Any]|None=None, claims:list[dict[str,Any]]|None=None, claim_refs:dict[str,Any]|None=None) -> dict[str,Any]:
    localized_copy=localized_copy or {}; primary=(language_contract or {}).get('primary_locale')
    src_numbers={k:set(_collect_numbers(str(v))) for k,v in fields.items() if not str(k).startswith('_')}
    claim_refs=claim_refs or {}; claims=claims or []
    numeric_authority_by_id={}
    for c in claims:
        cid=str(c.get('claim_id') or c.get('id') or '')
        grade=str(c.get('evidence_grade') or c.get('evidence_level') or '').upper()
        declared_status=str(c.get('status') or '').upper()
        publication=str(c.get('publication_status') or '').upper()
        blocked=(publication in {'BLOCKED','SOFT_ONLY_NO_HARD_CLAIM'} or declared_status in {'BLOCKED','PROHIBITED','REJECTED','INVALID'})
        numeric_authorized=(
            grade in {'A','B'}
            or declared_status in {'APPROVED','VERIFIED','ACTIVE'}
            or publication in {'HARD_CLAIM_ALLOWED_WITH_SCOPE','BOUNDED_SUPPORTED_CLAIM'}
        )
        if cid and numeric_authorized and not blocked:
            numeric_authority_by_id[cid]=c
    authorized_numbers={}
    for field,ids in claim_refs.items():
        ids=ids if isinstance(ids,list) else [ids]
        nums=set()
        for cid in ids:
            c=numeric_authority_by_id.get(str(cid))
            if c: nums.update(_collect_numbers(str(c.get('text') or c.get('claim') or '')))
        authorized_numbers[str(field)]=nums
    issues=[]; reviewed=[]
    for locale,payload in localized_copy.items():
        if not isinstance(payload,dict): continue
        for field,target in payload.items():
            if field not in fields: continue
            source_nums=src_numbers.get(field,set()); target_nums=set(_collect_numbers(str(target)))
            missing=sorted(source_nums-target_nums)
            raw_extra=target_nums-source_nums
            authorized_extra=sorted(raw_extra & authorized_numbers.get(str(field),set()))
            extra=sorted(raw_extra-authorized_numbers.get(str(field),set()))
            if missing or extra:
                issues.append({'locale':locale,'field':field,'issue':'NUMERIC_EQUIVALENCE_REVIEW','missing_source_numbers':missing,'extra_target_numbers':extra,'authorized_extra_numbers':authorized_extra,'why':'Numbers often encode size, concentration, duration or quantity. Extra numbers are allowed only when this exact field already carries an explicit approved Claim reference containing that number; all other drift remains blocked.'})
            reviewed.append({'locale':locale,'field':field,'source_locale':primary,'numeric_equivalence':'REVIEW' if missing or extra else ('PASS_WITH_FIELD_CLAIM_AUTHORITY' if authorized_extra else 'PASS_ON_LITERAL_NUMBERS'),'authorized_extra_numbers':authorized_extra})
    return {'status':'AUDITED_SUPPLIED_LOCAL_COPY' if reviewed else 'NO_LOCAL_COPY_SUPPLIED','reviewed':reviewed,'issues':issues,'note':'Deterministic audit preserves source-field numbers and permits only extra numeric tokens explicitly authorized by this field’s approved Claim refs. Native fluency, semantic claim equivalence, platform fit and culture still require review.'}





def terminology_memory_audit(localized_copy:dict[str,Any]|None, memory:Any=None) -> dict[str,Any]:
    """Audit locale copy against explicit terminology memory; never invent translations."""
    localized_copy=localized_copy or {}; entries=list(memory or []) if isinstance(memory,list) else []
    issues=[]; usage=[]
    for seq,e in enumerate(entries):
        if not isinstance(e,dict): continue
        locale=str(e.get('locale') or '')
        canonical=str(e.get('canonical') or e.get('term') or '')
        concept=e.get('concept') or e.get('term_id') or f'TERM-{seq+1}'
        if not locale or not canonical: continue
        payload=localized_copy.get(locale,{}) if isinstance(localized_copy.get(locale,{}),dict) else {}
        allowed=[canonical]+[str(x) for x in (e.get('allowed_variants') or []) if str(x)]
        forbidden=[str(x) for x in (e.get('forbidden_variants') or []) if str(x)]
        required=e.get('required_in_fields') or []
        if isinstance(required,str): required=[required]
        mode=str(e.get('consistency_mode') or 'PREFER_CANONICAL').upper()
        used=[]
        for field,value in payload.items():
            text=str(value or '').casefold()
            variants=[v for v in allowed if v.casefold() in text]
            if variants:
                used.append({'field':field,'variants':variants})
            bad=[v for v in forbidden if v.casefold() in text]
            if bad:
                issues.append({'locale':locale,'field':field,'concept':concept,'issue':'FORBIDDEN_TERMINOLOGY','severity':'BLOCK','variants':bad,'why':'The supplied terminology memory explicitly forbids these variants for this locale/concept.'})
        for field in required:
            text=str(payload.get(field) or '').casefold()
            if payload.get(field) not in (None,'') and not any(v.casefold() in text for v in allowed):
                issues.append({'locale':locale,'field':field,'concept':concept,'issue':'REQUIRED_TERMINOLOGY_MISSING','severity':'BLOCK','canonical':canonical,'allowed_variants':allowed,'why':'This field is explicitly bound to the supplied terminology memory and must use an approved equivalent.'})
        distinct=sorted({v for u in used for v in u['variants']})
        if len(distinct)>1:
            severity='BLOCK' if mode=='CANONICAL_ONLY' else 'REVIEW'
            issues.append({'locale':locale,'field':'*','concept':concept,'issue':'CROSS_FIELD_TERMINOLOGY_VARIATION','severity':severity,'variants':distinct,'fields':[u['field'] for u in used],'why':'Multiple approved variants are being used for one concept. Review consistency unless deliberate field-specific phrasing is documented.'})
        usage.append({'locale':locale,'concept':concept,'canonical':canonical,'allowed_variants':allowed,'consistency_mode':mode,'used':used})
    return {'status':'TERMINOLOGY_MEMORY_AUDITED' if entries else 'NO_TERMINOLOGY_MEMORY','entries':len(entries),'usage':usage,'issues':issues,'blocking_issue_count':sum(1 for x in issues if x.get('severity')=='BLOCK'),'review_issue_count':sum(1 for x in issues if x.get('severity')=='REVIEW'),'principle':'Terminology memory constrains supplied concepts only; the runtime never invents local-language equivalents.'}

def current_localized_copy(localized_copy:dict[str,Any]|None, history:Any=None) -> tuple[dict[str,Any],dict[tuple[str,str],dict[str,Any]]]:
    current={str(k):dict(v) for k,v in (localized_copy or {}).items() if isinstance(v,dict)}
    latest={}
    events=list(history or []) if isinstance(history,list) else []
    for seq,e in enumerate(events):
        if not isinstance(e,dict) or e.get('locale') in (None,'') or e.get('field') in (None,''): continue
        loc,field=str(e.get('locale')),str(e.get('field')); copy=e.get('copy') if e.get('copy') is not None else e.get('authored_copy')
        if copy is None: continue
        rank=(int(e.get('sequence')) if e.get('sequence') not in (None,'') else seq,str(e.get('created_at') or ''))
        key=(loc,field)
        if key not in latest or rank>=latest[key]['_rank']:
            latest[key]={**e,'_rank':rank,'_sequence':seq}
            current.setdefault(loc,{})[field]=copy
    return current,latest


def copy_authoring_iteration_plan(final_copy:dict[str,Any]) -> dict[str,Any]:
    author=[]; revise=[]; review=[]; delivery_locale=final_copy.get('delivery_locale') or 'zh-CN'
    for pkg in final_copy.get('packages',[]) or []:
        for row in pkg.get('fields',[]) or []:
            base={'locale':row.get('locale'),'field':row.get('field'),'current_version_id':row.get('current_version_id'),'current_copy':row.get('authored_copy'),'source_value':row.get('source_value'),'platform_job':row.get('platform_job'),'delivery_locale':delivery_locale,'delivery_translation':row.get('delivery_translation'),'delivery_companion_required':str(row.get('locale') or '').casefold()!=str(delivery_locale).casefold()}
            st=row.get('release_status')
            if st=='TO_AUTHOR': author.append({**base,'task':'AUTHOR','instruction':'Author native commerce copy from Strategy Authority / transcreation task while preserving facts, claim strength, numbers and platform field job. If target locale differs from delivery_locale, also return delivery_translation / delivery_note for human review in the delivery language.'})
            elif st in {'BLOCKED_HARD_CONSTRAINT','REVISION_OR_REVIEW_REQUIRED','REVIEW_STALE_AFTER_REVISION'}: revise.append({**base,'task':'REVISE','hard_issues':row.get('hard_issues'),'review':row.get('review'),'instruction':'Revise only the current locale/field; preserve approved facts/claims and resolve explicit hard/review issues. New copy must create a new version before re-review. Keep the delivery-language companion synchronized.'})
            if st not in {'TO_AUTHOR','APPROVED_FINAL'}: review.append({**base,'task':'REVIEW','required_dimensions':['native_fluency','claim_equivalence','platform_fit','culture_fit'],'instruction':'Review the current version, not an earlier draft. Approval must name the current_version_id when version history exists.'})
    return {'status':'COPY_AUTHORING_ITERATION_PLAN_COMPILED','authoring_tasks':author,'revision_tasks':revise,'review_tasks':review,'loop':'AUTHOR → HARD CHECK → PROFESSIONAL REVIEW → REVISE AS NEW VERSION → RE-REVIEW → APPROVED_FINAL','principle':'A review of an older version never approves a revised version.'}

def platform_native_listing_profile(platform_context:dict[str,Any]|None=None) -> dict[str,Any]:
    ctx=platform_context or {}; p=str(ctx.get('platform_family') or '').casefold(); site=ctx.get('site')
    if 'tiktok' in p:
        return {'platform_family':'tiktok_shop','site':site,'search_job':'Mobile product identity + exact category/spec relevance; do not turn title into promotional copy.','pdp_job':'Fast identity → relevance → proof → objection/usage clarity.','copy_rhythm':'Short, spoken-natural clauses; one primary value cue per field before secondary proof.','native_surfaces':['SEARCH_RESULTS','PDP','GALLERY','PDP_VIDEO','CREATOR','LIVE'],'why':'TikTok Shop discovery and content traffic can arrive with low prior intent, so copy must identify the exact product quickly and remain easy to reuse in spoken/visual commerce.'}
    if 'shopee' in p:
        return {'platform_family':'shopee','site':site,'search_job':'Mobile search clarity: product/category + decisive spec/variant + truthful value cue.','pdp_job':'Reduce comparison friction with structured attributes, offer clarity, package/usage and FAQ.','copy_rhythm':'Compact comparison-friendly phrasing; prioritize exact specs and objection resolution over brand prose.','native_surfaces':['SEARCH_RESULTS','PDP','GALLERY','PDP_VIDEO','FAQ','CHAT'],'why':'Shopee users often compare adjacent listings quickly, so exact product/variant clarity and risk reduction should outrank long-form brand narrative.'}
    if 'amazon' in p:
        return {'platform_family':'amazon','site':site,'search_job':'Readable keyword relevance + exact product identity within current title/style constraints.','pdp_job':'Evidence-rich detail hierarchy: title/attributes → bullets → gallery/A+ → FAQ/usage where available.','copy_rhythm':'Search-readable, non-promotional, specification precise; each bullet adds incremental decision information.','native_surfaces':['SEARCH_RESULTS','PDP','GALLERY','PDP_VIDEO','A_PLUS'],'why':'Amazon is strongly search/comparison driven; discoverability and decision proof must coexist without keyword stuffing or promotional leakage into restricted fields.'}
    if 'shopify' in p or 'dtc' in p:
        return {'platform_family':'dtc','site':site,'search_job':'Collection/search identity plus brand/product differentiation.','pdp_job':'Modular landing narrative: promise → proof → fit → objection → usage → offer/CTA → retention path.','copy_rhythm':'Brand-native but commerce-explicit; modules may be longer, yet each section must move one belief state.','native_surfaces':['COLLECTION','PDP','LANDING','UGC','CRM'],'why':'DTC controls the full page and lifecycle path, so copy can carry more narrative depth while still requiring explicit product truth, proof and next-action logic.'}
    return {'platform_family':ctx.get('platform_family'),'site':site,'search_job':'Exact product identity and truthful relevance.','pdp_job':'Sequence value, proof and risk reduction by field job.','copy_rhythm':'Native readable commerce phrasing, not literal translation.','native_surfaces':ctx.get('surfaces') or [],'why':'Platform-native authoring should preserve one Strategy Authority while adapting information order and field density to the actual surface.'}


def final_copy_release_workflow(fields:dict[str,Any], language_contract:dict[str,Any]|None, localized_copy:dict[str,Any]|None, localized_reviews:Any, localized_audit:dict[str,Any], rules:dict[str,Any]|None=None, platform_context:dict[str,Any]|None=None, localized_history:Any=None, terminology_audit:dict[str,Any]|None=None) -> dict[str,Any]:
    """Turn authored localized copy into an explicit draft/review/final-release workflow.

    Deterministic checks cover literal numbers and field constraints. Native fluency, claim equivalence, culture and platform fit are accepted only from explicit review records.
    """
    rules=rules or {}; localized_copy=localized_copy or {}; locales=_visible_locales(language_contract); primary=(language_contract or {}).get('primary_locale'); delivery_locale=(language_contract or {}).get('delivery_locale') or 'zh-CN'
    localized_copy,latest_versions=current_localized_copy(localized_copy,localized_history)
    reviews=[]
    if isinstance(localized_reviews,list): reviews=localized_reviews
    elif isinstance(localized_reviews,dict):
        for loc,payload in localized_reviews.items():
            if isinstance(payload,dict):
                for field,rv in payload.items():
                    if isinstance(rv,dict): reviews.append({'locale':loc,'field':field,**rv})
    review_map={(str(x.get('locale')),str(x.get('field'))):x for x in reviews if x.get('locale') is not None and x.get('field') is not None}
    terminology_audit=terminology_audit or {'issues':[]}
    term_block=set(); term_review=set()
    for ti in (terminology_audit.get('issues') or []):
        loc=str(ti.get('locale')); sev=ti.get('severity'); fld=ti.get('field')
        targets=[]
        if fld not in (None,'*'): targets=[str(fld)]
        elif isinstance(ti.get('fields'),list): targets=[str(x) for x in ti.get('fields') if x not in (None,'')]
        for tf in targets:
            (term_block if sev=='BLOCK' else term_review if sev=='REVIEW' else set()).add((loc,tf))
    numeric_issues={(str(x.get('locale')),str(x.get('field'))) for x in (localized_audit.get('issues') or [])}
    profile=platform_native_listing_profile(platform_context)
    packages=[]; counts=Counter()
    for locale in locales:
        supplied=localized_copy.get(locale,{}) if isinstance(localized_copy.get(locale,{}),dict) else {}
        field_rows=[]; final_fields={}
        for field,source_value in fields.items():
            if str(field).startswith('_'): continue
            draft=supplied.get(field)
            if draft in (None,'') and locale==primary: draft=source_value
            review=review_map.get((str(locale),str(field)))
            version_event=latest_versions.get((str(locale),str(field)))
            current_version_id=(version_event or {}).get('version_id') or (version_event or {}).get('revision_id')
            review_version_id=(review or {}).get('version_id') or (review or {}).get('revision_id')
            review_stale=bool(current_version_id and review and str(review_version_id or '')!=str(current_version_id))
            issues=[]
            if (str(locale),str(field)) in numeric_issues: issues.append('NUMERIC_EQUIVALENCE_REVIEW')
            if (str(locale),str(field)) in term_block: issues.append('TERMINOLOGY_MEMORY_BLOCK')
            terminology_review_required=((str(locale),str(field)) in term_review)
            rr=rules.get(field,{}) if isinstance(rules.get(field,{}),dict) else {}
            if field=='title' and draft not in (None,''):
                lint=lint_title(draft,rr.get('max_chars'),rr.get('required_terms'),rr.get('forbidden_terms'),rr.get('max_bytes'))
                issues.extend(lint.get('issues') or [])
            decision=str((review or {}).get('decision') or '').upper()
            dims=['native_fluency','claim_equivalence','platform_fit','culture_fit']
            dim_status={d:str((review or {}).get(d) or '').upper() for d in dims}
            all_review_dims=all(dim_status[d] in {'PASS','APPROVED','OK'} for d in dims)
            if draft in (None,'',[]): status='TO_AUTHOR'
            elif issues: status='BLOCKED_HARD_CONSTRAINT'
            elif review_stale: status='REVIEW_STALE_AFTER_REVISION'
            elif terminology_review_required and not review: status='REVISION_OR_REVIEW_REQUIRED'
            elif decision=='APPROVED' and all_review_dims: status='APPROVED_FINAL'
            elif review: status='REVISION_OR_REVIEW_REQUIRED'
            else: status='DRAFT_REVIEW_REQUIRED'
            if status=='APPROVED_FINAL': final_fields[field]=draft
            counts[status]+=1
            field_rows.append({'locale':locale,'field':field,'source_value':source_value,'authored_copy':draft,'delivery_locale':delivery_locale,'delivery_translation':(version_event or {}).get('delivery_translation'),'delivery_note':(version_event or {}).get('delivery_note'),'delivery_companion_status':('NOT_REQUIRED' if str(locale).casefold()==str(delivery_locale).casefold() else ('READY' if (version_event or {}).get('delivery_translation') not in (None,'') else 'TO_AUTHOR')),'current_version_id':current_version_id,'version_event':version_event,'review_version_id':review_version_id,'release_status':status,'hard_issues':issues,'review':review,'review_dimensions':dim_status,'platform_job':profile.get('pdp_job'),'terminology_review_required':terminology_review_required,'why':'Final release requires current-version authored copy + deterministic hard-constraint pass + explicit native fluency, claim-equivalence, platform-fit and culture-fit approval.'})
        packages.append({'locale':locale,'status':'APPROVED_FINAL' if field_rows and all(x['release_status']=='APPROVED_FINAL' for x in field_rows) else 'PARTIAL_OR_REVIEW_REQUIRED','final_fields':final_fields,'fields':field_rows,'platform_profile':profile})
    out={'status':'FINAL_COPY_WORKFLOW_COMPILED' if locales else 'NO_VISIBLE_LOCALES','primary_locale':primary,'delivery_locale':delivery_locale,'platform_profile':profile,'packages':packages,'release_counts':dict(counts),'release_rule':'No localized string becomes APPROVED_FINAL merely because it exists. It must pass deterministic hard checks and explicit professional language/claim/platform/culture review of the current version.','generation_contract':'Host/model authors or revises target-locale drafts from Strategy Authority + Transcreation Tasks; runtime audits hard invariants, version binding and review/release state.','version_history_supplied':bool(localized_history),'terminology_memory_audit':terminology_audit}
    out['iteration_plan']=copy_authoring_iteration_plan(out)
    return out

def claim_source_trace_summary(trace:list[dict[str,Any]]) -> dict[str,Any]:
    missing=[x for x in trace if x.get('has_value') and not x.get('source_ids') and not x.get('claim_ids')]
    return {'field_count':len(trace),'fields_with_value':sum(1 for x in trace if x.get('has_value')),'fields_without_explicit_trace':[x.get('field') for x in missing],'note':'Not every descriptive field requires a claim ID, but factual/claim-heavy fields should retain source lineage where feasible.'}


def listing_conversion_architecture(fields:dict[str,Any], keywords:dict[str,Any], objections:list[dict[str,Any]]|None=None, rules:dict[str,Any]|None=None)->dict[str,Any]:
    objections=objections or []; rules=rules or {}
    names=[str(k) for k,v in fields.items() if not str(k).startswith('_') and v not in (None,'',[],{})]
    for k,v in rules.items():
        if isinstance(v,dict) and v.get('required') and str(k) not in names: names.append(str(k))
    decision_map=field_decision_map(fields,rules)
    click_candidates=['title','brand','product_name','price','variant']
    click_fields=[x for x in click_candidates if x in names]
    if not click_fields:
        click_fields=[row.get('field') for row in decision_map if 'IDENTIFY' in str(row.get('decision_job') or '')][:3]
    post_candidates=['faq','usage','package','attributes','warnings','shipping','returns']
    post_fields=[x for x in post_candidates if x in names]
    return {
        'search_layer':{
            'job':'Match high-priority search intent while preserving readable product identity.',
            'keyword_priority':keyword_priority_plan(keywords),
            'why':'Search fields establish relevance before persuasive depth; keyword coverage without clarity can reduce click quality.'
        },
        'click_layer':{
            'job':'Make the exact product and first reason-to-click immediately legible.',
            'fields':click_fields,
            'dynamic_from_current_fields':True,
            'why':'Click surfaces only expose fields that actually exist or are required for this Listing contract; no price/variant/image slot is manufactured for completeness.'
        },
        'decision_layer':{
            'job':'Sequence relevance, benefit, proof, fit and objection resolution.',
            'field_decision_map':decision_map,
            'objections':objection_resolution_plan(objections),
            'why':'PDP/listing content should answer the next buyer question rather than repeat the same selling point across fields.'
        },
        'post_purchase_prevention':{
            'job':'Clarify package contents, usage, compatibility, size and expectations before purchase when relevant.',
            'fields':post_fields,
            'dynamic_from_current_fields':True,
            'why':'Expectation fields appear only when supplied/required/relevant; the runtime does not invent a universal after-sales checklist.'
        },
        'active_fields':names,
        'fixed_field_quota':None,
    }


def keyword_coverage(fields:dict[str,Any], architecture:dict[str,Any])->dict[str,Any]:
    blob=' '.join(str(v) for k,v in fields.items() if not str(k).startswith('_')).casefold()
    rows=[]
    for cluster,terms in (architecture.get('clusters') or {}).items():
        for r in terms:
            term=str(r.get('term') or '')
            rows.append({'term':term,'cluster':cluster,'covered':term.casefold() in blob if term else False,'priority_score':r.get('priority_score'),'decision_stage':_funnel_role(cluster)})
    high=sorted(rows,key=lambda x:x.get('priority_score') or 0,reverse=True)[:30]
    return {'top_terms':high,'covered_top_count':sum(1 for x in high if x['covered']),'top_count':len(high),'coverage_ratio':round(sum(1 for x in high if x['covered'])/len(high),4) if high else None,'note':'Coverage is literal/deterministic; semantic synonyms and naturalness require language review.'}


def repetition_audit(fields:dict[str,Any])->dict[str,Any]:
    texts=[]
    for k,v in fields.items():
        if str(k).startswith('_'): continue
        vals=v if isinstance(v,list) else [v]
        for x in vals:
            t=_norm(x)
            if t: texts.append((k,t.casefold()))
    repeats=[]
    for i,(ka,a) in enumerate(texts):
        for kb,b in texts[i+1:]:
            if len(a)>=20 and (a==b or a in b or b in a): repeats.append({'field_a':ka,'field_b':kb,'text':a[:160],'why':'相同长句跨字段重复，可能浪费信息位；若是关键Claim的策略性重复，应显式说明。'})
    return {'repeats':repeats,'count':len(repeats)}


def compile_listing(fields:dict[str,Any], facts:dict[str,Any], claims:list[dict[str,Any]], rules:dict[str,Any]|None=None, language_contract:dict[str,Any]|None=None, keyword_rows:list[dict[str,Any]]|None=None, platform_context:dict[str,Any]|None=None) -> dict[str,Any]:
    rules=rules or {}; checks={}; all_text=[]
    if 'title' in fields:
        tr=rules.get('title',{})
        checks['title']=lint_title(fields['title'],tr.get('max_chars'),tr.get('required_terms'),tr.get('forbidden_terms'),tr.get('max_bytes'))
    for k,v in fields.items():
        if str(k).startswith('_'): continue
        if isinstance(v,str): all_text.append(v)
        elif isinstance(v,list): all_text.extend(str(x) for x in v)
        elif isinstance(v,dict): all_text.extend(str(x) for x in v.values())
    checks['numeric_trace']=trace_copy('\n'.join(all_text),facts,claims)
    src_map=fields.get('_source_refs',{}) if isinstance(fields.get('_source_refs'),dict) else {}
    claim_map=fields.get('_claim_refs',{}) if isinstance(fields.get('_claim_refs'),dict) else {}
    trace=[]; contracts=[]
    field_names=[k for k in fields if not str(k).startswith('_')]
    for k,v in rules.items():
        if isinstance(v,dict) and v.get('required') and k not in field_names: field_names.append(k)
    for k in field_names:
        v=fields.get(k); src=src_map.get(k,[]); clm=claim_map.get(k,[])
        trace.append({'field':k,'source_ids':src,'claim_ids':clm,'has_value':v not in (None,'',[])})
        contracts.append(_field_contract(k,v,rules,src,clm,language_contract))
        rr=rules.get(k,{}) if isinstance(rules.get(k,{}),dict) else {}
        if rr.get('required') and v in (None,'',[]): checks[f'required:{k}']={'pass':False,'issues':['required field missing']}
    kw=keyword_architecture(keyword_rows or [])
    clean_fields={k:v for k,v in fields.items() if not str(k).startswith('_')}
    localized_copy=fields.get('_localized_copy',{}) if isinstance(fields.get('_localized_copy',{}),dict) else {}
    localized_history=fields.get('_localized_copy_history') or []
    current_copy,_latest_copy_versions=current_localized_copy(localized_copy,localized_history)
    transcreation=transcreation_task_matrix(clean_fields,language_contract,current_copy,kw)
    localization_audit=localized_copy_audit(clean_fields,language_contract,current_copy,claims,claim_map)
    terminology_audit=terminology_memory_audit(current_copy,fields.get('_terminology_memory'))
    final_copy=final_copy_release_workflow(clean_fields,language_contract,current_copy,fields.get('_localized_copy_reviews'),localization_audit,rules,platform_context,localized_history,terminology_audit)
    objections=fields.get('_objections',[])
    conversion=listing_conversion_architecture(clean_fields,kw,objections,rules)
    return {
        'status':'LISTING_CONTRACT_COMPILED','fields':clean_fields,'field_contracts':contracts,'checks':checks,'traceability':trace,
        'claim_source_trace_summary':claim_source_trace_summary(trace),
        'keywords':kw,'keyword_priority':keyword_priority_plan(kw),'keyword_coverage':keyword_coverage(clean_fields,kw),
        'repetition_audit':repetition_audit(clean_fields),'conversion_architecture':conversion,
        'field_decision_map':conversion['decision_layer']['field_decision_map'],'objection_resolution_plan':conversion['decision_layer']['objections'],
        'usage_plan':fields.get('_usage',[]),'package_plan':fields.get('_package',[]),'faq_plan':fields.get('_faq',[]),
        'localization_transcreation':localization_transcreation_contract(language_contract,fields.get('_localization_notes')),
        'platform_native_listing_profile':platform_native_listing_profile(platform_context),
        'transcreation_task_matrix':transcreation,'localized_copy_audit':localization_audit,'terminology_memory_audit':terminology_audit,'terminology_memory':fields.get('_terminology_memory') or [],'final_copy_workflow':final_copy,'copy_authoring_iteration_plan':final_copy.get('iteration_plan'),
        'pass':all(x.get('pass',True) for x in checks.values())
    }

def apply_host_copy_authoring_responses(fields:dict[str,Any], responses:list[dict[str,Any]]|None=None) -> tuple[dict[str,Any],dict[str,Any]]:
    """Apply host/model-authored locale copy as NEW VERSION EVENTS, never as implicit approval.

    Host responses are content generation/revision outputs. Review records remain separate authority.
    """
    out=dict(fields or {})
    loc={str(k):dict(v) for k,v in (out.get('_localized_copy') or {}).items() if isinstance(v,dict)}
    history=list(out.get('_localized_copy_history') or [])
    applied=[]; rejected=[]
    latest={}
    for e in history:
        if isinstance(e,dict) and e.get('locale') and e.get('field'):
            latest[(str(e['locale']),str(e['field']))]=e
    for seq,r in enumerate(responses or []):
        if not isinstance(r,dict): continue
        locale=str(r.get('locale') or ''); field=str(r.get('field') or ''); copy=r.get('copy') if r.get('copy') is not None else r.get('authored_copy')
        if not locale or not field or copy in (None,''):
            rejected.append({'response_index':seq,'reason':'LOCALE_FIELD_COPY_REQUIRED','response':r}); continue
        prior=latest.get((locale,field))
        parent=r.get('parent_version_id') or (prior or {}).get('version_id') or (prior or {}).get('revision_id')
        version_id=r.get('version_id') or r.get('revision_id') or f"HOST-{locale}-{field}-{len(history)+1}"
        if prior and str(version_id)==str((prior or {}).get('version_id') or (prior or {}).get('revision_id')) and str(copy)!=str((prior or {}).get('copy') or (prior or {}).get('authored_copy')):
            rejected.append({'response_index':seq,'locale':locale,'field':field,'reason':'VERSION_ID_REUSED_FOR_DIFFERENT_COPY','version_id':version_id}); continue
        event={'locale':locale,'field':field,'version_id':version_id,'parent_version_id':parent,'copy':copy,'delivery_translation':r.get('delivery_translation') or r.get('delivery_translation_zh') or r.get('zh_translation'),'delivery_note':r.get('delivery_note') or r.get('zh_note'),'created_at':r.get('created_at'),'author':r.get('author') or r.get('model') or 'HOST_MODEL','task_id':r.get('task_id'),'task_type':r.get('task_type') or ('REVISE' if prior else 'AUTHOR'),'source':'HOST_AUTHORING_RESPONSE','generation_notes':r.get('generation_notes'),'strategy_authority_ref':r.get('strategy_authority_ref')}
        history.append(event); latest[(locale,field)]=event; loc.setdefault(locale,{})[field]=copy
        applied.append({'locale':locale,'field':field,'version_id':version_id,'parent_version_id':parent,'task_id':r.get('task_id'),'status':'NEW_VERSION_REQUIRES_HARD_CHECK_AND_REVIEW'})
    out['_localized_copy']=loc; out['_localized_copy_history']=history
    return out,{'status':'HOST_AUTHORING_RESPONSES_APPLIED' if applied else ('HOST_AUTHORING_RESPONSES_REJECTED' if rejected else 'NO_HOST_AUTHORING_RESPONSES'),'applied':applied,'rejected':rejected,'principle':'Host/model generation creates a draft version only. It never inherits or creates professional review approval.'}
