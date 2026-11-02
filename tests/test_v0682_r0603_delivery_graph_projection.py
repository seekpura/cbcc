from pathlib import Path
import json

from runtime.cbcc import delivery_export


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_final_delivery_preserves_canonical_commerce_graph_lineage(monkeypatch, tmp_path: Path):
    project = tmp_path / "project"
    strategy_dir = project / "artifacts/strategy"
    strategy_dir.mkdir(parents=True)
    (strategy_dir / "MASTER_STRATEGY_CN.md").write_text("# strategy\n", encoding="utf-8")
    _write_json(strategy_dir / "strategy_authority.json", {"status": "READY"})

    graph = {
        "schema": "cbcc-canonical-commerce-graph-v1",
        "status": "CANONICAL_GRAPH_READY",
        "graph_sha256": "r0603-final-delivery-graph-sentinel",
        "projection_surfaces": [{"surface": "JSON", "role": "CANONICAL_AUTHORITY"}],
    }
    graph_path = project / "artifacts/canonical_commerce_graph.json"
    _write_json(graph_path, graph)
    original_bytes = graph_path.read_bytes()

    monkeypatch.setattr(delivery_export, "validate_strategy_delivery", lambda _: {"mode": "TASK_SCOPED", "status": "PASS"})
    monkeypatch.setattr(delivery_export, "materialize_source_truth_media", lambda project, package: {"status": "PASS", "copied_count": 0})
    monkeypatch.setattr(delivery_export, "resolve_platform_scope", lambda _: {"platform_status": "EXPLICIT", "market_status": "EXPLICIT", "primary_locale_status": "EXPLICIT", "platform": "TEST", "market": "TEST", "site": "TEST", "primary_locale": "en-US"})
    monkeypatch.setattr(delivery_export, "build_language_delivery_plan", lambda _: {"status": "PASS"})
    monkeypatch.setattr(delivery_export, "compile_upload_center", lambda _: {"task_scope": {"listing_active": False}, "copy_center": [], "localized_copy": [], "target": {}})
    monkeypatch.setattr(delivery_export, "normalize_upload_center", lambda x: x)
    monkeypatch.setattr(delivery_export, "normalize_global_chinese_interpretation", lambda x: x)
    monkeypatch.setattr(delivery_export, "audit_language_delivery", lambda center, plan: {"status": "PASS", "missing": []})
    monkeypatch.setattr(delivery_export, "render_upload_center_md_with_global_cn", lambda center, renderer: "# listing\n")
    monkeypatch.setattr(delivery_export, "build_project_hub_md", lambda center: "# hub\n")

    def _html(package, output, title=None):
        output.write_text("<html><body>中文释义</body></html>", encoding="utf-8")
        return output

    monkeypatch.setattr(delivery_export, "build_delivery_html", _html)
    monkeypatch.setattr(delivery_export, "apply_chinese_interpretation_ui", lambda x: x)
    monkeypatch.setattr(delivery_export, "apply_commercial_workspace_shell", lambda html, scope, plan: html)
    monkeypatch.setattr(delivery_export, "audit_final_chinese_interpretation", lambda package, center: {"status": "PASS", "global_human_content": {"final_status": "PASS"}, "listing": {"status": "PASS"}, "assets": {"status": "PASS"}})

    output = tmp_path / "delivery"
    manifest = delivery_export.export_delivery_package(project, output)
    copied = output / "supporting_analysis/canonical_commerce_graph.json"

    assert manifest["status"] == "DELIVERY_READY"
    assert copied.exists(), "final delivery dropped the canonical commerce graph lineage"
    assert copied.read_bytes() == original_bytes
    assert json.loads(copied.read_text(encoding="utf-8"))["graph_sha256"] == graph["graph_sha256"]
