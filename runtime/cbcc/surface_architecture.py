from __future__ import annotations
from typing import Any

# Surface architecture is a planning authority, not a fixed quota.  It classifies which expression
# form is appropriate for each information job and enriches assets with production-relevant states.
SURFACE_UNIVERSE = [
    'SEARCH_RESULTS','LISTING_PRIMARY','PDP_HERO','GALLERY','PDP','LONGFORM','A_PLUS','PDP_VIDEO',
    'SHORT_VIDEO','CREATOR','LIVE','PAID_AD','SOCIAL_CONTENT','STORE_BANNER','LANDING_PAGE_HERO',
    'COMPARISON','SPECIFICATION','FAQ','UGC_BRIEF','POST_PURCHASE','CRM'
]

_NATIVE_TEXT_INTENTS={'WARRANTY_SERVICE','DELIVERY_INSTALLATION','TOTAL_COST_OWNERSHIP','EXPECTATION_BOUNDARY','CARE_MAINTENANCE'}
_HYBRID_INTENTS={'PROOF','PERFORMANCE_PROOF','COMPATIBILITY','SIZE_CAPACITY','SIZE_FIT','INGREDIENT_COMPOSITION','INGREDIENT_DIETARY','PACKAGE_CONTENTS'}
_HUMAN_INTENTS={'RELEVANCE','USAGE','FIT_WEAR','PORTABILITY','SENSORY_PREP'}
_PRODUCT_REQUIRED={'IDENTIFY','DIFFERENTIATION','MATERIAL_SENSORY','SEAL_LEAK','STORAGE_STACKING','PERFORMANCE_PROOF','FIT_WEAR','PORTABILITY'}
_PRODUCT_OPTIONAL={'PROOF','INGREDIENT_COMPOSITION','INGREDIENT_DIETARY','WARRANTY_SERVICE','DELIVERY_INSTALLATION','CARE_MAINTENANCE','EXPECTATION_BOUNDARY'}


def _copy_budget(surface:str, intent:str, visible_copy:dict[str,Any]|None=None)->dict[str,Any]:
    """Semantic budget only.  It intentionally avoids inventing platform character limits."""
    surface=str(surface or '').upper(); intent=str(intent or '').upper(); visible_copy=visible_copy or {}
    if surface in {'SEARCH_RESULTS','LISTING_PRIMARY'}:
        units=1; layers=1; density='ULTRA_LOW'; product_dominance='VERY_HIGH'
    elif surface in {'PDP_HERO','PAID_AD','STORE_BANNER','LANDING_PAGE_HERO'}:
        units=2; layers=2; density='LOW'; product_dominance='HIGH'
    elif surface in {'GALLERY','COMPARISON','SPECIFICATION','FAQ'}:
        units=3 if intent in _HYBRID_INTENTS else 2; layers=3; density='MEDIUM'; product_dominance='MEDIUM_OR_JOB_DEPENDENT'
    elif surface in {'LONGFORM','A_PLUS','PDP'}:
        units=4; layers=4; density='SURFACE_NATIVE'; product_dominance='JOB_DEPENDENT'
    else:
        units=2; layers=2; density='LOW_TO_MEDIUM'; product_dominance='JOB_DEPENDENT'
    return {
        'message_unit_budget':units,
        'text_layer_budget':layers,
        'density_class':density,
        'product_dominance_target':product_dominance,
        'locked_copy':visible_copy,
        'hard_character_limit':None,
        'hard_limit_source':'CURRENT_PLATFORM_RULE_ONLY',
        'overflow_rule':'Move secondary explanation to the next native surface/text field instead of shrinking everything into one frame.'
    }


def _representation(intent:str, surface:str)->dict[str,Any]:
    intent=str(intent or '').upper(); surface=str(surface or '').upper()
    if intent in _NATIVE_TEXT_INTENTS and surface in {'FAQ','PDP','LONGFORM','CRM','POST_PURCHASE'}:
        mode='HYBRID' if intent in {'CARE_MAINTENANCE','DELIVERY_INSTALLATION'} else 'NATIVE_TEXT'
    elif intent in _HYBRID_INTENTS:
        mode='HYBRID'
    elif surface in {'FAQ','CRM','POST_PURCHASE'}:
        mode='NATIVE_TEXT'
    else:
        mode='IMAGE'
    return {
        'representation':mode,
        'reason':{
            'IMAGE':'The decision is best resolved through a visible spatial, product, human or evidence relationship.',
            'HYBRID':'The decision needs both visual evidence and precise explanatory copy/data.',
            'NATIVE_TEXT':'The decision is primarily precision/explanation-heavy and should not be forced into a poster-like image.'
        }[mode]
    }


def _product_presence(intent:str, surface:str)->dict[str,Any]:
    intent=str(intent or '').upper(); surface=str(surface or '').upper()
    if intent in _PRODUCT_REQUIRED or surface in {'SEARCH_RESULTS','LISTING_PRIMARY','PDP_HERO'}:
        state='REQUIRED'
    elif intent in _PRODUCT_OPTIONAL:
        state='OPTIONAL'
    elif surface in {'FAQ','POST_PURCHASE','CRM'}:
        state='OPTIONAL'
    else:
        state='REQUIRED'
    return {
        'planning_state':state,
        'production_resolution':'PRESENT' if state=='REQUIRED' else 'RESOLVE_PER_BLUEPRINT',
        'principle':'Product presence is a decision-role choice, not a rule that every asset must show a complete packshot.'
    }


def compile_surface_architecture(target:dict[str,Any], content_objects:list[dict[str,Any]], assets:list[dict[str,Any]], platform_compile:dict[str,Any]|None=None)->dict[str,Any]:
    platform_compile=platform_compile or {}; requested=set(target.get('surfaces') or []); supported=set(platform_compile.get('surfaces') or [])
    active_surfaces={str(a.get('surface')) for a in assets if a.get('surface')}
    object_surfaces={str(o.get('surface')) for o in content_objects if o.get('surface')}
    rows=[]
    for surface in SURFACE_UNIVERSE:
        if surface in active_surfaces:
            status='REQUIRED'; reason='Selected by the dynamic decision-to-asset architecture.'
        elif surface in requested:
            status='OPTIONAL'; reason='Explicitly requested target surface; no incremental asset was necessary yet.'
        elif surface in object_surfaces:
            status='OPTIONAL'; reason='Available as a content-object expression surface when an incremental decision job requires it.'
        else:
            status='NOT_APPLICABLE'
            reason='No current buyer-decision, platform or content-object requirement activates this surface.'
        if supported and surface not in supported and status in {'REQUIRED','OPTIONAL'}:
            evidence='PLANNING_AVAILABLE_CURRENT_PLATFORM_EVIDENCE_REQUIRED'
        else:
            evidence='VERIFIED_OR_NOT_REQUIRED'
        rows.append({'surface':surface,'status':status,'reason':reason,'platform_evidence_state':evidence})

    enriched=[]
    for asset in assets:
        a=dict(asset); intent=a.get('decision_intent'); surface=a.get('surface')
        rep=_representation(intent,surface); presence=_product_presence(intent,surface); budget=_copy_budget(surface,intent,a.get('visible_copy'))
        a['information_assetization']=rep
        a['product_presence']=presence
        a['surface_copy_budget']=budget
        a['surface_native_contract']={
            'surface':surface,
            'decision_job':a.get('strategic_job'),
            'representation':rep['representation'],
            'product_presence':presence['planning_state'],
            'copy_budget':budget,
            'mobile_scan_rule':'One primary decision answer must survive thumbnail/mobile scanning; supporting detail may move to adjacent native content.',
            'reuse_rule':'Reuse product truth and evidence; recurate composition/copy when the surface job changes instead of mechanically resizing artwork.'
        }
        enriched.append(a)
    decision_objects=[]
    for a in enriched:
        decision_objects.append({
            'object_id':'DCO-'+str(a.get('asset_id') or ''),
            'kind':'commerce_decision_content','family':a.get('family'),'surface':a.get('surface'),'curation_job':a.get('strategic_job'),
            'consumer_question':a.get('consumer_question'),'decision_intent':a.get('decision_intent'),'race_stage':a.get('race_stage'),
            'information_representation':(a.get('information_assetization') or {}).get('representation'),'product_presence':(a.get('product_presence') or {}).get('planning_state'),
            'copy_budget':a.get('surface_copy_budget'),'source_ids':a.get('source_ids') or [],'claim_ids':a.get('claim_ids') or [],
            'dependencies':a.get('dependencies') or [],'asset_id':a.get('asset_id')
        })
    return {
        'status':'DYNAMIC_SURFACE_ARCHITECTURE_COMPILED',
        'fixed_surface_quota':False,
        'surface_universe':rows,
        'assets':enriched,
        'decision_content_objects':decision_objects,
        'information_assetization_modes':['IMAGE','NATIVE_TEXT','HYBRID','SOURCE_VIEW','NOT_NEEDED','OFF_DOMAIN_HANDOFF'],
        'principle':'Information becomes an image only when image is the best decision medium. Surface count and asset count are consequences of buyer decisions, evidence and platform roles, never quotas.'
    }
