from pathlib import Path

p=Path('.changes/v0622_workspace_patch.py')
text=p.read_text(encoding='utf-8')
text=text.replace("new_func=r'''def _asset_page", 'new_func=r"""def _asset_page', 1)
text=text.replace("\n'''\ntext=text[:start]+new_func+text[end:]", '\n"""\ntext=text[:start]+new_func+text[end:]', 1)
text=text.replace("new_nav=r'''    agent_next_action", 'new_nav=r"""    agent_next_action', 1)
text=text.replace("\n'''\ntext=text[:nav_start]+new_nav+text[source_pos:]", '\n"""\ntext=text[:nav_start]+new_nav+text[source_pos:]', 1)
text=text.replace("new_pages=r'''    stat_rows=[]", 'new_pages=r"""    stat_rows=[]', 1)
text=text.replace("\n'''\ntext=text[:pages_start]+new_pages+text[pages_end:]", '\n"""\ntext=text[:pages_start]+new_pages+text[pages_end:]', 1)
p.write_text(text,encoding='utf-8')
