from __future__ import annotations

"""Phase 6 delivery-family lenses for REQ-070 / REQ-076 / REQ-077.

The family lenses are derived only from canonical asset objects that actually exist.  They are inserted
inside an existing project-authored route and never become a permanent capability menu.
"""

from pathlib import Path
from typing import Any, Mapping
import html
import json
import re

from .canonical_full_parity_v0671 import DATA_FILE

AUDIT_FILE = "DELIVERY_FAMILY_WORKSPACE_AUDIT.json"
MARKER = "CBCC_DELIVERY_FAMILY_WORKSPACE_V0680"

FAMILIES = {
    "longform": {
        "requirement_id": "REQ-070",
        "title": "A+ / PDP / Longform / Specification / Source-document",
        "tokens": {"A_PLUS", "PDP", "LONGFORM", "SPECIFICATION", "SOURCE_DOCUMENT", "FAQ", "COMPARISON"},
    },
    "store_landing": {
        "requirement_id": "REQ-076",
        "title": "Store / Banner / Landing / Campaign / Seasonal",
        "tokens": {"STORE", "STORE_BANNER", "BANNER", "LANDING", "LANDING_PAGE", "LANDING_PAGE_HERO", "CAMPAIGN", "SEASONAL"},
    },
    "crm": {
        "requirement_id": "REQ-077",
        "title": "CRM / Lifecycle / Post-purchase",
        "tokens": {"CRM", "EMAIL", "SMS", "LIFECYCLE", "POST_PURCHASE", "POST-PURCHASE", "RETENTION"},
    },
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _norm(value: Any) -> str:
    return str(value or "").strip().upper().replace(" ", "_")


def _identity(asset: Mapping[str, Any], index: int) -> str:
    manifest = asset.get("manifest") if isinstance(asset.get("manifest"), Mapping) else {}
    card = asset.get("card") if isinstance(asset.get("card"), Mapping) else {}
    return str(asset.get("asset_id") or asset.get("id") or manifest.get("asset_id") or card.get("asset_id") or f"asset-{index+1}")


def _classification_tokens(asset: Mapping[str, Any]) -> set[str]:
    manifest = asset.get("manifest") if isinstance(asset.get("manifest"), Mapping) else {}
    card = asset.get("card") if isinstance(asset.get("card"), Mapping) else {}
    prompt = asset.get("prompt_contract") if isinstance(asset.get("prompt_contract"), Mapping) else {}
    tokens: set[str] = set()
    for source in (asset, manifest, card, prompt):
        for key in ("surface", "family", "asset_family", "portfolio_family", "asset_type", "surface_role", "deployment_state"):
            value = source.get(key) if isinstance(source, Mapping) else None
            if value not in (None, ""):
                tokens.add(_norm(value))
    return tokens


def _family_for(asset: Mapping[str, Any]) -> str | None:
    tokens = _classification_tokens(asset)
    for family, spec in FAMILIES.items():
        if tokens.intersection(spec["tokens"]):
            return family
    return None


def extract_delivery_family_objects(payload: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    business = payload.get("canonical_business_objects") if isinstance(payload.get("canonical_business_objects"), Mapping) else {}
    assets = business.get("assets") if isinstance(business.get("assets"), list) else payload.get("assets")
    assets = assets if isinstance(assets, list) else []
    out: dict[str, list[dict[str, Any]]] = {}
    for i, raw in enumerate(assets):
        if not isinstance(raw, Mapping):
            continue
        family = _family_for(raw)
        if not family:
            continue
        row = dict(raw)
        row["_delivery_family_object_id"] = _identity(raw, i)
        out.setdefault(family, []).append(row)
    return out


def _route_spans(page: str) -> dict[str, tuple[int, int]]:
    starts = list(re.finditer(r'<section class="page(?: [^"]*)?" data-route="([^"]+)">', page))
    out: dict[str, tuple[int, int]] = {}
    for i, match in enumerate(starts):
        out.setdefault(match.group(1), (match.start(), starts[i + 1].start() if i + 1 < len(starts) else len(page)))
    return out


def _insert(page: str, route: str, fragment: str) -> tuple[str, bool]:
    span = _route_spans(page).get(route)
    if not span:
        return page, False
    block = page[span[0]:span[1]]
    close = block.rfind("</section>")
    pos = span[0] + close if close >= 0 else span[1]
    return page[:pos] + fragment + page[pos:], True


def _choose_route(page: str) -> str | None:
    routes = set(_route_spans(page))
    for candidate in ("assets", "content", "overview"):
        if candidate in routes:
            return candidate
    return None


def _panel(family: str, objects: list[dict[str, Any]]) -> str:
    spec = FAMILIES[family]
    cards = []
    for row in objects:
        oid = str(row["_delivery_family_object_id"])
        public = {k: v for k, v in row.items() if not k.startswith("_delivery_family_")}
        body = html.escape(json.dumps(public, ensure_ascii=False, indent=2, default=str))
        cards.append(
            f'<details class="cbcc-delivery-family-object-v0680 searchable" data-delivery-family-object="{html.escape(oid, quote=True)}">'
            f'<summary><b>{html.escape(oid)}</b></summary><pre>{body}</pre></details>'
        )
    return (
        f'<section class="panel cbcc-delivery-family-v0680" data-delivery-family="{family}" '
        f'data-requirement-id="{spec["requirement_id"]}">'
        f'<h2>{html.escape(spec["title"])}</h2>'
        '<p>仅在当前项目存在对应 canonical 资产对象时出现；这是交付 lens，不是固定能力菜单。</p>'
        + "".join(cards)
        + "</section>"
    )


def audit_delivery_family_workspace(package_dir: Path | str) -> list[dict[str, Any]]:
    package = Path(package_dir)
    payload = _read_json(package / DATA_FILE)
    html_path = package / "index.html"
    if not payload:
        return [{"code": "CANONICAL_JSON_MISSING_OR_INVALID", "path": DATA_FILE}]
    if not html_path.exists():
        return [{"code": "CANONICAL_HTML_MISSING", "path": "index.html"}]
    page = html_path.read_text(encoding="utf-8", errors="ignore")
    extracted = extract_delivery_family_objects(payload)
    issues: list[dict[str, Any]] = []
    for family, rows in extracted.items():
        family_marker = f'data-delivery-family="{family}"'
        if family_marker not in page:
            issues.append({"code": "DELIVERY_FAMILY_ROUTE_MISSING_V0680", "family": family})
            continue
        for row in rows:
            oid = str(row["_delivery_family_object_id"])
            marker = f'data-delivery-family-object="{html.escape(oid, quote=True)}"'
            if marker not in page:
                issues.append({"code": "DELIVERY_FAMILY_ROUTED_OBJECT_MISSING_V0680", "family": family, "object_id": oid})
    # A family absent from canonical objects must not be rendered as a fixed capability menu.
    for family in FAMILIES:
        if family not in extracted and f'data-delivery-family="{family}"' in page:
            issues.append({"code": "DELIVERY_FAMILY_FIXED_MENU_FALSE_POSITIVE_V0680", "family": family})
    return issues


def materialize_delivery_family_workspace(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    payload = _read_json(package / DATA_FILE)
    html_path = package / "index.html"
    if not payload or not html_path.exists():
        issues = audit_delivery_family_workspace(package)
        result = {"status": "INCOMPLETE", "families": {}, "issues": issues}
        _write_json(package / AUDIT_FILE, result)
        return result

    page = html_path.read_text(encoding="utf-8", errors="ignore")
    extracted = extract_delivery_family_objects(payload)
    if MARKER not in page:
        route = _choose_route(page)
        if route:
            for family, rows in extracted.items():
                page, _ = _insert(page, route, _panel(family, rows))
        marker = f'\n<div id="cbcc-delivery-family-workspace-v0680" data-contract="{MARKER}" hidden></div>\n'
        page = page.replace("</body>", marker + "</body>", 1) if "</body>" in page else page + marker
        html_path.write_text(page, encoding="utf-8")

    issues = audit_delivery_family_workspace(package)
    families = {
        family: {
            "status": "PASS" if not any(x.get("family") == family for x in issues) else "INCOMPLETE",
            "requirement_id": FAMILIES[family]["requirement_id"],
            "title": FAMILIES[family]["title"],
            "object_count": len(rows),
        }
        for family, rows in extracted.items()
    }
    result = {
        "status": "PASS" if not issues else "INCOMPLETE",
        "contract": "PHASE6_ACTIVATED_DELIVERY_FAMILY_DYNAMIC_HUMAN_WORKSPACE",
        "fixed_family_menu": False,
        "families": families,
        "issues": issues,
    }
    _write_json(package / AUDIT_FILE, result)
    return result
