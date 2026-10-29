from __future__ import annotations

from pathlib import Path


def main() -> None:
    source=Path('scripts/apply_v0631_prompt_workspace_ui.py').read_text(encoding='utf-8')
    ns={'__name__':'v0631_prompt_workspace_ui_runtime'}
    exec(compile(source,'scripts/apply_v0631_prompt_workspace_ui.py','exec'),ns)
    ns['main']()

    path=Path('runtime/cbcc/delivery_html.py')
    lines=path.read_text(encoding='utf-8').splitlines()
    repaired=[]
    i=0
    removed=False
    while i < len(lines):
        if lines[i].strip()=='if prompt_cn:':
            j=i+1
            while j < len(lines) and not lines[j].strip():
                j+=1
            if j < len(lines) and lines[j].strip()=='if prompt_en:':
                k=j+1
                while k < len(lines) and not lines[k].strip():
                    k+=1
                if k < len(lines) and lines[k].strip()=='if production_notes:':
                    # The UI migration intentionally removed the two duplicate prompt views. The
                    # now-empty branches are removed while preserving the production-notes branch.
                    i=k
                    removed=True
                    continue
        repaired.append(lines[i])
        i+=1
    if not removed:
        raise SystemExit('expected empty prompt_cn/prompt_en branches were not found after UI migration')
    path.write_text('\n'.join(repaired)+'\n',encoding='utf-8')
    print('Applied prompt workspace UI and repaired duplicate-view branches.')


if __name__=='__main__':
    main()
