from __future__ import annotations
from typing import Any
from .models import stable_hash

PROOF_INTENTS={'PROOF','PERFORMANCE_PROOF','DIFFERENTIATION','INGREDIENT_COMPOSITION','INGREDIENT_DIETARY','COMPATIBILITY','SEAL_LEAK','WARRANTY_SERVICE','TOTAL_COST_OWNERSHIP'}
HUMAN_INTENTS={'RELEVANCE','USAGE','FIT_WEAR','PORTABILITY','SENSORY_PREP'}
MATERIAL_INTENTS={'MATERIAL_SENSORY','WEATHER_BOUNDARY'}
SCALE_INTENTS={'SIZE_CAPACITY','SIZE_FIT','SITE_FIT','PORTABILITY','STORAGE_STACKING'}
PROCESS_INTENTS={'USAGE','SENSORY_PREP','CARE_MAINTENANCE','DELIVERY_INSTALLATION','STORAGE_STACKING'}
RISK_INTENTS={'WEATHER_BOUNDARY','WARRANTY_SERVICE','DELIVERY_INSTALLATION','EXPECTATION_BOUNDARY','COMPATIBILITY','SIZE_FIT','SITE_FIT'}
SYSTEM_INTENTS={'COMPATIBILITY','STORAGE_STACKING','PACKAGE_CONTENTS','SEAL_LEAK','SIZE_CAPACITY'}


def _product(product_truth:dict[str,Any])->dict[str,Any]:
    return (product_truth or {}).get('product') or product_truth or {}


def _appearance_text(pvi:dict[str,Any]|None)->str:
    pvi=pvi or {}
    vals=[]
    for key in ('appearance_facts','capture_risks','identity_faces','canonical_view_needs','known_materials'):
        v=pvi.get(key)
        if v not in (None,'',[],{}): vals.append(str(v))
    return ' '.join(vals).casefold()


def _candidate(mid:str,name:str,domain:str,intents:set[str],visual:str,composition:str,product_role:str,proof_mode:str,surfaces:list[str],why:str)->dict[str,Any]:
    return {
        'mechanism_id':mid,'mechanism_name':name,'domain':domain,'decision_intents':sorted(intents),
        'visual_mechanism':visual,'composition_camera_mechanism':composition,'product_role':product_role,
        'proof_mode':proof_mode,'surface_affinity':surfaces,'why':why,
    }


def compile_creative_opportunity_universe(
    product_truth:dict[str,Any], product_visual_intelligence:dict[str,Any]|None,
    category_family:str|None, assets:list[dict[str,Any]]|None,
    curation:dict[str,Any]|None=None, culture:dict[str,Any]|None=None,
    target:dict[str,Any]|None=None,
)->dict[str,Any]:
    """Build a search-before-selection universe of visual mechanisms, not a style library."""
    product=_product(product_truth); pvi=product_visual_intelligence or {}; curation=curation or {}; target=target or {}
    intents=[str(a.get('decision_intent') or 'DECISION_SUPPORT').upper() for a in (assets or [])]
    intent_set=set(intents); appearance=_appearance_text(pvi)
    has_material=any(x in appearance for x in ('material','glass','plastic','metal','fabric','nylon','finish','texture','transparent','reflect','gloss','matte','织','玻璃','塑料','金属','透明','反光')) or bool(intent_set&MATERIAL_INTENTS)
    flags={
        'human':bool(intent_set&HUMAN_INTENTS),'scale':bool(intent_set&SCALE_INTENTS),'process':bool(intent_set&PROCESS_INTENTS),
        'risk':bool(intent_set&RISK_INTENTS),'system':bool(intent_set&SYSTEM_INTENTS),'proof':bool(intent_set&PROOF_INTENTS),
        'contents':'PACKAGE_CONTENTS' in intent_set,
    }
    whitespace=curation.get('white_space') or []; cliches=curation.get('category_cliches') or []
    all_intents=set(intent_set) or {'DECISION_SUPPORT'}
    candidates=[
        _candidate('OPP-IDENTITY-GEOMETRY','Product Identity Geometry','PRODUCT_STRUCTURE',{'IDENTIFY','DIFFERENTIATION'},
            'Use silhouette, key face, label readability and authentic proportions as the first information carrier.',
            'Choose front/3Q/orthographic view from the identity face; negative space supports one proposition instead of a repeated centered packshot.',
            'Primary factual anchor','Real pack/label/geometry',['SEARCH_RESULTS','LISTING_PRIMARY','PDP_HERO','GALLERY'],
            'Recognition must come from the real object before stylistic abstraction.'),
        _candidate('OPP-INFORMATION-EDITORIAL','Information Hierarchy as Visual Form','INFORMATION_DESIGN',all_intents,
            'Turn message hierarchy, evidence plane and copy budget into spatial hierarchy before typography is overlaid.',
            'Asymmetric editorial field, modular evidence labels and deliberate text-safe negative space; hierarchy changes with the decision job.',
            'Hero, signature or absent according to Product Presence','Copy labels only visible/source-bound evidence',['GALLERY','PDP','LONGFORM','A_PLUS','COMPARISON','SPECIFICATION'],
            'Information design is a visual mechanism, not a decoration pass.'),
        _candidate('OPP-EVIDENCE-RELATIONSHIP','Evidence Relationship / Causal Proof','EVIDENCE_SYSTEM',PROOF_INTENTS,
            'Make a verified mechanism, specification, ingredient/composition fact, compatibility relation or test condition spatially attributable to the product.',
            'Use macro, sectional, relationship, measurement or cause→effect grammar chosen from the evidence type; avoid generic lab theatre.',
            'Evidence carrier; full pack optional when proof needs detail','Verified fact → visible evidence → buyer consequence',['GALLERY','PDP','LONGFORM','COMPARISON','SPECIFICATION','PDP_VIDEO'],
            'Proof should be visible as a relationship, not a badge.'),
        _candidate('OPP-HUMAN-DECISIVE-MOMENT','Human Use Decisive Moment','HUMAN_CONTEXT',HUMAN_INTENTS,
            'Use the exact hand/body/routine/handling moment that resolves scale, fit, use or relevance.',
            'Action-led crop, believable perspective and contact point; no generic model-plus-product posing.',
            'Active tool/object inside the action','Visible action / fit / handling relationship',['CREATOR','SHORT_VIDEO','PDP_VIDEO','GALLERY','SOCIAL_CONTENT'],
            'Human presence must carry decision information.'),
        _candidate('OPP-MATERIAL-OPTICS','Material / Optical Behavior','MATERIAL_CMF',MATERIAL_INTENTS|{'PROOF'},
            'Use real reflectivity, translucency, weave, texture, edge behavior and finish response as purchase evidence.',
            'Raking/broad-source/macro/negative-fill/polarization choices follow material behavior; background is selected for optical separation.',
            'Material specimen or product detail','Real material response; never fake gloss/texture',['GALLERY','PDP_HERO','LONGFORM','A_PLUS'],
            'CMF is both design language and capture engineering input.'),
        _candidate('OPP-SCALE-SPACE','Scale / Space Calibration','SPATIAL_RELATION',SCALE_INTENTS,
            'Translate dimensions, capacity or fit into a measured relationship with body, room, storage or a familiar scale.',
            'Orthographic, top-down, on-body or environmental clearance view using truthful scale references only.',
            'Measured object inside a real spatial system','Verified dimensions/capacity/fit',['GALLERY','PDP','SPECIFICATION','PDP_VIDEO','CREATOR'],
            'Numbers become useful when shoppers can map them to their own space/body/task.'),
        _candidate('OPP-PROCESS-SEQUENCE','Process / Sequence','BEHAVIOR_FLOW',PROCESS_INTENTS,
            'Expose the minimum sequence needed to use, prepare, care for, install or reset correctly.',
            'One decisive action per frame/beat; sequence length follows task complexity rather than a fixed three-step card.',
            'Object in transformation/use','Source-bound action and boundary',['PDP_VIDEO','SHORT_VIDEO','CREATOR','FAQ','POST_PURCHASE','LONGFORM'],
            'Operation uncertainty is solved by a visible sequence.'),
        _candidate('OPP-RISK-BOUNDARY','Risk / Boundary Visualization','RISK_REDUCTION',RISK_INTENTS,
            'Show condition → supported capability → explicit limit so the buyer forms an accurate expectation.',
            'Condition-state relation, supported-use diagram, service path or boundary annotation; never dramatize an unverified failure.',
            'Product/evidence as risk-reduction anchor','Verified limit / policy / compatibility boundary',['FAQ','PDP','GALLERY','LONGFORM','POST_PURCHASE'],
            'Trust often comes from showing where a claim stops.'),
        _candidate('OPP-SYSTEM-RELATIONSHIP','System / Compatibility Relationship','SYSTEM_MAP',SYSTEM_INTENTS,
            'Show how the product relates to compatible components, contained items, stack/nest systems or closure states.',
            'Relationship diagram, truthful exploded/inventory view or state relationship without outcome exaggeration.',
            'Node inside a real system','Compatibility / components / structural relation',['GALLERY','PDP','COMPARISON','SPECIFICATION','PDP_VIDEO'],
            'Many decisions concern the system around the object, not the isolated object.'),
        _candidate('OPP-CONTENTS-REVEAL','Package / Contents Reveal','OBJECT_INVENTORY',{'PACKAGE_CONTENTS'},
            'Turn “what exactly do I receive?” into an unambiguous inventory/open-package relationship.',
            'Top-down, open package or exploded-but-truthful inventory; quantity/components remain source-bound.',
            'Container plus verified included components','Package truth',['GALLERY','PDP','SPECIFICATION'],
            'Inventory clarity reduces fulfillment expectation errors.'),
        _candidate('OPP-CATEGORY-CONVENTION-BREAK','Category Convention Reframing','CATEGORY_WHITESPACE',all_intents,
            'Keep the category decision job but replace overused visual shorthand with a mechanism borrowed from an adjacent domain.',
            'Use editorial, exhibition, craft, architecture or information-design logic without copying a finished reference composition.',
            'Depends on the chosen mechanism','Product Truth stays the anchor',['GALLERY','PDP_HERO','PAID_AD','SOCIAL_CONTENT','STORE_BANNER'],
            'Differentiation should come from a different mechanism, not only a new color.'),
        _candidate('OPP-REMOTE-DOMAIN-SPATIAL','Remote-domain Spatial Grammar','REMOTE_DOMAIN',all_intents,
            'Borrow sequence, reveal, rhythm and framing from exhibition/architecture/editorial systems without borrowing branded artwork.',
            'Object-as-exhibit, threshold/reveal, modular grid, material field or spatial rhythm selected only when it serves the decision.',
            'Varies by decision','External reference never becomes product evidence',['PDP_HERO','GALLERY','LONGFORM','PAID_AD','STORE_BANNER'],
            'Remote-domain search expands possibility while keeping Product Truth intact.'),
    ]
    category_prior={
        'BEAUTY_PERSONAL_CARE':{'OPP-EVIDENCE-RELATIONSHIP','OPP-MATERIAL-OPTICS','OPP-HUMAN-DECISIVE-MOMENT'},
        'APPAREL_FIT':{'OPP-HUMAN-DECISIVE-MOMENT','OPP-SCALE-SPACE','OPP-MATERIAL-OPTICS'},
        'FASHION_ACCESSORY':{'OPP-HUMAN-DECISIVE-MOMENT','OPP-SCALE-SPACE','OPP-MATERIAL-OPTICS'},
        'HOME_DURABLE':{'OPP-SCALE-SPACE','OPP-SYSTEM-RELATIONSHIP','OPP-PROCESS-SEQUENCE','OPP-MATERIAL-OPTICS'},
        'HIGH_TICKET_DURABLE':{'OPP-SCALE-SPACE','OPP-EVIDENCE-RELATIONSHIP','OPP-RISK-BOUNDARY','OPP-PROCESS-SEQUENCE'},
        'ELECTRONICS':{'OPP-EVIDENCE-RELATIONSHIP','OPP-SYSTEM-RELATIONSHIP','OPP-RISK-BOUNDARY'},
        'FOOD_BEVERAGE':{'OPP-PROCESS-SEQUENCE','OPP-MATERIAL-OPTICS','OPP-EVIDENCE-RELATIONSHIP'},
    }.get(str(category_family or '').upper(),set())
    activated=[]
    for row in candidates:
        rel=set(row['decision_intents']); hits=sorted(intent_set&rel); score=0.48
        if row['mechanism_id'] in {'OPP-IDENTITY-GEOMETRY','OPP-INFORMATION-EDITORIAL'}: score+=0.16
        if hits: score+=min(0.30,0.09*len(hits))
        if row['mechanism_id'] in category_prior: score+=0.10
        if row['mechanism_id']=='OPP-MATERIAL-OPTICS' and has_material: score+=0.16
        if row['mechanism_id']=='OPP-HUMAN-DECISIVE-MOMENT' and flags['human']: score+=0.14
        if row['mechanism_id']=='OPP-SCALE-SPACE' and flags['scale']: score+=0.14
        if row['mechanism_id']=='OPP-PROCESS-SEQUENCE' and flags['process']: score+=0.14
        if row['mechanism_id']=='OPP-RISK-BOUNDARY' and flags['risk']: score+=0.14
        if row['mechanism_id']=='OPP-SYSTEM-RELATIONSHIP' and flags['system']: score+=0.14
        if row['mechanism_id']=='OPP-EVIDENCE-RELATIONSHIP' and flags['proof']: score+=0.14
        if row['mechanism_id']=='OPP-CONTENTS-REVEAL' and flags['contents']: score+=0.22
        if row['mechanism_id']=='OPP-CATEGORY-CONVENTION-BREAK' and (whitespace or cliches): score+=0.14
        if row['mechanism_id']=='OPP-REMOTE-DOMAIN-SPATIAL': score+=0.06
        r=dict(row); r['opportunity_id']='COP-'+stable_hash([product.get('name'),category_family,row['mechanism_id'],hits])[:10].upper()
        r['direction_role']={
            'OPP-INFORMATION-EDITORIAL':'SUPPORTING_SYSTEM',
            'OPP-CATEGORY-CONVENTION-BREAK':'DIFFERENTIATION_MODULATOR',
            'OPP-REMOTE-DOMAIN-SPATIAL':'SPATIAL_MODULATOR',
            'OPP-IDENTITY-GEOMETRY':'IDENTITY_ANCHOR',
        }.get(row['mechanism_id'],'PRIMARY_MECHANISM')
        r['score']=round(min(score,0.99),3)
        r['activation_signals']={'matched_decision_intents':hits,'category_prior':row['mechanism_id'] in category_prior,'material_signal':has_material if row['mechanism_id']=='OPP-MATERIAL-OPTICS' else None,'reference_whitespace':len(whitespace) if row['mechanism_id']=='OPP-CATEGORY-CONVENTION-BREAK' else None}
        activated.append(r)
    activated.sort(key=lambda x:(x['score'],x['mechanism_id']),reverse=True)
    selected=activated[:12]  # bounded 6–12 search universe; current library exposes 12 mechanisms.
    return {
        'status':'CREATIVE_OPPORTUNITY_UNIVERSE_COMPILED','product_name':product.get('name'),'category_family':category_family,
        'observed_decision_intents':intents,'opportunity_count':len(selected),'opportunities':selected,
        'reference_whitespace_signals':whitespace[:5],'category_cliche_signals':cliches[:5],
        'search_domains':['PRODUCT_STRUCTURE','EVIDENCE_SYSTEM','HUMAN_CONTEXT','MATERIAL_CMF','SPATIAL_RELATION','BEHAVIOR_FLOW','RISK_REDUCTION','SYSTEM_MAP','INFORMATION_DESIGN','CATEGORY_WHITESPACE','REMOTE_DOMAIN'],
        'selection_rule':'Explore mechanisms first; cluster into materially different directions only after product/decision/surface fit is visible. Opportunities are mechanisms, not finished styles.',
        'target_context':{'market':target.get('market'),'platform_family':target.get('platform_family'),'site':target.get('site'),'category':target.get('category')},
        'culture_boundary':'Culture/identity may change casting, language and scene when supported by evidence; never use identity as a stereotype-based style shortcut.',
    }
