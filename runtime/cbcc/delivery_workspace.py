from __future__ import annotations

from pathlib import Path

from .delivery_html import build_delivery_html as _build_legacy_delivery_html
from .project_authored_html import project_authored_html


_OBJECT_WORKSPACE_CSS = r'''
/* Asset object compatibility only. This layer must not define project-level information architecture. */
.asset-object-workspace{display:block!important}
.asset-object-navigator{position:static!important;top:auto!important;display:flex!important;gap:8px!important;overflow:auto!important;max-height:none!important;padding:8px!important;margin:0 0 12px!important;background:#fff!important;border:1px solid var(--line)!important;border-radius:16px!important}
.asset-object-nav-head{display:flex!important;min-width:max-content!important;align-items:center!important;gap:8px!important;padding:4px 8px!important;border:0!important;margin:0!important}
.asset-object-nav-head b{font-size:11px}.asset-object-nav-head span{font-size:9px;color:var(--muted)}
.asset-object-tab{display:block!important;min-width:max-content!important;border:1px solid var(--line)!important;background:#fff!important;text-align:left!important;border-radius:999px!important;padding:8px 12px!important;color:var(--ink)!important}
.asset-object-tab:hover{background:var(--soft)!important}.asset-object-tab.active{background:var(--accent)!important;color:#fff!important;border-color:var(--accent)!important}
.asset-object-tab-copy small{display:none!important}.asset-object-tab-copy b{display:block!important;font-size:11px!important;margin:0!important}
.asset-object-canvas{min-width:0}.asset-object-panel{background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 8px 28px rgba(20,35,28,.04)}
.asset-object-panel-head{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;padding:18px 20px;border-bottom:1px solid var(--line)}
.asset-object-panel-head span{font-size:9px;color:var(--muted);letter-spacing:.08em}.asset-object-panel-head h2{margin:2px 0 4px;font-size:20px}.asset-object-panel-head p{margin:0;color:var(--muted);max-width:860px}
.asset-object-panel-body{padding:18px 20px}
@media(max-width:760px){.asset-object-navigator{border-radius:12px}.asset-object-tab{padding:7px 10px}.asset-object-panel-body{padding:14px}.asset-object-panel-head{padding:14px}}
'''

_REPLACEMENTS = (
    ('asset-production-workspace', 'asset-object-workspace'),
    ('asset-production-rail', 'asset-object-navigator'),
    ('asset-rail-head', 'asset-object-nav-head'),
    ('asset-phase-copy', 'asset-object-tab-copy'),
    ('asset-phase-index', 'asset-object-tab-index'),
    ('asset-phase', 'asset-object-tab'),
    ('asset-production-stage', 'asset-object-canvas'),
    ('asset-stage-head', 'asset-object-panel-head'),
    ('asset-stage-body', 'asset-object-panel-body'),
    ('asset-stage-', 'asset-object-panel-'),
    ('asset-stage', 'asset-object-panel'),
    ('当前工作视图', '资产对象'),
    ('个相关视图 · 无固定先后顺序', '个对象视图 · 自由进入'),
    ('data-workspace-kind="asset-production"', 'data-workspace-kind="asset-object"'),
)


def _transform_asset_compatibility(page: str) -> str:
    """Keep old asset routes readable without imposing any project-level UI/IA."""
    out = page
    for before, after in _REPLACEMENTS:
        out = out.replace(before, after)
    marker = '</style>'
    if marker in out:
        out = out.replace(marker, _OBJECT_WORKSPACE_CSS + marker, 1)
    return out


def build_delivery_html(package_dir: Path, output: Path | None = None, title: str = 'CBCC Delivery') -> Path:
    """Build the human artifact as a project-authored object workspace.

    The legacy renderer remains the content authority so strategy/listing/asset depth is not lost.
    Presentation is then rewritten away from the old capability sidebar and phase-rail grammar.
    No operator dashboard or capability-proof section is injected at a fixed position.
    """
    package_dir = Path(package_dir)
    output = Path(output) if output else package_dir / 'index.html'
    result = _build_legacy_delivery_html(package_dir, output, title=title)
    text = result.read_text(encoding='utf-8')
    text = _transform_asset_compatibility(text)
    text = project_authored_html(text)
    result.write_text(text, encoding='utf-8')
    return result
