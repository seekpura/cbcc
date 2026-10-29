#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'runtime/cbcc/production_parameter_closure.py'
s=p.read_text(encoding='utf-8')

anchor="""def _blob(v: Any) -> str:\n    try:\n        return json.dumps(v, ensure_ascii=False).casefold()\n    except Exception:\n        return str(v).casefold()\n\n\n"""
insert=anchor+"""def _lang_value(v: Any, language: str) -> Any:\n    \"\"\"Project a bilingual authored value into one prompt language without losing neutral structure.\"\"\"\n    if not _meaningful(v):\n        return None\n    if isinstance(v, Mapping):\n        keys=('en','EN','en-US','en-GB') if language=='EN' else ('cn','CN','zh','zh-CN')\n        for key in keys:\n            if _meaningful(v.get(key)):\n                return v.get(key)\n        # A mapping without language keys is an execution structure (angles, ratios, geometry, etc.).\n        return {k:_lang_value(x,language) for k,x in v.items() if _meaningful(_lang_value(x,language))}\n    if isinstance(v, (list, tuple, set, frozenset)):\n        rows=[_lang_value(x,language) for x in v]\n        return [x for x in rows if _meaningful(x)]\n    text=str(v).strip()\n    if language=='EN' and _CJK_RE.search(text):\n        return None\n    return v\n\n\ndef _lang_txt(v: Any, language: str) -> str:\n    return _txt(_lang_value(v,language))\n\n\n"""
if 'def _lang_value(' not in s:
    if anchor not in s: raise SystemExit('missing blob anchor')
    s=s.replace(anchor,insert,1)

s=s.replace("raw=_txt(value)\n        if not raw:","raw=_lang_txt(value,language)\n        if not raw:",1)
# Now EN is already language-projected; this guard remains harmless, but remove it to avoid skipping neutral nested values.
s=s.replace("        if language=='EN' and _CJK_RE.search(raw):\n            continue\n",'',1)

old="""    occ=_txt(params.get('product_occupancy') or presence.get('scale_relationship'))\n    geom=_txt(params.get('layout_geometry') or params.get('composition_grammar'))\n    depth=_txt(params.get('scale_depth'))\n    camera='; '.join(_txt(params.get(k)) for k in ('focal_length','working_distance','camera_height','yaw_pitch_roll') if _meaningful(params.get(k)))\n    light='; '.join(_txt(params.get(k)) for k in ('key_light','fill_light','negative_fill','cct','light_ratio','shadow_policy','highlight_policy','reflection_control') if _meaningful(params.get(k)))\n    values=' '.join(x for x in (occ,geom,depth,camera,light) if x)\n    if language=='EN' and _CJK_RE.search(values):\n        return ''\n"""
new="""    occ=_lang_txt(params.get('product_occupancy') or presence.get('scale_relationship'),language)\n    geom=_lang_txt(params.get('layout_geometry') or params.get('composition_grammar'),language)\n    depth=_lang_txt(params.get('scale_depth'),language)\n    camera='; '.join(_lang_txt(params.get(k),language) for k in ('focal_length','working_distance','camera_height','yaw_pitch_roll') if _meaningful(_lang_txt(params.get(k),language)))\n    light='; '.join(_lang_txt(params.get(k),language) for k in ('key_light','fill_light','negative_fill','cct','light_ratio','shadow_policy','highlight_policy','reflection_control') if _meaningful(_lang_txt(params.get(k),language)))\n"""
if old not in s: raise SystemExit('missing composite language block')
s=s.replace(old,new,1)

old="""    selected={k:v for k,v in params.items() if not k.startswith('_')}\n    missing_bilingual=[k for k,v in selected.items() if _CJK_RE.search(_txt(v)) and _txt(v) not in en]\n"""
new="""    selected={k:v for k,v in params.items() if not k.startswith('_')}\n    missing_bilingual=[]\n    for k,v in selected.items():\n        raw=_txt(v)\n        en_value=_lang_txt(v,'EN')\n        # Only genuinely Chinese-only authored semantics are missing. A {cn,en} mapping is complete.\n        if _CJK_RE.search(raw) and not en_value:\n            missing_bilingual.append(k)\n"""
if old not in s: raise SystemExit('missing bilingual audit block')
s=s.replace(old,new,1)

old="""    if closure['model_generation_blocking']:\n        out['model_prompt_status']='ART_DIRECTION_EXECUTION_DEPTH_REQUIRED'\n    else:\n        out['model_prompt_status']='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'\n"""
new="""    prior_status=str(out.get('model_prompt_status') or '')\n    specific_prior={'BILINGUAL_RENDER_SEMANTICS_REQUIRED','COPY_RENDER_MODE_REQUIRED','AGENT_ART_DIRECTION_REQUIRED'}\n    if prior_status in specific_prior:\n        # Preserve the more precise upstream readiness reason; closure details remain visible alongside it.\n        out['model_prompt_status']=prior_status\n    elif closure['model_generation_blocking']:\n        out['model_prompt_status']='ART_DIRECTION_EXECUTION_DEPTH_REQUIRED'\n    else:\n        out['model_prompt_status']='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'\n"""
if old not in s: raise SystemExit('missing status block')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('patched bilingual closure + status priority')
