from __future__ import annotations

"""Phase 6 canonical JSON / Markdown / HTML delivery projection.

v0.6.71 remains the canonical payload builder and lossless static HTML projection authority.  Phase 6
reuses that authority, materializes a complete Markdown projection from the exact JSON bytes, records a
stable signature, and requires the same canonical business objects to have real routed Human Workspace
consumers before the final ZIP is rebuilt.
"""

from pathlib import Path
from typing import Any, Mapping
import hashlib
import html
import json
import re
import zipfile

from .canonical_full_parity_v0671 import (
    DATA_FILE,
    audit_generic_human_field_coverage,
    finalize_static_human_projection,
)

MARKDOWN_FILE = "CANONICAL_HUMAN_DATA.md"
AUDIT_FILE = "CANONICAL_DELIVERY_PARITY_AUDIT.json"
MARKDOWN_MARKER = "CBCC_CANONICAL_MARKDOWN_PROJECTION_V0680"
HTML_MARKER = "CBCC_CANONICAL_DELIVERY_PARITY_V0680"


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


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_signature(payload: Mapping[str, Any]) -> str:
    """Stable semantic signature independent of pretty-print whitespace or key insertion order."""
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _render_markdown(payload: Mapping[str, Any], signature: str) -> str:
    canonical_json = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str)
    business = payload.get("canonical_business_objects")
    object_names = sorted(str(k) for k in business) if isinstance(business, Mapping) else []
    index = "\n".join(f"- `{name}`" for name in object_names) or "- （当前包无 active canonical business object）"
    return (
        f"<!-- {MARKDOWN_MARKER} -->\n"
        f"<!-- canonical-signature: {signature} -->\n"
        "# Canonical Human Data｜规范业务对象完整投影\n\n"
        "本文件与 `CANONICAL_HUMAN_DATA.json`、`index.html` 使用同一个 canonical payload。"
        "下方 JSON 区块是无损 Markdown 投影，不重新解释、不裁剪字段。\n\n"
        "## Canonical Business Objects｜业务对象索引\n\n"
        f"{index}\n\n"
        "## Lossless Canonical Payload｜无损规范数据\n\n"
        "```json\n"
        f"{canonical_json}\n"
        "```\n"
    )


def _extract_markdown_payload(text: str) -> dict[str, Any]:
    match = re.search(
        r"## Lossless Canonical Payload｜无损规范数据\s*\n\s*```json\s*\n(.*?)\n```",
        text,
        re.S,
    )
    if not match:
        return {}
    try:
        value = json.loads(match.group(1))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _apply_html_signature(html_path: Path, signature: str) -> None:
    page = html_path.read_text(encoding="utf-8", errors="ignore")
    page = re.sub(
        r"\s*<div id=\"cbcc-canonical-delivery-parity-v0680\"[^>]*>.*?</div>\s*",
        "\n",
        page,
        flags=re.S,
    )
    badge = (
        f'\n<div id="cbcc-canonical-delivery-parity-v0680" '
        f'data-canonical-signature="{html.escape(signature, quote=True)}" '
        'style="display:none" aria-hidden="true">'
        f"{HTML_MARKER}</div>\n"
    )
    page = page.replace("</body>", badge + "</body>", 1) if "</body>" in page else page + badge
    html_path.write_text(page, encoding="utf-8")


def audit_canonical_delivery_parity(package_dir: Path | str) -> list[dict[str, Any]]:
    package = Path(package_dir)
    json_path = package / DATA_FILE
    md_path = package / MARKDOWN_FILE
    html_path = package / "index.html"
    payload = _read_json(json_path)
    issues: list[dict[str, Any]] = []

    if not payload:
        return [{"code": "CANONICAL_JSON_MISSING_OR_INVALID", "path": DATA_FILE}]

    signature = canonical_signature(payload)
    if not md_path.exists():
        issues.append({"code": "CANONICAL_MARKDOWN_MISSING", "path": MARKDOWN_FILE})
    else:
        md = md_path.read_text(encoding="utf-8", errors="ignore")
        if MARKDOWN_MARKER not in md or f"canonical-signature: {signature}" not in md:
            issues.append({"code": "MARKDOWN_CANONICAL_SIGNATURE_DRIFT", "path": MARKDOWN_FILE})
        markdown_payload = _extract_markdown_payload(md)
        if markdown_payload != payload:
            issues.append({"code": "MARKDOWN_CANONICAL_FIELD_DRIFT", "path": MARKDOWN_FILE})

    if not html_path.exists():
        issues.append({"code": "CANONICAL_HTML_MISSING", "path": "index.html"})
    else:
        html_text = html_path.read_text(encoding="utf-8", errors="ignore")
        if HTML_MARKER not in html_text or f'data-canonical-signature="{signature}"' not in html_text:
            issues.append({"code": "HTML_CANONICAL_SIGNATURE_DRIFT", "path": "index.html"})
        issues.extend(audit_generic_human_field_coverage(payload, html_text))

    return issues


def materialize_canonical_delivery_parity(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    prior = finalize_static_human_projection(package)
    if prior.get("status") != "PASS":
        result = {
            "status": "INCOMPLETE",
            "canonical_signature_sha256": None,
            "issues": list(prior.get("issues") or []) or [{"code": "V0671_CANONICAL_HTML_PROJECTION_INCOMPLETE"}],
            "upstream_projection": prior,
        }
        _write_json(package / AUDIT_FILE, result)
        return result

    payload = _read_json(package / DATA_FILE)
    if not payload:
        result = {
            "status": "INCOMPLETE",
            "canonical_signature_sha256": None,
            "issues": [{"code": "CANONICAL_JSON_MISSING_OR_INVALID", "path": DATA_FILE}],
            "upstream_projection": prior,
        }
        _write_json(package / AUDIT_FILE, result)
        return result

    signature = canonical_signature(payload)
    (package / MARKDOWN_FILE).write_text(_render_markdown(payload, signature), encoding="utf-8")
    _apply_html_signature(package / "index.html", signature)
    issues = audit_canonical_delivery_parity(package)
    result = {
        "status": "PASS" if not issues else "INCOMPLETE",
        "contract": "REQ-061_CANONICAL_JSON_MARKDOWN_HTML_SAME_SOURCE_PROJECTION",
        "canonical_signature_sha256": signature,
        "canonical_payload_source": DATA_FILE,
        "artifacts": {
            "json": DATA_FILE,
            "markdown": MARKDOWN_FILE,
            "html": "index.html",
        },
        "issues": issues,
        "upstream_projection": prior,
    }
    _write_json(package / AUDIT_FILE, result)
    return result


def _rebuild_export_zip(package: Path, zip_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    manifest_path = package / "DELIVERY_MANIFEST.json"
    files = []
    for f in sorted(package.rglob("*")):
        if f.is_file() and f.name != "DELIVERY_MANIFEST.json":
            files.append(
                {
                    "path": str(f.relative_to(package)).replace("\\", "/"),
                    "sha256": _sha256_file(f),
                    "bytes": f.stat().st_size,
                }
            )
    manifest["files"] = files
    manifest.pop("zip_sha256", None)
    manifest.pop("zip_bytes", None)
    _write_json(manifest_path, manifest)

    # Preserve the repository's established two-pass manifest/ZIP convention: the disk manifest
    # records the hash of the final ZIP while the ZIP contains the prior-pass manifest bytes.
    for _ in range(2):
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(package.rglob("*")):
                if f.is_file():
                    zf.write(f, Path(package.name) / f.relative_to(package))
        manifest["zip_sha256"] = _sha256_file(zip_path)
        manifest["zip_bytes"] = zip_path.stat().st_size
        _write_json(manifest_path, manifest)
    return manifest


def finalize_export_canonical_delivery_parity(export_manifest: Mapping[str, Any]) -> dict[str, Any]:
    manifest = dict(export_manifest or {})
    package_raw = str(manifest.get("package_dir") or "").strip()
    if not package_raw:
        raise FileNotFoundError("Delivery package missing for Phase 6 parity: package_dir is empty")
    package = Path(package_raw)
    zip_raw = str(manifest.get("zip_path") or "").strip()
    zip_path = Path(zip_raw) if zip_raw else package.with_suffix(".zip")
    if not package.exists():
        raise FileNotFoundError(f"Delivery package missing for Phase 6 parity: {package}")

    result = materialize_canonical_delivery_parity(package)
    if result.get("status") != "PASS":
        raise RuntimeError(
            "BLOCKED REQ-061 canonical JSON/Markdown/HTML parity failed: "
            + json.dumps(result.get("issues") or [], ensure_ascii=False)
        )

    # REQ-089 is stricter than whole-page field presence: the same canonical objects must be consumed
    # inside the project-authored Human Workspace routes.  The generic Archive remains secondary only.
    from .canonical_routed_workspace_v0680 import AUDIT_FILE as ROUTED_AUDIT_FILE
    from .canonical_routed_workspace_v0680 import materialize_routed_canonical_workspace

    routed = materialize_routed_canonical_workspace(package)
    if routed.get("status") != "PASS":
        raise RuntimeError(
            "BLOCKED REQ-089 routed canonical Human Workspace projection failed: "
            + json.dumps(routed.get("issues") or [], ensure_ascii=False)
        )

    disk_manifest = _read_json(package / "DELIVERY_MANIFEST.json") or manifest
    disk_manifest.update(
        {
            "canonical_human_data_json": DATA_FILE,
            "canonical_human_data_markdown": MARKDOWN_FILE,
            "canonical_delivery_parity_audit": AUDIT_FILE,
            "canonical_delivery_parity_status": result.get("status"),
            "canonical_delivery_signature_sha256": result.get("canonical_signature_sha256"),
            "canonical_routed_workspace_audit": ROUTED_AUDIT_FILE,
            "canonical_routed_workspace_status": routed.get("status"),
        }
    )
    workspace = dict(disk_manifest.get("workspace_contract") or {})
    workspace["canonical_json_markdown_html_same_source_parity"] = result.get("status")
    workspace["canonical_delivery_signature_sha256"] = result.get("canonical_signature_sha256")
    workspace["full_canonical_routed_human_workspace"] = routed.get("status")
    workspace["archive_is_primary_canonical_consumer"] = False
    disk_manifest["workspace_contract"] = workspace

    return _rebuild_export_zip(package, zip_path, disk_manifest)
