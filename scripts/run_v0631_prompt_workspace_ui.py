from __future__ import annotations

import re
from pathlib import Path


def main() -> None:
    source=Path('scripts/apply_v0631_prompt_workspace_ui.py').read_text(encoding='utf-8')
    ns={'__name__':'v0631_prompt_workspace_ui_runtime'}
    exec(compile(source,'scripts/apply_v0631_prompt_workspace_ui.py','exec'),ns)
    ns['main']()

    path=Path('runtime/cbcc/delivery_html.py')
    text=path.read_text(encoding='utf-8')
    text2,n=re.subn(
        r"\n        if prompt_cn:\s*\n        if prompt_en:\s*\n(        if production_notes:)",
        r"\n\1",
        text,
        count=1,
    )
    if n!=1 and 'if prompt_cn:\n            \n        if prompt_en:' in text:
        raise SystemExit('could not repair empty model-prompt branches')
    path.write_text(text2,encoding='utf-8')
    print('Applied prompt workspace UI and repaired duplicate-view branches.')


if __name__=='__main__':
    main()
