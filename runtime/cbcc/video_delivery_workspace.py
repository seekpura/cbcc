from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
import html
import json


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _text(value: Any) -> str:
    if value in (None, '', [], {}):
        return '—'
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def _copy_with_companion(label: str, value: Any, companion: Any = None) -> str:
    if value in (None, '', [], {}):
        return ''
    body = html.escape(_text(value))
    cn = ''
    if companion not in (None, '', [], {}):
        cn = f'<div class="vd-cn"><span>中文释义 / 用途</span><div>{html.escape(_text(companion))}</div></div>'
    return f'<div class="vd-row"><span>{html.escape(label)}</span><div class="vd-value">{body}</div>{cn}</div>'


def _shot_rows(row: dict[str, Any]) -> str:
    shots = row.get('shots') or row.get('shot_program') or row.get('script_bm') or []
    cards = []
    for i, shot in enumerate(shots, start=1):
        if isinstance(shot, dict):
            timing = shot.get('seconds') or shot.get('timing') or shot.get('duration') or shot.get('shot')
            job = shot.get('job') or shot.get('purpose') or shot.get('objective')
            visual = shot.get('visual') or shot.get('action') or shot.get('scene')
            visible = shot.get('visible_copy') or shot.get('copy') or shot.get('on_screen_text')
            zh = shot.get('delivery_translation_zh') or shot.get('visible_copy_zh') or shot.get('copy_zh')
        elif isinstance(shot, (list, tuple)):
            timing = shot[0] if len(shot) > 0 else None
            visible = shot[1] if len(shot) > 1 else None
            visual = shot[2] if len(shot) > 2 else None
            job = None
            zh = shot[3] if len(shot) > 3 else None
        else:
            timing = None; job = None; visual = shot; visible = None; zh = None
        cards.append(
            '<article class="vd-shot">'
            f'<header><span>{i:02d}</span><b>{html.escape(_text(timing))}</b></header>'
            + _copy_with_companion('镜头任务', job)
            + _copy_with_companion('画面 / 动作 / 场景', visual)
            + _copy_with_companion('目标市场屏显 / 台词', visible, zh)
            + '</article>'
        )
    return ''.join(cards) or '<div class="vd-empty">当前视频对象还没有逐镜头程序。</div>'


def render_video_workspace(package_dir: Path | str) -> str:
    package = Path(package_dir)
    universe = _read_json(package / 'video' / 'VIDEO_UNIVERSE.json')
    rows = [x for x in universe.get('assets') or [] if isinstance(x, dict)]
    if not rows:
        return ''
    cards = []
    for i, row in enumerate(rows, start=1):
        vid = str(row.get('video_id') or row.get('id') or f'VID-{i:02d}')
        title = row.get('title_zh') or row.get('title') or row.get('narrative_carrier') or vid
        exact_hook = row.get('hook') or row.get('shopper_question') or row.get('first_frame_copy')
        hook_zh = row.get('hook_zh') or row.get('delivery_translation_zh') or row.get('shopper_question_zh')
        cards.append(
            f'<section class="vd-card searchable" id="video-{html.escape(vid)}">'
            f'<div class="vd-head"><div><span>{html.escape(vid)}</span><h2>{html.escape(_text(title))}</h2></div>'
            f'<strong>{html.escape(_text(row.get("deployment_state") or row.get("pool") or row.get("surface")))}</strong></div>'
            '<div class="vd-meta">'
            + _copy_with_companion('Surface / 载体', row.get('surface') or row.get('family'))
            + _copy_with_companion('Narrative Carrier / 叙事载体', row.get('narrative_carrier'), row.get('narrative_carrier_zh'))
            + _copy_with_companion('Duration / 时长', row.get('duration_seconds') or row.get('format'))
            + _copy_with_companion('Hook / 第一帧', exact_hook, hook_zh)
            + _copy_with_companion('Subject Presence / 主体', row.get('subject_system') or row.get('subject'))
            + _copy_with_companion('CTA', row.get('cta'), row.get('cta_zh'))
            + _copy_with_companion('Voice / Subtitle Locale', {'voice': row.get('voice_locale'), 'subtitle': row.get('subtitle_locales')})
            + _copy_with_companion('Rights / Creator Contract', row.get('creator_contract') or row.get('rights'))
            + '</div><div class="vd-shots"><h3>逐镜头程序 / Shot Program</h3>' + _shot_rows(row) + '</div></section>'
        )
    return ''.join(cards)


def video_workspace_css() -> str:
    return '''
.vd-grid{display:grid;gap:14px}.vd-card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px}.vd-head{display:flex;justify-content:space-between;gap:14px;align-items:start;border-bottom:1px solid var(--line);padding-bottom:10px;margin-bottom:12px}.vd-head span{font:800 10px ui-monospace,monospace;color:var(--accent)}.vd-head h2{font-size:18px;margin:3px 0}.vd-head strong{font-size:9px;background:var(--soft);padding:5px 8px;border-radius:999px}.vd-meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px}.vd-row{border:1px solid var(--line);border-radius:11px;padding:10px;min-width:0}.vd-row>span{display:block;font-size:9px;color:var(--muted);margin-bottom:4px}.vd-value{white-space:pre-wrap;word-break:break-word}.vd-cn{margin-top:7px;background:#eef5f1;border-left:3px solid var(--accent);padding:7px 8px}.vd-cn span{font-size:8px;color:var(--accent);font-weight:800}.vd-cn div{margin-top:2px}.vd-shots{margin-top:14px}.vd-shots>h3{font-size:13px}.vd-shot{border-top:1px solid var(--line);padding:10px 0}.vd-shot header{display:flex;gap:10px;align-items:center;margin-bottom:7px}.vd-shot header span{font:800 9px ui-monospace,monospace;color:var(--accent)}.vd-shot header b{font-size:11px}.vd-empty{color:var(--muted);padding:10px;border:1px dashed var(--line);border-radius:10px}@media(max-width:700px){.vd-meta{grid-template-columns:1fr}}
'''


def apply_video_workspace_to_existing_html(package_dir: Path | str, html_path: Path | str | None = None) -> Path | None:
    """Mount already-materialized Video/Creator objects after base HTML export.

    v0.6.47 materializes video after the legacy HTML builder, so a build-wrapper alone is insufficient.
    This function patches the existing frozen cbcc-commercial-v1 document additively.
    """
    package = Path(package_dir)
    target = Path(html_path) if html_path else package / 'index.html'
    if not target.exists():
        return None
    body = render_video_workspace(package)
    if not body:
        return target
    page = target.read_text(encoding='utf-8')
    if 'data-route="video"' in page:
        return target
    nav_marker = '</div><div class="sidebar-foot">'
    nav = '<a href="#video" data-route="video" class="route-link"><span class="ico">▶</span>视频 / Creator</a>'
    if nav_marker in page:
        page = page.replace(nav_marker, nav + nav_marker, 1)
    route = (
        '<section class="page" data-route="video"><div class="page-head"><div>'
        '<div class="kicker">VIDEO · CREATOR · LIVE</div><h1>视频 / Creator 工作台</h1>'
        '<p>视频、Creator、UGC 与 Live 是独立商业资产对象，不受 Gallery 图片槽位限制；逐镜头、屏显、字幕、声音、版权、CTA 与落地承接按当前对象展开。</p>'
        '</div></div><div class="vd-grid">' + body + '</div></section>'
    )
    end = page.rfind('</div></div><script>')
    if end != -1:
        page = page[:end] + route + page[end:]
    elif '</body>' in page:
        page = page.replace('</body>', route + '</body>', 1)
    css = video_workspace_css()
    if '</style>' in page:
        page = page.replace('</style>', css + '</style>', 1)
    elif '</head>' in page:
        page = page.replace('</head>', '<style>' + css + '</style></head>', 1)
    target.write_text(page, encoding='utf-8')
    return target


def wrap_build_delivery_html(fn: Callable[..., Path]):
    """Add Video/Creator as an additive routed object inside cbcc-commercial-v1 when active."""
    def built(package_dir, output=None, title='CBCC Delivery', *args, **kwargs):
        result = fn(package_dir, output, title=title, *args, **kwargs)
        apply_video_workspace_to_existing_html(package_dir, result)
        return result
    return built
