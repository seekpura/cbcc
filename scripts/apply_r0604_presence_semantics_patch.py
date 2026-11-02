from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected one match, found {count}')
    p.write_text(text.replace(old, new), encoding='utf-8')


replace_once(
    'runtime/cbcc/video_creator.py',
    """    jobs=list(video_jobs or [])
    if not jobs:
""",
    """    video_jobs_supplied=video_jobs is not None
    jobs=list(video_jobs or [])
    if not jobs and not video_jobs_supplied:
""",
)

replace_once(
    'runtime/cbcc/campaign_architecture.py',
    """    jobs=list(explicit or [])
    if not jobs:
""",
    """    explicit_campaigns_supplied=explicit is not None
    jobs=list(explicit or [])
    if not jobs and not explicit_campaigns_supplied:
""",
)
