from __future__ import annotations

from typing import Any
import html
import re


WORKSPACE_SHELL_VERSION = 'cbcc-commercial-v1'

_SHELL_CSS = r'''
.cbcc-commandbar{position:relative;z-index:5;display:flex;align-items:center;gap:12px;justify-content:space-between;padding:10px 14px;background:rgba(248,249,247,.98);border-bottom:1px solid var(--line,#dde3df);font-size:11px}
.cbcc-commandbar-main{display:flex;align-items:center;gap:10px;min-width:0}.cbcc-commandbar-brand{font-weight:750;letter-spacing:.02em;white-space:nowrap}.cbcc-commandbar-state{display:flex;gap:7px;flex-wrap:wrap;min-width:0}.cbcc-state-chip{display:inline-flex;align-items:center;gap:5px;padding:5px 8px;border:1px solid var(--line,#dde3df);border-radius:999px;background:#fff;white-space:nowrap}.cbcc-state-chip b{font-size:9px;color:var(--muted,#6a746f);font-weight:650}.cbcc-shell-meta{font-size:9px;color:var(--muted,#6a746f);white-space:nowrap}.cbcc-shell-note{display:none}
@media(max-width:760px){.cbcc-commandbar{align-items:flex-start}.cbcc-commandbar-main{display:block}.cbcc-commandbar-state{margin-top:6px}.cbcc-shell-meta{display:none}}
@media print{.cbcc-commandbar{position:static}.cbcc-shell-meta{display:none}}
'''


def _txt(value: Any, fallback: str) -> str:
    value = str(value or '').strip()
    return value or fallback


def _language_label(plan: dict[str, Any]) -> str:
    mode = str(plan.get('mode') or '')
    labels = {
        'CN_ONLY': '中文',
        'EN_CN': '英文 + 中文释义',
        'EN_PLATFORM_PRIMARY_CN': '英文 + 平台主语言 + 中文释义',
        'EN_CN_PENDING_PLATFORM_PRIMARY': '英文 + 中文释义 · 主语言待指定',
    }
    return labels.get(mode, '语言方案待确认')


def apply_commercial_workspace_shell(page: str, scope: dict[str, Any], language_plan: dict[str, Any]) -> str:
    """Apply the frozen v1 commercial shell without replacing project-authored content.

    v1 is an interaction floor, not a fixed page taxonomy: existing project routes/subviews/assets remain
    authoritative. The command bar stays in normal document flow so the mature sidebar/topbar sticky
    offsets are untouched. Future releases may add objects or polish components but must not replace
    this shell without an explicit shell-version change.
    """
    if f'data-workspace-shell="{WORKSPACE_SHELL_VERSION}"' in page:
        return page

    platform = _txt(scope.get('platform'), '平台待指定')
    market = _txt(scope.get('market'), '市场待指定')
    language = _language_label(language_plan)
    commandbar = (
        '<div class="cbcc-commandbar" role="region" aria-label="CBCC 商业工作台状态">'
        '<div class="cbcc-commandbar-main">'
        '<div class="cbcc-commandbar-brand">CBCC 商业工作台</div>'
        '<div class="cbcc-commandbar-state">'
        f'<span class="cbcc-state-chip"><b>平台</b>{html.escape(platform)}</span>'
        f'<span class="cbcc-state-chip"><b>市场</b>{html.escape(market)}</span>'
        f'<span class="cbcc-state-chip"><b>语言</b>{html.escape(language)}</span>'
        '</div></div>'
        f'<div class="cbcc-shell-meta">{WORKSPACE_SHELL_VERSION}</div>'
        '<span class="cbcc-shell-note">一次只显示一个一级工作面</span>'
        '</div>'
    )

    # Root marker is the stable compatibility hook used by tests and future additive releases.
    if '<body' in page:
        page = re.sub(r'<body(\s[^>]*)?>', lambda m: (
            '<body' + (m.group(1) or '') + f' data-workspace-shell="{WORKSPACE_SHELL_VERSION}">'
        ), page, count=1)
        body_match = re.search(r'<body[^>]*>', page)
        if body_match:
            page = page[:body_match.end()] + commandbar + page[body_match.end():]

    if '</style>' in page:
        page = page.replace('</style>', _SHELL_CSS + '</style>', 1)
    elif '</head>' in page:
        page = page.replace('</head>', f'<style>{_SHELL_CSS}</style></head>', 1)

    return page
