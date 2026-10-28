from pathlib import Path

p=Path('.changes/v0622_regression_fix.py')
text=p.read_text(encoding='utf-8')
text=text.replace("new_func=r'''def _asset_page(a:dict[str,Any])->str:", 'new_func=r"""def _asset_page(a:dict[str,Any])->str:', 1)
needle="\n'''\ntext=text[:start]+new_func+text[end:]"
replacement='\n"""\ntext=text[:start]+new_func+text[end:]'
if needle not in text and replacement not in text:
    raise SystemExit('missing outer regression patch terminator')
text=text.replace(needle,replacement,1)
p.write_text(text,encoding='utf-8')
