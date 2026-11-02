from __future__ import annotations

"""REQ-089: route every human-relevant canonical business object into the Human Workspace.

The v0.6.71 archive proves complete HTML field presence, but archive presence is not a primary human
consumer.  This module projects the exact same canonical objects into the project-authored SaaS routes
that already exist.  It never creates a fixed capability menu: a preferred semantic route is used only
when the current project exposed that route; otherwise the object falls back to the always-human
`overview` route.  The archive remains a secondary trace surface and cannot satisfy this audit.
"""

from pathlib import Path
from typing import Any, Mapping
import html
import json
import re

from .canonical_full_parity_v0671 import DATA_FILE

AUDIT_FILE = "CANONICAL_ROUTED_WORKSPACE_AUDIT.json"
MARKER = "CBCC_CANONICAL_ROUTED_WORKSPACE_V0680"

ROUTE_CANDIDATES: dict[str, tuple[str, ...]] = {
    "human_delivery": ("overview",),
    "product_truth": ("product", "overview"),
    "target_context": ("market", "overview"),
    "culture_context": ("market", "overview"),
    "market_analysis": ("market", "overview"),
    "strategy_authority": ("strategy", "overview"),
    "compliance": ("risk", "overview"),
    "ads": ("content", "strategy", "overview"),
    "reviews": ("risk", "sources", "overview"),
    "sources": ("sources", "overview"),
    "asset_universe": ("assets", "visual", "overview"),
    "assets": ("assets", "prompts", "overview"),
}

OBJECT_TITLES = {
    "human_delivery": "交付工作台完整对象",
    "product_truth": "产品事实完整对象",
    "target_context": "目标市场 / 人群完整对象",
    "culture_context": "文化语境完整对象",
    "market_analysis": "市场研究完整对象",
    "strategy_authority": "策略权威完整对象",
    "compliance": "合规 / 风险完整对象",
    "ads": "广告优化完整对象",
    "reviews": "评论 / 客服 / 退货完整对象",
    "sources": "来源 / 证据完整对象",
    "asset_universe": "资产宇宙完整对象",
    "assets": "逐资产生产对象",
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _present(value: Any) -> bool:
    return value not in (None, "", [], {})


def _primitive(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


def _leaf_paths(value: Any, path: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            rows.extend(_leaf_paths(child, child_path))
        return rows
    if isinstance(value, list):
        for i, child in enumerate(value):
            rows.extend(_leaf_paths(child, f"{path}[{i}]"))
        return rows
    if _present(value):
        rows.append((path, _primitive(value)))
    return rows


def _routed_leaf_html(value: Any, path: str) -> str:
    if isinstance(value, Mapping):
        body = "".join(_routed_leaf_html(v, f"{path}.{k}" if path else str(k)) for k, v in value.items())
        if not body:
            return ""
        return (
            '<details class="cbcc-routed-node-v0680">'
            f"<summary>{html.escape(path or 'object')}</summary>{body}</details>"
        )
    if isinstance(value, list):
        body = "".join(_routed_leaf_html(v, f"{path}[{i}]") for i, v in enumerate(value))
        if not body:
            return ""
        return (
            '<details class="cbcc-routed-node-v0680">'
            f"<summary>{html.escape(path)} · {len(value)}</summary>{body}</details>"
        )
    if not _present(value):
        return ""
    text = _primitive(value)
    ep = html.escape(path, quote=True)
    ev = html.escape(text)
    ea = html.escape(text, quote=True)
    return (
        f'<div class="cbcc-routed-leaf-v0680 searchable" data-canonical-routed-path="{ep}">'
        f'<div><code>{ep}</code><button type="button" class="cbcc-copy-v0671" '
        f'data-copy-value="{ea}">复制</button></div><pre>{ev}</pre></div>'
    )


def _route_spans(page: str) -> dict[str, tuple[int, int]]:
    starts = list(re.finditer(r'<section class="page(?: [^"]*)?" data-route="([^"]+)">', page))
    spans: dict[str, tuple[int, int]] = {}
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(page)
        spans.setdefault(match.group(1), (match.start(), end))
    return spans


def _route_block(page: str, route: str) -> str:
    span = _route_spans(page).get(route)
    return page[span[0] : span[1]] if span else ""


def _insert_route(page: str, route: str, fragment: str) -> tuple[str, bool]:
    spans = _route_spans(page)
    span = spans.get(route)
    if not span:
        return page, False
    block = page[span[0] : span[1]]
    close = block.rfind("</section>")
    if close < 0:
        return page[: span[1]] + fragment + page[span[1] :], True
    pos = span[0] + close
    return page[:pos] + fragment + page[pos:], True


def _choose_route(page: str, object_id: str) -> str | None:
    existing = set(_route_spans(page))
    for route in ROUTE_CANDIDATES.get(object_id, ("overview",)):
        if route in existing:
            return route
    return "overview" if "overview" in existing else None


def _panel(object_id: str, value: Any) -> str:
    title = OBJECT_TITLES.get(object_id, object_id)
    path = f"canonical_business_objects.{object_id}"
    return (
        f'<details class="panel cbcc-canonical-routed-v0680" data-canonical-routed-object="{html.escape(object_id, quote=True)}">'
        f'<summary><b>{html.escape(title)}</b><span> · Canonical Object Detail</span></summary>'
        '<p>该对象直接来自 Canonical JSON；当前工作区是主消费入口，Archive 仅用于次级追溯。</p>'
        f"{_routed_leaf_html(value, path)}</details>"
    )


def audit_routed_canonical_workspace(package_dir: Path | str) -> list[dict[str, Any]]:
    package = Path(package_dir)
    payload = _read_json(package / DATA_FILE)
    html_path = package / "index.html"
    if not payload:
        return [{"code": "CANONICAL_JSON_MISSING_OR_INVALID", "path": DATA_FILE}]
    if not html_path.exists():
        return [{"code": "CANONICAL_HTML_MISSING", "path": "index.html"}]

    page = html_path.read_text(encoding="utf-8", errors="ignore")
    business = payload.get("canonical_business_objects")
    business = business if isinstance(business, Mapping) else {}
    issues: list[dict[str, Any]] = []

    for object_id, value in business.items():
        if not _present(value):
            continue
        object_marker = f'data-canonical-routed-object="{html.escape(str(object_id), quote=True)}"'
        route = None
        for candidate in ROUTE_CANDIDATES.get(str(object_id), ("overview",)):
            block = _route_block(page, candidate)
            if object_marker in block:
                route = candidate
                break
        if route is None:
            # If a preferred route was not emitted by project-authored IA, overview is the permitted
            # dynamic fallback. Archive/sources does not count unless sources is an explicit candidate.
            block = _route_block(page, "overview")
            if object_marker in block:
                route = "overview"
        if route is None:
            issues.append(
                {
                    "code": "HTML_CANONICAL_OBJECT_HAS_NO_ROUTED_HUMAN_CONSUMER_V0680",
                    "object_id": object_id,
                }
            )
            continue

        block = _route_block(page, route)
        missing: list[str] = []
        for path, _ in _leaf_paths(value, f"canonical_business_objects.{object_id}"):
            marker = f'data-canonical-routed-path="{html.escape(path, quote=True)}"'
            if marker not in block:
                missing.append(path)
        if missing:
            issues.append(
                {
                    "code": "HTML_CANONICAL_ROUTED_FIELD_COVERAGE_INCOMPLETE_V0680",
                    "object_id": object_id,
                    "route": route,
                    "missing_count": len(missing),
                    "missing": missing[:100],
                }
            )
    return issues


def _object_audit_rows(payload: Mapping[str, Any], page: str) -> dict[str, Any]:
    business = payload.get("canonical_business_objects")
    business = business if isinstance(business, Mapping) else {}
    rows: dict[str, Any] = {}
    for object_id, value in business.items():
        if not _present(value):
            continue
        object_marker = f'data-canonical-routed-object="{html.escape(str(object_id), quote=True)}"'
        route = None
        for candidate in ROUTE_CANDIDATES.get(str(object_id), ("overview",)):
            if object_marker in _route_block(page, candidate):
                route = candidate
                break
        if route is None and object_marker in _route_block(page, "overview"):
            route = "overview"
        leaves = _leaf_paths(value, f"canonical_business_objects.{object_id}")
        block = _route_block(page, route) if route else ""
        missing = [
            path
            for path, _ in leaves
            if f'data-canonical-routed-path="{html.escape(path, quote=True)}"' not in block
        ]
        rows[str(object_id)] = {
            "status": "PASS" if route and not missing else "INCOMPLETE",
            "route": route,
            "preferred_routes": list(ROUTE_CANDIDATES.get(str(object_id), ("overview",))),
            "leaf_count": len(leaves),
            "missing_count": len(missing),
        }
    return rows


def materialize_routed_canonical_workspace(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    payload = _read_json(package / DATA_FILE)
    html_path = package / "index.html"
    if not payload or not html_path.exists():
        issues = []
        if not payload:
            issues.append({"code": "CANONICAL_JSON_MISSING_OR_INVALID", "path": DATA_FILE})
        if not html_path.exists():
            issues.append({"code": "CANONICAL_HTML_MISSING", "path": "index.html"})
        result = {"status": "INCOMPLETE", "objects": {}, "issues": issues}
        _write_json(package / AUDIT_FILE, result)
        return result

    page = html_path.read_text(encoding="utf-8", errors="ignore")
    business = payload.get("canonical_business_objects")
    business = business if isinstance(business, Mapping) else {}

    if MARKER not in page:
        for object_id, value in business.items():
            if not _present(value):
                continue
            route = _choose_route(page, str(object_id))
            if route is None:
                continue
            page, _ = _insert_route(page, route, _panel(str(object_id), value))
        marker = f'\n<div id="cbcc-canonical-routed-workspace-v0680" data-contract="{MARKER}" hidden></div>\n'
        page = page.replace("</body>", marker + "</body>", 1) if "</body>" in page else page + marker
        html_path.write_text(page, encoding="utf-8")

    final_page = html_path.read_text(encoding="utf-8", errors="ignore")
    issues = audit_routed_canonical_workspace(package)
    result = {
        "status": "PASS" if not issues else "INCOMPLETE",
        "contract": "REQ-089_HUMAN_WORKSPACE_FULL_CANONICAL_ROUTED_PROJECTION",
        "archive_is_primary_consumer": False,
        "objects": _object_audit_rows(payload, final_page),
        "issues": issues,
        "ux_contract": {
            "project_authored_ia": True,
            "semantic_route_preference_with_overview_fallback": True,
            "archive_secondary_only": True,
            "canonical_object_ids_stable": True,
        },
    }
    _write_json(package / AUDIT_FILE, result)
    return result
