from __future__ import annotations

"""v0.6.74 cross-scope regression closure.

This module is deliberately additive.  It patches narrow consumer boundaries after the mature
v0.6.73 authority wiring has installed all prior wrappers.  It does not replace strategy, asset,
provider, or Human Workspace authorities.
"""

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Mapping
from collections import Counter
import json
import re
import html

VERSION = '0.6.74-cross-scope-regression-closure'

_FULL_DENY = {
    'TASK_SCOPED', 'TASK_SCOPE', 'PARTIAL', 'NOT_FULL', 'NON_FULL', 'SCOPED', 'MINIMAL',
}
_FULL_EXACT = {
    'FULL', 'FULL_PROJECT', 'FULL_DELIVERY', 'FULL_PACKAGE', 'FULL_COMMERCE', 'FULL_STRATEGY',
    'FULL_WORKSPACE', 'FULL_E2E', 'END_TO_END', 'COMPLETE_DELIVERY', 'COMPLETE_PROJECT', '完整交付', '全量交付', '完整项目', '全量项目',
}
_PROVENANCE_KEY = (
    r'(?:source_ids?|claim_ids?|evidence_ids?|source_refs?|evidence_refs?|'
    r'canonical_art_direction_sha256|authority_hash|lineage(?:_hash)?|provenance|'
    r'artifact_(?:path|id|uri)|source_binding_metadata|sha256)'
)
_PROVENANCE_RE = re.compile(
    rf'(?:\b{_PROVENANCE_KEY}\b\s*[:=]|'
    r'\bartifact\s+(?:path|id|uri)\b\s*[:=]|'
    r'(?:来源\s*(?:ID|编号|标识|追踪)|证据\s*(?:ID|编号|标识)|(?:内部)?谱系|溯源元数据|权威哈希|规范哈希)\s*[:：=])',
    re.I,
)
_PROVENANCE_ASSIGNMENT_RE = re.compile(
    rf'(?:\b{_PROVENANCE_KEY}\b|\bartifact\s+(?:path|id|uri)\b)\s*[:=]\s*'
    r'(?:\[[^\]\n]{0,500}\]|\{[^}\n]{0,500}\}|'
    r'[\"\'A-Za-z0-9_./:@+-]+(?:\s*,\s*[\"\'A-Za-z0-9_./:@+-]+)*)\s*,?\s*',
    re.I,
)
_CN_PROVENANCE_ASSIGNMENT_RE = re.compile(
    r'(?:来源\s*(?:ID|编号|标识|追踪)|证据\s*(?:ID|编号|标识)|(?:内部)?谱系|溯源元数据|权威哈希|规范哈希)'
    r'\s*[:：=]\s*[^，,；;。!?\n]{1,500}[，,]?\s*',
    re.I,
)


def _mode_token(value: Any) -> str:
    raw = str(value or '').strip()
    if not raw:
        return ''
    if re.search(r'[\u3400-\u9fff]', raw):
        return re.sub(r'\s+', '', raw)
    return re.sub(r'[^A-Z0-9]+', '_', raw.upper()).strip('_')


def is_full_strategy(strategy: Mapping[str, Any] | None) -> bool:
    s = dict(strategy or {})
    hp = s.get('human_projection') if isinstance(s.get('human_projection'), Mapping) else {}
    if hp.get('fixed_human_section_quota') is True:
        return True
    raw = hp.get('mode') or s.get('delivery_mode') or s.get('scope_mode') or ''
    token = _mode_token(raw)
    if token in _FULL_DENY or token.startswith('NOT_FULL') or token.startswith('NON_FULL'):
        return False
    if token in _FULL_EXACT:
        return True
    if token.startswith('FULL_') and any(x in token for x in ('PROJECT', 'DELIVERY', 'PACKAGE', 'COMMERCE', 'WORKSPACE', 'STRATEGY', 'E2E')):
        return True
    return token in {'完整', '全量'}


def split_markdown_table_row(line: str) -> list[str]:
    """Split a Markdown table row without treating an escaped pipe as a column boundary."""
    text = str(line or '').strip()
    if text.startswith('|'):
        text = text[1:]
    if text.endswith('|'):
        text = text[:-1]
    cells: list[str] = []
    buf: list[str] = []
    backslashes = 0
    for ch in text:
        if ch == '\\':
            backslashes += 1
            buf.append(ch)
            continue
        if ch == '|' and backslashes % 2 == 0:
            cells.append(''.join(buf).strip())
            buf = []
            backslashes = 0
            continue
        buf.append(ch)
        backslashes = 0
    cells.append(''.join(buf).strip())

    def unescape(cell: str) -> str:
        # Markdown table escaping used by Human Delivery: \| is literal pipe; \\ is literal slash.
        out: list[str] = []
        i = 0
        while i < len(cell):
            if cell[i] == '\\' and i + 1 < len(cell) and cell[i + 1] in {'\\', '|'}:
                out.append(cell[i + 1])
                i += 2
            else:
                out.append(cell[i])
                i += 1
        return ''.join(out)

    return [unescape(x) for x in cells]


def wrap_markdown_to_html(fn: Callable[[str], str]) -> Callable[[str], str]:
    if getattr(fn, '_cbcc_v0674_escaped_pipe', False):
        return fn
    sentinel = '\ue074CBCC_LITERAL_PIPE\ue075'

    def rendered(md: str) -> str:
        # Protect only odd-backslash-escaped pipes.  The legacy parser may keep its mature behavior
        # for every other Markdown construct.
        text = str(md or '')
        out: list[str] = []
        i = 0
        while i < len(text):
            if text[i] == '\\':
                j = i
                while j < len(text) and text[j] == '\\':
                    j += 1
                count = j - i
                if j < len(text) and text[j] == '|' and count % 2 == 1:
                    out.append('\\' * (count - 1))
                    out.append(sentinel)
                    i = j + 1
                    continue
            out.append(text[i])
            i += 1
        return fn(''.join(out)).replace(sentinel, '|')

    setattr(rendered, '_cbcc_v0674_escaped_pipe', True)
    return rendered


def safe_dump_no_aliases(value: Any, **kwargs: Any) -> str:
    import yaml

    class NoAliasSafeDumper(yaml.SafeDumper):
        def ignore_aliases(self, data):  # type: ignore[override]
            return True

    params = dict(kwargs)
    params.pop('Dumper', None)
    params.pop('default_flow_style', None)
    return yaml.dump(
        value,
        Dumper=NoAliasSafeDumper,
        default_flow_style=False,
        **params,
    )


class _YamlNoAliasProxy:
    def __init__(self, real: Any) -> None:
        self._real = real

    def safe_dump(self, value: Any, **kwargs: Any) -> str:
        return safe_dump_no_aliases(value, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._real, name)


_LISTING_CANONICAL_STATES = ['STRATEGY_READY', 'COPY_REVIEW_REQUIRED', 'PUBLISH_READY']
_FINAL_COPY_STATUSES = {'APPROVED_FINAL', 'FINAL_APPROVED', 'APPROVED', 'PUBLISH_READY'}
_REQUIRED_FIELD_HOLD_STATUSES = {'待补', '待查证', 'MISSING', 'MISSING_INPUT', 'INPUT_REQUIRED', 'HOLD'}


def _present(value: Any) -> bool:
    return value not in (None, '', [], {})


def _listing_lifecycle(center: Mapping[str, Any]) -> tuple[str | None, list[str]]:
    """Resolve the project-level Listing lifecycle without overwriting legacy field/readiness states.

    STRATEGY_READY: Listing architecture/strategy exists, but there is no target-locale authored copy to review yet.
    COPY_REVIEW_REQUIRED: Target-locale copy exists, but review/publish prerequisites are not all satisfied.
    PUBLISH_READY: Explicit submission scope + no blocking fields + final-approved target copy + Chinese companion closure.
    """
    task_scope = center.get('task_scope') if isinstance(center.get('task_scope'), Mapping) else {}
    readiness = center.get('readiness') if isinstance(center.get('readiness'), Mapping) else {}
    if not bool(task_scope.get('listing_active')):
        return None, ['listing_not_active']

    localized_all = [
        dict(row) for row in (center.get('localized_copy') or [])
        if isinstance(row, Mapping) and _present(row.get('value'))
    ]
    target = center.get('target') if isinstance(center.get('target'), Mapping) else {}
    visible_locales = target.get('visible_copy_locales') or []
    if not isinstance(visible_locales, (list, tuple, set, frozenset)):
        visible_locales = [visible_locales]
    target_locales = {str(x).strip().casefold() for x in visible_locales if str(x or '').strip()}
    if not target_locales and _present(target.get('locale')):
        target_locales = {str(target.get('locale')).strip().casefold()}
    localized = [
        row for row in localized_all
        if target_locales and str(row.get('locale') or '').strip().casefold() in target_locales
    ]
    copy_rows = [dict(row) for row in (center.get('copy_center') or []) if isinstance(row, Mapping)]

    pending_count = int(readiness.get('pending_count') or 0)
    required_field_hold = any(
        bool(row.get('required_for_current_scope'))
        and str(row.get('status') or '').strip().upper() in {x.upper() for x in _REQUIRED_FIELD_HOLD_STATUSES}
        for row in copy_rows
    )
    pending = pending_count > 0 or required_field_hold
    copy_center_missing_cn = any(
        _present(row.get('value'))
        and str(row.get('delivery_companion_status') or '').strip() == '待补中文释义'
        and (
            not target_locales
            or not _present(row.get('locale'))
            or str(row.get('locale')).strip().casefold() in target_locales
        )
        for row in copy_rows
    )
    default_delivery_locale = str(
        ((center.get('delivery_language') or {}).get('locale') if isinstance(center.get('delivery_language'), Mapping) else None)
        or ((center.get('target') or {}).get('delivery_locale') if isinstance(center.get('target'), Mapping) else None)
        or 'zh-CN'
    ).casefold()
    default_target_locale = str(
        ((center.get('target') or {}).get('locale') if isinstance(center.get('target'), Mapping) else None) or ''
    ).casefold()
    localized_missing_cn = False
    for row in localized:
        row_locale = str(row.get('locale') or default_target_locale or '').casefold()
        row_delivery_locale = str(row.get('delivery_locale') or default_delivery_locale or 'zh-CN').casefold()
        foreign_to_delivery = bool(row_locale and row_delivery_locale and row_locale != row_delivery_locale)
        explicit_missing = str(row.get('delivery_companion_status') or '').strip() == '待补中文释义'
        if (foreign_to_delivery and not _present(row.get('delivery_translation'))) or explicit_missing:
            localized_missing_cn = True
            break
    missing_cn = copy_center_missing_cn or localized_missing_cn

    if not localized:
        reasons = ['no_target_copy_for_review']
        if pending:
            reasons.append('required_fields_pending')
        if missing_cn:
            reasons.append('chinese_companion_missing')
        return 'STRATEGY_READY', reasons

    statuses = [str(row.get('status') or row.get('release_status') or '').strip().upper() for row in localized]
    all_final = bool(statuses) and all(status in _FINAL_COPY_STATUSES for status in statuses)
    submission_sensitive = bool(task_scope.get('listing_submission_sensitive'))

    if submission_sensitive and not pending and not missing_cn and all_final:
        return 'PUBLISH_READY', ['all_publish_conditions_met']

    reasons: list[str] = []
    if pending:
        reasons.append('required_fields_pending')
    if not all_final:
        reasons.append('copy_review_required')
    if missing_cn:
        reasons.append('chinese_companion_missing')
    if not submission_sensitive:
        reasons.append('submission_scope_not_validated')
    return 'COPY_REVIEW_REQUIRED', reasons or ['copy_review_required']


def apply_listing_three_state(center: Mapping[str, Any]) -> dict[str, Any]:
    """Add the canonical Listing lifecycle while preserving all legacy statuses verbatim."""
    out = deepcopy(dict(center or {}))
    state, reasons = _listing_lifecycle(out)
    readiness = out.get('readiness') if isinstance(out.get('readiness'), Mapping) else {}
    legacy_status = readiness.get('status')
    contract = {
        'schema_version': 'cbcc-listing-three-state-v0.6.74',
        'canonical_state': state,
        'allowed_states': list(_LISTING_CANONICAL_STATES),
        'legacy_status': legacy_status,
        'reasons': reasons,
        'publish_ready': state == 'PUBLISH_READY',
        'applicability': 'ACTIVE' if state else 'NOT_IN_CURRENT_SCOPE',
        'principle': 'STRATEGY_READY ≠ COPY_REVIEW_REQUIRED ≠ PUBLISH_READY. Legacy readiness/field statuses remain compatibility metadata and never substitute for the canonical lifecycle state.',
    }
    out['canonical_listing_state'] = state
    out['listing_status_contract'] = contract
    if isinstance(out.get('readiness'), dict):
        out['readiness']['canonical_state'] = state
    return out


def wrap_compile_upload_center(fn: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    if getattr(fn, '_cbcc_v0674_listing_three_state', False):
        return fn

    def compiled(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return apply_listing_three_state(fn(*args, **kwargs))

    setattr(compiled, '_cbcc_v0674_listing_three_state', True)
    return compiled


def _listing_state_banner_md(center: Mapping[str, Any]) -> str:
    state = center.get('canonical_listing_state')
    if not state:
        return ''
    contract = center.get('listing_status_contract') if isinstance(center.get('listing_status_contract'), Mapping) else {}
    legacy = contract.get('legacy_status') or '—'
    reasons = ' · '.join(str(x) for x in (contract.get('reasons') or [])) or '—'
    return (
        f'> 规范 Listing 状态：**{state}**｜兼容旧状态：**{legacy}**  \n'
        f'> 判定依据：{reasons}\n'
    )


def _insert_markdown_banner(text: str, banner: str) -> str:
    if not banner:
        return text
    raw = str(text or '')
    lines = raw.splitlines()
    if lines and lines[0].startswith('#'):
        rest = '\n'.join(lines[1:]).lstrip('\n')
        return lines[0] + '\n\n' + banner.rstrip() + '\n\n' + rest + ('\n' if raw.endswith('\n') else '')
    return banner.rstrip() + '\n\n' + raw


def wrap_render_upload_center_md(fn: Callable[[dict[str, Any]], str]) -> Callable[[dict[str, Any]], str]:
    if getattr(fn, '_cbcc_v0674_listing_state_projection', False):
        return fn

    def rendered(center: dict[str, Any]) -> str:
        return _insert_markdown_banner(fn(center), _listing_state_banner_md(center))

    setattr(rendered, '_cbcc_v0674_listing_state_projection', True)
    return rendered


def wrap_build_project_hub_md(fn: Callable[[dict[str, Any]], str]) -> Callable[[dict[str, Any]], str]:
    if getattr(fn, '_cbcc_v0674_listing_state_projection', False):
        return fn

    def rendered(center: dict[str, Any]) -> str:
        return _insert_markdown_banner(fn(center), _listing_state_banner_md(center))

    setattr(rendered, '_cbcc_v0674_listing_state_projection', True)
    return rendered


def wrap_listing_workspace(fn: Callable[[dict[str, Any]], str]) -> Callable[[dict[str, Any]], str]:
    if getattr(fn, '_cbcc_v0674_listing_state_projection', False):
        return fn

    def rendered(center: dict[str, Any]) -> str:
        body = fn(center)
        state = center.get('canonical_listing_state')
        if not state:
            return body
        contract = center.get('listing_status_contract') if isinstance(center.get('listing_status_contract'), Mapping) else {}
        legacy = str(contract.get('legacy_status') or '—')
        reasons = ' · '.join(str(x) for x in (contract.get('reasons') or [])) or '—'
        banner = (
            f'<div class="panel listing-state-contract" data-listing-state="{html.escape(str(state), quote=True)}">'
            f'<div class="kicker">LISTING STATE</div><h2>{html.escape(str(state))}</h2>'
            f'<p><b>兼容旧状态：</b>{html.escape(legacy)}<br><b>判定依据：</b>{html.escape(reasons)}</p>'
            '<p>规范状态用于区分“策略可继续”“文案仍需复核”和“当前提交范围可发布”；旧 readiness / 字段状态仅保留兼容与追溯。</p>'
            '</div>'
        )
        return banner + body

    setattr(rendered, '_cbcc_v0674_listing_state_projection', True)
    return rendered


def _read_json_mapping(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _explicit_visible_locales(payload: Mapping[str, Any]) -> list[str]:
    obj = dict(payload or {})
    target: Mapping[str, Any] = {}
    for key in ('target', 'commerce_target', 'market_target'):
        if isinstance(obj.get(key), Mapping):
            target = obj.get(key)  # type: ignore[assignment]
            break
    if not target:
        target = obj
    language = target.get('language') if isinstance(target.get('language'), Mapping) else {}
    value = obj.get('visible_copy_locales') or target.get('visible_copy_locales') or language.get('visible_copy_locales')
    if value in (None, '', [], {}):
        return []
    if not isinstance(value, (list, tuple, set, frozenset)):
        value = [value]
    return list(dict.fromkeys(str(x).strip() for x in value if str(x or '').strip()))


def wrap_resolve_platform_scope(fn: Callable[[Path], dict[str, Any]]) -> Callable[[Path], dict[str, Any]]:
    """Carry explicit visible-copy locales with the same current-request precedence as primary locale."""
    if getattr(fn, '_cbcc_v0674_visible_locales', False):
        return fn

    def resolved(project: Path | str) -> dict[str, Any]:
        project_path = Path(project)
        scope = dict(fn(project_path) or {})
        request = _read_json_mapping(project_path / 'meta/request.json')
        request_visible = _explicit_visible_locales(request)
        visible: list[str] = []
        if request_visible:
            visible = request_visible
        elif str(scope.get('primary_locale_source') or '').upper() == 'EXPLICIT_TARGET_CONTEXT':
            target_context = _read_json_mapping(project_path / 'artifacts/target_context.json')
            visible = _explicit_visible_locales(target_context)
        if not visible and scope.get('primary_locale_status') == 'EXPLICIT' and scope.get('primary_locale'):
            visible = [str(scope.get('primary_locale'))]
        if scope.get('primary_locale_status') == 'UNSPECIFIED' and not request_visible:
            visible = []
        scope['visible_copy_locales'] = list(dict.fromkeys(visible))
        return scope

    setattr(resolved, '_cbcc_v0674_visible_locales', True)
    return resolved


def apply_explicit_target_scope(target: Mapping[str, Any], scope: Mapping[str, Any]) -> dict[str, Any]:
    out = deepcopy(dict(target or {}))
    # These fields belong to explicit platform/market scope.  UNSPECIFIED must clear stale generated
    # defaults rather than silently inherit a previous fixture or platform compilation.
    out['platform'] = scope.get('platform') if scope.get('platform_status') in {'EXPLICIT', 'UNSPECIFIED'} else out.get('platform')
    out['market'] = scope.get('market') if scope.get('market_status') in {'EXPLICIT', 'UNSPECIFIED'} else out.get('market')
    out['site'] = scope.get('site') if scope.get('site') is not None or scope.get('platform_status') in {'EXPLICIT', 'UNSPECIFIED'} else out.get('site')
    out['locale'] = scope.get('primary_locale') if scope.get('primary_locale_status') in {'EXPLICIT', 'UNSPECIFIED'} else out.get('locale')
    out['platform_status'] = scope.get('platform_status')
    out['market_status'] = scope.get('market_status')
    out['primary_locale_status'] = scope.get('primary_locale_status')
    if scope.get('visible_copy_locales') is not None:
        raw_locales = scope.get('visible_copy_locales') or []
        if not isinstance(raw_locales, (list, tuple, set, frozenset)):
            raw_locales = [raw_locales]
        out['visible_copy_locales'] = [str(x) for x in raw_locales if str(x or '').strip()]
    elif scope.get('primary_locale_status') == 'EXPLICIT':
        # A current explicit locale must not leave a previous market's visible-copy locale set behind.
        out['visible_copy_locales'] = [scope.get('primary_locale')] if scope.get('primary_locale') else []
    elif scope.get('primary_locale_status') == 'UNSPECIFIED':
        out['visible_copy_locales'] = []
    return out


def wrap_target_summary(fn: Callable[[Path], dict[str, Any]], resolve_platform_scope: Callable[[Path], dict[str, Any]]) -> Callable[[Path], dict[str, Any]]:
    if getattr(fn, '_cbcc_v0674_explicit_scope', False):
        return fn

    def summarized(project: Path) -> dict[str, Any]:
        base = fn(project)
        return apply_explicit_target_scope(base, resolve_platform_scope(Path(project)))

    setattr(summarized, '_cbcc_v0674_explicit_scope', True)
    return summarized


def prompt_provenance_leaks(prompt: str) -> list[dict[str, Any]]:
    issues = []
    for match in _PROVENANCE_RE.finditer(str(prompt or '')):
        issues.append({'code': 'PROVENANCE_METADATA', 'match': match.group(0)[:240]})
    return issues


def _strip_provenance_assignments(clause: str) -> str:
    """Remove machine metadata assignments, not the visual instruction sharing their clause."""
    out = _PROVENANCE_ASSIGNMENT_RE.sub('', str(clause or ''))
    out = _CN_PROVENANCE_ASSIGNMENT_RE.sub('', out)
    return re.sub(r'^[\s,，:：-]+|[\s,，]+$', '', out).strip()


def strip_prompt_provenance_metadata(prompt: str) -> str:
    """Remove provenance metadata while preserving every surviving pixel/frame-changing clause."""
    rows: list[str] = []
    for raw in str(prompt or '').replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        if not raw.strip():
            continue
        clauses = re.split(r'(?<=[。!?；;])\s*', raw.strip())
        kept: list[str] = []
        for clause in clauses:
            c = clause.strip()
            if not c:
                continue
            if _PROVENANCE_RE.search(c):
                c = _strip_provenance_assignments(c)
            if c and not _PROVENANCE_RE.search(c):
                kept.append(c)
        if kept:
            rows.append(' '.join(kept))
    return '\n'.join(rows).strip() + ('\n' if rows else '')


def _augment_prompt_membrane(module: Any) -> None:
    if getattr(module, '_cbcc_v0674_provenance_patch', False):
        return
    old_sanitize = module.sanitize_model_prompt
    old_leaks = module.model_prompt_orchestration_leaks

    def sanitize(prompt: str, *args: Any, **kwargs: Any) -> str:
        return strip_prompt_provenance_metadata(old_sanitize(prompt, *args, **kwargs))

    def leaks(prompt: str) -> list[dict[str, Any]]:
        return list(old_leaks(prompt)) + prompt_provenance_leaks(prompt)

    module.sanitize_model_prompt = sanitize
    module.model_prompt_orchestration_leaks = leaks
    module._cbcc_v0674_provenance_patch = True


def materialize_source_ledger(package_dir: Path | str, result: Mapping[str, Any]) -> dict[str, Any]:
    package = Path(package_dir)
    root = package / 'sources'
    root.mkdir(parents=True, exist_ok=True)
    items = [deepcopy(dict(x)) for x in (result.get('items') or []) if isinstance(x, Mapping)]
    counts = Counter(str(x.get('status') or 'UNKNOWN') for x in items)
    ledger = {
        'schema_version': 'cbcc-source-ledger-v0.6.74',
        'status': str(result.get('status') or 'UNKNOWN'),
        'counts': dict(sorted(counts.items())),
        'items': items,
        'principle': 'Every declared/carryable product-truth source remains visible as copied, missing, or unresolved; the Human Sources workspace may not imply availability from a filename alone.',
    }
    (root / 'SOURCE_LEDGER.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# 来源台账', '', f"状态：**{ledger['status']}**", '', '| 状态 | 包内路径 | 原始来源 | Bytes / SHA256 |', '|---|---|---|---|']
    if not items:
        lines.append('| NO_SOURCE_DECLARED | — | 当前没有声明可携带真源 | — |')
    for row in items:
        source = str(row.get('source_path') or '—').replace('|', '\\|')
        packaged = str(row.get('package_path') or '—').replace('|', '\\|')
        meta = f"{row.get('bytes', '—')} / {str(row.get('sha256') or '—')[:16]}"
        lines.append(f"| {row.get('status') or 'UNKNOWN'} | {packaged} | {source} | {meta} |")
    lines += ['', '> 该台账只陈述真实来源可用性，不以占位图、文件名或历史平台默认值伪装为已加载真源。', '']
    (root / 'SOURCE_LEDGER.md').write_text('\n'.join(lines), encoding='utf-8')
    return ledger


def wrap_materialize_source_truth_media(fn: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    if getattr(fn, '_cbcc_v0674_source_ledger', False):
        return fn

    def materialized(project_dir: Path | str, package_dir: Path | str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        result = dict(fn(project_dir, package_dir, *args, **kwargs) or {})
        ledger = materialize_source_ledger(package_dir, result)
        result['source_ledger'] = {'status': ledger['status'], 'json': 'sources/SOURCE_LEDGER.json', 'human': 'sources/SOURCE_LEDGER.md'}
        audit = Path(package_dir) / 'SOURCE_TRUTH_MEDIA_AUDIT.json'
        if audit.exists():
            audit.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return result

    setattr(materialized, '_cbcc_v0674_source_ledger', True)
    return materialized


def _augment_strategy_source_aliases(module: Any) -> None:
    if getattr(module, '_cbcc_v0674_alias_patch', False):
        return
    old = module._active_domains

    def active(request: dict[str, Any]) -> set[str]:
        req = deepcopy(request or {})
        target = deepcopy(req.get('target') if isinstance(req.get('target'), Mapping) else {})
        aliases = {
            'platform_family': ('platform_family', 'platform'),
            'market': ('market', 'country', 'region'),
            'site': ('site', 'site_id'),
            'primary_locale': ('primary_locale', 'locale'),
            'category': ('category', 'category_name', 'category_path'),
        }
        for dest, keys in aliases.items():
            if target.get(dest) not in (None, '', [], {}):
                continue
            for key in keys:
                if req.get(key) not in (None, '', [], {}):
                    target[dest] = req[key]
                    break
        req['target'] = target
        return old(req)

    module._active_domains = active
    module._cbcc_v0674_alias_patch = True


def apply_v0674_patches() -> dict[str, Any]:
    """Install v0.6.74 after the complete v0.6.73 bootstrap. Safe to call repeatedly."""
    from . import delivery_contract
    from . import full_delivery_depth_v3
    from . import delivery_html
    from . import human_delivery
    from . import platform_scope
    from . import delivery_export
    from . import source_truth_media
    from . import asset_compiler
    from . import model_prompt_semantic_membrane
    from . import strategy_sources

    if getattr(delivery_contract, '_cbcc_v0674_installed', False):
        return {'status': 'ALREADY_INSTALLED', 'version': VERSION}

    delivery_contract._full_mode = is_full_strategy
    full_delivery_depth_v3._full = is_full_strategy
    # delivery_export imported the validator before the bootstrap replaced it; refresh the cached
    # symbol so export uses the final strict validator with the v0.6.74 FULL alias semantics.
    delivery_export.validate_strategy_delivery = delivery_contract.validate_strategy_delivery

    delivery_html.markdown_to_html = wrap_markdown_to_html(delivery_html.markdown_to_html)

    platform_scope.resolve_platform_scope = wrap_resolve_platform_scope(platform_scope.resolve_platform_scope)
    human_delivery._target_summary = wrap_target_summary(human_delivery._target_summary, platform_scope.resolve_platform_scope)
    human_delivery.compile_upload_center = wrap_compile_upload_center(human_delivery.compile_upload_center)
    human_delivery.render_upload_center_md = wrap_render_upload_center_md(human_delivery.render_upload_center_md)
    human_delivery.build_project_hub_md = wrap_build_project_hub_md(human_delivery.build_project_hub_md)
    delivery_export.compile_upload_center = human_delivery.compile_upload_center
    # delivery_export cached these Human renderers at import time; refresh them so final package Markdown
    # projects the canonical Listing state rather than only the legacy readiness string.
    delivery_export.render_upload_center_md = human_delivery.render_upload_center_md
    delivery_export.build_project_hub_md = human_delivery.build_project_hub_md
    # delivery_workspace calls delivery_html.build_delivery_html, whose global _listing_workspace is
    # resolved at runtime. Patching this final consumer projects the same canonical state into index.html.
    delivery_html._listing_workspace = wrap_listing_workspace(delivery_html._listing_workspace)

    source_truth_media.materialize_source_truth_media = wrap_materialize_source_truth_media(source_truth_media.materialize_source_truth_media)
    delivery_export.materialize_source_truth_media = source_truth_media.materialize_source_truth_media

    if not isinstance(asset_compiler.yaml, _YamlNoAliasProxy):
        asset_compiler.yaml = _YamlNoAliasProxy(asset_compiler.yaml)

    _augment_prompt_membrane(model_prompt_semantic_membrane)
    _augment_strategy_source_aliases(strategy_sources)

    delivery_contract._cbcc_v0674_installed = True
    return {
        'status': 'INSTALLED',
        'version': VERSION,
        'closures': [
            'FULL_ALIAS', 'EXPLICIT_PLATFORM_MARKET_LOCALE_SCOPE', 'LISTING_THREE_STATE',
            'MARKDOWN_ESCAPED_PIPE', 'YAML_NO_ALIAS_ANCHORS', 'SOURCE_LEDGER',
            'MODEL_PROMPT_PROVENANCE_MEMBRANE', 'TOP_LEVEL_TARGET_ALIAS_ACTIVATION',
        ],
    }
