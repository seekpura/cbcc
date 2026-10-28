from __future__ import annotations
from collections import defaultdict
from typing import Any
import hashlib
from .category_strategy import classify_decision_intent


def _f(v, default=0.0):
    try: return default if v in (None,'') else float(v)
    except (TypeError,ValueError): return default




def _clamp(v:float, lo:float=0.0, hi:float=1.0)->float:
    return max(lo,min(hi,float(v)))


def _source_quality_factor(source_ids:list[str]|None, market_depth:dict[str,Any], dataset_name:str)->dict[str,Any]:
    """Deterministically weight current-market evidence by documented research quality.

    Missing metadata reduces confidence but does not zero the evidence. Product Truth and explicit own
    shopper questions are not routed through this function. No source prestige is inferred.
    """
    rq=(market_depth.get('research_quality') or {}) if isinstance(market_depth,dict) else {}
    datasets={str(x.get('dataset')):x for x in (rq.get('datasets') or [])}
    sources={str(x.get('source_id')):x for x in (rq.get('sources') or []) if x.get('source_id') not in (None,'')}
    ds=datasets.get(dataset_name) or {}
    coverage=ds.get('source_id_coverage_ratio'); resolved=ds.get('resolved_source_ratio')
    traceability=1.0
    if ds:
        c=_clamp(_f(coverage,0.0)); r=_clamp(_f(resolved,0.0)); traceability=max(0.25,(c*r)**0.5)
    ids=[str(x) for x in (source_ids or []) if x not in (None,'')]
    cards=[sources[x] for x in ids if x in sources]
    if not cards:
        return {'multiplier':round(0.55*traceability,4),'traceability':round(traceability,4),'freshness':0.65,'representativeness':0.6,'scope_match':0.75,'source_quality':0.75,'source_ids':ids,'resolved_source_ids':[],'status':'QUALITY_METADATA_PARTIAL_OR_UNRESOLVED'}
    freshness_map={'WITHIN_DECLARED_FRESHNESS_WINDOW':1.0,'AGE_RECORDED_NO_THRESHOLD':0.82,'DATE_NOT_SUPPLIED':0.65,'OUTSIDE_DECLARED_FRESHNESS_WINDOW':0.25,'OBSERVATION_AFTER_AS_OF_REVIEW':0.35}
    rep_map={'REPRESENTATIVENESS_DOCUMENTED_NOT_PROVEN':0.9,'REPRESENTATIVENESS_UNKNOWN':0.6}
    q_tier={'HIGH':0.95,'MEDIUM':0.8,'LOW':0.55,'FIRST_PARTY':0.95,'PRIMARY':0.95,'SECONDARY':0.75}
    fs=[]; rs=[]; ss=[]; qs=[]
    for c in cards:
        fs.append(freshness_map.get(str(c.get('freshness_status') or ''),0.7))
        rs.append(rep_map.get(str(c.get('representativeness_status') or ''),0.65))
        ss.append(0.35 if c.get('scope_mismatches') else 1.0)
        if c.get('source_quality_score') is not None: qs.append(_clamp(_f(c.get('source_quality_score'),0.75)))
        elif c.get('source_quality_tier'): qs.append(q_tier.get(str(c.get('source_quality_tier')).upper(),0.75))
        else: qs.append(0.75)
    freshness=sum(fs)/len(fs); rep=sum(rs)/len(rs); scope=sum(ss)/len(ss); quality=sum(qs)/len(qs)
    # Multiplicative quality is intentionally conservative: one severe weakness materially reduces external evidence power.
    multiplier=max(0.05,traceability)*max(0.05,freshness)*max(0.05,rep)*max(0.05,scope)*max(0.05,quality)
    return {'multiplier':round(_clamp(multiplier,0.05,1.0),4),'traceability':round(traceability,4),'freshness':round(freshness,4),'representativeness':round(rep,4),'scope_match':round(scope,4),'source_quality':round(quality,4),'source_ids':ids,'resolved_source_ids':[str(c.get('source_id')) for c in cards],'status':'QUALITY_WEIGHT_COMPILED'}


def _agreement_factor(intent:str, signals:list[dict[str,Any]], request:dict[str,Any])->dict[str,Any]:
    families=sorted({str(x.get('source') or '') for x in signals if x.get('intent')==intent})
    declared=[]
    for row in request.get('market_evidence_conflicts') or request.get('evidence_conflicts') or []:
        if str(row.get('intent') or '').upper()==str(intent).upper(): declared.append(row)
    if declared:
        return {'factor':0.6,'status':'DECLARED_CONFLICT','source_families':families,'declared_conflicts':declared}
    external=[x for x in families if x not in {'OWN_SHOPPER_QUESTION','OWN_FEEDBACK','OWN_BEHAVIOR'}]
    if len(set(external))>=2: return {'factor':1.12,'status':'MULTI_SOURCE_FAMILY_CORROBORATION','source_families':families,'declared_conflicts':[]}
    if len(external)==1: return {'factor':0.92,'status':'SINGLE_EXTERNAL_SOURCE_FAMILY','source_families':families,'declared_conflicts':[]}
    return {'factor':1.0,'status':'OWN_INPUT_OR_NO_EXTERNAL_SIGNAL','source_families':families,'declared_conflicts':[]}


def _fit_id(kind:str,label:str,source_ids:list[str])->str:
    raw='|'.join([kind,label,*sorted(str(x) for x in source_ids)])
    return 'FIT-'+hashlib.sha256(raw.encode('utf-8')).hexdigest()[:10].upper()


def compile_market_evidence_fit_contract(request:dict[str,Any], market_analysis:dict[str,Any]|None)->dict[str,Any]:
    """Create Product-Truth-fit review tasks from market/search/review evidence.

    The runtime never auto-claims fit. Only explicit host responses or legacy market_theme_fit approvals
    can turn a candidate into an asset-routing job.
    """
    market_analysis=market_analysis or {}; candidates=[]
    for r in ((market_analysis.get('customer_voice') or {}).get('theme_summary') or [])[:20]:
        theme=str(r.get('theme') or '').strip()
        if not theme or theme=='UNCLASSIFIED': continue
        sids=list(r.get('source_ids') or []); cid=_fit_id('REVIEW_THEME',theme,sids)
        candidates.append({'candidate_id':cid,'kind':'REVIEW_THEME','label':theme,'source_ids':sids,'observed_signal':{'weighted_mentions':r.get('weighted_mentions'),'dominant_sentiment':r.get('dominant_sentiment')},'fit_status':'HOST_REVIEW_REQUIRED','question':'Does verified Product Truth genuinely address this observed market/review concern without inventing a comparative advantage?','asset_routing_status':'NOT_ROUTED_UNTIL_PRODUCT_TRUTH_FIT_CONFIRMED'})
    for r in ((market_analysis.get('keyword_demand') or {}).get('top_terms') or [])[:20]:
        term=str(r.get('term') or '').strip(); intent=str(r.get('intent') or '').strip()
        if not term: continue
        sids=list(r.get('source_ids') or []); cid=_fit_id('SEARCH_TERM',term,sids)
        candidates.append({'candidate_id':cid,'kind':'SEARCH_TERM','label':term,'intent':intent,'source_ids':sids,'observed_signal':{'volume':r.get('volume'),'priority_signal':r.get('priority_signal')},'fit_status':'HOST_REVIEW_REQUIRED','question':'Is this search demand semantically and factually relevant to the exact product/SKU, and if so what consumer decision question should it create?','asset_routing_status':'NOT_ROUTED_UNTIL_PRODUCT_TRUTH_FIT_CONFIRMED'})
    for r in ((market_analysis.get('competitor_listing_intelligence') or {}).get('proof_type_summary') or [])[:15]:
        label=str(r.get('proof_type') or '').strip()
        if not label: continue
        sids=list(r.get('source_ids') or []); cid=_fit_id('COMPETITOR_PROOF_NORM',label,sids)
        candidates.append({'candidate_id':cid,'kind':'COMPETITOR_PROOF_NORM','label':label,'source_ids':sids,'observed_signal':{'count':r.get('count')},'fit_status':'HOST_REVIEW_REQUIRED','question':'Is this competitor proof norm relevant to an own-product purchase question, and do we possess own evidence to answer it?','asset_routing_status':'NOT_ROUTED_UNTIL_PRODUCT_TRUTH_FIT_CONFIRMED'})
    byid={x['candidate_id']:x for x in candidates}
    responses=list(request.get('host_market_evidence_fit_responses') or [])
    # Legacy explicit approvals remain supported and are normalized into the same contract.
    for row in request.get('market_theme_fit') or []:
        label=str(row.get('theme') or row.get('market_theme') or '').strip()
        match=next((x for x in candidates if x.get('label')==label),None)
        responses.append({**row,'candidate_id':row.get('candidate_id') or (match or {}).get('candidate_id'),'fit_status':row.get('fit_status') or row.get('status')})
    approved=[]; applied=[]; rejected=[]
    for resp in responses:
        cid=resp.get('candidate_id'); c=byid.get(cid)
        if not c:
            rejected.append({'candidate_id':cid,'reason':'UNKNOWN_CANDIDATE_ID'}); continue
        status=str(resp.get('fit_status') or resp.get('status') or '').upper()
        confirmed=(status in {'CONFIRMED','APPROVED','TRUE','FIT','PRODUCT_TRUTH_FIT_CONFIRMED'} or resp.get('product_truth_fit') is True)
        c.update({'fit_status':'PRODUCT_TRUTH_FIT_CONFIRMED' if confirmed else 'NOT_CONFIRMED','fit_rationale':resp.get('why') or resp.get('fit_rationale'),'product_truth_refs':resp.get('product_truth_refs') or resp.get('claim_ids') or [],'consumer_question':resp.get('consumer_question') or resp.get('question')})
        applied.append(cid)
        if confirmed:
            q=c.get('consumer_question') or f"What should a shopper understand about the validated concern: {c.get('label')}?"
            approved.append({'theme':c.get('label'),'consumer_question':q,'fit_status':'CONFIRMED','product_truth_fit':True,'source_ids':c.get('source_ids') or [],'claim_ids':c.get('product_truth_refs') or [],'candidate_id':cid,'origin_kind':c.get('kind')})
            c['asset_routing_status']='APPROVED_FOR_DECISION_JOB_ROUTING'
    return {'status':'MARKET_EVIDENCE_FIT_CONTRACT_COMPILED' if candidates else 'NO_MARKET_EVIDENCE_CANDIDATES','candidates':candidates,'host_response_summary':{'received':len(responses),'applied':len(applied),'rejected':rejected},'approved_asset_jobs':approved,'boundary':'Market/search/review/competitor observations never become own-product claims or asset jobs until Product Truth fit is explicitly confirmed. The runtime generates review tasks; it does not invent semantic fit.'}

def _intent_from_keyword(row:dict[str,Any], category_family:str)->str|None:
    intent=str(row.get('intent') or row.get('cluster') or '').upper().strip()
    term=str(row.get('term') or row.get('keyword') or '').strip()
    direct={
        'COMPATIBILITY':'COMPATIBILITY','SIZE':'SIZE_FIT' if category_family=='APPAREL_FIT' else 'SIZE_CAPACITY',
        'FIT':'SIZE_FIT' if category_family=='APPAREL_FIT' else 'FIT_WEAR','MATERIAL':'MATERIAL_SENSORY',
        'INGREDIENT':'INGREDIENT_DIETARY' if category_family=='FOOD_BEVERAGE' else 'PROOF','NUTRITION':'INGREDIENT_DIETARY',
        'ALLERGEN':'INGREDIENT_DIETARY','USAGE':'USAGE','HOW_TO':'USAGE','PERFORMANCE':'PERFORMANCE_PROOF',
        'SERVICE':'WARRANTY_SERVICE','WARRANTY':'WARRANTY_SERVICE','INSTALLATION':'DELIVERY_INSTALLATION',
        'PACKAGE':'PACKAGE_CONTENTS','CAPACITY':'SIZE_CAPACITY','SPECIFICATION':'PROOF','PROOF':'PROOF',
        'BENEFIT':'RELEVANCE','PROBLEM':'RELEVANCE','CATEGORY':'IDENTIFY','BRAND':'IDENTIFY',
    }
    if intent in direct: return direct[intent]
    if term:
        inferred=classify_decision_intent(term,category_family)
        return None if inferred=='DECISION_SUPPORT' else inferred
    return None


def _evidence_signal_rows(request:dict[str,Any], market_depth:dict[str,Any], category_family:str)->list[dict[str,Any]]:
    rows=[]
    for q in request.get('shopper_questions') or []:
        intent=classify_decision_intent(str(q),category_family)
        if intent!='DECISION_SUPPORT':
            rows.append({'source':'OWN_SHOPPER_QUESTION','intent':intent,'strength':'HIGH','raw_weight':100.0,'quality_multiplier':1.0,'weighted_weight':100.0,'quality':{'status':'OWN_PROJECT_INPUT_NOT_MARKET_WEIGHTED'},'evidence':q,'authority':'OWN_PROJECT_INPUT'})
    kw=(market_depth.get('keyword_demand') or {}).get('top_terms') or []
    for r in kw[:50]:
        intent=_intent_from_keyword(r,category_family)
        if not intent: continue
        vol=_f(r.get('volume') or r.get('search_volume'),0.0); raw=10.0+min(vol,10000.0)/1000.0
        q=_source_quality_factor(r.get('source_ids') or [],market_depth,'keyword_rows')
        rows.append({'source':'MARKET_SEARCH','intent':intent,'strength':'MEDIUM','raw_weight':raw,'quality_multiplier':q['multiplier'],'weighted_weight':raw*q['multiplier'],'quality':q,'evidence':r,'authority':'SUPPLIED_MARKET_EVIDENCE'})
    cv=(market_depth.get('customer_voice') or {}).get('theme_summary') or []
    for r in cv[:60]:
        theme=str(r.get('theme') or '')
        if not theme or theme=='UNCLASSIFIED': continue
        intent=classify_decision_intent(theme,category_family)
        if intent=='DECISION_SUPPORT': continue
        cnt=_f(r.get('weighted_mentions') or r.get('count') or r.get('observed_count') or r.get('weight'),1.0); raw=20.0+min(cnt,100.0)
        q=_source_quality_factor(r.get('source_ids') or [],market_depth,'review_rows')
        rows.append({'source':'CUSTOMER_VOICE','intent':intent,'strength':'MEDIUM','raw_weight':raw,'quality_multiplier':q['multiplier'],'weighted_weight':raw*q['multiplier'],'quality':q,'evidence':r,'authority':'SUPPLIED_REVIEW_LABEL'})
    ci=market_depth.get('competitor_listing_intelligence') or {}
    for r in (ci.get('proof_type_summary') or [])[:40]:
        label=str(r.get('proof_type') or '')
        intent=classify_decision_intent(label,category_family)
        if intent=='DECISION_SUPPORT': continue
        raw=5.0+min(_f(r.get('count'),1),50.0); q=_source_quality_factor(r.get('source_ids') or [],market_depth,'competitor_listing_rows')
        rows.append({'source':'COMPETITOR_PROOF_NORM','intent':intent,'strength':'LOW','raw_weight':raw,'quality_multiplier':q['multiplier'],'weighted_weight':raw*q['multiplier'],'quality':q,'evidence':r,'authority':'COMPETITOR_OBSERVATION_ONLY'})
    return rows


def build_evidence_priority(request:dict[str,Any], market_depth:dict[str,Any], commerce_profile:dict[str,Any])->dict[str,Any]:
    family=commerce_profile.get('category_family') or 'GENERAL_COMMERCE'
    signals=_evidence_signal_rows(request,market_depth,family)
    agg=defaultdict(lambda:{'raw_weight':0.0,'quality_weighted':0.0,'signals':[],'highest':'LOW'})
    order={'LOW':1,'MEDIUM':2,'HIGH':3}
    for s in signals:
        a=agg[s['intent']]; a['raw_weight']+=s.get('raw_weight',s.get('weighted_weight',0.0)); a['quality_weighted']+=s.get('weighted_weight',0.0); a['signals'].append(s)
        if order.get(s['strength'],0)>order.get(a['highest'],0): a['highest']=s['strength']
    ranked=[]
    for intent,v in agg.items():
        agreement=_agreement_factor(intent,signals,request)
        adjusted=v['quality_weighted']*agreement['factor']
        ranked.append({'intent':intent,'raw_evidence_weight':round(v['raw_weight'],4),'quality_weighted_evidence':round(v['quality_weighted'],4),'agreement_factor':agreement['factor'],'agreement_status':agreement['status'],'source_families':agreement['source_families'],'evidence_weight':round(adjusted,4),'highest_strength':v['highest'],'signals':v['signals'][:12]})
    ranked.sort(key=lambda x:-x['evidence_weight'])
    return {
        'status':'EVIDENCE_PRIORITY_COMPILED' if ranked else 'NO_DECISION_EVIDENCE_PRESSURE',
        'category_family':family,'ranked_intents':ranked,
        'quality_model':{'dimensions':['freshness','source_id_coverage','source_resolution','representativeness_metadata','scope_match','explicit_source_quality','cross_source_agreement_or_declared_conflict'],'principle':'Weak, stale, scope-mismatched or poorly traceable evidence has less power to reorder strategy. Missing metadata lowers confidence; it never becomes a hidden veto. Own explicit shopper questions remain stronger project evidence.'},
        'authority_order':['PRODUCT_TRUTH_AND_VERIFIED_POLICY','OWN_SHOPPER_FEEDBACK_BEHAVIOR','QUALITY_WEIGHTED_CURRENT_MARKET_SEARCH_REVIEW_COMPETITOR_EVIDENCE','CATEGORY_PROFILE_PRIOR','GENERIC_FALLBACK'],
        'boundary':'Evidence priority can reorder which question is answered first, but cannot create a product fact, claim, compatibility, certification, service promise, sensory result or causal effect.'
    }

def _proof_intents(proof_type:str, family:str)->set[str]:
    p=str(proof_type).casefold()
    out=set()
    mapping=[
      (['size chart','garment measurement'],{'SIZE_FIT'}),(['fit/silhouette','on-body'],{'FIT_WEAR','SIZE_FIT'}),
      (['ingredient','nutrition','allergen','certification'],{'INGREDIENT_DIETARY'}),(['sensory','preparation','serving'],{'SENSORY_PREP'}),
      (['compatibility','interface'],{'COMPATIBILITY'}),(['performance','test conditions'],{'PERFORMANCE_PROOF'}),
      (['warranty','service'],{'WARRANTY_SERVICE'}),(['delivery','installation'],{'DELIVERY_INSTALLATION'}),
      (['site/size/utility','clearance'],{'SITE_FIT'}),(['total ownership','energy','consumable'],{'TOTAL_COST_OWNERSHIP'}),
      (['dimension','capacity'],{'SIZE_CAPACITY'}),(['material','construction','fabric','color'],{'MATERIAL_SENSORY'}),
      (['care','weather'],{'CARE_MAINTENANCE','WEATHER_BOUNDARY'}),(['usage','expectation'],{'USAGE','EXPECTATION_BOUNDARY'}),
      (['formula','ingredient/spec','claim-specific evidence','approved proof'],{'PROOF'}),(['label identity','product identity','exact product'],{'IDENTIFY'}),
      (['package','net content'],{'PACKAGE_CONTENTS'}),
    ]
    for terms,intents in mapping:
        if any(t in p for t in terms): out.update(intents)
    return out or {'PROOF'}


def _proof_condition(proof_type:str, family:str)->dict[str,Any]:
    p=str(proof_type).casefold()
    if 'compatibility' in p or 'interface' in p:
        return {'evidence_type':'COMPATIBILITY_MATRIX_OR_EXACT_SPEC','must_include':['exact model/interface/region or declared compatibility scope','source/version'],'do_not_infer':['compatibility from visual similarity','region support from brand presence']}
    if 'performance' in p:
        return {'evidence_type':'CONDITIONED_PERFORMANCE_EVIDENCE','must_include':['metric','test method','conditions/load/configuration','source/version'],'do_not_infer':['best-case number as universal outcome','causality from competitor claim']}
    if any(x in p for x in ['ingredient','nutrition','allergen','certification']):
        return {'evidence_type':'LABEL_OR_AUTHORIZED_SPEC','must_include':['current formula/label/spec','market/variant/lot or version when relevant','source'],'do_not_infer':['health benefit from ingredient presence','certification from visual symbols without source']}
    if any(x in p for x in ['sensory','preparation','serving']):
        return {'evidence_type':'REAL_PRODUCT_PREPARATION_OR_SENSORY_SOURCE','must_include':['real preparation/serving condition','source or approved sensory description'],'do_not_infer':['universal taste preference','synthetic food image as product evidence']}
    if any(x in p for x in ['size chart','garment measurement','fit/silhouette']):
        return {'evidence_type':'SIZE_FIT_EVIDENCE','must_include':['size chart or garment measurements','fit/model context when visualized'],'do_not_infer':['universal fit from one model','body outcome from garment label alone']}
    if 'site/size/utility' in p:
        return {'evidence_type':'SITE_FIT_CONTRACT','must_include':['product dimensions','required clearance/utility/interface','installation source when relevant'],'do_not_infer':['site compatibility without customer/site facts']}
    if 'warranty' in p or 'service' in p:
        return {'evidence_type':'CURRENT_MARKET_CHANNEL_POLICY','must_include':['market/channel scope','effective/current source','coverage/exclusions'],'do_not_infer':['service from brand reputation','policy portability across markets']}
    if 'delivery' in p or 'installation' in p:
        return {'evidence_type':'CURRENT_FULFILLMENT_SERVICE_FACT','must_include':['market/postcode/channel scope','service responsibility','fees/conditions when known'],'do_not_infer':['free installation','universal delivery coverage']}
    if 'total ownership' in p:
        return {'evidence_type':'OWNERSHIP_COST_INPUTS','must_include':['known consumables/energy/maintenance/subscription inputs','time horizon or replacement cycle source'],'do_not_infer':['lifetime savings without baseline/comparator']}
    if any(x in p for x in ['formula','claim-specific','approved proof']):
        return {'evidence_type':'CLAIM_SPECIFIC_SOURCE','must_include':['claim text/strength','evidence source','population/condition/time boundary when applicable'],'do_not_infer':['effect from ingredient presence alone','clinical strength from non-clinical evidence']}
    return {'evidence_type':'PRODUCT_TRUTH_OR_APPROVED_EVIDENCE','must_include':['traceable source supporting the decision fact'],'do_not_infer':['unsupported benefit escalation']}


def _proof_input_support(request:dict[str,Any], proof_type:str)->dict[str,Any]:
    product=request.get('product') or {}; claims=request.get('claims') or []; sources=request.get('sources') or []
    blob=' '.join([str(k) for k in product.keys()]+[str(v) for v in product.values() if not isinstance(v,(dict,list))]).casefold()
    p=str(proof_type).casefold(); signals=[]
    checks=[
      (['ingredient','nutrition','allergen','certification'],['ingredient','nutrition','allergen','certif','halal','vegan']),
      (['compatibility','interface'],['compatib','interface','connector','system','region']),
      (['performance'],['performance','battery','runtime','speed','latency','noise','suction','watt','power']),
      (['size chart','garment measurement','fit/silhouette'],['size_chart','size chart','measurement','fit','length','chest','waist']),
      (['site/size/utility'],['dimension','width','height','depth','clearance','utility','voltage','installation']),
      (['warranty','service'],['warranty','service','repair','support']),
      (['delivery','installation'],['delivery','installation','assembly','shipping']),
      (['total ownership'],['energy','consumable','replacement','maintenance','subscription']),
      (['formula','claim-specific','approved proof'],['formula','ingredient','active','claim','evidence']),
      (['label identity','product identity','exact product'],['name','category','product_type','net_content']),
      (['package','net content'],['package','packaging','net_content','count','contents']),
    ]
    terms=[]
    for proof_terms,input_terms in checks:
        if any(x in p for x in proof_terms): terms=input_terms; break
    for t in terms:
        if t in blob or any(t in str(k).casefold() for k in product.keys()): signals.append(t)
    if claims and any(x in p for x in ['proof','claim','performance','formula','ingredient']): signals.append('claims_supplied')
    if sources: signals.append('source_records_supplied')
    return {'status':'INPUT_SUPPORT_SIGNAL_PRESENT_REVIEW_EXACT_EVIDENCE' if signals else 'EVIDENCE_INPUT_NOT_FOUND','signals':sorted(set(signals)),'boundary':'Input signals only show where evidence may exist. Publication still requires exact source/claim trace and the declared evidence condition.'}


def reconcile_category_commerce(request:dict[str,Any], market_depth:dict[str,Any], commerce_profile:dict[str,Any])->dict[str,Any]:
    pressure=build_evidence_priority(request,market_depth,commerce_profile)
    sigmap={x['intent']:x for x in pressure.get('ranked_intents',[])}
    def prior_score(rank):
        r=int(rank or 99)
        schedule={1:40.0,2:24.0,3:14.0,4:8.0,5:5.0}
        return schedule.get(r,max(3.0,8.0-(r-4)*1.5))
    objections=[]
    for base in commerce_profile.get('objection_priorities') or []:
        x=dict(base); sig=sigmap.get(x.get('decision_intent')) or {}; w=_f(sig.get('evidence_weight'),0.0); ps=prior_score(x.get('rank'))
        x['category_prior_rank']=x.get('rank'); x['category_prior_score']=round(ps,4); x['evidence_pressure']=round(w,4); x['effective_priority_score']=round(ps+w,4)
        x['evidence_quality_status']=sig.get('agreement_status') or ('NO_CURRENT_EVIDENCE' if not w else 'QUALITY_WEIGHTED')
        x['effective_priority_basis']='QUALITY_WEIGHTED_EVIDENCE_PLUS_CATEGORY_PRIOR' if w>0 else 'CATEGORY_PRIOR_ONLY'
        objections.append(x)
    objections.sort(key=lambda x:(-x['effective_priority_score'],x.get('category_prior_rank') or 999))
    for i,x in enumerate(objections,1): x['effective_rank']=i

    proofs=[]
    for base in commerce_profile.get('proof_hierarchy') or []:
        x=dict(base); intents=_proof_intents(x.get('proof_type',''),commerce_profile.get('category_family',''))
        signals=[sigmap.get(i) for i in intents if sigmap.get(i)]; w=max([_f(z.get('evidence_weight'),0.0) for z in signals] or [0.0]); ps=prior_score(x.get('rank'))
        x['category_prior_rank']=x.get('rank'); x['category_prior_score']=round(ps,4); x['supports_decision_intents']=sorted(intents); x['evidence_pressure']=round(w,4); x['effective_priority_score']=round(ps+w,4)
        x['evidence_condition']=_proof_condition(x.get('proof_type',''),commerce_profile.get('category_family','')); x['input_evidence_support']=_proof_input_support(request,x.get('proof_type',''))
        x['effective_priority_basis']='QUALITY_WEIGHTED_EVIDENCE_PLUS_CATEGORY_PRIOR' if w>0 else 'CATEGORY_PRIOR_ONLY'; proofs.append(x)
    proofs.sort(key=lambda x:(-x['effective_priority_score'],x.get('category_prior_rank') or 999))
    for i,x in enumerate(proofs,1): x['effective_rank']=i

    prior_sequence=list((commerce_profile.get('message_architecture') or {}).get('sequence') or [])
    promoted=[x.get('decision_intent') for x in objections if x.get('evidence_pressure',0)>0 and x.get('effective_rank',99)<=4]
    effective_sequence=[]
    if prior_sequence: effective_sequence.append(prior_sequence[0])
    for intent in promoted[:4]:
        label=str(intent or '').replace('_',' ')
        if label and all(label.casefold() not in str(x).casefold() for x in effective_sequence): effective_sequence.append(label)
    for job in prior_sequence[1:] if prior_sequence else []:
        jc=' '.join(str(job).casefold().replace('_',' ').split())
        def _semantically_overlaps(existing):
            ec=' '.join(str(existing).casefold().replace('_',' ').split())
            return jc==ec or jc in ec or ec in jc
        if all(not _semantically_overlaps(x) for x in effective_sequence): effective_sequence.append(job)
    conflicts=[]
    if objections and objections[0].get('category_prior_rank')!=1:
        conflicts.append({'type':'CATEGORY_PRIOR_VS_CURRENT_EVIDENCE','category_prior_top':next((x.get('objection_key') for x in commerce_profile.get('objection_priorities',[]) if x.get('rank')==1),None),'evidence_effective_top':objections[0].get('objection_key'),'decision':'QUALITY_WEIGHTED_CURRENT_EVIDENCE_REORDERS_STRATEGY_PRIOR','why':'Current evidence only reorders the category prior after freshness/traceability/representativeness/scope/source-quality weighting and agreement/conflict adjustment. Weak or stale observations therefore have less power to displace a strong category prior.'})
    decisions=[]
    for x in objections[:6]:
        sig=sigmap.get(x.get('decision_intent')) or {}
        decisions.append({'what':f"Prioritize {x.get('objection_key')} at effective rank {x.get('effective_rank')}",'why':'Category prior and current evidence are combined rather than treated as binary winners. Current evidence receives less influence when it is stale, scope-mismatched, weakly traceable, poorly documented or single-source.','evidence':sig.get('signals',[])[:8],'evidence_quality':{'raw_weight':sig.get('raw_evidence_weight'),'quality_weighted':sig.get('quality_weighted_evidence'),'agreement_factor':sig.get('agreement_factor'),'agreement_status':sig.get('agreement_status')},'consumer_logic':x.get('question'),'platform_logic':'Express this decision on the surface that can resolve it with the least friction; exact platform policy remains separately authoritative.','business_logic':'Move scarce content/proof space toward the best-supported unresolved purchase uncertainty without letting weak research overrule stronger product/category knowledge.','execution':f"Resolve via {x.get('recommended_field')} with own-product evidence.",'measurement':'Decision-specific comprehension / CVR / FAQ-return-theme change; refresh evidence quality before treating priority as permanent.'})
    return {
      'status':'CATEGORY_EVIDENCE_RECONCILED','authority_precedence':pressure.get('authority_order'),'evidence_priority':pressure,'reconciliation_decisions':decisions,
      'effective_objection_priorities':objections,'effective_proof_hierarchy':proofs,
      'message_architecture':{'category_prior_sequence':prior_sequence,'effective_sequence':effective_sequence,'evidence_promoted_decision_intents':promoted[:8],'status':'EVIDENCE_RECONCILED_MESSAGE_INPUT','decision_rule':'Keep exact copy/claim facts authoritative; use only quality-weighted evidence to adjust order/module emphasis while category prior remains a scored fallback.'},
      'conflicts':conflicts,
      'boundary':'Current market/search/review evidence may change priority and sequence only after quality weighting; it never creates own-product facts or proves that competitor/customer observations apply to the product.'
    }

def validate_category_offer_with_evidence(commerce_profile:dict[str,Any], economics:dict[str,Any]|None, offer_input:dict[str,Any]|None)->dict[str,Any]:
    economics=economics or {}; offer_input=offer_input or {}
    patterns=(commerce_profile.get('offer_architecture') or {}).get('candidate_patterns') or []
    shared=economics.get('shared_growth_budget') or {}; scenarios=economics.get('scenarios') or []
    promo=economics.get('promo_response') or {}; bundle=economics.get('bundle_affinity') or {}; cycle=economics.get('repeat_replacement_cycle') or {}
    economically_blocked=False
    if shared.get('status')=='CALCULATED_FROM_INPUTS' and _f(shared.get('remaining_growth_pool'))<0: economically_blocked=True
    if scenarios and all((r.get('contribution') is not None and _f(r.get('contribution'))<=0) for r in scenarios): economically_blocked=True
    out=[]
    for p in patterns:
        low=str(p).casefold(); evidence=[]; status='EVIDENCE_REQUIRED_BEFORE_LOCK'
        if 'bundle' in low or 'multi-buy' in low or 'multipack' in low or 'sampler' in low:
            if bundle.get('status')=='BUNDLE_AFFINITY_COMPILED' and bundle.get('pairs'): evidence.append('observed_bundle_affinity')
        if any(x in low for x in ['retention','subscription','replenishment','repeat']):
            if cycle.get('status')=='REPEAT_REPLACEMENT_CYCLE_COMPILED' and cycle.get('observations'): evidence.append('repeat_replacement_cycle')
        if any(x in low for x in ['discount','promo','financing']):
            if promo.get('status')=='PROMO_RESPONSE_COMPILED' and promo.get('rows'): evidence.append('observed_promo_response')
        if 'configuration' in low or 'upgrade' in low or 'trade-up' in low:
            if economics.get('trade_up_architecture'): evidence.append('trade_up_architecture')
        if 'service' in low or 'warranty' in low or 'installation' in low or 'delivery' in low:
            if offer_input.get('service_capability_verified') or offer_input.get('service_policy_source_ids'): evidence.append('verified_service_capability')
        if economically_blocked: status='ECONOMICALLY_BLOCKED_UNTIL_PRICE_COST_MIX_CHANGES'
        elif evidence: status='EVIDENCE_SUPPORTED_TEST_CANDIDATE_NOT_LOCKED'
        out.append({'candidate_pattern':p,'status':status,'supporting_evidence':evidence,'why':'A category-shaped offer is worth testing only when product/service fit and economics/behavior evidence support it. Evidence-supported means testable, not automatically optimal.'})
    scenario_screen=[]
    for r in scenarios:
        scenario_screen.append({'scenario_id':r.get('scenario_id'),'sku':r.get('sku'),'price':r.get('price'),'contribution':r.get('contribution'),'contribution_margin':r.get('contribution_margin'),'break_even_roas':r.get('break_even_roas'),'coupon_headroom':r.get('coupon_headroom') or r.get('coupon_headroom_target_contribution'),'shared_growth_budget':r.get('shared_growth_budget'),'economic_status':'ECONOMICALLY_POSITIVE' if r.get('contribution') is not None and _f(r.get('contribution'))>0 else ('ECONOMICALLY_NON_POSITIVE' if r.get('contribution') is not None else 'ECONOMICS_INCOMPLETE')})
    return {'status':'CATEGORY_OFFER_EVIDENCE_VALIDATION','candidates':out,'scenario_economic_screen':scenario_screen,'promo_response':promo,'bundle_affinity':bundle,'repeat_replacement_cycle':cycle,'shared_growth_budget':shared,'boundary':'Offer validation cannot create service, warranty, financing, bundle availability or demand elasticity. Observational response is not causal incrementality.'}


def platform_category_intersection(platform:str, surface:str, family:str, reconciliation:dict[str,Any])->dict[str,Any]:
    p=(platform or '').casefold(); s=(surface or '').upper()
    top=[x.get('decision_intent') for x in reconciliation.get('effective_objection_priorities',[])[:3]]
    if 'amazon' in p:
        entry='Search comparison: exact identity and decision-critical structured facts first.'; density='HIGH_SCANNABILITY'; offer='Offer follows search/spec clarity and compliant field/surface rules.'
    elif 'shopee' in p:
        entry='Mobile comparison: exact variant/configuration plus price/value cue and objection resolution.'; density='COMPACT_COMPARISON'; offer='Promo can aid comparison only after configuration and contribution remain clear.'
    elif 'tiktok' in p:
        entry='Discovery commerce: identify exact product fast, then demonstrate the highest-priority unresolved decision.'; density='LOW_PER_BEAT'; offer='Creator/offer urgency follows value and proof; do not lead with discount when risk is unresolved.'
    elif 'shopify' in p or 'dtc' in p:
        entry='Owned landing: route traffic to the next unresolved belief using modular proof/risk modules.'; density='MODULAR_DEEP'; offer='Lifecycle/bundle/subscription logic should use contribution and repeat evidence.'
    else:
        entry='Use the surface entry state to resolve the highest-priority evidence-backed purchase question.'; density='SURFACE_DEPENDENT'; offer='Use only economically and operationally valid offer forms.'
    return {'status':'PLATFORM_CATEGORY_INTERSECTION','platform':platform,'surface':s,'category_family':family,'evidence_priority_intents':top,'entry_priority':entry,'information_density':density,'offer_role':offer,'proof_rule':'Use effective evidence-conditioned proof hierarchy; exact platform policy remains authoritative from the compiled pack.','why':'Platform mechanism changes how a category decision problem is expressed, while current evidence decides which category problem deserves priority. Neither layer may invent Product Truth.'}
