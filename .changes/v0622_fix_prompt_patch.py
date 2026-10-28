from pathlib import Path

p=Path('.changes/v0622_prompt_patch.py')
text=p.read_text(encoding='utf-8')
old="text=replace_once(text,clean_anchor,filter_code,'section relevance filter')"
new="""if 'def _prompt_section_relevance(' not in text:
    marker='\\ndef _cn_phrase('
    if marker not in text:
        raise SystemExit('missing prompt helper insertion boundary')
    helper_code=filter_code[len(clean_anchor):]
    text=text.replace(marker, helper_code+marker, 1)"""
if old in text:
    text=text.replace(old,new,1)
elif new not in text:
    raise SystemExit('prompt patch relevance statement not found')
p.write_text(text,encoding='utf-8')
