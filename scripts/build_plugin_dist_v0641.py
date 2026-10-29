#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0637 as v0637
from scripts import build_plugin_dist_v0638 as v0638

ROOT = Path(__file__).resolve().parents[1]

SAAS_AUTHORITY = r'''
## Project-Authored SaaS Workspace Authority — highest current precedence
- 最终 `index.html` 不是能力目录、流程图，也不是固定 dashboard/card grid。Host Agent 仍可按项目自行设计界面；Runtime 的确定性兜底使用项目身份 + Project Home + 可搜索 Project Objects 切换器，而不是永久能力菜单。
- Product / Market / Listing / Strategy / Content / Visual / Assets / Prompt / Risk / Sources 等系统能力不得自动成为常驻导航；只有当前项目真实存在的对象进入对象切换器。
- current priority / next action 与信息架构分离；资产内部 Design Card / Visual / Photography-CMF / Copy / Prompt / Production / QA 是同一对象的 lenses，不是 phase rail。
- 禁止把“去流水线”修成新的项目地图卡片墙；Host-native 可以选择项目适合的 canvas / portfolio / document / matrix / object browser 等界面。
- UI 变化不得压缩 v0.6.37 商业深度。
'''.strip()

DEFAULT_PROMPT = (
    'v0.6.41 人类交付最高权威：不要把去流水线修成新的固定 dashboard 或 card grid。最终 index.html 的信息架构由当前项目作者化。Runtime 兜底只保留项目身份、项目主页与可搜索的 Project Objects 切换器；Product/Market/Listing/Strategy/Visual/Assets 等能力不得成为永久菜单。current priority 与 IA 分离，资产子视图是 lenses 不是步骤。保持 v0.6.37 完整商业/创意/生产深度。'
)


def _inject(text: str, section: str) -> str:
    if section in text:
        return text
    marker = text.find('\n# ')
    if marker == -1:
        return section + '\n\n' + text
    end = text.find('\n', marker + 1)
    if end == -1:
        return text + '\n\n' + section + '\n'
    return text[:end + 1] + '\n' + section + '\n\n' + text[end + 1:]


def skill_wrapper(version: str) -> str:
    return _inject(v0638.skill_wrapper(version), SAAS_AUTHORITY)


def copy_repo_resources(dest: Path) -> None:
    v0638.copy_repo_resources(dest)
    p = dest / 'SKILL.md'
    text = p.read_text(encoding='utf-8')
    for old in ('version: 0.6.39-project-authored-html', 'version: 0.6.40-project-authored-html-runtime', 'version: 0.6.38-host-delivery-regression-fix'):
        text = text.replace(old, 'version: 0.6.41-project-authored-saas-workspace', 1)
    p.write_text(_inject(text, SAAS_AUTHORITY), encoding='utf-8')


def build(output_dir: Path) -> dict:
    base.DEFAULT_PROMPTS = [DEFAULT_PROMPT, v0638.HOST_DEFAULT_PROMPT, v0637.INTEGRATED_DEFAULT_PROMPT] + [
        p for p in base.DEFAULT_PROMPTS if p not in {DEFAULT_PROMPT, v0638.HOST_DEFAULT_PROMPT, v0637.INTEGRATED_DEFAULT_PROMPT}
    ]
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    data = base.build(output_dir)
    manifest_path = output_dir / 'release_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['release'] = 'Project-Authored SaaS Workspace + Commercial Operator Density'
    manifest['authority_version'] = '0.6.41-project-authored-saas-workspace'
    manifest.setdefault('delivery_contract', {}).update({
        'fixed_capability_sidebar_forbidden': True,
        'fixed_dashboard_card_grid_forbidden': True,
        'saas_object_switcher_runtime_fallback': True,
        'host_native_interface_remains_agent_authored': True,
        'next_action_separate_from_information_architecture': True,
        'asset_phase_rail_forbidden': True,
        'commercial_depth_preserved_from_v0637': True,
    })
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.41 project-authored SaaS workspace release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
