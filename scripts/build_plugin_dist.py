#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "cross-border-commerce-creative"
DISPLAY_NAME = "Cross-Border Commerce Creative"

EXCLUDE_PARTS = {".git", ".github", ".pytest_cache", "__pycache__", "dist", "evidence"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}

DEFAULT_PROMPTS = [
    "基于当前对话、上传资料和必要的最新公开信息，完成当前商品的跨境电商策略、Listing、内容、视觉策展与逐资产中英文 Canonical Prompt。人类交付默认中文，不要套固定模板。",
    "只做当前 SKU 的目标市场/平台视觉资产策展和逐资产生产提示词，本轮不生成图片；先建立商品真源、购买决策、创意机会和动态 Surface，并确保摄影/CMF/构图参数进入最终 Prompt。",
    "审查当前营销策划或提示词，定位写了但未被生产链消费、同风格同布局、产品失真、平台不原生或文案与画面脱节的责任层，只修对应层。",
]


def semver() -> str:
    raw = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", raw)
    if not match:
        raise SystemExit(f"VERSION does not start with strict semver: {raw}")
    return ".".join(match.groups())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def should_copy(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if not path.is_file():
        return False
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    return True


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def plugin_manifest(version: str) -> dict:
    return {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": PLUGIN_NAME,
        "version": version,
        "description": "Cross-border ecommerce Commerce Agent for product truth, dynamic research, strategy, listing, content, visual/photography, canonical prompts, production, review and learning.",
        "author": {"name": "CBCC"},
        "keywords": [
            "ecommerce", "cross-border", "commerce-agent", "marketing", "listing",
            "creative", "visual", "prompt", "photography", "production",
        ],
        "extensions": {
            "com.openai": {
                "interface": {
                    "displayName": DISPLAY_NAME,
                    "shortDescription": "跨境电商策略、内容与创意生产",
                    "longDescription": "跨境电商 Commerce Agent：从 Product Truth、证据与平台约束出发，动态完成研究、SKU/Offer、策略、Listing、内容、视觉摄影、图片/视频资产、Canonical Prompt、生产、Review 与学习闭环。默认中文人类交付；研究、框架、内容、Surface、资产与创意方向由当前任务动态决定，不套固定配额或流水线模板。",
                    "developerName": "CBCC",
                    "category": "Productivity",
                    "capabilities": ["Interactive"],
                    "defaultPrompt": DEFAULT_PROMPTS,
                }
            }
        },
    }


def compatibility_manifest(manifest: dict) -> dict:
    return {
        "interface": manifest["extensions"]["com.openai"]["interface"],
        "name": manifest["name"],
        "version": manifest["version"],
        "description": manifest["description"],
        "author": manifest["author"],
        "keywords": manifest["keywords"],
        "skills": "./skills",
    }


def skill_wrapper(version: str) -> str:
    return f'''---
name: cross-border-commerce-creative
description: 用于跨境电商 Product Truth、动态研究、SKU/Offer、Listing/Search、策略、内容、视觉摄影、图片/视频资产、逐资产中英文 Canonical Prompt、生产、Review 与学习闭环；默认中文人类交付，任务范围与资产结构动态决定。
---
# Cross-Border Commerce Creative v{version}

当前发行的完整 Agent/Skill 权威位于 `resources/SKILL.md`；`resources/VERSION`、`resources/CURRENT_HANDOFF.md` 与 `resources/CHANGELOG_V0629.md` 用于核对源码版本和发布状态。

## 使用原则
- 从用户目标、Product Truth、证据、目标市场/平台与当前交付范围开始，由 Agent 发现信息缺口并决定研究、策略、框架、内容、Surface、资产与创意方向。
- 不把固定研究清单、固定 RACE/AIDA/4P、固定 9 图/12 图、固定方向数、摄影字段配额或通用页面流水线作为创意/商业权威。
- 中文优先做人类交付；目标市场可见文案保留目标语言，并以合适方式提供中文释义/说明。
- 商品身份、包装、材质、颜色、结构与可见事实必须 source-bound；Claim、Compliance、平台当前证据、Review 与 Completion 按 `resources/SKILL.md` 和 Runtime 合同执行。
- 每个图片/视频资产的消费者决策问题、画面目标、Photography/CMF、构图、色彩管理、Product Fidelity、可编辑/冻结层与 Canonical Prompt 应保持可追踪连续性。

## Runtime / Host 边界
本 Plugin 携带当前 GitHub 源码 resources 供 Skill 使用与审计，但源码存在不等于云端 Runtime 已连接。需要 Provider、Plugin HTTP Action 或 MCP tool 时，必须使用实际运行且经过验证的宿主/部署；不得把打包源码伪报为远程工具连接。

## 当前主权威
开始复杂任务前先读取 `resources/SKILL.md`；需要当前版本状态时读取 `resources/CURRENT_HANDOFF.md`；需要安装/宿主说明时读取 `resources/INSTALL.md`。
'''


def openai_yaml() -> str:
    return '''interface:
  display_name: Cross-Border Commerce Creative
  short_description: 跨境电商策略、内容与创意生产
  default_prompt: 基于当前商品资料、真实商品真源和目标市场/平台，由 Agent 动态发现信息缺口并完成当前范围真正需要的研究、策略、Listing、内容、视觉策展与逐资产中英文 Canonical Prompt；人类交付默认中文，不套固定模板或固定资产配额。
policy:
  allow_implicit_invocation: true
'''


def usage_cn() -> str:
    return '''# 使用说明（v0.6.29）

1. 复杂任务先以 `resources/SKILL.md` 作为完整权威。
2. GitHub `main` 是唯一源码真源；Plugin/Skill 是派生发行物。
3. 人类交付默认中文，目标市场可见文案保留目标语言并配中文释义。
4. Agent 根据当前 Commerce Goal、Product Truth、证据和 Surface 动态决定研究、策略、内容、资产与创意方向。
5. Plugin 内含 Runtime 源码 resources，但需要真实 Provider/MCP/HTTP 执行时仍必须连接实际宿主。
'''


def cli_usage_cn() -> str:
    return '''# Runtime CLI

完整本地 Runtime 使用仓库/Runtime Release，不建议只抽取 Python 包。

```bash
python bin/cbcc.py --help
bash tests/run_smoke.sh
PYTHONPATH=runtime python -m cbcc.plugin_http_cli --bind 127.0.0.1 --port 8787
PYTHONPATH=runtime python -m cbcc.mcp_stdio_cli
```

更多说明见 `resources/INSTALL.md`。
'''


def copy_repo_resources(dest: Path) -> None:
    for src in sorted(ROOT.rglob("*")):
        if not should_copy(src):
            continue
        rel = src.relative_to(ROOT)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)


def zip_tree(source_dir: Path, output: Path, enclosing_dir: bool) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source_dir.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(source_dir)
            arcname = Path(source_dir.name) / rel if enclosing_dir else rel
            zf.write(path, arcname)


def build(output_dir: Path) -> dict:
    version = semver()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = plugin_manifest(version)

    with tempfile.TemporaryDirectory(prefix="cbcc-release-") as td:
        tmp = Path(td)
        plugin_root = tmp / PLUGIN_NAME
        skill_root = plugin_root / "skills" / PLUGIN_NAME
        resources = skill_root / "resources"

        write_text(plugin_root / "plugin.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        write_text(plugin_root / ".codex-plugin" / "plugin.json", json.dumps(compatibility_manifest(manifest), ensure_ascii=False, indent=2) + "\n")
        write_text(skill_root / "SKILL.md", skill_wrapper(version))
        write_text(skill_root / "agents" / "openai.yaml", openai_yaml())
        write_text(skill_root / "references" / "USAGE_CN.md", usage_cn())
        write_text(skill_root / "references" / "CLI_USAGE_CN.md", cli_usage_cn())
        copy_repo_resources(resources)

        plugin_zip = output_dir / f"{PLUGIN_NAME}-plugin-v{version}.zip"
        zip_tree(plugin_root, plugin_zip, enclosing_dir=True)

        # Standalone skill archive: one enclosing skill directory, no plugin manifest.
        standalone = tmp / f"{PLUGIN_NAME}-skill"
        shutil.copytree(skill_root, standalone / PLUGIN_NAME)
        skill_zip = output_dir / f"{PLUGIN_NAME}-skill-v{version}.zip"
        zip_tree(standalone / PLUGIN_NAME, skill_zip, enclosing_dir=True)

    release = {
        "version": version,
        "source_version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "artifacts": [
            {"file": plugin_zip.name, "sha256": sha256(plugin_zip), "bytes": plugin_zip.stat().st_size},
            {"file": skill_zip.name, "sha256": sha256(skill_zip), "bytes": skill_zip.stat().st_size},
        ],
    }
    manifest_path = output_dir / "release_manifest.json"
    write_text(manifest_path, json.dumps(release, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(release, ensure_ascii=False, indent=2))
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description="Build CBCC Agent Plugin and standalone Skill release archives from the current GitHub source tree.")
    ap.add_argument("--output-dir", default=str(ROOT / "dist"))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
