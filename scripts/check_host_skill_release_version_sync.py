#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")
FRONTMATTER_VERSION_RE = re.compile(r"(?m)^version:\s*([^\n]+)$")
H1_VERSION_RE = re.compile(r"(?m)^#\s+Cross-Border Commerce Creative v(\d+\.\d+\.\d+)\s*$")


def semver(value: str) -> str:
    m = SEMVER_RE.match((value or "").strip())
    if not m:
        raise ValueError(f"not semver-like: {value!r}")
    return ".".join(m.groups())


def audit_dist(dist: Path) -> dict:
    issues: list[str] = []
    plugin_json = dist / "plugin.json"
    codex_json = dist / ".codex-plugin/plugin.json"
    skill = dist / "SKILL.md"
    # Also accept a fully packaged plugin root where the active Skill lives under skills/...
    if not skill.exists():
        candidates = list(dist.glob("skills/*/SKILL.md"))
        if len(candidates) == 1:
            skill = candidates[0]
    if not plugin_json.exists(): issues.append("MISSING_PLUGIN_JSON")
    if not codex_json.exists(): issues.append("MISSING_CODEX_PLUGIN_JSON")
    if not skill.exists(): issues.append("MISSING_ACTIVE_HOST_SKILL")
    if issues:
        return {"status": "FAIL", "issues": issues}

    p = json.loads(plugin_json.read_text(encoding="utf-8"))
    c = json.loads(codex_json.read_text(encoding="utf-8"))
    skill_text = skill.read_text(encoding="utf-8")
    fm = FRONTMATTER_VERSION_RE.search(skill_text)
    h1 = H1_VERSION_RE.search(skill_text)
    values = {
        "plugin_json": semver(str(p.get("version") or "")),
        "codex_plugin_json": semver(str(c.get("version") or "")),
        "skill_frontmatter": semver(fm.group(1) if fm else ""),
        "skill_h1": semver(h1.group(1) if h1 else ""),
    }
    expected = values["plugin_json"]
    for name, value in values.items():
        if value != expected:
            issues.append(f"VERSION_MISMATCH:{name}:{value}!={expected}")
    skill_low = skill_text.lower()
    required_tokens = [
        "full hard rules",
        "race/ethnicity × gender × age × income × geography",
        "research → action → communication → evaluation",
        "final materialized package",
        "c-grade must never become a hard claim",
    ]
    missing = [x for x in required_tokens if x not in skill_low]
    if missing:
        issues.append("ACTIVE_HOST_SKILL_MISSING_V0648_CONTRACT:" + ",".join(missing))
    return {
        "status": "PASS" if not issues else "FAIL",
        "issues": issues,
        "versions": values,
        "active_skill": str(skill),
        "principle": "A release version is not valid unless the actual Host-facing Skill carries the same semantic version and current FULL hard contract.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dist")
    args = ap.parse_args()
    report = audit_dist(Path(args.dist).resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
