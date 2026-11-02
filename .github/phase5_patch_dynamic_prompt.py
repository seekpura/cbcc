from pathlib import Path

path = Path('runtime/cbcc/model_native_prompt_contract.py')
text = path.read_text(encoding='utf-8')

anchor = """def _lang(value: Any, language: str, missing: list[str], field: str) -> Any:\n"""
helper = """_MODEL_DYNAMIC_METADATA_KEYS = {\n    'authority', 'video_id', 'family', 'surface', 'authored_fields', 'authored_dynamic_fields',\n    'source_asset_id', 'dynamic_art_direction_source_video_id', 'runtime_may_invent_missing_dynamic_art_direction',\n    'provenance', 'sha256', 'hash', 'provider_asset_handle', 'ingest_status',\n}\n\n\ndef _model_dynamic_block(value: Any) -> Any:\n    \"\"\"Keep model-visible temporal/audio decisions while removing runtime/provenance metadata.\"\"\"\n    if not _meaningful(value):\n        return None\n    if isinstance(value, Mapping):\n        out = {}\n        for key, child in value.items():\n            if str(key) in _MODEL_DYNAMIC_METADATA_KEYS:\n                continue\n            cleaned = _model_dynamic_block(child)\n            if _meaningful(cleaned):\n                out[str(key)] = cleaned\n        return out or None\n    if isinstance(value, (list, tuple)):\n        rows = [_model_dynamic_block(item) for item in value]\n        rows = [item for item in rows if _meaningful(item)]\n        return rows or None\n    return deepcopy(value)\n\n\n"""
if '_MODEL_DYNAMIC_METADATA_KEYS' not in text:
    if anchor not in text:
        raise SystemExit('language helper anchor missing')
    text = text.replace(anchor, helper + anchor, 1)

fields_anchor = """    fields={\n"""
fields_prefix = """    motion_block=_model_dynamic_block(art.get('motion'))\n    timing_block=_model_dynamic_block(art.get('timing'))\n    audio_block=_model_dynamic_block(art.get('audio'))\n\n"""
model_fields_start = text.index('def _model_fields(')
fields_pos = text.index(fields_anchor, model_fields_start)
if 'motion_block=_model_dynamic_block' not in text[model_fields_start:fields_pos]:
    text = text[:fields_pos] + fields_prefix + text[fields_pos:]

old = """        'inclusive_human': L(_first(art, 'inclusive_human', 'representation') or inc, 'inclusive_human'),\n        'motion_timing': L(_first(art, 'motion_timing', 'timing', 'duration', 'shot_timing'), 'motion_timing'),\n        'shot_sequence': L(_first(art, 'shot_sequence', 'shot_plan', 'storyboard'), 'shot_sequence'),\n        'camera_motion': L(_first(art, 'camera_motion', 'motion_program'), 'camera_motion'),\n        'transition_audio': L(_first(art, 'transition_audio', 'transitions', 'audio_direction'), 'transition_audio'),\n"""
new = """        'inclusive_human': L(_first(art, 'inclusive_human', 'representation') or inc, 'inclusive_human'),\n        # Phase 4 canonical dynamic authority. Runtime/provenance metadata is stripped before\n        # language resolution so only frame/audio-changing decisions enter the acting plane.\n        'motion': L(motion_block, 'motion'),\n        'timing': L(timing_block, 'timing'),\n        'audio': L(audio_block, 'audio'),\n        # Backward-compatible legacy prompt fields remain supported when canonical blocks are absent.\n        'motion_timing': L(_first(art, 'motion_timing', 'duration', 'shot_timing'), 'motion_timing'),\n        'shot_sequence': L(_first(art, 'shot_sequence', 'shot_plan', 'storyboard'), 'shot_sequence'),\n        'camera_motion': L(_first(art, 'camera_motion', 'motion_program'), 'camera_motion'),\n        'transition_audio': L(_first(art, 'transition_audio', 'transitions', 'audio_direction'), 'transition_audio'),\n"""
if old in text:
    text = text.replace(old, new, 1)
elif "'motion': L(motion_block, 'motion')" not in text:
    raise SystemExit('dynamic field block shape changed')

old_cn = """        if is_video:\n            video=[]\n            for k,label in [('motion_timing','时长/节奏'),('shot_sequence','镜头顺序'),('camera_motion','镜头运动'),('transition_audio','转场/音频')]:\n                if f.get(k): video.append(f\"{label}：{_txt(f[k])}\")\n            if video: rows.append('动态执行：'+'；'.join(video)+'。')\n"""
new_cn = """        if is_video:\n            video=[]\n            if f.get('motion'):\n                video.append(f\"动作/镜头执行：{_txt(f['motion'])}\")\n            else:\n                for k,label in [('shot_sequence','镜头顺序'),('camera_motion','镜头运动')]:\n                    if f.get(k): video.append(f\"{label}：{_txt(f[k])}\")\n            if f.get('timing'):\n                video.append(f\"时长/节奏：{_txt(f['timing'])}\")\n            elif f.get('motion_timing'):\n                video.append(f\"时长/节奏：{_txt(f['motion_timing'])}\")\n            if f.get('audio'):\n                video.append(f\"声音/字幕执行：{_txt(f['audio'])}\")\n            elif f.get('transition_audio'):\n                video.append(f\"转场/音频：{_txt(f['transition_audio'])}\")\n            if video: rows.append('动态执行：'+'；'.join(video)+'。')\n"""
if old_cn in text:
    text = text.replace(old_cn, new_cn, 1)
elif "动作/镜头执行" not in text:
    raise SystemExit('CN video render block shape changed')

old_en = """    if is_video:\n        video=[]\n        for k,label in [('motion_timing','duration/rhythm'),('shot_sequence','shot sequence'),('camera_motion','camera motion'),('transition_audio','transitions/audio')]:\n            if f.get(k): video.append(f\"{label}: {_txt(f[k])}\")\n        if video: rows.append('Motion execution — '+'; '.join(video)+'.')\n"""
new_en = """    if is_video:\n        video=[]\n        if f.get('motion'):\n            video.append(f\"motion/shot execution: {_txt(f['motion'])}\")\n        else:\n            for k,label in [('shot_sequence','shot sequence'),('camera_motion','camera motion')]:\n                if f.get(k): video.append(f\"{label}: {_txt(f[k])}\")\n        if f.get('timing'):\n            video.append(f\"timing/rhythm: {_txt(f['timing'])}\")\n        elif f.get('motion_timing'):\n            video.append(f\"duration/rhythm: {_txt(f['motion_timing'])}\")\n        if f.get('audio'):\n            video.append(f\"voice/subtitle/audio execution: {_txt(f['audio'])}\")\n        elif f.get('transition_audio'):\n            video.append(f\"transitions/audio: {_txt(f['transition_audio'])}\")\n        if video: rows.append('Motion execution — '+'; '.join(video)+'.')\n"""
if old_en in text:
    text = text.replace(old_en, new_en, 1)
elif 'motion/shot execution' not in text:
    raise SystemExit('EN video render block shape changed')

path.write_text(text, encoding='utf-8')
