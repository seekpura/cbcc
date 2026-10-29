from __future__ import annotations
import re
from typing import Any
from .models import stable_hash
from .category_strategy import classify_decision_intent, decision_profile, surface_score

SURFACE_TO_MODE={
    'GALLERY':'AI_REFERENCE_PRODUCT','PDP':'GRAPHIC_DESIGN','PDP_VIDEO':'VIDEO',
    'CREATOR':'AI_REFERENCE_HUMAN_PRODUCT','PAID_AD':'GRAPHIC_DESIGN','FAQ':'DOCUMENTATION',
    'SEARCH_RESULTS':'AI_REFERENCE_PRODUCT','LIVE':'VIDEO','CRM':'GRAPHIC_DESIGN','LONGFORM':'GRAPHIC_DESIGN','A_PLUS':'GRAPHIC_DESIGN','SOCIAL_CONTENT':'GRAPHIC_DESIGN','STORE_BANNER':'GRAPHIC_DESIGN','LANDING_PAGE_HERO':'AI_REFERENCE_PRODUCT','COMPARISON':'GRAPHIC_DESIGN','SPECIFICATION':'GRAPHIC_DESIGN','UGC_BRIEF':'DOCUMENTATION','POST_PURCHASE':'GRAPHIC_DESIGN','SHORT_VIDEO':'VIDEO'
}

def _norm(s:str)->str: return ' '.join(str(s or '').split()).casefold()

def _decision_topic_signature(question:str,intent:str)->str:
    q=_norm(question)
    # Same intent does not automatically mean duplicate information.  Merge only within a stable
    # sub-topic; this preserves separate proof/operation questions while still combining repeated
    # capacity or wear/adjustment questions.
    if intent=='PROOF':
        if any(x in q for x in ['clinical','study','trial','tested','test condition']): return 'CLINICAL_EVIDENCE'
        if any(x in q for x in ['formula','ingredient','concentration','%']): return 'FORMULA_FACTS'
        return 'GENERAL_PROOF'
    if intent=='PERFORMANCE_PROOF':
        if any(x in q for x in ['insulation','cold','temperature']): return 'THERMAL_PERFORMANCE'
        if any(x in q for x in ['power sharing','simultaneous','multiple device','how many devices']): return 'MULTI_DEVICE_PERFORMANCE'
        return 'TASK_PERFORMANCE'
    if intent=='USAGE':
        if any(x in q for x in ['routine','step','when do','where does it fit']): return 'ROUTINE_USE'
        return 'OPERATION_USE'
    if intent=='DECISION_SUPPORT':
        if any(x in q for x in ['pocket','organization','organize','compartment']): return 'ORGANIZATION'
        if any(x in q for x in ['display','screen','readout']): return 'DISPLAY_VALUE'
        return stable_topic_tokens(q)
    if intent in {'FIT_WEAR','SIZE_CAPACITY','PACKAGE_CONTENTS','SEAL_LEAK','STORAGE_STACKING','CARE_MAINTENANCE','WEATHER_BOUNDARY','PORTABILITY','DIFFERENTIATION','INGREDIENT_COMPOSITION'}:
        return intent
    return stable_topic_tokens(q)

def stable_topic_tokens(q:str)->str:
    stop={'what','which','where','when','how','does','do','did','is','are','it','this','the','a','an','my','me','i','and','or','to','of','in','for','with','from','real','actually','should','can','will'}
    toks=[x.strip('.,?!:;()[]{}').casefold() for x in q.split()]
    toks=[x for x in toks if x and x not in stop and len(x)>2]
    return '|'.join(sorted(dict.fromkeys(toks))[:6]) or 'GENERAL'


def _visual_production_signature(intent:str, topic:str, surface:str, mode:str)->dict[str,Any]:
    """Decision-led production grammar used only when the author has not supplied a stronger one.

    This is not a fixed asset template or sequence.  It gives each decision job a distinct visual
    information shape so Provider execution does not collapse different questions into the same
    centered-packshot composition.
    """
    intent=str(intent or 'DECISION_SUPPORT').upper(); topic=str(topic or 'GENERAL').upper(); surface=str(surface or 'GALLERY').upper(); mode=str(mode or 'GRAPHIC_DESIGN').upper()
    profiles={
      'IDENTIFY': {
        'visual_job':'Make product identity and the primary proposition recoverable at first scan.',
        'composition_grammar':'identity-led hero; one dominant product anchor; deliberate negative space tied to locked copy',
        'camera_or_view':'front or truthful three-quarter view chosen for label/shape legibility, not decorative angle',
        'evidence_plane':'product identity / exact pack face',
        'context_role':'minimal context; context may support category recognition but must not compete with identity',
        'differentiation_axis':'scale + silhouette + label recoverability',
      },
      'USAGE': {
        'visual_job':'Show the actual operation/routine relationship that reduces use uncertainty.',
        'composition_grammar':'action-led process or interaction frame; product participates in the action rather than posing as a hero',
        'camera_or_view':'viewpoint that exposes hand/object/step relationship and the decision-critical contact point',
        'evidence_plane':'operation step / sequence / handling',
        'context_role':'realistic use context is primary; product remains identifiable but not artificially oversized',
        'differentiation_axis':'action choreography + step visibility',
      },
      'PROOF': {
        'visual_job':'Make the approved proof object legible and attributable to the product without turning proof into decoration.',
        'composition_grammar':'evidence-led hierarchy; proof or verified number is primary, product acts as traceable signature',
        'camera_or_view':'orthographic/graphic or evidence-plane view; use macro only when the evidence itself is physical',
        'evidence_plane':'approved claim / study / formula / measurable proof',
        'context_role':'supporting context only when it clarifies what the proof means',
        'differentiation_axis':'proof hierarchy + traceability',
      },
      'PERFORMANCE_PROOF': {
        'visual_job':'Show the product performing the named task or make the measurable performance relationship understandable.',
        'composition_grammar':'task/result relationship; product, input and outcome occupy a causal spatial relationship',
        'camera_or_view':'angle that exposes the task mechanism and comparison scale without hiding the product',
        'evidence_plane':'task performance / measurable relation',
        'context_role':'functional context is part of the evidence, not lifestyle decoration',
        'differentiation_axis':'task geometry + measurable relationship',
      },
      'COMPATIBILITY': {
        'visual_job':'Show what the product works with and where the boundary is.',
        'composition_grammar':'relationship diagram or real-object pairing; compatible object/context is visible in the same decision frame',
        'camera_or_view':'view exposing ports, dimensions, attachment points or pairing relationship',
        'evidence_plane':'compatibility boundary / connection point',
        'context_role':'only the devices/objects needed to resolve compatibility',
        'differentiation_axis':'object relationship + boundary visibility',
      },
      'PORTABILITY': {
        'visual_job':'Make carry burden and real-world scale understandable before purchase.',
        'composition_grammar':'scale-in-context; human hand/bag/desk/carry reference provides truthful size burden',
        'camera_or_view':'perspective preserving product scale relative to the chosen reference',
        'evidence_plane':'physical scale / carry context',
        'context_role':'context is the measurement reference',
        'differentiation_axis':'scale reference + carry scenario',
      },
      'SIZE_CAPACITY': {
        'visual_job':'Translate abstract dimensions/capacity into a purchase-use judgment.',
        'composition_grammar':'dimension or contents-reveal composition; numeric/scale information aligns to the physical object',
        'camera_or_view':'orthographic or open/section view that makes usable space measurable',
        'evidence_plane':'dimensions / capacity / contained objects',
        'context_role':'reference objects exist only to calibrate size/capacity',
        'differentiation_axis':'measurement + contents relationship',
      },
      'FIT_WEAR': {
        'visual_job':'Show on-body or in-situation fit instead of describing fit abstractly.',
        'composition_grammar':'human fit frame with the relevant body relationship, strap/drape/scale or wearing position visible',
        'camera_or_view':'distance and angle chosen to preserve the fit relationship rather than beauty portrait priority',
        'evidence_plane':'on-body fit / adjustment / wearing position',
        'context_role':'human is the fit reference, not a generic lifestyle model',
        'differentiation_axis':'body relationship + adjustment state',
      },
      'CARE_MAINTENANCE': {
        'visual_job':'Make cleaning, disassembly or maintenance steps and boundaries obvious.',
        'composition_grammar':'maintenance action or exploded/step view; relevant parts separated only as needed to show the process',
        'camera_or_view':'close functional view of the part being cleaned/removed/handled',
        'evidence_plane':'care action / removable parts / cleaning access',
        'context_role':'sink/tool/cloth only when it is part of the actual maintenance instruction',
        'differentiation_axis':'part state + maintenance action',
      },
      'SEAL_LEAK': {
        'visual_job':'Make closure state, seal mechanism or leak expectation visible.',
        'composition_grammar':'mechanism-led close view plus orientation/use state; do not rely on generic splash symbolism',
        'camera_or_view':'close angle exposing lid, seal, valve or closure interface',
        'evidence_plane':'closure/seal state',
        'context_role':'orientation or carry state exists to test the actual leak question',
        'differentiation_axis':'mechanism close-up + orientation',
      },
      'WEATHER_BOUNDARY': {
        'visual_job':'Show the supported environmental boundary without implying stronger protection than evidenced.',
        'composition_grammar':'environmental context with the product/material response readable; boundary statement stays visually attached to the relevant surface/feature',
        'camera_or_view':'angle that preserves material/closure evidence under the environmental condition',
        'evidence_plane':'supported weather/material boundary',
        'context_role':'weather is controlled evidence context, not cinematic spectacle',
        'differentiation_axis':'environment condition + material response',
      },
      'DIFFERENTIATION': {
        'visual_job':'Make the product-specific mechanism or usage distinction understandable without generic premium styling.',
        'composition_grammar':'feature-mechanism or mode comparison inside the same product; emphasize what is structurally different',
        'camera_or_view':'view exposing the differentiating feature or alternate mode',
        'evidence_plane':'product-specific differentiator',
        'context_role':'only context required to make the difference legible',
        'differentiation_axis':'mechanism / mode / structural difference',
      },
      'MATERIAL_SENSORY': {
        'visual_job':'Translate material or sensory character through truthful surface cues.',
        'composition_grammar':'material-led macro/detail with enough product identity to attribute the surface/texture correctly',
        'camera_or_view':'macro/detail view preserving truthful texture, finish and scale',
        'evidence_plane':'material / texture / finish',
        'context_role':'minimal; lighting and scale cues carry the material information',
        'differentiation_axis':'surface texture + highlight behavior',
      },
    }
    base=profiles.get(intent, {
        'visual_job':'Resolve the named shopper decision with one clearly visible information relationship.',
        'composition_grammar':'decision-led composition; the primary information relationship determines hierarchy instead of a reusable hero-card template',
        'camera_or_view':'view chosen to expose the decision-critical evidence plane',
        'evidence_plane':topic or intent,
        'context_role':'include only context that changes understanding of the decision',
        'differentiation_axis':'decision-specific evidence relationship',
    }).copy()
    if surface in {'CREATOR','LIVE'}:
        base['surface_native_modifier']='human/action opening and native framing may lead, but the assigned decision evidence must remain recoverable without relying on generic lifestyle mood.'
    elif surface in {'GALLERY','SEARCH_RESULTS','PDP'}:
        base['surface_native_modifier']='mobile-scan hierarchy; one primary answer per frame; preserve safe copy/product zones without defaulting every asset to the same centered-card layout.'
    elif surface=='PAID_AD':
        base['surface_native_modifier']='attention may be faster and bolder, but the hook must be the decision-specific evidence relationship rather than arbitrary visual novelty.'
    else:
        base['surface_native_modifier']='adapt to the target surface while preserving the decision-specific information hierarchy.'
    base.update({'decision_intent':intent,'decision_topic':topic,'surface':surface,'production_mode':mode})
    return base


def _editable_layer_contract(mode:str, product_fidelity:str)->dict[str,Any]:
    mode=str(mode or '').upper(); fidelity=str(product_fidelity or '').upper()
    layers=['typography_copy','layout_spacing','background_environment','shadow_contact','color_grade']
    if mode in {'AI_HUMAN_REAL_PRODUCT','VIDEO','REAL_PHOTO'}: layers += ['human_context','wardrobe_grooming','camera_crop','lighting_environment']
    if mode in {'GRAPHIC_DESIGN','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','VIDEO'}: layers += ['prop_context','graphic_evidence_layer']
    locked=fidelity in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}
    if locked:
        frozen=['product_master_pixels','logo','packaging_print','product_geometry','product_color_identity']
        rule='Explicit locked-source mode: source product pixels/identity stay immutable; only declared editable layers may change.'
    else:
        frozen=['verified_product_facts','approved_claim_facts','locked_copy']
        rule='Reference-guided mode: source files guide product design/identity but are not immutable pixel layers. Visual form may be redrawn, rerendered, restyled or recomposed; do not turn creative interpretation into unsupported product facts or claims.'
    return {'editable_layers':list(dict.fromkeys(layers)),'frozen_layers':frozen,'revision_rule':rule}


def _decision_profile(question:str, surface:str, family:str)->dict[str,Any]:
    intent=classify_decision_intent(question, category_family=family)
    return decision_profile(intent,question)


def _surface_score(question:str, obj:dict[str,Any], category_family:str='GENERAL_COMMERCE')->int:
    return surface_score(classify_decision_intent(question,category_family),obj,category_family)


def _atomic_question_parts(question:str, category_family:str)->list[dict[str,Any]]:
    q=' '.join(str(question or '').split())
    # Split only explicit compound interrogatives.  This prevents one long shopper question from
    # silently losing a second independent decision job (identity + routine, size + on-body fit).
    # If both clauses resolve to the same intent, keep the original question as one job.
    parts=re.split(r'\s+and\s+(?=(?:what|how|where|which|when|will|can|is|are|does|do)\b)',q,flags=re.I)
    if len(parts)!=2: return [{'question':q}]
    left,right=parts[0].strip(' ?'),parts[1].strip(' ?')
    if len(left.split())<3 or len(right.split())<3: return [{'question':q}]
    li=classify_decision_intent(left,category_family); ri=classify_decision_intent(right,category_family)
    # A generic boundary follow-up often qualifies the same specific capability (e.g.
    # water-repellent + "what is the boundary?").  Do not manufacture a second asset job.
    if 'EXPECTATION_BOUNDARY' in {li,ri} and li != ri:
        specific=ri if li=='EXPECTATION_BOUNDARY' else li
        if specific not in {'DECISION_SUPPORT','IDENTIFY'}:
            return [{'question':q,'decision_intent':specific}]
    if li=='DECISION_SUPPORT' or ri=='DECISION_SUPPORT' or li==ri: return [{'question':q}]
    return [
      {'question':left+'?','compound_parent':q,'compound_part':1,'decision_intent':li},
      {'question':right+'?','compound_parent':q,'compound_part':2,'decision_intent':ri},
    ]

def _context_questions(base:list[str], decision_context:dict[str,Any]|None, category_family:str='GENERAL_COMMERCE')->list[dict[str,Any]]:
    out=[]
    for q in (base or []):
        if not _norm(q): continue
        for part in _atomic_question_parts(q,category_family):
            out.append({'origin':'SHOPPER_QUESTION',**part})
    seen={_norm(x['question']) for x in out}; ctx=decision_context or {}
    # Listing objections are already semantically classified upstream.
    for row in ctx.get('listing_objections',[]) or []:
        text=row.get('objection') if isinstance(row,dict) else str(row)
        if text and _norm(text) not in seen:
            out.append({'question':text,'origin':'LISTING_OBJECTION','source':row}); seen.add(_norm(text))
    # Market/review themes create assets only after an explicit Product Truth fit decision.
    for row in ctx.get('market_theme_jobs',[]) or []:
        if not isinstance(row,dict): continue
        fit=str(row.get('fit_status') or row.get('status') or '').upper()
        if fit not in {'CONFIRMED','APPROVED','TRUE','FIT'} and row.get('product_truth_fit') is not True: continue
        theme=str(row.get('theme') or row.get('market_theme') or '').strip()
        q=str(row.get('consumer_question') or row.get('question') or (f'How does this product truthfully address the validated market concern: {theme}?' if theme else '')).strip()
        if q and _norm(q) not in seen:
            out.append({'question':q,'origin':'MARKET_THEME_FIT','source':row}); seen.add(_norm(q))

    # Feedback only creates additional jobs when it points to a communication layer.
    for issue in ctx.get('feedback_issues',[]) or []:
        cat=str(issue.get('category') or '').upper()
        if cat not in {'EXPECTATION_GAP','MISUNDERSTANDING','PARAMETER_CONFUSION','PACKAGE_CONFUSION','USAGE_DIFFICULTY','SIZE','COMPATIBILITY'}: continue
        q={
            'EXPECTATION_GAP':'What expectation should be clarified before purchase?',
            'MISUNDERSTANDING':'What product fact or message is customers misunderstanding?',
            'PARAMETER_CONFUSION':'Which parameter/specification needs clearer decision support?',
            'PACKAGE_CONFUSION':'What exactly is included in the package?',
            'USAGE_DIFFICULTY':'How should the product be used correctly?',
            'SIZE':'What size/scale information prevents a wrong purchase?',
            'COMPATIBILITY':'What compatibility boundary must be clear before purchase?',
        }[cat]
        if _norm(q) not in seen:
            out.append({'question':q,'origin':'FEEDBACK_SIGNAL','source':issue}); seen.add(_norm(q))
    return out


def build_asset_architecture(project_id:str,target:dict,questions:list[str],content_objects:list[dict[str,Any]],asset_jobs:list[dict[str,Any]]|None=None,decision_context:dict[str,Any]|None=None,category_family:str='GENERAL_COMMERCE')->dict[str,Any]:
    """Create assets from decision jobs. Explicit asset_jobs override defaults; no target count exists."""
    jobs=list(asset_jobs or [])
    asset_scope_active=bool(jobs)
    if not jobs:
        candidates=[o for o in content_objects if o.get('family') in {'VISUAL','RICH_CONTENT','VIDEO','CREATOR_AFFILIATE','LIVE','PAID','SOCIAL','STORE','CX','LIFECYCLE'}]
        requested=set(target.get('surfaces') or [])
        requested_candidates=[o for o in candidates if not requested or o.get('surface') in requested]
        if requested_candidates: candidates=requested_candidates
        asset_scope_active=bool(candidates)
        qrows=_context_questions(questions,decision_context,category_family)
        for qrow in qrows:
            q=qrow['question']
            if not candidates:
                # No current visual/video/creator/paid Surface: keep the question in Strategy/Listing; do not manufacture a GALLERY asset.
                continue
            ranked=sorted(candidates,key=lambda o:(_surface_score(q,o,category_family), bool(o.get('required'))),reverse=True)
            o=ranked[0]
            jobs.append({'consumer_question':q,'surface':o.get('surface'),'family':o.get('family'),'strategic_job':o.get('curation_job') or 'Resolve a purchase decision','source_ids':o.get('source_ids',[]),'claim_ids':o.get('claim_ids',[]),'decision_origin':qrow.get('origin'),'decision_source':qrow.get('source'),'decision_intent':qrow.get('decision_intent') or classify_decision_intent(q,category_family),'compound_parent':qrow.get('compound_parent'),'compound_part':qrow.get('compound_part'),'auto_curated':True})
    assets=[]; seen={}
    for idx,j in enumerate(jobs):
        q=' '.join(str(j.get('consumer_question') or '').split())
        if not q: continue
        surface=j.get('surface') or 'GALLERY'; intent=j.get('decision_intent') or classify_decision_intent(q,category_family)
        # Explicit jobs preserve author intent. Auto-curated jobs merge only when intent *and* sub-topic
        # match, preventing unrelated questions (e.g. product identity vs display value) from disappearing.
        topic=_decision_topic_signature(q,intent)
        key=(_norm(q),surface,j.get('family')) if not j.get('auto_curated') else (intent,topic,surface,j.get('family'))
        if key in seen:
            a=assets[seen[key]]; a['source_ids']=sorted(set(a['source_ids']+j.get('source_ids',[]))); a['claim_ids']=sorted(set(a['claim_ids']+j.get('claim_ids',[])))
            merged=a.setdefault('merged_consumer_questions',[a.get('consumer_question')])
            if q not in merged: merged.append(q)
            continue
        aid='AST-'+stable_hash([project_id,target.get('target_id'),q,surface,idx])[:10].upper(); mode=j.get('production_mode') or SURFACE_TO_MODE.get(surface,'GRAPHIC_DESIGN'); profile=decision_profile(intent,q)
        asset={
            'asset_id':aid,'asset_name':j.get('asset_name') or f"{j.get('family','CONTENT')} · {surface}",'asset_type':'VIDEO' if mode=='VIDEO' else ('DOCUMENTATION' if mode=='DOCUMENTATION' else 'IMAGE'),
            'consumer_question':q,'decision_intent':intent,'decision_topic':topic,'purchase_barrier':j.get('purchase_barrier') or profile['purchase_barrier'],'belief_target':j.get('belief_target') or profile['belief_target'],'strategic_job':j.get('strategic_job') or 'Resolve the stated consumer question',
            'journey_stage':j.get('journey_stage') or profile['journey_stage'],'entry_state':j.get('entry_state') or profile['entry_state'],'exit_state':j.get('exit_state') or profile['exit_state'],'race_stage':j.get('race_stage') or profile['race_stage'],
            'surface':surface,'surface_need':j.get('surface_need') or f'{surface} is selected because it is the strongest available surface for this decision question in the current content graph.','family':j.get('family'),
            'reason_to_exist':j.get('reason_to_exist') or profile['reason_to_exist'],'incremental_information':j.get('incremental_information') or profile['incremental_information'],
            'business_hypothesis':j.get('business_hypothesis') or f"If this asset resolves '{q}', the next-stage metric ({j.get('success_metric') or profile['success_metric']}) should improve without requiring unrelated strategy changes.",
            'decision_origin':j.get('decision_origin') or 'EXPLICIT_ASSET_JOB','decision_source':j.get('decision_source'),'compound_parent':j.get('compound_parent'),'compound_part':j.get('compound_part'),
            'handoff':j.get('handoff'),'production_mode':mode,'product_fidelity':j.get('product_fidelity','REFERENCE_GUIDED_NATIVE_LOCK'),'approved_visual_elements':j.get('approved_visual_elements',[]),'precision_boundaries':j.get('precision_boundaries',[]),
            'source_ids':j.get('source_ids',[]),'claim_ids':j.get('claim_ids',[]),'listing_reference':j.get('listing_reference',[]),'priority':j.get('priority','P1'),'status':j.get('status','ACTIVATE'),'dependencies':j.get('dependencies',[]),
            'success_metric':j.get('success_metric') or profile['success_metric'],'visible_copy':j.get('visible_copy',{}),'creative_brief':j.get('creative_brief',{}),
            'visual_production_signature':j.get('visual_production_signature') or _visual_production_signature(intent,topic,surface,mode),
            'editable_layer_contract':j.get('editable_layer_contract') or _editable_layer_contract(mode,j.get('product_fidelity','REFERENCE_GUIDED_NATIVE_LOCK'))
        }
        seen[key]=len(assets); assets.append(asset)
    # List order is presentation only. Asset relationships/handoffs are explicit author decisions.

    # Preserve an explicit question -> atomic decision -> asset lineage.  This is not a gate: it is
    # the audit trail that prevents an aggressive merge from silently swallowing incremental buyer information.
    decision_audit=[]
    for j in jobs:
        q=' '.join(str(j.get('consumer_question') or '').split())
        if not q: continue
        intent=j.get('decision_intent') or classify_decision_intent(q,category_family)
        topic=_decision_topic_signature(q,intent)
        matched=None; merged=False
        for a in assets:
            qs=[a.get('consumer_question')]+list(a.get('merged_consumer_questions') or [])
            if q in [x for x in qs if x]:
                matched=a; merged=(q!=a.get('consumer_question')); break
        decision_audit.append({
            'source_question':j.get('compound_parent') or q,
            'atomic_question':q,
            'compound_parent':j.get('compound_parent'),
            'compound_part':j.get('compound_part'),
            'decision_origin':j.get('decision_origin') or 'EXPLICIT_ASSET_JOB',
            'decision_intent':intent,'decision_topic':topic,
            'coverage_status':'MERGED_INTO_ASSET' if matched and merged else ('DEDICATED_ASSET' if matched else 'UNCOVERED'),
            'asset_id':matched.get('asset_id') if matched else None,
            'surface':matched.get('surface') if matched else j.get('surface'),
            'incremental_information':matched.get('incremental_information') if matched else None,
            'merge_basis':('SAME_INTENT_TOPIC_SURFACE_FAMILY' if matched and merged else None),
        })
    uncovered=[x for x in decision_audit if x['coverage_status']=='UNCOVERED']
    unrouted_questions=[]
    if not asset_scope_active:
        unrouted_questions=[{'question':x.get('question'),'origin':x.get('origin'),'decision_intent':x.get('decision_intent')} for x in _context_questions(questions,decision_context,category_family)]
    explicit_handoff_count=sum(1 for a in assets if a.get('handoff'))
    return {
        'status':'DYNAMIC_ASSET_ARCHITECTURE','fixed_count_authority':False,'asset_count':len(assets),'assets':assets,
        'decision_question_count':len({_norm(a.get('consumer_question')) for a in assets}),
        'source_shopper_question_count':len([q for q in questions if _norm(q)]),
        'atomic_decision_job_count':len(decision_audit),
        'decision_intent_count':len({a.get('decision_intent') for a in assets if a.get('decision_intent')}),
        'decision_question_audit':decision_audit,
        'decision_coverage_summary':{
            'status':'COVERAGE_COMPILED' if asset_scope_active else 'NO_ASSET_SURFACE_IN_CURRENT_SCOPE',
            'source_shopper_questions':len([q for q in questions if _norm(q)]),
            'atomic_decision_jobs':len(decision_audit),
            'covered_atomic_jobs':len(decision_audit)-len(uncovered),
            'uncovered_atomic_jobs':len(uncovered),
            'merged_atomic_jobs':sum(1 for x in decision_audit if x['coverage_status']=='MERGED_INTO_ASSET'),
            'principle':'Merge only when decision intent + sub-topic + surface + family match. A compound question may split into independent atomic jobs; every atomic job must remain traceable to a dedicated or explicitly merged asset.'
        },
        'asset_scope_active':asset_scope_active,
        'unrouted_questions':unrouted_questions,
        'relationship_mode':'EXPLICIT_ONLY',
        'explicit_handoff_count':explicit_handoff_count,
        'auto_sequence_authority':False,
        'category_family':category_family,
        'curation_basis':['Consumer Decision Question','Decision Intent','Decision Topic','Strategic Job','Surface Need','Incremental Information','Business Hypothesis']
    }
