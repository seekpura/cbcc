from __future__ import annotations

import json
from pathlib import Path


def _write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _center():
    return {
        "version": "0.6.71-test",
        "delivery_language": {"locale": "zh-CN"},
        "target": {"platform": "TikTok Shop", "site": "MY", "market": "Malaysia", "locale": "ms-MY", "delivery_locale": "zh-CN"},
        "product": {"brand": "KIYUU", "product_name": "K01"},
        "category": {"name": "Beauty", "status": "待查证"},
        "task_scope": {"listing_active": True, "listing_submission_sensitive": False, "families": ["LISTING", "GALLERY"]},
        "readiness": {"status": "READY_FOR_CURRENT_SCOPE", "pending_count": 0, "optional_gap_count": 0, "scope": "LISTING_CURRENT_TASK"},
        "copy_center": [
            {"group": "商品识别", "field": "title", "label": "产品标题", "value": "BM TITLE UNIQUE", "status": "READY", "required_for_current_scope": True, "copyable": True, "locale": "ms-MY", "delivery_translation": "中文标题唯一", "delivery_companion_status": "READY"},
            {"group": "购买决策", "field": "description", "label": "商品描述", "value": "BM DESCRIPTION UNIQUE", "status": "READY", "required_for_current_scope": True, "copyable": True, "locale": "ms-MY", "delivery_translation": "中文描述唯一", "delivery_companion_status": "READY"},
            {"group": "购买决策", "field": "bullets", "label": "卖点", "value": ["BM KP ONE", "BM KP TWO"], "status": "READY", "required_for_current_scope": True, "copyable": True, "locale": "ms-MY", "delivery_translation": ["中文卖点一", "中文卖点二"], "delivery_companion_status": "READY"},
            {"group": "事实 / 使用", "field": "attributes", "label": "属性", "value": {"Brand": "KIYUU", "Net Content": "30g"}, "status": "READY", "required_for_current_scope": True, "copyable": True, "locale": "ms-MY", "delivery_translation": "品牌与净含量", "delivery_companion_status": "READY"},
            {"group": "事实 / 使用", "field": "package", "label": "包装/包含物", "value": "1 tube", "status": "READY", "required_for_current_scope": True, "copyable": True, "locale": "ms-MY", "delivery_translation": "1支", "delivery_companion_status": "READY"},
            {"group": "购买决策", "field": "faq", "label": "FAQ", "value": [{"q": "BM FAQ Q", "a": "BM FAQ A"}], "status": "READY", "required_for_current_scope": False, "copyable": True, "locale": "ms-MY", "delivery_translation": "FAQ 中文释义", "delivery_companion_status": "READY"},
        ],
        "localized_copy": [
            {"locale": "en-MY", "field": "title", "value": "EN TITLE UNIQUE", "delivery_translation": "中文标题唯一"},
            {"locale": "en-MY", "field": "description", "value": "EN DESCRIPTION UNIQUE", "delivery_translation": "中文描述唯一"},
            {"locale": "en-MY", "field": "bullets", "value": ["EN KP ONE", "EN KP TWO"], "delivery_translation": ["中文卖点一", "中文卖点二"]},
        ],
        "field_groups": [
            {"group": "商品识别", "fields": ["title"], "ready": 1, "pending": 0},
            {"group": "购买决策", "fields": ["description", "bullets", "faq"], "ready": 3, "pending": 0},
            {"group": "事实 / 使用", "fields": ["attributes", "package"], "ready": 2, "pending": 0},
        ],
        "media_slots": [],
        "risks_and_holds": [],
    }


def _strategy():
    return {
        "human_projection": {"mode": "FULL"},
        "sections": {
            "01_information_completeness_assumptions_decisions": {
                "assumptions": [{"assumption": "A1", "status": "ASSUMPTION"}],
                "decision_log": [{"what": "BM primary", "why": "market language", "evidence": "project target", "tradeoff": "EN baseline retained", "execution": "BM primary copy", "measurement": "copy QA"}],
            },
            "02_product_truth_value_ladder": {"product_truth_audit_table": [{"item": "size", "fact_or_claim": "30g", "real_selling_point": "30g", "perceived_benefit": "known pack size", "emotional_value": "clarity", "non_claimable": "no efficacy inference", "evidence_grade": "A", "source_refs": ["excel"], "publication_rule": "FACT_ONLY", "basis": ["excel"], "tradeoff": "do not infer efficacy"}]},
            "03_platform_region_audience_culture_insight": {
                "context_why": {"platform": "TikTok commerce context", "region": "Malaysia context", "audience": "oily-skin routine context", "race_ethnicity_culture": "multi-ethnic context without stereotypes"},
                "intersectionality_table": [{"dimensions": ["race_ethnicity", "gender", "age", "income", "geography"], "implication": "do not infer behavior from identity", "evidence_or_assumption": "TO_VERIFY", "stereotype_guard": "no identity-to-need inference", "execution": "verify representation and language"}],
            },
            "04_marketing_core_strategy": {
                "positioning": {"target_user": "adult oily-skin shopper", "primary_conversion_proposition": "balanced daily routine"},
                "value_proposition": "VALUE PROP UNIQUE",
                "message_hierarchy": ["M1", "M2"],
                "framework_relationships": {"RACE": {"role": "process", "basis": "brief", "tradeoff": "one variable", "execution": "four stages", "measurement": "stage KPI"}},
            },
            "05_visual_photography_strategy": {"visual_thesis": "VISUAL THESIS UNIQUE", "people_applicability": "PERSON_PRESENT"},
            "06_platform_content_matrix": [{"platform": "TikTok Shop Malaysia", "audience": "adult", "topic": "oil balance", "hook": "HOOK", "script_structure": "STRUCT", "visual_form": "VIS", "cta": "CTA", "metric": "CTR", "race_stage": "COMMUNICATION", "culture_adaptation": "CHECK", "taboo_stereotype_check": "CHECK", "platform_dimensions": "1600x1600", "duration": "static", "cover_first_frame": "COVER", "subtitle_strategy": "BM", "music_rights": "N/A", "traffic_mechanism": "PDP", "landing_handoff": "PDP", "utm_attribution": "N/A", "why": "WHY"}],
            "07_race_execution_table": [{"stage": s, "objective": "OBJ", "key_actions": ["ACT"], "output": ["OUT"], "platform": "TikTok Shop Malaysia", "culture_check": "CHECK", "kpi": "KPI", "why": "WHY"} for s in ("RESEARCH", "ACTION", "COMMUNICATION", "EVALUATION")],
            "08_culture_adaptation_checklist": [{"adaptation_point": "language", "evidence_or_assumption": "TO_VERIFY", "inclusive_representation": "natural", "stereotype_taboo_risk": "avoid stereotypes", "script_check": "CHECK", "casting_check": "CHECK", "wardrobe_grooming_check": "CHECK", "color_check": "CHECK", "cta_check": "CHECK", "result": "TO_VERIFY", "modification": "modify responsible layer", "validation_result": "TO_VERIFY", "modification_action": "modify responsible layer", "why": "market context"}],
            "09_risk_measurement_priority_next_steps": {"resource_tradeoff_plan": {"constraints": ["unknown budget"], "keep": "P0 truth", "cut": "decorative repetition", "why": "protect truth"}},
        },
    }


def test_real_delivery_html_receives_canonical_payload_and_visible_static_projection(tmp_path: Path):
    from runtime.cbcc.delivery_html import build_delivery_html
    from runtime.cbcc.canonical_full_parity_v0671 import finalize_static_human_projection

    package = tmp_path / "package"
    package.mkdir()
    _write_json(package / "HUMAN_DELIVERY.json", _center())
    _write_json(package / "strategy/strategy_authority.json", _strategy())
    _write_json(package / "supporting_analysis/product_truth.json", {"inci": ["Water", "Glycerin"], "usage": "daily", "caution": "patch test", "barcode_status": "TO_VERIFY", "source_priority": ["Excel"]})
    build_delivery_html(package, package / "index.html")
    result = finalize_static_human_projection(package)
    assert result["status"] == "PASS"
    text = (package / "index.html").read_text(encoding="utf-8")
    assert "CBCC_CANONICAL_STATIC_PROJECTION_V0671" in text
    for token in ("EN DESCRIPTION UNIQUE", "BM KP ONE", "Net Content", "1 tube", "BM FAQ Q", "VALUE PROP UNIQUE", "VISUAL THESIS UNIQUE", "barcode_status", "source_priority"):
        assert token in text, token
    assert "data-canonical-path=" in text
    assert "CBCC_GLOBAL_SEARCH_INDEX_V0671" in text
    assert "navigator.clipboard.writeText" in text


def test_listing_markdown_is_field_parity_checked_against_human_delivery(tmp_path: Path):
    from runtime.cbcc.human_delivery import render_upload_center_md
    from runtime.cbcc.canonical_full_parity_v0671 import audit_listing_markdown_parity

    package = tmp_path / "package"
    package.mkdir()
    center = _center()
    _write_json(package / "HUMAN_DELIVERY.json", center)
    md = render_upload_center_md(center)
    (package / "01_LISTING_UPLOAD_READY.md").write_text(md, encoding="utf-8")
    assert audit_listing_markdown_parity(package) == []
    broken = md.replace("BM KP TWO", "")
    (package / "01_LISTING_UPLOAD_READY.md").write_text(broken, encoding="utf-8")
    issues = audit_listing_markdown_parity(package)
    assert issues and issues[0]["code"] == "LISTING_MARKDOWN_CANONICAL_FIELD_DRIFT"


def test_full_asset_package_lineage_covers_every_mature_file_and_detects_mutation(tmp_path: Path):
    from runtime.cbcc.asset_package_full_lineage_v0671 import materialize_full_asset_lineage, audit_full_asset_lineage

    root = tmp_path / "asset_packages"
    d = root / "G01"
    d.mkdir(parents=True)
    lineage = {"canonical_art_direction_sha256": "a" * 64, "prompt_cn_source_sha256": "a" * 64, "prompt_en_source_sha256": "a" * 64, "design_card_source_sha256": "a" * 64}
    files = {
        "00_asset_manifest.yaml": "asset_id: G01\n",
        "00_HUMAN_DESIGN_CARD_CN.md": "# card\n",
        "01_strategy.md": "# strategy\n",
        "02_visual_spec.md": "# visual\n",
        "03_photography_contract.json": "{}\n",
        "04_layout_contract.json": "{}\n",
        "05_prompt_CN.txt": "CN\n",
        "06_prompt_EN.txt": "EN\n",
        "07_generation_guidance.txt": "guide\n",
        "08_copy.md": "copy\n",
        "09_production_notes.md": "prod\n",
        "10_source_trace.md": "source\n",
        "11_strategy_authority_trace.json": "{}\n",
        "12_design_card.json": json.dumps({"canonical_prompt_lineage": lineage}),
        "13_prompt_contract.json": json.dumps({"canonical_prompt_lineage": lineage}),
        "14_visible_copy_block.json": "{}\n",
        "15_production_assembly_notes.json": "{}\n",
    }
    for name, content in files.items():
        (d / name).write_text(content, encoding="utf-8")
    result = materialize_full_asset_lineage(root)
    assert result["status"] == "PASS"
    manifest = json.loads((d / "CANONICAL_LINEAGE.json").read_text(encoding="utf-8"))
    assert set(files) <= set(manifest["files"])
    assert manifest["canonical_art_direction_sha256"] == "a" * 64
    assert audit_full_asset_lineage(root) == []
    (d / "02_visual_spec.md").write_text("mutated", encoding="utf-8")
    assert any(x["code"] == "ASSET_PACKAGE_FULL_LINEAGE_DRIFT" for x in audit_full_asset_lineage(root))


def test_strategy_completion_adds_major_decision_four_axis_why_and_real_interaction_rows():
    from runtime.cbcc.strategy_execution_completion_v0671 import complete_strategy_execution_v0671, completion_issues_v0671

    out = complete_strategy_execution_v0671(_strategy(), {"platform": "TikTok Shop Malaysia"})
    core = out["sections"]["04_marketing_core_strategy"]
    rows = core["major_decision_context_why"]
    assert rows
    for row in rows:
        assert set(row["context_why"]) >= {"platform", "region", "audience", "race_ethnicity_culture"}
        assert all((row["context_why"][k] or {}).get("why") for k in ("platform", "region", "audience", "race_ethnicity_culture"))
    interactions = out["sections"]["03_platform_region_audience_culture_insight"]["intersectionality_interaction_analysis"]
    assert len(interactions) >= 3
    for row in interactions:
        assert len(row["dimensions"]) >= 2
        assert row["mechanism"] and row["evidence_or_assumption"] and row["stereotype_guard"] and row["execution"] and row["verification_action"]
    assert completion_issues_v0671(out) == []


def test_human_asset_and_typography_relevance_is_explicit_without_inventing_identity():
    from runtime.cbcc.asset_execution_relevance_v0671 import complete_asset_execution_relevance, relevance_issues

    asset = {
        "asset_id": "G07",
        "visible_copy": {"copy_render_route": "MODEL_RENDER_INTEGRATED", "target_copy": "FOR OILY SKIN"},
        "asset_art_direction": {
            "subject": "adult person holding product",
            "human_context": {"age": "adult", "skin_tone": "natural diverse casting"},
            "typography": {"family": "neo-grotesk", "weight": "700/500", "hierarchy": "headline > support"},
        },
    }
    out = complete_asset_execution_relevance(asset)
    art = out["asset_art_direction"]
    decisions = art["human_relevance_decisions"]
    for key in ("hair_texture_style", "makeup_grooming", "wardrobe", "body_representation", "disability_representation", "pose", "expression", "gaze", "religious_cultural_presentation"):
        assert decisions[key]["status"] in {"SELECTED", "NOT_NEEDED", "TO_VERIFY"}
        assert decisions[key]["why"]
    # No missing identity dimension may be silently invented as a selected fact.
    assert decisions["disability_representation"]["status"] != "SELECTED"
    type_contract = art["typography_contract"]
    for key in ("family_character", "weight", "hierarchy", "line_breaking", "relative_scale", "alignment", "contrast", "safe_zone", "mobile_thumbnail_legibility", "product_geometry_relationship"):
        assert type_contract[key]["status"] in {"SELECTED", "NOT_NEEDED", "TO_VERIFY"}
        assert type_contract[key]["why"]
    assert relevance_issues(out) == []


def test_human_payload_exposes_independent_asset_production_objects(tmp_path: Path):
    from runtime.cbcc.canonical_full_parity_v0671 import build_canonical_human_payload

    package = tmp_path / "package"
    d = package / "asset_packages/G01"
    d.mkdir(parents=True)
    _write_json(package / "HUMAN_DELIVERY.json", _center())
    (d / "00_asset_manifest.yaml").write_text("asset_id: G01\nasset_name: Hero\n", encoding="utf-8")
    (d / "02_visual_spec.md").write_text("VISUAL SPEC UNIQUE", encoding="utf-8")
    _write_json(d / "03_photography_contract.json", {"lens": "85mm"})
    _write_json(d / "04_layout_contract.json", {"safe_zone": "mobile"})
    (d / "05_prompt_CN.txt").write_text("PROMPT CN UNIQUE", encoding="utf-8")
    (d / "06_prompt_EN.txt").write_text("PROMPT EN UNIQUE", encoding="utf-8")
    (d / "10_source_trace.md").write_text("SOURCE TRACE UNIQUE", encoding="utf-8")
    _write_json(d / "11_strategy_authority_trace.json", {"trace": "STRATEGY TRACE UNIQUE"})
    _write_json(d / "12_design_card.json", {"asset_id": "G01"})
    _write_json(d / "13_prompt_contract.json", {"status": "READY"})
    _write_json(d / "14_visible_copy_block.json", {"copy": "VISIBLE COPY UNIQUE"})
    _write_json(d / "15_production_assembly_notes.json", {"note": "PRODUCTION OBJECT UNIQUE"})
    payload = build_canonical_human_payload(package)
    a = payload["assets"][0]
    assert a["visual_spec"] == "VISUAL SPEC UNIQUE"
    assert a["photography_contract"]["lens"] == "85mm"
    assert a["layout_contract"]["safe_zone"] == "mobile"
    assert "SOURCE TRACE UNIQUE" in a["source_trace"]
    assert a["strategy_trace"]["trace"] == "STRATEGY TRACE UNIQUE"
    assert a["prompt_cn"] == "PROMPT CN UNIQUE"
    assert a["prompt_en"] == "PROMPT EN UNIQUE"
