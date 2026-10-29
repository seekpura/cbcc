from __future__ import annotations
from typing import Any


def _first(product:dict[str,Any], *keys):
    for k in keys:
        if product.get(k) not in (None,'',[],{}): return product.get(k)
    return None


def compile_product_visual_intelligence(product:dict[str,Any], source_product_assets:list[dict[str,Any]]|None, foundation_roles:list[str]|None, photography:dict[str,Any]|None=None, cmf:dict[str,Any]|None=None)->dict[str,Any]:
    """Compile product appearance/capture facts without inventing missing visual properties."""
    source_product_assets=source_product_assets or []; photography=photography or {}; cmf=cmf or {}
    known_views=[x.get('role') for x in source_product_assets if x.get('role')]
    material=_first(product,'material','materials') or cmf.get('material')
    finish=_first(product,'finish','surface_finish') or cmf.get('finish')
    geometry=_first(product,'geometry','shape','form_factor','dimensions')
    structure=_first(product,'structure','parts','components','closure','package_structure')
    transparency=_first(product,'transparency','opacity','transparent','translucent')
    reflective=_first(product,'reflective','reflection','gloss','gloss_level')
    label=_first(product,'label','label_copy','packaging_copy','front_label','printed_text')
    risks=[]
    if transparency not in (None,False,'opaque','OPAQUE'): risks.append('TRANSPARENCY_EDGE_BACKGROUND_INTERACTION')
    if reflective not in (None,False,'matte','MATTE'): risks.append('SPECULAR_REFLECTION_CAN_HIDE_PRINT_OR_SHAPE')
    if label: risks.append('LABEL_LEGIBILITY_AND_PRINT_FIDELITY')
    if material: risks.append('MATERIAL_RESPONSE_MUST_MATCH_REAL_PRODUCT')
    missing=[]
    for name,val in [('geometry',geometry),('material',material),('finish',finish),('label_or_pack_copy',label)]:
        if val in (None,'',[],{}): missing.append(name)
    roles=list(foundation_roles or [])
    return {
        'status':'SOURCE_BOUND' if source_product_assets else 'PLANNING_ONLY_SOURCE_MASTER_REQUIRED',
        'product_name':product.get('name') or product.get('product_name'),
        'appearance_facts':{'geometry':geometry,'structure':structure,'material':material,'finish':finish,'transparency':transparency,'reflective_behavior':reflective,'label_or_pack_copy':label},
        'source_master_views':known_views,'source_product_assets':source_product_assets,
        'foundation_roles':roles,
        'identity_faces':product.get('identity_faces') or product.get('key_views') or ['FRONT_OR_PRIMARY_LABEL_FACE'],
        'capture_risks':risks,
        'missing_visual_facts':missing,
        'canonical_view_needs':{
            'identity':'Front/primary readable face or truthful 3Q view.',
            'structure':'Side/back/open/detail only when the purchase decision requires it.',
            'material':'Macro/detail only when texture/finish/contents is decision-relevant and source-bound.',
            'scale':'Use dimension/on-body/context reference only when it changes purchase understanding.'
        },
        'render_permissions':{'REFERENCE_GUIDED_NATIVE_LOCK':'Use supplied real-product images as strong model reference inputs and natively render the same product identity in the final image; preserve package geometry/proportions/logo/brand wording/label layout/recognizable print/colors/material identity.','EXACT_PIXEL_COMPOSITE':'Explicit-only route: exact source pixels remain immutable and are composited as a source layer.','REFERENCE_CONSTRAINED':'Reconstruction must preserve verified identity; unknown pack details remain unknown.'},
        'principle':'Foundation assets define who the product is. Downstream creative may change environment, evidence hierarchy and composition, but must not re-invent product identity.'
    }


def compile_creative_anchor_plan(council:dict[str,Any], architecture:dict[str,Any], product_visual_intelligence:dict[str,Any], cmf:dict[str,Any]|None=None)->dict[str,Any]:
    selected=(council or {}).get('selected_direction') or {}; assets=architecture.get('assets') or []; cmf=cmf or {}
    roles=[]
    if any(str(a.get('decision_intent')).upper()=='IDENTIFY' for a in assets): roles.append('HERO_KEYFRAME_MASTER')
    if any(a.get('asset_type')=='IMAGE' for a in assets): roles.append('LIGHTING_REFERENCE_MASTER')
    if any(str(a.get('decision_intent')).upper() in {'MATERIAL_SENSORY','PROOF','PERFORMANCE_PROOF'} for a in assets) or cmf: roles.append('MATERIAL_RESPONSE_MASTER')
    if any(str(a.get('decision_intent')).upper() in {'RELEVANCE','USAGE','FIT_WEAR','PORTABILITY'} for a in assets): roles.append('SCENE_LANGUAGE_MASTER')
    rows=[]
    for role in roles:
        rows.append({'anchor_role':role,'status':'PLAN_LOCKED','direction_id':selected.get('direction_id'),'direction_route':selected.get('route'),'source_foundation_roles':product_visual_intelligence.get('foundation_roles') or [],'production_rule':'Produce and review this anchor once when the role is required; downstream assets reference the locked anchor rather than inventing a new visual system.','artifact_id':None,'lock_hash':None})
    return {'status':'CREATIVE_ANCHOR_PLAN_COMPILED','dynamic':True,'roles':rows,'direction_id':selected.get('direction_id'),'principle':'Foundation preserves product identity; Creative Anchors preserve the selected visual system. Neither forces all assets into the same composition.'}
