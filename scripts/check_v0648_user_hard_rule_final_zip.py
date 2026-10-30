#!/usr/bin/env python3
"""Validate the *final materialized FULL delivery package* against the user hard-rule contract.

This is intentionally package-level. It does not trust strategy prose, boolean audit flags,
or a Host-authored PASS declaration. It reads the actual files that ship to the user.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
import argparse, json, sys

CONTRACT = "USER_HARD_RULES_FULL_V1_FINAL_ZIP"
REQUIRED = {
    "01": "supporting_analysis/INFORMATION_COMPLETENESS_ASSUMPTION_DECISION.json",
    "02": "supporting_analysis/PRODUCT_FACT_AUDIT.json",
    "03": "supporting_analysis/PLATFORM_REGION_AUDIENCE_CULTURE.json",
    "04": "supporting_analysis/MARKETING_FRAMEWORK_CORE_STRATEGY.json",
    "05": "supporting_analysis/VISUAL_EXECUTION_LOCK.json",
    "06": "supporting_analysis/PLATFORM_CONTENT_MATRIX.json",
    "07": "supporting_analysis/RACE_FRAMEWORK.json",
    "08": "supporting_analysis/CULTURAL_ADAPTATION.json",
    "09": "supporting_analysis/COMPLIANCE_RISK_EVALUATION_PRIORITY.json",
    "claim": "supporting_analysis/CLAIM_EVIDENCE_MATRIX.json",
}
HTML_TOKENS = [
    "信息完整度", "产品事实审计", "平台 × 区域 × 人群 × 族裔文化",
    "营销框架与核心策略", "视觉总策略与拍摄执行", "分平台内容矩阵",
    "RACE传播框架执行表", "族裔文化适配检查表", "合规 · 风险 · 评估 · 优先级",
]

def _read_json(root: Path, rel: str, issues: list[str]) -> dict[str, Any]:
    p = root / rel
    if not p.exists() or p.stat().st_size < 20:
        issues.append(f"MISSING_REQUIRED_OBJECT:{rel}")
        return {}
    try:
        v = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        issues.append(f"INVALID_JSON:{rel}:{exc}")
        return {}
    if not isinstance(v, dict):
        issues.append(f"INVALID_ROOT_TYPE:{rel}")
        return {}
    return v

def _need(row: dict[str, Any], keys: list[str], prefix: str, issues: list[str]) -> None:
    for key in keys:
        if row.get(key) in (None, "", [], {}):
            issues.append(f"{prefix}_MISSING:{key}")

def audit_package(package_dir: str | Path) -> dict[str, Any]:
    root = Path(package_dir).resolve()
    issues: list[str] = []
    evidence: dict[str, Any] = {}
    if not root.exists():
        return {"contract": CONTRACT, "status": "FAIL", "issues": [f"PACKAGE_NOT_FOUND:{root}"], "project_completion_blocking": True}

    data = {key: _read_json(root, rel, issues) for key, rel in REQUIRED.items()}

    # 01: audit -> <=10 questions -> assumptions -> continue
    info = data["01"]
    qs = info.get("pending_questions") or []
    if len(qs) > 10: issues.append("PENDING_QUESTIONS_GT_10")
    for key in ("information_completeness", "pending_questions", "assumptions", "decision_log"):
        if not info.get(key): issues.append(f"DOMAIN01_MISSING:{key}")
    evidence["pending_questions_count"] = len(qs)

    # 02: fact/value/claim classes + A/B/C; C cannot be hard claim.
    fact = data["02"]
    rows = fact.get("rows") or []
    required_categories = {"真实卖点", "可感知利益", "情绪价值", "不可宣称项"}
    present_categories = {str(x.get("category") or "") for x in rows if isinstance(x, dict)}
    if not required_categories.issubset(present_categories):
        issues.append("PRODUCT_FACT_CATEGORY_COVERAGE_INCOMPLETE")
    grades = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict): continue
        grade = str(row.get("evidence_grade") or row.get("grade") or "").upper()
        grades.add(grade[:1])
        _need(row, ["item", "category", "source", "publish_rule"], f"FACT_ROW_{i}", issues)
        if grade.startswith("C") and row.get("hard_claim_allowed") is not False:
            issues.append(f"C_GRADE_HARD_CLAIM:{i}")
    if not {"A", "B", "C"}.intersection(grades):
        issues.append("EVIDENCE_GRADE_SYSTEM_MISSING")

    # 03: WHY + intersectionality + localization. race/ethnicity must not be silently dismissed in FULL.
    ctx = data["03"]
    why_rows = ctx.get("why_dimensions") or []
    why_blob = json.dumps(why_rows, ensure_ascii=False)
    for token in ("平台", "区域", "人群", "族裔文化"):
        if token not in why_blob: issues.append(f"WHY_DIMENSION_MISSING:{token}")
    inter_blob = json.dumps(ctx.get("intersectionality") or [], ensure_ascii=False)
    for token in ("族裔", "性别", "年龄", "收入", "地域"):
        if token not in inter_blob: issues.append(f"INTERSECTIONALITY_MISSING:{token}")
    loc_blob = json.dumps(ctx.get("localization_operating_table") or [], ensure_ascii=False)
    for token in ("语言", "节日", "支付", "物流", "宗教", "法规"):
        if token not in loc_blob: issues.append(f"LOCALIZATION_MISSING:{token}")
    legacy_market = root / "supporting_analysis/MARKET_AUDIENCE.json"
    if legacy_market.exists():
        try:
            m = json.loads(legacy_market.read_text(encoding="utf-8"))
            race_status = (m.get("status_dimensions") or {}).get("race_ethnicity")
            if race_status == "NOT_RELEVANT": issues.append("RACE_ETHNICITY_WRONGLY_NOT_RELEVANT")
        except Exception:
            pass

    # 04: every major strategy must have basis + tradeoff + cross-context why + execution + metric; explicit P0/P1/P2 tradeoffs.
    strat = data["04"]
    for i, row in enumerate(strat.get("strategy_rows") or []):
        if isinstance(row, dict):
            _need(row, ["decision", "basis", "tradeoff", "why_platform_region_audience_culture", "execution", "metric"], f"STRATEGY_ROW_{i}", issues)
    framework_blob = json.dumps(strat.get("framework_relationships") or [], ensure_ascii=False).upper()
    for token in ("RACE", "STP", "JTBD", "AIDA", "FABE", "4P", "FUNNEL"):
        if token not in framework_blob: issues.append(f"FRAMEWORK_RELATIONSHIP_MISSING:{token}")
    prio = {str(x.get("priority") or "") for x in (strat.get("resource_tradeoff") or []) if isinstance(x, dict)}
    if not {"P0", "P1", "P2"}.issubset(prio): issues.append("RESOURCE_TRADEOFF_P0_P1_P2_MISSING")

    # 05: visual execution depth + inclusive representation. Deep-skin plan must include exposure and bounce/diffusion when people are planned.
    vis = data["05"]
    for key in ("style_keywords", "moodboard_direction", "composition_rules", "palette", "lighting_master", "camera_framework", "scene_props_wardrobe", "inclusive_photography_p0", "platform_sizes", "shot_list"):
        if not vis.get(key): issues.append(f"VISUAL_EXECUTION_MISSING:{key}")
    inc_blob = json.dumps(vis.get("inclusive_photography_p0") or [], ensure_ascii=False)
    for token in ("深肤色", "发质", "体型", "残障", "年龄", "AI"):
        if token not in inc_blob: issues.append(f"INCLUSIVE_REPRESENTATION_MISSING:{token}")
    human_planned = any(tok in json.dumps(vis, ensure_ascii=False) for tok in ("人物", "Creator", "真人", "模特", "手部"))
    if human_planned:
        light_blob = json.dumps(vis.get("lighting_master") or {}, ensure_ascii=False).lower()
        if "ev" not in light_blob: issues.append("DEEP_SKIN_EXPOSURE_PLAN_MISSING")
        if not any(tok in light_blob for tok in ("bounce", "reflector", "反光板")): issues.append("DEEP_SKIN_BOUNCE_PLAN_MISSING")
        if not any(tok in light_blob for tok in ("diffusion", "柔光")): issues.append("DEEP_SKIN_DIFFUSION_PLAN_MISSING")

    # 06: platform matrix production fields including RACE + culture.
    matrix = data["06"].get("rows") or []
    matrix_fields = ["platform", "audience", "topic", "hook", "script_structure", "visual_form", "cta", "metric", "race_stage", "culture_taboo_check", "size_duration", "cover", "subtitle", "music_rights", "traffic_mechanism", "landing", "utm_attribution"]
    for i, row in enumerate(matrix):
        if isinstance(row, dict): _need(row, matrix_fields, f"CONTENT_MATRIX_ROW_{i}", issues)

    # 07: exact RACE order and full execution columns.
    race = data["07"].get("rows") or []
    if [x.get("stage") for x in race if isinstance(x, dict)] != ["Research", "Action", "Communication", "Evaluation"]:
        issues.append("RACE_ORDER_INVALID")
    for i, row in enumerate(race):
        if isinstance(row, dict): _need(row, ["objective", "key_actions", "outputs", "platform", "culture_validation", "metrics", "why"], f"RACE_ROW_{i}", issues)

    # 08: cultural check table, with evidence/assumption and modification action.
    culture = data["08"].get("rows") or []
    for i, row in enumerate(culture):
        if isinstance(row, dict): _need(row, ["check", "adaptation", "inclusive_representation", "stereotype_taboo", "result", "modification", "basis"], f"CULTURE_ROW_{i}", issues)

    # 09 + claim P0: self-check, A/B tests, risk/priority, claim evidence categories.
    risk = data["09"]
    for key in ("risk_list", "ab_tests", "self_check", "next_inputs"):
        if not risk.get(key): issues.append(f"DOMAIN09_MISSING:{key}")
    if len(risk.get("self_check") or []) < 6: issues.append("SELF_CHECK_TOO_SHALLOW")
    claim_blob = json.dumps(data["claim"], ensure_ascii=False)
    for token in ("功效", "成分", "认证", "价格", "销量"):
        if token not in claim_blob: issues.append(f"CLAIM_P0_CATEGORY_MISSING:{token}")

    # Human artifact must surface all 9 domains directly. A short custom report cannot replace them.
    html_path = root / "index.html"
    if not html_path.exists():
        issues.append("MISSING_INDEX_HTML")
    else:
        html_text = html_path.read_text(encoding="utf-8", errors="replace")
        for token in HTML_TOKENS:
            if token not in html_text: issues.append(f"INDEX_MISSING_DOMAIN:{token}")

    # Existing audit files are evidence only, never an authority that can overrule the real package check.
    status = "PASS" if not issues else "FAIL"
    return {
        "contract": CONTRACT,
        "status": status,
        "issues": issues,
        "evidence": evidence,
        "project_completion_blocking": True,
        "launch_readiness_separate": True,
        "principle": "PASS proves the user hard-rule delivery contract is materially present in the final package; it does not fabricate external regulatory/platform/economic readiness.",
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("package_dir")
    ap.add_argument("--write", default="qa/USER_HARD_RULE_VALIDATION.json")
    args = ap.parse_args()
    root = Path(args.package_dir).resolve()
    report = audit_package(root)
    out = root / args.write
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
