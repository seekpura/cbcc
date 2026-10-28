from __future__ import annotations
from typing import Any


def _present(d,key): return isinstance(d,dict) and d.get(key) not in (None,'',{},[])

def validate_photography_contract(c:dict[str,Any]) -> dict[str,Any]:
    issues=[]; suggestions=[]
    mode=c.get('capture_mode')
    if mode not in {'REAL_PHOTO','COMPOSITE','PHOTOREAL_AI','CG'}: issues.append({'code':'CAPTURE_MODE','field':'capture_mode','message':'Choose an execution mode.'})
    comp=c.get('composition') or {}; occ=comp.get('product_occupancy')
    if not isinstance(occ,dict) or not any(k in occ for k in ['height_pct','width_pct','group_width_pct']): issues.append({'code':'OCCUPANCY_PRECISION','field':'composition.product_occupancy','message':'Provide at least one numeric occupancy target such as height_pct.'})
    else:
        for k,v in occ.items():
            if k.endswith('_pct'):
                try:
                    fv=float(v)
                    if fv<=0 or fv>100: issues.append({'code':'OCCUPANCY_RANGE','field':f'composition.product_occupancy.{k}','message':'Percentage should be >0 and <=100.'})
                except Exception: issues.append({'code':'OCCUPANCY_NUMERIC','field':f'composition.product_occupancy.{k}','message':'Use a numeric percentage.'})
    cam=c.get('camera') or {}
    if mode in {'REAL_PHOTO','COMPOSITE','PHOTOREAL_AI'}:
        if not _present(cam,'focal_length_mm'): issues.append({'code':'FOCAL_LENGTH','field':'camera.focal_length_mm','message':'Specify focal length or an explicit perspective contract.'})
        if not (_present(cam,'camera_height') or _present(cam,'pitch_deg')): suggestions.append({'code':'CAMERA_GEOMETRY','message':'Camera height or pitch improves repeatability.'})
        if not _present(cam,'focus_plane'): suggestions.append({'code':'FOCUS_PLANE','message':'Define the focus plane for product/detail shots.'})
    light=c.get('lighting') or {}; key=light.get('key') or {}
    if not isinstance(key,dict) or not any(k in key for k in ['azimuth_deg','direction','position']): issues.append({'code':'KEY_DIRECTION','field':'lighting.key','message':'Define key-light direction/position.'})
    if isinstance(key,dict) and not any(k in key for k in ['modifier','modifier_type']): issues.append({'code':'KEY_MODIFIER','field':'lighting.key','message':'Define modifier type for a shoot-ready lighting contract.'})
    if not _present(light,'cct'): issues.append({'code':'CCT','field':'lighting.cct','message':'Specify color-temperature / white-balance intent.'})
    if not _present(light,'highlight_policy'): suggestions.append({'code':'HIGHLIGHT_POLICY','message':'Define highlight roll-off/clipping priority, especially for glossy packaging or skin.'})
    color=c.get('color_management') or {}
    if not _present(color,'output_space'): issues.append({'code':'OUTPUT_SPACE','field':'color_management.output_space','message':'Specify output color space.'})
    if not _present(color,'product_color_fidelity'): issues.append({'code':'PRODUCT_COLOR_FIDELITY','field':'color_management.product_color_fidelity','message':'Define how product/packaging color truth is preserved.'})
    human=c.get('human')
    if isinstance(human,dict) and human.get('present'):
        exposure=human.get('skin_tone_exposure') or {}
        for f in ['metering_priority','highlight_protection']:
            if not _present(exposure,f): suggestions.append({'code':'HUMAN_EXPOSURE','message':f'For human photography, add skin_tone_exposure.{f}.'})
    cmf=c.get('cmf')
    if isinstance(cmf,dict) and cmf:
        for f in ['color','material','finish']:
            if not _present(cmf,f): suggestions.append({'code':'CMF_DEPTH','message':f'CMF is present; specify {f} for execution clarity.'})
    return {'pass':not issues,'issues':issues,'suggestions':suggestions,'precision_level':'SHOOT_READY_MINIMUM' if not issues else 'INCOMPLETE'}


def validate_visual_semantics(items:list[dict[str,Any]]) -> dict[str,Any]:
    allowed={'ALLOW','ALLOW_AS_ABSTRACT','CONDITIONAL','BLOCK'}; issues=[]
    for i,x in enumerate(items):
        if not x.get('element'): issues.append({'index':i,'code':'MISSING_ELEMENT'})
        if x.get('decision') not in allowed: issues.append({'index':i,'code':'INVALID_DECISION'})
        if x.get('decision') in {'ALLOW','ALLOW_AS_ABSTRACT','CONDITIONAL'} and not x.get('strategic_relevance'): issues.append({'index':i,'code':'MISSING_RELEVANCE'})
    return {'pass':not issues,'issues':issues,'policy':'Elements are selected for strategic meaning; BLOCK is reserved for evidence/claim/culture/platform conflicts.'}
