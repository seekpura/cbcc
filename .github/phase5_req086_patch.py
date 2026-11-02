from pathlib import Path

path = Path('runtime/cbcc/prompt_compiler.py')
text = path.read_text(encoding='utf-8')

marker = "def _derived_photo_contract(asset: dict[str, Any], strategy_authority: dict[str, Any] | None, explicit: dict[str, Any] | None) -> dict[str, Any]:\n"
helper = '''def _asset_art_direction_photo_contract(asset: dict[str, Any]) -> dict[str, Any]:
    """Project the canonical per-asset photography authority without inventing new decisions."""
    art = asset.get('asset_art_direction') or {}
    if not isinstance(art, dict):
        return {}

    camera: dict[str, Any] = {}
    if _meaningful(art.get('camera_or_view')):
        camera['preferred_view'] = art.get('camera_or_view')
    if _meaningful(art.get('focal_length_mm')):
        camera['focal_length_mm'] = art.get('focal_length_mm')
    for nested_key in ('camera_position', 'focus_dof'):
        nested = art.get(nested_key)
        if isinstance(nested, dict):
            camera.update({k: v for k, v in nested.items() if _meaningful(v)})
    if _meaningful(camera):
        camera['authority'] = 'AGENT_ASSET_ART_DIRECTION'

    lighting = dict(art.get('lighting') or {}) if isinstance(art.get('lighting'), dict) else {}
    if _meaningful(lighting):
        lighting['authority'] = 'AGENT_ASSET_ART_DIRECTION'

    cmf = dict(art.get('cmf') or {}) if isinstance(art.get('cmf'), dict) else {}
    if _meaningful(cmf):
        cmf['authority'] = 'AGENT_ASSET_ART_DIRECTION'

    has_authority = any(_meaningful(v) for v in (camera, lighting, cmf))
    return _compact({
        'authority': 'AGENT_ASSET_ART_DIRECTION' if has_authority else None,
        'camera': camera,
        'lighting': lighting,
        'cmf': cmf,
    })


'''
if helper not in text:
    if marker not in text:
        raise SystemExit('REQ086 helper insertion marker missing')
    text = text.replace(marker, helper + marker, 1)

old = "    explicit=dict(explicit or {})\n    sections=(strategy_authority or {}).get('sections') or {}\n"
new = "    explicit=dict(explicit or {})\n    asset_direction_photo=_asset_art_direction_photo_contract(asset)\n    sections=(strategy_authority or {}).get('sections') or {}\n"
if new not in text:
    if old not in text:
        raise SystemExit('REQ086 derived contract start marker missing')
    text = text.replace(old, new, 1)

old = "    if isinstance(explicit.get('camera'),dict): camera.update(explicit.get('camera') or {})\n"
new = old + "    if isinstance(asset_direction_photo.get('camera'),dict): camera.update(asset_direction_photo.get('camera') or {})\n"
if new not in text:
    if old not in text:
        raise SystemExit('REQ086 camera merge marker missing')
    text = text.replace(old, new, 1)

old = "    if isinstance(explicit.get('lighting'),dict): lighting.update(explicit.get('lighting') or {})\n"
new = old + "    if isinstance(asset_direction_photo.get('lighting'),dict): lighting.update(asset_direction_photo.get('lighting') or {})\n"
if new not in text:
    if old not in text:
        raise SystemExit('REQ086 lighting merge marker missing')
    text = text.replace(old, new, 1)

old = "    if isinstance(cmf,dict) and cmf:\n        cmf=_merge({\n            'material':material.get('material'),'finish':material.get('finish'),'surface_behavior':material.get('surface_behavior'),\n            'optical_risks':material.get('optical_risks'),\n        },cmf)\n\n    color_management=explicit.get('color_management')\n"
new = "    if isinstance(cmf,dict) and cmf:\n        cmf=_merge({\n            'material':material.get('material'),'finish':material.get('finish'),'surface_behavior':material.get('surface_behavior'),\n            'optical_risks':material.get('optical_risks'),\n        },cmf)\n    if isinstance(asset_direction_photo.get('cmf'),dict):\n        cmf=_merge(cmf if isinstance(cmf,dict) else {}, asset_direction_photo.get('cmf') or {})\n\n    color_management=explicit.get('color_management')\n"
if new not in text:
    if old not in text:
        raise SystemExit('REQ086 CMF merge marker missing')
    text = text.replace(old, new, 1)

old = "    base={\n        'status':'ASSET_RELEVANCE_DERIVED_EXECUTION_CONTRACT',\n        'capture_mode':capture_mode,\n"
new = "    base={\n        'status':'ASSET_RELEVANCE_DERIVED_EXECUTION_CONTRACT',\n        'authority':asset_direction_photo.get('authority'),\n        'capture_mode':capture_mode,\n"
if new not in text:
    if old not in text:
        raise SystemExit('REQ086 authority marker missing')
    text = text.replace(old, new, 1)

old = "            f\"Prelight：{_txt(_cn_phrase(lm.get('prelight_plan')))}\",\n            f\"CMF：{_txt(_cn_phrase(lm.get('cmf')))}\", f\"需要表现的材质响应：{_txt(_cn_phrase(lm.get('material_response_to_show')))}\",\n"
new = "            f\"Prelight：{_txt(_cn_phrase(lm.get('prelight_plan')))}\",\n            f\"灯光执行合同：{_txt(_cn_phrase(photo_exec.get('lighting')))}\",\n            f\"CMF：{_txt(_cn_phrase(lm.get('cmf')))}\", f\"需要表现的材质响应：{_txt(_cn_phrase(lm.get('material_response_to_show')))}\",\n"
if new not in text:
    if old not in text:
        raise SystemExit('REQ086 CN lighting prompt marker missing')
    text = text.replace(old, new, 1)

old = "            f\"Prelight plan: {_txt(lm.get('prelight_plan'))}\", f\"Lighting diagram: {_txt(lm.get('lighting_diagram'))}\",\n            f\"CMF: {_txt(lm.get('cmf'))}\", f\"Material response to show: {_txt(lm.get('material_response_to_show'))}\",\n"
new = "            f\"Prelight plan: {_txt(lm.get('prelight_plan'))}\", f\"Lighting diagram: {_txt(lm.get('lighting_diagram'))}\",\n            f\"Lighting execution contract: {_txt(photo_exec.get('lighting'))}\",\n            f\"CMF: {_txt(lm.get('cmf'))}\", f\"Material response to show: {_txt(lm.get('material_response_to_show'))}\",\n"
if new not in text:
    if old not in text:
        raise SystemExit('REQ086 EN lighting prompt marker missing')
    text = text.replace(old, new, 1)

old = "    add('visual_boundaries_editability',relevance['boundaries'],'【视觉执行边界 / 可编辑性】','[VISUAL EXECUTION BOUNDARIES / EDITABILITY]')\n    focal=(card.get('composition_camera') or {}).get('focal_length_mm')\n"
new = "    add('visual_boundaries_editability',relevance['boundaries'],'【视觉执行边界 / 可编辑性】','[VISUAL EXECUTION BOUNDARIES / EDITABILITY]')\n\n    photo_exec=card.get('photography_execution') or {}\n    def add_scene_derived(name:str, value:Any):\n        if not isinstance(value,dict) or value.get('authority')!='AGENT_ASSET_ART_DIRECTION':\n            return\n        payload={k:v for k,v in value.items() if k!='authority' and _meaningful(v)}\n        def leaves(v:Any)->list[str]:\n            if isinstance(v,dict):\n                out=[]\n                for child in v.values(): out.extend(leaves(child))\n                return out\n            if isinstance(v,(list,tuple,set,frozenset)):\n                out=[]\n                for child in v: out.extend(leaves(child))\n                return out\n            return [str(v)] if _meaningful(v) else []\n        tokens=leaves(payload)\n        projected=bool(tokens) and all(token in prompt_en or token in prompt_cn for token in tokens)\n        checks.append({\n            'decision':name, 'required':True, 'projected':projected,\n            'authority':'AGENT_ASSET_ART_DIRECTION', 'value':payload,\n        })\n    add_scene_derived('scene_derived_camera',photo_exec.get('camera'))\n    add_scene_derived('scene_derived_lighting',photo_exec.get('lighting'))\n    add_scene_derived('scene_derived_cmf',photo_exec.get('cmf'))\n\n    focal=(card.get('composition_camera') or {}).get('focal_length_mm')\n"
if new not in text:
    if old not in text:
        raise SystemExit('REQ086 consumption audit marker missing')
    text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('REQ-086 patch applied')
