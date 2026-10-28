from __future__ import annotations
from typing import Any
from .models import stable_hash


def _score(direction:dict[str,Any])->float:
    vals=[]
    for k in ['product_fit','audience_fit','platform_fit','culture_fit','differentiation','production_feasibility','decision_coverage','opportunity_fit']:
        v=direction.get(k)
        if isinstance(v,(int,float)): vals.append(float(v))
    return round(sum(vals)/len(vals),3) if vals else 0.0


def compile_curation(references:list[dict[str,Any]]|None, competitor_patterns:list[dict[str,Any]]|None=None)->dict[str,Any]:
    references=references or []; competitor_patterns=competitor_patterns or []
    normalized=[]
    for r in references:
        role=str(r.get('role','VISUAL_REFERENCE')).upper()
        normalized.append({
            'reference_id':r.get('reference_id') or 'REF-'+stable_hash(r)[:10],
            'role':role,
            'source':r.get('source'),
            'usable_for':r.get('usable_for',[]),
            'not_truth_for':r.get('not_truth_for',[]),
            'notes':r.get('notes','')
        })
    clichés=[x for x in competitor_patterns if str(x.get('pattern_status')).upper()=='CLICHE']
    whitespace=[x for x in competitor_patterns if str(x.get('pattern_status')).upper()=='WHITESPACE']
    return {
        'status':'CURATED' if normalized or competitor_patterns else 'NO_REFERENCE_INPUT',
        'references':normalized,'category_cliches':clichés,'white_space':whitespace,
        'search_before_selection':{
            'mechanism_domains':['PRODUCT_STRUCTURE','CATEGORY_CONVENTION','ADJACENT_CATEGORY','EDITORIAL_INFORMATION_DESIGN','ARCHITECTURE_EXHIBITION_CRAFT'],
            'rule':'Borrow mechanisms, not finished compositions. Reference material never overrides Product Truth.'
        },
        'principle':'References guide visual decisions only within their declared role; they do not override Product Truth.'
    }


def _route_for_mechanism(mechanism_id:str)->str:
    mid=str(mechanism_id or '').upper()
    if mid in {'OPP-IDENTITY-GEOMETRY','OPP-INFORMATION-EDITORIAL','OPP-CATEGORY-CONVENTION-BREAK'}:
        return 'PRODUCT_TRUTH_EDITORIAL'
    if mid in {'OPP-EVIDENCE-RELATIONSHIP','OPP-SCALE-SPACE','OPP-SYSTEM-RELATIONSHIP','OPP-RISK-BOUNDARY'}:
        return 'EVIDENCE_MECHANISM'
    if mid in {'OPP-HUMAN-DECISIVE-MOMENT','OPP-PROCESS-SEQUENCE'}:
        return 'HUMAN_CONTEXT_ACTION'
    if mid in {'OPP-MATERIAL-OPTICS','OPP-CONTENTS-REVEAL','OPP-REMOTE-DOMAIN-SPATIAL'}:
        return 'MATERIAL_SENSORY_OBJECT'
    return 'PRODUCT_TRUTH_EDITORIAL'


def _legacy_opportunity_fallback(product_truth:dict[str,Any], decision_intents:list[str]|None=None)->dict[str,Any]:
    """Compatibility fallback for direct callers that have not compiled the opportunity universe yet."""
    product=(product_truth or {}).get('product') or product_truth or {}
    intents=[str(x or '').upper() for x in (decision_intents or []) if x]
    seeds=[
      ('OPP-IDENTITY-GEOMETRY','Product Identity Geometry','PRODUCT_STRUCTURE','Use real silhouette, key face, label readability and proportion as the first carrier.','Front/3Q/orthographic view chosen by the identity face.','Primary factual anchor','Real pack/geometry'),
      ('OPP-INFORMATION-EDITORIAL','Information Hierarchy as Visual Form','INFORMATION_DESIGN','Turn the decision hierarchy into spatial hierarchy.','Asymmetric editorial field with active negative space.','Hero/signature/absent by job','Source-bound copy/evidence'),
      ('OPP-EVIDENCE-RELATIONSHIP','Evidence Relationship / Causal Proof','EVIDENCE_SYSTEM','Turn proof into a visible causal or measured relationship.','Macro/sectional/relationship/measurement view selected by evidence.','Evidence carrier','Verified fact → visible relationship'),
      ('OPP-HUMAN-DECISIVE-MOMENT','Human Use Decisive Moment','HUMAN_CONTEXT','Use the exact human action that resolves use, scale or fit.','Action-led crop around the decisive contact point.','Active object in action','Visible action/fit/handling'),
      ('OPP-MATERIAL-OPTICS','Material / Optical Behavior','MATERIAL_CMF','Use truthful material response as purchase information.','Raking/broad-source/macro geometry follows material behavior.','Material subject','Real finish/texture/optics'),
      ('OPP-SCALE-SPACE','Scale / Space Calibration','SPATIAL_RELATION','Translate dimensions or fit into a truthful spatial relationship.','Orthographic/top-down/on-body/environmental scale view.','Measured object','Verified dimensions/fit'),
      ('OPP-PROCESS-SEQUENCE','Process / Sequence','BEHAVIOR_FLOW','Expose the minimum use/care/install sequence.','One decisive action per beat; no fixed three-step card.','Object in use','Source-bound action'),
      ('OPP-RISK-BOUNDARY','Risk / Boundary Visualization','RISK_REDUCTION','Show supported condition and explicit limit.','Condition-state or boundary annotation.','Risk-reduction anchor','Verified limit'),
      ('OPP-SYSTEM-RELATIONSHIP','System / Compatibility Relationship','SYSTEM_MAP','Show the object inside its real compatibility/component system.','Relationship or truthful exploded/inventory view.','System node','Compatibility/components'),
      ('OPP-CONTENTS-REVEAL','Package / Contents Reveal','OBJECT_INVENTORY','Make included contents unambiguous.','Top-down/open-package truthful inventory.','Container + included items','Package truth'),
      ('OPP-CATEGORY-CONVENTION-BREAK','Category Convention Reframing','CATEGORY_WHITESPACE','Keep the decision job while changing the category mechanism.','Borrow adjacent-domain grammar, never finished artwork.','Depends on job','Product Truth'),
      ('OPP-REMOTE-DOMAIN-SPATIAL','Remote-domain Spatial Grammar','REMOTE_DOMAIN','Borrow rhythm/reveal/framing from remote domains.','Object-as-exhibit / threshold / modular field when useful.','Varies by job','Reference is not evidence'),
    ]
    rows=[]
    for i,(mid,name,domain,visual,comp,role,proof) in enumerate(seeds):
        direction_role={'OPP-INFORMATION-EDITORIAL':'SUPPORTING_SYSTEM','OPP-CATEGORY-CONVENTION-BREAK':'DIFFERENTIATION_MODULATOR','OPP-REMOTE-DOMAIN-SPATIAL':'SPATIAL_MODULATOR','OPP-IDENTITY-GEOMETRY':'IDENTITY_ANCHOR'}.get(mid,'PRIMARY_MECHANISM')
        rows.append({'mechanism_id':mid,'mechanism_name':name,'domain':domain,'visual_mechanism':visual,'composition_camera_mechanism':comp,'product_role':role,'proof_mode':proof,'direction_role':direction_role,'score':round(0.86-i*0.015,3),'opportunity_id':'COP-'+stable_hash([product.get('name'),mid,intents])[:10].upper(),'activation_signals':{'fallback':True}})
    return {'status':'COMPATIBILITY_FALLBACK','opportunity_count':len(rows),'opportunities':rows,'observed_decision_intents':intents,'selection_rule':'Compatibility fallback only. Full compiler should provide Product/Decision/PVI-derived Creative Opportunity Universe.'}


def _auto_directions(product_truth:dict[str,Any], curation:dict[str,Any], culture:dict[str,Any], platform_compile:dict[str,Any], category_family:str|None=None, decision_intents:list[str]|None=None, opportunity_universe:dict[str,Any]|None=None)->list[dict[str,Any]]:
    """Synthesize a task-dependent number of materially different directions after mechanism search.

    Route labels are compatibility tags for downstream routing, not a fixed style library. The visible
    direction name, thesis, composition, product role and proof language are built from current
    Creative Opportunity mechanisms.
    """
    product=(product_truth or {}).get('product') or product_truth or {}
    name=product.get('name') or 'the product'; category=category_family or product.get('category') or 'GENERAL_COMMERCE'
    universe=opportunity_universe or _legacy_opportunity_fallback(product_truth,decision_intents)
    opportunities=[dict(x) for x in (universe.get('opportunities') or []) if isinstance(x,dict)]
    opportunities.sort(key=lambda x:(float(x.get('score') or 0),str(x.get('mechanism_id') or '')),reverse=True)
    if not opportunities:
        fallback=_legacy_opportunity_fallback(product_truth,decision_intents)
        opportunities=list(fallback.get('opportunities') or [])
    # Universal information/whitespace mechanisms are valuable modifiers but must not become the
    # default creative direction for every category. Primary mechanisms seed directions; support
    # mechanisms are paired once each where possible to produce genuinely different syntheses.
    primary_pool=[x for x in opportunities if x.get('direction_role')=='PRIMARY_MECHANISM']
    if not primary_pool:
        primary_pool=opportunities[:]
    if primary_pool:
        top_score=max(float(x.get('score') or 0) for x in primary_pool)
        direction_floor=max(0.55,top_score-0.12)
        leads=[x for x in primary_pool if float(x.get('score') or 0)>=direction_floor]
    else:
        leads=[]
    support_pool=[x for x in opportunities if x.get('opportunity_id') not in {y.get('opportunity_id') for y in leads}]
    used_support=set(); pairs=[]
    for lead in leads:
        candidates=[x for x in support_pool if x.get('opportunity_id') not in used_support and x.get('domain')!=lead.get('domain')]
        if not candidates:
            candidates=[x for x in opportunities if x.get('opportunity_id')!=lead.get('opportunity_id') and x.get('opportunity_id') not in used_support]
        if not candidates:
            candidates=[lead]
        secondary=max(candidates,key=lambda x:(float(x.get('score') or 0), 1 if x.get('direction_role')!='PRIMARY_MECHANISM' else 0, str(x.get('mechanism_id') or '')))
        used_support.add(secondary.get('opportunity_id'))
        pairs.append([lead,secondary])
    intent_list=[str(x or '').upper() for x in (decision_intents or []) if x]
    route_intents={
      'PRODUCT_TRUTH_EDITORIAL':{'IDENTIFY','RELEVANCE','EXPECTATION_BOUNDARY'},
      'EVIDENCE_MECHANISM':{'PROOF','PERFORMANCE_PROOF','DIFFERENTIATION','SIZE_CAPACITY','SIZE_FIT','SITE_FIT','COMPATIBILITY','PACKAGE_CONTENTS','SEAL_LEAK','WARRANTY_SERVICE','DELIVERY_INSTALLATION','TOTAL_COST_OWNERSHIP','INGREDIENT_COMPOSITION','INGREDIENT_DIETARY'},
      'HUMAN_CONTEXT_ACTION':{'RELEVANCE','USAGE','FIT_WEAR','PORTABILITY','SENSORY_PREP','STORAGE_STACKING'},
      'MATERIAL_SENSORY_OBJECT':{'MATERIAL_SENSORY','WEATHER_BOUNDARY','CARE_MAINTENANCE'},
    }
    category_route_prior={
      'APPAREL_FIT':'HUMAN_CONTEXT_ACTION','FASHION_ACCESSORY':'HUMAN_CONTEXT_ACTION',
      'HOME_DURABLE':'EVIDENCE_MECHANISM','HIGH_TICKET_DURABLE':'EVIDENCE_MECHANISM','ELECTRONICS':'EVIDENCE_MECHANISM',
      'FOOD_BEVERAGE':'MATERIAL_SENSORY_OBJECT',
    }.get(str(category).upper())
    white_space=[str(x.get('name') or x.get('pattern') or x.get('notes') or '') for x in curation.get('white_space',[])][:3]
    rows=[]
    for i,pair in enumerate(pairs):
        lead,second=pair[0],pair[1]
        route=_route_for_mechanism(lead.get('mechanism_id'))
        relevant=route_intents.get(route,set())
        hit=sum(1 for x in intent_list if x in relevant)
        coverage=(hit/len(intent_list)) if intent_list else 0.5
        opp_score=sum(float(x.get('score') or 0.5) for x in pair)/len(pair)
        product_fit=min(0.98,0.78+0.18*opp_score+(0.035 if route==category_route_prior else 0))
        audience_fit=min(0.98,0.78+0.15*coverage+(0.03 if route=='HUMAN_CONTEXT_ACTION' and coverage>=0.3 else 0))
        platform_fit=min(0.97,0.82+0.10*opp_score)
        culture_fit=0.91 if route!='HUMAN_CONTEXT_ACTION' else (0.90 if culture else 0.84)
        differentiation=min(0.99,0.80+0.16*opp_score+(0.03 if any(x.get('domain') in {'CATEGORY_WHITESPACE','REMOTE_DOMAIN'} for x in pair) else 0))
        production_feasibility=0.91 if route in {'PRODUCT_TRUTH_EDITORIAL','EVIDENCE_MECHANISM'} else 0.86
        decision_coverage=round(0.70+0.30*coverage,3)
        names=[str(x.get('mechanism_name') or x.get('mechanism_id')) for x in pair]
        visual=[str(x.get('visual_mechanism') or '') for x in pair if x.get('visual_mechanism')]
        comps=[str(x.get('composition_camera_mechanism') or '') for x in pair if x.get('composition_camera_mechanism')]
        roles=[str(x.get('product_role') or '') for x in pair if x.get('product_role')]
        proofs=[str(x.get('proof_mode') or '') for x in pair if x.get('proof_mode')]
        direction={
            'direction_name':' × '.join(names),
            'route':route,
            'buyer_entry':{'PRODUCT_TRUTH_EDITORIAL':'IDENTITY_AND_RELEVANCE','EVIDENCE_MECHANISM':'PROOF_AND_DIFFERENTIATION','HUMAN_CONTEXT_ACTION':'RELEVANCE_AND_USE','MATERIAL_SENSORY_OBJECT':'DESIRE_AND_QUALITY_SIGNAL'}.get(route,'DECISION_SUPPORT'),
            'creative_thesis':f"For {name}, synthesize "+' + '.join(names)+'. '+(' '.join(visual)),
            'composition_grammar':' / '.join(comps),
            'product_role':' + '.join(dict.fromkeys(roles)),
            'image_language':f"Current-product mechanism synthesis: {' + '.join(str(x.get('domain') or '') for x in pair)}. Coherence comes from Product Truth/CMF/type tokens; composition is rebuilt per decision job.",
            'proof_mechanism':' + '.join(dict.fromkeys(proofs)),
            'verbal_thesis':'One primary decision proposition per frame; visible text labels only the evidence/action/boundary actually shown.',
            'color_world':{'logic':'Derive the field from verified product/brand/material cues and the selected mechanism; never apply a universal category palette.','contrast':'Optimize figure/ground, material separation and mobile readability for the current Surface.'},
            'typography':'Deterministic final copy composition; hierarchy and text area follow current Surface copy budget and evidence plane.',
            'photography':'Camera, light and material behavior are selected from the paired opportunity mechanisms and Product Visual Intelligence; no generic premium-light preset.',
            'scene_props':'Only mechanism-relevant scale/use/evidence/context objects; no decorative prop kit.',
            'tradeoff':'This direction is chosen for its current decision/evidence fit; if the paired mechanisms stop adding information, use another direction rather than preserving a house template.',
            'direction_id':'DIR-'+stable_hash([category,[x.get('opportunity_id') for x in pair],route])[:8].upper(),
            'source':'CREATIVE_OPPORTUNITY_SYNTHESIS',
            'category_family':category,
            'opportunity_ids':[x.get('opportunity_id') for x in pair],
            'opportunity_mechanism_ids':[x.get('mechanism_id') for x in pair],
            'opportunity_mechanisms':names,
            'opportunity_score':round(opp_score,3),'opportunity_fit':round(opp_score,3),
            'search_before_selection_trace':{'universe_status':universe.get('status'),'universe_count':universe.get('opportunity_count'),'paired_opportunities':[{'id':x.get('opportunity_id'),'mechanism_id':x.get('mechanism_id'),'score':x.get('score'),'activation_signals':x.get('activation_signals')} for x in pair]},
            'decision_intent_fit':{'observed_intents':intent_list,'matched_intents':[x for x in intent_list if x in relevant],'coverage':round(coverage,3) if intent_list else None},
            'white_space_signals':white_space,
            'product_fit':round(product_fit,3),'audience_fit':round(audience_fit,3),'platform_fit':round(platform_fit,3),'culture_fit':round(culture_fit,3),'differentiation':round(differentiation,3),'production_feasibility':round(production_feasibility,3),'decision_coverage':decision_coverage,
        }
        direction['score']=_score(direction)
        rows.append(direction)
    return rows


def compile_creative_council(directions:list[dict[str,Any]]|None, curation:dict[str,Any], product_truth:dict[str,Any], culture:dict[str,Any], platform_compile:dict[str,Any], category_family:str|None=None, decision_intents:list[str]|None=None, opportunity_universe:dict[str,Any]|None=None)->dict[str,Any]:
    supplied=bool(directions)
    source_rows=list(directions or _auto_directions(product_truth,curation,culture,platform_compile,category_family,decision_intents,opportunity_universe))
    rows=[]
    for d in source_rows:
        row=dict(d); row['direction_id']=row.get('direction_id') or 'DIR-'+stable_hash(row)[:8].upper()
        for k in ['product_fit','audience_fit','platform_fit','culture_fit','differentiation','production_feasibility','decision_coverage','opportunity_fit']:
            row.setdefault(k,0.80)
        row['score']=_score(row); rows.append(row)
    rows.sort(key=lambda x:(x.get('score',0),x.get('opportunity_score',0),x.get('direction_id','')),reverse=True)
    selected=next((x for x in rows if str(x.get('decision')).upper()=='SELECT'), rows[0] if rows else None)
    if selected: selected=dict(selected); selected['decision']='SELECT'
    alternatives=[x for x in rows if not selected or x.get('direction_id')!=selected.get('direction_id')]
    return {
        'status':'SELECTED' if selected else 'NO_DIRECTION_AVAILABLE',
        'direction_source':'USER_SUPPLIED' if supplied else 'CREATIVE_OPPORTUNITY_SYNTHESIS',
        'directions':rows,'selected_direction':selected,'alternative_directions':alternatives,
        'creative_opportunity_universe_status':(opportunity_universe or {}).get('status') if opportunity_universe else 'COMPATIBILITY_FALLBACK',
        'creative_opportunity_count':(opportunity_universe or {}).get('opportunity_count') if opportunity_universe else 12,
        'selected_opportunity_ids':(selected or {}).get('opportunity_ids') or [],
        'search_before_selection_trace':{'rule':'Explore until the agent has enough materially different, evidence-supported options to make the decision. No fixed mechanism or direction count is authoritative. Stable route labels are compatibility tags only.','opportunity_status':(opportunity_universe or {}).get('status'),'opportunity_count':(opportunity_universe or {}).get('opportunity_count'),'direction_count':len(rows)},
        'minimum_material_difference_contract':{'required_differences':'TASK_DEPENDENT','dimensions':['buyer_entry','creative_thesis','composition_grammar','product_role','image_language','proof_mechanism','verbal_thesis','color_world'],'rule':'Differentiate on the dimensions that materially change the shopper experience; do not satisfy a numeric diversity quota.'},
        'council_roles':['ECOMMERCE_STRATEGY','BUYER_DECISION','ART_DIRECTION','PRODUCT_TRUTH','CLAIMS_EVIDENCE','PLATFORM_COMPLIANCE','LOCALIZATION','PRODUCTION_SCALABILITY'],
        'red_team_checks':['product_truth_fit','shopper_decision_fit','culture_fit','platform_fit','production_feasibility','category_cliche_risk','same_layout_collapse_risk','fixed_direction_library_leak'],
        'curation_status':curation.get('status'),'culture_status':culture.get('status'),'platform_status':platform_compile.get('status'),
        'truth_bound':bool(product_truth),
        'principle':'The selected design system creates coherence, not sameness. Directions are synthesized from the current Creative Opportunity Universe; asset-level expression still changes with buyer decision, evidence plane, Surface and production mode.'
    }

def _expression_variant(asset:dict[str,Any], direction:dict[str,Any], ordinal:int)->dict[str,Any]:
    """Derive expression from the actual asset decision signature; never rotate a fixed layout library."""
    del ordinal
    sig=dict(asset.get('visual_production_signature') or {})
    authored=asset.get('agent_visual_expression') if isinstance(asset.get('agent_visual_expression'),dict) else {}
    composition=authored.get('composition_grammar') or sig.get('composition_grammar') or 'Build hierarchy from the decision-critical evidence relationship.'
    view=authored.get('preferred_view') or authored.get('camera_or_view') or sig.get('camera_or_view') or 'Choose the view that exposes the decision-critical evidence plane.'
    context=authored.get('context_role') or sig.get('context_role') or 'Include only context that changes the shopper decision.'
    variant_id=authored.get('variant_id') or 'EXPR-'+stable_hash([asset.get('asset_id'),asset.get('decision_intent'),composition,view,context,direction.get('direction_id')])[:8].upper()
    return {
        'variant_id':variant_id,
        'spatial_rhythm':authored.get('spatial_rhythm') or 'DECISION_DERIVED',
        'composition_grammar':composition,
        'preferred_view':view,
        'context_role':context,
        'direction_id':direction.get('direction_id'),'direction_route':direction.get('route'),'direction_thesis':direction.get('creative_thesis'),
        'authority':'AGENT_OR_ASSET_DECISION_SIGNATURE' if authored or sig else 'GENERAL_FALLBACK',
        'same_layout_guard':'Do not inherit the previous asset composition. Rebuild hierarchy from this asset decision job and its evidence plane.',
    }

def apply_creative_system_to_assets(architecture:dict[str,Any], council:dict[str,Any], cmf:dict[str,Any]|None=None, photography:dict[str,Any]|None=None)->dict[str,Any]:
    selected=(council or {}).get('selected_direction') or {}; alternatives=(council or {}).get('alternative_directions') or []
    assets=[]
    for i,raw in enumerate(architecture.get('assets') or []):
        a=dict(raw)
        # Use selected system for continuity; for jobs that structurally benefit from another route, inherit a secondary influence.
        direction=selected
        intent=str(a.get('decision_intent') or '').upper()
        if alternatives:
            preferred={'PROOF':'EVIDENCE_MECHANISM','PERFORMANCE_PROOF':'EVIDENCE_MECHANISM','MATERIAL_SENSORY':'MATERIAL_SENSORY_OBJECT','USAGE':'HUMAN_CONTEXT_ACTION','FIT_WEAR':'HUMAN_CONTEXT_ACTION','RELEVANCE':'HUMAN_CONTEXT_ACTION'}.get(intent)
            direction=next((d for d in [selected]+alternatives if d.get('route')==preferred),selected)
        expression=_expression_variant(a,direction,i)
        sig=dict(a.get('visual_production_signature') or {})
        sig.update({
            'creative_direction_id':direction.get('direction_id'),
            'creative_direction_route':direction.get('route'),
            'expression_variant':expression,
            'composition_grammar':expression.get('composition_grammar') or sig.get('composition_grammar'),
            'camera_or_view':expression.get('preferred_view') or sig.get('camera_or_view'),
            'context_role':expression.get('context_role') or sig.get('context_role'),
        })
        a['visual_production_signature']=sig
        a['creative_direction']=direction
        a['visual_expression_variant']=expression
        brief=dict(a.get('creative_brief') or {})
        brief.update({
            'creative_thesis':direction.get('creative_thesis'),
            'composition':expression.get('composition_grammar'),
            'camera_or_view':expression.get('preferred_view'),
            'lighting':direction.get('photography'),
            'color':(cmf or {}).get('color') or direction.get('color_world'),
            'typography':direction.get('typography'),
            'scene_props':direction.get('scene_props'),
            'image_language':direction.get('image_language'),
            'proof_mechanism':direction.get('proof_mechanism'),
            'verbal_thesis':direction.get('verbal_thesis'),
        })
        a['creative_brief']=brief
        assets.append(a)
    out=dict(architecture); out['assets']=assets
    out['creative_system_assignment']={
        'selected_direction_id':selected.get('direction_id'),
        'selected_direction':selected,
        'direction_count':len((council or {}).get('directions') or []),
        'asset_expression_count':len(assets),
        'same_layout_guard':'Coherence comes from shared truth/color/type/material principles; composition, camera, product role and evidence plane must change with the asset decision job.'
    }
    return out


def compile_cmf(cmf:dict[str,Any]|None)->dict[str,Any]:
    cmf=cmf or {}; issues=[]
    for key in ['color','material','finish']:
        if not cmf.get(key): issues.append(key)
    surface=cmf.get('surface_behavior',{}) or {}
    return {
        'status':'EXECUTION_READY' if not issues else ('PARTIAL' if cmf else 'NOT_SUPPLIED'),
        'color':cmf.get('color'),'material':cmf.get('material'),'finish':cmf.get('finish'),
        'surface_behavior':surface,'missing':issues,
        'capture_implications':cmf.get('capture_implications',[]),
        'post_implications':cmf.get('post_implications',[])
    }


def compile_inclusive_photography(culture:dict[str,Any], photography:dict[str,Any]|None, assets:list[dict[str,Any]]|None=None)->dict[str,Any]:
    photo=photography or {}; human=photo.get('human') or {}; casting=culture.get('casting_constraints',{}) or {}; inter=culture.get('intersectionality',{}) or {}
    human_intents={'RELEVANCE','USAGE','FIT_WEAR','SIZE_FIT','SENSORY_PREP'}
    human_required=False; reasons=[]
    for a in assets or []:
        intent=str(a.get('decision_intent') or '').upper()
        route=str((a.get('creative_direction') or {}).get('route') or '').upper()
        sig=a.get('visual_production_signature') or {}
        context=' '.join(str(sig.get(k) or '') for k in ['context_role','visual_job','camera_or_view']).lower()
        if intent in human_intents or 'HUMAN_CONTEXT' in route or any(x in context for x in ['human','hand','body','wear','use context','routine']):
            human_required=True; reasons.append({'asset_id':a.get('asset_id'),'intent':intent,'route':route,'context_role':sig.get('context_role')})
    present=bool(human.get('present') or casting or human_required)
    skin=human.get('skin_tone_exposure') or ({
        'metering':'Meter skin and product/label separately; protect highlights and retain shadow chroma/detail.',
        'deep_skin_bracket':'Use neutral reference and test +0.3 / +0.7 EV brackets only as starting comparisons when needed; choose final exposure by truthful skin tone, highlight protection and product readability.',
        'reflector':'Use neutral white/soft fill to recover shadow detail; avoid tiny hard silver sources that create artificial hotspots unless the scene deliberately needs that texture.',
        'diffusion':'Large diffusion close enough to create broad tonal transitions; add negative fill for form rather than underexposing deep skin.',
        'post':'No automatic whitening, skin-tone homogenization or texture erasure.'
    } if present else {})
    hair={
        'hair':(casting.get('hair') if isinstance(casting,dict) else None) or ('Preserve real straight/wavy/curly/coily/protective style texture; use edge separation for dark hair instead of changing texture.' if present else None),
        'wardrobe':(casting.get('wardrobe') if isinstance(casting,dict) else None) or ('Choose wardrobe from product task, locale and scene; do not use ethnicity as costume.' if present else None),
        'makeup':(casting.get('makeup') if isinstance(casting,dict) else None) or ('Keep real skin texture/tone; makeup supports the scene and product, not whitening/youthifying.' if present else None),
    }
    return {
        'status':'APPLICABLE_P0' if present else 'NOT_APPLICABLE_NO_HUMAN_ASSET',
        'activation_basis':reasons,
        'casting':casting,
        'intersectionality_context':inter,
        'skin_tone_exposure':skin,
        'hair_and_styling':hair,
        'body_age_disability':({'rule':'Represent age/body/disability naturally when relevant to the target/use case; do not erase mobility aids, age markers or body diversity in generation/retouching.','casting_boundary':'No tokenistic or inspirational framing; the person exists to perform the real decision/use task.'} if present else {}),
        'ai_bias_controls':(['no default whitening','no slimming/body reshaping','no youthifying','no hair-texture homogenization','no disability erasure','check hands/assistive devices/hair edges/body proportions'] if present else []),
        'representation_principle':'Represent the approved audience context without using identity dimensions as automatic behavior predictions.',
        'review_required':present,
        'p0_rule':'If people/hands/body relation appear in any asset, inclusive photography and AI-bias QA are P0 production requirements.'
    }
