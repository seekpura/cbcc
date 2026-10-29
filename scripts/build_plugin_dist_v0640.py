#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0637 as v0637
from scripts import build_plugin_dist_v0638 as v0638

ROOT = Path(__file__).resolve().parents[1]

PROJECT_AUTHORITY = r'''
## Project-Authored Human HTML Runtime Authority — highest current precedence
- `index.html` 是当前商品项目的人类产品界面，不是 CBCC 能力目录或流程图。永久导航不得镜像 Product / Market / Listing / Strategy / Content / Visual / Assets / Prompt / Risk / Sources 等能力分类。
- 首屏使用当前项目对象地图；current priority / next action 单独呈现，不拥有信息架构权。页面数、组合、对象名称由真实商品、市场、平台、Locale、商业决策、资产宇宙与生产对象决定。
- 资产详情是一个对象的多个 lens，不是 Design Card → 画面 → 摄影 → 文案 → Prompt → QA 的 phase rail。通用模块导航不得制造 01→02→03 的伪流程。
- Operator board、七工具连续性、Runtime/Consumer/hash/Gate 只在当前项目需要时进入次级 Inspector/Archive，不得作为固定主页面或自动插在项目最前面。
- UI 动态化不得压缩 v0.6.37 的商业深度；完整 Strategy、Listing 最终文案、Visual/Video 策展、逐资产 Design Card、Model Prompt CN/EN、Visible Copy Block、Production/Assembly Notes 与当前相关 Economics/Ads/Review/Evidence 仍需直接可用。
- 最终 renderer 必须实际调用 `project_authored_html()`；只有 Skill 文案声明“不要流水线”而运行时仍输出固定 sidebar 不算修复。
'''.strip()

PROJECT_DEFAULT_PROMPT = (
    'v0.6.40 最高权威：最终 index.html 的信息架构是当前项目的设计输出。永久导航不得镜像 CBCC 能力目录；首屏是当前项目对象地图，当前重点/next action 与信息架构分离。不得使用固定左侧 Product→Market→Listing→Strategy→Content→Visual→Assets→Prompt→Risk→Sources 菜单、固定页面数、固定 dashboard、固定资产 phase rail 或 01→02→03 阅读顺序。最终 renderer 必须实际执行 project-authored HTML 转换。'
)


def _inject(text: str, section: str) -> str:
    if section in text:
        return text
    marker = text.find('\n# ')
    if marker == -1:
        return section + '\n\n' + text
    heading_end = text.find('\n', marker + 1)
    if heading_end == -1:
        return text + '\n\n' + section + '\n'
    return text[:heading_end + 1] + '\n' + section + '\n\n' + text[heading_end + 1:]


def skill_wrapper(version: str) -> str:
    return _inject(v0638.skill_wrapper(version), PROJECT_AUTHORITY)


def copy_repo_resources(dest: Path) -> None:
    v0638.copy_repo_resources(dest)
    canonical_path = dest / 'SKILL.md'
    canonical = canonical_path.read_text(encoding='utf-8')
    canonical = canonical.replace('version: 0.6.39-project-authored-html', 'version: 0.6.40-project-authored-html-runtime', 1)
    canonical = canonical.replace('version: 0.6.38-host-delivery-regression-fix', 'version: 0.6.40-project-authored-html-runtime', 1)
    canonical = _inject(canonical, PROJECT_AUTHORITY)
    canonical_path.write_text(canonical, encoding='utf-8')


def build(output_dir: Path) -> dict:
    base.DEFAULT_PROMPTS = [PROJECT_DEFAULT_PROMPT, v0638.HOST_DEFAULT_PROMPT, v0637.INTEGRATED_DEFAULT_PROMPT] + [
        p for p in base.DEFAULT_PROMPTS
        if p not in {PROJECT_DEFAULT_PROMPT, v0638.HOST_DEFAULT_PROMPT, v0637.INTEGRATED_DEFAULT_PROMPT}
    ]
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    data = base.build(output_dir)
    manifest_path = output_dir / 'release_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['release'] = 'Project-Authored HTML Runtime + Commercial Operator Density'
    manifest['authority_version'] = '0.6.40-project-authored-html-runtime'
    manifest.setdefault('delivery_contract', {}).update({
        'project_authored_html_runtime_wired': True,
        'project_object_map_first_screen': True,
        'fixed_capability_sidebar_forbidden': True,
        'permanent_navigation_capability_catalog_forbidden': True,
        'next_action_separate_from_information_architecture': True,
        'asset_phase_rail_forbidden': True,
        'operator_board_primary_injection_forbidden': True,
        'commercial_depth_preserved_from_v0637': True,
    })
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.40 project-authored HTML runtime release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
