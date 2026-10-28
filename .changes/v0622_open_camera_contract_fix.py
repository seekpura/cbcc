from pathlib import Path

p=Path('runtime/cbcc/prompt_compiler.py')
text=p.read_text(encoding='utf-8')
text=text.replace(
    "'camera_or_view': brief.get('camera_or_view') or sig.get('camera_or_view') or camera.get('view') or camera.get('preferred_view'),",
    "'camera_or_view': brief.get('camera_or_view') or sig.get('camera_or_view') or camera.get('view') or camera.get('preferred_view') or camera.get('perspective_contract') or camera.get('viewpoint'),",
    1,
)
text=text.replace(
    "'distance': camera.get('distance') or camera.get('working_distance'), 'camera_height': camera.get('camera_height'),",
    "'distance': camera.get('distance') or camera.get('working_distance') or camera.get('camera_distance'), 'camera_height': camera.get('camera_height'),",
    1,
)
old="""        'photography_execution': {
            'capture_mode': p.get('capture_mode'),
            'composition': composition_execution,
            'color_management': color_management_execution,
        },
"""
new="""        'photography_execution': {
            'capture_mode': p.get('capture_mode'),
            'camera': _compact(camera),
            'composition': composition_execution,
            'lighting': _compact(lighting),
            'cmf': _compact(cmf),
            'color_management': color_management_execution,
            'repeatable_capture': p.get('repeatable_capture'),
            'prelight_required': p.get('prelight_required'),
        },
"""
if old not in text:
    raise SystemExit('photography_execution target missing')
text=text.replace(old,new,1)
# Add an open-contract prompt line so future camera fields are not silently lost even when no dedicated display mapping exists.
old_cn="""            f\"构图执行合同：{_txt(_cn_phrase(photo_exec.get('composition')))}\",
"""
new_cn="""            f\"构图执行合同：{_txt(_cn_phrase(photo_exec.get('composition')))}\",
            f\"摄影机执行合同：{_txt(_cn_phrase(photo_exec.get('camera')))}\",
"""
if old_cn in text:
    text=text.replace(old_cn,new_cn,1)
old_en="""            f\"Composition execution contract: {_txt(photo_exec.get('composition'))}\",
"""
new_en="""            f\"Composition execution contract: {_txt(photo_exec.get('composition'))}\",
            f\"Camera execution contract: {_txt(photo_exec.get('camera'))}\",
"""
if old_en in text:
    text=text.replace(old_en,new_en,1)
p.write_text(text,encoding='utf-8')
