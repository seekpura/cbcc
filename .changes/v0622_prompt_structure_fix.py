from pathlib import Path

p=Path('runtime/cbcc/prompt_compiler.py')
text=p.read_text(encoding='utf-8')
old="""    return _compact({
        'asset_id': asset.get('asset_id'), 'asset_name': asset.get('asset_name'), 'asset_type': asset.get('asset_type'),
"""
new="""    return {
        'asset_id': asset.get('asset_id'), 'asset_name': asset.get('asset_name'), 'asset_type': asset.get('asset_type'),
"""
if old in text:
    text=text.replace(old,new,1)
elif new not in text:
    raise SystemExit('design card return start not found')
old_end="""        'editable_layer_contract': asset.get('editable_layer_contract') or {},
    })


def _render_safe_text"""
new_end="""        'editable_layer_contract': asset.get('editable_layer_contract') or {},
    }


def _render_safe_text"""
if old_end in text:
    text=text.replace(old_end,new_end,1)
elif new_end not in text:
    raise SystemExit('design card return end not found')
p.write_text(text,encoding='utf-8')
