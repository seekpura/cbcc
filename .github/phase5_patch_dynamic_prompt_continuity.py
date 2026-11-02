from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'{label}: expected source shape not found')
    return text.replace(old, new, 1)


# 1) Canonical Phase 4 dynamic Art Direction -> model-facing fields.
path = Path('runtime/cbcc/model_native_prompt_contract.py')
text = path.read_text(encoding='utf-8')

old = """def _art(asset: Mapping[str, Any]) -> dict[str, Any]:\n    value=asset.get('asset_art_direction')\n    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}\n\n\n"""
new = """def _art(asset: Mapping[str, Any]) -> dict[str, Any]:\n    value=asset.get('asset_art_direction')\n    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}\n\n\n_DYNAMIC_NON_ACTING_KEYS = {'authority', 'authored_fields', 'video_id', 'family', 'surface'}\n\n\ndef _dynamic_model_value(value: Any) -> Any:\n    \"\"\"Keep frame/audio-changing dynamic decisions while stripping provenance/orchestration metadata.\"\"\"\n    if not _meaningful(value):\n        return None\n    if isinstance(value, Mapping):\n        out={}\n        for key, child in value.items():\n            if str(key) in _DYNAMIC_NON_ACTING_KEYS:\n                continue\n            if str(key) == 'narrative_carrier' and isinstance(child, str):\n                child = child.replace('_', ' ').strip().lower()\n            resolved=_dynamic_model_value(child)\n            if _meaningful(resolved):\n                out[key]=resolved\n        return out or None\n    if isinstance(value, (list, tuple)):\n        out=[_dynamic_model_value(x) for x in value]\n        return [x for x in out if _meaningful(x)] or None\n    return value\n\n\n"""
text = replace_once(text, old, new, 'dynamic helper')

old = """        'inclusive_human': L(_first(art, 'inclusive_human', 'representation') or inc, 'inclusive_human'),\n        'motion_timing': L(_first(art, 'motion_timing', 'timing', 'duration', 'shot_timing'), 'motion_timing'),\n        'shot_sequence': L(_first(art, 'shot_sequence', 'shot_plan', 'storyboard'), 'shot_sequence'),\n        'camera_motion': L(_first(art, 'camera_motion', 'motion_program'), 'camera_motion'),\n        'transition_audio': L(_first(art, 'transition_audio', 'transitions', 'audio_direction'), 'transition_audio'),\n        'post_look': L(_first(art, 'post_look', 'grade', 'finishing_look'), 'post_look'),\n"""
new = """        'inclusive_human': L(_first(art, 'inclusive_human', 'representation') or inc, 'inclusive_human'),\n        # Phase 4 canonical dynamic authority. These are the same per-object motion/timing/audio\n        # decisions projected from video_creator; provenance fields are intentionally excluded.\n        'motion': L(_dynamic_model_value(art.get('motion')), 'motion'),\n        'timing': L(_dynamic_model_value(art.get('timing')), 'timing'),\n        'audio': L(_dynamic_model_value(art.get('audio')), 'audio'),\n        # Backward-compatible legacy dynamic fields remain consumable when canonical fields are absent.\n        'motion_timing': L(_first(art, 'motion_timing', 'duration', 'shot_timing'), 'motion_timing'),\n        'shot_sequence': L(_first(art, 'shot_sequence', 'shot_plan', 'storyboard'), 'shot_sequence'),\n        'camera_motion': L(_first(art, 'camera_motion', 'motion_program'), 'camera_motion'),\n        'transition_audio': L(_first(art, 'transition_audio', 'transitions', 'audio_direction'), 'transition_audio'),\n        'post_look': L(_first(art, 'post_look', 'grade', 'finishing_look'), 'post_look'),\n"""
text = replace_once(text, old, new, 'canonical dynamic model fields')

old_cn = """        if is_video:\n            video=[]\n            for k,label in [('motion_timing','时长/节奏'),('shot_sequence','镜头顺序'),('camera_motion','镜头运动'),('transition_audio','转场/音频')]:\n                if f.get(k): video.append(f\"{label}：{_txt(f[k])}\")\n            if video: rows.append('动态执行：'+'；'.join(video)+'。')\n"""
new_cn = """        if is_video:\n            video=[]\n            if f.get('motion'):\n                video.append(f\"动作/镜头程序：{_txt(f['motion'])}\")\n            else:\n                for k,label in [('shot_sequence','镜头顺序'),('camera_motion','镜头运动')]:\n                    if f.get(k): video.append(f\"{label}：{_txt(f[k])}\")\n            if f.get('timing'):\n                video.append(f\"时长/节奏：{_txt(f['timing'])}\")\n            elif f.get('motion_timing'):\n                video.append(f\"时长/节奏：{_txt(f['motion_timing'])}\")\n            if f.get('audio'):\n                video.append(f\"音频/配音：{_txt(f['audio'])}\")\n            elif f.get('transition_audio'):\n                video.append(f\"转场/音频：{_txt(f['transition_audio'])}\")\n            if video: rows.append('动态执行：'+'；'.join(video)+'。')\n"""
text = replace_once(text, old_cn, new_cn, 'CN dynamic render')

old_en = """    if is_video:\n        video=[]\n        for k,label in [('motion_timing','duration/rhythm'),('shot_sequence','shot sequence'),('camera_motion','camera motion'),('transition_audio','transitions/audio')]:\n            if f.get(k): video.append(f\"{label}: {_txt(f[k])}\")\n        if video: rows.append('Motion execution — '+'; '.join(video)+'.')\n"""
new_en = """    if is_video:\n        video=[]\n        if f.get('motion'):\n            video.append(f\"motion/shot program: {_txt(f['motion'])}\")\n        else:\n            for k,label in [('shot_sequence','shot sequence'),('camera_motion','camera motion')]:\n                if f.get(k): video.append(f\"{label}: {_txt(f[k])}\")\n        if f.get('timing'):\n            video.append(f\"duration/rhythm: {_txt(f['timing'])}\")\n        elif f.get('motion_timing'):\n            video.append(f\"duration/rhythm: {_txt(f['motion_timing'])}\")\n        if f.get('audio'):\n            video.append(f\"audio/voice direction: {_txt(f['audio'])}\")\n        elif f.get('transition_audio'):\n            video.append(f\"transitions/audio: {_txt(f['transition_audio'])}\")\n        if video: rows.append('Motion execution — '+'; '.join(video)+'.')\n"""
text = replace_once(text, old_en, new_en, 'EN dynamic render')
path.write_text(text, encoding='utf-8')


# 2) Corrected audit must surface canonical dynamic decisions that Phase 4 explicitly left unresolved.
path = Path('runtime/cbcc/model_native_prompt_audit_fix.py')
text = path.read_text(encoding='utf-8')
old = """    language_missing=[]\n    for item in missing_en:\n        if item not in language_missing:\n            language_missing.append(item)\n\n    missing=[row['decision'] for row in checks if row.get('required',True) and not row.get('projected')]\n"""
new = """    language_missing=[]\n    for item in missing_en:\n        if item not in language_missing:\n            language_missing.append(item)\n\n    # Phase 4 may explicitly leave one dynamic decision unresolved. Preserve that boundary here;\n    # Prompt runtime is not allowed to manufacture audio/motion/timing merely to make itself READY.\n    dynamic_missing=[str(x) for x in (asset.get('dynamic_art_direction_missing') or []) if str(x) in {'motion','timing','audio'}]\n    for decision in dynamic_missing:\n        checks.append(_check(decision,'AGENT_DYNAMIC_DECISION_REQUIRED','AGENT_DECISION',False))\n\n    missing=[row['decision'] for row in checks if row.get('required',True) and not row.get('projected')]\n"""
text = replace_once(text, old, new, 'dynamic missing audit')
path.write_text(text, encoding='utf-8')


# 3) Production-parameter closure consumes the same canonical dynamic values and never overwrites an upstream missing decision with fake READY.
path = Path('runtime/cbcc/production_parameter_closure.py')
text = path.read_text(encoding='utf-8')
text = replace_once(
    text,
    "from typing import Any, Mapping\n",
    "from typing import Any, Mapping\n\nfrom . import model_native_prompt_contract as native\n",
    'import native dynamic sanitizer',
)

old = """    if video:\n        add('duration_timing', ('duration','timing','beat_timing','shot_timing'), ('video','motion'))\n        add('shot_sequence', ('shot_sequence','shot_plan','storyboard'), ('video','motion'))\n        add('camera_motion', ('camera_motion','motion_program'), ('video','motion','camera'))\n        add('subject_motion', ('subject_motion','action_motion'), ('video','motion'))\n        add('fps', ('fps','frame_rate'), ('video','motion','camera'))\n        add('stabilization', ('stabilization','stabilisation'), ('video','motion','camera'))\n        add('transition_audio', ('transition_audio','transitions','audio_direction','music_direction'), ('video','motion','audio'))\n        add('cta_hold', ('cta_hold','end_frame_hold','final_hold'), ('video','motion'))\n        add('subtitle_safe_zone', ('subtitle_safe_zone','caption_safe_zone'), ('video','motion','typography'))\n"""
new = """    if video:\n        canonical_motion=native._dynamic_model_value(art.get('motion'))\n        canonical_timing=native._dynamic_model_value(art.get('timing'))\n        canonical_audio=native._dynamic_model_value(art.get('audio'))\n        if _meaningful(canonical_motion): params['motion']=canonical_motion\n        if _meaningful(canonical_timing): params['timing']=canonical_timing\n        if _meaningful(canonical_audio): params['audio']=canonical_audio\n        if not _meaningful(canonical_timing):\n            add('duration_timing', ('duration','timing','beat_timing','shot_timing'), ('video','motion'))\n        if not _meaningful(canonical_motion):\n            add('shot_sequence', ('shot_sequence','shot_plan','storyboard'), ('video','motion'))\n            add('camera_motion', ('camera_motion','motion_program'), ('video','motion','camera'))\n            add('subject_motion', ('subject_motion','action_motion'), ('video','motion'))\n        add('fps', ('fps','frame_rate'), ('video','motion','camera'))\n        add('stabilization', ('stabilization','stabilisation'), ('video','motion','camera'))\n        if not _meaningful(canonical_audio):\n            add('transition_audio', ('transition_audio','transitions','audio_direction','music_direction'), ('video','motion','audio'))\n        add('cta_hold', ('cta_hold','end_frame_hold','final_hold'), ('video','motion'))\n        add('subtitle_safe_zone', ('subtitle_safe_zone','caption_safe_zone'), ('video','motion','typography'))\n"""
text = replace_once(text, old, new, 'canonical dynamic selected parameters')

old = """def _append_selected(prompt: str, params: Mapping[str, Any], language: str) -> tuple[str, list[str]]:\n    out=prompt.rstrip()\n    appended=[]\n"""
new = """def _append_selected(prompt: str, params: Mapping[str, Any], language: str, skip_keys: set[str] | None=None) -> tuple[str, list[str]]:\n    out=prompt.rstrip()\n    appended=[]\n    skip_keys=set(skip_keys or set())\n"""
text = replace_once(text, old, new, 'append selected signature')
text = replace_once(
    text,
    """    for key,value in params.items():\n        if key.startswith('_') or not _meaningful(value):\n            continue\n""",
    """    for key,value in params.items():\n        if key.startswith('_') or key in skip_keys or not _meaningful(value):\n            continue\n""",
    'append selected skip keys',
)
text = replace_once(
    text,
    """'duration_timing':'时长/节拍','shot_sequence':'镜头序列','camera_motion':'镜头运动','subject_motion':'主体运动','fps':'帧率'""",
    """'motion':'动作/镜头程序','timing':'时长/节拍','audio':'音频/配音','duration_timing':'时长/节拍','shot_sequence':'镜头序列','camera_motion':'镜头运动','subject_motion':'主体运动','fps':'帧率'""",
    'dynamic labels',
)

old = """    cn=out.get('model_prompt_cn') or out.get('prompt_cn') or ''\n    en=out.get('model_prompt_en') or out.get('prompt_en') or ''\n    cn,app_cn=_append_selected(cn,params,'CN')\n    en,app_en=_append_selected(en,params,'EN')\n"""
new = """    cn=out.get('model_prompt_cn') or out.get('prompt_cn') or ''\n    en=out.get('model_prompt_en') or out.get('prompt_en') or ''\n    # An explicit hand-authored model prompt must prove it already contains canonical dynamic\n    # decisions; closure may not silently repair a lossy manual override and call it authoritative.\n    manual_prompt_override=any(_meaningful(art.get(k)) for k in ('model_prompt_cn','model_prompt_en','generation_prompt_cn','generation_prompt_en'))\n    skip_dynamic={'motion','timing','audio'} if manual_prompt_override else set()\n    cn,app_cn=_append_selected(cn,params,'CN',skip_dynamic)\n    en,app_en=_append_selected(en,params,'EN',skip_dynamic)\n"""
text = replace_once(text, old, new, 'manual dynamic override closure')

old = """    prior_status=str(out.get('model_prompt_status') or '')\n    specific_prior={'BILINGUAL_RENDER_SEMANTICS_REQUIRED','COPY_RENDER_MODE_REQUIRED','AGENT_ART_DIRECTION_REQUIRED'}\n    if prior_status in specific_prior:\n        # Preserve the more precise upstream readiness reason; closure details remain visible alongside it.\n        out['model_prompt_status']=prior_status\n    elif closure['model_generation_blocking']:\n        out['model_prompt_status']='ART_DIRECTION_EXECUTION_DEPTH_REQUIRED'\n    else:\n        out['model_prompt_status']='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'\n"""
new = """    prior_status=str(out.get('model_prompt_status') or '')\n    specific_prior={'BILINGUAL_RENDER_SEMANTICS_REQUIRED','COPY_RENDER_MODE_REQUIRED','AGENT_ART_DIRECTION_REQUIRED'}\n    audit_missing=list((out.get('prompt_consumption_audit') or {}).get('missing_decisions') or [])\n    if prior_status in specific_prior:\n        # Preserve the more precise upstream readiness reason; closure details remain visible alongside it.\n        out['model_prompt_status']=prior_status\n    elif closure['model_generation_blocking']:\n        out['model_prompt_status']='ART_DIRECTION_EXECUTION_DEPTH_REQUIRED'\n    elif audit_missing:\n        out['model_prompt_status']=prior_status if prior_status not in {'','MODEL_NATIVE_PROMPT_READY','MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'} else 'MODEL_PROMPT_NEEDS_AGENT_DECISIONS'\n    else:\n        out['model_prompt_status']='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'\n"""
text = replace_once(text, old, new, 'no fake prompt readiness')
path.write_text(text, encoding='utf-8')
