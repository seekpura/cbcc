from __future__ import annotations

from pathlib import Path


def main() -> None:
    source=Path('scripts/apply_v0631_human_workspace_depth.py').read_text(encoding='utf-8')
    old="text2,n=re.subn(pat,new,text,flags=re.S)"
    new="text2,n=re.subn(pat,lambda _m:new,text,flags=re.S)"
    if old not in source and new not in source:
        raise SystemExit('migration escape anchor missing')
    source=source.replace(old,new,1)
    ns={'__name__':'v0631_human_workspace_depth_runtime'}
    exec(compile(source,'scripts/apply_v0631_human_workspace_depth.py','exec'),ns)
    ns['main']()


if __name__=='__main__':
    main()
