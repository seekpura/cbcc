from __future__ import annotations
from pathlib import Path
import json, hashlib
from .models import *
from .platform import PlatformCompiler
from .state import ProjectState
from .tools.market import analyze_market
from .tools.source_adapters import compile_source_adapters
from .tools.economics import unit_economics, scenario_matrix, economics_strategy
from .tools.listing import compile_listing, apply_host_copy_authoring_responses
from .tools.ads import analyze_ads, analyze_ad_portfolio
from .tools.feedback import analyze_feedback
from .tools.experiment import evaluate_binary_experiment, compile_experiment_analysis
from .tools.seven_agent import compile_seven_agent_synthesis
from .tools.visual import validate_photography_contract
from .assets import required_foundation_roles, FoundationAssetRecord
from .culture import compile_culture_context
from .locale import compile_language_profiles
from .asset_architecture import build_asset_architecture
from .category_strategy import infer_category_family
from .asset_compiler import compile_asset_packages, validate_asset_packages
from .decision import compile_persuasion_frameworks
from .decision_authority import (
    derive_task_content_families,
    selected_decision_frameworks,
    compile_decision_question_authority,
    compile_decision_trace_rows,
    augment_agent_next_action,
)
from .scope_readiness import compile_required_content_families, compile_gate_scope, request_intent_present
from .research import compile_research_gate, apply_host_research_response
from .agent_autonomy import (
    compile_agent_autonomy_plan, research_requirements_from_plan, derive_content_families,
    agent_creative_opportunities, agent_creative_directions,
)
from .agent_autonomy import (
    compile_agent_autonomy_plan, research_requirements_from_plan, derive_content_families,
    agent_creative_opportunities, agent_creative_directions, compile_agent_next_action,
)
from .creative import compile_curation, compile_creative_council, compile_cmf, compile_inclusive_photography, apply_creative_system_to_assets
from .creative_opportunity import compile_creative_opportunity_universe
from .video_creator import build_video_creator_plan, enrich_video_plan_with_strategy
from .surface_architecture import compile_surface_architecture
from .campaign_architecture import compile_paid_campaign_architecture
from .product_visual_intelligence import compile_product_visual_intelligence, compile_creative_anchor_plan
from .compliance import compile_compliance
from .production import build_production_run, apply_production_result, materialize_provider_jobs, ingest_provider_job_results
from .review import materialize_review_workspace, refresh_review_workspace
from .strategy_authority import build_master_strategy, materialize_strategy, apply_strategy_annotations, build_strategy_host_authoring_request
from .strategy_sources import compile_strategy_reasoning_context
from .claim_authority import compile_claim_authority
from .evidence_reconciliation import compile_market_evidence_fit_contract
from .pricing_economics_authority import compile_pricing_economics_authority
from .seven_tool_continuity import compile_seven_tool_continuity
from .io import load_tabular, apply_field_map

DEFAULT_FAMILIES=['LISTING','SEARCH','OFFER_PROMOTION','VISUAL','RICH_CONTENT','VIDEO','CREATOR_AFFILIATE','LIVE','PAID','SOCIAL','STORE','CX','LIFECYCLE','MEASUREMENT','COMPLIANCE']
FAMILY_KIND={'LISTING':'product_title','SEARCH':'search_intent_map','OFFER_PROMOTION':'offer_message','VISUAL':'visual_asset_plan','RICH_CONTENT':'rich_content_plan','VIDEO':'product_video_plan','CREATOR_AFFILIATE':'creator_brief','LIVE':'live_brief','PAID':'paid_creative_brief','SOCIAL':'social_content_plan','STORE':'store_merchandising_plan','CX':'faq_objection_map','LIFECYCLE':'lifecycle_content','MEASUREMENT':'measurement_plan','COMPLIANCE':'claim_trace'}
FAMILY_SURFACE={'LISTING':'PDP','SEARCH':'SEARCH_RESULTS','OFFER_PROMOTION':'PDP','VISUAL':'GALLERY','RICH_CONTENT':'LONGFORM','VIDEO':'PDP_VIDEO','CREATOR_AFFILIATE':'CREATOR','LIVE':'LIVE','PAID':'PAID_AD','SOCIAL':'SOCIAL_CONTENT','STORE':'STORE_BANNER','CX':'FAQ','LIFECYCLE':'CRM','MEASUREMENT':None,'COMPLIANCE':None}

def _write(path:Path,data):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8'); return str(path)

def _sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def _normalize_source_product_assets(records, resolution_roots):
    """Bind supplied product/source files as design references by default; exact immutable-source semantics are explicit-only."""
    out=[]
    roots=[Path(x) for x in resolution_roots if x]
    for i,raw in enumerate(records or []):
        r=dict(raw or {})
        aid=str(r.get('asset_id') or r.get('master_id') or f'PRODUCT-MASTER-{i+1:02d}')
        raw_path=r.get('path') or r.get('file_path')
        resolved=None
        if raw_path:
            cand=Path(str(raw_path)).expanduser()
            candidates=[cand] if cand.is_absolute() else [root/cand for root in roots]+[cand]
            resolved=next((x.resolve() for x in candidates if x.exists() and x.is_file()),None)
        actual_hash=_sha256_file(resolved) if resolved else None
        declared_hash=str(r.get('sha256') or '').lower() or None
        if actual_hash and declared_hash and actual_hash!=declared_hash:
            status='HASH_MISMATCH'
        elif actual_hash:
            status='HASH_VERIFIED_LOCAL'
        elif r.get('provider_asset_handle') and declared_hash:
            status='EXTERNAL_HANDLE_HASH_DECLARED'
        else:
            status='MISSING_SOURCE_FILE'
        requested_fidelity=str(r.get('fidelity_mode') or r.get('product_fidelity') or '').upper()
        exact_pixel=bool(r.get('exact_pixel_layer') is True or r.get('exact_pixel_composite') is True or requested_fidelity in {'EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'})
        identity_lock=bool(r.get('pixel_lock',False) or r.get('lock_real_product',False) or requested_fidelity in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE'})
        fidelity_mode='EXACT_PIXEL_COMPOSITE' if exact_pixel else ('REFERENCE_GUIDED_NATIVE_LOCK' if identity_lock else (requested_fidelity or 'REFERENCE_GUIDED'))
        if fidelity_mode in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}:
            fidelity_mode='REFERENCE_GUIDED_NATIVE_LOCK'
        out.append({
            'asset_id':aid,
            'role':r.get('role') or r.get('view') or 'PRODUCT_MASTER',
            'path':str(resolved) if resolved else (str(raw_path) if raw_path else None),
            'provider_asset_handle':r.get('provider_asset_handle'),
            'sha256':actual_hash or declared_hash,
            'ingest_status':status,
            'pixel_lock':exact_pixel,
            'identity_lock':bool(identity_lock or fidelity_mode=='REFERENCE_GUIDED_NATIVE_LOCK'),
            'fidelity_mode':fidelity_mode,
            'source_usage':r.get('source_usage') or ('EXACT_PIXEL_SOURCE_LAYER' if exact_pixel else ('MODEL_REFERENCE_INPUT' if fidelity_mode=='REFERENCE_GUIDED_NATIVE_LOCK' else 'DESIGN_REFERENCE')),
            'allowed_transforms':r.get('allowed_transforms') or (['PROPORTIONAL_SCALE','PLACEMENT','MASK_OR_CROP','COMPOSITE'] if exact_pixel else (['REFERENCE_INPUT','NATIVE_RENDER','CAMERA_MATCH','PERSPECTIVE_MATCH','LIGHTING_MATCH','DEPTH_MATCH'] if fidelity_mode=='REFERENCE_GUIDED_NATIVE_LOCK' else ['REFERENCE','REDRAW','RERENDER','RESTYLE','RECOMPOSE','PROPORTIONAL_SCALE','PLACEMENT','MASK_OR_CROP','COMPOSITE'])),
            'identity_features':r.get('identity_features') or ['package_geometry','package_proportions','logo','brand_wording','label_layout','recognizable_pack_print','product_color_identity','material_appearance'],
            'note':r.get('note'),
        })
    return out


def _flatten_listing_rules(pc:dict)->dict:
    rules={}
    for r in pc.get('rules',[]):
        payload=r.get('payload') if isinstance(r,dict) else None
        if isinstance(payload,dict) and payload.get('listing_field'):
            rules[payload['listing_field']]=payload.get('constraints',{})
    return rules

def _product_truth_source_ids(request:dict)->list[str]:
    """Return only sources that explicitly belong to Product Truth.

    Market/context sources must not be attached to the Product Truth document simply because
    they exist in the same project. Field-level provenance remains in product_source_refs.
    """
    ids=[]
    explicit=request.get('product_source_ids') or []
    if not isinstance(explicit,list): explicit=[explicit]
    ids.extend(str(x) for x in explicit if x)
    source_map=request.get('product_source_refs') or (request.get('product') or {}).get('_source_refs') or {}
    if isinstance(source_map,dict):
        for refs in source_map.values():
            if not isinstance(refs,list): refs=[refs]
            ids.extend(str(x) for x in refs if x)
    product_markers=('PRODUCT_TRUTH','PRODUCT','PACK','PACKAGING','FORMULA','SPECIFICATION','SPEC','LABEL','COA','MSDS','SDS')
    for src in request.get('sources') or []:
        sid=src.get('source_id')
        blob=' '.join(str(src.get(k) or '') for k in ['kind','scope','domain','source_type','evidence_type','title']).upper()
        if sid and any(m in blob for m in product_markers): ids.append(str(sid))
    return list(dict.fromkeys(ids))


def build_project(project_dir:Path,request:dict,packs_dir:Path):
    p=Path(project_dir)
    try: st=ProjectState.load(p)
    except Exception: st=ProjectState.init(p,request.get('project_id','project'),version='0.6.12-portable-provider-package-production-receipt')
    st.data['request_hash']=stable_hash(request); st.data['runtime_version']='0.6.32-production-parameter-closure'; st.save(); _write(st.meta/'request.json',request)

    agent_plan=compile_agent_autonomy_plan(request)
    _write(p/'artifacts/agent_autonomy_plan.json',agent_plan)

    evidence={'sources':request.get('sources',[]),'assumptions':request.get('assumptions',[])}
    ep=_write(p/'artifacts/evidence.json',evidence); st.set_gate('EVIDENCE','READY_REVIEW',[ep],evidence); st.checkpoint('EVIDENCE','READY_REVIEW')

    research_gate=compile_research_gate(research_requirements_from_plan(request,agent_plan),request.get('sources',[]),request.get('research_as_of'))
    research_gate['agent_autonomy']={'plan_status':agent_plan.get('status'),'authority':(agent_plan.get('research') or {}).get('authority'),'stop_conditions':(agent_plan.get('research') or {}).get('stop_conditions') or []}
    if request.get('host_research_responses'): research_gate=apply_host_research_response(research_gate,request.get('host_research_responses'))
    rgp=_write(p/'artifacts/research_gate.json',research_gate)
    for a in research_gate.get('actions',[]):
        if a.get('status')!='RESOLVED': st.add_action(a)

    facts=request.get('product',{})
    claim_authority=compile_claim_authority(request.get('claims',[]),request.get('sources',[]))
    claims=claim_authority.get('claims') or []
    _write(p/'artifacts/claim_authority.json',claim_authority)
    truth={'product':facts,'claims':claims,'unknowns':request.get('unknowns',[]),'source_ids':_product_truth_source_ids(request),'provenance_rule':'Only explicit Product Truth sources are attached here; market/context sources remain in their own evidence domains. Field-level mappings use product_source_refs.'}
    tp=_write(p/'artifacts/product_truth.json',truth); st.set_gate('PRODUCT_TRUTH','READY_REVIEW',[tp],truth); st.checkpoint('PRODUCT_TRUTH','READY_REVIEW')
    entity=CommerceEntity(request.get('sku','SKU-1'),'SKU',facts.get('name','Unnamed product'),facts,source_ids=truth['source_ids'])
    ce={'entities':[entity.to_dict()]}; cp=_write(p/'artifacts/commerce_entity.json',ce); st.set_gate('COMMERCE_ENTITY','READY_REVIEW',[cp],ce)

    foundation_roles=required_foundation_roles(request.get('foundation_needs',{}))
    foundation={'dynamic':True,'roles':[FoundationAssetRecord(f'FND-{i+1:02d}',role,product_fidelity=request.get('product_fidelity','REFERENCE_GUIDED')).to_dict() for i,role in enumerate(foundation_roles)]}
    _write(p/'artifacts/foundation_plan.json',foundation)
    source_product_assets=_normalize_source_product_assets(request.get('source_product_assets'),[Path(request.get('source_asset_root')) if request.get('source_asset_root') else None,Path(packs_dir),Path.cwd()])
    _write(p/'artifacts/source_product_assets.json',{'status':'SOURCE_PRODUCT_ASSETS_BOUND' if source_product_assets else 'NOT_SUPPLIED','assets':source_product_assets,'count':len(source_product_assets),'principle':'Source files are design/product references by default. Pixel-level preservation is explicit-only (LOCKED_SOURCE_COMPOSITE/LOCKED_PIXEL). Reference-guided work may redraw, rerender, restyle or recompose while keeping verified product facts and selected identity cues honest.'})
    product_visual_intelligence=compile_product_visual_intelligence(facts,source_product_assets,foundation_roles,request.get('photography_contract'),request.get('cmf') or (request.get('photography_contract') or {}).get('cmf'))
    _write(p/'artifacts/product_visual_intelligence.json',product_visual_intelligence)

    t=request['target']
    lang=AssetLanguageContract(primary_locale=t.get('primary_locale','en-US'), support_locales=t.get('support_locales',[]), visible_copy_locales=t.get('visible_copy_locales') or [t.get('primary_locale','en-US')], script_subtitle_locales=t.get('script_subtitle_locales',[]), prompt_instruction_locale=t.get('prompt_instruction_locale','zh-CN'), source_lineage=t.get('language_source_ids',[]), delivery_locale=t.get('delivery_locale') or request.get('delivery_locale') or 'zh-CN')
    target=TargetContext(t.get('target_id','TARGET-1'),t['market'],t.get('jurisdiction',t['market']),t['platform_family'],t['site'],t.get('program'),t.get('surfaces',[]),t.get('category'),lang,source_ids=t.get('source_ids',[]))
    tc=target.to_dict(); tcp=_write(p/'artifacts/target_context.json',tc); st.set_gate('TARGET_CONTEXT','READY_REVIEW',[tcp],tc); st.checkpoint('TARGET_CONTEXT','READY_REVIEW')

    culture=compile_culture_context(request.get('audience_culture'))
    culture['language_profiles']=compile_language_profiles(lang.primary_locale,lang.support_locales,lang.visible_copy_locales)
    cup=_write(p/'artifacts/culture_context.json',culture); st.set_gate('CULTURE_CONTEXT','READY_REVIEW',[cup],culture); st.checkpoint('CULTURE_CONTEXT','READY_REVIEW')
    _write(p/'artifacts/language_profiles.json',culture['language_profiles'])

    domain={}
    adapter_bundle=compile_source_adapters(request.get('research_source_adapters'),request.get('research_adapter_previous_state'))
    if adapter_bundle.get('status')=='SOURCE_ADAPTERS_COMPILED':
        _write(p/'artifacts/research_source_adapter_refresh.json',{k:v for k,v in adapter_bundle.items() if k!='refresh_state'})
        _write(p/'artifacts/research_source_adapter_state.json',adapter_bundle.get('refresh_state') or {})
    adapter_datasets=adapter_bundle.get('datasets') or {}
    market_rows=list(request.get('market_rows') or []) + list(adapter_datasets.get('market_rows') or [])
    if not market_rows and request.get('market_file'):
        market_rows=load_tabular(request['market_file'],request.get('market_sheet'))
    keyword_rows=list(request.get('market_keyword_rows') or []) + list(adapter_datasets.get('market_keyword_rows') or [])
    review_rows=list(request.get('market_review_rows') or []) + list(adapter_datasets.get('market_review_rows') or [])
    competitor_rows=list(request.get('competitor_listing_rows') or request.get('market_competitor_listing_rows') or []) + list(adapter_datasets.get('competitor_listing_rows') or [])
    market_supplemental=bool(keyword_rows or review_rows or competitor_rows)
    if market_rows or market_supplemental:
        market_sources=list(request.get('market_source_records') or []) + list(adapter_bundle.get('source_records') or [])
        known={str(x.get('source_id')) for x in market_sources if x.get('source_id') not in (None,'')}
        for src in request.get('sources',[]) or []:
            if src.get('source_id') not in (None,'') and str(src.get('source_id')) not in known:
                market_sources.append(src); known.add(str(src.get('source_id')))
        research_scope={**{'market':t.get('market'),'site':t.get('site'),'platform_family':t.get('platform_family'),'category':t.get('category')},**(request.get('market_research_scope') or {})}
        domain['market']=analyze_market(market_rows or [],request.get('market_price_step'),request.get('market_config_key','configuration'),keyword_rows,request.get('market_field_map'),review_rows,competitor_rows,market_sources,request.get('market_research_as_of') or request.get('research_as_of'),research_scope,request.get('market_research_ingestion'))
        domain['market']['source_adapter_refresh']={k:v for k,v in adapter_bundle.items() if k not in {'datasets','refresh_state'}}
        _write(p/'artifacts/market_analysis.json',domain['market'])
    econ_input=request.get('offer_economics') or {}
    if econ_input.get('scenarios'):
        domain['economics']={'currency':econ_input.get('currency',t.get('currency','USD')),**economics_strategy(
            econ_input['scenarios'],
            econ_input.get('demand_signals') or request.get('demand_signals'),
            econ_input.get('behavior_rows') or econ_input.get('portfolio_behavior_rows') or request.get('portfolio_behavior_rows'),
            econ_input.get('pair_behavior_rows') or econ_input.get('portfolio_pair_rows') or request.get('portfolio_pair_rows'),
            econ_input.get('cohort_rows') or econ_input.get('portfolio_cohort_rows') or request.get('portfolio_cohort_rows'),
            econ_input.get('incrementality_rows') or econ_input.get('portfolio_incrementality_rows') or request.get('portfolio_incrementality_rows'),
            econ_input.get('switch_rows') or econ_input.get('portfolio_switch_rows') or request.get('portfolio_switch_rows'),
            econ_input.get('holdout_rows') or econ_input.get('portfolio_holdout_rows') or request.get('portfolio_holdout_rows'),
            econ_input.get('promo_response_rows') or request.get('promo_response_rows'),
            econ_input.get('bundle_affinity_rows') or request.get('bundle_affinity_rows'),
            econ_input.get('repeat_cycle_rows') or econ_input.get('replacement_cycle_rows') or request.get('repeat_cycle_rows')
        )}
    elif econ_input.get('price') is not None and econ_input.get('costs') is not None:
        domain['economics']={'currency':econ_input.get('currency',t.get('currency','USD')),**unit_economics(econ_input['price'],econ_input['costs'],econ_input.get('target_contribution',econ_input.get('minimum_contribution',0)))}
    else:
        flat_keys=['landed_cost','platform_fee','fulfillment','affiliate_commission','ad_cost','tax','refund_allowance']
        if econ_input.get('price') is not None and any(k in econ_input for k in flat_keys):
            costs={k:econ_input.get(k) for k in flat_keys}
            domain['economics']={'currency':econ_input.get('currency',t.get('currency','USD')),**unit_economics(econ_input['price'],costs,econ_input.get('target_contribution',econ_input.get('minimum_contribution',0)))}
        else:
            domain['economics']={'currency':econ_input.get('currency',t.get('currency','USD')),'status':'INSUFFICIENT_DATA','missing':['price','costs']}
    ed=domain['economics']; ecp=_write(p/'artifacts/offer_economics.json',ed); st.set_gate('OFFER_ECONOMICS','READY_REVIEW',[ecp],ed)
    pricing_economics=compile_pricing_economics_authority(request,domain.get('market'),domain.get('economics'))
    domain['pricing_economics_authority']=pricing_economics
    if isinstance(domain.get('economics'),dict):
        domain['economics']['pricing_economics_authority']=pricing_economics
    _write(p/'artifacts/pricing_economics_authority.json',pricing_economics)
    if request.get('ad_rows'):
        domain['ads']=analyze_ad_portfolio(request.get('ad_rows') or [], econ_input.get('price'), econ_input.get('costs'), request.get('ad_thresholds')); _write(p/'artifacts/ad_analysis.json',domain['ads'])
    elif request.get('ad_analysis'):
        aa=request['ad_analysis']; domain['ads']=analyze_ads(aa.get('ad_data',{}),aa.get('price'),aa.get('costs'),aa.get('thresholds')); _write(p/'artifacts/ad_analysis.json',domain['ads'])
    if request.get('feedback_rows'):
        domain['feedback']=analyze_feedback(request['feedback_rows']); _write(p/'artifacts/feedback_analysis.json',domain['feedback'])
    if request.get('experiment'):
        x=request['experiment']; domain['experiment']=compile_experiment_analysis(x); _write(p/'artifacts/experiment_analysis.json',domain['experiment'])

    # v0.6.25: decision questions/frameworks are compiled after Listing/current task signals are known.
    # No generic four-question journey or all-framework list is injected here.
    questions=[]

    required_rules=request.get('required_platform_rules',[])
    platform_target={**t,'visible_copy_locales':lang.visible_copy_locales}
    pc=PlatformCompiler(packs_dir).compile(platform_target,required_rules)
    pcp=_write(p/'artifacts/platform_compile.json',pc)
    research_blocks_platform=any('PLATFORM_COMPILE' in (x.get('required_for') or []) and x.get('status')!='RESOLVED' for x in research_gate.get('actions',[]))
    platform_ready=(pc['status']=='VERIFIED_FOR_REQUEST' and not research_blocks_platform) or bool(request.get('planning_only'))
    st.set_gate('PLATFORM_COMPILE','READY_REVIEW' if platform_ready else 'HOLD',[pcp],pc)
    for a in pc.get('research_actions',[]): st.add_action(a)
    if not platform_ready:
        # Strategy authoring continues with known evidence. Only submission-sensitive readiness remains on HOLD.
        st.checkpoint('PLATFORM_COMPILE','HOLD_RESEARCH_REQUIRED_STRATEGY_CONTINUES')

    # Listing 2.0: platform field contracts + evidence trace. Semantic copy generation stays upstream.
    if request.get('listing_input'):
        li=request['listing_input']; listing_rules={**_flatten_listing_rules(pc),**li.get('rules',{})}
        listing_fields=dict(li.get('fields',{}))
        if li.get('terminology_memory') is not None and '_terminology_memory' not in listing_fields: listing_fields['_terminology_memory']=li.get('terminology_memory')
        host_authoring_responses=li.get('host_authoring_responses') or request.get('host_copy_authoring_responses')
        host_authoring_apply={'status':'NO_HOST_AUTHORING_RESPONSES','applied':[],'rejected':[]}
        if host_authoring_responses:
            listing_fields,host_authoring_apply=apply_host_copy_authoring_responses(listing_fields,host_authoring_responses)
            _write(p/'artifacts/listing_copy_host_authoring_apply.json',host_authoring_apply)
        compiled_listing=compile_listing(listing_fields,facts,claims,listing_rules,lang.to_dict(),li.get('keywords',[]),tc)
        compiled_listing['host_authoring_apply']=host_authoring_apply
        domain['listing']={'compiled':compiled_listing,'keywords':compiled_listing.get('keywords',{}),'field_contracts':compiled_listing.get('field_contracts',[]),'status':compiled_listing.get('status')}
        _write(p/'artifacts/listing_analysis.json',domain['listing'])
        _write(p/'artifacts/listing_final_copy.json',compiled_listing.get('final_copy_workflow') or {})
        _write(p/'artifacts/listing_copy_authoring_tasks.json',((compiled_listing.get('copy_authoring_iteration_plan') or {}).get('authoring_tasks') or []))
        _write(p/'artifacts/listing_copy_revision_tasks.json',((compiled_listing.get('copy_authoring_iteration_plan') or {}).get('revision_tasks') or []))
        _write(p/'artifacts/listing_copy_review_tasks.json',((compiled_listing.get('copy_authoring_iteration_plan') or {}).get('review_tasks') or []))
        _write(p/'artifacts/listing_copy_host_authoring_requests.json',{'authoring_tasks':((compiled_listing.get('copy_authoring_iteration_plan') or {}).get('authoring_tasks') or []),'revision_tasks':((compiled_listing.get('copy_authoring_iteration_plan') or {}).get('revision_tasks') or []),'terminology_memory':compiled_listing.get('terminology_memory') or [],'response_contract':{'required':['locale','field','copy'],'recommended':['delivery_translation','delivery_note','version_id','parent_version_id','task_id','created_at','author','generation_notes'],'delivery_locale':lang.delivery_locale,'companion_rule':'If locale differs from delivery_locale, return a concise delivery_translation in the delivery locale. For search terms/keywords, explain intent rather than forcing a literal translation.','boundary':'A host response creates a new draft version only. Explicit professional review of that exact version is still required for APPROVED_FINAL.'}})
        for pkg in (compiled_listing.get('final_copy_workflow') or {}).get('packages',[]):
            loc=str(pkg.get('locale') or 'unknown').replace('/','_')
            lines=[f"# Listing Final Copy — {loc}",'',f"Status: {pkg.get('status')}",'']
            for row in pkg.get('fields',[]):
                lines += [f"## {row.get('field')}",f"Release: {row.get('release_status')}",f"Version: {row.get('current_version_id') or 'LEGACY/UNVERSIONED'}",'',str(row.get('authored_copy') or ''),'']
            outp=p/'artifacts/listing_final_copy'/f'{loc}.md'; outp.parent.mkdir(parents=True,exist_ok=True); outp.write_text('\n'.join(lines),encoding='utf-8')
    _write(p/'artifacts/domain_analysis.json',domain)

    families=derive_task_content_families(request,agent_plan,available_families=DEFAULT_FAMILIES)
    selected_frameworks=selected_decision_frameworks(request,agent_plan)
    agent_plan['strategy_frameworks']=selected_frameworks
    agent_plan['content_scope_authority']='EXPLICIT_TASK_SIGNALS_ONLY'
    agent_plan['target_surfaces_are_constraints_not_content_quotas']=True
    question_authority=compile_decision_question_authority(
        request,agent_plan,
        listing=((domain.get('listing') or {}).get('compiled') or {}),
        active_families=families,
    )
    questions=list(question_authority.get('shopper_questions') or [])
    agent_plan['decision_question_authority']={
        'status':question_authority.get('status'),
        'question_count':question_authority.get('question_count',0),
        'decision_gap_count':len(question_authority.get('decision_gaps') or []),
        'synthetic_default_questions':False,
    }
    _write(p/'artifacts/agent_autonomy_plan.json',agent_plan)
    dqa=_write(p/'artifacts/decision_question_authority.json',question_authority)
    traces=compile_decision_trace_rows(question_authority,selected_frameworks)
    persuasion_requested=[x for x in selected_frameworks if x in {'AIDA','FABE','4P'}]
    persuasion=compile_persuasion_frameworks(questions,facts,domain.get('economics'),persuasion_requested)
    dd={
        'status':'DECISION_TRACE_COMPILED' if traces else 'NO_DECISION_TRACE_REQUIRED',
        'traces':traces,
        'frameworks':selected_frameworks,
        'framework_selection_authority':'EXPLICIT_AGENT_OR_USER_ONLY',
        'fixed_framework_quota':False,
        'synthetic_default_questions':False,
        'question_authority_artifact':dqa,
        'persuasion':persuasion,
        'culture_status':culture.get('status'),'race_ethnicity':culture.get('race_ethnicity'),'intersectionality':culture.get('intersectionality'),
        'domain_inputs':{'market':domain.get('market',{}).get('status'),'economics':domain.get('economics',{}).get('status'),'ads':domain.get('ads',{}).get('status'),'feedback':domain.get('feedback',{}).get('status'),'experiment':domain.get('experiment',{}).get('status')},
        'principle':'Decision Trace records current authored/grounded decision jobs. Question order does not assign funnel/RACE stage, and runtime capability does not select a framework.'
    }
    dp=_write(p/'artifacts/decision_trace.json',dd)
    st.set_gate('DECISION','READY_REVIEW',[dp,dqa],dd); st.checkpoint('DECISION','READY_REVIEW')

    content_requiredness=compile_required_content_families(request,agent_plan,families,question_authority)
    gate_scope=compile_gate_scope(request,families,content_requiredness,question_authority)
    _write(p/'artifacts/content_requiredness.json',content_requiredness)
    _write(p/'artifacts/gate_scope.json',gate_scope)
    for gate,meta in gate_scope.get('gates',{}).items():
        st.set_gate_scope(
            gate,
            required_for_current_scope=meta.get('required_for_current_scope',False),
            blocking_for_current_scope=meta.get('blocking_for_current_scope',False),
            scope_reason=meta.get('scope_reason',''),
            scope_status=meta.get('scope_status'),
        )
    required_by_family={row.get('family'):bool(row.get('required_for_current_scope')) for row in content_requiredness.get('rows',[])}
    capabilities=set(pc.get('capabilities',[])); objects=[]
    requested_surfaces=set(t.get('surfaces') or [])
    supported_surfaces=set(pc.get('surfaces') or [])
    for fam in families:
        fam_surface=FAMILY_SURFACE.get(fam)
        # Platform packs are evidence/submission authorities, not a strategy censorship list.
        # If the user requested a surface, keep the strategic object even when exact platform evidence for that surface is missing.
        capability_verified=(not capabilities) or fam in capabilities or fam in {'MEASUREMENT','COMPLIANCE'}
        surface_verified=(not fam_surface) or (fam_surface in supported_surfaces)
        oid='CO-'+stable_hash([request.get('project_id'),target.target_id,fam,len(objects)])[:12]
        payload={'shopper_questions':questions,'platform_status':pc['status'],'business_capabilities':pc.get('business_capabilities',{}),'culture_status':culture.get('status'),'platform_capability_status':'VERIFIED_OR_DECLARED' if capability_verified and surface_verified else 'STRATEGY_PLANNING_RESEARCH_REQUIRED','platform_capability_verified':capability_verified,'platform_surface_verified':surface_verified,'target_surface_requested':(not fam_surface) or (not requested_surfaces) or (fam_surface in requested_surfaces)}
        if fam=='LISTING' and domain.get('listing'): payload['listing_contract']=domain['listing']
        obj=ContentObject(oid,FAMILY_KIND.get(fam,fam.lower()),fam,'Resolve shopper decision job',target.target_id,FAMILY_SURFACE.get(fam),required_by_family.get(fam,False),
            payload=payload,source_ids=truth['source_ids'],upstream_hashes={'PRODUCT_TRUTH':st.data['gates']['PRODUCT_TRUTH']['authority_hash'],'TARGET_CONTEXT':st.data['gates']['TARGET_CONTEXT']['authority_hash'],'CULTURE_CONTEXT':st.data['gates']['CULTURE_CONTEXT']['authority_hash']},language=lang)
        objects.append(obj.to_dict()); _write(p/f'artifacts/objects/{oid}.json',obj.to_dict())
    cg={'objects':objects,'dynamic_count':len(objects),'fixed_count_authority':False,'scope_authority':'AGENT_OR_TASK_DERIVED','agent_plan_status':agent_plan.get('status'),
        'requiredness':content_requiredness,'required_object_count':sum(1 for o in objects if o.get('required')),
        'supporting_object_count':sum(1 for o in objects if not o.get('required'))}
    cgp=_write(p/'artifacts/content_graph.json',cg); st.set_gate('CONTENT_GRAPH','READY_REVIEW',[cgp],cg); st.checkpoint('CONTENT_GRAPH','READY_REVIEW')

    market_fit_contract=compile_market_evidence_fit_contract(request,domain.get('market'))
    _write(p/'artifacts/market_evidence_fit_contract.json',market_fit_contract)
    market_theme_jobs=list(market_fit_contract.get('approved_asset_jobs') or []) + list(request.get('market_theme_fit') or [])
    category_family=infer_category_family(request)
    architecture=build_asset_architecture(request.get('project_id','project'),tc,questions,objects,request.get('asset_jobs'),{'listing_objections':((domain.get('listing') or {}).get('compiled') or {}).get('objection_resolution_plan',[]),'feedback_issues':(domain.get('feedback') or {}).get('issues',[]),'market_theme_jobs':market_theme_jobs},category_family)
    surface_architecture=compile_surface_architecture(tc,objects,architecture.get('assets') or [],pc)
    architecture['assets']=surface_architecture.get('assets') or architecture.get('assets') or []
    architecture['surface_architecture']=surface_architecture
    _write(p/'artifacts/surface_architecture.json',surface_architecture)
    _write(p/'artifacts/decision_content_graph.json',{'objects':surface_architecture.get('decision_content_objects') or [],'dynamic_count':len(surface_architecture.get('decision_content_objects') or []),'fixed_count_authority':False,'principle':'One object per actual decision/content job after information assetization; not one object per generic family quota.'})

    photography_validation=None
    if request.get('photography_contract') is not None:
        photography_validation=validate_photography_contract(request['photography_contract']); _write(p/'artifacts/photography_validation.json',photography_validation)
    curation=compile_curation(request.get('creative_references'),request.get('competitor_visual_patterns'))
    _write(p/'artifacts/curation.json',curation)
    cmf=compile_cmf(request.get('cmf') or (request.get('photography_contract') or {}).get('cmf'))
    _write(p/'artifacts/cmf_contract.json',cmf)
    inclusive=compile_inclusive_photography(culture,request.get('photography_contract'),architecture.get('assets') or [])
    _write(p/'artifacts/inclusive_photography.json',inclusive)
    creative_opportunity_universe=compile_creative_opportunity_universe(
        truth,product_visual_intelligence,category_family,architecture.get('assets') or [],curation,culture,tc,
        agent_opportunities=agent_creative_opportunities(agent_plan),
    )
    _write(p/'artifacts/creative_opportunity_universe.json',creative_opportunity_universe)
    council=compile_creative_council(request.get('creative_directions') or agent_creative_directions(agent_plan),curation,truth,culture,pc,category_family,[a.get('decision_intent') for a in architecture.get('assets') or []],creative_opportunity_universe)
    _write(p/'artifacts/creative_council.json',council)
    architecture=apply_creative_system_to_assets(architecture,council,cmf,request.get('photography_contract'))
    inclusive=compile_inclusive_photography(culture,request.get('photography_contract'),architecture.get('assets') or [])
    _write(p/'artifacts/inclusive_photography.json',inclusive)
    creative_anchors=compile_creative_anchor_plan(council,architecture,product_visual_intelligence,cmf)
    _write(p/'artifacts/creative_anchor_plan.json',creative_anchors)
    for _asset in architecture.get('assets') or []:
        _asset['product_visual_intelligence']={'status':product_visual_intelligence.get('status'),'appearance_facts':product_visual_intelligence.get('appearance_facts'),'capture_risks':product_visual_intelligence.get('capture_risks'),'identity_faces':product_visual_intelligence.get('identity_faces')}
        _asset['creative_anchor_plan']={'direction_id':creative_anchors.get('direction_id'),'roles':[x.get('anchor_role') for x in creative_anchors.get('roles') or []]}
    aap=_write(p/'artifacts/asset_architecture.json',architecture); st.set_gate('ASSET_ARCHITECTURE','READY_REVIEW',[aap],architecture); st.checkpoint('ASSET_ARCHITECTURE','READY_REVIEW')
    creative={'design_system_status':'DIRECTION_SELECTED' if council.get('status')=='SELECTED' else 'TO_BE_CURATED','content_object_ids':[o['object_id'] for o in objects if o['family'] in {'VISUAL','VIDEO','CREATOR_AFFILIATE','PAID'}],
              'positive_first':True,'photography_contract_required':bool(request.get('photography_contract')),'photography_planning_is_advisory':True,'photography_validation':photography_validation,
              'foundation_asset_ids':[x['asset_id'] for x in foundation['roles']], 'source_truth_binding':st.data['gates']['PRODUCT_TRUTH']['authority_hash'],
              'culture_context_hash':st.data['gates']['CULTURE_CONTEXT']['authority_hash'],'language_profiles':culture['language_profiles'],
              'curation':curation,'creative_opportunity_universe':creative_opportunity_universe,'creative_council':council,'cmf':cmf,'inclusive_photography':inclusive,
              'surface_architecture':surface_architecture,'asset_expression_assignment':architecture.get('creative_system_assignment'),'product_visual_intelligence':product_visual_intelligence,'creative_anchor_plan':creative_anchors,
              'agent_autonomy_plan':agent_plan}
    crp=_write(p/'artifacts/creative_contract.json',creative)
    creative_ready=council.get('status')=='SELECTED'
    creative['photography_validation_is_advisory']=True
    creative['photography_validation_blocks_project_completion']=False
    st.set_gate('CREATIVE','READY_REVIEW' if creative_ready else 'HOLD',[crp],creative)

    video_plan=build_video_creator_plan(request.get('project_id','project'),objects,questions,lang.to_dict(),request.get('video_jobs'),assets=architecture.get('assets'),creative_council=council)
    _write(p/'artifacts/video_creator_plan.json',video_plan)
    paid_campaigns=compile_paid_campaign_architecture(request.get('project_id','project'),tc,architecture.get('assets') or [],truth,domain.get('economics'),domain.get('ads'),request.get('paid_campaigns'),objects)
    _write(p/'artifacts/paid_campaign_architecture.json',paid_campaigns)
    seven_agent_synthesis=compile_seven_agent_synthesis(domain=domain,architecture=architecture,video_plan=video_plan,paid_campaigns=paid_campaigns,source_product_assets=source_product_assets)
    seven_tool_continuity=compile_seven_tool_continuity(
        domain=domain,architecture=architecture,video_plan=video_plan,paid_campaigns=paid_campaigns,
        pricing_economics=domain.get('pricing_economics_authority'))
    seven_agent_synthesis['v0636_continuity']=seven_tool_continuity
    seven_agent_synthesis['capabilities']=seven_tool_continuity.get('capabilities') or seven_agent_synthesis.get('capabilities') or []
    seven_agent_synthesis['all_seven_first_class']=seven_tool_continuity.get('all_seven_first_class')
    seven_agent_synthesis['pricing_economics_integrity']=seven_tool_continuity.get('pricing_economics_integrity')
    _write(p/'artifacts/seven_tool_continuity.json',seven_tool_continuity)
    architecture['commerce_capability_inputs']=seven_agent_synthesis.get('asset_inputs') or {}
    for _asset in architecture.get('assets') or []:
        _asset['commerce_context']=seven_agent_synthesis.get('asset_inputs') or {}
    _write(p/'artifacts/seven_agent_synthesis.json',seven_agent_synthesis)
    _write(p/'artifacts/asset_architecture.json',architecture)
    creative['video_creator_plan']=video_plan
    creative['paid_campaign_architecture']=paid_campaigns
    creative['decision_content_graph']=surface_architecture.get('decision_content_objects') or []
    _write(p/'artifacts/creative_contract.json',creative)

    compliance=compile_compliance(truth,claims,domain.get('listing'),architecture.get('assets'),pc,research_gate)
    cop=_write(p/'artifacts/compliance_report.json',compliance)

    # Knowledge / ontology / prompt authorities are compiled into a project-specific reasoning context.
    pricing_consumers=(domain.get('pricing_economics_authority') or {}).get('downstream_consumers') or {}
    if domain.get('listing'):
        domain['listing']['pricing_offer_context']=pricing_consumers.get('listing_creative') or {}
        _write(p/'artifacts/listing_pricing_offer_context.json',domain['listing']['pricing_offer_context'])
    if domain.get('ads'):
        domain['ads']['pricing_economics_context']=pricing_consumers.get('advertising_optimization') or {}
        _write(p/'artifacts/ads_pricing_economics_context.json',domain['ads']['pricing_economics_context'])
    _write(p/'artifacts/product_strategy_pricing_context.json',pricing_consumers.get('product_strategy') or {})

    strategy_context=compile_strategy_reasoning_context(request)
    _write(p/'artifacts/strategy_reasoning_context.json',strategy_context)

    # Strategy Authority: positive commercial design is the main deliverable; governance remains a background guardrail.
    strategy_request=dict(request); strategy_request['claims']=claims; strategy_request['_market_evidence_fit_contract']=market_fit_contract; strategy_request['_agent_autonomy_plan']=agent_plan
    strategy=build_master_strategy(
        strategy_request, truth=truth, research_gate=research_gate, market=domain.get('market'), economics=domain.get('economics'),
        culture=culture, platform_compile=pc, creative=creative, photography_validation=photography_validation,
        asset_architecture=architecture, compliance=compliance, experiment=domain.get('experiment'), listing=domain.get('listing'), ads=domain.get('ads'), feedback=domain.get('feedback'), authoring_context=strategy_context)
    strategy_host_request=build_strategy_host_authoring_request(strategy,strategy_context,request.get('strategy_annotations'))
    _write(p/'artifacts/strategy_host_authoring_request.json',strategy_host_request)
    strategy=apply_strategy_annotations(strategy,request.get('strategy_annotations'))
    # Bind Strategy §5 photography/CMF decisions back into video production contracts before final materialization.
    video_plan=enrich_video_plan_with_strategy(video_plan,strategy,source_product_assets=source_product_assets,culture=culture)
    creative['video_creator_plan']=video_plan
    _write(p/'artifacts/video_creator_plan.json',video_plan)
    _write(p/'artifacts/creative_contract.json',creative)
    try:
        strategy['sections']['05_visual_photography_strategy']['video_creator_plan']=video_plan
    except Exception:
        pass
    strategy_artifacts=materialize_strategy(p/'artifacts/strategy',strategy)
    sap=_write(p/'artifacts/strategy_authority.json',strategy)
    revision_routing=(((strategy.get('sections') or {}).get('09_risk_measurement_priority_next_steps') or {}).get('performance_learning') or {}).get('strategy_revision_routing') or {'status':'NO_REVISION_SIGNAL_SUPPLIED'}
    _write(p/'artifacts/strategy_revision_routing.json',revision_routing)
    core=((strategy.get('sections') or {}).get('04_marketing_core_strategy') or {})
    visual=((strategy.get('sections') or {}).get('05_visual_photography_strategy') or {})
    perf=(((strategy.get('sections') or {}).get('09_risk_measurement_priority_next_steps') or {}).get('performance_learning') or {})
    # Capability integration is materialized after asset/production compilation so the map reflects the actual project data flow.
    st.set_gate('STRATEGY_AUTHORITY','READY_REVIEW',[sap,strategy_artifacts['markdown']],strategy)
    st.checkpoint('STRATEGY_AUTHORITY','READY_REVIEW')

    asset_compile={'status':'NOT_REQUESTED','asset_count':0}
    if request.get('compile_assets'):
        asset_compile=compile_asset_packages(p/'artifacts/asset_packages',architecture['assets'],facts,tc,culture,lang.to_dict(),culture['language_profiles'],request.get('photography_contract'),request.get('production_provider_preferences'),strategy,source_product_assets)
        asset_compile['validation']=validate_asset_packages(p/'artifacts/asset_packages')
        acp=_write(p/'artifacts/asset_compile.json',asset_compile); st.set_gate('ASSET_COMPILE','READY_REVIEW' if creative_ready and asset_compile['validation']['pass'] else 'HOLD',[acp],asset_compile)
    else:
        acp=_write(p/'artifacts/asset_compile.json',asset_compile); st.set_gate('ASSET_COMPILE','PENDING',[acp],asset_compile)

    production_run={'status':'NOT_REQUESTED','assets':[]}
    production_artifacts=[]
    if request_intent_present(request,'production_run') and request.get('compile_assets') and asset_compile.get('status')=='COMPILED':
        pr=request.get('production_run') or {}
        production_run=build_production_run(p/'artifacts/asset_packages',request.get('production_provider_preferences'),pr.get('asset_ids'),pr.get('revision_scope'))
        provider_jobs=materialize_provider_jobs(p/'artifacts/asset_packages',production_run,p/'artifacts/provider_jobs')
        production_run['provider_jobs']=provider_jobs
        if pr.get('results'): production_run=apply_production_result(production_run,pr.get('results'))
        elif pr.get('ingest_provider_results'): production_run=ingest_provider_job_results(production_run,p/'artifacts/provider_jobs')
        prp=_write(p/'artifacts/production_run.json',production_run); production_artifacts=[prp,str(p/'artifacts/provider_jobs/PROVIDER_JOB_INDEX.json')]
        st.set_gate('PRODUCTION','READY_REVIEW' if production_run.get('status')=='COMPLETE' else 'PENDING',production_artifacts,production_run)
    else:
        st.set_gate('PRODUCTION','PENDING',[],production_run)

    agent_next_action=compile_agent_next_action(
        agent_plan,request=request,research_gate=research_gate,asset_architecture=architecture,
        creative_council=council,compliance=compliance,production_run=production_run,
        gate_scope=gate_scope,content_requiredness=content_requiredness,
    )
    agent_next_action=augment_agent_next_action(agent_next_action,question_authority)
    _write(p/'artifacts/agent_next_action.json',agent_next_action)

    def _capability_row(name,input_active,input_status,consumers,downstream_ok=True):
        status='INTEGRATED_ACTIVE' if input_active and downstream_ok else ('INTEGRATED_INACTIVE_NO_PROJECT_INPUT' if not input_active else 'INTEGRATION_GAP')
        return {'capability':name,'project_input_active':bool(input_active),'input_status':input_status,'runtime_wiring_status':status,'consumers':consumers,'integrated':status!='INTEGRATION_GAP'}
    final_copy=((domain.get('listing') or {}).get('compiled') or {}).get('final_copy_workflow') or {}
    integration_map={
      'status':'CAPABILITY_INTEGRATION_MAP_COMPILED','principle':'A capability counts as integrated only when its output changes or constrains Strategy Authority, Dynamic Asset Architecture, Final Copy, per-asset production contracts, Provider Jobs, or Measurement/Revision Routing. File existence, registry count or passing tests alone do not count.',
      'capabilities':[
        _capability_row('PRODUCT_TRUTH',True,'READY_REVIEW',['Strategy §2 Value Ladder','Compliance','Listing/Asset/Final Copy truth boundary'],bool(truth)),
        _capability_row('MARKET_COMPETITOR_CUSTOMER',bool(domain.get('market')),(domain.get('market') or {}).get('status','NOT_SUPPLIED'),['Strategy §3 Market','Strategy §4 Quality-weighted Evidence Reconciliation','Market Evidence Fit Contract → Asset Architecture after explicit fit'],bool(domain.get('market'))),
        _capability_row('SOURCE_ADAPTER_RESEARCH_QUALITY',bool(request.get('research_source_adapters') or request.get('market_source_records')),adapter_bundle.get('status') or (domain.get('market') or {}).get('research_quality',{}).get('status','NOT_SUPPLIED'),['Market analysis','Evidence-quality weighting','Research refresh/risk register'],True),
        _capability_row('PRODUCT_SKU_OFFER_ECONOMICS',bool(request.get('offer_economics')), (domain.get('economics') or {}).get('status','NOT_SUPPLIED'),['Strategy §4 Product/SKU/Offer','Ads economic guardrails','Strategy §9 portfolio/incrementality'],bool(domain.get('economics'))),
        _capability_row('POSITIONING_MESSAGE',True,'COMPILED',['Strategy §4 Positioning/Message','Listing Strategy','Platform Content Matrix','Asset Portfolio'],bool(core.get('positioning'))),
        _capability_row('HOST_STRATEGY_AUTHORING',bool(request.get('strategy_annotations')),'HOST_ANNOTATIONS_SUPPLIED' if request.get('strategy_annotations') else 'AVAILABLE_NOT_SUPPLIED',['Strategy Authority interpretation/WHY/value translation','Protected-boundary annotation application'],True),
        _capability_row('LISTING_SEARCH',bool(domain.get('listing')),(domain.get('listing') or {}).get('status','NOT_SUPPLIED'),['Strategy §4 Listing','Dynamic Asset objection inputs','Claim/source trace'],bool(domain.get('listing'))),
        _capability_row('FINAL_COPY_WORKFLOW',bool(request.get('listing_input')),final_copy.get('status','NOT_SUPPLIED'),['Final Copy packages','Author/Revision/Review tasks','Delivery Builder'],bool(domain.get('listing'))),
        _capability_row('HOST_COPY_AUTHORING',bool((request.get('listing_input') or {}).get('host_authoring_responses') or request.get('host_copy_authoring_responses')),'HOST_RESPONSES_SUPPLIED' if ((request.get('listing_input') or {}).get('host_authoring_responses') or request.get('host_copy_authoring_responses')) else 'NOT_SUPPLIED',['Copy version creation','Hard-check rerun','Version-bound re-review'],True),
        _capability_row('ADS',bool(domain.get('ads')),(domain.get('ads') or {}).get('status','NOT_SUPPLIED'),['Strategy §9 diagnostics','Strategy Revision Routing'],(not domain.get('ads')) or revision_routing.get('status')=='STRATEGY_REVISION_ROUTING_COMPILED'),
        _capability_row('FEEDBACK',bool(domain.get('feedback')),(domain.get('feedback') or {}).get('status','NOT_SUPPLIED'),['Dynamic Asset communication issues','Strategy §9 local revision routing'],(not domain.get('feedback')) or revision_routing.get('status')=='STRATEGY_REVISION_ROUTING_COMPILED'),
        _capability_row('EXPERIMENT_CAUSAL',bool(domain.get('experiment')),(domain.get('experiment') or {}).get('status','NOT_SUPPLIED'),['Strategy §9 causal design','Measurement architecture'],True),
        _capability_row('CULTURE_INTERSECTIONALITY',bool(request.get('audience_culture')),culture.get('status','NOT_SUPPLIED'),['Strategy §3/8','Casting/visual/copy implications'],True),
        _capability_row('VISUAL_PHOTOGRAPHY_CMF',bool(request.get('photography_contract') or request.get('visual_strategy') or request.get('cmf')),creative.get('design_system_status'),['Strategy §5','Asset 02/03 contracts','Provider production contracts'],bool(visual)),
        _capability_row('DYNAMIC_ASSET_CURATION',True,architecture.get('status'),['Strategy §5 portfolio','00–11 per-asset packages','Provider jobs when production requested'],architecture.get('status')=='DYNAMIC_ASSET_ARCHITECTURE'),
        _capability_row('KNOWLEDGE_ONTOLOGY_PROMPTS',True,strategy_context.get('status'),['Section authority bindings across 01–09'],bool(strategy_context.get('selected_prompts')) and bool(strategy_context.get('selected_knowledge'))),
        _capability_row('COMPLIANCE',True,compliance.get('status'),['Strategy §9 risk','Claim/source publication boundary','Execution readiness'],True),
        _capability_row('ASSET_COMPILER',bool(request.get('compile_assets')),asset_compile.get('status'),['Per-asset 00–11 production packages','Package validation'],(not request.get('compile_assets')) or asset_compile.get('status')=='COMPILED'),
        _capability_row('PROVIDER_PRODUCTION',request_intent_present(request,'production_run'),production_run.get('status'),['Frozen Provider Jobs','Provider Result ingestion','Review workspace'],(not request_intent_present(request,'production_run')) or bool(production_run.get('provider_jobs'))),
        _capability_row('REVIEW_LOCAL_REVISION_PACKAGE_HASH',bool(request.get('compile_assets')),'WIRED' if request.get('compile_assets') else 'NOT_REQUESTED',['Asset package hash binding','Review workspace','Local revision scope','Provider result/package-hash validation'],True),
        _capability_row('MEASUREMENT_REVISION_INTEGRATION',bool(domain.get('ads') or domain.get('feedback') or domain.get('experiment')),revision_routing.get('status'),['Strategy §9','Decision Index','Local revision candidates'],True),
        _capability_row('POST_PRODUCTION_LEARNING_LOOP',(p/'artifacts/learning_latest.json').exists(),'LEARNING_APPLIED' if (p/'artifacts/learning_latest.json').exists() else 'NOT_YET_APPLIED',['Local Revision lineage','Measurement gate','Learning ledger','Strategy Authority local-layer overlays'],True),
      ],
      'market_evidence_fit':{'status':market_fit_contract.get('status'),'candidate_count':len(market_fit_contract.get('candidates') or []),'approved_asset_job_count':len(market_fit_contract.get('approved_asset_jobs') or [])},
      'revision_routing_status':revision_routing.get('status'),'asset_compile_status':asset_compile.get('status'),'production_status':production_run.get('status')
    }
    integration_map['integration_gaps']=[x['capability'] for x in integration_map['capabilities'] if x.get('runtime_wiring_status')=='INTEGRATION_GAP']
    _write(p/'artifacts/capability_integration_map.json',integration_map)

    execution={'objects':[{'object_id':o['object_id'],'status':'AWAITING_REVIEW' if creative_ready else 'WAITING_CREATIVE_CONTRACT','one_physical_object_one_contract':True} for o in objects],
               'strategy_authority':{'status':strategy.get('status'),'artifact':str(p/'artifacts/strategy/MASTER_STRATEGY_CN.md')},'asset_packages':asset_compile,'production_run':production_run,'video_creator_plan':video_plan,'compliance':compliance,'prompt_state_isolation':True,'research_gate':research_gate}
    exp=_write(p/'artifacts/execution_contract.json',execution); execution_ready=creative_ready and compliance.get('status')!='HOLD' and (not request.get('compile_assets') or asset_compile.get('status')=='COMPILED')
    st.set_gate('EXECUTION','READY_REVIEW' if execution_ready else 'PENDING',[exp],execution); st.checkpoint('EXECUTION','READY_REVIEW' if st.data['gates']['EXECUTION']['status']=='READY_REVIEW' else 'PENDING_CONTRACTS')
    # final_ready is derived from current-scope closure; never reset it as a static pipeline flag.
    refresh_review_workspace(p,st)
    return st.data
