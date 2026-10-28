from __future__ import annotations
from typing import Any


def _present(d,key): return isinstance(d,dict) and d.get(key) not in (None,'',{},[])


def _required_dimensions(c:dict[str,Any])->set[str]:
    raw=c.get('required_dimensions') or c.get('execution_requirements') or []
    if isinstance(raw,str): raw=[raw]
    if isinstance(raw,dict): raw=[k for k,v in raw.items() if v]
    return {str(x).upper() for x in raw if str(x or '').strip()}


def validate_photography_contract(c:dict[str,Any]) -> dict[str,Any]:
    """Validate only the execution dimensions that are materially relevant to the current asset.

    This validator must not force an Agent to invent focal lengths, lighting diagrams or numeric occupancy
    targets merely to satisfy a generic photography checklist. Precision becomes mandatory only when the
    user/Agent explicitly locks that dimension, when the selected execution mode needs repeatability, or
    when product/colour fidelity requires it.
    """
    issues=[]; suggestions=[]; evaluated=[]; not_applicable=[]
    mode=str(c.get('capture_mode') or '').upper()
    if mode not in {'REAL_PHOTO','COMPOSITE','PHOTOREAL_AI','CG'}:
        issues.append({'code':'CAPTURE_MODE','field':'capture_mode','message':'Choose the execution mode that matches the current asset.'})
    required=_required_dimensions(c)
    repeatable=bool(c.get('repeatable_capture') or c.get('shoot_ready') or 'REPEATABLE_CAPTURE' in required)

    comp=c.get('composition') or {}; occ=comp.get('product_occupancy')
    occupancy_required=bool('PRODUCT_OCCUPANCY' in required or 'OCCUPANCY' in required)
    if isinstance(occ,dict) and occ:
        evaluated.append('PRODUCT_OCCUPANCY')
        for k,v in occ.items():
            if k.endswith('_pct'):
                try:
                    fv=float(v)
                    if fv<=0 or fv>100:
                        issues.append({'code':'OCCUPANCY_RANGE','field':f'composition.product_occupancy.{k}','message':'Percentage should be >0 and <=100.'})
                except Exception:
                    issues.append({'code':'OCCUPANCY_NUMERIC','field':f'composition.product_occupancy.{k}','message':'Use a numeric percentage.'})
    elif occupancy_required:
        issues.append({'code':'OCCUPANCY_PRECISION','field':'composition.product_occupancy','message':'This asset explicitly locks product occupancy; provide the relevant numeric target.'})
    else:
        not_applicable.append('PRODUCT_OCCUPANCY_LOCK')

    cam=c.get('camera') or {}
    camera_relevant=bool(cam or 'CAMERA' in required or 'PERSPECTIVE' in required or (mode=='REAL_PHOTO' and repeatable))
    if camera_relevant:
        evaluated.append('CAMERA_OR_PERSPECTIVE')
        perspective_keys=['focal_length_mm','perspective_contract','field_of_view','camera_distance','viewpoint','camera_height','pitch_deg']
        if not any(_present(cam,key) for key in perspective_keys):
            issues.append({'code':'PERSPECTIVE_CONTRACT','field':'camera','message':'Provide the perspective information that is actually needed for this shot; a semantic perspective/view contract is acceptable and a numeric focal length is not mandatory.'})
        if repeatable and not (_present(cam,'camera_height') or _present(cam,'pitch_deg') or _present(cam,'camera_distance')):
            suggestions.append({'code':'CAMERA_GEOMETRY','message':'For repeatable capture, add whichever camera geometry value materially controls the intended perspective.'})
        if mode=='REAL_PHOTO' and repeatable and not _present(cam,'focus_plane'):
            suggestions.append({'code':'FOCUS_PLANE','message':'For repeatable product/detail capture, define the decision-critical focus plane.'})
    else:
        not_applicable.append('CAMERA_PRECISION')

    light=c.get('lighting') or {}; key=light.get('key') or {}
    lighting_relevant=bool(light or 'LIGHTING' in required or (mode=='REAL_PHOTO' and repeatable))
    if lighting_relevant:
        evaluated.append('LIGHTING')
        if not isinstance(key,dict) or not any(k in key for k in ['azimuth_deg','direction','position','relationship','intent']):
            issues.append({'code':'KEY_DIRECTION','field':'lighting.key','message':'Describe the key-light relationship needed for this shot. Numeric azimuth is optional unless explicitly required.'})
        if repeatable and isinstance(key,dict) and not any(k in key for k in ['modifier','modifier_type','source_size','diffusion']):
            suggestions.append({'code':'KEY_MODIFIER','message':'For repeatable capture, define the source/modifier characteristic that materially affects the product or skin.'})
        if ('COLOR_TEMPERATURE' in required or repeatable) and not (_present(light,'cct') or _present(light,'white_balance_intent')):
            suggestions.append({'code':'CCT','message':'Add color-temperature/white-balance intent when repeatability or color matching requires it.'})
        if not _present(light,'highlight_policy') and any(x in str(c).lower() for x in ['gloss','reflect','metal','glass','skin']):
            suggestions.append({'code':'HIGHLIGHT_POLICY','message':'A highlight policy may improve truthful glossy/material/skin rendering.'})
    else:
        not_applicable.append('LIGHTING_PRECISION')

    color=c.get('color_management') or {}
    fidelity=str(c.get('product_fidelity') or '').upper()
    color_required=bool(color or 'COLOR_MANAGEMENT' in required or fidelity=='LOCKED_PIXEL' or c.get('exact_product_color') is True)
    if color_required:
        evaluated.append('COLOR_MANAGEMENT')
        if not _present(color,'output_space'):
            issues.append({'code':'OUTPUT_SPACE','field':'color_management.output_space','message':'Color management is relevant for this asset; specify the required output space.'})
        if not _present(color,'product_color_fidelity'):
            issues.append({'code':'PRODUCT_COLOR_FIDELITY','field':'color_management.product_color_fidelity','message':'Define how verified product/packaging color is preserved.'})
    else:
        not_applicable.append('COLOR_MANAGEMENT')

    human=c.get('human')
    if isinstance(human,dict) and human.get('present'):
        evaluated.append('HUMAN_EXPOSURE')
        exposure=human.get('skin_tone_exposure') or {}
        for f in ['metering_priority','highlight_protection']:
            if not _present(exposure,f):
                suggestions.append({'code':'HUMAN_EXPOSURE','message':f'Human imagery is present; add skin_tone_exposure.{f} when it materially affects truthful rendering.'})
    else:
        not_applicable.append('HUMAN_EXPOSURE')

    cmf=c.get('cmf')
    if isinstance(cmf,dict) and cmf:
        evaluated.append('CMF')
        for f in ['color','material','finish']:
            if not _present(cmf,f):
                suggestions.append({'code':'CMF_DEPTH','message':f'CMF is being used; specify {f} only if it changes capture, rendering or product truth.'})
    else:
        not_applicable.append('CMF')

    if issues:
        precision='INCOMPLETE_RELEVANT_DIMENSIONS'
    elif repeatable:
        precision='REPEATABLE_CAPTURE_READY'
    elif evaluated:
        precision='RELEVANCE_READY'
    else:
        precision='MODE_ONLY_NO_EXTRA_PRECISION_REQUIRED'
    return {
        'pass':not issues,
        'issues':issues,
        'suggestions':suggestions,
        'precision_level':precision,
        'evaluated_dimensions':evaluated,
        'not_applicable_dimensions':not_applicable,
        'required_dimensions':sorted(required),
        'principle':'Photography parameters are execution tools, not mandatory form fields. Require only dimensions that materially control this asset or preserve verified product truth.',
    }


def validate_visual_semantics(items:list[dict[str,Any]]) -> dict[str,Any]:
    allowed={'ALLOW','ALLOW_AS_ABSTRACT','CONDITIONAL','BLOCK'}; issues=[]
    for i,x in enumerate(items):
        if not x.get('element'): issues.append({'index':i,'code':'MISSING_ELEMENT'})
        if x.get('decision') not in allowed: issues.append({'index':i,'code':'INVALID_DECISION'})
        if x.get('decision') in {'ALLOW','ALLOW_AS_ABSTRACT','CONDITIONAL'} and not x.get('strategic_relevance'): issues.append({'index':i,'code':'MISSING_RELEVANCE'})
    return {'pass':not issues,'issues':issues,'policy':'Elements are selected for strategic meaning; BLOCK is reserved for evidence/claim/culture/platform conflicts.'}
